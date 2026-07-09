# Post-Implementation Methodology Review: Entry-from-Nonemployment Remodel

**Date:** 2026-07-08
**Author:** methodology-reviewer (focused post-implementation audit, W9)
**Under review:** implementation of `Infrastructure/plans/2026-07-08_entry-from-nonemployment-implementation_rev2.md`
**Predecessor memo:** `Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md` (ST-1…ST-14)
**Code read:** `code/01_data_preparation/01h_nonemployed_pool.py`, `code/01_data_preparation/01i_household_links.py`, `code/02_descriptive_analysis/02d_matching_simulation.py`, `code/02_descriptive_analysis/02b_behavioral_scenarios.py` (schedule/response machinery), `code/00_setup/00_config.py`, `docs/entry_from_nonemployment_methodology.md`, delta note `Infrastructure/session_logs/2026-07-08_entry-remodel-delta-note.md`

Read-only review; no code or data in the project lane was modified. Verification scripts were run from `temp/` against the produced parquet outputs (see Evidence). Findings are tagged PI-1…PI-14 with HIGH/MEDIUM/LOW severity; per scope, I err on the side of flagging.

---

## Verdict summary

| Q | Topic | Verdict | Key findings |
|---|-------|---------|--------------|
| Q1 | Mid-implementation net-gain-space gate reformulation | **SOUND** (with disclosures) | PI-4 (MEDIUM), PI-7 (LOW), PI-8 (LOW) |
| Q2 | Conditional-Mills pool imputation | **SOUND** (math verified; one sample-definition caveat) | PI-2 (MEDIUM) |
| Q3 | Selection-equation shifters (spouse-employed×married, child-under-5) | **SOUND** (no ST-6 artifact) | PI-13 (LOW) |
| Q4a | 02d gate reproduces calibration; pay-up grid | **SOUND** (identity verified empirically) | PI-7 (LOW, shared) |
| Q4b | Entrant firm-capture accounting | **FLAWED-FIXABLE** | **PI-1 (HIGH)** |
| Q5 | Quantile-matched entrant hours | **FLAWED-FIXABLE** (sensitivity required before publication) | PI-3 (MEDIUM), interacts with PI-4 |
| Q6 | Delta attribution A→B→C | **SOUND** (as sequential decomposition; staging incomplete vs plan) | PI-5 (MEDIUM) |
| Q7 | New concerns / disclosure coverage | Mostly adequate; one plan deliverable missing | PI-6 (MEDIUM), PI-9/10/11/12/14 (LOW) |

**Bottom line:** the mid-implementation design change is not merely acceptable — it is a genuine improvement over the plan's formula, and the reasons are economically substantive, not just numerical (see Q1). The one HIGH finding is unrelated to that change: the entrant firm-capture formula `(1−β)·subsidy` contradicts the model's own minimum-wage truncation for the ~60% of entrants whose Nash wage is pinned at $7.25, overstating the headline rigid-mode firm-capture figure by roughly a third to a half (verified against the produced outputs). It does not affect entry counts or gross/net costs.

---

## Q1 — The net-gain-space reformulation (scrutinized hardest)

**What changed:** the plan's gate `NI(package) ≥ NI(r·h)`, `r = y(1+m)`, was replaced mid-implementation by: viable iff `NI(package) − NI(0) ≥ (1+m)·max(NI(y·h) − NI(0), $1,000)`, which collapses to `m ≤ g_net` with `g_net = [NI(package) − NI(y·h)] / max(NI(y·h) − NI(0), $1,000)`, capped at 3.0.

**Verdict: SOUND.** I attempted to break this reformulation and could not. Point by point:

### (a) Is it economically coherent as a reservation concept?

Yes — and it fixes a perversity in the plan's formula that goes beyond the reported calibration infeasibility. Under the structural reading (predecessor memo Q1a), the money-metric cost of working `h` hours is `C_i`, and the person enters iff `NI(package) − NI(0) ≥ C_i`. The plan parameterized `C_i = NI(y(1+m)·h) − NI(0)`; the reformulation parameterizes `C_i = (1+m)·max(NI(y·h) − NI(0), floor)`. Both are calibration devices, but consider the person the non-monotonicity actually comes from: someone on a transfer plateau or in a cliff trough, whose `NI()` is locally flat, so `NI(r·h) ≈ NI(package) ≈ NI(0)` for a wide range of `r`. Under the plan's gate this person is viable **at any markup** — precisely the reported ~0.44 hard floor for single mothers. But this person's *actual net return to work is approximately zero*; any positive cost of work should make them the *hardest* to induce, not unconditionally viable. The gross-reservation form gets this exactly backwards (the disutility of work vanishes from the comparison wherever the schedule is flat). The net-gain form gets it right: their `net_gain_base` hits the floor, so entry requires an actual net gain of at least `$1,000·(1+m)` — which the clawed-back package rarely delivers. So the infeasibility was not a numerical nuisance to be patched; it was the formula telling you it encoded the wrong economics in high-EMTR regions. The reformulation is the correct response.

### (b) Is anything lost vs. the gross-reservation form?

Two things, both tolerable and one already implicitly disclosed:

1. **The schedule's shape above base income no longer enters viability.** Deliberate — that shape (the cliff troughs) is exactly what broke monotonicity. The schedule still enters through `NI(package)`, `NI(y·h)`, and `NI(0)`, so the phase-out economics (single mothers' median reachable `g_net` 0.132 vs. men's 0.253 — verified against the pool file; the doc's #3.3 claim is accurate for the reachable subset) is fully preserved where it matters.
2. **The implied heterogeneity of costs of work changes.** Under the new form, the dollar-valued cost-of-work distribution scales with the person's *own net return to work*: a high-EMTR household with `net_gain_base = $2,000` has costs distributed over `$2,000·(1+m)`; one with `$15,000` over `$15,000·(1+m)`. There is no behavioral evidence that costs of work (childcare, commuting, home production) scale with one's EMTR environment. But (i) the old form's alternative — costs scaling with productivity through the schedule — was equally unestimated, (ii) this is the standard scale-free assumption behind any proportional/elasticity-based participation model, and (iii) the $1,000 floor is precisely the safeguard against its pathological corner (tiny absolute gains inducing entry). **Recommend one disclosure sentence in the methodology doc #3.2** naming this: "the multiplicative form implies dollar costs of work proportional to the person's own net return; the floor bounds the implication for near-zero-return households."

### (c) Does it change the interpretation of the exponential markup distribution?

Yes, and this should be stated more explicitly than doc #3.2 currently does. `m` is no longer a gross-wage markup: `reservation_wage_{edge} = y(1+m)` is now a *label* that never passes through the schedule (the code and doc correctly call it "descriptive gross-equivalent," but see PI-8 on a stale comment). The exponential now describes proportional net-gain requirements, and because viability collapses to `u ≤ 1 − exp(−λ·g_net)`, the whole apparatus is now exactly a **single-index entry-probability model in `g_net`** — person-level entry probability `1 − exp(−λ_c·g_net_i)`, calibrated so the cell mean matches the saturated target. That is transparent and arguably cleaner than the plan's version. It has one consequence the band disclosure (ST-9) only partially covers: **PI-4** below.

**PI-4 (MEDIUM) — the exponential CDF, not the saturating response form, governs within-cell composition, and it can exceed the model's own participation ceiling person-level.** The calibration matches the cell *mean* of `response_multiplier(ε, g_net, M=1.5) − 1`, which caps any person's implied entry probability at `M − 1 = 0.5`. But the allocation rule `P(enter) = 1 − exp(−λ·g_net)` is unbounded toward 1: for high-`g_net` (lowest-MPL) individuals it can substantially exceed 0.5 (e.g., at the single-mothers central solve, a `g_net = 3` person's probability is on the order of 0.7+ while the response form says 0.5 is the ceiling). The aggregate is right by construction, but within cell the model over-selects the very lowest-MPL people as entrants relative to its own saturation logic — and those are exactly the people the M7 hours mapping assigns the fewest hours (PI-3), so the two artifacts compound in the same cost-reducing direction. Fix options: none required for the aggregate; either (i) disclose in doc #3 (extend the ST-9 sentence: the exponential form fixes *who* enters, and it tilts harder toward the lowest-MPL tail than the saturating response would), or (ii) if the composition ever becomes load-bearing (e.g., by-cell fiscal results), swap the allocation rule to `u_i ≤ response_multiplier(ε, g_net_i, M) − 1` directly (person-level saturated probability, no λ needed at the central edge — though the band's nested-set property would then need re-derivation).

### (d) The $1,000 floor and 3.0 cap

Defensible. The floor functions as a de-minimis absolute net-return-to-work threshold — economically sensible (nobody enters a job for less than ~$1,000/yr net), prevents the division blowup, and blocks the pathological corner in (b). The cap limits floored rows' leverage on the calibration. Verified: 297 rows sit at the floor (39 of them gate-viable), ~60 at the cap, of 181,960 — immaterial, and the counts print each run as the doc says. Two LOW-severity residuals in **PI-7**: (i) neither value has a sensitivity run (a one-line check at floor ∈ {$500, $2,000}, cap ∈ {2, 4} would close this); (ii) a subtle 01h/02d inconsistency for floored rows: the gate `req ≤ gnb·(1+g_net)` uses the *floored* base on both sides, but the *actual* net gain at the max package, `NI(package) − NI(0)`, is strictly smaller than `gnb·(1+g_net)` when the raw base is under $1,000 — so a floored gate-viable row can fail every wage on the pay-up grid (including `w = y`) and still be entered via the "unresolved pays `w = y`" fallback with an actual net gain below its nominal requirement. Bounded by 39 rows; flag, do not fix urgently.

### (e) Is the m = 0 interpretation sound?

Yes, exactly. At `m = 0` the new gate reads `NI(package) − NI(0) ≥ NI(y·h) − NI(0)` ⟺ `NI(package) ≥ NI(y·h)` — identical to the plan's gate at `r = y`. The two parameterizations coincide at the indifference point and diverge only in how the requirement scales above it. "Indifferent at own unsubsidized MPL" is the correct reading under both.

---

## Q2 — Conditional-Mills imputation

**Verdict: SOUND** on the math; one MEDIUM caveat on what the selection outcome actually measures.

**Math check (line-by-line):** probit of `D` on `Xsel` over the full `est` sample ✓; employed rows' wage equation carries `imr = φ(Xγ)/Φ(Xγ)` (correct `E[ε|D=1]` up to `ρσ`) ✓; `lam_coef` = coefficient on IMR = `ρσ` ✓; pool prediction `lam0 = −φ(Xγ)/(1−Φ(Xγ)) < 0` (correct `E[ε|D=0]` term) ✓; `xb_cond = Xβ + ρσ·λ₀` ✓; column alignment via `Xwp[Xw.columns]` with `imr = 0` contributing zero to `xb` ✓; Puhani sensitivity (conditional / Mills=0 / plain OLS, each with its own smearing factor) printed ✓.

**Duan smearing:** estimated on employed residuals, applied to the pool. Strictly, `E[exp(ε)|X, D=0] ≠ E[exp(e)|D=1]`-based smearing — both truncations compress the conditional error variance relative to σ², in different amounts. Second-order, already disclosed in the predecessor memo's terms; no action beyond the existing disclosure.

**Magnitude plausibility:** `ln(21.00/15.92) = 0.277`. With `ρσ = +0.297`, this implies a pool-average `|λ₀| ≈ 0.93`, i.e., a pool-average participation index around `+0.25` (fitted `P(D=1) ≈ 0.6`). For a non-employed pool whose observables (the probit's X) explain relatively little of non-employment, that is exactly the plausible range — the median moving $21.00 → $15.92 is consistent with the estimated `ρσ`, not evidence of an implementation error. The direction check in the pipeline (conditional median below employed median) passes by ~$5.

**PI-2 (MEDIUM) — the selection outcome is "employed wage-earner with a valid wage," not "employed."** `D = obs_wage.notna()`, so employed people without an observable wage (self-employed; earnings nonresponse/allocation) sit in `D = 0` alongside the non-employed. Pre-remodel this was cosmetic (Mills = 0 meant the probit index never touched pool predictions). Post-remodel it is first-order: `ρσ` and `λ₀` now directly price the pool's negative selection, and both are estimated off a probit that conflates non-employment with wage-missingness among the employed. The contamination plausibly attenuates or distorts `ρσ` (self-employed "non-earners" are not negatively selected on potential wages). **Fix (cheap):** restrict `est` to (employed with valid wage) ∪ (non-employed), dropping employed-without-valid-wage rows from the probit, and re-inspect the p25/p50/p75 diagnostic. If the median moves materially, the current $15.92 inherits the contamination; if not, disclose and move on.

---

## Q3 — Selection-equation shifters

**Verdict: SOUND.** The ST-6 failure mode (regressor constructed differently by the selection outcome `D`) is fully avoided:

- `01i` builds links from the **full household roster before any employment split**, one row per person 16–64, keyed `(YEAR, MONTH, SERIAL, PERNUM)`. Nothing in the construction touches wages, employment status of the *person*, or MISH (spouse `EMPSTAT` is populated in all rotations; spouse *earnings* are MISH-4/8-only and correctly quarantined to sensitivity use).
- `01h` merges the links onto `org` **before** carving out `est` and the pool, with int64-cast keys on both sides ✓, so `D=0` and `D=1` rows receive identically constructed flags.
- The wage equation (`_design(wage_eq=True)`) excludes all household shifters ✓; the selection equation adds `spouse_employed_married` and `child_under5` ✓. The `× married` interaction the predecessor memo required is effectively enforced twice (`spouse_is_employed` already requires `spouse_linkable`, which requires married; the explicit `& MARST∈{1,2}` is redundant but harmless) — zero-for-unmarried is structural, not fake variation.
- The Mroz/Puhani disclosure lineage is in the docstring and doc #3.7 ✓.

**PI-13 (LOW) — residual measurement/verification items.** (i) The ~5% unlinkable married are coded `spouse_is_employed = False` — measurement error concentrated in complex households; the rule is identical across `D`, so no artifact, but it attenuates the shifter; disclosed in 01i, fine. (ii) `own_child_under5` uses the household fallback for non-head/spouse persons (construction varies by RELATE, not by `D`; disclosed). (iii) The predecessor memo's cheap falsification check — regress log wage on spouse employment among the employed, conditional on X — was not implemented (it was memo guidance rather than a plan line item, but it costs three lines and would strengthen doc #3.7).

---

## Q4 — The 02d gate, pay-up grid, and firm capture

### (a) Gate reproduces the calibration set — **verified, exactly**

Algebra: `req = (1+m)·gnb` and the gate `req ≤ gnb·(1+g_net)·(1+1e-9)` ⟺ `m ≤ g_net·(1+1e-9) + 1e-9` — the identical indicator the λ-bisection averaged (both sides use the clipped `g_net` and floored `gnb`, stored once in the pool). Empirical: recomputing the central-edge gate from the pool parquet gives **1.418M** induced (matches the reported 1.42M); the delta note's "realized = target to 4 decimals" and beta-invariance (gate at max package by construction) are consistent with this. ✓

### (b) Pay-up grid — sound

Given `NI()` is non-monotone, a grid scan of `[w_e, y]` taking the lowest clearing wage is the right structure (monotone search invalid — exactly ST-4's prescription); the `t = 1` endpoint means `w = y` is always tried; the unresolved-pays-`y` fallback is a safe numerical backstop whose only substantive exposure is the 39 floored rows in PI-7. Nine points is coarse — a cleared worker may be paid up to `(y − w_e)/8` above the minimal clearing wage, slightly reducing the subsidy (cost-conservative) — acceptable; note it in a comment if the grid is ever tuned. The cliff diagnostic (0.143M at central) is computed and reported per the plan ✓.

### (c) Firm capture on entrants — **PI-1 (HIGH): the `(1−β)·subsidy` formula contradicts the model's own wage truncation**

The code computes entrant firm capture as `(1−beta) * subsidy_annual_e * we`. That equals actual firm surplus **only at the interior Nash solution**, where `w_e + (1−β)·s(w_e) = y` holds by construction. It fails in two cases the model itself creates:

1. **The FED_MIN floor (the big one).** For β = 0.5 the interior wage is `(y − 6.72)/0.6`, which is below $7.25 for every entrant with `y < $11.07`. Verified against the pool: **59.7% of central-edge entrants have `w_e` pinned at $7.25** (80.9% at β = 0.3; 41.0% at β = 0.7). For a pinned entrant the firm's surplus is `(y − 7.25)·h` — e.g., $0.75/hr for `y = 8` — while the code credits `(1−β)·0.8·(16.80 − 7.25) = $3.82/hr`, a fivefold overstatement for that person. The truncation means the *worker* keeps more than the β share (their take-home `w + s(w)` exceeds the Nash allocation); the code's formula hands that slice to the firm anyway.
2. **Pay-up rows.** `w_final > w_e` moves further surplus to the worker (`f(w) = w + (1−β)s(w)` is increasing), so `(1−β)·s(w_final) > y − w_final` strictly; at the `w_final = y` fallback the firm's actual capture is zero while the formula still credits `(1−β)·s(y) > 0`. 0.143M entrants at central.

Verified magnitudes (recomputed from the pool at `w_e`, i.e., *before* the pay-up worsens it): claimed entrant firm capture **$3.8B vs. actual firm surplus $2.8B** at β = 0.5; **$5.9B vs. $3.9B** at β = 0.3; $2.0B vs. $1.6B at β = 0.7. This is HIGH, not MEDIUM, because in **rigid mode — the headline configuration (`incumbent_wage_rigid: True`)** — incumbent firm capture is identically zero, so the published `firm_capture_bn` and `firm_capture_pct_of_gross` rows (3.7/2.0/5.7 $B; 3.8/2.1/5.8%) consist *entirely* of this formula: they are overstated by roughly a third to a half. The incidence narrative ("how much of the subsidy do firms capture?") is a central output of 02d. Entry counts, gross cost, and net cost are unaffected (`s_e` correctly uses `w_final`).

**Fix (small):** entrant firm capture per person-year = `(y − w_final) · h` (equivalently `min((1−β)·s(w_final), y − w_final)·h`, and note the same truncation-blind formula sits in `_entrants_synthetic` — fix or annotate both. The correction is worker-favorable: it *strengthens* the pro-worker incidence story rather than weakening it.

One adjacent observation, disclosure-grade: for pay-up and `w_final = y` matches the firm's participation constraint is exactly (or nearly) binding; with any hiring/training cost those marginal matches would not form, so entry is slightly overstated among the 0.14M cliff cases. One sentence next to the cliff diagnostic covers it.

---

## Q5 — Quantile-matched entrant hours

**Verdict: FLAWED-FIXABLE** — the direction is defensible; the strength of the assumption is not yet earned, and it is doing first-order work in the headline costs.

Verified from outputs: entrant hours p25/p50/p75/mean = **576/912/1,152/879**, against incumbent annual hours p10/p25/p50 = 768/1,200/1,920. Entrant median MPL is $10.24, so entrants sit around the incumbents' p10–p15 of hours. The delta note correctly attributes the cost stability (gross $102.0B → $97.2B despite +0.5M entrants) largely to this: per-entrant subsidy dollars roughly halve relative to the flat 2,000 hours.

Three concerns, jointly **PI-3 (MEDIUM):**

1. **Maximal rank dependence is an untested upper bound on the gradient.** Rank-to-rank mapping assumes comonotonicity between entrant MPL and hours (rank correlation 1). The true within-cell wage–hours rank correlation among incumbents is positive but well below 1; a conditional-mean mapping (`E[hours | wage percentile]`) would compress toward the cell mean and raise entrant hours and costs. The implemented choice is the *most* cost-reducing member of the defensible family.
2. **The mapping runs pool-rank → incumbent-hours-rank, not MPL-position → incumbent-hours-rank.** A pool-median person (MPL $15.92) receives incumbent *median* hours, though an incumbent earning $15.92 sits well below the incumbent wage median and works fewer hours. The alternative ("entrants behave like incumbents at the same wage") is at least as natural and gives *lower* hours — so the two dimensions of the choice cut in opposite directions, which is precisely why a sensitivity is needed rather than a sign argument.
3. **Interaction with PI-4:** the exponential allocation over-selects the lowest-MPL tail into entry, and the mapping then assigns that tail the fewest hours — the artifacts compound in the same direction on per-entrant cost. Note hours also feed *viability* through `g_net` (both `NI(package)` and `NI(y·h)` scale with `h` through a nonlinear schedule), so this is not purely a cost-side assumption.

**Is 880 hrs/yr plausible?** Not indefensible — ~20 hrs/wk part-year is a recognizable marginal-entrant profile, and low-wage incumbents' annual hours are genuinely low (p10 = 768). But it is well below welfare-to-work benchmarks the project itself anchors on (SSP *required* 30+ hrs/wk; its entrants were full-time by construction), and no benchmark comparison is currently disclosed.

**Fix:** add two hours-sensitivity rows to `entry_margin_band.parquet` (flat 2,000; the wage-positioned mapping from item 2) and one sentence in doc #3.8 benchmarking the 880 mean. If the gross-cost band across hours variants is wide, it belongs in the write-up alongside the eps band.

---

## Q6 — Delta attribution (A = 0.935M → B = 1.92M → C = 1.42M)

**Verdict: SOUND as far as it goes.** The decomposition logic is valid sequential (path) attribution: B − A = +0.99M isolates the ST-7 imputation under the *old* rule (which is clean — the old gross gate `y + s(y) ≥ r` is hours-free, so the M7 change cannot contaminate stage B), and C − B = −0.50M isolates the rule change under the *new* MPL. Two flags:

**PI-5 (MEDIUM) — staging is coarser than the plan required, and order-dependence is unlabeled.** Plan verification 5 (and W8) required the baseline shift attributed to "(a) ST-7 imputation, (b) ST-11 saturation, (c) net gate/basis, (d) band values" with staged commits "so each delta is isolable" — explicitly because they cut in different directions. The delta note delivers (a) cleanly but bundles (b) and (c) into a single −0.50M ("saturating … and the net-of-transfer basis together"). Since both components of the bundle cut the same direction, the bundling is less dangerous than the plan feared, but the plan's requirement was not met and the (b)-vs-(c) split is exactly what a reader needs to judge how much of the pullback is functional-form judgment (ceiling M = 1.5) versus schedule facts (EMTRs). ((d) is a true zero at the central edge — central band values equal the old central scenario — worth one line saying so.) Additionally, any sequential decomposition is order-dependent (the imputation effect is evaluated under the old rule; the rule effect under the new MPL; interactions land in whichever stage comes second) — one labeling sentence in the delta note closes this. If the staged commits from W8 exist, re-running the B-stage with saturation-only and net-only variants is mechanical.

---

## Q7 — New concerns introduced by the implementation; disclosure coverage

Disclosures that are **adequate as delivered:** taxable/countable subsidy treatment (doc #4, with the phase-out reintroduction caveat); UI and part-year timing direction-of-bias (doc #5); band scope ST-9; men-cell heterogeneity; deferred M6 fixed costs; spouse-link coverage; ST-13 synthetic-path repointing and labeling (verified in code — `_entrants_synthetic` reads `eps_ext_band["central"]` and is loudly labeled; the band writes only on the pool path ✓); household-coordination sensitivity rows present in the band file ✓; g_net cell asymmetry (doc #3.3 verified accurate: reachable medians 0.132 / 0.246 / 0.253).

Gaps:

**PI-6 (MEDIUM) — the unemployed-vs-NILF split flag (plan W6, ST-3 minimum fix) was not implemented.** The pool parquet carries no EMPSTAT-derived flag (verified: column list). The plan's W6 line item was "UI/timing disclosures **+ unemployed-vs-NILF split flag**"; only the prose disclosure shipped. Without the flag, the UI omission's materiality cannot even be bounded from outputs (what share of induced entrants are unemployed vs. NILF?), and the promised minimum fix — "split the pool by a UI-plausible flag and disclose" — is unfulfillable downstream. Cheap fix: carry `EMPSTAT`-derived `is_unemployed` through 01h's output and add a by-status row to the band table.

**PI-8 (LOW) — the `reservation_wage` columns are now purely descriptive, but the code says otherwise.** 01h's comment on the alias reads "Back-compat alias (02d's headline grid and any external reader): central edge" — but 02d no longer reads `reservation_wage` at all (the gate contract is `required_net_gain_*`). Any external reader (the app?) treating `reservation_wage` as a gross wage that passes through the schedule will mis-use it. Fix the comment; grep consumers of `reservation_wage` outside 02d.

**PI-9 (LOW) — ST-14 relabel not done.** 02b was deliberately untouched ("as designed" per the delta note), but plan W7 included the 02b benchmark relabel avoiding the `central` name collision across `cfg["behavioral"]["scenarios"]` and `cfg["matching"]["eps_ext_band"]`. The collision persists in outputs (`behavioral_scenarios.parquet` scenario `central` vs. band edge `central`). Was LOW in the stress-test memo; remains LOW; still open.

**PI-10 (LOW) — reconciliation wedge attribution is qualitative.** `entry_reconciliation.parquet` carries the two numbers (0.72M vs 1.42M) and a prose note naming the four wedge sources, but no quantitative attribution (plan W7: "wedge **attributed to** population/form/basis/elasticity source"). A staged bridge (02b central → swap population → swap basis → swap form → 1.42M) would take one afternoon and turn a review liability into the strength the predecessor memo described.

**PI-11 (LOW) — schedule grid max $65k vs. package incomes.** `np.interp` clamps beyond the grid. For the *reachable* set (MPL < $16.80, entrant hours ≤ ~3,000) package income tops out near the $65k edge, so clamping is immaterial for entry; it does bite `ni_base = NI(y·h)` for high-MPL/high-hours *non-reachable* pool rows, whose stored `g_net` is therefore distorted — currently harmless (they can never be viable; `m = 100`) but a trap if anyone later consumes pool `g_net` descriptively. One comment line in 01h suffices.

**PI-12 (LOW) — key diagnostics are console-only.** The Puhani three-variant MPL comparison, per-cell×edge target-vs-realized calibration identity, the g_net floor/cap counts, and the corr(markup, month) check are all printed but not persisted to any output artifact. They are the evidentiary core of the remodel's verification; route them to a small parquet/JSON next to the pool so W9-style reviews and the replication protocol can check them without re-running.

**PI-14 (LOW) — the ST-10 diagnostic is pooled, not within-cell.** Plan verification 1 specified "correlation of `m` with survey month ≈ 0 **within cell**"; 01h computes it pooled across cells (+0.008). Pooled ≈ 0 is reassuring and the hash construction makes within-cell skew implausible, but the check as specified is three lines.

---

## Consolidated findings

| ID | Severity | Location | Finding | Fix |
|----|----------|----------|---------|-----|
| PI-1 | **HIGH** | `02d::_entrants_from_pool` (and `_entrants_synthetic`) | Entrant firm capture `(1−β)·s` ignores the FED_MIN truncation (59.7% of central entrants pinned at $7.25) and pay-up wages; rigid-mode headline firm capture — which is 100% entrant capture — overstated ~⅓–½ (claimed $3.8B vs actual $2.8B at β=0.5; $5.9B vs $3.9B at β=0.3). Entry/costs unaffected. | Compute entrant capture as `(y − w_final)·h`; annotate the synthetic path. |
| PI-2 | MEDIUM | `01h::heckman_impute` | Selection outcome `D` = "has valid observed wage," conflating non-employment with employed non-earners (self-employed, nonresponse) — now first-order since `ρσ·λ₀` is used in pool predictions. | Drop employed-without-valid-wage rows from the probit sample; re-check the $15.92 median. |
| PI-3 | MEDIUM | `01h::_entry_hours` | Comonotone pool-rank→incumbent-hours-rank mapping is the most cost-reducing member of the defensible family (entrant mean 879 hrs/yr, ≈ incumbent p10–p15); halves per-entrant cost; also feeds viability via `g_net`; no sensitivity or benchmark disclosed. | Add hours-sensitivity rows (flat 2,000; wage-positioned mapping) to the band file; benchmark 880 in doc #3.8. |
| PI-4 | MEDIUM | `01h::assign_reservation_band` | Within-cell entrant composition follows `1−exp(−λ·g_net)`, which exceeds the person-level saturation ceiling (M−1 = 0.5) for high-`g_net` individuals; compounds PI-3's cost direction. Aggregate calibration unaffected. | Disclose (extend ST-9 sentence), or move to a person-level saturated allocation if composition becomes load-bearing. |
| PI-5 | MEDIUM | delta note | ST-11 (saturation) and ST-1/2 (net basis) deltas bundled into one −0.50M stage; plan required separate attribution; sequential order-dependence unlabeled; (d) band-values = 0 at central unstated. | Re-run the two sub-stages from the staged commits; add order-dependence sentence. |
| PI-6 | MEDIUM | `01h` output / plan W6 | Unemployed-vs-NILF split flag (ST-3 minimum fix, explicit W6 deliverable) not implemented; UI omission cannot be bounded from outputs. | Carry an `is_unemployed` flag into the pool; add by-status band row. |
| PI-7 | LOW | `01h`/`02d` | $1,000 floor / 3.0 cap not sensitivity-tested (297/~60 rows); floored gate-viable rows (39) can enter at `w=y` with actual net gain below nominal requirement via the fallback. | One sensitivity run; a comment on the fallback. |
| PI-8 | LOW | `01h` output comment | `reservation_wage` alias comment claims 02d consumes it; 02d does not; external misuse risk for a now-descriptive column. | Fix comment; grep external consumers. |
| PI-9 | LOW | 02b outputs | ST-14 `central` name collision across config namespaces persists (relabel skipped). | Relabel 02b scenarios as benchmarks. |
| PI-10 | LOW | `entry_reconciliation.parquet` | Wedge attribution qualitative, not quantitative (plan W7 wording). | Staged 02b→02d bridge. |
| PI-11 | LOW | schedules / `01h` | $65k grid clamp distorts stored `g_net` for non-reachable high-income pool rows (harmless today; trap for future consumers). | Comment; or NaN `g_net` for non-reachable rows. |
| PI-12 | LOW | `01h` prints | Core verification diagnostics (Puhani variants, calibration identity, floor/cap counts, timing corr) console-only. | Persist to a diagnostics artifact. |
| PI-13 | LOW | `01i`/`01h` | Unlinkable-married coded False (attenuation, disclosed); hh-fallback under-5 flag for non-head/spouse (disclosed); memo's wage-on-spouse-employment falsification regression not run. | Run the three-line falsification check; keep disclosures. |
| PI-14 | LOW | `01h` diagnostic | corr(markup, month) computed pooled; plan specified within-cell. | Compute per cell. |

---

## Evidence

**Sources (read in full this session):** `code/01_data_preparation/01h_nonemployed_pool.py`; `code/01_data_preparation/01i_household_links.py`; `code/02_descriptive_analysis/02d_matching_simulation.py`; `code/02_descriptive_analysis/02b_behavioral_scenarios.py` (lines 80–149: `_resolve_schedule`, `_ni_adjusted`, `response_multiplier`, `assign_cell`); `code/00_setup/00_config.py`; `docs/entry_from_nonemployment_methodology.md`; `Infrastructure/session_logs/2026-07-08_entry-remodel-delta-note.md`; the rev2 plan and the ST-1…ST-14 stress-test memo.

**Verification runs (read-only against produced outputs; scripts at `temp/postimpl_review_checks.py`, `temp/postimpl_check2.py`, run with the project `.venv`):**
- Gate identity: recomputed central-edge viable mass from `nonemployed_pool.parquet` = **1.418M**, matching the reported 1.42M and the algebraic equivalence `req ≤ gnb(1+g_net)(1+1e-9) ⟺ m ≤ g_net(1+ε)+ε`.
- PI-1 magnitudes: FED_MIN-pinned entrant shares 59.7% / 80.9% / 41.0% at β = 0.5/0.3/0.7; claimed vs. actual entrant firm capture $3.8B vs $2.8B, $5.9B vs $3.9B, $2.0B vs $1.6B (actuals computed at `w_e`; pay-up wages lower them further). Rigid-mode published firm capture rows (3.7/2.0/5.7 $B) confirmed to be entrant-only.
- Q5: entrant hours p25/p50/p75/mean = 576/912/1,152/879; entrant MPL p25/p50/p75 = 8.34/10.24/12.10; incumbent hours p10/p25/p50 = 768/1,200/1,920.
- Doc #3.3 g_net claim verified over the reachable subset: medians 0.132 (single_mothers) / 0.246 (other_women) / 0.253 (men). (Whole-cell medians differ — 0.044/0.050/0.000 — because non-reachable rows carry g_net = 0; the doc's framing is correct for the calibration population.)
- Floor/cap incidence: 297 rows at the $1,000 floor, 39 of them gate-viable.
- Band and reconciliation files inspected: 3 as-modeled + 2 coordination-sensitivity rows present; reconciliation 0.72M vs 1.42M with the qualitative note.
- Pool schema inspected: no unemployed/NILF flag present (PI-6).

**Confidence:** High on PI-1 (algebra plus direct recomputation from produced data), the Q4a gate identity, PI-2's mechanism (read from code; magnitude untested — that is the recommended check), PI-6 (column list), and Q1's monotonicity/coherence analysis (analytic). Medium on PI-3's magnitude (the sensitivity that would pin it down is the recommended fix), PI-4's compositional size (analytic bound, not simulated), and the Q2 plausibility arithmetic (average-λ₀ back-of-envelope, heterogeneity ignored).

**Assumptions:** the produced parquets on disk correspond to the delta note's verified run (md5-stable per the note; induced entry matched to 0.002M); `_resolve_schedule`'s fallback ladder returns a schedule for every (fkey, state) in the pool (no group silently dropped — inferred, not instrumented); the staged commits referenced in W8 exist and can be re-run for PI-5. Two probe scripts were left in `temp/` (project-permitted scratch location); nothing in `code/`, `data/`, `docs/`, or `output/` was modified.
