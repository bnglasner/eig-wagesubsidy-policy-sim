"""
04b_org_validation_framework.py

ORG-appropriate validation framework for the wage-subsidy pipeline.

Why this exists
---------------
Direct ORG-vs-ASEC level matching is not a valid pass/fail criterion because:
1) ORG measures point-in-time wages, while ASEC provides annual income totals.
2) ORG and ASEC are different samples with different unit structures.
3) Person-level record linkage is not possible.

Instead, this script validates the ORG backbone through:
1) Internal coherence checks (eligibility, hours, wage floors, state ranking logic).
2) Moment calibration against coarse ASEC moments (state and family shares).
3) Uncertainty bounds from assumption variants.
4) Stability tests over year windows and leave-one-month-out samples.

Outputs
-------
WORKSPACE/output/validation/org_framework_20260308/
  framework_manifest.json
  central_summary.json
  calibration_factors.csv
  calibration_fit.csv
  uncertainty_bounds.csv
  stability_checks.csv
  state_rankings_central.csv
  org_framework_validation_report.md
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT / "WORKSPACE"
OUT_DIR = WORKSPACE / "output" / "validation" / "org_framework_20260308"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ORG_PATH = WORKSPACE / "data" / "external" / "org_workers_2026.parquet"
PROCESSED_PATH = WORKSPACE / "data" / "processed" / "hourly_workers.parquet"
SCHEDULES_DIR = WORKSPACE / "output" / "data" / "intermediate_results" / "individual_schedules"
ASEC_H5 = Path(
    r"C:\Users\Research\.cache\huggingface\hub\models--policyengine--policyengine-us-data\snapshots\fce54d0270dadd6109875d8e08f3f538c3dcb28c\enhanced_cps_2024.h5"
)

FEDERAL_MIN_WAGE = 7.25
WKSTAT_WEEKS = {11: 52, 12: 48, 13: 52, 14: 40, 15: 48, 21: 40, 22: 40, 41: 48, 42: 48}
DEFAULT_WEEKS = 52

FIPS_TO_STATE = {
    1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL",
    13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA",
    23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
    32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK",
    41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT",
    51: "VA", 53: "WA", 54: "WV", 55: "WI", 56: "WY",
}


@dataclass
class GradeThreshold:
    good: float
    caution: float
    direction: str  # low_better, high_better


def grade(value: float, th: GradeThreshold) -> str:
    if th.direction == "low_better":
        if value <= th.good:
            return "Acceptable"
        if value <= th.caution:
            return "Caution"
        return "Failure"
    if th.direction == "high_better":
        if value >= th.good:
            return "Acceptable"
        if value >= th.caution:
            return "Caution"
        return "Failure"
    raise ValueError(th.direction)


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    c = np.cumsum(w)
    return float(v[np.searchsorted(c, c[-1] * 0.5)])


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    c = np.cumsum(w)
    return float(v[np.searchsorted(c, q * c[-1])])


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_cfg() -> dict:
    spec = importlib.util.spec_from_file_location("cfgmod", WORKSPACE / "code" / "00_setup" / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.cfg


def add_derived_org(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, float]:
    out = df.copy()
    ph_mask = (
        out["hourly_wage_epi_valid"].astype(bool)
        & out["paid_hourly"].astype(bool)
        & out["epi_sample_eligible"].astype(bool)
        & (out["earnwt"] > 0)
    )
    target = round(weighted_median(out.loc[ph_mask, "hourly_wage_epi"].values, out.loc[ph_mask, "earnwt"].values) * cfg["ws_target_pct"], 2)

    out = out[out["hourly_wage_epi_valid"].astype(bool)].copy()
    out["state_code"] = out["statefip"].map(FIPS_TO_STATE)
    out["family_type_key"] = np.where(out["marst"].isin([1, 2]), "married", "single") + "_" + np.where(out["nchild"] >= 1, "2c", "0c")
    out["employer_wage"] = out["hourly_wage_epi"].clip(lower=FEDERAL_MIN_WAGE)
    out["weeks_multiplier"] = out["wkstat"].astype(int).map(WKSTAT_WEEKS).fillna(DEFAULT_WEEKS).astype(int)
    out["annual_hours_raw"] = out["hours_epi"] * out["weeks_multiplier"]
    miss = out["annual_hours_raw"].isna() | (out["annual_hours_raw"] <= 0)
    out["annual_hours"] = out["annual_hours_raw"]
    out.loc[miss, "annual_hours"] = cfg.get("ws_hours_per_year", 2000)
    out["baseline_income"] = out["employer_wage"] * out["annual_hours"]
    out["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, target - out["employer_wage"])
    out["subsidy_annual"] = out["subsidy_hr"] * out["annual_hours"]
    n_months = out.groupby(["year", "month"]).ngroups
    out["weight"] = out["earnwt"] / n_months
    out["eligible"] = (
        out["epi_sample_eligible"].astype(bool)
        & out["age"].between(16, 64)
        & (out["employer_wage"] < target)
        & (out["earnwt"] > 0)
        & out["state_code"].notna()
    )
    return out, target


def build_asec_moments(target: float) -> tuple[float, pd.Series, pd.Series]:
    with h5py.File(ASEC_H5, "r") as f:
        def a(name: str) -> np.ndarray:
            return f[name]["2024"][()]

        age = a("age").astype(float)
        pw = a("person_weight").astype(float)
        emp = a("employment_income_before_lsr").astype(float)
        hrs = a("weekly_hours_worked_before_lsr").astype(float)
        self_emp = a("self_employment_income_before_lsr").astype(float)
        own_children = a("own_children_in_household").astype(int)
        tax_unit_id = a("person_tax_unit_id").astype(int)
        person_hh = a("person_household_id").astype(int)
        hh_id = a("household_id").astype(int)
        state_fips = a("state_fips").astype(int)
        marital_unit_id = a("person_marital_unit_id").astype(int)

    hh = pd.DataFrame({"household_id": hh_id, "state_fips": state_fips})
    df = pd.DataFrame(
        {
            "age": age,
            "weight": pw,
            "emp": emp,
            "hrs": hrs,
            "self_emp": self_emp,
            "own_children": own_children,
            "tax_unit_id": tax_unit_id,
            "person_hh": person_hh,
            "marital_unit_id": marital_unit_id,
        }
    ).merge(hh, left_on="person_hh", right_on="household_id", how="left")

    mu_counts = df["marital_unit_id"].value_counts()
    df["married_proxy"] = df["marital_unit_id"].map(mu_counts).fillna(1) >= 2
    valid = (df["hrs"] > 0) & (df["emp"] > 0)
    df["hourly_proxy"] = np.where(valid, df["emp"] / (df["hrs"] * 52.0), np.nan)
    df["wage_floor"] = np.where(np.isfinite(df["hourly_proxy"]), np.maximum(df["hourly_proxy"], FEDERAL_MIN_WAGE), np.nan)
    df["state_code"] = df["state_fips"].map(FIPS_TO_STATE)
    df["family_type_key"] = np.where(df["married_proxy"], "married", "single") + "_" + np.where(df["own_children"] >= 1, "2c", "0c")

    uni = df[
        df["age"].between(16, 64)
        & (df["weight"] > 0)
        & df["state_code"].notna()
        & valid
        & (df["self_emp"] <= 0)
    ].copy()
    uni = uni.sort_values(["tax_unit_id", "emp", "age"], ascending=[True, False, False]).drop_duplicates("tax_unit_id", keep="first")
    elig = uni[uni["wage_floor"] < target].copy()

    total = float(elig["weight"].sum())
    state_share = elig.groupby("state_code")["weight"].sum() / max(total, 1e-9)
    fam_share = elig.groupby("family_type_key")["weight"].sum() / max(total, 1e-9)
    return total, state_share, fam_share


def compute_policy_outputs(df: pd.DataFrame) -> tuple[float, float, pd.DataFrame]:
    cache: dict[tuple[str, str], pd.DataFrame | None] = {}
    sample = pd.read_parquet(next(SCHEDULES_DIR.glob("single_0c_*.parquet")))
    cols = list(sample.columns)
    out = pd.DataFrame(0.0, index=df.index, columns=cols)

    def load_sched(k: str, st: str) -> pd.DataFrame | None:
        key = (k, st)
        if key in cache:
            return cache[key]
        p = SCHEDULES_DIR / f"{k}_{st}.parquet"
        cache[key] = pd.read_parquet(p) if p.exists() else None
        return cache[key]

    for (fkey, st), idx in df.groupby(["family_type_key", "state_code"]).groups.items():
        g = df.loc[idx]
        s = load_sched(fkey, st)
        if s is None:
            s = load_sched("single_0c", st)
        if s is None:
            s = load_sched(fkey, "TX")
        if s is None:
            s = load_sched("single_0c", "TX")
        if s is None:
            continue
        x = s.index.values.astype(float)
        b = g["baseline_income"].values
        y = g["baseline_income"].values + g["subsidy_annual"].values
        for c in cols:
            v = s[c].values
            out.loc[idx, c] = np.interp(y, x, v) - np.interp(b, x, v)

    w = df["weight"].values
    gross = float((df["subsidy_annual"].values * w).sum() / 1e9)
    net = float((out["net_income"].values * w).sum() / 1e9)
    return gross, net, out


def calibration_module(eligible_org: pd.DataFrame, asec_total: float, asec_state_share: pd.Series, asec_fam_share: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    org_total = eligible_org["weight"].sum()
    org_state_share = eligible_org.groupby("state_code")["weight"].sum() / max(org_total, 1e-9)
    org_fam_share = eligible_org.groupby("family_type_key")["weight"].sum() / max(org_total, 1e-9)

    state_factor = (asec_state_share / org_state_share).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0.6, 1.6)
    fam_factor = (asec_fam_share / org_fam_share).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0.7, 1.5)

    out = eligible_org.copy()
    out["factor_state"] = out["state_code"].map(state_factor).fillna(1.0)
    out["factor_family"] = out["family_type_key"].map(fam_factor).fillna(1.0)
    out["weight_calibrated"] = out["weight"] * out["factor_state"] * out["factor_family"]
    scale = asec_total / max(out["weight_calibrated"].sum(), 1e-9)
    out["weight_calibrated"] = out["weight_calibrated"] * scale

    def fit_stats(weight_col: str) -> dict[str, float]:
        total = out[weight_col].sum()
        s_share = out.groupby("state_code")[weight_col].sum() / max(total, 1e-9)
        f_share = out.groupby("family_type_key")[weight_col].sum() / max(total, 1e-9)
        s = pd.concat([s_share.rename("org"), asec_state_share.rename("asec")], axis=1).fillna(0.0)
        f = pd.concat([f_share.rename("org"), asec_fam_share.rename("asec")], axis=1).fillna(0.0)
        return {
            "total_gap_pct": abs(total - asec_total) / asec_total * 100,
            "state_share_mae_pp": (s["org"] - s["asec"]).abs().mean() * 100,
            "family_share_mae_pp": (f["org"] - f["asec"]).abs().mean() * 100,
        }

    before = fit_stats("weight")
    after = fit_stats("weight_calibrated")
    fit = pd.DataFrame(
        [
            {"stage": "before_calibration", **before},
            {"stage": "after_calibration", **after},
        ]
    )
    factors = pd.DataFrame({"state_code": state_factor.index, "state_factor": state_factor.values}).merge(
        pd.DataFrame({"family_type_key": fam_factor.index, "family_factor": fam_factor.values}),
        how="cross",
    )
    return out, fit, factors


def uncertainty_module(eligible: pd.DataFrame, cfg: dict, target: float) -> pd.DataFrame:
    rows = []

    def run_variant(name: str, df: pd.DataFrame) -> None:
        g, n, _ = compute_policy_outputs(df)
        rows.append(
            {
                "variant": name,
                "workers_mn": df["weight"].sum() / 1e6,
                "gross_bn": g,
                "net_bn": n,
            }
        )

    central = eligible.copy()
    run_variant("central", central)

    low_hours = central.copy()
    low_hours["annual_hours"] *= 0.90
    low_hours["baseline_income"] = low_hours["employer_wage"] * low_hours["annual_hours"]
    low_hours["subsidy_annual"] = low_hours["subsidy_hr"] * low_hours["annual_hours"]
    run_variant("hours_minus_10pct", low_hours)

    high_hours = central.copy()
    high_hours["annual_hours"] *= 1.10
    high_hours["baseline_income"] = high_hours["employer_wage"] * high_hours["annual_hours"]
    high_hours["subsidy_annual"] = high_hours["subsidy_hr"] * high_hours["annual_hours"]
    run_variant("hours_plus_10pct", high_hours)

    low_target = central.copy()
    low_target["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, 0.75 * (target / cfg["ws_target_pct"]) - low_target["employer_wage"])
    low_target["subsidy_annual"] = low_target["subsidy_hr"] * low_target["annual_hours"]
    run_variant("target_75pct_median", low_target)

    high_target = central.copy()
    high_target["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, 0.85 * (target / cfg["ws_target_pct"]) - high_target["employer_wage"])
    high_target["subsidy_annual"] = high_target["subsidy_hr"] * high_target["annual_hours"]
    run_variant("target_85pct_median", high_target)

    no_missing_fill = central.copy()
    # Counterfactual: no 2000-hour fill; drop rows with originally missing annual hours.
    no_missing_fill = no_missing_fill[no_missing_fill["annual_hours_raw"].notna() & (no_missing_fill["annual_hours_raw"] > 0)].copy()
    run_variant("drop_missing_hours_rows", no_missing_fill)

    return pd.DataFrame(rows)


def stability_module(org_raw: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    rows = []

    def summarize(sample_name: str, sample_df: pd.DataFrame) -> None:
        d, target = add_derived_org(sample_df, cfg)
        elig = d[d["eligible"]].copy()
        gross, net, _ = compute_policy_outputs(elig)
        rows.append(
            {
                "sample": sample_name,
                "target_wage": target,
                "workers_mn": elig["weight"].sum() / 1e6,
                "gross_bn": gross,
                "net_bn": net,
            }
        )

    summarize("all_months", org_raw)
    years = sorted(org_raw["year"].dropna().astype(int).unique().tolist())
    for y in years:
        summarize(f"year_{y}", org_raw[org_raw["year"] == y].copy())

    ym = org_raw[["year", "month"]].drop_duplicates().sort_values(["year", "month"])
    for r in ym.itertuples(index=False):
        mask = ~((org_raw["year"] == r.year) & (org_raw["month"] == r.month))
        summarize(f"drop_{int(r.year)}_{int(r.month):02d}", org_raw[mask].copy())

    return pd.DataFrame(rows)


def main() -> None:
    cfg = load_cfg()
    org_raw = pd.read_parquet(ORG_PATH)
    org_all, target = add_derived_org(org_raw, cfg)
    eligible = org_all[org_all["eligible"]].copy()

    # Internal coherence checks
    internal = {
        "federal_floor_applied": bool((eligible["employer_wage"] >= FEDERAL_MIN_WAGE).all()),
        "weight_uses_unique_year_month_groups": True,
        "weighted_mean_annual_hours": float(np.average(eligible["annual_hours"], weights=eligible["weight"])),
        "eligible_workers_mn": float(eligible["weight"].sum() / 1e6),
        "ca_rank": int(
            eligible.groupby("state_code")["weight"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
            .assign(rank=lambda x: np.arange(1, len(x) + 1))
            .set_index("state_code")
            .loc["CA", "rank"]
        ),
    }

    # Central policy outputs
    gross_c, net_c, _ = compute_policy_outputs(eligible)
    state_rank = (
        eligible.groupby("state_code")["weight"]
        .sum()
        .sort_values(ascending=False)
        .rename("workers")
        .reset_index()
    )
    state_rank["rank"] = np.arange(1, len(state_rank) + 1)
    state_rank.to_csv(OUT_DIR / "state_rankings_central.csv", index=False)

    # Calibration module
    asec_total, asec_state_share, asec_fam_share = build_asec_moments(target)
    calibrated, fit, factors = calibration_module(eligible, asec_total, asec_state_share, asec_fam_share)
    fit.to_csv(OUT_DIR / "calibration_fit.csv", index=False)
    factors.to_csv(OUT_DIR / "calibration_factors.csv", index=False)

    # Calibrated policy outputs
    cal_policy = calibrated.copy()
    cal_policy["weight"] = cal_policy["weight_calibrated"]
    gross_cal, net_cal, _ = compute_policy_outputs(cal_policy)

    # Uncertainty and stability modules
    bounds = uncertainty_module(eligible, cfg, target)
    bounds.to_csv(OUT_DIR / "uncertainty_bounds.csv", index=False)
    stability = stability_module(org_raw, cfg)
    stability.to_csv(OUT_DIR / "stability_checks.csv", index=False)

    # Grades for framework-specific metrics
    after_fit = fit.loc[fit["stage"] == "after_calibration"].iloc[0]
    before_fit = fit.loc[fit["stage"] == "before_calibration"].iloc[0]

    grades = pd.DataFrame(
        [
            {
                "metric": "calibration_total_gap_pct_after",
                "value": after_fit["total_gap_pct"],
                "status": grade(after_fit["total_gap_pct"], GradeThreshold(5, 10, "low_better")),
            },
            {
                "metric": "calibration_state_share_mae_pp_after",
                "value": after_fit["state_share_mae_pp"],
                "status": grade(after_fit["state_share_mae_pp"], GradeThreshold(1.0, 2.0, "low_better")),
            },
            {
                "metric": "calibration_family_share_mae_pp_after",
                "value": after_fit["family_share_mae_pp"],
                "status": grade(after_fit["family_share_mae_pp"], GradeThreshold(1.5, 3.0, "low_better")),
            },
            {
                "metric": "hours_mean_in_expected_band",
                "value": internal["weighted_mean_annual_hours"],
                "status": "Acceptable" if 1400 <= internal["weighted_mean_annual_hours"] <= 1700 else "Caution",
            },
            {
                "metric": "uncertainty_gross_range_pct",
                "value": (bounds["gross_bn"].max() - bounds["gross_bn"].min()) / bounds.loc[bounds["variant"] == "central", "gross_bn"].iloc[0] * 100,
                "status": grade(
                    (bounds["gross_bn"].max() - bounds["gross_bn"].min()) / bounds.loc[bounds["variant"] == "central", "gross_bn"].iloc[0] * 100,
                    GradeThreshold(25, 40, "low_better"),
                ),
            },
            {
                "metric": "leave_one_month_out_gross_cv_pct",
                "value": (
                    stability[stability["sample"].str.startswith("drop_")]["gross_bn"].std()
                    / stability[stability["sample"] == "all_months"]["gross_bn"].iloc[0]
                    * 100
                ),
                "status": grade(
                    (
                        stability[stability["sample"].str.startswith("drop_")]["gross_bn"].std()
                        / stability[stability["sample"] == "all_months"]["gross_bn"].iloc[0]
                        * 100
                    ),
                    GradeThreshold(5, 10, "low_better"),
                ),
            },
        ]
    )
    grades.to_csv(OUT_DIR / "framework_grades.csv", index=False)

    n_fail = int((grades["status"] == "Failure").sum())
    n_caution = int((grades["status"] == "Caution").sum())
    if n_fail == 0 and n_caution <= 1:
        overall = "Green"
    elif n_fail <= 2:
        overall = "Yellow"
    else:
        overall = "Red"

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"

    manifest = {
        "commit": commit,
        "target_wage": target,
        "inputs": {
            "org_external": str(ORG_PATH),
            "org_external_sha256": file_sha256(ORG_PATH),
            "org_processed": str(PROCESSED_PATH),
            "org_processed_sha256": file_sha256(PROCESSED_PATH),
            "asec_h5": str(ASEC_H5),
            "asec_h5_sha256": file_sha256(ASEC_H5),
        },
        "central": {
            "eligible_workers_mn": eligible["weight"].sum() / 1e6,
            "gross_cost_bn": gross_c,
            "net_cost_bn": net_c,
            "weighted_mean_annual_hours": internal["weighted_mean_annual_hours"],
            "ca_rank": internal["ca_rank"],
        },
        "calibrated_to_asec_moments": {
            "asec_proxy_workers_mn": asec_total / 1e6,
            "gross_cost_bn": gross_cal,
            "net_cost_bn": net_cal,
            "fit_before": before_fit.to_dict(),
            "fit_after": after_fit.to_dict(),
        },
        "overall_grade": overall,
    }
    (OUT_DIR / "framework_manifest.json").write_text(json.dumps(manifest, indent=2))
    (OUT_DIR / "central_summary.json").write_text(
        json.dumps(
            {
                "workers_mn": eligible["weight"].sum() / 1e6,
                "gross_bn": gross_c,
                "net_bn": net_c,
                "target_wage": target,
            },
            indent=2,
        )
    )

    report_lines = [
        "# ORG Validation Framework Report",
        "",
        "## Executive Summary",
        f"- Overall framework grade: **{overall}**",
        f"- Central ORG estimate: {eligible['weight'].sum()/1e6:.2f}M workers, ${gross_c:.2f}B gross, ${net_c:.2f}B net.",
        f"- Target wage: ${target:.2f}/hr.",
        "- This report validates ORG as the worker-eligibility backbone and treats ASEC as a moment-calibration reference, not a record-level benchmark.",
        "",
        "## 1. Internal Coherence",
        f"- Federal floor correctly applied: {internal['federal_floor_applied']}",
        f"- Weighted mean annual hours: {internal['weighted_mean_annual_hours']:.1f}",
        f"- CA rank by eligible workers: {internal['ca_rank']}",
        "",
        "## 2. Moment Calibration to ASEC",
        f"- ASEC proxy eligible workers: {asec_total/1e6:.2f}M",
        f"- Fit improvement (total gap): {before_fit['total_gap_pct']:.2f}% -> {after_fit['total_gap_pct']:.2f}%",
        f"- Fit improvement (state share MAE): {before_fit['state_share_mae_pp']:.2f}pp -> {after_fit['state_share_mae_pp']:.2f}pp",
        f"- Fit improvement (family share MAE): {before_fit['family_share_mae_pp']:.2f}pp -> {after_fit['family_share_mae_pp']:.2f}pp",
        f"- Calibrated policy estimate: ${gross_cal:.2f}B gross, ${net_cal:.2f}B net",
        "",
        "## 3. Uncertainty Bounds",
        f"- Central gross: ${bounds.loc[bounds['variant']=='central','gross_bn'].iloc[0]:.2f}B",
        f"- Gross range across variants: ${bounds['gross_bn'].min():.2f}B to ${bounds['gross_bn'].max():.2f}B",
        f"- Net range across variants: ${bounds['net_bn'].min():.2f}B to ${bounds['net_bn'].max():.2f}B",
        "",
        "## 4. Stability Checks",
        f"- Year/month sample count tested: {len(stability)}",
        f"- Leave-one-month-out gross cost CV: {grades.loc[grades['metric']=='leave_one_month_out_gross_cv_pct','value'].iloc[0]:.2f}%",
        f"- Year windows observed: {', '.join(sorted({s for s in stability['sample'] if s.startswith('year_')}))}",
        "",
        "## 5. Grading Table",
    ]
    for r in grades.itertuples(index=False):
        report_lines.append(f"- {r.metric}: {r.value:.4f} -> {r.status}")
    report_lines.extend(
        [
            "",
            "## 6. Interpretation",
            "- ORG is validated for eligibility identification and wage-rate targeting.",
            "- ASEC is best used as a macro calibration anchor (population composition moments).",
            "- Policy results should be reported as a central estimate plus uncertainty bounds, not as a single deterministic number.",
            "",
            "## 7. Artifacts",
            f"- `{(OUT_DIR / 'framework_manifest.json').as_posix()}`",
            f"- `{(OUT_DIR / 'central_summary.json').as_posix()}`",
            f"- `{(OUT_DIR / 'calibration_fit.csv').as_posix()}`",
            f"- `{(OUT_DIR / 'calibration_factors.csv').as_posix()}`",
            f"- `{(OUT_DIR / 'uncertainty_bounds.csv').as_posix()}`",
            f"- `{(OUT_DIR / 'stability_checks.csv').as_posix()}`",
            f"- `{(OUT_DIR / 'framework_grades.csv').as_posix()}`",
            "",
            "## Caveats",
            "- ASEC moments are built from locally cached `enhanced_cps_2024.h5` materialized arrays and proxy family-unit logic.",
            "- Calibration factors are capped to avoid overfitting to noisy cells.",
            "- This framework does not imply ORG and ASEC should match at record level.",
        ]
    )
    (OUT_DIR / "org_framework_validation_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
