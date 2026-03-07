# EIG Style Assets (Vendored)

This directory vendors key components from the separate EIG Style Guide repo so
agents can apply EIG styling without external path lookups.

## Included Components

1. Canonical tokens:
   - `INFRA/style/tokens/eig-style-tokens.v1.json`
2. Source design references (vendored for provenance):
   - `INFRA/style/sources/2022 Style Guide.pdf`
   - `INFRA/style/sources/2020 EIG Design Style Guide.docx`
3. Policy and implementation docs:
   - `INFRA/style/docs/`
4. Theme helpers:
   - `INFRA/style/themes/r/`
   - `INFRA/style/themes/python/`
   - `INFRA/style/themes/stata/`
5. Compliance checks:
   - `INFRA/style/scripts/compliance/`
6. Font checks and installers:
   - `INFRA/style/scripts/fonts/`

## Canonical Entry Points

1. Style docs index:
   - `INFRA/style/docs/README.md`
2. Theme usage:
   - `INFRA/style/themes/README.md`
3. Datawrapper contract:
   - `INFRA/style/docs/datawrapper-integration.md`

## Important Rules

1. Do not edit token values in `INFRA/style/tokens/eig-style-tokens.v1.json` unless explicitly requested.
2. Default to 2022 primary palette usage; use legacy palettes only under `INFRA/style/docs/eig-legacy-palette-policy.md`.
3. For Datawrapper workflows, validate manifests with:
   - `python3 INFRA/style/scripts/compliance/check_datawrapper_manifest.py <manifest_path>`
