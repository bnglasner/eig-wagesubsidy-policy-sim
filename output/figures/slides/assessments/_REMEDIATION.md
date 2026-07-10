# Slide-figure assessment — consolidated remediation

18/18 assessed. Verdicts: 17 Minor fixes, 1 Ship as-is (fig12), 0 Needs work.

## Applying (high value)
**Deck integration (generator / JSON):**
- **fig05 [HIGH]** — rendered with the WIDE helper, so its two-column bullets never appeared (map sat centered with an empty right column). → switch call to `figTwoCol`.
- **fig06 [HIGH]** — annotation described the 59M→10–15M *pool*, but the figure is a single-worker reservation-wage schematic. → rewrite annotation to the threshold mechanic.
- **fig07b [MEDIUM]** — headline "mostly job-seekers" contradicts the bars (other non-participants 64% > unemployed 33%). → rewrite headline to the accurate "barely any are disabled or retired" point.
- **fig08 [MEDIUM]** — headline "most … above target" fights the gold-shaded 47.8% below-target mass and overstates a 52% majority. → reframe to the below-target comparison (47.8% vs 21.7%).

**Figure code (05c/05d):**
- **fig03 [MEDIUM]** — highlight vector lacked "Female" (headline leads with women) and gold marked both the highest and lowest education bar. → highlight = Female, 16–24, Less than HS.
- **fig04 [MEDIUM]** — white interior "N.M workers" labels on gold are low-contrast. → dark label color.
- **fig02 [MEDIUM]** — orphaned "Unattributed*" asterisk (footnote nulled on slides) and a "−0.0" negative-zero label. → drop asterisk in slide mode; clamp near-zero.
- **fig07 [MEDIUM]** — precedent tick labels too small at projection. → bump size.
- **fig09 [MEDIUM]** — bargaining scenarios out of order (0.5, 0.7, 0.3). → reorder ascending.
- **fig11b [MEDIUM]** — the ~53 hr/wk crossover (the headline's point) is computed but never drawn; the two dark-green lines are hard to tell apart. → mark the crossover; differentiate the "without subsidy" line.
- **fig15 [MEDIUM]** — redundant value axis (every bar labeled). → drop x-axis on slide.
- **fig10 [MEDIUM]** — floor/high cost-per-job endpoints read as a reader trap. → label with entrant counts.
- **fig13 [LOW]** — x-limit ($125B) overshoots data (~$100B), underfilling the panel. → tighten limit.
- **fig01 [MEDIUM]** — unlabeled no-subsidy identity line; $21 median unmarked. → add "No subsidy" label + median marker.

## Accepted as-is (documented, not changed)
- **Neutral grays** (`#9AA0A6`, `#999999`, etc.) flagged as non-token across several figures: the 2022 EIG palette has **no gray token**, and `style-figure-rules.md` explicitly permits "neutral gray" for de-emphasis. Compliant; left as-is.
- **fig11 y-axis truncation** — this is a net-income *level* chart where the message is the cliff drops; a zero baseline would compress and bury the point. Defensible; left as-is (the shaded gaps are drawn line-to-line, so no inflation).
- **fig14** — headline nuance and twocol density noted; the right-column bullets carry the interpretation; left as-is.
- **fig12** — Ship as-is.
