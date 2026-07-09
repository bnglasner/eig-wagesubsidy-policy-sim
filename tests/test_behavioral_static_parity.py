"""
Regression test: the `static` behavioral scenario in 02b must reproduce the
static cost from 02a exactly (the spec's non-negotiable "static path unchanged").

Run:  .venv_verify/bin/python tests/test_behavioral_static_parity.py
(or via pytest if available). Requires 02a's summary.parquet to exist.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
_SUMMARY = _ROOT / "output/data/intermediate_results/population/summary.parquet"
_WORKERS = _ROOT / "data/processed/hourly_workers.parquet"


def _load_02b():
    path = _ROOT / "code/02_descriptive_analysis/02b_behavioral_scenarios.py"
    spec = importlib.util.spec_from_file_location("mod_02b", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_static_scenario_matches_02a():
    assert _SUMMARY.exists(), "Run 02a first to produce summary.parquet"
    assert _WORKERS.exists(), "Run 01a first to produce hourly_workers.parquet"

    mod = _load_02b()
    static_scn = mod.cfg["behavioral"]["scenarios"]["static"]
    income_max = float(mod.cfg["behavioral"]["schedule_income_max"])
    workers = pd.read_parquet(_WORKERS)

    res = mod._scenario_costs(workers, static_scn, income_max)
    ref = pd.read_parquet(_SUMMARY).iloc[0]

    # Point-estimate tolerance per .claude/rules/replication-protocol.md (< 0.01).
    assert abs(res["gross_cost_bn"] - float(ref["gross_cost_bn"])) < 0.01, (
        f"gross mismatch: 02b={res['gross_cost_bn']} vs 02a={ref['gross_cost_bn']}"
    )
    assert abs(res["net_cost_bn"] - float(ref["net_cost_bn"])) < 0.01, (
        f"net mismatch: 02b={res['net_cost_bn']} vs 02a={ref['net_cost_bn']}"
    )
    assert abs(res["n_workers_mn"] - float(ref["n_workers_mn"])) < 0.01, (
        f"workers mismatch: 02b={res['n_workers_mn']} vs 02a={ref['n_workers_mn']}"
    )
    assert res["induced_workers_mn"] == 0.0, "static scenario must induce zero entrants"
    return res, ref


if __name__ == "__main__":
    res, ref = test_static_scenario_matches_02a()
    print("PASS — static parity holds.")
    print(f"  gross_cost_bn : 02b={res['gross_cost_bn']}  02a={float(ref['gross_cost_bn'])}")
    print(f"  net_cost_bn   : 02b={res['net_cost_bn']}  02a={float(ref['net_cost_bn'])}")
    print(f"  n_workers_mn  : 02b={res['n_workers_mn']}  02a={float(ref['n_workers_mn'])}")
