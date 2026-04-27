#!/usr/bin/env bash
# gorgon-gaze: UserPromptSubmit hook.
# Lightweight refresh trigger — only re-runs the full snapshot if the cached
# snapshot is older than 10 minutes. Advisory-only, fail-open. MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SNAPSHOT="${PLUGIN_ROOT}/state/snapshot.json"
STALE_SECS=600

if [[ -f "$SNAPSHOT" ]]; then
  AGE=$(( $(date +%s) - $(stat -c %Y "$SNAPSHOT" 2>/dev/null || stat -f %m "$SNAPSHOT" 2>/dev/null || echo 0) ))
  if [[ "$AGE" -lt "$STALE_SECS" ]]; then
    exit 0
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CAPTURE="${SCRIPT_DIR}/../session-start/capture-snapshot.py"
python3 "$CAPTURE" "$PLUGIN_ROOT" 2>/dev/null || true
exit 0
