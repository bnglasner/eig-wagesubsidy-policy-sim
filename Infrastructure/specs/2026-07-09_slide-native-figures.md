# Requirements Spec — Slide-Native Companion Figures

**Status:** DRAFT (awaiting approval)
**Date:** 2026-07-09
**Owner:** Benjamin Glasner / Adam Ozimek (EIG)
**Related:** `Infrastructure/plans/2026-07-09_companion-slide-deck.md`; deck at `output/slides/2026-07-09_80-80-companion-deck.pptx`

## Objective
Produce a parallel set of figures **authored explicitly for the 16:9 slide deck** — sized to the slide figure zone, with in-figure titles/sources stripped (the slide supplies them natively), projection-legible type, and Tufte/EIG-compliant simplification — plus an independent, per-figure Tufte/EIG assessment of each output and its integration into the deck.

## Confirmed decisions (from user)
- **Output:** parallel set at `output/figures/slides/`; `output/figures/main/` (document figures) untouched. **CLEAR.**
- **Figure text:** strip both the "Figure N." title **and** the source line from slide figures; the slide supplies a native EIG headline + a one-line reader annotation + the source line. **CLEAR.**
- **Assessment:** independent per-figure written Tufte/EIG critique saved as a report, then apply fixes and re-verify. **CLEAR.**

## Requirements

### R1 — Layout classes (MUST)
Two slide layout classes, chosen per figure:
- **`wide`** — single-figure slide. Figure fills a zone of ~9.0 × 3.9 in (AR ≈ 2.30). Author the ggplot at AR ≈ 2.30. Applies to bar/line/distribution/waterfall charts.
- **`twocol`** — figure on the left (~5.0 in wide), native takeaway bullets/annotation on the right. Author at AR ≈ 1.1–1.5. Applies to small-multiples and near-square outputs: `fig03` (take-up), `fig14` (uncertainty grid), `fig05` (state map), and any figure the assessment flags as needing side annotation.

### R2 — Strip in-figure chrome (MUST)
Slide figures render with `title = NULL`, `subtitle = NULL`, `caption = NULL`. No "Figure N." and no source line baked into the raster.

### R3 — Projection legibility (MUST)
Slide theme raises base type vs. the document theme (doc `base_size ≈ 10`). Target slide `base_size ≈ 16–18`; axis labels, data labels, and in-plot annotations scaled up so they read at presentation distance. Per-figure `geom_text`/annotation sizes are re-authored (a theme delta alone is insufficient — label sizes live in the geoms).

### R4 — Brand + Tufte compliance (MUST)
- Colors only from the 2022 primary token palette (`Infrastructure/style/tokens/eig-style-tokens.v1.json`); no legacy sets.
- Source Serif Pro / Open Sans via the existing theme.
- Horizontal gridlines only; no boxed borders; lie factor ≈ 1; maximize data-ink; ≤ 2 series colors + neutral gray where feasible (`Infrastructure/style/docs/tufte-principles.md`, `tufte-analytical-design.md`, `style-figure-rules.md`).

### R5 — Single source of truth for slide text (MUST)
A committed per-figure spec drives both the R dims and the deck text: `code/05_figures_tables/slide_figures.json`. Per figure: `slug`, `layout` (`wide`/`twocol`), `export_w`, `export_h`, `headline`, `annotation` (one-line reader follow-along), `source` (default EIG line), and `bullets` (for `twocol`). R reads dims; the deck generator reads headline/annotation/source/bullets. Seed values reuse the headlines/notes already in the current deck.

### R6 — Harness extension, non-destructive (MUST)
- `eig_save_fig(..., target = c("main","slide"))` selects the output dir (`output/figures/slides/` for `slide`). Default `main` — existing behavior unchanged.
- New `eig_slidify(p, tokens, base_size)` helper applies R2 + R3 theme deltas.
- Each of the 18 figure functions gains a guarded slide-variant save driven by the JSON spec. Document builds are unaffected when the slide flag is off.

### R7 — Both raster + vector (SHOULD)
Slide figures export PNG (300 dpi) and SVG, mirroring the document set.

### R8 — Deck integration (MUST)
The deck generator consumes `output/figures/slides/*` and renders, per figure slide: native EIG headline (from spec), the figure fit to its zone, a one-line native annotation, and the native source line. Removes reliance on baked-in figure titles (resolves the earlier title-duplication).

### R9 — Independent assessment (MUST)
Per-figure Tufte/EIG critique (fresh-eyes specialist), each covering: (a) the slide figure in isolation (data-ink, lie factor, legibility, palette, chartjunk), and (b) its integration into the slide (headline–figure fit, annotation usefulness, whitespace, hierarchy). Saved to `output/figures/slides/assessments/` (or `review-reports/`). Fixes applied and re-verified.

## Non-goals
- Not changing the document (brief) figures except where a shared root cause is trivially co-fixable (flagged, not assumed).
- Not re-running the analysis pipeline; figures rebuild from existing parquet intermediates.

## Clarity status
- Layout AR targets: **ASSUMED** (2.30 wide / ~1.2 twocol) — refined per figure during assessment; user may override.
- Slide `base_size` 16–18: **ASSUMED**.
- Assessment report location: **ASSUMED** `output/figures/slides/assessments/`.
- Everything in "Confirmed decisions": **CLEAR.**
