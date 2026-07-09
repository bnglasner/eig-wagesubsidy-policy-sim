"""
PolicyEngine version + hourly_wage input comparison.

Two modes:
  --mode single   Run this version's simulations, save results JSON
  --mode diff     Load both saved JSONs, print the comparison report

Results directory is controlled by env var RESULTS_DIR (defaults to ./results).
"""
import argparse
import json
import os
import sys
import importlib.metadata

VERSION = importlib.metadata.version("policyengine-us")
YEAR    = "2026"
RESULTS_DIR = os.environ.get("RESULTS_DIR", os.path.join(os.path.dirname(__file__), "results"))

# ── Test combos: (key, state, n_adults, n_children, child_ages) ──────────────
# Chosen to span the main variation axes: single vs married, children, states
# with very different tax/benefit rules.
TEST_COMBOS = [
    ("single_0c",  "TX", 1, 0, []),
    ("single_2c",  "CA", 1, 2, [8, 3]),
    ("married_2c", "NY", 2, 2, [8, 3]),
]

# Income grid matches production pipeline: $0–$65k in $500 steps (131 pts)
INCOME_GRID = list(range(0, 65_001, 500))

# ── Variable lists ────────────────────────────────────────────────────────────

CORE_VARS = [
    "eitc",
    "snap",
    "federal_income_tax",
    "state_income_tax",
    "employee_social_security_tax",
    "employee_medicare_tax",
    "household_net_income",
]

# Try multiple name variants for the overtime deduction
OVERTIME_CANDIDATES = [
    "overtime_deduction",
    "exempt_overtime_income",
    "no_tax_on_overtime",
    "overtime_income_deduction",
]

# Benefits with multiple possible variable names across PE versions
BENEFIT_CANDIDATES = {
    "medicaid_chip":    ["medicaid_and_chip", "medicaid", "medicaid_benefit",
                         "medicaid_and_chip_benefit"],
    "aca_ptc":          ["premium_tax_credit", "aca_premium_tax_credit", "ptc"],
    "child_tax_credit": ["refundable_ctc", "child_tax_credit_refundable",
                         "additional_child_tax_credit"],
    "tanf":             ["tanf", "tanf_max_benefit"],
    "ssi":              ["ssi"],
    "housing":          ["housing_assistance", "section_8_housing_assistance",
                         "housing_choice_voucher", "section_8"],
    "ccdf":             ["ccdf_subsidy", "ccdf", "child_care_subsidy"],
    "wic":              ["wic", "wic_benefit"],
    "school_meals":     ["school_meal_subsidy", "nslp", "free_school_meals",
                         "free_and_reduced_price_school_meals"],
    "liheap":           ["liheap", "liheap_benefit"],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_situation(employment_income, n_adults, n_children, child_ages, state,
                    hourly_wage=None):
    people      = {}
    all_members = []

    person1 = {
        "age":               {YEAR: 35},
        "employment_income": {YEAR: float(employment_income)},
    }
    if hourly_wage is not None:
        person1["hourly_wage"] = {YEAR: float(hourly_wage)}

    people["person1"] = person1
    all_members.append("person1")

    if n_adults == 2:
        people["person2"] = {
            "age":               {YEAR: 33},
            "employment_income": {YEAR: 0.0},
        }
        all_members.append("person2")

    for i, age in enumerate(child_ages):
        cid = f"child{i+1}"
        people[cid] = {
            "age":               {YEAR: int(age)},
            "employment_income": {YEAR: 0.0},
        }
        all_members.append(cid)

    adult_members = ["person1"] if n_adults == 1 else ["person1", "person2"]

    return {
        "people":        people,
        "families":      {"family1": {"members": all_members}},
        "marital_units": {"marital_unit1": {"members": adult_members}},
        "tax_units": {
            "tax_unit1": {
                "members":           all_members,
                "tax_unit_is_joint": {YEAR: n_adults == 2},
            }
        },
        "spm_units":  {"spm_unit1": {"members": all_members}},
        "households": {
            "household1": {
                "members":    all_members,
                "state_code": {YEAR: state},
            }
        },
    }


def safe_get(sim, var):
    try:
        return float(sim.calculate(var, YEAR).sum())
    except Exception:
        return None


def run_income_point(employment_income, n_adults, n_children, child_ages, state,
                     hourly_wage=None):
    from policyengine_us import Simulation

    situation = build_situation(
        employment_income, n_adults, n_children, child_ages, state, hourly_wage
    )
    sim    = Simulation(situation=situation)
    result = {"employment_income": employment_income}

    for var in CORE_VARS:
        result[var] = safe_get(sim, var)

    for label, candidates in BENEFIT_CANDIDATES.items():
        for candidate in candidates:
            val = safe_get(sim, candidate)
            if val is not None:
                result[label] = val
                break

    # Overtime deduction: try all candidate names, store any non-None hit
    for var in OVERTIME_CANDIDATES:
        val = safe_get(sim, var)
        if val is not None:
            result[f"overtime__{var}"] = val

    return result


def run_combo(combo_key, state, n_adults, n_children, child_ages):
    print(f"    [{combo_key} / {state}]", flush=True)
    no_hw   = []
    with_hw = []

    for i, inc in enumerate(INCOME_GRID):
        if i % 26 == 0:
            pct = int(i / len(INCOME_GRID) * 100)
            print(f"      {pct:3d}%  income=${inc:,}", flush=True)

        no_hw.append(
            run_income_point(inc, n_adults, n_children, child_ages, state,
                             hourly_wage=None)
        )
        hw = inc / 2080.0 if inc > 0 else 0.0
        with_hw.append(
            run_income_point(inc, n_adults, n_children, child_ages, state,
                             hourly_wage=hw)
        )

    return {"no_hourly_wage": no_hw, "with_hourly_wage": with_hw}


# ── Modes ─────────────────────────────────────────────────────────────────────

def mode_single():
    print(f"\n  policyengine-us v{VERSION}")
    all_results = {"version": VERSION, "combos": {}}

    for combo_key, state, n_adults, n_children, child_ages in TEST_COMBOS:
        all_results["combos"][f"{combo_key}_{state}"] = run_combo(
            combo_key, state, n_adults, n_children, child_ages
        )

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"pe_results_{VERSION}.json")
    with open(out_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Saved → {out_path}")


def mode_diff():
    import glob

    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "pe_results_*.json")))
    if len(files) < 2:
        print(f"ERROR: Need two result files in {RESULTS_DIR}. Found {len(files)}.")
        sys.exit(1)

    with open(files[0]) as f:
        old = json.load(f)
    with open(files[1]) as f:
        new = json.load(f)

    v_old, v_new = old["version"], new["version"]

    sep = "=" * 65
    print(f"\n{sep}")
    print(f"  POLICYENGINE VERSION COMPARISON REPORT")
    print(f"  OLD: {v_old}   NEW: {v_new}")
    print(f"{sep}")

    any_hw_effect  = False
    any_ver_effect = False

    for combo_key in old["combos"]:
        if combo_key not in new["combos"]:
            continue

        print(f"\n{'─'*65}")
        print(f"  Combo: {combo_key}")
        print(f"{'─'*65}")

        # ── Question 1: does hourly_wage input change outputs? ────────────────
        new_no   = new["combos"][combo_key]["no_hourly_wage"]
        new_yes  = new["combos"][combo_key]["with_hourly_wage"]

        hw_diffs = {}
        for r_no, r_yes in zip(new_no, new_yes):
            for k in set(list(r_no.keys()) + list(r_yes.keys())):
                if k == "employment_income":
                    continue
                vo = r_no.get(k)
                vn = r_yes.get(k)
                if vo is not None and vn is not None and abs(vn - vo) > 0.01:
                    hw_diffs.setdefault(k, []).append(vn - vo)

        print("\n  [A] Effect of passing hourly_wage= into situation (new version)")
        if hw_diffs:
            any_hw_effect = True
            print(f"  {'Variable':<45}  {'max |Δ|':>12}  {'mean Δ':>12}")
            print(f"  {'-'*45}  {'-'*12}  {'-'*12}")
            for k, diffs in sorted(hw_diffs.items(), key=lambda x: -max(abs(d) for d in x[1])):
                max_d  = max(abs(d) for d in diffs)
                mean_d = sum(diffs) / len(diffs)
                print(f"  {k:<45}  ${max_d:>10,.2f}  ${mean_d:>+10,.2f}")
        else:
            print("  → NO EFFECT. hourly_wage input does not change any output.")

        # ── Question 2: version diff (baseline, no hourly_wage) ───────────────
        old_pts = old["combos"][combo_key]["no_hourly_wage"]
        new_pts = new["combos"][combo_key]["no_hourly_wage"]

        ver_diffs = {}
        for r_old, r_new in zip(old_pts, new_pts):
            all_keys = set(list(r_old.keys()) + list(r_new.keys()))
            for k in all_keys:
                if k == "employment_income":
                    continue
                vo = r_old.get(k)
                vn = r_new.get(k)
                if vo is not None and vn is not None and abs(vn - vo) > 0.01:
                    ver_diffs.setdefault(k, []).append(vn - vo)
                elif vo is None and vn is not None:
                    ver_diffs.setdefault(f"NEW:{k}", []).append(vn)
                elif vo is not None and vn is None:
                    ver_diffs.setdefault(f"GONE:{k}", []).append(-vo)

        print(f"\n  [B] Version diff: {v_old} → {v_new} (no hourly_wage baseline)")
        if ver_diffs:
            any_ver_effect = True
            print(f"  {'Variable':<45}  {'max |Δ|':>12}  {'mean Δ':>12}  {'# pts':>6}")
            print(f"  {'-'*45}  {'-'*12}  {'-'*12}  {'-'*6}")
            for k, diffs in sorted(ver_diffs.items(), key=lambda x: -max(abs(d) for d in x[1])):
                max_d  = max(abs(d) for d in diffs)
                mean_d = sum(diffs) / len(diffs)
                n      = len(diffs)
                flag   = " ◄ LARGE" if max_d > 1000 else ""
                print(f"  {k:<45}  ${max_d:>10,.2f}  ${mean_d:>+10,.2f}  {n:>6}{flag}")
        else:
            print(f"  → NO CHANGES between {v_old} and {v_new} for this combo.")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SUMMARY")
    print(f"{sep}")
    print(f"  hourly_wage input effect: {'YES — see [A] above' if any_hw_effect else 'None detected'}")
    print(f"  Version upgrade effect:   {'YES — see [B] above' if any_ver_effect else 'None detected'}")

    if any_ver_effect:
        print("""
  RECOMMENDATION: The schedules have changed materially between versions.
  Consider regenerating all 204 pre-computed parquets using the new version.
  Run: python code/01_data_preparation/01b_precompute_individual.py
""")
    else:
        print("""
  RECOMMENDATION: Schedules are stable across this version range.
  No regeneration needed unless you want hourly_wage-specific modeling.
""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["single", "diff"], default="single")
    args = parser.parse_args()

    if args.mode == "single":
        mode_single()
    else:
        mode_diff()


if __name__ == "__main__":
    main()
