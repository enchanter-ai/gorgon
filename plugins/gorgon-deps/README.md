# gorgon-deps

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

1-hop and 2-hop dependency neighbourhood query for a file. Owns engine **G1 Tarjan SCC** (uses the adjacency built by gorgon-gaze).

## Slash command

```
/gorgon:deps <file>
```

Returns `imports_1hop`, `imports_2hop`, `importers_1hop`, `importers_2hop` for
the requested file.
