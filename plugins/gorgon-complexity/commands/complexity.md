---
description: Per-function McCabe cyclomatic + per-module Halstead volume report.
---

# /gorgon:complexity

Returns the top-N most complex functions by McCabe cyclomatic, alongside the
parent module's Halstead volume.

## Usage

```
/gorgon:complexity [N]
```

## Arguments

| Argument | Type | Default | Purpose |
|----------|------|---------|---------|
| N        | int  | 10      | Top-N functions to return. |

## Example

```
/gorgon:complexity 20
```

## Invokes

This command invokes the `complexity-report` skill. See
[../skills/complexity-report/SKILL.md](../skills/complexity-report/SKILL.md).
