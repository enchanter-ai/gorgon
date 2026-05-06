"""
Gorgon event-bus helpers — typed wrappers over shared.scripts.publish.publish.

Exposes one function per published topic listed in `CLAUDE.md § Events`.
Every helper is fail-open per shared/foundations/conduct/hooks.md — advisory, never raises.

Phase-1 file-tail fallback: publishes go through Pech's `publish.py` (copied
verbatim into `shared/scripts/publish.py`) which JSONL-appends events to the
enchanted-mcp bus file. See docs/ecosystem.md (sibling repo) for the cross-plugin contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the sibling publish.py is importable regardless of invocation cwd.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from publish import publish  # noqa: E402


def publish_snapshot_captured(
    session_id: str,
    repo_root: str,
    file_count: int,
    edge_count: int,
    captured_at: str,
) -> None:
    """gorgon.snapshot.captured — emitted by gorgon-gaze on SessionStart."""
    publish(
        "gorgon.snapshot.captured",
        {
            "session_id": session_id,
            "repo_root": repo_root,
            "file_count": file_count,
            "edge_count": edge_count,
            "captured_at": captured_at,
        },
    )


def publish_hotspot_detected(
    file: str,
    score: float,
    ci_low: float,
    ci_high: float,
    N: int,
    rank: int,
    hotspot_kind: str,
) -> None:
    """gorgon.hotspot.detected — honest-numbers contract: (value, ci_low, ci_high, N) required.

    hotspot_kind in {complexity, coupling, churn-magnet}.
    """
    publish(
        "gorgon.hotspot.detected",
        {
            "file": file,
            "score": score,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "N": N,
            "rank": rank,
            "hotspot_kind": hotspot_kind,
        },
    )


def publish_cycle_detected(
    scc_members: list,
    edges: list,
    severity: str,
) -> None:
    """gorgon.cycle.detected — emitted by gorgon-gaze when G1 finds an SCC of size > 1.

    severity in {info, warn, error} based on SCC size.
    """
    publish(
        "gorgon.cycle.detected",
        {
            "scc_members": list(scc_members),
            "edges": list(edges),
            "severity": severity,
        },
    )


def publish_snapshot_refreshed(
    session_id: str,
    dirty_nodes: list,
    turn: int,
) -> None:
    """gorgon.snapshot.refreshed — emitted by gorgon-watcher after PostToolUse re-parse."""
    publish(
        "gorgon.snapshot.refreshed",
        {
            "session_id": session_id,
            "dirty_nodes": list(dirty_nodes),
            "turn": turn,
        },
    )


__all__ = [
    "publish_snapshot_captured",
    "publish_hotspot_detected",
    "publish_cycle_detected",
    "publish_snapshot_refreshed",
]
