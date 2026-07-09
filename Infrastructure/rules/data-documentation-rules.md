# Data Documentation Rules

These are binding rules for the `data-dictionary-agent` and the `/document-data` command. Follow them exactly. They also govern any agent that writes to the dataset registry.

---

## Canonical Sources

- Registry: `Infrastructure/references/datasets/registry.yaml`
- Category docs: `Infrastructure/references/datasets/README.md`
- Validator: `Infrastructure/scripts/validate_dataset_registry.py`
- Artifact intake: `Infrastructure/commands/literature-intake.md`

---

## Scope

The data-dictionary agent acquires authoritative data dictionaries/codebooks for the datasets a project uses, and converts them into structured variable documentation. It documents the variables that are **used in the analysis code or clearly implied by the research question** — not the entire codebook. The set expands as code evolves.

It does **not**: edit analysis code, drafts, or figures; perform literature mapping (that is `literature-scout`); or assess identification strategy (that is `methodology-reviewer`).

---

## Rule DD-1: No Fabrication (highest priority)

1. Record only what the authoritative source states. Never infer a variable's universe, question wording, definition, or coding from its name or from a related dataset.
2. When a field is not available in the source, write the literal marker `[unverified: <what is missing>]`. A flagged gap is acceptable; a fabricated field is a critical failure.
3. Never invent a variable name. Every variable documented must exist in the codebook for the stated vintage. This is the target of `ai-skeptic` rule AS-1c.
4. Separate observed facts (from the codebook) from any interpretation the agent adds.

---

## Rule DD-2: Vintage Pinning

1. Every documented variable must record the `vintage` (year or release) it describes.
2. Definitions, universes, and question wording change across vintages (ACS year-to-year, CPS redesigns such as 2014 ASEC and 2019 NHIS, IPUMS harmonization). Documenting one vintage's variable against another's data is an error.
3. When the project uses multiple vintages of one dataset, document each vintage whose definitions differ, and note breaks in comparability.

---

## Rule DD-3: Acquisition

1. **Permission first.** Before fetching or downloading any external document, state the dataset, vintage, exact source, and whether it is a download or a read, and wait for approval. Acquire only what was approved.
2. **Authority order.** Prefer, in order: (a) the codebook/DDI shipped with the project's own data extract; (b) official agency technical documentation for the exact vintage; (c) the provider's variable pages. Never use aggregators or secondary summaries for variable semantics.
3. **Client-rendered pages.** IPUMS variable pages and many agency portals are JavaScript-rendered; a plain web fetch returns a shell. Use the browser tools or the bundled documentation. Do not retrieve blocked content through alternative scraping.
4. **Save the artifact.** Store the retrieved codebook under `Infrastructure/references/literature/data_dictionaries/` with intake naming (`YYYY_dataset_dictionary.ext`) and add a `parsed` catalog entry recording the vintage in `relevance_note`.

---

## Rule DD-4: Two-Layer Governance

The registry holds two layers, distinguished by `layer` and `verification`:

1. **Template layer** (`layer: template`, `verification: verified`) — reusable, cross-project knowledge (dataset identification, weights, pitfalls, currency signals). Human-curated and authoritative. The agent **must not** create, edit, or downgrade template entries' curated metadata.
2. **Project layer** — per-project variable documentation. Written by the agent at `verification: parsed`. Either appended as `variables` under an existing template dataset, or as a new `layer: project` dataset entry when the dataset is unrecognized.
3. **Per-variable verification.** Each variable carries its own `verification`, default `parsed`. The agent never writes `verified`; promotion is a human step.
4. A consumer (e.g., `methodology-reviewer`) treats a `verified` template entry as authoritative and a `parsed` entry as a lead to confirm before it drives a HIGH finding.

The validator enforces: `template` ⇒ `verified`; `project` ⇒ `parsed`.

---

## Rule DD-5: Output

1. **Dual output is mandatory.** Every documentation pass produces both human-readable Markdown under `Infrastructure/references/datasets/docs/` and structured entries in `registry.yaml`.
2. **Markdown naming:** `<dataset-id>_<vintage>.md`; split per-variable only for large datasets. Lead with dataset, vintage, and source; one section per variable covering definition, universe, question wording, coding/special values, and comparability.
3. **Registry variable entries** require `name`, `vintage`, and `source` (a value or an explicit `[unverified: ...]` marker). Add the doc path to the dataset's `docs:` list. Set top-level `last_updated`.

---

## Rule DD-6: Validation Before Handoff

1. Run `python3 Infrastructure/scripts/validate_dataset_registry.py` and fix every error.
2. Run `python3 Infrastructure/scripts/validate_literature_catalog.py` if a codebook artifact was added.
3. Confirm referenced doc paths exist (the validator checks this).
4. Close with an `Evidence` section: `Sources`, `Confidence` (per documented dataset), `Assumptions` (vintages, variables, scope boundary).

---

## Rule DD-7: Consumer Contract

The registry is read by other agents; changes must preserve their contract:

1. `methodology-reviewer` reads `weights` and `pitfalls` for MR-VU1/VU2/VU3. Do not remove or restructure these fields without updating that agent.
2. `code-reviewer` reads `identification` and `currency.search_strategy` for the Data Currency table.
3. `ai-skeptic` reads `identification.variable_names` for AS-1c fabrication checks.
4. Adding project `variables` and `docs` is always safe; it never alters template metadata.
