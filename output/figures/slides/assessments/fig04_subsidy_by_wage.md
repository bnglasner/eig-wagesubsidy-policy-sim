# fig04_subsidy_by_wage — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Clean single-encoding horizontal bar chart: one gold series, no gridlines, no boxed border, no baked-in title/source (slide branding supplies all chrome). Fully data-ink efficient.
- Lie factor ~1: bars start at $0, linear x-axis, values read directly off bar ends. Sorted low-wage-to-high top-to-bottom, matching the headline's "lowest → largest" reading.
- Dual-labeling is genuinely additive: bar-end labels give the average subsidy, interior labels give the worker count — surfacing the honest counter-story that the smallest checks ($2,206) go to by far the largest group (11.7M).
- Headline is accurate and "by construction" is earned: the 80% gap-to-target formula mechanically pays more at lower wages.

**Issues:**
- `- [MEDIUM] White interior "N.M workers" labels sit on eig_gold_600 (a mid-tone amber), giving marginal text contrast — legible at full res but weak at slide scale, and these labels carry data (worker counts), not decoration → in 05d_supporting_figures.R:270 change interior label color from "white" to a dark token (e.g. COL[["eig_black"]] or eig_teal_900), or move counts outside/under the bar-end value.`
- `- [LOW] Annotation restates the two chart endpoints already labeled on the bars ($10,281, $2,206) — accurate but only mildly additive → recharge it with the worker-count inversion the chart already shows, e.g. "...yet the $13–16.80 group is by far the largest, 11.7M workers." This makes the subtitle earn its space and pre-frames the equity point.`
- `- [LOW] No vertical reference lines to gauge bar length against the $0/$3,000/$6,000/$9,000 ticks; acceptable here because every bar is directly labeled, but note the design leans entirely on labels for magnitude → keep as-is unless a de-labeled variant is needed.`

**Integration:** Fits the WIDE slot cleanly — no clipping of the "$10,281" bar-end label (16% right expansion provides headroom) or the rotated "Hourly wage bracket" axis title. Hierarchy is correct: green kicker "WHO GETS THE MONEY?" → navy headline → italic serif annotation → chart. Palette, fonts (Source Serif headline / Open Sans body + axes), and the absence of a figure-baked title/source all comply with EIG brand. Headline and annotation numbers match the figure exactly. Ship after the interior-label contrast fix; the rest are polish.

**Top 3 prioritized:**
1. MEDIUM — darken white-on-gold interior worker-count labels (05d line 270).
2. LOW — rework annotation to carry the worker-count inversion, not restate endpoints.
3. LOW — no magnitude gridlines; fine given direct labels, monitor only.
