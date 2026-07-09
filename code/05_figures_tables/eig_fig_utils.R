# eig_fig_utils.R
# Shared harness for the EIG-styled figure suite (R/ggplot2).
#
# Responsibilities:
#   * Resolve the repo root robustly (works under Rscript or interactive).
#   * Source the canonical EIG theme + tokens (no bespoke styling here).
#   * Register a "Source Serif Pro" alias when only "Source Serif 4" is
#     installed, so the theme's headline font renders headless.
#   * Provide eig_save_fig() -> writes BOTH <slug>.png (300 dpi) and <slug>.svg
#     to output/figures/main/.
#   * Provide the canonical bottom-left source annotation string + helper.
#
# All data are read with arrow::read_parquet in the figure driver.

suppressWarnings(suppressMessages({
  library(ggplot2)
  library(dplyr)
}))

# ---------------------------------------------------------------------------
# Repo-root resolution
# ---------------------------------------------------------------------------
# Marker used to identify the repository root.
.EIG_ROOT_MARKER <- file.path("Infrastructure", "style", "themes", "r", "eig_theme.R")

eig_find_repo_root <- function() {
  candidates <- character(0)

  # 1) Script path, if launched via Rscript (--file=...).
  args <- commandArgs(trailingOnly = FALSE)
  fa <- grep("^--file=", args, value = TRUE)
  if (length(fa) > 0) {
    sp <- normalizePath(sub("^--file=", "", fa[1]), mustWork = FALSE)
    candidates <- c(candidates, dirname(sp))
  }

  # 2) Current working directory.
  candidates <- c(candidates, normalizePath(getwd(), mustWork = FALSE))

  for (start in candidates) {
    d <- start
    for (i in seq_len(10)) {
      if (file.exists(file.path(d, .EIG_ROOT_MARKER))) {
        return(d)
      }
      parent <- dirname(d)
      if (identical(parent, d)) break
      d <- parent
    }
  }
  stop(
    "Could not locate repo root (marker not found: ", .EIG_ROOT_MARKER, ").",
    call. = FALSE
  )
}

# ---------------------------------------------------------------------------
# Font registration
# ---------------------------------------------------------------------------
# The theme requests EIG_FONT_HEADLINE_PRIMARY = "Source Serif Pro". Modern
# installs ship "Source Serif 4" instead. Register an alias so ragg/svglite
# (both of which resolve fonts through systemfonts) find the headline family.
eig_register_fonts <- function(tokens) {
  if (!requireNamespace("systemfonts", quietly = TRUE)) {
    return(invisible(FALSE))
  }
  fams <- unique(systemfonts::system_fonts()$family)
  hp <- tokens$EIG_FONT_HEADLINE_PRIMARY
  if (!(hp %in% fams) && "Source Serif 4" %in% fams) {
    try(
      systemfonts::register_variant(name = hp, family = "Source Serif 4"),
      silent = TRUE
    )
    return(invisible(TRUE))
  }
  invisible(FALSE)
}

# ---------------------------------------------------------------------------
# Setup: source theme + tokens, register fonts, assert (with fallback)
# ---------------------------------------------------------------------------
eig_setup <- function() {
  root <- eig_find_repo_root()
  theme_path <- file.path(root, "Infrastructure", "style", "themes", "r", "eig_theme.R")
  tokens_path <- file.path(root, "Infrastructure", "style", "themes", "r", "eig_tokens.R")

  # Source theme helpers into the global environment so figure functions see them.
  source(theme_path, local = FALSE)
  tokens <- eig_load_tokens(tokens_path)

  eig_register_fonts(tokens)
  eig_assert_fonts(tokens, allow_fallback = TRUE)

  list(root = root, tokens = tokens)
}

# ---------------------------------------------------------------------------
# Canonical source annotation
# ---------------------------------------------------------------------------
EIG_SOURCE_LINE <- "Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026."

# Build a bottom-left caption combining the source line with an optional note.
# Rendered via the theme's plot.caption (hjust = 0, small gray, left-aligned).
eig_caption <- function(source = EIG_SOURCE_LINE, note = NULL) {
  if (is.null(note) || !nzchar(note)) {
    return(source)
  }
  paste0(note, "\n", source)
}

# ---------------------------------------------------------------------------
# Save helper: writes BOTH PNG (300 dpi) and SVG to output/figures/main/
# ---------------------------------------------------------------------------
eig_save_fig <- function(plot, slug,
                         width = 6.5, height = 3.5,
                         root = NULL) {
  if (is.null(root)) root <- eig_find_repo_root()
  outdir <- file.path(root, "output", "figures", "main")
  dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

  png_path <- file.path(outdir, paste0(slug, ".png"))
  svg_path <- file.path(outdir, paste0(slug, ".svg"))

  ggplot2::ggsave(
    filename = png_path, plot = plot,
    width = width, height = height, units = "in",
    dpi = 300, device = ragg::agg_png, bg = "white"
  )
  ggplot2::ggsave(
    filename = svg_path, plot = plot,
    width = width, height = height, units = "in",
    device = svglite::svglite, bg = "white"
  )

  info <- file.info(c(png_path, svg_path))
  cat(sprintf(
    "  wrote %-42s  %5.1f x %-4.1f in  png %6.0f KB  svg %6.0f KB\n",
    slug, width, height,
    info$size[1] / 1024, info$size[2] / 1024
  ))
  invisible(c(png = png_path, svg = svg_path))
}
