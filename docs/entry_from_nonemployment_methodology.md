# Entry from Non-Employment: Methodology, Band Provenance, and Disclosures

> **Revision 2026-07-09 (survey-weighted estimation + full-review fixes — HEADLINE REBASE, user sign-off).**
> A `/full-review` + `/review-style` pass on the re-centered drafts drove three changes. (MR-001)
> The Heckman estimation is now **survey-weighted as primary**: the selection probit by WTFINL
> (population participation) and the wage OLS by EARNWT (ORG earnings weight), per the project weight
> convention and dataset registry; unweighted estimation is retained as a robustness (it targets the
> same conditional mean and is consistent/efficient there — Solon-Haider-Wooldridge 2015; weighted vs
> unweighted conditional pool median $18.91 vs $20.10). The weighted pool is poorer (median MPL
> $18.28→$17.18; below-target 41.4%→47.8%), lifting the headline. **New headline: evidence-central
> 1.48M** (floor 1.02M; high 3.80M; full 27-cell grid 0.23–3.80M); by group sm 0.24 / ow 1.06 /
> men 0.18; entrant gross $8.5B / net $6.2B; composition ~33% unemployed / ~3% disabled+retired; mean
> hours ≈976; clawback medians (evc pool) 19/27/24%; cliff ~1 in 9; rigid-central $94.4B/$75.2B; all-
> renegotiate bound $161.7B. (MR-006/CC-003/AS-002) PI-3 `entrant_hours_sensitivity` and the
> coordination/take-up stress tests are now computed on the **evidence-central pool** in 02g
> (`entry_central_stress.parquet`; marginal $/job rank $5,731 → independent $10,261). Full-review
> verdict: no fabrications, no correctness bugs, all headline numbers reproduce; residual leftovers
> (appendix §5 "0.83M central", stale clawback, Fig 14 caption, footnote-8 KM attribution) fixed.
>
> **Revision 2026-07-09 (headline re-center + scenario grid + PI-3 — superseded by the weighting rebase above).**
> A holistic evaluation (`Infrastructure/explorations/2026-07-09_holistic-eval/`) found the 0.83M
> headline was a THREE-WAY conservative floor (non-employment penalty 0, offer-dispersion λ 0.75,
> accepted-wage σ truncation) presented as a neutral central, with the uncertainty shown one axis
> at a time (hiding the super-additive joint envelope). Decisions (user): (Q1) **re-center** — new
> headline is the **evidence-central 1.25M**, which corrects the one non-neutral choice with a
> STATUS-DIFFERENTIATED non-employment penalty (`unemployed:0.05, nilf_other:0.10, disabled:0.15,
> retired:0.15`, pool-weighted mean ≈10-11%), λ 0.75 retained; the **0.83M** floor (penalty 0) is
> kept as a LABELED conservative anchor; a **3.37M** high joint corner (penalty 20% × λ 1.0 × upper
> eps) tops the range. (Q2) **scenario grid + full decomposition** — new
> `code/02_descriptive_analysis/02g_entry_scenario_grid.py` writes `entry_scenario_grid.parquet`
> (27 cells = penalty {0,10,20%} × λ {0.5,0.75,1.0} × eps {lower,central,upper}; full range
> **0.18–3.37M**) and `entry_headline_scenarios.parquet` (the 3 bundles). (Q3) **PI-3** — 02d writes
> `entrant_hours_sensitivity.parquet` (rank / independent / median hours mappings): the rank map's
> low marginal cost per entrant ($4,018 gross / floor) roughly doubles under an independent draw
> ($9,576) — HIGH for the marginal-cost/FTE story, LOW for the fiscal total. Evidence-central:
> entrants 1.25M (sm 0.20 / ow 0.91 / men 0.14), gross $6.4B / net $4.5B, composition ~33%
> unemployed / ~3% disabled+retired, mean hours ≈910, clawback medians 15/23/21%. Deferred as
> DISCLOSED limitations only (not modeled, per Q3): incumbent hours-margin net basis, UI/SSDI in
> NI(0), fixed cost of work. Canonical pool unchanged (01h untouched; determinism preserved). Plan:
> `Infrastructure/plans/2026-07-09_entry-model-recenter-implementation.md` (APPROVED). The
> two-sided-bias framing (MPL conservatism vs frictionless-matching/fixed-cost/UI upward biases) is
> now the headline's honest qualifier; do not present 1.25M as precise — it is the center of a
> two-sided range.
>
> **Revision 2026-07-09 (reality assessment):** four changes landed after the entry-model
> reality assessment (`Infrastructure/explorations/2026-07-09_entry-model-reality-assessment.md`):
> (1) **Paid-hourly wage frame (E2)** — the MPL equation is now estimated on paid-hourly earners
> only (the market the $16.80 target prices; previously all earners incl. 44% salaried, which
> inflated the selection correction: ρσ +0.297 → +0.075 on the clean frame and the imputation
> variants converged, resolving the MR-001 band's 7× spread as frame contamination).
> (2) **Status-aware entry lottery (E1)** — per-person markups scale with prior-status weights
> (unemployed 5.0 / NILF-other 1.0 / disabled 0.15 / retired 0.15; CPS U→E vs N→E flow ratios,
> MMS 2013) × the selection-probit propensity, normalized to mean 1 within cell×reachable, so
> calibrated totals are unchanged but entrants are labor-market-proximate (unemployed now 35%
> of entrants, disabled+retired ~1%; previously 9.4% and 12.6%).
> (3) **Non-employment wage-penalty band (E2 follow-on)** — the weakly-identified selection
> correction cannot detect unobserved offer decay, so 02f runs an explicit {0, 10%, 20%} MPL
> penalty anchored to Schmieder-von Wachter-Bender (2016, ~0.8%/month) and Krueger-Mueller
> (2016, accepted ≈ 0.90× prior). This is now the dominant MPL uncertainty axis
> (entry 0.46M → 0.71M → 1.18M).
> (4) **Incumbent intensive margin (E5)** — `incumbent_hours_margin.parquet` reports added
> hours/FTE/cost for eligible incumbents below 40 hrs/wk over `eps_int_band` {0.05/0.20/0.33};
> the EITC's hours null is a phase-out design artifact the 80-80 does not share. In FTE terms
> the central hours margin (0.25M) exceeds the entry margin (~0.17M).
> Headline entry: **0.46M central** (eps band 0.13–0.85M; penalty band to 1.18M; take-up 0.80
> scalar 0.37M). The calibrated markups are **entry-resistance residuals** (nonwage job values,
> health, benefit interactions — Hall-Mueller 2018), not measured reservation wages; no direct
> reservation-wage measurement exists for NILF adults.
>
> **(6) Offer dispersion folded into the headline (2026-07-09, latest — HEADLINE REBASE).**
> Mean imputation made reachability a deterministic cliff at each person's conditional mean.
> Offers are now mean-preserving lognormal draws around the (Mills-corrected, smeared)
> conditional mean with GROUP-SPECIFIC residual SDs (educ × age, 0.29–0.55; dispersion rises
> with both) scaled by λ (headline 0.75, netting out ~CPS measurement error; band {0.50, 1.00}
> via 02f's "dispersion" axis; `EIG_MPL_LAMBDA` override). Hash-quantile draws salted
> independently of the entry lottery; deterministic. Effects: below-target 31.0% → **41.4%**
> (workers 23.6%); entry central 0.46M → **0.83M** (eps band 0.25–1.47M; dispersion band
> 0.62–1.12M; penalties 1.21/1.70M; estock 0.71M; take-up 0.66M; spouse-zeroed 0.69M);
> E/R ratios reconcile toward 1 (1.41/0.72/0.94); clawback medians 14.4/18.9/14.9% (gap vs
> other women narrowed — reachable single mothers sit less deep in phase-out ranges than
> mean imputation implied); cliff pay-up 0.115M (~1 in 7); costs rigid-central $93.1B gross /
> $74.2B net; entry FTE 0.32M vs hours-margin central 0.25M.
>
> **(5) Base-semantics sensitivity (2026-07-09, later).** The participation elasticities are
> employment-RATE semantics: their natural count base is the affected group's eligible EMPLOYED
> stock E_c (sm 2.22M / ow 10.12M / men 8.46M), not the reachable non-employed pool R_c the
> headline calibration uses. The pool now carries `required_net_gain_estock` (central edge
> recalibrated on target × E_c/R_c, feasibility-capped; E/R = 2.32 / 0.95 / 1.26), and
> `entry_margin_band.parquet` reports the "employment-stock semantics" row: total 0.52M vs
> 0.46M — but single mothers 0.12M vs 0.05M (the pool-share convention understates the cell
> with the smallest reachable pool relative to its workforce). The convention also explains why
> the E2 frame fix moved entry so sharply: pool-share entry scales with reachability (55.9% →
> 31.0%), which employment-rate semantics does not imply. Both bases are published.

**Scope:** the structural entry margin in `code/01_data_preparation/01h_nonemployed_pool.py` (pool construction, MPL imputation, reservation-wage band calibration) and `code/02_descriptive_analysis/02d_matching_simulation.py` (viability gate, entrant hours, fiscal costs, band reporting).
**Governing artifacts:** spec `Infrastructure/specs/2026-07-08_entry-from-nonemployment-remodel.md`; challenge report `Infrastructure/specs/2026-07-08_entry-remodel-challenge-report.md`; plan `Infrastructure/plans/2026-07-08_entry-from-nonemployment-implementation_rev2.md`; methodology memo `Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md`.

## 1. Where the literature is a target vs. a prior vs. a bound (M1)

| Consumer | Config source | Literature role |
|---|---|---|
| `02b_behavioral_scenarios.py` (reduced-form cost band) | `cfg["behavioral"]["scenarios"]` | **Literal target** — an explicitly labeled "EITC/CBO benchmark": what the policy costs *if* it behaves as the EITC/CBO participation literature implies. Not structural; unchanged by this remodel. |
| `01h` reservation calibration + `02d` structural entry | `cfg["matching"]["eps_ext_band"]` | **Prior/band** — lower/central/upper reservation-wage columns calibrated per band edge; the published structural entry number is a band, not a point. Central anchors remain EITC/CBO-derived (no evidence licensed moving them); edges carry wage-subsidy-specific anchors. |

## 2. Band provenance (per cell)

- **single_mothers** — central 0.50 (CBO/EITC mid-range); upper anchored by the Canadian SSP (Card & Hyslop 2005 / SRDC final report: any-employment +10.4pp*** Year 2 on a 30.1% control base; conversion under the any-employment margin and net stimulus basis per the 2026-07-08 sign-off); lower 0.25 (Kleven-haircut floor).
- **other_women** — 0.05 / 0.20 / 0.40 (user-approved 2026-07-08). Two-channel provenance: the married-women *negatives* in the EITC/WFTC/PPE-married literature (Eissa & Hoynes 2004; Brewer et al. 2006; Stancanelli 2008 married) operate through **household-income assessment**, a channel the individually-wage-assessed 80-80 does not have, and are deliberately NOT imported. The lower edge (0.05, near zero but positive) reflects the surviving intra-household coordination/income-effect channel (Bonin et al. 2003 mechanism; Blau & Kahn 2007 show it shrinking) and the Paycheck Plus Atlanta null. The upper edge (0.40) reflects secondary earners' historically higher own-wage elasticities and the verified Paycheck Plus NYC women's employment effect (+4.6pp*** Y2 / +3.2pp*** pooled, MDRC Table ES.2).
- **men** — central 0.05 (CBO 0–0.1 midpoint; retained — no evidence supports raising it). Upper informed by Paycheck Plus NYC's "disadvantaged men" effect (**Year-3 +5.8pp\*\*; pooled Years 1–3 +2.8pp not significant**; subgroup = noncustodial parents/formerly incarcerated, N≈620/arm), **diluted to the cell level** by the subgroup's share of the model's "men" cell — using the undiluted 5.8pp for all men would be indefensible. Lower edge 0.00 reinforced by the Atlanta null and the Bonin coordination mechanism.

## 3. Calibration mechanics (what changed 2026-07-08 and why)

1. **Band, not equality.** The single equality-solved markup rate is replaced by three per-cell λ solves (lower/central/upper), producing three reservation-wage columns over the *same* individuals.
2. **Net criterion inside the calibration (ST-1), in NET-GAIN space.** The reservation requirement is defined directly on net gains: person *i* enters iff `NI(package) − NI(0) ≥ (1+m_i) · max(NI(y·h) − NI(0), floor)`, with `m_i` the exponential markup. *Implementation note (2026-07-08, supersedes the rev2 plan's formula):* the plan's gross-reservation form `NI(package) ≥ NI(r·h)` proved **non-monotone in the markup** — benefit-cliff troughs in `NI()` put a hard floor on the viable share (single mothers ≈ 0.44 at any λ), making calibration infeasible (the failure mode ST-4 anticipated, in stronger form). The net-gain form is monotone in `m` by construction, collapses to the closed condition `m_i ≤ g_net_i`, and preserves the interpretation that `m = 0` means indifference at the person's own unsubsidized MPL. The bisection therefore converges exactly (realized = target to ~4 decimals, printed per cell × edge each run). The pool carries `required_net_gain_{edge}` and `ni_zero` as the explicit gate contract for 02d; `reservation_wage_{edge} = y·(1+m)` is retained as a descriptive gross-equivalent only.
3. **Net stimulus basis (ST-2).** The stimulus is `g_net = [NI(package) − NI(y·h)] / max(NI(y·h) − NI(0), floor)` — the proportional increase in the net return to work, which in the net-gain formulation is *identical* to the person's viability headroom `m_max`. Denominators floored at $1,000/yr and `g_net` capped at 3.0 (cliff guard); row counts hitting either are printed each run (~300 and ~60 of 182k). `NI(0)` includes means-tested transfers at zero earnings for the (coarse) family type. Note the economics this surfaces: under the taxable/countable design assumption (#4), median `g_net` for single mothers (≈0.13) is roughly **half** that of men/other women (≈0.25) — transfer phase-outs claw back much of the subsidy's net value exactly where the gross calibration assumed the largest stimulus.
4. **Saturating person-level response (ST-11).** The bisection target is the weighted mean of `response_multiplier(eps, g_net_i, ceiling_ext) − 1` over reachable persons — the same Michaelis-Menten form 02b uses, for the same reason (the linear `eps×g` form over-extrapolates at this subsidy's large gains).
5. **Hash-ranked markups (ST-10).** Per-person ranks `u` come from a hash of the stable person ID (YEAR-MONTH-SERIAL-PERNUM), not row order — restoring independence of the markup from survey timing/geography and making entrant composition invariant to file order. The same `u` is reused across the three edges (common random numbers), so the three viable sets are **nested by construction** and the reservation columns are pointwise monotone (asserted in the pipeline).
6. **Selection-corrected imputation (ST-7).** The pool's potential wage is imputed at the **conditional** mean for non-participants, `Xβ + ρσ·(−φ/(1−Φ))`, not the unconditional `Xβ` — retaining the negative selection on unobservables the Heckman estimates. Both variants' distributions are printed each run as the headline diagnostic.
7. **Participation shifters (replacing rev1's withdrawn matched-spouse-income instrument).** The selection equation adds real in-CPS **spouse-employed × married** (RELATE-paired household rosters, `01i_household_links.py`) and **own-child-under-5**. Honest position: *no bulletproof exclusion restriction exists in these data* — spouse employment is exposed to the assortative-mating critique, children to the motherhood-penalty critique, and the pre-existing `married`/`nchild` exclusions to the marriage-premium critique (all disclosed, Mroz 1987 / Puhani 2000 lineage). A Puhani-style sensitivity (Heckman conditional vs. Mills=0 vs. OLS-on-employed) is printed each run.
8. **Entrant hours (M7).** Entrants receive quantile-matched annual hours: each entrant's MPL percentile within their cell maps to the same percentile of incumbent annual hours in that cell (from `hourly_workers.parquet`), replacing the flat 2,000.

## 4. Design assumption: subsidy tax treatment (user decision, 2026-07-08)

The schedules treat the subsidy as **ordinary earned income — taxable and countable against means-tested benefits**. This is a deliberate, conservative modeling choice. It partially re-introduces the benefit-phase-out interactions the policy's public framing says the design avoids; if the statutory design excluded the subsidy from means-tested program income, viability and gross cost would be higher and cliff interactions smaller. The cliff-diagnostic count in 02d quantifies how much this choice bites.

## 5. Disclosed limitations

- **Household coordination (Bonin channel).** Individuals are modeled independently; a partner's response to a spouse's subsidized earnings is not modeled. Bounded, not solved: `entry_margin_band.parquet` carries sensitivity rows zeroing/halving induced entry for married entrants with an employed spouse (~66% of linkable married pool rows). This is a **reported bound, not a calibrated behavior** — no transportable magnitude exists (Bonin is an ex-ante simulation under German institutions).
- **"Men" cell heterogeneity.** Responsiveness concentrates in a disadvantaged/noncustodial subgroup (Paycheck Plus NYC; Parents' Fair Share) that CPS cannot identify (no custody/justice-involvement variables). The cell-level band edge is a diluted blend that understates response for that subgroup and overstates it for other men.
- **Fixed cost of work (M6) — deferred.** No childcare/commuting *expense* measure exists in-repo; the net viability test therefore still overstates entry likelihood, most for single mothers. The under-5 and household-composition covariates shift the participation *propensity* by need but do not price the cost. Unblock paths queued: ASEC re-pull with SPM expense variables; ATUS (deferred).
- **UI and part-year timing (ST-3).** `NI(0)` omits unemployment insurance for the unemployed subset (overstates their net gain from entry and their fiscal cost saving), and the annual schedule is applied to a survey-month employment state (overstates the counterfactual-zero-income year for part-year workers). Both cut toward overstating entry; disclosed, not yet modeled.
- **Band scope (ST-9).** The band represents `eps_ext` scenario uncertainty only — not sampling error, not the exponential-markup functional form, not the identity of marginal entrants (fixed by the shared rank).
- **Spouse-link coverage.** ~5% of married pool members live in complex households where RELATE pairing cannot identify the spouse (flagged, not guessed); a queued SPLOC re-pull closes this. Spouse *earnings* are observed only for the MISH 4/8 quarter of married rows and are used only in sensitivities.

## 6. Reconciling 02b and 02d entry numbers

The two entry-margin numbers answer different questions and differ by construction: population (02b up-weights observed low-wage incumbents; 02d draws from the actual non-employed pool), stimulus basis (02b gross; 02d net), response aggregation (02b person-level multiplier on workers; 02d calibrated pool share), and elasticity source (benchmark scenarios vs. band). The pipeline writes `entry_reconciliation.parquet` attributing the wedge; do not quote the two numbers side-by-side without that attribution.
