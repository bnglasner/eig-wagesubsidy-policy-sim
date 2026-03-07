* run_all.do -- baseline pipeline orchestrator

* Root detection --------------------------------------------------------------
* Priority: EIG_PROJECT_ROOT env var -> current working directory.
* Set EIG_PROJECT_ROOT or cd to the repo root before invoking this file.
local env_root : env EIG_PROJECT_ROOT
if `"`env_root'"' != "" {
    cd `"`env_root'"'
}

* Bootstrap config ------------------------------------------------------------
do "WORKSPACE/code/00_setup/00_config.do"

* Tier stage map --------------------------------------------------------------
local tier = $project_scope_tier
if      `tier' == 1 local active_stages "01 02 05"
else if `tier' == 2 local active_stages "01 02 03 05"
else if `tier' == 3 local active_stages "01 02 03 04 05"
else {
    di as err "Invalid project_scope_tier: `tier' (expected 1, 2, or 3)"
    exit 198
}

di as res "Active pipeline tier: `tier' (stages: `active_stages')"

* ============================================================================
* Readable Pipeline Flags (one component per line)
* ============================================================================
* Stage flags
local RUN_STAGE_01_DATA_PREPARATION     1
local RUN_STAGE_02_DESCRIPTIVE_ANALYSIS 1
local RUN_STAGE_03_MAIN_ESTIMATION      1
local RUN_STAGE_04_ROBUSTNESS           1
local RUN_STAGE_05_FIGURES_TABLES       1

* Script flags
* Default 0 because baseline ships with R stage placeholders only.
local RUN_01A_DATA_INGEST       0
local RUN_02A_DESCRIPTIVE_STATS 0
local RUN_03A_MAIN_MODEL        0
local RUN_04A_ROBUSTNESS_CHECKS 0
local RUN_05A_MAIN_OUTPUTS      0

* Behavior flags
local STOP_ON_ERROR_ANY_STAGE 0
local FAIL_HARD_STAGES "01 02 03"

* Apply tier constraints to stage flags
if strpos(" `active_stages' ", " 01 ") == 0 local RUN_STAGE_01_DATA_PREPARATION     0
if strpos(" `active_stages' ", " 02 ") == 0 local RUN_STAGE_02_DESCRIPTIVE_ANALYSIS 0
if strpos(" `active_stages' ", " 03 ") == 0 local RUN_STAGE_03_MAIN_ESTIMATION      0
if strpos(" `active_stages' ", " 04 ") == 0 local RUN_STAGE_04_ROBUSTNESS           0
if strpos(" `active_stages' ", " 05 ") == 0 local RUN_STAGE_05_FIGURES_TABLES       0

di as txt "Stage flags:"
di as txt "  RUN_STAGE_01_DATA_PREPARATION     = `RUN_STAGE_01_DATA_PREPARATION'"
di as txt "  RUN_STAGE_02_DESCRIPTIVE_ANALYSIS = `RUN_STAGE_02_DESCRIPTIVE_ANALYSIS'"
di as txt "  RUN_STAGE_03_MAIN_ESTIMATION      = `RUN_STAGE_03_MAIN_ESTIMATION'"
di as txt "  RUN_STAGE_04_ROBUSTNESS           = `RUN_STAGE_04_ROBUSTNESS'"
di as txt "  RUN_STAGE_05_FIGURES_TABLES       = `RUN_STAGE_05_FIGURES_TABLES'"

di as txt "Script flags:"
di as txt "  RUN_01A_DATA_INGEST       = `RUN_01A_DATA_INGEST'"
di as txt "  RUN_02A_DESCRIPTIVE_STATS = `RUN_02A_DESCRIPTIVE_STATS'"
di as txt "  RUN_03A_MAIN_MODEL        = `RUN_03A_MAIN_MODEL'"
di as txt "  RUN_04A_ROBUSTNESS_CHECKS = `RUN_04A_ROBUSTNESS_CHECKS'"
di as txt "  RUN_05A_MAIN_OUTPUTS      = `RUN_05A_MAIN_OUTPUTS'"

local n_success 0
local n_failed 0
local n_skipped 0

* --- 01a --------------------------------------------------------------------
local script_id "01a"
local stage_num "01"
local script_path "WORKSPACE/code/01_data_preparation/01a_data_ingest.do"
local script_label "Data ingest"
local run_stage_flag `RUN_STAGE_01_DATA_PREPARATION'
local run_script_flag `RUN_01A_DATA_INGEST'

if `run_stage_flag' == 0 {
    di as txt "[SKIP STAGE] `script_id' (stage `stage_num' disabled)"
    local ++n_skipped
}
else if `run_script_flag' == 0 {
    di as txt "[SKIP FLAG] `script_id' (script flag disabled)"
    local ++n_skipped
}
else if !fileexists("`script_path'") {
    di as err "FAILED: Script not found: `script_path'"
    local ++n_failed
    if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
        exit 459
    }
}
else {
    di as res "Running `script_id' | `script_label' | `script_path'"
    capture noisily do "`script_path'"
    if _rc == 0 {
        local ++n_success
        di as res "Completed `script_id'"
    }
    else {
        di as err "FAILED: `script_id' returned code " _rc
        local ++n_failed
        if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
            exit _rc
        }
    }
}

* --- 02a --------------------------------------------------------------------
local script_id "02a"
local stage_num "02"
local script_path "WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.do"
local script_label "Descriptive stats"
local run_stage_flag `RUN_STAGE_02_DESCRIPTIVE_ANALYSIS'
local run_script_flag `RUN_02A_DESCRIPTIVE_STATS'

if `run_stage_flag' == 0 {
    di as txt "[SKIP STAGE] `script_id' (stage `stage_num' disabled)"
    local ++n_skipped
}
else if `run_script_flag' == 0 {
    di as txt "[SKIP FLAG] `script_id' (script flag disabled)"
    local ++n_skipped
}
else if !fileexists("`script_path'") {
    di as err "FAILED: Script not found: `script_path'"
    local ++n_failed
    if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
        exit 459
    }
}
else {
    di as res "Running `script_id' | `script_label' | `script_path'"
    capture noisily do "`script_path'"
    if _rc == 0 {
        local ++n_success
        di as res "Completed `script_id'"
    }
    else {
        di as err "FAILED: `script_id' returned code " _rc
        local ++n_failed
        if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
            exit _rc
        }
    }
}

* --- 03a --------------------------------------------------------------------
local script_id "03a"
local stage_num "03"
local script_path "WORKSPACE/code/03_main_estimation/03a_main_model.do"
local script_label "Main model"
local run_stage_flag `RUN_STAGE_03_MAIN_ESTIMATION'
local run_script_flag `RUN_03A_MAIN_MODEL'

if `run_stage_flag' == 0 {
    di as txt "[SKIP STAGE] `script_id' (stage `stage_num' disabled)"
    local ++n_skipped
}
else if `run_script_flag' == 0 {
    di as txt "[SKIP FLAG] `script_id' (script flag disabled)"
    local ++n_skipped
}
else if !fileexists("`script_path'") {
    di as err "FAILED: Script not found: `script_path'"
    local ++n_failed
    if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
        exit 459
    }
}
else {
    di as res "Running `script_id' | `script_label' | `script_path'"
    capture noisily do "`script_path'"
    if _rc == 0 {
        local ++n_success
        di as res "Completed `script_id'"
    }
    else {
        di as err "FAILED: `script_id' returned code " _rc
        local ++n_failed
        if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
            exit _rc
        }
    }
}

* --- 04a --------------------------------------------------------------------
local script_id "04a"
local stage_num "04"
local script_path "WORKSPACE/code/04_robustness_heterogeneity/04a_robustness_checks.do"
local script_label "Robustness checks"
local run_stage_flag `RUN_STAGE_04_ROBUSTNESS'
local run_script_flag `RUN_04A_ROBUSTNESS_CHECKS'

if `run_stage_flag' == 0 {
    di as txt "[SKIP STAGE] `script_id' (stage `stage_num' disabled)"
    local ++n_skipped
}
else if `run_script_flag' == 0 {
    di as txt "[SKIP FLAG] `script_id' (script flag disabled)"
    local ++n_skipped
}
else if !fileexists("`script_path'") {
    di as err "FAILED: Script not found: `script_path'"
    local ++n_failed
    if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
        exit 459
    }
}
else {
    di as res "Running `script_id' | `script_label' | `script_path'"
    capture noisily do "`script_path'"
    if _rc == 0 {
        local ++n_success
        di as res "Completed `script_id'"
    }
    else {
        di as err "FAILED: `script_id' returned code " _rc
        local ++n_failed
        if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
            exit _rc
        }
    }
}

* --- 05a --------------------------------------------------------------------
local script_id "05a"
local stage_num "05"
local script_path "WORKSPACE/code/05_figures_tables/05a_main_outputs.do"
local script_label "Main outputs"
local run_stage_flag `RUN_STAGE_05_FIGURES_TABLES'
local run_script_flag `RUN_05A_MAIN_OUTPUTS'

if `run_stage_flag' == 0 {
    di as txt "[SKIP STAGE] `script_id' (stage `stage_num' disabled)"
    local ++n_skipped
}
else if `run_script_flag' == 0 {
    di as txt "[SKIP FLAG] `script_id' (script flag disabled)"
    local ++n_skipped
}
else if !fileexists("`script_path'") {
    di as err "FAILED: Script not found: `script_path'"
    local ++n_failed
    if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
        exit 459
    }
}
else {
    di as res "Running `script_id' | `script_label' | `script_path'"
    capture noisily do "`script_path'"
    if _rc == 0 {
        local ++n_success
        di as res "Completed `script_id'"
    }
    else {
        di as err "FAILED: `script_id' returned code " _rc
        local ++n_failed
        if `STOP_ON_ERROR_ANY_STAGE' == 1 | `: list stage_num in FAIL_HARD_STAGES' {
            exit _rc
        }
    }
}

di as res "Pipeline complete"
di as txt "  Success: `n_success'"
di as txt "  Failed:  `n_failed'"
di as txt "  Skipped: `n_skipped'"



