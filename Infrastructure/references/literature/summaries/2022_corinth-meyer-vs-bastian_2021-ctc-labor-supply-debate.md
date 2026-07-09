# The 2021 Child Tax Credit Labor-Supply Debate (Corinth, Meyer et al. vs. Bastian; Jones & Michelmore; Schanzenbach & Strain)

- **Tier:** 1 mixed (NBER working papers; AEA P&P) with Tier 3 commentary.
- **Type:** paper
- **Thread:** A (the live ex-ante vs. ex-post conflict on a near-universal transfer).
- **Evidence class:** MIXED — explicitly contrast modeled (ex-ante) vs. measured (ex-post).

## The conflict (paraphrased)
- **Corinth, Meyer, Stadnicki & Wu (2021, NBER w29366)** — *modeled / ex-ante*
  microsimulation. Replacing the CTC with an unconditional child allowance (removing the
  work incentive by paying full credit regardless of work) would reduce parental
  employment by ~**1.5 million**, using an assumed extensive-margin elasticity of **0.75**.
  (DOI 10.3386/w29366; published 2024 in *AEA Papers and Proceedings* / related outlets.)
- **Bastian (2024)** — *modeled / ex-ante* with a menu of elasticities. Preferred estimate:
  ~**367,000** parents stop working, an order of magnitude smaller than Corinth et al.,
  driven mostly by the smaller assumed elasticity. Published *National Tax Journal* 77(2):
  263–311 (June 2024); DOI 10.1086/728703. (Circulated earlier as a 2022 working paper.)
- **Ananat, Glasner, Hamilton & Parolin (2022, NBER w29823)** — *measured / ex-post*
  CPS/real-world evidence from the April–December 2021 monthly payments found **no clear
  reduction** in parental employment during the period the credit was paid. (DOI
  10.3386/w29823.) Corroborated by Schanzenbach & Strain and Jones & Michelmore.

## Conflict note (central)
The disagreement is almost entirely about the **assumed extensive-margin elasticity**
and modeled vs. measured method — the same fault line as Kleven (2024) vs. the EITC
consensus. The headline employment-loss number is a near-linear function of the chosen
elasticity.

## CORRECTION (prior scout misattribution — resolved this pass)
The prior entry attributed **NBER w29823** to Corinth/Meyer (the ex-ante microsimulation).
That is wrong. Validated via DOI content negotiation:
- **w29823 = Ananat, Glasner, Hamilton & Parolin (2022)**, "Effects of the Expanded Child
  Tax Credit on Employment Outcomes: Evidence from Real-World Data from April to December
  2021" — the *ex-post* side of the debate. DOI 10.3386/w29823.
- **w29366 = Corinth, Meyer, Stadnicki & Wu (2021)**, "The Anti-Poverty, Targeting, and
  Labor Supply Effects of Replacing a Child Tax Credit with a Child Allowance" — the
  *ex-ante* microsimulation carrying the 1.5M-job-loss / elasticity-0.75 result. DOI
  10.3386/w29366.
The catalog `source_url` has been corrected accordingly.

## Bibliographic details (validated via DOI content negotiation)
- Corinth et al.: NBER w29366 (2021), DOI 10.3386/w29366. Authors Kevin Corinth, Bruce
  Meyer, Matthew Stadnicki, Derek Wu — confirmed.
- Bastian: *National Tax Journal* 77(2): 263–311 (2024), DOI 10.1086/728703. Author Jacob
  Bastian — confirmed. Preferred-case figure ~367,000 parents — confirmed from abstract.
- Ananat et al.: NBER w29823 (2022), DOI 10.3386/w29823 — confirmed.

`[unverified: Schanzenbach & Strain and Jones & Michelmore exact NBER numbers/DOIs not
individually validated this pass — they enter only as corroborating ex-post citations, not
as load-bearing entries. Confirm before formal citation.]`

## BibTeX (validated via DOI content negotiation)
```bibtex
@techreport{Corinth_2021,
  title={The Anti-Poverty, Targeting, and Labor Supply Effects of Replacing a Child Tax Credit with a Child Allowance},
  url={http://dx.doi.org/10.3386/w29366},
  DOI={10.3386/w29366},
  institution={National Bureau of Economic Research},
  type={NBER Working Paper}, number={29366},
  author={Corinth, Kevin and Meyer, Bruce and Stadnicki, Matthew and Wu, Derek},
  year={2021}, month=Oct
}

@article{Bastian_2024,
  title={How Would a Permanent 2021 Child Tax Credit Expansion Affect Poverty and Employment?},
  volume={77}, ISSN={1944-7477},
  url={http://dx.doi.org/10.1086/728703}, DOI={10.1086/728703},
  number={2}, journal={National Tax Journal},
  publisher={University of Chicago Press},
  author={Bastian, Jacob}, year={2024}, month=June, pages={263--311}
}

@techreport{Ananat_2022,
  title={Effects of the Expanded Child Tax Credit on Employment Outcomes: Evidence from Real-World Data from April to December 2021},
  url={http://dx.doi.org/10.3386/w29823},
  DOI={10.3386/w29823},
  institution={National Bureau of Economic Research},
  type={NBER Working Paper}, number={29823},
  author={Ananat, Elizabeth and Glasner, Benjamin and Hamilton, Christal and Parolin, Zachary},
  year={2022}, month=Mar
}
```

## Why it matters for 80-80 (critical)
This is the most direct modern case study of exactly the modeling choice the 80-80
faces: how a chosen labor-supply elasticity drives the headline behavioral-cost number,
and how ex-ante simulations diverge from ex-post measurement. The 80-80 model should
present an elasticity sensitivity band and an explicit modeled-vs-measured caveat.
