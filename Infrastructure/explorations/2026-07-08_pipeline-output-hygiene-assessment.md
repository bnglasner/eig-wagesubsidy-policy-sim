# Pipeline Output Hygiene Assessment

**Date:** 2026-07-08
**Type:** Exploration / read-only assessment (no code or data changed)
**Question:** How effectively does the pipeline persist intermediary outputs, so that figures, tables, and numeric analyses can grab intermediate elements without re-running upstream stages? Where are the gaps, and what is the lightest-weight "easy grab" process?

---

## Summary

The pipeline is **well-structured for its aggregated analysis tables** — stage 02 writes clean,
narrow, discoverable parquets under `output/data/intermediate_results/population/`, and stages 05a/05b
and the Streamlit app read them without recomputing anything upstream. The **microdata checkpoints**
(`data/processed/`) and the **PolicyEngine schedule caches** (`individual_schedules/`,
`matched_schedules/`) are likewise persisted and reused via idempotent skip-if-exists logic.

The weaknesses are concentrated in four places:

1. **Diagnostics computed only to stdout.** 01h (Heckman/reservation-band calibration) and 01e
   (match quality) print rich, non-reconstructable diagnostics that no file captures. 01h is the
   worst case — every calibration target-vs-realized number, the IMR coefficient, the pool MPL
   percentiles, and the `corr(markup, month)` check vanish when the console scrolls.
2. **DataFrames written with columns dropped.** 02d computes per-cell induced entry, incumbent-wage
   change, and cliff/hours detail for all six matching scenarios but drops the per-cell and
   detail dicts before writing `matching_simulation.parquet`; only the central-rigid case survives
   (in `entry_margin_band.parquet`).
3. **Orphaned / stale outputs with no owner.** `incidence_decomposition.parquet` +
   `incidence_by_segment.parquet` are left over from the superseded, now-disabled 02c;
   `matched_population/` + `matched_schedules/` are stale relative to an **empty `data/external/`**
   (the matched pipeline cannot currently regenerate). Nothing marks any of these as stale.
4. **No index/manifest and a broken contract reference.** There is no single place listing the
   intermediate tables and their contents; the `STAGE_OUTPUT_CONTRACTS.md` that three stage READMEs
   cite does not exist; and `pct_in_group` is emitted all-null in 02a because its base file is absent
   (02e was added to fill it but is not wired into `run_all.py`).

Nothing here blocks the current figures — the values a consumer needs mostly do exist somewhere.
The issue is **discoverability and reuse friction**, which is exactly the user's concern.

---

## 1. Stage-by-stage table

Pipeline is Tier 1; `run_all.py` registers stages in this order. R ingest (00) → 01a/01b/01i/01h →
02a/02b/02c/02d → 03a → 04a → 05a. `02e` and `05b` **exist but are not registered** in `run_all.py`.

| Stage / script | Key inputs | Saved outputs | Notable computed-but-unsaved artifacts |
|---|---|---|---|
| **00_ingest** (R, 00a→01a→01b) | IPUMS CPS API | `data/raw/cps_org/year=*/`, `data/intermediate/cps_org_panel/year=*/` | — (R side not in scope) |
| **01a** data_ingest | `data/intermediate/cps_org_panel/` | `data/processed/hourly_workers.parquet`; `data/processed/org_target_wage.json` | Weighted median wage detail, eligible-worker/gross-cost/avg-subsidy headline, top-10 states, WKSTAT/hours fallback counts, 40-hr cap counts — **stdout only** (headline recomputed by 02a summary) |
| **01b** precompute_individual | `app/utils/household_sim` + PolicyEngine | `individual_schedules/{family}_{state}.parquet` (204 configs) | Per-combo timings — stdout only (disabled by default: `RUN_01B=False`) |
| **01i** household_links | raw `data/raw/cps_org/` partitions | `data/processed/household_links.parquet` | spouse-linkable %, spouse-employed %, own_child_under5 %, hh-fallback share — **stdout only** |
| **01h** nonemployed_pool | raw ORG partitions; `household_links.parquet`; `hourly_workers.parquet`; `org_target_wage.json`; imports 02b | `data/processed/nonemployed_pool.parquet` | **Largest gap.** Heckman IMR coef (ρσ), smearing, pool MPL p25/50/75 (conditional/Mills=0/plain-OLS), g_net floor/cap counts, per-cell reachable N + median g_net, **per-cell/per-edge calibration target vs realized**, weighted MPL percentiles, MPL<target %, `corr(markup, survey month)` — **all stdout only** |
| **01d** asec_preprocess | `data/external/asec_persons_*.parquet` | `data/external/asec_earners_{yyyy}.parquet` | Match-prep summary — stdout only. **Cannot run: `data/external/` empty** |
| **01e** match_org_to_asec | `org_workers_*.parquet`, `asec_earners_*.parquet` | `data/external/org_asec_matches.parquet` | Match quality (median/p95 distance, spouse-income %, unique ASEC HHs utilised, fallback states) — **stdout only**. Cannot run (inputs absent) |
| **01f** precompute_matched_schedules | `org_asec_matches.parquet` | `matched_schedules/{config}_{state}.parquet` (3,760 files) | Compute-estimate gate, per-config timings — stdout only. Files present but stale |
| **02a** descriptive_stats | `hourly_workers.parquet`; `individual_schedules/`; (`org_workers_*` for base pop) | `population/`: `summary`, `by_state`, `by_wage_bracket`, `by_family_type`, `program_interactions`, `by_sex`, `by_race_ethnicity`, `by_education`, `by_age_bin` (9) | `pct_in_group` **emitted null** (base file `org_workers_*.parquet` absent → the try/except silently degrades) |
| **02b** behavioral_scenarios | `hourly_workers.parquet`; `individual_schedules/` | `population/behavioral_scenarios.parquet` (4 rows, wide) | Good coverage — induced-by-cell and above-grid % are saved as columns |
| **02c** incidence (DISABLED, superseded by 02d) | `hourly_workers.parquet`; imports 02b | `population/incidence_decomposition.parquet`, `population/incidence_by_segment.parquet` | **Orphaned:** files persist on disk but `RUN_02C=False`; nothing regenerates or reads them |
| **02d** matching_simulation | `hourly_workers.parquet`; `nonemployed_pool.parquet`; imports 02b; reads `behavioral_scenarios.parquet` | `population/matching_simulation.parquet` (6 rows), `entry_margin_band.parquet` (5 rows), `entry_reconciliation.parquet` (1 row) | **`induced_by_cell` and `entrant_detail` (cliff_payup, mean_entry_hours) dropped** from the 6-row main table (line 302). Only central-rigid survives via `entry_margin_band`. Docstring promises a `matching_by_cell.parquet` that is never written |
| **03a** apply_matched_to_population (Tier 2+, not run at Tier 1) | `org_asec_matches.parquet`; `matched_schedules/`; `population/` (for comparison) | `matched_population/`: same 9 + `comparison`, `program_comparison` (11) | Cannot regenerate (inputs absent); outputs present but stale |
| **04a** robustness (disabled at Tier 1) | — | — | — |
| **05a** main_outputs | `population/{summary,by_state,by_wage_bracket,by_family_type,program_interactions}` | **none** (verify + print only) | Headline metrics, top-5 states, wage-bracket, family-type, program-interaction, and demographic breakdowns are **printed, not consolidated** into a table (all source values do exist in the population parquets) |
| **05b** state_choropleth (not registered in run_all) | `population/by_state.parquet` | `output/figures/main/fig1_avg_subsidy_by_state.{png,svg}` | — (clean single-purpose figure script) |
| **02e** take_up_by_group (not registered in run_all) | `cps_org_panel` via 01a adapter; `org_target_wage.json` | `population/take_up_by_group.parquet` (20 rows) | Purpose-built to fill 02a's null `pct_in_group`; clean |

---

## 2. Saved-output inventory

Format is parquet unless noted. "Documented?" = whether a consumer can learn the file exists and its
schema without reading the producing script (a docstring in the producing script counts as partial).

| Path | Format | Produced by | Consumed by | Documented? |
|---|---|---|---|---|
| `data/processed/hourly_workers.parquet` | parquet | 01a | 02a, 02b, 02d, 01h, 02e (indirect) | Partial (01a docstring) |
| `data/processed/org_target_wage.json` | json | 01a | 01h, 02e | Partial (01a docstring) |
| `data/processed/household_links.parquet` | parquet | 01i | 01h | Partial (01i docstring) |
| `data/processed/nonemployed_pool.parquet` | parquet | 01h | 02d | Partial (01h docstring) |
| `data/intermediate/cps_org_panel/year=*/part-0.parquet` | parquet (partitioned) | 00_ingest (R) | 01a, 02e | Partial |
| `data/raw/cps_org/year=*/part-0.parquet` | parquet (partitioned) | 00_ingest (R) | 01h, 01i | `_manifest.csv` present |
| `data/external/*` (asec_*, org_workers_*, org_asec_matches) | parquet | 01c/01d/01e | 01e, 01f, 03a, 02a base-pop | **No — directory empty** |
| `output/.../individual_schedules/{family}_{state}.parquet` | parquet (204) | 01b | 02a, 02b, 02d, app | Partial (01b docstring) |
| `output/.../matched_schedules/{config}_{state}.parquet` | parquet (3,760) | 01f | 03a, app | Partial; stale |
| `output/.../population/summary.parquet` | parquet | 02a | 05a, app | Partial (02a docstring) |
| `output/.../population/by_state.parquet` | parquet | 02a | 05a, 05b, app | Partial |
| `output/.../population/by_{wage_bracket,family_type,sex,race_ethnicity,education,age_bin}.parquet` | parquet | 02a | 05a, app | Partial |
| `output/.../population/program_interactions.parquet` | parquet | 02a | 05a, app | Partial |
| `output/.../population/behavioral_scenarios.parquet` | parquet | 02b | 02d (reconciliation); figures TBD | Partial |
| `output/.../population/matching_simulation.parquet` | parquet | 02d | figures TBD | Partial |
| `output/.../population/entry_margin_band.parquet` | parquet | 02d | figures TBD | Partial |
| `output/.../population/entry_reconciliation.parquet` | parquet | 02d | figures TBD | Partial |
| `output/.../population/take_up_by_group.parquet` | parquet | 02e | figures TBD | Partial |
| `output/.../population/incidence_{decomposition,by_segment}.parquet` | parquet | 02c (disabled) | **none** | **No — orphaned** |
| `output/.../matched_population/*.parquet` (11) | parquet | 03a | app (matched mode) | Partial; stale |
| `output/figures/main/fig1_avg_subsidy_by_state.{png,svg}` | png/svg | 05b | publication | Yes (05b header) |

`output/data/intermediate_results/README.md` and `data/processed/README.md` exist but are **generic
template stubs** — they describe the folders' purpose, not the actual files or schemas. All parquet
outputs are gitignored (only READMEs/.gitkeep tracked), except the app-facing schedules note in
`.gitignore` (lines 78-79) — worth confirming which schedules are meant to ship for Streamlit Cloud.

---

## 3. Findings (prioritized)

### HIGH

- **H1. 01h calibration diagnostics have no home.** The entire Heckman + reservation-band calibration
  audit trail (IMR coef ρσ, smearing, pool MPL p25/50/75 across three imputation variants, g_net
  floor/cap counts, per-cell reachable N and median g_net, **per-cell/per-edge target vs realized**,
  MPL<target %, `corr(markup, survey month)`) is printed to stdout and lost. This is the most
  methodologically load-bearing stage and the one whose numbers a brief/appendix or a reviewer would
  most want to cite or re-check. **Fix:** write a `data/processed/nonemployed_pool_diagnostics.json`
  (scalars + the per-cell/edge calibration table) at the end of `01h.main()`.

- **H2. 02d drops per-scenario cell + detail columns.** `matching_simulation.parquet` keeps 6 rows but
  strips `induced_by_cell` and `entrant_detail` (line 302). A figure showing "who is induced to enter,
  by scenario" or "cliff pay-up entrants by beta" cannot be built from saved files — only the single
  central-rigid case exists (in `entry_margin_band.parquet`). **Fix:** flatten the dicts into columns
  (`induced_single_mothers_M`, `induced_other_women_M`, `induced_men_M`, `cliff_payup_entrants_M`,
  `mean_entry_hours`) and keep them in `matching_simulation.parquet`, matching `entry_margin_band`'s
  schema so the two are stackable.

- **H3. `pct_in_group` emitted null; 02e not wired in.** 02a's `pct_in_group` (take-up rate per
  group/state) is silently null because the base-population file `data/external/org_workers_*.parquet`
  is absent. 02e was written to fill this from the in-repo panel but is **not registered in
  `run_all.py`**, so a clean run never produces `take_up_by_group.parquet`. **Fix:** register 02e in
  `run_all.py` (and 05b, which actually renders Figure 1 — currently only 05a runs, and it only
  verifies). Optionally have 02a source its denominator from the same in-repo adapter 02e uses so
  `pct_in_group` is populated at the source rather than in a parallel file.

### MEDIUM

- **M2. Orphaned 02c incidence outputs.** `incidence_decomposition.parquet` and
  `incidence_by_segment.parquet` sit in `population/` but 02c is `RUN_02C=False` and superseded by 02d.
  A consumer grepping the folder cannot tell they are dead. **Fix:** delete them (regenerable if ever
  re-enabled) or move to an `output/.../population/_deprecated/` subfolder; note the supersession.

- **M3. Stale matched pipeline vs empty `data/external/`.** `matched_population/` (11) and
  `matched_schedules/` (3,760) exist, but `data/external/` is empty, so 01d/01e/01f/03a cannot
  regenerate them and the app's matched mode is showing outputs that no current input reproduces.
  **Fix:** document in a manifest whether these are intentionally shipped snapshots or should be
  rebuilt; flag them as snapshot-only if inputs are not committed.

- **M4. Missing `STAGE_OUTPUT_CONTRACTS.md` + mismatched stage READMEs.** `05_figures_tables/README.md`
  cites `Infrastructure/docs/STAGE_OUTPUT_CONTRACTS.md` as the source of truth; it does not exist.
  `02_descriptive_analysis/README.md` declares required outputs `descriptive_summary.*` /
  `descriptive_qc.*` and `03_main_estimation/README.md` declares `main_estimates.*` /
  `model_diagnostics.*` — none of these paths are what the stages actually write. The declared
  contract and the real outputs have drifted. **Fix:** either create the contracts doc from the real
  output inventory (see recommendation below) or update the READMEs to match reality.

- **M5. No consolidated headline table from 05a.** 05a prints the entire headline + demographic story
  to stdout but writes nothing. A blog/brief wanting one flat "key numbers" table must re-read the six
  population parquets and re-join. **Fix:** have 05a additionally write a small
  `output/tables/main/headline_summary.csv` (or parquet) — the values are already in memory.

### LOW

- **L6. 01a/01e/01i one-line summaries are stdout only.** Lower stakes than 01h; 01a's headline is
  reproduced by 02a's `summary.parquet`. Fold into the manifest/diagnostics JSON if convenient.
- **L7. 02d docstring names a `matching_by_cell.parquet` that is never written** — stale doc; remove
  or implement (H2 effectively implements the intent).
- **L8. Schedule caches live under `intermediate_results/` but are model inputs, not analysis
  outputs.** `individual_schedules/` and `matched_schedules/` are PolicyEngine lookup tables consumed
  by 02*/03a, mixed in the same tree as analysis-consumable aggregates. Not wrong, but a consumer
  scanning `intermediate_results/` for "tables I can plot" wades through 4,000 schedule files. A
  manifest that separates `role: schedule-cache` from `role: analysis-table` resolves this cheaply.

---

## 4. Recommended "easy grab" process (proportional to a Tier-1 project)

Adopt one convention and one tiny helper — no framework.

**Convention.** Every analysis-consumable intermediate lands in
`output/data/intermediate_results/population/` (already true) as parquet, and each producing stage
appends one row per file it writes to a single **`_manifest.csv`** in that folder, with columns:
`file, produced_by, rows, columns, description, role` (`role` ∈ `analysis-table` | `schedule-cache` |
`diagnostic` | `deprecated`). Writing the manifest is ~5 lines at the end of each `main()` (append or
rewrite-own-rows). This is the single place a figure/table author, a reviewer, or a future session
reads to answer "what intermediate tables exist and what's in each" — the thing that is missing today.

**Helper.** Add `code/_utils/intermediates.py` with two functions: `list_intermediates()` (prints the
manifest) and `load(name)` (returns the parquet by stem, raising a clear error naming the producing
stage if absent). Figures then do `from _utils.intermediates import load; df = load("by_state")`
instead of hard-coding paths.

**Promote these currently-printed diagnostics to files** (highest value first): 01h →
`data/processed/nonemployed_pool_diagnostics.json` (H1); 02d per-scenario cell/detail columns into
`matching_simulation.parquet` (H2); 05a headline → `output/tables/main/headline_summary.csv` (M5). Then
wire **02e** and **05b** into `run_all.py` (H3) so a clean run produces the take-up table and Figure 1,
and either delete the orphaned 02c incidence files or mark them `role: deprecated` in the manifest (M2).
Finally, reconcile the stage READMEs / `STAGE_OUTPUT_CONTRACTS.md` reference against the manifest so the
declared contract and the real outputs stop drifting (M4).

This keeps the current, working structure; it adds one CSV per run and one 30-line helper, and it turns
every "printed but not saved" number that matters into a grab-able file.

---

## Evidence

**Sources (files inspected).** `code/run_all.py`; `code/00_setup/00_config.py`;
`code/01_data_preparation/{01a_data_ingest,01b_precompute_individual,01d_asec_preprocess,01e_match_org_to_asec,01f_precompute_matched_schedules,01h_nonemployed_pool,01i_household_links}.py`;
`code/02_descriptive_analysis/{02a_descriptive_stats,02b_behavioral_scenarios,02c_incidence,02d_matching_simulation,02e_take_up_by_group}.py`;
`code/03_matched_analysis/03a_apply_matched_to_population.py`;
`code/05_figures_tables/{05a_main_outputs,05b_state_choropleth}.py` and `05_figures_tables/README.md`;
`app/tabs/population.py`; `.gitignore`; the READMEs under `data/processed/` and
`output/data/intermediate_results/`; and a live inventory of `data/` + `output/` plus parquet
schema/value inspection via `.venv/bin/python` (pandas).

**Confidence.** High for the saved-output inventory, the stdout-only diagnostics in 01h/01i/01e/05a,
the 02d column drop, the null `pct_in_group`, the unregistered 02e/05b, the orphaned 02c files, the
empty `data/external/`, and the missing `STAGE_OUTPUT_CONTRACTS.md` — all directly observed in code and
on disk. Medium for downstream consumers of the 02b/02d/02e tables (figures/briefs not yet built; the
app's population tab reads only the 02a/03a core set), so "consumed by: figures TBD" reflects intended,
not yet realized, use.

**Assumptions.** (1) Tier stays 1, so 03a/04a are out of the normal run and the matched pipeline's
staleness is not currently load-bearing. (2) `data/external/` being empty is a checkout state, not a
deletion — the matched outputs on disk were built in an earlier session with those inputs present.
(3) The R ingest stage (00) is out of scope per the task; its outputs were treated as given inputs.
(4) No code or data was modified; all recommendations are for a follow-up implementation session.
