# Agent Task Routing And Token Budget Rules

Use this document to keep startup work scoped, reliable, and efficient.

## Startup Token Thresholds

1. Soft threshold: `12,000` input tokens
2. Hard threshold: `18,000` input tokens

### Required Behavior

1. Below soft threshold: proceed normally.
2. Between soft and hard thresholds: switch to scoped retrieval only (task-relevant files/sections).
3. At or above hard threshold: pause broad loading and ask the user to narrow scope.

## Scoped Retrieval Protocol

1. Identify the active task category before reading files.
2. Load only the mapped files for that task (table below).
3. Summarize and proceed; do not index the full repository by default.
4. If required context is still missing, ask one targeted clarification question.

## Pilot Task Routing Map

| Task | Primary Files To Load First | Optional Files |
|------|-----------------------------|----------------|
| New project initialization and intake confirmation | `docs/START_HERE.md`, `docs/PROJECT_INTAKE.md`, `AGENTS.md`, `AI_AGENT_ROUTING.md` | `.codex/playbooks/project-bootstrap.md`, `.claude/skills/eig-project-bootstrap/SKILL.md` |
| Data source onboarding and governance classification | `docs/DATA_GOVERNANCE_POLICY.md`, `docs/DATA_SOURCES_OUTPUTS_CATALOG.md`, `data/raw/README.md` | `docs/PROJECT_DECISIONS.md` |
| Pipeline stage status check | `quality_reports/project_tracker.md`, `docs/STAGE_OUTPUT_CONTRACTS.md`, `docs/PIPELINE_LANGUAGE_PROFILE.md` | `code/run_all.R` (or language-equivalent run-all file) |
| Summary doc generation | `quality_reports/project_tracker.md`, `docs/PROJECT_DECISIONS.md`, relevant stage README/scripts for the requested summary | `docs/REVIEW_RUBRIC.md` |
| Reproducibility/readiness check before external sharing | `docs/STAGE_OUTPUT_CONTRACTS.md`, `docs/DATA_GOVERNANCE_POLICY.md`, `.gitignore`, `docs/PIPELINE_LANGUAGE_PROFILE.md` | `scripts/validate_structure.sh`, `scripts/validate_stage_contracts.sh` |

## Clarification Prompt Patterns

Use concise prompts like:

1. "Which file or section should I prioritize for this task: intake, data governance, or stage outputs?"
2. "Should I restrict review to `docs/` only for this pass, or include stage scripts now?"
3. "I am near the startup context budget. Which component should I skip for now?"

