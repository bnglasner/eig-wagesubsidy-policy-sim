# Session Log — 2026-07-09 — run_all.py Python-stage execution fix

## Goal
Fix the CRITICAL bug (code-error CE-001, ai-skeptic AS-001): `code/run_all.py::execute_python_script()`
loaded each Python stage with the file stem as the module name and only called `exec_module()`, so the
stage's `if __name__ == "__main__": main()` guard never fired. Every Python stage was recorded as SUCCESS
while running none of the analysis; only the R stages (subprocess) actually executed.

## Changes (2 files)
1. `code/run_all.py` — after `exec_module(mod)`, invoke `mod.main()` explicitly when a `main` callable
   exists (guarded for stages that do their work at import time). Minimal, does not touch the R path.
2. `code/05_figures_tables/05a_main_outputs.py` — latent bug surfaced by fix #1: the demographic-breakdown
   loop read `pct_workers`, but `by_sex/by_race_ethnicity/by_education/by_age_bin` expose
   `pct_of_recipients` (the analogue of `pct_workers` used for family_type/wage_bracket). Changed to
   `pct_of_recipients`. Print-only verification stage; no data implications. This stage had never actually
   run before, so the bug was invisible.

## Verification
- Ran `code/run_all.py` end-to-end (tier 1; R ingest already satisfied from cache, so R flags toggled off
  for the controlled run then restored — committed diff is only the two fixes above). Interpreter:
  repo `.venv` (numpy/pandas/pyarrow present; `policyengine_us` only needed by disabled 01b).
- All data-producing Python stages now execute with real elapsed times (01i 10.5s, 01h 3.9s, 02d 9.3s,
  02f 40.0s, 02g 59.5s) instead of ~0.0s import-only "SUCCESS".
- Outputs FRESH: `data/processed/{hourly_workers,household_links,nonemployed_pool}.parquet` (+ evidence-central
  pool, diagnostics json, org_target_wage.json) and 27/27 enabled `population/*.parquet`.
  `household_links.parquet` and `nonemployed_pool.parquet` were absent before the fix — direct proof the
  stages never ran. The only STALE files are `incidence_{by_segment,decomposition}.parquet` from 02c, which
  is intentionally disabled (`RUN_02C_INCIDENCE=False`, superseded by 02d).
- Determinism: two full Python-stage runs produced 27/27 byte-for-byte identical outputs (sha256).
- Final run status: 11 SUCCESS / 0 FAILED / 5 SKIPPED.

## Appendix §10 (reproducibility)
No change needed. §10 claims the pipeline "runs end-to-end from code/run_all.py" and is "deterministic ...
byte-for-byte across reruns." The first half was FALSE before the fix and is now TRUE; the determinism half
is confirmed (27/27 identical). The fix restored the claim's validity rather than requiring it to be weakened.

## Environment note
Worktree lacks the gitignored input data; copied `data/intermediate/cps_org_panel` and `data/raw/cps_org`
(incl. IPUMS extract cache) from the main working tree so the Python stages had their R-produced inputs.
Copied data is gitignored and does not appear in the commit.
