# run_all.py -- baseline pipeline orchestrator
# Canonical name: code/run_all.py
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import time
from pathlib import Path


def find_project_root(start: Path = Path.cwd(), max_up: int = 10) -> Path:
    cur = start.resolve()
    for _ in range(max_up + 1):
        if (cur / "code" / "run_all.py").exists():
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
cfg_path = PROJECT_ROOT / "code" / "00_setup" / "00_config.py"
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
RUN_00_INGEST_ORG = True               # vendored EIG-Wage-Figure R ORG build (00a→01a→01b) → data/{raw,intermediate}/. Needs Rscript + IPUMS key (.Renviron). 00a is IPUMS-cache-guarded (no resubmit unless samples/variables change).
RUN_01A_DATA_INGEST = True             # CPS extraction → data/processed/hourly_workers.parquet
RUN_01B_PRECOMPUTE_INDIVIDUAL = False  # set True to regenerate individual_schedules/
RUN_01I_HOUSEHOLD_LINKS = True         # In-ORG spouse links + child-under-5 flags (required by 01h)
RUN_01H_NONEMPLOYED_POOL = True        # ORG non-employed pool for 02d (raw partitions: no-op if absent; household_links: hard requirement, run 01i first)
RUN_02A_DESCRIPTIVE_STATS = True       # population aggregation → intermediate_results/population/
RUN_02B_BEHAVIORAL_SCENARIOS = True    # dynamic cost band → population/behavioral_scenarios.parquet
RUN_02C_INCIDENCE = False              # SUPERSEDED by 02d (band-clearing incidence; kept for reference)
RUN_02D_MATCHING_SIMULATION = True     # structural matching sim → population/matching_simulation.parquet
RUN_02E_TAKE_UP_BY_GROUP = True        # take-up rate by demographic group → population/take_up_by_group.parquet
RUN_02F_MPL_IMPUTATION_BAND = True     # MPL-imputation sensitivity band (MR-001) → population/mpl_imputation_band.parquet
RUN_02G_ENTRY_SCENARIO_GRID = True     # Joint scenario grid + 3 headline bundles → population/entry_scenario_grid.parquet, entry_headline_scenarios.parquet
RUN_03A_MAIN_MODEL = False
RUN_04A_ROBUSTNESS_CHECKS = False
RUN_05A_MAIN_OUTPUTS = True            # verify outputs + print summary
RUN_05_R_FIGURES = True                # EIG R/ggplot2 publication figures (05c + 05d); needs Rscript

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
print(f"  RUN_00_INGEST_ORG = {RUN_00_INGEST_ORG}")
print(f"  RUN_01A_DATA_INGEST = {RUN_01A_DATA_INGEST}")
print(f"  RUN_01B_PRECOMPUTE_INDIVIDUAL = {RUN_01B_PRECOMPUTE_INDIVIDUAL}")
print(f"  RUN_01I_HOUSEHOLD_LINKS = {RUN_01I_HOUSEHOLD_LINKS}")
print(f"  RUN_01H_NONEMPLOYED_POOL = {RUN_01H_NONEMPLOYED_POOL}")
print(f"  RUN_02A_DESCRIPTIVE_STATS = {RUN_02A_DESCRIPTIVE_STATS}")
print(f"  RUN_02B_BEHAVIORAL_SCENARIOS = {RUN_02B_BEHAVIORAL_SCENARIOS}")
print(f"  RUN_02C_INCIDENCE = {RUN_02C_INCIDENCE}")
print(f"  RUN_02D_MATCHING_SIMULATION = {RUN_02D_MATCHING_SIMULATION}")
print(f"  RUN_02E_TAKE_UP_BY_GROUP = {RUN_02E_TAKE_UP_BY_GROUP}")
print(f"  RUN_02F_MPL_IMPUTATION_BAND = {RUN_02F_MPL_IMPUTATION_BAND}")
print(f"  RUN_02G_ENTRY_SCENARIO_GRID = {RUN_02G_ENTRY_SCENARIO_GRID}")
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


def run_r_stage(
    script_id: str,
    stage: str,
    r_scripts: list[str],
    label: str,
    run_stage_flag: bool,
    run_script_flag: bool,
) -> None:
    """Run a sequence of vendored R scripts via Rscript (subprocess), chained in
    order. Used for the internalized CPS ORG wage build (code/00_ingest/). The R
    dependency is dev/pipeline-only; the Streamlit app deployment stays Python."""
    if not run_stage_flag:
        print(f"[SKIP STAGE] {script_id} (stage {stage} disabled)")
        run_log.append({"script_id": script_id, "stage": stage, "path": ";".join(r_scripts),
                        "status": "SKIPPED_STAGE", "elapsed_seconds": 0.0, "error_msg": ""})
        return
    if not run_script_flag:
        print(f"[SKIP FLAG] {script_id} (script flag disabled)")
        run_log.append({"script_id": script_id, "stage": stage, "path": ";".join(r_scripts),
                        "status": "SKIPPED_FLAG", "elapsed_seconds": 0.0, "error_msg": ""})
        return

    rscript = shutil.which("Rscript")
    if rscript is None:
        err = "Rscript not found on PATH; cannot run the R ORG ingestion stage."
        run_log.append({"script_id": script_id, "stage": stage, "path": ";".join(r_scripts),
                        "status": "FAILED", "elapsed_seconds": 0.0, "error_msg": err})
        print(f"FAILED: {err}")
        if STOP_ON_ERROR_ANY_STAGE or stage in FAIL_HARD_STAGES:
            raise RuntimeError(f"Pipeline halted at {script_id}: {err}")
        return

    print(f"Running {script_id} | {label}")
    t0 = time.time()
    status, err = "SUCCESS", ""
    try:
        for rs in r_scripts:
            if not Path(rs).exists():
                raise FileNotFoundError(f"R script not found: {rs}")
            print(f"  Rscript {rs}")
            subprocess.run([rscript, rs], cwd=str(PROJECT_ROOT), check=True)
    except Exception as exc:  # noqa: BLE001
        status, err = "FAILED", str(exc)
        print(f"FAILED: {err}")
    elapsed = round(time.time() - t0, 1)

    run_log.append({"script_id": script_id, "stage": stage, "path": ";".join(r_scripts),
                    "status": status, "elapsed_seconds": elapsed, "error_msg": err})

    if status == "FAILED" and (STOP_ON_ERROR_ANY_STAGE or stage in FAIL_HARD_STAGES):
        raise RuntimeError(f"Pipeline halted at {script_id}: {err}")


pipeline_start = time.time()

run_r_stage(
    script_id="00_ingest",
    stage="01",
    r_scripts=[
        "code/00_ingest/00a_download-ipums-cps.R",
        "code/00_ingest/01a_load-ipums-cps.R",
        "code/00_ingest/01b_build-org-panel.R",
    ],
    label="Vendored CPS ORG wage build (EIG-Wage-Figure 00a->01a->01b)",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_00_INGEST_ORG,
)

run_script(
    script_id="01a",
    stage="01",
    script_path="code/01_data_preparation/01a_data_ingest.py",
    label="Data ingest",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01A_DATA_INGEST,
)

run_script(
    script_id="01b",
    stage="01",
    script_path="code/01_data_preparation/01b_precompute_individual.py",
    label="Pre-compute individual calculator schedules",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01B_PRECOMPUTE_INDIVIDUAL,
)

run_script(
    script_id="01i",
    stage="01",
    script_path="code/01_data_preparation/01i_household_links.py",
    label="In-ORG household links (spouse employment, child-under-5)",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01I_HOUSEHOLD_LINKS,
)

run_script(
    script_id="01h",
    stage="01",
    script_path="code/01_data_preparation/01h_nonemployed_pool.py",
    label="ORG non-employed pool (matching sim input)",
    run_stage_flag=RUN_STAGE_01_DATA_PREPARATION,
    run_script_flag=RUN_01H_NONEMPLOYED_POOL,
)

run_script(
    script_id="02a",
    stage="02",
    script_path="code/02_descriptive_analysis/02a_descriptive_stats.py",
    label="Descriptive stats",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02A_DESCRIPTIVE_STATS,
)

run_script(
    script_id="02b",
    stage="02",
    script_path="code/02_descriptive_analysis/02b_behavioral_scenarios.py",
    label="Behavioral (dynamic) cost scenarios",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02B_BEHAVIORAL_SCENARIOS,
)

run_script(
    script_id="02c",
    stage="02",
    script_path="code/02_descriptive_analysis/02c_incidence.py",
    label="Wage incidence + dynamic-cost decomposition",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02C_INCIDENCE,
)

run_script(
    script_id="02d",
    stage="02",
    script_path="code/02_descriptive_analysis/02d_matching_simulation.py",
    label="Structural search-and-matching simulation",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02D_MATCHING_SIMULATION,
)

run_script(
    script_id="02e",
    stage="02",
    script_path="code/02_descriptive_analysis/02e_take_up_by_group.py",
    label="Take-up rate by demographic group",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02E_TAKE_UP_BY_GROUP,
)

run_script(
    script_id="02f",
    stage="02",
    script_path="code/02_descriptive_analysis/02f_mpl_imputation_band.py",
    label="MPL-imputation sensitivity band (MR-001)",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02F_MPL_IMPUTATION_BAND,
)

run_script(
    script_id="02g",
    stage="02",
    script_path="code/02_descriptive_analysis/02g_entry_scenario_grid.py",
    label="Entry scenario grid + headline bundles (re-center)",
    run_stage_flag=RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
    run_script_flag=RUN_02G_ENTRY_SCENARIO_GRID,
)

run_script(
    script_id="03a",
    stage="03",
    script_path="code/03_main_estimation/03a_main_model.py",
    label="Main model",
    run_stage_flag=RUN_STAGE_03_MAIN_ESTIMATION,
    run_script_flag=RUN_03A_MAIN_MODEL,
)

run_script(
    script_id="04a",
    stage="04",
    script_path="code/04_robustness_heterogeneity/04a_robustness_checks.py",
    label="Robustness checks",
    run_stage_flag=RUN_STAGE_04_ROBUSTNESS,
    run_script_flag=RUN_04A_ROBUSTNESS_CHECKS,
)

run_script(
    script_id="05a",
    stage="05",
    script_path="code/05_figures_tables/05a_main_outputs.py",
    label="Main outputs",
    run_stage_flag=RUN_STAGE_05_FIGURES_TABLES,
    run_script_flag=RUN_05A_MAIN_OUTPUTS,
)

# EIG R/ggplot2 publication figures (Figures 1-13). These read the population parquets and
# write PNG+SVG to output/figures/main/. R (not Python) because the canonical EIG figure theme
# lives in Infrastructure/style/themes/r/. Skipped gracefully if Rscript is absent.
if RUN_STAGE_05_FIGURES_TABLES and RUN_05_R_FIGURES:
    _rscript = shutil.which("Rscript")
    if _rscript is None:
        print("05c/05d | [skip] Rscript not on PATH — R figures not regenerated.")
    else:
        for _fig_script in ("code/05_figures_tables/05c_core_figures.R",
                            "code/05_figures_tables/05d_supporting_figures.R"):
            print(f"  Rscript {_fig_script}")
            _t0 = time.time()
            _rc = subprocess.run([_rscript, _fig_script], cwd=str(PROJECT_ROOT)).returncode
            run_log.append({"script_id": Path(_fig_script).stem, "status":
                            "SUCCESS" if _rc == 0 else "FAILED",
                            "elapsed_seconds": round(time.time() - _t0, 1)})

# Intermediate-outputs manifest (the "easy grab" index; see code/_utils/intermediates.py).
run_script(
    script_id="05z",
    stage="05",
    script_path="code/05_figures_tables/05z_build_manifest.py",
    label="Build intermediate-outputs manifest",
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



