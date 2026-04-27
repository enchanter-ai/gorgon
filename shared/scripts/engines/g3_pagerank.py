"""
G3 — PageRank Symbol-Graph Hotspot Ranking

Reference:
    Brin S. and Page L. (1998), "The anatomy of a large-scale hypertextual
    Web search engine", Computer Networks and ISDN Systems 30(1-7):107-117.

Role:
    Rank files by import-graph centrality. A file with high import-fan-in *and*
    high transitive reach scores high — captures god-modules invisible to
    per-file metrics like cyclomatic complexity.

Stdlib only: power-iteration on a sparse adjacency map. Dangling nodes
redistribute uniformly (the standard Brin-Page treatment).
"""
from __future__ import annotations


def pagerank(
    adj: dict,
    damping: float = 0.85,
    eps: float = 1e-6,
    max_iter: int = 200,
) -> dict:
    """Compute PageRank over an outgoing-adjacency dict.

    Accepts either {node: [out, ...]} or {node: {out: weight, ...}}.
    Returns {node: score} with sum(scores) == 1.0 within float error.

    Edge case for very large repos: caller may inspect convergence by checking
    whether the returned dict contains a `__convergence_warning__` key — we do
    not surface it here; the wrapper layer adds it on iteration cap.
    """
    nodes = list(adj.keys())
    for outs in list(adj.values()):
        if isinstance(outs, dict):
            it = outs.keys()
        else:
            it = outs
        for dst in it:
            if dst not in adj:
                nodes.append(dst)
    nodes = list(dict.fromkeys(nodes))
    n = len(nodes)
    if n == 0:
        return {}

    idx = {node: i for i, node in enumerate(nodes)}
    out_lists: list = []
    for node in nodes:
        raw = adj.get(node, [])
        if isinstance(raw, dict):
            out_lists.append(list(raw.keys()))
        else:
            out_lists.append(list(raw))

    pr = [1.0 / n] * n
    teleport = (1.0 - damping) / n

    for _ in range(max_iter):
        new = [teleport] * n
        dangling_mass = 0.0
        for i, out_list in enumerate(out_lists):
            if not out_list:
                dangling_mass += pr[i]
                continue
            share = damping * pr[i] / len(out_list)
            for dst in out_list:
                new[idx[dst]] += share
        dang_share = damping * dangling_mass / n
        for i in range(n):
            new[i] += dang_share
        delta = sum(abs(new[i] - pr[i]) for i in range(n))
        pr = new
        if delta < eps:
            break

    return {nodes[i]: pr[i] for i in range(n)}
