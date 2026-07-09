# Orchestration Plan: Internalize the CPS ORG wage build

**Date:** 2026-07-07 · **Status:** DRAFT (awaiting approval) · **Spec:** `Infrastructure/specs/2026-07-07_org-wage-internalization.md`

## Objective

Vendor the EIG-Wage-Figure R wage-construction stages into `code/00_ingest/` (config + annotated inert-guards), scope to the most recent 12 complete months, rewire this repo's Python stages to consume the EIG-native wage elements, retire the cross-repo dependency, and pass a method-fidelity gate before any downstream extension.

## Workstreams

| # | Workstream | Route (Agent/Command) | Depends on | Status |
|---|---|---|---|---|
| W1 | Document CPS ORG variables + 12-month vintage into the registry | `data-dictionary-agent` / `/document-data` | — (starts now) | Pending |
| W2 | Vendor + config-scope `00a/01a/01b`; enumerate inert-guards | implementation (build) | Approval; W7 gate for submit | Pending |
| W3 | IPUMS extract definition + **human-gate submit/download** | implementation (build) | W2 defined; **user go-ahead (M13)** | Pending |
| W4 | Python rewire: `01a_data_ingest.py`, `01h_nonemployed_pool.py`; retire `00_export`; `run_all` R stage | implementation (build) | W2, W3 outputs | Pending |
| W5 | Method-fidelity / parity gate + companion run + report | implementation + `methodology-reviewer` | W2, W4 | Pending |
| W6 | Reviews: methodology (vendored subset + weighting), code (R config diff, Python rewire, parquet handoff), maintenance (drift vs `33bbcb7`) | `methodology-reviewer`, `code-reviewer`, `maintenance-agent` | W5 pass | Pending |
| W7 | Pipeline-gated numeric + consistency reviews; downstream `02a`/`02b`/`02d`; new baseline | `/review-numbers`, `/review-consistency` | pipeline success (W4/W5) | Pending |
| W8 | Docs: `PROJECT.md` Data-in-Scope, `docs/` internalization note (+SHA), R-package deps, session log | implementation + `eig-writer` (note) | W5 | Pending |

## Execution Waves

1. **Wave 0 — Approvals (now):** user approves this spec + plan. In parallel, **W1** (`data-dictionary-agent`) can start immediately (no pipeline dependency) to document the ORG variables/vintage; and I present the **W3** extract definition for the M13 human-gate.
2. **Wave 1 — Vendor + gate the extract:** **W2** (vendor `00a/01a/01b`, config + inert-guards, enumerate diff) → present extract definition → **on user go-ahead**, submit/download (**W3**). Tier 2; checkpoint the raw `.dat.gz` + partitions.
3. **Wave 2 — Rewire Python (W4):** retire `00_export`; rewire `01a`/`01h` to EIG-native inputs; add the `Rscript` ingestion stage to `run_all.py`. Verify `hourly_workers.parquet` + `nonemployed_pool.parquet` build locally.
4. **Wave 3 — Method-fidelity gate (W5):** run companion full-history EIG run (via `EIG_ORG_RAW_DIR`), key-align on `(CPSIDP,MONTH,MISH)`, compare wage/hours/flags/weights on the overlapping 12 months; write parity report. **Stop and isolate if it fails materially** (do not proceed to W6/W7).
5. **Wave 4 — Specialist reviews (W6):** methodology-reviewer (fidelity of vendored subset; `EARNWT`-for-employed vs `WTFINL`-for-non-employed weighting), code-reviewer (R config diff, Python rewire, parquet handoff), maintenance-agent (drift check). Run in parallel after the gate passes.
6. **Wave 5 — Pipeline-gated reviews + downstream (W7) & docs (W8):** confirm `02b`==`02a` parity test passes; run `02d`; record new baseline + delta; number/consistency reviews per the shared pipeline-runner; finalize docs and session log.

## Routing summary (what runs now / waits / why)

- **Now:** approval of spec+plan; `data-dictionary-agent` (W1) — independent of the pipeline. Present extract definition for the human-gate.
- **Waits on approval:** vendoring build (W2).
- **Waits on user go-ahead (outward-facing, quota):** IPUMS submit (W3).
- **Waits on data:** Python rewire (W4), gate (W5), all reviews (W6/W7).
- Review commands are pipeline-gated per `.claude/rules/review-pipeline-runner.md`; they do not run until the pipeline (through `02`) succeeds.

## Performance / Cost Tier Notes

- Highest expected tier: **Tier 2** (IPUMS extract build + download; 12 monthly samples, <1 GB; per-year `ranger` RF fits are minutes-scale). No Tier 3/4 step anticipated.
- Long-run safeguards: `00a` cache-validity check prevents re-submitting an unchanged extract; checkpoint raw `.dat.gz` and both partition sets; single-thread seeded RF for determinism; timeout already set in `00a` (`extract_timeout_sec_num`).

## Completion Criteria

All spec MUST items (M1–M14) satisfied and Success Criteria 1–8 met; method-fidelity gate passed and reported; specialist reviews clean or dispositioned; downstream static parity test green on internalized data; deliverables (registry, docs+SHA, R deps, parity report, updated `PROJECT.md`) present.

## Next Action

Await user approval of this spec + plan, then present the W3 IPUMS extract definition for the M13 human-gate. No build and no IPUMS submission until approved.
