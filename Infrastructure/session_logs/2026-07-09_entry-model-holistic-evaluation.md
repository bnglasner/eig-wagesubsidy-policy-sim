# Session Log — Entry-Model Holistic Evaluation (2026-07-09)

**Task:** Independent, fresh-thread holistic evaluation of the entry-from-nonemployment build
(80-80 subsidy). No analysis-code changes; deliverables are evaluation report + headline-centering
memo + ranked fix list as NEW dated files. Specialists routed in parallel.

## Setup / verification done
- Read PROJECT.md, methodology doc, config, 01h/01i/02b/02d/02f, reality-assessment memos, delta note.
- `pytest tests/` → 1 passed (static parity). Live outputs match the handoff summary (0.83M central etc.).
- Launched 3 background specialists (methodology on Q1–Q5; number-verification + doc-consistency on drafts).

## Incremental findings (verified against live outputs myself)
1. **Q3a/Q6 — no double-count of the count.** Offline replication of the lottery: cell entrant totals
   are EXACTLY invariant to the status-weight vector (men 0.086M, sm 0.134M, ow 0.606M under
   baseline 5/1/.15/.15, uniform, moderate 3/1/.3/.3, extreme 10/1/.05/.05). eps alone sets the
   count; status weights only reallocate WHO. So men are not penalized twice in the COUNT.
2. **Q6 — composition is a knob, cost is robust.** Men unemployed-share swings 13.5% (uniform) →
   47.3% (baseline) → 64.4% (extreme) with the never-tested judgment weights; but entrant mean
   hours barely move (788→810), so the fiscal headline is robust to status weights while the
   "38% unemployed / labor-market-proximate" NARRATIVE is manufactured by the 5.0 weight.
3. **Q5 — hours mapping is load-bearing (PI-3).** corr(MPL, entry_hours) = +0.87/+0.88/+0.90 by cell
   (near-mechanical from rank-rank). Entrants are selected low-MPL → assigned the LOWEST in-cell
   hours (~768 vs cell-avg ~1600-1760). The low marginal-cost-per-entrant and entry-FTE 0.32M
   are artifacts of this untested coupling; an independent-hours draw ≈ doubles entrant hours/FTE.
   BUT entrant gross is only $3.3B of $93.1B, so headline gross/net barely moves — PI-3 is HIGH for
   the labor-supply/marginal-cost story, LOW for the fiscal total.
4. **Q4 — saturation behaves.** pen20/skewstat_hi builds: realized≈target to 4 dp at all edges;
   every target << 0.90 cap (max sm-upper ≈0.13); ceiling_ext caps individual response at +0.5 as
   intended; g_net cap hits 116–194 rows. No pathological binding. Extra entry = more reachable +
   higher median g_net (men g_net 0.146→0.235 under pen20) → confirms Q2 non-separability.
5. **Q1 direction check (from mpl_imputation_band):** all three headline conservatisms push entry
   DOWN — penalty 0 (pen10 1.21M, pen20 1.70M), λ=0.75 (lam100 1.12M), accepted-wage σ truncation
   (understates low tail even at λ=1). The skew "1.46M" is really the ~15% mean-penalty outcome
   (delta note: skew shape ~neutral at matched mean), i.e. the 0.83-vs-1.46 choice is a
   duration-penalty-magnitude choice (0% vs ~15%).

## Draft spot-check (Q9, mine) — all current
Main draft + appendix numbers match the live 2026-07-09 run (static 89.75/72.12; reduced-form
92.3/96.9/103.9; structural 92.6–93.5/73.7–74.6; entry 0.83M + all variant rows; by-sex/state/
program shares). Two stale appendix numbers: §4 imputation medians "$19.62–$22.17" (now
$18.28/$19.49/$20.65) and §8 "~0.5M entrants" (now 0.83M).

## Deliverables written (Infrastructure/explorations/2026-07-09_holistic-eval/)
- 2026-07-09_entry-model-holistic-evaluation.md (per-question verdicts)
- 2026-07-09_headline-centering-decision-memo.md (Q1 user decision)
- 2026-07-09_ranked-fix-list.md (16 items, effort-estimated, wave-ordered)

## Specialist corroboration (2 of 3 in)
- **methodology-reviewer** (review-reports/methodology-report.html): concurs Q1 under-centered,
  penalty=0 the weak link; MR-001 HIGH. Key balance added: offsetting UPWARD biases (frictionless
  matching find-rate 1, no fixed cost, UI omitted from NI(0)) make net direction two-sided → I
  refined Q1/memo away from "center is 1.5M" to "penalty≠0 co-central ≈1.1–1.2M + two-sided
  disclosure." Q2 joint corner could exceed 2.5–3M. Q3 double-count VERIFIED ABSENT. Q4 the
  min(0.90,·) is dead code; ceiling_ext=1.5 untested. Q5 both confirmed.
- **conceptual-consistency-reviewer** (review-reports/doc-consistency-report.html): 1 HIGH
  (CC-001 appendix "~0.5M"), CC-004 Figure 6 caption still "reservation wage", CC-002 composition
  disagrees across docs, CC-003 firm-capture 2% vs <1%, CC-007 unweighted OLS vs EARNWT claim.
  Added to fix list #5, #15.
- **data-consistency-reviewer** (number verification, review-reports/doc-number-report.html): DONE.
  All 96 numbers reconcile to the live run; NO 0.46M/1.42M-era survivors. Findings: DN-001 HIGH
  (appendix $158B vs live 160.3B), DN-002 MEDIUM (appendix "under one percent" firm capture wrong
  for headline β=0.5 = 1.5%), DN-003 ($19.62–$22.17 stale), DN-004 (23.6% comparator not
  persisted), DN-005 (Fig11b household $ not persisted), DN-006/8 (composition wording). Folded
  into fix list #5, #5b. Infra note: nonemployed_pool/household_links live in data/processed/ not
  the population/ dir the manifest indexes — confirm the path split is intentional.

## Session close
All 3 specialists in and integrated; 3 deliverables + this log written. All 9 questions answered
with verified evidence. Static parity PASS; canonical pool preserved byte-identical. No analysis
code modified. Awaiting user decision on Q1 (headline centering, Option A recommended).

## Decision log
- Headline recommendation: Option A (re-center on joint evidence bundle, 0.83M as labeled floor,
  two-sided bias disclosure). Genuine user judgment call — flagged as such, not overridden.
- No analysis code changed (plan-first honored). pen20/skewstat_hi builds run read-only + deleted.
