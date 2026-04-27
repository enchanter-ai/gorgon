# gorgon-gaze

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

Captures the initial codebase snapshot on SessionStart and refreshes on
UserPromptSubmit when the snapshot is older than 10 minutes. Owns engines
**G1 Tarjan SCC** and **G3 PageRank**.

## What it does

Walks `*.py` files in the project root, parses each via stdlib `ast`, builds
the file-level import adjacency, then runs Tarjan SCC (G1) and PageRank
power-iteration (G3). Persists `state/snapshot.json` atomically.

## Inputs

- SessionStart hook payload (no fields required).
- UserPromptSubmit hook payload (refresh trigger).

## Outputs

- `state/snapshot.json` — `{captured_at, repo_root, file_count, edge_count, scc_count, ranks, ...}`.
- `state/parse-failures.jsonl` — per-file parse errors (continuation, not abort).

## Events

**Publishes:** `gorgon.snapshot.captured`, `gorgon.cycle.detected`.
