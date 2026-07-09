# Session Log — Combine drafts → Word doc + full-review + review-style

**Date:** 2026-07-09
**Task (user, via /orchestrate):** Combine the summary brief and technical appendix into a single Word doc with figures integrated in place; run /full-review and /review-style on the combined draft.
**Full-log cadence:** not yet set this session (asked to defer; incremental logging applied).

## Decisions & events

1. **Scoping.** Two source drafts in `drafts/` (summary + technical appendix). Figures fig01–fig15 referenced but absent from `output/figures/main/`. Figure scripts `05c`/`05d` (R) fully implemented; population parquets present; R 4.5.2 + packages installed.
2. **Combined artifacts.** Built `drafts/2026-07-09_combined-brief-and-appendix.md` (review source) and `.docx` (deliverable). Merge = brief body → page break → appendix, both "Evidence (strip before publication)" blocks retained for review. Fixed stale in-text link to the appendix (`[..](…technical-appendix.md)` → "the technical appendix below").
3. **Figures regenerated:** ran `05c` + `05d`. 15/17 generated. 2 (`fig08_pool_wage_distribution`, `fig12_clawback_net_gain`) require `data/processed/nonemployed_pool.parquet`, a stage-01 output — initially absent (empty `data/raw/`). Salvaged `fig14`/`fig15` (they don't need the pool; had only been skipped when `05d` halted at `fig08`).
4. **Word doc.** pandoc md→docx (abs image paths, placeholders for the 2 missing figs). Added `<Default Extension="png">` to `[Content_Types].xml` (pandoc omitted it → images would not render). Validated PASS. 35 pp, 15 images, 7 tables, 11 footnotes, TOC, page break. PDF spot-check: figures + tables render correctly.
5. **Number discrepancy flagged (pre-rerun):** `fig14` code/subtitle said evidence-central **1.25M / floor 0.83M / high 3.37M**; draft says **1.48M / 1.02M / 3.80M** → committed intermediates looked like a prior vintage.
6. **Pipeline decision (user):** initially "run full microsim first"; on report that `run_all.py` hard-fails at `00_ingest` (no repo `.Renviron`, empty `data/raw/`), user clarified IPUMS keys ARE set (home `~/.Renviron` + env var) and R works → do a **fresh data pull**; treat re-run output as source of truth and validate the draft after.
7. **Full pipeline launched:** `.venv/bin/python code/run_all.py` (tier 1 → stages 01/02/05). Submitted IPUMS extract #580; regenerates intermediates + all 17 figures. PolicyEngine not needed (01b precompute off; 408 schedules present).
8. **/review-style:** ran eig-reviewer on the combined draft → `drafts/review-reports/style-review-report.html`. 7 ERRORs / 8 SUGGESTIONs. Headline errors: figures lack markdown `Source:` lines; two citation systems (footnotes in brief vs. author-date in appendix); unresolved `[TO VERIFY]`; Chicago-with-parens journal format; bare URLs; footnote [^5] is not a real citation.

## Pending
- Await pipeline completion → verify 17 figures + fresh intermediates → rebuild docx with fig08/fig12 → spawn 5 /full-review agents (code, methodology, ai-skeptic, number, consistency) against fresh outputs + combined draft. Reports overwrite `drafts/review-reports/`.
- Validate the 1.48M/1.02M/3.80M draft figures against fresh pipeline output.

## ⚠️ Pipeline bug found (high severity)
`run_all.py::execute_python_script()` loads each Python stage via `importlib` `exec_module()` with the module name = file stem, so `__name__` is never `"__main__"`. Every Python stage guards `if __name__ == "__main__": main()`, so **`main()` never runs** under `run_all.py` — the scripts are only imported. "SUCCESS" == "imported without error." Only the R stages (run via `subprocess.run`) actually execute. Result of the "fresh" run: raw CPS + ORG panel refreshed (R), but `hourly_workers.parquet`, `household_links.parquet`, `nonemployed_pool.parquet`, and all `population/*.parquet` were NOT regenerated (all still 16:14 checkout mtime). Workaround: ran the Python stages directly (`.venv/bin/python code/.../NN_*.py`) in dependency order. To be surfaced in code-error + ai-skeptic reports.

## Results — reviews (all complete)

Draft numbers **validated against the fresh re-run**: floor 1.02M / evidence-central 1.48M / high 3.80M (groups 0.24/1.06/0.18), grid 0.23–3.80M, gross $89.75B / net $72.12B, 20.81M workers, $4,314 avg. The earlier "1.25M" was a stale hardcoded string in `05d`'s fig14 subtitle, not the data.

Full-review (overwrote `drafts/review-reports/`):
- **Code** (CE): 1 CRITICAL, 2 HIGH, 1 MED, 2 SUGG. CE-001 run_all main() no-op (CRITICAL); CE-002 02a label/positional indexing bug (HIGH); CE-003 fig14 stale subtitle (HIGH).
- **Methodology** (MR): risk HIGH — 2 HIGH (no exclusion restriction in Heckman; entry calibrated not identified), 12 MED, 3 LOW. Weights EARNWT/WTFINL validated correct.
- **AI-skeptic** (AS): SUSPECT — 1 CRITICAL (AS-001 reproduced run_all bug), 2 HIGH (fig14; falsified §10 reproducibility claim), 3 MED, 5 LOW, 1 INFO. Citations + CPS variables CLEAN (no fabrication).
- **Numbers** (DN): 96 extracted / 85 verified / 11 flagged, no CRITICAL. HIGH: DN-001 fig14 subtitle, DN-002 ρσ +0.08 vs +0.11.
- **Consistency** (CC): 48 claims / 42 consistent / 6 flagged, risk HIGH. CC-001 eligibility filter lacks `PAIDHOUR==2` (~4.9M salaried counted as "paid-hourly") — most likely to move published numbers; CC-002 fig14.

Style review (`style-review-report.html`): 7 ERROR / 8 SUGGESTION.

### Convergent cross-report issues (fix first)
1. **run_all.py never runs the Python analysis** (CE-001, AS-001, AS-003) — CRITICAL. Fix the `exec_module`/`__main__` invocation.
2. **fig14 stale subtitle 1.25M/0.83M/3.37M** (CE-003, AS-002, DN-001, CC-002) — 1-line fix at `05d_supporting_figures.R:617` + stale comments in 00_config/02g.
3. **Eligibility frame** (CC-001) — decide whether eligibility is paid-hourly only; `01a` currently includes salaried with imputed wage.
4. **ρσ +0.08 vs +0.11** (DN-002, CC-003) — reconcile brief Evidence block.

## Status: COMPLETE (deliverables + 6 reports). Handoff below.
- Deliverable: `drafts/2026-07-09_combined-brief-and-appendix.docx` (35pp, 17 figs, 7 tables, validated) + review-source `.md`.
- Open for author: the 4 convergent issues above; the [TO VERIFY] citations; the EIG style errors (dual citation systems, figure Source: lines).

## Paid-hourly eligibility correction (user decision, 2026-07-09)
User decided the subsidy applies to paid-hourly workers only (resolves CC-001). Changes:
- `01a_data_ingest.py`: added `org["paid_hourly"]` to the eligibility mask (+ the n_dependents companion mask), with a documenting comment.
- `02e_take_up_by_group.py`: added `paid_hourly` to the base filter so both numerator (recipients) and denominator ("group's workers") are on the paid-hourly frame.
- `05d_supporting_figures.R:617`: fixed fig14's stale hardcoded subtitle to 1.49M/1.02M/3.81M (resolves CE-003/AS-002/DN-001/CC-002).

**Pipeline-orchestration note:** `run_all.py` still can't run the Python stages (the `main()`/`__name__` bug), so stages were run directly with `.venv/bin/python`. A scripting bug in my first re-run helper (`[ $rc -ne 0 ] && return $rc` returns 1 on success) silently stopped the chain after 01a; caught it and re-ran downstream correctly.

**Impact (paid-hourly only):** eligible 20.81M→**15.88M**; gross $89.75B→**$55.88B**; net (static) $72.12B→**$45.11B**; net band $72–78B→**$45.1–47.6B**; avg subsidy $4,314→**$3,518**; overall take-up 15.5%→**21.7%** of paid-hourly workers (base 73.3M). Entry essentially unchanged (1.49M evidence-central; entry is on the non-employed pool). Structural firm capture ~3% sticky / up to ~58% ($109.1B) all-renegotiate. Marginal cost/entrant ~$5,300 gross/$3,900 net; fully-loaded ~$32,000/job. Notably, gross now falls within the project's $40–60B target range.

**Draft fully re-synced** (~55 numeric/prose edits across brief + appendix + internal Evidence blocks, voice preserved; framing shifts handled: "one in seven/eight"→"one in ten"; "a fifth of the hourly workforce"→"more than a fifth of paid-hourly workers"; "quarter-million" FTE→"nearly 200,000"). Straggler re-scan clean. Docx rebuilt (17 figs, validated). Re-verify: number + consistency reviewers re-run against the corrected draft (in progress).

Note: the two SOURCE drafts (`2026-07-08_…summary.md`, `2026-07-09_…technical-appendix.md`) still carry the pre-correction numbers; the combined file is authoritative for the deliverable.

## Re-verify results (paid-hourly draft) — CLEAN
Re-ran number + consistency reviewers on the corrected draft (overwrote the two reports):
- **Consistency:** 62 claims, 59 consistent, 3 flagged (2 MEDIUM, 1 LOW), **no HIGH**; risk HIGH→MEDIUM. **CC-001 RESOLVED** (paid-hourly enforced in 01a + 02e; text matches code).
- **Numbers:** 124 extracted, 112 verified; every headline reconciles. Residuals fixed this session: DN-001 (stale 0.08–0.36 hours band in brief Evidence block → 0.06–0.28); clawback medians 19/24→18/23 to match code (18.1/26.9/23.1); "one in nine"→"one in eight" cliff-payup (12.4%); brief base-semantics direction ("raise"→"slightly lower" single-mother entry). Final straggler scan clean; docx rebuilt + validated (17 figs, 7 tables).
- fig02/fig14 visually confirmed showing new numbers; rendered figures carry Source lines (style review's "figures lack Source" applies to md text, not the images).

**Remaining open (author, not blocking):** superseded all-earner-frame illustrative figures ($26.00 median, ρσ+0.30, $31/$15.34 predicted wages, Fig 11b household net-income readouts) are labeled historical/illustrative and not reproducible from the current pipeline (expected); EIG style errors from /review-style (dual citation systems, [TO VERIFY] citations); the two source drafts still hold pre-correction numbers (combined file is authoritative); run_all.py main() bug (chip spawned).

## Merge → align → main → additional full-review (user, 2026-07-09)
- **Merged** the fix-task branch (`claude/magical-varahamihira-7a0d6f`, uncommitted worktree) into master by applying its 2-file diff: `run_all.py` (call `main()` after `exec_module`, guarded) + `05a_main_outputs.py` (`pct_workers`→`pct_of_recipients`). Brought over its session log. My tree hadn't touched either file → clean apply.
- **Aligned**: ran the fixed `python code/run_all.py` once → 14 SUCCESS / 0 FAILED; every Python stage runs with real elapsed times (02g 63.5s, 02f 45.6s…); IPUMS cache-hit (no resubmit); canonical outputs = delivered paid-hourly numbers (15.88M/$55.88B/$45.11B). Confirms one command now reproduces the doc.
- **Committed to master** (data/output parquets are TRACKED, so canonical paid-hourly intermediates committed too; figures are gitignored, preserved in the docx):
  - `ae5c6e1` run_all.py stage-execution fix (+05a)
  - `6706345` paid-hourly eligibility + combined/resynced deliverable + canonical intermediates
  - `acd0f55` resync fig10 + fig13 hard-codes to paid-hourly regime (+1.25M comments, appendix footer clawback)
- **Additional /full-review** (5 agents, committed master): code 0 CRIT/1 HIGH; methodology HIGH risk 2 HIGH/7 MED (design-inherent + new MR-003 salaried-sector trade-off from paid-hourly); ai-skeptic **CAUTION** (0 CRIT/0 HIGH, up from SUSPECT); numbers 0 CRIT/0 HIGH (118/111 verified); consistency 2 HIGH (fig10/fig13 hard-codes). Prior CRITICAL/HIGH all confirmed RESOLVED (run_all, 05a, fig14, CC-001 paid-hourly).
- **Post-review fixes** (my deliverable-correctness misses): fig10 + fig13 hard-codes (the 2 consistency HIGH), appendix footer clawback (DN MEDIUM), 05d 1.25M comments (AS MEDIUM). Regenerated figures, rebuilt+validated docx, visually confirmed fig10/fig13. Ran a confirmatory number+consistency pass.
- **Remaining (chipped/expected, not blocking):** `02a _agg_by_group` label/positional index bug — pre-existing, output-neutral (masked on current data), HIGH → chip `task_ecbce045`. `_manifest.csv` mislabels floor as "0.83M" (05z, INFO). Superseded all-earner-frame illustrative appendix figures labeled historical (expected). `.claude/worktrees/…` left in place (content now in master; remove with `git worktree remove` when that session closes).

## Scope note
- Code-facing reviews scoped to `code/` (47 files; the analysis pipeline), excluding `Infrastructure/` tooling and `app/`. Several `.do`/`03`/`04` files are template baseline stubs (tier-1 project).
