# gorgon-deps

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

> **Status: unsupported / not yet wired.** `gorgon-gaze` computes the import
> adjacency in memory but only persists `ranks` (plus summary counts) to
> `snapshot.json` — the edge list itself is never written to disk. There is
> currently nothing in the snapshot for this skill's "build the reverse
> adjacency from the snapshot" step to read. Do not rely on `/gorgon:deps`
> until the snapshot schema is extended to persist edges.

1-hop and 2-hop dependency neighbourhood query for a file. Owns engine **G1 Tarjan SCC** (uses the adjacency built by gorgon-gaze).

## Slash command

```
/gorgon:deps <file>
```

Returns `imports_1hop`, `imports_2hop`, `importers_1hop`, `importers_2hop` for
the requested file.
