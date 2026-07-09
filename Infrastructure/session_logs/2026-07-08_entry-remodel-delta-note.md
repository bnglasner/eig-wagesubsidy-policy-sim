# Delta / Replication Note — Entry-from-Nonemployment Remodel (implementation)

## Full-review + survey-weighting wave (2026-07-09, /orchestrate → /full-review + /review-style, user sign-off)

Six reviews (code, methodology, ai-skeptic, numbers, consistency, EIG style) run in parallel on the
re-centered drafts. Verdict: no fabrications (all citations web-verified), no correctness bugs, 104/118
numbers reconciled; residual HIGH findings were prose leftovers. User decisions → three actions:

- **MR-001 — survey-weighted Heckman now PRIMARY.** `01h`: selection probit weighted by WTFINL
  (GLM-probit freq_weights), wage OLS by EARNWT (WLS); unweighted kept as robustness with a
  Solon-Haider-Wooldridge (2015) justification (`EIG_HECKMAN_WEIGHTS=unweighted`; conditional pool
  median weighted $18.91 vs unweighted $20.10, persisted in diagnostics). Weighted pool is poorer
  (median MPL $18.28→$17.18; below-target 41.4%→47.8%) → headline rises.
- **MR-006/CC-003/AS-002 — PI-3 + stress on the evidence-central pool.** `02g` now recomputes
  `entrant_hours_sensitivity` on the evc pool and writes `entry_central_stress.parquet`
  (spouse-zeroed, take-up 0.80). 05z registers both.
- **Mechanical/style fixes.** Appendix §5 "0.83M central" leftover (CC-001/DN-001); Evidence-block
  clawback (CC-002); Fig 14 draft caption (CC-004); footnote-8 Krueger-Mueller reservation-vs-accepted
  attribution (AS-001); numerals-with-percent, `7/10/9 million` consistency, source-line org name,
  "evidence-central estimate". Deferred (disclosed pending): footnotes 6–8 Chicago→EIG format conversion
  and the `[TO VERIFY]` citation content (needs publication data).

**NEW HEADLINE (weighted primary): evidence-central 1.48M** (floor 1.02M; high 3.80M; grid 0.23–3.80M);
by group sm 0.24 / ow 1.06 / men 0.18; entrant gross $8.5B / net $6.2B; composition ~33% unemployed /
~3% disabled+retired; mean hours ≈976; clawback (evc pool) 19/27/24%; cliff ~1 in 9; rigid-central
$94.4B/$75.2B; all-renegotiate $161.7B; PI-3 marginal $5,731 rank / $10,261 independent; stress
spouse-zeroed 1.20M / take-up 1.19M. Both drafts + methodology-doc banner re-propagated and reconciled
to the live parquets; all figures regenerated. **Verification:** static parity PASS; canonical pool
deterministic (md5 `aab5b110…` byte-identical ×2); every draft number traces to `entry_headline_scenarios`/
`entry_central_stress`/`entrant_hours_sensitivity`/`matching_simulation`. Reports in
`Infrastructure/explorations/2026-07-09_recenter-review/review-reports/`.


## Re-center implementation — Wave 1 (2026-07-09, holistic-evaluation follow-up, user sign-off)

Plan: `Infrastructure/plans/2026-07-09_entry-model-recenter-implementation.md` (APPROVED). Decisions:
Option A re-center; scenario grid + full decomposition; PI-3 only (incumbent-basis/UI/fixed-cost
disclosed, not modeled). Locked params: status-differentiated penalty U:0.05/NILF:0.10/dis·ret:0.15
(mean ≈11%), λ=0.75 central, full 27-cell grid.

**Wave 1 code (done, verified):**
- `00_config.py` — added `cfg["matching"]["entry_recenter"]`, `["entry_scenario_grid"]`,
  `["entry_hours_modes"]`. No change to eps anchors or tax treatment.
- `02d` — added `hours_override` to `_entrants_from_pool`; `_entrant_hours_by_mode`
  (rank/independent/median); `entrant_hours_sensitivity` → `entrant_hours_sensitivity.parquet` (PI-3).
- **NEW `02g_entry_scenario_grid.py`** → `entry_scenario_grid.parquet` (27 cells) +
  `entry_headline_scenarios.parquet` (3 bundles). Reuses 01h env selectors (no 01h change) + 02d
  entrant calc. Builds 9 pools, cleans them, canonical pool preserved byte-identical.
- `run_all.py` — registered `RUN_02G_ENTRY_SCENARIO_GRID` after 02f. `05z` registry — 3 new stems.
- **No change to 01h** — all pool-variation mechanisms already existed; canonical pool md5
  unchanged (99ee7198…) before/after; rank hours-mode reproduces canonical entry_hours exactly.

**Wave 1 results:**
- Headline bundles: conservative_floor **0.83M** (labeled); **evidence_central 1.25M** (sm 0.20 /
  ow 0.91 / men 0.14; entrant gross $6.4B / net $4.5B); high joint corner **3.37M** (pen20×λ1.0×upper).
- 27-cell grid monotone in all axes; range **0.18–3.37M**; super-additive interaction confirmed
  (pen10×λ1.0 central = 1.51M > either lever alone).
- **PI-3 entrant_hours_sensitivity** (central edge): rank 768h / FTE 0.32M / $4,018 gross-$2,527 net
  per job; independent 1630h / 0.68M / $9,576-$5,630; median 1864h / 0.77M / $11,375-$7,127. The
  marginal-cost-per-job story is ~2.4× sensitive to the untested rank coupling (fiscal TOTAL barely
  moves — entrants are a few $B of ~$93B).
- Verification: static parity PASS; all 5 touched files compile; manifest 21 analysis-tables.

**Wave 2 — figures (done, rendered & verified):** re-pointed **fig14** (mpl_uncertainty) to the
27-cell scenario grid (penalty×λ×eps, evidence-central 1.25M called out); re-pointed **fig07**
(entry by group) to the 3 headline bundles (floor 0.83→evidence-central 1.25→high 3.37, by cell);
updated **fig10** (cost per job) hardcoded values to marginal $5.1K, fully-loaded $22K/$59K/$89K
(high/evidence-central/floor). fig12 (clawback) and fig08 (pool wage dist) left on the base pool
(consistent with prose). All render via Rscript 4.5.2; visually checked fig07/10/14.

**Wave 3 — prose (done):** both drafts + methodology-doc banner re-centered to 1.25M evidence-central
with 0.83M labeled floor, 3.37M high, two-sided-bias disclosure. Fixed DN-001 ($158→160.3B),
DN-002 (firm capture "under one percent"→1.5% at headline β), stale medians ($19.62–22.17→
18.28–20.65), "~0.5M"→1.25M, Figure 6 "reservation wage"→"entry threshold" caption, composition
wording (a third unemployed / ~3% disabled+retired), cost-per-job ($5,100 marginal / $59K
fully-loaded + PI-3 caveat), men 0.14M. All re-centered numbers reconcile to
`entry_headline_scenarios.parquet` and the evidence-central diagnostics.

**Verification:** static parity PASS; canonical pool md5 unchanged (99ee7198…) through all edits;
figures render clean.

**Consistency alignment (2026-07-09, post-Wave-3, user request):** the two figures that lagged the
re-center are now on the evidence-central pool. 02g persists `nonemployed_pool_evidence_central.parquet`
(data/processed) + `entry_central_composition.parquet` (population/). **fig12** (clawback) reads the
evidence-central pool → sm 15.5% / men 21.1% / ow 24.6% (was floor 13/15/18); **fig07b** (entrants by
status) reads the composition table → unemployed 0.412M (33%) / other-NILF 0.799M / disabled 0.028M /
retired 0.010M (~3%). Prose aligned in both drafts: clawback "about 15 / 25 / 21 percent" (was 14/19/15,
"a quarter of the advantage"→"a third"); cliff "roughly one in eight." Manifest = 22 analysis-tables.
Parity PASS; canonical pool still byte-identical.

**Remaining (Wave 4, user):** fresh `/full-review` + `/review-style` on the re-centered drafts;
resolve `[TO VERIFY]` citations; check `app/app.py` for the central entry figure; cover sheet.


## Reality-assessment implementation wave (2026-07-09) — HEADLINE REBASELINE

User approved the assessment's ranked recommendations; all implemented:
- **E2 — paid-hourly wage frame.** `01h` estimation sample = non-employed + paid-hourly earners (was: all earners incl. 44% salaried, median $26.00 vs the $21.00 paid-hourly frame the target prices). Effect: ρσ +0.297 → **+0.075** (much of the old "selection" was the salaried/hourly divide); imputation variants converge (medians $19.62/$20.97/$22.17 weighted) — **the MR-001 7× entry spread is resolved as frame contamination**; pool below target 55.9% → **31.0%** (vs workers' 23.6% — negative selection preserved). Honest note: the assessment predicted the fix would cut the other way; it did not.
- **E2 follow-on — non-employment wage-penalty band.** `EIG_MPL_PENALTY` in 01h; 02f now runs two axes: imputation {conditional 0.46M / mills0 0.39M / plain 0.25M} and penalty {10% → 0.71M, 20% → 1.18M} (Schmieder 0.8%/mo offer decay; KM accepted ≈0.90×). Penalty is the dominant MPL uncertainty.
- **E1 — status-aware entry lottery.** m_i = −ln(1−u)/（λ·s_i), s = status weight (unemployed 5.0 / nilf 1.0 / disabled 0.15 / retired 0.15; CPS flow ratios, MMS 2013) × probit propensity, mean-1 normalized (calibrated totals unchanged). Entrant composition: unemployed 9.4% → **35%**; disabled+retired 12.6% → **~1%**. Pool carries `prior_status`, `emp_propensity`; 02d reports entrants by status.
- **E5 — incumbent hours margin.** `cfg["matching"]["eps_int_band"]` {0.05/0.20/0.33}; new `02d::incumbent_hours_margin` → `incumbent_hours_margin.parquet`: added FTE {0.08/**0.25**/0.36}M, gross {+0.8/+2.4/+3.3}B, net {+0.3/+1.9/+1.7}B (upper net < central: added earnings push some households across cliffs → offsetting savings). In FTE terms the central hours margin (0.25M) EXCEEDS the entry margin (~0.17M FTE at 741 hrs).
- **E6 — take-up 0.80 sensitivity row** in entry_margin_band (0.37M central).
- **NEW HEADLINE:** entry central **0.46M** (eps band 0.13–0.85M; penalty to 1.18M) vs prior 1.42M. Rigid-central gross **$91.0B** / net **$72.5B** (was 97.2/77.5). Firm capture rigid 0.3–0.9% (fewer, cheaper entrants); flex bound ≤$158.0B/54.9%. Clawback medians (weighted, reachable): sm **8.2%** / ow 17.1% / men 11.8%. Marginal cost per entrant $2,826 gross / $870 net; fully-loaded $158k central → $61k at pen20. Cliff pay-up 0.109M (~24% of entrants). Mean entry hours ≈741.
- **Verification:** static parity PASS; 01h determinism byte-identical ×2; 02b untouched (0.72M benchmark); canonical pool never overwritten by 02f variants; manifest 21 intermediates (adds incumbent_hours_margin).
- **Docs:** methodology doc revision banner (4 changes + entry-resistance-residual language); draft fully renumbered (see below); assessment memos in explorations/.
- **Offer dispersion folded into headline (2026-07-09, latest — SECOND HEADLINE REBASE, user question "what is the primary barrier for men?"):** diagnosis showed the primary barrier was the conditional-MEAN imputation making reachability a deterministic cliff (73% of non-employed men offered $0; only 0.14M men imputed below $12; the model disputed "serious increase in pay" for most men). Fix (user-approved: group σ by educ×age / λ=0.75 central with {0.5,1.0} band / fold into headline): mean-preserving lognormal offer draws around the Mills-corrected conditional mean, group residual SDs 0.29–0.55, hash-quantile draws salted independently of the entry lottery. **New headline: entry 0.83M central** (eps 0.25–1.47M; dispersion 0.62–1.12M; penalties 1.21/1.70M; estock 0.71M; take-up 0.66M; spouse-zeroed 0.69M); below-target 41.4% (workers 23.6%); men 0.09M central (0.24 upper); by status: unemployed 38%, disabled+retired ~2%; rigid-central $93.1B/$74.2B; firm capture 0.8–2.0% rigid / ≤54.8% flex ≤$160.3B; clawback medians 14.4/18.9/14.9% (single-mother gap NARROWED vs mean-imputation era — disclosed honestly in draft); cliff pay-up 0.115M (1 in 7); marginal $3,976 gross/$2,530 net; fully-loaded $44k(pen20)–$89k(central) — now below the state/local incentive band; entry FTE 0.32M vs hours 0.25M; central ≈ the 1990s-EITC-scale benchmark (0.9M on the new reachable pool). E/R base ratios reconcile toward 1 (1.41/0.72/0.94). 02f now runs three axes (7 variants). Verification: parity PASS, determinism byte-identical ×2, suffixed pools cleaned. Both drafts + appendix + methodology banner updated; figures refreshed (fig14 three-axis, fig10 new values).
- **Session close (2026-07-09): holistic-evaluation handoff written** to `Infrastructure/plans/2026-07-09_entry-model-holistic-evaluation-handoff.md` — a self-contained fresh-thread prompt covering the current architecture (all six layers), the 2026-07-09 headline + full variant table, the file map, and nine evaluation questions incl. the open headline-centering decision (0.83M three-way-conservative central vs the 1.46M evidence-weighted mixture), one-at-a-time vs joint uncertainty, the men's-cell double-counting risk, stale W2c conversions, PI-3, status-weight sensitivity, the flipped 02b/02d relationship, and publication readiness. No further code changes this session.
- **Left-skew offer hypothesis tested (2026-07-09, user question):** implemented as status-conditioned penalty mixtures (`EIG_MPL_STATUS_PENALTY`; duration-heterogeneous decay: unemployed small per KM 0.90× accepted-wage evidence, long-detached groups large per compounded Schmieder decay) — the evidence-grounded generator of left skew, vs a parametric skewness knob. Two 02f variants (axis "skew"): moderate (U5/NILF15/DR20, mean ≈15%) → **1.46M** entry, 58.6% below target; heavy (U10/NILF25/DR30) → 1.99M. **Key finding: at matched mean penalty, the skew SHAPE is roughly neutral for the total** (1.46M ≈ the uniform-penalty interpolation at 15%) because the E1 status weights counteract it (bigger penalties make NILF/disabled more reachable, but their entry weights are lower); what the skew changes is the composition and the evidence interpretation (each group's discount maps to its spell-length distribution). Three supporting rationales documented incl. the acceptance-truncation point (σ estimated on accepted wages understates the offer distribution's low tail even at λ=1). Headline unchanged; variants persisted in `mpl_imputation_band.parquet` (now four axes, 9 variants); manifest updated. Also: our accepted-wage σ truncation argument implies even λ=1.0 is not a true upper bound on dispersion — noted for the record.
- **Base-semantics sensitivity added (2026-07-09, user question on Figure 7):** user asked whether elasticities estimated on larger bases were being applied to the shrunken reachable pool. Diagnosis: the elasticities are employment-RATE semantics (base = affected group's eligible EMPLOYED stock, E_c), while the calibration uses the reachable non-employed pool (R_c) — a convention that couples entry to the imputation frame's reachability (why the E2 fix moved entry so hard) and that flipped from generous (old frame E/R=0.64) to conservative (new frame E/R=1.14 aggregate; single mothers 2.32). Per user decision ("report both as a band"): pool now carries estock reservation columns (central edge recalibrated on target × E_c/R_c, feasibility-capped; unit bug fixed — R_c needed /n_months); `entry_margin_band.parquet` gains the "employment-stock semantics" row (**total 0.52M vs 0.46M; single mothers 0.12M vs 0.05M**); Fig 7 gains the marker; Table 4 + prose + tech appendix §5 + methodology doc banner all updated. Parity passes; existing rows byte-consistent.
- **Technical appendix drafted (2026-07-09):** `drafts/2026-07-09_technical-appendix.md` — reader-friendly companion walking through the full modeling chain (data foundation, two-model design, pool composition, paid-hourly imputation frame + penalty band, net-gain entry decision + status-weighted lottery + elasticity provenance table, hours margin, bargaining/incidence, safety-net interaction, limitations, uncertainty table, reproducibility) with per-decision sourcing labeled accounting / transported evidence / disclosed judgment. Linked from the main draft's "How sure are you?" section. All numbers from the 2026-07-09 run; citations author-date prose (convert to EIG footnotes if it ships publicly).

**Date:** 2026-07-08 · **Baseline:** `2026-07-08_replication_targets.md` · **Plan:** rev2 (all user decisions signed off, including W2c band values)

## Verification results (W8)

| Check | Result |
|---|---|
| Reservation-column pointwise monotonicity (lower ≥ central ≥ upper) | **PASS** (asserted in 01h; guaranteed under shared hash-rank u) |
| Calibration identity (realized viable share = saturated net target, per cell × edge) | **PASS** (equal to 4 decimals, printed per run) |
| ST-10 fix: corr(markup, survey month) | **+0.008 ≈ 0** (pre-fix: rank deterministically increasing in month) |
| Determinism: 01h rerun → pool parquet md5 | **PASS** (byte-identical: `e5b09cc3…`) |
| `tests/test_behavioral_static_parity.py` | **PASS** |
| 02b re-run vs baseline (all four scenarios, gross/net/induced) | **MATCH — no drift** (02b untouched, as designed) |
| Induced entry invariant across beta grid | **PASS** (1.42M in all six 02d rows; gate is at max package by construction) |

## Headline deltas (beta=central, rigid, central band edge)

| Quantity | Pre-remodel | Post-remodel |
|---|---|---|
| Pool MPL p25/p50/p75 (weighted) | 15.53 / **21.00** / 28.18 | 12.00 / **15.92** / 20.72 |
| Share of pool with MPL < $16.80 | 30.9% | 55.9% |
| Induced entry (central) | 0.94M | **1.42M** (band 0.44–2.47M) |
| — single_mothers / other_women / men | 0.069 / 0.778 / 0.088 | 0.23 / 1.03 / 0.16 |
| 02d gross / net cost (rigid-central) | $102.0B / $78.4B | **$97.2B / $77.5B** |
| Entrant hours | 2,000 flat | quantile-matched, mean ≈ 880/yr |

## Delta attribution (A → B → C decomposition)

- **A. Old rule, old MPL (baseline): 0.935M.**
- **B. Old linear-gross rule, new conditional-Mills MPL: 1.92M** (+0.99M). The ST-7 imputation fix (selection-consistent conditional-mean prediction; pool median $21.00 → $15.92) roughly doubles reachable mass (30.9% → 55.9% below target) and would have doubled entry on its own.
- **C. New saturated + net-basis rule, new MPL (final): 1.42M** (−0.50M vs B). The ST-11 saturating person-level response and the ST-1/ST-2 net-of-transfer basis together pull half of that back — most sharply for single mothers, whose median net stimulus (g_net ≈ 0.13) is about half the men's/other-women's (≈ 0.25) because benefit phase-outs claw back subsidy value under the taxable+countable design assumption.
- Net effect: +0.49M vs baseline. The two prior-session-invisible corrections cut in opposite directions, exactly as predicted in the challenge report (item 10); the imputation fix dominates.
- Costs move little despite more entrants (gross $102.0B → $97.2B) because quantile-matched entrant hours (mean ≈ 880/yr vs the old flat 2,000) roughly halve per-entrant subsidy dollars, and 0.14M entrants clear reservation only via above-Nash "pay-up" wages (cliff diagnostic, reported in `entry_margin_band.parquet`).

## Design change vs the rev2 plan text (documented mid-implementation)

The plan's net gate `NI(package) ≥ NI(r·h)` proved **non-monotone in the markup** in exactly the way ST-4 warned, but harder: benefit-cliff troughs in NI() put a hard *floor* on the viable share (single mothers ≈ 0.44 at any λ), making calibration infeasible. Reformulated in **net-gain space** — viable iff `NI(package) − NI(0) ≥ (1+m)·max(NI(y·h) − NI(0), $1,000)` — which is monotone in m by construction and collapses to the closed form `m ≤ g_net`. Same net basis, same schedules, well-posed calibration. Recorded in `docs/entry_from_nonemployment_methodology.md` #3.2; flagged for the W9 methodology review to scrutinize.

## Post-review fixes (W9, same day)

- **Code review** (`Infrastructure/explorations/2026-07-08_entry-remodel-code-review.md`): CE-001 HIGH (01i missing from `run_all.py` — registered with `RUN_01I_HOUSEHOLD_LINKS`, sequenced before 01h), CE-002 MEDIUM (`weight_override` now applied before row filtering), CE-003 LOW (NaN-truthy fallback ladder → `_first_finite`), CE-004 LOW (`hh_other_nonemployed_adult` self-exclusion arithmetic). Outputs verified byte-identical after CE fixes.
- **Methodology review** (`.../2026-07-08_entry-remodel-postimpl-methodology-review.md`): net-gain reformulation judged **SOUND** ("an improvement over the plan text" — the gross form made high-EMTR people viable at any markup, economically backwards); conditional-Mills math verified; gate reproduces calibration exactly; no ST-6 artifact. **PI-1 HIGH fixed:** entrant firm capture was `(1−β)·subsidy`, which only holds at the interior Nash wage — 59.7% of central entrants are pinned at the $7.25 floor. Corrected to actual firm surplus `(y − w_final)·h`. Rigid-mode firm capture: 2.1–5.8% → **1.6–3.5%** of gross ($1.6–3.5B); flex worst case 55.6% → 54.3%. Entry counts and gross/net costs unchanged; parity test passes. **PI-6** implemented (pool now carries `is_unemployed` for the UI-disclosure split). **PI-3 MEDIUM open:** entrant-hours mapping sensitivity required before publication (flagged in the draft's Evidence section). **PI-5/PI-8 noted** (delta stages bundled; stale comment fixed).
- Pool parquet md5 changed by the `is_unemployed` column addition (schema change, values unchanged); determinism re-verified within the new schema via identical consecutive stats.

## Figures + output-hygiene wave (2026-07-08, later)

- **13-figure EIG R/ggplot2 suite** built on a reusable harness (`code/05_figures_tables/eig_fig_utils.R`) + drivers `05c_core_figures.R` (Figs 1–6 core) and `05d_supporting_figures.R` (Figs 7–13), using the canonical EIG R theme/tokens. Choropleth regenerated in R (tigris/sf), superseding the Python `05b` (now deprecated, retained as the app's interactive-choropleth pattern source). Figures renumbered to draft reading order (fig01…fig13). PNG (300 dpi) + SVG in `output/figures/main/`.
- **Output-hygiene assessment** (`Infrastructure/explorations/2026-07-08_pipeline-output-hygiene-assessment.md`) + proportional fixes implemented:
  - **H1** — `01h` now persists `data/processed/nonemployed_pool_diagnostics.json` (Heckman IMR/smearing, pool MPL percentiles across all three imputation variants, per-cell/edge calibration target-vs-realized, g_net guards, corr(markup,month)).
  - **H2** — `02d` flattens per-scenario dicts into `matching_simulation.parquet` (induced entry by cell, cliff pay-up, mean entry hours for all six rows, not just central-rigid).
  - **H3** — `02e` (take-up) and the R figure step (`05c`/`05d` via Rscript) + manifest builder (`05z`) wired into `run_all.py`; `05b` deprecated.
  - **Easy-grab mechanism** — `code/05_figures_tables/05z_build_manifest.py` writes `output/data/intermediate_results/population/_manifest.csv` (file/producer/rows/columns/role/description; 16 analysis-tables, 2 deprecated, 1 diagnostic), and `code/_utils/intermediates.py` gives `list_intermediates(role=)` / `load(stem)` so figures/tables grab by stem.
  - Left as flagged recommendations (not implemented): M2 delete orphaned 02c outputs, M3 stale matched pipeline (needs ASEC re-pull), and a full STAGE_OUTPUT_CONTRACTS doc.
- **Post-hygiene verification:** 01h determinism (md5 stable across reruns), 02b static parity test passes, entry/cost values unchanged, all 13 R figures re-render against the updated parquets. New `is_unemployed` pool column (PI-6) changed the pool md5 vs the pre-hygiene value; data values are identical.
- **Figures renumbered to draft reading order** (fig01…fig13) and **integrated into the draft** at their sections with sequential bold captions and prose references (verified: 13 references, all paths resolve, captions 1–13 in order). `code/05_figures_tables/FIGURES_README.md` documents regeneration + R package deps. `kaleido` was a transient install for the deprecated Python 05b and is not a pipeline requirement (R is canonical; plotly stays pinned for the app).
## Full-review pass + fixes (2026-07-08, later)

`/full-review` on the draft produced 5 HTML reports in `drafts/review-reports/` (0 CRITICAL; 1 HIGH; number verification 106/125 exact, no mismatches; AI-skeptic Trust=CAUTION, no fabrications). Three findings actioned per user direction:

- **MR-001 (HIGH) — modeling extension DONE.** The Heckman MPL imputation has no clean exclusion restriction (identified off IMR functional form). Added `EIG_MPL_IMPUTATION` selector to `01h` (default `conditional` → canonical pool byte-identical; `mills0`/`plain` write suffixed pools) and new `02f_mpl_imputation_band.py` that rebuilds the pool under all three imputations and reports the entry/cost spread → `mpl_imputation_band.parquet`. **Result:** induced entry 1.42M (conditional, headline) / 0.69M (Mills=0) / 0.20M (plain OLS); pool median MPL $15.92 / $20.90 / $25.70; below-target 55.9% / 31.4% / 15.3%. Disclosed in the draft's "How sure are you?" as a genuine uncertainty source. Wired into `run_all.py` (02f) and the manifest.
- **CC-001 (MEDIUM) — fixed.** Draft clawback percentages corrected from the stale memo values (13% / 25%) to the current weighted medians that Figure 12 plots (single mothers ~15%, other groups ~25–28%), resolving the body-vs-figure contradiction. "Roughly half" narrative retained (consistency reviewer confirmed it holds).
- **AS-002 (MEDIUM) — fixed.** Figure 11b subsidized-hours cap changed 2,000 → **2,080** (40 hr/wk × 52 wk) to match the pipeline (`ws_subsidy_hours_cap * 52`). Re-rendered; cap line relabeled "2,080 hrs/yr", caption note clarified (50-week x-axis, 2,080-hour cap). New anchors: 20/40 hr/wk gains unchanged (+$7,817 / +$5,628); 60 hr/wk crossover value −$2,307; crossover now 53.0 hr/wk. Draft Fig 11b prose updated (cap description; "roughly 53 hours").

Post-fix verification: 02b static parity passes; canonical `nonemployed_pool.parquet` byte-identical (02f writes/cleans suffixed variants only); manifest rebuilt (17 analysis-tables incl. `mpl_imputation_band`, 2 deprecated, 1 diagnostic); loader reads the new band; all 14 draft figure refs present and in order.

## Entry-model reality assessment (2026-07-09, user gut-check)

User challenged (A) pool MPL levels vs the hourly median and (B) the small extensive-margin effect. Full assessment: `Infrastructure/explorations/2026-07-09_entry-model-reality-assessment.md` (synthesis), `...-methodology.md` (plausibility memo), + 7 new primary-verified literature entries (Grogger 2003, Fang-Keane 2004, Krueger 2017, Maestas-Mullen-Strand 2013, Hall-Mueller 2018, Fehr-Goette 2007, Schmieder et al. 2016; catalog 73 entries).
- **Intuition A VALIDATED:** MPL equation estimated on ALL earners (median $26.00, 44% salaried) vs paid-hourly target frame ($21.00) → MR-001 band edges asymmetrically implausible (plain-OLS 0.20M not credible); disabled/retired get near-population imputed wages.
- **Intuition B: count partially refuted, composition validated.** 1.42M = 4.4pp of reachable — above the 1990s-EITC-alone precedent (~3.5-4pp/6yrs), between Paycheck Plus and SSP; realistic entry-risk set ~10-15M (Krueger 2017 health barriers; MMS 2013 SSDI capacity) → 10-15% yield. BUT 68% of modeled entrants are 16-24 NILF-other, 12.6% disabled/retired, only 9.4% unemployed (hash-uniform rank artifact); median-man implied markup 15.6× (don't call these "reservation wages").
- **Most evidence-indicted element: the intensive margin** — eps_int=0.05 is an EITC design artifact; clean no-phase-out evidence supports ~0.2-0.33; 8.2M part-time incumbents face a 25-54% marginal-hour raise modeled at ≈0 (0.15-0.7M FTE unmodeled).
- **Ranked further work:** (1) re-estimate wage eq on paid-hourly frame + rerun MR-001 band (~1d); (2) incumbent hours margin in 02d (~1-2d); (3) status-aware entry propensity + entry-by-status reporting (~1-2d); (4) asymmetric band + precedent-ladder presentation; (5) take-up scalar + ramp-in language; (6) immediate prose fixes. No model changes made this pass (assessment only).

## Figure 11b added (`fig11b_net_income_by_hours`, in `05d`): net income vs annual hours (0–3,000 = 60 hr/wk × 50 wk) at a fixed $10/hr for the single_2c_PA household, with vs without the subsidy. Anchors verified (20 hr/wk gain +$7,817; 40 hr/wk NI_no $66,811 / NI_sub $72,440; 60 hr/wk crossover to −$2,394). **Notable finding surfaced:** under the taxable+countable treatment (Decision 5), the with-subsidy net-income curve CROSSES BELOW the no-subsidy curve at ~2,694 annual hours (53.9 hr/wk) — counting the subsidy as income pushes the household across the Medicaid/childcare cliffs, making the subsidy net-negative at very high hours for this illustrative household. Placed after Figure 11 in the safety-net section with honest prose tying it to the statutory-treatment design choice. Suite now 14 figures.

## New outputs

- `data/processed/household_links.parquet` (01i: real spouse links, 312,282 linkable; child-under-5 flags)
- `data/processed/nonemployed_pool.parquet` — new schema: person keys, spouse/child flags, `entry_hours`, `g_net`, `ni_zero`, `net_gain_base`, `reservation_wage_{lower,central,upper}` (+alias), `required_net_gain_{lower,central,upper}`
- `output/data/intermediate_results/population/entry_margin_band.parquet` (3 band rows + 2 coordination-sensitivity rows)
- `output/data/intermediate_results/population/entry_reconciliation.parquet` (02b 0.72M vs 02d 1.42M with wedge attribution)
