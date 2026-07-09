#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# PolicyEngine version comparison runner
# Tests two questions:
#   1. Does passing `hourly_wage` into a PE situation change any outputs?
#   2. How much did the 1.592.4 → 1.632.2 upgrade change the schedules?
#
# Usage:
#   chmod +x run_comparison.sh
#   ./run_comparison.sh
#
# Requirements: Python 3.12, internet access (~300 MB download for both PEs)
# Runtime: ~5–10 minutes (131 income pts × 3 combos × 2 versions × 2 hw modes)
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLD_VER="1.592.4"
NEW_VER="1.632.2"
OLD_VENV="$SCRIPT_DIR/.venv_pe_old"
NEW_VENV="$SCRIPT_DIR/.venv_pe_new"
COMPARE_SCRIPT="$SCRIPT_DIR/pe_compare.py"
RESULTS_DIR="$SCRIPT_DIR/results"

mkdir -p "$RESULTS_DIR"

echo "============================================================"
echo " PolicyEngine Version Comparison"
echo " OLD: policyengine-us==$OLD_VER"
echo " NEW: policyengine-us==$NEW_VER"
echo "============================================================"

# ── Create venvs if they don't exist ─────────────────────────────────────────
if [ ! -d "$OLD_VENV" ]; then
    echo ""
    echo "Creating venv for $OLD_VER ..."
    python3.12 -m venv "$OLD_VENV"
    "$OLD_VENV/bin/pip" install -q "policyengine-us==$OLD_VER"
    echo "  Done."
else
    echo "  (old venv already exists, skipping install)"
fi

if [ ! -d "$NEW_VENV" ]; then
    echo ""
    echo "Creating venv for $NEW_VER ..."
    python3.12 -m venv "$NEW_VENV"
    "$NEW_VENV/bin/pip" install -q "policyengine-us==$NEW_VER"
    echo "  Done."
else
    echo "  (new venv already exists, skipping install)"
fi

# ── Run comparison script in each venv ───────────────────────────────────────
echo ""
echo "Running OLD version ($OLD_VER) ..."
RESULTS_DIR="$RESULTS_DIR" "$OLD_VENV/bin/python" "$COMPARE_SCRIPT" --mode single

echo ""
echo "Running NEW version ($NEW_VER) ..."
RESULTS_DIR="$RESULTS_DIR" "$NEW_VENV/bin/python" "$COMPARE_SCRIPT" --mode single

# ── Diff ─────────────────────────────────────────────────────────────────────
echo ""
echo "Diffing results ..."
RESULTS_DIR="$RESULTS_DIR" "$NEW_VENV/bin/python" "$COMPARE_SCRIPT" --mode diff

echo ""
echo "Done. Full results saved to: $RESULTS_DIR"
