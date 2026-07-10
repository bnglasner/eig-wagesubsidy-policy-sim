# fig07_entry_band_by_cell — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Honest encoding: x-axis anchored at 0M, linear, no truncation — the range bars (floor→high) and central point map to real magnitudes at lie factor ≈ 1.
- Clean data-ink economy — light-green range bar (alpha 0.55) recedes, dark-green central point advances; no chartjunk, no boxed border, y-gridlines suppressed, only the intended horizontal reading.
- Two-tone value hierarchy works: bold black central labels (`1.49M`, size 2.7·ts) read as the headline number; muted gray endpoint numbers sit quietly at the bar ends.
- Slide integration is correct on the non-negotiables: no baked-in title, source, or caption in the PNG (all `NULL` under `slide = TRUE`, lines 102, 104); eyebrow → headline → annotation → figure → source hierarchy is intact.

**Issues:**
- `- [MEDIUM] Precedent tick labels on the Total row are the smallest text in the figure (size 2.1·ts, lines 84-87) and drop further in the slide down-scale; four stacked two-line gray labels ("Paycheck Plus scale", "1990s EITC-alone scale", "Paycheck Plus men Y3 scale", "SSP scale") are marginal at projection distance → bump to ~2.4·ts and/or shorten to one line each (drop "scale"); the axis already reads "millions" so the ladder can be terser.`
- `- [LOW] Non-token raw hex grays introduced only in this figure: #BBBBBB tick (line 83), #999999 precedent labels (line 87), #777777 endpoint labels (lines 93, 96). Token-only rule (brand non-negotiable #2) — the module already defines a single neutral GRAY (line 39); consolidate these to the token-derived gray(s) rather than three ad-hoc values.`
- `- [LOW] Unit label inconsistency: central labels carry the suffix ("1.49M", line 89) but floor/high endpoint labels drop it ("1.02", "3.81", lines 92, 95). Harmless given the axis title, but a reader scanning only the bar ends sees bare numbers → either add "M" to endpoints or rely on the axis for all three.`

**Integration:** Fits the WIDE frame with no clipping — the far-right "3.81" and "SSP scale" clear the ~4M axis bound (limits c(-0.1, 3.9) + 6% right expand). Headline ("benchmarked against the closest real-world precedents") is faithful: groups on the y-axis, precedent reference ticks on the Total row. Annotation is additive, not a restatement — it names the central/floor/high for Total and locates it "between Paycheck Plus and the Self-Sufficiency Project," which the precedent ladder shows but the chart text does not spell out. Source line is applied by the slide template, not the figure. Ticks are localized to the Total row (no global gridlines), so there is no false implication they apply to the subgroup rows.

Top 3 prioritized: (1) precedent-label legibility at projection; (2) consolidate to token grays; (3) endpoint unit consistency.
