# fig12_clawback_net_gain — Tufte/EIG assessment
**Verdict:** Ship as-is

**Strengths:**
- Textbook emphasis: single-mother bar in token accent purple (`eig_purple_800` #39274F, line 578) against neutral gray comparison bars — one encoded color plus gray, exactly the minimal-color pattern EIG/Tufte prefer.
- Clean data-ink: no boxed border, no gridlines (y-grid blanked line 599), no baked-in title or source in the PNG — all deck chrome lives on the slide layer.
- Lie factor ~1: x-axis anchored at 0%, bar lengths proportional, value labels (18.1/23.1/26.9) let the reader read exact magnitudes.
- Correct hierarchy and integration on the slide: serif headline, italic annotation, kicker, and a proper `Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.` line; no clipping.

**Issues:**
- `- [LOW] Comparison bars use #9AA0A6, a net-new gray not in the token set (line 579) → acceptable neutral (no token gray equivalent exists), but document it as an intentional de-emphasis gray or swap to a documented neutral to stay strictly token-derived.`
- `- [LOW] Value labels make the x-axis largely redundant data-ink (ticks 0/10/20/30% + axis title, lines 588–592) → optional: drop the x-axis title and/or ticks to lean the display further, since the annotation already frames the metric.`
- `- [LOW] Headline clause "half is clawed back" is not visualized by this net-gain chart, which shows returns of 18.1/23.1/26.9%, not a clawback fraction → confirm that claim is supported elsewhere in the deck; the annotation ("rises ~18% vs ~27% and ~23%") maps cleanly to the bars and is fine.`

**Integration:** Emphasis color is on-brand (token purple `eig_purple_800` for single mothers, neutral gray for others) and reads instantly — headline "single mothers gain the least" matches the shortest bar. Whitespace: three short bars on a WIDE slide leave a visibly empty right third (bars top out at 26.9% against a 30%+ axis); this reads as intentional breathing room rather than a flaw for a single-message slide, but it is the layout's only soft spot — no fix needed.

Top 3 (all LOW / optional): (1) document or swap the non-token gray; (2) trim redundant x-axis given value labels; (3) verify the "half is clawed back" headline claim against source analysis.
