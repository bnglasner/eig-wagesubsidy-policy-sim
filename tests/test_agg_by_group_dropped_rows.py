"""
Regression test for 02a `_agg_by_group`: when `valid_mask` drops one or more
rows, `net_income_delta` (filtered positionally) must stay aligned with each
group's rows. The pre-fix code indexed the length-m array with the DataFrame's
ORIGINAL labels, which raised IndexError (or silently pulled the wrong worker's
delta) whenever a non-trailing row was dropped. See code-error-report.html.

Both cases below drop a non-trailing row, so on the pre-fix code they raise
IndexError; on the fixed code they return the correctly aligned group means.

Run:  .venv/bin/python tests/test_agg_by_group_dropped_rows.py   (or via pytest)
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]


def _load_02a():
    path = _ROOT / "code/02_descriptive_analysis/02a_descriptive_stats.py"
    spec = importlib.util.spec_from_file_location("mod_02a", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_notna_path_drops_row_and_stays_aligned():
    """A NaN group value is dropped by the `.notna()` branch (no ordered_labels)."""
    mod = _load_02a()
    workers = pd.DataFrame({
        "grp":            ["A", None, "A", "B"],   # row 1 (non-trailing) is dropped
        "weight":         [1.0, 1.0, 1.0, 1.0],
        "subsidy_annual": [100.0, 100.0, 100.0, 100.0],
    })  # default RangeIndex 0..3, as produced by read_parquet in production
    net_income_delta = np.array([10.0, 999.0, 30.0, 40.0])  # 999 belongs to the dropped row

    out = mod._agg_by_group(
        workers, net_income_delta,
        total_weights=3.0, gross_cost_bn=1.0, col="grp",
    )
    got = dict(zip(out["grp"], out["avg_net_income_gain"]))
    # Correct alignment: A = mean(10, 30) = 20; B = 40. A misalignment would give
    # A = mean(10, 40) = 25 and B would index out of bounds (pre-fix crash).
    assert got == {"A": 20.0, "B": 40.0}, got


def test_ordered_labels_path_drops_row_and_stays_aligned():
    """A value outside `ordered_labels` is dropped by the `.isin()` branch."""
    mod = _load_02a()
    workers = pd.DataFrame({
        "grp":            ["A", "Z", "B", "A"],    # row 1 ("Z") is dropped
        "weight":         [1.0, 1.0, 1.0, 1.0],
        "subsidy_annual": [100.0, 100.0, 100.0, 100.0],
    })
    net_income_delta = np.array([10.0, 999.0, 40.0, 20.0])  # 999 belongs to the dropped "Z" row

    out = mod._agg_by_group(
        workers, net_income_delta,
        total_weights=3.0, gross_cost_bn=1.0, col="grp",
        ordered_labels=["A", "B"],
    )
    got = dict(zip(out["grp"], out["avg_net_income_gain"]))
    # Correct alignment: A = mean(10, 20) = 15; B = 40.
    assert got == {"A": 15.0, "B": 40.0}, got


if __name__ == "__main__":
    test_notna_path_drops_row_and_stays_aligned()
    test_ordered_labels_path_drops_row_and_stays_aligned()
    print("PASS — _agg_by_group stays aligned when valid_mask drops a non-trailing row.")
