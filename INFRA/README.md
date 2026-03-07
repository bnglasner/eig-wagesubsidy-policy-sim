# About This Infrastructure Layer

This folder contains baseline infrastructure for EIG research projects: docs, scripts, templates, and AI agent configuration.

For the primary project entry point, see the root `README.md`.
For an internal relationship map, see `INFRA/docs/ARCHITECTURE.md`.

## Stage Structure

```text
WORKSPACE/code/
  00_setup/
  01_data_preparation/
  02_descriptive_analysis/
  03_main_estimation/
  04_robustness_heterogeneity/
  05_figures_tables/
WORKSPACE/data/
  raw/
  processed/
WORKSPACE/output/
  figures/{main,appendix}/
  tables/{main,appendix}/
  data/intermediate_results/
INFRA/quality_reports/
  plans/
  specs/
  session_logs/
  merges/
WORKSPACE/explorations/
  ARCHIVE/
```

## Setup Notes

1. Copy `INFRA/.Renviron.example` to `.Renviron` (repo root) and add keys as needed.
2. Keep large raw data out of git; document acquisition in `WORKSPACE/data/raw/README.md`.
3. Keep reproducible outputs in `WORKSPACE/output/`; decide what to track via `.gitignore`.

## Validation Commands

Run from repo root:

```bash
bash INFRA/scripts/validate_structure.sh
bash INFRA/scripts/validate_agent_parity.sh
bash INFRA/scripts/validate_stage_contracts.sh
```

Template default for stage contracts is warn mode. Switch to strict mode after project artifacts exist:

```bash
STAGE_CONTRACT_MODE=fail bash INFRA/scripts/validate_stage_contracts.sh
```
