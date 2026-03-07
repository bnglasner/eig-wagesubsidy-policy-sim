#!/usr/bin/env bash
set -euo pipefail

# Template-friendly behavior:
# - warn (default): report missing artifacts but exit 0
# - fail: report missing artifacts and exit 1
mode="${STAGE_CONTRACT_MODE:-warn}"
if [[ "$mode" != "warn" && "$mode" != "fail" ]]; then
  echo "Invalid STAGE_CONTRACT_MODE: $mode (expected warn|fail)"
  exit 2
fi

# Read project scope tier (env var overrides file value)
# Filter out the template placeholder line (contains '[') to get the set value only
tier_from_file=$(grep -i "Project scope tier" INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md 2>/dev/null \
  | grep -v '\[' | grep -oE '[123]' | head -1)
tier="${EIG_PROJECT_TIER:-${tier_from_file:-3}}"
echo "Project scope tier: $tier"

findings=0
contracts_doc="INFRA/docs/STAGE_OUTPUT_CONTRACTS.md"

ensure_pattern_documented() {
  local pattern="$1"
  if ! grep -Fq "$pattern" "$contracts_doc"; then
    echo "CONTRACT DRIFT: pattern not documented in $contracts_doc -> $pattern"
    findings=$((findings + 1))
  fi
}

check_pattern() {
  local pattern="$1"
  shopt -s nullglob
  local matches=( $pattern )
  shopt -u nullglob
  if [[ "${#matches[@]}" -eq 0 ]]; then
    echo "MISSING ARTIFACT PATTERN: $pattern"
    findings=$((findings + 1))
    return
  fi

  local non_empty=0
  local f
  for f in "${matches[@]}"; do
    if [[ -f "$f" && -s "$f" ]]; then
      non_empty=1
      break
    fi
  done
  if [[ "$non_empty" -eq 0 ]]; then
    echo "EMPTY ARTIFACT(S): $pattern"
    findings=$((findings + 1))
  fi
}

check_non_empty_dir() {
  local d="$1"
  if [[ ! -d "$d" ]]; then
    echo "MISSING DIRECTORY: $d"
    findings=$((findings + 1))
    return
  fi

  if [[ -z "$(find "$d" -mindepth 1 -type f ! -name '.gitkeep' -print -quit)" ]]; then
    echo "NO OUTPUT FILES IN: $d"
    findings=$((findings + 1))
  fi
}

# Stage 01 (all tiers)
ensure_pattern_documented "WORKSPACE/data/processed/analysis_dataset.*"
check_pattern "WORKSPACE/data/processed/analysis_dataset.*"
ensure_pattern_documented "WORKSPACE/output/data/intermediate_results/data_dictionary.*"
check_pattern "WORKSPACE/output/data/intermediate_results/data_dictionary.*"
ensure_pattern_documented "INFRA/quality_reports/data_report.html"
check_pattern "INFRA/quality_reports/data_report.html"

# Stage 02 (all tiers)
ensure_pattern_documented "WORKSPACE/output/tables/main/descriptive_summary.*"
check_pattern "WORKSPACE/output/tables/main/descriptive_summary.*"
ensure_pattern_documented "WORKSPACE/output/data/intermediate_results/descriptive_qc.*"
check_pattern "WORKSPACE/output/data/intermediate_results/descriptive_qc.*"

# Stage 03 (tier 2+)
if [[ "$tier" -ge 2 ]]; then
  ensure_pattern_documented "WORKSPACE/output/tables/main/main_estimates.*"
  check_pattern "WORKSPACE/output/tables/main/main_estimates.*"
  ensure_pattern_documented "WORKSPACE/output/data/intermediate_results/model_diagnostics.*"
  check_pattern "WORKSPACE/output/data/intermediate_results/model_diagnostics.*"
fi

# Stage 04 (tier 3 only)
if [[ "$tier" -ge 3 ]]; then
  ensure_pattern_documented "WORKSPACE/output/tables/appendix/robustness_results.*"
  check_pattern "WORKSPACE/output/tables/appendix/robustness_results.*"
  ensure_pattern_documented "WORKSPACE/output/tables/appendix/heterogeneity_results.*"
  check_pattern "WORKSPACE/output/tables/appendix/heterogeneity_results.*"
fi

# Stage 05 main outputs (all tiers)
ensure_pattern_documented "WORKSPACE/output/figures/main/*"
check_non_empty_dir "WORKSPACE/output/figures/main"
ensure_pattern_documented "WORKSPACE/output/tables/main/*"
check_non_empty_dir "WORKSPACE/output/tables/main"
ensure_pattern_documented "INFRA/quality_reports/output_report.html"
check_pattern "INFRA/quality_reports/output_report.html"

# Stage 05 appendix outputs (tier 3 only)
if [[ "$tier" -ge 3 ]]; then
  ensure_pattern_documented "WORKSPACE/output/figures/appendix/*"
  check_non_empty_dir "WORKSPACE/output/figures/appendix"
  ensure_pattern_documented "WORKSPACE/output/tables/appendix/*"
  check_non_empty_dir "WORKSPACE/output/tables/appendix"
fi

if [[ "$findings" -eq 0 ]]; then
  echo "Stage contract check: PASS"
  exit 0
fi

if [[ "$mode" == "fail" ]]; then
  echo "Stage contract check: FAILED ($findings issue(s))"
  exit 1
fi

echo "Stage contract check: WARN ($findings issue(s))"
exit 0




