# Data Report Agent

Generate or update the project's data processing HTML report at `INFRA/quality_reports/data_report.html`.

## Purpose

Produce a single, self-contained HTML report documenting: data sources and their sample characteristics, sample construction and restrictions, variable transformations, merges and joins, the processed analysis dataset, and all pipeline outputs. The report must accurately reflect the actual pipeline scripts and any run artifacts that exist; it must not fabricate or estimate values.

## Source Priority (read in this order)

1. `INFRA/docs/PROJECT_DECISIONS.md` — project name, tier, primary and secondary language, unit of analysis, time period, geography
2. `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md` — source IDs, names, access tiers, acquisition methods, file formats, output IDs, sensitivity tiers, publication approval status
3. `WORKSPACE/data/raw/README.md` — acquisition details, file sizes, retrieval dates, known caveats
4. `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` — primary language, secondary language
5. Stage 01 scripts (`WORKSPACE/code/01_data_preparation/`) — transformations, sample restrictions, merge steps, producing script names
6. Stage 02 scripts (`WORKSPACE/code/02_descriptive_analysis/`) — any additional restrictions or derived variables applied at this stage
7. `WORKSPACE/output/data/intermediate_results/descriptive_qc.*` — actual N counts, variable counts, and summary statistics (use only if the pipeline has been run and this file exists)
8. `WORKSPACE/output/data/intermediate_results/data_dictionary.*` — variable-level metadata (use only if it exists)

## Procedure

1. Read all source files listed above.
2. Copy `INFRA/templates/data_report.html` to `INFRA/quality_reports/data_report.html`.
3. Populate the report by replacing every placeholder marker with project-specific content:

   **Header block**
   - `<!-- PROJECT_NAME -->`: project name from `PROJECT_DECISIONS.md`
   - `<!-- GENERATED_DATE -->`: today's date (YYYY-MM-DD)
   - `<!-- TIER -->`: scope tier and label
   - `<!-- PRIMARY_LANG -->` and `<!-- SECONDARY_LANG -->`: from language profile
   - `<!-- HEADER_SCRIPT -->`: the stage 01 script that produces the analysis dataset

   **Section 1 — Data Sources**
   - One `.source-card` block per source in `DATA_SOURCES_OUTPUTS_CATALOG.md`
   - Fill all fields from catalog, `WORKSPACE/data/raw/README.md`, and `PROJECT_DECISIONS.md`
   - Set the badge class to `badge-public`, `badge-licensed`, `badge-restricted`, or `badge-sensitive` matching the source tier

   **Section 2 — Sample Restrictions**
   - One `<tr>` per filter or restriction step found in stage 01 and stage 02 scripts
   - Pull N counts from `descriptive_qc.*` if the pipeline has been run; otherwise use `[PIPELINE NOT YET RUN]`
   - Compute % retained as N after Ã· N before Ã— 100, or mark `[PIPELINE NOT YET RUN]`

   **Section 3 — Transformations**
   - One `<tr>` per variable created, recoded, cleaned, dropped, or renamed in stage 01 or 02 scripts
   - Include the source variable(s) in the description when a variable is derived

   **Section 4 — Merges & Joins**
   - One `<tr>` per merge or join operation found in stage 01 scripts
   - If no merges were performed, replace the placeholder row with a single row: `<td colspan="12">No merges performed.</td>`

   **Section 5 — Processed Analysis Dataset**
   - Fill from `descriptive_qc.*` and `data_dictionary.*` when the pipeline has run; otherwise from catalog and `PROJECT_DECISIONS.md`
   - File size: from the actual file if it exists (`WORKSPACE/data/processed/analysis_dataset.*`), otherwise `[PIPELINE NOT YET RUN]`

   **Section 6 — Pipeline Outputs**
   - One `<tr>` per artifact in the Outputs section of `DATA_SOURCES_OUTPUTS_CATALOG.md`

   **Open Items block**
   - List every field left as `[NOT YET DOCUMENTED]` or `[PIPELINE NOT YET RUN]`, with enough context for a human to resolve it
   - If there are no open items, remove the entire `<!-- OPEN_ITEMS_SECTION -->` block

4. Set `<!-- LAST_UPDATED -->` to the current date and time (YYYY-MM-DD HH:MM).
5. Write the completed file to `INFRA/quality_reports/data_report.html`.

## Handling Missing Information

- If a value appears nowhere in the source files, use `[NOT YET DOCUMENTED]` and add the gap to the Open Items block.
- If the pipeline has not been run, use `[PIPELINE NOT YET RUN]` for N counts, file sizes, and any other run-time values. Do not estimate.
- Do not remove sections because data is missing; use the appropriate placeholder text so the gaps are visible.

## Non-Negotiables

1. Do not alter the HTML structure, CSS, section order, or `<!-- SECTION -->` / `<!-- /SECTION -->` comment markers.
2. Do not include credentials, API keys, or absolute local file paths that expose restricted access details.
3. Do not fabricate or estimate numerical values (N counts, file sizes, match rates). Source every number from an actual file.
4. Sensitivity tier and publication approval for each output must match `DATA_SOURCES_OUTPUTS_CATALOG.md` exactly. If missing, use `[NOT CLASSIFIED]` or `[PENDING]` and add to Open Items.
5. The report must be re-runnable: running this agent again after the pipeline executes should update all `[PIPELINE NOT YET RUN]` placeholders with actual values.

## Required Output

Return to the user:
1. Confirmation that `INFRA/quality_reports/data_report.html` was written.
2. A bulleted list of every field left as `[NOT YET DOCUMENTED]` or `[PIPELINE NOT YET RUN]`.
3. Any open governance questions (missing sensitivity tiers, unconfirmed publication approval, unclassified sources).



