# gorgon-hotspots

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

Top-N hotspot ranking with bootstrap 95% CI per file. Owns engine **G3 PageRank**.

## Slash command

```
/gorgon:hotspots [N]
```

Reads `plugins/gorgon-gaze/state/snapshot.json` and returns the top-N files
ranked by PageRank centrality, each with `(score, ci_low, ci_high, N, hotspot_kind)`.

## Events

**Publishes:** `gorgon.hotspot.detected` (one per surfaced hotspot).
