"""
01a_data_ingest.py — Identify eligible hourly workers from CPS ORG microdata.

Replaces the PolicyEngine Microsimulation-based approach. Uses the EPI-constructed
hourly wage (hourly_wage_epi) from the CPS Outgoing Rotation Group to identify
eligible workers — eliminating the part-year contamination that plagued the prior
annual-income / assumed-hours wage proxy.

Architecture (two-source design)
---------------------------------
  CPS ORG (org_workers_{year}.parquet)
    └─ Who is eligible and at what wage rate
  PolicyEngine pre-computed schedules (individual_schedules/)
    └─ How taxes and transfers respond to the subsidy
  These two sources are NEVER merged at the record level.

Eligibility (EIG 80-80 Rule)
-----------------------------
  1. epi_sample_eligible == True  (age ≥16, not self-employed)
  2. hourly_wage_epi_valid == True (non-missing, positive, finite)
  3. age in [16, 64]  (65+ excluded as proxy for Social Security recipients)
  4. employer_wage = max(hourly_wage_epi, FEDERAL_MIN_WAGE) < TARGET_WAGE
     where TARGET_WAGE = 80% of weighted median paid-hourly wage (dynamic)
  5. NOT a tax dependent: exclude relate==301 (child of household head) AND age < 19
     (qualifying child dependents are not eligible for the wage subsidy)

WKSTAT weeks multiplier (confirmed from IPUMS DDI extract #304)
---------------------------------------------------------------
  11 → 52  FT hours (35+), usually FT
  12 → 48  PT non-economic, usually FT (at-work not usual)
  13 → 52  Not at work, usually FT (on leave; FT worker)
  14 → 40  FT hours, usually PT for economic reasons (usual status drives)
  15 → 48  FT hours, usually PT for non-economic reasons
  21 → 40  PT economic, usually FT
  22 → 40  PT, usually PT for economic reasons (chronic involuntary PT)
  41 → 48  PT, usually PT for non-economic reasons (voluntary PT)
  42 → 48  Not at work, usually PT
  50/60/99 → filtered out (unemployed / NIU — no valid wage)

Output schema (unchanged — 02a_descriptive_stats.py reads this directly)
--------------------------------------------------------------------------
WORKSPACE/data/processed/hourly_workers.parquet
  state_code        str    two-letter state abbreviation
  family_type_key   str    single_0c | single_2c | married_0c | married_2c
  employer_wage     float  hourly wage after federal minimum floor
  annual_hours      float  hours_epi × weeks_multiplier(wkstat)
  baseline_income   float  employer_wage × annual_hours
  subsidy_hr        float  0.80 × max(0, TARGET_WAGE − employer_wage)
  subsidy_annual    float  subsidy_hr × annual_hours
  weight            float  earnwt / n_months  (monthly-average population weight)
"""
from __future__ import annotations

import importlib.util
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]          # WORKSPACE/code/

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED
PATH_DATA           = _cfg_mod.PATH_DATA

# ── Policy parameters ─────────────────────────────────────────────────────────
FEDERAL_MIN_WAGE = cfg["ws_base_wage"]    # 7.25
SUBSIDY_PCT      = cfg["ws_subsidy_pct"]  # 0.80
TARGET_PCT       = cfg["ws_target_pct"]   # 0.80

# ── WKSTAT → annual weeks multiplier ─────────────────────────────────────────
# Source: IPUMS DDI codebook for extract #304 (confirmed March 2026).
# See WORKSPACE/docs/org_integration_methodology.md §15.3 for full table.
WKSTAT_WEEKS: dict[int, int] = {
    11: 52,   # Full-time hours (35+), usually full-time
    12: 48,   # Part-time for non-economic reasons, usually full-time
    13: 52,   # Not at work, usually full-time (on leave; FT worker)
    14: 40,   # Full-time hours, usually part-time for economic reasons
    15: 48,   # Full-time hours, usually part-time for non-economic reasons
    21: 40,   # Part-time for economic reasons, usually full-time
    22: 40,   # Part-time hours, usually part-time for economic reasons
    41: 48,   # Part-time hours, usually part-time for non-economic reasons
    42: 48,   # Not at work, usually part-time
}
DEFAULT_WEEKS = 52  # conservative fallback for any unclassified code

# ── FIPS → state abbreviation ─────────────────────────────────────────────────
FIPS_TO_STATE: dict[int, str] = {
     1: "AL",  2: "AK",  4: "AZ",  5: "AR",  6: "CA",  8: "CO",  9: "CT",
    10: "DE", 11: "DC", 12: "FL", 13: "GA", 15: "HI", 16: "ID", 17: "IL",
    18: "IN", 19: "IA", 20: "KS", 21: "KY", 22: "LA", 23: "ME", 24: "MD",
    25: "MA", 26: "MI", 27: "MN", 28: "MS", 29: "MO", 30: "MT", 31: "NE",
    32: "NV", 33: "NH", 34: "NJ", 35: "NM", 36: "NY", 37: "NC", 38: "ND",
    39: "OH", 40: "OK", 41: "OR", 42: "PA", 44: "RI", 45: "SC", 46: "SD",
    47: "TN", 48: "TX", 49: "UT", 50: "VT", 51: "VA", 53: "WA", 54: "WV",
    55: "WI", 56: "WY",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    """Compute weighted median via sorted cumulative weights."""
    idx = np.argsort(values)
    vals_s = values[idx]
    wts_s  = weights[idx]
    cumw   = np.cumsum(wts_s)
    return float(vals_s[np.searchsorted(cumw, cumw[-1] * 0.5)])


def _weeks(wkstat: int) -> int:
    return WKSTAT_WEEKS.get(int(wkstat), DEFAULT_WEEKS)


def _family_key(marst: int, nchild: int) -> str:
    prefix = "married" if marst in {1, 2} else "single"
    suffix = "2c" if nchild >= 1 else "0c"
    return f"{prefix}_{suffix}"


# IPUMS educ codes → grouped education labels
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

def _educ_group(code: int) -> str:
    return _EDUC_MAP.get(int(code), "Unknown")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── 1. Locate input file ──────────────────────────────────────────────────
    ext_dir = PATH_DATA / "external"
    candidates = sorted(ext_dir.glob("org_workers_*.parquet"))
    if not candidates:
        raise FileNotFoundError(
            f"No org_workers_*.parquet found in {ext_dir}.\n"
            "Run 00_export_org_data.py first."
        )
    org_path = candidates[-1]   # most recent year
    print(f"01a | Reading ORG workers from: {org_path.name}")

    org = pd.read_parquet(org_path)
    print(f"  Total rows: {len(org):,}  |  years: {sorted(org['year'].unique())}")

    # ── 2. Dynamic median wage and TARGET_WAGE ────────────────────────────────
    # Weighted median of paid-hourly EPI-eligible workers over all loaded months.
    ph_mask = (
        org["hourly_wage_epi_valid"].astype(bool) &
        org["paid_hourly"].astype(bool) &
        org["epi_sample_eligible"].astype(bool) &
        (org["earnwt"] > 0)
    )
    ph = org[ph_mask]
    if len(ph) == 0:
        raise RuntimeError("No paid-hourly EPI-eligible workers with valid wages found.")

    median_wage = _weighted_median(ph["hourly_wage_epi"].values, ph["earnwt"].values)
    TARGET_WAGE = round(median_wage * TARGET_PCT, 2)
    print(f"  Weighted median wage (paid-hourly): ${median_wage:.2f}/hr")
    print(f"  TARGET_WAGE (80% of median):        ${TARGET_WAGE:.2f}/hr")

    # ── 3. Eligibility filter ─────────────────────────────────────────────────
    # Apply federal minimum wage floor first
    org = org[org["hourly_wage_epi_valid"].astype(bool)].copy()
    org["employer_wage"] = org["hourly_wage_epi"].clip(lower=FEDERAL_MIN_WAGE)

    # Tax dependent exclusion: child of household head (relate==301) under age 19
    # These workers are qualifying child dependents and not eligible for the subsidy.
    # relate column may be absent in older ORG exports — default to no exclusion if missing.
    if "relate" in org.columns:
        is_dependent = (org["relate"] == 301) & (org["age"] < 19)
    else:
        is_dependent = pd.Series(False, index=org.index)

    mask = (
        org["epi_sample_eligible"].astype(bool) &
        (org["age"] >= 16) & (org["age"] <= 64) &
        (org["employer_wage"] < TARGET_WAGE) &
        (org["earnwt"] > 0) &
        ~is_dependent
    )
    eligible = org[mask].copy()
    n_dependents = is_dependent[
        org["epi_sample_eligible"].astype(bool) &
        (org["age"] >= 16) & (org["age"] <= 64) &
        (org["employer_wage"] < TARGET_WAGE) &
        (org["earnwt"] > 0)
    ].sum()
    print(f"  Eligible workers (unweighted rows): {len(eligible):,}  "
          f"(excluded {n_dependents:,} tax dependents)")

    if len(eligible) == 0:
        raise RuntimeError(
            "Zero eligible workers found after filtering. "
            "Check TARGET_WAGE, wage floor, and input data."
        )

    # ── 4. State code ─────────────────────────────────────────────────────────
    n_before = len(eligible)
    eligible["state_code"] = eligible["statefip"].map(FIPS_TO_STATE)

    unknown_fips = eligible[eligible["state_code"].isna()]["statefip"].unique()
    if len(unknown_fips):
        print(f"  [warn] Dropping {eligible['state_code'].isna().sum():,} rows "
              f"with unmapped FIPS codes: {sorted(unknown_fips)}")
    eligible = eligible[eligible["state_code"].notna()].copy()
    if len(eligible) < n_before:
        print(f"  After FIPS filter: {len(eligible):,} rows")

    # ── 5. Family type key ────────────────────────────────────────────────────
    eligible["family_type_key"] = [
        _family_key(int(m), int(n))
        for m, n in zip(eligible["marst"], eligible["nchild"])
    ]

    # ── 6. Annual hours via WKSTAT ────────────────────────────────────────────
    wkstat_vals = eligible["wkstat"].astype(int)
    fallback_mask = ~wkstat_vals.isin(WKSTAT_WEEKS)
    if fallback_mask.sum() > 0:
        unknown_codes = wkstat_vals[fallback_mask].value_counts().to_dict()
        print(f"  [warn] {fallback_mask.sum():,} rows with unclassified WKSTAT "
              f"(defaulting to {DEFAULT_WEEKS} weeks): {unknown_codes}")

    eligible["weeks_multiplier"] = wkstat_vals.map(WKSTAT_WEEKS).fillna(DEFAULT_WEEKS).astype(int)
    eligible["annual_hours"]     = eligible["hours_epi"] * eligible["weeks_multiplier"]

    # Guard: if hours_epi is missing, fall back to config default
    fallback_hours_mask = eligible["annual_hours"].isna() | (eligible["annual_hours"] <= 0)
    if fallback_hours_mask.sum() > 0:
        default_annual = cfg.get("ws_hours_per_year", 2000)
        print(f"  [warn] {fallback_hours_mask.sum():,} rows with missing/zero annual_hours "
              f"— defaulting to {default_annual} hrs/yr")
        eligible.loc[fallback_hours_mask, "annual_hours"] = default_annual

    # ── 7. Subsidy calculation ────────────────────────────────────────────────
    eligible["baseline_income"] = eligible["employer_wage"] * eligible["annual_hours"]
    eligible["subsidy_hr"]      = (
        SUBSIDY_PCT * np.maximum(0.0, TARGET_WAGE - eligible["employer_wage"])
    )
    eligible["subsidy_annual"]  = eligible["subsidy_hr"] * eligible["annual_hours"]

    # ── 8. Population weight (earnwt / n_months) ──────────────────────────────
    # Dividing by the number of unique months converts monthly ORG weights to
    # annual-average weights. DO NOT sum earnwt directly across months.
    # Count unique year-month combinations, not just unique month numbers.
    # This correctly handles multi-year pools where months repeat across years.
    n_months = eligible.groupby(["year", "month"]).ngroups
    eligible["weight"] = eligible["earnwt"] / n_months
    print(f"  Pooled year-months: {n_months}  ->  weight = earnwt / {n_months}")

    # ── 9. Demographics ───────────────────────────────────────────────────────
    eligible["educ_group"] = eligible["educ"].apply(_educ_group)

    # ── 10. Build output DataFrame ────────────────────────────────────────────
    out_cols = [
        "state_code", "family_type_key",
        "employer_wage", "annual_hours", "baseline_income",
        "subsidy_hr", "subsidy_annual", "weight",
        "sex_label", "race_ethnicity", "educ_group", "age_bin",
    ]
    # Only keep demographic cols that were actually exported (older ORG files may lack them)
    out_cols = [c for c in out_cols if c in eligible.columns]
    df = eligible[out_cols].reset_index(drop=True)

    # ── 11. Save ──────────────────────────────────────────────────────────────
    out_path = PATH_DATA_PROCESSED / "hourly_workers.parquet"
    df.to_parquet(out_path, index=False)

    total_workers_mn = df["weight"].sum() / 1e6
    gross_cost_bn    = (df["subsidy_annual"] * df["weight"]).sum() / 1e9
    avg_subsidy      = (df["subsidy_annual"] * df["weight"]).sum() / df["weight"].sum()
    median_subsidy   = np.average(df["subsidy_hr"], weights=df["weight"])

    print(f"\n  Saved: {out_path}")
    print(f"  Weighted eligible workers:  {total_workers_mn:.2f}M  (target: 25–30M)")
    print(f"  Gross annual program cost:  ${gross_cost_bn:.2f}B  (target: $40–60B)")
    print(f"  Average annual subsidy:     ${avg_subsidy:,.0f}/worker")
    print(f"  Weighted mean hourly subsidy: ${median_subsidy:.2f}/hr")

    # State-level sanity check
    state_counts = (
        df.groupby("state_code")["weight"].sum()
        .sort_values(ascending=False)
        .head(10)
        / 1e6
    )
    print(f"\n  Top 10 states by eligible workers (M):")
    for st, wt in state_counts.items():
        print(f"    {st}: {wt:.2f}M")


if __name__ == "__main__":
    main()
