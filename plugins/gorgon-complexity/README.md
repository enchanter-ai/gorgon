# gorgon-complexity

*Part of [Gorgon](../../README.md) — passive structural intelligence for the current snapshot.*

Per-function McCabe + per-module Halstead report. Owns engines **G2 McCabe**
and **G4 Halstead Volume**.

## Slash command

```
/gorgon:complexity [N]
```

Returns the top-N most complex functions by McCabe cyclomatic, plus the
parent module's Halstead volume and the function's percentile rank.
