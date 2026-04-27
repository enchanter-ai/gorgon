---
description: Return 1-hop and 2-hop dependency neighbourhood of a file (both directions).
---

# /gorgon:deps

Returns the 1-hop and 2-hop dependency neighbourhood of a given file in both
directions: files that the target imports, and files that import the target.

## Usage

```
/gorgon:deps <file>
```

## Arguments

| Argument | Type   | Default | Purpose |
|----------|--------|---------|---------|
| file     | string | —       | Relative path within the repo. |

## Example

```
/gorgon:deps src/core/registry.py
```

## Invokes

This command invokes the `deps-query` skill. See
[../skills/deps-query/SKILL.md](../skills/deps-query/SKILL.md).
