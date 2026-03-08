"""
02a_descriptive_stats.py — Aggregate population-level wage subsidy impacts.

Loads hourly_workers.parquet (from 01a_data_ingest.py), looks up safety net
changes from pre-computed income schedules (built by 01b_precompute_individual.py),
then aggregates with CPS survey weights to produce five output files:

Output files  (WORKSPACE/output/data/intermediate_results/population/)
-----------------------------------------------------------------------
  summary.parquet          Scalar headline metrics (1 row)
  by_state.parquet         Workers, cost, and avg subsidy by state (51 rows)
  by_wage_bracket.parquet  Distribution across $2 wage brackets
  by_family_type.parquet   Distribution across 4 family type categories
  program_interactions.parquet  Per-program net change in spending/revenue
  by_sex.parquet           Distribution by sex (Male / Female)
  by_race_ethnicity.parquet    Distribution by race/ethnicity group
  by_education.parquet     Distribution by education attainment group
  by_age_bin.parquet       Distribution by age bin (16-24 through 55-64)

Safety net lookup
-----------------
For each (family_type_key, state_code) group of workers, load the matching
pre-computed parquet and interpolate benefit/tax values at:
  - baseline_income  (annual employment income without subsidy)
  - subsidy_income   (baseline_income + subsidy_annual)

The delta for each component is subsidy_income value minus baseline_income value.
Net cost to government ≈ gross_subsidy + Σ(Δ benefit programs) + Σ(Δ tax components)
                        = Σ(Δ net_income) for all eligible workers.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]   # WORKSPACE/code/
_APP  = _HERE.parents[2] / "app"

for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg               = _cfg_mod.cfg
PATH_DATA                = _cfg_mod.PATH_DATA
PATH_DATA_PROCESSED      = _cfg_mod.PATH_DATA_PROCESSED
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

from utils.household_sim import (
    COMPONENTS,
    FAMILY_KEYS,
    TRANSFER_KEYS,
    _SCHEDULE_COLS,
    _SCHEDULES_DIR,
)

# ── Constants ──────────────────────────────────────────────────────────────────

_OUT_DIR = PATH_OUTPUT_INTERMEDIATE / "population"
_OUT_DIR.mkdir(parents=True, exist_ok=True)

_INPUT_PATH = PATH_DATA_PROCESSED / "hourly_workers.parquet"

# Wage brackets for distribution charts
_WAGE_BRACKETS = [
    ("$7.25-$9",    7.25,  9.00),
    ("$9-$11",      9.00, 11.00),
    ("$11-$13",    11.00, 13.00),
    ("$13-$16.80", 13.00, 16.80),
]

# Program labels for the interaction table (from COMPONENTS)
_COMPONENT_LABELS: dict[str, str] = {key: label for key, label, _, _ in COMPONENTS}

# Tax keys (stored as negative values for worker, positive for government)
_TAX_KEYS = ["federal_tax", "state_tax", "payroll_tax"]

# Education code -> group label (mirrors 01a_data_ingest.py)
_EDUC_MAP: dict[int, str] = {
    1: "Less than HS",  2: "Less than HS",
   10: "Less than HS", 20: "Less than HS", 30: "Less than HS",
   40: "Less than HS", 50: "Less than HS", 60: "Less than HS",
   71: "HS diploma / GED", 73: "HS diploma / GED",
   81: "Some college / Associate's", 91: "Some college / Associate's",
   92: "Some college / Associate's",
  111: "Bachelor's degree",
  123: "Graduate degree", 124: "Graduate degree", 125: "Graduate degree",
}

# ── Schedule cache ─────────────────────────────────────────────────────────────

_schedule_cache: dict[tuple[str, str], pd.DataFrame | None] = {}


def _load_schedule(family_type_key: str, state_code: str) -> pd.DataFrame | None:
    cache_key = (family_type_key, state_code)
    if cache_key not in _schedule_cache:
        path = _SCHEDULES_DIR / f"{family_type_key}_{state_code}.parquet"
        if path.exists():
            _schedule_cache[cache_key] = pd.read_parquet(path)
        else:
            _schedule_cache[cache_key] = None
    return _schedule_cache[cache_key]


# ── Safety net interaction lookup ──────────────────────────────────────────────

def _lookup_deltas(workers: pd.DataFrame) -> pd.DataFrame:
    """
    For each worker, interpolate component deltas from pre-computed schedules.

    Returns a DataFrame with the same index as `workers`, with one column per
    component in _SCHEDULE_COLS plus 'net_income'.
    """
    delta_cols = _SCHEDULE_COLS  # includes net_income
    out = pd.DataFrame(
        np.nan,
        index=workers.index,
        columns=delta_cols,
    )

    groups = workers.groupby(["family_type_key", "state_code"])
    n_groups = len(groups)
    n_fallback = 0

    for (fkey, state), grp_idx in groups.groups.items():
        grp = workers.loc[grp_idx]
        schedule = _load_schedule(fkey, state)

        # Fallback: try single_0c for same state, then TX as last resort
        if schedule is None:
            schedule = _load_schedule("single_0c", state)
            n_fallback += len(grp_idx)
        if schedule is None:
            schedule = _load_schedule(fkey, "TX")
            n_fallback += len(grp_idx)
        if schedule is None:
            schedule = _load_schedule("single_0c", "TX")
        if schedule is None:
            # No schedule available at all — zero deltas
            for col in delta_cols:
                out.loc[grp_idx, col] = 0.0
            continue

        income_axis = schedule.index.values.astype(float)
        baseline_incomes = grp["baseline_income"].values
        subsidy_incomes  = (grp["baseline_income"] + grp["subsidy_annual"]).values

        for col in delta_cols:
            sched_vals = schedule[col].values
            baseline_v = np.interp(baseline_incomes, income_axis, sched_vals)
            subsidy_v  = np.interp(subsidy_incomes,  income_axis, sched_vals)
            out.loc[grp_idx, col] = subsidy_v - baseline_v

    if n_fallback:
        print(f"  [warn] Used fallback schedule for {n_fallback:,} workers "
              f"(no exact match for their family_type × state).")

    # PolicyEngine's household_net_income excludes in-kind health subsidies
    # (ACA PTC and Medicaid/CHIP). Add their deltas to net_income so that
    # avg_net_income_gain and net_cost_bn reflect total compensation changes.
    if "aca_ptc" in out.columns:
        out["net_income"] = out["net_income"] + out["aca_ptc"]
    if "medicaid_chip" in out.columns:
        out["net_income"] = out["net_income"] + out["medicaid_chip"]

    return out


# ── Aggregation helpers ────────────────────────────────────────────────────────

def _weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    w_sum = weights.sum()
    if w_sum == 0:
        return 0.0
    return float((values * weights).sum() / w_sum)


def _wage_bracket_label(wage: float) -> str:
    for label, lo, hi in _WAGE_BRACKETS:
        if lo <= wage < hi:
            return label
    return "$13-$16.80"


def _agg_by_group(
    workers: pd.DataFrame,
    net_income_delta: np.ndarray,
    total_weights: float,
    gross_cost_bn: float,
    col: str,
    ordered_labels: list[str] | None = None,
    base_group_totals: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Generic weighted aggregation over a categorical column.

    base_group_totals: mapping from group label -> total earnwt in the full
    base population (pre-wage-threshold). Used to compute pct_in_group.
    """
    if ordered_labels:
        valid_mask = workers[col].isin(ordered_labels)
    else:
        valid_mask = workers[col].notna()
    workers = workers[valid_mask]
    net_income_delta = net_income_delta[valid_mask.values]
    rows = []
    groups = workers.groupby(col, observed=True)
    for label, grp in groups:
        w  = grp["weight"].values
        gs = grp["subsidy_annual"].values
        nd = net_income_delta[grp.index]
        eligible_wt = w.sum()
        if base_group_totals is not None and label in base_group_totals:
            base_wt = base_group_totals[label]
            pct_in_group = round(eligible_wt / base_wt * 100, 1) if base_wt > 0 else None
        else:
            pct_in_group = None
        rows.append({
            col:                   label,
            "n_workers_k":         round(eligible_wt / 1e3, 1),
            "pct_of_recipients":   round(eligible_wt / total_weights * 100, 1),
            "pct_in_group":        pct_in_group,
            "avg_annual_subsidy":  round(_weighted_mean(gs, w), 0),
            "avg_net_income_gain": round(_weighted_mean(nd, w), 0),
            "gross_cost_mn":       round((gs * w).sum() / 1e6, 1),
        })
    df = pd.DataFrame(rows)
    if ordered_labels:
        df[col] = pd.Categorical(df[col], categories=ordered_labels, ordered=True)
        df = df.sort_values(col).reset_index(drop=True)
        df[col] = df[col].astype(str)
    return df


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not _INPUT_PATH.exists():
        raise FileNotFoundError(
            f"hourly_workers.parquet not found at {_INPUT_PATH}\n"
            "Run 01a_data_ingest.py first."
        )

    print("02a | Loading hourly_workers.parquet …")
    workers = pd.read_parquet(_INPUT_PATH)
    print(f"  Records: {len(workers):,}")

    weights = workers["weight"].values
    gross_subsidies = workers["subsidy_annual"].values

    total_workers_mn = weights.sum() / 1e6
    gross_cost_bn    = (gross_subsidies * weights).sum() / 1e9

    # ── Safety net interaction deltas ─────────────────────────────────────────
    print("02a | Computing safety net interaction deltas …")
    deltas = _lookup_deltas(workers)

    # Net income delta = gross_subsidy + all program and tax deltas
    # (net_income is already computed in the schedule, so just use it)
    net_income_delta = deltas["net_income"].values

    # Government net cost = sum of delta_net_income (worker gains = govt spends)
    net_cost_bn = (net_income_delta * weights).sum() / 1e9
    avg_subsidy  = float((gross_subsidies * weights).sum() / weights.sum())

    # ── Summary ───────────────────────────────────────────────────────────────
    print("02a | Building summary …")
    summary = pd.DataFrame([{
        "gross_cost_bn":      round(gross_cost_bn, 2),
        "net_cost_bn":        round(net_cost_bn, 2),
        "n_workers_mn":       round(total_workers_mn, 2),
        "avg_annual_subsidy": round(avg_subsidy, 0),
        "n_records_raw":      len(workers),
    }])
    summary.to_parquet(_OUT_DIR / "summary.parquet", index=False)
    print(f"  Gross cost: ${gross_cost_bn:.2f}B | Net cost: ${net_cost_bn:.2f}B | "
          f"Workers: {total_workers_mn:.2f}M | Avg subsidy: ${avg_subsidy:,.0f}")

    # ── By state ──────────────────────────────────────────────────────────────
    print("02a | Aggregating by state …")
    state_rows = []
    for state_code, grp in workers.groupby("state_code"):
        w  = grp["weight"].values
        gs = grp["subsidy_annual"].values
        nd = net_income_delta[grp.index]
        state_rows.append({
            "state_code":        state_code,
            "n_workers_k":       round(w.sum() / 1e3, 1),
            "gross_cost_mn":     round((gs * w).sum() / 1e6, 1),
            "net_cost_mn":       round((nd * w).sum() / 1e6, 1),
            "avg_annual_subsidy": round(_weighted_mean(gs, w), 0),
        })
    by_state = pd.DataFrame(state_rows).sort_values("state_code")
    by_state.to_parquet(_OUT_DIR / "by_state.parquet", index=False)

    # ── By wage bracket ───────────────────────────────────────────────────────
    print("02a | Aggregating by wage bracket …")
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

    # ── By family type ────────────────────────────────────────────────────────
    print("02a | Aggregating by family type …")
    _FT_LABELS = {
        "single_0c":   "Single, no children",
        "single_2c":   "Single, with children",
        "married_0c":  "Married, no children",
        "married_2c":  "Married, with children",
    }
    ft_rows = []
    for fkey, grp in workers.groupby("family_type_key"):
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

    # ── Program interactions ──────────────────────────────────────────────────
    print("02a | Computing program interaction table …")
    prog_rows = []
    for col in _SCHEDULE_COLS:
        if col == "net_income":
            continue
        delta_vals = deltas[col].values
        avg_delta  = _weighted_mean(delta_vals, weights)
        total_mn   = (delta_vals * weights).sum() / 1e6
        label      = _COMPONENT_LABELS.get(col, col)
        prog_rows.append({
            "program":              label,
            "key":                  col,
            "avg_delta_per_worker": round(avg_delta, 0),
            "total_delta_mn":       round(total_mn, 1),
            "pct_of_gross_cost":    round(total_mn / (gross_cost_bn * 1e3) * 100, 1),
        })
    program_interactions = pd.DataFrame(prog_rows)
    # Also add gross wage subsidy row for context
    program_interactions = pd.concat([
        pd.DataFrame([{
            "program":              "Wage subsidy",
            "key":                  "wage_subsidy",
            "avg_delta_per_worker": round(avg_subsidy, 0),
            "total_delta_mn":       round(gross_cost_bn * 1e3, 1),
            "pct_of_gross_cost":    100.0,
        }]),
        program_interactions,
    ], ignore_index=True)
    program_interactions.to_parquet(_OUT_DIR / "program_interactions.parquet", index=False)

    # ── Base population for pct_in_group denominators ────────────────────────
    # Load the full ORG file and apply the same filter as 01a minus the wage
    # threshold to get total weighted workers in each demographic group.
    # earnwt / n_months cancels in the ratio, so raw earnwt is used here.
    print("02a | Computing base population group totals ...")
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
            if "educ" in org_base.columns:
                org_base["educ_group"] = org_base["educ"].map(
                    lambda c: _EDUC_MAP.get(int(c), "Unknown")
                )
            # Normalize by n_months so the denominator matches the eligible
            # workers' weight = earnwt / n_months used in _agg_by_group.
            n_months_base = org_base.groupby(["year", "month"]).ngroups
            for col in ["sex_label", "race_ethnicity", "educ_group", "age_bin"]:
                if col in org_base.columns:
                    _base_group_totals[col] = (
                        org_base.groupby(col, observed=True)["earnwt"]
                        .sum()
                        .div(n_months_base)
                        .to_dict()
                    )
            print(f"  Base population rows: {len(org_base):,}  "
                  f"(n_months={n_months_base})")
        else:
            print("  [warn] No ORG file found — pct_in_group will be omitted.")
    except Exception as e:
        print(f"  [warn] Base population load failed ({e}) — pct_in_group will be omitted.")

    # ── Demographic breakdowns (only if columns are present) ──────────────────
    _EDUC_ORDER = [
        "Less than HS", "HS diploma / GED",
        "Some college / Associate's", "Bachelor's degree", "Graduate degree",
    ]
    _AGE_ORDER = ["16-24", "25-34", "35-44", "45-54", "55-64"]

    demo_outputs: dict[str, pd.DataFrame] = {}

    if "sex_label" in workers.columns:
        print("02a | Aggregating by sex ...")
        demo_outputs["by_sex"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), gross_cost_bn, "sex_label",
            base_group_totals=_base_group_totals.get("sex_label"),
        )

    if "race_ethnicity" in workers.columns:
        print("02a | Aggregating by race/ethnicity ...")
        demo_outputs["by_race_ethnicity"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), gross_cost_bn, "race_ethnicity",
            base_group_totals=_base_group_totals.get("race_ethnicity"),
        )

    if "educ_group" in workers.columns:
        print("02a | Aggregating by education ...")
        demo_outputs["by_education"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), gross_cost_bn, "educ_group",
            ordered_labels=_EDUC_ORDER,
            base_group_totals=_base_group_totals.get("educ_group"),
        )

    if "age_bin" in workers.columns:
        print("02a | Aggregating by age bin ...")
        demo_outputs["by_age_bin"] = _agg_by_group(
            workers, net_income_delta, weights.sum(), gross_cost_bn, "age_bin",
            ordered_labels=_AGE_ORDER,
            base_group_totals=_base_group_totals.get("age_bin"),
        )

    for name, df in demo_outputs.items():
        df.to_parquet(_OUT_DIR / f"{name}.parquet", index=False)

    print(f"\n02a | Complete. Output written to: {_OUT_DIR}")
    print(f"  summary.parquet")
    print(f"  by_state.parquet          ({len(by_state)} rows)")
    print(f"  by_wage_bracket.parquet   ({len(by_wage_bracket)} rows)")
    print(f"  by_family_type.parquet    ({len(by_family_type)} rows)")
    print(f"  program_interactions.parquet ({len(program_interactions)} rows)")
    for name, df in demo_outputs.items():
        print(f"  {name}.parquet ({len(df)} rows)")


if __name__ == "__main__":
    main()
