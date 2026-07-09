# CBO (2012) — Effective Marginal Tax Rates for Low- and Moderate-Income Workers

- **Tier:** 2 (official government economic research, CBO Publication 43709)
- **Type:** technical_note
- **DOI:** none (CBO report; no DOI assigned)
- **Source:** https://www.cbo.gov/publication/43709 (site blocks automated fetch, HTTP 403
  confirmed this pass — consistent with the existing catalog's notes on other CBO PDFs);
  companion summary at https://www.cbo.gov/publication/43710
- **Thread:** 6 (EITC-design-decomposition — re-verifying the "CBO effective-marginal-
  tax-rate work" referenced generically in `00_config.py` comments)
- **Evidence class:** Modeled — CBO's own tax/benefit microsimulation of statutory and
  phase-out schedules facing low- and moderate-income workers.

## Finding (paraphrased, corroborated via CBO's own public summary and secondary coverage)
Published November 2012, this is the report specifically about **effective marginal tax
rates (EMTRs)** — distinct from the labor-supply-elasticity working papers (McClelland &
Mok 2012-12, pub 43675; the dynamic-scoring methodology notes, pubs 43674/43680) already
in this catalog. It computes the combined marginal rate low- and moderate-income workers
face from federal income tax, federal payroll tax, state income tax, and the phase-out of
means-tested transfers (SNAP, and by extension programs with similar phase-out structure).
Headline finding: EMTRs for this population average **about 30 percent**, with roughly a
third from the federal income tax (importantly, **the EITC's own phase-out is a
significant driver of elevated EMTRs in specific income ranges** for the credit's target
population), more than a third from payroll taxes, and the remainder from state taxes and
transfer phase-outs. EMTRs vary substantially by marital status and presence of children
because the EITC and other credits are structured around family composition.

## Why this matters for the decomposition question (directly on point)
This is the primary official-source evidence for the project's own articles' claim that
the EITC's **phase-out creates a "cliff"-like elevated effective marginal tax rate** —
the precise mechanism the 80-80 is designed to avoid by construction (a flat 80 percent
fill rate with no phase-out range in the wage-subsidy formula itself, though the worker
still faces the ambient tax-and-transfer system's own EMTR on top of it). It is important
to disclose that the CBO's own report also documents that a large share of the elevated
EMTR facing low-income workers comes from the **general** tax-and-transfer system (payroll
tax, SNAP phase-out, state income tax) and not from the EITC's phase-out alone — so a wage
subsidy that avoids its own internal cliff does **not** exempt a worker from the ambient
EMTR of the rest of the system (a point directly relevant to Requirement M5's push toward
net-of-tax-and-transfer income, since the PolicyEngine schedules already used in this
project's `individual_schedules` output should already reflect this ambient EMTR
regardless of the wage-subsidy formula's own shape).

## Verified vs. flagged
- Report identity (CBO Publication 43709, "Effective Marginal Tax Rates for Low- and
  Moderate-Income Workers," November 2012) corroborated via the CBO publication landing
  page metadata (title, publication number, and release framing found via WebSearch) and
  the companion CBO blog summary (pub 43710). This is the correct, distinct CBO citation
  for "EMTR work," as opposed to the labor-supply-elasticity or dynamic-scoring CBO
  publications already cataloged.
- `[unverified: the exact ~30 percent average EMTR figure and its component breakdown
  (roughly a third federal income tax, more than a third payroll tax, remainder state tax
  plus SNAP phase-out) were read from a WebSearch-generated summary of the report, not
  the primary PDF — cbo.gov returned HTTP 403 to direct fetch this pass, consistent with
  prior sessions' notes on CBO PDF access. Confirm against the primary PDF
  (11-15-2012-MarginalTaxRates.pdf) before using these figures as a formally cited number
  in a public-facing brief.]`

## No BibTeX (government report, no DOI)
```bibtex
@techreport{CBO_2012_EMTR,
  title        = {Effective Marginal Tax Rates for Low- and Moderate-Income Workers},
  institution  = {Congressional Budget Office},
  type         = {CBO Publication},
  number       = {43709},
  year         = {2012},
  month        = {Nov},
  note         = {No DOI assigned; PDF access returned HTTP 403 to automated fetch this pass}
}
```
