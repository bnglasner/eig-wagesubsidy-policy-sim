#!/usr/bin/env bash
#
# check_org_vendor_drift.sh
# -------------------------------------------------------------------------
# UPSTREAM-DRIFT check for the vendored CPS ORG ingestion stage.
#
# Three R stages were vendored from the canonical repo
#   EIG-Wage-Figure-Explain-Everything @ 33bbcb7
# into code/00_ingest/. Pristine upstream copies at that SHA are kept in
#   code/00_ingest/.upstream_33bbcb7/
#
# Vendoring rule (the ONLY differences allowed vs. upstream):
#   (a) configuration edits, and
#   (b) annotated inert-guards,
# each annotated with an EIG-VENDOR-CONFIG or EIG-VENDOR-GUARD tag inside the
# same contiguous diff hunk. 01b must be BYTE-IDENTICAL to upstream.
#
# This script:
#   1. Diffs each vendored file against its pristine .upstream_33bbcb7/ copy
#      and asserts that no hunk introduces or removes un-annotated logic
#      (a "logic change" = a non-blank, non-comment added or removed line).
#      Every such hunk must carry an EIG-VENDOR-CONFIG / EIG-VENDOR-GUARD tag.
#      01b must be byte-identical.
#   2. If the canonical repo is on disk, checks whether it has advanced beyond
#      the pinned SHA for these files (a re-sync signal).
#
# Exit codes:
#   0  clean (no un-annotated drift)
#   1  HIGH: un-annotated logic drift, or 01b not byte-identical, or a
#      required vendored/pristine file is missing
#
# Staleness / pristine-integrity issues are reported as MEDIUM/INFO warnings
# and do NOT change the exit code.
#
# Configuration:
#   UPSTREAM_SHA   pinned canonical commit (default 33bbcb7)
#   CANONICAL_REPO path to the canonical repo working copy
#                  (default: <repo-root>/../EIG-Wage-Figure-Explain-Everything)
# -------------------------------------------------------------------------

set -u

# ---- pinned upstream reference -----------------------------------------
UPSTREAM_SHA="${UPSTREAM_SHA:-33bbcb7}"

# ---- derive repo root (no hardcoded absolute paths) --------------------
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Infrastructure/scripts/ -> repo root is two levels up.
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

CANONICAL_REPO="${CANONICAL_REPO:-$REPO_ROOT/../EIG-Wage-Figure-Explain-Everything}"

VENDOR_DIR="$REPO_ROOT/code/00_ingest"
PRISTINE_DIR="$VENDOR_DIR/.upstream_33bbcb7"

# Files vendored and the mode of comparison.
#   strict  -> byte-identical required
#   annotated -> only blank/comment/tagged changes allowed
VENDORED_FILES="00a_download-ipums-cps.R 01a_load-ipums-cps.R 01b_build-org-panel.R"
STRICT_FILES="01b_build-org-panel.R"

# Location of these files inside the canonical repo (relative to its root).
CANONICAL_SUBDIR="code"

# ---- reporting helpers -------------------------------------------------
HIGH_COUNT=0
MED_COUNT=0
INFO_COUNT=0
PASS_COUNT=0

report_high() { printf 'HIGH   | %s\n' "$1"; HIGH_COUNT=$((HIGH_COUNT + 1)); }
report_med()  { printf 'MEDIUM | %s\n' "$1"; MED_COUNT=$((MED_COUNT + 1)); }
report_info() { printf 'INFO   | %s\n' "$1"; INFO_COUNT=$((INFO_COUNT + 1)); }
report_pass() { printf 'PASS   | %s\n' "$1"; PASS_COUNT=$((PASS_COUNT + 1)); }

is_strict() {
  case " $STRICT_FILES " in
    *" $1 "*) return 0 ;;
    *) return 1 ;;
  esac
}

echo "==============================================================="
echo " ORG vendor UPSTREAM-DRIFT check"
echo "==============================================================="
echo " repo root      : $REPO_ROOT"
echo " pinned SHA     : $UPSTREAM_SHA"
echo " vendor dir     : $VENDOR_DIR"
echo " pristine dir   : $PRISTINE_DIR"
echo " canonical repo : $CANONICAL_REPO"
echo "---------------------------------------------------------------"

# ---- 1. vendored-vs-pristine drift -------------------------------------
echo
echo "[1] Vendored files vs. pristine upstream copies"
echo "---------------------------------------------------------------"

# awk program: given a unified diff on stdin, classify each hunk.
# A hunk is flagged as un-annotated logic drift when it contains a
# non-blank / non-comment added ('+') or removed ('-') line but no
# EIG-VENDOR-CONFIG / EIG-VENDOR-GUARD tag anywhere in the hunk.
# Prints one offending line per flagged hunk on stderr; exit status via
# the "DRIFT" marker on stdout count.
classify_hunk() {
  awk '
    function flush_hunk() {
      if (in_hunk && logic && !tagged) {
        printf("    un-annotated change near hunk: %s\n", header)
        printf("      e.g.: %s\n", sample)
        drift++
      }
    }
    /^@@/ {
      flush_hunk()
      in_hunk = 1; logic = 0; tagged = 0; header = $0; sample = ""
      next
    }
    {
      if (!in_hunk) next
      marker = substr($0, 1, 1)
      if (marker != "+" && marker != "-") next
      body = substr($0, 2)
      # tag detection (anywhere in changed line)
      if (body ~ /EIG-VENDOR-CONFIG/ || body ~ /EIG-VENDOR-GUARD/) tagged = 1
      # strip leading whitespace
      stripped = body
      sub(/^[ \t]+/, "", stripped)
      # blank?
      if (stripped == "") next
      # R comment?
      if (substr(stripped, 1, 1) == "#") next
      # otherwise this is a logic line
      logic = 1
      if (sample == "") sample = marker body
    }
    END {
      flush_hunk()
      printf("DRIFT=%d\n", drift + 0)
    }
  '
}

for f in $VENDORED_FILES; do
  vend="$VENDOR_DIR/$f"
  pris="$PRISTINE_DIR/$f"

  if [ ! -f "$vend" ]; then
    report_high "$f: vendored file missing at $vend"
    continue
  fi
  if [ ! -f "$pris" ]; then
    report_high "$f: pristine copy missing at $pris"
    continue
  fi

  if is_strict "$f"; then
    if diff -q "$pris" "$vend" >/dev/null 2>&1; then
      report_pass "$f: byte-identical to upstream (strict)"
    else
      report_high "$f: MUST be byte-identical to upstream but differs"
      diff "$pris" "$vend" | sed 's/^/         /' | head -20
    fi
    continue
  fi

  # annotated mode
  if diff -q "$pris" "$vend" >/dev/null 2>&1; then
    report_pass "$f: unchanged from upstream"
    continue
  fi

  result="$(diff -u "$pris" "$vend" | classify_hunk)"
  drift_lines="$(printf '%s\n' "$result" | grep -v '^DRIFT=' || true)"
  drift_count="$(printf '%s\n' "$result" | sed -n 's/^DRIFT=//p')"
  drift_count="${drift_count:-0}"

  if [ "$drift_count" -gt 0 ]; then
    report_high "$f: $drift_count hunk(s) with un-annotated logic drift"
    printf '%s\n' "$drift_lines" | sed 's/^/         /'
  else
    report_pass "$f: all changes are blank/comment/EIG-VENDOR-tagged (annotated config/guard edits only)"
  fi
done

# ---- 2. canonical advancement (staleness) ------------------------------
echo
echo "[2] Upstream advancement / pristine integrity (canonical repo)"
echo "---------------------------------------------------------------"

if [ ! -d "$CANONICAL_REPO/.git" ]; then
  report_info "canonical repo not found at $CANONICAL_REPO (set CANONICAL_REPO to enable the staleness check); skipping advancement check"
else
  CANON_HEAD="$(git -C "$CANONICAL_REPO" rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "    canonical HEAD : $CANON_HEAD"
  echo "    pinned SHA     : $UPSTREAM_SHA"

  # Does the pinned SHA resolve in the canonical repo?
  if ! git -C "$CANONICAL_REPO" rev-parse --verify --quiet "${UPSTREAM_SHA}^{commit}" >/dev/null 2>&1; then
    report_med "pinned SHA $UPSTREAM_SHA does not resolve in $CANONICAL_REPO; cannot verify advancement"
  else
    for f in $VENDORED_FILES; do
      pris="$PRISTINE_DIR/$f"
      canon_path="$CANONICAL_SUBDIR/$f"

      # 2a. pristine-integrity: .upstream copy must equal canonical@pinned
      if [ -f "$pris" ]; then
        if git -C "$CANONICAL_REPO" show "$UPSTREAM_SHA:$canon_path" > "$REPO_ROOT/.org_vendor_pinned.$$" 2>/dev/null; then
          if diff -q "$REPO_ROOT/.org_vendor_pinned.$$" "$pris" >/dev/null 2>&1; then
            : # pristine matches pinned SHA
          else
            report_med "$f: pristine copy does not match canonical@$UPSTREAM_SHA (pristine may have been edited)"
          fi
        else
          report_info "$f: not found in canonical@$UPSTREAM_SHA at $canon_path (path may have moved)"
        fi
        rm -f "$REPO_ROOT/.org_vendor_pinned.$$"
      fi

      # 2b. advancement: canonical@HEAD content vs pinned-SHA content
      pinned_blob="$(git -C "$CANONICAL_REPO" rev-parse --quiet --verify "$UPSTREAM_SHA:$canon_path" 2>/dev/null || true)"
      head_blob="$(git -C "$CANONICAL_REPO" rev-parse --quiet --verify "HEAD:$canon_path" 2>/dev/null || true)"
      if [ -n "$pinned_blob" ] && [ -n "$head_blob" ]; then
        if [ "$pinned_blob" = "$head_blob" ]; then
          report_pass "$f: canonical still at pinned content (no upstream advancement)"
        else
          report_med "$f: canonical HEAD has advanced beyond $UPSTREAM_SHA -- vendored copy may be stale; re-sync recommended"
        fi
      fi
    done
  fi
fi

# ---- summary -----------------------------------------------------------
echo
echo "==============================================================="
echo " Summary: PASS=$PASS_COUNT  HIGH=$HIGH_COUNT  MEDIUM=$MED_COUNT  INFO=$INFO_COUNT"
echo "==============================================================="

if [ "$HIGH_COUNT" -gt 0 ]; then
  echo "RESULT: FAIL (un-annotated drift or strict-file violation)"
  exit 1
fi
echo "RESULT: PASS (no un-annotated logic drift)"
exit 0
