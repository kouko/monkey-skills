#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Shared filesystem primitives for durable (non-cache) local stores under
skills/analysis-kpi/scripts/ (Rule-of-Three extract: kpi_store.py +
review_queue.py + a third durable store share this same pattern, so it is
now a standalone module rather than duplicated per file — see
docs/loom/memory/durable-store-mirrors-cache-util-not-imports-it.md for
why it still does NOT import data-markets/scripts/cache_util.py: a
durable store roots under the DATA dir and never expires, unlike
cache_util's evictable cache dir).

Provides: `resolve_store_dir` (DATA-dir resolution ladder), the
`_UNSAFE_KEY_CHARS` path-safety sanitize regex, `_atomic_write`
(tmp+rename), and `_acquire_series_lock` / `_release_series_lock`
(per-path `fcntl.flock` guarding a full read-modify-write cycle).
Moved verbatim out of kpi_store.py — behavior is byte-identical.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover — non-POSIX host (e.g. Windows)
    fcntl = None

_warned_no_fcntl = False

# Mirrors cache_util._UNSAFE_KEY_CHARS: any char outside [A-Za-z0-9_-] is
# replaced with `_`, so a company/kpi_id can never escape the store dir via
# `../` or a path separator.
_UNSAFE_KEY_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


def resolve_store_dir() -> Path:
    """Resolve the durable DATA dir for the KPI store.

    Precedence ladder (highest to lowest):
      1. KPI_STORE_DIR env var (stripped; empty after strip = unset) — test
         override + explicit operator control.
      2. $XDG_DATA_HOME/investing-toolkit/kpi-store (only if XDG_DATA_HOME
         set + non-empty).
      3. ~/.local/share/investing-toolkit/kpi-store (default).

    A DATA dir, NOT cache_util's cache dir: a bitemporal series is
    irreplaceable history that must survive cache eviction.
    """
    override = os.environ.get("KPI_STORE_DIR", "").strip()
    if override:
        return Path(override)

    xdg_data_home = os.environ.get("XDG_DATA_HOME", "").strip()
    if xdg_data_home:
        return Path(xdg_data_home) / "investing-toolkit" / "kpi-store"

    return Path.home() / ".local" / "share" / "investing-toolkit" / "kpi-store"


def _atomic_write(path: Path, envelope: dict) -> None:
    """Write the series envelope atomically (tmp + rename), mirroring
    cache_util.save_cache's write pattern (:225).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=str(path.parent),
        prefix=f".{path.name}.", suffix=".tmp", delete=False,
    ) as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2)
        tmp = Path(f.name)
    tmp.rename(path)


def _acquire_series_lock(series_path: Path):
    """Open (creating if absent) a STABLE per-series lock file and take an
    exclusive `fcntl.flock` on it, to guard the FULL read-modify-write cycle
    in `append` (from `_load_series` through `_atomic_write`).

    The lock is taken on `<series_path>.lock`, NOT the series JSON itself:
    the JSON is replaced via tmp+rename (`_atomic_write`), so its inode
    changes on every write and a lock held on it would not span the rename.
    A dedicated lock file's inode is stable across the whole critical
    section.

    Returns the open lock-file handle (caller releases via
    `fcntl.flock(..., LOCK_UN)` then `.close()`), or `None` if `fcntl` is
    unavailable on this platform — a stated, single-warning degradation
    (see `append`), never a silent skip.
    """
    if fcntl is None:
        return None
    series_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(str(series_path) + ".lock")
    lock_file = open(lock_path, "a+")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
    except OSError:
        # Don't leak the just-opened fd if the blocking lock wait is
        # interrupted (e.g. EINTR) — close before propagating.
        lock_file.close()
        raise
    return lock_file


def _release_series_lock(lock_file) -> None:
    if lock_file is None:
        return
    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
    lock_file.close()
