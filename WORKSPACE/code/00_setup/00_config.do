* 00_config.do -- baseline project configuration

* Root detection --------------------------------------------------------------
* Priority: EIG_PROJECT_ROOT env var -> current working directory.
* Either set EIG_PROJECT_ROOT in your environment or cd to the repo root
* before running any pipeline do-file.
local env_root : env EIG_PROJECT_ROOT
if `"`env_root'"' != "" {
    global path_project `"`env_root'"'
}
else {
    global path_project "`c(pwd)'"
    di as txt "NOTE: EIG_PROJECT_ROOT not set. Using cwd: $path_project"
    di as txt "      cd to repo root or set EIG_PROJECT_ROOT before running."
}

* Path globals ---------------------------------------------------------------
global path_code                "$path_project/WORKSPACE/code"
global path_data                "$path_project/WORKSPACE/data"
global path_data_raw            "$path_data/raw"
global path_data_processed      "$path_data/processed"
global path_output              "$path_project/WORKSPACE/output"
global path_output_fig_main     "$path_output/figures/main"
global path_output_fig_appendix "$path_output/figures/appendix"
global path_output_tbl_main     "$path_output/tables/main"
global path_output_tbl_appendix "$path_output/tables/appendix"
global path_output_intermediate "$path_output/data/intermediate_results"

* Project settings -----------------------------------------------------------
global project_name        "[PROJECT_NAME]"
global audience            "[AUDIENCE]"
global project_scope_tier  3   /* 1=Descriptive/Blog  2=Analytical Brief  3=Full Research Paper */
global currency_base_year  2025
global seed                1234

* Directory creation ---------------------------------------------------------
* Base directories (all tiers) -- create parent dirs before children
foreach d in "$path_data_raw" "$path_data_processed" ///
             "$path_output/figures" "$path_output/tables" ///
             "$path_output_fig_main" "$path_output_tbl_main" {
    capture mkdir "`d'"
}

* Tier 2+: intermediate results
if $project_scope_tier >= 2 {
    capture mkdir "$path_output/data"
    capture mkdir "$path_output_intermediate"
}

* Tier 3: appendix directories
if $project_scope_tier >= 3 {
    capture mkdir "$path_output_fig_appendix"
    capture mkdir "$path_output_tbl_appendix"
}

set seed $seed
di as res "Loaded config. Project root: $path_project"



