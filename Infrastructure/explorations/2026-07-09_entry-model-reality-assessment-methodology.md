# Reality Assessment: Is the Dynamic Entry Model a Plausible Picture of the 80-80 Subsidy?

**Date:** 2026-07-09
**Author:** methodology-reviewer (plausibility memo — NOT the HTML pipeline report)
**Question:** Not internal validity (already reviewed: ST-1…14, PI-1…14, MR-001). The question here is **realism**: if the 80-80 subsidy — permanent, universal, per-paycheck, individually assessed, no phase-out, filling 80% of the gap to $16.80 — were enacted, is the model's dynamic entry story (who enters, how many, at what hours, at what cost) a reasonable representation of what would happen? And which model elements move the headline enough to deserve further work?
**Code read:** `code/01_data_preparation/01h_nonemployed_pool.py`, `code/02_descriptive_analysis/02d_matching_simulation.py`, `code/02_descriptive_analysis/02b_behavioral_scenarios.py`, `code/00_setup/00_config.py`, `docs/entry_from_nonemployment_methodology.md`; predecessor memos `Infrastructure/explorations/2026-07-08_entry-remodel-*.md`; outputs `entry_margin_band.parquet`, `mpl_imputation_band.parquet`, `matching_simulation.parquet`, `entry_reconciliation.parquet`, `data/processed/nonemployed_pool_diagnostics.json`.

Read-only assessment. One verification script was run against the produced pool parquet (see Evidence); nothing in the project lane was modified.

---

## Verdict summary

| # | Element | Realism verdict | How much it moves the headline |
|---|---------|-----------------|--------------------------------|
| E1 | Pool definition & hash-uniform entry propensity | **QUESTIONABLE** overall; entrant *composition* **IMPLAUSIBLE** (68% of entrants aged 16–24; 12.6% disabled/retired; only ~19% prime-age able-bodied) | **HIGH** for composition, fiscal mix, and the draft's story; **MEDIUM** for the level (base definition scales it) |
| E2 | MPL imputation on the all-earner (44% salaried) wage structure | Headline (conditional) **PLAUSIBLE-with-caveat**; MR-001 band edges **asymmetrically implausible** — Mills=0 marginal, plain-OLS **NOT CREDIBLE** | **HIGH** for the band's interpretation (0.20M "conservative" edge is an artifact); MEDIUM for the headline |
| E3 | Elasticity transport (eps_ext from temporary/categorical/lump-sum/phased-out programs) | Central anchor **PLAUSIBLE**; symmetric-ish band structure **QUESTIONABLE** — every removed design friction cuts one way (up) | **HIGH** — the eps band is already the single largest driver (0.44M–2.47M, a 5.6× spread) |
| E4 | Exponential reservation-markup device | **PLAUSIBLE** as an aggregate calibration device (disclosed as such); **IMPLAUSIBLE** as person-level behavior (median man "requires 15.6× his net gain"; unemployed treated as near-inert) | **MEDIUM** (composition; interacts with E1) |
| E5 | Intensive margin (eps_int = 0.05; 02d has none) | **QUESTIONABLE** — the near-zero anchor is transported from *phase-out* designs; the 80-80 pays a ~25–54% raise on every marginal hour to 40/wk | **MEDIUM** for cost (~1–5% of gross); **HIGH** for the effective-labor-supply story (plausibly 20–100% of the extensive margin in FTE terms) |
| E6 | Demand side, take-up, dynamics | 100% take-up **IMPLAUSIBLE**; no demand/displacement channel **QUESTIONABLE**; static steady-state presented without a ramp-in **QUESTIONABLE** | **MEDIUM** each; take-up is a proportional scalar on everything |

**Bottom line.** The model's *aggregate* entry band (0.44–1.42–2.47M) sits comfortably inside the historical program benchmarks and is defensible as a headline. What is not yet a defensible picture of reality is (i) *who* enters — the composition is an artifact of a risk pool that treats full-time students, SSDI recipients, and retirees as interchangeable with discouraged workers at the same g_net; (ii) the MR-001 "conservative" band edges, which inherit a salaried-inclusive wage structure the entrants' jobs will not have; and (iii) the near-total absence of an incumbent hours margin for a policy whose most distinctive feature is a large, unclawed-back subsidy on marginal hours.

---

## E1. Pool definition and the risk set — QUESTIONABLE (composition IMPLAUSIBLE)

**What the model does.** The risk pool is *every* non-employed person 16–64 with valid WTFINL: 59.28M = 7.0M unemployed + 33.8M NILF-other (16.7M of them aged 16–24, mostly students) + 9.7M disabled (EMPSTAT 32) + 8.7M retired (EMPSTAT 36). Within a cell, entry probability is `1 − exp(−λ·g_net)` with the person's rank `u` drawn hash-uniform — **no taste heterogeneity by non-employment reason**. The selection probit in `01h` *knows* about household structure (spouse employment, child under 5) but its propensity is used only for the Mills term, never to allocate entry.

**What that produces.** Verified from the pool file: 68.2% of central-edge entrants are aged 16–24 (the orchestrator's decomposition: 60% are 16–24 NILF-other specifically); 12.6% are disabled or retired; only ~19% are prime-age (25–54) able-bodied; and just 9.4% are unemployed — the one group with revealed current labor-market attachment.

**Is that realistic?** Partly defensible, mostly not:

- *Youth-heavy entry is not absurd per se.* Teen and student labor supply is genuinely elastic, and a 54% raise on a $10 job would pull students into part-time work. Some youth tilt is a feature, not a bug.
- *But the anchors say otherwise.* The eps_ext values were estimated on welfare-recipient single mothers (SSP, EITC) and disadvantaged adult men (Paycheck Plus). Applying their magnitudes to a pool that is 28% students-and-teens and 31% disabled/retired, with **uniform** within-cell propensity, means the calibrated aggregate is filled by whoever has the biggest g_net — mechanically the young and the low-MPL — rather than by whoever the evidence says responds.
- *The disabled and retired are mispriced in both directions.* The wage equation cannot see disability or retirement, so their MPLs (medians $17.10 and $20.56 vs. $13.76 for NILF-other) are overstated — which *under*-selects them (smaller gap to $16.80). Cutting the other way, `NI(0)` contains no SSDI/SSI or Social Security income and no SGA cash-cliff (~$1,600/mo), so for the disabled who *are* reachable, the counterfactual is understated and the entry incentive overstated. Neither error is calibrated; they roughly offset only by accident.
- *The level is exposed too.* The 32.6M reachable pool is already 1.56× the strict elasticity-semantics base (20.8M eligible incumbents) — a *generous* convention. If disabled+retired reachable members (very roughly ~8M of the 32.6M at the observed reachable shares) were excluded outright with eps unchanged, the headline would fall on the order of 20–25%. Full exclusion is too aggressive (SSDI work incentives exist; some early retirees un-retire for a 54% raise), but the current all-in, equal-propensity treatment is the opposite extreme.

**Downstream distortion.** Composition drives fiscal cost through family type (entrants are heavily `single_0c` → small transfer offsets; entrant net $5.3B on gross $7.4B), through entry hours (young/low-MPL entrants get the fewest quantile-matched hours — part of why mean entry hours are 879), and through the draft's story: a policy sold on helping struggling workers whose modeled marginal entrant is a 19-year-old student working ~880 hours a year is a communications and review liability.

**Options (increasing effort):** (a) carry an EMPSTAT-class column into the pool and report entry-by-status in `entry_margin_band.parquet` (pure disclosure; the `is_unemployed` flag already exists); (b) allocate `u` by the *existing* selection-probit propensity rank instead of hash-uniform within cell — the aggregate calibration is unchanged by construction, but composition shifts toward those observably closer to the labor market; (c) status-specific eps (or propensity shifters) for disabled/retired/students, with disclosed judgment values. Option (b) reuses machinery already estimated and is the natural middle ground.

**Severity: HIGH** for composition/fiscal mix/story; **MEDIUM** for the headline level.

---

## E2. MPL imputation scale — band edges asymmetrically implausible

**The mismatch.** The wage equation is estimated on **all employed earners** — 44% salaried, median $26.00 — while the policy target is 80% of the **paid-hourly** median ($21.00 → $16.80), and the jobs entrants would actually take are paid-hourly jobs. Predicting non-workers' potential wages off a salaried-inclusive structure imports the salaried returns to education and experience into a population that would not receive them.

**Where it bites.** The MR-001 sensitivity band (`mpl_imputation_band.parquet`): conditional $15.92 → 1.42M entry; Mills=0 $20.90 → 0.69M; plain OLS $25.70 → 0.20M. The plain-OLS variant says the median non-employed person — 68% of whom are under 25 or over 54, disproportionately low-education — could command $25.70/hr, *above the all-worker median*. That is not a "conservative scenario"; it is the salaried wage structure assigned to non-workers, and it is not credible. The gap between the plain-OLS pool median ($25.70) and the paid-hourly employed median ($21.00) suggests roughly **$4–5/hr of pure scale inflation** in the band's upper-MPL edges. The conditional variant is partially shielded — the ρσ·λ₀ correction (−$5/hr at the median) plausibly absorbs much of the same inflation, though for a partly wrong reason (it attributes to unobservable selection what is partly a sampling-frame artifact).

**Consequence for the band's meaning.** As published, the MR-001 band reads as symmetric model uncertainty: "entry could be as low as 0.20M." In reality the band is **asymmetrically implausible**: conditional plausible, Mills=0 marginal, plain-OLS not credible. Quoting 0.20M as the conservative bound of a defensible range would be misleading in the policy-favorable direction for skeptics and the policy-unfavorable direction for advocates — either way, wrong.

**Fix (cheap, high-value):** re-estimate the wage equation (and probit `D`) restricting the earner sample to **paid-hourly workers** (`PAIDHOUR == 2`, the same frame that defines the $21.00 target), rerun all three imputations, and report both frames. Expectation: the plain-OLS median drops toward ~$21, Mills=0 toward ~$17, conditional toward ~$13–14 — i.e., the band *tightens from above* and its edges become interpretable. If the conditional headline moves materially, that is important to know *before* publication. This also resolves the smearing-factor transport (1.17 estimated on all-earner residuals). Note PI-2 (employed-without-valid-wage rows contaminating `D`) should be folded into the same re-estimation.

**Severity: HIGH** for the band; **MEDIUM** for the headline.

---

## E3. Elasticity transport — the design mismatch is one-directional

**The structure today.** eps_ext centered on EITC/CBO (0.50/0.20/0.05) with band edges to 0.65/0.40/0.15, calibrated on a net, saturating basis. Every anchor comes from programs that were **temporary** (SSP 3 years; Paycheck Plus 3 years), **categorical/means-tested** (welfare recipients, very-low-income singles), **lump-sum annual** (EITC), or **phased-out** (EITC). The 80-80 removes each of those frictions:

1. **Permanent** — SSP/PP participants knew the clock was ticking; effects still *grew* through the programs (PP men Y3 +5.8pp > pooled +2.8; SSP peaked Y2). Permanence adds option value and time for information diffusion; demonstration-program effects are a floor, not a ceiling, for the steady state.
2. **Universal** — no eligibility screening, no recertification, no stigma, and full information spillover through employers and coworkers.
3. **Per-paycheck** — the EITC's participation effect operates through an annual lump sum many recipients do not connect to marginal work decisions (Chetty & Saez 2013 salience evidence); an hourly wage fill is maximally salient.
4. **No phase-out** — no clawback region deterring second earners or hours growth.

Each removed friction argues the true response sits **at or above** the anchors. The only countervailing force is population transport: the anchor populations (welfare single mothers, disadvantaged NYC singles) were plausibly the *most* latently responsive groups, and the 80-80's pool includes many low-attachment members — but the cell structure (men at 0.05) and the saturation ceiling already price much of that in.

**Benchmark ladder (verified figures, given).** Central 1.42M = **4.4pp** of the 32.6M reachable pool. Historical any-employment effects, scaled to this base: PP-NYC pooled (+1.9pp) → 0.6M; PP-NYC men Y3 (+5.8pp) → 1.9M; SSP Y2 (+10.4pp) → 3.4M; the 1990s single-mother employment surge (~15pp) → 4.9M. The model's full band (0.44–2.47M) spans the bottom-to-middle of this ladder; its **upper edge sits below the SSP-scale point** even though SSP was temporary, conditioned on 30+ hours, and offered a less generous permanent-income equivalent.

**Verdict.** Centering on EITC/CBO is fine — no better central anchor exists. But a roughly symmetric band around it mis-states the uncertainty: the design-mismatch arguments are asymmetric. Recommend (i) making the band **explicitly asymmetric** — keep the lower edge (population-transport doubt is real), extend or annotate the upper edge to the SSP-scale ~3.4M; and (ii) publishing the benchmark ladder itself next to the band (one small table), so readers can see where the model sits against every program the anchors come from. This is a judgment-and-documentation change, not a rebuild — but it needs user sign-off since it changes what the topline band says.

**Severity: HIGH** — the eps band is already the largest single lever on the headline.

---

## E4. The reservation-markup mechanism — honest device, implausible micro-story

**What eps = 0.05 actually asserts.** From the calibration diagnostics: the median required markup on a person's own net gain is 3.0× (single mothers), 5.1× (other women), **15.6× (men)**; a person at the median g_net enters with probability 4.4% / 4.1% / 1.2%. This is the honest person-level content of the aggregate elasticities — and stating it this way is a strength of the current design (the device is disclosed as a device, and the aggregate is what is calibrated).

**Where it fails as a picture of reality.** The exponential markup treats the ~7.0M **unemployed** — people currently searching for work, whose reservation wages Krueger & Mueller (2016) measured at roughly 0.8–1.0× their prior wage and declining with duration — identically to a retiree or a full-time student with the same g_net. The result (verified): the unemployed are 12% of the pool but only 9.4% of entrants, and a median unemployed man responds to a ~25% increase in his net return to work with a ~1% entry probability. For active searchers, that is not a defensible behavioral claim; a permanent 54%-raise-at-the-bottom policy would visibly change which job offers the unemployed accept and how fast.

**Why fixing it is not free.** Anchoring the unemployed to a Krueger-Mueller reservation structure (r ≈ 0.8×prior wage, deterministic viability gate — exactly what 02d already does for *incumbents* via `reservation_ratio: 0.80`) would admit most reachable unemployed and blow entry through every benchmark unless a job-finding/matching friction is added simultaneously (see E6). So the exponential device is partly *standing in* for unmodeled search frictions. The tractable middle ground is the same as E1's: status-split eps or propensity-ranked allocation, so the unemployed get a larger share of the calibrated aggregate without abandoning the aggregate discipline. A full KM-anchored rebuild is only worth it if the entry-composition results become load-bearing in the draft.

**Severity: MEDIUM** (composition channel; the aggregate is calibrated regardless). The "median man requires 15.6× his net gain" framing should appear in the methodology doc as a disclosed implication — better to own it than have a reviewer derive it.

---

## E5. The missing intensive margin — the wrong transport for this design's signature feature

**The design fact.** The 80-80 has **no phase-out to 40 hours/week**: a $10/hr worker's marginal hour pays $10 + 0.8×(16.80−10) = $15.44 — a **54% marginal-hour raise** — on every additional hour up to 40/wk. This is the single feature that most distinguishes it from the EITC, whose plateau/phase-out gives most recipients a *zero or negative* marginal-hours incentive.

**The model's treatment.** eps_int = 0.05 (02b central; 0.15 upper), sourced as "EITC: large entry, negligible hours." But the near-zero EITC hours finding is evidence about a *phase-out* design — transported to a policy that inverts the marginal incentive, it is not a conservative reading of the literature; it is the wrong analogy. Meanwhile **02d — the structural headline — has no incumbent hours margin at all**: incumbents' `annual_hours` never respond.

**Scale of the omission (rough sizing, given facts).** 8.2M of the 20.8M eligible incumbents work <35 hrs/wk, with ~2.7M FTE-equivalents of headroom to 35 hrs. With an intensive (Hicksian) elasticity of 0.1–0.3 (Chetty 2012's bounds; CBO's 0.24 substitution central) applied to marginal-hour net wage gains of roughly 20–50%: Δhours/hours ≈ 3–15% on the part-time margin. On a base of ~8.2M × ~1,100 annual hours ≈ 9.0B hours, that is **0.3–1.3B added hours ≈ 0.15–0.7M FTE**. For comparison, the central extensive margin is 1.42M entrants × 879 hours ≈ 1.25B hours ≈ 0.66M FTE. So a modest part-time hours response adds **20–100% of the entire extensive margin in effective-labor-supply terms**, while adding only ~$1–5B of gross cost (added hours × ~$3–4/hr average subsidy) on a $97B gross base.

**Realism caveats that keep this from being a pure upside error:** hours are substantially employer-set (scheduling, demand constraints), the same net-basis discipline used for entry (EMTRs shrink the take-home raise) applies, and income effects cut against. But eps_int = 0.05 with no 02d hours margin is the *floor* of the defensible range for a no-phase-out per-hour subsidy, presented without a band.

**Fix:** add an incumbent part-time hours margin to 02d (or at minimum sensitivity rows to the band file) with eps_int ∈ {0.1, 0.3} applied to <35-hr eligible incumbents on the net marginal-hour gain, capped at 35–40 hrs; report added FTE and cost. Reuses `response_multiplier` and the schedule machinery; a day or two of work.

**Severity: MEDIUM** for cost; **HIGH** for any "labor supply effect" claim in the draft.

---

## E6. What else the structure misses

1. **Demand side / displacement — QUESTIONABLE (MEDIUM).** 02d equates viability with employment: every viable match forms, instantly, with no vacancy-creation constraint, no congestion, and no displacement of unsubsidized or higher-wage workers by newly cheap subsidized labor. In an MP framework the subsidy raises match surplus and hence job creation, so the *direction* of entry is right, but the model has no friction on match formation at all — 1.42M added job seekers find jobs at rate 1. This overstates the speed and, at the margin, the level of entry (PI-1's adjacent observation — marginal matches with zero firm surplus would not form with any hiring cost — is the small tip of this). Tractable response: a disclosed job-finding haircut (e.g., match-efficiency parameter or an f(θ) from the literature) as a sensitivity row, not a full GE rebuild.
2. **Take-up < 100% — IMPLAUSIBLE as is (MEDIUM).** The model implicitly assumes every eligible worker-employer pair claims the subsidy. Benchmarks: EITC ~78%, SNAP ~82%, WIC ~50–60%. Employer-intermediated per-paycheck delivery could beat the EITC (it resembles withholding), but small-employer administrative friction, informality, and employer non-participation argue for 70–90%, not 100%. This is a proportional scalar on entry, hours, and cost alike — one multiplicative sensitivity row and one disclosure sentence.
3. **Dynamics — QUESTIONABLE (MEDIUM, presentation).** Entry builds over years: PP men's effect tripled by Y3; SSP peaked in Y2; the 1990s single-mother surge took half a decade. The model is a static steady state. The 1.42M and its costs should be labeled **"steady state, reached over roughly 3–5 years"** with a simple ramp-in profile for year-by-year fiscal presentation; presenting them as year-1 flows overstates early costs and invites false-precision critique.
4. **Small/covered elsewhere:** stigma and information frictions (largely designed away by universality + per-paycheck delivery — fine); the GE feedback of entry on the $21.00 median that defines the target (second-order); the taxable/countable subsidy assumption (already disclosed, doc #4 — note it interacts with E3: the *statutory* design would likely exclude the subsidy from means-tests, which raises g_net and entry, another asymmetric-upward argument).

---

## Ranked recommendations (expected headline impact × tractability)

| Rank | Element | Action | Effort | Why it wins |
|------|---------|--------|--------|-------------|
| 1 | **E2** | Re-estimate the Heckman on **paid-hourly earners only** (`PAIDHOUR == 2`, matching the $21.00 target frame; fold in PI-2's D-definition fix); rerun the three-variant MR-001 band; publish both frames | ~1 day (env-var variant of `01h` + `02f` rerun) | The MR-001 band is currently the model's stated model-uncertainty range, and its "conservative" edge is an artifact. This either tightens the band defensibly or moves the headline — both essential to know pre-publication. |
| 2 | **E1** | (a) Add an EMPSTAT-class column + entry-by-status rows to `entry_margin_band.parquet` (disclosure); (b) allocate `u` by **selection-probit propensity rank** within cell instead of hash-uniform (aggregate calibration unchanged by construction; composition shifts toward the labor-market-proximate) | (a) hours; (b) ~1–2 days | The entrant composition (68% aged 16–24, 12.6% disabled/retired) is the least defensible published-facing feature of the model; it drives fiscal mix and the draft's story, and (b) fixes it with machinery already estimated. |
| 3 | **E5** | Add an incumbent part-time hours margin (eps_int 0.1/0.3 sensitivity on the <35-hr eligible subset, net-basis marginal-hour gain, capped at 35–40 hrs) to 02d or as band-file rows; re-anchor the eps_int discussion away from EITC phase-out evidence | ~1–2 days | The no-phase-out marginal-hour subsidy is the policy's signature; a 0.15–0.7M-FTE channel (up to ~100% of the extensive margin's labor-supply content) is currently modeled at ~zero, on the strength of evidence from designs with the opposite marginal incentive. |
| 4 | E3 | Restructure the eps band as explicitly asymmetric (keep lower, extend/annotate upper toward SSP-scale ~3.4M); publish the benchmark ladder table | days (judgment + docs; needs user sign-off) | Largest lever on the headline, but the change is interpretive rather than computational; do after 1–3 so the ladder is computed on the corrected base. |
| 5 | E6 (take-up) | One multiplicative take-up sensitivity (0.7/0.85/1.0) applied to entry and cost rows | hours | Trivial, proportional, and pre-empts an obvious reviewer question. |
| 6 | E6 (dynamics) | Relabel headline as steady state; add a disclosed 3–5-year ramp-in profile for fiscal presentation | hours | Pure presentation; avoids overstating year-1 costs. |
| 7 | E4 | Status-split eps or KM-anchored reservation for the unemployed subset — only if entry composition becomes load-bearing after rank 2 | week+ | Mostly subsumed by rank 2(b); a full rebuild requires simultaneously adding matching frictions (E6.1) to avoid benchmark blow-through. |
| 8 | E6 (demand) | Disclosed job-finding/match-efficiency haircut sensitivity | days | Real but hardest to discipline with evidence; disclosure plus a haircut row is proportionate for a Tier-1 public simulation. |

---

## Evidence

**Sources (read in full this session):** `code/01_data_preparation/01h_nonemployed_pool.py`; `code/02_descriptive_analysis/02d_matching_simulation.py`; `code/02_descriptive_analysis/02b_behavioral_scenarios.py`; `code/00_setup/00_config.py` (behavioral + matching namespaces); `docs/entry_from_nonemployment_methodology.md`; `Infrastructure/explorations/2026-07-08_entry-remodel-methodology-stress-test.md`; `Infrastructure/explorations/2026-07-08_entry-remodel-postimpl-methodology-review.md`; `data/processed/nonemployed_pool_diagnostics.json`; `output/data/intermediate_results/population/{entry_margin_band,mpl_imputation_band,matching_simulation,entry_reconciliation}.parquet`.

**Verification run (read-only, `.venv/bin/python` against `data/processed/nonemployed_pool.parquet`):** recomputed the central-edge gate (`required_net_gain_central ≤ net_gain_base·(1+g_net)`): induced 1.418M ✓ (matches 1.42M); entrant age composition 16–24 = **68.2%**, 25–54 = 24.2%, 55–64 = 7.5%; entrant unemployed share = **9.4%**; entrant mean hours 878.6 ✓; entrant median MPL $10.26 ✓; pool population by age bin (16–24 = 19.8M of 59.28M) ✓.

**Quantitative facts taken as given from the orchestrator's same-session decomposition (not re-derived):** pool split 7.0M unemployed / 33.8M NILF-other (16.7M aged 16–24) / 9.7M disabled / 8.7M retired; entrant shares 60% 16–24-NILF-other, 12.6% disabled+retired, ~19% prime-age able-bodied; MPL medians by status ($13.76/$17.10/$20.56); all-earner estimation median $26.00 with 44% salaried vs. paid-hourly median $21.00; calibration-implied median markups 3.0×/5.1×/15.6× and median-g_net entry probabilities 4.4%/4.1%/1.2%; benchmark conversions (SSP-Y2 → 3.4M; PP-NYC pooled → 0.6M; PP men Y3 → 1.9M; 1990s surge → 4.9M); base ratio 32.6M/20.8M = 1.56×; intensive-margin facts (8.2M part-time; ~2.7M FTE headroom; 54% marginal-hour raise at $10). Where cheaply checkable against outputs (entrant age/status shares, gate mass, hours), the given facts were consistent with my recomputation.

**Literature (prior knowledge, standard citations):** Card & Hyslop 2005 / SRDC (SSP); MDRC Paycheck Plus reports (NYC, Atlanta); Meyer & Rosenbaum 2001; McClelland & Mok 2012 (CBO review); Kleven 2024; Chetty 2012; Chetty & Saez 2013 (EITC salience); Chetty, Guren, Manoli & Weber 2011 / CBO 0.24 (intensive-margin bounds); Krueger & Mueller 2016 (measured reservation wages); Mortensen & Pissarides 1994 (matching frictions); EITC/SNAP/WIC take-up literature (Currie 2006 lineage); Solon-lineage caution on scale transport.

**Confidence:** High on E1's composition facts and E2's band asymmetry (recomputed or read directly from produced outputs); High on the *direction* of every E3 design-mismatch argument (each is a removed friction with a known sign); Medium on all magnitude sizings (E1's ~20–25% base sensitivity, E2's ~$4–5 scale inflation, E5's 0.15–0.7M FTE) — these are back-of-envelope by design and are exactly what the ranked next steps would pin down; Medium on E6 take-up range (program analogies, not estimates for an employer-intermediated design).

**Assumptions:** the parquet outputs on disk correspond to the current headline run (consistent with the diagnostics JSON and the 2026-07-08 delta note); the PolicyEngine schedules contain no SSDI/SSA income at zero earnings (inferred from the family-type/state keying; the `01f` precompute was not read this session); PAIDHOUR is available in the raw partitions to support the E2 re-estimation (it is read in `_employed_hourly_wage`, so yes for the same partitions). No files outside `Infrastructure/explorations/` were created; the verification script was run inline (nothing persisted to `temp/`).
