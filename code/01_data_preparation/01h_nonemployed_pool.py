"""
01h_nonemployed_pool.py — Build the ORG non-employed pool for the matching simulation (02d).

Reads the RAW, pre-gate ORG partitions (full household rosters) and replicates the two wage
steps 01b would do (sentinel stripping; selection-corrected MPL imputation). Remodeled
2026-07-08 per Infrastructure/plans/2026-07-08_entry-from-nonemployment-implementation_rev2.md
(user-approved) and the challenge report of the same date. What this stage now does:

  1. WAGE SENTINELS — unchanged (HOURWAGE >= 999.99; EARNWEEK era-specific sentinels).

  2. MPL via HECKMAN two-step with a SELECTION-CONSISTENT prediction (ST-7). The selection
     probit gains real household shifters merged from 01i_household_links.py (spouse-employed
     x married; own child under 5) alongside the pre-existing married/nchild terms, plus
     STATEFIP and a finer 8-bucket education in BOTH equations (M3). The pool's potential wage
     is imputed at the CONDITIONAL mean for non-participants,
         E[log w | X, D=0] = X*beta + rho_sigma * (-phi/(1-Phi)),
     which sits below X*beta when workers are positively selected — the previous Mills=0
     (unconditional) prediction discarded exactly that selection and made the pool median equal
     the employed median. Both variants plus a plain-OLS (no-IMR) imputation are printed each
     run (Puhani-style sensitivity). DISCLOSED: no bulletproof exclusion restriction exists in
     these data (assortative mating; motherhood penalty; marriage premium) — see
     docs/entry_from_nonemployment_methodology.md #3.7.

  3. RESERVATION-WAGE BAND (M2), replacing the single equality-solved markup:
     three lambda-bisections per cell (lower/central/upper eps_ext from
     cfg["matching"]["eps_ext_band"]), each calibrated on the NET, SATURATING, PERSON-LEVEL
     criterion (ST-1/2/11):
       - stimulus: g_net_i = [NI(y+s(y)) - NI(y*h)] / [NI(y*h) - NI(0)] (net return to work),
       - target:   weighted mean of response_multiplier(eps, g_net, ceiling_ext) - 1
                   over reachable (MPL < target) persons,
       - viable(lambda): NI((y + s(y))*h_i) >= NI(r_i(lambda)*h_i), r_i = y_i*(1+m_i),
     run through the same PolicyEngine schedules 02b/02d use for fiscal costs. Markups use a
     HASH-of-person-ID rank (ST-10) — independent of file order — and the SAME rank across the
     three edges (common random numbers), so the three viable sets are nested and the three
     reservation columns are pointwise monotone (asserted). Subsidy treated as taxable/countable
     ordinary income (user decision 2026-07-08; disclosed in the methodology doc #4).

  4. ENTRANT HOURS (M7): quantile-matched — each pool member's MPL percentile within cell maps
     to the same percentile of incumbent annual hours in that cell (hourly_workers.parquet).

Output: data/processed/nonemployed_pool.parquet — one row per non-employed person 16-64, now
carrying person keys (YEAR, MONTH, SERIAL, PERNUM), household-link flags, entry_hours, and
reservation_wage_{lower,central,upper} (reservation_wage aliases the central column).
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_PROJECT = _cfg_mod.PATH_PROJECT
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED

# 02b supplies the schedule readers (_resolve_schedule/_ni_adjusted) and the saturating
# response form — the SAME machinery the fiscal-cost side uses, per ST-1's consistency fix.
_b_spec = importlib.util.spec_from_file_location(
    "mod_02b", _CODE / "02_descriptive_analysis" / "02b_behavioral_scenarios.py")
_b = importlib.util.module_from_spec(_b_spec)
_b_spec.loader.exec_module(_b)

SUBSIDY_PCT = float(cfg.get("ws_subsidy_pct", 0.80))
FED_MIN = float(cfg.get("ws_base_wage", 7.25))
CAP_HOURS = float(cfg.get("ws_subsidy_hours_cap", 40)) * 52.0
_SAT_EXT = float(cfg.get("behavioral", {}).get("saturation", {}).get("ceiling_ext", 1.5))
# g_net guards near benefit cliffs: floor on the net return to work (annual $) and cap on the
# proportional net gain. Rows hitting either are counted and printed (methodology doc #3.3).
_GNET_DENOM_FLOOR = 1000.0
_GNET_CAP = 3.0

# Diagnostics accumulator (H1, output-hygiene assessment 2026-07-08): the Heckman +
# reservation-band calibration audit trail was previously only printed to stdout. Functions
# populate this dict; main() persists it to nonemployed_pool_diagnostics.json alongside the pool.
DIAG: dict = {}

# MPL-imputation selector (MR-001, methodology review 2026-07-08). The Heckman prediction has no
# bulletproof exclusion restriction, so the correction is identified off the IMR's functional
# form. To bound that fragility, the pool can be built under any of the three imputations the
# two-step produces; 02f_mpl_imputation_band.py runs all three and reports the entry/cost spread.
# Default "conditional" (the D=0 selection-consistent prediction) is the headline and leaves the
# canonical nonemployed_pool.parquet byte-identical; other variants write suffixed pool files.
_IMPUTATION = os.environ.get("EIG_MPL_IMPUTATION", "conditional")
_IMPUTATION_LABEL = {"conditional": "conditional Mills (D=0)", "mills0": "Mills=0 (unconditional)",
                     "plain": "plain OLS (no IMR)"}.get(_IMPUTATION, _IMPUTATION)
# Non-employment wage-offer penalty (E2 follow-on, reality assessment 2026-07-09). On the clean
# paid-hourly frame the selection correction is small (rho*sigma ~ +0.08) and weakly identified
# (no clean exclusion restriction), so unobserved wage penalties of the long-non-employed are
# largely undetectable from the cross-section. External evidence supports a real penalty:
# Schmieder-von Wachter-Bender (2016) measure ~0.8%/month causal wage-offer decay; Krueger-
# Mueller (2016) unemployed accept at ~0.90x prior wages. EIG_MPL_PENALTY applies a uniform
# disclosed haircut to the pool's imputed MPL (duration heterogeneity unmodeled — disclosed);
# 02f runs the {0, 0.10, 0.20} band. Default 0 (the headline is the frame estimate).
_MPL_PENALTY = float(os.environ.get("EIG_MPL_PENALTY", "0"))
# Offer-dispersion scale (2026-07-09): lambda x group residual SD of mean-preserving lognormal
# spread around each person's conditional-mean imputation. See cfg["matching"]["offer_dispersion"]
# for rationale. Headline default = lambda_central (0.75); 02f runs the {0.50, 1.00} band.
_OFFER_LAMBDA = float(os.environ.get(
    "EIG_MPL_LAMBDA", str(cfg["matching"].get("offer_dispersion", {}).get("lambda_central", 0.75))))
# MR-001 (full-review 2026-07-09): SURVEY-WEIGHTED estimation is now PRIMARY. The selection probit
# is weighted by WTFINL (population participation) and the wage OLS by EARNWT (the ORG earnings
# weight), matching the project's weight convention (PROJECT.md: EARNWT for earner wages, WTFINL for
# the non-employed) and the dataset registry (MR-VU2). Unweighted estimation is retained as a
# robustness (EIG_HECKMAN_WEIGHTS=unweighted → suffixed pool): it targets the SAME conditional-mean
# E[log w | X] the imputation uses, where unweighted OLS/probit is consistent and more efficient
# (Solon, Haider & Wooldridge 2015), so the two should agree closely — the primary run prints the
# unweighted-vs-weighted conditional pool median as a robustness diagnostic.
_HECKMAN_WEIGHTS = os.environ.get("EIG_HECKMAN_WEIGHTS", "weighted")
_WEIGHTED_HECKMAN = _HECKMAN_WEIGHTS != "unweighted"
_POOL_SUFFIX = "" if _IMPUTATION == "conditional" else f"__{_IMPUTATION}"
if not _WEIGHTED_HECKMAN:
    _POOL_SUFFIX += "__unwtd"
if _MPL_PENALTY > 0:
    _POOL_SUFFIX += f"__pen{int(round(_MPL_PENALTY * 100))}"
if os.environ.get("EIG_MPL_STATUS_PENALTY", ""):
    _POOL_SUFFIX += "__skewstat" + os.environ.get("EIG_POOL_TAG", "")
if abs(_OFFER_LAMBDA - float(cfg["matching"].get("offer_dispersion", {}).get("lambda_central", 0.75))) > 1e-9:
    _POOL_SUFFIX += f"__lam{int(round(_OFFER_LAMBDA * 100))}"


def _load_target_wage() -> float:
    p = PATH_DATA_PROCESSED / "org_target_wage.json"
    if p.exists():
        try:
            return float(json.loads(p.read_text())["target_wage"])
        except Exception:  # noqa: BLE001
            pass
    return float(cfg.get("ws_target_wage", 16.80))


TARGET_WAGE = _load_target_wage()
_EMPLOYED_EMPSTAT = {10, 12}
_ORG_MISH = {4, 8}

# Finer 8-bucket education (M3) — all 16 IPUMS EDUC codes are loaded in the raw partitions.
_EDUC_FINE_MAP = {
    1: "primary_or_less", 2: "primary_or_less", 10: "primary_or_less", 20: "primary_or_less",
    30: "primary_or_less",
    40: "some_hs", 50: "some_hs", 60: "some_hs", 71: "some_hs",
    73: "hs_grad",
    81: "some_college",
    91: "assoc", 92: "assoc",
    111: "ba",
    123: "ma", 124: "prof_phd", 125: "prof_phd",
}
_EDUC_FINE_DUMMIES = ["some_hs", "hs_grad", "some_college", "assoc", "ba", "ma", "prof_phd"]
# Coarse groups retained for cell assignment / output compatibility.
_EDUC_MAP = {
    1: "Less than HS", 2: "Less than HS", 10: "Less than HS", 20: "Less than HS",
    30: "Less than HS", 40: "Less than HS", 50: "Less than HS", 60: "Less than HS",
    71: "HS diploma / GED", 73: "HS diploma / GED",
    81: "Some college / Associate's", 91: "Some college / Associate's", 92: "Some college / Associate's",
    111: "Bachelor's degree", 123: "Graduate degree", 124: "Graduate degree", 125: "Graduate degree",
}
_FIPS = {1:"AL",2:"AK",4:"AZ",5:"AR",6:"CA",8:"CO",9:"CT",10:"DE",11:"DC",12:"FL",13:"GA",15:"HI",
    16:"ID",17:"IL",18:"IN",19:"IA",20:"KS",21:"KY",22:"LA",23:"ME",24:"MD",25:"MA",26:"MI",27:"MN",
    28:"MS",29:"MO",30:"MT",31:"NE",32:"NV",33:"NH",34:"NJ",35:"NM",36:"NY",37:"NC",38:"ND",39:"OH",
    40:"OK",41:"OR",42:"PA",44:"RI",45:"SC",46:"SD",47:"TN",48:"TX",49:"UT",50:"VT",51:"VA",53:"WA",
    54:"WV",55:"WI",56:"WY"}
_STATE_REF = "CA"   # reference state dummy (largest sample)


def _find_raw_org_dir() -> Path | None:
    env = os.environ.get("EIG_ORG_RAW_DIR", "")
    cands = ([Path(env)] if env else []) + [
        PATH_PROJECT / "data" / "raw" / "cps_org",
        PATH_PROJECT.parent / "EIG-Wage-Figure-Explain-Everything" / "data" / "raw" / "cps_org"]
    for c in cands:
        if c.is_dir() and list(c.glob("year=*/part-0.parquet")):
            return c
    return None


def _col(df, *names):
    for n in names:
        if n in df.columns:
            return df[n]
    return None


def _employed_hourly_wage(df: pd.DataFrame) -> np.ndarray:
    """Hourly wage for employed earners, IPUMS sentinels stripped (unchanged from pre-remodel)."""
    n = len(df)
    hw = _col(df, "HOURWAGE_CANON_NUM", "HOURWAGE")
    ew = _col(df, "EARNWEEK_CANON_NUM", "EARNWEEK")
    h1 = _col(df, "UHRSWORK1"); ho = _col(df, "UHRSWORKORG"); paid = _col(df, "PAIDHOUR")
    yr = _col(df, "YEAR"); mo = _col(df, "MONTH")
    hw = np.asarray(hw, float) if hw is not None else np.full(n, np.nan)
    ew = np.asarray(ew, float) if ew is not None else np.full(n, np.nan)
    hrs = np.asarray(h1, float) if h1 is not None else np.full(n, np.nan)
    if ho is not None:
        hrs = np.where(np.isnan(hrs), np.asarray(ho, float), hrs)
    hrs = np.where((hrs >= 997) | (hrs <= 0), np.nan, hrs)
    hw = np.where(hw >= 999.99, np.nan, hw)
    yr = np.asarray(yr, float) if yr is not None else np.full(n, 2025.0)
    mo = np.asarray(mo, float) if mo is not None else np.full(n, 6.0)
    star2 = (yr > 2023) | ((yr == 2023) & (mo >= 4))
    ew = np.where(ew >= np.where(star2, 999999.99, 9999.99), np.nan, ew)
    paid = np.asarray(paid, float) if paid is not None else np.full(n, 2.0)
    wage = np.where(paid == 2, hw, np.divide(ew, hrs, out=np.full(n, np.nan), where=hrs > 0))
    return np.where(wage > 0, wage, np.nan)


def _age_bin(a):
    a = int(a)
    return "16-24" if a < 25 else "25-34" if a < 35 else "35-44" if a < 45 else "45-54" if a < 55 else "55-64"


def _family_key(marst, nchild):
    prefix = "married" if int(marst) in {1, 2} else "single"
    return f"{prefix}_{'2c' if int(nchild) >= 1 else '0c'}"


def _assign_matching_cell(sex_label, family_type_key):
    if sex_label == "Male":
        return "men"
    return "single_mothers" if family_type_key == "single_2c" else "other_women"


def _design(df: pd.DataFrame, wage_eq: bool) -> pd.DataFrame:
    """Design matrix. Wage equation: age, age^2, fine education, sex, race/ethnicity, state.
    Selection equation additionally includes the household participation shifters:
    married, nchild, has_child (pre-existing), spouse-employed x married, own child under 5.
    DISCLOSED (methodology doc #3.7): these are conventional Mroz-lineage shifters, not clean
    instruments — each has a documented potential direct wage association."""
    age = df["AGE"].to_numpy(float)
    race = df["RACE"].to_numpy(float); hisp = df["HISPAN"].to_numpy(float)
    cols = {"const": np.ones(len(df)), "age": age, "age2": age ** 2 / 100.0}
    fine = df["educ_fine"].to_numpy()
    for e in _EDUC_FINE_DUMMIES:
        cols[f"educ[{e}]"] = (fine == e).astype(float)
    cols["male"] = (df["sex_label"].to_numpy() == "Male").astype(float)
    cols["black"] = (race == 200).astype(float)
    cols["other_race"] = (~np.isin(race, [100, 200])).astype(float)
    cols["hispanic"] = (hisp > 0).astype(float)
    st = df["state_code"].to_numpy()
    for s in sorted(set(_FIPS.values())):
        if s != _STATE_REF:
            cols[f"st[{s}]"] = (st == s).astype(float)
    if not wage_eq:
        cols["married"] = df["MARST"].isin([1, 2]).to_numpy().astype(float)
        cols["nchild"] = df["NCHILD"].to_numpy(float)
        cols["has_child"] = (df["NCHILD"].to_numpy(float) >= 1).astype(float)
        cols["spouse_employed_married"] = (
            df["spouse_is_employed"].to_numpy(bool) & df["MARST"].isin([1, 2]).to_numpy()
        ).astype(float)
        cols["child_under5"] = df["own_child_under5"].to_numpy(bool).astype(float)
    return pd.DataFrame(cols, index=df.index)


def heckman_impute(est: pd.DataFrame, pool: pd.DataFrame) -> np.ndarray:
    """Two-step Heckman with the SELECTION-CONSISTENT (D=0 conditional) pool prediction (ST-7).
    Prints the Mills=0 (unconditional), conditional, and plain-OLS imputations side by side."""
    D = est["obs_wage"].notna().to_numpy().astype(int)
    Xsel = _design(est, wage_eq=False)
    sel = D == 1
    y = np.log(est.loc[est.index[sel], "obs_wage"].to_numpy(float))
    w_sel = est["WTFINL"].to_numpy(float)                        # participation weight (probit)
    w_wage = est.loc[est.index[sel], "EARNWT"].to_numpy(float)   # ORG earnings weight (wage OLS)

    def _fit(weighted: bool) -> dict:
        """Two-step fit. weighted (MR-001 primary): probit by WTFINL (GLM-probit freq_weights),
        wage OLS/plain by EARNWT (WLS); else unweighted. Returns params, designs, smearings."""
        if weighted:
            pparams = np.asarray(sm.GLM(
                D, Xsel.to_numpy(),
                family=sm.families.Binomial(sm.families.links.Probit()),
                freq_weights=w_sel).fit().params)
        else:
            pparams = np.asarray(sm.Probit(D, Xsel.to_numpy()).fit(disp=0, maxiter=200).params)
        imr = norm.pdf(Xsel.to_numpy() @ pparams) / np.clip(norm.cdf(Xsel.to_numpy() @ pparams), 1e-8, None)
        Xw_ = _design(est.loc[est.index[sel]], wage_eq=True)
        Xw_["imr"] = imr[sel]
        if weighted:
            o = sm.WLS(y, Xw_.to_numpy(), weights=w_wage).fit()
            op = sm.WLS(y, Xw_.drop(columns="imr").to_numpy(), weights=w_wage).fit()
            sm_, smp = (float(np.average(np.exp(o.resid), weights=w_wage)),
                        float(np.average(np.exp(op.resid), weights=w_wage)))
        else:
            o = sm.OLS(y, Xw_.to_numpy()).fit()
            op = sm.OLS(y, Xw_.drop(columns="imr").to_numpy()).fit()
            sm_, smp = float(np.mean(np.exp(o.resid))), float(np.mean(np.exp(op.resid)))
        return {"pparams": pparams, "ols": o, "ols_plain": op, "Xw": Xw_,
                "smear": sm_, "smear_plain": smp}

    fit = _fit(_WEIGHTED_HECKMAN)
    probit_params = fit["pparams"]; ols = fit["ols"]; ols_plain = fit["ols_plain"]
    Xw = fit["Xw"]; smear = fit["smear"]; smear_plain = fit["smear_plain"]
    lam_coef = float(np.asarray(ols.params)[-1])         # rho*sigma (coefficient on IMR)
    _wlabel = "weighted (WTFINL probit / EARNWT wage)" if _WEIGHTED_HECKMAN else "unweighted"
    print(f"  Heckman [{_wlabel}]: probit N={len(D):,} (employed-earner share {D.mean():.2f}); "
          f"wage OLS N={sel.sum():,}; IMR coef (rho*sigma)={lam_coef:+.3f}; smearing={smear:.3f}")
    DIAG["heckman"] = {
        "weighting": _wlabel,
        "probit_N": int(len(D)), "employed_earner_share": round(float(D.mean()), 4),
        "wage_ols_N": int(sel.sum()), "imr_coef_rho_sigma": round(lam_coef, 4),
        "smearing": round(smear, 4),
    }

    # Pool predictions.
    Xwp = _design(pool, wage_eq=True)
    Xwp["imr"] = 0.0
    xb = Xwp[Xw.columns].to_numpy() @ np.asarray(ols.params)   # unconditional E[log w | X]
    Xselp = _design(pool, wage_eq=False)
    lp_pool = Xselp.to_numpy() @ probit_params
    lam0 = -norm.pdf(lp_pool) / np.clip(1.0 - norm.cdf(lp_pool), 1e-8, None)   # < 0
    xb_cond = xb + lam_coef * lam0                        # E[log w | X, D=0] (ST-7)
    # Puhani sensitivity: plain OLS on employed (no IMR) predicted at pool X.
    xb_plain = Xwp[Xw.columns].drop(columns="imr").to_numpy() @ np.asarray(ols_plain.params)

    # MR-001 robustness (SHW 2015): the unweighted fit targets the SAME conditional mean, so its
    # pre-dispersion pool median should track the weighted one closely. Printed + persisted.
    if _WEIGHTED_HECKMAN:
        try:
            rf = _fit(False)
            xb_u = Xwp[rf["Xw"].columns].to_numpy() @ np.asarray(rf["ols"].params)
            lp_u = Xselp.to_numpy() @ rf["pparams"]
            lam0_u = -norm.pdf(lp_u) / np.clip(1.0 - norm.cdf(lp_u), 1e-8, None)
            med_u = float(np.percentile(np.maximum(
                FED_MIN, np.exp(xb_u + float(np.asarray(rf["ols"].params)[-1]) * lam0_u) * rf["smear"]), 50))
            med_w = float(np.percentile(np.maximum(FED_MIN, np.exp(xb_cond) * smear), 50))
            print(f"  MR-001 robustness: conditional pool median (pre-dispersion) "
                  f"weighted ${med_w:.2f} vs unweighted ${med_u:.2f}")
            DIAG["heckman_robustness_unweighted"] = {
                "conditional_median_weighted": round(med_w, 2),
                "conditional_median_unweighted": round(med_u, 2)}
        except Exception as e:  # noqa: BLE001
            print(f"  [warn] MR-001 unweighted robustness fit failed: {e}")

    # ── Offer dispersion (2026-07-09): mean-preserving lognormal spread around the
    # conditional mean, with GROUP-SPECIFIC residual SDs (education x age; dispersion rises
    # with both) and a hash-quantile draw salted independently of the entry lottery. Mean
    # imputation alone makes reachability a deterministic cliff at the conditional mean —
    # every demographic cell in reality has mass on both sides of the target.
    resid_df = pd.DataFrame({
        "ef": est.loc[est.index[sel], "educ_fine"].to_numpy(),
        "ag": pd.cut(est.loc[est.index[sel], "AGE"].to_numpy(),
                     [15, 24, 39, 64], labels=["16-24", "25-39", "40-64"]),
        "r": ols.resid})
    sd_all = float(ols.resid.std())
    sd_grp = resid_df.groupby(["ef", "ag"], observed=True)["r"].agg(["std", "size"])
    sd_map = {k: (float(v["std"]) if v["size"] >= 100 else sd_all) for k, v in sd_grp.iterrows()}
    pool_ag = pd.cut(pool["AGE"].to_numpy(), [15, 24, 39, 64], labels=["16-24", "25-39", "40-64"])
    sigma_g = np.array([sd_map.get((ef, ag), sd_all)
                        for ef, ag in zip(pool["educ_fine"].to_numpy(), pool_ag)])
    ids = pool[["YEAR", "MONTH", "SERIAL", "PERNUM"]].astype(np.int64).copy()
    ids["_salt"] = "wage_draw"                                     # independent of entry-lottery hash
    h = pd.util.hash_pandas_object(ids, index=False).to_numpy()
    u_wage = (pd.Series(h).rank(method="first").to_numpy() - 0.5) / len(h)
    ls = _OFFER_LAMBDA * sigma_g
    spread = np.exp(ls * norm.ppf(u_wage) - 0.5 * ls ** 2)         # E[spread] = 1 (mean-preserving)
    DIAG["offer_dispersion"] = {
        "lambda": _OFFER_LAMBDA, "sd_overall": round(sd_all, 3),
        "sd_group_min_max": [round(min(sd_map.values()), 3), round(max(sd_map.values()), 3)],
        "n_groups": len(sd_map)}

    mpl_uncond = np.maximum(FED_MIN, np.exp(xb) * smear * spread)
    mpl_cond = np.maximum(FED_MIN, np.exp(xb_cond) * smear * spread)
    mpl_plain = np.maximum(FED_MIN, np.exp(xb_plain) * smear_plain * spread)
    q = lambda v: "/".join(f"{np.percentile(v, p):.2f}" for p in (25, 50, 75))
    print(f"  Offer dispersion: lambda={_OFFER_LAMBDA} x group sd (range "
          f"{min(sd_map.values()):.2f}-{max(sd_map.values()):.2f}, {len(sd_map)} educ-x-age groups)")
    print(f"  Pool MPL p25/p50/p75 — conditional (USED): {q(mpl_cond)} | "
          f"Mills=0: {q(mpl_uncond)} | plain OLS: {q(mpl_plain)}")
    pcts = lambda v: {p: round(float(np.percentile(v, p)), 2) for p in (25, 50, 75)}
    DIAG["pool_mpl_unweighted_pctiles"] = {
        "conditional_used": pcts(mpl_cond), "mills0_preremodel": pcts(mpl_uncond),
        "plain_ols": pcts(mpl_plain),
    }
    # MR-001: return the selected imputation (default conditional). See _IMPUTATION.
    # Also return the pool's selection-probit propensity Phi(Xg) — reused by the E1
    # status-aware entry lottery in assign_reservation_band.
    propensity = norm.cdf(lp_pool)
    mpl_sel = {"conditional": mpl_cond, "mills0": mpl_uncond, "plain": mpl_plain}[_IMPUTATION]
    return mpl_sel, propensity


def _cellmedian_fallback(est: pd.DataFrame, pool: pd.DataFrame) -> np.ndarray:
    """Fallback if Heckman fails: employed cell-median x (1 - 0.10 discount)."""
    emp = est[est["obs_wage"].notna()]
    def wmed(v, w):
        v = np.asarray(v, float); w = np.asarray(w, float); ok = ~np.isnan(v) & (w > 0)
        if ok.sum() == 0: return np.nan
        v, w = v[ok], w[ok]; i = np.argsort(v); cw = np.cumsum(w[i]); return float(v[i][np.searchsorted(cw, cw[-1]*0.5)])
    cell = {f"{s}|{e}|{a}": wmed(g["obs_wage"], g["EARNWT"]) for (s, e, a), g in
            emp.groupby(["sex_label", "educ_group", "age_bin"])}
    sexm = {s: wmed(g["obs_wage"], g["EARNWT"]) for s, g in emp.groupby("sex_label")}
    overall = wmed(emp["obs_wage"], emp["EARNWT"])
    def _first_finite(*vals):
        for v in vals:
            if v is not None and np.isfinite(v):     # NaN is truthy; `or` chains cannot fall back (CE-003)
                return v
        return np.nan
    out = np.array([_first_finite(cell.get(f"{s}|{e}|{a}"), sexm.get(s), overall)
                    for s, e, a in zip(pool["sex_label"], pool["educ_group"], pool["age_bin"])], float)
    return np.maximum(FED_MIN, out * 0.90)


def _entry_hours(nonemp: pd.DataFrame, mpl: np.ndarray) -> np.ndarray:
    """M7: quantile-matched entrant hours. MPL percentile within cell -> same percentile of
    incumbent annual hours within cell (hourly_workers.parquet). Falls back to 2,000 for a
    cell absent from the incumbent file."""
    hw_path = PATH_DATA_PROCESSED / "hourly_workers.parquet"
    default = float(cfg.get("ws_hours_per_year", 2000))
    hours = np.full(len(nonemp), default)
    if not hw_path.exists():
        print("  [warn] hourly_workers.parquet missing — entry hours fixed at default.")
        return hours
    inc = pd.read_parquet(hw_path)
    inc_cells = _b.assign_cell(inc)
    cells = nonemp["mcell"].to_numpy()
    for c in ("single_mothers", "other_women", "men"):
        pidx = np.where(cells == c)[0]
        ih = np.sort(inc.loc[inc_cells == c, "annual_hours"].to_numpy(float))
        if len(pidx) == 0 or len(ih) == 0:
            continue
        ranks = pd.Series(mpl[pidx]).rank(method="average", pct=True).to_numpy()
        hours[pidx] = np.quantile(ih, np.clip(ranks, 0.0, 1.0))
    return hours


def _eligible_stock_by_cell() -> dict:
    """Weighted eligible EMPLOYED workers per cell (hourly_workers.parquet) — the base the
    participation elasticities were estimated against (employment-rate semantics). Used by the
    employment-stock calibration variant."""
    hw_path = PATH_DATA_PROCESSED / "hourly_workers.parquet"
    if not hw_path.exists():
        return {}
    inc = pd.read_parquet(hw_path)
    inc_cells = _b.assign_cell(inc)
    return {c: float(inc.loc[inc_cells == c, "weight"].sum())
            for c in ("single_mothers", "other_women", "men")}


class _NetIncome:
    """Vectorized NI() over a fixed set of rows, with (family_type_key, state) group positions
    and schedules resolved once. NI includes means-tested transfers at zero earnings and the
    ACA-PTC/Medicaid add-backs (02b._ni_adjusted); the subsidy passes through as ordinary
    taxable/countable income (user decision 2026-07-08 — methodology doc #4)."""

    def __init__(self, fkey: np.ndarray, state: np.ndarray):
        self.n = len(fkey)
        key = pd.DataFrame({"f": fkey, "s": state})
        self.groups = []
        for (fk, st), idx in key.groupby(["f", "s"]).groups.items():
            sch = _b._resolve_schedule(fk, st)
            pos = key.index.get_indexer(idx)
            if sch is not None:
                self.groups.append((sch, pos))

    def __call__(self, income: np.ndarray) -> np.ndarray:
        out = np.zeros(self.n, float)
        for sch, pos in self.groups:
            out[pos] = _b._ni_adjusted(sch, income[pos])
        return out


def assign_reservation_band(nonemp: pd.DataFrame, mpl: np.ndarray, hours: np.ndarray,
                            propensity: np.ndarray | None = None,
                            elig_stock: dict | None = None,
                            n_months: int = 1) -> pd.DataFrame:
    """Per-cell, per-band-edge lambda-bisection on the NET, SATURATING, PERSON-LEVEL criterion.

    The reservation requirement lives in NET-GAIN space: person i works iff the net gain of the
    offered package clears (1+m_i) times the net gain their own unsubsidized MPL would deliver,
        NI(package) - NI(0)  >=  (1+m_i) * max(NI(y*h) - NI(0), floor),
    with m_i ~ Exponential(lambda_c_edge). This is the monotone-in-m form of the net criterion:
    the naive gross-reservation form NI(package) >= NI(r*h) is NON-monotone in m because NI()
    has benefit-cliff troughs (ST-4) — empirically it put a hard FLOOR on the viable share
    (single_mothers ~0.44 at any lambda), making calibration infeasible. In net-gain space the
    condition collapses to  m_i <= g_net_i  where
        g_net_i = [NI(package) - NI(y*h)] / max(NI(y*h) - NI(0), floor)
    is ALSO the net stimulus (ST-2) — the net analog of the old gross closed form (m <= g).
    Design change vs the rev2 plan text, documented in the methodology doc #3 and session log.

    u_i is a HASH-of-person-ID rank (independent of file order; ST-10), shared across the three
    edges (common random numbers -> nested viable sets, pointwise-monotone reservation columns).
    """
    T = TARGET_WAGE
    band = cfg["matching"]["eps_ext_band"]
    edges = ("lower", "central", "upper")
    y = np.asarray(mpl, float)
    h = np.asarray(hours, float)
    wt = nonemp["WTFINL"].to_numpy(float)
    cells = nonemp["mcell"].to_numpy()

    # Package/base/zero net incomes (person-level, schedule-keyed) — computed once.
    ni = _NetIncome(nonemp["family_type_key"].to_numpy(), nonemp["state_code"].to_numpy())
    s_hr = SUBSIDY_PCT * np.maximum(0.0, T - y)
    package_inc = y * h + s_hr * np.minimum(h, CAP_HOURS)
    ni_package = ni(package_inc)
    ni_base = ni(y * h)
    ni_zero = ni(np.zeros(len(y)))

    # Net stimulus == net viability headroom: g_net = m_max (see docstring).
    net_gain_base = np.maximum(ni_base - ni_zero, _GNET_DENOM_FLOOR)
    n_floor = int((ni_base - ni_zero < _GNET_DENOM_FLOOR).sum())
    g_net = (ni_package - ni_base) / net_gain_base
    n_cap = int((g_net > _GNET_CAP).sum())
    g_net = np.clip(g_net, 0.0, _GNET_CAP)
    print(f"  g_net: net-return-to-work denom < ${_GNET_DENOM_FLOOR:.0f} floored: "
          f"{n_floor:,} rows | capped at {_GNET_CAP}: {n_cap:,} rows")
    DIAG["g_net_guards"] = {"denom_floor": _GNET_DENOM_FLOOR, "n_floored": int(n_floor),
                            "cap": _GNET_CAP, "n_capped": int(n_cap)}
    DIAG["calibration"] = {}

    # Hash-ranked u (ST-10): stable person-ID hash -> within-(cell, reachable) rank in (0,1).
    ids = nonemp[["YEAR", "MONTH", "SERIAL", "PERNUM"]].astype(np.int64)
    hsh = pd.util.hash_pandas_object(ids, index=False).to_numpy()

    m_edge = {e: np.full(len(nonemp), 100.0) for e in (*edges, "estock")}   # non-reachable: never viable
    for c in ("single_mothers", "other_women", "men"):
        idx = np.where(cells == c)[0]
        if len(idx) == 0:
            continue
        gross_gap = SUBSIDY_PCT * np.maximum(0.0, T - y[idx]) / np.maximum(y[idx], 1e-9)
        reach = gross_gap > 1e-9
        if reach.sum() == 0 or wt[idx][reach].sum() == 0:
            continue
        ridx = idx[reach]
        u = (pd.Series(hsh[ridx]).rank(method="first").to_numpy() - 0.5) / len(ridx)
        wr = wt[ridx]
        gr = g_net[ridx]
        # E1 (reality assessment 2026-07-09): status-aware entry lottery. The per-person markup
        # becomes m_i = -ln(1-u_i)/(lambda_c * s_i), where s_i = status_weight x probit
        # propensity, normalized to weighted mean 1 over (cell x reachable) so the cell-level
        # calibration target is unaffected. Entry probability then scales with s_i: active
        # job-seekers (weight 5.0) are ~33x more likely to be the marginal entrant than a
        # disabled or retired person (0.15), fixing the hash-uniform composition artifact
        # (68% of entrants aged 16-24; unemployed at 9.4%).
        sw = cfg["matching"].get("entry_status_weights", {})
        status_r = nonemp["prior_status"].to_numpy()[ridx]
        w_status = np.array([float(sw.get(s, 1.0)) for s in status_r])
        prop_r = (np.asarray(propensity, float)[idx][reach]
                  if propensity is not None else np.ones(len(ridx)))
        s_i = w_status * np.clip(prop_r, 1e-4, None)
        s_i = s_i / np.average(s_i, weights=wr)                     # mean-1 normalization
        print(f"  {c}: reachable {len(ridx):,} | median g_net {np.median(gr):.3f} | "
              f"propensity-score s: p10/p50/p90 = "
              f"{np.percentile(s_i,10):.2f}/{np.percentile(s_i,50):.2f}/{np.percentile(s_i,90):.2f}")
        DIAG["calibration"][c] = {"reachable_N": int(len(ridx)),
                                  "median_g_net": round(float(np.median(gr)), 4),
                                  "status_score_p10_p50_p90": [round(float(np.percentile(s_i, p)), 3)
                                                               for p in (10, 50, 90)],
                                  "edges": {}}
        # Base-semantics wedge (2026-07-09, user question): the literature's participation
        # elasticities are EMPLOYMENT-RATE semantics — their natural count base is the
        # affected group's eligible EMPLOYED stock E_c, not the reachable non-employed pool
        # R_c this calibration uses. The "estock" variant below recalibrates the central
        # edge on target_share x (E_c / R_c) (feasibility-capped), reported as a
        # sensitivity row alongside the pool-share headline.
        E_c = float(elig_stock.get(c, 0.0)) if elig_stock else 0.0
        # wr is raw WTFINL (person-months); divide by n_months to match hourly_workers'
        # month-averaged weights so E/R compares stocks on the same basis.
        R_c = float(wr.sum()) / max(n_months, 1)
        er_ratio = (E_c / R_c) if R_c > 0 else 0.0
        DIAG["calibration"][c]["base_semantics"] = {
            "eligible_employed_stock_M": round(E_c / 1e6, 2),
            "reachable_pool_M": round(R_c / 1e6, 2), "E_over_R": round(er_ratio, 3)}

        def _solve(target: float) -> np.ndarray:
            if target <= 0:
                lam = 1e-6
            else:
                lo, hi = 1e-6, 1e6
                for _ in range(60):
                    mid = np.sqrt(lo * hi)
                    frac = float(np.average(
                        (u <= 1.0 - np.exp(-mid * s_i * gr)).astype(float), weights=wr))
                    lo, hi = (mid, hi) if frac < target else (lo, mid)
                lam = np.sqrt(lo * hi)
            return -np.log(1.0 - u) / (lam * s_i)

        for e in edges:
            eps = float(band[e][c])
            # ST-11: saturated, person-level target (same response form as 02b).
            target = min(0.90, float(np.average(
                _b.response_multiplier(eps, gr, _SAT_EXT) - 1.0, weights=wr)))
            m_edge[e][ridx] = _solve(target)
            realized = float(np.average((m_edge[e][ridx] <= gr).astype(float), weights=wr))
            print(f"    {c}/{e}: eps={eps:.2f} target={target:.4f} realized={realized:.4f}")
            DIAG["calibration"][c]["edges"][e] = {
                "eps": eps, "target_share": round(target, 4), "realized_share": round(realized, 4)}
            if e == "central" and er_ratio > 0:
                t_es = min(0.90, target * er_ratio)
                m_edge["estock"][ridx] = _solve(t_es)
                r_es = float(np.average((m_edge["estock"][ridx] <= gr).astype(float), weights=wr))
                print(f"    {c}/estock: target={t_es:.4f} realized={r_es:.4f} (E/R={er_ratio:.2f})")
                DIAG["calibration"][c]["edges"]["estock"] = {
                    "eps": eps, "target_share": round(t_es, 4), "realized_share": round(r_es, 4)}

    out = pd.DataFrame(index=nonemp.index)
    for e in (*edges, "estock"):
        out[f"reservation_wage_{e}"] = y * (1.0 + m_edge[e])        # descriptive gross-equivalent
        out[f"required_net_gain_{e}"] = (1.0 + m_edge[e]) * net_gain_base   # 02d's gate contract
    out["g_net"] = g_net
    out["ni_zero"] = ni_zero
    out["net_gain_base"] = net_gain_base
    # Nested-set / pointwise-monotonicity assertion (guaranteed under shared u; a violation
    # is a bug, not a modeling outcome — see stress-test memo Q3a).
    assert (out["reservation_wage_lower"] >= out["reservation_wage_central"] - 1e-9).all()
    assert (out["reservation_wage_central"] >= out["reservation_wage_upper"] - 1e-9).all()
    return out


def main() -> None:
    raw_dir = _find_raw_org_dir()
    if raw_dir is None:
        print("01h | Raw ORG partitions not found (EIG-Wage-Figure .../data/raw/cps_org or "
              "EIG_ORG_RAW_DIR). 02d will use its synthetic pool.")
        return
    parts = sorted(raw_dir.glob("year=*/part-0.parquet"))[-2:]
    org = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    print(f"01h | Read {len(org):,} raw ORG rows from {raw_dir} ({[p.parent.name for p in parts]})")
    for req in ("AGE", "SEX", "EDUC", "MARST", "NCHILD", "EMPSTAT", "STATEFIP", "WTFINL",
                "EARNWT", "MISH", "RACE", "HISPAN", "SERIAL", "PERNUM"):
        if req not in org.columns:
            print(f"01h | [warn] raw partitions missing {req} — cannot build pool. Aborting."); return

    org = org[(org["AGE"] >= 16) & (org["AGE"] <= 64)].copy()
    org["sex_label"] = np.where(org["SEX"].astype(int) == 1, "Male", "Female")
    org["educ_group"] = org["EDUC"].apply(lambda c: _EDUC_MAP.get(int(c), "Less than HS"))
    org["educ_fine"] = org["EDUC"].apply(lambda c: _EDUC_FINE_MAP.get(int(c), "primary_or_less"))
    org["age_bin"] = org["AGE"].apply(_age_bin)
    org["family_type_key"] = [_family_key(m, n) for m, n in zip(org["MARST"], org["NCHILD"])]
    org["mcell"] = [_assign_matching_cell(s, f) for s, f in zip(org["sex_label"], org["family_type_key"])]
    org["state_code"] = org["STATEFIP"].map(_FIPS).fillna("TX")
    org["hwage"] = _employed_hourly_wage(org)
    org["is_employed"] = org["EMPSTAT"].astype(int).isin(_EMPLOYED_EMPSTAT)
    # E2 (reality assessment 2026-07-09): the wage-equation FRAME is the PAID-HOURLY labor
    # market — the market the $16.80 target prices and the one entrants would join. The prior
    # frame (all employed earners incl. salaried, median $26.00 vs paid-hourly $21.00) imputed
    # non-workers' potential wages on a salaried-inflated scale, contaminating the MR-001
    # band's "conservative" edges. obs_wage is therefore set only for PAID-HOURLY earners
    # (PAIDHOUR==2 with a valid HOURWAGE); salaried and wage-unobserved employed are DROPPED
    # from the estimation sample below (they belong to neither the D=1 wage frame nor the
    # D=0 counterfactual pool).
    paid = _col(org, "PAIDHOUR")
    org["is_paid_hourly_earner"] = (org["is_employed"] &
                                    (np.asarray(paid, float) == 2) & np.isfinite(org["hwage"]))
    org["obs_wage"] = np.where(org["is_paid_hourly_earner"], org["hwage"], np.nan)

    # Household links (01i): real spouse employment + child-under-5 shifters.
    links_path = PATH_DATA_PROCESSED / "household_links.parquet"
    if not links_path.exists():
        raise FileNotFoundError(f"{links_path} not found. Run 01i_household_links.py first.")
    links = pd.read_parquet(links_path)
    key = ["YEAR", "MONTH", "SERIAL", "PERNUM"]
    for k in key:
        org[k] = org[k].astype(np.int64)
    org = org.merge(links, on=key, how="left")
    for c in ("spouse_is_employed", "own_child_under5", "hh_child_under5", "spouse_linkable"):
        org[c] = org[c].astype("boolean").fillna(False).to_numpy(bool)
    print(f"01h | Household links merged: spouse-linkable {org['spouse_linkable'].mean():.1%} "
          f"of persons | spouse employed (linkable married): "
          f"{org.loc[org['spouse_linkable'], 'spouse_is_employed'].mean():.1%}")

    # Non-employed pool: all rotations (population), valid WTFINL.
    nonemp = org[~org["is_employed"]].copy()
    n_pre = len(nonemp)
    nonemp = nonemp[nonemp["WTFINL"].notna() & (nonemp["WTFINL"] > 0)].copy()
    # Prior labor-force status (E1): drives the entry-propensity weights and the
    # entry-by-status reporting downstream.
    _es = nonemp["EMPSTAT"].astype(int)
    nonemp["prior_status"] = np.select(
        [_es.isin([20, 21, 22]), _es.eq(32), _es.eq(36)],
        ["unemployed", "disabled", "retired"], default="nilf_other")
    # Estimation sample (E2 frame): ORG rotation, non-employed OR paid-hourly earner. Employed
    # rows outside the paid-hourly wage frame (salaried; no valid hourly wage) are excluded —
    # they are neither the wage-setting population nor plausible counterfactual non-workers.
    est = org[org["MISH"].astype(int).isin(_ORG_MISH) &
              (~org["is_employed"] | org["is_paid_hourly_earner"])].copy()
    n_months = org.groupby(["YEAR", "MONTH"]).ngroups
    print(f"01h | non-employed 16-64: {len(nonemp):,} (dropped {n_pre-len(nonemp):,} bad WTFINL) | "
          f"est sample (non-employed + paid-hourly earners): {len(est):,} "
          f"({est['obs_wage'].notna().sum():,} paid-hourly earners) | months={n_months}")
    if len(nonemp) == 0:
        print("01h | [warn] no non-employed rows. 02d uses synthetic pool."); return

    try:
        mpl, propensity = heckman_impute(est, nonemp)
        method = f"Heckman selection-corrected [{_IMPUTATION_LABEL}]"
    except Exception as e:                                                # noqa: BLE001
        print(f"  [warn] Heckman failed ({e}); falling back to cell-median x0.9")
        mpl = _cellmedian_fallback(est, nonemp)
        propensity = None                                # status weights alone drive the lottery
        method = "cell-median fallback"

    if _MPL_PENALTY > 0:
        mpl = np.maximum(FED_MIN, mpl * (1.0 - _MPL_PENALTY))
        method += f" x (1-{_MPL_PENALTY:.2f}) non-employment penalty"
        DIAG["mpl_penalty"] = _MPL_PENALTY
    # Status-conditioned penalty mixture (2026-07-09, left-skew hypothesis): duration-
    # heterogeneous offer decay applied by prior labor-force status ("unemployed:0.05,
    # nilf_other:0.15,..."). A mixture of small (short-spell unemployed; KM accepted ~0.90x)
    # and large (long-detached NILF/disabled/retired; Schmieder decay compounded) penalties
    # LEFT-SKEWS the aggregate offer distribution — the evidence-grounded alternative to a
    # uniform penalty or a parametric skewness knob. Variant only (02f); not the headline.
    _sp_env = os.environ.get("EIG_MPL_STATUS_PENALTY", "")
    if _sp_env:
        sp = {k: float(v) for k, v in (kv.split(":") for kv in _sp_env.split(","))}
        pen_i = nonemp["prior_status"].map(sp).fillna(0.0).to_numpy(float)
        mpl = np.maximum(FED_MIN, mpl * (1.0 - pen_i))
        method += f" x status-penalty mixture ({_sp_env})"
        DIAG["mpl_status_penalty"] = sp
    hours = _entry_hours(nonemp, mpl)
    band = assign_reservation_band(nonemp, mpl, hours, propensity,
                                   elig_stock=_eligible_stock_by_cell(), n_months=n_months)

    out = pd.DataFrame({
        "YEAR": nonemp["YEAR"].to_numpy(), "MONTH": nonemp["MONTH"].to_numpy(),
        "SERIAL": nonemp["SERIAL"].to_numpy(), "PERNUM": nonemp["PERNUM"].to_numpy(),
        "cell": nonemp["mcell"].to_numpy(), "sex_label": nonemp["sex_label"].to_numpy(),
        "educ_group": nonemp["educ_group"].to_numpy(), "age_bin": nonemp["age_bin"].to_numpy(),
        "family_type_key": nonemp["family_type_key"].to_numpy(),
        "state_code": nonemp["state_code"].to_numpy(),
        "spouse_linkable": nonemp["spouse_linkable"].to_numpy(),
        "spouse_is_employed": nonemp["spouse_is_employed"].to_numpy(),
        "own_child_under5": nonemp["own_child_under5"].to_numpy(),
        "mpl": mpl, "entry_hours": hours, "g_net": band["g_net"].to_numpy(),
        "ni_zero": band["ni_zero"].to_numpy(), "net_gain_base": band["net_gain_base"].to_numpy(),
        "reservation_wage_lower": band["reservation_wage_lower"].to_numpy(),
        "reservation_wage_central": band["reservation_wage_central"].to_numpy(),
        "reservation_wage_upper": band["reservation_wage_upper"].to_numpy(),
        "required_net_gain_lower": band["required_net_gain_lower"].to_numpy(),
        "required_net_gain_central": band["required_net_gain_central"].to_numpy(),
        "required_net_gain_upper": band["required_net_gain_upper"].to_numpy(),
        # Base-semantics sensitivity (employment-stock calibration of the central edge).
        "reservation_wage_estock": band["reservation_wage_estock"].to_numpy(),
        "required_net_gain_estock": band["required_net_gain_estock"].to_numpy(),
        # Descriptive gross-equivalent alias only — 02d gates on required_net_gain_* (the
        # reservation_wage columns do not enter any downstream computation).
        "reservation_wage": band["reservation_wage_central"].to_numpy(),
        # UI-plausibility split flag (ST-3/PI-6): unemployed (EMPSTAT 20-22) vs NILF. NI(0)
        # omits UI for the unemployed subset; this flag lets consumers split/reweight.
        "is_unemployed": nonemp["EMPSTAT"].astype(int).isin([20, 21, 22]).to_numpy(),
        # E1: prior labor-force status (drives the entry lottery; enables entry-by-status
        # reporting in 02d) and the selection-probit employment propensity.
        "prior_status": nonemp["prior_status"].to_numpy(),
        "emp_propensity": (np.asarray(propensity, float) if propensity is not None
                           else np.full(len(nonemp), np.nan)),
        "weight": (nonemp["WTFINL"] / n_months).to_numpy(),
    })
    out_path = PATH_DATA_PROCESSED / f"nonemployed_pool{_POOL_SUFFIX}.parquet"
    out.to_parquet(out_path, index=False)
    wt = out["weight"].to_numpy()
    mp = out["mpl"].to_numpy()
    def wq(x, qq):
        i = np.argsort(x); cw = np.cumsum(wt[i]); return float(np.asarray(x)[i][np.searchsorted(cw, cw[-1]*qq)])
    pct_below = 100 * wt[mp < TARGET_WAGE].sum() / wt.sum()
    # ST-10 diagnostic: markups must not correlate with survey timing.
    m_c = out["reservation_wage_central"].to_numpy() / mp - 1.0
    reach_mask = mp < TARGET_WAGE
    month_code = (out["YEAR"].to_numpy() * 12 + out["MONTH"].to_numpy())[reach_mask]
    rho_t = float(np.corrcoef(np.minimum(m_c[reach_mask], 50), month_code)[0, 1])
    print(f"01h | Wrote {out_path} | {len(out):,} rows | pop {wt.sum()/1e6:.2f}M | MPL via {method}")
    print(f"       MPL p25/p50/p75 (weighted) = {wq(mp,.25):.2f}/{wq(mp,.5):.2f}/{wq(mp,.75):.2f} | "
          f"MPL < target ${TARGET_WAGE}: {pct_below:.1f}% | corr(markup, survey month) = {rho_t:+.3f}")
    print(f"       Plausibility check (M4): pool median should sit meaningfully below the employed "
          f"median (~$21.00 pre-remodel red flag).")

    # Persist the diagnostics audit trail (H1). See docs/entry_from_nonemployment_methodology.md.
    DIAG["summary"] = {
        "method": method, "target_wage": TARGET_WAGE, "n_rows": int(len(out)),
        "population_M": round(float(wt.sum() / 1e6), 2),
        "pool_mpl_weighted_pctiles": {25: round(wq(mp, .25), 2), 50: round(wq(mp, .5), 2),
                                      75: round(wq(mp, .75), 2)},
        "pct_mpl_below_target": round(float(pct_below), 1),
        "corr_markup_survey_month": round(rho_t, 4),
    }
    diag_path = PATH_DATA_PROCESSED / f"nonemployed_pool_diagnostics{_POOL_SUFFIX}.json"
    diag_path.write_text(json.dumps(DIAG, indent=2, sort_keys=True))
    print(f"       Diagnostics -> {diag_path}")


if __name__ == "__main__":
    main()
