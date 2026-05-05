# Gorgon

<p align="center">
  <img src="docs/assets/social-preview.jpg" alt="Gorgon mascot" width="1280">
</p>

<p>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-3fb950?style=for-the-badge"></a>
  <img alt="7 plugins" src="https://img.shields.io/badge/Plugins-7-bc8cff?style=for-the-badge">
  <img alt="5 engines" src="https://img.shields.io/badge/Engines-G1%E2%80%93G5-58a6ff?style=for-the-badge">
  <img alt="3 agents" src="https://img.shields.io/badge/Agents-3-d29922?style=for-the-badge">
  <img alt="Phase 1" src="https://img.shields.io/badge/Phase-1-f0883e?style=for-the-badge">
  <a href="https://www.repostatus.org/#active"><img alt="Project Status: Active" src="https://www.repostatus.org/badges/latest/active.svg"></a>
</p>

> **An @enchanter-ai product — algorithm-driven, agent-managed, self-learning.**

Gazes at the repository, freezes its current structure into an immutable snapshot, and surfaces hotspots, cycles, and complexity by structural rank. Passive codebase intelligence — orthogonal to per-change trust (Crow), workflow weaving (Sylph), and intent anchoring (Djinn).

**6 sub-plugins. 5 engines. 3 agents. 3 slash commands. Out-of-context structural snapshot. One install.**

> Session start, **gorgon-gaze** walks 247 `*.py` files in the repo, builds the import adjacency, and runs **G1 Tarjan** + **G3 PageRank** in 0.4s. Snapshot persists atomically to `state/snapshot.json`. Turn 14, the developer edits `plugins/auth/registry.py`. **gorgon-watcher** re-parses the touched file plus its 6 importers and updates the adjacency without a full re-walk. Turn 22, the developer asks `/gorgon:hotspots`. Top result: `plugins/auth/registry.py — score=0.087, CI=(0.071, 0.103), N=247, kind=coupling` — high import-fan-in, low cyclomatic, classic god-module signature. Turn 38, `/compact` fires — **gorgon-learning** computes drift between this snapshot and the prior, updates the per-(repo × hotspot-kind) Gauss posterior in `state/learnings.jsonl`. Next session, the same hotspot scores against a tighter expected envelope.
>
> Time: deterministic, zero per-turn LLM calls on the critical path. Developer effort: read one ranked list.

## TL;DR

**In plain English:** The scariest file in your codebase isn't the 800-line monster. It's the twenty-line one that 200 other files import. Gorgon finds it before it finds you.

**Technically:** G1 Tarjan SCC detects import cycles via iterative O(V+E) traversal over stdlib-`ast` edges stored in `state/snapshot.json`; G3 PageRank power-iteration (damping 0.85) ranks files by import centrality, exposing high-fan-in god-modules invisible to cyclomatic-only tools; G2 McCabe cyclomatic complexity labels each changed function per `PostToolUse`. Every hotspot advisory carries `(score, ci_low, ci_high, N)` from a non-parametric bootstrap — rows without N are rejected and never emitted.

---

## Origin

**Gorgon** takes its name from **Ice and Fire** — the Gorgon, a serpent-haired entity whose petrifying gaze freezes those it sees into immutable stone. That is literally the function of this plugin: gaze at the repository, freeze its current structure into an immutable snapshot, and report back what the structure is.

The question this plugin answers: *What does this codebase actually look like right now?*

## Who this is for

- Architects auditing god-modules — files that look small but have import fan-in from half the codebase, invisible to cyclomatic-only tools.
- Reviewers chasing coupling-driven hotspots before they become production incidents: files ranked high by G3 PageRank centrality are statistically more defect-prone than their line-count suggests.
- Teams whose CI flagged a flaky test in `utils/registry.py` but whose `git log` shows it was only touched twice — Gorgon surfaces structural criticality that churn-based tools miss.

Not for:

- Single-file code review. If the question is "is this function correct?", Gorgon is overhead; run a linter or Crow.
- Mixed-language repos in Phase 1. Static AST parsing covers `*.py` only; non-Python edges are silently absent from the graph — the limitation is surfaced in every advisory, but the signal is incomplete.

## Contents

- [How It Works](#how-it-works)
- [What Makes Gorgon Different](#what-makes-gorgon-different)
- [The Full Lifecycle](#the-full-lifecycle)
- [Install](#install)
- [Quickstart](#quickstart)
- [7 Plugins, 3 Agents](#7-plugins-3-agents)
- [The Science Behind Gorgon](#the-science-behind-gorgon)
- [vs Everything Else](#vs-everything-else)
- [Agent Conduct (13 Modules)](#agent-conduct-13-modules)
- [Architecture](#architecture)
- [License](#license)

## How It Works

On `SessionStart`, **gorgon-gaze** walks `*.py` files in the project root,

<p align="center">
  <a href="docs/assets/pipeline.mmd" title="View pipeline source (Mermaid)">
    <img src="docs/assets/pipeline.svg"
         alt="Gorgon six-subplugin architecture blueprint — Claude Code session input flowing through gorgon-gaze (G1 Tarjan + G3 PageRank full snapshot at SessionStart), gorgon-watcher (G1 + G2 incremental refresh on PostToolUse), three skill-invoked sub-plugins (gorgon-hotspots G3 ranking, gorgon-deps G1 BFS neighbourhood, gorgon-complexity G2 + G4 reports), and gorgon-learning (G5 Gauss hotspot-drift posterior on PreCompact); publishing four gorgon.* events on the enchanted-mcp bus with optional peer-plugin enrichment from Crow and Sylph"
         width="100%" style="max-width: 1100px;">
  </a>
</p>

<sub align="center">

Source: [docs/assets/pipeline.mmd](docs/assets/pipeline.mmd) · Regeneration command in [docs/assets/README.md](docs/assets/README.md).

</sub>

parses each via stdlib `ast`, builds the file-level import adjacency, runs
**G1 Tarjan SCC** (cycle detection, O(V+E) iterative) and **G3 PageRank**
power-iteration (centrality, damping 0.85). The result is persisted
atomically to `plugins/gorgon-gaze/state/snapshot.json`.

On `PostToolUse(Write|Edit)`, **gorgon-watcher** re-parses the touched file
plus its 1-hop importers, updates the adjacency, and recomputes **G2 McCabe
cyclomatic** on the changed functions. Dirty nodes accumulate for the next
gaze.

On `PreCompact`, **gorgon-learning** folds the snapshot's drift signature
into the per-(repo × hotspot-kind) posterior via **G5 Gauss Accumulation**.

On demand: `/gorgon:hotspots`, `/gorgon:deps <file>`, `/gorgon:complexity` —
each reads the snapshot and returns ranked, CI-banded answers.

## What Makes Gorgon Different

### Structural coupling is explicit, not approximated

LangChain CodeSplitter and LlamaIndex code-RAG split files by character window and retrieve by vector cosine. Cross-file coupling — function A in module M imports function B in module N — collapses to nearest-neighbour similarity, which is not a graph property. Hotspots that emerge from import fan-in are invisible. Gorgon's G1 Tarjan SCC operates on **explicit AST import edges** (`Import`/`ImportFrom`). Cycles are detected, not approximated.

### Analysis runs out of context, not through it

AutoGPT and BabyAGI "explore the codebase" loops read every file at session start, flood 200k tokens into context, then forget the first 50 files by the time they process the last 50 (Liu et al. "Lost in the Middle", NAACL 2024). Gorgon **never feeds source to the agent**. SessionStart runs deterministic AST analysis into `state/snapshot.json`; advisories cite hotspots by `(path, score, CI, N)` — not by re-injecting source.

### Hotspot kind is labelled, not collapsed

SonarQube, lizard, and radon rank by cyclomatic complexity alone. A 20-line file imported by 200 others is a far higher-risk hotspot than a 200-line file imported by nothing — but cyclomatic ranks them in reverse. Gorgon labels `hotspot_kind ∈ {complexity, coupling, churn-magnet}` explicitly and combines **G2 McCabe + G3 PageRank**. Both axes survive into every advisory.

### Ranking is recency-blind by construction

ChatGPT and Cursor "explain this codebase" sessions bias toward the README, top-of-file docstrings, and recently-touched files. Silent god-modules with high centrality and no documentation never surface. G3 PageRank centrality is computed over the static import graph; under-documented files score high precisely because import fan-in is unaffected by docstring presence or recent edits.

### Honest numbers, or no numbers

Every advisory carries `(score, ci_low, ci_high, N)` from a non-parametric bootstrap. Missing N → the row is rejected, never emitted with an invented confidence band.

## The Full Lifecycle

Gorgon is **hook-driven for capture** and **skill-invoked for query**. No phase blocks tool completion.

<p align="center">
  <a href="docs/assets/lifecycle.mmd" title="View lifecycle source (Mermaid)">
    <img src="docs/assets/lifecycle.svg"
         alt="Gorgon hook lifecycle blueprint — five phases: 1 GAZE (SessionStart full *.py walk + G1 Tarjan SCC + G3 PageRank into atomic snapshot.json), 2 WATCH (PostToolUse Write|Edit re-parse touched file + 1-hop importers + G2 cyclomatic recount), 3 QUERY (UserPromptSubmit or skill invocation: /gorgon:hotspots G3 ranking, /gorgon:deps G1 BFS, /gorgon:complexity G2 + G4 report), 4 LEARN (PreCompact G5 Gauss posterior update with top-N stability across snapshots), 5 NEXT-SESSION (tighter expected hotspot envelope per-(repo × hotspot-kind))"
         width="100%" style="max-width: 1100px;">
  </a>
</p>

<sub align="center">

Source: [docs/assets/lifecycle.mmd](docs/assets/lifecycle.mmd) · Regeneration command in [docs/assets/README.md](docs/assets/README.md).

</sub>


| Phase | Event or Skill | Sub-plugin | Engines | Output |
|-------|----------------|------------|---------|--------|
| Capture | SessionStart | `gorgon-gaze` | G1 + G3 | `state/snapshot.json`; `gorgon.snapshot.captured` |
| Refresh | UserPromptSubmit | `gorgon-gaze` | G1 | appended snapshot delta; `gorgon.snapshot.refreshed` |
| Watch | PostToolUse (Write\|Edit) | `gorgon-watcher` | G1 + G2 | dirty-node list; `gorgon.hotspot.detected` |
| Learn | PreCompact | `gorgon-learning` | G5 | `state/posterior.json`, `state/learnings.jsonl` |
| Query — hotspots | `/gorgon:hotspots` | `gorgon-hotspots` | G3 | ranked table with bootstrap CI |
| Query — deps | `/gorgon:deps <file>` | `gorgon-deps` | G1 | 1-hop / 2-hop neighbourhood |
| Query — complexity | `/gorgon:complexity` | `gorgon-complexity` | G2 + G4 | per-function McCabe + per-module Halstead |

Every capture phase is hook-driven and fail-open. Every query phase is skill-invoked on demand.

## Install

```
/plugin marketplace add enchanter-ai/gorgon
/plugin install full@gorgon
```

Or cherry-pick: `/plugin install gorgon-hotspots@gorgon`.

## Quickstart

```
/plugin install full@gorgon
/gorgon:hotspots 7
```

Expected: a table of the top-7 PageRank-ranked Python files with
`(score, ci_low, ci_high, N, hotspot_kind)`.

## 7 Plugins, 3 Agents

| Plugin              | Trigger                       | Engines     | Agent (tier)                |
|---------------------|-------------------------------|-------------|------------------------------|
| gorgon-gaze         | SessionStart, UserPromptSubmit | G1, G3      | (none — pure compute)        |
| gorgon-watcher      | PostToolUse(Write\|Edit)      | G1, G2      | gorgon-watcher (Haiku)       |
| gorgon-hotspots     | /gorgon:hotspots              | G3          | gorgon-analyst (Sonnet) + gorgon-orchestrator (Opus) |
| gorgon-deps         | /gorgon:deps                  | G1          | (none — pure read)           |
| gorgon-complexity   | /gorgon:complexity            | G2, G4      | (none — pure compute)        |
| gorgon-learning     | PreCompact                    | G5          | (none — pure compute)        |
| full                | meta                          | —           | —                            |

## What You Get Per Session

Every `SessionStart` rebuilds the import-graph snapshot; every `PostToolUse(Write|Edit)` refreshes the affected node + 1-hop importers; every `PreCompact` folds a drift summary into the cross-session posterior. All writes go through the atomic `shared/scripts/state_io.atomic_write_json` helper.

```
plugins/gorgon-gaze/state/
└── snapshot.json              full repo import-adjacency + G1 SCCs + G3 PageRank scores

plugins/gorgon-watcher/state/
└── dirty-nodes.jsonl          append-only log of files whose adjacency was refreshed mid-session

plugins/gorgon-learning/state/
├── posteriors.json            per-(repo × hotspot-kind) hotspot-drift posterior (G5 EMA)
└── learnings.jsonl            per-snapshot append-only drift summary (backtesting source)

plugins/gorgon-hotspots/state/
└── last-report.json           most recent /gorgon:hotspots output

plugins/gorgon-complexity/state/
└── last-report.json           most recent /gorgon:complexity output
```

Events published on the `gorgon.*` namespace (Phase-1 file-tail fallback via shared `publish.py`):

- `gorgon.snapshot.captured` — `{session_id, repo_root, file_count, edge_count, captured_at}`
- `gorgon.hotspot.detected` — `{file, score, ci_low, ci_high, N, rank, hotspot_kind}`
- `gorgon.cycle.detected` — `{scc_members, edges, severity}`
- `gorgon.snapshot.refreshed` — `{session_id, dirty_nodes, turn}`

Optional subscriptions (Phase-2 enrichment): `crow.change.classified`, `sylph.workflow.classified`.

## Roadmap

Tracked in [docs/ROADMAP.md](docs/ROADMAP.md) and the shared [ecosystem map](https://github.com/enchanter-ai/wixie/blob/main/docs/ecosystem.md). For upcoming work specific to Gorgon, see issues tagged [roadmap](https://github.com/enchanter-ai/gorgon/labels/roadmap).

## The Science Behind Gorgon

| ID | Name                                  | Reference                                                                              |
|----|---------------------------------------|----------------------------------------------------------------------------------------|
| G1 | Tarjan Strongly-Connected-Components  | Tarjan R.E. (1972), SIAM J. Computing 1(2):146-160                                     |
| G2 | McCabe Cyclomatic Complexity          | McCabe T.J. (1976), IEEE TSE SE-2(4):308-320                                           |
| G3 | PageRank                              | Brin S. & Page L. (1998), Computer Networks 30(1-7):107-117                            |
| G4 | Halstead Volume                       | Halstead M.H. (1977), "Elements of Software Science", Elsevier North-Holland           |
| G5 | Gauss Accumulation                    | Gauss C.F. (1809), "Theoria motus corporum coelestium" (least-squares foundation)      |

Full derivations: [`docs/science/README.md`](docs/science/README.md).

## vs Everything Else

Honest comparison against adjacent tools.

| Feature                                | Gorgon | LangChain CodeSplitter | SonarQube | Cursor index | Crow (sibling) |
|----------------------------------------|:------:|:----------------------:|:---------:|:------------:|:--------------:|
| Explicit AST import-edge graph         |   ✓    |           —            |     ✓     |      ✓       |       —        |
| Centrality (PageRank) ranking          |   ✓    |           —            |     —     |      —       |       —        |
| Per-(file) bootstrap 95% CI            |   ✓    |           —            |     —     |      —       |       —        |
| Hotspot-kind labels (not collapsed)    |   ✓    |           —            |     —     |      —       |       —        |
| Per-change trust scores                |   —    |           —            |     —     |      —       |       ✓        |
| Dependencies                           | stdlib |        Python+vec DB    |    JVM    |   binary     |    bash+jq     |

Gorgon answers a structural question that adjacent tools either don't ask or
collapse into a single number.

## Agent Conduct (13 Modules)

Every skill inherits a reusable behavioral contract from
[shared/conduct/](shared/conduct/) — loaded once into [CLAUDE.md](CLAUDE.md),
applied across all plugins.

| Module                         | What it governs                                                            |
|--------------------------------|----------------------------------------------------------------------------|
| [discipline.md](shared/conduct/discipline.md) | think-first, simplicity, surgical edits, goal-driven loops |
| [context.md](shared/conduct/context.md)       | attention-budget hygiene, U-curve, checkpoint protocol     |
| [verification.md](shared/conduct/verification.md) | baseline snapshots, dry-run, post-change diff read-back |
| [delegation.md](shared/conduct/delegation.md)     | subagent contracts, tool whitelisting, parallel rules    |
| [failure-modes.md](shared/conduct/failure-modes.md) | F01-F14 taxonomy                                       |
| [tool-use.md](shared/conduct/tool-use.md)         | right-tool-first-try, parallel vs. serial               |
| [formatting.md](shared/conduct/formatting.md)     | XML/Markdown/minimal/few-shot, prefill + stop seq.      |
| [skill-authoring.md](shared/conduct/skill-authoring.md) | SKILL.md frontmatter discipline                    |
| [hooks.md](shared/conduct/hooks.md)               | advisory-only, injection over denial, fail-open         |
| [precedent.md](shared/conduct/precedent.md)       | log self-observed failures, consult before risky steps  |
| [tier-sizing.md](shared/conduct/tier-sizing.md)   | Opus intent-level, Sonnet decomposed, Haiku step-by-step|
| [web-fetch.md](shared/conduct/web-fetch.md)       | WebFetch is Haiku-tier-only; cache and budget           |
| [inference-substrate.md](shared/conduct/inference-substrate.md) | inference-engine emit-only contract        |

## Architecture

`docs/architecture/` — Phase 2 will host auto-generated mermaid diagrams.

## Acknowledgments

- **Tarjan R.E.** — the 1972 strongly-connected-components algorithm underpinning G1.
- **McCabe T.J.** — the 1976 cyclomatic complexity measure underpinning G2.
- **Brin S. and Page L.** — the 1998 PageRank paper underpinning G3.
- **Halstead M.H.** — the 1977 software-science volume metrics underpinning G4.
- **Gauss C.F.** — the 1809 least-squares foundation underpinning G5.
- **Liu et al.** — "Lost in the Middle" (NAACL 2024) — documented the recall valley that justifies the out-of-context snapshot design.
- **Sourcegraph** — the 2022 "What is a code hotspot" retrospective that documented the limits of single-axis hotspot ranking.
- **Alex Modder and Raptorfarian** — Ice and Fire (2018) — the Minecraft mod whose Gorgon entity gave this plugin its name and metaphor.
- **@enchanter-ai** siblings — Wixie, Emu, Crow, Hydra, Lich, Sylph, Pech, Djinn, Naga — for the canonical template, the event-bus pattern, and the ecosystem contract.

## Versioning & release cadence

Gorgon follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Breaking changes to engine signatures, event payloads, or the honest-numbers tuple shape bump the major version. Additive engines or sub-plugins bump the minor. Bug fixes bump the patch. See [CHANGELOG.md](CHANGELOG.md) for the running history.

## Contributing

Pull requests welcome. Key rules:

- Do not edit `shared/conduct/*.md` in a Gorgon PR; raise the change in the [schematic](https://github.com/enchanter-ai/schematic) repo so it propagates to every sibling.
- Every new engine needs an Author-Year docstring citation and a `docs/science/README.md` section.
- Every hook script opens with the subagent-loop guard and exits 0 fail-open.
- Honest-numbers contract on every advisory: no N, no advisory.
- Stdlib only — no `pip install`, no tree-sitter, no networkx. Run `python -m unittest discover tests/` before opening the PR.

## Citation

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

```
@software{gorgon_2026,
  title   = {Gorgon: Static codebase intelligence for long-horizon Claude Code sessions},
  author  = {{enchanter-ai}},
  year    = {2026},
  url     = {https://github.com/enchanter-ai/gorgon},
  license = {MIT}
}
```

## License

MIT — see [LICENSE](LICENSE).

---

## Role in the ecosystem

Gorgon closes the C-class structural-intelligence gap. Crow scores trust in
*what changed* (per-file Beta-Bernoulli). Gorgon maps *what exists* (the
static structural graph at this moment). Sylph weaves git history (workflow
patterns over time). Gorgon analyses the current static snapshot only. The
signals are orthogonal — they must not be merged.
