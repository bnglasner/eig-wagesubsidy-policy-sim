# Stancanelli (2008) — Evaluating the Impact of the French Tax Credit on the Employment Rate of Women

- **Tier:** 1 (Journal of Public Economics)
- **Type:** paper
- **DOI:** 10.1016/j.jpubeco.2008.02.007
- **Source:** https://www.sciencedirect.com/science/article/abs/pii/S004727270800039X ; OFCE
  working-paper version WP2004-07
- **Thread:** 6 (EITC-design-decomposition — European in-work-benefit evidence structured
  differently from the EITC's annual credit)
- **Evidence class:** Measured/ex-post — quasi-experimental, French Labour Force Survey 1999-2005.

## Finding (paraphrased)
Evaluates France's **Prime pour l'Emploi (PPE)**, introduced in 2001 and reformed in 2004
to be payable in advance rather than only as an annual year-end credit — itself an
instructive natural experiment in payment timing. Unlike the EITC, French tax credits of
this era were assessed against **household (joint) income**, not individual earnings.
Central findings, by household type:
- **Married women: a significant NEGATIVE employment effect** (roughly 3.2-3.4 percentage
  points lower employment rate after the credit's introduction) — the credit's household
  income test creates a disincentive for a second earner once the primary earner's income
  already qualifies the household, or pushes the household past the relevant income
  threshold.
- **Cohabiting women:** positive but only weakly significant effect.
- **Lone mothers:** positive but statistically insignificant effect.

## Why this matters for the decomposition question
This is exactly the kind of non-EITC, differently-structured in-work-benefit evidence the
project needs to isolate design channels: PPE is **not** an EITC clone (household income
test vs. the EITC's family-structure-based but individually-filed test; the 2004 reform
even moved toward more frequent/advance payment, a partial salience experiment in itself),
and it still produces a **negative** participation effect for a specific household type.
This directly supports the project's own emphasis (Requirement M5, the net-of-household-
income reservation-wage framing) that **household-level income testing, not just annual
timing or categorical eligibility, is an independent design lever** that can suppress
participation regardless of how "EITC-like" or "wage-subsidy-like" the instrument is. It
pairs with Blundell, Duncan, McCrae & Meghir (2000, already cataloged) on the UK WFTC,
which finds the same qualitative pattern (single-parent/primary-earner gains partly offset
by second-earner disincentives under a joint income test) — two independent European
programs, two different credit designs, the same household-testing mechanism producing a
negative or muted extensive-margin effect for a subset of the eligible population.

## Caveats
- French labor-market and family-taxation context (quotient familial, joint filing norms)
  differs from the largely individual-based U.S. tax/benefit system the 80-80 operates in;
  the household-income-test mechanism is the transportable lesson, not the point magnitude.
- Reduced-form employment-rate comparison across LFS waves with a break in the series in
  2003 requiring separate 1999-2002 and 2003-05 analysis; identification relies on
  before/after variation around the 2001 introduction and 2004 reform, not a randomized or
  sharp discontinuity design.
- The 80-80, as an individually-filed wage fill (not household-income-tested), is
  structurally different from PPE on exactly this dimension — this paper is evidence about
  what would happen if the 80-80 *were* household-tested, i.e., a caution about a design
  choice the project has (per PROJECT.md) not made, not a direct forecast for the 80-80 as
  specified.

## 2026-07-08 addendum — assessment structure re-verified (other_women band pass)
Abstract re-read this pass (via RePEc/ScienceDirect metadata): the PPE is computed on
**individual earnings** but with **"conditioning on total household resources"** — an
eligibility ceiling on family income, not a household-based credit amount. This refines
the summary above, which loosely described the credit as "assessed against household
(joint) income." The abstract's own group contrast is the paper's most valuable feature
for the 80-80:
- **Married women** (jointly taxed; household conditioning bites): employment effect
  **negative, roughly three percentage points** — the abstract attributes this to the
  household-resources condition.
- **Cohabiting women** (taxed as individuals in France; household conditioning effectively
  absent): employment effect **positive** — the abstract describes it as larger in
  magnitude ("twice as large") than the married-women effect. `[unverified: the exact
  cohabiting-women point estimate and its significance level not read from the paywalled
  full text; the original summary's "weakly significant" characterization and this pass's
  "twice as large" phrasing both come from abstract-level sources and should be reconciled
  against the paper's tables before quantitative use.]`
This within-paper contrast is the closest thing in the catalog to a direct test of
individual vs. household assessment holding the instrument fixed: when the household test
does not bite, a worker-side earnings credit RAISES partnered women's employment. That is
the design cell the 80-80 occupies for the entire `other_women` population.

## Validated BibTeX
```bibtex
@article{Stancanelli_2008,
  title   = {Evaluating the impact of the French tax credit on the employment rate of women},
  volume  = {92},
  ISSN    = {0047-2727},
  url     = {http://dx.doi.org/10.1016/j.jpubeco.2008.02.007},
  DOI     = {10.1016/j.jpubeco.2008.02.007},
  number  = {10-11},
  journal = {Journal of Public Economics},
  publisher = {Elsevier BV},
  author  = {Stancanelli, Elena G.F.},
  year    = {2008},
  month   = {Oct},
  pages   = {2036--2047}
}
```
DOI content negotiation resolved; author/year/title/venue/pages match.
