#!/usr/bin/env python3
"""
capture-snapshot.py — Phase-1 placeholder runner for gorgon-gaze SessionStart.

Walks $PWD for *.py files, builds an import-edge adjacency, runs G1 Tarjan +
G3 PageRank, writes state/snapshot.json atomically.

Stdlib-only. On any per-file parse error, append to state/parse-failures.jsonl
and continue — never abort the whole snapshot.
"""
from __future__ import annotations

import ast
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
REPO_ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

# Ensure shared/scripts is importable.
SHARED_SCRIPTS = PLUGIN_ROOT.parent.parent / "shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from engines.g1_tarjan_scc import tarjan_scc  # noqa: E402
from engines.g3_pagerank import pagerank  # noqa: E402
from state_io import atomic_write_json, append_jsonl  # noqa: E402


def _resolve_imports(tree: ast.AST) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                out.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                out.append(node.module)
    return out


# Stdlib module names — canonical filter (Python >= 3.10).
# `sys.stdlib_module_names` is a frozenset of every top-level stdlib module.
_STDLIB = frozenset(getattr(sys, "stdlib_module_names", frozenset()))


def _build_module_index(root: Path, py_files: list) -> dict:
    """Map dotted-module name -> rel path for every *.py file under root.

    Both `pkg.sub.mod` and `pkg.sub` (for `__init__.py`) are indexed so an
    `import pkg.sub` resolves to the package file.
    """
    index: dict = {}
    for rel in py_files:
        parts = list(Path(rel).with_suffix("").parts)
        if not parts:
            continue
        if parts[-1] == "__init__":
            parts = parts[:-1]
            if not parts:
                continue
        dotted = ".".join(parts)
        index[dotted] = rel
        # Also index the leaf name so a bare `import g3_pagerank` (when
        # shared/scripts is on sys.path) resolves to its file.
        leaf = parts[-1]
        index.setdefault(leaf, rel)
    return index


def _filter_imports(raw: list, module_index: dict) -> list:
    """Drop stdlib + unresolved (third-party / unknown) imports.

    A raw import name like `engines.g3_pagerank` resolves first by full dotted
    match, then by progressively trimming trailing components (covers
    `from engines.g3_pagerank import pagerank` -> module `engines.g3_pagerank`,
    and `import a.b.c` when only `a.b` is a repo file).
    """
    kept = []
    for name in raw:
        top = name.split(".", 1)[0]
        if top in _STDLIB:
            continue
        parts = name.split(".")
        resolved = None
        while parts:
            candidate = ".".join(parts)
            if candidate in module_index:
                resolved = module_index[candidate]
                break
            parts.pop()
        if resolved is None:
            continue
        kept.append(resolved)
    return kept


def _walk_repo(root: Path) -> dict:
    raw_adj: dict = {}
    failures_path = PLUGIN_ROOT / "state" / "parse-failures.jsonl"
    py_files: list = []
    for p in root.rglob("*.py"):
        rel = str(p.relative_to(root))
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, ValueError) as exc:
            append_jsonl(failures_path, {"path": rel, "error": str(exc)})
            continue
        raw_adj[rel] = _resolve_imports(tree)
        py_files.append(rel)

    module_index = _build_module_index(root, py_files)
    adj: dict = {rel: _filter_imports(raw, module_index) for rel, raw in raw_adj.items()}
    return adj


def main() -> int:
    started = time.time()
    adj = _walk_repo(REPO_ROOT)
    file_count = len(adj)
    edge_count = sum(len(v) for v in adj.values())

    sccs = tarjan_scc(adj)
    nontrivial = [s for s in sccs if len(s) > 1]
    ranks = pagerank(adj)

    snapshot = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(REPO_ROOT),
        "file_count": file_count,
        "edge_count": edge_count,
        "scc_count": len(sccs),
        "nontrivial_scc_count": len(nontrivial),
        "ranks": ranks,
        "duration_ms": int((time.time() - started) * 1000),
    }

    out_path = PLUGIN_ROOT / "state" / "snapshot.json"
    atomic_write_json(out_path, snapshot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
