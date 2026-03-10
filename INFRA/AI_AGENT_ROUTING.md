# AI Agent Routing

Use this file to route different AI systems to their configuration layers.

## If the active agent is Claude Code

1. Read root `INFRA/AGENTS.md` first.
2. Then prioritize `INFRA/.claude/` for agent/rule/skill behavior.
3. Use `.claude/skills/eig-project-bootstrap/SKILL.md` for bootstrap automation (invokable as a Claude Code skill command).
4. For writing, reviewing, or figure work: use `INFRA/.claude/agents/eig-writer.md`,
   `eig-reviewer.md`, or `eig-data-viz.md`.
5. For /review-style, /cite, /cover-sheet, /smart-brevity: see `INFRA/.claude/commands/`.

## If the active agent is Codex / ChatGPT

1. Read root `INFRA/AGENTS.md` first.
2. Then prioritize `INFRA/.codex/` for rules, playbooks, and reviewer instructions.
3. For minimal startup, use `INFRA/docs/AI_START.md`. For full bootstrap execution, use `INFRA/.codex/playbooks/project-bootstrap.md`.
4. For writing, reviewing, or figure work: use `INFRA/.codex/agents/eig-writer.md`,
   `eig-reviewer.md`, or `eig-data-viz.md`.
5. For review-style, cite, cover-sheet, smart-brevity workflows: see `INFRA/.codex/commands/`.

## Style Toolkit Routing

Four style entry points exist. Use the right one for the task:

| Task | Entry Point |
|------|-------------|
| **Generate** figure/chart code in R, Python, or Stata | `INFRA/.claude/agents/eig-data-viz.md` (or `.codex` equivalent) |
| **Design or policy review** — which colors, layout rules, token usage | `INFRA/.claude/agents/eig-style-guide-agent.md` (or `.codex` equivalent) |
| **Apply** EIG theme tokens to existing project code (invokable) | `.claude/skills/eig-style-apply/SKILL.md` |
| **Audit** existing outputs/code for style compliance (invokable) | `.claude/skills/eig-style-review/SKILL.md` |
| **Datawrapper** manifest validation and CI compliance (invokable) | `.claude/skills/eig-style-datawrapper/SKILL.md` |

All five ultimately derive from the same canonical sources: `INFRA/docs/eig-brand-guidelines.md`
(color/typography rules) and `INFRA/style/tokens/eig-style-tokens.v1.json` (token values).

## Skill Invocability Note

Skills that are operationally invokable as Claude Code slash commands must live in root `.claude/skills/`:
- `.claude/skills/eig-project-bootstrap/` — project bootstrap automation
- `.claude/skills/eig-style-apply/` — apply EIG style tokens/themes
- `.claude/skills/eig-style-review/` — review figure/table styling
- `.claude/skills/eig-style-datawrapper/` — Datawrapper chart styling

Skills in `INFRA/.claude/` are reference/playbook documentation, not invokable slash commands.
`INFRA/style/SKILL.md` is a style-subsystem orchestration reference, also not invokable.

## Shared Requirement

Regardless of platform, the authoritative intake and project documents are:
- `INFRA/docs/AI_START.md` (minimal-read startup sequence)
- `INFRA/docs/PROJECT_INTAKE.md`
- `INFRA/docs/PROJECT_DECISIONS.md`
- `INFRA/docs/AI_BASELINE_APPLICATION_PLAYBOOK.md`
- `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`
- `INFRA/docs/DATA_GOVERNANCE_POLICY.md`
- `INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md`
- `INFRA/docs/STAGE_OUTPUT_CONTRACTS.md`
- `INFRA/docs/REVIEW_RUBRIC.md`

For EIG style and brand standards:
- `INFRA/docs/eig-writing-style.md`
- `INFRA/docs/eig-citation-style.md`
- `INFRA/docs/eig-brand-guidelines.md`
- `INFRA/docs/eig-figure-style.md`
- `INFRA/docs/eig-document-process.md`

For parity checks across platform adapters, run:
- `INFRA/scripts/validate_agent_parity.sh`
- Review `INFRA/docs/PLATFORM_PARITY_CHECKLIST.md`
