# EIG Style System — Orchestration Reference

> **Not an invokable skill.** This file is an in-directory orchestration guide for the
> `INFRA/style/` subsystem. It is not in `.claude/skills/` and cannot be invoked as a
> Claude Code slash command.
>
> For invokable style skills, see:
> - `.claude/skills/eig-style-apply/SKILL.md` — apply theme tokens to project code
> - `.claude/skills/eig-style-review/SKILL.md` — audit outputs for EIG style compliance
> - `.claude/skills/eig-style-datawrapper/SKILL.md` — Datawrapper manifest validation
>
> For routing guidance, see `INFRA/AI_AGENT_ROUTING.md` → "Style Toolkit Routing".

Use this reference when an agent or developer needs a full picture of the `INFRA/style/`
subsystem — its scope, source priority, constraints, and Datawrapper workflow.

All paths below are relative to the `INFRA/style/` directory.

## Scope
- Publication-ready styling for figures/tables using EIG tokens and policy.
- Cross-tool consistency for R, Python, and Stata outputs.
- Datawrapper publishing governance (manifest + legacy metadata checks).

## Required Source Priority
1. Canonical docs index:
`docs/README.md`
2. Canonical tokens:
`tokens/eig-style-tokens.v1.json`
3. If Datawrapper is in scope:
`docs/datawrapper-integration.md`

Do not treat external project scripts as policy sources.

## Non-Negotiable Constraints
1. Do not change token values in:
`tokens/eig-style-tokens.v1.json`
2. Default to 2022 primary palette usage.
3. Only allow legacy semantic palettes under:
`docs/eig-legacy-palette-policy.md`
4. Do not introduce hardcoded net-new hex values when token equivalents exist.
5. Keep guidance auditable: emit explicit paths, fields, and commands.

## Standard Workflow
1. Load requirements from `docs/README.md` and task-specific doc(s).
2. Identify output surface:
- Static chart/table theme update.
- Datawrapper pipeline/publish update.
- Compliance/CI setup.
3. Implement with minimal duplication:
- Add links to canonical docs instead of repeating long policy text.
- Keep policy central; add bridges in implementation docs.
4. Validate:
- Check cross-links and required paths.
- Confirm policy consistency with legacy-palette metadata fields.
5. Report:
- Findings/gaps.
- Files changed and why.
- Open decisions requiring signoff.

## Datawrapper Mode (When Applicable)
Required behavior:
1. Use token-derived colors from canonical token source.
2. Require publish manifest schema fields:
- `run_timestamp_utc`, `figure_key`, `chart_id`, `chart_url`, `rows_uploaded`, `palette_mode`, `token_source_path`, `token_version`, `legacy_metadata_path`
3. If `palette_mode=legacy`, require metadata sidecar fields:
- `legacy_palette_used`, `legacy_set_id`, `legacy_palette_justification`, `approver`, `approval_date`
4. Validate using:
```bash
python3 "scripts/compliance/check_datawrapper_manifest.py" "<manifest_path>"
python3 "scripts/compliance/check_legacy_metadata.py" "<metadata_json_path>"
```
5. CI convention for downstream repos:
- Default workflow path: `.github/workflows/datawrapper-compliance.yml`
- Template source:
`docs/ci/datawrapper-compliance.workflow.template.yml`

## Key References
- `docs/agent-01-design-spec.md`
- `docs/agent-02-r-implementation.md`
- `themes/README.md`
- `docs/datawrapper-downstream-adoption-checklist.md`

## Output Expectations
For implementation requests, produce:
1. Concise findings (new/redundant/conflicting/missing).
2. File-by-file edits with rationale.
3. Verification status (links, policy consistency, commands run).
4. Remaining open questions (only if true blockers/signoff items remain).
