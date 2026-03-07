#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

RSCRIPT_BIN="$(command -v Rscript || true)"
if [[ -z "$RSCRIPT_BIN" ]]; then
  for candidate in \
    "/c/Program Files/R/R-4.4.3/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.4.2/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.4.1/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.4.0/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.3.3/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.3.2/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.3.1/bin/Rscript.exe" \
    "/c/Program Files/R/R-4.3.0/bin/Rscript.exe"; do
    if [[ -x "$candidate" ]]; then
      RSCRIPT_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$RSCRIPT_BIN" ]]; then
  for candidate in \
    "/mnt/c/Program Files/R/R-4.4.3/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.4.2/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.4.1/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.4.0/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.3.3/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.3.2/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.3.1/bin/Rscript.exe" \
    "/mnt/c/Program Files/R/R-4.3.0/bin/Rscript.exe"; do
    if [[ -x "$candidate" ]]; then
      RSCRIPT_BIN="$candidate"
      break
    fi
  done
fi

if [[ -z "$RSCRIPT_BIN" ]]; then
  ps_path=""
  PS_EXE="$(command -v powershell.exe || true)"
  if [[ -z "$PS_EXE" && -x "/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe" ]]; then
    PS_EXE="/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
  fi
  if [[ -n "$PS_EXE" ]]; then
    ps_path="$("$PS_EXE" -NoProfile -Command '$p="C:\Program Files\R"; if (Test-Path $p) { Get-ChildItem -Recurse -Filter Rscript.exe -Path $p -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName }' 2>/dev/null || true)"
  fi
  ps_path="$(echo "$ps_path" | tr -d '\r')"
  if [[ -n "$ps_path" ]]; then
    RSCRIPT_BIN="$ps_path"
  fi
fi

if [[ "$RSCRIPT_BIN" == *":\\"* ]]; then
  if command -v cygpath >/dev/null 2>&1; then
    RSCRIPT_BIN="$(cygpath -u "$RSCRIPT_BIN")"
  fi
fi

if [[ -z "$RSCRIPT_BIN" ]]; then
  echo "Rscript not found in PATH or standard Windows install locations."
  exit 1
fi

if [[ -d "/mnt/c/Users/Research/AppData/Local/Temp" ]]; then
  tmp_root="$(mktemp -d -p /mnt/c/Users/Research/AppData/Local/Temp eig_smoke_XXXXXX)"
else
  tmp_root="$(mktemp -d 2>/dev/null || mktemp -d -t eig_smoke)"
fi
cleanup() {
  rm -rf "$tmp_root"
}
trap cleanup EXIT

cp -R "$ROOT_DIR" "$tmp_root/repo"
rm -rf "$tmp_root/repo/.git"

repo="$tmp_root/repo"
export EIG_PROJECT_ROOT="$repo"

cat > "$repo/WORKSPACE/code/01_data_preparation/01a_data_ingest.R" <<'EOF'
source("WORKSPACE/code/00_setup/00_config.R")

data("mtcars")
analysis_dataset <- mtcars
saveRDS(analysis_dataset, file = file.path(path_data_processed, "analysis_dataset.rds"))

data_dictionary <- data.frame(
  variable = names(analysis_dataset),
  class = sapply(analysis_dataset, class),
  stringsAsFactors = FALSE
)
write.csv(
  data_dictionary,
  file = file.path(path_output_intermediate, "data_dictionary.csv"),
  row.names = FALSE
)
EOF

cat > "$repo/WORKSPACE/code/02_descriptive_analysis/02a_descriptive_stats.R" <<'EOF'
source("WORKSPACE/code/00_setup/00_config.R")

analysis_dataset <- readRDS(file.path(path_data_processed, "analysis_dataset.rds"))

summary_tbl <- data.frame(
  variable = names(analysis_dataset),
  mean = sapply(analysis_dataset, mean),
  sd = sapply(analysis_dataset, sd),
  stringsAsFactors = FALSE
)
write.csv(
  summary_tbl,
  file = file.path(path_output_tbl_main, "descriptive_summary.csv"),
  row.names = FALSE
)

qc <- data.frame(
  n_rows = nrow(analysis_dataset),
  n_cols = ncol(analysis_dataset),
  stringsAsFactors = FALSE
)
write.csv(
  qc,
  file = file.path(path_output_intermediate, "descriptive_qc.csv"),
  row.names = FALSE
)
EOF

cat > "$repo/WORKSPACE/code/03_main_estimation/03a_main_model.R" <<'EOF'
source("WORKSPACE/code/00_setup/00_config.R")

analysis_dataset <- readRDS(file.path(path_data_processed, "analysis_dataset.rds"))
fit <- lm(mpg ~ wt + hp, data = analysis_dataset)

coef_tbl <- data.frame(
  term = names(coef(fit)),
  estimate = as.numeric(coef(fit)),
  stringsAsFactors = FALSE
)
write.csv(
  coef_tbl,
  file = file.path(path_output_tbl_main, "main_estimates.csv"),
  row.names = FALSE
)

diag_tbl <- data.frame(
  r_squared = summary(fit)$r.squared,
  adj_r_squared = summary(fit)$adj.r.squared,
  stringsAsFactors = FALSE
)
write.csv(
  diag_tbl,
  file = file.path(path_output_intermediate, "model_diagnostics.csv"),
  row.names = FALSE
)
EOF

cat > "$repo/WORKSPACE/code/04_robustness_heterogeneity/04a_robustness_checks.R" <<'EOF'
source("WORKSPACE/code/00_setup/00_config.R")

analysis_dataset <- readRDS(file.path(path_data_processed, "analysis_dataset.rds"))

robust_tbl <- data.frame(
  spec = "mpg ~ wt",
  estimate = coef(lm(mpg ~ wt, data = analysis_dataset))[2],
  stringsAsFactors = FALSE
)
write.csv(
  robust_tbl,
  file = file.path(path_output_tbl_appendix, "robustness_results.csv"),
  row.names = FALSE
)

het_tbl <- aggregate(mpg ~ cyl, data = analysis_dataset, FUN = mean)
write.csv(
  het_tbl,
  file = file.path(path_output_tbl_appendix, "heterogeneity_results.csv"),
  row.names = FALSE
)
EOF

cat > "$repo/WORKSPACE/code/05_figures_tables/05a_main_outputs.R" <<'EOF'
source("WORKSPACE/code/00_setup/00_config.R")

analysis_dataset <- readRDS(file.path(path_data_processed, "analysis_dataset.rds"))

png(file.path(path_output_fig_main, "scatter_mpg_wt.png"), width = 800, height = 500)
plot(analysis_dataset$wt, analysis_dataset$mpg, xlab = "Weight", ylab = "MPG")
dev.off()

png(file.path(path_output_fig_appendix, "scatter_mpg_hp.png"), width = 800, height = 500)
plot(analysis_dataset$hp, analysis_dataset$mpg, xlab = "Horsepower", ylab = "MPG")
dev.off()

summary_tbl <- data.frame(
  variable = names(analysis_dataset),
  mean = sapply(analysis_dataset, mean),
  sd = sapply(analysis_dataset, sd),
  stringsAsFactors = FALSE
)
write.csv(
  summary_tbl,
  file = file.path(path_output_tbl_main, "descriptive_summary.csv"),
  row.names = FALSE
)
EOF

cat > "$repo/INFRA/quality_reports/data_report.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Smoke Test Data Report</title></head>
  <body><h1>Smoke Test Data Report</h1></body>
</html>
EOF

cat > "$repo/INFRA/quality_reports/output_report.html" <<'EOF'
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Smoke Test Output Report</title></head>
  <body><h1>Smoke Test Output Report</h1></body>
</html>
EOF

cd "$repo"
"$RSCRIPT_BIN" WORKSPACE/code/run_all.R

PLACEHOLDER_MODE=fail bash INFRA/scripts/validate_structure.sh
STAGE_CONTRACT_MODE=fail bash INFRA/scripts/validate_stage_contracts.sh
bash INFRA/scripts/validate_agent_parity.sh

echo "Smoke test: PASS"
