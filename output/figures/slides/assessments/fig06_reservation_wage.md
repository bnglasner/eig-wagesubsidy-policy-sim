# fig06_reservation_wage — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Honest schematic: both bars anchor at $0 on a 0–$18 axis, so the lie factor is ~1 and the mechanic reads at a glance — the offer moves from $12 (below the $14 line) to $15.84 (clears it).
- High data-ink, no chartjunk: two bars, one reference line, one shaded region, direct value labels, no legend needed.
- Brand-clean: no baked-in title or source; `eig_green_700` and `eig_purple_800` are both 2022-primary tokens; no boxed border; y-gridlines suppressed.
- Headline "The subsidy exists to clear a worker's entry threshold" maps precisely onto what the figure shows.

**Issues:**
- `- [HIGH] Annotation does not describe this figure. "Of 59M non-employed adults, a realistic wage-responsive pool is ~10–15M" is a pool-sizing claim; this figure is a single-worker reservation-wage schematic with no pool magnitudes on it. → Move this annotation to the pool figure (fig13_pool_wage_distribution) and replace it here with a threshold-mechanic line (e.g., "The subsidy lifts a $12 offer past the $14 reservation wage, turning a rejected job into an accepted one").`
- `- [MEDIUM] Figure/ground collision on the "won't work" zone. The gray employer-offer bar (GRAY #9AA0A6) sits inside the gray shaded "will not work below this" band, so the very contrast that should signal "this offer falls short" is muted. → Differentiate them: give the below-threshold region a light tan wash (eig_tan_500 at low alpha) at line 557-558, or use a darker neutral for the offer bar at line 573.`
- `- [LOW] Hard-coded off-brand gray. GRAY <- "#9AA0A6" (line 39) is a net-new hex, not a token; non-negotiable #2 wants token-derived colors. → Map to an EIG neutral token or document the exception in the legacy-palette note.`

**Integration:**
Headline fits this figure exactly — the schematic is a clean visual proof of "clearing the entry threshold." The annotation does NOT fit: it quantifies the responsive pool (59M → 10–15M), a claim with no visual referent in a single-worker wage-level chart, and it reads as if it belongs to the non-employed potential-wage distribution figure. The "Reservation wage: $14" and "will not work below this" call-outs are legible at slide scale and correctly labeled. Figure sits within its WIDE zone with no clipping; hierarchy (kicker → headline → annotation → chart → source) is intact.

**Top 3 prioritized:**
1. [HIGH] Fix the annotation/figure mismatch (move pool claim off this slide; add a threshold-mechanic line).
2. [MEDIUM] Resolve the gray-bar-on-gray-band figure/ground collision.
3. [LOW] Replace the hard-coded `#9AA0A6` gray with a token or document the exception.
