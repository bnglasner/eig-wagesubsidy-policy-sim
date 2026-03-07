# WORKSPACE/code

This directory contains all pipeline scripts for the project.

## Stage Numbering

Scripts follow a zero-padded numeric prefix that determines execution order:

| Stage | Directory | Purpose |
|-------|-----------|---------|
| `00` | `00_setup/` | Project configuration and path bootstrap (sourced by every stage) |
| `01` | `01_data_preparation/` | Raw data acquisition, cleaning, analysis-ready dataset construction |
| `02` | `02_descriptive_analysis/` | Summary statistics, distributions, QC artifacts |
| `03` | `03_main_estimation/` | Primary model or analysis (Tier 2+ only) |
| `04` | `04_robustness_heterogeneity/` | Robustness checks and subgroup analyses (Tier 3 only) |
| `05` | `05_figures_tables/` | Publication-ready figures and tables |

Active stages depend on the project scope tier set in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.

## Pipeline Entrypoint

`run_all.*` (language-specific: `.R`, `.py`, `.do`) orchestrates the full pipeline.

It includes an explicit, one-per-line flag section — e.g.:

```r
RUN_STAGE_01_DATA_PREPARATION     <- TRUE
RUN_STAGE_02_DESCRIPTIVE_ANALYSIS <- TRUE
...
```

Set any flag to `FALSE` to skip that stage. Do not use compact vector-only declarations
as the primary run-all control surface (see `INFRA/AGENTS.md` non-negotiables).

## Adding a New Script

1. Create the file in the appropriate stage directory (e.g., `03_main_estimation/03b_iv_spec.R`).
2. Add a corresponding `TRUE`/`FALSE` flag line to `run_all.*` in stage order.
3. Update the stage README to document the new script's role and outputs.
4. If the script produces required outputs, update `INFRA/docs/STAGE_OUTPUT_CONTRACTS.md`.

## Config Bootstrap

Every pipeline script must source the project config at the top:

- R: `source("WORKSPACE/code/00_setup/00_config.R")`
- Python: `import code.setup.config as cfg` (or equivalent relative import)
- Stata: `do "$path_WORKSPACE/code/00_setup/00_config.do"`

See `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` for the active language profile.
