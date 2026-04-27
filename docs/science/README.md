# Formal Derivations — Gorgon

This document holds the paper-grounded derivations for Gorgon's five engines.
One section per engine listed in `CLAUDE.md § Algorithms`.

---

## G1 — Tarjan Strongly-Connected-Components

**Reference:** Tarjan R.E. (1972), "Depth-first search and linear graph algorithms",
SIAM Journal on Computing 1(2):146-160.

**Signature:** `tarjan_scc(adj: dict[str, list[str]]) -> list[list[str]]`

### Derivation

Given a directed graph G = (V, E), a strongly-connected component is a
maximal subset S ⊆ V such that ∀ u, v ∈ S there exists a directed path
from u to v. Tarjan's algorithm performs a single depth-first traversal
maintaining two values per node:
- `index[v]` — DFS visit order.
- `lowlink[v]` — smallest index reachable from v's DFS subtree (including v).

When `lowlink[v] == index[v]`, every node currently above v on the auxiliary
stack belongs to a single SCC rooted at v. Linear time O(V + E).

### Implementation notes

- Stdlib only. Iterative DFS via an explicit work-stack of `(node, child_index)`
  tuples — no Python recursion-limit risk on large repos (`sys.setrecursionlimit`
  workaround discouraged).
- Adjacency: `dict[str, list[str]]`. Destination-only nodes (referenced but not
  keys) are seeded into the visit set so their SCC is captured.

### Failure modes

- **Self-loop edge** counts as a 1-node SCC (size = 1). Treat as non-trivial
  cycle by SCC size > 1 OR self-loop check.

---

## G2 — McCabe Cyclomatic Complexity

**Reference:** McCabe T.J. (1976), "A Complexity Measure",
IEEE Transactions on Software Engineering SE-2(4):308-320.

**Signature:** `cyclomatic(tree: ast.AST) -> dict[str, int]`

### Derivation

For a control-flow graph CFG = (N, E) of a single-entry single-exit function
body, cyclomatic complexity is:

    M = E − N + 2P    (where P = number of connected components, here P = 1)

Equivalently, M = (decision points + 1). Decision points include `if`, `for`,
`while`, `try`/`except`, boolean operators (each additional operand in a
chain), conditional expressions, and assertions.

### Implementation notes

- Stdlib `ast.walk` over the function body.
- Counted node types: `If`, `For`, `AsyncFor`, `While`, `Try`, `ExceptHandler`,
  `With`, `AsyncWith`, `IfExp`, `Assert`, `comprehension`, plus
  `BoolOp` (each additional operand adds one branch).
- Lambda is folded into its enclosing scope (no separate score).

### Failure modes

- **Match/case (3.10+).** Each `case` adds a decision point — track separately
  if expanding to that node type.
- **Class-level statements.** Not scored — McCabe is per-function.

---

## G3 — PageRank Symbol-Graph Hotspot Ranking

**Reference:** Brin S. and Page L. (1998), "The anatomy of a large-scale
hypertextual Web search engine", Computer Networks and ISDN Systems
30(1-7):107-117.

**Signature:** `pagerank(adj: dict[str, dict[str, float]] | dict[str, list[str]],
damping: float = 0.85, eps: float = 1e-6, max_iter: int = 200) -> dict[str, float]`

### Derivation

PageRank computes the stationary distribution of a random surfer model on a
directed graph. Power iteration:

    PR(v) = (1−d)/N + d · Σ_{u ∈ in(v)} PR(u) / |out(u)|

with damping factor d = 0.85. Dangling nodes (no out-edges) redistribute
their mass uniformly across all N nodes — the standard Brin-Page treatment.

### Implementation notes

- Stdlib only. Sparse representation: `dict[node, list[neighbour]]` or
  `dict[node, dict[neighbour, weight]]`.
- Convergence: ‖PR_t − PR_{t-1}‖_1 < eps (default 1e-6).
- **Hard cap**: 200 iterations regardless of eps (large-repo guard). On cap,
  caller may surface `convergence_warning: true` in the snapshot payload.
- Sum-to-one preserved within float error (~1e-9 on 10k-node graphs).

### Failure modes

- **Disconnected components.** Each receives independent rank mass; both
  groups are scored coherently within themselves.
- **Self-loop on a leaf.** PageRank concentrates on the leaf; treat as a
  pathological hot-spot in advisory text.

---

## G4 — Halstead Volume Metrics

**Reference:** Halstead M.H. (1977), "Elements of Software Science",
Elsevier North-Holland.

**Signature:** `halstead(source: str) -> dict[str, float]`
(keys: `n1, n2, N1, N2, vocabulary, length, volume`).

### Derivation

Given:
- n1 = distinct operators
- n2 = distinct operands
- N1 = total operator occurrences
- N2 = total operand occurrences

Then:
- vocabulary η = n1 + n2
- length N = N1 + N2
- volume V = N · log2(η)

Volume captures the information content needed to encode the program in the
chosen vocabulary. Complementary to G2 — Halstead catches dense
data-shuffling code that McCabe under-weights.

### Implementation notes

- Stdlib `tokenize.generate_tokens` over the source string.
- Operators include: `OP` tokens plus Python control-flow keywords
  (`if, elif, else, for, while, try, except, finally, with, as, return,
  yield, break, continue, pass, import, from, raise, and, or, not, is, in,
  lambda, def, class, global, nonlocal, assert, del, async, await`).
- Operands include: `NAME` (non-keyword), `NUMBER`, `STRING`, f-string parts.
- Comments, indentation tokens, encoding markers excluded.
- Fail-open on `TokenizeError` / `IndentationError` / `SyntaxError` — return
  zeros rather than aborting the snapshot.

### Failure modes

- **Single-token files.** vocabulary = 1 → log2(1) = 0 → volume = 0. Returned
  as-is; not an error.

---

## G5 — Gauss Accumulation: Hotspot-Drift Signature

**Reference:** Gauss C.F. (1809), "Theoria motus corporum coelestium in
sectionibus conicis solem ambientium" (least-squares foundation for
recursive EMA-with-posterior updates). Ecosystem precedent: Wixie F6,
Emu A7, Crow H6, Djinn D5.

**Signature:** `update_posterior(prior: dict, observation: dict, alpha: float = 0.3) -> dict`

### Derivation

Per-(repo × hotspot-kind) drift posterior maintained as an EMA mean and an
EMA-of-squared-deviation variance estimator (Welford-like recurrence on
the EMA — approximate but stable):

    μ_t = (1 − α) · μ_{t−1} + α · x_t
    σ²_t = (1 − α) · σ²_{t−1} + α · (x_t − μ_{t−1})²

with α = 0.3 (half-life ≈ 30 snapshots). Top-N stability is the Jaccard
similarity of the current top-N set to the previous snapshot's top-N.

### Implementation notes

- Stdlib `math.sqrt`. Atomic JSONL append for `learnings.jsonl` via
  `state_io.append_jsonl`.
- Posterior persists in `plugins/gorgon-learning/state/posterior.json` via
  write-tmp-rename through `state_io.atomic_write_json`.

### Failure modes

- **First observation seeds the posterior** with σ = 0 (cannot estimate
  variance from one sample). Subsequent observations accumulate.
- **Cold-start drift.** A new repo's first 3-5 snapshots produce wide bands.
  This is correct — the posterior tells the developer "I do not yet have a
  stable expected envelope".
