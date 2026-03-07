"""
01a_data_ingest.py — Extract eligible hourly workers from PolicyEngine CPS microdata.

Uses PolicyEngine-US Microsimulation (CPS) to identify workers whose wages fall
within the EIG 80-80 Rule eligibility range ($7.25–$16.80/hr), compute gross
subsidy amounts, and assign family-type keys for pre-computed schedule lookup.

Assumptions
-----------
- Hourly wage proxy: employment_income / annual_hours_worked.
  If PE-US cannot provide annual_hours_worked, defaults to 2,080 hrs/yr
  (40 hrs/wk × 52 wks). This is a full-time equivalent approximation; workers
  with the same income but different actual hours may be mis-classified at the
  margins, but aggregate cost estimates are robust to this assumption.
- Family type: derived from filing_status (married/single) and child count.
  Workers with 1+ dependents are mapped to the "2 children" schedule as the
  closest available approximation.
- State: from the worker's household state_code. Falls back to "TX" with a
  warning if state_code cannot be resolved at person level.

Output
------
WORKSPACE/data/processed/hourly_workers.parquet
  state_code        str    two-letter state abbreviation
  family_type_key   str    single_0c | single_2c | married_0c | married_2c
  employer_wage     float  hourly wage proxy
  annual_hours      float  annual hours (real or assumed 2080)
  baseline_income   float  annual employment income (employer_wage × annual_hours)
  subsidy_hr        float  hourly wage subsidy (80-80 rule)
  subsidy_annual    float  annual subsidy (subsidy_hr × annual_hours)
  weight            float  CPS person survey weight
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]          # WORKSPACE/code/
_APP  = _HERE.parents[2] / "app"  # WORKSPACE/app/

for _p in [str(_CODE / "00_setup"), str(_APP)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Load config via file path (directory name has numeric prefix)
_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
cfg = _cfg_mod.cfg
PATH_DATA_PROCESSED = _cfg_mod.PATH_DATA_PROCESSED

# ── Subsidy formula (inlined to avoid cross-package import) ───────────────────
_MEDIAN_WAGE  = cfg["ws_median_hourly_wage"]   # 21.00
_TARGET_PCT   = cfg["ws_target_pct"]           # 0.80  → target_wage = 16.80
_SUBSIDY_PCT  = cfg["ws_subsidy_pct"]          # 0.80
_BASE_WAGE    = cfg["ws_base_wage"]            # 7.25
_TARGET_WAGE  = cfg["ws_target_wage"]          # 16.80


def _hourly_subsidy(employer_wage: float | np.ndarray) -> float | np.ndarray:
    gap = np.maximum(0.0, _TARGET_WAGE - employer_wage)
    eligible = employer_wage >= _BASE_WAGE
    return np.where(eligible, _SUBSIDY_PCT * gap, 0.0)


# ── PolicyEngine helpers ───────────────────────────────────────────────────────

def _safe_calc(sim, var: str) -> np.ndarray | None:
    """Try to get a variable from the Microsimulation; return None on failure."""
    try:
        result = sim.calculate(var)
        if hasattr(result, "values"):
            return np.asarray(result.values)
        return np.asarray(result)
    except Exception as exc:
        print(f"  [warn] Could not calculate {var!r}: {exc}")
        return None


# ── Main extraction ───────────────────────────────────────────────────────────

def main() -> None:
    print("01a | Loading PolicyEngine CPS Microsimulation …")
    from policyengine_us import Microsimulation

    sim = Microsimulation()
    print("  Microsimulation loaded.")

    # ── Person-level variables ────────────────────────────────────────────────
    employment_income = _safe_calc(sim, "employment_income")
    if employment_income is None:
        raise RuntimeError("Could not retrieve employment_income from Microsimulation.")

    n_persons = len(employment_income)
    print(f"  Total CPS persons: {n_persons:,}")

    age             = _safe_calc(sim, "age")
    is_head         = _safe_calc(sim, "is_tax_unit_head")
    person_weight   = _safe_calc(sim, "person_weight")
    if person_weight is None:
        person_weight = _safe_calc(sim, "household_weight")
    if person_weight is None:
        print("  [warn] No weight variable found; using weight=1 for all persons.")
        person_weight = np.ones(n_persons)

    # ── Annual hours ──────────────────────────────────────────────────────────
    annual_hours = _safe_calc(sim, "annual_hours_worked")
    if annual_hours is None:
        # Try deriving from weeks × weekly hours
        weeks   = _safe_calc(sim, "weeks_worked_last_year")
        hrs_wk  = _safe_calc(sim, "usual_weekly_hours_worked")
        if hrs_wk is None:
            hrs_wk = _safe_calc(sim, "weekly_hours_worked")
        if weeks is not None and hrs_wk is not None:
            annual_hours = weeks * hrs_wk
            print("  annual_hours derived from weeks_worked × weekly_hours.")
        else:
            annual_hours = np.full(n_persons, 2_080.0)
            print("  [warn] Hours data unavailable — defaulting to 2,080 hrs/yr (40 hrs × 52 wks).")

    # Guard against zeros to avoid division errors
    annual_hours = np.where(annual_hours > 0, annual_hours, 2_080.0)

    # ── State code ────────────────────────────────────────────────────────────
    state_raw = _safe_calc(sim, "state_code")
    if state_raw is not None and len(state_raw) == n_persons:
        state_arr = np.array([str(s) for s in state_raw])
    else:
        print("  [warn] state_code not available at person level — defaulting to 'TX'.")
        state_arr = np.full(n_persons, "TX")

    # ── Family type indicators ────────────────────────────────────────────────
    # Married: filing_status == "JOINT" or is_tax_unit_joint
    filing_status = _safe_calc(sim, "filing_status")
    is_married_arr: np.ndarray
    if filing_status is not None:
        is_married_arr = np.array([str(s).upper() in ("JOINT", "MARRIED_FILING_JOINTLY")
                                   for s in filing_status])
    else:
        is_tax_joint = _safe_calc(sim, "tax_unit_is_joint")
        if is_tax_joint is not None:
            is_married_arr = is_tax_joint.astype(bool)
        else:
            print("  [warn] Marital status unavailable — treating all as single.")
            is_married_arr = np.zeros(n_persons, dtype=bool)

    # Children: try several variable names
    child_count: np.ndarray | None = None
    for _var in ("count_qualifying_children_for_ctc", "child_count",
                 "count_dependents", "tax_unit_children"):
        child_count = _safe_calc(sim, _var)
        if child_count is not None:
            break
    if child_count is None:
        print("  [warn] Child count unavailable — treating all as no children.")
        child_count = np.zeros(n_persons)

    has_children = child_count >= 1

    # ── Filter to eligible workers ────────────────────────────────────────────
    # 1. Tax unit head (one record per family)
    # 2. Working age
    # 3. Has employment income
    # 4. Implied hourly wage in [$7.25, $16.80]
    hourly_wage = employment_income / annual_hours

    mask_head    = (is_head is None) or (is_head.astype(bool))
    mask_age     = (age is None) or ((age >= 16) & (age <= 64))
    mask_income  = employment_income > 0
    mask_wage    = (hourly_wage >= _BASE_WAGE) & (hourly_wage < _TARGET_WAGE)

    if is_head is None:
        combined_mask = mask_age & mask_income & mask_wage
    else:
        combined_mask = mask_head.astype(bool) & mask_age.astype(bool) & mask_income & mask_wage

    n_eligible = combined_mask.sum()
    print(f"  Eligible workers (pre-weight): {n_eligible:,}")
    if n_eligible == 0:
        raise RuntimeError(
            "Zero eligible workers found. Check variable names and PE-US version. "
            "Try running: python -c \"from policyengine_us import Microsimulation; "
            "sim=Microsimulation(); print(dir(sim))\""
        )

    # ── Build output DataFrame ────────────────────────────────────────────────
    employer_wage_eligible = hourly_wage[combined_mask]
    annual_hours_eligible  = annual_hours[combined_mask]
    baseline_income        = employment_income[combined_mask]
    subsidy_hr             = _hourly_subsidy(employer_wage_eligible)
    subsidy_annual         = subsidy_hr * annual_hours_eligible
    weight_eligible        = person_weight[combined_mask]
    state_eligible         = state_arr[combined_mask]
    married_eligible       = is_married_arr[combined_mask]
    children_eligible      = has_children[combined_mask]

    # Map to family type key
    def _family_key(married: bool, has_child: bool) -> str:
        prefix = "married" if married else "single"
        suffix = "2c" if has_child else "0c"
        return f"{prefix}_{suffix}"

    family_type_keys = np.array([
        _family_key(m, c)
        for m, c in zip(married_eligible, children_eligible)
    ])

    df = pd.DataFrame({
        "state_code":       state_eligible,
        "family_type_key":  family_type_keys,
        "employer_wage":    employer_wage_eligible,
        "annual_hours":     annual_hours_eligible,
        "baseline_income":  baseline_income,
        "subsidy_hr":       subsidy_hr,
        "subsidy_annual":   subsidy_annual,
        "weight":           weight_eligible,
    })

    # ── Save ─────────────────────────────────────────────────────────────────
    out_path = PATH_DATA_PROCESSED / "hourly_workers.parquet"
    df.to_parquet(out_path, index=False)

    total_workers_mn = df["weight"].sum() / 1e6
    gross_cost_bn    = (df["subsidy_annual"] * df["weight"]).sum() / 1e9
    avg_subsidy      = (df["subsidy_annual"] * df["weight"]).sum() / df["weight"].sum()

    print(f"  Saved: {out_path}")
    print(f"  Weighted eligible workers:  {total_workers_mn:.2f}M")
    print(f"  Gross annual program cost:  ${gross_cost_bn:.2f}B")
    print(f"  Average annual subsidy:     ${avg_subsidy:,.0f}/worker")


if __name__ == "__main__":
    main()
