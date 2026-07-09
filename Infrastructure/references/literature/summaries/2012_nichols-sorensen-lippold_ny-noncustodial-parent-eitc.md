# Nichols, Sorensen & Lippold (2012) — The New York Noncustodial Parent EITC: Its Impact on Child Support Payments and Employment

- **Tier:** 2 (Urban Institute research report; regression-discontinuity evaluation of a
  real state tax-credit program, not a peer-reviewed journal article)
- **Type:** paper
- **DOI:** `[unverified: Urban Institute report, no DOI issued]`
- **Source:** https://www.urban.org/research/publication/new-york-noncustodial-parent-eitc-its-impact-child-support-payments-and-employment
- **Thread:** 6 (EITC-design-decomposition — household-composition/childless-worker channel)
- **Evidence class:** Measured/ex-post — regression discontinuity (RD), exploiting the drop
  in eligibility when a noncustodial parent's youngest child turns 18.

## Finding (paraphrased)
New York State enacted a noncustodial-parent EITC (NCP EITC) in 2006 specifically to reach
low-income parents who are excluded from the standard federal and state EITC because their
child does not reside with them for more than half the year — the exact custody/residency-
based categorical exclusion the user's hypothesis is about, distinct from the childless-
credit-generosity channel. Using a regression-discontinuity design around the age-18 cutoff
that ends NCP EITC eligibility, the study finds the credit **increased the proportion of
noncustodial parents paying their child support obligation in full by approximately one
percentage point**, with the effect concentrated among parents with lower child-support
orders. `[unverified: the study's abstract and title indicate it also examines employment
impacts, but the specific employment point estimate was not retrieved in readable form this
pass — the primary PDF returned unreadable binary content on WebFetch, and available
secondary summaries described the child-support finding in detail but not the employment
coefficient. This should be treated as an open item, not assumed to be null or positive,
until the primary report table is read directly.]` The authors note their estimates may
represent upper-bound impacts, reflecting only the program's first four years, and that
program take-up was low (5,280 recipients, about $2 million in credits in the first year),
which the report attributes to limited awareness rather than program design.

## Why this matters for the household-composition-channel question
This is a genuine, if narrow, natural experiment in exactly the mechanism the user
describes: New York created a credit specifically to reach a categorically excluded
population (noncustodial parents), and a credible RD design finds a real behavioral
response (on child-support compliance, robustly) for that population. It is the closest
state-level analog to what the 80-80 would do nationally by not conditioning on custody at
all. Two things temper how far this can be extended:
1. The confirmed, credible result is on **child-support compliance**, not employment — a
   related but distinct outcome. A parent who was already working can pay more child
   support without any change in employment status; the paper's title suggests an
   employment analysis exists, but this pass could not verify its direction or magnitude.
2. Very low take-up (5,280 recipients) limits the population-level relevance and this
   study's power to detect an employment effect even if one exists.

## Caveats
- `[unverified: employment point estimate — see above. Do not cite this paper as evidence
  of a positive OR null employment effect until the primary table is confirmed.]`
- Low program take-up in the sample period reduces external validity for a nationally
  scaled, near-automatic subsidy like the 80-80.
- New York-specific state tax and child-support-enforcement institutional context; the
  interaction with the state's child-support enforcement apparatus (order size, enforcement
  intensity) may be a scope condition for the compliance result that would not carry over to
  a subsidy with no child-support-linkage mechanism at all.

## BibTeX
```bibtex
@techreport{Nichols_2012_NY_NCP_EITC,
  title       = {The New York Noncustodial Parent EITC: Its Impact on Child Support Payments and Employment},
  institution = {Urban Institute},
  author      = {Nichols, Austin and Sorensen, Elaine and Lippold, Kye},
  year        = {2012},
  month       = {July},
  url         = {https://www.urban.org/research/publication/new-york-noncustodial-parent-eitc-its-impact-child-support-payments-and-employment}
}
```
Author list, year, and title confirmed via direct WebFetch of the Urban Institute
publication landing page (high confidence). `[unverified: no DOI/registered identifier
exists for this report.]`
