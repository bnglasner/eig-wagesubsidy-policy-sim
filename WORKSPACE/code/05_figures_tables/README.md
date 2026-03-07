# 05_figures_tables

Purpose: publication-ready figures/tables and export-ready supporting files.

Contract summary:
- Source of truth: `INFRA/docs/STAGE_OUTPUT_CONTRACTS.md`
- Required outputs: `WORKSPACE/output/figures/main/*`, `WORKSPACE/output/figures/appendix/*`, `WORKSPACE/output/tables/main/*`, `WORKSPACE/output/tables/appendix/*`, `INFRA/quality_reports/output_report.html`
- Minimum check: required final artifacts exist and are non-empty

HTML report note: `INFRA/quality_reports/output_report.html` must be produced before this stage
passes strict contract checks. Use `INFRA/templates/output_report.html` as the starting template.
Copy it to `INFRA/quality_reports/output_report.html` and fill in output inventory information
(figure list, table list, key findings, unresolved issues). The stage contract validator checks
for its presence and non-empty content.



