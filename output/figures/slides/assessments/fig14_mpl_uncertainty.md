# fig14_mpl_uncertainty — Tufte/EIG assessment
**Verdict:** Minor fixes

**Strengths:**
- Brand-clean: all three legend colors are token-derived (`eig_green_500`, `eig_green_700`, `eig_gold_600`, lines 689–691), no boxed border, sans typography, and slide mode correctly nulls title/subtitle/caption (lines 697–706) so the deck owns the headline and source line.
- The two-greens-plus-gold ramp is luminance-differentiated (light green → dark green → gold), so the λ series survives grayscale/most CVD; gold reads as the clear high-dispersion anchor.
- Sound labor division with the layout: the chart cannot show the $45–48B cost (not plotted), and the right bullets carry that firm result plus the "why we headline evidence-central" reasoning the dense scatter cannot.
- 27 points render without destructive overlap — `position_dodge(width = 0.6)` (line 687) cleanly separates the three λ dots in each penalty row for the central/upper facets.

**Issues:**
- `- [MEDIUM] "Single largest lever" does not read unambiguously from the chart: within a facet the penalty (y-row) march rightward is large, but the elasticity facet-to-facet shift spans nearly the entire x-range (lower ~0.2–0.7M vs upper ~1.4–3.8M), so a viewer could conclude elasticity is the biggest lever. The chart shows joint variation, not penalty dominance. → Either soften the headline to match the bullets' joint-variation framing, or add a within-facet penalty-range cue (e.g., annotate the central facet's 0%→20% horizontal span) to isolate the lever the headline names.`
- `- [MEDIUM] At TWOCOL scale (slide-27.jpg) legibility degrades: the top legend dots shrink to near-illegible, the 0/10/20% tick labels are very small, and the two greens (0.5 vs 0.75) become hard to separate in the compressed lower-elasticity cluster. → Bump point size for slide mode (currently 3.2 × ts, ts=1.35, line 664/687) and/or enlarge legend key + axis text via the slide branch; consider widening the left column a few percent.`
- `- [LOW] No reference gridlines on the quantitative (x) axis, which is the headline metric (induced entrants). Horizontal-only is the EIG default, but here the quantitative axis is horizontal, so reading whether a point sits at 1.5M vs 2M is imprecise. Adding light vertical gridlines at 1M/2M/3M would aid reading but conflicts with brand rule 5 (avoid vertical gridlines). → Keep the brand rule and flag as an open decision; do not silently add vertical grids.`

**Integration:**
Density is high but the standalone PNG handles it well; the strain is only at slide scale, where point/legend sizing (MEDIUM #2) is the binding constraint. The scatter fits the left column with no clipping — both axis titles, all tick labels, and the top legend are fully visible. The right bullets do carry the interpretation the chart cannot (cost firmness, joint-driver framing, headline justification), which is the correct use of TWOCOL. Left/right balance is reasonable; the chart could take a little more width to relieve the legibility issue without starving the bullets.

**Top 3 (prioritized):** (1) reconcile "single largest lever" headline with what the chart shows (MEDIUM #1); (2) enlarge slide-mode points/legend/axis text for TWOCOL legibility (MEDIUM #2); (3) decide on x-axis reference lines as an open brand-vs-quality call (LOW #3).
