# Project Intake (Required Before Customization)

## Intake Quality Gates

Use these gates to decide whether implementation may begin.

- `BLOCKER`: Must be answered before implementation starts.
- `SOFT_REQUIRED`: May proceed only with explicit assumptions recorded in `docs/PROJECT_DECISIONS.md`.
- `OPTIONAL`: Helpful context; does not block implementation.

### BLOCKER fields

- **Project scope tier** *(answer this first — it gates all downstream questions)*
- Topic area
- Primary research question
- Intended audience
- Data source access type and acquisition method
- External account prerequisites for any API-accessed source (register, agree to terms, generate key, add to `.Renviron`)
- Core outcomes
- Preferred baseline design
- Primary pipeline language and execution toolchain
- Definition of done

### SOFT_REQUIRED execution context (remaining fields)

Provide concise, execution-relevant context for these fields. Helpful detail improves implementation quality, but avoid speculative or low-value background.
This context is used to prioritize follow-up questions when `BLOCKER` fields are incomplete.

| Field | Gate | Why this helps execution |
|------|------|--------------------------|
| Project name | SOFT_REQUIRED | Ensures consistent naming in config, outputs, and reporting. |
| One-sentence project objective | SOFT_REQUIRED | Aligns script scope and keeps analysis focused. |
| Secondary questions | SOFT_REQUIRED | Helps prioritize optional analyses without changing core scope. |
| Unit of analysis | SOFT_REQUIRED | Determines merge keys, aggregation logic, and model structure. |
| Time period | SOFT_REQUIRED | Defines filtering windows and panel setup. |
| Geography | SOFT_REQUIRED | Guides geographic joins, mappings, and subgrouping. |
| Core explanatory variables / treatments | SOFT_REQUIRED | Clarifies exposure construction and model inputs. |
| Data source name | SOFT_REQUIRED | Supports source tracking and reproducibility documentation. |
| Raw file format | SOFT_REQUIRED | Informs ingest/parsing approach and tool choice. |
| Update frequency | SOFT_REQUIRED | Supports refresh cadence and pipeline expectations. |
| Key identifiers | SOFT_REQUIRED | Critical for joins, deduplication, and validation. |
| Known quality caveats | SOFT_REQUIRED | Prevents avoidable inference and data-quality errors. |
| Main figures needed | SOFT_REQUIRED | Sets concrete output targets for stage `05`. |
| Main tables needed | SOFT_REQUIRED | Sets concrete output targets for stage `05`. |
| Required narrative outputs | SOFT_REQUIRED | Aligns code outputs to memo/brief/deck deliverables. |
| Figure/table style constraints | SOFT_REQUIRED | Avoids rework on formatting at the end of the pipeline. |
| Runtime constraints | SOFT_REQUIRED | Guides tradeoffs in method complexity and batching. |
| Compute environment | SOFT_REQUIRED | Prevents environment mismatch and dependency issues. |
| Pipeline entrypoint command | SOFT_REQUIRED | Defines how to run end-to-end verification for the active language. |
| Secondary language(s) | SOFT_REQUIRED | If set, agent must pause before implementing any cross-language step and present integration options with pros and cons for each before proceeding. |
| Confidentiality constraints | SOFT_REQUIRED | Shapes data handling, logging, and output boundaries. |
| Deliverable deadline | SOFT_REQUIRED | Supports staging and sequencing decisions. |
| Preferred coding style | SOFT_REQUIRED | Improves maintainability and team readability. |
| Risk tolerance for assumptions | SOFT_REQUIRED | Controls when to pause vs proceed with assumptions. |
| Whether agent may create placeholders when blocked | SOFT_REQUIRED | Controls behavior under missing inputs. |
| Whether agent should prioritize speed or rigor by default | SOFT_REQUIRED | Sets default optimization strategy for execution. |
| Data classification tiers present | SOFT_REQUIRED | Establishes handling expectations per `docs/DATA_GOVERNANCE_POLICY.md`. |

## 1) Project Identity
- Project name:
- **Project scope tier** *(BLOCKER — select one)*:
  - `1` — Descriptive / Blog post (stages: data prep, descriptive analysis, figures only)
  - `2` — Analytical Brief / Report (adds: main estimation, regression tables)
  - `3` — Full Research Paper (adds: robustness checks, heterogeneity, appendix outputs)
- Topic area:
- One-sentence project objective:
- Intended audience (policy brief, academic paper, internal memo, public dashboard):

> **Tier branching:** Tier 1 projects may skip all fields marked *(Tier 2+)* or *(Tier 3)*. Tier 2 projects may skip fields marked *(Tier 3)*.

## 2) Research Design
- Primary research question:
- Secondary questions (optional):
- Unit of analysis (tract, county, person, firm, state, etc.):
- Time period:
- Geography:
- Core outcomes:
- Core explanatory variables / treatments: *(Tier 2+)*
- Preferred design (descriptive, DiD, event study, panel FE, synthetic control, ML, other): *(Tier 2+)*

## 3) Data Sources
For each source, provide:
- Name:
- Access type (public, licensed, restricted):
- How to obtain (URL, API, manual download, request contact):
- External account prerequisites *(BLOCKER if access method = API)*:
  *e.g., register at provider site, agree to data use terms, generate API key, add to `.Renviron` as `PROVIDER_KEY=<value>` before first run*
- Raw file format:
- Update frequency:
- Key identifiers:
- Known quality caveats:

## 4) Output Requirements
- Main figures needed:
- Main tables needed:
- Appendix outputs needed: *(Tier 3)*
- Required narrative outputs (brief, memo, deck, manuscript):
- Figure/table style constraints:

## 5) Reproducibility + Operations
- Runtime constraints:
- Compute environment (local, server, cluster):
- Primary pipeline language (R/Python/Stata/Other):
- Secondary language(s) (if any):
  *If populated, agent must pause before implementing any cross-language step and ask the user to choose an integration approach. Present at minimum: (a) manual pre-step — user runs secondary script before main pipeline (simple, no extra dependencies); (b) shell call from primary runner — runner invokes secondary script via a shell command (automated, but requires both runtimes on PATH and is fragile cross-platform); (c) documented external prerequisite — acquisition step documented in `data/raw/README.md`, not wired into the runner (clearest for external reproducibility). State pros and cons for each given the project's compute environment and reproducibility requirements.*
- Pipeline entrypoint command:
- Confidentiality constraints:
- Deliverable deadline:
- Definition of done:
- Data classification tiers present in this project (select all that apply: PUBLIC / LICENSED / RESTRICTED / HIGHLY_SENSITIVE):
  *Classification determines handling and approvals. See `docs/DATA_GOVERNANCE_POLICY.md` for tier rules.*

## 6) Agent Instructions
- Preferred coding style:
- Risk tolerance for assumptions (low/medium/high):
- Whether agent may create placeholders when blocked:
- Whether agent should prioritize speed or rigor by default:
