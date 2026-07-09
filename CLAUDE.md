# Repository Instructions

> New to this repo? Read `README.md` (Getting Started) for the research workflow, the command set, and where everything lives.

## Startup Order

0. If the user is new or asks how to use this template, point them to `README.md` (Getting Started).
1. Read `PROJECT.md` first. If the title is missing, stop and ask for it before doing deeper work.
2. Read `Infrastructure/GUARDRAILS.md`.
3. Read `Infrastructure/AI_WORKFLOW.md`.
4. Review the relevant files in `Infrastructure/rules/`.
5. For style-sensitive figures, tables, or prose, use `Infrastructure/style/docs/README.md`.

## Repository Layout

This repo is both an active project workspace and a reusable template. Project work and outputs live in the workspace lane; shared logic lives in `Infrastructure/`. For the full structural census — what every part is and how the parts relate — read `Infrastructure/TEMPLATE_CENSUS.md`.

Project lane (where work and outputs go):

- `PROJECT.md` — project context; the title is required before substantive work.
- `code/` — analysis scripts; the starter pipeline is `code/run_all.R`.
- `data/raw`, `data/processed` — inputs as received, and cleaned checkpoints.
- `drafts/` — prose in progress.
- `output/figures`, `output/tables` — finished figures and tables.

Shared brain (`Infrastructure/`, the source of truth):

- `Infrastructure/GUARDRAILS.md`, `Infrastructure/AI_WORKFLOW.md` — behavior rules and the five-step session process (read at startup); `Infrastructure/README.md` indexes the tree.
- `Infrastructure/rules/` — binding governance and review/style rules; each review agent reads its matching rules file.
- `Infrastructure/agents/` — specialist agents: the code, methodology, number (data-consistency), conceptual-consistency, and AI-skeptic reviewers, plus data-dictionary, literature-scout, eig-writer, eig-style-guide, eig-reviewer, maintenance, and orchestrator.
- `Infrastructure/commands/` — workflow playbooks: the review commands, full-review, document-data, literature-intake, orchestrate, cite, cover-sheet, smart-brevity, maintenance-check.
- `Infrastructure/templates/` — output shells (review reports, session log, requirements spec, orchestration plan, style outputs).
- `Infrastructure/skills/`, `Infrastructure/style/skills/` — invokable skills.
- `Infrastructure/references/literature/` — papers, summaries, and codebooks, indexed by `Infrastructure/references/literature/catalog.yaml`.
- `Infrastructure/references/datasets/registry.yaml` — recognized-dataset weights, pitfalls, and variable documentation; read by the review agents.
- `Infrastructure/style/` — EIG visual and editorial standard: index `Infrastructure/style/docs/README.md`, design tokens `Infrastructure/style/tokens/eig-style-tokens.v1.json`, themes under `Infrastructure/style/themes/`.
- `Infrastructure/plans/`, `Infrastructure/specs/`, `Infrastructure/session_logs/`, `Infrastructure/explorations/` — recoverable project records.
- `Infrastructure/root_instructions/`, `Infrastructure/adapter_configs/`, `Infrastructure/scripts/` — canonical adapter sources, per-adapter configs, and the sync/validation scripts.

Generation model: the root `CLAUDE.md` and `AGENTS.md` and the `.claude/`, `.codex/`, and `.agents/` trees are generated from `Infrastructure/` by `make brain-sync`. Do not hand-edit generated copies; change the canonical file under `Infrastructure/`, then re-sync. The control panel is the `Makefile` (`make brain-sync`, `make brain-check`, `make parity-check`, `make maintenance-check`, `make template-reset`).

## Canonical Sources

- Treat `Infrastructure/` as the source of truth for shared workflow, guardrails, review logic, and style logic.
- Update canonical files in `Infrastructure/` first, then run `make brain-sync`.
- Run `make brain-check` after changing canonical AI files.

## Claude Runtime Notes

- Project-level Claude memory loads from this `CLAUDE.md`.
- Claude slash-command workflows live in `.claude/commands/`.
- Claude project subagents live in `.claude/agents/`.
- Claude project skills live in `.claude/skills/`.
- Claude project settings live in `.claude/settings.json`.
