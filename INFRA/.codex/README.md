# Codex Configuration Layer

This folder provides Codex-specific guidance parallel to `.claude/`.

## How Codex Uses This

1. `AGENTS.md` in repository root is the primary instruction contract.
2. `AI_AGENT_ROUTING.md` defines platform routing between `.claude/` and `.codex/`.
3. Files in this folder provide Codex-operational details and reusable playbooks.

## Structure

- `agents/`: reviewer and specialist prompts for Codex-style subtasking,
  including a dedicated code-commenting agent for step-by-step annotation
- `commands/`: slash-command equivalents (`/review-style`, `/cite`, `/cover-sheet`,
  `/smart-brevity`)
- `rules/`: concise execution rules for reproducible analysis workflows
- `playbooks/`: end-to-end procedures (bootstrap/customization/verification)

> **Note:** Invokable Codex skills live at the repository root in `.codex/skills/`,
> not here. This folder contains reference documentation only.

## Scope

This layer is plain Markdown and intentionally tool-agnostic. It does not depend on Claude slash-command runtime behavior.
