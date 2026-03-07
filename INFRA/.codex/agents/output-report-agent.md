# Codex Output Report Agent

Generate or update the project's analytic output summary HTML report at `INFRA/quality_reports/output_report.html`.

## Purpose

Produce a self-contained HTML report that functions as a summary brief: it opens with the analysis title, research question, and primary findings, then presents each figure and table as a structured output card with title, subtitle, contextual note, what-it-shows/does-not-show descriptions, and a methodology bar. The report is designed to be readable by a policy or research audience, not just the analyst.

## Source Priority (read in this order)

1. `INFRA/docs/PROJECT_DECISIONS.md` — project name, analysis title, research question, analytic scope (time period, geography, unit of analysis, population), known scope limits
2. `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md` — output IDs, names, types (figure/table), file paths, producing scripts, sensitivity tiers, publication approval status, descriptions
3. `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` — primary language, tier
4. Stage 05 scripts (`WORKSPACE/code/05_figures_tables/`) — section headers, comments, variable labels, filter conditions applied within each output-producing block; code block location for each output
5. Stage 02–04 scripts — any filter conditions or sample definitions that feed directly into specific outputs
6. `WORKSPACE/output/data/intermediate_results/descriptive_qc.*` — actual N counts for analytic sample descriptions (use only if it exists)
7. Actual output files in `WORKSPACE/output/figures/` and `WORKSPACE/output/tables/` — confirm existence; read table dimensions if accessible

## Procedure

1. Read all source files listed above.
2. Copy `INFRA/templates/output_report.html` to `INFRA/quality_reports/output_report.html`.
3. Populate the report by replacing every placeholder marker with project-specific content:

   **Header block**
   - `<!-- PROJECT_NAME -->`: project name from `PROJECT_DECISIONS.md`
   - `<!-- ANALYSIS_TITLE -->`: full descriptive analysis title from `PROJECT_DECISIONS.md`
   - `<!-- GENERATED_DATE -->`: today's date (YYYY-MM-DD)
   - `<!-- TIER -->`: scope tier and label from language profile
   - `<!-- N_OUTPUTS -->`: count of figures and tables from catalog (e.g., "3 figures, 2 tables")

   **Research Brief**
   - `<!-- RESEARCH_QUESTION -->`: primary research question verbatim from `PROJECT_DECISIONS.md`
   - `<!-- ANALYTIC_SCOPE -->`: time period, geography, unit of analysis, and population from `PROJECT_DECISIONS.md`
   - `<!-- PRIMARY_FINDINGS -->`: scaffold 3–5 bullet points from output descriptions in the catalog and any narrative notes in `PROJECT_DECISIONS.md`. Mark every bullet with "(requires human review)" — do not assert findings as confirmed; flag the entire block with the existing warning note in the template
   - `<!-- SCOPE_LIMITS -->`: populate from any explicit scope limitations, caveats, or "what we do not address" notes in `PROJECT_DECISIONS.md`; if absent, leave `[NOT YET DOCUMENTED]` and add to Open Items

   **Output Cards — one card per artifact in the catalog**
   - Use the figure card template for figures; use the table card template for tables
   - Remove the placeholder card templates from the final report; replace them with populated cards only
   - For each output:
     - `<!-- OUT_ID -->`: output ID from catalog
     - `<!-- CARD_TITLE -->`: output name from catalog or a publication-ready title derived from script section headers
     - `<!-- CARD_SUBTITLE -->`: subtitle providing geographic scope, time period, or unit of analysis for this specific output
     - Badge: set `badge-main` or `badge-appendix` based on the file path (`WORKSPACE/output/figures/main/` → main, `WORKSPACE/output/figures/appendix/` → appendix)
     - `<!-- FIGURE_SRC -->`: relative path from `INFRA/quality_reports/` to the figure file (e.g., `../WORKSPACE/output/figures/main/fig01.png`). Verify the file exists before setting; if it does not exist, leave `src=""` so the image is hidden and the `.figure-missing` placeholder text is shown
     - `<!-- FIGURE_ALT -->`: descriptive alt text for accessibility
     - `<!-- FIGURE_NOTE -->`: contextual note for the reader — what to look for, how to read the axes, any callout annotations. Derive from script comments or catalog notes
     - `<!-- TABLE_HREF -->` and `<!-- TABLE_FILENAME -->`: relative path and filename for table outputs
     - `<!-- TABLE_DIMS -->`: row Ã— column count if the file exists and is readable; otherwise `[PIPELINE NOT YET RUN]`
     - `<!-- WHAT_SHOWN -->`: sentence to paragraph describing what the output illustrates — derive from catalog description, script section name, and any inline comments. Flag as requiring human review
     - `<!-- WHAT_NOT_SHOWN -->`: explicit statement of what is excluded, not estimated, or not identifiable from this specific output — derive from catalog notes, known data limitations, or scope decisions in `PROJECT_DECISIONS.md`. Flag as requiring human review
     - Methodology bar fields:
       - `<!-- METHOD_SAMPLE -->`: analytic sample for this specific output — if it differs from the main analytic sample (e.g., restricted to a subset year or subgroup), state the difference; otherwise summarize the main sample from `descriptive_qc.*` or `PROJECT_DECISIONS.md`
       - `<!-- METHOD_SOURCE -->`: source ID(s) and name(s) from catalog
       - `<!-- METHOD_SCRIPT -->`: script path from catalog; append section name, function name, or line range if identifiable from script structure
       - `<!-- METHOD_FILTERS -->`: any filter conditions applied within the producing script beyond the main sample restrictions; if none, write "None beyond main sample"

   **Open Items block**
   - List every `[NOT YET DOCUMENTED]` or `[PIPELINE NOT YET RUN]` field with enough context for a human to resolve it
   - Always include a bullet noting that Primary Findings require human editorial review
   - If there are no open items beyond the findings review, remove all other bullets but retain the findings review bullet
   - Remove the entire block only if it is genuinely empty

4. Set `<!-- LAST_UPDATED -->` to the current date and time (YYYY-MM-DD HH:MM).
5. Write the completed file to `INFRA/quality_reports/output_report.html`.

## Handling Missing Information

- If a figure file does not exist, set `src=""` — do not guess or construct a path that may be wrong
- If a table file does not exist or is not readable, use `[PIPELINE NOT YET RUN]` for dimensions
- If a catalog description is missing, derive a minimal description from the script section header or leave `[NOT YET DOCUMENTED]` and add to Open Items
- If `PROJECT_DECISIONS.md` does not contain scope limits or a full analysis title, leave those fields as `[NOT YET DOCUMENTED]` and add to Open Items
- Do not assert, infer, or estimate any analytical finding from figure or table content

## Non-Negotiables

1. Do not assert analytical findings as confirmed — every finding bullet must be flagged as requiring human review. The agent's role is to scaffold structure and populate sourced metadata, not to interpret results.
2. Do not alter the HTML structure, CSS, section order, or `<!-- SECTION -->` / `<!-- /SECTION -->` comment markers.
3. Do not include credentials, API keys, or absolute local file paths that expose restricted access details.
4. Do not embed or render raw table file content in the HTML — use the `.table-ref` link block only.
5. Sensitivity tier and publication approval for each output must match `DATA_SOURCES_OUTPUTS_CATALOG.md` exactly. If missing, use `[NOT CLASSIFIED]` or `[PENDING]` and add to Open Items.
6. The report must be re-runnable: invoking this agent after the pipeline executes should update figure `src` paths and table dimensions without losing any human-edited content in the description fields.

## Required Output

Return to the user:
1. Confirmation that `INFRA/quality_reports/output_report.html` was written.
2. A list of outputs included (IDs and titles).
3. A bulleted list of every field left as `[NOT YET DOCUMENTED]` or `[PIPELINE NOT YET RUN]`.
4. A reminder that all Primary Findings bullets require human editorial review before publication.

