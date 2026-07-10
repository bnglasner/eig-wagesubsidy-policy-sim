# fig11_benefit_cliff — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- On-brand 2022 primary palette only: green_700 line, gold_600 cliff points, teal_900 labels, neutral gray reference line — no invented hex, no legacy semantics.
- Clean slide integration: title/caption correctly `NULL` when `slide=TRUE` (lines 397, 399), so no baked-in title/source competes with the deck headline; horizontal gridlines only, no boxed border.
- The three in-plot annotations are non-overlapping and each sits in open whitespace beside (not on) its gold point — the primary risk on a busy multi-cliff line is well managed via the per-label `hjust`/`vjust` vectors (lines 390).
- Headline is faithful: the drops at ~$38k and ~$43.5k are visually the story, and "inherits everyone else's" maps directly to the TANF/Medicaid/childcare annotations; subtitle is additive, not redundant.

**Issues:**
- `- [MEDIUM] Truncated y-axis (starts ~$40,000, not $0) exaggerates cliff magnitude → lie factor >1. The $70k→$52k drop reads as ~60% of plot height but is ~26% of the value. → In fig code line 395, either set y limits to include 0, or add drop-magnitude labels (e.g. "-$18k") so the dramatized visual is anchored to a real number.`
- `- [LOW] The "earnings only" reference line is near-useless at projection: on the truncated + non-square panel its dashed slope-1 line is not visually 45°, so it no longer reads as an intuitive "earnings alone" baseline, and it only appears in the bottom-right corner. → Consider dropping it (data-ink saving) or extend it across the full x-range so the widening gap = benefit value is legible.`
- `- [LOW] The rotated "earnings only" label (annotate text, lines 383–385) crowds the plot edge and the leading glyph reads as clipped/against the line at projection. → Nudge x left / lower the angle, or remove with the reference line above.`

**Integration:** Fits the WIDE frame with no clipping; annotation legibility is the key risk on this chart and it passes — all three cliff labels are readable and non-overlapping at projection, each attached to a distinct gold point. Hierarchy (eyebrow → title → subtitle → chart → source) is intact and the annotation layer stays subordinate to the headline.

Top 3 prioritized: (1) truncated y-axis lie factor; (2) weak "earnings only" reference line; (3) rotated label crowding/clip.
