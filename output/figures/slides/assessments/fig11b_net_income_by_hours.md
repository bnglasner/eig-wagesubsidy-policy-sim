# fig11b_net_income_by_hours — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Brand-clean: all five colors resolve to the 2022 `/colors/brand` primary palette (lines `eig_teal_900`/`eig_green_700`, fills `eig_gold_600`/`eig_tan_500`), horizontal gridlines only, no boxed border, and title/caption correctly `NULL` in slide mode (05d_supporting_figures.R:500-514) — no baked-in chrome.
- The gold-vs-tan ribbon is an honest, effective encoding: the gap is drawn line-to-line (05d:456-459), so the truncated y-axis does not inflate the difference, and the two-color sign split (gain vs. loss) directly narrates the clawback.
- Two-line legend with explicit `breaks` order, clear dual x-axis ("Annual hours worked" + "(NN hr/wk)" per tick, 05d:471), and the repositioned italic annotation now sits in open right-center space clear of both lines and the vertical cap label.

**Issues:**
- `- [MEDIUM] The crossover — the entire headline claim ("past ~53 hrs the clawback swallows the subsidy") — is computed but never drawn. cross_x is derived (05d:462-468) then discarded; no point, vline, or label marks it, so the reader cannot locate the ~53 hr/wk / ~2,650-hr threshold the headline names. → Add a marker at cross_x (e.g., geom_point + short "clawback begins" callout, or a light vline) so the tan region is anchored to a labeled hours value.`
- `- [MEDIUM] The two series are both very dark, low-luminance greens (#024140 vs #19644D), so near the crossover — where the lines converge and the story lives — the reader cannot tell which line is which; the tan fill is small and carries most of the burden. → Widen inter-series contrast within the brand palette (pair one dark line with a lighter/neutral gray line, keeping the palette), and/or increase the loss-ribbon salience (raise alpha or darken tan).`
- `- [LOW] On the slide the vertical "Subsidy hours cap (2,080 hrs/yr)" label rises into the top gridline/legend band and reads as truncated ("...(2,08"), because it is anchored at y=55500 growing upward (05d:484-487). → Lower the anchor y or reduce slide label size so the full "(2,080 hrs/yr)" clears the legend.`

**Integration:**
- Annotation collision fix HELD: the italic "Counted as income…" wraps to four lines and left-anchors at x=2160/y=60000 in slide mode (05d:491-498), sitting in open space clear of both lines, the tan region, and the vertical cap label. No clipping of the chart; kicker → headline → subhead → chart → source hierarchy is intact.
- Crossover visibility is the weak link for integration: the tan "loss" wedge exists in the upper-right and does support the headline directionally, but it is small, light, and unlabeled, and the headline's "~53 hours" value appears nowhere on the plot. Marking cross_x (Issue 1) is what would make the slide's claim self-evidently visible.

**Top 3 (prioritized):** (1) mark the crossover / ~53-hr threshold; (2) raise inter-series line contrast so the crossover is legible; (3) fix the vertical cap-label crowding at slide top.
