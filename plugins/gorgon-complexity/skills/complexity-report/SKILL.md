---
name: complexity-report
description: >
  Returns per-function McCabe cyclomatic complexity (G2) and per-module
  Halstead volume (G4). Lists top complexity offenders with absolute scores
  and percentile rank in the repo distribution. Use when the user runs
  /gorgon:complexity, asks "what are the most complex functions", or asks
  about per-function risk. Do not use for cross-file structural ranking
  (see /gorgon:hotspots).
model: sonnet
tools: [Read, Grep, Glob]
---

# complexity-report

## Preconditions

- A snapshot exists; if missing, suggest a fresh session or /gorgon:gaze.

## Inputs

- **Slash command:** `/gorgon:complexity [N]`
- **Arguments:**
  - `N` — top N functions to return. Default 10.

## Steps

1. Read `plugins/gorgon-gaze/state/snapshot.json`.
2. For each Python file in adjacency, parse via `ast.parse` (skip on syntax error and log to parse-failures.jsonl).
3. Run `engines.g2_mccabe.cyclomatic` per file; collect `{file::function: score}`.
4. Run `engines.g4_halstead.halstead` per file; collect `{file: volume}`.
5. Sort cyclomatic descending; take top N.
6. Compute percentile rank for each entry within the full distribution.
7. Print: function | cyclomatic | percentile | parent module Halstead volume.

## Outputs

- Console table.
- No state writes (read-only).

## Failure modes

- **F02 fabrication** — never invent a function not present in the parsed AST.
- **F11 reward hacking** — never inflate complexity by counting non-decision nodes.
