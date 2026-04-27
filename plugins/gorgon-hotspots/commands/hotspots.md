---
description: Return top-N hotspot ranking with bootstrap 95% CI per file.
---

# /gorgon:hotspots

Returns the top-N hotspots in the current snapshot — file path, PageRank score,
bootstrap 95% CI, sample count N, and a hotspot-kind label.

## Usage

```
/gorgon:hotspots [N]
```

## Arguments

| Argument | Type | Default | Purpose |
|----------|------|---------|---------|
| N        | int  | 7       | Top-N files to return. Cap 50. |

## Example

```
/gorgon:hotspots 5
```

Reads `plugins/gorgon-gaze/state/snapshot.json` and returns the five highest
PageRank-scored files with bootstrap 95% CI bands and labelled hotspot kinds.

## Invokes

This command invokes the `hotspots-report` skill. See
[../skills/hotspots-report/SKILL.md](../skills/hotspots-report/SKILL.md).
