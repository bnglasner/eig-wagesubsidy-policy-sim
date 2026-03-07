# Pipeline Language Profile

Define the active pipeline implementation language for this repository.

Project root layout note: the repository root contains `WORKSPACE/` (code, data, outputs, explorations) and `INFRA/` (docs, scripts, templates, agent config).

## Required Fields

- Primary language: `[R|Python|Stata|Other]`
- Pipeline entrypoint path: `[language-specific runner path]`
  - R: `WORKSPACE/code/run_all.R`
  - Python: `WORKSPACE/code/run_all.py`
  - Stata: `WORKSPACE/code/run_all.do`
- Pipeline execution command: `[command to run entrypoint]`
  - R: `Rscript WORKSPACE/code/run_all.R`
  - Python: `python WORKSPACE/code/run_all.py`
  - Stata: `stata-mp -b do WORKSPACE/code/run_all.do` (adjust flavor as needed)
- Project bootstrap config path: `[language-specific config/bootstrap file path]`
  - R: `WORKSPACE/code/00_setup/00_config.R`
  - Python: `WORKSPACE/code/00_setup/00_config.py`
  - Stata: `WORKSPACE/code/00_setup/00_config.do`
- Stage script extension convention: `[.R|.py|.do|mixed|other]`
- Secondary language(s): `[none|language -- see integration approach in INFRA/docs/PROJECT_DECISIONS.md]`
- Project scope tier: `[1|2|3]` (1=Descriptive/Blog, 2=Analytical Brief, 3=Full Research Paper)

## Active Values In This Repository

- Primary language: `Python`
- Pipeline entrypoint path: `WORKSPACE/code/run_all.py`
- Pipeline execution command: `python WORKSPACE/code/run_all.py`
- Project bootstrap config path: `WORKSPACE/code/00_setup/00_config.py`
- Stage script extension convention: `.py`
- Secondary language(s): `none`
- Project scope tier: `1`
- Note: R and Stata runners are present from the template but are not the active pipeline for this project. Interactive app lives in `WORKSPACE/app/` and is launched separately with `streamlit run WORKSPACE/app/app.py`.

## Multi-Language Guidance

- If this template is adapted for Python, Stata, or another language, update all fields above.
- Keep stage folder structure (`01`-`05`) regardless of language.
- Keep validators and playbooks aligned with this profile and document assumptions in `INFRA/docs/PROJECT_DECISIONS.md`.


