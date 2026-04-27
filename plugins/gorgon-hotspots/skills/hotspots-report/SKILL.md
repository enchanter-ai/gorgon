---
name: hotspots-report
description: >
  Returns the top-N hotspot ranking with bootstrap 95% CI per file. Reads the
  current snapshot at plugins/gorgon-gaze/state/snapshot.json. Use when the
  user runs /gorgon:hotspots, asks "which files matter most", or asks "where
  is the structural risk in this codebase". Do not use for per-function
  complexity (see /gorgon:complexity) or for dependency neighbourhoods
  (see /gorgon:deps).
model: sonnet
tools: [Read, Grep, Glob]
---

# hotspots-report

## Preconditions

- `plugins/gorgon-gaze/state/snapshot.json` exists. If not, the user is told
  to start a new session (gaze runs on SessionStart) and the skill exits.

## Inputs

- **Slash command:** `/gorgon:hotspots [N]`
- **Arguments:**
  - `N` — top N files to return. Default 7. Cap 50.

## Steps

1. Read `plugins/gorgon-gaze/state/snapshot.json` (Read tool). If missing, return advisory: "no snapshot — start a new session or run /gorgon:gaze".
2. Sort `snapshot.ranks` descending; take top N.
3. For each file in top N, compute bootstrap CI from a per-file sample of the snapshot's per-function complexity values. Pass through `shared/scripts/bootstrap_ci.py`.
4. Spawn the gorgon-analyst Sonnet agent (via Agent tool) with the top-N files; receive `hotspot_kind` per file.
5. Spawn the gorgon-orchestrator Opus agent with the labelled set; receive the final ranked advisory.
6. Print the advisory table to the user (file | score | CI | N | kind | rationale).

## Outputs

- Console table for the user.
- No state writes.

## Handoff

If the user asks to drill into a file, hand off to `/gorgon:deps <file>` or
`/gorgon:complexity`.

## Failure modes

- **F02 fabrication** — never invent a hotspot not in the snapshot.
- **F11 reward hacking** — never weaken the honest-numbers gate to surface
  more files; if `N` is missing on a candidate, drop it.
