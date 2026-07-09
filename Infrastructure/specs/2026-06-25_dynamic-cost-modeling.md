# Requirements Specification: Dynamic (Behavioral) Cost Modeling for the 80-80 Rule

**Date:** 2026-06-25
**Status:** APPROVED
**Suggested Save Location:** `Infrastructure/specs/2026-06-25_dynamic-cost-modeling.md`

## Objective

Extend the static 80-80 cost model with a behavioral layer that adjusts employment and hours
in response to the subsidy, recomputes earnings and the tax/safety-net recapture, and reports
gross and net cost as a **sensitivity band across the contested elasticity literature** — never
a single behavioral point estimate.

## Background (evidence-grounded)

The literature scout (26 catalog entries, `Infrastructure/references/literature/catalog.yaml`)
establishes four facts that constrain this design:

1. **No elasticity exists for a per-hour wage-fill design.** All measured estimates come from
   the EITC, CTC, NIT, in-work credits (UK WFTC), or earnings supplements (Canadian SSP, the
   closest analog — Card & Hyslop 2005). Every behavioral number is necessarily *transported /
   ex-ante* and must be disclosed as such.
2. **The extensive-margin parameter is contested at its foundation:** Kleven (2024) ~0 (fragile)
   vs. Chetty (2012) ~0.25 vs. Keane (2011) higher. The headline net cost swings materially
   across this band — so the band, not a point, is the deliverable.
3. **The 80-80 base is where evidence is weakest** (prime-age men, secondary earners, childless
   adults); the sharpest estimates are for single mothers.
4. **Recapture machinery exists** (Bastian & Jones 2021 ~83% recovered; Hendren policy
   elasticity; CBO/JCT dynamic scoring) but is mechanically tied to the large elasticities
   Kleven disputes.

The current pipeline is **purely static** (Explore confirmed: no elasticity/labor-supply code).
Cost = weighted sum of `subsidy_annual` (gross) plus interpolated tax/transfer deltas (net).

## Requirements

### MUST Have (Non-Negotiable)

- [ ] Model both margins separately: **extensive** (employment entry) and **intensive** (hours),
      with distinct parameters — never a single blended elasticity.
- [ ] Report results as a **3-point sensitivity band**: Lower = Kleven (~0 entry), Central =
      Chetty steady-state (extensive ~0.25, intensive ~0.33), Upper = Keane. Static remains the
      reference scenario.
- [ ] Convert the subsidy into a **percent change in the effective return to work** per worker
      (the behavioral stimulus), then apply elasticities to that — not to the dollar subsidy.
- [ ] Propagate behavioral earnings changes through the **existing schedule interpolation** so
      tax recapture and safety-net offsets are recomputed at the new income (insertion Point B).
- [ ] Every transported elasticity is logged with its **source population and margin** and an
      explicit `[transported assumption]` disclosure; results carry an Evidence section.
- [ ] Behavioral layer is **opt-in and additive** — the static model remains the default and is
      never overwritten. Gross/net static outputs must be reproducible unchanged.

### SHOULD Have (Preferred)

- [ ] **Income-effect parameter** for inframarginal workers (hours reduction from higher income),
      sourced from NIT/CTC evidence, applied to the intensive margin.
- [ ] **Wage pass-through / incidence parameter** (Rothstein 2010) as a separate scenario knob:
      a share of the subsidy captured by employers via market-wage depression, changing effective
      worker benefit and distribution. Default 0 (full worker capture) with a documented alt.
- [ ] **Take-up / salience parameter** (Chetty, Friedman & Saez 2013) on the extensive response.
- [ ] A scenario-comparison output table (static vs. lower/central/upper) at stage 05.
- [ ] Streamlit calculator exposes the behavioral scenario as a selector (insertion Point E).

### MAY Have (Optional, If Time)

- [ ] Population-heterogeneous elasticities (single mothers vs. men vs. secondary earners) rather
      than one band applied uniformly.
- [ ] An MVPF-style summary statistic (Hendren & Sprung-Keyser) for the central scenario.
- [ ] Re-precompute PolicyEngine schedules on an expanded income grid if behavioral incomes fall
      outside the current $0–$65k / $500-step range.

## Proposed Architecture (maps to Explore's insertion points)

| Point | File / line | Change |
|---|---|---|
| A | `code/01_data_preparation/01a_data_ingest.py` after L269 | New `apply_behavioral_response()`: compute % return-to-work gain, apply extensive + intensive elasticities → `annual_hours_behavioral`, `subsidy_annual_behavioral`; static columns retained. |
| B | `code/02_descriptive_analysis/02a_descriptive_stats.py` L132–163 | Interpolate schedules at behavioral income (`baseline_behavioral + subsidy_behavioral`) so recapture reflects induced earnings. |
| C | `02a` L259–262 | Aggregate gross cost from behavioral subsidy when scenario active. |
| D | `code/05_figures_tables/05a_main_outputs.py` | Scenario-comparison table (static / lower / central / upper). |
| E | `app/tabs/calculator.py` L348–378 | Optional behavioral-scenario selector. |

Parameters centralized in `code/00_setup/00_config.py` (new `behavioral` block), defaulting to OFF.

## Clarity Status

| Aspect | Status | Notes |
|--------|--------|-------|
| Sensitivity band, not point estimate | CLEAR | Forced by the Kleven↔Chetty↔Keane conflict. |
| Extensive vs intensive modeled separately | CLEAR | Standard; load-bearing margin is extensive. |
| Static model preserved as default | CLEAR | Additive, opt-in. |
| Exact central elasticity values | ASSUMED | Chetty 2012 steady-state (ext ~0.25, int ~0.33); user can override. Magnitudes are Medium-confidence per scout (abstract-level, not full-text). |
| Wage pass-through inclusion | ASSUMED | Built as an off-by-default scenario knob; promote to MUST if you want incidence in the headline. |
| Stochastic entry vs. expected-value entry | ASSUMED | Expected-value (fractional employment shift on weights), not simulated individuals. Simpler, matches the weighted-aggregate design. |
| Re-precompute PE schedules? | RESOLVED | Only 0.5–1.1% of workers exceed the $65k grid across scenarios (incomes clamped, flagged in-run). Grid extension is not urgent; revisit only if upper-scenario tail estimates are published. |
| Verbatim CBO 0.19 elasticity | BLOCKED-minor | CBO PDF unreachable (HTTP 403); 0.24/−0.05 corroborated. Confirm before any published use. Not used as a scenario anchor (band uses Kleven/Chetty/Keane). |

## Success Criteria

- Running the pipeline with the behavioral block OFF reproduces current static gross/net cost
  exactly (regression check).
- With the block ON, the pipeline emits gross and net cost for all three band scenarios plus
  static, each labeled with its elasticity assumptions and sources.
- Every behavioral parameter traces to a catalog entry; `[transported assumption]` disclosures
  present; `/review-numbers` and `/review-methodology` pass on the new outputs.

## Approval

[x] User approved: 2026-06-25 (Benjamin Glasner) — "Approve and launch"

---

## Amendment 1 — 2026-06-25 (approved: "follow your recommendations")

Triggered by a cross-comparison with an independent design pass. Our static baseline
($94.37B gross / $73.18B net, real CPS ORG microdata) is trusted; the other pass's
$70/$60B was hypothetical and is disregarded. Three improvements adopted, in priority order.

### A1.1 — Cell-specific extensive elasticities (DONE)
- **Why:** a single blended `eps_ext` mis-weights the response. The 80-80 base is ~41% men,
  ~48% other women, ~11% single mothers; CBO (McClelland & Mok 2012) puts the participation
  elasticity at ~0-0.1 for men vs 0.3-1.2 for EITC-eligible single mothers. A blended value
  applies single-mother responsiveness to prime-age men, where EITC evidence does not transfer.
- **What:** `eps_ext` is now keyed by demographic cell (single_mothers / other_women / men),
  assigned in 02b from `sex_label` + `family_type_key`. Intensive `eps_int` central lowered
  0.33 → 0.10 (the 0.33 was Chetty's Hicksian *steady-state bound*, not an intensive-hours
  elasticity; consensus and our own scout finding — "large entry, negligible hours" — support ~0.1).
- **Result:** central induced 1.34M → 0.93M; net cost now *rises* with behavior (the prior
  "pays for itself" was an artifact of the high blended elasticities). 02b reports induced-by-cell.
- **Status:** implemented, static parity re-verified.

### A1.2b — Incidence REBUILT as segmented competitive markets (DONE)
Replaced the single-national-market version after the user correctly noted it conflated
competitive incidence with employer manipulation and over-hit near-target workers. The rebuild:
- **Segmented:** each $1 employer-wage band is its own competitive market, clearing on its OWN
  cell-specific supply shift. Bands of mostly prime-age men (eps_ext~0) see ~no wage decline.
- **Outside-option floor:** total comp cannot be bid below the worker's pre-policy wage
  (comp_floor_frac=1.0) — a universal subsidy raises every employer's offer, so anyone pushed
  below their outside option is poached.
- **Demand-side rationing:** demand responds to the REALIZED (floor-truncated) wage, not the
  notional clearing pressure. Where the minimum-wage floor binds (bottom bands), the supply
  surge cannot be absorbed → queuing/unemployment, not jobs → induced employment rationed to
  min(supply, demand). This was a real bug in the first segmented pass (demand used theta_s).
- **Result (central eta_d=-0.3):** static $73.2B → +entry $77.4B → +hours $78.4B →
  +incidence **$116.2B net** (avg wage -10.6%, worker capture 64%). Band over eta_d:
  slack $103.9B / tight $136.4B. Per band: $7-8 wants 30% entry but realizes 0.2% (absorb 0.01,
  wage floored); mid-bands $10-13 clear with -20 to -29% wages; top bands barely move.
- **Down from** the single-market $153.5B; the decomposition + per-band table are the outputs.
- **Residual caveat:** mid-band wage declines are driven by supply shifts from the eps*g
  linearization at large g, which may still overstate the bottom-of-mid response. The eta_d band
  brackets demand uncertainty; large-g supply remains the open transported assumption.
- **Status:** implemented, runs, 02b static parity preserved. Outputs incidence_decomposition
  + incidence_by_segment. Supersedes A1.2 below.

### A1.2d — Entrants enter at the BOTTOM (DONE — corrects a real flaw)
User-identified flaw: the prior 02c cloned extensive entrants into every wage band, manufacturing
supply shifts/wage declines/backfill in the middle and upper bands where new low-skill workers
never land. Corrected theory (competitive incidence, demand fixed): entrants are low-productivity
→ enter at the bottom; the supply shock and any wage decline localize there (where the minimum
wage converts it to rationing); middle/upper bands get no entrants, so with a near-zero hours
response their wages and subsidies are essentially unchanged.
- **Rebuild:** entrants sized from the cell-specific extensive response, then POOLED and placed
  across bands <= entry_ceiling ($11) proportional to incumbent density; incumbents contribute
  only the intensive (hours) margin, now near-zero (central eps_int 0.10 → 0.05). New config:
  `entry_ceiling`. Static parity preserved (re-verified PASS).
- **Result (central eta_d=-0.3):** static $73.2B → +entry $77.9B → +hours $79.2B →
  +incidence **$91.9B net** (avg wage −5.2%, worker capture **81%**). Band: slack $89.3B /
  tight $99.1B. Incidence now adds only ~$13B (was ~$37B); employers capture ~19% (was ~36%).
- **Per band:** entrants land only in $7–11; wages fall 13–29% in the $9–12 entry zone (where
  not floored), ~0 at the very bottom ($7–8, rationed), and just −0.5 to −4.5% in $12–16.80 —
  and that residual is ONLY the small hours response (vanishes at eps_int=0).
- **Status:** done; this is the defensible headline. Supersedes A1.2b/c. Residual: extensive
  pool still sized from incumbents' g (true non-employed pool = A1.3, data-blocked).

### A1.2c — Bounded (saturating) entry function (DONE)
Replaced linear `1 + eps*g` with a Michaelis-Menten form `m = 1 + (M-1)*eps*g/((M-1)+eps*g)`:
local slope = the literature elasticity at the margin, asymptote = ceiling M (employment can
rise at most M_ext=1.5x a band's baseline; hours M_int=1.4x). `cfg["behavioral"]["saturation"]`.
At eps=0 it returns 1 → static parity preserved. Used in both 02b and 02c.
- **Effect:** 02b central induced 0.93M → 0.73M (bites hardest at the bottom, want 30% → 21%).
  Incidence central net $116.2B → $114.2B; band $101.4B (slack) / $134.6B (tight).
- **The diagnostic finding:** bounding the SUPPLY form barely moved the headline, because the
  incidence cost is governed by the INELASTIC labor DEMAND (eta_d=-0.3), not the supply
  functional form. To clear a ~7-11% mid-band supply shift with eta_d=-0.3 mechanically requires
  a ~20-29% wage decline; that is arithmetic of inelastic demand, not supply over-extrapolation.
  => The dominant remaining uncertainty is eta_d (the $101-135B band), now properly bracketed.
- **Status:** done. Remaining structural limitation is A1.3 (extensive margin still scales the
  employed base, not a true non-employed pool) — data-blocked.

### A1.2 — Labor-demand elasticity + incidence module (superseded by A1.2b/A1.2c)
- **Built:** `code/02_descriptive_analysis/02c_incidence.py` — single-market partial-equilibrium
  fixed point on the employer-wage multiplier theta; `cfg["behavioral"]["incidence"]` with
  eta_d = {central -0.30, slack -0.50, tight -0.15} (Hamermesh/Lichter; Busso-Gregory-Kline
  slack-dependence). Outputs `incidence_decomposition.parquet` (waterfall) and worker-capture %.
- **Result (central scenario):** static $73.2B net → +entry $77.4B → +hours $78.4B →
  **+incidence (eta_d=-0.3): employer wage −17.7%, net $153.5B, worker capture 51%**. Band over
  eta_d: slack $127.5B (capture 63%) … tight $201.1B (capture 36%). Worker-capture ~50% is
  Rothstein-consistent ($0.70 to worker); the COST LEVEL balloons because an 80% wage-FILL
  backfills 80 cents of every wage dollar employers cut — a genuine runaway-leakage property of
  this design, and exactly the channel the commenters (Hall, Scholl) flagged.
- **CAVEAT (load-bearing):** the single national market with a *uniform* wage cut almost
  certainly OVERSTATES the level — the labor-supply boost is concentrated among the lowest-wage
  workers, but the clearing wage cut is applied to the whole low-wage pool, including the ~46%
  near the $16.80 target whose widened gaps drive most of the cost jump. The capture *share* is
  credible; the cost *level* is an upper structure. **Next refinement: segment into per-wage-bin
  (or per-cell) markets so the depression localizes where the supply shift actually occurs.**
- **Status:** implemented + runs; decomposition is the headline output. Magnitude flagged as
  ex-ante upper bound pending the segmented-market refinement.

### A1.2-prior note (superseded)
- **Why:** our pass-through is an unanchored `phi` knob. Incidence should fall out of the
  relative slopes of labor supply and demand; we never scouted the labor-DEMAND elasticity.
- **What:** a follow-up literature scout (launched) is sourcing Lichter-Peichl-Siegloch (2015,
  ~ -0.3, more elastic for low-skill, publication-bias haircut), Hamermesh, Popp (2023), and —
  critically — Busso, Gregory & Kline (2013, Empowerment Zones) as the closest real-world
  wage-credit pass-through benchmark. Then build a partial-equilibrium incidence step (new 02c
  or 02b extension): supply shift → move down a constant-elasticity demand curve → employer
  wage falls → per-job subsidy `s(w_emp)` rises → iterate to a fixed point on `w_emp`. The
  decomposition (static → +entry → +hours → ±incidence) becomes the headline output.
- **Status:** scout running; solver to be built on its verified parameters. Labor-demand
  elasticity `eta_d` will be a config triple (central ≈ -0.3 pending verification).

### A1.3 — Non-employed entry pool with low entry wages (BLOCKED — needs data)
- **Why:** the extensive margin currently scales the *employed* eligible stock (entrants
  resemble the marginal employed worker, inheriting near-target wages → understates entrant
  subsidy cost). The policy's real target is the *non-employed* (the ~10M jobless prime-age men).
- **What (designed, not built):** source a non-employed prime-age pool from CPS (not in the
  current ORG extract), assign each a reservation wage, let entry occur as `w + s(w)` clears it,
  and draw entrant wages from the *bottom* of the wage distribution. Calibrate the realized
  aggregate elasticity back to the A1.1 cell targets.
- **Status (updated 2026-07):** BUILT as `01h_nonemployed_pool.py`, sourcing the non-employed from
  the ORG **raw** partitions (EIG-Wage-Figure `data/raw/cps_org`, pre-01b-gate — they retain
  non-employed + WTFINL + EMPSTAT). MPL imputed from sex×educ×age employed cells; reservation
  calibrated to the cell elasticities; WTFINL-weighted. `02d` auto-consumes the pool when present,
  else synthetic. Toy-tested; runs on the real extract once downloaded (IPUMS `00a→01a`).
  Caveat: extract lacks NCHILD → single-mothers cell collapses into other_women and child transfers
  understated; one-line NCHILD add to wage-figure `00a` resolves it (01h auto-uses NCHILD if present).

### Amendment success criteria
- A1.1: static parity preserved (✓); induced reported by cell (✓).
- A1.2: incidence module reproduces no-incidence band when `eta_d → -∞` (full worker capture)
  and `phi=0`; labor-demand elasticities trace to catalog entries.
- A1.3: when built, realized aggregate elasticity matches the cell targets within tolerance.
