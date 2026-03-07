# EIG Theme Assets (Vendored In Template)

## Canonical Source
All generated token files come from:
`INFRA/style/tokens/eig-style-tokens.v1.json`

## Sync Tokens Across Languages
If you add `INFRA/style/scripts/sync_tokens.py` in the future, run from repo root:

```bash
python3 INFRA/style/scripts/sync_tokens.py
```

Current generated token files:
- `INFRA/style/themes/python/eig_tokens.py`
- `INFRA/style/themes/r/eig_tokens.R`
- `INFRA/style/themes/stata/eig_tokens.do`

## Python Usage
```python
from INFRA.style.themes.python.eig_theme import assert_eig_fonts, set_eig_theme, eig_plotly_template

assert_eig_fonts(allow_fallback=False)
set_eig_theme()
```

## R Usage
```r
source("INFRA/style/themes/r/eig_theme.R")
tokens <- eig_load_tokens("INFRA/style/themes/r/eig_tokens.R")
eig_assert_fonts(tokens, allow_fallback = FALSE)
```

## Stata Usage
```stata
do INFRA/style/themes/stata/eig_theme.do
eig_load_tokens "INFRA/style/themes/stata/eig_tokens.do"
eig_assert_fonts
eig_graph_defaults
```

## Datawrapper Integration
- Source-of-truth token usage:
Use `INFRA/style/tokens/eig-style-tokens.v1.json` (or language token files synced from it) as the only color source for Datawrapper publishing scripts.
- Legacy palette constraints:
Default Datawrapper outputs to 2022 primary tokens. Legacy semantic sets are exception-only and must satisfy `INFRA/style/docs/eig-legacy-palette-policy.md`.
- Metadata and governance behavior:
When legacy colors are used, require metadata fields (`legacy_palette_used`, `legacy_set_id`, `legacy_palette_justification`, `approver`, `approval_date`) and validate with `INFRA/style/scripts/compliance/check_legacy_metadata.py`.
- CI enforcement:
Run `python3 INFRA/style/scripts/compliance/check_datawrapper_manifest.py <manifest_path>` in CI and fail on validation errors.
- Reference workflow template:
`INFRA/style/docs/ci/datawrapper-compliance.workflow.template.yml`

## Legacy Metadata Compliance Check
```bash
python3 INFRA/style/scripts/compliance/check_legacy_metadata.py INFRA/style/docs/legacy-metadata.template.json
```
