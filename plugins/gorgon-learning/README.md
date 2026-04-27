# gorgon-learning

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

PreCompact hook that persists the hotspot-drift signature posterior. Owns
engine **G5 Gauss Accumulation**.

## What it does

On PreCompact: read the latest gorgon-gaze snapshot, fold the top-of-distribution
score into the per-(repo x hotspot-kind) posterior via G5, write
`state/posterior.json` atomically and append a `state/learnings.jsonl` row.

## Outputs

- `state/posterior.json` — `{repo: {kind: {median_score, sigma, n_snapshots, top_n_stability, last_seen}}}`.
- `state/learnings.jsonl` — one row per compaction event.
