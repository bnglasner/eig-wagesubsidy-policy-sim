# fig07b_entrants_by_status — Tufte/EIG assessment
**Verdict:** Minor fixes
**Strengths:**
- Brand-clean: single `eig_green_700` token fill, Open Sans body labels, no boxed border, no vertical gridlines, no baked-in title/source (all set `NULL` when `slide=TRUE`) — deck supplies headline/kicker/source.
- Honest encoding: zero baseline, linear scale, bars sorted by magnitude (`reorder(status, entrants_M)`, line 147) — lie factor ≈ 1.
- Direct value labels on every bar remove any need for the reader to trace back to the axis; annotation's "~3%" claim (disabled+retired = 0.050M of 1.494M = 3.3%) is accurate.

**Issues:**
- `- [HIGH] Headline "mostly job-seekers" contradicts the bar ranking and its own annotation. The largest bar is "Other non-participants" (0.948M ≈ 64%), which the chart explicitly distinguishes from "Unemployed" (0.496M ≈ 33%) — i.e. the plurality are NOT job-seekers, and "a third are unemployed searchers" is not "mostly." → Reframe the slide headline to the point the data supports, e.g. "Entrants come off the sidelines — almost none are disabled or retired." (Slide text, not figure code.)`
- `- [LOW] Redundant scale ink: with every bar directly labeled, the x-axis title, ticks, and "M" suffix are near-redundant (data-ink). "Induced entrants (millions)" also double-states units with the "M" tick suffix (lines 155, 159). → Optionally drop the x-axis ("millions" stays only in the axis title) or shorten the title to "Induced entrants"; low priority since the axis still anchors scale.`
- `- [LOW] Optional emphasis to sharpen the (corrected) headline: if the slide's point becomes "not disabled/retired," a two-tone treatment — gray the tiny Disabled/Retired bars, keep green for the two active-margin groups — would carry the contrast visually. Single green is fully acceptable per brand; treat as an enhancement only.`

**Integration:** Fits the WIDE frame cleanly with no clipping; the 0.948M label clears the right edge via the `0.14` right expansion (line 156). ts=1.9 labels are legible at slide scale. Hierarchy is correct (kicker → headline → annotation → chart → source). The one real integration defect is the headline itself: it overstates the "job-seeker" share and conflicts with both the top-ranked bar and the annotation — fix the copy, not the chart.

Top 3 prioritized: (1) HIGH headline/ranking mismatch; (2) LOW redundant axis/unit ink; (3) LOW optional two-tone emphasis.
