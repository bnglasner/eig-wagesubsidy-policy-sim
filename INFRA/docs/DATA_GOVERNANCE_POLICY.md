# Data Governance Policy (Baseline Default)

## Classification Tiers

Every source must be classified by a human before implementation:

- `PUBLIC`
- `LICENSED`
- `RESTRICTED`
- `HIGHLY_SENSITIVE`

If classification is unclear, the agent must ask for clarification.

## Commit + Publication Policy

- Default assumption: no data is published to GitHub directly.
- Applies to raw, processed, and derived datasets across all tiers.
- For `PUBLIC` data only, the agent may ask whether specific processed outputs are approved for publication.
- For `LICENSED`, `RESTRICTED`, and `HIGHLY_SENSITIVE` tiers, publication decisions are human-only manual decisions and should not be prompted as an agent approval question.

## Derived Output Policy

- Derived outputs follow the same publication policy as source data.
- If an output contains potentially identifying detail, default to non-public handling until the human explicitly defines an approved redaction/aggregation rule.

## Access + Credential Policy

- Credentials must live only in `.Renviron`, secret manager tooling, or other local environment management.
- Credentials must never be committed to repository files.
- Final code review and project review must include an explicit credential-exposure check.

## Acquisition Trace Requirements

Maintain source metadata and output metadata in:

- `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md`

If any required field is unknown, ask the human and record the answer.

## Retention + Cleanup Policy

- Agents must not automatically delete data.
- Retention and cleanup rules must be explicitly provided by the human project owner.
- Agents should ask what needs local persistence versus temporary storage.

## Sharing + Export Constraints

- No raw sensitive exports to email/chat.
- External sharing should use approved redacted/aggregated outputs only.
- External collaborator access rules must be documented.

## Logging + Audit

For non-public sources or sensitive workflows, log purpose, date, script/output context, and exceptions in session logs and `INFRA/docs/PROJECT_DECISIONS.md`.

## Cloud Storage Prohibition (AI Agents)

- AI agents must not access, sync, authenticate, or otherwise interact with Google Drive or Dropbox (including APIs, desktop sync folders, scripts, or web links).
- If a user requests any Google Drive or Dropbox interaction, the agent may only provide step-by-step instructions for a human to perform manually, and must not execute or automate those steps.

## Violation / Fallback Behavior

If a request conflicts with this policy:

1. Pause implementation.
2. State the conflict clearly.
3. Propose compliant alternatives.
4. Request explicit human direction for exceptions.



