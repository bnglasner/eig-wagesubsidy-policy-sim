# fig15_hours_margin — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Brand-clean slide variant: `title = NULL` and `caption = NULL` when `slide` (lines 752, 754), single 2022-palette fill `eig_green_700` (line 744), no boxed border, deck supplies the eyebrow/headline/source. No baked-in chrome.
- Direct value labels (`bar_lab`, lines 738–739) carry both the FTE count and the gross-dollar consequence per row — reader never leaves the bar to decode magnitude.
- Lie factor ≈ 1: bars share a common zero baseline, linear x, ordered by `added_fte_M` (line 740); 0.06/0.19/0.28 bar lengths are faithful to the values.
- Numbers reconcile with the deck: upper bar 0.28M ↔ headline "~280K"; annotation range 0.19–0.28M matches central→upper; ε labels self-document the elasticity assumptions.

**Issues:**
- `- [MEDIUM] Redundant x-axis: direct labels ("0.28M FTE (+$2.4B gross)") already state every value, so the 0.0M–0.4M ticks + axis title duplicate the same information (data-ink).` → Drop the x-axis for the slide variant: add `axis.text.x/axis.title.x/axis.ticks.x = element_blank()` (or a short caption note that bars are added FTE) in the `slide` theme block near line 761; the labeled bars stand alone.
- `- [LOW] Unit double-labeled: tick suffix "M" (line 749) and axis title "(millions)" (line 753) both denote millions.` → If the axis is retained, drop "(millions)" from the title since the "M" suffix and label text already carry the unit.
- `- [LOW] Headline anchors on the upper bound (0.28M/~280K) while the "central" ε = 0.20 row (0.19M) is visually indistinct in a single-hue chart.` → Optional: emphasize the central row (e.g., keep 0.20 in `eig_green_700` and drop the other two to a neutral gray/lighter green via a conditional fill) so the eye lands on the consensus estimate the annotation cites, not the ceiling. Keeps within palette; still one encoded hue + neutral.

**Integration:**
- No label clipping: `expand = expansion(mult = c(0, 0.45))` (line 750) reserves 45% right headroom; the longest suffix "(+$2.4B gross)" clears the panel edge in both the PNG and slide-28 render.
- Redundant axis is the main Tufte cost — the value axis adds ink without adding information given the direct labels; erasing it is the highest-value fix.

**Top 3 (prioritized):**
1. [MEDIUM] Erase the redundant x-axis on the slide variant (labels already carry all values).
2. [LOW] Remove duplicated "(millions)" unit if the axis is kept.
3. [LOW] Consider highlighting the central ε = 0.20 row to match the consensus framing rather than the upper-bound headline.
