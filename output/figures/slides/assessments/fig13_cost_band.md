# fig13_cost_band — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Clean two-color encoding: `eig_green_700` for the three core models and `GRAY` for the disclosed bound, plus a light `eig_green_500` reference band — 2 series colors + neutral, fully within the 2022 primary palette (no legacy). Dashed linetype reinforces the bound's "not a forecast" status redundantly with color.
- High data-ink ratio: no chartjunk, no boxed border, no vertical gridlines, direct value labels ($45B, $46–$48B, etc.) in lieu of a legend or gridline lookups. Slide variant correctly suppresses baked-in title/source (title/caption `NULL`).
- Faithful to the message and the headline: the three core rows all fall inside the shaded $45–48B band while the flex row sits far right, so the "only wholesale renegotiation escapes" claim reads directly off the geometry (lie factor ≈ 1 for a position/range plot).
- Bound is honestly demoted: gray + dashed + the "disclosed upper bound, not a forecast" annotation prevent the $63–100B tail from being read as a competing estimate.

**Issues:**
- `- [LOW] The three core rows compress into a tiny left region; at slide scale (ts=1.9) the two endpoint dots on the reduced-form and structural rows render as overlapping "peanut" blobs rather than legible ranges → consider a thin range bar (or smaller point size at 05d line 208–209 `geom_point(... size = 3)`) so the short $46–48B / $47–48B spans read as intervals from the back of a room.`
- `- [LOW] The WIDE panel underfills its slide zone: data max is ~$100B against a $125B axis limit, leaving substantial dead space right of the $120B tick (slide right ~15–18% empty). Optionally tighten `limits = c(40, 125)` toward ~110 (05d line 226) or widen the placement to use the wide layout, without clipping the $63–$100B label.`
- `- [LOW] X-axis starts at $40B, not $0 (05d line 226 `limits = c(40, 125)`). Acceptable and even helpful for a Cleveland-style position plot (no length-from-zero encoding), but worth a one-line confirmation it is intentional; the truncation is what makes the core clustering legible.`

**Integration:** Headline "Only wholesale wage renegotiation escapes the $45–48B net range." matches the geometry exactly — the flex/bound row is the sole escapee. The subtitle annotation "Static, reduced-form, and structural models all cluster in the $45–48B net range." is additive, not redundant: it names the three clustered families the chart shows as blobs. Hierarchy is correct (kicker → bold teal headline → italic subtitle → chart → source line), source line present at slide level ("Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026."). No clipping of the right-edge $63–$100B label. Only cosmetic polish (dot legibility, zone fill) separates this from ship-ready.

Top 3 prioritized: (1) core-range dot legibility at projection; (2) underfilled wide zone / axis upper limit; (3) confirm intentional $40B axis start.
