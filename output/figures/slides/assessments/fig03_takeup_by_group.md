# fig03_takeup_by_group — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Exemplary data-ink economy: value axis, ticks, and gridlines are deliberately dropped on the slide variant (05c line 409-419) because every bar is directly labeled — no chartjunk, no box, only the single dashed reference line survives.
- Fully brand-compliant: two-color emphasis uses `eig_green_700` (#19644D) and `eig_gold_600` (#E1AD28), both 2022 primary tokens (line 384-385); no legacy palette; strip titles in `eig_teal_900`; no baked-in title/source on the slide (title/caption NULL, lines 391-396).
- Graphical integrity holds: the x-scale is shared across all five facets (only `scales = "free_y"`, line 389), so bar lengths are comparable panel-to-panel and the 21.7% dashed line sits at the same x everywhere; within-facet bars sort descending via `reorder` (line 373).
- Clean left/right slide balance: figure fills the left column with no clipping — the widest label "43.0%" and the "Race and ethnicity" strip both clear the panel edge thanks to the 0.28 right-expansion (line 388) and 16pt right margin (line 418).

**Issues:**
- `- [MEDIUM] Visual emphasis does not match the headline: the lede leads with "women," yet the Sex panel has no gold bar — gold marks only 16-24, Less than HS, and Graduate degree (highlight vector, line 366). The reader's eye is drawn to age/education standouts, but the headline's first claim is unhighlighted → add "Female" to the highlight vector on line 366 so the gold cue covers all three headline groups.`
- `- [MEDIUM] Gold carries two opposite meanings in the Education panel — it flags both the maximum (Less than HS, 37.4%) and the minimum (Graduate, 6.8%). Gold conventionally reads as "the standout high," so labeling the lowest bar gold can misread → either drop Graduate from the highlight vector (line 366) and let the length contrast carry it, or state in the annotation that gold marks the endpoints of the credential gradient.`
- `- [LOW] Data labels collide with the dashed reference line for bars ending near 21.7% (e.g., "19.7%", "16.0%" in the Age panel overlap the dashed line) → minor; nudge these labels or shorten the dashed line's vertical extent. Not a blocker.`
- `- [LOW] The odd fifth panel (Family type) leaves the bottom-right quadrant of the 2-col small-multiple empty, adding whitespace inside the left column → acceptable for an odd count; optionally trim figure height or reflow to 3x2 with the empty cell top-right.`

**Integration:**
The four right-column bullets are mostly redundant with the chart: every headline number (26.2/17.2, 43.0, 37.4/6.8, 23.5/13.5) is already directly labeled on a bar. The bullets earn their place only through two additions — the "60.5% of recipients" women's share (genuinely absent from the chart) and the narrative framing ("highest of any group"). Net: partially complementary, largely repetitive; tightening the bullets to lead with what the chart cannot show (recipient composition, the policy takeaway) would reduce the echo. Note one narrative slip: the bullet "single parents 23.5% vs married parents 13.5%" cherry-picks the parent comparison, but the chart's tallest Family-type bar is actually "Single, no children" at 28.5% — the visual's top family group goes unmentioned. Left/right balance and headline/annotation fit are good; no clipping.

**Top 3 prioritized:** (1) MEDIUM — highlight "Female" so the gold cue matches the headline's "women" claim; (2) MEDIUM — resolve gold's dual high/low meaning in the Education panel; (3) LOW — de-conflict data labels from the dashed line.
