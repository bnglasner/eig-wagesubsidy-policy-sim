# INFRA/AGENTS.md

## Purpose

This repository is a baseline shell for new EIG research projects. Any AI agent working here must follow a question-first customization workflow before implementing changes.

## Platform Routing

1. Read `INFRA/AI_AGENT_ROUTING.md` to determine platform-specific config.
2. Claude Code agents should use `INFRA/.claude/`.
3. Codex/ChatGPT agents should use `INFRA/.codex/`.
4. `INFRA/AGENTS.md` remains the cross-platform top-level contract.

## Mandatory Workflow

Use these workflow IDs in all platform-specific adapters to prevent drift. For full execution steps, see `INFRA/docs/PROCESS_FLOW.md`.

1. **WF1** (`PARITY:WF1:INTAKE_READ`): Read `INFRA/docs/PROJECT_INTAKE.md`; verify all `BLOCKER` fields.
2. **WF2** (`PARITY:WF2:MISSING_REQUIRED_ASK_AND_PAUSE`, `PARITY:WF2:MAX5_CONTEXTUAL_FOLLOWUPS`): If any `BLOCKER` is missing, ask at most 5 targeted follow-up questions using completed `BLOCKER` answers and prior `SOFT_REQUIRED` context, then pause implementation.
3. **WF3** (`PARITY:WF3:DECISIONS_LOGGED`): Convert intake answers into decisions in `INFRA/docs/PROJECT_DECISIONS.md`.
4. **WF4** (`PARITY:WF4:STRUCTURE_CUSTOMIZED`): Apply baseline structure and naming from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
5. **WF5** (`PARITY:WF5:PLACEHOLDERS_UPDATED`, `PARITY:WF5:LANGUAGE_PROFILE_UPDATED`): Update placeholders in `WORKSPACE/README.md`, `INFRA/CLAUDE.md`, and `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
6. **WF6** (`PARITY:WF6:SESSION_LOGGED`): Create a session log in `INFRA/quality_reports/session_logs/`.

Platform-specific instructions in `INFRA/.claude/` and `INFRA/.codex/` must preserve `WF1`–`WF6`.

## Required Intake Questions

Collect and confirm intake fields according to `INFRA/docs/PROJECT_INTAKE.md` quality gates:
- `BLOCKER` fields must be complete before implementation.
- `SOFT_REQUIRED` fields should be collected and used for context; proceed with explicit assumptions in `INFRA/docs/PROJECT_DECISIONS.md` when needed.
- `OPTIONAL` fields are non-blocking context only.

## Implementation Rules

- Keep staged script numbering (`00` to `05`).
- No hardcoded absolute paths in production scripts.
- For any generated run-all orchestrator (for example `WORKSPACE/code/run_all.R`), include a readable flag section that lists every drafted pipeline component explicitly with a `TRUE` or `FALSE` setting.
- In run-all files, define flags one component per line in stage order with clear labels/comments; do not use compact list-only flag declarations that hide what will run.
- If `Secondary language(s)` is populated in the intake, pause before implementing any cross-language step. Present the user with integration options and pros and cons for each (see `INFRA/docs/PROJECT_INTAKE.md` field note). Do not choose an approach without explicit user direction.
- Keep all paths relative to project root from the bootstrap/config entry defined in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
- Preserve reproducibility boundaries in `.gitignore`.
- Do not delete template files unless replaced by project-specific equivalents.

## Cloud Storage Prohibition (AI Agents)

- AI agents must not access, sync, authenticate, or otherwise interact with Google Drive or Dropbox (including APIs, desktop sync folders, scripts, or web links).
- If a user requests any Google Drive or Dropbox interaction, the agent may only provide step-by-step instructions for a human to perform manually, and must not execute or automate those steps.

## Data Governance Defaults

`INFRA/docs/DATA_GOVERNANCE_POLICY.md` is the authoritative policy source.

Enforce these gateway requirements in all implementations:

- Classify all data sources with human confirmation before implementation.
- Treat dataset publication and sensitive-data handling as policy-controlled decisions, not agent defaults.
- Never store credentials in repository files.
- Never auto-delete project data without explicit human instructions.
- Ask for clarification when governance metadata is incomplete or ambiguous.

## Deliverable Contract for AI Agents

For each non-trivial request, return:
1. Files changed
2. Why each change was made
3. Verification run (commands + pass/fail)
4. Remaining assumptions or open decisions

---

## EIG Style & Communications Standards

All written outputs and figures must comply with EIG style. These standards apply alongside the
WF1–WF6 workflow contract and do not modify it. Apply all rules from the canonical style
documentation below to every written output and figure.

**Full style documentation:**

| Topic | File |
|-------|------|
| Writing & style rules | `INFRA/docs/eig-writing-style.md` |
| Citation format & library notes | `INFRA/docs/eig-citation-style.md` |
| Document review process & cover sheet | `INFRA/docs/eig-document-process.md` |
| Brand guidelines (logo, colors, typography) | `INFRA/docs/eig-brand-guidelines.md` |
| Figure & table standards | `INFRA/docs/eig-figure-style.md` |

**Style agents** — when a task matches a role below, read the file and follow all instructions:

| Role | File | Invoke When Asked To |
|------|------|---------------------|
| EIG Writer | `INFRA/.claude/agents/eig-writer.md` | Draft any publication, blog post, brief, or report |
| EIG Reviewer | `INFRA/.claude/agents/eig-reviewer.md` | Audit any document against EIG style rules |
| EIG Data Viz | `INFRA/.claude/agents/eig-data-viz.md` | Generate chart or figure code in any EIG-supported tool |

**Commands** — when any of these are invoked, read the file and follow all instructions:

| Command | File | What It Does |
|---------|------|--------------|
| `/review-style` | `INFRA/.claude/commands/review-style.md` | Audit text; return ERROR/SUGGESTION report by category |
| `/cite` | `INFRA/.claude/commands/cite.md` | Format a citation in EIG style from natural-language input |
| `/cover-sheet` | `INFRA/.claude/commands/cover-sheet.md` | Generate filled EIG cover sheet; flag missing fields |
| `/smart-brevity` | `INFRA/.claude/commands/smart-brevity.md` | Rewrite using Smart Brevity six-step framework |

**Brand assets:** Fonts in `INFRA/assets/fonts/` (Tiempos Text + Galaxie Polaris; see `INFRA/assets/fonts/INSTALL.md`). Logos in `INFRA/assets/logo/` (EIG + Agglomerations; see `INFRA/assets/logo/README.md`).
