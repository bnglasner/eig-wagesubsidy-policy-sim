#!/usr/bin/env bash
# template_reset.sh — scrub project-workspace directories back to their
# fresh-template baseline before distributing this template into a new
# project. Removes dated plans, specs, session logs, and explorations that
# accumulated during template development so they do not ship into copies.
#
# Preserved in every workspace directory: README.md, .gitkeep, and (for
# explorations/) ACTIVE_PROJECTS.md. Everything else under these directories
# is removed.
#
# Usage:
#   bash Infrastructure/scripts/template_reset.sh [--dry-run] [--yes]
#
#   --dry-run   List what would be removed; change nothing.
#   --yes       Skip the interactive confirmation prompt.
set -euo pipefail

# Resolve repo root from this script's location (scripts/ is one level under Infrastructure/).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

WORKSPACE_DIRS=(
  "Infrastructure/plans"
  "Infrastructure/specs"
  "Infrastructure/session_logs"
  "Infrastructure/explorations"
)

# Names preserved in every workspace dir.
KEEP=("README.md" ".gitkeep" "ACTIVE_PROJECTS.md")

DRY_RUN=false
ASSUME_YES=false
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --yes|-y)  ASSUME_YES=true ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

is_kept() {
  local base="$1"
  for k in "${KEEP[@]}"; do
    [ "$base" = "$k" ] && return 0
  done
  return 1
}

# Collect removal targets (top-level entries inside each workspace dir that
# are not in KEEP). Directories are removed recursively.
targets=()
for rel in "${WORKSPACE_DIRS[@]}"; do
  dir="$REPO_ROOT/$rel"
  [ -d "$dir" ] || continue
  while IFS= read -r entry; do
    base="$(basename "$entry")"
    is_kept "$base" && continue
    targets+=("$entry")
  done < <(find "$dir" -mindepth 1 -maxdepth 1)
done

if [ "${#targets[@]}" -eq 0 ]; then
  echo "Workspace already at template baseline; nothing to remove."
  exit 0
fi

echo "Template reset will remove the following from the workspace directories:"
for t in "${targets[@]}"; do
  echo "  - ${t#$REPO_ROOT/}"
done

if [ "$DRY_RUN" = true ]; then
  echo "(--dry-run: no changes made.)"
  exit 0
fi

if [ "$ASSUME_YES" != true ]; then
  printf "Proceed with removal? [y/N] "
  read -r reply
  case "$reply" in
    y|Y|yes|YES) ;;
    *) echo "Aborted; no changes made."; exit 0 ;;
  esac
fi

for t in "${targets[@]}"; do
  rm -rf "$t"
done

echo "Template reset complete. Preserved README.md / .gitkeep / ACTIVE_PROJECTS.md in each workspace directory."
echo "Review with 'git status' and commit the cleaned workspace before distributing."
