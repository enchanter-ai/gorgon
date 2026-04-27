#!/usr/bin/env bash
# gorgon-gaze: SessionStart hook.
# Walks the repo, builds the import graph, runs G1 Tarjan + G3 PageRank,
# persists state/snapshot.json atomically. Advisory-only, fail-open. MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "${SCRIPT_DIR}/capture-snapshot.py" "$PLUGIN_ROOT" 2>/dev/null || true
exit 0
