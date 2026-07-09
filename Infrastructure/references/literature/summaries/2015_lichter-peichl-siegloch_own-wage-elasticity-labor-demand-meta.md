# Lichter, Peichl & Siegloch (2015) — The Own-Wage Elasticity of Labor Demand: A Meta-Regression Analysis

- **Tier:** 1 (European Economic Review)
- **Type:** paper
- **DOI:** 10.1016/j.euroecorev.2015.08.007
- **Source:** https://www.sciencedirect.com/science/article/abs/pii/S0014292115001233 ; IZA DP 7958 (https://docs.iza.org/dp7958.pdf)
- **Thread:** B angle 3 (incidence & wage pass-through) — parameterizes the labor-DEMAND elasticity that governs how a wage-subsidy-induced supply shift splits between wages and employment.
- **Evidence class:** Meta-analysis of measured (ex-post) estimates; the synthesis itself is a statistical aggregation, not a single new measurement.

## Finding (paraphrased)
Comprehensive meta-regression of the labor-demand literature: **942 own-wage labor-demand
elasticity estimates from 105 studies**. Headline distribution of collected estimates:
**mean −0.508, median −0.386** (SD 0.774). Model specification and data choices explain
>80% of the across-study variation. After conditioning on a benchmark/best-practice
specification and correcting for publication selection, the authors land on a consensus
own-wage labor-demand elasticity of **about −0.3** — i.e., a 10% wage increase lowers
labor demanded by roughly 3% (inelastic).

Key heterogeneity for the 80-80:
- **Demand is MORE elastic (more negative) for low-skilled and "atypical"/marginal
  workers** than for the average worker — exactly the population a low-wage fill targets.
- **Long-run > short-run** in absolute value (adjustment costs damp the short-run response).
- **Publication selection bias is present and upward (in absolute value):** larger-magnitude
  elasticities are over-represented in print, so **bias-corrected estimates are SMALLER in
  absolute value** than the raw mean/median. This is why the −0.3 consensus sits well below
  the raw −0.508 mean.

## Why it matters for 80-80 (incidence module)
The 80-80 is a worker-side wage fill, but if it induces entry/hours it shifts low-skill
labor supply outward; how far the equilibrium wage falls (and thus how much leaks to
employers — the Rothstein channel) depends on the **own-wage labor-demand elasticity**.
This meta-analysis is the magnitude anchor: central ≈ −0.3, with a more elastic (more
negative) value appropriate for a low-skill pool, and the publication-bias correction
arguing AGAINST using the larger raw estimates as the central case.

## Verified vs. flagged
- Mean −0.508 / median −0.386, 942 estimates / 105 studies: corroborated across the IZA
  working paper, RePEc/EconPapers, and the journal abstract.
- ~−0.3 bias-corrected consensus, more-elastic-for-low-skilled, long-run > short-run,
  upward publication selection: corroborated via the IZA DP text and multiple summaries.
- `[unverified: the authors' single preferred point estimate after the full benchmark +
  selection correction (variously summarized near −0.25 to −0.3) could not be pinned to an
  exact figure this pass — ScienceDirect returns HTTP 403. Use "about −0.3" as the
  reported consensus, not a quoted point estimate.]`

## Validated BibTeX
```bibtex
@article{Lichter_2015,
  title   = {The own-wage elasticity of labor demand: A meta-regression analysis},
  volume  = {80},
  ISSN    = {0014-2921},
  DOI     = {10.1016/j.euroecorev.2015.08.007},
  journal = {European Economic Review},
  publisher = {Elsevier BV},
  author  = {Lichter, Andreas and Peichl, Andreas and Siegloch, Sebastian},
  year    = {2015},
  month   = {Nov},
  pages   = {94--119}
}
```
DOI content negotiation resolved; author/year/title/venue/pages match the journal record.
