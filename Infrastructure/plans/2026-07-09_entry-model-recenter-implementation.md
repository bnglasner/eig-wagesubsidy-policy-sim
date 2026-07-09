# Implementation Plan: Entry-Model Re-Center + Scenario Grid + PI-3

**Date:** 2026-07-09 · **Status:** APPROVED (user sign-off 2026-07-09) — Wave 1 authorized
**Locked decisions:** (1) evidence-central penalty = **status-differentiated** `unemployed:0.05, nilf_other:0.10, disabled:0.15, retired:0.15` (weighted mean ≈10–11%); (2) central dispersion **λ=0.75** (λ∈{0.5,1.0} as grid axes); (3) **full 27-cell** grid = uniform-penalty {0,10,20%} × λ {0.5,0.75,1.0} × eps {lower,central,upper} (9 pool builds). Headline evidence-central uses the status-differentiated penalty (better composition, ≈ same magnitude as the grid's uniform-10% cell).
**Basis:** holistic evaluation (`Infrastructure/explorations/2026-07-09_holistic-eval/`) + user decisions (2026-07-09):
Q1 **Re-center (Option A)**; Q2 **scenario grid + full decomposition**; Q3 pre-pub modeling scope = **PI-3 hours sensitivity only** (incumbent net-basis, UI-in-NI(0), fixed-cost of work → **disclosed limitations, not modeled**); Q4 **plan-for-approval**.
**Job tier (perf-governance):** Tier 2 (2–15 min) — ≤9 pool rebuilds + figure re-render. No Tier-3 controls needed.

---

## Requirements (from the 2026-07-09 decisions)

- **R1 (MUST)** — Add a jointly-specified **evidence-central** entry scenario that corrects the one non-neutral choice (penalty = 0), keep 0.83M as an explicitly **labeled conservative floor**, and attach a **two-sided bias disclosure** (MPL-side conservatism vs. matching/fixed-cost/UI upward biases).
- **R2 (MUST)** — Present uncertainty as **3 headline joint bundles** (Conservative / Evidence-central / High) **and** publish the **full joint-corner decomposition matrix** (penalty × λ × eps). Retain the existing one-at-a-time table as the marginal-axis view.
- **R3 (MUST)** — Add a **PI-3 entrant-hours sensitivity**: report entry FTE, marginal $/job, and fully-loaded $/job under ≥2 alternative hours mappings besides the current rank-rank.
- **R4 (MUST)** — Fix the confirmed correctness/consistency defects (DN-001 $158→160.3B; DN-002 firm-capture "under one percent" → 1.5% at headline β; stale $19.62–$22.17 medians; "~0.5M entrants"; Figure 6 "reservation wage" caption; cross-doc composition wording).
- **R5 (SHOULD)** — Strengthen disclosure language for the **deferred** limitations (incumbent net-basis, UI in NI(0), fixed cost of work) so they read as deliberate scope choices.
- **R6 (MUST)** — Determinism, static parity, and canonical-pool preservation must hold after all changes; both drafts + methodology doc regenerated together; fresh review before ship.
- **Out of scope (MUST NOT):** re-open eps anchors or the taxable/countable tax treatment; build a Monte-Carlo probabilistic model; fold take-up/demand realism into the potential-entry central.

---

## Open decisions to confirm at approval (please initial)

1. **Evidence-central penalty magnitude.** Proposed: **uniform 10% non-employment wage penalty** (this is the existing `pen10` variant → co-central **≈1.21M**), which lands in the ~1.1–1.2M range you anchored on and is the simplest defensible choice. *Alternative:* a status-differentiated penalty (e.g. unemployed 5% / NILF 10% / disabled·retired 15%, mean ≈10%) — this changes entrant **composition** but leaves the **count ≈ the same** (Q6 finding), at the cost of a new config vector. **Recommend uniform 10%.** ☐ confirm / ☐ use status-differentiated
2. **Central dispersion λ.** Proposed: **keep λ=0.75 as the central**, with λ=1.0 as a grid axis (avoids compounding two upward corrections into the headline; keeps the co-central at ~1.2M rather than ~1.5M). ☐ confirm / ☐ move central to λ=1.0
3. **Grid granularity.** Proposed full decomposition = **penalty {0, 10, 20%} × λ {0.5, 0.75, 1.0} × eps {lower, central, upper} = 27 cells** (from only **9 pool builds** — eps edges are read from the 3 pre-computed `required_net_gain_*` columns per pool, no extra rebuild). ☐ confirm / ☐ coarser

The three headline bundles under proposals 1–2 (to be recomputed exactly, not asserted):
| Bundle | Penalty | λ | eps | Expected entry |
|---|---|---|---|---|
| Conservative floor | 0% | 0.75 | central | **0.83M** (current) |
| **Evidence-central** | 10% | 0.75 | central | **≈1.2M** |
| High | 20% | 1.0 | upper | **≈2.5–3M** (joint corner; methodology MR-002) |

---

## Files to modify / create

**Code (analysis — the gated part):**
1. `code/00_setup/00_config.py` — add `cfg["matching"]["entry_scenario_grid"]` (axis lists), the evidence-central bundle definition, and `entry_hours_mode` default. No change to eps anchors or tax treatment.
2. `code/01_data_preparation/01h_nonemployed_pool.py` — add `EIG_ENTRY_HOURS_MODE ∈ {rank, independent, median}` to `_entry_hours` (rank = current default; independent = hash-quantile draw from the cell hours distribution uncoupled from MPL; median = cell-median). No other logic change; canonical pool (rank, penalty 0, λ0.75) stays byte-identical.
3. **NEW** `code/02_descriptive_analysis/02g_entry_scenario_grid.py` — builds the 9 (penalty×λ) pools via the existing `02f._build_variant_pool` machinery, runs `02d._entrants_from_pool` across the 3 eps edges for each, writes `entry_scenario_grid.parquet` (27-cell decomposition) + `entry_headline_scenarios.parquet` (the 3 bundles). Cleans up suffixed pools (mirrors 02f).
4. `code/02_descriptive_analysis/02d_matching_simulation.py` — add an **entrant-hours-sensitivity** table (`entrant_hours_sensitivity.parquet`): entry FTE, mean hours, marginal $/job (gross & net), fully-loaded $/job under the 3 hours modes at the evidence-central bundle. (PI-3.)
5. `code/run_all.py` — register `RUN_02G_ENTRY_SCENARIO_GRID = True`, sequence after 02f.
6. `code/05_figures_tables/05d_supporting_figures.R` (and/or 05c) — re-point the headline; replace/augment Fig 14 with the scenario grid; new hours-sensitivity figure; update Fig 7/10 to the re-centered headline. `05z_build_manifest.py` re-scans automatically.

**Docs / drafts (prose — lower risk, still in this plan):**
7. `docs/entry_from_nonemployment_methodology.md` — revision banner: re-center, grid+decomposition, two-sided bias disclosure, PI-3, dead-`min(0.90,·)` note; re-annotate W2c anchor conversions on the realized-g_net scale (Q3b).
8. `drafts/2026-07-08_wage-subsidy-impact-cost-summary.md` — re-center headline to the evidence-central with 0.83M as labeled floor + range-forward framing; two-sided bias disclosure; **Figure 6 caption** fix; **firm-capture wording** (harmonize with appendix); composition wording; reconciliation "cost not entry" scoping.
9. `drafts/2026-07-09_technical-appendix.md` — §4 medians, §7 $158→160.3B + firm-capture 1.5%, §8 ~0.5M→0.83M; add evidence-central bundle + grid + PI-3 + updated §9 uncertainty table; EARNWT/OLS wording (CC-007); deferred-limitation disclosures (R5).
10. `app/app.py` — **verify/update** if it surfaces the central entry figure (check before editing).

**Explicitly NOT modeled (disclosed only, per Q3):** incumbent hours-margin net basis; UI/SSDI in `NI(0)`; fixed cost of work. Language added in R5.

---

## Execution waves

- **Wave 0 — approval.** You confirm the three open decisions above. No code until then. ✅ DONE.
- **Wave 1 — code (files 1–5). ✅ DONE & VERIFIED (2026-07-09).** Implemented config + 02d PI-3 + NEW 02g grid + run_all wiring + 05z registry. **Simplification vs plan:** 01h needed NO change — all pool-variation selectors (`EIG_MPL_PENALTY/LAMBDA/STATUS_PENALTY`) already existed, so PI-3 hours modes live entirely in 02d and the canonical pool is byte-identical by construction. Results: conservative_floor 0.83M, **evidence_central 1.25M**, high 3.37M; PI-3 marginal $/job 2.4× sensitive to hours coupling. Static parity PASS.
- **Wave 2 — figures. ✅ DONE (2026-07-09).** fig14 → scenario grid; fig07 → 3 headline bundles by group; fig10 → re-centered $/job ($5.1K marginal; $22K/$59K/$89K fully-loaded). fig12/fig08 kept on base pool (consistent). All render via Rscript 4.5.2; fig07/10/14 visually verified. (app/app.py not yet checked — flagged.)
- **Wave 3 — docs/drafts. ✅ DONE (2026-07-09).** Both drafts + methodology-doc banner re-centered to 1.25M; DN-001/DN-002/stale-median/Figure-6/composition/cost-per-job fixes applied; all numbers reconcile to `entry_headline_scenarios.parquet`.
- **Wave 4 — ship gate. ⏳ USER.** Fresh `/full-review` (5 agents) + `/review-style` on the updated drafts; resolve the `[TO VERIFY]`/`[TO FILL]` footnote citations (main draft 1–5); check `app/app.py` for the central entry figure; optionally regenerate fig07b on the evidence-central pool; `/cover-sheet`; final read-through.

## Verification (per `.claude/rules/verification-protocol.md`)

- [ ] `python -m pytest tests/` — static parity PASS (before and after).
- [ ] `01h` determinism: canonical pool byte-identical across two reruns; md5 unchanged vs pre-change (rank/penalty0/λ0.75 path untouched).
- [ ] 02g grid: realized ≈ target per cell (assert to 4 dp, as 01h already prints); 9 suffixed pools cleaned; canonical pool never overwritten.
- [ ] PI-3: entrant-hours sensitivity table populated for 3 modes; marginal/fully-loaded $/job recomputed.
- [ ] Manifest rebuilt; new parquets indexed; loader reads them.
- [ ] All figure refs in both drafts resolve; captions in order.
- [ ] Number re-verification: re-run the doc-number check against the new outputs (target 0 mismatches).
- [ ] Session log updated at each wave; delta note appended.

## Risks / notes

- **Perf:** 9 pool builds ≈ 1.5–4 min total (each 01h ≈ seconds); Tier 2, no gating.
- **Headline change propagates everywhere** — the re-center touches every entry/cost figure and both drafts; Wave 3 must move all numbers together to avoid new stale-number defects.
- **PI-3 may materially move the marginal-cost/FTE story** (independent-hours ≈ doubles entrant hours) but **not** the fiscal total (entrants are $3.3B of $93.1B) — the prose in draft §"cost per new job" must be re-checked against the sensitivity, not just updated numerically.
- **Determinism guard:** the new hours modes and grid use the existing hash-quantile pattern (salted), so all outputs stay byte-reproducible.
