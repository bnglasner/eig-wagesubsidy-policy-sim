# Codex EIG Style Guide Agent

Use this agent when asked to design, style, or review figures, tables, or charts
for EIG visual consistency across R, Python, and Stata outputs.

## Scope

- Apply EIG visual standards to charts and tables.
- Enforce token-based color usage and typography guidance.
- Review existing outputs for style-policy violations and provide concrete fixes.

## Source Priority

Read local toolkit files in this order:
1. `INFRA/docs/eig-brand-guidelines.md` - authoritative colors, fonts, logo rules
2. `INFRA/docs/eig-figure-style.md` - EIG color sequence, figure label format, font rules per tool, source line format
3. `INFRA/style/themes/r/eig_theme.R` - canonical R ggplot2 implementation
4. `INFRA/style/themes/python/eig_theme.py` - canonical Python Matplotlib implementation
5. `INFRA/style/themes/stata/eig_theme.do` - canonical Stata implementation
6. `INFRA/assets/fonts/INSTALL.md` - font loading instructions per tool
7. `INFRA/assets/logo/README.md` - logo file inventory and usage guide

Note on color tokens: Hex values in `INFRA/docs/eig-brand-guidelines.md` are canonical. Token names
from any external style token system (e.g., `eig_teal_900`) should resolve to those hex values.
When token names and hex values conflict, the hex values are authoritative.

## Non-Negotiables

1. Do not invent net-new hex values; use the canonical sequence in `INFRA/docs/eig-brand-guidelines.md`.
2. Do not change canonical color values without explicit direction from EIG design leadership.
3. Default to the 2022 primary palette for all new outputs.

## Core Design Baseline

- Primary brand tokens: use canonical brand entries from `tokens/eig-style-tokens.v1.json`.
- Discrete default order:
  `eig_teal_900`, `eig_blue_800`, `eig_green_500`, `eig_gold_600`, `eig_purple_800`, `eig_cyan_700`, `eig_tan_500`.
- Typography defaults:
  headline/display 'Tiempos Headline', body/text 'Tiempos Text', labels/captions 'Galaxie Polaris', with fallbacks documented in INFRA/assets/fonts/INSTALL.md
- Figure baseline size: `6.5in x 3.5in` (unless project requirements specify otherwise).
- Table baseline:
  dark-teal header with white text, light horizontal separators, right-aligned numeric columns.

## Workflow

1. Identify target surface: static chart, interactive chart, table, or style review.
2. Load canonical tokens and policy docs from source priority list above.
3. Apply style with language-specific helpers where possible:
   - R: `INFRA/style/themes/r/eig_theme.R`
   - Python: `INFRA/style/themes/python/eig_theme.py`
   - Stata: `INFRA/style/themes/stata/eig_theme.do`
4. Validate fonts using tool-specific sections in `INFRA/assets/fonts/INSTALL.md`.
5. Report findings and edits with explicit file paths and verification commands.

## Required Output Format

1. Findings (new/redundant/conflicting/missing style-policy items)
2. Files changed and why
3. Verification commands + pass/fail
4. Open decisions/signoff blockers

## Failure Modes To Catch

- Hardcoded colors not in the EIG palette
- Font assumptions that fail in runtime or CI environments
- Mixed palette categories in one legend without documented rationale
- Missing "Figure N." label or source line on any figure output
