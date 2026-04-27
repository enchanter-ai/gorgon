# gorgon-watcher

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

Per-edit incremental refresh of the touched file plus its 1-hop importers.
Owns engines **G1 Tarjan SCC** (incremental update) and **G2 McCabe Cyclomatic
Complexity** (per-function recount).

## What it does

PostToolUse(Write|Edit|MultiEdit) hook re-parses the touched Python file and
records dirty nodes for the next gaze. Recomputes G2 cyclomatic on the
changed functions and stores the result in `state/dirty.json`.

## Inputs

- PostToolUse hook payload with `tool_input.file_path`.

## Outputs

- `state/dirty.json` — `{dirty_nodes, updated_at, last_file, last_cyclomatic}`.

## Events

**Publishes:** `gorgon.snapshot.refreshed`.
