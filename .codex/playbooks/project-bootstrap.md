# EIG Project Bootstrap Playbook (Codex / ChatGPT)

Use this playbook when applying the EIG baseline shell to a new project.
Paste this playbook into your Codex or ChatGPT session along with the filled
`INFRA/docs/PROJECT_INTAKE.md` and the contents of `INFRA/AGENTS.md`.

## Steps

1. **WF1** (`PARITY:WF1:INTAKE_READ`): Read `INFRA/docs/START_HERE.md`,
   `INFRA/docs/TEMPLATE_SCOPE.md`, `INFRA/docs/AGENT_TASK_ROUTING.md`, and
   `INFRA/docs/PROJECT_INTAKE.md`; verify all required intake fields are present.

2. **WF2** (`PARITY:WF2:MISSING_REQUIRED_ASK_AND_PAUSE`,
   `PARITY:WF2:MAX5_CONTEXTUAL_FOLLOWUPS`): If any `BLOCKER` field is missing,
   ask at most 5 targeted follow-up questions using completed `BLOCKER` answers
   and prior `SOFT_REQUIRED` context to prioritize the highest-value
   clarifications. Pause implementation until all blocker fields are confirmed.
   Apply startup token thresholds from `INFRA/docs/AGENT_TASK_ROUTING.md`:
   soft `12,000` and hard `18,000` input tokens. At/above hard threshold,
   pause broad loading and ask for scoped file/section targets.

3. **WF3** (`PARITY:WF3:DECISIONS_LOGGED`): Write `INFRA/docs/PROJECT_DECISIONS.md`
   from confirmed intake answers, recording decisions, assumptions, and open
   questions.

4. **WF4** (`PARITY:WF4:STRUCTURE_CUSTOMIZED`): Rename or extend staged scripts
   to match the actual research design. Scaffold only the stages required by the
   active project scope tier from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`: Tier 1 ->
   stages 01, 02, 05; Tier 2 -> stages 01, 02, 03, 05; Tier 3 -> all stages.
   Document data acquisition in `WORKSPACE/data/raw/README.md`. Populate
   `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md` per `INFRA/docs/DATA_GOVERNANCE_POLICY.md`
   (use short-form catalog for Tier 1). In run-all orchestrators, include an
   explicit, readability-first flag section that lists every drafted component
   one line at a time with `TRUE`/`FALSE` settings in stage order.

5. **WF5** (`PARITY:WF5:PLACEHOLDERS_UPDATED`,
   `PARITY:WF5:LANGUAGE_PROFILE_UPDATED`): Update placeholders in `INFRA/README.md`,
   `INFRA/CLAUDE.md`, and `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`. Set the `Project
   bootstrap config path` to the language-appropriate file:
   `WORKSPACE/code/00_setup/00_config.R` for R, `WORKSPACE/code/00_setup/00_config.py` for Python,
   or `WORKSPACE/code/00_setup/00_config.do` for Stata.

6. **WF6** (`PARITY:WF6:SESSION_LOGGED`): Create a session log in
   `INFRA/quality_reports/session_logs/` using the template in
   `INFRA/templates/session-log.md`, and update `INFRA/quality_reports/project_tracker.md`
   status rows as work progresses.

## Validation

After completing the steps above, run:

- `INFRA/scripts/validate_structure.sh`
- `INFRA/scripts/validate_agent_parity.sh`
- `INFRA/scripts/validate_stage_contracts.sh` (template default: warn mode)
- The language-specific pipeline command from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`
  (when the environment is configured)

After required stage artifacts exist in the project repository, switch to strict
stage contract enforcement: `STAGE_CONTRACT_MODE=fail`.

## Deliverable Contract

For each non-trivial session, return:

1. Files changed
2. Reason for each change
3. Verification results
4. Open questions/assumptions
