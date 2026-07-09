# EIG Tufte Critique

Use this skill to **ideate** new data visualizations and **critique** existing figures,
tables, dashboards, and results graphics for graphical excellence — the design-quality
layer that sits on top of EIG brand compliance. Apply when designing a chart, improving a
draft figure, reviewing a dashboard, deciding between visualization approaches, or reducing
chartjunk / raising data density.

This skill answers "is this a *good display of the data*?" It is the complement to
`eig-style-review`, which answers "is this *on-brand and compliant*?" Run both for a full
figure review.

## Source Priority

1. `Infrastructure/style/docs/tufte-principles.md` (data-ink, lie factor, chartjunk, small multiples, density)
2. `Infrastructure/style/docs/tufte-analytical-design.md` (six principles, sparklines, layering, range-frames, causality)
3. `Infrastructure/style/docs/eig-figure-style.md` (brand standards that constrain the design space)
4. `Infrastructure/style/docs/agent-01-design-spec.md` (tokens, output coverage matrix)

## EIG Reconciliation (binding)

- **Color.** The EIG brand palette governs *which* hues are allowed; Tufte governs *how
  many*. Prefer one or two series colors plus neutral gray. Do not override brand hues for
  "grayscale" — minimize the *count* of encoded colors instead. Highlight/callout uses Gold
  per `eig-figure-style.md` §1.
- **Sizing.** The 6.5 × 3.5 in standard figure is a default, not a ceiling. Small-multiple
  arrays and high-density displays may exceed it; note the exception.
- **Never relax** a brand non-negotiable (source line, `Figure N.` caption, token colors,
  no vertical gridlines, no plot box) to satisfy a Tufte preference. Where they genuinely
  conflict, flag it as an open decision rather than silently choosing.

## Workflow — New Visualizations

1. **Clarify the data story.** What comparison matters? What is the key insight? Who is the audience?
2. **Select approach via Tufte principles.**
   - High comparison need → small multiples (identical scales across panels)
   - Dense data → data tables, sparklines, layered display
   - Time series → line chart, minimal grid, range-frame axis
   - Part-to-whole → avoid pie charts; prefer bar or table
   - Results (regression/event study) → coefficient/event-study plot with neutral baseline, Gold highlight, annotated treatment moment
3. **Design with data-ink in mind.** Start minimal; every element earns its ink; default to the fewest encoded colors.
4. **Eraser test.** For every element (label, tick, gridline, border, annotation): can it be erased without losing information conveyed elsewhere? Drop duplicate encodings (numeric label next to a marked value; legend duplicating direct labels).
5. **Collision test.** For every text element, mentally draw its bounding box. Does anything cross it? Standard fixes: move prose to the figcaption; relocate epoch/band labels to a strip above the plot; push baseline labels to the margin; add leader lines.
6. **Tufte test.** Run the quick checklist below.
7. **Hand off implementation** to `eig-style-apply` / `eig-style-guide-agent` for token-correct R/Python/Stata code.

## Workflow — Critiquing Visualizations

1. **Graphical integrity.** Estimate the lie factor if proportions look off; verify baselines, consistent intervals, deflated money; check for 3D distortion or truncated axes.
2. **Chartjunk.** Flag decoration, heavy grids, moiré patterns, 3D effects, gratuitous icons.
3. **Data-ink ratio.** What can be erased? What is redundant?
4. **Analytical design.** Walk the six principles (comparison, causality, multivariate, integration, documentation, content). The lowest-scoring principle is the biggest opportunity.
5. **Improvements.** Give specific before/after recommendations, each tied to a principle and respecting EIG brand non-negotiables.

## Required Findings Format

For each finding:

1. Severity (`Critical`, `Medium`, `Optional`)
2. Principle invoked (e.g. data-ink, lie factor, "compared to what?", layering)
3. Evidence (the specific element or code/output location)
4. Before → after recommendation
5. EIG-compliance note (confirm the fix keeps brand non-negotiables, or flag a conflict)

## Quick Checklist

- [ ] Lie Factor ≈ 1.0 (no visual distortion)
- [ ] Data-ink ratio maximized; eraser test passed
- [ ] Zero chartjunk; collision test passed
- [ ] Answers "compared to what?"
- [ ] Shows causality/mechanism where relevant
- [ ] Multivariate where the question is multivariate (not over-reduced)
- [ ] Words, numbers, images integrated — not segregated
- [ ] Reveals multiple levels of detail (micro + macro) where useful
- [ ] Layering: primary data dominates; secondary recedes
- [ ] Appropriate data density (shrink where it gains impact)
- [ ] Fewest encoded colors (1–2 + gray) within the EIG palette
- [ ] All EIG brand non-negotiables intact (source line, caption, tokens, gridlines, no box)
