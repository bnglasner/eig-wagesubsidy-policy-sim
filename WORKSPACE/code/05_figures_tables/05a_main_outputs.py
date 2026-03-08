"""
05a_main_outputs.py — Verify population pipeline outputs and print summary.

Reads the five parquet files produced by 02a_descriptive_stats.py and prints
a console summary for pipeline verification. No new files are created.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
PATH_OUTPUT_INTERMEDIATE = _cfg_mod.PATH_OUTPUT_INTERMEDIATE

_POP_DIR = PATH_OUTPUT_INTERMEDIATE / "population"

_FILES = [
    "summary.parquet",
    "by_state.parquet",
    "by_wage_bracket.parquet",
    "by_family_type.parquet",
    "program_interactions.parquet",
]


def main() -> None:
    print("05a | Verifying population pipeline outputs ...")

    missing = [f for f in _FILES if not (_POP_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing output files in {_POP_DIR}:\n"
            + "\n".join(f"  {f}" for f in missing)
            + "\nRun 02a_descriptive_stats.py first."
        )

    summary = pd.read_parquet(_POP_DIR / "summary.parquet").iloc[0]
    by_state  = pd.read_parquet(_POP_DIR / "by_state.parquet")
    by_wb     = pd.read_parquet(_POP_DIR / "by_wage_bracket.parquet")
    by_ft     = pd.read_parquet(_POP_DIR / "by_family_type.parquet")
    prog      = pd.read_parquet(_POP_DIR / "program_interactions.parquet")

    print("\n-- Headline metrics ------------------------------------------")
    print(f"  Gross annual program cost:   ${summary['gross_cost_bn']:.2f}B")
    print(f"  Net annual program cost:     ${summary['net_cost_bn']:.2f}B")
    print(f"  Eligible workers:            {summary['n_workers_mn']:.2f}M")
    print(f"  Average annual subsidy:      ${summary['avg_annual_subsidy']:,.0f}")

    print("\n-- Top 5 states by gross cost --------------------------------")
    top5 = by_state.nlargest(5, "gross_cost_mn")
    for _, row in top5.iterrows():
        print(f"  {row['state_code']}  {row['n_workers_k']:,.0f}k workers  "
              f"${row['gross_cost_mn']:,.0f}M gross  ${row['avg_annual_subsidy']:,.0f} avg")

    print("\n-- By wage bracket -------------------------------------------")
    for _, row in by_wb.iterrows():
        print(f"  {row['wage_bracket']:15s}  {row['n_workers_k']:,.0f}k workers  "
              f"${row['avg_annual_subsidy']:,.0f} avg subsidy")

    print("\n-- By family type --------------------------------------------")
    for _, row in by_ft.iterrows():
        print(f"  {row['family_type']:30s}  {row['pct_workers']:.1f}%  "
              f"${row['avg_annual_subsidy']:,.0f} avg subsidy")

    print("\n-- Program interactions (avg per eligible worker) ------------")
    for _, row in prog.iterrows():
        sign = "+" if row["avg_delta_per_worker"] >= 0 else ""
        print(f"  {row['program']:30s}  {sign}${row['avg_delta_per_worker']:,.0f}/worker  "
              f"${row['total_delta_mn']:+,.0f}M total")

    # ── Demographic breakdowns (optional) ─────────────────────────────────────
    _DEMO = {
        "by_sex":            ("sex_label",      "By sex"),
        "by_race_ethnicity": ("race_ethnicity",  "By race/ethnicity"),
        "by_education":      ("educ_group",      "By education"),
        "by_age_bin":        ("age_bin",         "By age"),
    }
    for fname, (group_col, title) in _DEMO.items():
        path = _POP_DIR / f"{fname}.parquet"
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        print(f"\n-- {title} {'--' * (28 - len(title) // 2)}")
        for _, row in df.iterrows():
            print(f"  {str(row[group_col]):30s}  {row['pct_workers']:5.1f}%  "
                  f"${row['avg_annual_subsidy']:,.0f} avg subsidy  "
                  f"{row['n_workers_k']:,.0f}k workers")

    print(f"\n05a | All outputs verified. Files in: {_POP_DIR}")


if __name__ == "__main__":
    main()
