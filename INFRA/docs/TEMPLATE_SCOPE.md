# Template Scope: Can And Cannot Do

## What This Template Is Designed To Do

1. Provide a standardized project skeleton for EIG research workflows.
2. Support staged pipelines from data loading through outputs (`00` to `05`).
3. Work across mixed team roles and technical backgrounds.
4. Improve consistency, clarity, and reproducibility across projects.
5. Support AI-assisted implementation under explicit governance and review rules.

## What This Template Is Not Designed To Do

1. Replace human interpretation of results or policy judgment.
2. Act as an autonomous primary source of truth.
3. Invent missing facts, metadata, or evidence.
4. Force all projects within a tier to follow identical logic.
5. Perform cloud storage operations (including Google Drive and Dropbox access).

## Human-Only Decisions

1. Data classification tier confirmation.
2. Publication approval decisions for outputs.
3. Final interpretation of model outputs and narrative claims.
4. Approval of major structural replacements or removals.

## AI Role Boundaries

1. AI agents facilitate implementation, quality checks, and documentation.
2. AI agents must ask for clarification when scope, governance, or source metadata is ambiguous.
3. AI agents should load only relevant sections for the active task (see `docs/AGENT_TASK_ROUTING.md`).

