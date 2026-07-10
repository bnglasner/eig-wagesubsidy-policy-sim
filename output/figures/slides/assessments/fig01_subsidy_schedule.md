# fig01_subsidy_schedule — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Brand-clean: series colors are all 2022 primary tokens (green_500/green_700, gold_600, teal_900); horizontal gridlines only, no boxed panel border, and in slide mode title/caption are correctly `NULL` so the deck supplies "Figure N" and the source line (lines 200, 203).
- Strong direct labeling — the wedge is named in place ("Subsidy"), the three worked points carry inline `$X → $Y` labels, and there is no legend to decode.
- Numbers verify exactly: take_home(8)=15.04, take_home(12)=15.84, take_home(15)=16.44, and target = 0.80 × $21.00 = $16.80. Headline ("fills 80% of the gap to a $16.80 target") faithfully describes the plotted `w + 0.8·max(0, target−w)` schedule.
- Dek is genuinely additive, not redundant: it supplies the derivation (80% of the $21 median) and the meaning of the $7.25 floor, neither of which the headline states.

**Issues:**
- [MEDIUM] The dashed identity line (lower wedge boundary = employer-wage-only take-home) is never labeled, so a reader must infer that the wedge floor means "no subsidy." Comprehension of the whole figure hinges on that inference. → Add a direct label along the dashed line (e.g., `annotate("text", ...)` reading "No subsidy" or "Employer wage only") near the `geom_line(aes(y = emp), ...)` at lines 169–170; this is higher value than the gold "Subsidy" label alone.
- [MEDIUM] The dek anchors the target to "the $21.00 paid-hourly median," but the chart carries no marker at $21 even though the x-axis runs to it; the right third ($16.80–$21) is low-density whitespace showing only the rising no-subsidy segment. → Add a point/label at (21, 21) reading "$21 median" (x range is set at line 156, `seq(base_wage, 21, ...)`), so the dek's key number is visible on the chart and the right zone earns its space.
- [LOW] Raw hex grays are used instead of token-derived neutrals: `"#999999"` for the $7.25 floor vline (line 176) and `"#666666"` for the floor label (line 191). → Swap both to a gray from the `COL` token map for token purity (function otherwise sources every color from tokens).
- [LOW] The dotted vertical $7.25 floor line (line 176) sits essentially on the left axis/plot edge and duplicates the x-min where the schedule starts — near-redundant data-ink. → Consider dropping the vline and keeping only the "$7.25 floor" text label, which already carries the information.
- [LOW] Mild crowding at the convergence point near $16.80 where the take-home point, the teal target vline, and the "$15 → $16.44" label cluster; readable in the WIDE PNG but tightest element on the slide render. → Nudge the third worked-point label (hjust/vjust at line 182) or move it left of its point to open the kink.
- [LOW] The figure carries two "80s" (80% match rate in the headline, target = 80% of median in the dek) — inherent to the "80-80" program name, not a figure defect, but flag that the coincidence can momentarily read as one number applied twice. No code change.

**Integration:**
Headline matches the chart's mechanism exactly and the dek is accurate and additive (derivation + floor meaning), which is the ideal split. The figure fits its WIDE zone with no clipping or overlap and sits cleanly under the two-line headline. The main integration gap is that the dek's "$21.00 median" has no on-chart referent (see MEDIUM #2), leaving the right third under-labeled; addressing that also tightens visual balance. Authored at ts=1.9/base_size=17, axis and worked-point labels remain legible at projection distance.
