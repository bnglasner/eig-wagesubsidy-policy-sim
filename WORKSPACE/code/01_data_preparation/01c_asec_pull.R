# ==============================================================================
# 02a_asec_pull.R
# CPS ASEC (Annual Social and Economic Supplement) — IPUMS API pull
#
# Pulls the most recent available ASEC vintage (targets 2025 covering income
# year 2024; falls back to 2024 covering income year 2023) and saves a single
# person-level parquet for use in the ORG–ASEC statistical matching pipeline.
#
# Modelled on EIG IPUMS Example / WORKSPACE/code/01_data_preparation/01a_cps_pull.R
#
# Variables requested
# -------------------
#   Identifiers    : YEAR SERIAL PERNUM RELATE FAMUNIT
#   Demographics   : AGE SEX RACE HISPAN MARST EDUC NCHILD STATEFIP
#   Employment     : EMPSTAT CLASSWKR PAIDHOUR WKSWORK2 UHRSWORKLY
#   Income         : INCWAGE INCTOT
#   Weights        : ASECWT EARNWT
#
# Output
# ------
#   WORKSPACE/data/external/asec_persons_{YYYY}.parquet
#     One row per person in the ASEC supplement.
#     Downstream: 01d_asec_preprocess.py builds household-level matching records.
#
# Requirements
# ------------
#   ipumsr >= 0.8.0, arrow, dplyr, haven
#   IPUMS_API_KEY in .Renviron  (same key used by EIG IPUMS Example project)
#
# Usage
# -----
#   Rscript WORKSPACE/code/01_data_preparation/02a_asec_pull.R
#   (or set EIG_WAGESUBSIDY_ROOT env var and run from any directory)
# ==============================================================================

library(ipumsr)
library(arrow)
library(dplyr)
library(haven)

# ── Locate project root ───────────────────────────────────────────────────────
# Walks up the directory tree until it finds WORKSPACE/app/app.py.
# Override by setting EIG_WAGESUBSIDY_ROOT env var.

find_project_root <- function(
    start  = getwd(),
    marker = file.path("WORKSPACE", "app", "app.py"),
    max_up = 10L
) {
  cur <- normalizePath(start, winslash = "/", mustWork = FALSE)
  for (i in seq_len(max_up + 1L)) {
    if (file.exists(file.path(cur, marker))) return(cur)
    parent <- normalizePath(file.path(cur, ".."), winslash = "/", mustWork = FALSE)
    if (identical(parent, cur)) break
    cur <- parent
  }
  NA_character_
}

path_project <- Sys.getenv("EIG_WAGESUBSIDY_ROOT", unset = "")
if (!nzchar(path_project)) path_project <- find_project_root()
if (is.na(path_project) || !dir.exists(path_project)) {
  stop(
    "Could not locate wage-subsidy project root.\n",
    "Set EIG_WAGESUBSIDY_ROOT or run from within the repository.",
    call. = FALSE
  )
}
path_project <- normalizePath(path_project, winslash = "/", mustWork = TRUE)

OUTPUT_DIR <- file.path(path_project, "WORKSPACE", "data", "external")
dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

message("Project root : ", path_project)
message("Output dir   : ", OUTPUT_DIR)

# ── Configuration ─────────────────────────────────────────────────────────────
# Target years in preference order.
# 2025 ASEC  = March 2025 supplement, income reference year 2024 (most recent).
# 2024 ASEC  = March 2024 supplement, income reference year 2023 (fallback).
TARGET_YEARS  <- c(2025L, 2024L)
FORCE_REFRESH <- FALSE   # TRUE = re-download even if parquet already exists

# IPUMS CPS ASEC variables.
# See https://cps.ipums.org/cps-action/variables/group for full descriptions.
ASEC_VARS <- c(
  # ── Identifiers ──────────────────────────────────────────────────────────
  "YEAR", "SERIAL", "PERNUM",
  "RELATE",       # relationship to household head (101=head, 201=spouse, 301=child...)
  "FAMUNIT",      # family unit number within household (distinguishes subfamilies)
  # ── Demographics ─────────────────────────────────────────────────────────
  "AGE", "SEX",
  "RACE", "HISPAN",
  "MARST",        # marital status (1=married-spouse present, ..., 6=never married)
  "EDUC",         # educational attainment (IPUMS harmonised codes)
  "NCHILD",       # number of own children in household
  "STATEFIP",     # state FIPS code
  # ── Employment ───────────────────────────────────────────────────────────
  "EMPSTAT",      # employment status
  "CLASSWKR",     # class of worker (21-28 = wage/salary; 13-14 = self-employed)
  "PAIDHOUR",     # paid by the hour (2=yes)
  "WKSWORK2",     # weeks worked last year, grouped (1=1-13 ... 6=50-52)
  "UHRSWORKLY",   # usual hours worked per week last year
  # ── Income ───────────────────────────────────────────────────────────────
  "INCWAGE",      # wage and salary income last year
  "INCTOT",       # total personal income
  # ── Weights ──────────────────────────────────────────────────────────────
  "ASECWT",       # ASEC person weight
  "EARNWT"        # earner supplement weight (for income/earnings analysis)
)

# ── API key ───────────────────────────────────────────────────────────────────
api_key <- Sys.getenv("IPUMS_API_KEY")
if (!nzchar(api_key)) {
  stop(
    "IPUMS_API_KEY not found in environment.\n",
    "Add  IPUMS_API_KEY=<your_key>  to ~/.Renviron and restart R.",
    call. = FALSE
  )
}
set_ipums_api_key(api_key, overwrite = TRUE, save = FALSE)

# ── Resolve most recent available ASEC vintage ────────────────────────────────
message("[SETUP] Fetching CPS sample catalogue from IPUMS API ...")
si <- get_sample_info("cps")

asec_catalogue <- si |>
  filter(grepl("ASEC", description, ignore.case = TRUE)) |>
  mutate(yr = as.integer(sub("^cps(\\d{4}).*", "\\1", name))) |>
  filter(!is.na(yr)) |>
  arrange(desc(yr))

if (nrow(asec_catalogue) == 0L) {
  stop("No ASEC samples found in the IPUMS CPS catalogue. Check your API key and IPUMS access.", call. = FALSE)
}

available_asec_years <- unique(asec_catalogue$yr)
message(
  "  ASEC years in catalogue: ",
  paste(head(available_asec_years, 6), collapse = ", "),
  if (length(available_asec_years) > 6) " ..." else ""
)

asec_year <- NA_integer_
for (y in TARGET_YEARS) {
  if (y %in% available_asec_years) {
    asec_year <- y
    break
  }
}
if (is.na(asec_year)) {
  asec_year <- available_asec_years[1]
  message("  Target years (", paste(TARGET_YEARS, collapse = ", "), ") not found.")
  message("  Falling back to most recent available: ", asec_year)
} else {
  message("  Using ASEC vintage: ", asec_year,
          "  (income reference year: ", asec_year - 1L, ")")
}

asec_sample_id <- asec_catalogue$name[asec_catalogue$yr == asec_year]
if (length(asec_sample_id) == 0L) {
  stop("No sample ID found for ASEC year ", asec_year, call. = FALSE)
}
asec_sample_id <- asec_sample_id[1]   # exactly one ASEC supplement per year
message("  Sample ID  : ", asec_sample_id)

# ── Cache check ───────────────────────────────────────────────────────────────
out_path <- file.path(OUTPUT_DIR, sprintf("asec_persons_%d.parquet", asec_year))

if (file.exists(out_path) && !FORCE_REFRESH) {
  message(
    "[CACHE] ", basename(out_path), " already exists — skipping pull.\n",
    "  Set FORCE_REFRESH <- TRUE to re-download."
  )
  quit(save = "no", status = 0L)
}

# ── Submit and download extract ───────────────────────────────────────────────
message("[PULLING] Submitting IPUMS CPS ASEC extract for ", asec_year, " ...")

extract_def <- define_extract_micro(
  collection     = "cps",
  description    = paste0("CPS ASEC ", asec_year, " -- EIG wage-subsidy matching pipeline"),
  samples        = asec_sample_id,
  variables      = ASEC_VARS,
  data_format    = "fixed_width",
  data_structure = "rectangular"
)

submitted <- submit_extract(extract_def)
message("  Extract submitted (number: ", submitted$number, "). Waiting for IPUMS ...")
completed <- wait_for_extract(submitted)

# Download into a raw subdirectory; keep the DDI .xml for documentation.
dl_dir <- file.path(OUTPUT_DIR, sprintf("asec_%d_raw", asec_year))
dir.create(dl_dir, recursive = TRUE, showWarnings = FALSE)
message("  Downloading to ", dl_dir, " ...")
dl_paths <- download_extract(completed, download_dir = dl_dir)

# ── Read, strip labels, save as parquet ───────────────────────────────────────
message("  Reading and parsing extract ...")
raw_df <- read_ipums_micro(dl_paths) |>
  zap_labels()

message("  Rows read : ", format(nrow(raw_df), big.mark = ","))
message("  Writing parquet: ", out_path)
write_parquet(raw_df, out_path)

message(
  "\n[DONE] ", basename(out_path), "\n",
  "  Rows      : ", format(nrow(raw_df), big.mark = ","), "\n",
  "  Columns   : ", ncol(raw_df), "\n",
  "  ASEC year : ", asec_year, "  (income reference year ", asec_year - 1L, ")\n",
  "\nNext step: python WORKSPACE/code/01_data_preparation/01d_asec_preprocess.py"
)

# Remove .dat.gz; keep .xml DDI codebook for documentation.
gz_files <- list.files(dl_dir, pattern = "\\.dat\\.gz$", full.names = TRUE)
if (length(gz_files) > 0L) {
  file.remove(gz_files)
  message("  Removed ", length(gz_files), " .dat.gz file(s) (parquet retained).")
}
