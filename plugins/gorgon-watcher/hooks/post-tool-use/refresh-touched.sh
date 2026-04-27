#!/usr/bin/env bash
# gorgon-watcher: PostToolUse hook (Write|Edit|MultiEdit).
# Re-parses the touched file plus its 1-hop importers, updates adjacency,
# recomputes G2 cyclomatic for changed functions. Advisory-only, fail-open.
# MUST exit 0.

if [[ -n "${CLAUDE_SUBAGENT:-}" ]]; then
  exit 0
fi

trap 'exit 0' ERR INT TERM
set -uo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Read hook input (file path) from stdin if present.
INPUT="$(cat 2>/dev/null || true)"

python3 "${SCRIPT_DIR}/refresh-touched.py" "$PLUGIN_ROOT" <<<"$INPUT" 2>/dev/null || true
exit 0
