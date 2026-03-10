"""
03a_apply_matched_to_population.py
Re-run the population aggregation using matched ASEC household schedules.

This script is the matched-pipeline equivalent of 02a_descriptive_stats.py.
The key difference is in the safety-net interaction lookup:

  02a (stylised):  group workers by (family_type_key, state_code) and apply
                   one shared PE schedule to the entire group.  Spouse income
                   is assumed to be zero; child ages are fixed archetypes.

  03a (matched):   for each worker, look up the PE schedule that was pre-
                   computed for their matched ASEC household configuration
                   (real spouse income, real child ages, real n_adults).
                   Workers whose matched config has no pre-computed schedule
                   fall back to the stylised schedule.

Output
------
  WORKSPACE/output/data/intermediate_results/matched_population/
    summary.parquet
    by_state.parquet
    by_wage_bracket.parquet
    by_family_type.parquet
    program_interactions.parquet
    comparison.parquet      â€” side-by-side diff vs. stylised outputs

The matched_population/ outputs do NOT overwrite the existing population/
outputs, so the two approaches can be compared before deciding to promote
the matched results.

Usage
-----
    python WORKSPACE/code/03_matched_analysis/03a_apply_matched_to_population.py

Prerequisites
-------------
    01c_asec_pull.R              â†’  asec_persons_{YYYY}.parquet
    01d_asec_preprocess.py       â†’  asec_earners_{YYYY}.parquet
    01e_match_org_to_asec.py     â†’  org_asec_matches.parquet
    01f_precompute_matched_schedules.py  â†’  matched_schedules/{key}_{state}.parquet
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# â”€â”€ Path setup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]          # WORKSPACE/code/
_APP  = _HERE.parents[2] / "app"

for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
PATH_DATA                = _cfg_mod.PATH_DATA
PATH_DATA_PROCESSED      = _cfg_mod.PATH_DATA_PROCESSED
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

from utils.household_sim import (       # noqa: E402
    COMPONENTS,
    _SCHEDULE_COLS,
    _SCHEDULES_DIR,
    load_matched_schedule,
    matched_schedule_available,
    matched_schedule_path,
)

# â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_EXTERNAL_DIR  = PATH_DATA / "external"
_MATCHES_PATH  = _EXTERNAL_DIR / "org_asec_matches.parquet"
_OUT_DIR       = PATH_OUTPUT_INTERMEDIATE / "matched_population"
_STYLISED_DIR  = PATH_OUTPUT_INTERMEDIATE / "population"   # for comparison
_OUT_DIR.mkdir(parents=True, exist_ok=True)

_COMPONENT_LABELS: dict[str, str] = {key: label for key, label, _, _ in COMPONENTS}

_WAGE_BRACKETS = [
    ("$7.25-$9",    7.25,  9.00),
    ("$9-$11",      9.00, 11.00),
    ("$11-$13",    11.00, 13.00),
    ("$13-$16.80", 13.00, 16.80),
]

_EDUC_MAP: dict[int, str] = {
     1: "Less than HS",  2: "Less than HS",
    10: "Less than HS", 20: "Less than HS", 30: "Less than HS",
    40: "Less than HS", 50: "Less than HS", 60: "Less than HS",
    71: "HS diploma / GED", 72: "HS diploma / GED", 73: "HS diploma / GED",
    81: "Some college / Associate's", 91: "Some college / Associate's", 92: "Some college / Associate's",
   111: "Bachelor's degree", 121: "Graduate degree", 122: "Graduate degree", 123: "Graduate degree", 124: "Graduate degree", 125: "Graduate degree",
}

# WKSTAT â†’ annual weeks (mirrors 01a_data_ingest.py)
_WKSTAT_WEEKS: dict[int, float] = {
    11: 52, 12: 48, 13: 52, 14: 40, 15: 48,
    21: 40, 22: 40, 41: 48, 42: 48,
}
_DEFAULT_WEEKS = 52.0

# Subsidy parameters (mirrors DEFAULT_PARAMS in utils/subsidy.py)
_TARGET_PCT    = float(_cfg_mod.cfg.get("ws_target_pct", 0.80))
_SUBSIDY_PCT   = float(_cfg_mod.cfg.get("ws_subsidy_pct", 0.80))
_FED_MIN_WAGE  = float(_cfg_mod.cfg.get("ws_base_wage", 7.25))
_TARGET_WAGE   = float(_cfg_mod.cfg.get("ws_target_wage", 16.80))

# â”€â”€ Config-key helpers (must match 01f_precompute_matched_schedules.py exactly) â”€â”€

_SPOUSE_BUCKET_BOUNDS = [0, 1, 7_500, 12_500, 17_500, 22_500, 27_500, 37_500, 52_500, 72_500]
_SPOUSE_BUCKET_REPRS  = [0, 5_000, 10_000, 15_000, 20_000, 25_000, 32_500, 45_000, 62_500, 87_500]


def _discretise_child_age(age: int) -> int:
    if age <= 2:  return 1
    if age <= 5:  return 4
    if age <= 12: return 9
    return 15


def _discretise_spouse_income(income: float) -> float:
    income = max(0.0, income)
    for i in range(len(_SPOUSE_BUCKET_BOUNDS) - 1, -1, -1):
        if income >= _SPOUSE_BUCKET_BOUNDS[i]:
            return float(_SPOUSE_BUCKET_REPRS[i])
    return 0.0


def _config_key(n_adults: int, n_children: int, children_ages_repr: tuple[int, ...], spouse_bucket: float) -> str:
    ages_str  = "_".join(map(str, children_ages_repr)) if children_ages_repr else "none"
    spouse_k  = int(spouse_bucket // 1000)
    return f"{n_adults}a_{n_children}c_{ages_str}_s{spouse_k}k"


def _worker_config_key(row: "pd.Series") -> str:
    """Derive the matched config key for one worker row from org_asec_matches."""
    n_adults    = 2 if row.get("marital_binary", 0) == 1 else 1
    spouse_raw  = float(row.get("asec_spouse_income", 0.0) or 0.0)
    spouse_buck = _discretise_spouse_income(spouse_raw)

    ages_raw = row.get("asec_children_ages", "[]")
    if isinstance(ages_raw, str):
        try:
            ages_raw = json.loads(ages_raw)
        except Exception:
            ages_raw = []
    ages_raw   = [int(a) for a in ages_raw if 0 <= int(a) < 18][:3]
    ages_repr  = tuple(sorted(_discretise_child_age(a) for a in ages_raw))
    n_children = len(ages_repr)

    return _config_key(n_adults, n_children, ages_repr, spouse_buck)


def _matched_family_type_key(row: "pd.Series") -> str:
    """
    Derive family-type buckets from matched ASEC household context.

    This is used for matched-population reporting so the Population-Level
    Impacts tab reflects matched spouse/child context rather than the ORG-side
    household snapshot.
    """
    spouse_income = float(row.get("asec_spouse_income", 0.0) or 0.0)
    n_adults = 2 if (row.get("marital_binary", 0) == 1 or spouse_income > 0.0) else 1

    ages_raw = row.get("asec_children_ages", "[]")
    if isinstance(ages_raw, str):
        try:
            ages_raw = json.loads(ages_raw)
        except Exception:
            ages_raw = []
    n_children = len([int(a) for a in ages_raw if 0 <= int(a) < 18][:3])
    if n_children == 0:
        n_children = int(row.get("asec_n_children", 0) or 0)

    prefix = "married" if n_adults == 2 else "single"
    suffix = "2c" if n_children >= 1 else "0c"
    return f"{prefix}_{suffix}"


# â”€â”€ Schedule cache â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_matched_cache:   dict[tuple[str, str], pd.DataFrame | None] = {}
_stylised_cache:  dict[str, pd.DataFrame | None]             = {}


def _load_matched(config_key: str, state: str) -> pd.DataFrame | None:
    k = (config_key, state)
    if k not in _matched_cache:
        _matched_cache[k] = load_matched_schedule(config_key, state)
    return _matched_cache[k]


def _load_stylised(family_type_key: str, state: str) -> pd.DataFrame | None:
    k = f"{family_type_key}_{state}"
    if k not in _stylised_cache:
        path = _SCHEDULES_DIR / f"{family_type_key}_{state}.parquet"
        _stylised_cache[k] = pd.read_parquet(path) if path.exists() else None
    return _stylised_cache[k]


# â”€â”€ Worker economics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _compute_economics(workers: pd.DataFrame, target_wage: float) -> pd.DataFrame:
    """
    Derive annual_hours, baseline_income, subsidy_hr, subsidy_annual, weight
    from the raw ORG columns in org_asec_matches.parquet.
    Mirrors the logic in 01a_data_ingest.py.
    """
    workers = workers.copy()
    workers["employer_wage"] = (
        pd.to_numeric(workers["hourly_wage_epi"], errors="coerce")
        .fillna(_FED_MIN_WAGE)
        .clip(lower=_FED_MIN_WAGE)
    )
    workers["annual_hours"] = (
        workers["wkstat"].map(_WKSTAT_WEEKS).fillna(_DEFAULT_WEEKS)
        * pd.to_numeric(workers["hours_epi"], errors="coerce")
    )
    fallback_hours = workers["annual_hours"].isna() | (workers["annual_hours"] <= 0)
    workers.loc[fallback_hours, "annual_hours"] = 2000.0
    workers["baseline_income"] = workers["employer_wage"] * workers["annual_hours"]
    workers["subsidy_hr"]      = (
        _SUBSIDY_PCT * (target_wage - workers["employer_wage"]).clip(lower=0.0)
    )
    workers["subsidy_annual"]  = workers["subsidy_hr"] * workers["annual_hours"]

    n_months = workers.groupby(["year", "month"]).ngroups
    workers["weight"] = workers["earnwt"] / max(n_months, 1)

    return workers


# â”€â”€ Matched delta lookup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _lookup_matched_deltas(workers: pd.DataFrame) -> pd.DataFrame:
    """
    For each worker, interpolate component deltas from the matched PE schedule.

    Falls back to the stylised (family_type_key, state_code) schedule when:
      - the matched config schedule doesn't exist (01f not yet run for that config)
      - the matched schedule file is missing for any other reason

    Returns a DataFrame indexed like `workers` with one column per _SCHEDULE_COLS.
    """
    out = pd.DataFrame(
        np.nan,
        index=workers.index,
        columns=_SCHEDULE_COLS,
    )

    n_matched   = 0
    n_fallback  = 0
    n_missing   = 0

    for idx, row in workers.iterrows():
        baseline_inc = float(row["baseline_income"])
        subsidy_inc  = float(row["baseline_income"] + row["subsidy_annual"])
        state        = str(row["state_code"])
        fkey         = str(row.get("family_type_key", "single_0c"))

        config_key = _worker_config_key(row)
        schedule   = _load_matched(config_key, state)

        if schedule is None:
            # Fall back to stylised schedule for this family_type Ã— state
            schedule  = _load_stylised(fkey, state)
            n_fallback += 1
        else:
            n_matched += 1

        if schedule is None:
            n_missing += 1
            for col in _SCHEDULE_COLS:
                out.at[idx, col] = 0.0
            continue

        income_axis = schedule.index.values.astype(float)
        for col in _SCHEDULE_COLS:
            sched_vals = schedule[col].values
            baseline_v = float(np.interp(baseline_inc, income_axis, sched_vals))
            subsidy_v  = float(np.interp(subsidy_inc,  income_axis, sched_vals))
            out.at[idx, col] = subsidy_v - baseline_v

    print(
        f"  Delta lookup: {n_matched:,} matched schedule, "
        f"{n_fallback:,} stylised fallback, {n_missing:,} missing (zeroed)"
    )

    # ACA PTC and Medicaid/CHIP are in-kind â€” add to net_income for consistency
    if "aca_ptc" in out.columns:
        out["net_income"] = out["net_income"] + out["aca_ptc"]
    if "medicaid_chip" in out.columns:
        out["net_income"] = out["net_income"] + out["medicaid_chip"]

    return out


# â”€â”€ Aggregation helpers (same as 02a) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return 0.0
    v = values[mask]
    w = weights[mask]
    order = np.argsort(v)
    v = v[order]
    w = w[order]
    cdf = np.cumsum(w)
    cutoff = 0.5 * w.sum()
    return float(v[np.searchsorted(cdf, cutoff, side="left")])


def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if not mask.any():
        return 0.0
    v = values[mask]
    w = weights[mask]
    return float(np.dot(v, w) / w.sum())


def _wage_bracket_label(wage: float) -> str:
    for label, lo, hi in _WAGE_BRACKETS:
        if lo <= wage < hi:
            return label
    return "$13-$16.80"


def _agg_by_group(
    workers: pd.DataFrame,
    net_income_delta: np.ndarray,
    total_weights: float,
    col: str,
    ordered_labels: list[str] | None = None,
    base_group_totals: dict[str, float] | None = None,
) -> pd.DataFrame:
    if ordered_labels:
        valid_mask = workers[col].isin(ordered_labels)
    else:
        valid_mask = workers[col].notna()
    workers = workers[valid_mask]
    net_income_delta = net_income_delta[valid_mask.values]

    rows = []
    groups = workers.groupby(col, observed=True)
    for label, grp in groups:
        w = grp["weight"].values
        gs = grp["subsidy_annual"].values
        nd = net_income_delta[grp.index]
        eligible_wt = w.sum()
        if base_group_totals is not None and label in base_group_totals:
            base_wt = base_group_totals[label]
            pct_in_group = round(eligible_wt / base_wt * 100, 1) if base_wt > 0 else None
        else:
            pct_in_group = None
        rows.append({
            col: label,
            "n_workers_k": round(eligible_wt / 1e3, 1),
            "pct_of_recipients": round(eligible_wt / total_weights * 100, 1),
            "pct_in_group": pct_in_group,
            "avg_annual_subsidy": round(_weighted_mean(gs, w), 0),
            "avg_net_income_gain": round(_weighted_mean(nd, w), 0),
            "gross_cost_mn": round((gs * w).sum() / 1e6, 1),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=[
            col, "n_workers_k", "pct_of_recipients", "pct_in_group",
            "avg_annual_subsidy", "avg_net_income_gain", "gross_cost_mn",
        ])
    if ordered_labels:
        df[col] = pd.Categorical(df[col], categories=ordered_labels, ordered=True)
        df = df.sort_values(col).reset_index(drop=True)
        df[col] = df[col].astype(str)
    return df


# â”€â”€ Main â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main() -> None:
    if not _MATCHES_PATH.exists():
        raise FileNotFoundError(
            f"{_MATCHES_PATH} not found.\n"
            "Run 01e_match_org_to_asec.py first."
        )

    print("03a | Loading org_asec_matches.parquet ...")
    workers = pd.read_parquet(_MATCHES_PATH)
    print(f"  {len(workers):,} matched ORG workers")

    target_wage = _TARGET_WAGE
    print(f"  Target wage: ${target_wage:.2f}/hr  (configured)")

    # â”€â”€ Derive economics â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Computing worker economics ...")
    workers = _compute_economics(workers, target_wage)

    # Derive ORG-side family_type_key for stylised fallback schedule lookup.
    def _fkey(row):
        married = row["marst"] in {1, 2}
        has_children = int(row.get("nchild", 0)) >= 1
        prefix = "married" if married else "single"
        suffix = "2c" if has_children else "0c"
        return f"{prefix}_{suffix}"
    workers["family_type_key"] = workers.apply(_fkey, axis=1)
    workers["matched_family_type_key"] = workers.apply(_matched_family_type_key, axis=1)

    weights         = workers["weight"].values
    gross_subsidies = workers["subsidy_annual"].values
    total_workers_mn = weights.sum() / 1e6
    gross_cost_bn    = (gross_subsidies * weights).sum() / 1e9

    # â”€â”€ Matched delta lookup â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Looking up matched fiscal interaction deltas ...")
    deltas           = _lookup_matched_deltas(workers)
    net_income_delta = deltas["net_income"].values
    net_cost_bn      = (net_income_delta * weights).sum() / 1e9
    avg_subsidy      = _weighted_mean(gross_subsidies, weights)

    # â”€â”€ Summary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Building summary ...")
    summary = pd.DataFrame([{
        "gross_cost_bn":      round(gross_cost_bn, 2),
        "net_cost_bn":        round(net_cost_bn, 2),
        "n_workers_mn":       round(total_workers_mn, 2),
        "avg_annual_subsidy": round(avg_subsidy, 0),
        "n_records_raw":      len(workers),
        "source":             "matched",
    }])
    summary.to_parquet(_OUT_DIR / "summary.parquet", index=False)
    print(f"  Gross cost: ${gross_cost_bn:.2f}B | Net cost: ${net_cost_bn:.2f}B | "
          f"Workers: {total_workers_mn:.2f}M | Avg subsidy: ${avg_subsidy:,.0f}")

    # â”€â”€ By state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Base-population denominators for "pct_in_group" rates
    _state_base_totals: dict[str, float] = {}
    _base_group_totals: dict[str, dict[str, float]] = {}
    try:
        org_candidates = sorted((PATH_DATA / "external").glob("org_workers_*.parquet"))
        if org_candidates:
            org_raw = pd.read_parquet(org_candidates[-1])
            base_mask = (
                org_raw["epi_sample_eligible"].astype(bool) &
                org_raw["hourly_wage_epi_valid"].astype(bool) &
                (org_raw["age"] >= 16) & (org_raw["age"] <= 64) &
                (org_raw["earnwt"] > 0)
            )
            if "relate" in org_raw.columns:
                base_mask &= ~((org_raw["relate"] == 301) & (org_raw["age"] < 19))
            org_base = org_raw[base_mask].copy()
            n_months_base = org_base.groupby(["year", "month"]).ngroups

            fips_to_state = {
                 1: "AL",  2: "AK",  4: "AZ",  5: "AR",  6: "CA",  8: "CO",  9: "CT",
                10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL",
                18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD",
                25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
                32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND",
                39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD",
                47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
                55: "WI", 56: "WY",
            }
            org_base["_state_code"] = org_base["statefip"].map(fips_to_state)
            _state_base_totals = (
                org_base.groupby("_state_code", observed=True)["earnwt"]
                .sum().div(max(n_months_base, 1)).to_dict()
            )

            if "educ" in org_base.columns:
                org_base["educ_group"] = pd.cut(
                    org_base["educ"],
                    bins=[0, 60, 73, 111, 999],
                    labels=["lt_hs", "hs", "some_college", "ba_plus"],
                    right=True,
                ).astype(str)
            for col in ["sex_label", "race_ethnicity", "educ_group", "age_bin"]:
                if col in org_base.columns:
                    _base_group_totals[col] = (
                        org_base.groupby(col, observed=True)["earnwt"]
                        .sum()
                        .div(max(n_months_base, 1))
                        .to_dict()
                    )
    except Exception as e:
        print(f"  [warn] Base population denominator load failed ({e})")

    print("03a | Aggregating by state ...")
    state_rows = []
    for state_code, grp in workers.groupby("state_code"):
        w  = grp["weight"].values
        gs = grp["subsidy_annual"].values
        nd = net_income_delta[grp.index]
        eligible_wt = w.sum()
        base_wt = _state_base_totals.get(state_code, 0)
        pct_in_group = round(eligible_wt / base_wt * 100, 1) if base_wt > 0 else None
        state_rows.append({
            "state_code":         state_code,
            "n_workers_k":        round(eligible_wt / 1e3, 1),
            "pct_in_group":       pct_in_group,
            "gross_cost_mn":      round((gs * w).sum() / 1e6, 1),
            "net_cost_mn":        round((nd * w).sum() / 1e6, 1),
            "avg_annual_subsidy": round(_weighted_mean(gs, w), 0),
        })
    by_state = pd.DataFrame(state_rows).sort_values("state_code")
    by_state.to_parquet(_OUT_DIR / "by_state.parquet", index=False)

    # â”€â”€ By wage bracket â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Aggregating by wage bracket ...")
    workers["wage_bracket"] = workers["employer_wage"].apply(_wage_bracket_label)
    bracket_rows = []
    for label, lo, hi in _WAGE_BRACKETS:
        grp = workers[workers["wage_bracket"] == label]
        if len(grp) == 0:
            continue
        w  = grp["weight"].values
        gs = grp["subsidy_annual"].values
        bracket_rows.append({
            "wage_bracket":       label,
            "wage_min":           lo,
            "wage_max":           hi,
            "n_workers_k":        round(w.sum() / 1e3, 1),
            "pct_workers":        round(w.sum() / weights.sum() * 100, 1),
            "avg_hourly_subsidy": round(_weighted_mean(grp["subsidy_hr"].values, w), 2),
            "avg_annual_subsidy": round(_weighted_mean(gs, w), 0),
        })
    by_wage_bracket = pd.DataFrame(bracket_rows)
    by_wage_bracket.to_parquet(_OUT_DIR / "by_wage_bracket.parquet", index=False)

    # â”€â”€ By family type â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Aggregating by family type ...")
    ft_rows = []
    _FT_LABELS = {
        "single_0c":  "Single, no children",
        "single_2c":  "Single, with children",
        "married_0c": "Married, no children",
        "married_2c": "Married, with children",
    }
    for fkey, grp in workers.groupby("matched_family_type_key"):
        w  = grp["weight"].values
        gs = grp["subsidy_annual"].values
        nd = net_income_delta[grp.index]
        ft_rows.append({
            "family_type":         _FT_LABELS.get(fkey, fkey),
            "family_type_key":     fkey,
            "n_workers_k":         round(w.sum() / 1e3, 1),
            "pct_workers":         round(w.sum() / weights.sum() * 100, 1),
            "avg_annual_subsidy":  round(_weighted_mean(gs, w), 0),
            "avg_net_income_gain": round(_weighted_mean(nd, w), 0),
        })
    by_family_type = pd.DataFrame(ft_rows)
    by_family_type.to_parquet(_OUT_DIR / "by_family_type.parquet", index=False)

    # â”€â”€ Program interactions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Computing program interaction table ...")
    prog_rows = []
    for col in _SCHEDULE_COLS:
        if col == "net_income":
            continue
        delta_vals = deltas[col].values
        avg_delta  = _weighted_mean(delta_vals, weights)
        total_mn   = (delta_vals * weights).sum() / 1e6
        prog_rows.append({
            "program":              _COMPONENT_LABELS.get(col, col),
            "key":                  col,
            "avg_delta_per_worker": round(avg_delta, 0),
            "total_delta_mn":       round(total_mn, 1),
            "pct_of_gross_cost":    round(total_mn / (gross_cost_bn * 1e3) * 100, 1),
        })
    program_interactions = pd.concat([
        pd.DataFrame([{
            "program":              "Wage subsidy",
            "key":                  "wage_subsidy",
            "avg_delta_per_worker": round(avg_subsidy, 0),
            "total_delta_mn":       round(gross_cost_bn * 1e3, 1),
            "pct_of_gross_cost":    100.0,
        }]),
        pd.DataFrame(prog_rows),
    ], ignore_index=True)
    program_interactions.to_parquet(_OUT_DIR / "program_interactions.parquet", index=False)
    # Demographic breakdown outputs (mirrors 02a schema)
    _EDUC_ORDER = ["lt_hs", "hs", "some_college", "ba_plus"]
    _AGE_ORDER = ["16-24", "25-34", "35-44", "45-54", "55-64"]

    demo_outputs: dict[str, pd.DataFrame] = {}
    if "sex_label" in workers.columns:
        print("03a | Aggregating by sex ...")
        demo_outputs["by_sex"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), "sex_label",
            base_group_totals=_base_group_totals.get("sex_label"),
        )
    if "race_ethnicity" in workers.columns:
        print("03a | Aggregating by race/ethnicity ...")
        demo_outputs["by_race_ethnicity"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), "race_ethnicity",
            base_group_totals=_base_group_totals.get("race_ethnicity"),
        )
    if "educ_group" in workers.columns:
        print("03a | Aggregating by education ...")
        demo_outputs["by_education"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), "educ_group",
            ordered_labels=_EDUC_ORDER,
            base_group_totals=_base_group_totals.get("educ_group"),
        )
    if "age_bin" in workers.columns:
        print("03a | Aggregating by age bin ...")
        demo_outputs["by_age_bin"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), "age_bin",
            ordered_labels=_AGE_ORDER,
            base_group_totals=_base_group_totals.get("age_bin"),
        )
    for name, df in demo_outputs.items():
        df.to_parquet(_OUT_DIR / f"{name}.parquet", index=False)

    # â”€â”€ Comparison against stylised estimates â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print("03a | Building comparison vs. stylised estimates ...")
    stylised_summary_path = _STYLISED_DIR / "summary.parquet"
    if stylised_summary_path.exists():
        s = pd.read_parquet(stylised_summary_path).iloc[0]
        comparison = pd.DataFrame([{
            "metric":                "Gross cost ($B)",
            "stylised":              s.get("gross_cost_bn", None),
            "matched":               round(gross_cost_bn, 2),
        }, {
            "metric":                "Net cost ($B)",
            "stylised":              s.get("net_cost_bn", None),
            "matched":               round(net_cost_bn, 2),
        }, {
            "metric":                "Workers (M)",
            "stylised":              s.get("n_workers_mn", None),
            "matched":               round(total_workers_mn, 2),
        }, {
            "metric":                "Avg annual subsidy ($)",
            "stylised":              s.get("avg_annual_subsidy", None),
            "matched":               round(avg_subsidy, 0),
        }])
        comparison["delta"] = comparison["matched"] - comparison["stylised"]
        comparison["delta_pct"] = (
            (comparison["delta"] / comparison["stylised"].abs() * 100)
            .round(1)
        )
        comparison.to_parquet(_OUT_DIR / "comparison.parquet", index=False)
        print("\n  Stylised vs. matched comparison:")
        print(comparison.to_string(index=False))

    # â”€â”€ Program-level comparison â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        stylised_prog_path = _STYLISED_DIR / "program_interactions.parquet"
        if stylised_prog_path.exists():
            sp = pd.read_parquet(stylised_prog_path).set_index("key")
            mp = program_interactions.set_index("key")
            common = sp.index.intersection(mp.index)
            prog_comp = pd.DataFrame({
                "program":    sp.loc[common, "program"],
                "stylised_delta_mn": sp.loc[common, "total_delta_mn"],
                "matched_delta_mn":  mp.loc[common, "total_delta_mn"],
            })
            prog_comp["diff_mn"] = (
                prog_comp["matched_delta_mn"] - prog_comp["stylised_delta_mn"]
            ).round(1)
            prog_comp_path = _OUT_DIR / "program_comparison.parquet"
            prog_comp.to_parquet(prog_comp_path, index=False)
            print("\n  Program-level delta comparison (matched - stylised, $M):")
            print(prog_comp.to_string(index=False))
    else:
        print("  [info] No stylised summary found â€” skipping comparison.")

    print(f"\n03a | Complete. Output written to:\n  {_OUT_DIR}")


if __name__ == "__main__":
    main()
