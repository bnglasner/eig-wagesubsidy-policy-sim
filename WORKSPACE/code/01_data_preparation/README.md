# 01_data_preparation

Purpose: raw data acquisition, cleaning, harmonization, and construction of analysis-ready datasets.

Contract summary:
- Source of truth: `INFRA/docs/STAGE_OUTPUT_CONTRACTS.md`
- Required outputs: `WORKSPACE/data/processed/analysis_dataset.*`, `WORKSPACE/output/data/intermediate_results/data_dictionary.*`, `INFRA/quality_reports/data_report.html`
- Minimum check: dataset loads and required identifiers are present

HTML report note: `INFRA/quality_reports/data_report.html` must be produced before this stage
passes strict contract checks. Use `INFRA/templates/data_report.html` as the starting template.
Copy it to `INFRA/quality_reports/data_report.html` and fill in dataset summary information
(row counts, source provenance, QC flags). The stage contract validator checks for its presence
and non-empty content.




