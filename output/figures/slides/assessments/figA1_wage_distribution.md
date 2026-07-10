# figA1_wage_distribution — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Brand-clean: below-target bars use `eig_gold_600` (#E1AD28), at/above use `eig_green_700` (#19644D), dashed line + label use `eig_teal_900` (#024140) — all 2022 primary tokens (05d lines 810, 827–828). Horizontal gridlines only, no boxed border, no baked-in title/source (all `labs()` set to NULL when `slide=TRUE`), so the deck kicker/headline/annotation/source own the framing.
- The two-color split is warranted: color encodes the single decision the figure exists to show (below vs. at/above the $16.80 eligibility threshold), not decoration. Direct in-panel region labels replace a legend (`guide = "none"`, lines 818–825) — good data-ink economy.
- Honest split at the cutoff: the $16–17 bin is stacked into a gold below-target segment and a green at/above segment, with the dashed line landing at its right edge — the eligibility count is not fudged onto a bin boundary. Lie factor ≈ 1 (zero baseline, linear count axis, whole-dollar bins).
- Round-dollar heaping the annotation cites is genuinely visible: local spikes at $15, $20, $25, and $30 stand above their neighbors, so the annotation is additive rather than asserting something the bars do not show.

**Issues:**
- `- [LOW] On the slide, the ~9.5% tail above $40 is truncated with no on-slide disclosure (caption is NULL when slide=TRUE, so the standalone note "a thin tail of X% earning above $40 is not shown" at lines 842–845 does not appear). The headline 22% is computed on the full uncounted pool (below_pct from d_full, line 787), so the finding is unaffected — but a viewer sees the axis stop at $40 with no cue. Fix: fold the tail note into the slide annotation or source line.`
- `- [LOW] Headline says "About one in five" (20%) while the in-panel label and math show 22% (21.7% rounded, line 819). Defensible as "about one in five," but the gap invites a picky reader to round the other way. Fix: either soften to "more than one in five"/"over a fifth" in the headline, or accept as-is (both figures are present and mutually consistent).`
- `- [LOW] At WIDE with the figure scaled down under the headline+annotation stack, the smallest in-panel text ("$16.80 / target wage", "Below target (eligible): 22%") is legible but is the first thing that will suffer if this slide is ever shown smaller. No change needed now; keep ts=1.9 and avoid shrinking the plot area further.`

**Integration:** Clean fit, no clipping. Hierarchy reads correctly: green kicker ("TECHNICAL APPENDIX · THE ELIGIBLE BASE") → serif dark-green headline → italic sans annotation → chart → source line. Headline ("one in five … below the target") and the in-panel "Below target (eligible): 22%" agree; the annotation about round-dollar heaping and the "dense stretch" at the target is confirmed by the bars (spikes at $15/$20/$25/$30; the $16–19 bins are the densest region around the cutoff), so it adds texture rather than restating the headline. Source line present and correctly external to the figure. Only integration gap is the unstated $40 truncation noted above.

**Top 3 (prioritized):** (1) LOW — disclose the >$40 tail truncation on the slide; (2) LOW — reconcile "one in five" vs. 22% wording; (3) LOW — protect small-label legibility if the slide is ever downscaled.
