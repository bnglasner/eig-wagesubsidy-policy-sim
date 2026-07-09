---
name: document-data
description: >-
  Acquire the authoritative data dictionary for a dataset the project uses, pin it to the vintage in use, and convert the relevant variables into per-variable Markdown plus structured entries in the dataset registry.
---

# Document Data Playbook

Acquire the authoritative data dictionary for a dataset the project uses, pin it to the vintage in use, and convert the relevant variables into per-variable Markdown plus structured entries in the dataset registry.

Use this playbook whenever a project takes on a new data source, or when analysis code starts using variables that are not yet documented. It is the intake path for the [`data-dictionary-agent`](../agents/data-dictionary-agent.md) and is governed by [`data-documentation-rules.md`](../rules/data-documentation-rules.md).

## Canonical Locations

- Registry (structured knowledge): `Infrastructure/references/datasets/registry.yaml`
- Human-readable docs: `Infrastructure/references/datasets/docs/`
- Saved codebook artifacts: `Infrastructure/references/literature/data_dictionaries/`
- Literature catalog (artifact index): `Infrastructure/references/literature/catalog.yaml`

## Workflow

1. **Load first.** Read `registry.yaml` (recognized datasets already carry a curated `template` layer — do not re-create it), the literature catalog (reuse a codebook already saved), `PROJECT.md` Data in Scope, and the analysis code. The documentation target is the intersection of in-scope datasets and variables used or clearly implied by the question.
2. **Confirm scope and ask permission.** State each dataset, the vintage(s) to document, and the exact source to retrieve (download vs. read). Wait for approval before any fetch or download.
3. **Acquire the codebook, vintage-pinned.** Prefer the DDI/codebook shipped with the project's own extract, then official agency documentation for the exact vintage, then the provider's variable pages (use browser tools for JavaScript-rendered pages). Save the artifact under `data_dictionaries/` with `YYYY_dataset_dictionary.ext` naming and add a `parsed` literature catalog entry recording the vintage.
4. **Extract relevant variables.** For each variable record only what the source states: definition, universe, question wording, source/vintage, coding and special values (missing codes, topcoding, allocation flags), and comparability. Record any missing field as `[unverified: ...]`. Never infer from a variable name.
5. **Write dual output.**
   - Markdown: `Infrastructure/references/datasets/docs/<dataset-id>_<vintage>.md`.
   - Registry: append the variables (each with `name`, `vintage`, `source`, `verification: parsed`) to the matching dataset's `variables:` list and add the doc path to `docs:`. If the dataset is unrecognized, add a new `layer: project`, `verification: parsed` entry. Update `last_updated`. Never edit the `verified` template metadata.
6. **Validate.**
   ```bash
   python3 Infrastructure/scripts/validate_dataset_registry.py
   python3 Infrastructure/scripts/validate_literature_catalog.py
   ```
7. **Hand off.** Report which datasets and vintages are now documented and which fields remain `[unverified: ...]`. The registry now feeds `methodology-reviewer`, `code-reviewer`, and `ai-skeptic`.

## Required Registry Fields (project variables)

Every variable appended to the registry must include:

- `name`: variable name exactly as it appears in the codebook
- `vintage`: the year/release it describes (or `[unverified: ...]`)
- `source`: publishing authority and document (or `[unverified: ...]`)
- `verification`: `parsed` (the agent never writes `verified`)

Recommended where available: `definition`, `universe`, `question`, `topcoding`, `coding`, `comparability`.

## Quality Check Before Handoff

- [ ] Permission was obtained before any download/fetch
- [ ] Every documented variable is pinned to a vintage
- [ ] No field was inferred; gaps are marked `[unverified: ...]`
- [ ] Codebook artifact saved and catalogued; doc paths resolve
- [ ] `validate_dataset_registry.py` passes
- [ ] Template metadata (weights, pitfalls) was not altered
