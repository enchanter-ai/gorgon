# Gorgon — Agent Contract

Audience: Claude. Gorgon gazes at the repository, freezes its current
structure into an immutable snapshot, and surfaces hotspots, cycles, and
complexity by structural rank. Passive codebase intelligence — orthogonal
to per-change trust (Crow), workflow weaving (Sylph), and intent anchoring
(Djinn).

## Shared behavioral modules

These apply to every skill in every plugin. Load once; do not re-derive.

- @shared/foundations/conduct/discipline.md — coding conduct: think-first, simplicity, surgical edits, goal-driven loops
- @shared/foundations/conduct/context.md — attention-budget hygiene, U-curve placement, checkpoint protocol
- @shared/foundations/conduct/verification.md — independent checks, baseline snapshots, dry-run for destructive ops
- @shared/foundations/conduct/delegation.md — subagent contracts, tool whitelisting, parallel vs. serial rules
- @shared/foundations/conduct/failure-modes.md — 14-code taxonomy for accumulated-learning logs
- @shared/foundations/conduct/doubt-engine.md — adversarial self-check before agreement; active counter to F01 sycophancy
- @shared/foundations/conduct/tool-use.md — tool-choice hygiene, error payload contract, parallel-dispatch rules
- @shared/foundations/conduct/formatting.md — per-target format (XML/Markdown/minimal/few-shot), prefill + stop sequences
- @shared/foundations/conduct/skill-authoring.md — SKILL.md frontmatter discipline, discovery test
- @shared/foundations/conduct/hooks.md — advisory-only hooks, injection over denial, fail-open
- @shared/foundations/conduct/precedent.md — log self-observed failures to `state/precedent-log.md`; consult before risky steps
- @shared/foundations/conduct/tier-sizing.md — Opus intent-level, Sonnet decomposed, Haiku senior-to-junior
- @shared/foundations/conduct/web-fetch.md — WebFetch is Haiku-tier-only; cache and budget
- @shared/conduct/inference-substrate.md — emit-only contract for the Wixie inference engine

When a module conflicts with a plugin-local instruction, the plugin wins — but log the override.

## Lifecycle

Gorgon is **hook-driven** for capture (gorgon-gaze, gorgon-watcher, gorgon-learning)
and **skill-invoked** for query (gorgon-hotspots, gorgon-deps, gorgon-complexity).
Each capture writes to plugin-local `state/`; each query reads from
`plugins/gorgon-gaze/state/snapshot.json`.

| Event or Skill              | Sub-plugin         | Role                                                                 |
|-----------------------------|--------------------|----------------------------------------------------------------------|
| SessionStart                | gorgon-gaze        | Capture initial snapshot (G1 + G3) into state/snapshot.json          |
| UserPromptSubmit            | gorgon-gaze        | Refresh snapshot if stale (subagent-guarded)                         |
| PostToolUse (Write\|Edit)   | gorgon-watcher     | Re-parse touched file + 1-hop importers (G1 + G2)                    |
| PreCompact                  | gorgon-learning    | Update G5 hotspot-drift posterior + append learnings.jsonl           |
| /gorgon:hotspots            | gorgon-hotspots    | Top-N ranking with bootstrap CI                                      |
| /gorgon:deps `<file>`       | gorgon-deps        | 1-hop / 2-hop neighbourhood (both directions)                        |
| /gorgon:complexity          | gorgon-complexity  | Per-function McCabe + per-module Halstead                            |

See `./plugins/<name>/hooks/hooks.json` for matchers. Agents in `./shared/agents/`.

## Algorithms

G1 Tarjan SCC · G2 McCabe Cyclomatic · G3 PageRank Hotspot Ranking ·
G4 Halstead Volume · G5 Gauss Accumulation (drift signature). Derivations
in `docs/science/README.md`. **Defining engine:** G3 PageRank.

| ID | Name                                  | Plugin               | Algorithm |
|----|---------------------------------------|----------------------|-----------|
| G1 | Tarjan Strongly-Connected-Components  | gorgon-gaze, gorgon-deps | Iterative Tarjan over `dict[str, list[str]]` adjacency, O(V+E). |
| G2 | McCabe Cyclomatic Complexity          | gorgon-watcher, gorgon-complexity | AST decision-node count: `If`, `For`, `While`, `Try`, `ExceptHandler`, `BoolOp`, `IfExp`, `Assert`, comprehensions. |
| G3 | PageRank Symbol-Graph Hotspot Ranking | gorgon-gaze, gorgon-hotspots | Power-iteration on sparse adjacency, damping 0.85, eps 1e-6, max-iter 200. |
| G4 | Halstead Volume Metrics               | gorgon-complexity    | `tokenize`-driven operator/operand counts; V = (N1+N2)·log2(n1+n2). |
| G5 | Gauss Accumulation: Hotspot-Drift     | gorgon-learning      | EMA mean + EMA variance with sample-count tracked alongside posterior. |

## Behavioral contracts

Markers: **[H]** hook-enforced (deterministic) · **[A]** advisory (relies on your adherence).

1. **IMPORTANT — Honest-numbers contract on every advisory.** [A] Every emitted
   `gorgon.hotspot.detected` event and every `/gorgon:hotspots` row carries
   `(score, ci_low, ci_high, N)`. Missing N → reject the row, never inflate.
2. **YOU MUST scope to Python in Phase 1.** [A] Static AST parsing uses stdlib
   `ast` and `tokenize` — Python only. Mixed-language repos: surface the
   limitation in the advisory; do NOT silently ignore non-`*.py` files.
3. **YOU MUST NOT collapse hotspot kinds.** [A] `complexity`, `coupling`, and
   `churn-magnet` are orthogonal. Never blend into a single number — the
   developer needs the kind label to know what action applies.

## State paths

| State file                                              | Owner             | Purpose                                                |
|---------------------------------------------------------|-------------------|--------------------------------------------------------|
| `plugins/gorgon-gaze/state/snapshot.json`               | gorgon-gaze       | Captured import graph + Tarjan + PageRank output       |
| `plugins/gorgon-gaze/state/parse-failures.jsonl`        | gorgon-gaze       | Per-file AST parse errors (continuation, not abort)    |
| `plugins/gorgon-watcher/state/dirty.json`               | gorgon-watcher    | Dirty-node list + last per-file cyclomatic recount     |
| `plugins/gorgon-learning/state/posterior.json`          | gorgon-learning   | G5 per-(repo × hotspot-kind) drift posterior           |
| `plugins/gorgon-learning/state/learnings.jsonl`         | gorgon-learning   | Append-only compaction-event log                       |
| `plugins/<sub>/state/precedent-log.md`                  | per sub-plugin    | Self-observed operational failures (see @shared/foundations/conduct/precedent.md) |

## Agent tiers

| Tier         | Model  | Used for                                                          |
|--------------|--------|-------------------------------------------------------------------|
| Orchestrator | Opus   | Final advisory composition (gorgon-orchestrator)                  |
| Executor     | Sonnet | Hotspot-kind labelling (gorgon-analyst)                           |
| Validator    | Haiku  | Per-edit AST shape check (gorgon-watcher)                         |

Respect the tiering. Routing a Haiku validation task to Opus burns budget and breaks the cost contract.

## Anti-patterns

- **Vector-similarity over AST chunks.** LangChain CodeSplitter / LlamaIndex
  CodeSplitter style. Cross-file relations collapse to nearest-neighbour cosine
  and hotspots that emerge from coupling become invisible. Counter: G1 + G3
  operate on explicit AST-resolved import edges.
- **Read-everything-into-context.** AutoGPT / BabyAGI "explore the codebase"
  loops flood 200k tokens then forget the long tail. Counter: Gorgon never
  feeds source to the agent; it computes deterministically out of context and
  cites by `(path, score, CI, N)`.
- **Single-metric collapse.** Cyclomatic alone, churn alone, centrality alone.
  A 20-line file imported by 200 others is a higher-risk hotspot than a
  200-line file imported by nothing — but cyclomatic ranks them in reverse.
  Counter: G2 + G3 + G4 ship combined with explicit `hotspot_kind` labels;
  no single rank-collapse.

---

## Brand invariants (survive unchanged into every sibling)

1. **Zero external runtime deps.** Hooks: bash + jq only. Scripts: Python 3.8+ stdlib only. No npm/pip/cargo at runtime.
2. **Managed agent tiers.** Opus = orchestrator/judgment. Sonnet = executor/loops. Haiku = validator/format.
3. **Named formal algorithm per engine.** ID prefix letter + number. Academic-style citation in the docstring.
4. **Emu-style marketplace.** Each sub-plugin ships `.claude-plugin/plugin.json` + `{agents,commands,hooks,skills,state}/` + `README.md`.
5. **Dark-themed PDF report.** Produced by `docs/architecture/generate.py` (Phase 2).
6. **Gauss Accumulation learning.** Per-session learnings at `plugins/gorgon-learning/state/posterior.json`.
7. **enchanted-mcp event bus.** Inter-plugin coordination via published/subscribed events namespaced `gorgon.<event>`.
8. **Diagrams from source of truth.** `docs/architecture/generate.py` (Phase 2) reads `plugin.json` + `hooks.json` + `SKILL.md` frontmatter.

Events this plugin publishes: `gorgon.snapshot.captured`, `gorgon.hotspot.detected`, `gorgon.cycle.detected`, `gorgon.snapshot.refreshed`.
Events this plugin subscribes to (optional): `crow.change.classified`, `sylph.workflow.classified`.
