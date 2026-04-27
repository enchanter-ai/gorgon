#!/usr/bin/env python3
"""
update-posterior.py — Phase-1 runner for gorgon-learning PreCompact.

Reads the gorgon-gaze snapshot, computes a single observation, folds it into
the per-(repo x hotspot-kind) posterior via G5. Persists learnings.jsonl.
Stdlib only. Fail-open.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

PLUGIN_ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
SHARED_SCRIPTS = PLUGIN_ROOT.parent.parent / "shared" / "scripts"
sys.path.insert(0, str(SHARED_SCRIPTS))

from engines.g5_gauss import update_posterior  # noqa: E402
from state_io import read_json, atomic_write_json, append_jsonl  # noqa: E402


def main() -> int:
    gaze_snapshot = PLUGIN_ROOT.parent / "gorgon-gaze" / "state" / "snapshot.json"
    snap = read_json(gaze_snapshot, default=None)
    if not snap:
        return 0

    ranks = snap.get("ranks", {})
    if not ranks:
        return 0
    top_score = max(ranks.values())

    posterior_path = PLUGIN_ROOT / "state" / "posterior.json"
    posteriors = read_json(posterior_path, default={})
    repo_key = snap.get("repo_root", "unknown")
    kinds = ["complexity", "coupling", "churn-magnet"]

    now = datetime.now(timezone.utc).isoformat()
    for kind in kinds:
        prior = posteriors.get(repo_key, {}).get(kind, {})
        observation = {
            "hotspot_score": top_score,
            "top_n_stability": 1.0,
            "captured_at": now,
        }
        new_post = update_posterior(prior, observation)
        posteriors.setdefault(repo_key, {})[kind] = new_post

    atomic_write_json(posterior_path, posteriors)
    append_jsonl(PLUGIN_ROOT / "state" / "learnings.jsonl",
                 {"updated_at": now, "repo": repo_key, "top_score": top_score})
    return 0


if __name__ == "__main__":
    sys.exit(main())
