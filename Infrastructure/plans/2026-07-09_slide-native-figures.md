# Orchestration Plan — Slide-Native Companion Figures

**Status:** COMPLETED 2026-07-09 — 18 slide-native figures built (`output/figures/slides/`), integrated into the deck with native headline/annotation/source, independently assessed per-figure (18 reports in `output/figures/slides/assessments/`), and remediated. See session log + `_REMEDIATION.md`.
**Spec:** `Infrastructure/specs/2026-07-09_slide-native-figures.md`

## Objective
Build a parallel, slide-optimized figure set (`output/figures/slides/`) for all 18 figures, integrate them into the 16:9 deck with native headline/annotation/source, and run an independent per-figure Tufte/EIG assessment with fixes.

## Workstreams & routing

| ID | Workstream | Route | Depends on |
|----|------------|-------|-----------|
| W1 | Spec + per-figure content/dims sheet (`slide_figures.json`) | Orchestrator (done in spec) → finalize JSON | — |
| W2 | Harness: `eig_slidify()` + `eig_save_fig(target=)` + slides dir | Direct (R), eig-style-guide conventions | W1 |
| W3 | Author 18 slide figure variants (label sizes, legends, AR, strip chrome) | Direct (R) in batches; eig-style-guide-agent conventions | W2 |
| W4 | Regenerate slide figures (run R) | Direct (Rscript) | W3 |
| W5 | Deck integration: generator reads slides + native headline/annotation/source | Direct (pptxgenjs) | W1, W4 |
| W6 | **Independent Tufte/EIG assessment** per figure (figure + slide integration) | **Fan-out specialist subagents** (eig-style-guide-agent / eig-reviewer; fresh-eyes visual) | W4, W5 |
| W7 | Remediation: apply assessment fixes, re-render, re-verify | Direct + re-render | W6 |
| W8 | Finalize: optional `/review-code` on new R, session log, deliverables | code-reviewer (optional) | W7 |

## Execution waves
1. **Wave 1 — Foundation:** W1 finalize JSON spec; W2 harness; author ONE pilot figure end-to-end (e.g., `fig02` waterfall wide + `fig03` twocol) → render → eyeball. Locks the pattern before scaling. *(Checkpoint: confirm pilot looks right.)*
2. **Wave 2 — Build:** W3 author remaining figures in batches (wide batch, twocol batch); W4 regenerate all.
3. **Wave 3 — Integrate:** W5 rebuild deck against the slide set; render.
4. **Wave 4 — Assess (independent):** W6 fan out per-figure Tufte/EIG critiques of the rendered slide figures + their deck slides; collect written reports.
5. **Wave 5 — Remediate:** W7 apply fixes, re-render, re-verify (fresh-eyes visual QA pass).
6. **Wave 6 — Finalize:** W8 logs + optional code review.

## Performance / cost governance
- **Figure regeneration (W4):** Tier 2 (~2–10 min; the state map needs `sf`/`tigris`). Checkpointed by rendering in batches.
- **Assessment fan-out (W6):** the main cost driver — up to ~18 specialist subagents (or ~6 batches). Per `performance-cost-governance.md`, this is the escalation-worthy step. Default plan: **batch into ~6 groups** to bound cost, each a focused multi-figure critique; escalate to per-figure only for flagship figures (fig02, fig03, fig10, fig11, fig14). *(User can opt for full per-figure fan-out.)*
- No Tier 4 runs. No pipeline rerun.

## Completion criteria
- `output/figures/slides/` has all 18 figures (PNG+SVG), chrome-stripped, projection-legible, brand+Tufte compliant.
- Deck rebuilt against the slide set with native headline + one-line annotation + source per figure slide; renders with no overflow/overlap (fresh-eyes verified).
- Per-figure assessment reports saved; all accepted fixes applied and re-verified.
- `slide_figures.json` committed as the single source of truth; harness change is non-destructive (doc build unaffected).

## Risks / notes
- Per-figure geom label re-sizing is real work (not a theme toggle) — batched to stay consistent.
- The map (`fig05`) and small-multiples (`fig03`, `fig14`) go `twocol`; assessment may reclassify others.
- Keep `output/figures/main/` untouched; the brief is unaffected.

## Next action
- On approval: execute Wave 1 (finalize JSON, harness, pilot) and pause at the pilot checkpoint for a look before scaling.
