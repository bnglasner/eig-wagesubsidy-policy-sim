# Architecture Overview

This document describes the internal structure of the EIG baseline template and how its major
pieces relate. For the canonical Document Map (purpose → file index), see the root `README.md`.

---

## Two-Zone Model

The repository is divided into two zones with distinct roles:

```
repo root/
├── WORKSPACE/   ← human-facing workbench: code, data, outputs, explorations
└── INFRA/       ← baseline infrastructure: docs, scripts, templates, agent config
```

**Why two zones?**
- `INFRA/` should be touched rarely — its contents define the system, not the project.
- `WORKSPACE/` is where all project-specific work happens; it evolves every session.
- This separation means a researcher can be fully productive in `WORKSPACE/` without
  needing to understand or modify `INFRA/`. It also means the baseline can be updated
  in one place and propagated to all project copies.

**Boundary rule:** Project-specific code, data, and outputs always go in `WORKSPACE/`.
Template rules, validators, AI configuration, and style assets always stay in `INFRA/`.

---

## Template vs. Derivative Project

This repository is a **template**. It is not used directly for research. The intended
lifecycle is:

1. Copy (fork/clone/template) this repo to create a new project repository.
2. Confirm you are working in the copy, not the template itself.
3. Run the bootstrap workflow (WF1-WF6 in `INFRA/AGENTS.md`) to configure the copy.
4. All project-specific work happens in the derived repo; this template stays pristine.

This means changes to INFRA/ in this template repository are improvements to the
baseline, not project implementations. They propagate to new projects but do not
retroactively change existing derived repos.

---

## Pipeline Stage Dependency Graph

Stages run in sequence. Each stage's outputs are inputs to subsequent stages:

```
00_setup (config/paths)
     │
     ▼
01_data_preparation ──► data/processed/analysis_dataset.*
                         output/data/intermediate_results/data_dictionary.*
                         quality_reports/data_report.html
     │
     ▼
02_descriptive_analysis ──► output/tables/main/descriptive_summary.*
                              output/data/intermediate_results/descriptive_qc.*
     │
     ▼  (Tier 2+ only)
03_main_estimation ──► output/tables/main/main_estimates.*
                        output/data/intermediate_results/model_diagnostics.*
     │
     ▼  (Tier 3 only)
04_robustness_heterogeneity ──► output/tables/appendix/robustness_results.*
                                  output/tables/appendix/heterogeneity_results.*
     │
     ▼
05_figures_tables ──► output/figures/main/*
                       output/figures/appendix/*
                       output/tables/main/*
                       output/tables/appendix/*
                       quality_reports/output_report.html
```

Stages 03 and 04 are gated by project scope tier (set in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`):
- Tier 1 (Descriptive/Blog): stages 01, 02, 05
- Tier 2 (Analytical Brief): stages 01, 02, 03, 05
- Tier 3 (Full Research Paper): all stages

---

## INFRA/ Subsystem Map

```
INFRA/
├── CLAUDE.md                  ← Claude Code entry point + core rules
├── AGENTS.md                  ← Cross-platform contract (WF1-WF6)
├── AI_AGENT_ROUTING.md        ← Platform routing + style toolkit routing
├── MEMORY.md                  ← Project-level AI learning log (not user-level memory)
├── README.md                  ← INFRA zone explanation
│
├── docs/                      ← Process and governance documentation
│   ├── START_HERE.md          ← Human onboarding, first 5 minutes
│   ├── AI_START.md            ← AI agent minimal startup sequence
│   ├── PROCESS_FLOW.md        ← Canonical WF1-WF6 end-to-end flow
│   ├── PROJECT_INTAKE.md      ← Intake questionnaire (BLOCKER/SOFT_REQUIRED/OPTIONAL)
│   ├── PROJECT_DECISIONS.md   ← Logged decisions for this project
│   ├── PIPELINE_LANGUAGE_PROFILE.md ← Active language, tier, entrypoints
│   ├── STAGE_OUTPUT_CONTRACTS.md    ← Required artifacts per stage
│   ├── DATA_GOVERNANCE_POLICY.md    ← Data classification and handling rules
│   ├── DATA_SOURCES_OUTPUTS_CATALOG.md ← Per-source provenance catalog
│   ├── AGENT_TASK_ROUTING.md  ← Token budget rules and task-to-file routing map
│   ├── TEMPLATE_SCOPE.md      ← What this template can and cannot do
│   ├── ARCHITECTURE.md        ← This file
│   ├── REVIEW_RUBRIC.md       ← Quality gates (80/90/95)
│   ├── PLATFORM_PARITY_CHECKLIST.md ← Cross-platform consistency checklist
│   ├── AI_BASELINE_APPLICATION_PLAYBOOK.md ← Paste-ready bootstrap prompt
│   └── eig-*.md               ← EIG brand/writing/figure/citation/document style docs
│
├── .claude/                   ← Claude Code configuration
│   ├── agents/                ← Reference agent docs (not invokable skills)
│   ├── commands/              ← /review-style, /cite, /cover-sheet, /smart-brevity
│   └── rules/                 ← code-conventions, plan-first-workflow
│
├── .codex/                    ← Codex/ChatGPT configuration (mirrors .claude/)
│   ├── agents/
│   ├── commands/
│   ├── rules/
│   └── playbooks/             ← project-bootstrap.md (Codex equivalent of root skill)
│
├── scripts/                   ← Bash validators
│   ├── smoke_test.sh          ← Full pipeline test in temp dir
│   ├── validate_structure.sh  ← Required paths + stage dirs
│   ├── validate_agent_parity.sh ← WF parity tokens across platforms
│   └── validate_stage_contracts.sh ← Stage artifact presence
│
├── style/                     ← Vendored EIG style system
│   ├── tokens/                ← Canonical design tokens (JSON)
│   ├── themes/r|python|stata/ ← Language-specific theme helpers
│   ├── docs/                  ← Style implementation guides, Datawrapper docs
│   ├── scripts/               ← Font checks, Datawrapper compliance validators
│   └── sources/               ← Source design PDFs (provenance only)
│
├── assets/                    ← Brand assets
│   ├── fonts/                 ← Tiempos + Galaxie Polaris OTF files
│   └── logo/                  ← EIG + Agglomerations logos (SVG, PNG, EPS, AI)
│
├── templates/                 ← Fill-in document templates
│   ├── session-log.md
│   ├── quality-report.md
│   ├── requirements-spec.md
│   ├── data_report.html       ← Template for INFRA/quality_reports/data_report.html
│   └── output_report.html     ← Template for INFRA/quality_reports/output_report.html
│
└── quality_reports/           ← Build-time outputs (session logs, plans, trackers)
    ├── project_tracker.md
    ├── session_logs/
    ├── plans/
    ├── merges/
    └── specs/
```

---

## Validator Architecture

Three validators + one smoke test provide layered assurance:

| Script | What it checks | Mode |
|--------|---------------|------|
| `validate_structure.sh` | Required files exist; stage dirs have READMEs and scripts | `warn`/`fail` for placeholder-only stages |
| `validate_agent_parity.sh` | WF1-WF6 parity tokens in all bootstrap files; deliverable contract present | `fail` on missing |
| `validate_stage_contracts.sh` | Required output artifacts exist and are non-empty | `warn` (default) or `fail` |
| `smoke_test.sh` | Full R pipeline in isolated temp dir; all three validators in strict mode | `fail` on any issue |

The smoke test is the only check that runs actual R code. The three validators are
structure-only and run without any runtime dependencies.

---

## AI Configuration Architecture

Platform-specific AI configurations live in `INFRA/.claude/` and `INFRA/.codex/`, but both
platforms share the same cross-platform contract in `INFRA/AGENTS.md`. The parity validator
enforces that both platforms implement WF1-WF6 with identical parity tokens and deliverable
contract fields.

Invokable Claude Code skills live at the **repository root** in `.claude/skills/`, not in
`INFRA/.claude/`. This is because Claude Code resolves skills from the project root, not from
subdirectories. `INFRA/.claude/agents/` contains reference documentation that agents read for
guidance; it is not the source of invokable commands.
