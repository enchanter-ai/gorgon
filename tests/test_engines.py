"""
Gorgon engine sanity tests — stdlib only.
Run: python -m unittest tests.test_engines -v
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "shared" / "scripts"))

from engines.g1_tarjan_scc import tarjan_scc
from engines.g2_mccabe import cyclomatic
from engines.g3_pagerank import pagerank
from engines.g4_halstead import halstead
from engines.g5_gauss import update_posterior
from bootstrap_ci import bootstrap_ci


class TestG1TarjanSCC(unittest.TestCase):
    def test_empty_graph_returns_empty(self):
        self.assertEqual(tarjan_scc({}), [])

    def test_three_node_cycle_is_one_scc(self):
        adj = {"a": ["b"], "b": ["c"], "c": ["a"]}
        sccs = tarjan_scc(adj)
        self.assertEqual(len(sccs), 1)
        self.assertEqual(set(sccs[0]), {"a", "b", "c"})

    def test_dag_yields_singletons(self):
        adj = {"a": ["b", "c"], "b": ["c"], "c": []}
        sccs = tarjan_scc(adj)
        self.assertEqual(len(sccs), 3)
        for s in sccs:
            self.assertEqual(len(s), 1)

    def test_dest_only_node_visited(self):
        # 'd' is a destination but not a key; algorithm must still visit it.
        adj = {"a": ["d"]}
        sccs = tarjan_scc(adj)
        members = {n for s in sccs for n in s}
        self.assertIn("a", members)
        self.assertIn("d", members)


class TestG2McCabe(unittest.TestCase):
    def test_simple_function_complexity_1(self):
        import ast as _ast
        tree = _ast.parse("def f():\n    return 1\n")
        scores = cyclomatic(tree)
        self.assertEqual(scores["f"], 1)

    def test_if_adds_one(self):
        import ast as _ast
        tree = _ast.parse("def f(x):\n    if x:\n        return 1\n    return 0\n")
        scores = cyclomatic(tree)
        self.assertEqual(scores["f"], 2)

    def test_method_qualified_name(self):
        import ast as _ast
        tree = _ast.parse("class C:\n    def m(self, x):\n        return x\n")
        scores = cyclomatic(tree)
        self.assertIn("C.m", scores)

    def test_boolop_chain_counts_extra_branches(self):
        import ast as _ast
        tree = _ast.parse("def f(a, b, c):\n    return a and b and c\n")
        scores = cyclomatic(tree)
        # 1 base + 2 extra operands in the BoolOp chain (a-and-b, then -and-c).
        self.assertGreaterEqual(scores["f"], 3)


class TestG3PageRank(unittest.TestCase):
    def test_empty_graph(self):
        self.assertEqual(pagerank({}), {})

    def test_scores_sum_to_one(self):
        dag = {"a": ["b", "c"], "b": ["c"], "c": []}
        pr = pagerank(dag)
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=3)
        self.assertGreater(pr["c"], pr["a"])  # c has fan-in

    def test_dangling_node_survives(self):
        dag = {"a": ["b"], "b": []}
        pr = pagerank(dag)
        self.assertIn("b", pr)
        self.assertIn("a", pr)

    def test_dict_adjacency_form_supported(self):
        dag = {"a": {"b": 1.0, "c": 1.0}, "b": {"c": 1.0}, "c": {}}
        pr = pagerank(dag)
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=3)


class TestG4Halstead(unittest.TestCase):
    def test_empty_source_returns_zeros(self):
        h = halstead("")
        self.assertEqual(h["volume"], 0.0)

    def test_simple_assignment_yields_volume(self):
        h = halstead("x = 1 + 2\n")
        self.assertGreater(h["volume"], 0.0)
        self.assertEqual(h["N1"] + h["N2"], h["length"])

    def test_syntax_error_fails_open(self):
        h = halstead("def f(:\n")
        self.assertEqual(h["volume"], 0.0)


class TestG5Gauss(unittest.TestCase):
    def test_first_observation_seeds_posterior(self):
        p = update_posterior({}, {"hotspot_score": 0.8, "top_n_stability": 1.0,
                                  "captured_at": "2026-04-25T00:00:00Z"})
        self.assertEqual(p["n_snapshots"], 1)
        self.assertAlmostEqual(p["median_score"], 0.8, places=4)
        self.assertEqual(p["sigma"], 0.0)

    def test_repeated_same_obs_converges(self):
        p = {}
        for _ in range(20):
            p = update_posterior(p, {"hotspot_score": 0.9, "top_n_stability": 1.0,
                                     "captured_at": "2026-04-25T00:00:00Z"})
        self.assertAlmostEqual(p["median_score"], 0.9, places=2)
        self.assertLess(p["sigma"], 0.05)
        self.assertEqual(p["n_snapshots"], 20)


class TestBootstrapCI(unittest.TestCase):
    def test_empty_returns_zeros(self):
        self.assertEqual(bootstrap_ci([]), (0.0, 0.0, 0.0, 0))

    def test_single_sample_collapses_band(self):
        v, lo, hi, n = bootstrap_ci([0.7])
        self.assertEqual((v, lo, hi, n), (0.7, 0.7, 0.7, 1))

    def test_multi_sample_band_ordering(self):
        v, lo, hi, n = bootstrap_ci([0.5, 0.6, 0.7, 0.8, 0.9, 0.55, 0.65, 0.75])
        self.assertLessEqual(lo, v)
        self.assertLessEqual(v, hi)
        self.assertEqual(n, 8)


if __name__ == "__main__":
    unittest.main()
