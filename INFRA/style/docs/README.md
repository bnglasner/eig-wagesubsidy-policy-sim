# EIG Style Docs Index

## Purpose
Central index for the EIG style-system documentation used by researchers and agents across projects and tooling.

Path note for this template integration:
all paths in this index are relative to the `INFRA/style/` directory in this repository.

## Start Here (Read Order)
1. Design specification:
`docs/agent-01-design-spec.md`
2. R implementation:
`docs/agent-02-r-implementation.md`
3. Legacy palette policy:
`docs/eig-legacy-palette-policy.md`
4. Design signoff checklist:
`docs/eig-design-signoff-checklist.md`

## Datawrapper Workflow Docs
1. Datawrapper integration contract:
`docs/datawrapper-integration.md`
2. Downstream adoption checklist:
`docs/datawrapper-downstream-adoption-checklist.md`
3. CI template:
`docs/ci/datawrapper-compliance.workflow.template.yml`
4. Root handoff entrypoint:
`DATAWRAPPER_PIPELINE_AGENT_HANDOFF.md`

## Agent Quickstart
Use this when an agent needs to produce EIG-consistent charts and publish to Datawrapper with compliance checks.

1. Load canonical design and pipeline rules:
- `docs/agent-01-design-spec.md`
- `docs/datawrapper-integration.md`
2. Apply token-derived colors only from:
- `tokens/eig-style-tokens.v1.json`
3. Publish/update Datawrapper charts from R pipeline using:
- `DatawRappr::dw_data_to_chart(x = ..., chart_id = ...)`
4. Emit publish manifest with required fields:
- `run_timestamp_utc`, `figure_key`, `chart_id`, `chart_url`, `rows_uploaded`, `palette_mode`, `token_source_path`, `token_version`, `legacy_metadata_path`
5. If legacy palette is used, add metadata sidecar and validate:
```bash
python3 "scripts/compliance/check_legacy_metadata.py" "<metadata_json_path>"
```
6. Validate Datawrapper manifest:
```bash
python3 "scripts/compliance/check_datawrapper_manifest.py" "<manifest_path>"
```
7. Ensure CI runs the compliance workflow (default downstream path):
- `.github/workflows/datawrapper-compliance.yml`
- Template source: `docs/ci/datawrapper-compliance.workflow.template.yml`

## Reference Assets
1. Canonical tokens:
`tokens/eig-style-tokens.v1.json`
2. Theme assets overview:
`themes/README.md`
3. Manifest validator:
`scripts/compliance/check_datawrapper_manifest.py`
4. Legacy metadata validator:
`scripts/compliance/check_legacy_metadata.py`

## Repo Links
- [agent-01-design-spec.md](agent-01-design-spec.md)
- [agent-02-r-implementation.md](agent-02-r-implementation.md)
- [eig-legacy-palette-policy.md](eig-legacy-palette-policy.md)
- [eig-design-signoff-checklist.md](eig-design-signoff-checklist.md)
- [datawrapper-integration.md](datawrapper-integration.md)
- [datawrapper-downstream-adoption-checklist.md](datawrapper-downstream-adoption-checklist.md)
- [ci/datawrapper-compliance.workflow.template.yml](ci/datawrapper-compliance.workflow.template.yml)
