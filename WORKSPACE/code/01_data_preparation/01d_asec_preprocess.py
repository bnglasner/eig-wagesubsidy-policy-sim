"""
01d_asec_preprocess.py
Build earner-level matching records from CPS ASEC person-level parquet.

For each ASEC household this script identifies:
  - Primary earner  : highest-wage employed adult (age 16–64, wage/salary,
                      positive INCWAGE), acting as the principal match target.
  - Spouse income   : INCWAGE of the spouse (RELATE == 201) if present.
  - Dependent children : persons with RELATE in {301, 303} and age < 18,
                         with their actual ages recorded.

Output
------
WORKSPACE/data/external/asec_earners_{YYYY}.parquet
  One row per primary earner household.  Columns cover matching covariates,
  raw household context for PolicyEngine, and diagnostic fields.

Usage
-----
    python WORKSPACE/code/01_data_preparation/01d_asec_preprocess.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE        = Path(__file__).resolve()
PROJECT_ROOT = _HERE.parents[3]
EXTERNAL_DIR = PROJECT_ROOT / "WORKSPACE" / "data" / "external"

# ── ASEC reference tables ─────────────────────────────────────────────────────

# WKSWORK2 grouped weeks → midpoint weeks worked
# 1=1-13wks, 2=14-26, 3=27-39, 4=40-47, 5=48-49, 6=50-52
WKSWORK2_MIDPOINTS: dict[int, float] = {
    1: 7.0, 2: 20.0, 3: 33.0, 4: 43.5, 5: 48.5, 6: 51.0,
}

# RELATE codes
RELATE_HEAD         = 101
RELATE_SPOUSE       = 202  # 201 deprecated in 2025 ASEC; all spouses coded 202
RELATE_CHILD_CODES  = {301, 303}  # own child (303 unused in 2025 but harmless)

# CLASSWKR codes for wage-and-salary workers (private + government)
WAGE_SALARY_CODES = {21, 22, 23, 24, 25, 27, 28}

# MARST: 1=married-spouse present (the only code where PE spouse income matters)
MARST_MARRIED_SP = 1

# ── Derived covariate helpers ─────────────────────────────────────────────────

def _educ_group(educ: pd.Series) -> pd.Series:
    """Map IPUMS EDUC codes to 4 broad groups (mirrors ORG educ_group)."""
    return pd.cut(
        educ,
        bins=[0, 60, 73, 111, 999],
        labels=["lt_hs", "hs", "some_college", "ba_plus"],
        right=True,
    ).astype(str)


def _age_bin(age: pd.Series) -> pd.Series:
    """Five age bands matching the ORG age_bin labels."""
    return pd.cut(
        age,
        bins=[15, 25, 35, 45, 55, 65],
        labels=["16-25", "26-35", "36-45", "46-55", "56-64"],
        right=True,
    ).astype(str)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── Find most recent ASEC parquet ─────────────────────────────────────────
    asec_files = sorted(EXTERNAL_DIR.glob("asec_persons_*.parquet"), reverse=True)
    if not asec_files:
        raise FileNotFoundError(
            f"No asec_persons_*.parquet found in {EXTERNAL_DIR}.\n"
            "Run 01c_asec_pull.R first."
        )
    asec_path = asec_files[0]
    asec_year = int(asec_path.stem.split("_")[-1])
    print(f"Loading {asec_path.name} ...")

    df = pd.read_parquet(asec_path)
    df.columns = df.columns.str.upper()
    print(f"  {len(df):,} person records across {df['SERIAL'].nunique():,} households")

    # ── Household-level context: children ─────────────────────────────────────
    # Dependent children: RELATE in {301, 303}, age < 18.
    # Collect their actual ages into a list keyed by SERIAL.
    child_mask = df["RELATE"].isin(RELATE_CHILD_CODES) & (df["AGE"] < 18)
    children = df[child_mask].copy()

    children_by_hh: pd.Series = (
        children.groupby("SERIAL")["AGE"]
        .apply(lambda ages: sorted(ages.tolist()))
        .rename("children_ages")
    )

    # ── Household-level context: spouse income ────────────────────────────────
    spouses = df[df["RELATE"] == RELATE_SPOUSE].copy()
    spouses["spouse_incwage"] = spouses["INCWAGE"].clip(lower=0)
    spouse_income_by_hh: pd.Series = spouses.set_index("SERIAL")["spouse_incwage"]

    # ── Primary earner candidates ─────────────────────────────────────────────
    # Head or spouse of head, age 16–64, wage/salary, positive wage income,
    # with valid hours and weeks data.
    earner_mask = (
        df["RELATE"].isin({RELATE_HEAD, RELATE_SPOUSE})
        & df["AGE"].between(16, 64)
        & df["CLASSWKR"].isin(WAGE_SALARY_CODES)
        & (df["INCWAGE"] > 0)
        & (df["WKSWORK2"].between(1, 6))
        & (df["UHRSWORKLY"] > 0)
    )
    earners = df[earner_mask].copy()
    print(f"  {len(earners):,} earner candidates (wage/salary, age 16-64, positive income)")

    # ── Implied hourly wage ───────────────────────────────────────────────────
    earners["wks_worked"]       = earners["WKSWORK2"].map(WKSWORK2_MIDPOINTS)
    earners["annual_hours_asec"] = earners["UHRSWORKLY"] * earners["wks_worked"]
    earners["hourly_wage_asec"]  = (
        earners["INCWAGE"] / earners["annual_hours_asec"]
    ).clip(lower=0.01)

    # ── One primary earner per household (highest wage) ───────────────────────
    earners_sorted = earners.sort_values(
        ["SERIAL", "hourly_wage_asec"], ascending=[True, False]
    )
    primary = earners_sorted.drop_duplicates(subset="SERIAL", keep="first").copy()
    print(f"  {len(primary):,} unique primary-earner households retained")

    # ── Attach children and spouse income ─────────────────────────────────────
    primary = primary.join(children_by_hh, on="SERIAL", how="left")
    primary["children_ages"]  = primary["children_ages"].apply(
        lambda x: x if isinstance(x, list) else []
    )
    primary["n_children_hh"] = primary["children_ages"].apply(len)

    primary = primary.join(spouse_income_by_hh, on="SERIAL", how="left")
    primary["spouse_incwage"] = primary["spouse_incwage"].fillna(0.0)

    # ── Derived matching covariates ───────────────────────────────────────────
    primary["marital_binary"] = (primary["MARST"] == MARST_MARRIED_SP).astype(int)
    primary["sex_binary"]     = (primary["SEX"] == 1).astype(int)   # 1=male
    primary["educ_group"]     = _educ_group(primary["EDUC"])
    primary["age_bin"]        = _age_bin(primary["AGE"])
    primary["nchild_bin"]     = primary["n_children_hh"].clip(upper=3).astype(int)

    # Wage decile within state (decile 0 = lowest)
    primary["wage_decile"] = (
        primary.groupby("STATEFIP")["hourly_wage_asec"]
        .transform(lambda x: pd.qcut(x, q=10, labels=False, duplicates="drop"))
        .fillna(0)
        .astype(int)
    )

    # ── Select and save ───────────────────────────────────────────────────────
    out_cols = [
        # Identifiers
        "SERIAL", "PERNUM", "YEAR",
        # Matching covariates (align with ORG covariate names in 02c)
        "STATEFIP", "marital_binary", "nchild_bin",
        "age_bin", "sex_binary", "educ_group", "wage_decile",
        # Household context for PolicyEngine
        "n_children_hh", "children_ages", "spouse_incwage",
        # Primary earner wage data
        "hourly_wage_asec", "annual_hours_asec", "INCWAGE", "INCTOT",
        # Raw demographics (kept for QC / secondary matching passes)
        "AGE", "SEX", "RACE", "HISPAN", "MARST", "EDUC", "NCHILD",
        # Weights
        "ASECWT", "EARNWT",
    ]
    out_cols = [c for c in out_cols if c in primary.columns]
    out = primary[out_cols].copy().reset_index(drop=True)

    out_path = EXTERNAL_DIR / f"asec_earners_{asec_year}.parquet"
    out.to_parquet(out_path, index=False)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\nSaved: {out_path}")
    print(f"  Rows             : {len(out):,}")
    print(f"  States (FIPS)    : {out['STATEFIP'].nunique()}")
    print(f"  Median wage      : ${out['hourly_wage_asec'].median():.2f}/hr")
    print(f"  Spouse income >0 : {(out['spouse_incwage'] > 0).mean():.1%}")
    print(f"  Has children     : {(out['n_children_hh'] > 0).mean():.1%}")
    print(f"\nNext step: python WORKSPACE/code/01_data_preparation/01e_match_org_to_asec.py")


if __name__ == "__main__":
    main()
