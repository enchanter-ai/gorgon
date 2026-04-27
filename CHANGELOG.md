# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-04-25

### Added
- Initial Phase-1 scaffold.
- 5 engines: G1 Tarjan SCC, G2 McCabe cyclomatic, G3 PageRank, G4 Halstead volume, G5 Gauss accumulation.
- 7 plugins: gorgon-gaze, gorgon-watcher, gorgon-hotspots, gorgon-deps, gorgon-complexity, gorgon-learning, full.
- 4 hook bindings: SessionStart, UserPromptSubmit, PostToolUse(Write|Edit|MultiEdit), PreCompact.
- 3 agents: gorgon-watcher (Haiku), gorgon-analyst (Sonnet), gorgon-orchestrator (Opus).
- 4 events published: gorgon.snapshot.captured, gorgon.hotspot.detected, gorgon.cycle.detected, gorgon.snapshot.refreshed.
- Honest-numbers contract: every advisory carries (value, ci_low, ci_high, N).
- 13 inherited shared/conduct modules.
