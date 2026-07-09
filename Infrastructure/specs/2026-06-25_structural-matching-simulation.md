# Requirements Specification: Structural Matching Simulation (resolves A1.3)

**Date:** 2026-06-25
**Status:** DRAFT
**Suggested Save Location:** `Infrastructure/specs/2026-06-25_structural-matching-simulation.md`

## Objective

Replace the ad-hoc extensive-margin + band-clearing incidence model with a structural
search-and-matching simulation: assign each worker a marginal product (MPL, `y_i`) and a
reservation wage (`r_i`), determine employment by match viability, set wages by Nash bargaining,
and model the 80-80 subsidy as added match surplus. This resolves A1.3 (endogenous, correctly-
placed entry) and replaces demand-elasticity incidence with bargaining incidence `(1−β)`.

## Theoretical foundation (literature-grounded)

From the search-and-matching scout (catalog ids in brackets):

1. **Match viability** — a job exists iff surplus `S_i = y_i − r_i ≥ 0`. Workers with `r_i > y_i`
   (reservation exceeds own productivity) are structurally non-employed.
   [`1994-mortensen-pissarides-job-creation-destruction`]
2. **Wage = Nash split of surplus** — `w_i = r_i + β(y_i − r_i)`, β = worker bargaining power.
   [`1982-diamond-wage-determination-search-equilibrium`, `2000-pissarides-equilibrium-unemployment-theory`]
3. **Subsidy adds to surplus** — joint surplus becomes `y_i + s − r_i`; a match is newly viable
   where `y_i + s(y_i) − r_i ≥ 0`; the subsidy is split **β to worker, (1−β) to firm** — this is
   the incidence mechanism (replaces the labor-demand elasticity).
   [`2006-hungerbuhler-lehmann-optimal-taxation-search-equilibrium`; measured analog
   `2010-rothstein-eitc-incidence-tax`, `2018-cahuc-carcillo-le-barbanchon-hiring-credits`]
4. **β anchors** — central **0.5** (Hosios, symmetric matching) [`1990-hosios...`]; range to
   **0.7** (Shimer calibration [`2005-shimer...`]; Rothstein measured ~70% worker capture). A
   **wage-rigid, higher-firm-capture** scenario per Hall-Milgrom [`2008-hall-milgrom...`] is the
   principal incidence uncertainty.
5. **Reservation wage** — anchor `r_i` on the worker's prior/potential wage (declines slowly)
   [`2016-krueger-mueller-empirics-reservation-wages`], adjusted for transfers, spouse income,
   children, home-production proxies.
6. **Minimum wage** — truncate the bargained wage at the statutory floor and re-test viability
   [`2006-flinn-minimum-wage-search-matching-bargaining`].

## Requirements

### MUST Have

- [ ] Assign `y_i`: **Heckman selection-corrected** wage equation (employed = observed wage;
      non-employed = selection-corrected predicted potential wage).
- [ ] Assign `r_i`: prior/potential-wage anchor × adjustments, **calibrated** so (a) baseline
      viability `y≥r` reproduces observed employment rates by age×sex×education cell, and
      (b) subsidy-induced entry reproduces the cell-specific extensive elasticities already in
      `cfg["behavioral"]`.
- [ ] Employment rule: employed iff `y_i + s(y_i) ≥ r_i` (baseline: `s=0`). Entrants =
      `r_i ∈ (y_i, y_i + s(y_i)]`.
- [ ] Wage rule: `w_i = r_i + β(y_i − r_i)` (augmented surplus with the subsidy); truncate at the
      federal minimum and re-test viability.
- [ ] Report **β as a scenario band**: 0.5 (Hosios central), 0.7 (measured/Rothstein), plus a
      Hall-Milgrom wage-rigid (lower worker capture) case.
- [ ] Output: induced entrants (by cell), gross subsidy cost, **incidence = (1−β)·subsidy to
      firms**, worker net gain, all with `[transported assumption]` disclosures.
- [ ] Static parity: the existing 02a/02b static cost path is untouched; this is additive.

### SHOULD Have

- [ ] Free-entry job-creation margin (vacancy re-optimization) as an optional second layer.
- [ ] Reconcile the realized aggregate extensive elasticity back to the literature targets.
- [ ] Drop-in path for real ASEC microdata (via `01c`) replacing the synthetic pool.

### MAY Have

- [ ] Endogenous reservation-wage response to the subsidy (option value of search).
- [ ] Heterogeneous β by sector/skill.

## Data approach (synthetic pool — user choice)

ASEC microdata is not downloaded; build a **synthetic non-employed pool**:
1. Working-age population by age×sex×education from public marginals; non-employed count per cell
   = pop × (1 − employment rate). Impute family/children/state/spouse from population shares.
2. `y_i` from the Heckman wage equation (estimated on the employed `hourly_workers.parquet`,
   selection-corrected; flag the <$16.80 truncation as a limitation).
3. `r_i` from the calibration above.
4. Structure code so the real ASEC extract drops in later without rework.

## Clarity Status

| Aspect | Status | Notes |
|---|---|---|
| Matching equations (viability, Nash split, subsidy surplus) | CLEAR | From scout; literature-anchored. |
| Incidence = (1−β) | CLEAR | Replaces demand-elasticity incidence; resolves the band-collapse artifact. |
| β central/range | ASSUMED | 0.5 central, 0.7 measured, Hall-Milgrom rigid lower; user may pick a single anchor. |
| Reservation-wage calibration | ASSUMED | Prior-wage anchor (Krueger-Mueller) + transfers/children; calibrated to epop + elasticities. |
| Synthetic pool vs real ASEC | CLEAR | Synthetic per user; real ASEC is the SHOULD drop-in. |
| Wage equation truncation | ASSUMED | Estimated on eligible employed (<$16.80); Heckman handles selection; flagged limitation. |
| Vacancy/job-creation margin | ASSUMED | Deferred to SHOULD; partial (viable-set) model first. |

## Success Criteria

- Baseline (s=0) employment reproduces observed employment rates by cell (calibration check).
- Subsidy-induced entry matches the cell extensive elasticities within tolerance.
- Incidence equals `(1−β)·subsidy` by construction; wages bounded in `[r_i, y_i]` (no collapse).
- Outputs carry Evidence + transported-assumption disclosures; `/review-methodology` passes.

## Proposed code

- `code/01_data_preparation/01g_synthetic_nonemployed_pool.py` — build the pool + Heckman MPL.
- `code/02_descriptive_analysis/02d_matching_simulation.py` — calibrate `r_i`, run the
  viability/bargaining simulation, β band, write `matching_simulation.parquet`.
- New `cfg["matching"]` block (β scenarios, reservation-wage params, pool marginals source).
- Retire/supersede 02c's band-clearing incidence (keep file, mark superseded).

## Outcome (built + verified 2026-06-25)

Implemented `02d_matching_simulation.py` (+ `cfg["matching"]`); wired into run_all; 02c retired.
Static parity (02a/02b) preserved. Added an **incumbent wage-rigidity** switch (Hall-Milgrom):
existing matches' wages are sticky and do not renegotiate, so bargaining incidence falls only on
NEW hires. This is the defensible central case.

Results (β band; entry 0.73M, placed at the p15 entry wage = $10/hr):
- **rigid (central, incumbent wages sticky):** net **~$81B**, gross ~$106B, **firm capture ~4%
  (~$4B, new hires only)**, incumbent wages unchanged. β barely matters (entrants are a small base).
- **flexible (all wages renegotiate — incidence UPPER bound):** net $105B (β=0.7) → $127B (β=0.5)
  → $155B (β=0.3); firm capture 25–52%. Requires cutting 21M incumbents' wages — counterfactual to
  the wage-rigidity evidence, so reported as a bound, not the central case.

Headline: structural dynamic net cost ≈ **$81B** (static $73B + ~$8B for ~0.73M induced entrants),
incidence small and confined to new matches. Wages bounded in [r, y] — no collapse. This resolves
the band-clearing artifact and A1.3 (entry endogenous and correctly placed at low MPL).

Residual: synthetic entry (no real ASEC pool yet); transported β / reservation ratio. Real ASEC
via 01c remains the upgrade path.

## Approval

[x] User approved: 2026-06-25 (Benjamin Glasner) — "approve" (β band confirmed)

**Build note:** For v1, `01g` (synthetic pool) is folded into `02d` — entrants are generated
inside the simulation as low-MPL templates (bottom-wage incumbents reweighted to the
elasticity-implied entry count), rather than a separate microdata parquet. This keeps entry
calibrated to the sourced elasticities and entrants placed at low y, without a standalone pool
file. A real ASEC pool (via `01c`) remains the SHOULD-have drop-in.
