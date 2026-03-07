---
name: eig-project-bootstrap
description: Apply this baseline shell to a specific EIG project using the required intake questionnaire.
argument-hint: "[project-name]"
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob"]
disable-model-invocation: true
---

# EIG Project Bootstrap

## Steps

1. **WF1** (`PARITY:WF1:INTAKE_READ`): Read `INFRA/docs/START_HERE.md`, `INFRA/docs/TEMPLATE_SCOPE.md`, `INFRA/docs/AGENT_TASK_ROUTING.md`, and `INFRA/docs/PROJECT_INTAKE.md`; verify all required intake fields.
2. **WF2** (`PARITY:WF2:MISSING_REQUIRED_ASK_AND_PAUSE`, `PARITY:WF2:MAX5_CONTEXTUAL_FOLLOWUPS`): Ask at most 5 targeted follow-up questions only for missing `BLOCKER` fields, using completed `BLOCKER` answers and prior `SOFT_REQUIRED` context to prioritize high-value clarifications, then pause implementation until blocker fields are confirmed. Apply startup token thresholds from `INFRA/docs/AGENT_TASK_ROUTING.md`: soft `12,000` and hard `18,000` input tokens. At/above the hard threshold, stop broad loading and ask for scoped file/section targets.
3. **WF3** (`PARITY:WF3:DECISIONS_LOGGED`): Write `INFRA/docs/PROJECT_DECISIONS.md` from confirmed answers.
4. **WF4** (`PARITY:WF4:STRUCTURE_CUSTOMIZED`): Rename or extend staged scripts to match the actual design. Scaffold only the stages required by the active project scope tier from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`: Tier 1 → stages 01, 02, 05; Tier 2 → stages 01, 02, 03, 05; Tier 3 → all stages. Document data acquisition in `WORKSPACE/data/raw/README.md`. Populate `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md` per `INFRA/docs/DATA_GOVERNANCE_POLICY.md` (use short-form catalog for Tier 1).
   In run-all orchestrators, include an explicit, readability-first flag section that lists every drafted component one line at a time with `TRUE`/`FALSE` settings in stage order.
5. **WF5** (`PARITY:WF5:PLACEHOLDERS_UPDATED`, `PARITY:WF5:LANGUAGE_PROFILE_UPDATED`): Customize placeholders in `INFRA/README.md`, `INFRA/CLAUDE.md`, and `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`. Set the `Project bootstrap config path` to the language-appropriate file: `WORKSPACE/code/00_setup/00_config.R` for R, `WORKSPACE/code/00_setup/00_config.py` for Python, or `WORKSPACE/code/00_setup/00_config.do` for Stata.
6. **WF6** (`PARITY:WF6:SESSION_LOGGED`): Create session log in `INFRA/quality_reports/session_logs/` and update `INFRA/quality_reports/project_tracker.md`.

## Validation

Run:
- `INFRA/scripts/validate_structure.sh`
- `INFRA/scripts/validate_agent_parity.sh`
- `INFRA/scripts/validate_stage_contracts.sh` (template default: warn mode)
- Language-specific pipeline command from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` (when environment is configured)

After required artifacts exist in the generated project repository, switch stage contract checks to strict mode with `STAGE_CONTRACT_MODE=fail` in CI.

## Deliverable Contract

- Files changed
- Reason for each change
- Verification results
- Open questions/assumptions


