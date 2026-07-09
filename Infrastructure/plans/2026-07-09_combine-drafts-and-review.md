# Plan: Combine drafts → Word doc, full-review, review-style

**Status:** COMPLETED (2026-07-09)
**Date:** 2026-07-09
**Objective (from user):** Combine the summary draft and the technical appendix into a single Word document with figures integrated in the appropriate places, then run `/full-review` and `/review-style` against the combined draft.

## Key findings from scoping

1. **Two source drafts** in `drafts/`:
   - `2026-07-08_wage-subsidy-impact-cost-summary.md` (~2,900 words; references 17 figures fig01–fig15 incl. 07b, 11b; 3 inline tables).
   - `2026-07-09_technical-appendix.md` (no own figures; cross-references the summary's figures).
2. **Figures do not exist on disk.** `output/figures/main/` and `output/figures/appendix/` contain only `.gitkeep`. The summary references PNGs that were never committed / not regenerated in this checkout.
3. **Figures ARE regeneratable cheaply.** The R scripts `code/05_figures_tables/05c_core_figures.R` and `05d_supporting_figures.R` are fully implemented and emit every `fig01`–`fig15` PNG+SVG (300 dpi) to `output/figures/main/`. They read from parquet intermediates — all 23 exist under `output/data/intermediate_results/population/`. R 4.5.2 and all required packages (arrow, ggplot2, ragg, sf, tigris, …) are installed. This is a Tier 1–2 run; it does NOT require re-running the microsimulation.
4. **Tooling:** pandoc and soffice available; docx skill available.
5. **full-review pipeline gate:** No top-level `runall`/`run_all` script exists at repo root (pipeline entrypoint is `code/run_all.py`; `code/run_all.R` is a template stub). The full microsimulation is Tier 3/4 (escalation-gated). Prior review reports already exist (`drafts/review-reports/`, dated 2026-07-09) and intermediates are current.
6. **Reviewer format constraint:** the number and consistency reviewers parse `.md`/`.tex`/`.pdf`, NOT `.docx`. Review must target a markdown/PDF form of the combined draft, not the `.docx`.

## Approach

Produce **two artifacts** from the merge:
- `drafts/2026-07-09_combined-brief-and-appendix.md` — canonical review source (figures referenced by relative path).
- `drafts/2026-07-09_combined-brief-and-appendix.docx` — deliverable, figures embedded at the referenced positions.

## Execution waves

**Wave 0 — unblocked, runs now**
- W0.1 Regenerate figures: `Rscript code/05_figures_tables/05c_core_figures.R` then `05d_supporting_figures.R`. Verify all referenced fig01–fig15 (+07b,11b) PNGs land in `output/figures/main/`.
- W0.2 Build combined markdown (summary body → appendix; strip the two internal "Evidence (strip before publication)" blocks into an internal note or retain per user; keep figure refs and tables; single coherent heading hierarchy).

**Wave 1 — Word doc (depends on W0.1 + W0.2)**
- W1.1 Convert combined markdown → `.docx` via the docx skill / pandoc, embedding figures at their referenced positions. Verify each image renders and tables carry over.

**Wave 2 — reviews (depend on combined markdown; run in parallel)**
- W2.1 `/review-style` on the combined markdown (eig-reviewer behavior; writing + citation + figure rules).
- W2.2 `/full-review` on the project, with the combined markdown as the selected document. Pipeline-gate handling per user decision (see Open Decision). Spawns code, methodology, ai-skeptic, number, consistency reviewers → `drafts/review-reports/` (or a fresh subdir).

**Wave 3 — report**
- Combined findings summary; verification per `.claude/rules/verification-protocol.md`; session log.

## Open decision (user)
- How to satisfy full-review's pipeline gate given the full sim is Tier 3/4 and prior reports/intermediates are current: (a) re-run full Python pipeline first, (b) run only the cheap figure/table/manifest stages then review, or (c) proceed to review agents against current intermediates + combined draft, skipping the expensive re-run.

## Verification
- All 17 figure PNGs present and non-empty; each embeds in the `.docx`.
- `.docx` opens; headings, tables, figures, captions intact.
- Five review reports written; style review returns issue list.
