# Ranked Fix List — Entry Model (post-holistic-evaluation, 2026-07-09)

Ranked by (impact on a defensible, publication-ready result) × (tractability). Effort is calendar estimate for one analyst. "Blocker" = should be resolved before publication. Each ties to an evaluation question.

| # | Fix | Q | Severity | Effort | Blocker? |
|---|---|---|---|---|---|
| 1 | **Headline-centering decision** (Option A recommended): user picks evidence-central vs conservative-floor; if A, add one jointly-specified evidence-central scenario (~1.1–1.5M) and relabel 0.83M as the floor | Q1 | HIGH | 0.5–1 d (after decision) | **Yes** |
| 2 | **Scenario-grid uncertainty presentation**: replace/front the 9 one-at-a-time rows with 3–4 coherent joint bundles (Conservative / Evidence-central / High); keep one-at-a-time as an appendix decomposition | Q2 | HIGH | 1–2 d | **Yes** (enables #1) |
| 3 | **PI-3 — entrant hours-mapping sensitivity**: run entrant hours under ≥2 alternatives (independent draw; cell-median) vs the current rank-rank; report the range on marginal-cost-per-job, fully-loaded $/job, and entry-FTE | Q5 | HIGH (story) / LOW (fiscal total) | 1 d | **Yes** |
| 4 | **Re-derive/annotate W2c band-edge anchors on the post-dispersion g_net scale** (eps are slopes applied over realized net stimulus 0.13–0.19, not the anchor's ~0.7); fix the prose provenance | Q3b | MEDIUM | 0.5 d | Yes (prose) |
| 5 | **Fix stale/inconsistent draft numbers** (doc-consistency + number-verification + my spot-check): appendix §7 all-renegotiate bound **"$158B" → 160.3B** (main draft correct; DN-001 HIGH); appendix §7 firm capture **"under one percent" is wrong for the headline β=0.5 case (1.5%)** — only β=0.7 is <1% (DN-002 / CC-003); §4 imputation medians "$19.62–$22.17" → $18.28/$19.49/$20.65 (DN-003); §8 "~0.5M entrants" → ~0.83M (CC-001); **Figure 6 caption "clears a worker's reservation wage"** vs the disavowal (CC-004); reconcile entrant-composition across docs (summary "two-fifths / 2%" vs appendix "a third / 1%"; live 38% / 1.93% — CC-002/DN-006/008) | Q9 | HIGH (bound + firm-capture) | 0.5 d | Yes (correctness) |
| 5b | **Source or drop unverifiable comparators**: "23.6% of paid-hourly workers below target" (DN-004) and Figure 11b household dollars ($7,800/$5,600/53h — DN-005) are not persisted in any supplied output; confirm they trace to a figure script / add to a diagnostic | Q9 | MEDIUM | 0.25 d | Recommended |
| 6 | **Incumbent hours margin → net basis**: apply eps_int on the net-of-transfer marginal-hour gain (consistent with the entry gate), not gross g; will modestly lower the 0.25M-FTE central | Q5 | MEDIUM | 0.5–1 d | Recommended |
| 7 | **Status-weight composition disclosure**: one line noting the entrant *composition* (not count/cost) is sensitive to the 5.0/1.0/.15/.15 judgment weights; optionally report composition under an alternative weight | Q6 | MEDIUM (narrative) | 0.25 d | Recommended |
| 8 | **UI in `NI(0)` for the unemployed subset** (or an explicit bound): now binds harder because entrants are ~38% unemployed post-E1; overstates their net gain and fiscal saving | Q8 | MEDIUM | 1–2 d (data) / 0.25 d (bound) | Disclose now, model later |
| 9 | **Fixed cost of work (childcare/commuting)**: queued ASEC+SPM / SPLOC+NCHLT5 re-pull; biases single-mother entry up — the group the clawback story centers on | Q8 | MEDIUM | multi-day (data acquisition) | Disclose now, model later |
| 10 | **Reconciliation refresh**: update `entry_reconciliation` note to reflect the narrowed 0.72↔0.83 wedge; scope "nearly the same place" to *cost* in the main draft | Q7 | LOW | 0.25 d | Recommended |
| 11 | **Resolve `[TO VERIFY]`/`[TO FILL]` citations** (main draft footnotes 1–5: prior-post dates/URLs, per-job-cost sources, report months) | Q9 | LOW | 0.5 d | **Yes** (pre-ship) |
| 12 | **Fresh `/full-review` + `/review-style`** on both drafts after #1–#5 land; the last full pass predates all three rebases | Q9 | — | 0.5 d | **Yes** (pre-ship) |
| 13 | **Demand-side / matching-friction sensitivity** (disclosed job-finding haircut row): entry currently forms at rate 1; offsets the Q1 MPL conservatism | Q8 | LOW | 1–2 d | Optional |
| 14 | **Ramp-in labeling**: present entry/cost as steady-state reached over ~3–5 yrs (already partly disclosed) | Q8 | LOW | 0.25 d | Optional |
| 15 | **Reconcile "EARNWT for everything measured on workers" vs unweighted wage OLS** (CC-007): the Heckman log-wage OLS in 01h is unweighted; either weight it or soften the appendix claim | Q9 | LOW | 0.25 d | Optional |
| 16 | **Remove/annotate dead `min(0.90,·)` cap** and add a `ceiling_ext=1.5` sensitivity: the 0.90 target cap can never bind (ceiling caps individual response at +0.5), and the 1.5 ceiling — the operative bound — is never sensitivity-tested (methodology MR-008) | Q4 | LOW | 0.25 d | Optional |

## Suggested execution order

**Wave 1 (unblock the headline):** #1 decision → #2 scenario grid → #3 PI-3. These three determine the central number and its defensibility; everything downstream depends on them.
**Wave 2 (correctness + consistency, ~1 day):** #4, #5, #6, #7, #10 — cheap, mostly prose/basis fixes.
**Wave 3 (disclosure now, model later):** #8, #9 as disclosures (already in the drafts' limitations); schedule the data pulls separately. #13, #14 optional.
**Wave 4 (ship gate):** #11 citations → #12 fresh full review + style review → cover sheet.

## What NOT to do
- Do **not** re-open the eps central anchors (Q1 is an MPL-side/penalty issue, not an elasticity-anchor issue — the anchors are primary-verified and the design-difference arguments run *upward* from them).
- Do **not** build a full Monte-Carlo probabilistic uncertainty model (Q2) — over-engineering for transported-judgment parameters; the scenario grid is the right altitude for a Tier-1 public tool.
- Do **not** fold take-up/demand realism into the potential-entry central (double-counts the separate scalars).
