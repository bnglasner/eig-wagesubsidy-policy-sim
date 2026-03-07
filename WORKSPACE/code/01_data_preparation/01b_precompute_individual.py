"""
01b_precompute_individual.py
Pre-compute income → benefit/tax schedules for the individual calculator app.

For each (family_type × state) combination (4 × 51 = 204 pairs), runs
PolicyEngine-US at every $500 annual income increment from $0 to $65,000
(131 points each) and saves a parquet file.

At runtime the app interpolates from these files — no PolicyEngine calls needed.

Output
------
WORKSPACE/output/data/intermediate_results/individual_schedules/{key}_{state}.parquet
    Index  : annual_income (0, 500, 1000, ..., 65000)
    Columns: eitc, child_tax_credit, snap, ssi, tanf, housing, other_benefits,
             federal_tax, state_tax, payroll_tax, net_income

Runtime
-------
~204 combinations × 131 income points = 26,724 PolicyEngine calls.
With 4 parallel workers this typically finishes in 30–60 minutes.
Run from the project root:

    python WORKSPACE/code/01_data_preparation/01b_precompute_individual.py

Or via the pipeline:

    python WORKSPACE/code/run_all.py   (set RUN_01B_PRECOMPUTE_INDIVIDUAL = True)
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────

_HERE = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[3]          # eig-wagesubsidy-policy-sim/
APP_DIR = PROJECT_ROOT / "WORKSPACE" / "app"

# Add app/ to sys.path so we can import utils.*
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from utils.household_sim import FAMILY_TYPES, FAMILY_KEYS, compute_income_point  # noqa: E402
from utils.states import US_STATES  # noqa: E402

# ── Configuration ─────────────────────────────────────────────────────────────

# Annual income grid: $0 to $65,000 in $500 increments
INCOME_POINTS: list[int] = list(range(0, 65_001, 500))   # 131 points

OUTPUT_DIR = (
    PROJECT_ROOT
    / "WORKSPACE" / "output" / "data" / "intermediate_results" / "individual_schedules"
)

MAX_WORKERS = 16  # parallel processes; tuned for Threadripper PRO 7945WX (12c/24t, 127GB RAM)


# ── Worker function (must be top-level for multiprocessing pickling) ──────────

def _compute_and_save(family_type: str, state_code: str) -> tuple[str, str, float]:
    """
    Compute the income schedule for one (family_type, state) pair and save it.
    Returns (family_type, state_code, elapsed_seconds).
    """
    t0 = time.time()

    rows = []
    for income in INCOME_POINTS:
        row = compute_income_point(float(income), family_type, state_code)
        row["annual_income"] = income
        rows.append(row)

    df = pd.DataFrame(rows).set_index("annual_income")

    family_key = FAMILY_KEYS[family_type]
    out_path = OUTPUT_DIR / f"{family_key}_{state_code}.parquet"
    df.to_parquet(out_path)

    return family_type, state_code, round(time.time() - t0, 1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build task list — skip already-completed combinations
    tasks = []
    skipped = 0
    for family_type in FAMILY_TYPES:
        family_key = FAMILY_KEYS[family_type]
        for state_code in US_STATES:
            out_path = OUTPUT_DIR / f"{family_key}_{state_code}.parquet"
            if out_path.exists():
                skipped += 1
            else:
                tasks.append((family_type, state_code))

    total = len(tasks) + skipped
    print(f"Pre-computation: {len(tasks)} combinations to run, {skipped} already done "
          f"({total} total).")
    print(f"Income grid: {len(INCOME_POINTS)} points × {len(tasks)} combos "
          f"= {len(INCOME_POINTS) * len(tasks):,} PolicyEngine calls.")
    print(f"Workers: {MAX_WORKERS}")

    if not tasks:
        print("Nothing to do — all schedules already exist.")
        return

    completed = 0
    failed: list[tuple[str, str, str]] = []
    wall_start = time.time()

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_map = {
            pool.submit(_compute_and_save, ft, sc): (ft, sc)
            for ft, sc in tasks
        }

        for future in as_completed(future_map):
            ft, sc = future_map[future]
            try:
                _, _, elapsed = future.result()
                completed += 1
                pct = 100 * completed / len(tasks)
                eta_s = (time.time() - wall_start) / completed * (len(tasks) - completed)
                print(
                    f"  [{completed:>3}/{len(tasks)}  {pct:5.1f}%]  "
                    f"{ft} / {sc}  ({elapsed}s)  "
                    f"ETA {eta_s/60:.1f} min"
                )
            except Exception as exc:
                failed.append((ft, sc, str(exc)))
                print(f"  FAILED: {ft} / {sc} — {exc}")

    wall_elapsed = round(time.time() - wall_start, 1)
    print(f"\nDone. {completed} succeeded, {len(failed)} failed in {wall_elapsed}s "
          f"({wall_elapsed/60:.1f} min).")
    if failed:
        print("Failed combinations:")
        for ft, sc, err in failed:
            print(f"  {ft} / {sc}: {err}")


if __name__ == "__main__":
    main()
