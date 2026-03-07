# 00_config.py -- baseline project configuration
from __future__ import annotations
import os
from pathlib import Path


def _find_project_root(start: Path = Path.cwd(), max_up: int = 10) -> Path:
    cur = start.resolve()
    for _ in range(max_up + 1):
        if (cur / "WORKSPACE" / "code" / "run_all.py").exists() or \
           (cur / "WORKSPACE" / "code" / "run_all.R").exists() or \
           (cur / "WORKSPACE" / "code" / "run_all.do").exists():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    raise RuntimeError(
        "Could not locate project root. "
        "Set EIG_PROJECT_ROOT or run from the repo root."
    )


# Project root: env var takes priority, then walk upward from this file
_env_root = os.environ.get("EIG_PROJECT_ROOT", "")
PATH_PROJECT = Path(_env_root).resolve() if _env_root else _find_project_root(
    Path(__file__).resolve().parent
)

# Paths
PATH_CODE                = PATH_PROJECT / "WORKSPACE" / "code"
PATH_DATA                = PATH_PROJECT / "WORKSPACE" / "data"
PATH_DATA_RAW            = PATH_DATA / "raw"
PATH_DATA_PROCESSED      = PATH_DATA / "processed"
PATH_OUTPUT              = PATH_PROJECT / "WORKSPACE" / "output"
PATH_OUTPUT_FIG_MAIN     = PATH_OUTPUT / "figures" / "main"
PATH_OUTPUT_FIG_APPENDIX = PATH_OUTPUT / "figures" / "appendix"
PATH_OUTPUT_TBL_MAIN     = PATH_OUTPUT / "tables" / "main"
PATH_OUTPUT_TBL_APPENDIX = PATH_OUTPUT / "tables" / "appendix"
PATH_OUTPUT_INTERMEDIATE = PATH_OUTPUT / "data" / "intermediate_results"

# Project settings
cfg = {
    "project_name":       "eig-wagesubsidy-policy-sim",
    "audience":           "Public — interactive web simulation + blog post",
    "project_scope_tier": 1,   # 1=Descriptive/Blog  2=Analytical Brief  3=Full Research Paper
    "currency_base_year": 2024,
    "fig_width":          6.5,
    "fig_height":         3.5,
    "fig_dpi":            300,
    "seed":               1234,
    # Wage subsidy policy parameters (EIG 80-80 Rule)
    "ws_median_hourly_wage":  20.00,  # 2024 CPS median hourly wage for hourly workers
    "ws_target_pct":          0.80,   # target wage = 80% of median
    "ws_subsidy_pct":         0.80,   # subsidy covers 80% of gap
    "ws_base_wage":           7.25,   # federal minimum wage (base wage floor)
    # Derived (convenience)
    "ws_target_wage":         16.00,  # 0.80 * 20.00
    "ws_max_subsidy":         7.00,   # 0.80 * (16.00 - 7.25) ≈ 7.00
    "ws_hours_per_year":      2000,   # 40 hrs/wk * 50 wks
}

# Directory creation — base dirs (all tiers)
for _d in [PATH_DATA_RAW, PATH_DATA_PROCESSED, PATH_OUTPUT_FIG_MAIN, PATH_OUTPUT_TBL_MAIN]:
    _d.mkdir(parents=True, exist_ok=True)

# Tier 2+: intermediate results
if cfg["project_scope_tier"] >= 2:
    PATH_OUTPUT_INTERMEDIATE.mkdir(parents=True, exist_ok=True)

# Tier 3: appendix directories
if cfg["project_scope_tier"] >= 3:
    PATH_OUTPUT_FIG_APPENDIX.mkdir(parents=True, exist_ok=True)
    PATH_OUTPUT_TBL_APPENDIX.mkdir(parents=True, exist_ok=True)

print(f"Loaded config. Project root: {PATH_PROJECT}")
