# Krueger & Mueller (2016) — A Contribution to the Empirics of Reservation Wages

- **Tier:** 1 (American Economic Journal: Economic Policy)
- **Type:** paper
- **DOI:** 10.1257/pol.20140211
- **Source:** https://www.aeaweb.org/articles?id=10.1257/pol.20140211 ; AEJ: Economic Policy 8(1):142-179
- **Thread:** 4 (reservation-wage determinants and levels — for calibrating r_i).
- **Evidence class:** Measured (ex-post). High-frequency longitudinal survey of unemployed workers (New Jersey).

## Finding (paraphrased)
Tracks reservation wages of unemployed workers at high frequency over the spell. Main
empirical findings:
- Reservation wages **start high relative to a calibrated search model's prediction and
  decline only slowly** over the unemployment spell — far less than standard theory implies.
- Workers appear to **anchor their reservation wage on their previous wage**; the prior
  wage is a strong predictor of the reservation wage. Reservation wages measured in earlier
  interviews predict subsequent job acceptance.
- The slow decline and prior-wage anchoring are interpreted as workers persistently
  misjudging prospects rather than optimally updating.

## Why it matters for 80-80 (Thread 4 core)
Directly informs how to **calibrate the value of non-employment / reservation wage r_i
from observable characteristics**. The central empirical lesson — reservation wages anchor
near the prior wage and adjust sluggishly — supports parameterizing r_i as a function of a
worker's recent/prior earnings (a high share of the prior wage), rather than from UI
generosity alone. This is the empirical bridge from observed characteristics to the
structural object r in the surplus condition y - r.

## Verified vs. flagged
- DOI 10.1257/pol.20140211 resolves to "A Contribution to the Empirics of Reservation
  Wages," AEJ: Economic Policy 8(1):142-179, Krueger & Mueller, 2016; all fields match.
- Anchoring-on-prior-wage and slow-decline findings confirmed against the AEA abstract.
- ~~`[unverified: the precise reservation-wage-to-prior-wage ratio ... not pinned]`~~
  **Resolved 2026-07-09** — see addendum below.

## Primary-source addendum (2026-07-09): ratio numbers pinned from NBER w19870 full text

NBER WP 19870 (the working-paper version) downloaded from nber.org and read directly.

- **Level of the reservation wage: essentially 100 percent of the previous wage at entry.**
  Table 2 / Section 5: "Across all durations, the reservation wage ratio is essentially
  equal to the previous wage, on average, in both samples" (their NJ survey and Feldstein
  & Poterba's 1976 CPS sample, which found it slightly *above* the prior wage). Table A
  entries cluster ~0.97-1.09.
- **Decline over the spell: 0.05-0.14 percent per week** of unemployment (longitudinal
  fixed-effects estimates) — even slower than Feldstein-Poterba's cross-section, which
  shows a ratio only ~10pp lower at 50+ weeks than at <5 weeks.
- **Calibrated optimal benchmark: ~0.75 falling to ~0.66** over 99 weeks (their search-model
  calibration with UI at 60 percent of prior wage). Measured reservation wages thus start
  ~25-35 percent ABOVE the optimizing-model level and barely fall.
- **Accepted wages: ~0.90** — the ratio of the accepted reemployment weekly wage to the
  pre-unemployment wage is 0.90 for respondents (0.92 sample frame), i.e., actual accepted
  offers sit ~10 percent below the prior wage while *stated* reservation wages sit at it.
- Interpretation the authors favor: anchoring on the prior wage / persistent
  overconfidence, not fully rational updating.

**80-80 implication (Q1, entry-margin reality-anchoring pass):** for the *unemployed*, the
measured reservation wage is ~1.0x the own prior wage — high relative to offers (which are
~0.9x and falling with duration per Schmieder et al. 2016, now cataloged), but nothing like
double-digit multiples of the net gain from working. No comparable direct measurement
exists for the NILF population; KM's sample is UI recipients. Very large calibrated markups
for NILF groups therefore cannot be validated OR refuted by direct reservation-wage
measurement — they are the model's residual, and Hall-Mueller (2018, now cataloged) shows
such residuals bundle nonwage job values and non-work option values (health, caregiving,
benefits) rather than a literal wage demand.

## Validated BibTeX
```bibtex
@article{Krueger_2016,
  title   = {A Contribution to the Empirics of Reservation Wages},
  volume  = {8},
  ISSN    = {1945-774X},
  DOI     = {10.1257/pol.20140211},
  number  = {1},
  journal = {American Economic Journal: Economic Policy},
  publisher = {American Economic Association},
  author  = {Krueger, Alan B. and Mueller, Andreas I.},
  year    = {2016},
  month   = {Feb},
  pages   = {142--179}
}
```
DOI content negotiation resolved; author/year/title/venue/pages match.
