# fig02_cost_waterfall — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Clean brand compliance: all four series fills are 2022-primary tokens (green_700 endpoints, gold_600 adds-cost, blue_800 recaptured) plus a neutral gray for the reconciliation plug; no legacy hues, no baked-in title or source line, horizontal gridlines only, no boxed border.
- Graphical integrity is sound: y-axis anchored at $0 with endpoint bars drawn to zero and floating bridge bars in between, so the lie factor is ~1 — the gross→net drop is not exaggerated.
- Offsets are ordered by magnitude (13.9, 7.5, 7.1 …), which lets the eye read the bridge as a monotone descent and makes the two dominant recaptures (Medicaid/CHIP, SNAP) obvious.
- Signed value labels on every bar carry the exact deltas, so the chart is self-documenting without dense axis reading.

**Issues:**
- `- [MEDIUM] The "Unattributed*" bar carries an asterisk whose explanatory footnote is dropped on the slide (caption = NULL at line 330), so the slide shows a dangling "*" with no referent and an unexplained +2.2 reconciliation plug. → Either surface a one-line footnote in the slide zone, rename the bar to "Unattributed" without the asterisk, or fold the plug into "Other" so the reconciliation category disappears from the projected view (label built at line 262; type/legend at lines 263, 322).`
- `- [MEDIUM] The mid-section bars and labels (Federal income tax −2.9 through Unattributed +2.2: −1.3, −1.0, −0.9, +1.0, −0.0, +2.2) are cramped on a 13-category WIDE waterfall and sit near the legibility floor at projection distance; the +1.0 gold "Child tax credit" bar in particular is a hairline. → Consider collapsing the sub-$1.5B tail (State income tax, EITC, Child tax credit, Other, Unattributed) into one "Other offsets (net)" bar to cut categories and let the survivors grow, or raise label size above 2.5*ts (line 319) for the WIDE variant.`
- `- [LOW] "Other (net ~0)" prints as "−0.0", a negative-zero artifact of sprintf("%+.1f", value) (line 284). → Clamp |value| < 0.05 to render "~0" or "0.0" so no bar shows a signed zero.`
- `- [LOW] The 4-category color legend partly double-encodes direction that the +/− signed labels already convey (gold = "+", blue = "−"); acceptable per spec, but the "Reconciliation" swatch applies to a single bar. → Optional: drop "Reconciliation" from legend breaks (line 322) and rely on the footnote, keeping a 3-key legend.`

**Integration:**
Headline reconciles exactly to the figure: $55.9B rounds to "$56B gross" and $45.1B to "$45B net." The annotation ("Recaptured taxes and SNAP/Medicaid savings, partly offset by higher ACA premium credits") is additive and accurate — it names the two largest recaptures and correctly identifies ACA (+13.9, the sole large gold adds-cost bar) as the offsetting term, rather than restating the headline. Slide hierarchy is correct (kicker → headline → annotation → figure → source). The rotated left-most label "Gross wage-subsidy cost" clears the panel edge in both the standalone PNG and the slide (the slide-only l=26 margin at line 338 does its job) — no clipping. The one integration gap is the orphaned "Unattributed*" asterisk (see issue 1); the figure also reads slightly small within the WIDE zone, leaving unused horizontal margin, but that is a layout choice, not a defect.

**Top 3 (prioritized):** (1) resolve the orphaned "Unattributed*" asterisk on the slide; (2) reduce mid-section category crowding / raise small-label legibility for projection; (3) fix the "−0.0" negative-zero label.
