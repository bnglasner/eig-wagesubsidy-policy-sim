# Platform Parity Checklist (Claude + Codex)

Use this checklist after meaningful changes to `INFRA/AGENTS.md`, `INFRA/.claude/`, or `INFRA/.codex/`.

## Objective Parity (script-backed)

- [ ] `./INFRA/scripts/validate_agent_parity.sh` passes.
- [ ] Both platform bootstrap files reference `WF1` to `WF6`.
- [ ] Routing still points each platform to the correct folder.

## Subjective Parity (human review)

- [ ] Instructions are equally clear for Claude and Codex users.
- [ ] Platform-specific optimizations do not change required outcomes.
- [ ] Both platforms enforce missing-intake follow-up questions before implementation.
- [ ] Deliverable expectations match across platforms (files changed, rationale, verification, assumptions/open questions).
- [ ] New contributors can follow either platform path without reading internal tool/runtime details.

## Review Note

If parity is intentionally broken for a project-specific reason, document the exception in `INFRA/docs/PROJECT_DECISIONS.md`.

## EIG Style Toolkit Parity (human review)

- [ ] `INFRA/.claude/agents/eig-writer.md` and `INFRA/.codex/agents/eig-writer.md` are identical.
- [ ] `INFRA/.claude/agents/eig-reviewer.md` and `INFRA/.codex/agents/eig-reviewer.md` are identical.
- [ ] `INFRA/.claude/agents/eig-data-viz.md` and `INFRA/.codex/agents/eig-data-viz.md` are identical.
- [ ] `INFRA/.claude/commands/` and `INFRA/.codex/commands/` contain identical files (all 4).
- [ ] Both versions of `eig-style-guide-agent.md` are identical.
- [ ] Both `INFRA/CLAUDE.md` and `INFRA/AGENTS.md` reference the canonical EIG style documentation (`INFRA/docs/eig-writing-style.md` and related docs) rather than embedding rules inline.

## Root Skill Format Divergence (intentional — review only)

Root `.claude/skills/*/SKILL.md` files include YAML frontmatter (`name`, `description`,
`allowed-tools`, etc.) because Claude Code parses this metadata for skill invocation.
Root `.codex/skills/*/SKILL.md` files do not include this frontmatter because Codex/ChatGPT
does not use it.

**This divergence is intentional.** The parity validator checks file existence only, not
frontmatter presence. Human review should confirm:

- [ ] The non-frontmatter body of each paired skill (`.claude/` vs `.codex/`) remains
  logically equivalent — same workflow steps, same non-negotiables, same file references.
- [ ] Any wording differences between paired skills are intentional platform adaptations,
  not accidental drift.



