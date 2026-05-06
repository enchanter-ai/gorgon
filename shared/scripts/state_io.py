"""
state_io.py — atomic write-tmp-rename persistence helpers.

Every JSON state file in Gorgon goes through `atomic_write_json`. No direct
open('w') on state paths, ever. See `shared/foundations/conduct/verification.md` and
Djinn's state_io.py for the invariant this enforces.

JSONL appends go through `append_jsonl`, which is locked + flushed via
`append_jsonl_locked` so concurrent writers (e.g., gorgon-watcher
PostToolUse + gorgon-learning pre-compact) cannot interleave bytes.

Stdlib only.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path | str, data: Any) -> None:
    """Atomically write `data` as JSON to `path` via write-tmp-rename.

    - Creates parent dirs if missing.
    - Writes to a temp file in the same directory (so rename is atomic on POSIX and Windows).
    - fsyncs the temp file before rename.
    - Never partial-writes the destination.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=p.name + ".",
        suffix=".tmp",
        dir=str(p.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, separators=(",", ":"), ensure_ascii=False)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, p)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def read_json(path: Path | str, default: Any = None) -> Any:
    """Read JSON; return `default` if the file is missing or malformed."""
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def append_jsonl_locked(path: Path | str, line: str) -> None:
    """Append one JSON line, locked + flushed. Cross-platform.

    Holds an exclusive lock for the duration of the write so concurrent
    writers cannot interleave bytes. Honest-numbers contract for posterior
    updates depends on this — see audit F-016 / `shared/conduct/inference-substrate.md`.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if not line.endswith("\n"):
        line += "\n"
    with p.open("a", encoding="utf-8") as f:
        if sys.platform == "win32":
            import msvcrt
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            finally:
                try:
                    f.seek(0)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
        else:
            import fcntl
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def append_jsonl(path: Path | str, record: dict) -> None:
    """JSONL append, locked + fsynced. Fail-open: never raises to the caller."""
    try:
        line = json.dumps(record, separators=(",", ":"))
        append_jsonl_locked(Path(path), line)
    except OSError:
        pass
