# fig08_pool_wage_distribution — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Fully brand-compliant: every color is token-derived and 2022-primary (`eig_green_700`, `eig_gold_600`, `eig_teal_900`, `eig_black`); horizontal gridlines only, no boxed border, and no baked-in title/source under `slide=TRUE` (05d_supporting_figures.R:641,643).
- High data-ink ratio and honest encoding: a single clean density curve, a legitimate area fill (not a gridline) marking the below-target region, blanked y density ticks (05d:648), and an x-axis anchored at $0 with no truncation — lie factor ≈ 1.
- Both annotations are legible and well placed at WIDE `ts=1.9`: the "$16.80 target" label sits just right of the reference line near the peak with no curve collision, and "47.8% of the pool below the target" sits cleanly inside the shaded area (05d:629–636).
- Deck hierarchy is clean: green eyebrow, serif headline, italic annotation, figure, then source line — no clipping and the figure fits the WIDE frame.

**Issues:**
- `- [MEDIUM] Visual emphasis contradicts the headline. The gold-shaded, labeled region is the BELOW-target mass (47.8%), the visually dominant element, yet the headline claims "most... could still command offers ABOVE the target." The reader must mentally compute 52.2% (a thin majority) from the one number shown. The eye is pulled to the opposite of the framing. → Shade/annotate the above-target region instead of (or in addition to) below, or add an "above target" callout so the dominant visual matches the headline (05d:624–625,633–636).`
- `- [LOW] Slide annotation cites an unanchored comparison. "vs. 21.7% of paid-hourly workers" has no visual referent in this single-series density; the reader cannot verify or locate it on the chart. → Keep as contextual text, but consider a small comparison overlay/reference, or move the 21.7% contrast to the paired paid-hourly figure (figA1).`
- `- [LOW] "Most" is a near-coin-flip (52.2% vs 47.8%). The word overstates a razor-thin majority that the near-symmetric split around the target honestly shows. → Soften the headline (e.g., "roughly half... could still command offers above the target") to match what the figure depicts.`

**Integration:** The figure is technically excellent and brand-clean, but its framing works against the slide. The headline is an "above target" story; the chart shades, labels, and thereby foregrounds the "below target" story, and the only quantitative annotation (47.8%) is the complement of the headline claim. The near-50/50 split around the $16.80 line means "most above" is literally true (52.2%) but visually undersold — the honest picture is a coin flip, not a comfortable majority. The italic subhead adds a 21.7% paid-hourly comparison that the chart cannot show. Net: no rendering or brand defects; the fixes are about aligning visual emphasis and headline strength with the near-even distribution the figure faithfully reports.

**Top 3 prioritized:**
1. [MEDIUM] Realign shading/annotation emphasis (or headline) so the dominant visual supports "most above the target."
2. [LOW] Anchor or relocate the "21.7% of paid-hourly workers" comparison that has no visual in this figure.
3. [LOW] Soften "Most" to reflect the 52.2%/47.8% near-even split.
