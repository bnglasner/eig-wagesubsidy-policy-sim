# code-conventions

Read the active language from `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md` and apply the
appropriate language section below. Universal rules apply regardless of language.

## Universal Rules

- Source the project bootstrap config defined in `INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md`
  at the top of every pipeline script.
- Use relative paths derived from config objects (no hardcoded absolute paths).
- Keep script names numeric and stage-scoped (`00` to `05`).
- In run-all orchestrators, declare execution flags as explicit one-per-component
  `TRUE`/`FALSE` lines in stage order with readable labels/comments.
- Do not rely on compact list/vector-only flag declarations as the primary run-all
  control surface.
- Ensure each output artifact maps to a producing script.
- Avoid hidden side effects and unintended mutations of shared or global state.

## R

Applies when primary language is `R`.

- Source `WORKSPACE/code/00_setup/00_config.R` at the top of every pipeline script.
- Reference all paths via config objects (`path_data_raw`, `path_output_fig_main`, etc.).
- Avoid `<<-` and direct assignment to the global environment outside of config.

## Python

Applies when primary language is `Python`.

- Import config at the top of every pipeline script:
  `import code.setup.config as cfg` (or equivalent relative import from project root).
- Reference all paths via `pathlib.Path` objects exported from config
  (`PATH_DATA_RAW`, `PATH_OUTPUT_FIG_MAIN`, etc.).
- Avoid mutable module-level state; encapsulate processing in functions or classes.

## Stata

Applies when primary language is `Stata`.

- Run `do "$path_WORKSPACE/code/00_setup/00_config.do"` at the top of every pipeline do-file.
- Reference all paths via global macros defined in config
  (`$path_data_raw`, `$path_output_fig_main`, etc.).
- Use `capture log close` / `log using` consistently for reproducible output tracking.

