# run_all.py -- baseline pipeline orchestrator
# Canonical name: WORKSPACE/code/run_all.py
from __future__ import annotations

import importlib.util
import os
import time
from pathlib import Path


def find_project_root(start: Path = Path.cwd(), max_up: int = 10) -> Path:
    cur = start.resolve()
    for _ in range(max_up + 1):
        if (cur / "WORKSPACE" / "code" / "run_all.py").exists():
            return cur
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    raise RuntimeError(
        "Could not locate project root. "
        "Set EIG_PROJECT_ROOT or run from the repo root."
    )


def execute_python_script(script_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Python script: {script_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)


env_root = os.environ.get("EIG_PROJECT_ROOT", "")
PROJECT_ROOT = Path(env_root).resolve() if env_root else find_project_root(
    Path(__file__).resolve().parent
)
os.chdir(PROJECT_ROOT)
print(f"Project root: {PROJECT_ROOT}")

# Load config by file path -- avoids Python module-name restrictions on 00_setup/
cfg_path = PROJECT_ROOT / "WORKSPACE" / "code" / "00_setup" / "00_config.py"
if not cfg_path.exists():
    raise FileNotFoundError(f"Config not found: {cfg_path}")
cfg_spec = importlib.util.spec_from_file_location("eig_config", cfg_path)
if cfg_spec is None or cfg_spec.loader is None:
    raise RuntimeError(f"Could not load config: {cfg_path}")
cfg = importlib.util.module_from_spec(cfg_spec)
cfg_spec.loader.exec_module(cfg)

tier_stages: dict[int, list[str]] = {
    1: ["01", "02", "05"],
    2: ["01", "02", "03", "05"],
    3: ["01", "02", "03", "04", "05"],
}

tier = int(cfg.cfg["project_scope_tier"])
if tier not in tier_stages:
    raise ValueError(f"Invalid project_scope_tier in cfg: {tier} (expected 1, 2, or 3)")
active_stages = tier_stages[tier]

# ============================================================================
# Readable Pipeline Flags (one component per line)
# ============================================================================
# Stage flags
RUN_STAGE_01_DATA_PREPARATION = True
RUN_STAGE_02_DESCRIPTIVE_ANALYSIS = True
RUN_STAGE_03_MAIN_ESTIMATION = True
RUN_STAGE_04_ROBUSTNESS = True
RUN_STAGE_05_FIGURES_TABLES = True

# Script flags
# Default FALSE because baseline ships with R stage placeholders only.
RUN_01A_DATA_INGEST = False
RUN_01B_PRECOMPUTE_INDIVIDUAL = False   # set True to regenerate individual_schedules/
RUN_02A_DESCRIPTIVE_STATS = False
RUN_03A_MAIN_MODEL = False
RUN_04A_ROBUSTNESS_CHECKS = False
RUN_05A_MAIN_OUTPUTS = False

# Behavior flags
STOP_ON_ERROR_ANY_STAGE = False
FAIL_HARD_STAGES = {"01", "02", "03"}

# Apply tier constraints to stage flags
if "01" not in active_stages:
    RUN_STAGE_01_DATA_PREPARATION = False
if "02" not in active_stages:
    RUN_STAGE_02_DESCRIPTIVE_ANALYSIS = False
if "03" not in active_stages:
    RUN_STAGE_03_MAIN_ESTIMATION = False
if "04" not in active_stages:
    RUN_STAGE_04_ROBUSTNESS = False
if "05" not in active_stages:
    RUN_STAGE_05_FIGURES_TABLES = False

print(f"Active pipeline tier: {tier} (stages: {', '.join(active_stages)})")
print("Stage flags:")
print(f"  RUN_STAGE_01_DATA_PREPARATION = {RUN_STAGE_01_DATA_PREPARATION}")
print(f"  RUN_STAGE_02_DESCRIPTIVE_ANALYSIS = {RUN_STAGE_02_DESCRIPTIVE_ANALYSIS}")
print(f"  RUN_STAGE_03_MAIN_ESTIMATION = {RUN_STAGE_03_MAIN_ESTIMATION}")
print(f"  RUN_STAGE_04_ROBUSTNESS = {RUN_STAGE_04_ROBUSTNESS}")
print(f"  RUN_STAGE_05_FIGURES_TABLES = {RUN_STAGE_05_FIGURES_TABLES}")
print("Script flags:")
print(f"  RUN_01A_DATA_INGEST = {RUN_01A_DATA_INGEST}")
print(f"  RUN_01B_PRECOMPUTE_INDIVIDUAL = {RUN_01B_PRECOMPUTE_INDIVIDUAL}")
print(f"  RUN_02A_DESCRIPTIVE_STATS = {RUN_02A_DESCRIPTIVE_STATS}")
print(f"  RUN_03A_MAIN_MODEL = {RUN_03A_MAIN_MODEL}")
print(f"  RUN_04A_ROBUSTNESS_CHECKS = {RUN_04A_ROBUSTNESS_CHECKS}")
print(f"  RUN_05A_MAIN_OUTPUTS = {RUN_05A_MAIN_OUTPUTS}")

run_log: list[dict[str, object]] = []


def run_script(
    script_id: str,
    stage: str,
    script_path: str,
    label: str,
    run_stage_flag: bool,
    run_script_flag: bool,
) -> None:
    if not run_stage_flag:
        print(f"[SKIP STAGE] {script_id} (stage {stage} disabled)")
        run_log.append(
            {
                "script_id": script_id,
                "stage": stage,
                "path": script_path,
                "status": "SKIPPED_STAGE",
                "elapsed_seconds": 0.0,
                "error_msg": "",
            }
        )
        return

    if not run_script_flag:
        print(f"[SKIP FLAG] {script_id} (script flag disabled)")
        run_log.append(
            {
                "script_id": script_id,
                "stage": stage,
                "path": script_path,
                "status": "SKIPPED_FLAG",
                "elapsed_seconds": 0.0,
                "error_msg": "",
            }
        )
        return

    path_obj = Path(script_path)
    if not path_obj.exists():
        err = f"Script not found: {script_path}"
        run_log.append(
            {
                "script_id": script_id,
                "stage": stage,
                "path": script_path,
                "status": "FAILED",
                "elapsed_seconds": 0.0,
                "error_msg": err,
            }
        )
        print(f"FAILED: {err}")
        if STOP_ON_ERROR_ANY_STAGE or stage in FAIL_HARD_STAGES:
            raise RuntimeError(f"Pipeline halted at {script_id}: {err}")
        return

    print(f"Running {script_id} | {label} | {script_path}")
    t0 = time.time()
    try:
        execute_python_script(path_obj)
        status = "SUCCESS"
        err = ""
    except Exception as exc:  # noqa: BLE001
        status = "FAILED"
        err = str(exc)
        print(f"FAILED: {err}")
    elapsed = round(time.time() - t0, 1)

    run_log.append(
        {
            "script_id": script_id,
            "stage": stage,
            "path": script_path,
            "status": status,
            "elapsed_seconds": elapsed,
            "error_msg": err,
        }
    )

    if status == "FAILED" and (STOP_ON_ERROR_ANY_STAGE or stage in FAIL_HARD_STAGES):
        raise RuntimeError(f"Pipeline halted at {script_id}: {err}")


pipeline_start = time.time()

run_script(
    script_id="01a",
    stage="01",
    script_path="WORKSPACE/code/01_data_preparation/01a_data_ingest.py",
    label="Data ingest",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01A_DATA_INGEST,
)

run_script(
    script_id="01b",
    stage="01",
    script_path="WORKSPACE/code/01_data_preparation/01b_precompute_individual.py",
    label="Pre-compute individual calculator schedules",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01B_PRECOMPUTE_INDIVIDUAL,
)

run_script(
    script_id="02a",
    stage="02",
    script_path="WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.py",
    label="Descriptive stats",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02A_DESCRIPTIVE_STATS,
)

run_script(
    script_id="03a",
    stage="03",
    script_path="WORKSPACE/code/03_main_estimation/03a_main_model.py",
    label="Main model",
    run_stage_flag=RUN_STAGE_03_MAIN_ESTIMATION,
    run_script_flag=RUN_03A_MAIN_MODEL,
)

run_script(
    script_id="04a",
    stage="04",
    script_path="WORKSPACE/code/04_robustness_heterogeneity/04a_robustness_checks.py",
    label="Robustness checks",
    run_stage_flag=RUN_STAGE_04_ROBUSTNESS,
    run_script_flag=RUN_04A_ROBUSTNESS_CHECKS,
)

run_script(
    script_id="05a",
    stage="05",
    script_path="WORKSPACE/code/05_figures_tables/05a_main_outputs.py",
    label="Main outputs",
    run_stage_flag=RUN_STAGE_05_FIGURES_TABLES,
    run_script_flag=RUN_05A_MAIN_OUTPUTS,
)

pipeline_elapsed = round(time.time() - pipeline_start, 1)
n_success = sum(1 for row in run_log if row["status"] == "SUCCESS")
n_failed = sum(1 for row in run_log if row["status"] == "FAILED")
n_skipped = sum(
    1
    for row in run_log
    if row["status"] in {"SKIPPED_STAGE", "SKIPPED_FLAG"}
)

print("Pipeline complete")
print(f"  Success: {n_success}")
print(f"  Failed:  {n_failed}")
print(f"  Skipped: {n_skipped}")
print(f"  Elapsed: {pipeline_elapsed}s")
for row in run_log:
    print(f"  {row['script_id']} -> {row['status']} ({row['elapsed_seconds']}s)")



