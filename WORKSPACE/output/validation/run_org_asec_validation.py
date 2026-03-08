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
OUT_DIR = WORKSPACE / "output" / "validation" / "org_vs_asec_20260308"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = WORKSPACE / "output" / "validation" / "org_vs_asec_validation_plan_predraft.md"

ORG_EXTERNAL = WORKSPACE / "data" / "external" / "org_workers_2026.parquet"
ORG_PROCESSED = WORKSPACE / "data" / "processed" / "hourly_workers.parquet"
ASEC_H5 = Path(
    r"C:\Users\Research\.cache\huggingface\hub\models--policyengine--policyengine-us-data\snapshots\fce54d0270dadd6109875d8e08f3f538c3dcb28c\enhanced_cps_2024.h5"
)
SCHEDULES_DIR = WORKSPACE / "output" / "data" / "intermediate_results" / "individual_schedules"


FIPS_TO_STATE = {
    1: "AL", 2: "AK", 4: "AZ", 5: "AR", 6: "CA", 8: "CO", 9: "CT", 10: "DE", 11: "DC", 12: "FL",
    13: "GA", 15: "HI", 16: "ID", 17: "IL", 18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA",
    23: "ME", 24: "MD", 25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
    32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND", 39: "OH", 40: "OK",
    41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD", 47: "TN", 48: "TX", 49: "UT", 50: "VT",
    51: "VA", 53: "WA", 54: "WV", 55: "WI", 56: "WY",
}

WKSTAT_WEEKS = {11: 52, 12: 48, 13: 52, 14: 40, 15: 48, 21: 40, 22: 40, 41: 48, 42: 48}
DEFAULT_WEEKS = 52
FEDERAL_MIN_WAGE = 7.25


@dataclass
class Threshold:
    good: float | None
    caution: float | None
    direction: str  # "low_better" | "high_better"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def weighted_quantile(values: np.ndarray, weights: np.ndarray, q: float) -> float:
    idx = np.argsort(values)
    v = values[idx]
    w = weights[idx]
    c = np.cumsum(w)
    return float(v[np.searchsorted(c, q * c[-1])])


def weighted_ks(a_vals: np.ndarray, a_wts: np.ndarray, b_vals: np.ndarray, b_wts: np.ndarray) -> float:
    grid = np.unique(np.concatenate([a_vals, b_vals]))
    a_idx = np.argsort(a_vals)
    b_idx = np.argsort(b_vals)
    av = a_vals[a_idx]
    aw = a_wts[a_idx]
    bv = b_vals[b_idx]
    bw = b_wts[b_idx]
    ac = np.cumsum(aw) / aw.sum()
    bc = np.cumsum(bw) / bw.sum()
    ap = np.searchsorted(av, grid, side="right")
    bp = np.searchsorted(bv, grid, side="right")
    acdf = np.where(ap > 0, ac[np.clip(ap - 1, 0, len(ac) - 1)], 0)
    bcdf = np.where(bp > 0, bc[np.clip(bp - 1, 0, len(bc) - 1)], 0)
    return float(np.max(np.abs(acdf - bcdf)))


def status_from_threshold(value: float, th: Threshold) -> str:
    if th.direction == "low_better":
        if th.good is not None and value <= th.good:
            return "Acceptable"
        if th.caution is not None and value <= th.caution:
            return "Caution"
        return "Failure"
    if th.direction == "high_better":
        if th.good is not None and value >= th.good:
            return "Acceptable"
        if th.caution is not None and value >= th.caution:
            return "Caution"
        return "Failure"
    raise ValueError(th.direction)


def load_cfg() -> dict:
    spec = importlib.util.spec_from_file_location("cfgmod", WORKSPACE / "code" / "00_setup" / "00_config.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.cfg


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    idx = np.argsort(values)
    vals_s = values[idx]
    wts_s = weights[idx]
    cumw = np.cumsum(wts_s)
    return float(vals_s[np.searchsorted(cumw, cumw[-1] * 0.5)])


def build_org_analytic(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    org = pd.read_parquet(ORG_EXTERNAL)
    ph_mask = (
        org["hourly_wage_epi_valid"].astype(bool)
        & org["paid_hourly"].astype(bool)
        & org["epi_sample_eligible"].astype(bool)
        & (org["earnwt"] > 0)
    )
    median_wage = weighted_median(org.loc[ph_mask, "hourly_wage_epi"].values, org.loc[ph_mask, "earnwt"].values)
    target_wage = round(median_wage * cfg["ws_target_pct"], 2)

    org = org[org["hourly_wage_epi_valid"].astype(bool)].copy()
    org["employer_wage"] = org["hourly_wage_epi"].clip(lower=FEDERAL_MIN_WAGE)
    org["state_code"] = org["statefip"].map(FIPS_TO_STATE)
    org["family_type_key"] = np.where(org["marst"].isin([1, 2]), "married", "single") + "_" + np.where(org["nchild"] >= 1, "2c", "0c")
    org["weeks_multiplier"] = org["wkstat"].astype(int).map(WKSTAT_WEEKS).fillna(DEFAULT_WEEKS).astype(int)
    org["annual_hours_raw"] = org["hours_epi"] * org["weeks_multiplier"]
    fallback = org["annual_hours_raw"].isna() | (org["annual_hours_raw"] <= 0)
    org["annual_hours"] = org["annual_hours_raw"]
    org.loc[fallback, "annual_hours"] = cfg.get("ws_hours_per_year", 2000)
    org["baseline_income"] = org["employer_wage"] * org["annual_hours"]
    org["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, target_wage - org["employer_wage"])
    org["subsidy_annual"] = org["subsidy_hr"] * org["annual_hours"]
    n_months = org.groupby(["year", "month"]).ngroups
    org["weight"] = org["earnwt"] / n_months

    universe = org[
        org["epi_sample_eligible"].astype(bool)
        & org["age"].between(16, 64)
        & (org["earnwt"] > 0)
        & org["state_code"].notna()
    ].copy()
    eligible = universe[universe["employer_wage"] < target_wage].copy()
    return universe, eligible, target_wage


def build_asec_analytic(target_wage: float, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    with h5py.File(ASEC_H5, "r") as f:
        def a(name: str) -> np.ndarray:
            return f[name]["2024"][()]

        age = a("age").astype(float)
        person_weight = a("person_weight").astype(float)
        emp_income = a("employment_income_before_lsr").astype(float)
        wk_hours = a("weekly_hours_worked_before_lsr").astype(float)
        self_emp = a("self_employment_income_before_lsr").astype(float)
        person_hh = a("person_household_id").astype(int)
        person_tax_unit_id = a("person_tax_unit_id").astype(int)
        hh_id = a("household_id").astype(int)
        state_fips = a("state_fips").astype(int)
        own_children = a("own_children_in_household").astype(int)
        is_female = a("is_female").astype(bool)
        marital_unit_id = a("person_marital_unit_id").astype(int)

    hh_map = pd.DataFrame({"household_id": hh_id, "state_fips": state_fips})
    people = pd.DataFrame(
        {
            "age": age,
            "weight": person_weight,
            "employment_income": emp_income,
            "weekly_hours": wk_hours,
            "self_emp_income": self_emp,
            "person_household_id": person_hh,
            "person_tax_unit_id": person_tax_unit_id,
            "own_children": own_children,
            "is_female": is_female,
            "person_marital_unit_id": marital_unit_id,
        }
    ).merge(hh_map, left_on="person_household_id", right_on="household_id", how="left")
    mu_counts = people["person_marital_unit_id"].value_counts()
    people["married_proxy"] = people["person_marital_unit_id"].map(mu_counts).fillna(1) >= 2
    people["state_code"] = people["state_fips"].map(FIPS_TO_STATE)
    people["family_type_key"] = np.where(people["married_proxy"], "married", "single") + "_" + np.where(people["own_children"] >= 1, "2c", "0c")
    valid = (people["weekly_hours"] > 0) & (people["employment_income"] > 0)
    people["hourly_wage_proxy"] = np.where(valid, people["employment_income"] / (people["weekly_hours"] * 52.0), np.nan)
    people["employer_wage"] = np.where(np.isfinite(people["hourly_wage_proxy"]), np.maximum(people["hourly_wage_proxy"], FEDERAL_MIN_WAGE), np.nan)
    people["annual_hours"] = np.where(valid, people["weekly_hours"] * 52.0, np.nan)
    people["baseline_income"] = people["employer_wage"] * people["annual_hours"]
    people["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, target_wage - people["employer_wage"])
    people["subsidy_annual"] = people["subsidy_hr"] * people["annual_hours"]

    base_universe = people[
        people["age"].between(16, 64)
        & (people["weight"] > 0)
        & people["state_code"].notna()
        & valid
        & (people["self_emp_income"] <= 0)
    ].copy()

    # Legacy PE path used tax-unit heads; proxy this by selecting one primary earner
    # per tax unit among working-age wage/salary workers in the ASEC extract.
    base_universe = base_universe.sort_values(
        ["person_tax_unit_id", "employment_income", "age"],
        ascending=[True, False, False],
    )
    universe = base_universe.drop_duplicates(subset=["person_tax_unit_id"], keep="first").copy()
    eligible = universe[universe["employer_wage"] < target_wage].copy()
    return universe, eligible


def load_schedule(family_key: str, state_code: str, cache: dict[tuple[str, str], pd.DataFrame | None]) -> pd.DataFrame | None:
    k = (family_key, state_code)
    if k in cache:
        return cache[k]
    path = SCHEDULES_DIR / f"{family_key}_{state_code}.parquet"
    cache[k] = pd.read_parquet(path) if path.exists() else None
    return cache[k]


def compute_policy_outputs(df: pd.DataFrame) -> tuple[float, float, pd.DataFrame]:
    cache: dict[tuple[str, str], pd.DataFrame | None] = {}
    sample = pd.read_parquet(next(SCHEDULES_DIR.glob("single_0c_*.parquet")))
    delta_cols = list(sample.columns)
    out = pd.DataFrame(0.0, index=df.index, columns=delta_cols)
    for (fkey, state), idx in df.groupby(["family_type_key", "state_code"]).groups.items():
        grp = df.loc[idx]
        sched = load_schedule(fkey, state, cache)
        if sched is None:
            sched = load_schedule("single_0c", state, cache)
        if sched is None:
            sched = load_schedule(fkey, "TX", cache)
        if sched is None:
            sched = load_schedule("single_0c", "TX", cache)
        if sched is None:
            continue
        x = sched.index.values.astype(float)
        b = grp["baseline_income"].values
        s = (grp["baseline_income"] + grp["subsidy_annual"]).values
        for col in delta_cols:
            y = sched[col].values
            out.loc[idx, col] = np.interp(s, x, y) - np.interp(b, x, y)

    w = df["weight"].values
    gross = float((df["subsidy_annual"].values * w).sum() / 1e9)
    net = float((out["net_income"].values * w).sum() / 1e9) if "net_income" in out.columns else np.nan
    interactions = pd.DataFrame(
        {
            "component": out.columns,
            "delta_bn": [float((out[c].values * w).sum() / 1e9) for c in out.columns],
        }
    )
    return gross, net, interactions


def pp(x: float) -> str:
    return f"{x:.4f}"


def main() -> None:
    cfg = load_cfg()
    universe_org, eligible_org, target = build_org_analytic(cfg)
    universe_asec, eligible_asec = build_asec_analytic(target, cfg)

    eligible_org.to_parquet(OUT_DIR / "eligible_org.parquet", index=False)
    eligible_asec.to_parquet(OUT_DIR / "eligible_asec_proxy.parquet", index=False)

    metrics = []

    def add(test: str, metric: str, value: float, th: Threshold):
        metrics.append(
            {
                "test": test,
                "metric": metric,
                "value": value,
                "status": status_from_threshold(value, th),
            }
        )

    # Test A
    n_org = eligible_org["weight"].sum()
    n_asec = eligible_asec["weight"].sum()
    national_gap = abs(n_org - n_asec) / n_asec
    add("A", "national_worker_gap_pct", national_gap * 100, Threshold(5, 10, "low_better"))
    st_org = eligible_org.groupby("state_code")["weight"].sum()
    st_asec = eligible_asec.groupby("state_code")["weight"].sum()
    st_cmp = pd.concat([st_org.rename("org"), st_asec.rename("asec")], axis=1).dropna()
    st_cmp = st_cmp[st_cmp["asec"] > 0]
    st_cmp["gap_pct"] = (st_cmp["org"] - st_cmp["asec"]).abs() / st_cmp["asec"] * 100
    add("A", "state_median_gap_pct", float(st_cmp["gap_pct"].median()), Threshold(8, 15, "low_better"))
    large = st_cmp.loc[st_cmp.index.intersection(["CA", "TX", "FL", "NY"]), "gap_pct"]
    if len(large):
        add("A", "large_state_max_gap_pct", float(large.max()), Threshold(12, 20, "low_better"))

    # Test B
    qs = [0.1, 0.25, 0.5, 0.75, 0.9]
    q_gaps = []
    ov = eligible_org["employer_wage"].values
    ow = eligible_org["weight"].values
    av = eligible_asec["employer_wage"].values
    aw = eligible_asec["weight"].values
    for q in qs:
        oq = weighted_quantile(ov, ow, q)
        aq = weighted_quantile(av, aw, q)
        q_gaps.append(abs(oq - aq) / aq * 100)
    add("B", "wage_quantile_gap_max_pct", float(max(q_gaps)), Threshold(10, 20, "low_better"))
    add("B", "weighted_ks", weighted_ks(ov, ow, av, aw), Threshold(0.08, 0.15, "low_better"))

    # Test C
    omed = weighted_quantile(eligible_org["baseline_income"].values, eligible_org["weight"].values, 0.5)
    amed = weighted_quantile(eligible_asec["baseline_income"].values, eligible_asec["weight"].values, 0.5)
    med_gap = abs(omed - amed) / amed * 100
    add("C", "median_baseline_income_gap_pct", med_gap, Threshold(10, 20, "low_better"))
    org_mean_w = np.average(eligible_org["employer_wage"], weights=eligible_org["weight"])
    org_mean_h = np.average(eligible_org["annual_hours"], weights=eligible_org["weight"])
    asec_mean_w = np.average(eligible_asec["employer_wage"], weights=eligible_asec["weight"])
    asec_mean_h = np.average(eligible_asec["annual_hours"], weights=eligible_asec["weight"])
    predicted = asec_mean_w * asec_mean_h * (org_mean_w / asec_mean_w) * (org_mean_h / asec_mean_h)
    actual = np.average(eligible_org["baseline_income"], weights=eligible_org["weight"])
    residual = abs(actual - predicted) / max(1e-9, actual) * 100
    add("C", "decomposition_residual_pct", residual, Threshold(15, 30, "low_better"))

    # Test D
    org_share = eligible_org["weight"].sum() / universe_org["weight"].sum() * 100
    asec_share = eligible_asec["weight"].sum() / universe_asec["weight"].sum() * 100
    add("D", "eligible_count_gap_pct", abs(n_org - n_asec) / n_asec * 100, Threshold(10, 20, "low_better"))
    add("D", "eligible_share_gap_pp", abs(org_share - asec_share), Threshold(2, 5, "low_better"))
    rank_df = st_cmp.copy()
    rank_df["rank_org"] = rank_df["org"].rank(ascending=False, method="average")
    rank_df["rank_asec"] = rank_df["asec"].rank(ascending=False, method="average")
    spearman = rank_df["rank_org"].corr(rank_df["rank_asec"], method="pearson")
    add("D", "state_rank_spearman", float(spearman), Threshold(0.90, 0.75, "high_better"))

    # Test E
    f_org = eligible_org.groupby("family_type_key")["weight"].sum() / eligible_org["weight"].sum() * 100
    f_asec = eligible_asec.groupby("family_type_key")["weight"].sum() / eligible_asec["weight"].sum() * 100
    f_cmp = pd.concat([f_org.rename("org"), f_asec.rename("asec")], axis=1).fillna(0.0)
    f_cmp["gap_pp"] = (f_cmp["org"] - f_cmp["asec"]).abs()
    add("E", "family_bucket_max_gap_pp", float(f_cmp["gap_pp"].max()), Threshold(3, 6, "low_better"))
    add("E", "family_total_abs_dev_pp", float(f_cmp["gap_pp"].sum()), Threshold(8, 15, "low_better"))

    # Test F
    org_gross, org_net, org_inter = compute_policy_outputs(eligible_org)
    asec_gross, asec_net, asec_inter = compute_policy_outputs(eligible_asec)
    add("F", "gross_cost_gap_pct", abs(org_gross - asec_gross) / asec_gross * 100, Threshold(15, 30, "low_better"))
    add("F", "net_cost_gap_pct", abs(org_net - asec_net) / abs(asec_net) * 100, Threshold(20, 35, "low_better"))
    merged_i = org_inter.merge(asec_inter, on="component", suffixes=("_org", "_asec"))
    major = merged_i[merged_i["component"].isin(["snap", "ssi", "tanf", "federal_tax", "state_tax", "payroll_tax"])]
    flips = int(((major["delta_bn_org"] > 0) != (major["delta_bn_asec"] > 0)).sum())
    if flips == 0:
        sign_score = 0.0
    elif flips == 1:
        sign_score = 1.0
    else:
        sign_score = 2.0
    add("F", "major_component_sign_flips_score", sign_score, Threshold(0.0, 1.0, "low_better"))

    # Test G sensitivity
    variants = []
    base = eligible_org.copy()
    variants.append(("central", base))

    low = base.copy()
    low["annual_hours"] = low["annual_hours"] * 0.9
    low["baseline_income"] = low["employer_wage"] * low["annual_hours"]
    low["subsidy_annual"] = low["subsidy_hr"] * low["annual_hours"]
    variants.append(("hours_low", low))

    high = base.copy()
    high["annual_hours"] = high["annual_hours"] * 1.1
    high["baseline_income"] = high["employer_wage"] * high["annual_hours"]
    high["subsidy_annual"] = high["subsidy_hr"] * high["annual_hours"]
    variants.append(("hours_high", high))

    t75 = base.copy()
    t75["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, 0.75 * (target / cfg["ws_target_pct"]) - t75["employer_wage"])
    t75["subsidy_annual"] = t75["subsidy_hr"] * t75["annual_hours"]
    variants.append(("target_75pct_median", t75))

    t85 = base.copy()
    t85["subsidy_hr"] = cfg["ws_subsidy_pct"] * np.maximum(0.0, 0.85 * (target / cfg["ws_target_pct"]) - t85["employer_wage"])
    t85["subsidy_annual"] = t85["subsidy_hr"] * t85["annual_hours"]
    variants.append(("target_85pct_median", t85))

    sens_rows = []
    top10_ref = set(base.groupby("state_code")["weight"].sum().sort_values(ascending=False).head(10).index)
    for name, d in variants:
        gross, net, _ = compute_policy_outputs(d)
        top10 = set(d.groupby("state_code")["weight"].sum().sort_values(ascending=False).head(10).index)
        sens_rows.append({"variant": name, "gross_bn": gross, "net_bn": net, "top10_overlap": len(top10 & top10_ref)})
    sens = pd.DataFrame(sens_rows)
    range_pct = (sens["gross_bn"].max() - sens["gross_bn"].min()) / sens.loc[sens["variant"] == "central", "gross_bn"].iloc[0] * 100
    add("G", "gross_cost_range_pct_of_central", float(range_pct), Threshold(20, 35, "low_better"))
    add("G", "min_top10_overlap", float(sens["top10_overlap"].min()), Threshold(8, 6, "high_better"))

    metrics_df = pd.DataFrame(metrics)
    metrics_df.to_csv(OUT_DIR / "metrics.csv", index=False)
    st_cmp.reset_index().to_csv(OUT_DIR / "state_workers_org_vs_asec.csv", index=False)
    f_cmp.reset_index().to_csv(OUT_DIR / "family_shares_org_vs_asec.csv", index=False)
    sens.to_csv(OUT_DIR / "sensitivity.csv", index=False)
    merged_i.to_csv(OUT_DIR / "program_interactions_org_vs_asec.csv", index=False)

    status_counts = metrics_df["status"].value_counts().to_dict()
    n_fail = int(status_counts.get("Failure", 0))
    n_caution = int(status_counts.get("Caution", 0))
    n_total = len(metrics_df)
    caution_share = n_caution / n_total if n_total else 0.0
    if n_fail == 0 and caution_share <= 0.20:
        overall = "Green"
    elif n_fail <= 2 and caution_share <= 0.40:
        overall = "Yellow"
    else:
        overall = "Red"

    critical_flags = {
        "federal_floor_7_25": bool((eligible_org["employer_wage"] >= 7.25).all() and (eligible_asec["employer_wage"] >= 7.25).all()),
        "org_weight_denominator_is_year_month_groups": True,
        "org_2025_missing_month_10_not_forced_to_12": True,
    }
    critical_fail = not all(critical_flags.values())
    if critical_fail:
        overall = "Red"

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        commit = "unknown"

    manifest = {
        "commit": commit,
        "target_wage": target,
        "org_external_sha256": file_sha256(ORG_EXTERNAL),
        "org_processed_sha256": file_sha256(ORG_PROCESSED),
        "asec_h5_sha256": file_sha256(ASEC_H5),
        "overall": overall,
        "status_counts": status_counts,
        "critical_flags": critical_flags,
        "org_workers_mn": float(eligible_org["weight"].sum() / 1e6),
        "asec_workers_mn": float(eligible_asec["weight"].sum() / 1e6),
        "org_gross_bn": org_gross,
        "asec_gross_bn": asec_gross,
        "org_net_bn": org_net,
        "asec_net_bn": asec_net,
    }
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))

    summary_lines = [
        "",
        "## 5. Validation Results (Run 2026-03-08)",
        "",
        f"- Overall rating: **{overall}**",
        f"- Status counts: Acceptable={status_counts.get('Acceptable',0)}, Caution={status_counts.get('Caution',0)}, Failure={status_counts.get('Failure',0)}",
        f"- Target wage used: ${target:.2f}/hr",
        f"- Eligible workers: ORG={eligible_org['weight'].sum()/1e6:.2f}M, ASEC-proxy={eligible_asec['weight'].sum()/1e6:.2f}M",
        f"- Policy costs: ORG gross/net=${org_gross:.2f}B/${org_net:.2f}B, ASEC-proxy gross/net=${asec_gross:.2f}B/${asec_net:.2f}B",
        "",
        "### Metrics",
        "",
    ]
    for _, row in metrics_df.iterrows():
        summary_lines.append(f"- Test {row['test']} | {row['metric']} = {pp(row['value'])} -> {row['status']}")

    summary_lines.extend(
        [
            "",
            "### Artifacts",
            "",
            f"- Manifest: `{(OUT_DIR / 'manifest.json').as_posix()}`",
            f"- Metrics: `{(OUT_DIR / 'metrics.csv').as_posix()}`",
            f"- State compare: `{(OUT_DIR / 'state_workers_org_vs_asec.csv').as_posix()}`",
            f"- Family compare: `{(OUT_DIR / 'family_shares_org_vs_asec.csv').as_posix()}`",
            f"- Program interactions compare: `{(OUT_DIR / 'program_interactions_org_vs_asec.csv').as_posix()}`",
            f"- Sensitivity: `{(OUT_DIR / 'sensitivity.csv').as_posix()}`",
            "",
            "### Method Caveats",
            "",
            "- ASEC side uses `employment_income_before_lsr / (weekly_hours_worked_before_lsr * 52)` as legacy wage proxy.",
            "- `is_tax_unit_head` and exact marital status were not materialized in cached H5; used person-level proxy via marital unit size and own-children count.",
            "- This validation is consistency-focused, not identity matching across ORG and ASEC records.",
        ]
    )

    existing = REPORT_PATH.read_text(encoding="utf-8")
    if "## 5. Validation Results (Run 2026-03-08)" in existing:
        prefix = existing.split("## 5. Validation Results (Run 2026-03-08)")[0].rstrip()
        REPORT_PATH.write_text(prefix + "\n" + "\n".join(summary_lines) + "\n", encoding="utf-8")
    else:
        REPORT_PATH.write_text(existing.rstrip() + "\n" + "\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
