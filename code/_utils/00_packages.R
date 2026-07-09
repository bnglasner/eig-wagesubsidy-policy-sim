# 00_packages -- minimal package loader for the internalized CPS ORG ingestion
#
# EIG-VENDOR NOTE: This file is NOT one of the vendored canonical wage-build
# scripts. It is a purpose-built environment shim for THIS repo's internalized
# ORG ingestion stage (code/00_ingest/). The vendored stages 00a/01a/01b source
# it verbatim via source(here::here("code", "_utils", "00_packages.R")). It
# loads ONLY the subset of packages the wage-CONSTRUCTION path needs -- it
# deliberately omits the deflator/figure/summary packages (fredr, readxl,
# jsonlite, rvest, xml2, scales, yaml, zoo) and the weighted_stats.R helpers
# from the canonical EIG-Wage-Figure _utils/00_packages.R, because none of
# 00a/01a/01b use them. See Infrastructure/specs/2026-07-07_org-wage-internalization.md
# (requirement M10: dev/pipeline-only R dependency set).

required_packages_list <- list(
  ipumsr  = "0.8.0",    # define/submit/download extract, DDI parsing, read_ipums_micro (00a, 01a)
  arrow   = "14.0.0",   # parquet read/write for year partitions (01a, 01b)
  dplyr   = "1.1.0",    # if_else, coalesce, group_by/summarise (01a, 01b)
  haven   = "2.5.4",    # zap_labels for IPUMS labelled columns (01a)
  fs      = "1.6.3",    # path handling / directory management (00a, 01a, 01b)
  here    = "1.0.1",    # project-root-relative paths (all)
  tibble  = "3.2.0",    # diagnostic tibbles / manifests (01a, 01b)
  stringr = "1.5.0",    # sample-name / partition parsing (00a, 01a, 01b)
  readr   = "2.1.0",    # write_csv for manifests / diagnostics (01a, 01b)
  ranger  = "0.16.0"    # per-year RF hours-vary imputer (01b)
)

required_packages_chr <- names(required_packages_list)

installed_packages_chr <- rownames(installed.packages())
missing_packages_chr   <- setdiff(required_packages_chr, installed_packages_chr)

if (length(missing_packages_chr) > 0L) {
  stop(
    "Missing required R packages for ORG ingestion: ",
    paste(missing_packages_chr, collapse = ", "),
    ". Install via install.packages() before running code/00_ingest/."
  )
}

for (pkg in required_packages_chr) {
  installed_ver_chr <- as.character(utils::packageVersion(pkg))
  required_ver_chr  <- required_packages_list[[pkg]]
  if (utils::compareVersion(installed_ver_chr, required_ver_chr) < 0L) {
    warning(
      "Package '", pkg, "' version ", installed_ver_chr,
      " is older than the pinned minimum ", required_ver_chr, "."
    )
  }
}

suppressPackageStartupMessages({
  library(ipumsr)
  library(arrow)
  library(dplyr)
  library(haven)
  library(fs)
  library(here)
  library(tibble)
  library(stringr)
  library(readr)
  library(ranger)
})

message("00_packages.R (00_ingest) -- ", length(required_packages_chr),
        " packages checked and loaded.")
