---
name: deps-query
description: >
  Returns the 1-hop and 2-hop dependency neighbourhood of a given file in
  both directions (imports it depends on, importers that depend on it).
  Reads plugins/gorgon-gaze/state/snapshot.json. Use when the user runs
  /gorgon:deps <file>, asks "what depends on X", or asks "what does X
  import". Do not use for cross-file complexity (see /gorgon:complexity).
model: sonnet
tools: [Read, Grep, Glob]
---

# deps-query

## Preconditions

- `plugins/gorgon-gaze/state/snapshot.json` exists.
- Caller passed a `file` argument that exists in the snapshot's adjacency.

## Inputs

- **Slash command:** `/gorgon:deps <file>`
- **Arguments:**
  - `file` — relative path within the repo.

## Steps

1. Read `plugins/gorgon-gaze/state/snapshot.json`.
2. Build the reverse adjacency on the fly (snapshot stores forward edges only).
3. Collect 1-hop importers (rev-adj[file]) and 1-hop imports (fwd-adj[file]).
4. Collect 2-hop sets by one more iteration; deduplicate against the 1-hop sets.
5. Return four lists: `imports_1hop`, `imports_2hop`, `importers_1hop`, `importers_2hop`.

## Outputs

- Console listing per direction (max 50 per list, with truncation note).
- No state writes.

## Failure modes

- **F02 fabrication** — never invent an edge that is not in the snapshot.
- **F04 task drift** — if the user asks "and fix X" — hand back to gorgon-orchestrator,
  do not do it.
