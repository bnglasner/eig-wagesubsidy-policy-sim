"""
02d_matching_simulation.py — Structural search-and-matching simulation of the 80-80 subsidy.

Resolves A1.3 and replaces the band-clearing incidence model (02c, superseded). Employment is
determined by match VIABILITY and wages by NASH BARGAINING; the subsidy is added match surplus
split between worker and firm. Incidence is the bargaining share (1 - beta), bounded and micro-
founded — not an aggregate labor-demand elasticity, so wages cannot collapse to the floor.

Foundations (catalog): Mortensen-Pissarides 1994; Diamond 1982 / Pissarides 2000;
Hungerbuhler-Lehmann 2006; Hosios 1990; Shimer 2005; Rothstein 2010; Hall-Milgrom 2008;
Krueger-Mueller 2016; Flinn 2006. Spec: 2026-06-25_structural-matching-simulation.md.

Model
-----
Each worker i has marginal product y_i and reservation wage r_i. A job is viable iff surplus
S_i = y_i - r_i >= 0; the bargained wage is w_i = r_i + beta*(y_i - r_i). A per-hour subsidy
s(w) = 80% * max(0, target - w) adds to joint surplus; the firm and worker renegotiate, and the
NEW employer wage solves  w1 + (1-beta)*s(w1) = w0  (worker take-home rises by beta*s, the firm
captures (1-beta)*s via a lower cash wage). Wages are truncated at the federal minimum (Flinn).

Calibration (transported / synthetic — flagged):
  - Incumbents (observed in hourly_workers.parquet): y_i = w0_i * [rho + (1-rho)/beta] inferred
    from the bargaining identity with the observed wage; r_i = rho * w0_i (Krueger-Mueller).
  - Entrants: the cell-specific extensive response (same magnitude as 02b) placed at a LOW
    marginal product (entry_wage_percentile of the eligible wage distribution) — entrants are
    low-y by construction, so they enter at the bottom. Counterfactual = non-employment (income 0).

Output: matching_simulation.parquet (beta band) + matching_by_cell.parquet.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_APP = _HERE.parents[2] / "app"
for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

_b_spec = importlib.util.spec_from_file_location(
    "mod_02b", _CODE / "02_descriptive_analysis" / "02b_behavioral_scenarios.py")
_b = importlib.util.module_from_spec(_b_spec)
_b_spec.loader.exec_module(_b)

_OUT_DIR = PATH_OUTPUT_INTERMEDIATE / "population"
_INPUT_PATH = PATH_DATA_PROCESSED / "hourly_workers.parquet"
FED_MIN = float(cfg.get("ws_base_wage", 7.25))
SUBSIDY_PCT = float(cfg.get("ws_subsidy_pct", 0.80))
_SAT = cfg.get("behavioral", {}).get("saturation", {"ceiling_ext": 1.5})


def _recover_target(w):
    ew = w["employer_wage"].to_numpy(float); shr = w["subsidy_hr"].to_numpy(float)
    return float(np.median(ew + shr / SUBSIDY_PCT))


def renegotiated_wage(w0, beta, target):
    """Employer wage after the subsidy is bargained over. Solves w1 + (1-beta)*s(w1) = w0 with
    s(w1)=SUBSIDY_PCT*(target-w1); truncated at the minimum wage and capped at w0 (never rises)."""
    a = SUBSIDY_PCT * (1.0 - beta)
    w1 = (w0 - a * target) / (1.0 - a)          # interior solution while w1 < target
    w1 = np.minimum(w1, w0)                       # the subsidy cannot push the cash wage up
    w1 = np.maximum(w1, FED_MIN)                  # statutory floor (Flinn truncation)
    return w1


def _ni_cost(w, employer_earned, subsidy_annual, weight, cf_income):
    """Government net cost ($B) via the schedule net-income identity:
       net = [NI(employer_earned+subsidy) - NI(cf)] - (employer_earned - cf), weighted."""
    i_policy = employer_earned + subsidy_annual
    dens = np.zeros(len(w), float)
    key = pd.DataFrame({"f": w["family_type_key"].to_numpy(), "s": w["state_code"].to_numpy()}, index=w.index)
    for (fk, st), idx in key.groupby(["f", "s"]).groups.items():
        sch = _b._resolve_schedule(fk, st); pos = key.index.get_indexer(idx)
        if sch is None:
            continue
        ni_p = _b._ni_adjusted(sch, i_policy[pos])
        ni_cf = _b._ni_adjusted(sch, cf_income[pos])
        dens[pos] = (ni_p - ni_cf) - (employer_earned[pos] - cf_income[pos])
    return float((dens * weight).sum() / 1e9)


def _subsidy_annual(s_hr, subsidy_hours):
    return s_hr * subsidy_hours


def simulate(w, beta, target, rho, entry_wage, incumbent_rigid):
    """Run the matching simulation for one beta. Returns a dict of aggregates.
    incumbent_rigid: if True (Hall-Milgrom), existing matches' wages do NOT renegotiate (w1=w0),
    so firm capture falls only on new hires (entrants). If False, all matches renegotiate (Nash)."""
    w0 = w["employer_wage"].to_numpy(float)
    annual_hours = w["annual_hours"].to_numpy(float)
    baseline_income = w["baseline_income"].to_numpy(float)
    subsidy_hr0 = w["subsidy_hr"].to_numpy(float)
    subsidy_annual0 = w["subsidy_annual"].to_numpy(float)
    weight = w["weight"].to_numpy(float)
    subsidy_hours0 = np.divide(subsidy_annual0, subsidy_hr0,
                               out=np.zeros_like(subsidy_annual0), where=subsidy_hr0 > 0)
    cells = _b.assign_cell(w)

    # ---- Incumbents: sticky wage (rigid) or renegotiated (flexible Nash). ----
    w1 = w0.copy() if incumbent_rigid else renegotiated_wage(w0, beta, target)
    s_hr1 = SUBSIDY_PCT * np.maximum(0.0, target - w1)
    subsidy_annual1 = _subsidy_annual(s_hr1, subsidy_hours0)
    employer_earned1 = w1 * annual_hours
    firm_capture_bn = float(((w0 - w1) * annual_hours * weight).sum() / 1e9)  # wage-bill drop -> firm
    gross_incumbent_bn = float((subsidy_annual1 * weight).sum() / 1e9)
    net_incumbent_bn = _ni_cost(w, employer_earned1, subsidy_annual1, weight, baseline_income)

    # ---- Entrants: real ORG pool (01h) if present, else synthetic fallback. ----
    pool_path = PATH_DATA_PROCESSED / "nonemployed_pool.parquet"
    if pool_path.exists():
        pool_src = "ORG pool"
        ge, ne, fce, induced_M, ind_by_cell, detail = _entrants_from_pool(
            pd.read_parquet(pool_path), beta, target)
    else:
        pool_src = "synthetic (band central eps)"
        ge, ne, fce, induced_M, ind_by_cell, detail = _entrants_synthetic(
            w, beta, target, entry_wage, cells, weight, subsidy_hr0, w0)

    gross = gross_incumbent_bn + ge
    net = net_incumbent_bn + ne
    firm_capture = firm_capture_bn + fce
    return {
        "beta": beta,
        "entrant_source": pool_src,
        "induced_M": induced_M,
        "induced_by_cell": ind_by_cell,
        "entrant_detail": detail,
        "incumbent_wage_change_pct": round(float((((w1 - w0) / w0) * annual_hours * weight).sum()
                                                  / (annual_hours * weight).sum()) * 100, 1),
        "gross_cost_bn": round(gross, 1),
        "net_cost_bn": round(net, 1),
        "firm_capture_bn": round(firm_capture, 1),
        "firm_capture_pct_of_gross": round(firm_capture / gross * 100, 1) if gross else None,
        "entry_wage": round(float(entry_wage), 2),
    }


def _entrant_fiscal(fkey, state, i_policy, employer_earned):
    """Net fiscal density (per row) for entrants: NI(i_policy) - NI(0) - employer_earned."""
    dens = np.zeros(len(fkey), float)
    key = pd.DataFrame({"f": fkey, "s": state})
    for (fk, st), idx in key.groupby(["f", "s"]).groups.items():
        sch = _b._resolve_schedule(fk, st); pos = key.index.get_indexer(idx)
        if sch is None:
            continue
        ip = i_policy[pos] if np.ndim(i_policy) else np.full(len(pos), i_policy)
        ee = employer_earned[pos] if np.ndim(employer_earned) else np.full(len(pos), employer_earned)
        dens[pos] = (_b._ni_adjusted(sch, ip) - _b._ni_adjusted(sch, np.zeros(len(pos)))) - ee
    return dens


_PAYUP_GRID_STEPS = 9   # wage grid over [w_e, y] for the net-basis pay-up search (ST-4)


def _entrant_hours_by_mode(pool, mode: str) -> np.ndarray:
    """PI-3 sensitivity: entrant annual hours under alternative MPL→hours couplings, aligned to
    the UNfiltered pool (so it can be passed as hours_override before row filtering).
      rank        — MPL-percentile → incumbent-hours-percentile within cell (01h default; the
                    headline mapping, corr(MPL,hours) ≈ +0.9, so low-MPL entrants get low hours);
      independent — hash-quantile draw from the cell incumbent-hours distribution, UNCOUPLED from
                    MPL (salted independently; deterministic);
      median      — cell-median incumbent hours for every entrant.
    Falls back to the flat default for a cell absent from hourly_workers.parquet."""
    hw_path = PATH_DATA_PROCESSED / "hourly_workers.parquet"
    default = float(cfg.get("ws_hours_per_year", 2000))
    n = len(pool)
    hours = np.full(n, default)
    if not hw_path.exists():
        return hours
    inc = pd.read_parquet(hw_path)
    inc_cells = _b.assign_cell(inc)
    cells = pool["cell"].to_numpy()
    mpl = pool["mpl"].to_numpy(float)
    ids = pool[["YEAR", "MONTH", "SERIAL", "PERNUM"]].astype(np.int64).copy()
    ids["_salt"] = "entry_hours_indep"                       # independent of MPL and entry lottery
    hsh = pd.util.hash_pandas_object(ids, index=False).to_numpy()
    for c in ("single_mothers", "other_women", "men"):
        pidx = np.where(cells == c)[0]
        ih = np.sort(inc.loc[inc_cells == c, "annual_hours"].to_numpy(float))
        if len(pidx) == 0 or len(ih) == 0:
            continue
        if mode == "rank":
            ranks = pd.Series(mpl[pidx]).rank(method="average", pct=True).to_numpy()
            hours[pidx] = np.quantile(ih, np.clip(ranks, 0.0, 1.0))
        elif mode == "independent":
            u = (pd.Series(hsh[pidx]).rank(method="first").to_numpy() - 0.5) / len(pidx)
            hours[pidx] = np.quantile(ih, np.clip(u, 0.0, 1.0))
        elif mode == "median":
            hours[pidx] = float(np.median(ih))
        else:
            raise ValueError(f"unknown entry_hours mode: {mode}")
    return hours


def entrant_hours_sensitivity(pool, beta, target):
    """PI-3 (holistic eval 2026-07-09): the entrant-hours mapping drives the low marginal cost per
    entrant and the entry-FTE figure. The headline "rank" mapping mechanically assigns low-MPL
    entrants the fewest hours (corr ≈ +0.9). This reports entry FTE, entrant gross/net, and
    marginal $/job under all three mappings at the central edge, so the sensitivity of those
    claims to the untested coupling is visible. Fiscal TOTALS are barely affected (entrants are a
    few $B of ~$93B); the marginal-cost and FTE story is where this bites."""
    rows = []
    for mode in cfg.get("matching", {}).get("entry_hours_modes", ["rank", "independent", "median"]):
        h = _entrant_hours_by_mode(pool, mode)
        ge, ne, fce, ind, by_cell, det = _entrants_from_pool(
            pool, beta, target, edge="central", hours_override=h)
        mean_h = det.get("mean_entry_hours", 0.0)
        fte = ind * mean_h / 2000.0 if ind else 0.0
        rows.append({
            "hours_mode": mode,
            "mean_entry_hours": mean_h,
            "induced_M": ind,
            "entry_fte_M": round(fte, 2),
            "entrant_gross_bn": round(ge, 1),
            "entrant_net_bn": round(ne, 1),
            "marginal_gross_per_job": round(ge * 1e9 / (ind * 1e6), 0) if ind else None,
            "marginal_net_per_job": round(ne * 1e9 / (ind * 1e6), 0) if ind else None,
        })
    return pd.DataFrame(rows)


def _entrants_from_pool(pool, beta, target, edge="central", weight_override=None, hours_override=None):
    """Entrants = non-employed persons the subsidy makes viable on the NET criterion calibrated
    in 01h (2026-07-08 remodel):  net gain of the offered package >= required_net_gain_{edge},
    where required_net_gain = (1+m)*max(NI(y*h)-NI(0), floor).  Viability at the MAX package
    (w = y) reduces to the closed form  required <= net_gain_base*(1+g_net)  — identical to the
    calibration condition, so induced entry reproduces the calibrated target by construction.

    Wage setting: Nash-renegotiated wage w_e (firm captures (1-beta) of the subsidy on the new
    match). Because NI() has benefit cliffs, "pay up to clear the reservation" is a GRID SEARCH
    for the lowest w in [w_e, y] whose net gain clears the requirement (ST-4); a cliff
    diagnostic (rows where w_e's package failed but a higher wage cleared) is returned.
    Per-person entrant hours come from the pool's quantile-matched entry_hours (M7).
    Counterfactual = non-employment at the schedule's NI(0). weight_override supports the
    household-coordination sensitivity rows (zero/halve spouse-employed married entrants)."""
    need = ["mpl", "entry_hours", "g_net", "net_gain_base", "ni_zero",
            f"required_net_gain_{edge}", "weight"]
    pool = pool.copy()
    if weight_override is not None:
        # Positional contract: override is built against the UNfiltered pool, so it must be
        # applied before any row filtering (CE-002).
        pool["weight"] = np.asarray(weight_override, float)
    if hours_override is not None:
        # Same positional contract as weight_override — built against the UNfiltered pool (PI-3).
        pool["entry_hours"] = np.asarray(hours_override, float)
    pool = pool.dropna(subset=[c for c in need if c in pool.columns])
    pool = pool[pool["weight"] > 0]
    y = pool["mpl"].to_numpy(float)
    h = pool["entry_hours"].to_numpy(float)
    req = pool[f"required_net_gain_{edge}"].to_numpy(float)
    gnb = pool["net_gain_base"].to_numpy(float)
    gnet = pool["g_net"].to_numpy(float)
    ni_zero = pool["ni_zero"].to_numpy(float)
    wt = pool["weight"].to_numpy(float)
    cell = pool["cell"].to_numpy()
    cap_hours = float(cfg.get("ws_subsidy_hours_cap", 40)) * 52.0
    fkey = pool["family_type_key"].to_numpy(); state = pool["state_code"].to_numpy()

    viable = req <= gnb * (1.0 + gnet) * (1.0 + 1e-9)      # calibration-identical max-package gate

    def _net_gain_at(w):
        inc = w * h + SUBSIDY_PCT * np.maximum(0.0, target - w) * np.minimum(h, cap_hours)
        dens = _entrant_fiscal(fkey, state, inc, np.zeros(len(w)))   # = NI(inc) - NI(0)
        return dens, inc

    w_e = renegotiated_wage(y, beta, target)
    ng_we, _ = _net_gain_at(w_e)
    clears_at_we = ng_we >= req
    w_final = w_e.copy()
    payup = viable & ~clears_at_we
    n_payup = int(payup.sum())
    if n_payup:
        # Lowest clearing wage on a grid over [w_e, y] (monotone search invalid across cliffs).
        remaining = payup.copy()
        for t in np.linspace(0.0, 1.0, _PAYUP_GRID_STEPS)[1:]:
            if not remaining.any():
                break
            w_try = w_e + t * (y - w_e)
            ng_try, _ = _net_gain_at(np.where(remaining, w_try, w_final))
            newly = remaining & (ng_try >= req)
            w_final = np.where(newly, w_try, w_final)
            remaining = remaining & ~newly
        # Numerical safety: anything still unresolved pays the full MPL (max package).
        w_final = np.where(remaining, y, w_final)

    s_e = SUBSIDY_PCT * np.maximum(0.0, target - w_final)
    subsidy_annual_e = s_e * np.minimum(h, cap_hours)
    employer_earned_e = w_final * h
    we = wt * viable
    dens = _entrant_fiscal(fkey, state, employer_earned_e + subsidy_annual_e, employer_earned_e)
    gross = float((subsidy_annual_e * we).sum() / 1e9)
    net = float((dens * we).sum() / 1e9)
    # Entrant firm capture = the firm's ACTUAL surplus (y - w_final)*h, not (1-beta)*subsidy:
    # the two coincide only at the interior Nash wage, and most entrants are pinned at the
    # $7.25 floor (or paid up across a cliff), where (1-beta)*s overstates capture (PI-1).
    firm_capture = float((np.maximum(0.0, y - w_final) * h * we).sum() / 1e9)
    by_cell = {c: round(float(we[cell == c].sum() / 1e6), 2) for c in ("single_mothers", "other_women", "men")}
    detail = {
        "cliff_payup_entrants_M": round(float(wt[payup].sum() / 1e6), 3),
        "mean_entry_hours": round(float(np.average(h, weights=we)) if we.sum() > 0 else 0.0, 0),
    }
    # Entry by prior labor-force status (E1 reporting, reality assessment 2026-07-09).
    if "prior_status" in pool.columns:
        st = pool["prior_status"].to_numpy()
        for s in ("unemployed", "nilf_other", "disabled", "retired"):
            detail[f"entrants_{s}_M"] = round(float(we[st == s].sum() / 1e6), 3)
    return gross, net, firm_capture, round(float(we.sum() / 1e6), 2), by_cell, detail


def _entrants_synthetic(w, beta, target, entry_wage, cells, weight, subsidy_hr0, w0):
    """Fallback (no ORG pool): entrants sized from the cell extensive response, placed at the low
    entry wage; template family/state from the eligible rows. Reads the BAND's central eps
    (cfg["matching"]["eps_ext_band"]) so the entry margin cannot silently depend on a different
    config namespace than the pool path (ST-13); loudly labeled in entrant_source."""
    g_base = np.divide(subsidy_hr0, w0, out=np.zeros_like(subsidy_hr0), where=w0 > 0)
    eps_ext = np.array([float(cfg["matching"]["eps_ext_band"]["central"][c]) for c in cells])
    entrant_w = weight * (_b.response_multiplier(eps_ext, g_base, _SAT["ceiling_ext"]) - 1.0)
    ENTRY_HOURS = float(cfg.get("ws_hours_per_year", 2000))
    w_e1 = float(renegotiated_wage(np.array([float(entry_wage)]), beta, target)[0])
    s_hr_e = SUBSIDY_PCT * max(0.0, target - w_e1)
    subsidy_annual_e = s_hr_e * ENTRY_HOURS
    employer_earned_e = w_e1 * ENTRY_HOURS
    dens = _entrant_fiscal(w["family_type_key"].to_numpy(), w["state_code"].to_numpy(),
                           employer_earned_e + subsidy_annual_e, employer_earned_e)
    gross = float((subsidy_annual_e * entrant_w).sum() / 1e9)
    net = float((dens * entrant_w).sum() / 1e9)
    # Actual firm surplus at the (possibly floor-pinned) wage, mirroring _entrants_from_pool (PI-1).
    firm_capture = float((max(0.0, float(entry_wage) - w_e1) * ENTRY_HOURS * entrant_w).sum() / 1e9)
    by_cell = {c: round(float(entrant_w[cells == c].sum() / 1e6), 2) for c in ("single_mothers", "other_women", "men")}
    return gross, net, firm_capture, round(float(entrant_w.sum() / 1e6), 2), by_cell, {}


def incumbent_hours_margin(w, target):
    """E5 (reality assessment 2026-07-09): the intensive margin for eligible incumbents below
    40 hrs/wk. The 80-80 pays s(w) on every marginal hour to the 40-hr cap with NO phase-out —
    a 25-54% marginal-hour raise for low-wage part-timers — but the EITC-derived eps_int=0.05
    was estimated on designs whose plateau/phase-out suppresses exactly this incentive.
    Sensitivity over cfg["matching"]["eps_int_band"] {0.05 benchmark-floor / 0.20 central /
    0.33 Chetty-2012 consensus}: added hours via the same saturating response form as 02b
    (gross-g stimulus, 02b convention), capped at 40 hrs/wk; added government net cost via the
    schedule identity (added subsidy minus added recapture). Writes incumbent_hours_margin.parquet.
    The 02b benchmark scenario table is deliberately untouched."""
    band = cfg["matching"].get("eps_int_band", {"lower": 0.05, "central": 0.20, "upper": 0.33})
    sat_int = float(cfg.get("behavioral", {}).get("saturation", {}).get("ceiling_int", 1.4))
    w0 = w["employer_wage"].to_numpy(float)
    hrs_wk = w["hours_epi"].to_numpy(float)
    annual0 = w["annual_hours"].to_numpy(float)
    s_hr = w["subsidy_hr"].to_numpy(float)
    sub0 = w["subsidy_annual"].to_numpy(float)
    base_inc = w["baseline_income"].to_numpy(float)
    wt = w["weight"].to_numpy(float)
    weeks = np.divide(annual0, hrs_wk, out=np.full(len(w), 50.0), where=hrs_wk > 0)
    below_cap = hrs_wk < 40.0
    g = np.divide(s_hr, w0, out=np.zeros_like(s_hr), where=w0 > 0)
    rows = []
    for edge, eps in band.items():
        mult = _b.response_multiplier(float(eps), g, sat_int)
        new_wk = np.where(below_cap, np.minimum(40.0, hrs_wk * mult), hrs_wk)
        add_annual = (new_wk - hrs_wk) * weeks
        earned0 = w0 * annual0
        earned1 = w0 * (annual0 + add_annual)
        sub1 = sub0 + s_hr * add_annual            # added hours are below the 40-hr cap => subsidized
        # Government net-cost delta via the same schedule identity used for incumbents:
        net0 = _ni_cost(w, earned0, sub0, wt, base_inc)
        net1 = _ni_cost(w, earned1, sub1, wt, base_inc)
        rows.append({
            "eps_int_edge": edge, "eps_int": float(eps),
            "workers_below_cap_M": round(float(wt[below_cap].sum() / 1e6), 1),
            "added_hours_bn": round(float((add_annual * wt).sum() / 1e9), 2),
            "added_fte_M": round(float((add_annual * wt).sum() / 2000.0 / 1e6), 2),
            "added_subsidy_gross_bn": round(float(((sub1 - sub0) * wt).sum() / 1e9), 1),
            "added_net_cost_bn": round(net1 - net0, 1),
        })
    return pd.DataFrame(rows)


def main() -> None:
    mcfg = cfg.get("matching", {})
    if not mcfg.get("enabled"):
        print("02d | matching simulation disabled — skipping."); return
    if not _INPUT_PATH.exists():
        raise FileNotFoundError(f"{_INPUT_PATH} not found. Run 01a first.")
    print("02d | Loading hourly_workers.parquet …")
    w = pd.read_parquet(_INPUT_PATH)
    target = _recover_target(w)
    rho = float(mcfg["reservation_ratio"])
    pctl = float(mcfg["entry_wage_percentile"])
    entry_wage = float(np.percentile(w["employer_wage"].to_numpy(float), pctl))
    print(f"  Target ${target:.2f}/hr | reservation ratio {rho} | entry wage = p{pctl:.0f} "
          f"= ${entry_wage:.2f}/hr | beta {mcfg['beta']}")

    rows = []
    for rigid in (True, False):
        wage_mode = "rigid" if rigid else "flex"
        for tag, beta in mcfg["beta"].items():
            r = simulate(w, beta, target, rho, entry_wage, rigid)
            r = {"scenario": f"{wage_mode}-{tag}", "wage_mode": wage_mode, **r}
            rows.append(r)
            print(f"  {wage_mode:5s} {tag:8s} (beta={beta}) | +{r['induced_M']:.2f}M "
                  f"| incumbent wage {r['incumbent_wage_change_pct']:5.1f}% "
                  f"| gross ${r['gross_cost_bn']:6.1f}B | net ${r['net_cost_bn']:6.1f}B "
                  f"| firm capture {r['firm_capture_pct_of_gross']}% (${r['firm_capture_bn']:.1f}B)")
        if rigid:
            print("  " + "-" * 100)

    # Flatten per-scenario dicts into columns (H2, output-hygiene assessment 2026-07-08) so the
    # full scenario table — induced entry by cell, cliff pay-up, mean entry hours — survives to
    # disk for all six rows, not just the central-rigid case in entry_margin_band.parquet.
    def _flatten(r: dict) -> dict:
        out = {k: v for k, v in r.items() if k not in ("induced_by_cell", "entrant_detail")}
        for c, v in (r.get("induced_by_cell") or {}).items():
            out[f"induced_{c}_M"] = v
        for k, v in (r.get("entrant_detail") or {}).items():
            out[k] = v
        return out
    pd.DataFrame([_flatten(r) for r in rows]).to_parquet(
        _OUT_DIR / "matching_simulation.parquet", index=False)

    # ---- Extensive-margin band + household-coordination sensitivity (W7). ----------------
    # Isolates eps_ext scenario uncertainty at fixed beta=central, wage_mode=rigid. Only
    # meaningful on the pool path (a band re-solved via lambda has no synthetic analog).
    pool_path = PATH_DATA_PROCESSED / "nonemployed_pool.parquet"
    if pool_path.exists():
        pool = pd.read_parquet(pool_path)
        beta_c = float(mcfg["beta"]["central"])
        band_rows = []
        for edge in ("lower", "central", "upper"):
            ge, ne, fce, ind, by_cell, det = _entrants_from_pool(pool, beta_c, target, edge=edge)
            band_rows.append({"band_edge": edge, "variant": "as-modeled", "induced_M": ind,
                              **{f"induced_{k}_M": v for k, v in by_cell.items()},
                              "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1),
                              "cliff_payup_entrants_M": det["cliff_payup_entrants_M"],
                              "mean_entry_hours": det["mean_entry_hours"]})
        # Household-coordination sensitivity (Bonin channel; user decision 4, 2026-07-08):
        # zero / halve induced entry for married entrants whose linked spouse is employed.
        # A reported BOUND, not a calibrated behavior (methodology doc #5).
        sp = (pool["spouse_is_employed"].astype(bool) if "spouse_is_employed" in pool.columns
              else pd.Series(False, index=pool.index))
        for tag, factor in (("spouse-employed zeroed", 0.0), ("spouse-employed halved", 0.5)):
            wov = pool["weight"].to_numpy(float) * np.where(sp.to_numpy(), factor, 1.0)
            ge, ne, fce, ind, by_cell, det = _entrants_from_pool(
                pool, beta_c, target, edge="central", weight_override=wov)
            band_rows.append({"band_edge": "central", "variant": tag, "induced_M": ind,
                              **{f"induced_{k}_M": v for k, v in by_cell.items()},
                              "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1),
                              "cliff_payup_entrants_M": det["cliff_payup_entrants_M"],
                              "mean_entry_hours": det["mean_entry_hours"]})
        # Base-semantics sensitivity (2026-07-09, user question): the participation
        # elasticities are employment-rate semantics, so their natural count base is the
        # eligible EMPLOYED stock per cell (E_c), not the reachable non-employed pool (R_c)
        # the headline calibration uses. The "estock" reservation columns recalibrate the
        # central edge on target x (E_c/R_c); reported as a sensitivity row.
        if "required_net_gain_estock" in pool.columns:
            ge, ne, fce, ind, by_cell, det = _entrants_from_pool(pool, beta_c, target, edge="estock")
            band_rows.append({"band_edge": "central", "variant": "employment-stock semantics",
                              "induced_M": ind,
                              **{f"induced_{k}_M": v for k, v in by_cell.items()},
                              "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1),
                              "cliff_payup_entrants_M": det["cliff_payup_entrants_M"],
                              "mean_entry_hours": det["mean_entry_hours"]})
        # Take-up sensitivity (E6, reality assessment 2026-07-09): mature income-support
        # programs reach ~78-82% of eligibles (EITC ~78%, SNAP ~82%); modeled entry assumes
        # 100%. A proportional 0.80 scalar, disclosed — not a behavioral model of take-up.
        wov = pool["weight"].to_numpy(float) * 0.80
        ge, ne, fce, ind, by_cell, det = _entrants_from_pool(
            pool, beta_c, target, edge="central", weight_override=wov)
        band_rows.append({"band_edge": "central", "variant": "take-up 0.80", "induced_M": ind,
                          **{f"induced_{k}_M": v for k, v in by_cell.items()},
                          "entrant_gross_bn": round(ge, 1), "entrant_net_bn": round(ne, 1),
                          "cliff_payup_entrants_M": det["cliff_payup_entrants_M"],
                          "mean_entry_hours": det["mean_entry_hours"]})
        band_df = pd.DataFrame(band_rows)
        band_df.to_parquet(_OUT_DIR / "entry_margin_band.parquet", index=False)
        print("\n02d | entry_margin_band.parquet (beta=central, rigid):")
        print(band_df.to_string(index=False))

        # Entry by prior labor-force status (E1 reporting), central edge.
        ge_c, ne_c, _, ind_c, _, det_c = _entrants_from_pool(pool, beta_c, target, edge="central")
        st_cols = {k: v for k, v in det_c.items() if k.startswith("entrants_")}
        if st_cols:
            print("02d | central entrants by prior status (M): " +
                  ", ".join(f"{k.replace('entrants_','').replace('_M','')}={v}"
                            for k, v in st_cols.items()))

        # E5: incumbent intensive-margin sensitivity (see incumbent_hours_margin docstring).
        ihm = incumbent_hours_margin(w, target)
        ihm.to_parquet(_OUT_DIR / "incumbent_hours_margin.parquet", index=False)
        print("\n02d | incumbent_hours_margin.parquet (eligible incumbents below 40 hrs/wk):")
        print(ihm.to_string(index=False))

        # PI-3 (holistic eval 2026-07-09): entrant-hours mapping sensitivity — bounds how much the
        # low marginal cost per entrant and the entry-FTE figure depend on the rank-rank coupling.
        ehs = entrant_hours_sensitivity(pool, beta_c, target)
        ehs.to_parquet(_OUT_DIR / "entrant_hours_sensitivity.parquet", index=False)
        print("\n02d | entrant_hours_sensitivity.parquet (PI-3, central edge, 3 hours mappings):")
        print(ehs.to_string(index=False))

        # ---- 02b-vs-02d entry reconciliation (ST-12). ------------------------------------
        recon_note = ("Wedge sources: population (02b up-weights observed low-wage incumbents; "
                      "02d draws from the non-employed pool), stimulus basis (02b gross wage "
                      "gain; 02d net return to work), response aggregation (02b person-level "
                      "multiplier on workers; 02d calibrated pool share), elasticity source "
                      "(behavioral.scenarios benchmark vs matching.eps_ext_band).")
        try:
            bs = pd.read_parquet(_OUT_DIR / "behavioral_scenarios.parquet")
            b_central = float(bs.loc[bs["scenario"] == "central", "induced_workers_mn"].iloc[0])
        except Exception:  # noqa: BLE001
            b_central = np.nan
        d_central = float(band_df.loc[(band_df.band_edge == "central") &
                                      (band_df.variant == "as-modeled"), "induced_M"].iloc[0])
        recon = pd.DataFrame([{
            "b02_central_induced_M": b_central, "d02_central_induced_M": d_central,
            "note": recon_note}])
        recon.to_parquet(_OUT_DIR / "entry_reconciliation.parquet", index=False)
        print(f"\n02d | Reconciliation: 02b central {b_central:.2f}M (EITC/CBO benchmark, gross, "
              f"incumbent-weighted) vs 02d central {d_central:.2f}M (structural band, net, pool). "
              f"Do not quote side-by-side without the wedge attribution "
              f"(entry_reconciliation.parquet).")

    print(f"\n02d | Complete. Wrote matching_simulation.parquet")
    print("  Incidence = bargaining share (1-beta), bounded; wages stay in [r, y] (no collapse).")
    print("  TRANSPORTED/SYNTHETIC: beta and reservation ratio imported from the matching literature;")
    print("  entry calibrated to the eps_ext BAND on a net, saturating basis (2026-07-08 remodel).")
    print("  See docs/entry_from_nonemployment_methodology.md for provenance and disclosures.")


if __name__ == "__main__":
    main()
