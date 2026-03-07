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

def _safe_calc(sim, var: str, expected_len: int | None = None) -> np.ndarray | None:
    """
    Try to get a variable from the Microsimulation; return None on failure.
    If expected_len is given, returns None when the result length doesn't match
    (variable is at a different entity level than expected).
    """
    try:
        result = sim.calculate(var)
        arr = np.asarray(result.values if hasattr(result, "values") else result)
        if expected_len is not None and len(arr) != expected_len:
            print(f"  [warn] {var!r} has {len(arr)} records "
                  f"(expected {expected_len} — likely a different entity level). Skipping.")
            return None
        return arr
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

    age             = _safe_calc(sim, "age",             expected_len=n_persons)
    is_head         = _safe_calc(sim, "is_tax_unit_head", expected_len=n_persons)
    person_weight   = _safe_calc(sim, "person_weight",   expected_len=n_persons)
    if person_weight is None:
        person_weight = _safe_calc(sim, "household_weight", expected_len=n_persons)
    if person_weight is None:
        print("  [warn] No weight variable found; using weight=1 for all persons.")
        person_weight = np.ones(n_persons)

    # ── Annual hours ──────────────────────────────────────────────────────────
    _hours_vars = [
        "annual_hours_worked", "hours_worked", "employment_hours",
        "weekly_hours_worked", "usual_weekly_hours",
    ]
    annual_hours = None
    for _hvar in _hours_vars:
        annual_hours = _safe_calc(sim, _hvar, expected_len=n_persons)
        if annual_hours is not None:
            # If clearly weekly (median < 80), scale to annual
            if np.median(annual_hours[annual_hours > 0]) < 80:
                annual_hours = annual_hours * 52
                print(f"  annual_hours derived from weekly {_hvar} × 52.")
            else:
                print(f"  annual_hours from {_hvar!r}.")
            break
    if annual_hours is None:
        annual_hours = np.full(n_persons, 2_080.0)
        print("  [warn] Hours data unavailable — defaulting to 2,080 hrs/yr (40 hrs × 52 wks).")

    # Guard against zeros to avoid division errors
    annual_hours = np.where(annual_hours > 0, annual_hours, 2_080.0)

    # ── Entity-level expansion helper ─────────────────────────────────────────
    def _expand_to_person(entity_key: str, values: np.ndarray) -> np.ndarray | None:
        """
        Expand an entity-level array to person level using nb_persons().
        Assumes persons are stored in entity order in the PE dataset (standard for CPS).
        Returns None if the total person count doesn't match n_persons.
        """
        try:
            sizes = np.array(sim.populations[entity_key].nb_persons())
            if sizes.sum() != n_persons:
                return None
            return np.repeat(values, sizes)
        except Exception as exc:
            print(f"  [warn] Could not expand {entity_key} → person: {exc}")
            return None

    # ── State code ────────────────────────────────────────────────────────────
    # state_code is household-level; expand to person level via household sizes
    state_arr: np.ndarray | None = None

    # First try: direct person-level variable
    for _svar in ("state_code", "state"):
        _raw = _safe_calc(sim, _svar, expected_len=n_persons)
        if _raw is not None:
            state_arr = np.array([str(s) for s in _raw])
            print(f"  state_code from {_svar!r} at person level.")
            break

    # Second try: expand household-level state_code to persons via group sizes
    if state_arr is None:
        _hh_state = _safe_calc(sim, "state_code")  # household level, any length
        if _hh_state is not None:
            _expanded = _expand_to_person("household", _hh_state)
            if _expanded is not None:
                state_arr = np.array([str(s) for s in _expanded])
                print("  state_code expanded from household → person via nb_persons().")

    if state_arr is None:
        print("  [warn] state_code unavailable — defaulting to 'TX'.\n"
              "         State-level breakdown will not be accurate.")
        state_arr = np.full(n_persons, "TX")

    # ── Family type indicators ────────────────────────────────────────────────
    # Married: try person-level first, then expand from tax_unit level
    is_married_arr: np.ndarray | None = None

    # Person-level attempts
    for _mvar in ("filing_status", "tax_unit_is_joint", "is_tax_unit_joint", "is_married"):
        _raw = _safe_calc(sim, _mvar, expected_len=n_persons)
        if _raw is not None:
            if _mvar == "filing_status":
                is_married_arr = np.array([
                    str(s).upper() in ("JOINT", "MARRIED_FILING_JOINTLY") for s in _raw
                ])
            else:
                is_married_arr = _raw.astype(bool)
            print(f"  married status from {_mvar!r} at person level.")
            break

    # Tax-unit-level expansion
    if is_married_arr is None:
        for _mvar in ("filing_status", "tax_unit_is_joint"):
            _raw = _safe_calc(sim, _mvar)  # any length
            if _raw is not None:
                _expanded = _expand_to_person("tax_unit", _raw)
                if _expanded is not None:
                    if _mvar == "filing_status":
                        is_married_arr = np.array([
                            str(s).upper() in ("JOINT", "MARRIED_FILING_JOINTLY")
                            for s in _expanded
                        ])
                    else:
                        is_married_arr = _expanded.astype(bool)
                    print(f"  married status expanded from tax_unit via {_mvar!r}.")
                    break

    if is_married_arr is None:
        print("  [warn] Marital status unavailable — treating all as single.")
        is_married_arr = np.zeros(n_persons, dtype=bool)

    # Children: try person-level then expand from tax_unit / household level
    child_count: np.ndarray | None = None

    for _var in ("count_qualifying_children_for_ctc", "child_count",
                 "count_dependents", "spm_unit_children", "household_count_children"):
        _raw = _safe_calc(sim, _var, expected_len=n_persons)
        if _raw is not None:
            child_count = _raw
            print(f"  child count from {_var!r} at person level.")
            break

    if child_count is None:
        for _var in ("tax_unit_children", "count_dependents", "child_count"):
            _raw = _safe_calc(sim, _var)  # any length
            if _raw is not None:
                _expanded = _expand_to_person("tax_unit", _raw)
                if _expanded is not None:
                    child_count = _expanded
                    print(f"  child count expanded from tax_unit via {_var!r}.")
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
