#!/usr/bin/env python3
"""
refresh-touched.py — Phase-1 placeholder runner for gorgon-watcher PostToolUse.

Reads JSON hook payload from stdin, extracts tool_input.file_path, re-parses
that file, updates the dirty-nodes list in state/dirty.json. Atomic writes.
Stdlib-only. Fail-open.
"""
from __future__ import annotations

import ast
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
SHARED_SCRIPTS = PLUGIN_ROOT.parent.parent / "shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from engines.g2_mccabe import cyclomatic  # noqa: E402
from state_io import atomic_write_json, read_json, append_jsonl  # noqa: E402


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0
    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path or not file_path.endswith(".py"):
        return 0

    p = Path(file_path)
    if not p.exists():
        return 0
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, ValueError) as exc:
        append_jsonl(PLUGIN_ROOT / "state" / "parse-failures.jsonl",
                     {"path": str(p), "error": str(exc)})
        return 0

    cyclo = cyclomatic(tree)

    dirty_path = PLUGIN_ROOT / "state" / "dirty.json"
    dirty = read_json(dirty_path, default={"dirty_nodes": [], "updated_at": None})
    dn = set(dirty.get("dirty_nodes", []))
    dn.add(str(p))
    out = {
        "dirty_nodes": sorted(dn),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_file": str(p),
        "last_cyclomatic": cyclo,
    }
    atomic_write_json(dirty_path, out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
