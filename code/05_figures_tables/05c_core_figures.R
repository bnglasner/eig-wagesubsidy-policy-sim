#!/usr/bin/env Rscript
# 05c_core_figures.R
# Batch 1 of the EIG-styled figure suite (R/ggplot2).
#
# Builds:
#   Figure 1 - State choropleth of average annual subsidy      (fig1_avg_subsidy_by_state)
#   Figure 2 - The 80-80 subsidy schedule                      (fig2_subsidy_schedule)
#   Figure 3 - Cost recapture waterfall (gross -> net)         (fig3_cost_waterfall)
#   Figure 4 - Take-up rate by group                           (fig4_takeup_by_group)
#   Figure 5 - Cost per new job (log scale)                    (fig5_cost_per_job)
#   Figure 6 - Single-mother safety-net clawback               (fig6_clawback_net_gain)
#
# Each figure is its own function so Batch 2 can add more to this driver
# (or a sibling file) using the same harness.

suppressWarnings(suppressMessages({
  library(arrow)
  library(dplyr)
  library(ggplot2)
  library(scales)
}))

# --- source the harness (theme + tokens + save_fig) ------------------------
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

DATA_POP <- file.path(ROOT, "output", "data", "intermediate_results", "population")
pop <- function(name) read_parquet(file.path(DATA_POP, paste0(name, ".parquet")))

# ===========================================================================
# FIGURE 1 - State choropleth: average annual subsidy per eligible worker
# ===========================================================================
fig1_choropleth <- function() {
  suppressWarnings(suppressMessages({
    library(sf)
    library(tigris)
  }))
  options(tigris_use_cache = TRUE)

  by_state <- pop("by_state") %>%
    select(state_code, avg_annual_subsidy)

  geo_ok <- tryCatch({
    geo <- tigris::states(cb = TRUE, year = 2022, progress_bar = FALSE)
    TRUE
  }, error = function(e) {
    message("  [fig1] tigris fetch failed: ", conditionMessage(e))
    FALSE
  })

  if (!geo_ok) {
    stop("[fig1] tigris geometry unavailable and no offline fallback triggered here.",
         call. = FALSE)
  }

  # Keep 50 states + DC; drop territories. Inset AK/HI via shift_geometry.
  geo <- geo %>%
    filter(!STUSPS %in% c("PR", "VI", "GU", "MP", "AS")) %>%
    tigris::shift_geometry() %>%
    left_join(by_state, by = c("STUSPS" = "state_code"))

  # DC is a pinpoint; pull its centroid to add a labeled callout instead of
  # dropping it (it is the highest value).
  dc <- geo %>% filter(STUSPS == "DC")
  dc_val <- dc$avg_annual_subsidy[1]
  dc_ctr <- suppressWarnings(sf::st_coordinates(sf::st_centroid(sf::st_geometry(dc))))
  dc_x <- dc_ctr[1, 1]; dc_y <- dc_ctr[1, 2]

  p <- ggplot(geo) +
    geom_sf(aes(fill = avg_annual_subsidy), color = "white", linewidth = 0.15) +
    scale_fill_gradient(
      low = COL[["eig_cream_100"]], high = COL[["eig_gold_600"]],
      name = "Avg. annual\nsubsidy",
      labels = scales::label_dollar(),
      guide = guide_colorbar(barwidth = 0.8, barheight = 6)
    ) +
    # DC callout: point + leader + label
    annotate("point", x = dc_x, y = dc_y, size = 1.6,
             color = COL[["eig_teal_900"]]) +
    annotate("segment",
             x = dc_x, y = dc_y,
             xend = dc_x + 620000, yend = dc_y - 380000,
             color = COL[["eig_teal_900"]], linewidth = 0.3) +
    annotate("text",
             x = dc_x + 640000, y = dc_y - 430000,
             label = sprintf("D.C. — highest, %s", scales::dollar(dc_val)),
             hjust = 0, vjust = 1, size = 2.9,
             family = tokens$EIG_FONT_BODY_PRIMARY,
             color = COL[["eig_teal_900"]]) +
    labs(
      title = "Figure 5. Average annual subsidy per eligible worker by state.",
      caption = eig_caption()
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(
      axis.title = element_blank(),
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      panel.grid = element_blank(),
      legend.position = "right"
    )

  eig_save_fig(p, "fig05_avg_subsidy_by_state",
               width = 6.5, height = 4.6, root = ROOT)
}

# ===========================================================================
# FIGURE 2 - The 80-80 subsidy schedule (computed from the formula)
# ===========================================================================
fig2_subsidy_schedule <- function() {
  target <- 16.80
  base_wage <- 7.25
  match_rate <- 0.80

  take_home <- function(w) w + match_rate * pmax(0, target - w)

  x <- seq(base_wage, 21, by = 0.02)
  df <- data.frame(emp = x, th = take_home(x))

  # Worked points computed fresh at the $16.80 target.
  pts <- data.frame(emp = c(8, 12, 15))
  pts$th <- take_home(pts$emp)
  pts$lab <- sprintf("$%.0f → $%.2f", pts$emp, pts$th)

  p <- ggplot(df, aes(emp)) +
    # subsidy wedge: between 45-degree employer-wage line and take-home
    geom_ribbon(aes(ymin = emp, ymax = th),
                fill = COL[["eig_gold_600"]], alpha = 0.35) +
    # 45-degree line (no subsidy reference)
    geom_line(aes(y = emp), color = COL[["eig_green_500"]],
              linetype = "22", linewidth = 0.5) +
    # take-home schedule
    geom_line(aes(y = th), color = COL[["eig_green_700"]], linewidth = 1.1) +
    # reference lines: base wage and target
    geom_vline(xintercept = target, color = COL[["eig_teal_900"]],
               linetype = "solid", linewidth = 0.3) +
    geom_vline(xintercept = base_wage, color = "#999999",
               linetype = "dotted", linewidth = 0.3) +
    # worked points
    geom_point(data = pts, aes(y = th), size = 2.2,
               color = COL[["eig_green_700"]]) +
    geom_text(data = pts, aes(y = th, label = lab),
              hjust = -0.12, vjust = 1.5, size = 2.7,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    annotate("text", x = target, y = 8.4, label = "$16.80 target",
             hjust = -0.06, size = 2.8, fontface = "bold",
             family = tokens$EIG_FONT_BODY_PRIMARY,
             color = COL[["eig_teal_900"]]) +
    annotate("text", x = base_wage, y = 20.4, label = "$7.25 floor",
             hjust = -0.08, size = 2.6,
             family = tokens$EIG_FONT_BODY_PRIMARY, color = "#666666") +
    annotate("text", x = 10.6, y = 13.1, label = "Subsidy",
             size = 2.9, fontface = "bold",
             family = tokens$EIG_FONT_BODY_PRIMARY,
             color = COL[["eig_gold_600"]]) +
    scale_x_continuous(labels = scales::label_dollar(), expand = expansion(mult = c(0.01, 0.03))) +
    scale_y_continuous(labels = scales::label_dollar()) +
    coord_cartesian(ylim = c(7, 21)) +
    labs(
      title = "Figure 1. How the 80-80 subsidy fills the wage gap.",
      x = "Employer hourly wage",
      y = "Worker take-home hourly wage",
      caption = eig_caption(
        note = "The subsidy pays 80 percent of the gap between the employer wage and the $16.80 target."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10)

  eig_save_fig(p, "fig01_subsidy_schedule",
               width = 6.5, height = 4.0, root = ROOT)
}

# ===========================================================================
# FIGURE 3 - Cost recapture waterfall (gross -> net)
# ===========================================================================
fig3_cost_waterfall <- function() {
  pi <- pop("program_interactions")
  s <- pop("summary")

  val <- function(k) pi$total_delta_mn[pi$key == k] / 1000  # -> $B

  gross <- val("wage_subsidy")
  net_target <- s$net_cost_bn[1]

  # Material components (ordered for the bridge).
  comp <- tibble::tribble(
    ~label,                    ~key,
    "ACA health subsidies",    "aca_ptc",
    "Medicaid / CHIP",         "medicaid_chip",
    "SNAP",                    "snap",
    "Payroll taxes",           "payroll_tax",
    "Other benefits",          "other_benefits",
    "Federal income tax",      "federal_tax",
    "TANF",                    "tanf",
    "State income tax",        "state_tax",
    "EITC",                    "eitc",
    "Child tax credit",        "child_tax_credit"
  ) %>% mutate(value = vapply(key, val, numeric(1)))

  # Collapse near-zero programs into a single bar.
  near_zero_keys <- c("wic", "school_meals", "ssi", "housing", "ccdf", "liheap")
  other_val <- sum(pi$total_delta_mn[pi$key %in% near_zero_keys]) / 1000

  # Reconciliation: authoritative net (72.12B, = sum of by-state net) minus the
  # sum implied by program_interactions. Documented, not faked.
  pi_sum <- gross + sum(comp$value) + other_val
  recon <- net_target - pi_sum

  steps <- bind_rows(
    tibble::tibble(label = "Gross wage-subsidy cost", value = gross, type = "Endpoint"),
    comp %>% transmute(label, value,
                       type = ifelse(value >= 0, "Adds cost", "Recaptured")),
    tibble::tibble(label = "Other (net ~0)", value = other_val, type = "Recaptured"),
    tibble::tibble(label = "Unattributed*", value = recon,
                   type = "Reconciliation"),
    tibble::tibble(label = "Net cost", value = net_target, type = "Endpoint")
  )

  # Compute floating-bar geometry.
  n <- nrow(steps)
  ybot <- numeric(n); ytop <- numeric(n); cum <- 0
  for (i in seq_len(n)) {
    if (steps$label[i] == "Gross wage-subsidy cost") {
      ybot[i] <- 0; ytop[i] <- steps$value[i]; cum <- steps$value[i]
    } else if (steps$label[i] == "Net cost") {
      ybot[i] <- 0; ytop[i] <- steps$value[i]
    } else {
      y0 <- cum; y1 <- cum + steps$value[i]
      ybot[i] <- min(y0, y1); ytop[i] <- max(y0, y1); cum <- y1
    }
  }
  steps <- steps %>% mutate(
    idx = row_number(), ybot = ybot, ytop = ytop,
    lbl = ifelse(type %in% c("Endpoint"),
                 sprintf("$%.1f", value),
                 sprintf("%+.1f", value)),
    lab_y = ytop + 2.2
  )
  steps$label <- factor(steps$label, levels = steps$label)

  fills <- c(
    "Endpoint"       = COL[["eig_green_700"]],
    "Adds cost"      = COL[["eig_gold_600"]],
    "Recaptured"     = COL[["eig_blue_800"]],
    "Reconciliation" = "#B0B0B0"
  )

  # Connector lines: run at the cumulative top of each non-final bar.
  cum_tops <- numeric(n); c2 <- 0
  for (i in seq_len(n)) {
    if (steps$label[i] %in% c("Gross wage-subsidy cost", "Net cost")) {
      c2 <- steps$value[i]
    } else {
      c2 <- c2 + steps$value[i]
    }
    cum_tops[i] <- c2
  }
  connectors <- data.frame(
    x = steps$idx[-n] + 0.4,
    xend = steps$idx[-1] - 0.4,
    y = cum_tops[-n]
  )

  p <- ggplot(steps) +
    geom_segment(data = connectors,
                 aes(x = x, xend = xend, y = y, yend = y),
                 color = "#BBBBBB", linewidth = 0.3, linetype = "22") +
    geom_rect(aes(xmin = idx - 0.4, xmax = idx + 0.4,
                  ymin = ybot, ymax = ytop, fill = type)) +
    geom_text(aes(x = idx, y = lab_y, label = lbl),
              size = 2.5, family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_fill_manual(values = fills, name = NULL,
                      breaks = c("Endpoint", "Adds cost", "Recaptured", "Reconciliation")) +
    scale_x_continuous(breaks = steps$idx, labels = levels(steps$label),
                       expand = expansion(mult = c(0.02, 0.02))) +
    scale_y_continuous(labels = scales::label_dollar(suffix = "B"),
                       expand = expansion(mult = c(0, 0.08))) +
    labs(
      title = "Figure 2. From gross to net: taxes and safety-net offsets.",
      x = NULL, y = "Program cost",
      caption = eig_caption(
        note = "*Unattributed reconciles program-level offsets to the state-summed net cost. Values in billions of dollars."
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1, size = 7.5),
      legend.position = "top"
    )

  eig_save_fig(p, "fig02_cost_waterfall",
               width = 7.6, height = 4.8, root = ROOT)

  invisible(list(pi_sum = pi_sum, net = net_target, recon = recon))
}

# ===========================================================================
# FIGURE 4 - Take-up rate by group (small multiples)
# ===========================================================================
fig4_takeup_by_group <- function() {
  overall <- 15.5
  tug <- pop("take_up_by_group")

  highlight <- c("16-24", "Less than HS", "Graduate degree")
  d <- tug %>%
    mutate(
      dimension = factor(dimension,
                         levels = c("Sex", "Age", "Education",
                                    "Race and ethnicity", "Family type")),
      hl = ifelse(group %in% highlight, "Notable", "Other"),
      group = reorder(group, take_up_pct)
    )

  p <- ggplot(d, aes(x = take_up_pct, y = group, fill = hl)) +
    geom_vline(xintercept = overall, color = COL[["eig_teal_900"]],
               linetype = "dashed", linewidth = 0.4) +
    geom_col(width = 0.72) +
    geom_text(aes(label = sprintf("%.1f%%", take_up_pct)),
              hjust = -0.15, size = 2.4,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_fill_manual(values = c("Notable" = COL[["eig_gold_600"]],
                                 "Other" = COL[["eig_green_700"]]),
                      guide = "none") +
    scale_x_continuous(labels = scales::label_percent(scale = 1),
                       expand = expansion(mult = c(0, 0.18))) +
    facet_wrap(~ dimension, scales = "free_y", ncol = 2) +
    labs(
      title = "Figure 3. Share of each group's hourly workers who qualify.",
      x = "Take-up rate", y = NULL,
      caption = eig_caption(
        note = paste0("Dashed line: overall take-up (15.5%). Denominator is the ",
                      "wage-observed hourly workforce (134.3M).")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(
      panel.grid.major.y = element_blank(),
      strip.text = element_text(face = "bold", hjust = 0,
                                color = COL[["eig_teal_900"]]),
      axis.text.y = element_text(size = 7.5),
      panel.spacing.x = unit(1.1, "lines")
    )

  eig_save_fig(p, "fig03_takeup_by_group",
               width = 7.2, height = 6.4, root = ROOT)
}

# ===========================================================================
# FIGURE 5 - Cost per new job (log scale)
# ===========================================================================
fig5_cost_per_job <- function() {
  # Re-centered 2026-07-09 (paid-hourly eligibility; evidence-central headline):
  #   marginal    = gross subsidy paid per entrant-year at the evidence-central
  #                 (entrant gross $7.8B / 1.49M entrants ~ $5,266; PI-3: the rank
  #                 hours mapping; an independent draw ~doubles it — see caption).
  #   fully loaded = total net cost ($47.9B, structural) / induced entrants, as a range:
  #                 conservative floor (1.02M) ~ $47,000; evidence-central (1.49M)
  #                 ~ $32,100; high joint corner (3.81M) ~ $12,600.
  #                 The whole range sits BELOW the state & local incentive band
  #                 ($106K-$196K). Alternatives unchanged.
  marginal <- 5266
  full_lo <- 12572    # high joint corner (3.81M)
  full_hi <- 46961    # conservative floor (1.02M)
  full_mid <- 32148   # evidence-central (1.49M)

  d <- tibble::tribble(
    ~policy,                                        ~value,   ~lo,     ~hi,     ~grp,
    "80-80 subsidy (marginal, per entrant)",         marginal, NA,      NA,      "eig_marginal",
    "80-80 subsidy (fully loaded)",                  NA,       full_lo, full_hi, "eig_full",
    "State & local incentives",                     106000,   106000,  196000,  "other",
    "Buy American provisions",                      154000,   NA,      NA,      "other",
    "Steel tariffs",                                900000,   NA,      NA,      "other"
  )
  # Dot plot on log scale (a bar to zero is undefined on log axes).
  d <- d %>% mutate(order_val = ifelse(is.na(value), lo, value),
                    policy = reorder(policy, order_val))

  dollar_k <- scales::label_dollar(scale_cut = scales::cut_short_scale())

  d <- d %>% mutate(
    lab = case_when(
      grp == "eig_marginal" ~ sprintf("$%.1fK", value / 1000),
      policy == "Buy American provisions" ~ paste0(dollar_k(value), "+"),
      !is.na(lo) & !is.na(value) ~ sprintf("%s–%s", dollar_k(lo), dollar_k(hi)),
      !is.na(value) ~ dollar_k(value),
      TRUE ~ NA_character_
    ),
    lab_x = ifelse(!is.na(hi), hi, value)
  )

  # Fully-loaded endpoints get their own variant labels.
  full_row <- filter(d, grp == "eig_full")
  full_pts <- tibble::tibble(
    policy = full_row$policy[c(1, 1, 1)],
    x = c(full_lo, full_mid, full_hi),
    lab = c(sprintf("%s\nhigh scenario", dollar_k(full_lo)),
            sprintf("%s evidence-central", dollar_k(full_mid)),
            sprintf("%s\nfloor", dollar_k(full_hi))),
    hj = c(1.1, 0.5, -0.1),
    vj = c(1.4, -1.1, 1.4)
  )

  fills <- c("eig_marginal" = COL[["eig_green_700"]],
             "eig_full" = COL[["eig_gold_600"]],
             "other" = "#9AA0A6")

  p <- ggplot(d, aes(y = policy, color = grp)) +
    # ranges: fully-loaded 80-80 and state/local
    geom_segment(data = filter(d, !is.na(lo)),
                 aes(x = lo, xend = hi, y = policy, yend = policy),
                 linewidth = 1.4) +
    geom_point(data = filter(d, !is.na(value)), aes(x = value), size = 3.4) +
    geom_point(data = full_pts, aes(x = x, y = policy), size = 3.4,
               color = COL[["eig_gold_600"]]) +
    geom_text(data = filter(d, !is.na(lab)),
              aes(x = lab_x, label = lab), hjust = -0.18, size = 2.6,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    geom_text(data = full_pts, aes(x = x, y = policy, label = lab, hjust = hj, vjust = vj),
              size = 2.5, lineheight = 0.95,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_color_manual(values = fills, guide = "none") +
    # Pin the row order to the reorder() levels: all layers override `data`,
    # so the discrete scale otherwise trains in layer-appearance order and
    # silently ignores the ascending-cost ordering.
    scale_y_discrete(limits = levels(d$policy)) +
    scale_x_log10(labels = dollar_k,
                  breaks = c(1e3, 1e4, 1e5, 1e6),
                  limits = c(2e3, 3e6),
                  expand = expansion(mult = c(0.02, 0.02))) +
    labs(
      title = "Figure 10. Cost per job: the 80-80 subsidy\nversus other job-creation policies.",
      x = "Cost per job (log scale)", y = NULL,
      caption = eig_caption(
        note = paste0("Fully loaded = total net cost / induced entrants (floor / evidence-central / high). Marginal is\n",
                      "the gross subsidy per entrant-year (an independent hours mapping roughly doubles it).\n",
                      "Alternatives cited in EIG's first Agglomerations post (NBER; AEA; Peterson Institute).")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig10_cost_per_job",
               width = 7.0, height = 4.1, root = ROOT)
}

# ===========================================================================
# FIGURE 6 - Single-mother safety-net clawback
# ===========================================================================
fig6_clawback_net_gain <- function() {
  # Read the evidence-central pool (status-differentiated ~10% penalty) so the clawback matches
  # the published headline entry; falls back to the canonical floor pool if it is absent.
  evc <- file.path(ROOT, "data", "processed", "nonemployed_pool_evidence_central.parquet")
  np <- read_parquet(if (file.exists(evc)) evc else
                     file.path(ROOT, "data", "processed", "nonemployed_pool.parquet"))

  wmed <- function(x, w) {
    o <- order(x); x <- x[o]; w <- w[o]
    cw <- cumsum(w) / sum(w)
    x[which(cw >= 0.5)[1]]
  }

  d <- np %>%
    filter(g_net > 0) %>%
    group_by(cell) %>%
    summarise(med = wmed(g_net, weight), .groups = "drop") %>%
    mutate(
      pct = med * 100,
      label = recode(cell,
                     single_mothers = "Single mothers",
                     other_women = "Other women",
                     men = "Men"),
      hl = ifelse(cell == "single_mothers", "Single mothers", "Comparison"),
      label = reorder(label, pct)
    )

  fills <- c("Single mothers" = COL[["eig_purple_800"]],
             "Comparison" = "#9AA0A6")

  p <- ggplot(d, aes(x = pct, y = label, fill = hl)) +
    geom_col(width = 0.62) +
    geom_text(aes(label = sprintf("%.1f%%", pct)),
              hjust = -0.15, size = 3.0,
              family = tokens$EIG_FONT_BODY_PRIMARY,
              color = COL[["eig_black"]]) +
    scale_fill_manual(values = fills, guide = "none") +
    scale_x_continuous(labels = scales::label_percent(scale = 1),
                       expand = expansion(mult = c(0, 0.16))) +
    labs(
      title = "Figure 12. The safety-net clawback:\nmedian net gain from working, by group.",
      x = "Median net gain in the return to work", y = NULL,
      caption = eig_caption(
        note = paste0("Net gain reflects taxes and means-tested phase-outs, assuming the ",
                      "subsidy counts toward benefit eligibility. Reachable workers only.")
      )
    ) +
    eig_theme_ggplot(tokens = tokens, base_size = 10) +
    theme(panel.grid.major.y = element_blank())

  eig_save_fig(p, "fig12_clawback_net_gain",
               width = 6.5, height = 3.5, root = ROOT)
}

# ===========================================================================
# Driver
# ===========================================================================
cat("Building EIG core figure suite (Batch 1)\n")
cat("Repo root:", ROOT, "\n\n")

fig1_choropleth()
fig2_subsidy_schedule()
wf <- fig3_cost_waterfall()
fig4_takeup_by_group()
fig5_cost_per_job()
fig6_clawback_net_gain()

cat(sprintf(
  "\nWaterfall reconciliation: program_interactions sum = $%.2fB, net target = $%.2fB, unattributed bar = %+.2fB\n",
  wf$pi_sum, wf$net, wf$recon
))
cat("Done.\n")
