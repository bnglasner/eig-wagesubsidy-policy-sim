# fig09_firm_capture — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Correct color semantics: saturated `eig_green_700` for the realistic/headline series and neutral `GRAY` for the disclosed upper bound (lines 325–326). Gray-as-de-emphasis is textbook Tufte and honestly signals "this is a bound, not a forecast."
- Clean brand compliance: 2-color palette only, horizontal gridlines only, no boxed border, and no baked-in title/source on the slide PNG (title/caption set to `NULL` when `slide` is TRUE, lines 331–335). Slide chrome (kicker, headline, italic annotation, source line) is layered in the deck, exactly as intended.
- Direct value labels on every bar (line 321) make the 2.9 / 1.7 / 3.9% realistic numbers readable without decoding axis position, and the legend spells out "realistic" vs "bound." No label collisions.

**Issues:**
- `- [MEDIUM] Visual hierarchy inverts the headline: the tall gray "bound" bars (43.4 / 26.8 / 58.4%) dominate the pre-attentive field by height/area, while the green "~3%" story the headline tells is nearly flat against the axis. Height is a stronger cue than saturation, so a scanning viewer may read "firms capture a lot" before the labels correct them. → Anchor the eye to green: add a direct annotation/callout on the green cluster (e.g., a short "~3% realistic" leader) or a subtle highlight, near the geom at lines 319–324. Do not shrink the gray bars — the contrast is the point — but give the reader an explicit visual entry to the realistic series.`
- `- [LOW] Non-monotonic x-axis order: display sequence is Central (β=0.5) → Measured (β=0.7) → Rigid (β=0.3), so β runs 0.5, 0.7, 0.3 (lines 308–309). A parameter axis reads more naturally in monotone order. → Reorder factor levels to β ascending (Rigid 0.3, Central 0.5, Measured 0.7) at lines 308–309.`
- `- [LOW] Annotation/label wording drift: legend/series says "renegotiate," axis title is "share of gross cost," and the headline says "keep." All fine, but confirm "Sticky incumbent wages (realistic)" vs annotation's "wage stickiness" stay stable across the deck (terminology consistency). No code change required.`

**Integration:** Partially. The headline ("about 3%"), the annotation ("no more than ~4% … $7.25 floor"), and the green value labels (2.9/1.7/3.9%) all tell the realistic story, and the annotation is genuinely additive (it explains the mechanism — the wage floor — that the chart cannot show). But the chart does not fully *foreground* that story: the largest, most eye-catching objects on the slide are the gray upper-bound bars, which are the deliberately de-emphasized series. The color choice pulls toward green while the geometry pulls toward gray, leaving a mild tension between what the eye lands on and what the headline claims. Fits the WIDE layout with no clipping and matches the headline's substance; the recommended anchor on the green cluster would close the last gap.

**Top 3 (prioritized):**
1. [MEDIUM] Anchor the eye to the green realistic series (callout/highlight) so the headline's 3% is the visual entry point.
2. [LOW] Reorder x-axis to monotone β (0.3, 0.5, 0.7).
3. [LOW] Keep series/annotation terminology stable across the deck.
