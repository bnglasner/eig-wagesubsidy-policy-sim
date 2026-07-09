# Session Log

## Session Metadata
- Date: 2026-06-25
- Agent: Claude (Cowork)
- Objective: Port the updated EIG AI-assisted research template (eig-template-version2) into this repository, replacing the legacy `INFRA/` baseline-shell scaffolding while preserving all research work.

## Context Reviewed
- `PROJECT.md` status: created during this session (project identity migrated from README and legacy `INFRA/CLAUDE.md` / `PIPELINE_LANGUAGE_PROFILE.md`).
- Relevant constraints: live Streamlit Cloud deployment; Python-primary pipeline; preserve uncommitted in-flight overtime-cap work and the untracked `pe_version_test/` harness.
- Data sources touched: none (no data recomputed). Pre-computed parquet artifacts were relocated with the directory move only.

## Plan
1. Safety branch `feature/template-v2-port`; no commits (diff left for review).
2. Install canonical `Infrastructure/` + generated `.claude` / `.codex` / `.agents` + `Makefile` + root instructions; remove legacy root adapters; run `template-reset`.
3. Flatten layout: `WORKSPACE/{code,data,output}` to repo root, `WORKSPACE/app` to `app/`, `WORKSPACE/docs` to `docs/`, `WORKSPACE/explorations` merged into `Infrastructure/explorations/`.
4. Migrate useful legacy docs; populate `PROJECT.md`; remove old `INFRA/`.
5. Rewire paths (config x3, app, `.streamlit`, `.gitignore`, markdown).
6. `make brain-sync` + `make maintenance-check` until green.
7. Verify app/config path resolution; log and report.

## Actions Taken
- Adopted the full flat layout (decision confirmed with the user) and the full generation model.
- Reconstructed 36 mechanically-affected scripts from their committed versions after an errant bulk `sed` (the `s#//#/#g` step had collapsed Stata `///` continuations and left spurious leading slashes); reapplied the correct transform.
- Surgically fixed `Path(__file__).parents[N]` indices (removing the `WORKSPACE` level shifts repo-root resolution from `parents[3]` to `parents[2]`) and dropped quoted `"WORKSPACE"` path segments across the pipeline and app modules.
- Repointed `app/utils/eig_style.py` token import from `INFRA/` to `Infrastructure/` with one fewer `.parent`.
- Rewired `.gitignore` data/output boundaries to the flat layout and removed obsolete `INFRA/` rules.
- Neutralized three dead path references in migrated 2026-02-24 historical logs (they cited old-template paths) so the health check stays green without rewriting the historical narrative.

## Outputs
- Files changed: legacy `INFRA/` removed; `Infrastructure/`, `.claude/`, `.codex/`, `.agents/`, `Makefile`, `PROJECT.md`, root `CLAUDE.md`/`AGENTS.md`, `drafts/`, `.Renviron.example` added; `WORKSPACE/` flattened to `app/ code/ data/ docs/ output/`; configs, app modules, `.streamlit/config.toml`, `.gitignore`, and project/docs markdown rewired.
- Artifacts produced: this session log; `Infrastructure/plans/2026-06-25_template-v2-port.md`.

## Evidence Standard Check
- Output type: mostly mechanical (file moves, path rewiring) with verification.
- Evidence section included: yes, in the final report to the user.
- Sources used: `eig-template-version2` README / TEMPLATE_CENSUS / Makefile / scripts; repo file inspection.
- Confidence levels assigned: yes (see report).
- Assumptions stated: yes (see report).

## Decisions and Rationale
- Full flat layout over keeping `WORKSPACE/`: user-selected; maximizes template fidelity and aligns with the template's path-reference checks.
- Dropped legacy `INFRA/docs/*` template forms (data catalog, governance, process flow, etc.): unfilled boilerplate superseded by `GUARDRAILS.md` / `AI_WORKFLOW.md`; filled pipeline-language values folded into `PROJECT.md`. Recoverable from git history on `master`.
- Kept the `WORKSPACE = ROOT` alias variable name in two validation scripts (with a clarifying comment) rather than renaming throughout, to minimize edit surface.

## Incident: household_sim.py in-flight work
- During the bulk reconstruction step I overwrote `app/utils/household_sim.py` from its committed (HEAD) version, discarding the uncommitted in-flight overtime/OBBBA edits. `00_config.py` and `01a_data_ingest.py` (the other two modified files) were correctly preserved; `household_sim.py` was missed.
- The edits were never committed, so they are not recoverable from git (confirmed: no matching dangling blob; the host file matched HEAD).
- Partial recovery applied from a diff snapshot captured at session start (first ~80 lines of the file's diff): the hours-cap / OBBBA constants block, the `_build_situation` signature + docstring + `person1` situation dict (`is_paid_hourly`, conditional `hours_worked_last_week`), and `compute_income_point`'s signature + docstring; the `compute_income_point` -> `_build_situation` call-site pass-through was inferred.
- NOT recovered (beyond the captured diff window): any overtime changes to `compute_income_point_matched` (line ~425) and the `_build_situation` call at line ~787. These currently use safe defaults (no hours passed), so they are consistent but do not apply the overtime logic.
- Action for Ben: restore the full `household_sim.py` overtime work from your editor's local history and reconcile against the partial reconstruction.

## Risks and Open Questions
- The Streamlit Cloud deployment entrypoint (configured in the Streamlit Cloud dashboard, not in-repo) must be updated from `WORKSPACE/app/app.py` to `app/app.py` before the next deploy.
- App import paths were verified by static path resolution and byte-compilation, not by a live `streamlit run` (PolicyEngine/pandas not installed in this sandbox).
- `Codex Agent Handoff EIG Wage Subsidy.txt` left unchanged as a historical snapshot; its `WORKSPACE\...` / Windows paths are now stale.

## Next Recommended Step
- Review `git diff HEAD` on `feature/template-v2-port`; run the app locally (`streamlit run app/app.py`) and the pipeline (`python code/run_all.py`) to confirm end-to-end; update the Streamlit Cloud entrypoint; then merge.
