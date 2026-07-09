# Datasets

This category is the canonical, machine-readable store of **dataset and variable knowledge** for recognized public datasets. It is the structured-knowledge counterpart to [`literature/`](../literature/): where `literature/` catalogs *source artifacts* (papers, codebooks, data dictionaries) and bibliographic metadata, `datasets/` holds the *extracted, structured knowledge* those sources contain — weights, pitfalls, identification signals, and per-variable documentation pinned to vintage.

It is maintained primarily by the [`data-dictionary-agent`](../../agents/data-dictionary-agent.md) and consumed by the review fleet.

## Contents

| Path | Purpose |
|---|---|
| [`registry.yaml`](registry.yaml) | The single source of truth for recognized-dataset knowledge. Read by agents; validated by `validate_dataset_registry.py`. |
| [`docs/`](docs/) | Human-readable per-dataset / per-variable Markdown written by the data-dictionary-agent. |

## Who reads `registry.yaml`

- `methodology-reviewer` — MR-VU1/VU2/VU3: correct survey weights by analysis context and dataset-specific pitfalls.
- `code-reviewer` — Data Currency table: dataset identification signals and `search_strategy`.
- `ai-skeptic` — AS-1c: known `variable_names` for fabrication detection.
- `data-dictionary-agent` — appends project-layer `variables`, `vintages`, and `docs`.

Each consumer reads this file instead of carrying its own copy of the knowledge, so a correction here propagates to every reviewer.

## Two layers (governance)

The registry holds two kinds of knowledge, distinguished by `layer` and `verification`:

- **`layer: template` / `verification: verified`** — reusable, cross-project knowledge curated by humans and shipped with the template (the dataset metadata, weights, and pitfalls). A reviewer treats these as authoritative.
- **`layer: project` / `verification: parsed`** — per-project variable documentation acquired by the data-dictionary-agent from the codebook for the vintage actually in use. These are provisional until a human promotes them; a reviewer treats a `parsed` entry as a lead to confirm, not as ground truth.

Per-variable entries carry their own `verification` (default `parsed`), so a project can append `parsed` variables under a `verified` template dataset without downgrading the curated metadata. The agent never writes `verified`; promotion is a human step. Nothing is ever invented — an unconfirmed field is recorded as a `[unverified: ...]` marker.

## Schema (summary)

```yaml
version: 1
last_updated: YYYY-MM-DD
datasets:
  - id: <slug>                  # unique
    name: <full name>
    layer: template | project
    verification: verified | parsed
    kind: survey | administrative | aggregate
    agency: <publishing organization>
    identification:
      file_patterns: [<glob>, ...]
      variable_names: [<name>, ...]   # used by ai-skeptic AS-1c
      loaders: [<loader call>, ...]
      comments: [<string>, ...]
    weights:                          # list, or the string `not_applicable`
      - context: <analysis context>
        ipums_name: <name|null>       # or a single `name:` field
        census_name: <name|null>
        notes: <string>
    pitfalls:
      - id: <slug>
        description: <string>
        severity: HIGH | MEDIUM | LOW
        why: <string>                 # optional econometric intuition
        what_to_check: <string>       # optional checklist text
    currency:
      search_strategy: <web-search query>   # used by code-reviewer
    vintages: []                      # project layer
    variables:                        # project layer (per-variable docs)
      - name: <variable>
        vintage: <year/release>       # required (or [unverified: ...])
        source: <authority + doc>     # required (or [unverified: ...])
        definition: <string>
        universe: <string>
        question: <question wording>
        topcoding: <string|false>
        verification: parsed | verified
    docs: []                          # repository-relative MD paths under docs/
```

Full rules are enforced by [`validate_dataset_registry.py`](../../scripts/validate_dataset_registry.py).

## Validation

Run after every edit:

```bash
python3 Infrastructure/scripts/validate_dataset_registry.py
```

`make dataset-registry-check` runs the same check, and `make maintenance-check` runs it as part of the routine hygiene pass (alongside MT-6 coverage checks).

## Adding to the registry

Use the [`/document-data`](../../commands/document-data.md) playbook. In short: acquire the codebook for the vintage in use (catalog the artifact under `literature/`), extract the relevant variables, write human-readable docs under `docs/`, append `parsed` entries to `registry.yaml`, then validate.
