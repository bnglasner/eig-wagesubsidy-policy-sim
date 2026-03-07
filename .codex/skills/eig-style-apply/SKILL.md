# Skill: EIG Style Apply

Use this skill when implementing or updating figure/table styling in project code.

## Source Priority

1. `INFRA/style/docs/README.md`
2. `INFRA/style/tokens/eig-style-tokens.v1.json`
3. `INFRA/style/themes/README.md`
4. Language-specific references:
   - R: `INFRA/style/docs/agent-02-r-implementation.md`
   - Python: `INFRA/style/docs/agent-04-python-implementation.md`
   - Stata: `INFRA/style/docs/agent-03-stata-implementation.md`
5. Policy:
   - `INFRA/style/docs/eig-legacy-palette-policy.md`

## Workflow

1. Detect active language from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`.
2. Apply vendored helpers:
   - R: `source("INFRA/style/themes/r/eig_theme.R")`
   - Python: `from style.themes.python.eig_theme import ...`
   - Stata: `do INFRA/style/themes/stata/eig_theme.do`
3. Use token-derived colors and typography only.
4. Validate fonts when requested:
   - `Rscript INFRA/style/scripts/fonts/check-fonts.R`
   - `python3 INFRA/style/scripts/fonts/check-fonts.py`
   - `do INFRA/style/scripts/fonts/check-fonts.do`

## Non-Negotiables

1. Do not invent net-new hex values when token equivalents exist.
2. Do not edit `INFRA/style/tokens/eig-style-tokens.v1.json` unless explicitly requested.
3. Default to 2022 primary palette usage.
4. Legacy palettes require policy justification per `INFRA/style/docs/eig-legacy-palette-policy.md`.
