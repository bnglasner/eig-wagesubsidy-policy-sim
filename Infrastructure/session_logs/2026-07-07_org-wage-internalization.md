# Session Log — ORG wage-build internalization (planning)

**Date:** 2026-07-07 · **Full-log cadence:** milestone-based (assumed; confirm)

## Goal
Internalize the CPS ORG wage-construction pipeline into the wage-subsidy repo by vendoring the EIG-Wage-Figure R stages (recent-12-month, `*2`-only, nominal) and adapting the Python stages to consume EIG-native wage elements. Plan-first; IPUMS submit is human-gated.

## Key findings (recon)
- Canonical repo = `EIG-Wage-Figure-Explain-Everything` @ SHA `33bbcb7`. Stages `00a` (extract, all 1982+), `01a` (load→`data/raw/cps_org/year=YYYY/part-0.parquet`), `01b` (SWA gate + seeded `ranger` RF hours + sex-separate Pareto + 2023m4–2024m12 bridge → `data/intermediate/cps_org_panel/`).
- Canonical emits `nominal_weekly_wage_num`/`uhrsworkorg_used_num`/`hours_imputed_flag`/`pareto_topcode_imputed_flag`, NOT the EPI-named cols (`hourly_wage_epi`,`hours_epi`,`epi_sample_eligible`,`paid_hourly`,`weekly_earn_epi`). Those belong to the defunct `real-wages-generations-ipums` (not on disk).
- Nominal hourly-wage routing lives at top of out-of-scope `02a_build_real_wages.R`; deterministic transform of EIG columns → reproducible in Python.
- `01h` already reads the EIG raw partitions (2023–2026 present) with native names; employed path (`00_export`/`01a`) is the stale one. `data/external/` has no `org_workers` file.

## Decisions (user, 2026-07-07)
1. Adopt EIG-native elements; adapter is **Python-side** (not reconstructing old EPI schema).
2. Use EIG process/values for the hourly wage; deflation out; `$0.50` nominal floor assumed unless vetoed.
3. Vendored-file edits = config **+ annotated `# EIG-VENDOR-GUARD:` inert-guards**, each enumerated.
4. Parity relaxed to **faithful method replication** on the new window (key-aligned closeness), not byte-identity.

## Surfaced gap (needs veto at IPUMS gate)
- `WKSTAT` is required for the annual-hours method but is not in the EIG base list nor the user's stated additions (`NCHILD`,`RELATE`). Added as spec MUST M4.

## Artifacts
- Spec: `Infrastructure/specs/2026-07-07_org-wage-internalization.md` (DRAFT).
- Plan: `Infrastructure/plans/2026-07-07_org-wage-internalization.md` (DRAFT).

## Progress
- Spec + plan APPROVED by user (2026-07-07).
- `data-dictionary-agent` launched (background) to document ORG vars + vintage into the registry.
- Vendored R stages into `code/00_ingest/` (`00a`,`01a`,`01b`) + minimal loader `code/_utils/00_packages.R` + `.here` anchor. Pristine upstream kept at `code/00_ingest/.upstream_33bbcb7/`.
- Diff vs `33bbcb7`: `01b` byte-identical; `00a` config-only (recent-12, *2-only, +NCHILD/RELATE/WKSTAT); `01a` inert-guards only (legacy-col safety). Clean.

## Progress (continued)
- IPUMS gate APPROVED (WKSTAT + geo vars kept; straight-through). Ran `00_ingest` end-to-end: extract `cps_00579`, 2025m5–2026m5, 1,116,101 rows; Q-flags all present (*2-only held); panel 116,515 employed earners; RF fit both years; Pareto/bridge inert as predicted.
- Wtd median paid-hourly = **$21.00 → target $16.80** (matches config exactly).
- W4 Python rewire done: `01a` adapter (`_load_and_adapt_org_panel`), `01h` raw-dir default → in-repo, `00_export` retired to stub, `run_all.py` R stage (`RUN_00_INGEST_ORG`).
- Pipeline verified via scratchpad venv: 01a/01h/02a/02b/02d run; **static parity test `test_behavioral_static_parity.py` PASSED** (M12).
- W5 method-fidelity gate **PASS**: 99.98% bit-identical vs full-history companion; only RF-imputed hours on truncated 2025 differ (2.4%, mean |Δ|1.3hr) — expected windowing effect; 2026 (identical months) bit-identical incl. imputed. Report: `2026-07-07_replication_report.md`.
- New baseline recorded: static gross $89.70B / net $72.09B / 20.81M workers (was 25–30M / $40–60B stale band — window shift, documented not forced).
- W8 docs: PROJECT.md Data-in-Scope updated; `docs/org_ingestion_internalized.md` written (SHA `33bbcb7`, crosswalk, handoff, R deps, drift control).

## W6 reviews (complete) + dispositions
- **maintenance/drift**: PASS exit 0; created `Infrastructure/scripts/check_org_vendor_drift.sh` (01b byte-identical; 00a/01a only EIG-VENDOR-tagged). 1 INFO (staleness needs canonical clone).
- **methodology**: 0 HIGH / 6 MED / 5 LOW (overall MED). Both focus conclusions verified (inert window; EARNWT/WTFINL correct).
- **code**: 0 CRIT/HIGH / 1 MED / 2 LOW / 1 INFO / 2 SUGG. Vendor guards correct+inert; handoff intact.
- **Fixes applied (user-approved 2026-07-08):** MR-003 (01a persists dynamic TARGET_WAGE to `data/processed/org_target_wage.json`; 01h reads it, cfg fallback) and CE-001 (subsidy_hours uses fallback-repaired hours → +$0.05B). Kept $0.50 nominal floor (MR-006, documented). Re-verified: parity test PASSES; static gross $89.75B / net $72.12B.
- **Deferred (documented):** MR-004 (per-year RF on partial year — in replication report), MR-001/002/005 (pre-existing 01h Heckman/variance/annualization assumptions), CE-002/003/004, CE-005/006/MR-007-011 (LOW/SUGG).

## Open / next
- Reports in `review-reports/` (methodology-report.html, code-error-report.html) + drift script. All green (0 HIGH/CRITICAL).
- **Not committed to git yet** (awaiting user go-ahead; then branch/commit off `feature/template-v2-port`).
- Session-only: scratchpad venv + companion (not in repo). Data-dictionary `parsed` entries need a later authoritative ORG-DDI fetch to promote beyond `parsed`.
