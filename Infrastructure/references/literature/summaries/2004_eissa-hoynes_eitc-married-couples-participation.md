# Eissa & Hoynes (2004) — Taxes and the Labor Market Participation of Married Couples: The Earned Income Tax Credit

- **Tier:** 1 (Journal of Public Economics)
- **Type:** paper
- **DOI:** 10.1016/j.jpubeco.2003.09.005
- **Source:** https://www.sciencedirect.com/science/article/abs/pii/S0047272703001440 ;
  working-paper version NBER w6856 ("The Earned Income Tax Credit and the Labor Supply of
  Married Couples"); companion review Eissa & Hoynes NBER w11729 ("Behavioral Responses to
  Taxes: Lessons from the EITC and Labor Supply"), read directly this pass.
- **Thread:** 6 (EITC-design-decomposition — the canonical secondary-earner /
  married-women evidence; anchors the `other_women` band question)
- **Evidence class:** Measured/ex-post — difference-in-differences (married mothers vs.
  married women without children, CPS) plus a reduced-form participation model in net
  after-tax gains to entering work.

## Finding (verified against primary/near-primary sources)
The canonical result that the EITC **reduced married women's labor-force participation**:

- NBER w6856 abstract (read directly): "EITC expansions between 1984 and 1996 increased
  married men's labor force participation only slightly but reduced married women's labor
  force participation **by over a full percentage point**;" family labor supply and pre-tax
  family earnings **fell** among married couples. The authors' own summary: "the EITC is
  effectively subsidizing married mothers to stay at home."
- Eissa & Hoynes w11729, p. 15 (read directly): the DiD comparing married mothers to
  married women without children finds "the 1993 EITC expansion led to a **one percentage
  point reduction** in the participation rate of married mothers;" the reduced-form model
  finds "the expansions in the EITC between 1984 and 1996 led to about a **one percentage
  point reduction** in the employment of married mothers" (similar to, somewhat smaller
  than, the DiD). Consistent with Ellwood (2000).
- Hours (from the companion chapter, Eissa & Hoynes, *Tax Policy and Labor Market
  Performance*, described in w11729 p. 15): 1984-96 EITC expansions led to a small **1-4
  percent decrease in annual hours** of working married women with children. Heim (2005,
  structural) finds similar hours impacts but **no** employment effect for married women —
  a within-literature conflict on the participation margin worth carrying.

## The mechanism — and which half transfers to the 80-80
The EITC is assessed on **household** income. A married woman whose husband's earnings
already place the family on the credit's plateau or phase-out faces a positive
participation tax on her *first* dollar of earnings: her entry raises household income and
*phases the credit out*. Two distinct channels are bundled in the measured ~1pp decline:

1. **Household-income phase-out channel (does NOT apply to the 80-80).** The subsidy
   itself is withdrawn as the second earner's income comes in. The 80-80 is assessed on the
   *individual worker's own wage*, so a married woman's eligibility and subsidy amount are
   untouched by her husband's earnings. This — the dominant, design-specific channel behind
   Eissa-Hoynes' negative result — is structurally absent from the 80-80.
2. **Household income effect / intra-household coordination channel (DOES apply).** When
   one partner's take-home pay rises (here via the husband's EITC on the plateau; under the
   80-80 via a partner's wage fill), the other partner's participation can fall through an
   ordinary income effect on household labor supply. This is the same channel Bonin, Kempe
   & Schneider (2003, cataloged) find under a **non-categorical, individually-assessed**
   German Kombilohn (higher-earning partners reduce labor supply once the subsidized
   partner secures the household income floor). Eissa-Hoynes cannot separate the two
   channels — but the PPE contrast (Stancanelli 2008, cataloged: negative only where
   household conditioning bites, positive for individually-taxed cohabiting women) and
   Kombilohn (income-effect channel alone produces a much smaller, but nonzero, negative
   drag) bracket them.

## Why it matters for the `other_women` band
This is the single most-cited piece of evidence that a work subsidy can push a
secondary-earner cell's participation **down**, not up. Read correctly for the 80-80: the
big negative (phase-out) channel is designed out; the residual income-effect channel is
real but second-order. It justifies a *wider-downward* band for `other_women` (lower bound
at or slightly below the EITC/CBO default), NOT a negative central value.

## Caveats
- Identification is DiD around EITC expansions; Kleven (2024, cataloged) shows extensive-
  margin EITC estimates are specification-sensitive, which cuts in both directions here.
- The treated population is married *mothers* (children required for the credit); the
  project's `other_women` cell also contains married childless women and single childless
  women, for whom this evidence is indirect.
- 1984-96 U.S. context; Blau & Kahn (2007, cataloged) show married women's labor-supply
  elasticities fell sharply toward men's levels by 2000, so both the positive own-wage and
  negative cross/income responses are likely smaller today.

## Validated BibTeX (DOI content negotiation)
```bibtex
@article{Eissa_2004,
  title   = {Taxes and the labor market participation of married couples: the earned income tax credit},
  volume  = {88},
  ISSN    = {0047-2727},
  url     = {http://dx.doi.org/10.1016/j.jpubeco.2003.09.005},
  DOI     = {10.1016/j.jpubeco.2003.09.005},
  number  = {9-10},
  journal = {Journal of Public Economics},
  publisher = {Elsevier BV},
  author  = {Eissa, Nada and Hoynes, Hilary Williamson},
  year    = {2004},
  month   = {Aug},
  pages   = {1931--1958}
}
```
DOI resolves; author/year/title/venue/pages match the Crossref record (343 citations
indexed). Headline magnitudes cross-checked against two Eissa-Hoynes-authored sources
(w6856 abstract; w11729 full text pp. 12-16). `[unverified: the published JPubE tables'
exact point estimates and standard errors not read from the paywalled journal text; the
"~1pp" magnitude is the authors' own characterization in both NBER companions.]`
