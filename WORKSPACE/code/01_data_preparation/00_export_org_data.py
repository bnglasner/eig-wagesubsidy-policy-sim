"""
00_export_org_data.py — Export EIG-relevant columns from the real-wages ORG panel.

Reads the most recent year(s) of ORG panel parquets from the real-wages-generations-ipums
repository and writes a trimmed, EIG-specific file to WORKSPACE/data/external/.

Usage
-----
    python 00_export_org_data.py                    # auto-discovers real-wages repo
    python 00_export_org_data.py --org-dir PATH     # explicit path to org_panel_by_year/

Output
------
WORKSPACE/data/external/org_workers_{year}.parquet
  year, month, mish, earnwt, age, statefip, nchild, marst, wkstat,
  classwkr, paid_hourly, hours_epi, hours_epi_valid, hourly_wage_epi,
  hourly_wage_epi_valid, epi_sample_eligible, weekly_earn_epi
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pandas as pd

# ── Path setup ────────────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]          # WORKSPACE/code/

_cfg_spec = importlib.util.spec_from_file_location(
    "eig_config", _CODE / "00_setup" / "00_config.py"
)
_cfg_mod = importlib.util.module_from_spec(_cfg_spec)
_cfg_spec.loader.exec_module(_cfg_mod)
PATH_DATA = _cfg_mod.PATH_DATA

# ── Columns to export ─────────────────────────────────────────────────────────
EXPORT_COLS = [
    "year",
    "month",
    "mish",
    "earnwt",
    "age",
    "statefip",
    "nchild",
    "marst",
    "wkstat",
    "classwkr",
    "paid_hourly",
    "hours_epi",
    "hours_epi_valid",
    "hourly_wage_epi",
    "hourly_wage_epi_valid",
    "epi_sample_eligible",
    "weekly_earn_epi",
    # Demographics for breakdown analysis
    "sex_label",
    "race_ethnicity",
    "educ",
    "age_bin",
    # Household relationship — used to identify tax dependents
    "relate",
]


def _find_real_wages_org_dir() -> Path:
    """Walk up from EIG project root to find the sibling real-wages repo."""
    candidates = [
        _HERE.parents[4] / "real-wages-generations-ipums",   # common sibling layout
        _HERE.parents[3] / "real-wages-generations-ipums",
        _HERE.parents[2] / "real-wages-generations-ipums",
    ]
    for c in candidates:
        org_dir = c / "data" / "processed" / "org_panel_by_year"
        if org_dir.is_dir():
            return org_dir
    raise FileNotFoundError(
        "Could not auto-discover real-wages-generations-ipums repo. "
        "Pass --org-dir explicitly."
    )


def main(org_dir: Path | None = None) -> None:
    if org_dir is None:
        org_dir = _find_real_wages_org_dir()

    print(f"00_export | Reading ORG panel from: {org_dir}")

    parquets = sorted(org_dir.glob("org_panel_*.parquet"))
    if not parquets:
        raise FileNotFoundError(f"No org_panel_*.parquet files found in {org_dir}")

    # Use the most recent two years to maximise sample size for median computation
    recent = parquets[-2:] if len(parquets) >= 2 else parquets[-1:]
    print(f"  Using files: {[p.name for p in recent]}")

    frames = []
    for p in recent:
        df = pd.read_parquet(p)
        # Keep only EIG-relevant columns that exist in this parquet
        cols = [c for c in EXPORT_COLS if c in df.columns]
        missing = [c for c in EXPORT_COLS if c not in df.columns]
        if missing:
            print(f"  [warn] {p.name}: missing columns {missing}")
        frames.append(df[cols])

    combined = pd.concat(frames, ignore_index=True)
    print(f"  Combined rows: {len(combined):,}  |  years: {sorted(combined['year'].unique())}")

    # ── Output ────────────────────────────────────────────────────────────────
    out_dir = PATH_DATA / "external"
    out_dir.mkdir(parents=True, exist_ok=True)

    # File name reflects the max year in the export
    max_year = int(combined["year"].max())
    out_path = out_dir / f"org_workers_{max_year}.parquet"

    combined.to_parquet(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(combined):,} rows, {combined['year'].nunique()} years)")

    # Quick summary
    valid = combined[combined["hourly_wage_epi_valid"] == True]
    print(f"  Valid-wage workers: {len(valid):,}  "
          f"| paid-hourly: {valid['paid_hourly'].sum():,}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--org-dir",
        type=Path,
        default=None,
        help="Path to org_panel_by_year/ directory in real-wages repo.",
    )
    args = parser.parse_args()
    main(args.org_dir)
