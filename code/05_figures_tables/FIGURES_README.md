# Publication figures (Figures 1–13)

EIG-styled figure suite for the wage-subsidy impact/cost summary
(`drafts/2026-07-08_wage-subsidy-impact-cost-summary.md`). Built in R/ggplot2 against the
canonical EIG theme (`Infrastructure/style/themes/r/eig_theme.R`), reading the pipeline's
intermediate parquets. Outputs: `output/figures/main/figNN_slug.{png,svg}` (PNG 300 dpi).

## Regenerate

    Rscript code/05_figures_tables/05c_core_figures.R        # Figures 1–6
    Rscript code/05_figures_tables/05d_supporting_figures.R  # Figures 7–13

`run_all.py` runs both automatically after stage 05 when `RUN_05_R_FIGURES = True`
(skipped gracefully if Rscript is absent).

## Files

- `eig_fig_utils.R` — shared harness: `eig_setup()`, `eig_save_fig()`, `eig_caption()`, source line.
- `05c_core_figures.R` — Fig 1 subsidy schedule, 2 cost waterfall, 3 take-up, 4 progressivity,
  5 state choropleth, 6 reservation-wage schematic.
- `05d_supporting_figures.R` — Fig 7 entry band, 8 pool wage distribution, 9 firm capture,
  10 cost per job, 11 benefit cliff, 12 clawback, 13 cost band.
- `05b_state_choropleth.py` — DEPRECATED (Python/plotly; superseded by Fig 5 in 05c; retained
  only as the Streamlit app's interactive-choropleth pattern source).

## R packages (not in code/_utils/00_packages.R, which is ORG-ingestion-only)

arrow, ggplot2, dplyr, sf, tigris, scales, showtext, systemfonts, ragg, svglite.
