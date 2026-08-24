"""
Snapshot-persistence test: gorgon-gaze must write a usable import `adjacency`
into snapshot.json so the /gorgon:deps (deps-query) skill has edges to read.

This is the regression guard for the T2 fix — before it, the adjacency was
built in memory and discarded, leaving /gorgon:deps hollow.

Run: python -m unittest tests.test_snapshot_adjacency -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CAPTURE = (
    REPO_ROOT
    / "plugins"
    / "gorgon-gaze"
    / "hooks"
    / "session-start"
    / "capture-snapshot.py"
)


class TestSnapshotPersistsAdjacency(unittest.TestCase):
    def _run_capture(self, plugin_root: Path, repo_root: Path) -> dict:
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = str(repo_root)
        # The temp plugin_root does not sit under the real repo, so the
        # script's relative shared/scripts path won't resolve — put the real
        # one on PYTHONPATH so `engines`/`state_io` import.
        shared_scripts = str(REPO_ROOT / "shared" / "scripts")
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            shared_scripts + os.pathsep + existing if existing else shared_scripts
        )
        proc = subprocess.run(
            [sys.executable, str(CAPTURE), str(plugin_root)],
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        snap_path = plugin_root / "state" / "snapshot.json"
        self.assertTrue(snap_path.exists(), "snapshot.json was not written")
        return json.loads(snap_path.read_text(encoding="utf-8"))

    def test_adjacency_field_present_and_maps_edges(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            repo_root = root / "repo"
            plugin_root = root / "plugin"
            (repo_root / "pkg").mkdir(parents=True)
            (plugin_root / "state").mkdir(parents=True)

            # a.py imports b (repo-internal); b.py imports only stdlib.
            (repo_root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
            (repo_root / "pkg" / "a.py").write_text(
                "import os\nimport pkg.b\n", encoding="utf-8"
            )
            (repo_root / "pkg" / "b.py").write_text(
                "import sys\n", encoding="utf-8"
            )

            snap = self._run_capture(plugin_root, repo_root)

            self.assertIn("adjacency", snap, "snapshot missing 'adjacency' field")
            adj = snap["adjacency"]
            a_key = str(Path("pkg/a.py"))
            b_key = str(Path("pkg/b.py"))
            self.assertIn(a_key, adj)
            # a.py's only repo-internal edge is to pkg/b.py; stdlib is filtered.
            self.assertEqual(adj[a_key], [b_key])
            # b.py imports only stdlib -> no internal edges.
            self.assertEqual(adj[b_key], [])
            # edge_count must agree with the persisted adjacency.
            self.assertEqual(
                snap["edge_count"], sum(len(v) for v in adj.values())
            )


if __name__ == "__main__":
    unittest.main()
