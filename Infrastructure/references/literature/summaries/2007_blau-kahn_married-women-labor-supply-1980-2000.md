# Blau & Kahn (2007) — Changes in the Labor Supply Behavior of Married Women: 1980–2000

- **Tier:** 1 (Journal of Labor Economics)
- **Type:** paper
- **DOI:** 10.1086/513416
- **Source:** https://www.journals.uchicago.edu/doi/10.1086/513416 ; NBER w11230
  (abstract read directly this pass)
- **Thread:** 6 / Thread A (the time-trend qualifier on ALL married-women elasticity
  evidence used for the `other_women` band)
- **Evidence class:** Measured/ex-post — repeated cross-sections (March CPS), labor-supply
  functions estimated separately by decade.

## Finding (verified against NBER w11230 abstract)
Married women's labor supply became dramatically less elastic over 1980–2000:

- "Between 1980 and 2000, women's own wage elasticity fell by **50 to 56 percent**."
- Married women's labor supply "became less responsive to their husbands' wages": the
  cross-wage elasticity declined "by **38 to 47 percent** in absolute value."
- The married-women labor supply function "shifted sharply to the right in the 1980s, with
  little shift in the 1990s."
- Robust to selection correction, taxes, and subgroup analysis (per abstract).

`[unverified: the commonly cited LEVEL estimates (total-hours own-wage elasticity falling
from roughly 0.8-0.9 in 1980 to roughly 0.4 in 2000) were not read from the full text this
pass — only the percentage declines above are verified from the authors' abstract. The
levels should be pinned to the paper's tables before appearing in code or published
claims.]`

## Why it matters for the `other_women` band
Two opposing implications, both load-bearing:

1. **Upward pressure on the band's width:** married women (the bulk of `other_women`) are
   *historically the most wage-elastic demographic group* — the classic labor-supply
   literature (surveyed in McClelland & Mok 2012, cataloged: married women's participation
   elasticity ~0-0.3, above men's and single women's ~0-0.1) is built largely on their
   behavior. An individually-assessed wage subsidy hits exactly the own-wage margin on
   which married women respond most. A band for `other_women` that sits *below* the
   single-mother band but *above* the men band — as the current EITC/CBO default does — is
   qualitatively the right ordering.
2. **Downward pressure on the level:** the responsiveness that generated the old 0.8-0.9
   estimates is roughly half gone by 2000 (and CBO's review notes the decline continued).
   Calibrating today's `other_women` cell to older married-women elasticities would
   overstate entry. The decline also shrinks the negative husband's-wage cross-elasticity —
   i.e., the household-coordination drag (the Bonin/Eissa-Hoynes income-effect channel) is
   itself smaller today than in the historical estimates.

Net: supports keeping the `other_women` central value moderate (between men and single
mothers), widening the band in BOTH directions, and discounting pre-1990s married-women
elasticities as upper-bound-only evidence.

## Caveats
- Ends in 2000; Heim (2007) and CBO (2012) report the decline continuing into the 2000s,
  so even the 2000 levels are likely upper bounds for the 2025-26 CPS population the model
  uses. `[unverified: Heim 2007 continuation not re-verified this pass; McClelland-Mok's
  "declined but still above men" characterization is the corroborated statement.]`
- Hours-inclusive elasticities, not pure extensive-margin participation elasticities; the
  project's `eps_ext` is participation-only, so magnitudes transfer qualitatively.

## Validated BibTeX (DOI content negotiation)
```bibtex
@article{Blau_2007,
  title   = {Changes in the Labor Supply Behavior of Married Women: 1980--2000},
  volume  = {25},
  ISSN    = {1537-5307},
  url     = {http://dx.doi.org/10.1086/513416},
  DOI     = {10.1086/513416},
  number  = {3},
  journal = {Journal of Labor Economics},
  publisher = {University of Chicago Press},
  author  = {Blau, Francine D. and Kahn, Lawrence M.},
  year    = {2007},
  month   = {July},
  pages   = {393--438}
}
```
DOI resolves; author/year/title/venue/pages match.
