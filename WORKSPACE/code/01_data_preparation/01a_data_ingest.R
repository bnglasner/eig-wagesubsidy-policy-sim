source("WORKSPACE/code/00_setup/00_config.R")

# ============================================================================
# 01a_data_ingest.R -- Data acquisition and raw-to-processed transformation
# ============================================================================
# Replace the TODO block below with project-specific ingest code.
#
# SOURCE-SPECIFIC NA PATTERN:
#   When a variable is unavailable in one source but available in another,
#   assign NA explicitly rather than referencing a missing column. Example:
#
#     cps_data <- raw_cps |>
#       transmute(
#         year        = as.integer(YEAR),
#         birthyr_raw = NA_integer_,   # BIRTHYR not in CPS Basic Monthly
#         age         = as.integer(AGE)
#       )
#
# PER-SOURCE QC PATTERN:
#   When a fallback/derived rate legitimately differs by source, split QC
#   checks by source instead of using a single combined threshold. Example:
#
#     pct_derived_src1 <- mean(df$var_source[df$source == "SRC1"] == "derived")
#     pct_derived_src2 <- mean(df$var_source[df$source == "SRC2"] == "derived")
#     message("  Derived rate -- SRC1: ", round(100 * pct_derived_src1, 1),
#             "% | SRC2: ", round(100 * pct_derived_src2, 1), "%")
#     if (pct_derived_src2 > 0.20) warning("QC WARN: high derived rate in SRC2")
#
# ============================================================================

message("TODO: implement data ingest and raw-to-processed transformations")
