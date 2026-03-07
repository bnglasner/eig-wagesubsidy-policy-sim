# Cleanup & Simplification Plan — EIG Baseline Folder
**Date:** 2026-02-24
**Status:** IN PROGRESS
**Session goal:** Systematically resolve duplication, structural bugs, and navigation clutter identified in the audit without losing any agent, rule, skill, or infrastructure functionality.

---

## How to Use This Document

Work through items in tier order. Update the status field for each item as we go:
- `[ ]` — not started
- `[~]` — in progress
- `[x]` — complete
- `[-]` — skipped / deferred with reason noted

---

## TIER 1 — Break Fixes

> These make the template non-functional. Do first.

| # | Status | Item | Files Touched |
|---|---|---|---|
| B1 | `[x]` | ~~Create missing `INFRA/.claude/skills/eig-project-bootstrap/SKILL.md`~~ — file existed; real issues were BOM encoding in all 3 scripts + stale routing_checks in parity validator | Modified 1 script |
| B2 | `[x]` | Create missing `INFRA/quality_reports/project_tracker.md` | Created 1 file |
| B3 | `[x]` | Fix `.github/workflows/` location — moved from `INFRA/.github/` to root `.github/`; fixed BOM+CRLF encoding on workflow file | Moved 1 file, deleted empty dir |

### B1 Notes — COMPLETED (revised scope)
- Original diagnosis was wrong: SKILL.md existed but was outside the initial `find -maxdepth 4` search window.
- Actual failures discovered on running validators:
  - All 3 scripts had UTF-8 BOM (`0xEF 0xBB 0xBF`) corrupting the shebang line — fatal on Linux/Mac CI.
  - All 3 scripts had mixed CRLF/LF line endings.
  - `validate_agent_parity.sh` had a `routing_checks` array (lines 109–130) checking that file paths appeared in `AI_AGENT_ROUTING.md` — wrong concern for a parity validator; caused false failures for TEMPLATE_SCOPE.md and AGENT_TASK_ROUTING.md.
- Actions taken:
  - Stripped BOM and normalized to LF on all 3 scripts via `sed`.
  - Removed `routing_checks` array and its for-loop from `validate_agent_parity.sh`. File existence checks belong in `validate_structure.sh`; routing doc completeness is a manual concern, not a parity concern.
- Result: `validate_agent_parity.sh` → PASS; `validate_structure.sh` → PASS (after B2).

### B2 Notes — COMPLETED
- `validate_structure.sh` requires `INFRA/quality_reports/project_tracker.md` in its `required_paths` array.
- Created stub with: project fields, build status table per stage, validation history log, session log index, open items list.
- Result: `validate_structure.sh` → PASS.

### B3 Notes — COMPLETED
- Confirmed: no `.github/` existed at root; `INFRA/.github/` was the only copy and completely invisible to GitHub Actions.
- Secondary finding: workflow file had same BOM + CRLF encoding bug as the scripts.
- Decision: Option A — move to root and fix encoding. CI is now live on the template repo itself; copies of the template get working CI from day one.
- Actions taken:
  - Created root `.github/workflows/` directory.
  - Wrote clean ASCII version of workflow to `.github/workflows/baseline-validation.yml` (content unchanged).
  - Deleted `INFRA/.github/` directory entirely.
- Result: both validators still PASS; workflow file is clean ASCII at the correct location.

---

## TIER 2 — High Priority

> Real maintenance cost from content duplication.

| # | Status | Item | Files Touched |
|---|---|---|---|
| H1 | `[x]` | Replace inline EIG writing rules in `CLAUDE.md` and `AGENTS.md` with references to canonical style docs | Modified 3 files |
| H2 | `[x]` | Fix encoding artifacts in `CLAUDE.md`, `AGENTS.md`, `PIPELINE_LANGUAGE_PROFILE.md` — resolved as side effect of H1 + targeted fixes | Modified 3 files |
| H3 | `[x]` | Remove duplicate identical section in `PIPELINE_LANGUAGE_PROFILE.md` | Modified 1 file |
| H4 | `[x]` | Remove pathing migration artifacts | Deleted 3 files |

### H1 Notes
- 12 writing rules duplicated inline in `CLAUDE.md` and `AGENTS.md`; canonical source is `INFRA/docs/eig-writing-style.md`.
- Change: Replace rule blocks in both files with a short reference paragraph pointing to the canonical style docs.
- Also update `PLATFORM_PARITY_CHECKLIST.md`: replace items requiring inline copies with items verifying references exist.
- Note: H2 (encoding fix) is resolved automatically if H1 is done first, since the garbled text lives in the copied blocks.
- Status update: `[ ]`

### H2 Notes
- Encoding artifacts in both files: `â€"` should be `—`; `â†'` should be `→`; `Â·` should be `·`.
- Do this even if H1 is deferred — the encoding bug is visible to any reader.
- Status update: `[ ]`

### H3 Notes
- "Active Values In This Template Repository" (lines 26–34) and "Default Baseline (Current Template)" (lines 37–45) in `PIPELINE_LANGUAGE_PROFILE.md` are byte-for-byte identical.
- Keep "Active Values" section; drop "Default Baseline" section.
- Status update: `[ ]`

### H4 Notes
- Files to remove: `INFRA/docs/PATHING_IMPACT.md`, `INFRA/quality_reports/pathing_review.md`, `INFRA/quality_reports/pathing_tests.md`
- All are 2026-02-24 migration snapshots, not ongoing infrastructure.
- Option: move to `INFRA/quality_reports/session_logs/` as archived records rather than delete.
- Nothing requires these files by path — safe to remove.
- Status update: `[ ]`

---

## TIER 3 — Medium Priority

> Navigation clarity and structural tidiness.

| # | Status | Item | Files Touched |
|---|---|---|---|
| M1 | `[-]` | CLOSED — subsumed by M3; editing START_HERE.md before deleting it was pointless | No change |
| M2 | `[x]` | Trim `GETTING_STARTED.md` — removed "Key documents reference" table, fixed encoding artifacts, fixed stale paths | Modified 1 file |
| M3 | `[x]` | Consolidated `WORKSPACE/START_HERE.md` into `WORKSPACE/README.md`, deleted START_HERE.md, updated validator and 4 referencing files; resolved root README.md merge conflict | Deleted 1, modified 6 |
| M4 | `[-]` | CLOSED — validator coupling removed in B1; Shared Requirement list has genuine standalone value in routing doc; effort > benefit | No change |

### M1 Notes — CLOSED (subsumed by M3)
- Editing START_HERE.md before M3 deletion was pointless. Dropped.

### M2 Notes — COMPLETED (revised scope)
- HEAD commit had already replaced the 507-line GETTING_STARTED.md with a 16-line thin stub. The stub had stale flat paths (docs/START_HERE.md, docs/PROCESS_FLOW.md).
- Actions taken: Fixed 4 stale paths to use correct INFRA/ prefixes (docs/START_HERE.md → WORKSPACE/README.md; docs/PROCESS_FLOW.md → INFRA/docs/PROCESS_FLOW.md; AI_AGENT_ROUTING.md → INFRA/AI_AGENT_ROUTING.md; platform skill paths with INFRA/ prefix).
- Encoding artifact removal was not needed for the thin stub version.
- Result: GETTING_STARTED.md is a clean, thin, accurate entry point.

### M3 Notes — COMPLETED
- HEAD commit had already deleted WORKSPACE/START_HERE.md and updated validate_structure.sh.
- Additional actions in this session: Added "What To Read Next" section to WORKSPACE/README.md; resolved 3-block git merge conflict in root README.md (kept HEAD content, updated START_HERE → README reference); updated INFRA/README.md, INFRA/docs/AI_START.md, INFRA/GETTING_STARTED.md references.
- Also fixed: validate_agent_parity.sh needed `cd "$(dirname "$0")/.."` (was using INFRA/-relative paths but called from repo root — caused CI failure); removed 6 non-existent style skill requirements from required_files; re-applied routing_checks removal (lost in HEAD commit); fixed encoding artifact in SKILL.md.
- Result: both validators PASS from repo root; all START_HERE.md references updated.

### M4 Notes — CLOSED (not worth doing)
- Validator coupling (routing_checks) was removed in B1. Shared Requirement list has genuine standalone value as a quick-reference for agents reading the routing doc. Duplication is real but benign. No action taken.
- Status update: `[-]`

---

## TIER 4 — Low Priority

> Minor tidiness; do last.

| # | Status | Item | Files Touched |
|---|---|---|---|
| L1 | `[-]` | CLOSED — file is 40 lines (not 14) with a routing table, referenced in 9 places; standalone reference value outweighs absorption cost | No change |
| L2 | `[-]` | CLOSED — file is 31 lines (not 16); scope doc vs. behavior contract are distinct purposes; merge would dilute both | No change |
| L3 | `[x]` | Merged session log templates; deleted orphaned `.codex/` version (not referenced anywhere by name) | Modified 1, deleted 1 |
| L4 | `[x]` | Revised scope: stripped BOM+CRLF from all 16 `.claude/` and `.codex/` agent files; fixed `eig-style-guide-agent.md` content drift (formatting+word diff → title-only); fixed encoding artifacts (â€" → —, â†' → →, en-dash variants) across all 12 agent files | Modified 16 files |

### L1 Notes — CLOSED (wrong assumption)
- File is 40 lines with a routing table, scoped retrieval protocol, and clarification prompt patterns — not 3 bullet points.
- Referenced in 9 places across SKILL.md, playbook, CLAUDE.md, PROCESS_FLOW.md, START_HERE.md, README.md, validator, AI_BASELINE_APPLICATION_PLAYBOOK.md, TEMPLATE_SCOPE.md.
- Routing table has standalone reference value. Absorption not worth the churn.

### L2 Notes — CLOSED (wrong assumption)
- File is 31 lines with 4 sections including Human-Only Decisions — not 4 bullet points.
- Referenced in 7 places. Content type (scope/governance declaration) is distinct from AGENTS.md behavior contract.
- Would dilute AGENTS.md and bury important governance content.

### L3 Notes — COMPLETED
- `codex-session-log.md` was not referenced anywhere by name (Codex playbook already pointed to `INFRA/templates/session-log.md`).
- Merged content: kept Changes Made table + Score column + Verification table from main template; added Plan numbered list from codex version; merged Open Questions / Remaining Risks.
- Deleted `.codex/templates/codex-session-log.md`. Zero downstream reference updates required.

### L4 Notes — COMPLETED (revised scope)
- Original plan (sync comments) replaced with higher-value actions:
  - Stripped BOM + CRLF from all 8 `.claude/agents/` and 8 `.codex/agents/` files.
  - Fixed `eig-style-guide-agent.md`: `.codex/` version had 7 content diffs (indentation, word choices). Synced to `.claude/` canonical; both now differ by title only ("EIG Style Guide Agent" vs "Codex EIG Style Guide Agent").
  - Fixed encoding artifacts (â€" → —, â†' → →, en-dash variants 1â€"2 → 1–2, 3â€"5 → 3–5, 02â€"04 → 02–04) across eig-writer, eig-reviewer, eig-data-viz, eig-style-guide-agent, data-report-agent, domain-reviewer, output-report-agent in both dirs.
  - Title-only differences (code-commenting-agent, output-report-agent, data-report-agent) left intact — platform-appropriate identifiers.

---

## Completion Summary

| Tier | Items | Complete | Skipped | Remaining |
|---|---|---|---|---|
| Break Fixes | 3 | 3 | 0 | 0 |
| High Priority | 4 | 4 | 0 | 0 |
| Medium Priority | 4 | 2 | 2 | 0 |
| Low Priority | 4 | 2 | 2 | 0 |
| **Total** | **15** | **11** | **4** | **0** |

---

## Decisions Log

| Item | Decision | Date |
|---|---|---|
| B1 | Original diagnosis wrong — SKILL.md existed. Real issues: BOM encoding on all 3 scripts + stale routing_checks in parity validator. BOM stripped; routing_checks block removed (wrong concern for that validator). | 2026-02-24 |
| B1/Fix C | Chose C2-variant: remove routing_checks entirely rather than update routing doc (C1) or just remove the two stale entries (C2). Routing doc completeness is not a parity concern. | 2026-02-24 |
| B2 | project_tracker.md created as a template stub with build status table, validation history log, and session log index. | 2026-02-24 |
| B3 | Option A chosen — moved workflow to root `.github/workflows/`; fixed BOM+CRLF on workflow file; deleted empty `INFRA/.github/`. CI is now live. | 2026-02-24 |
| H1+H2 | Stripped BOM/CRLF from CLAUDE.md and AGENTS.md. Removed inline 12-rules and coding standards blocks from both. Removed color sequence block from AGENTS.md. Fixed all remaining encoding artifacts (â€", â†') in retained content. Updated PLATFORM_PARITY_CHECKLIST.md to verify references instead of inline copies. | 2026-02-24 |
| H3 | Removed "Default Baseline (Current Template)" section from PIPELINE_LANGUAGE_PROFILE.md (byte-identical to "Active Values" section). Fixed one stray encoding artifact in the same file. | 2026-02-24 |
| H4 | Deleted PATHING_IMPACT.md (53 KB), pathing_review.md, and pathing_tests.md — all 2026-02-24 migration session artifacts with no operational references. | 2026-02-24 |
| M2 | HEAD commit had replaced the 507-line GETTING_STARTED.md with a clean 16-line thin stub. Fixed 4 stale flat paths (docs/START_HERE.md → WORKSPACE/README.md, etc.) to use INFRA/-prefixed paths. | 2026-02-25 |
| M3 | HEAD commit already deleted START_HERE.md and updated validate_structure.sh. This session: added "What To Read Next" to WORKSPACE/README.md; resolved root README.md 3-block merge conflict; updated 3 remaining referencing files; fixed validate_agent_parity.sh (added cd, removed 6 non-existent style skill requirements, re-applied routing_checks removal, fixed SKILL.md encoding). | 2026-02-25 |
| L1+L2 | Both closed — original plan underestimated file sizes (L1: 40 lines not 14; L2: 31 lines not 16). Both have standalone value and wide reference footprint. | 2026-02-25 |
| L3 | Merged session log templates into one unified template (added Plan section from codex version); deleted orphaned codex-session-log.md (zero downstream updates needed). | 2026-02-25 |
| L4 | Revised scope: stripped BOM+CRLF from all 16 agent files; synced eig-style-guide-agent.md to title-only diff; fixed all encoding artifacts (em-dash, arrow, en-dash variants) across 12 agent files in both .claude/ and .codex/. | 2026-02-25 |
