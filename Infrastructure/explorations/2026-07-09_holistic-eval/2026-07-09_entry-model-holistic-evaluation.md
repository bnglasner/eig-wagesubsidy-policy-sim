# Holistic Evaluation — Entry-from-Nonemployment Model (80-80 Subsidy)

**Date:** 2026-07-09 · **Type:** independent fresh-thread evaluation (no prior-session memory) · **Scope:** the accumulated structural entry build after three headline rebases in two days (0.94M → 1.42M → 0.46M → **0.83M**). Read-only; no analysis code changed.
**Companion deliverables:** `2026-07-09_headline-centering-decision-memo.md` (Q1 user decision), `2026-07-09_ranked-fix-list.md` (effort-estimated actions). Specialist HTML reports in `review-reports/`.
**Verification basis:** all quantitative claims below were checked by me against the live outputs (`data/processed/nonemployed_pool.parquet`, `nonemployed_pool_diagnostics.json`, `output/data/intermediate_results/population/*.parquet`) using `.venv/bin/python`; `pytest tests/` passes (static parity). Two read-only pool rebuilds (`EIG_MPL_PENALTY=0.20`, `EIG_MPL_STATUS_PENALTY=...`) were run to probe the band extremes and then deleted (canonical pool preserved, byte-identical).

---

## Overall judgment

The build is **internally coherent, well-verified, and unusually honest** — the calibration reproduces its targets to four decimals, the pipeline is deterministic, the drafts' numbers match the live run, and nearly every contestable choice is disclosed with a sensitivity row. It has been genuinely responsive: the 2026-07-08 methodology memo's two worst indictments (implausible entrant composition; salaried-frame contamination) were both fixed, and the fixes hold up under my re-checks.

The remaining problem is **not** any single layer — each revision was correct in isolation. It is that the **headline centering now embeds three independent, same-direction conservatisms on the potential-wage side (Q1)**, presented as a neutral "central," while the uncertainty is displayed **one-axis-at-a-time (Q2)** so the reader — and the authors — cannot see the joint evidence-central at all. The cost result is robust and publication-grade; the **entry central is defensibly a floor, not a center**, and the presentation should say so or move. Everything else is either sound (Q3, Q4, Q7) or a bounded, disclosed limitation (Q5 hours, Q6 composition, Q8).

**Verdict tally:** correctly centered / sound — Q3, Q4, Q7. Over-corrected (too conservative, mislabeled) — Q1, and the Q2 architecture that hides it. Under-tested but not wrong — Q5 (hours mapping), Q6 (status weights). Presentation/limitations — Q8, Q9.

---

## Q1 — Headline centering: **the central is a conservative floor, not the evidence-weighted center.** Recommend re-centering (or explicit relabeling).

**Verified: all three conservatisms push entry in the same direction (down).** From `mpl_imputation_band.parquet`:

| Lever | Headline choice | Direction if relaxed toward evidence | Entry |
|---|---|---|---|
| Non-employment duration penalty | **0%** | Schmieder-vWB 0.8%/mo; KM accept ≈0.90× → penalty is real, positive | pen10 **1.21M**, pen20 **1.70M** |
| Offer-dispersion λ | **0.75** | measurement-error trim, but σ is on *accepted* wages (low tail truncated) → understates dispersion even at 1.0 | lam100 **1.12M** |
| Residual σ base | accepted-wage σ, no Flinn correction | truncation ⇒ true offer dispersion larger | (compounds λ upward) |

The central 0.83M is the point where **all three** sit at their entry-minimizing end simultaneously. None is neutral:

- **penalty = 0 is a choice to ignore positively-evidenced offer decay,** not a neutral baseline. For a pool dominated by long-detached NILF (33.8M NILF-other + 9.7M disabled + 8.7M retired vs 7.0M unemployed), Schmieder's 0.8%/mo compounds to ~9% at one year and ~18% at two. The evidence-central mean penalty for *this* pool is plausibly ~10–15%, not 0.
- **λ = 0.75 double-counts conservatism.** The build's own delta note documents the offsetting truncation argument: because σ is estimated on *accepted* wages, it understates the offer distribution's low tail, so even λ=1.0 is not an upper bound. Trimming to 0.75 for measurement error while ignoring the truncation deflation is conservative twice.

**The "0.83 vs 1.46" choice is really a duration-penalty choice.** The delta note establishes (and I confirm from the diagnostics) that the skew *shape* is ≈ neutral at matched mean penalty — the status-mixture 1.46M is essentially "the ~15% mean-penalty outcome," because the E1 status weights counteract the skew. So the honest framing is not "central vs skew hypothesis"; it is **"0% penalty (0.83M) vs an evidence-central ~10–15% penalty (1.2–1.5M)."**

**Where the model sits on its own precedent ladder confirms this.** The drafts scale the 1990s-EITC-alone precedent to ~0.9M on the reachable pool and say the central "essentially matches it." But at the 1.42M era the build's own reality assessment placed 1.42M (4.4pp) *above* the EITC-alone precedent and *between* Paycheck Plus and SSP. Dropping to 0.83M (3.4pp) now puts the central *at or below* the single most-conservative macro precedent — i.e., the dispersion rebase moved the headline from "generous side of the record" to "the floor of the record," which is a large swing to absorb silently as "central."

**Counter-considerations — the important two-sided balance (concur with methodology-reviewer MR-001):** the model also carries offsetting *upward* biases on the potential-entry number, and not all are separable scalars.
- **Take-up < 100%** (row: 0.66M) *is* a clean separable scalar — folding it into the potential central would double-use it, so it stays separate and does not offset.
- **But frictionless matching (every viable match forms at find-rate 1), no fixed cost of work, and UI/SSDI omitted from `NI(0)`** are genuine upward biases baked into the potential count that are **not** pulled out as scalars. They push the modeled potential *up* and partially offset the MPL-side conservatism.
- The eps central anchors, if anything, lean conservative in the other direction (the design differences — permanent, universal, per-paycheck, no phase-out — all argue response *above* the EITC anchors).

So the net direction is **genuinely two-sided**: the potential-wage side is understated (penalty = 0 is not neutral) *while* the matching/fixed-cost side is overstated. This is exactly why the fix is **not** "swap 0.83M for 1.46M."

**Recommendation (detail in the decision memo):** (i) stop pinning the non-employment penalty at its no-effect floor — a modest evidence-based penalty belongs in any honest central; adopting ~10% alone yields a penalty-inclusive co-central of **≈1.1–1.2M**. (ii) **Disclose both bias sets** so the reader sees the MPL conservatism and the matching/fixed-cost optimism are offsetting. Concretely: (a) re-center on a **coherent, jointly-specified evidence bundle** (status-differentiated ~10–15% penalty + λ=1.0 — see Q2) with 0.83M retained as the explicit conservative lower anchor and the two-sided bias disclosure attached; or (b) keep 0.83M but relabel it "deliberately conservative (no wage penalty, trimmed dispersion)" and lead with the range. Do **not** continue presenting 0.83M as the neutral central. Genuine user judgment call; recommendation is (a).

---

## Q2 — Uncertainty architecture: **one-at-a-time is not honest here; the axes interact, and the joint evidence-central is unshown.** Recommend a small scenario grid.

**Verified interactions (not independent):**
- **Penalty moves reachability AND g_net AND the base ratio jointly.** From my pen20 rebuild: reachable men 25,949 → 42,758; men median g_net 0.146 → 0.235; single-mother E/R 1.41 → 0.86. A penalty is not a clean shift of one axis — it changes who is reachable, how large each person's net stimulus is, and the employment-stock reconciliation simultaneously.
- **Dispersion interacts with the quantile-matched hours** (Q5): more dispersion pulls in more low-MPL entrants, who via the +0.9 MPL–hours rank correlation get the fewest hours — so entry count and mean entry hours move together, not separately.

Displaying nine variants as one-at-a-time deviations from the central therefore **understates the true spread** (correlated upward levers compound) and, more importantly, **never displays the joint evidence-central**: there is no row in any output that sets penalty≈10–15% AND λ=1.0 together. The reader sees "0.83M central" and a scatter of single-lever excursions, but not the coherent "if the evidence-central holds on every axis" number — which is the one a skeptic will compute themselves.

**Recommendation:** replace (or front) the nine one-at-a-time rows with **3–4 coherent, jointly-specified scenarios** — e.g. *Conservative* (penalty 0, λ0.75, take-up 0.8), *Evidence-central* (status-differentiated penalty ~12%, λ1.0, take-up 1.0), *High* (penalty 20%, λ1.0, upper eps) — each a single internally-consistent bundle, with the one-at-a-time table retained as an appendix decomposition. This is more honest than a symmetric-looking band and directly answers "what if the central evidence holds everywhere." A full probabilistic (Monte Carlo over joint parameter draws) treatment is *not* necessary for a Tier-1 public simulation and would over-engineer a model whose parameters are transported judgment, not sampling distributions; the scenario grid is the right altitude.

---

## Q3 — Men's-cell double-counting: **NO double-count of the count (verified). Band-edge conversions: a real consistency concern, flag MEDIUM.**

**Q3a — verified clean.** I replicated the entry lottery offline under four status-weight vectors (baseline 5/1/.15/.15, uniform 1/1/1/1, moderate 3/1/.3/.3, extreme 10/1/.05/.05). The cell **totals are exactly invariant**: men **0.086M**, single mothers **0.134M**, other women **0.606M** under every vector. The mean-1 normalization (`s_i /= average(s_i, weights=wr)`) plus the λ-bisection to a fixed eps-based target guarantees the count is set by eps alone; the status weights only reallocate *who*. So men are **not** penalized twice in the count — eps=0.05 sets the men total, and the disabled/retired 0.15 weights only move composition. This is correct by construction and confirmed empirically.

**Q3b — the band-edge conversions predate the g_net rescaling: MEDIUM concern.** The W2c anchor arithmetic (methodology doc §2 / appendix §5) derived, e.g., single-mothers upper eps ≈ 0.49 from "+10.4pp on a 30.1% base over a net stimulus ≈ 0.7." But eps is applied in-model over the *realized* g_net, whose median is now **0.13–0.19 per cell** (diagnostics), not 0.7. Because eps enters a *saturating* response over the realized g_net, an eps calibrated against a 0.7-stimulus context but applied over a 0.13–0.19 realized stimulus produces a **smaller** employment response than the anchor program measured — i.e., the "upper" edge is, if anything, *more conservative* than the SSP evidence it is named for. This does not make the band wrong, but the prose provenance ("SSP implies ≈0.49") is no longer a clean mapping to what the model does, and the direction of the inconsistency (conservative) reinforces Q1. **Action:** re-derive or re-annotate the anchor→eps conversions on the post-dispersion g_net scale, or state explicitly that the edges are elasticity slopes applied over the model's realized (small) net stimulus, not the anchor's stimulus.

---

## Q4 — Saturation ceiling at extremes: **behaves correctly. No pathology. Verified.**

I rebuilt the pool at pen20 (63.6% below target) and skewstat_hi (69.5% below target) and read the calibration diagnostics:
- **realized ≈ target to 4 decimals at every cell × edge** even at the extremes (e.g. pen20 single-mothers central target 0.1047 / realized 0.1048; men upper 0.0395 / 0.0396).
- **The 0.90 min() cap never binds** — the largest target anywhere is single-mothers upper ≈ 0.13; the saturating `ceiling_ext=1.5` caps each *person's* response at +0.5, and the *mean* stays far below 0.90.
- **g_net cap (3.0) hits only 116 rows at pen20 and 194 at skewstat_hi** (of ~180k), negligible.

The extra entry at extremes comes cleanly from more reachable people + higher median g_net, not from ceiling artifacts. This layer is sound.

---

## Q5 — Hours margins: **entrant hours mapping is load-bearing and untested (PI-3); it is HIGH for the labor-supply/marginal-cost story, LOW for the fiscal total. Incumbent-margin basis inconsistency is real but second-order.**

**Verified: the rank-rank mapping mechanically assigns entrants the lowest hours.** corr(MPL, entry_hours) within cell is **+0.87 / +0.88 / +0.90** (sm/ow/men). Pool-wide weighted mean `entry_hours` is ~1,600–1,760, but **entrants** — selected for being below the wage target (low MPL) — are mapped to the bottom of the hours distribution, giving the reported entrant mean **~768 hrs (≈0.37 FTE)**. The whole "low marginal cost per entrant" ($3,976 gross / $2,530 net) and "entry FTE 0.32M" figures are downstream of this untested coupling. An alternative that assigns hours *independently* of MPL rank (e.g. cell-median or an independent draw) would roughly **double** entrant hours → entry FTE ≈ 0.66M, which would then *exceed* the incumbent hours margin (0.25M), flipping the appendix's "comparable margins" framing.

**Scope of the impact:** entrant gross is only **$3.3B of $93.1B** total (incumbents dominate the subsidy bill), so PI-3 barely moves headline gross/net cost. It **materially** moves the marginal-cost-per-job, the fully-loaded $44k–$89k range, and the entry-vs-hours-FTE comparison — all of which are load-bearing rhetorical points in the drafts. **Action (PI-3, still open):** run the hours mapping under ≥2 alternatives (independent draw; cell-median) and report the range on the marginal-cost and FTE claims before publication.

**Incumbent-margin basis:** confirmed — `incumbent_hours_margin` applies eps_int on **gross g** (`s_hr/w0`, the 02b convention), while the entry gate uses **net g_net**. For consistency the incumbent margin should use the net marginal-hour gain; on a net basis it would be *smaller* (EMTRs shrink the take-home raise). This partially offsets the E5 argument that eps_int=0.05 understates. Net effect: the 0.25M-FTE central incumbent margin is modestly overstated by the gross basis. **Action:** move the incumbent margin to a net-of-transfer marginal-hour stimulus for basis-consistency with the entry gate (MEDIUM).

---

## Q6 — Status-weight sensitivity: **never run before; I ran it. Composition is highly sensitive; cost/hours are robust. The "38% unemployed" narrative is a knob.**

Offline sensitivity (central edge, expected-entrant composition), by weight vector:

| Weights (U/N/D/R) | men entrants | men comp % U/N/D/R | men mean H | sm mean H | ow mean H |
|---|---|---|---|---|---|
| uniform 1/1/1/1 | 0.086M | 13.5 / 70.4 / 11.9 / 4.2 | 788 | 863 | 737 |
| moderate 3/1/.3/.3 | 0.086M | 34.6 / 61.2 / 3.1 / 1.1 | 788 | 865 | 732 |
| **baseline 5/1/.15/.15** | 0.086M | 47.3 / 50.9 / 1.3 / 0.5 | 796 | 873 | 736 |
| extreme 10/1/.05/.05 | 0.086M | 64.4 / 35.2 / 0.3 / 0.1 | 810 | 890 | 749 |

Two clean findings: (1) the **count is invariant** (as Q3a); (2) **composition swings enormously** (men unemployed share 13.5%→64.4%) while **mean entry hours barely move** (788→810). So the fiscal headline is **robust** to the status weights, but the publishable "**nearly two-fifths are unemployed job-seekers**" narrative is **manufactured by the disclosed-judgment 5.0 weight** — under a uniform lottery it would be ~14%. The 5.0 weight is defensible (CPS U→E vs N→E flow ratio ~5–6×), but it has never been sensitivity-tested and the composition story rests entirely on it. **Action:** add a one-line disclosure that the entrant-composition (not the count or cost) is sensitive to the status weights, and/or report the composition under an alternative weight as a footnote. LOW for cost, MEDIUM for the narrative.

---

## Q7 — Coherence of the two entry numbers: **adequately handled; the flip is disclosed correctly. Minor: refresh the reconciliation note and the "same place" phrasing.**

The 02b benchmark (0.72M) now sits *below* the 02d structural central (0.83M) — the relationship flipped with the dispersion rebase (previously 0.72M vs 1.42M). Checks:
- `entry_reconciliation.parquet` reports 0.72 / 0.83 with a **direction-agnostic** wedge note (population / stimulus basis / aggregation / elasticity source) — it survives the flip and remains accurate.
- The **appendix §2 handles this correctly**: it states the two "differ on entry (0.72 versus 0.83 million)" with full attribution, and reserves the "land within a few billion dollars of each other" claim for *net cost* — which is true ($76.1B reduced-form central vs $74.2B structural).
- The **main draft** says the two approaches "land in nearly the same place" without specifying that this is about *cost*; adjacent to Table 1 that is fine, but a reader could over-extend it to entry. Minor.

**Action:** (a) update the reconciliation note to acknowledge the wedge has *narrowed* to ~0.11M and the models now nearly agree on entry too (a strengthened robustness point); (b) in the main draft, scope "nearly the same place" to cost explicitly. Both LOW.

---

## Q8 — Standing limitations, ranked by how hard they bind *now*

Given everything the rebases changed, the binding order has shifted:

1. **No fixed cost of work (childcare/commuting) — binds hardest.** It biases entry *up* precisely for **single mothers**, the group the entire clawback narrative and the strongest-evidence cell are built on. The net-gain test with no expense term overstates their entry likelihood most. (Queued: ASEC+SPM, SPLOC+NCHLT5; ATUS deferred.) Note the asymmetry with Q1: for single mothers specifically, entry may be *overstated* (no fixed cost) even as the aggregate is *understated* (Q1 MPL conservatism).
2. **No demand-side / displacement / matching friction.** Entry forms at rate 1; overstates the level and speed. Partially *offsets* the Q1 MPL-side conservatism at the aggregate — worth stating that these two biases point opposite ways.
3. **UI absent from `NI(0)` — now worse than before E1.** It overstates the net gain and fiscal saving for the unemployed subset, which the E1 rebase pushed from 9.4% to ~38% of entrants. The limitation therefore *binds harder now* than when it was first disclosed — the composition fix made it more material. (Pool carries `is_unemployed` to bound it.)
4. **Annual schedule vs monthly employment status (part-year).** Overstates the counterfactual-zero year; moderate.
5. **Take-up scalar only.** Disclosed and bounded (0.66M row); low residual risk.
6. **Ramp-in dynamics.** Presentation only; disclosed as steady-state.

The drafts' own limitations sections (main "How sure are you?"; appendix §8) already list all six honestly; the value-add here is the **binding order** and the two interaction notes (fixed-cost vs Q1 for single mothers; UI omission worsened by E1).

---

## Q9 — Publication readiness: **numbers are current and accurate (my spot-check passes); sequence the review AFTER the Q1 decision.**

**My independent number spot-check (main draft + appendix) — all match the live 2026-07-09 run:** static 89.75/72.12, 20.81M, $4,314; reduced-form 92.3/96.9/103.9 gross & 73.6/76.1/77.9 net; structural rigid 92.6–93.5 / 73.7–74.6; entry 0.83M with band/dispersion/penalty/estock/spouse/take-up rows; by-group 0.13/0.61/0.09; by-sex $4,199/$4,481; states LA $5,521 / MS $5,529 / CA $3,751 / WV $4,734 (134.3k); program shares SNAP −13.0 / Medicaid −14.4 / ACA +26.4 / TANF −3.2; clawback 14/19/15; cliff 115k; hours 0.08/0.25/0.36 FTE. The drafts absorbed the rebases cleanly.

**Stale / inconsistent numbers (number-verification + doc-consistency reports; all in the appendix or cross-doc):**
- **DN-001 (HIGH):** appendix §7 all-renegotiate bound quoted as **"$158 billion"**; live flex-rigid gross is **160.3** and the main draft correctly says $160B — a cross-document inconsistency on a disclosed bound.
- **DN-002 (MEDIUM):** appendix §7 "firms capture **under one percent**" is wrong for the headline β=0.5 case (**1.5%**); only β=0.7 is <1%. Main draft's "about 2 percent" (the max) is correct.
- §4 imputation medians **"$19.62–$22.17"** → current with-dispersion **$18.28 / $19.49 / $20.65** (pre-dispersion E2-wave values).
- §8 "**~0.5 million entrants**" → ~0.83M (argument unaffected).
- Figure 6 caption still says "**clears a worker's reservation wage**" — contradicts the same draft's line-260 disavowal (CC-004).
- Cross-doc composition disagreement (summary "two-fifths / 2%" vs appendix "a third / 1%"; live 38% / 1.93%) and two comparators not persisted in any output ("23.6% of workers below target"; Figure 11b household dollars).

**The number-verification headline verdict:** all 96 checked numbers reconcile to the live 2026-07-09 run; **no 0.46M/1.42M-era survivors** and none of the flagged old markers (clawback 8.2/13/25, gross $91.0/$97.2B, entry hours 741/880/2000) appear. The drafts absorbed the rebases cleanly; the residual items above are appendix/wording, not headline errors.

**Open blockers before ship:** the Q1 centering decision (may change the central number throughout *both* drafts and every figure); PI-3 hours sensitivity (the marginal-cost/FTE claims depend on it); and the `[TO VERIFY]` / `[TO FILL]` citation details in footnotes 1–5 of the main draft.

**Recommended review/editorial sequence:**
1. **User resolves Q1** (headline centering) — first, because it propagates through both drafts and all entry/cost figures.
2. If re-centered, **re-run pipeline + regenerate the R figure suite**; if only relabeled, edit prose + captions.
3. Close **PI-3** (hours-mapping sensitivity) and fix the two stale appendix numbers.
4. **Fresh `/full-review`** (all five agents) on both drafts — the last full pass predates all three rebases and is stale.
5. **`/review-style` + eig-reviewer** for EIG voice/citation/figure compliance; resolve `[TO VERIFY]`/`[TO FILL]` footnotes.
6. **`/cover-sheet`** and final read-through.

Do not ship on the pre-rebase review.

---

## Meta-observation on the three-revision history

Each revision was locally correct: E2 (paid-hourly frame) fixed a real contamination; E1 (status weights) fixed a real composition artifact; the dispersion rebase fixed a real deterministic-cliff artifact. But the **cumulative** effect on the headline was not monitored for one-directional drift: E2 raised entry (frame), E1 left the count unchanged (composition-only), and dispersion raised it, while the *defaults chosen alongside* dispersion (penalty 0, λ 0.75) pulled it back down — landing at 0.83M via a path that stacked conservatism on the potential-wage side without an offsetting check. The structure is coherent; what is missing is a **joint, evidence-central scenario** that the one-at-a-time architecture (Q2) structurally cannot show. Fixing Q2 largely resolves Q1's presentation problem.
