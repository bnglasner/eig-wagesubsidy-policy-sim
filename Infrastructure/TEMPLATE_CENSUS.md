# Template Census

**Census date: 2026-06-16.**
**Scope:** A full point-in-time inventory of the EIG AI-Assisted Research Template — what every part is, where it lives, and how the parts relate. This is the detailed reference behind the short "Repository layout" orientation block in `CLAUDE.md` and `AGENTS.md`. When the structure changes materially, refresh this file and update the census date above.

> How to refresh: re-walk the tree (`Infrastructure/scripts/check_internal_path_references.py` validates that every path cited here still resolves), update the affected sections, bump the census date, and confirm `make maintenance-check` passes.

---

## 1. The two identities

This repository is simultaneously two things, and almost every design choice follows from that (`.claude/rules/meta-governance.md`):

1. **An active project workspace** — a real research project runs here. The project-facing lane is `PROJECT.md`, `code/`, `data/`, `drafts/`, and `output/`.
2. **A reusable template** — the same shell is copied into new projects. The reusable lane is everything under `Infrastructure/` plus the generated adapter trees (`.claude/`, `.codex/`, `.agents/`).

The dividing rule: generic, portable logic lives in `Infrastructure/`; project-specific execution and outputs live in the workspace lane. `make template-reset` scrubs the workspace lane back to baseline before distribution.

---

## 2. Top-level map

| Path | Role | Lane |
|---|---|---|
| `PROJECT.md` | Single source of project context (title, question, data in scope, deliverables). Title is the one hard requirement before substantive work. | Project |
| `README.md` | Human getting-started guide and lifecycle map. Not in the agent startup read. | Both |
| `CLAUDE.md` | Root project memory auto-loaded by Claude every session. Generated from `Infrastructure/root_instructions/CLAUDE.md`. | Adapter (generated) |
| `AGENTS.md` | Root instructions auto-loaded by Codex. Generated from `Infrastructure/root_instructions/AGENTS.md`. | Adapter (generated) |
| `Makefile` | Entry point for sync and validation targets (see §7). | Template |
| `Infrastructure/` | The shared "AI brain": workflow, guardrails, review logic, style system, references, and the canonical sources for all adapter copies (§4–§6). | Template |
| `.claude/` | Claude adapter surface: `agents/`, `commands/`, `rules/`, `templates/`, `skills/`, `settings.json`, `README.md`. Generated. | Adapter (generated) |
| `.codex/` | Codex adapter surface: `agents/` (`.md` + native `.toml`), `commands/`, `rules/`, `templates/`, `skills/`, `config.toml`, `README.md`. Generated. | Adapter (generated) |
| `.agents/skills/` | Codex repo-local workflow skills (skill-discovery surface). Generated. | Adapter (generated) |
| `code/` | Analysis scripts. Ships with `code/run_all.R` (the starter pipeline orchestrator). | Project |
| `data/` | `data/raw` (inputs as received) and `data/processed` (checkpoints). | Project |
| `drafts/` | Working prose and write-ups. | Project |
| `output/` | `output/figures` and `output/tables` (publication artifacts). | Project |

Note: the generated trees (`.claude/`, `.codex/`, `.agents/`) are **not** hand-edited. They are byte-for-byte mirrors produced from `Infrastructure/`; edits there are overwritten on the next sync and flagged by drift checks.

---

## 3. Project workspace lane (where work and outputs go)

- **Frame:** `PROJECT.md`. The agent reads it first every session; if the title is missing it stops and asks.
- **Code:** `code/`. The starter `code/run_all.R` sets a clean environment (`rm(list = ls())`, `options(scipen = 999)`, `set.seed(42)`), resolves the project root without hard-coded paths, declares required packages, and toggles numbered scripts with `TRUE`/`FALSE` flags at the top. Add numbered scripts and flip the flags.
- **Data:** `data/raw` for source data as received; `data/processed` for cleaned checkpoints (the user's convention saves checkpoints in both `.rds` and `.parquet`).
- **Drafts:** `drafts/` for prose deliverables in progress.
- **Outputs:** `output/figures` and `output/tables` for finished artifacts.
- **Review outputs (runtime):** pipeline-gated review commands write self-contained HTML reports to a `review-reports/` directory inside the review target at runtime (created on demand; not present in the fresh template).

---

## 4. Infrastructure: the shared brain

`Infrastructure/` is the canonical source of truth. Its own index is `Infrastructure/README.md`.

### 4.1 Core workflow and guardrails (read at session start)

| File | What it governs |
|---|---|
| `Infrastructure/GUARDRAILS.md` | Non-negotiable behavior: scope alignment, the Evidence standard (Sources / Confidence / Assumptions), change control, reproducibility, communication. |
| `Infrastructure/AI_WORKFLOW.md` | The five-step session process: load context → frame → execute → validate → handoff. |
| `Infrastructure/README.md` | Index of the Infrastructure tree, the update policy, and the adapter-parity model. |

### 4.2 Governance and review rules — `Infrastructure/rules/`

Binding rule files. Some are workflow/governance; most encode the review fleet's logic (each review agent reads its matching rules file). Current set:

- Workflow & governance: `Infrastructure/rules/plan-first-workflow.md`, `Infrastructure/rules/session-logging.md`, `Infrastructure/rules/verification-protocol.md`, `Infrastructure/rules/meta-governance.md`, `Infrastructure/rules/constitutional-governance.md`, `Infrastructure/rules/performance-cost-governance.md`, `Infrastructure/rules/exploration-protocol.md`, `Infrastructure/rules/replication-protocol.md`, `Infrastructure/rules/maintenance-rules.md`, `Infrastructure/rules/review-pipeline-runner.md`.
- Review logic: `Infrastructure/rules/code-quality-rules.md`, `Infrastructure/rules/methodology-rules.md`, `Infrastructure/rules/doc-number-rules.md`, `Infrastructure/rules/doc-consistency-rules.md`, `Infrastructure/rules/ai-skeptic-rules.md`, `Infrastructure/rules/data-documentation-rules.md`.
- Style logic: `Infrastructure/rules/style-writing-rules.md`, `Infrastructure/rules/style-citation-rules.md`, `Infrastructure/rules/style-figure-rules.md`, `Infrastructure/rules/style-datawrapper-rules.md`.

### 4.3 Specialist agents — `Infrastructure/agents/`

Canonical agent specs (generated into adapter agent surfaces). Current roster:

| Agent | Purpose |
|---|---|
| `Infrastructure/agents/code-reviewer.md` | Definitive code bugs plus efficiency/readability suggestions. |
| `Infrastructure/agents/methodology-reviewer.md` | Identification strategy, standard errors, weights, sample restrictions. |
| `Infrastructure/agents/data-consistency-reviewer.md` | Verifies every number in the write-up against the code that produced it. |
| `Infrastructure/agents/conceptual-consistency-reviewer.md` | Whether the prose describes what the code actually does. |
| `Infrastructure/agents/ai-skeptic.md` | Fabricated citations/functions/variables, undisclosed assumptions, edge-case fragility. |
| `Infrastructure/agents/data-dictionary-agent.md` | Acquires vintage-correct codebooks; writes the dataset registry. |
| `Infrastructure/agents/literature-scout.md` | Maps the literature and builds the annotated catalog. |
| `Infrastructure/agents/eig-writer.md` | Drafts briefs, blog posts, and summaries in EIG voice. |
| `Infrastructure/agents/eig-style-guide-agent.md` | Publication-ready figure code with token-based colors/typography. |
| `Infrastructure/agents/eig-reviewer.md` | Audits prose/figures against EIG style rules. |
| `Infrastructure/agents/maintenance-agent.md` | Runs the repository hygiene checks. |
| `Infrastructure/agents/orchestrator.md` | Decomposes a multi-stream objective and routes to specialists. |

### 4.4 Command playbooks — `Infrastructure/commands/`

Reusable workflow entrypoints. On Claude they surface as slash commands under `.claude/commands/`; on Codex they are mirrored as both `.codex/commands/` and skills. Current set: `cite`, `cover-sheet`, `document-data`, `full-review`, `literature-intake`, `maintenance-check`, `orchestrate`, `review-ai`, `review-code`, `review-consistency`, `review-methodology`, `review-numbers`, `review-style`, `smart-brevity` (each `Infrastructure/commands/<name>.md`).

### 4.5 Output templates — `Infrastructure/templates/`

Structures that agents fill in. Includes the review report shells (`Infrastructure/templates/code-error-report.md`, `methodology-report.md`, `doc-number-report.md`, `doc-consistency-report.md`, `ai-skeptic-report.md`), workflow templates (`Infrastructure/templates/requirements-spec.md`, `Infrastructure/templates/session_log.md`, `Infrastructure/templates/orchestration-plan.md`), and style outputs (`Infrastructure/templates/style-cover-sheet.md`, `style-citation-output.md`, `style-review-report.md`, `smart-brevity-output.md`, `constitutional-governance.md`, `maintenance-report.md`).

### 4.6 Skills — `Infrastructure/skills/` and `Infrastructure/style/skills/`

Reusable invokable skills (distinct from command workflows). Non-style: `Infrastructure/skills/literature-intake.md`. Style: `Infrastructure/style/skills/eig-style-apply.md`, `eig-style-datawrapper.md`, `eig-style-review.md`, `eig-tufte-critique.md`.

### 4.7 Knowledge stores — `Infrastructure/references/`

Two complementary stores (`Infrastructure/references/README.md` is the index):

- **Literature** (`Infrastructure/references/literature/`): source artifacts. `Infrastructure/references/literature/catalog.yaml` is the machine-readable index; `papers/`, `summaries/`, and `data_dictionaries/` hold the files. Entries are added via the intake playbook and validated by `Infrastructure/scripts/validate_literature_catalog.py`.
- **Datasets** (`Infrastructure/references/datasets/`): extracted structured knowledge. `Infrastructure/references/datasets/registry.yaml` is the single source of truth for recognized-dataset weights, pitfalls, identification signals, and per-variable docs; human-readable docs go in `Infrastructure/references/datasets/docs/`. Validated by `Infrastructure/scripts/validate_dataset_registry.py`. Two-layer governance: `template`/`verified` (human-curated) vs. `project`/`parsed` (agent-written, provisional). Read by `methodology-reviewer`, `code-reviewer`, and `ai-skeptic`.

### 4.8 Style subsystem — `Infrastructure/style/`

The EIG visual and editorial standard.

- Docs index: `Infrastructure/style/docs/README.md` (writing, citation, figure, brand, document-process, Datawrapper, and the Tufte graphical-quality layer).
- Design tokens: `Infrastructure/style/tokens/eig-style-tokens.v1.json` (the source of approved colors/typography).
- Theme implementations: `Infrastructure/style/themes/r/`, `Infrastructure/style/themes/python/`, `Infrastructure/style/themes/stata/`.
- Worked examples: `Infrastructure/style/examples/r/`, `python/`, `stata/`.
- Compliance and font scripts: `Infrastructure/style/scripts/` (e.g., `Infrastructure/style/scripts/compliance/check_datawrapper_manifest.py`, `Infrastructure/style/scripts/sync_tokens.py`, and `Infrastructure/style/scripts/fonts/`).
- Brand assets: `Infrastructure/style/assets/` (logos, fonts).

### 4.9 Canonical adapter sources — `Infrastructure/root_instructions/` and `Infrastructure/adapter_configs/`

- `Infrastructure/root_instructions/CLAUDE.md`, `AGENTS.md`, `claude_README.md`, `codex_README.md` — the sources that generate the root `CLAUDE.md`/`AGENTS.md` and the adapter README files.
- `Infrastructure/adapter_configs/` — per-adapter configuration and metadata: `claude.settings.json`, `codex.config.toml`, and the metadata TSVs (`codex_agent_metadata.tsv`, `claude_agent_frontmatter.tsv`, `claude_command_frontmatter.tsv`, `claude_skill_frontmatter.tsv`) that supply frontmatter/tool permissions during generation.

### 4.10 Project workspace records (inside Infrastructure)

Recoverable session context, scrubbed by `make template-reset`:

- `Infrastructure/plans/` — saved plans for non-trivial work (plan-first).
- `Infrastructure/specs/` — requirements specs for ambiguous/high-effort tasks.
- `Infrastructure/session_logs/` — recorded session history (template: `Infrastructure/templates/session_log.md`).
- `Infrastructure/explorations/` — sandbox for early experiments.

### 4.11 Scripts — `Infrastructure/scripts/`

| Script | Job |
|---|---|
| `Infrastructure/scripts/manage_generated_copies.sh` | Generates all adapter copies from canonical sources; `sync` writes, `check` reports drift. |
| `Infrastructure/scripts/check_skill_parity.py` | Verifies every canonical surface is mirrored and flags orphan adapter files. |
| `Infrastructure/scripts/check_adapter_metadata_coverage.py` | Verifies metadata TSVs cover every agent/skill. |
| `Infrastructure/scripts/check_canonical_consistency.py` | Detects unintended duplication/divergence among canonical sources. |
| `Infrastructure/scripts/check_internal_path_references.py` | Validates internal path references across all Markdown. |
| `Infrastructure/scripts/validate_literature_catalog.py` | Validates the literature catalog schema and paths. |
| `Infrastructure/scripts/validate_dataset_registry.py` | Validates the dataset registry schema and two-layer governance. |
| `Infrastructure/scripts/check_catalog_staleness.py` | Flags literature entries not verified recently. |
| `Infrastructure/scripts/run_maintenance_checks.sh` | Runs the full maintenance suite, continuing past failures. |
| `Infrastructure/scripts/template_reset.sh` | Scrubs the workspace lane to baseline for distribution. |
| `Infrastructure/scripts/simulate_cps_review_smoke_test.sh` | CPS-themed smoke test for adapter content and discovery. |

---

## 5. The canonical → adapter generation model

Claude and Codex have different native runtime surfaces, so the same logic is authored once in `Infrastructure/` and generated into each adapter tree. `Infrastructure/scripts/manage_generated_copies.sh` is the engine.

| Capability | Claude surface | Codex surface | Canonical source |
|---|---|---|---|
| Root instructions | `CLAUDE.md` | `AGENTS.md` | `Infrastructure/root_instructions/` |
| Workflows | `.claude/commands/` | `.codex/commands/` + `.codex/skills/` + `.agents/skills/` | `Infrastructure/commands/` |
| Agents | `.claude/agents/*.md` | `.codex/agents/*.toml` + `*.md` | `Infrastructure/agents/` + `Infrastructure/adapter_configs/codex_agent_metadata.tsv` |
| Skills | `.claude/skills/<name>/SKILL.md` | `.codex/skills/<name>/SKILL.md` + `.agents/skills/<name>/SKILL.md` | `Infrastructure/skills/`, `Infrastructure/style/skills/` |
| Rules & templates | `.claude/rules/`, `.claude/templates/` | `.codex/rules/`, `.codex/templates/` | `Infrastructure/rules/`, `Infrastructure/templates/` |
| Adapter README | `.claude/README.md` | `.codex/README.md` | `Infrastructure/root_instructions/claude_README.md`, `codex_README.md` |
| Adapter config | `.claude/settings.json` | `.codex/config.toml` | `Infrastructure/adapter_configs/` |

Notable asymmetry: Claude exposes review/orchestration workflows as slash commands (not auto-discovered skills), while Codex bundles them as both commands and skills because of its skill-discovery mechanism. The workflow content is identical.

**The rule that follows:** change logic in `Infrastructure/` first, then run `make brain-sync`; never edit the generated trees directly.

---

## 6. How a review actually wires together

A review command threads four canonical pieces. Using code review as the example:

1. **Command** `Infrastructure/commands/review-code.md` runs the shared pipeline-detection step (`Infrastructure/rules/review-pipeline-runner.md`): it finds and executes the project's `run_all` script and stops if the pipeline fails.
2. **Agent** `Infrastructure/agents/code-reviewer.md` is spawned read-only.
3. **Rules** `Infrastructure/rules/code-quality-rules.md` define what to flag and how to assign severity.
4. **Template** `Infrastructure/templates/code-error-report.md` is the HTML shell the agent fills in, written to a runtime `review-reports/` directory in the target.

The other reviews follow the same pattern: methodology (`review-methodology` → `methodology-reviewer` → `methodology-rules.md`), numbers (`review-numbers` → `data-consistency-reviewer` → `doc-number-rules.md`), consistency (`review-consistency` → `conceptual-consistency-reviewer` → `doc-consistency-rules.md`), AI skeptic (`review-ai` → `ai-skeptic` → `ai-skeptic-rules.md`), and `full-review` runs all five. The review agents read the dataset registry (`Infrastructure/references/datasets/registry.yaml`) for weights and pitfalls, which is why documenting data with `/document-data` strengthens the reviews.

---

## 7. Make targets (control panel)

| Target | Action |
|---|---|
| `make brain-sync` | Regenerate all adapter copies from canonical `Infrastructure/` sources. |
| `make brain-check` | Report content drift between canonical sources and generated copies. |
| `make parity-check` | Structural integrity: mirrors present, no orphan adapter files, metadata coverage, canonical consistency. |
| `make literature-check` | Validate the literature catalog. |
| `make dataset-registry-check` | Validate the dataset registry. |
| `make maintenance-check` | Run the full check suite (drift, parity, metadata, consistency, literature, path references, staleness), continuing past failures. |
| `make brain-simulate` | Run the CPS-themed review smoke test. |
| `make template-reset` | Scrub the workspace lane to baseline (`ARGS="--dry-run"` to preview). |

---

## 8. A session, start to finish

1. **Startup:** read `PROJECT.md` (request title if missing), `Infrastructure/GUARDRAILS.md`, `Infrastructure/AI_WORKFLOW.md`, and the relevant `Infrastructure/rules/`; for style-sensitive work, `Infrastructure/style/docs/README.md`. Ask the chosen full-log cadence.
2. **Plan-first:** for non-trivial work, draft a plan to `Infrastructure/plans/` (and a spec to `Infrastructure/specs/` when ambiguous) before implementing.
3. **Execute:** scripts in `code/`, data in `data/`, prose in `drafts/`, artifacts in `output/`. Reuse `Infrastructure/` guidance rather than duplicating it.
4. **Validate:** verify outputs (`Infrastructure/rules/verification-protocol.md`); attach an Evidence section to any claim-bearing output.
5. **Handoff:** log decisions/blockers incrementally and a full summary per cadence to `Infrastructure/session_logs/`.

---

## 9. Where things go — quick index

| If you need to… | Go to |
|---|---|
| Set project context | `PROJECT.md` |
| Write analysis code | `code/` (start from `code/run_all.R`) |
| Store input / cleaned data | `data/raw`, `data/processed` |
| Draft prose | `drafts/` |
| Save figures / tables | `output/figures`, `output/tables` |
| Find a paper or codebook | `Infrastructure/references/literature/` |
| Find dataset/variable knowledge | `Infrastructure/references/datasets/registry.yaml` |
| Apply EIG figure/prose style | `Infrastructure/style/docs/README.md`, `Infrastructure/style/tokens/eig-style-tokens.v1.json` |
| Change agent/command/rule behavior | edit the canonical file in `Infrastructure/`, then `make brain-sync` |
| Save a plan / spec / session log | `Infrastructure/plans/`, `Infrastructure/specs/`, `Infrastructure/session_logs/` |
| Run a quality check | the `make` targets in §7 |
