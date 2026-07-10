# 05e_slide_figures.R
# Build the slide-native companion figures into output/figures/slides/.
# Sources the figure-function definitions from 05c/05d with their document
# drivers suppressed (EIG_FIG_NO_RUN), then calls each with slide = TRUE.
# Dimensions + slide text come from code/05_figures_tables/slide_figures.json
# (see Infrastructure/specs/2026-07-09_slide-native-figures.md).

EIG_FIG_NO_RUN <- TRUE

.this_dir <- (function() {
  args <- commandArgs(trailingOnly = FALSE)
  fa <- grep("^--file=", args, value = TRUE)
  if (length(fa) > 0) return(dirname(normalizePath(sub("^--file=", "", fa[1]))))
  file.path(getwd(), "code", "05_figures_tables")
})()

source(file.path(.this_dir, "05c_core_figures.R"))   # defs only (driver guarded)
source(file.path(.this_dir, "05d_supporting_figures.R"))

cat("Building slide-native companion figures -> output/figures/slides/\n\n")

# --- 05c (function name -> output slug) ---
fig2_subsidy_schedule(slide = TRUE)    # fig01_subsidy_schedule
fig3_cost_waterfall(slide = TRUE)      # fig02_cost_waterfall
fig4_takeup_by_group(slide = TRUE)     # fig03_takeup_by_group      (twocol)
fig1_choropleth(slide = TRUE)          # fig05_avg_subsidy_by_state (twocol, map)
fig5_cost_per_job(slide = TRUE)        # fig10_cost_per_job
fig6_clawback_net_gain(slide = TRUE)   # fig12_clawback_net_gain

# --- 05d ---
fig7_entry_band_by_cell(slide = TRUE)     # fig07_entry_band_by_cell
fig7b_entrants_by_status(slide = TRUE)    # fig07b_entrants_by_status
fig8_cost_band(slide = TRUE)              # fig13_cost_band
fig9_subsidy_by_wage(slide = TRUE)        # fig04_subsidy_by_wage
fig10_firm_capture(slide = TRUE)          # fig09_firm_capture
fig11_benefit_cliff(slide = TRUE)         # fig11_benefit_cliff
fig11b_net_income_by_hours(slide = TRUE)  # fig11b_net_income_by_hours
fig12_reservation_wage(slide = TRUE)      # fig06_reservation_wage
fig13_pool_wage_distribution(slide = TRUE) # fig08_pool_wage_distribution
fig14_mpl_uncertainty(slide = TRUE)       # fig14_mpl_uncertainty      (twocol)
fig15_hours_margin(slide = TRUE)          # fig15_hours_margin
figA1_wage_distribution(slide = TRUE)     # figA1_wage_distribution

cat("\nSlide figures done.\n")
