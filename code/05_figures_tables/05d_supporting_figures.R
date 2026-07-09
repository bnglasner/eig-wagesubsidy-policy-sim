#!/usr/bin/env Rscript
# 05d_supporting_figures.R
# Batch 2 of the EIG-styled figure suite (R/ggplot2). Figures 7-15.
#
# Reuses the Batch 1 harness (eig_fig_utils.R) and the canonical EIG theme +
# tokens. Each figure is its own function.
#
#   Figure 7  - Induced entry band by group      (fig7_entry_band_by_cell)
#   Figure 7b - Entrants by prior status          (fig7b_entrants_by_status)
#   Figure 8  - Net cost stable across models     (fig8_cost_band)
#   Figure 9  - Subsidy by wage bracket           (fig9_subsidy_by_wage)
#   Figure 10 - Firm capture, sticky vs flexible  (fig10_firm_capture)
#   Figure 11 - Benefit cliffs (single parent)    (fig11_benefit_cliff)
#   Figure 12 - Reservation-wage schematic        (fig12_reservation_wage)
#   Figure 13 - Non-employed potential-wage dist. (fig13_pool_wage_distribution)
#   Figure 14 - Entry under mpl uncertainty       (fig14_mpl_uncertainty)
#   Figure 15 - Intensive margin: added hours     (fig15_hours_margin)

suppressWarnings(suppressMessages({
  library(arrow)
  library(dplyr)
  library(ggplot2)
  library(scales)
}))

# --- source the shared harness ---------------------------------------------
.this_dir <- (function() {
  args <- commandArgs(trailingOnly = FALSE)
  fa <- grep("^--file=", args, value = TRUE)
  if (length(fa) > 0) return(dirname(normalizePath(sub("^--file=", "", fa[1]))))
  file.path(getwd(), "code", "05_figures_tables")
})()
source(file.path(.this_dir, "eig_fig_utils.R"))

ctx <- eig_setup()
tokens <- ctx$tokens
ROOT <- ctx$root
COL <- tokens$EIG_COLORS
GRAY <- "#9AA0A6"

DATA_POP <- file.path(ROOT, "output", "data", "intermediate_results", "population")
pop <- function(name) read_parquet(file.path(DATA_POP, paste0(name, ".parquet")))

# ===========================================================================
# FIGURE 7 - Induced entry into work, by group (central + lower-upper band)
# ===========================================================================
fig7_entry_band_by_cell <- function() {
  # Re-centered (2026-07-09): per group, the range from the conservative floor (no wage penalty)
  # to the high joint corner, with the evidence-central marked. Reads the three headline bundles.
  hs <- pop("entry_headline_scenarios")
  get <- function(scn, col) hs[[col]][hs$scenario == scn]

  rows <- tibble::tibble(
    group = c("Total", "Single mothers", "Other women", "Men"),
    col = c("induced_M", "induced_single_mothers_M",
            "induced_other_women_M", "induced_men_M")
  ) %>%
    mutate(
      lo = vapply(col, function(c) get("conservative_floor", c), numeric(1)),
      mid = vapply(col, function(c) get("evidence_central", c), numeric(1)),
      hi = vapply(col, function(c) get("high", c), numeric(1)),
      group = factor(group, levels = rev(c("Total", "Single mothers",
                                           "Other women", "Men")))
    )

  # Precedent ladder: each precedent's employment effect scaled to the model's
  # reachable pool, shown as reference ticks on the Total row.
  prec <- tibble::tibble(
    x = c(0.6, 1.2, 1.9, 3.4),
    lab = c("Paycheck Plus\nscale", "1990s EITC-alone\nscale",
            "Paycheck Plus\nmen Y3 scale", "SSP scale")
  )
  total_y <- which(levels(rows$group) == "Total")

  p <- ggplot(rows, aes(y = group)) +
    geom_linerange(aes(xmin = lo, xmax = hi),
                   color = COL[["eig_green_500"]], linewidth = 2.2, alpha = 0.55) +
    geom_segment(data = prec,
                 aes(x = x, xend = x,
                     y = total_y - 0.16, yend = total_y + 0.16),
                 inherit.aes = FALSE, color = "#BBBBBB", linewidth = 0.5) +
    geom_text(data = prec,
              aes(x = x, y = total_y - 0.24, label = lab),
              inherit.aes = FALSE, vjust = 1, size = 2.1, lineheight = 0.9,
              color = "#999999", family = tokens$EIG_FONT_BODY_PRIMARY) +
    geom_point(aes(x = mid), size = 3.6, color = COL[["eig_green_700"]]) +
    geom_text(aes(x = mid, label = sprintf("%.2fM", mid)),
              vjust = -1.1, size = 2.7, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    geom_text(aes(x = hi, label = sprintf("%.2f", hi)),
              hjust = -0.35, vjust = 0.5, size = 2.3, color = "#777777",
              family = tokens$EIG_FONT_BODY_PRIMARY) +
    geom_text(aes(x = lo, label = sprintf("%.2f", lo)),
              hjust = 1.35, vjust = 0.5, size = 2.3, color = "#777777",
              family = tokens$EIG_FONT_BODY_PRIMARY) +
    scale_x_continuous(labels = scales::label_number(suffix = "M"),
                       limits = c(-0.1, 3.9),
                       expand = expansion(mult = c(0.02, 0.06))) +
    labs(
      title = "Figure 7. Induced entry into work, by group\n(evidence-central, with floor–high range).",
      x = "Induced entrants (millions)", y = NULL,
      caption = eig_caption(
        note = paste0("The bar spans the conservative floor (no non-employment wage penalty) to the high joint\n",
                      "corner (20% penalty, full dispersion, upper elasticity); the point is the evidence-central\n",
                      "(status-differentiated ~10% penalty). Reference marks scale each precedent's employment\n",
                      "effect to the model's reachable pool.")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig07_entry_band_by_cell",
               width = 7.2, height = 4.0, root = ROOT)
}

# ===========================================================================
# FIGURE 7b - Who the model predicts will enter, by prior status
# ===========================================================================
fig7b_entrants_by_status <- function() {
  # Evidence-central composition (status-differentiated ~10% penalty; 1.25M headline), written by
  # 02g to entry_central_composition.parquet: unemployed 0.412M, other NILF 0.799M, disabled
  # 0.028M, retired 0.010M (~33% / 64% / 2% / 1%). Falls back to the floor sim if absent.
  comp_path <- file.path(DATA_POP, "entry_central_composition.parquet")
  if (file.exists(comp_path)) {
    comp <- read_parquet(comp_path)
    getc <- function(s) comp$entrants_M[comp$prior_status == s]
    ev <- c(getc("unemployed"), getc("nilf_other"), getc("disabled"), getc("retired"))
  } else {
    ms <- pop("matching_simulation")
    ev <- c(ms$entrants_unemployed_M[1], ms$entrants_nilf_other_M[1],
            ms$entrants_disabled_M[1], ms$entrants_retired_M[1])
  }
  d <- tibble::tibble(
    status = c("Unemployed", "Other non-participants", "Disabled", "Retired"),
    entrants_M = ev
  ) %>%
    mutate(status = reorder(status, entrants_M))

  p <- ggplot(d, aes(x = entrants_M, y = status)) +
    geom_col(width = 0.62, fill = COL[["eig_green_700"]]) +
    geom_text(aes(label = sprintf("%.3fM", entrants_M)),
              hjust = -0.15, size = 3.0,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_x_continuous(labels = scales::label_number(suffix = "M"),
                       expand = expansion(mult = c(0, 0.14))) +
    labs(
      title = "Figure 7b. Who the model predicts will enter,\nby prior status.",
      x = "Induced entrants (millions)", y = NULL,
      caption = eig_caption(
        note = paste0("Entry propensity is weighted by prior labor-force status (CPS U-to-E vs. N-to-E flow ratios;\n",
                      "SSDI work-capacity evidence) and the employment probit; calibrated totals are unchanged.")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig07b_entrants_by_status",
               width = 6.5, height = 3.2, root = ROOT)
}

# ===========================================================================
# FIGURE 8 - Net annual cost is stable across models
# ===========================================================================
fig8_cost_band <- function() {
  ms <- pop("matching_simulation")
  s <- pop("summary")

  static_net <- s$net_cost_bn[1]                      # 72.12
  bs <- pop("behavioral_scenarios") %>%
    filter(scenario != "static")
  rf_lo <- min(bs$net_cost_bn); rf_hi <- max(bs$net_cost_bn)   # reduced-form band

  rigid <- ms %>% filter(wage_mode == "rigid")
  flex <- ms %>% filter(wage_mode == "flex")

  rows <- tibble::tribble(
    ~group,                                       ~lo,        ~mid,                       ~hi,        ~kind,
    "Static (no behavioral response)",            static_net, static_net,                 static_net, "core",
    "Reduced-form behavioral band",               rf_lo,      (rf_lo + rf_hi) / 2,        rf_hi,      "core",
    "Structural, sticky incumbent wages",         min(rigid$net_cost_bn), median(rigid$net_cost_bn), max(rigid$net_cost_bn), "core",
    "Structural, all wages renegotiate (bound)",  min(flex$net_cost_bn),  median(flex$net_cost_bn),  max(flex$net_cost_bn),  "bound"
  ) %>%
    mutate(group = factor(group, levels = rev(group)))

  p <- ggplot(rows, aes(y = group, color = kind)) +
    annotate("rect", xmin = 72, xmax = 78, ymin = -Inf, ymax = Inf,
             fill = COL[["eig_green_500"]], alpha = 0.12) +
    geom_linerange(aes(xmin = lo, xmax = hi, linetype = kind), linewidth = 1.8) +
    geom_point(aes(x = lo), size = 3) +
    geom_point(aes(x = hi), size = 3) +
    geom_text(aes(x = hi, label = sprintf("$%.0f–$%.0fB", lo, hi)),
              data = filter(rows, lo != hi),
              hjust = -0.12, vjust = 0.5, size = 2.6,
              family = tokens$EIG_FONT_BODY_PRIMARY, color = COL[["eig_black"]]) +
    geom_text(aes(x = mid, label = sprintf("$%.0fB", mid)),
              data = filter(rows, lo == hi),
              hjust = -0.3, vjust = 0.5, size = 2.6,
              family = tokens$EIG_FONT_BODY_PRIMARY, color = COL[["eig_black"]]) +
    annotate("text", x = 135, y = 1, label = "disclosed upper bound,\nnot a forecast",
             size = 2.4, color = GRAY, fontface = "italic",
             family = tokens$EIG_FONT_BODY_PRIMARY, vjust = -0.9) +
    scale_color_manual(values = c("core" = COL[["eig_green_700"]], "bound" = GRAY),
                       guide = "none") +
    scale_linetype_manual(values = c("core" = "solid", "bound" = "22"),
                          guide = "none") +
    scale_x_continuous(labels = scales::label_dollar(suffix = "B"),
                       limits = c(60, 165),
                       expand = expansion(mult = c(0.01, 0.06))) +
    labs(
      title = "Figure 13. Net annual cost is stable across models; only full\nwage renegotiation escapes the $72–78 billion range.",
      x = "Net annual cost", y = NULL,
      caption = eig_caption(
        note = "Shaded band marks the $72–78B core range. Values in billions of dollars."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank(),
          axis.text.y = element_text(size = 8.5),
          # Long y labels push the panel right; anchor the (wide) title to the
          # full plot so it does not clip at the right edge.
          plot.title.position = "plot")

  eig_save_fig(p, "fig13_cost_band",
               width = 7.4, height = 3.8, root = ROOT)
}

# ===========================================================================
# FIGURE 9 - The lowest-wage workers receive the largest subsidies
# ===========================================================================
fig9_subsidy_by_wage <- function() {
  wb <- pop("by_wage_bracket") %>%
    mutate(wage_bracket = factor(wage_bracket,
                                 levels = rev(c("$7.25-$9", "$9-$11",
                                                "$11-$13", "$13-$16.80"))))

  p <- ggplot(wb, aes(x = avg_annual_subsidy, y = wage_bracket)) +
    geom_col(width = 0.7, fill = COL[["eig_gold_600"]]) +
    geom_text(aes(label = scales::dollar(avg_annual_subsidy)),
              hjust = -0.12, size = 3.0, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    geom_text(aes(label = sprintf("%.1fM workers", n_workers_k / 1000)),
              x = 200, hjust = 0, vjust = 0.5, size = 2.5,
              family = tokens$EIG_FONT_BODY_PRIMARY, color = "white") +
    scale_x_continuous(labels = scales::label_dollar(),
                       expand = expansion(mult = c(0, 0.16))) +
    labs(
      title = "Figure 4. The lowest-wage workers receive\nthe largest subsidies.",
      x = "Average annual subsidy", y = "Hourly wage bracket",
      caption = eig_caption(
        note = "Bar labels show the average annual subsidy; interior labels show the number of workers."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig04_subsidy_by_wage",
               width = 6.6, height = 3.4, root = ROOT)
}

# ===========================================================================
# FIGURE 10 - Employers capture little under realistic wage stickiness
# ===========================================================================
fig10_firm_capture <- function() {
  ms <- pop("matching_simulation")

  beta_lab <- c("0.3" = "Rigid (β = 0.3)",
                "0.5" = "Central (β = 0.5)",
                "0.7" = "Measured (β = 0.7)")

  d <- ms %>%
    transmute(
      beta_tag = factor(beta_lab[as.character(beta)],
                        levels = c("Central (β = 0.5)", "Measured (β = 0.7)",
                                   "Rigid (β = 0.3)")),
      series = ifelse(wage_mode == "rigid",
                      "Sticky incumbent wages (realistic)",
                      "All wages renegotiate (bound)"),
      capture = firm_capture_pct_of_gross
    ) %>%
    mutate(series = factor(series,
                           levels = c("Sticky incumbent wages (realistic)",
                                      "All wages renegotiate (bound)")))

  p <- ggplot(d, aes(x = beta_tag, y = capture, fill = series)) +
    geom_col(position = position_dodge(width = 0.7), width = 0.62) +
    geom_text(aes(label = sprintf("%.1f%%", capture)),
              position = position_dodge(width = 0.7),
              vjust = -0.4, size = 2.7, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_fill_manual(values = c("Sticky incumbent wages (realistic)" = COL[["eig_green_700"]],
                                 "All wages renegotiate (bound)" = GRAY),
                      name = NULL) +
    scale_y_continuous(labels = scales::label_percent(scale = 1),
                       expand = expansion(mult = c(0, 0.1))) +
    labs(
      title = "Figure 9. Employers capture little under realistic wage stickiness.",
      x = "Pass-through scenario", y = "Firm capture (share of gross cost)",
      caption = eig_caption(
        note = "The all-wages-renegotiate case is a disclosed upper bound, not a forecast."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(legend.position = "top")

  eig_save_fig(p, "fig09_firm_capture",
               width = 6.8, height = 4.0, root = ROOT)
}

# ===========================================================================
# FIGURE 11 - Benefit cliffs a single-parent household crosses
# ===========================================================================
fig11_benefit_cliff <- function() {
  state <- "PA"  # Medicaid-expansion state; clear multi-cliff schedule
  sched_files <- Sys.glob(file.path(ROOT,
    "output/data/intermediate_results/individual_schedules/single_2c_*.parquet"))
  if (length(sched_files) == 0) {
    sched_files <- Sys.glob(file.path(ROOT,
      "output/data/intermediate_results/individual_schedules/single_1c_*.parquet"))
    state <- "?"
  }
  file <- grep(sprintf("single_2c_%s", state), sched_files, value = TRUE)
  if (length(file) == 0) file <- sched_files[1]

  d <- as.data.frame(read_parquet(file)) %>%
    filter(annual_income <= 45000) %>%
    mutate(ni = net_income + aca_ptc + medicaid_chip)

  # Cliff annotations (attributed from PA program deltas).
  cliffs <- tibble::tribble(
    ~x,      ~lab,
    8500,    "TANF ends",
    38000,   "Adults lose Medicaid (→ ACA)",
    43500,   "Childcare & remaining benefits phase out"
  ) %>%
    mutate(y = approx(d$annual_income, d$ni, x)$y)

  p <- ggplot(d, aes(x = annual_income)) +
    geom_abline(slope = 1, intercept = 0, color = GRAY,
                linetype = "22", linewidth = 0.4) +
    annotate("text", x = 41000, y = 41000, label = "earnings only",
             angle = 33, size = 2.5, color = "#888888", vjust = -0.5,
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    geom_line(aes(y = ni), color = COL[["eig_green_700"]], linewidth = 1.1) +
    geom_point(data = cliffs, aes(x = x, y = y), color = COL[["eig_gold_600"]],
               size = 2.6) +
    geom_text(data = cliffs, aes(x = x, y = y, label = lab),
              hjust = c(-0.06, 1.04, 1.04), vjust = c(1.8, 2.2, 1.6),
              size = 2.5, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_teal_900"]]) +
    scale_x_continuous(labels = scales::label_dollar(),
                       expand = expansion(mult = c(0.01, 0.03))) +
    scale_y_continuous(labels = scales::label_dollar()) +
    labs(
      title = "Figure 11. Why the clawback bites: net income and the\nbenefit cliffs a single-parent household crosses.",
      x = "Annual earnings", y = "Net income (incl. ACA & Medicaid value)",
      caption = eig_caption(
        note = paste0("One representative single-parent, two-child schedule (Pennsylvania), illustrative.\n",
                      "Net income includes ACA premium tax credits and Medicaid value, per the model.")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10)

  eig_save_fig(p, "fig11_benefit_cliff",
               width = 7.0, height = 4.4, root = ROOT)
  invisible(basename(file))
}

# ===========================================================================
# FIGURE 11b - Net income by hours worked, with vs. without the 80-80 subsidy
# ===========================================================================
fig11b_net_income_by_hours <- function() {
  file <- file.path(ROOT,
    "output/data/intermediate_results/individual_schedules/single_2c_PA.parquet")

  d <- as.data.frame(read_parquet(file))
  d <- d[order(d$annual_income), ]
  d$ni <- d$net_income + d$aca_ptc + d$medicaid_chip

  # Model net income on the earned-income axis (matches Figure 11 and the app).
  NI <- function(x) approx(d$annual_income, d$ni, xout = x, rule = 2)$y

  wage <- 10                       # fixed employer wage, $/hr
  target <- 16.80
  sub_ph <- 0.80 * (target - wage) # $5.44/hr
  cap_hours <- 2080                # subsidy cap: 40 hr/wk x 52 wk = 2,080 hrs/yr (matches the
                                   # pipeline's ws_subsidy_hours_cap * 52 in 01h/02d)

  H <- seq(0, 3000, by = 25)
  curve <- tibble::tibble(
    hours = H,
    no_sub = NI(wage * H),
    with_sub = NI(wage * H + sub_ph * pmin(H, cap_hours))
  )

  long <- bind_rows(
    curve %>% transmute(hours, ni = no_sub, series = "Without the wage subsidy"),
    curve %>% transmute(hours, ni = with_sub, series = "With the wage subsidy")
  ) %>%
    mutate(series = factor(series,
                           levels = c("With the wage subsidy",
                                      "Without the wage subsidy")))

  # Shade the vertical gap: gold where the subsidy adds net income,
  # neutral red where counting it as income turns it net-negative.
  gap <- curve %>%
    mutate(ymin = pmin(no_sub, with_sub),
           ymax = pmax(no_sub, with_sub),
           sign = ifelse(with_sub >= no_sub, "gain", "loss"))

  # Real crossover: where the advantage turns negative (with_sub drops below no_sub).
  cross_x <- {
    dff <- curve$with_sub - curve$no_sub
    idx <- which(dff[-length(dff)] > 0 & dff[-1] <= 0)
    idx <- idx[idx > 1][1]  # ignore the trivial H=0 tie
    if (is.na(idx)) NA_real_ else approx(
      dff[c(idx, idx + 1)], curve$hours[c(idx, idx + 1)], xout = 0)$y
  }

  hrs_breaks <- seq(0, 3000, by = 500)
  hrs_labels <- sprintf("%d\n(%d hr/wk)", hrs_breaks, hrs_breaks / 50)

  p <- ggplot() +
    geom_ribbon(data = filter(gap, sign == "gain"),
                aes(x = hours, ymin = ymin, ymax = ymax),
                fill = COL[["eig_gold_600"]], alpha = 0.30) +
    geom_ribbon(data = filter(gap, sign == "loss"),
                aes(x = hours, ymin = ymin, ymax = ymax),
                fill = COL[["eig_tan_500"]], alpha = 0.40) +
    geom_vline(xintercept = cap_hours, color = COL[["eig_teal_900"]],
               linetype = "dashed", linewidth = 0.4) +
    geom_line(data = long, aes(x = hours, y = ni, color = series),
              linewidth = 1.1) +
    annotate("text", x = cap_hours - 40, y = 55500,
             label = "Subsidy hours cap (2,080 hrs/yr)", angle = 90,
             hjust = 0, vjust = 1.2, size = 2.5, color = COL[["eig_teal_900"]],
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    annotate("text", x = 2560, y = 63200,
             label = "Counted as income, the subsidy pushes\nthe household across benefit cliffs",
             hjust = 0.5, size = 2.5, fontface = "italic", color = COL[["eig_tan_500"]],
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    scale_color_manual(
      values = c("With the wage subsidy" = COL[["eig_green_700"]],
                 "Without the wage subsidy" = COL[["eig_teal_900"]]),
      name = NULL,
      breaks = c("Without the wage subsidy", "With the wage subsidy")) +
    scale_x_continuous(breaks = hrs_breaks, labels = hrs_labels,
                       expand = expansion(mult = c(0.02, 0.05))) +
    scale_y_continuous(labels = scales::label_dollar()) +
    labs(
      title = "Figure 11b. Net income by hours worked, with and without\nthe 80-80 subsidy.",
      x = "Annual hours worked", y = "Net income (incl. ACA & Medicaid value)",
      caption = eig_caption(
        note = paste0("Illustrative: single parent of two, Pennsylvania, fixed $10 per hour. Hours span 0-60 per\n",
                      "week over a 50-week year; the subsidy is capped at 2,080 hours per year (the model's 40-hour-\n",
                      "per-week cap) and counted as taxable income. Net income includes ACA premium tax credits and Medicaid value.")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(legend.position = "top")

  eig_save_fig(p, "fig11b_net_income_by_hours",
               width = 7.2, height = 4.6, root = ROOT)

  invisible(list(
    a1000 = c(no = NI(wage * 1000), sub = NI(wage * 1000 + sub_ph * 1000)),
    a2000 = c(no = NI(wage * 2000), sub = NI(wage * 2000 + sub_ph * min(2000, cap_hours))),
    a3000 = c(no = NI(wage * 3000), sub = NI(wage * 3000 + sub_ph * min(3000, cap_hours))),
    crossover_hours = cross_x
  ))
}

# ===========================================================================
# FIGURE 12 - How the subsidy clears a worker's reservation wage (schematic)
# ===========================================================================
fig12_reservation_wage <- function() {
  target <- 16.80
  offer <- 12
  reservation <- 14
  subsidized <- offer + 0.80 * max(0, target - offer)  # 15.84

  d <- tibble::tribble(
    ~label,                       ~value,   ~grp,
    "Employer offer",              offer,   "offer",
    "Offer + 80-80 subsidy",       subsidized, "subsidized"
  ) %>%
    mutate(label = factor(label, levels = rev(c("Employer offer",
                                                "Offer + 80-80 subsidy"))))

  p <- ggplot(d, aes(x = value, y = label, fill = grp)) +
    # "won't work below this" region up to the reservation wage
    annotate("rect", xmin = 0, xmax = reservation, ymin = -Inf, ymax = Inf,
             fill = GRAY, alpha = 0.14) +
    geom_vline(xintercept = reservation, color = COL[["eig_purple_800"]],
               linetype = "solid", linewidth = 0.5) +
    geom_col(width = 0.55) +
    geom_text(aes(label = scales::dollar(value, accuracy = 0.01)),
              hjust = -0.15, size = 3.0, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    annotate("text", x = reservation, y = 2.55,
             label = sprintf("Reservation wage: %s", scales::dollar(reservation)),
             hjust = 1.03, vjust = 0, size = 2.7, fontface = "bold",
             color = COL[["eig_purple_800"]],
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    annotate("text", x = reservation / 2, y = 0.42, label = "will not work below this",
             size = 2.5, color = "#777777", fontface = "italic",
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    scale_fill_manual(values = c("offer" = GRAY,
                                 "subsidized" = COL[["eig_green_700"]]),
                      guide = "none") +
    scale_x_continuous(labels = scales::label_dollar(),
                       limits = c(0, 18),
                       expand = expansion(mult = c(0, 0.05))) +
    coord_cartesian(clip = "off") +
    labs(
      title = "Figure 6. How the subsidy clears\na worker's reservation wage.",
      x = "Hourly wage", y = NULL,
      caption = eig_caption(
        note = "Illustrative round numbers, consistent with the $16.80 target."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank(),
          plot.margin = margin(5.5, 12, 5.5, 5.5))

  eig_save_fig(p, "fig06_reservation_wage",
               width = 6.6, height = 3.2, root = ROOT)
}

# ===========================================================================
# FIGURE 13 - Imputed potential wages of the non-employed
# ===========================================================================
fig13_pool_wage_distribution <- function() {
  np_full <- read_parquet(file.path(ROOT, "data", "processed", "nonemployed_pool.parquet")) %>%
    as.data.frame() %>%
    filter(!is.na(mpl), mpl >= 0)

  target <- 16.80
  # Below-target share computed on the full (uncapped) pool.
  below <- sum(np_full$weight[np_full$mpl < target]) / sum(np_full$weight) * 100

  # Density display capped at $45.
  np <- np_full %>% filter(mpl <= 45)

  # Weighted density.
  dens <- density(np$mpl, weights = np$weight / sum(np$weight),
                  from = 0, to = 45, n = 512)
  dd <- data.frame(x = dens$x, y = dens$y)

  p <- ggplot(dd, aes(x = x, y = y)) +
    geom_area(data = filter(dd, x <= target),
              fill = COL[["eig_gold_600"]], alpha = 0.45) +
    geom_line(color = COL[["eig_green_700"]], linewidth = 1.0) +
    geom_vline(xintercept = target, color = COL[["eig_teal_900"]],
               linetype = "solid", linewidth = 0.4) +
    annotate("text", x = target, y = max(dd$y) * 0.96,
             label = "$16.80 target", hjust = -0.05, size = 2.8,
             fontface = "bold", color = COL[["eig_teal_900"]],
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    annotate("text", x = 8.4, y = max(dd$y) * 0.45,
             label = sprintf("%.1f%% of the pool\nbelow the target", below),
             size = 2.9, color = COL[["eig_black"]],
             family = tokens$EIG_FONT_BODY_PRIMARY) +
    scale_x_continuous(labels = scales::label_dollar(),
                       expand = expansion(mult = c(0.01, 0.02))) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.06))) +
    labs(
      title = "Figure 8. Imputed potential wages of the non-employed,\nrelative to the target.",
      x = "Imputed potential hourly wage", y = "Weighted density",
      caption = eig_caption(
        note = "Weighted by survey weights; potential wage (mpl) capped at $45 for display."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(axis.text.y = element_blank())

  eig_save_fig(p, "fig08_pool_wage_distribution",
               width = 6.8, height = 3.8, root = ROOT)
}

# ===========================================================================
# FIGURE 14 - Induced entry under potential-wage uncertainty
# ===========================================================================
fig14_mpl_uncertainty <- function() {
  # Re-centered (2026-07-09): the full 27-cell joint decomposition of induced entry —
  #   non-employment wage penalty {0,10,20%} × offer dispersion λ {0.5,0.75,1.0} × participation
  #   elasticity {lower,central,upper} — faceted by elasticity, penalty on the y-axis, λ by color.
  #   The evidence-central (status-differentiated ~10% penalty, λ 0.75, central elasticity = 1.25M)
  #   is the headline; the no-penalty/λ0.75/central cell (0.83M) is the labeled conservative floor.
  gr <- pop("entry_scenario_grid")

  d <- gr %>%
    mutate(
      pen = factor(sprintf("%d%%", round(penalty * 100)),
                   levels = c("0%", "10%", "20%")),
      eps = factor(recode(eps_edge,
                          lower = "Lower elasticity",
                          central = "Central elasticity",
                          upper = "Upper elasticity"),
                   levels = c("Lower elasticity", "Central elasticity", "Upper elasticity")),
      lam = factor(lambda, levels = c(0.5, 0.75, 1.0))
    )
  rng <- sprintf("%.2f–%.2f million", min(gr$induced_M), max(gr$induced_M))

  p <- ggplot(d, aes(x = induced_M, y = pen, color = lam)) +
    geom_point(size = 3.2, position = position_dodge(width = 0.6)) +
    facet_wrap(~ eps, ncol = 1) +
    scale_color_manual(values = c("0.5" = COL[["eig_green_500"]],
                                  "0.75" = COL[["eig_green_700"]],
                                  "1" = COL[["eig_gold_600"]]),
                       name = "Offer dispersion λ") +
    scale_x_continuous(labels = scales::label_number(suffix = "M"),
                       limits = c(0, 3.5),
                       expand = expansion(mult = c(0.02, 0.05))) +
    labs(
      title = "Figure 14. Induced entry across the\nparameter grid.",
      subtitle = "Evidence-central 1.49M; conservative floor 1.02M; high corner 3.81M.",
      x = "Induced entrants (millions)", y = "Non-employment wage penalty",
      caption = eig_caption(
        note = paste0("All 27 combinations of wage penalty, offer dispersion, and participation\n",
                      "elasticity (full range ", rng, "). The evidence-central applies a status-\n",
                      "differentiated ~10% penalty at λ 0.75 and central elasticity; the floor applies\n",
                      "no penalty. Penalty anchored to Schmieder, von Wachter, and Bender (2016).")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank(),
          legend.position = "top",
          strip.text = element_text(face = "bold", hjust = 0,
                                    color = COL[["eig_teal_900"]]))

  eig_save_fig(p, "fig14_mpl_uncertainty",
               width = 6.8, height = 6.2, root = ROOT)
}

# ===========================================================================
# FIGURE 15 - The intensive margin: added hours among part-time incumbents
# ===========================================================================
fig15_hours_margin <- function() {
  hm <- pop("incumbent_hours_margin")

  d <- hm %>%
    mutate(
      eps_lab = sprintf("ε = %.2f (%s)", eps_int,
                        recode(eps_int_edge,
                               lower = "EITC-benchmark floor",
                               central = "central",
                               upper = "upper")),
      bar_lab = sprintf("%.2fM FTE  (+$%.1fB gross)",
                        added_fte_M, added_subsidy_gross_bn),
      eps_lab = reorder(eps_lab, added_fte_M)
    )

  p <- ggplot(d, aes(x = added_fte_M, y = eps_lab)) +
    geom_col(width = 0.62, fill = COL[["eig_green_700"]]) +
    geom_text(aes(label = bar_lab),
              hjust = -0.06, size = 2.8,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_x_continuous(labels = scales::label_number(suffix = "M"),
                       expand = expansion(mult = c(0, 0.45))) +
    labs(
      title = "Figure 15. The intensive margin: added hours\namong part-time incumbents.",
      x = "Added full-time-equivalent workers (millions)", y = NULL,
      caption = eig_caption(
        note = paste0("The 80-80 pays the full per-hour subsidy on every added hour up to 40 hours per week\n",
                      "(no phase-out). ε = 0.05 is the EITC-benchmark floor; 0.20–0.33 reflects consensus\n",
                      "intensive-margin elasticities for clean wage variation (Chetty 2012).")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig15_hours_margin",
               width = 6.6, height = 3.2, root = ROOT)
}

# ===========================================================================
# Driver
# ===========================================================================
cat("Building EIG supporting figure suite (Batch 2)\n")
cat("Repo root:", ROOT, "\n\n")

fig7_entry_band_by_cell()
fig7b_entrants_by_status()
fig8_cost_band()
fig9_subsidy_by_wage()
fig10_firm_capture()
f11 <- fig11_benefit_cliff()
anch <- fig11b_net_income_by_hours()
fig12_reservation_wage()
fig13_pool_wage_distribution()
fig14_mpl_uncertainty()
fig15_hours_margin()

cat("\nFig 11 schedule file used:", f11, "\n")
cat(sprintf("Fig 11b anchors  H=1000: no=$%.0f sub=$%.0f | H=2000: no=$%.0f sub=$%.0f | H=3000: no=$%.0f sub=$%.0f | crossover=%.0f hrs (%.1f hr/wk)\n",
            anch$a1000["no"], anch$a1000["sub"], anch$a2000["no"], anch$a2000["sub"],
            anch$a3000["no"], anch$a3000["sub"], anch$crossover_hours, anch$crossover_hours / 50))
cat("Done.\n")
