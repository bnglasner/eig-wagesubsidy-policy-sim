# Orchestration Plan: Evaluate the entry-from-nonemployment remodel spec

**Date:** 2026-07-08 · **Status:** ACTIVE · **Spec:** `Infrastructure/specs/2026-07-08_entry-from-nonemployment-remodel.md`

## Objective

Stress-test the draft spec (which proposes letting EITC-literature elasticities *inform* rather than *mechanically dictate* entry-from-nonemployment behavior in `01h`/`02d`) against a literature-scout evidence sweep and a data-dictionary feasibility assessment, then synthesize into a revised spec for user approval. **No implementation in this plan.**

## Workstreams

| Workstream | Route (Agent/Command) | Dependency | Status |
|---|---|---|---|
| W1 — Evidence sweep beyond EITC (wage-subsidy-specific, salience/take-up, matching-with-participation literature); re-verify existing EITC citations | `literature-scout` | none — starts now | **Complete** |
| W2 — Data feasibility: net-of-transfer reservation, fixed-cost proxy, entrant hours distribution, finer covariates | `data-dictionary-agent` | none — starts now | **Complete** |
| W3 — Synthesize W1+W2 into a revised spec | orchestrator (me) | W1, W2 complete | **Complete** |
| W4 — Present revised spec for user approval | orchestrator (me) | W3 | **In progress — this message** |

## Execution Waves

1. **Wave 1 (now, parallel):** W1 and W2. Both are pre-analysis/documentation workstreams with no pipeline dependency, per the routing matrix — they can run concurrently.
2. **Wave 2 (after Wave 1):** W3 — resolve as many BLOCKED clarity items in the spec as the evidence allows; flag genuine judgment calls for the user.
3. **Wave 3 (finalization):** W4 — present the revised spec; on approval, a separate implementation spec/plan is drafted (out of scope here).

## Performance/Cost Tier Notes

- Highest expected tier: Tier 1–2 (literature search + in-repo data inspection; no extract, no long-running compute).
- No long-run safeguards needed beyond normal agent runtime.

## Completion Criteria

- Both W1 and W2 reports read and incorporated.
- Revised spec written with BLOCKED items resolved or explicitly narrowed to a user decision.
- User has the revised spec to approve before any implementation work begins.

## Next Action

Launch `literature-scout` (W1) and `data-dictionary-agent` (W2) in parallel now; synthesize on return.
