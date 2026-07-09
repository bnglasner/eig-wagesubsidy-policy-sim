"""
02e_take_up_by_group.py — Take-up rate by demographic group (share of each group's
hourly workers who are subsidy-eligible).

Fills the gap left by 02a's `pct_in_group`, which is emitted null because its base-population
file (data/external/org_workers_*.parquet) is absent from this checkout. Here the base is
reconstructed from the in-repo CPS ORG panel via 01a's own adapter, so the recipient counts
match the published by_* tables exactly and the denominator is the same pre-wage-threshold
universe 02a intends. Output is a clean intermediate for figures/tables/numeric use.

Denominator = wage-observed hourly workforce ages 16-64 (epi_sample_eligible &
hourly_wage_epi_valid & earnwt>0, minus the child-dependent exclusion), earnwt/n_months
weighted. NOT all employed persons (excludes self-employed and workers without a measurable
hourly wage). Numerator = that base restricted to employer_wage < target.

Output: output/data/intermediate_results/population/take_up_by_group.parquet
  columns: dimension, group, recipients_k, base_k, share_of_recipients_pct, take_up_pct
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve()
_CODE = _HERE.parents[1]
_spec = importlib.util.spec_from_file_location("m01a", _CODE / "01_data_preparation" / "01a_data_ingest.py")
_m01a = importlib.util.module_from_spec(_spec); sys.modules["m01a"] = _m01a; _spec.loader.exec_module(_m01a)

_cfg_spec = importlib.util.spec_from_file_location("eig_config", _CODE / "00_setup" / "00_config.py")
_cfg = importlib.util.module_from_spec(_cfg_spec); _cfg_spec.loader.exec_module(_cfg)
PATH_OUTPUT_INTERMEDIATE = _cfg.PATH_OUTPUT_INTERMEDIATE
PATH_DATA_PROCESSED = _cfg.PATH_DATA_PROCESSED

FED = float(_cfg.cfg.get("ws_base_wage", 7.25))

_EDUC_MAP = {1: "Less than HS", 2: "Less than HS", 10: "Less than HS", 20: "Less than HS",
    30: "Less than HS", 40: "Less than HS", 50: "Less than HS", 60: "Less than HS",
    71: "HS diploma / GED", 73: "HS diploma / GED",
    81: "Some college / Associate's", 91: "Some college / Associate's", 92: "Some college / Associate's",
    111: "Bachelor's degree", 123: "Graduate degree", 124: "Graduate degree", 125: "Graduate degree"}
_DIMS = {"sex_label": "Sex", "age_bin": "Age", "educ_group": "Education",
         "race_ethnicity": "Race and ethnicity", "family_type": "Family type"}


def _load_target() -> float:
    import json
    p = PATH_DATA_PROCESSED / "org_target_wage.json"
    if p.exists():
        try:
            return float(json.loads(p.read_text())["target_wage"])
        except Exception:  # noqa: BLE001
            pass
    return float(_cfg.cfg.get("ws_target_wage", 16.80))


def main() -> None:
    target = _load_target()
    org = _m01a._load_and_adapt_org_panel()
    # Paid-hourly frame: both the numerator (recipients) and the denominator
    # (the group's workers) are restricted to paid-hourly workers, matching the
    # subsidy's paid-hourly eligibility (01a) and the target/imputation frame.
    # (Consistency review CC-001, 2026-07-09.)
    base = org[
        org["epi_sample_eligible"].astype(bool) &
        org["paid_hourly"].astype(bool) &
        org["hourly_wage_epi_valid"].astype(bool) &
        org["age"].between(16, 64) & (org["earnwt"] > 0)
    ].copy()
    base = base[~((base["relate"] == 301) & (base["age"] < 19))]
    base["employer_wage"] = base["hourly_wage_epi"].clip(lower=FED)
    base["educ_group"] = base["educ"].map(lambda c: _EDUC_MAP.get(int(c), "Unknown"))
    base["family_type"] = [
        ("Married" if int(m) in (1, 2) else "Single") + (", with children" if int(n) >= 1 else ", no children")
        for m, n in zip(base["marst"], base["nchild"])]
    n_months = base.groupby(["year", "month"]).ngroups
    recip = base[base["employer_wage"] < target]

    rows = []
    total_recip = recip["earnwt"].sum() / n_months
    for col, dim in _DIMS.items():
        b = base.groupby(col)["earnwt"].sum() / n_months
        r = recip.groupby(col)["earnwt"].sum() / n_months
        for g in b.index:
            rk = float(r.get(g, 0.0)); bk = float(b.get(g, 0.0))
            rows.append({
                "dimension": dim, "group": str(g),
                "recipients_k": round(rk / 1e3, 1), "base_k": round(bk / 1e3, 1),
                "share_of_recipients_pct": round(100 * rk / total_recip, 1) if total_recip else None,
                "take_up_pct": round(100 * rk / bk, 1) if bk > 0 else None,
            })
    out = pd.DataFrame(rows)
    out_dir = PATH_OUTPUT_INTERMEDIATE / "population"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "take_up_by_group.parquet"
    out.to_parquet(out_path, index=False)
    overall = 100 * total_recip / (base["earnwt"].sum() / n_months)
    print(f"02e | Wrote {out_path} | {len(out)} group rows | overall take-up {overall:.1f}% "
          f"(recipients {total_recip/1e6:.2f}M / base {base['earnwt'].sum()/n_months/1e6:.2f}M)")


if __name__ == "__main__":
    main()
