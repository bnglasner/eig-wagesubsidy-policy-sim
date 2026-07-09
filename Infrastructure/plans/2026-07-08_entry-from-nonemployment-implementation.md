# Implementation Plan: Entry-from-nonemployment remodel (M1–M7, M6 deferred)

**Date:** 2026-07-08 · **Status:** DRAFT — for user approval before any code changes
**Spec:** `Infrastructure/specs/2026-07-08_entry-from-nonemployment-remodel.md` (REVISED, two evaluation rounds)
**Prior plan (evaluation routing, complete):** `Infrastructure/plans/2026-07-08_entry-from-nonemployment-remodel.md`

## Objective

Implement the spec's resolved items: replace the equality-solved extensive-margin calibration with a literature-informed band (M2), strengthen the participation/wage equation (M3, M4), move entrant viability to a net-of-transfer basis (M5), and give entrants a data-informed hours distribution instead of a fixed 2,000 (M7). Document throughout (M1). **M6 (fixed cost of work) is explicitly excluded from this pass** — it is blocked on a new ATUS acquisition per the spec, sequenced separately.

## Open design decisions requiring your confirmation (read before approving)

These are not fully resolved by the spec and I am not deciding them unilaterally:

1. **Verify before calibrating.** The two candidate band-anchor numbers — the SSP (Card-Hyslop) employment effect and Paycheck Plus NYC's 5.8pp "disadvantaged men" estimate — are **both flagged `[unverified]`** in their own literature summaries (secondary-source figures, primary tables unreadable via fetch). I am treating primary-source verification of these two numbers as a **hard prerequisite** (Wave 2a) before any `eps_ext`-band value is computed or wired into config. If verification fails or the primary source remains inaccessible, I will say so explicitly rather than proceed on the secondary number.
2. **`other_women` cell has no wage-subsidy-specific anchor.** Card-Hyslop is about single parents; Paycheck Plus/Parents' Fair Share are about men. Proposed default: **leave `other_women`'s band unchanged, explicitly labeled EITC/CBO-only** (no new upper-anchor evidence). Flag if you want a separate targeted literature check instead.
3. **Net-of-transfer viability formula (M5).** Proposed: compare the **net gain** of taking the job (`NI_schedule(employer_earned + subsidy) − NI_schedule(0)`) against the **net gain the reservation wage implies** (`NI_schedule(r_i × hours) − NI_schedule(0)`), both run through the same PolicyEngine schedule — rather than independently re-deriving a "net reservation wage." This keeps `r_i` on the same gross-wage-equivalent basis M2/M4 calibrate it on, while making the *comparison* net-of-transfer, which is what the source articles actually argue for.
4. **Reporting structure for the band.** Proposed: keep `02d`'s existing 6-row (wage_mode × beta) headline grid computed at the **central** `eps_ext` band point (unchanged shape), and add a **new small table** `entry_margin_band.parquet` (3 rows: lower/central/upper `eps_ext`, at fixed beta=central/wage_mode=rigid) isolating the extensive-margin uncertainty on its own. Alternative: full cross-product (3 × 2 × 3 = 18 rows) — more thorough, harder to read. Recommend the separate-table approach.
5. **New config namespace.** Proposed: `cfg["matching"]["eps_ext_band"] = {"lower": {...}, "central": {...}, "upper": {...}}`, **separate** from `cfg["behavioral"]["scenarios"]`. This keeps `02b`'s existing EITC/CBO-benchmark scenario table untouched (per the spec's Scope Note — `02b` is not claiming to be structural, and continuing to use the literal literature values there is fine) while giving `02d`/`01h` their own band, avoiding the current implicit coupling (`01h` currently hardwires `cfg["behavioral"]["scenarios"]["central"]`).

## Workstreams

| # | Workstream | Files | Depends on | Tier |
|---|---|---|---|---|
| W1 | M1 documentation scaffolding + new config namespace (scaffold only, placeholder values) | `code/00_setup/00_config.py`, inline comments in `01h`/`02d`, new `docs/entry_from_nonemployment_methodology.md` | none | 1 |
| W2a | **Verify** SSP and Paycheck Plus NYC primary-source figures | literature verification (may need a targeted agent pass) | none | 1 |
| W2b | Compute candidate `eps_ext_band` values from verified figures; confirm `other_women` treatment | analysis only, no code | W2a | 1 |
| W2c | **Human checkpoint:** present candidate band values for sign-off | — | W2b | — |
| W3 | M3: extend `01h::_design` with `STATEFIP` + finer `EDUC` | `code/01_data_preparation/01h_nonemployed_pool.py` | none (parallel to W1/W2) | 1 |
| W4 | M4 (exclusion restriction): extend ASEC match to the non-employed pool for `spouse_income` | new `code/01_data_preparation/01i_match_nonemployed_to_asec.py` (mirrors `01e`) | W3 (shares the pool-loading path) | 2 (nearest-neighbor match, ~182k rows — runtime-estimate before running) |
| W5 | M2: band mechanism in `01h::assign_reservation` (3× λ-solve, 3 reservation columns); M4 plausibility check (p25 diagnostic) | `code/01_data_preparation/01h_nonemployed_pool.py` | W2c, W3, W4 | 1 |
| W6 | M5: net-of-transfer viability in `02d::_entrants_from_pool`; M7: quantile-matched entrant hours from `hourly_workers.parquet` | `code/02_descriptive_analysis/02d_matching_simulation.py` | W5 | 1 |
| W7 | New reporting: `entry_margin_band.parquet`; docstring/doc updates disclosing household-coordination and subgroup-heterogeneity limitations | `code/02_descriptive_analysis/02d_matching_simulation.py`, `docs/entry_from_nonemployment_methodology.md` | W6 | 1 |
| W8 | Verification: full pipeline re-run, static parity test, new sanity checks, delta/replication note | `tests/`, `Infrastructure/session_logs/` | W7 | 1–2 |
| W9 | Specialist review: methodology (calibration + exclusion-restriction validity + net-of-transfer formula), code (new script + refactors) | `.claude/agents/methodology-reviewer.md`, `.claude/agents/code-reviewer.md` | W8 | — |
| W10 | Present results; decide M6/ATUS sequencing as a follow-on | — | W9 | — |

## Execution Waves

1. **Wave 1 (now):** W1 (docs/config scaffold) and W3 (STATEFIP/EDUC extension) can start immediately and in parallel — both are self-contained, low-risk changes to `01h` with no interdependency on the band mechanism.
2. **Wave 2 (parallel to Wave 1):** W2a (verify SSP/Paycheck-Plus primary figures) → W2b (compute candidates) → **W2c human checkpoint** — do not proceed to W5 until you sign off on the numbers.
3. **Wave 3:** W4 (ASEC-match extension for spouse income) — Tier 2, state the actual runtime estimate before running the nearest-neighbor match on ~182k rows.
4. **Wave 4:** W5 (band mechanism + plausibility check) — needs W2c's signed-off values, W3's design-matrix extension, and W4's spouse-income column.
5. **Wave 5:** W6 (net-of-transfer viability + entrant hours) → W7 (new reporting + disclosures).
6. **Wave 6:** W8 verification (full re-run, parity test, new checks, delta note) → **do not proceed to W9 if the parity test or any new sanity check fails; isolate and report.**
7. **Wave 7:** W9 specialist reviews (methodology + code), run in parallel. → W10 present + decide M6/ATUS sequencing.

## Concrete code changes

### W1 — Config + docs scaffold
- `00_config.py`: add `cfg["matching"]["eps_ext_band"] = {"lower": {...}, "central": {...}, "upper": {...}}` with **placeholder values equal to the current `central`/`lower`/`upper` `eps_ext` entries** until W2c confirms real numbers — never ship unconfirmed literature-derived numbers silently.
- Add inline comments at every point `01h`/`02d` reads `eps_ext` or `cfg["behavioral"]["scenarios"]`, stating literature role (target/prior/bound) per M1.
- New `docs/entry_from_nonemployment_methodology.md`: band provenance (which source anchors which edge, per cell), the two disclosed limitations (household coordination unmodeled; "men" cell can't be split by disadvantage/custodial status with current data), and a pointer to the spec.

### W2 — Verify, compute, checkpoint
- W2a: confirm the SSP employment-effect magnitude and the Paycheck Plus NYC 5.8pp figure against primary sources (MDRC/Econometrica tables), not secondary summaries. If a primary source stays unreadable via fetch, say so plainly and treat the number as unusable for calibration (fall back to a documented qualitative "meaningfully wider" band rather than a false-precision figure).
- W2b: `eps_ext_implied ≈ Δemployment_share / mean_g_experienced_by_treatment_group`, using each program's own documented generosity (SSP: ~doubling earnings, g≈1.0 conditional on full-time work; Paycheck Plus: credit increment ≈ $1,500/yr over the ~$500 control baseline, relative to the treatment group's earnings — needs the primary report's earnings baseline, not assumed).
- W2c: present candidates + `other_women` default to you; get explicit sign-off before they enter `00_config.py`.

### W3 — `01h::_design`
- Expand `_EDUC_MAP`-equivalent granularity used inside `_design()` (or add a parallel finer factor) using the full IPUMS EDUC code set already loaded (confirmed present, all 16 codes).
- Add `STATEFIP` as a categorical covariate in both the wage equation and the selection equation (confirmed populated, no sparsity issue).
- Re-run the Heckman fit diagnostics (existing `print` block) to confirm the fit still converges and note any change in the IMR coefficient (currently +0.296) — a stronger, more negative-selection-consistent IMR would be a good sign this is working, not required to "succeed" on any threshold.

### W4 — New `01i_match_nonemployed_to_asec.py`
- Mirror `01e_match_org_to_asec.py`'s existing `NearestNeighbors` (ball-tree, single neighbor) approach, applied to the non-employed pool instead of the eligible-worker pool.
- Output: `asec_spouse_income`, `asec_n_children` (reuse exact field names from `01e` for consistency) attached to `nonemployed_pool.parquet`'s upstream rows (or a sidecar joined by a stable row key).
- State the runtime estimate before running (Tier 2 per performance-cost-governance) — ~182k rows nearest-neighbor match; `01e`'s existing runtime on the smaller eligible-worker pool is the baseline reference point to extrapolate from.

### W5 — `01h::assign_reservation` band mechanism
- Generalize the existing bisection so it runs once per band edge (`lower`/`central`/`upper`) per cell, reading `cfg["matching"]["eps_ext_band"][edge][cell]` instead of the single hardwired `cfg["behavioral"]["scenarios"]["central"]["eps_ext"]`.
- **Reuse the same per-person rank `u`** (already deterministic) across all three edges — only `λ_c` differs — so the three reservation columns (`reservation_wage_lower`, `reservation_wage_central`, `reservation_wage_upper`) are the *same* individuals, just three consistent draws, not three independent random pools. This is a small, cheap change (bisection is not the expensive step; the Heckman/MPL imputation, unchanged, still runs once).
- Add spouse income to the selection-equation design matrix (`Xsel` in `heckman_impute`) as a new exclusion restriction, alongside the existing married/nchild dummies (do **not** add it to the wage equation — spouse income should affect participation, not the individual's own wage).
- Add the p25 plausibility-check diagnostic: print/log the resulting non-employed MPL distribution's percentiles against a documented expectation (e.g., "median non-employed MPL should sit meaningfully below the employed median" — currently it does not, at $21.00 = the employed median exactly), so a future run can see at a glance whether the added exclusion restriction improved this.

### W6 — `02d::_entrants_from_pool` and hours
- Replace the gross-wage viability test with the net-of-transfer formula from Open Decision #3, using the pool's `family_type_key`/`state_code` (or the ASEC-matched, higher-precision household fields from W4 if ready) to key into `_resolve_schedule`.
- Replace fixed `ENTRY_HOURS` with quantile-matched hours: rank each entrant's `mpl` within their cell's non-employed distribution, map that percentile to the same percentile of `hours_epi`/`annual_hours` among **incumbents in the same cell** (`hourly_workers.parquet`), per M7's confirmed (cell) or (cell × wage-bracket) granularity — not (state × cell), which is too sparse.

### W7 — Reporting + disclosure
- New `entry_margin_band.parquet`: 3 rows (lower/central/upper `eps_ext`), `induced_M`, `gross_cost_bn`, `net_cost_bn`, computed at fixed `beta=central`, `wage_mode=rigid`, so the table isolates extensive-margin uncertainty cleanly from the existing bargaining-power sensitivity.
- Update `02d`'s module docstring and `01h`'s header comment to state the band's provenance and the two disclosed limitations (per M1/W1).

## Verification (per `.claude/rules/verification-protocol.md` and the replication-first protocol)

1. Re-run `01h` → confirm 3 reservation-wage columns exist, are monotonic in the expected direction (`reservation_wage_lower ≤ reservation_wage_central ≤ reservation_wage_upper` is **not** guaranteed by construction — check whether it should be and assert it if so), and that the central-band induced-viable share is in the same ballpark as today's baseline (women/single_mothers central unchanged; men central unchanged — only upper/lower edges move).
2. Re-run `02d` → confirm `entry_margin_band.parquet` writes cleanly; confirm the existing 6-row grid's **central**-band numbers shift from today's baseline **only because of M5** (net-of-transfer viability), not because of an accidental central-value change in M2 — isolate and attribute the delta.
3. Re-run `01a → 01h → 02a → 02b → 02d` end-to-end; confirm `tests/test_behavioral_static_parity.py` still passes (it depends only on `01a`/`02a`/`02b`, none of which change in this plan, so it should be unaffected — treat any failure as a real regression, not expected).
4. Add new automated checks: determinism (re-running `01h` with unchanged inputs reproduces identical reservation columns), and a monotonicity/sanity assertion on `entry_margin_band.parquet` (or an explicit documented note if lower/central/upper are not guaranteed monotonic in cost).
5. Write a delta/replication note in `Infrastructure/session_logs/` documenting the pre- vs. post-change baseline shift (expected, from M5's net-of-transfer correction and M2's band-vs-equality change) — same convention used for the ORG-internalization baseline shift earlier this project.

## Performance/Cost Tier Notes

- Highest expected tier: **Tier 2** (W4's nearest-neighbor ASEC match on ~182k non-employed rows). State the runtime estimate before running; `01e`'s existing runtime on the smaller eligible-worker pool is the reference point.
- Everything else (band bisection, viability formula, quantile-matched hours) is cheap, vectorized, sub-second-scale — Tier 1.
- No Tier 3/4 step anticipated; no IPUMS re-extract needed (uses data already internalized in `code/00_ingest/`).

## Completion Criteria

- M1–M5, M7 implemented per the concrete changes above; M6 explicitly not attempted this pass.
- W2c sign-off obtained before any literature-derived number enters `00_config.py`.
- Verification steps 1–5 pass; static parity test unaffected; delta note written.
- Methodology and code reviews return with no unresolved HIGH/CRITICAL findings.
- Spec's Success Criteria and remaining Clarity Status items closed or explicitly re-flagged.

## Next Action

Await your sign-off on the five Open Design Decisions above (especially #1, the verify-before-calibrate gate), then begin Wave 1 (W1 + W3, parallel, low-risk) and Wave 2a (verification) simultaneously.
