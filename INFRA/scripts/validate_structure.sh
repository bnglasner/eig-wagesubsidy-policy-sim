#!/usr/bin/env bash
set -euo pipefail

required_paths=(
  "README.md"
  "WORKSPACE/data/raw/README.md"
  "WORKSPACE/data/processed/README.md"
  "INFRA/CLAUDE.md"
  "INFRA/docs/PROJECT_INTAKE.md"
  "INFRA/docs/START_HERE.md"
  "INFRA/docs/PROCESS_FLOW.md"
  "INFRA/docs/PROJECT_DECISIONS.md"
  "WORKSPACE/README.md"
  "INFRA/docs/AI_START.md"
  "INFRA/docs/TEMPLATE_SCOPE.md"
  "INFRA/docs/AGENT_TASK_ROUTING.md"
  "INFRA/docs/AI_BASELINE_APPLICATION_PLAYBOOK.md"
  "INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md"
  "INFRA/docs/PLATFORM_PARITY_CHECKLIST.md"
  "INFRA/docs/REVIEW_RUBRIC.md"
  "INFRA/docs/DATA_GOVERNANCE_POLICY.md"
  "INFRA/docs/DATA_SOURCES_OUTPUTS_CATALOG.md"
  "INFRA/docs/STAGE_OUTPUT_CONTRACTS.md"
  "INFRA/AGENTS.md"
  "INFRA/AI_AGENT_ROUTING.md"
  "INFRA/scripts/validate_agent_parity.sh"
  "INFRA/scripts/validate_stage_contracts.sh"
  "INFRA/quality_reports/project_tracker.md"
)

missing=0
for p in "${required_paths[@]}"; do
  if [[ ! -e "$p" ]]; then
    echo "MISSING: $p"
    missing=1
  fi
done

# Read project scope tier (env var overrides file value)
# Filter out the template placeholder line (contains '[') to get the set value only
tier_from_file=$(grep -i "Project scope tier" INFRA/docs/PIPELINE_LANGUAGE_PROFILE.md 2>/dev/null \
  | grep -v '\[' | grep -oE '[123]' | head -1)
tier="${EIG_PROJECT_TIER:-${tier_from_file:-3}}"
echo "Project scope tier: $tier"

case "$tier" in
  1) required_stage_dirs=(
       "WORKSPACE/code/01_data_preparation"
       "WORKSPACE/code/02_descriptive_analysis"
       "WORKSPACE/code/05_figures_tables"
     ) ;;
  2) required_stage_dirs=(
       "WORKSPACE/code/01_data_preparation"
       "WORKSPACE/code/02_descriptive_analysis"
       "WORKSPACE/code/03_main_estimation"
       "WORKSPACE/code/05_figures_tables"
     ) ;;
  3) required_stage_dirs=(
       "WORKSPACE/code/01_data_preparation"
       "WORKSPACE/code/02_descriptive_analysis"
       "WORKSPACE/code/03_main_estimation"
       "WORKSPACE/code/04_robustness_heterogeneity"
       "WORKSPACE/code/05_figures_tables"
     ) ;;
  *) echo "Invalid tier: $tier (expected 1, 2, or 3)"; exit 2 ;;
esac

for d in "${required_stage_dirs[@]}"; do
  if [[ ! -d "$d" ]]; then
    echo "MISSING STAGE DIRECTORY: $d"
    missing=1
    continue
  fi

  if [[ ! -f "$d/README.md" ]]; then
    echo "MISSING STAGE README: $d/README.md"
    missing=1
  fi

  if ! find "$d" -maxdepth 1 -type f ! -name "README.md" -print -quit | grep -q .; then
    echo "MISSING STAGE SCRIPT FILE: $d"
    missing=1
  fi
done

placeholder_mode="${PLACEHOLDER_MODE:-warn}"
if [[ "$placeholder_mode" != "warn" && "$placeholder_mode" != "fail" ]]; then
  echo "INVALID PLACEHOLDER_MODE: $placeholder_mode (use warn or fail)"
  exit 2
fi

placeholder_markers=(
  "placeholder"
  "TODO: implement"
)

placeholder_missing=0
for d in "${required_stage_dirs[@]}"; do
  if [[ ! -d "$d" ]]; then
    continue
  fi

  mapfile -t stage_files < <(find "$d" -maxdepth 1 -type f ! -name "README.md")
  if [[ "${#stage_files[@]}" -eq 0 ]]; then
    continue
  fi

  non_placeholder_found=0
  for f in "${stage_files[@]}"; do
    if grep -qiE "placeholder|TODO: implement" "$f"; then
      continue
    fi
    non_placeholder_found=1
    break
  done

  if [[ "$non_placeholder_found" -eq 0 ]]; then
    echo "PLACEHOLDER-ONLY STAGE: $d"
    if [[ "$placeholder_mode" == "fail" ]]; then
      placeholder_missing=1
    fi
  fi
done

if ! find WORKSPACE/code -maxdepth 1 -type f -name "run_all.*" -print -quit | grep -q .; then
  echo "MISSING PIPELINE ENTRYPOINT: WORKSPACE/code/run_all.[ext]"
  missing=1
fi

if find WORKSPACE/code -maxdepth 1 -type f -name "99_run_all.*" -print -quit | grep -q .; then
  echo "INVALID PIPELINE ENTRYPOINT NAME: WORKSPACE/code/99_run_all.[ext] (use WORKSPACE/code/run_all.[ext])"
  missing=1
fi

if [[ "$missing" -eq 1 || "$placeholder_missing" -eq 1 ]]; then
  echo "Baseline structure check: FAILED"
  exit 1
fi

echo "Baseline structure check: PASS"



