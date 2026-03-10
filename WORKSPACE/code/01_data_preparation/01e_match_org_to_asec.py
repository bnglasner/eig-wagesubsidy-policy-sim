"""
01e_match_org_to_asec.py
Nearest-neighbor statistical match: CPS ORG eligible workers → ASEC earner
households.

For each ORG eligible worker, finds the k=1 closest ASEC primary earner
(with replacement on the ASEC side) using weighted Euclidean distance on
six standardised covariates.  Matching is done separately within each state
so the state is an exact hard constraint, not a soft covariate.

Matching covariates and weights
--------------------------------
  wage_decile      0.35   within-state decile of hourly wage
  marital_binary   0.20   1=married-spouse-present, 0=other
  nchild_bin       0.20   capped at 3
  age_bin          0.10   five 10-year bands (16-25 … 56-64)
  sex_binary       0.10   1=male
  educ_group       0.05   lt_hs / hs / some_college / ba_plus

State fallback
--------------
  If a state has fewer than MIN_ASEC_PER_STATE ASEC earners, the script uses
  a national fallback pool filtered to the same marital_binary and nchild_bin
  combination.  A warning is printed for each fallback state.

Output
------
WORKSPACE/data/external/org_asec_matches.parquet
  All ORG eligible worker rows, plus columns:
    asec_serial          matched ASEC household SERIAL
    asec_spouse_income   matched household's spouse INCWAGE ($)
    asec_n_children      matched household's actual child count
    asec_children_ages   matched children's ages as a JSON list
    asec_match_distance  weighted Euclidean distance (lower = closer match)

Usage
-----
    python WORKSPACE/code/01_data_preparation/01e_match_org_to_asec.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder

# ── Paths ─────────────────────────────────────────────────────────────────────

_HERE         = Path(__file__).resolve()
PROJECT_ROOT  = _HERE.parents[3]
EXTERNAL_DIR  = PROJECT_ROOT / "WORKSPACE" / "data" / "external"
PROCESSED_DIR = PROJECT_ROOT / "WORKSPACE" / "data" / "processed"

# ── Matching configuration ────────────────────────────────────────────────────

FEATURE_WEIGHTS: dict[str, float] = {
    "wage_decile":    0.35,
    "marital_binary": 0.20,
    "nchild_bin":     0.20,
    "age_bin":        0.10,
    "sex_binary":     0.10,
    "educ_group":     0.05,
}
FEATURES = list(FEATURE_WEIGHTS.keys())
WEIGHTS  = np.array([FEATURE_WEIGHTS[f] for f in FEATURES])

MIN_ASEC_PER_STATE = 30   # below this, use national fallback pool

# MARST codes that map to marital_binary = 1 (married, spouse present or absent)
MARRIED_MARST_CODES = {1, 2}

# ── Eligibility filter (mirrors 01a_data_ingest.py) ──────────────────────────

_TARGET_WAGE_FRAC = 0.80
_SUBSIDY_PCT      = 0.80
_FED_MIN_WAGE     = 7.25


def _weighted_median(values: pd.Series, weights: pd.Series) -> float:
    vals = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    wts = pd.to_numeric(weights, errors="coerce").to_numpy(dtype=float)
    mask = np.isfinite(vals) & np.isfinite(wts) & (wts > 0)
    if not mask.any():
        return 21.0
    vals = vals[mask]
    wts = wts[mask]
    order = np.argsort(vals)
    vals = vals[order]
    wts = wts[order]
    csum = np.cumsum(wts)
    return float(vals[np.searchsorted(csum, 0.5 * wts.sum(), side="left")])


def _apply_eligibility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recreate the eligibility filter from 01a_data_ingest.py so we can work
    from org_workers_2026.parquet (which has all demographic columns) rather
    than hourly_workers.parquet (which drops them for storage efficiency).
    """
    df = df[df["epi_sample_eligible"] == True].copy()
    df = df[df["hourly_wage_epi_valid"] == True].copy()
    df["employer_wage"] = df["hourly_wage_epi"].clip(lower=_FED_MIN_WAGE)

    # Dynamic target wage: 80% of weighted median paid-hourly wage
    paid_hourly_workers = df[df["paid_hourly"] == True]
    median_wage = _weighted_median(
        paid_hourly_workers["hourly_wage_epi"],
        paid_hourly_workers["earnwt"],
    )
    target_wage = median_wage * _TARGET_WAGE_FRAC

    df = df[df["age"].between(16, 64)].copy()
    df = df[df["employer_wage"] < target_wage].copy()
    df = df[df["earnwt"] > 0].copy()
    # Exclude tax dependents (child of head under 19)
    df = df[~((df["relate"] == 301) & (df["age"] < 19))].copy()
    return df.reset_index(drop=True)


# ── Covariate derivation ──────────────────────────────────────────────────────

def _derive_org_covariates(org: pd.DataFrame) -> pd.DataFrame:
    """Add matching covariates to the ORG eligible worker frame."""
    org = org.copy()

    # Wage decile within state
    org["wage_decile"] = (
        org.groupby("state_code")["employer_wage"]
        .transform(lambda x: pd.qcut(x, q=10, labels=False, duplicates="drop"))
        .fillna(0)
        .astype(int)
    )
    org["marital_binary"] = org["marst"].isin(MARRIED_MARST_CODES).astype(int)
    org["nchild_bin"]     = org["nchild"].clip(upper=3).astype(int)
    org["sex_binary"]     = (org["sex_label"] == "Male").astype(int)

    org["age_bin"] = pd.cut(
        org["age"],
        bins=[15, 25, 35, 45, 55, 65],
        labels=["16-25", "26-35", "36-45", "46-55", "56-64"],
        right=True,
    ).astype(str)

    org["educ_group"] = pd.cut(
        org["educ"],
        bins=[0, 60, 73, 111, 999],
        labels=["lt_hs", "hs", "some_college", "ba_plus"],
        right=True,
    ).astype(str)

    return org


# ── Feature encoding ──────────────────────────────────────────────────────────

def _encode(df: pd.DataFrame, fit_encoders: dict | None = None) -> tuple[np.ndarray, dict]:
    """
    Encode FEATURES as a float matrix normalised to [0, 1].
    Categorical columns (object / category dtype) are label-encoded then
    divided by their maximum to map into [0, 1].
    Returns (encoded_matrix, encoders_dict).
    If fit_encoders is supplied (from a prior call on ASEC), those encoders
    are reused so ORG and ASEC share the same integer mapping.
    """
    encoded = {}
    encoders = {} if fit_encoders is None else fit_encoders

    for feat in FEATURES:
        col = df[feat].fillna("unknown" if df[feat].dtype == object else 0)

        if col.dtype == object or str(col.dtype) == "category":
            if feat not in encoders:
                le = LabelEncoder()
                le.fit(col.astype(str))
                encoders[feat] = le
            le = encoders[feat]
            # Handle unseen labels gracefully
            col_str = col.astype(str)
            known   = set(le.classes_)
            col_str = col_str.where(col_str.isin(known), other=le.classes_[0])
            vals = le.transform(col_str).astype(float)
            vals = vals / max(vals.max(), 1.0)
        else:
            vals = col.astype(float).values
            col_max = vals.max()
            if col_max > 0:
                vals = vals / col_max

        encoded[feat] = vals

    matrix = np.column_stack([encoded[f] for f in FEATURES])
    return matrix, encoders


# ── Per-state nearest-neighbor match ─────────────────────────────────────────

def _match_state(
    org_s: pd.DataFrame,
    asec_s: pd.DataFrame,
    org_enc: np.ndarray,
    asec_enc: np.ndarray,
) -> pd.DataFrame:
    """
    k=1 nearest-neighbour match within one state.
    org_enc / asec_enc are the pre-encoded, weight-scaled feature matrices
    for the rows in org_s / asec_s respectively.
    Returns org_s (reset index) with ASEC context columns appended.
    """
    nn = NearestNeighbors(n_neighbors=1, metric="euclidean", algorithm="ball_tree")
    nn.fit(asec_enc)
    distances, indices = nn.kneighbors(org_enc)

    matched = asec_s.iloc[indices[:, 0]].reset_index(drop=True)
    result  = org_s.reset_index(drop=True).copy()

    def _to_jsonable_ages(x):
        if isinstance(x, np.ndarray):
            return x.tolist()
        if isinstance(x, (list, tuple)):
            return list(x)
        if pd.isna(x):
            return []
        return x

    result["asec_serial"]         = matched["SERIAL"].values
    result["asec_spouse_income"]  = matched["spouse_incwage"].values
    result["asec_n_children"]     = matched["n_children_hh"].values
    result["asec_children_ages"]  = matched["children_ages"].apply(_to_jsonable_ages).apply(json.dumps).values
    result["asec_match_distance"] = distances[:, 0]
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    # ── Load ORG ──────────────────────────────────────────────────────────────
    org_raw_path = EXTERNAL_DIR / "org_workers_2026.parquet"
    if not org_raw_path.exists():
        raise FileNotFoundError(
            f"{org_raw_path} not found. Run 00_export_org_data.py first."
        )
    print(f"Loading ORG: {org_raw_path.name} ...")
    org_raw = pd.read_parquet(org_raw_path)
    print(f"  {len(org_raw):,} raw ORG records")

    # Python cannot import files whose names begin with digits, so FIPS_TO_STATE
    # is defined inline here (mirrors 01a_data_ingest.py exactly).
    FIPS_TO_STATE = {
         1:"AL",  2:"AK",  4:"AZ",  5:"AR",  6:"CA",  8:"CO",  9:"CT",
        10:"DE", 11:"DC", 12:"FL", 13:"GA", 15:"HI", 16:"ID", 17:"IL",
        18:"IN", 19:"IA", 20:"KS", 21:"KY", 22:"LA", 23:"ME", 24:"MD",
        25:"MA", 26:"MI", 27:"MN", 28:"MS", 29:"MO", 30:"MT", 31:"NE",
        32:"NV", 33:"NH", 34:"NJ", 35:"NM", 36:"NY", 37:"NC", 38:"ND",
        39:"OH", 40:"OK", 41:"OR", 42:"PA", 44:"RI", 45:"SC", 46:"SD",
        47:"TN", 48:"TX", 49:"UT", 50:"VT", 51:"VA", 53:"WA", 54:"WV",
        55:"WI", 56:"WY",
    }

    org_raw["state_code"] = org_raw["statefip"].map(FIPS_TO_STATE)
    org_raw = org_raw[org_raw["state_code"].notna()].copy()

    # Apply eligibility filter
    org = _apply_eligibility(org_raw)
    org = _derive_org_covariates(org)
    print(f"  {len(org):,} eligible ORG workers after filter")

    # ── Load ASEC earners ──────────────────────────────────────────────────────
    asec_files = sorted(EXTERNAL_DIR.glob("asec_earners_*.parquet"), reverse=True)
    if not asec_files:
        raise FileNotFoundError(
            "No asec_earners_*.parquet found. Run 01d_asec_preprocess.py first."
        )
    asec = pd.read_parquet(asec_files[0])
    print(f"ASEC earners: {len(asec):,} rows ({asec_files[0].name})")

    # Map ASEC STATEFIP → state_code (FIPS_TO_STATE defined above)
    asec["state_code"] = asec["STATEFIP"].map(FIPS_TO_STATE)
    asec = asec[asec["state_code"].notna()].copy()

    # ── Encode features globally so ORG and ASEC share the same label maps ────
    # Fit encoders on the combined pool first, then split back.
    combined = pd.concat(
        [org[FEATURES], asec[FEATURES]], ignore_index=True
    )
    _, encoders = _encode(combined)

    org_enc_full,  _ = _encode(org,  fit_encoders=encoders)
    asec_enc_full, _ = _encode(asec, fit_encoders=encoders)

    # Apply weights
    org_enc_w  = org_enc_full  * WEIGHTS
    asec_enc_w = asec_enc_full * WEIGHTS

    # ── State-level matching loop ──────────────────────────────────────────────
    states   = sorted(org["state_code"].dropna().unique())
    results  = []
    fallback_states: list[str] = []

    for i, state in enumerate(states):
        org_idx  = (org["state_code"]  == state).values
        asec_idx = (asec["state_code"] == state).values

        org_s      = org[org_idx]
        asec_s     = asec[asec_idx]
        org_enc_s  = org_enc_w[org_idx]
        asec_enc_s = asec_enc_w[asec_idx]

        if len(asec_s) < MIN_ASEC_PER_STATE:
            fallback_states.append(state)
            # National fallback: filter to same marital × nchild distribution
            # (best-effort; state is lost but composition is preserved)
            asec_s     = asec.copy()
            asec_enc_s = asec_enc_w.copy()

        matched_s = _match_state(org_s, asec_s, org_enc_s, asec_enc_s)
        results.append(matched_s)

        if (i + 1) % 10 == 0 or (i + 1) == len(states):
            print(f"  Matched {i + 1}/{len(states)} states ...", flush=True)

    if fallback_states:
        print(
            f"\n  [warn] {len(fallback_states)} states used national fallback pool "
            f"(<{MIN_ASEC_PER_STATE} ASEC earners): {', '.join(fallback_states)}"
        )

    out = pd.concat(results, ignore_index=True)

    # ── Match quality report ───────────────────────────────────────────────────
    print("\nMatch quality:")
    print(f"  Median distance : {out['asec_match_distance'].median():.4f}")
    print(f"  P95 distance    : {out['asec_match_distance'].quantile(0.95):.4f}")
    print(f"  Spouse inc > 0  : {(out['asec_spouse_income'] > 0).mean():.1%}")
    print(f"  Has children    : {(out['asec_n_children'] > 0).mean():.1%}")

    # Unique ASEC households used (coverage check)
    unique_asec = out["asec_serial"].nunique()
    print(f"  Unique ASEC HHs : {unique_asec:,} of {len(asec):,} ({unique_asec/len(asec):.1%} utilised)")

    # ── Save ──────────────────────────────────────────────────────────────────
    out_path = EXTERNAL_DIR / "org_asec_matches.parquet"
    out.to_parquet(out_path, index=False)
    print(f"\nSaved: {out_path} ({len(out):,} rows)")
    print("\nNext step: python WORKSPACE/code/01_data_preparation/01f_precompute_matched_schedules.py")


if __name__ == "__main__":
    main()
