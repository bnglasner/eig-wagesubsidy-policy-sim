# Data Sources And Outputs Catalog

Use this file to catalog all project inputs and outputs. Keep entries concise and execution-relevant.

**Tier 1 projects** (Descriptive/Blog): use the short-form tables below.
**Tier 2–3 projects**: use the full tables further below.

---

## Tier 1 Short Form (Descriptive / Blog)

### Inputs — Short Form

| Source ID | Source Name | Tier | Access Method | File Format | Key Identifiers | Commit Allowed | Notes |
|-----------|-------------|------|---------------|-------------|-----------------|----------------|-------|
| SRC001 | [name] | [PUBLIC/LICENSED/RESTRICTED] | [URL/manual/API] | [csv/xlsx/etc.] | [id fields] | No | [notes] |

### Outputs — Short Form

| Output ID | Output Name | Producing Script | Sensitivity Tier | Publication Approved? | Notes |
|-----------|-------------|------------------|------------------|----------------------|-------|
| OUT001 | [name] | [path/to/script] | [tier] | [Yes/No/Pending] | [notes] |

---

## Full Catalog (Tier 2–3)

## Inputs (Data Sources)

| Source ID | Source Name | Tier (`PUBLIC`/`LICENSED`/`RESTRICTED`/`HIGHLY_SENSITIVE`) | Acquisition Method | Access Type | Retrieval Date | Owner / Contact | File Format | Key Identifiers | License / Restrictions | Commit Allowed (default `No`) | Publication Approved? (human) | Notes / Open Questions |
|-----------|-------------|-------------------------------------------------------------|--------------------|-------------|----------------|-----------------|-------------|-----------------|------------------------|-------------------------------|-------------------------------|------------------------|
| SRC001 | [name] | [tier] | [URL/API/manual/request] | [public/licensed/restricted] | YYYY-MM-DD | [name/team] | [csv/parquet/etc.] | [id fields] | [terms/constraints] | No | [Yes/No/Pending] | [notes] |

## Outputs (Derived Artifacts)

| Output ID | Output Name | Producing Script | Output Type | Source IDs Used | Contains Row-Level Data? | Sensitivity Tier | Redaction / Aggregation Rule | Commit Allowed (default `No`) | Publication Approved? (human) | Notes / Open Questions |
|-----------|-------------|------------------|-------------|-----------------|--------------------------|------------------|------------------------------|-------------------------------|-------------------------------|------------------------|
| OUT001 | [name] | [path] | [table/figure/dataset] | [SRC001,...] | [Yes/No] | [tier] | [rule] | No | [Yes/No/Pending] | [notes] |

## Guidance

- Human owners must confirm classification tiers and publication approval decisions.
- Agents should ask for clarification if any tier, restriction, or approval state is missing.
- Do not add speculative fields that are not needed for implementation decisions.
