"""
G1 — Tarjan Strongly-Connected-Components

Reference:
    Tarjan R.E. (1972), "Depth-first search and linear graph algorithms",
    SIAM Journal on Computing 1(2):146-160.

Role:
    Detect dependency cycles and identify SCCs in the file-level import graph.
    Emit gorgon.cycle.detected for any non-trivial SCC (size > 1).

Stdlib only: iterative DFS over a dict[str, list[str]] adjacency map.
"""
from __future__ import annotations


def tarjan_scc(adj: dict) -> list:
    """Return a list of SCCs, each SCC a list of node ids.

    Linear-time O(V+E). Iterative — no Python recursion-limit risk on large repos.
    Adjacency: dict[str, list[str]] mapping node -> outgoing neighbours.
    """
    index_counter = [0]
    stack: list = []
    on_stack: set = set()
    indices: dict = {}
    lowlinks: dict = {}
    result: list = []

    # Make sure every reachable node has a key (so we visit dest-only nodes too).
    nodes = list(adj.keys())
    for outs in list(adj.values()):
        for dst in outs:
            if dst not in adj:
                nodes.append(dst)
    seen_seed: set = set()
    seeds: list = []
    for n in nodes:
        if n not in seen_seed:
            seen_seed.add(n)
            seeds.append(n)

    for start in seeds:
        if start in indices:
            continue
        # work stack: (node, child-iter-index)
        work: list = [(start, 0)]
        while work:
            node, pi = work[-1]
            if pi == 0:
                indices[node] = index_counter[0]
                lowlinks[node] = index_counter[0]
                index_counter[0] += 1
                stack.append(node)
                on_stack.add(node)
            neighbours = adj.get(node, [])
            if pi < len(neighbours):
                work[-1] = (node, pi + 1)
                w = neighbours[pi]
                if w not in indices:
                    work.append((w, 0))
                elif w in on_stack:
                    lowlinks[node] = min(lowlinks[node], indices[w])
            else:
                if lowlinks[node] == indices[node]:
                    scc: list = []
                    while True:
                        w = stack.pop()
                        on_stack.discard(w)
                        scc.append(w)
                        if w == node:
                            break
                    result.append(scc)
                work.pop()
                if work:
                    parent = work[-1][0]
                    lowlinks[parent] = min(lowlinks[parent], lowlinks[node])
    return result
