#!/usr/bin/env bash
# Run every test in tests/ via stdlib unittest discovery.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
python3 -m unittest discover tests/ -v
