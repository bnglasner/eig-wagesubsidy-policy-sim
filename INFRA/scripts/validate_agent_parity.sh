#!/usr/bin/env bash
set -euo pipefail

# Run from INFRA/ regardless of call location
cd "$(dirname "$0")/.."

missing=0

required_files=(
  "AGENTS.md"
  "AI_AGENT_ROUTING.md"
  ".codex/playbooks/project-bootstrap.md"
  ".codex/agents/eig-style-guide-agent.md"
  ".claude/agents/eig-style-guide-agent.md"
  "docs/PLATFORM_PARITY_CHECKLIST.md"
)

for p in "${required_files[@]}"; do
  if [[ ! -e "$p" ]]; then
    echo "MISSING: $p"
    missing=1
  fi
done

# Bootstrap skill (invokable from root .claude/skills/)
if [[ ! -e "../.claude/skills/eig-project-bootstrap/SKILL.md" ]]; then
  echo "MISSING: .claude/skills/eig-project-bootstrap/SKILL.md"
  missing=1
fi

# Root-level style skills — parity check between .claude/skills/ and .codex/skills/
root_style_skills=(
  "eig-style-apply"
  "eig-style-review"
  "eig-style-datawrapper"
)
for skill in "${root_style_skills[@]}"; do
  if [[ ! -e "../.claude/skills/${skill}/SKILL.md" ]]; then
    echo "MISSING: .claude/skills/${skill}/SKILL.md"
    missing=1
  fi
  if [[ ! -e "../.codex/skills/${skill}/SKILL.md" ]]; then
    echo "MISSING: .codex/skills/${skill}/SKILL.md"
    missing=1
  fi
done

if [[ "$missing" -eq 1 ]]; then
  echo "Agent parity check: FAILED (missing required files)"
  exit 1
fi

step_ids=(WF1 WF2 WF3 WF4 WF5 WF6)
for wf in "${step_ids[@]}"; do
  if ! grep -q "$wf" AGENTS.md; then
    echo "MISSING WORKFLOW ID IN AGENTS.md: $wf"
    missing=1
  fi
  if ! grep -q "$wf" ".codex/playbooks/project-bootstrap.md"; then
    echo "MISSING WORKFLOW ID IN .codex/playbooks/project-bootstrap.md: $wf"
    missing=1
  fi
  if ! grep -q "$wf" "../.claude/skills/eig-project-bootstrap/SKILL.md"; then
    echo "MISSING WORKFLOW ID IN .claude/skills/eig-project-bootstrap/SKILL.md: $wf"
    missing=1
  fi
done

check_pattern() {
  local file="$1"
  local label="$2"
  local pattern="$3"
  if ! grep -qi "$pattern" "$file"; then
    echo "MISSING SEMANTIC CHECK IN $file ($label): $pattern"
    missing=1
  fi
}

warn_count=0
warn_pattern() {
  local file="$1"
  local label="$2"
  local pattern="$3"
  if ! grep -qi "$pattern" "$file"; then
    echo "WARN: FALLBACK REGEX NOT MATCHED IN $file ($label): $pattern"
    warn_count=$((warn_count + 1))
  fi
}

# Token-first semantic checks (v2 strict)
parity_tokens=(
  "PARITY:WF1:INTAKE_READ"
  "PARITY:WF2:MISSING_REQUIRED_ASK_AND_PAUSE"
  "PARITY:WF2:MAX5_CONTEXTUAL_FOLLOWUPS"
  "PARITY:WF3:DECISIONS_LOGGED"
  "PARITY:WF4:STRUCTURE_CUSTOMIZED"
  "PARITY:WF5:PLACEHOLDERS_UPDATED"
  "PARITY:WF5:LANGUAGE_PROFILE_UPDATED"
  "PARITY:WF6:SESSION_LOGGED"
)
parity_files=(
  "AGENTS.md"
  ".codex/playbooks/project-bootstrap.md"
  "../.claude/skills/eig-project-bootstrap/SKILL.md"
)
for f in "${parity_files[@]}"; do
  for t in "${parity_tokens[@]}"; do
    check_pattern "$f" "PARITY TOKEN" "$t"
  done
done

# Transition fallback checks (warning-only)
warn_pattern "AGENTS.md" "WF1 fallback" "WF1.*PROJECT_INTAKE\\.md"
warn_pattern "AGENTS.md" "WF2 fallback" "WF2.*at most 5.*follow-up.*BLOCKER.*SOFT_REQUIRED.*pause"
warn_pattern "AGENTS.md" "WF3 fallback" "WF3.*PROJECT_DECISIONS\\.md"
warn_pattern "AGENTS.md" "WF4 fallback" "WF4.*baseline structure.*naming"
warn_pattern "AGENTS.md" "WF5 fallback" "WF5.*README\\.md.*CLAUDE\\.md.*PIPELINE_LANGUAGE_PROFILE\\.md"
warn_pattern "AGENTS.md" "WF6 fallback" "WF6.*session_logs"

# Deliverable contract parity
deliverable_files=(
  ".codex/playbooks/project-bootstrap.md"
  "../.claude/skills/eig-project-bootstrap/SKILL.md"
)
deliverable_patterns=(
  "Files changed"
  "Reason for each change"
  "Verification results"
  "Open questions/assumptions"
)
for f in "${deliverable_files[@]}"; do
  for p in "${deliverable_patterns[@]}"; do
    check_pattern "$f" "Deliverable Contract" "$p"
  done
done

if [[ "$missing" -eq 1 ]]; then
  echo "Agent parity check: FAILED"
  exit 1
fi

if [[ "$warn_count" -gt 0 ]]; then
  echo "Agent parity check: PASS (with $warn_count fallback warnings)"
  exit 0
fi

echo "Agent parity check: PASS"
