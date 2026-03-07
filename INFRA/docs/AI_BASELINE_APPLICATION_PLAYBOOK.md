# AI Baseline Application Playbook

Use this when asking an AI agent to apply this baseline to a new project.

Two-zone structure:
- `WORKSPACE/` is the human-facing workbench (data, outputs, explorations).
- `INFRA/` contains baseline infrastructure (code, docs, scripts, templates, agent config).

## Agent Task Prompt (Copy/Paste)

For a minimal-read startup, use `INFRA/docs/AI_START.md` first. This playbook is the phase-2
execution guide after BLOCKER intake fields are complete.

**Note:** The canonical end-to-end workflow (WF1–WF6 with full step details) lives in
`INFRA/docs/PROCESS_FLOW.md`. The prompt below is a paste-ready operationalisation of that
flow — it is intentionally self-contained so it can be dropped into a Codex or ChatGPT session
without requiring the agent to first navigate the repository. If the two diverge, PROCESS_FLOW.md
is authoritative.

```text
Apply the baseline shell in this repository to my project.

First, read:
- INFRA/AGENTS.md
- INFRA/AI_AGENT_ROUTING.md
- INFRA/docs/AI_START.md
- INFRA/docs/PROJECT_INTAKE.md
- INFRA/docs/DATA_GOVERNANCE_POLICY.md
- INFRA/docs/STAGE_OUTPUT_CONTRACTS.md
- INFRA/docs/REVIEW_RUBRIC.md

Then:
1) Validate intake completeness.
2) Ask only missing required questions.
3) Create INFRA/docs/PROJECT_DECISIONS.md from intake answers.
4) Use scoped retrieval and token-budget rules from `INFRA/docs/AGENT_TASK_ROUTING.md` (startup soft threshold: `12,000`, hard threshold: `18,000` input tokens).
5) Rename and customize staged WORKSPACE/code/ folder READMEs to match my research question and data sources.
6) Update INFRA/README.md, INFRA/CLAUDE.md, and INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md placeholders.
7) Ensure output and data boundaries in .gitignore remain valid.
8) Populate INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md and follow INFRA/docs/DATA_GOVERNANCE_POLICY.md defaults.
9) Keep `INFRA/quality_reports/project_tracker.md` updated as components move from `not_started` to `done`.
10) Log work in INFRA/quality_reports/session_logs/YYYY-MM-DD_<short-title>.md.
11) Run a lightweight verification pass (`validate_structure.sh`, `validate_agent_parity.sh`, and `validate_stage_contracts.sh`) and report what still needs human input.
12) Once required stage artifacts exist in the generated project repo, switch CI stage contract checks to strict mode (`STAGE_CONTRACT_MODE=fail`).
13) Set the active language profile defaults in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` (primary language, entrypoint path, execution command, bootstrap/config path).
```

## Expected Customization Outcomes

- Script names reflect project-specific workflows.
- `WORKSPACE/data/raw/README.md` includes acquisition instructions for all sources.
- `INFRA/docs/PROJECT_DECISIONS.md` documents assumptions and unresolved choices.
- Pipeline entrypoint and execution command in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` align to the current project stage and language.
- `INFRA/quality_reports/project_tracker.md` captures real-time build status across code, data, checks, and reporting.




