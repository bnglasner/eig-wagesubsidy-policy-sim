# INFRA/CLAUDE.md -- EIG Baseline

**Project:** eig-wagesubsidy-policy-sim
**Institution:** Economic Innovation Group (EIG)
**Primary Audience:** Public — interactive web simulation embedded in EIG content + blog post
**Scope Tier:** 1 (Descriptive / Interactive Tool)
**Primary Language:** Python (PolicyEngine-US + Streamlit)
**Policy:** EIG "80-80 Rule" wage subsidy (Glasner & Ozimek)

## Core Principles

- Plan-first for non-trivial work
- Spec-before-implementation for ambiguous requests
- Verification before completion
- Replication-first extension workflow
- No hardcoded absolute paths
- Reproducible outputs mapped to scripts

## Required Artifacts

- specs: `INFRA/quality_reports/specs/`
- plans: `INFRA/quality_reports/plans/`
- session logs: `INFRA/quality_reports/session_logs/`
- merge report: `INFRA/quality_reports/merges/`

## Quality Gates

- 80: commit-ready
- 90: review-ready
- 95: aspirational

## Standard Commands

```bash
# Use the language-specific pipeline command in INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md
```

## Startup References

Read `INFRA/docs/AI_START.md` — it lists everything to read and in what order.

## Non-Negotiables

1. All scripts use the bootstrap/config entry defined in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
2. Every output has a producing script.
3. Data acquisition steps are documented in `WORKSPACE/data/raw/README.md`.
4. Key assumptions and design choices are documented in `INFRA/docs/PROJECT_DECISIONS.md`.
5. Credentials must never appear in repository files; use `.Renviron` or local secret tooling.
6. Final code/project review must include a credential-exposure check.

---

## EIG Style Toolkit

Apply EIG communications and brand standards to all written outputs and figures. Full rules are in the canonical style documentation below.

**Style documentation:** `INFRA/docs/eig-writing-style.md` | `INFRA/docs/eig-citation-style.md` |
`INFRA/docs/eig-document-process.md` | `INFRA/docs/eig-brand-guidelines.md` | `INFRA/docs/eig-figure-style.md`

**Style system:** `INFRA/style/themes/r/` | `INFRA/style/themes/python/` | `INFRA/style/themes/stata/` | tokens: `INFRA/style/tokens/` | docs: `INFRA/style/docs/`

**Brand assets:** Fonts in `INFRA/assets/fonts/` (Tiempos Text + Galaxie Polaris; see `INFRA/assets/fonts/INSTALL.md`)
| Logos in `INFRA/assets/logo/` (see `INFRA/assets/logo/README.md`)

**Writing & style agents:** `INFRA/.claude/agents/eig-writer.md` | `INFRA/.claude/agents/eig-reviewer.md`
| `INFRA/.claude/agents/eig-data-viz.md`

**Commands:** `/review-style` | `/cite` | `/cover-sheet` | `/smart-brevity`
(full workflows in `INFRA/.claude/commands/`)

