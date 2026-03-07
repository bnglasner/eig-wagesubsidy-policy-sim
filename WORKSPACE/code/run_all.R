# run_all.R -- baseline pipeline orchestrator
# Canonical name: WORKSPACE/code/run_all.R

local({
  root <- Sys.getenv("EIG_PROJECT_ROOT", unset = "")

  if (!nzchar(root)) {
    args <- commandArgs(trailingOnly = FALSE)
    file_arg <- grep("^--file=", args, value = TRUE)
    if (length(file_arg) > 0L) {
      script_path <- normalizePath(sub("^--file=", "", file_arg[1]), winslash = "/")
      root <- dirname(dirname(dirname(script_path)))
    }
  }

  if (!nzchar(root)) {
    cur <- normalizePath(getwd(), winslash = "/", mustWork = FALSE)
    for (i in seq_len(10L)) {
      if (file.exists(file.path(cur, "WORKSPACE", "code", "run_all.R"))) {
        root <- cur
        break
      }
      parent <- normalizePath(file.path(cur, ".."), winslash = "/", mustWork = FALSE)
      if (identical(parent, cur)) break
      cur <- parent
    }
  }

  if (nzchar(root) && dir.exists(root)) {
    setwd(root)
    message("Project root: ", root)
  } else {
    stop("Could not find project root. Set EIG_PROJECT_ROOT or setwd() to repo root.", call. = FALSE)
  }
})

source("WORKSPACE/code/00_setup/00_config.R")

tier_stages <- list(
  "1" = c("01", "02", "05"),
  "2" = c("01", "02", "03", "05"),
  "3" = c("01", "02", "03", "04", "05")
)

tier_key <- as.character(cfg$project_scope_tier)
if (!tier_key %in% names(tier_stages)) {
  stop("Invalid project_scope_tier in cfg: ", tier_key, " (expected 1, 2, or 3)", call. = FALSE)
}
active_stages <- tier_stages[[tier_key]]

# ============================================================================
# Readable Pipeline Flags (one component per line)
# ============================================================================
# Stage flags
RUN_STAGE_01_DATA_PREPARATION     <- TRUE
RUN_STAGE_02_DESCRIPTIVE_ANALYSIS <- TRUE
RUN_STAGE_03_MAIN_ESTIMATION      <- TRUE
RUN_STAGE_04_ROBUSTNESS           <- TRUE
RUN_STAGE_05_FIGURES_TABLES       <- TRUE

# Script flags
RUN_01A_DATA_INGEST       <- TRUE
RUN_02A_DESCRIPTIVE_STATS <- TRUE
RUN_03A_MAIN_MODEL        <- TRUE
RUN_04A_ROBUSTNESS_CHECKS <- TRUE
RUN_05A_MAIN_FIGURES      <- TRUE

# Behavior flags
STOP_ON_ERROR_ANY_STAGE <- FALSE
FAIL_HARD_STAGES        <- c("01", "02", "03")

# Apply tier constraints to stage flags
if (!("01" %in% active_stages)) RUN_STAGE_01_DATA_PREPARATION     <- FALSE
if (!("02" %in% active_stages)) RUN_STAGE_02_DESCRIPTIVE_ANALYSIS <- FALSE
if (!("03" %in% active_stages)) RUN_STAGE_03_MAIN_ESTIMATION      <- FALSE
if (!("04" %in% active_stages)) RUN_STAGE_04_ROBUSTNESS           <- FALSE
if (!("05" %in% active_stages)) RUN_STAGE_05_FIGURES_TABLES       <- FALSE

message("Active pipeline tier: ", tier_key, " (stages: ", paste(active_stages, collapse = ", "), ")")
message("Stage flags:")
for (.nm in sort(ls(pattern = "^RUN_STAGE_"))) message("  ", .nm, " = ", get(.nm))
message("Script flags:")
for (.nm in sort(ls(pattern = "^RUN_[0-9]"))) message("  ", .nm, " = ", get(.nm))
rm(.nm)

execution_log <- data.frame(
  script_id = character(),
  stage = character(),
  label = character(),
  path = character(),
  status = character(),
  start_time = character(),
  end_time = character(),
  elapsed_seconds = numeric(),
  error_msg = character(),
  stringsAsFactors = FALSE
)

record_log <- function(script_id, stage, label, path, status, t0, t1, err) {
  elapsed <- if (is.na(t0) || is.na(t1)) 0 else as.numeric(difftime(t1, t0, units = "secs"))
  execution_log[nrow(execution_log) + 1, ] <<- list(
    script_id = script_id,
    stage = stage,
    label = label,
    path = path,
    status = status,
    start_time = if (is.na(t0)) "" else as.character(t0),
    end_time = if (is.na(t1)) "" else as.character(t1),
    elapsed_seconds = round(elapsed, 1),
    error_msg = err
  )
}

run_script <- function(script_id, stage, script_path, label, run_stage_flag, run_script_flag) {
  if (!isTRUE(run_stage_flag)) {
    message("[SKIP STAGE] ", script_id, " (stage ", stage, " disabled)")
    record_log(script_id, stage, label, script_path, "SKIPPED_STAGE", NA, NA, "")
    return(invisible(NULL))
  }

  if (!isTRUE(run_script_flag)) {
    message("[SKIP FLAG] ", script_id, " (script flag disabled)")
    record_log(script_id, stage, label, script_path, "SKIPPED_FLAG", NA, NA, "")
    return(invisible(NULL))
  }

  message("Running ", script_id, " | ", label, " | ", script_path)
  t0 <- Sys.time()
  status <- tryCatch({
    source(script_path, local = new.env(parent = globalenv()))
    "SUCCESS"
  }, error = function(e) {
    paste0("FAILED: ", conditionMessage(e))
  })
  t1 <- Sys.time()

  if (identical(status, "SUCCESS")) {
    record_log(script_id, stage, label, script_path, "SUCCESS", t0, t1, "")
    message("Completed ", script_id, " in ",
            round(as.numeric(difftime(t1, t0, units = "secs")), 1), "s")
    return(invisible(NULL))
  }

  err <- sub("^FAILED: ", "", status)
  record_log(script_id, stage, label, script_path, "FAILED", t0, t1, err)
  message(status)

  if (isTRUE(STOP_ON_ERROR_ANY_STAGE) || stage %in% FAIL_HARD_STAGES) {
    stop("Pipeline halted at ", script_id, ": ", err, call. = FALSE)
  }

  invisible(NULL)
}

pipeline_start <- Sys.time()

run_script(
  script_id = "01a",
  stage = "01",
  script_path = "WORKSPACE/code/01_data_preparation/01a_data_ingest.R",
  label = "Data ingest",
  run_stage_flag = RUN_STAGE_01_DATA_PREPARATION,
  run_script_flag = RUN_01A_DATA_INGEST
)

run_script(
  script_id = "02a",
  stage = "02",
  script_path = "WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.R",
  label = "Descriptive stats",
  run_stage_flag = RUN_STAGE_02_DESCRIPTIVE_ANALYSIS,
  run_script_flag = RUN_02A_DESCRIPTIVE_STATS
)

run_script(
  script_id = "03a",
  stage = "03",
  script_path = "WORKSPACE/code/03_main_estimation/03a_main_model.R",
  label = "Main model",
  run_stage_flag = RUN_STAGE_03_MAIN_ESTIMATION,
  run_script_flag = RUN_03A_MAIN_MODEL
)

run_script(
  script_id = "04a",
  stage = "04",
  script_path = "WORKSPACE/code/04_robustness_heterogeneity/04a_robustness_checks.R",
  label = "Robustness checks",
  run_stage_flag = RUN_STAGE_04_ROBUSTNESS,
  run_script_flag = RUN_04A_ROBUSTNESS_CHECKS
)

run_script(
  script_id = "05a",
  stage = "05",
  script_path = "WORKSPACE/code/05_figures_tables/05a_main_figures.R",
  label = "Main figures",
  run_stage_flag = RUN_STAGE_05_FIGURES_TABLES,
  run_script_flag = RUN_05A_MAIN_FIGURES
)

pipeline_end <- Sys.time()
n_success <- sum(execution_log$status == "SUCCESS")
n_failed <- sum(execution_log$status == "FAILED")
n_skipped <- sum(execution_log$status %in% c("SKIPPED_STAGE", "SKIPPED_FLAG"))

message("Pipeline complete")
message("  Success: ", n_success)
message("  Failed:  ", n_failed)
message("  Skipped: ", n_skipped)
message("  Elapsed: ", round(as.numeric(difftime(pipeline_end, pipeline_start, units = "secs")), 1), "s")

for (i in seq_len(nrow(execution_log))) {
  row <- execution_log[i, ]
  message("  ", row$script_id, " -> ", row$status, " (", row$elapsed_seconds, "s)")
}



