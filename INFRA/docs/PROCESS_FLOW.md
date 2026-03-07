# Baseline Process Flow (Canonical)

This is the single source of truth for end-to-end baseline application flow.
Other startup/playbook documents should point here instead of duplicating steps.

## Scope

Use this flow when turning the baseline template into a new project repository.

## Pre-Flight

1. Create a new project copy from this template.
2. Confirm you are not editing the template repository directly.
3. Read:
   - `INFRA/docs/TEMPLATE_SCOPE.md`
   - `INFRA/docs/AGENT_TASK_ROUTING.md`

## Mandatory Workflow (WF1-WF6)

1. **WF1** (`PARITY:WF1:INTAKE_READ`)
   - Read `INFRA/docs/PROJECT_INTAKE.md`.
   - Verify all `BLOCKER` fields are complete.

2. **WF2** (`PARITY:WF2:MISSING_REQUIRED_ASK_AND_PAUSE`, `PARITY:WF2:MAX5_CONTEXTUAL_FOLLOWUPS`)
   - If any `BLOCKER` is missing, ask at most 5 targeted follow-up questions.
   - Pause implementation until blockers are resolved.
   - Apply startup token thresholds from `INFRA/docs/AGENT_TASK_ROUTING.md`:
     - soft: `12,000` input tokens
     - hard: `18,000` input tokens

3. **WF3** (`PARITY:WF3:DECISIONS_LOGGED`)
   - Record confirmed decisions and assumptions in `INFRA/docs/PROJECT_DECISIONS.md`.

4. **WF4** (`PARITY:WF4:STRUCTURE_CUSTOMIZED`)
   - Customize stage structure/scripts by tier from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
   - Populate `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md`.
   - Document acquisition in `WORKSPACE/data/raw/README.md`.
   - For figure/table/chart work, use local style assets under `INFRA/style/themes/`.
   - Preserve `.gitignore` data/output boundaries.

5. **WF5** (`PARITY:WF5:PLACEHOLDERS_UPDATED`, `PARITY:WF5:LANGUAGE_PROFILE_UPDATED`)
   - Update placeholders in `WORKSPACE/README.md`, `INFRA/CLAUDE.md`, and `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
   - Set language-appropriate bootstrap config path.

6. **WF6** (`PARITY:WF6:SESSION_LOGGED`)
   - Update `INFRA/quality_reports/project_tracker.md`.
   - Log the session in `INFRA/quality_reports/session_logs/`.

## Verification

Run:

```bash
bash INFRA/scripts/validate_structure.sh
bash INFRA/scripts/validate_agent_parity.sh
bash INFRA/scripts/validate_stage_contracts.sh
```

Template default for stage contracts is warn mode.
Switch to strict mode after project artifacts exist:

```bash
STAGE_CONTRACT_MODE=fail bash INFRA/scripts/validate_stage_contracts.sh
```

## Document Map

The canonical Document Map (purpose → file) lives in the root `README.md`. See that file for the
complete index. Do not duplicate it here.
