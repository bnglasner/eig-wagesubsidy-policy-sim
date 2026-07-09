# Implementation Plan (REV 2): Entry-from-nonemployment remodel

**Date:** 2026-07-08 · **Status:** DRAFT rev2 — supersedes `2026-07-08_entry-from-nonemployment-implementation.md` (rev1, retained unmodified for the record); for user approval before any code changes
**Why a rev2:** the challenge/verification pass (`Infrastructure/specs/2026-07-08_entry-remodel-challenge-report.md`) overturned four load-bearing rev1 choices and corrected one feasibility fact (ASEC microdata is not on disk). Methodology detail: `Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md` (ST-1…ST-14).
**Spec:** `Infrastructure/specs/2026-07-08_entry-from-nonemployment-remodel.md` — still the governing spec; its M2 band mechanism, M3, M5, M7 directions stand. Its M4 mechanism (ASEC-match spouse income) is replaced per below.

## What changed from rev1 (summary)

| rev1 element | rev2 disposition | Driver |
|---|---|---|
| W2a "verify SSP/Paycheck-Plus numbers" | **DONE** this session (all primary-pinned; see challenge report item 1) | verification agents |
| W4: extend ASEC NN match for `spouse_income` exclusion restriction | **STRUCK.** ASEC microdata absent from repo; matched spouse income vacuous as instrument (ST-5/6); earner-file composition biased for the non-employed | data re-audit + ST-5/6 |
| (new) | **W4′: real in-ORG spouse link** (SERIAL/PERNUM/RELATE rosters; 96.6% linkable; spouse EMPSTAT all rotations) + own-child-under-5 derivation + row keys added to `01h` output | data re-audit |
| Net gate layered on gross λ-calibration | **λ-bisection itself calibrates on the net criterion**; stimulus basis moves net with it | ST-1, ST-2 |
| Linear `eps × mean(g)` bisection target | **Saturated person-level target** via `response_multiplier` + `ceiling_ext` | ST-11 |
| Row-order rank `u` | **Hash-of-person-ID rank** (fallback: seeded within-cell permutation), reused across edges | ST-10 |
| (absent in rev1) | **Conditional-Mills pool prediction** (`Xβ + ρσ·(−φ/(1−Φ))`), both variants reported | ST-7 |
| `other_women` band left "EITC/CBO-only" | **Widen lower to ~0.05, keep central 0.20 / upper 0.40, relabel provenance** (anchored both sides) | literature agent B |
| Household coordination deferred entirely | **Sensitivity row using spouse-employed flag** (crude, disclosed bound; not central-case) | data re-audit + Bonin mechanism |
| Verification step 1 "monotonicity not guaranteed" | Corrected: monotonicity of the 3 reservation columns **is guaranteed** under shared `u` — assert it as a test | ST-9/Q3a |

## Open design decisions — RESOLVED (user sign-off, 2026-07-08)

1. **Calibration route: NET-BASIS CALIBRATION.** The λ-bisection itself uses the net criterion `NI(package) ≥ NI(r·h)` (ST-1 primary fix). Accepted cost: `01h` acquires a dependency on the 02b schedule machinery and pool household keys.
2. **Band-value conversion conventions: (a) ANY-EMPLOYMENT margin** (matches the 80-80's any-hours design; SSP-implied eps ≈ 0.35–0.5 rather than the full-time 0.8–1.1); **(b) NET stimulus basis** (consistent with ST-2 and the net gate; EITC/CBO elasticities are net-return concepts). The *numeric* band values computed under these conventions still go to the W2c human checkpoint before entering config; the verified record supports a **modest** men upper edge (NYC pooled +2.8 ns / Y3 +5.8\*\*, diluted by the disadvantaged-subgroup share of the "men" cell, against Atlanta's precise null).
3. **`other_women` band: 0.05 / 0.20 / 0.40 ADOPTED** (lower edge widened from 0.10; central/upper retained) with the two-channel provenance labeling: household-phase-out negatives excluded as inapplicable; coordination channel bounds the lower edge near zero; PPE-cohabiting/PP-NYC-women anchor the upper.
4. **Household-coordination sensitivity: INCLUDE** as labeled sensitivity rows in the entry-margin reporting (spouse-employed entrants zeroed and halved variants) — a reported bound, never a central-case adjustment.
5. **Subsidy tax treatment: TAXABLE + COUNTABLE (current schedule behavior) RETAINED** as the headline design assumption. Must be stated explicitly in `docs/entry_from_nonemployment_methodology.md` (ST-3 disclosure), including the note that this partially re-introduces benefit-phase-out interactions the policy's public framing says it avoids — a deliberate, conservative modeling choice.
6. **Re-pull queue: APPROVED (two items; ATUS not queued):** (a) **SPLOC + NCHLT5** added to the CPS basic-monthly extract — closes the ~5% complex-household spouse-link gap and replaces the derived under-5 flag with the exact variable; (b) **ASEC re-pull including SPMCHXPNS/SPMCAPXPNS** — re-materializes the absent ASEC microdata and adds a childcare/work-expense proxy. Both remain permission-gated at execution time per DD-3 (state dataset/vintage/source before fetching). Sequencing: the small basic-monthly re-pull should run early (Wave 1, parallel to W4′ — if it lands first, W4′ uses SPLOC/NCHLT5 directly; otherwise W4′ ships with the RELATE-pairing/derived-flag versions and upgrades later); the ASEC re-pull can run in parallel and feeds household-composition precision in W6 and the M6 expense proxy. ATUS deferred to the M6 follow-on decision (W10).

## Workstreams (rev2)

| # | Workstream | Files | Depends on | Tier |
|---|---|---|---|---|
| W1 | M1 documentation + `cfg["matching"]["eps_ext_band"]` scaffold (placeholders = current values); ST-8/ST-9 disclosures drafted | `00_config.py`, `docs/entry_from_nonemployment_methodology.md` | none | 1 |
| W2b | Unit conversions from verified numbers (subgroup dilution for men; margin/basis per Decision 2); `other_women` per Decision 3 | analysis note only | Decisions 2–3 | 1 |
| W2c | **Human checkpoint:** sign off band values before they enter config | — | W2b | — |
| W3 | M3: `01h::_design` finer EDUC + STATEFIP (unchanged from rev1) | `01h` | none | 1 |
| W4′ | Spouse link + child-under-5 module: add YEAR/MONTH/SERIAL/PERNUM row keys to `01h` output; build `spouse_is_employed` (RELATE pairing, all rotations; ~5% unlinkable flagged), spouse earnings (MISH 4/8 sidecar), own/household under-5 flags | new `01i_household_links.py` (in-ORG; no ASEC) | none (parallel to W3) | 1–2 (roster groupby on ~1.1M rows — state runtime estimate first) |
| W5 | Reservation + imputation overhaul: (a) conditional-Mills pool prediction, both variants reported (ST-7); (b) selection equation adds spouse-employed×married + child-under-5; Puhani-style sensitivity (Heckman vs OLS vs Mills-variant) (ST-5/6 replacement); (c) hash-ranked `u` (ST-10) reused across edges; (d) λ-bisection per band edge on the **net, saturated, person-level** criterion (ST-1/2/11) — brings `_resolve_schedule`/`_ni_adjusted` and household keys into `01h`'s dependency chain; (e) p25/median MPL diagnostic vs documented expectation | `01h` | W2c, W3, W4′ | 1–2 |
| W6 | 02d gate consistent with W5's calibration; cliff handling: evaluate at offered package, grid-search `[w_e, y]` for net-clearing wage, report cliff-diagnostic count (ST-4); UI/timing disclosures + unemployed-vs-NILF split flag (ST-3); M7 quantile-matched entrant hours (unchanged); repoint or loudly label `_entrants_synthetic` and exclude synthetic path from band outputs (ST-13) | `02d` | W5 | 1 |
| W7 | Reporting: `entry_margin_band.parquet` (3 band rows at fixed beta=central/wage_mode=rigid) + **02b-vs-02d reconciliation table** (wedge attributed to population/form/basis/elasticity source, ST-12) + household-coordination sensitivity row (Decision 4) + 02b benchmark relabel avoiding `central` collision (ST-14) + band-scope disclosure (ST-9) | `02d`, docs | W6 | 1 |
| W8 | Verification: full re-run; **assert** pointwise monotonicity of the 3 reservation columns; determinism check; static parity test (unchanged expectation); delta note attributing the baseline shift to ST-7 vs ST-11 vs net gate — the three cut in different directions and must be separately attributed (run them in staged commits so each delta is isolable) | `tests/`, session log | W7 | 1–2 |
| W9 | Specialist reviews (methodology + code), parallel | — | W8 | — |
| W10 | Present; decide re-pull menu sequencing (Decision 6) | — | W9 | — |

## Execution waves

1. **Wave 1:** W1 + W3 + W4′ in parallel (all self-contained; W4′ states its runtime estimate before running).
2. **Wave 2:** W2b → W2c human checkpoint (band values; Decisions 2–3).
3. **Wave 3:** W5 (staged internally: ST-7 fix first and re-inspect the MPL distribution *before* calibrating bands — the imputation shift changes `g` and hence every downstream number).
4. **Wave 4:** W6 → W7.
5. **Wave 5:** W8 staged verification → W9 reviews → W10.

## Verification (revised from rev1)

1. `01h`: three reservation columns exist; **assert** `reservation_lower ≥ reservation_central ≥ reservation_upper` pointwise (guaranteed under shared `u`; violation = bug). Confirm hash-rank determinism and that markups no longer correlate with YEAR/MONTH (new check: correlation of `m` with survey month ≈ 0 within cell).
2. MPL diagnostic: conditional-Mills median must sit below the employed median (direction expected from ρσ>0); report both variants' p25/p50/p75.
3. `02d`: net-calibrated central induced entry equals the saturated net target by construction — verify the identity holds (this replaces rev1's "isolate the M5 delta" step, which is moot under the ST-1 fix); cliff-diagnostic count reported.
4. End-to-end re-run; static parity test unaffected (any failure = real regression).
5. Delta/replication note attributing the baseline shift to (a) ST-7 imputation, (b) ST-11 saturation, (c) net gate/basis, (d) band values — staged commits so each is isolable.

## Performance/cost

Highest tier: W4′ roster linkage (~1.1M raw rows, groupby-based — Tier 1–2; estimate before running) and W5's schedule-in-the-loop bisection (60 iterations × cell × 3 edges of interpolation on ~180k rows — vectorizable, Tier 1–2; if the schedule lookup proves heavy, precompute `NI(r·h)` on the schedule grid once per household key). No Tier 3/4 anticipated. No new data acquisition in this pass (Decision 6 items are all deferred and permission-gated).

## Completion criteria

- M1–M5, M7 implemented per above with M6 still explicitly deferred; all four blocking challenge findings (ST-1/2, ST-5/6/7, ST-10, ST-11) reflected in code; W2c sign-off obtained before any band value enters config; verification 1–5 pass; methodology and code reviews return no unresolved HIGH/CRITICAL findings.

## Evidence

- **Sources:** challenge report (`Infrastructure/specs/2026-07-08_entry-remodel-challenge-report.md`) and its cited primaries; methodology memo (`Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md`); data re-audit findings (session log `2026-07-08_entry-remodel-critical-reexamination.md`); code files as cited therein.
- **Confidence:** High that the four blocking rev1 defects are real and the fixes are correct in direction (read from code; independently reviewed). Medium on runtime tiers (not yet measured) and on the exact band values (deliberately deferred to W2c).
- **Assumptions:** pool row keys can be added to `01h` output without disturbing downstream consumers (only `02d` reads the pool; verify at W4′); the 02b schedule machinery is importable into `01h` without circular-dependency issues (both already load config the same way; verify at W5).
