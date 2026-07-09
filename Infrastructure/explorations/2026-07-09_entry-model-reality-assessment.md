# Entry-Model Reality Assessment: How Reasonable Is the Dynamic Entry Build?

**Date:** 2026-07-09 · **Trigger:** user gut-check — (A) pool MPL levels look too high relative to the hourly-worker median; (B) modeled entry (1.42M central) looks small given millions of able-bodied non-working adults who would gain thousands of dollars net.
**Inputs:** quantitative decomposition (this session, orchestrator); methodology plausibility memo (`2026-07-09_entry-model-reality-assessment-methodology.md`); targeted literature pass (7 new primary-verified sources, catalog thread-7-entry-anchor); model outputs (`entry_margin_band`, `mpl_imputation_band`, `nonemployed_pool_diagnostics`).
**Scope:** assessment only — no model changes made. Companion to `docs/entry_from_nonemployment_methodology.md`.

---

## 1. Direct answers to the two intuitions

### Intuition A — "Pool MPL above the hourly-worker median is hard to believe": **VALIDATED, with a specific mechanism**

- The potential-wage (MPL) equation is estimated on **all employed earners** — median **$26.00**, 44 percent salaried — while the policy target derives from the **paid-hourly median ($21.00)**. Non-workers' potential wages are therefore imputed on a wage structure that includes salaried professionals, then compared against a threshold priced off the hourly labor market they would actually enter.
- The consequence shows up exactly where the user's eye caught it: the MR-001 imputation band's "conservative" edges (Mills=0 median $20.90 → 0.69M entry; plain-OLS median **$25.70** → 0.20M) implicitly claim the non-working population carries the all-earner wage structure. **The plain-OLS scenario is not credible** and the band is asymmetrically implausible as currently presented.
- Independent evidence agrees the pool's real opportunities are lower: wage offers decay causally ~0.8 percent per month of non-employment (Schmieder-von Wachter-Bender 2016) — 17-plus percent for the multi-year NILF stock — and even recently unemployed workers accept at ~0.90× their own prior wage (Krueger-Mueller 2016, now pinned from the primary).
- Within-pool, the high-MPL tail sits in the two groups whose imputed wages mean least: the **disabled ($17.10 median)** and **retired ($20.56)** — the wage equation cannot observe disability or retirement, so it imputes near-population wages to people mostly outside the labor market for non-wage reasons.
- **Direction of the fix matters:** re-estimating on the paid-hourly frame makes the pool *poorer and larger below target* (more reachable people, bigger fills, higher cost per entrant) — while also weakening the "millions leaving thousands on the table" arithmetic per person, because the table is set at wages many cannot command.

### Intuition B — "1.42M entry feels small": **PARTIALLY REFUTED on the count; VALIDATED on composition**

The measured record repeatedly falsifies the intuition that large permanent gains move non-workers en masse:

| Precedent | Effect | Scaled to our 32.6M reachable pool |
|---|---|---|
| 1990s EITC expansion (subsidy component alone; Grogger 2003, Fang-Keane 2004 primaries) | +3.5–4pp over ~6 years, most responsive demographic ever measured | ~1.2–1.3M |
| Paycheck Plus NYC pooled | +1.9pp | 0.6M |
| Paycheck Plus NYC disadvantaged men, Y3 | +5.8pp | 1.9M |
| SSP Year-2 (welfare single mothers, generous, full-time-conditioned) | +10.4pp | 3.4M |
| Full 1990s single-mother surge (EITC + welfare reform + boom, 9 years) | ~11.3pp | ~3.7M |
| **Model central** | **4.4pp** | **1.42M** |

- The full 1990s episode — permanent, several thousand dollars a year, plus coercive sticks and a boom — moved single mothers ~11pp over nine years, with the EITC component ~3.5–4pp. The model's central sits **above** the EITC-alone precedent and between Paycheck Plus and SSP: *reasonable, if anything on the generous side*.
- The risk-set arithmetic reframes "small": roughly **half of prime-age NILF men report serious health conditions**; 25–35 percent are on SSDI, whose marginal recipients (~23 percent of applicants) would work at only ~28pp even under total benefit denial (Maestas-Mullen-Strand 2013); 60 percent of prime-age NILF women cite home responsibilities; the 16.7M 16–24 NILF-other are mostly in school; retirements are essentially permanent (Krueger 2017). A defensible wage-responsive entry-risk set is **~10–15M**, against which 1.42M is a **10–15 percent yield** — not the 2.4 percent the 59M denominator suggests.
- **But the composition is implausible (the valid core of the intuition):** because entry is hash-uniform within cell, **68 percent of modeled entrants are 16–24 NILF-other (mostly students), 12.6 percent are disabled or retired, and only 9.4 percent are unemployed** — active job-seekers are modeled as near-inert while students carry the entry margin. The aggregate may be right while the people are wrong, which distorts entrant hours, family types, fiscal mix, and the publishable story.
- One more honesty point: the calibrated markups (median man requires **15.6×** his own net gain to enter; single mothers 3.0×) are reduced-form residuals bundling nonwage job values (Hall-Mueller 2018: two-thirds of offer rejections are nonwage), health, and benefit-loss risk. They are defensible as a calibration device; **calling them "reservation wages" in prose would overclaim** — no direct reservation-wage measurement exists for NILF adults at all (a genuine literature gap).

---

## 2. Element-by-element verdicts (merged methodology + literature)

| # | Element | Verdict | Impact on headline |
|---|---|---|---|
| E1 | Pool definition & hash-uniform entry propensity | Composition **IMPLAUSIBLE** (68% teen/young NILF; 12.6% disabled/retired; 9.4% unemployed); level QUESTIONABLE | HIGH (composition, fiscal mix, story) |
| E2 | MPL on all-earner (44% salaried) structure | Headline conditional PLAUSIBLE-with-caveat; **band edges asymmetrically implausible** (plain-OLS not credible) | HIGH (band interpretation); MEDIUM (headline) |
| E3 | eps_ext transport (temporary/categorical/lump-sum/phased-out programs → permanent/universal/per-paycheck/no-phase-out design) | Central PLAUSIBLE; near-symmetric band QUESTIONABLE — all four removed frictions cut upward; upper edge (2.47M) sits below SSP-scale (3.4M) | HIGH (largest single lever; band spans 5.6×) |
| E4 | Exponential markup device | PLAUSIBLE as disclosed aggregate device; IMPLAUSIBLE as micro behavior; do not label "reservation wages" | MEDIUM (mostly subsumed by E1) |
| E5 | Intensive margin: eps_int = 0.05; 02d has none | **QUESTIONABLE — the most evidence-indicted element.** The hours null is an EITC *design artifact* (plateau/phase-out kills the marginal-hour incentive); clean no-phase-out wage variation supports intensive elasticities ~0.2–0.33 (Chetty 2012 Hicksian consensus; Fehr-Goette 2007 Frisch 1.1+ upper bound; SSP and even employer-side Huttunen show part-time→full-time conversion). 8.2M eligible part-timers face a 25–54% marginal-hour raise modeled at ≈zero. Rough sizing: 0.15–0.7M FTE-equivalents, ~$1–5B gross | MEDIUM (cost); HIGH (labor-supply story) |
| E6 | Take-up 100%; no match-formation friction; static steady state | Take-up IMPLAUSIBLE (EITC ~78%, SNAP ~82% — a proportional scalar on everything); demand side and ramp-in QUESTIONABLE (PP effects grew to Y3; 1990s built over 6–9 years) | MEDIUM each |

## 3. What actually drives the modeled outcomes

Ordered by leverage on the entry headline: (1) **eps_ext values** (band spans 0.44–2.47M); (2) **MPL imputation variant** (1.42M → 0.69M → 0.20M across MR-001 variants — but the low edges are scale-contaminated per E2); (3) **the net-stimulus haircut** (taxable+countable cuts single mothers' g_net to ~0.13); (4) **reachability** (55.9% below target, driven jointly by imputation and the $16.80 target frame); (5) the saturation ceiling (secondary at current g). The *composition* of entry is driven entirely by the hash-uniform rank (E1). The *cost* story is additionally driven by entrant hours (~880/yr, rank-rank mapped) and the absent incumbent hours margin (E5).

## 4. Ranked further-work list (impact × tractability)

1. **Re-estimate the wage equation on paid-hourly earners** (same frame as the $21.00 target), rerun the MR-001 band. ~1 day. Either tightens the band defensibly or moves the headline; the current 0.20M "conservative" edge is a salaried-structure artifact and should not survive to publication as-is.
2. **Add the incumbent hours margin** to 02d (eps_int sensitivity 0.1/0.2/0.33 on 8.2M part-time incumbents, net-basis marginal-hour gain, cap 40). ~1–2 days. The no-phase-out per-hour raise is the policy's signature feature; the current build models its most direct margin at approximately zero on evidence from designs with the opposite marginal incentive.
3. **Status-aware entry propensity**: allocate the within-cell rank by the already-estimated selection-probit propensity (or add EMPSTAT-class shifters), and report entry-by-status in `entry_margin_band.parquet`. ~1–2 days. Leaves the calibrated aggregate unchanged by construction; fixes the least defensible publishable fact (entrants who are mostly teenage students; disabled/retired at 12.6%; unemployed at 9.4%).
4. **Asymmetric band + benchmark ladder presentation**: disclose that every design friction the 80-80 removes cuts upward from the EITC-anchored central; present the precedent ladder (EITC-alone 1.2M / PP 0.6–1.9M / SSP 3.4M / 1990s-full 3.7M) alongside the band so readers can locate the model in evidence space. ~½ day, mostly prose/figure.
5. **Take-up scalar** (~0.75–0.85 sensitivity row) and **ramp-in language** (present entry as a steady-state level reached over several years, per PP-Y3 and the 1990s). ~½ day.
6. **Prose fix (immediate):** stop describing calibrated markups as "reservation wages"; they are entry-resistance residuals (nonwage job values + health + benefit interactions). Add the Krueger-2017/MMS-2013 risk-set framing to the draft's entry section.

## 5. Bottom line

The build's **aggregate entry level is defensible — evidence-anchored on the generous side of the measured record** — and the user's "feels small" arithmetic is the exact intuition the ex-post literature repeatedly falsifies. What is *not* yet defensible for publication: (a) the **who** — entry composition dominated by student-age NILF with the unemployed nearly inert; (b) the **wage scale** — an all-earner imputation frame that both inflates the "conservative" band edges and understates how poor (and how numerous) the truly sub-target pool is; and (c) the **hours margin** — the policy's most distinctive incentive, modeled at zero on borrowed evidence from programs designed to suppress it. Items 1–3 above are each ~1–2 days and would materially upgrade realism without re-litigating the elasticity anchors.

## Evidence

- **Sources (quantitative):** this session's decompositions on `data/processed/nonemployed_pool.parquet` + raw ORG partitions (EMPSTAT/WKSTAT joins via person keys), `nonemployed_pool_diagnostics.json`, `mpl_imputation_band.parquet`, `hourly_workers.parquet`, est-sample wage recomputation (all-earner $26.00 / paid-hourly $21.00 / salaried share 44%); independently re-verified by the methodology memo (gate mass 1.418M; entrant 16–24 share 68.2%; unemployed share 9.4%).
- **Sources (literature, all primary/near-primary verified, cataloged):** Krueger-Mueller 2016 (pinned); Hall-Mueller 2018; Grogger 2003; Fang-Keane 2004; Maestas-Mullen-Strand 2013; Krueger 2017; Fehr-Goette 2007; Schmieder-von Wachter-Bender 2016; plus existing Abraham-Kearney 2020, CEA 2016, Meyer-Rosenbaum 2001, Chetty 2012, SSP/Paycheck Plus primaries.
- **Confidence:** High on the decomposition facts and the E2/E5 indictments (mechanical + primary-verified evidence). Medium on the ~10–15M risk-set construction (synthesis, not a published estimate) and the "reasonable-to-generous" verdict (judgment over conflicting precedents). Low on any reservation-wage statement about NILF adults (no direct measurement exists — flagged as a genuine gap).
- **Assumptions:** the 80-80's design differences (permanent, universal, per-paycheck, no phase-out) shift responsiveness upward relative to measured programs but cannot be separately quantified (the prior challenge session's Direction-2 rejection stands); German wage-decay evidence transported to the US labor market `[unverified: US displaced-worker analog not cataloged this pass]`.
