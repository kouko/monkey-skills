"""cache_util.py — investing-toolkit shared cache directory resolution.

Single source of truth for where per-market data clients (yfinance, FRED,
NBS, EDINET, TDnet, MOPS, TWSE, FinanceDataReader, akshare, ...) cache
fetched data. Replaces the per-client `os.environ.get(...) or Path.home()...`
pattern (see yfinance_client.py:32), whose bare `or` treats any truthy
string — including a misexpanded env var like `${CLAUDE_PLUGIN_DATA}/cache`
collapsing to the literal `/cache` — as a valid, writable path.

Precedence ladder (highest to lowest), uv/XDG dev-CLI convention:

    1. explicit arg (CLI-flag passthrough)
    2. INVESTING_TOOLKIT_CACHE env var (stripped; empty after strip = unset)
    3. $XDG_CACHE_HOME/investing-toolkit (only if XDG_CACHE_HOME set + non-empty)
    4. ~/.cache/investing-toolkit (default)

The ladder picks exactly one candidate directory. That candidate is then
run through a single writability gate: create it if missing, probe with a
real write. If either step fails, a loud one-line warning naming the
rejected path and the fallback is printed to stderr, and resolution falls
back to <tempfile.gettempdir()>/investing-toolkit. Contract: this function
returns a writable directory Path, or raises RuntimeError when neither
the candidate nor the tempdir fallback is writable.
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def _resolve_candidate(explicit: str | None) -> Path:
    if explicit is not None and explicit.strip() != "":
        return Path(explicit.strip())

    env_cache = os.environ.get("INVESTING_TOOLKIT_CACHE", "").strip()
    if env_cache:
        return Path(env_cache)

    xdg_cache_home = os.environ.get("XDG_CACHE_HOME", "").strip()
    if xdg_cache_home:
        return Path(xdg_cache_home) / "investing-toolkit"

    return Path.home() / ".cache" / "investing-toolkit"


def _is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False

    probe = path / f".cache_util_write_probe_{os.getpid()}"
    try:
        probe.write_text("")
        probe.unlink()
    except OSError:
        return False
    return True


def resolve_cache_dir(explicit: str | None = None) -> Path:
    """Resolve the investing-toolkit cache directory. Always writable."""
    candidate = _resolve_candidate(explicit)

    if _is_writable(candidate):
        return candidate

    fallback = Path(tempfile.gettempdir()) / "investing-toolkit"
    sys.stderr.write(
        f"WARNING: cache dir '{candidate}' is not writable; "
        f"falling back to '{fallback}'\n"
    )
    sys.stderr.flush()
    try:
        fallback.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        sys.stderr.write(
            f"FATAL: cache dir '{candidate}' is not writable and the "
            f"last-resort fallback '{fallback}' could not be created "
            f"either ({e}); investing-toolkit has no writable cache dir.\n"
        )
        sys.stderr.flush()
        raise RuntimeError(
            "cache dir resolution failed: no writable directory found "
            f"(rejected candidate={candidate!r}, rejected fallback={fallback!r})"
        ) from e
    return fallback


# ---------------------------------------------------------------------------
# Cadence-aware TTL + fail-open cache read/write helpers
#
# Generalizes the per-client `_compute_ttl` / `load_cache` / `save_cache`
# block previously duplicated across 14 data clients (see e.g.
# data-tw/scripts/dgbas_client.py's "cache helpers (synced)" block). Band
# contract: investing-toolkit/docs/cache-policy.md §"TTL bands" — that
# doc is the SSOT; this helper matches it band-for-band except where noted.
# ---------------------------------------------------------------------------

CACHE_SCHEMA_VERSION = "2.0"

_UNSAFE_KEY_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


def compute_ttl(cadence: str, staleness_days: int | None) -> int:
    """Return TTL seconds for a cadence + observed staleness.

    Bands per cache-policy.md §"TTL bands" (fresh / imminent / overdue).
    `staleness_days is None` (no reference_period known yet, e.g. first
    fetch) is always treated as overdue, per the same section.

    LOOM-SIMPLIFY: `tick` returns a flat 60s TTL. cache-policy.md
    §"TTL bands" documents tick as "60s (during market hours) / 1h
    (after-hours)", trading-hours-aware per market — but that needs a
    `market` + wall-clock check this function's (cadence, staleness_days)
    signature has no room for, and the only existing implementation
    (dgbas_client.py's `_compute_ttl`, which this generalizes) already
    takes the same flat-60s shortcut since it has no tick presets to
    exercise the distinction. | ceiling: a caller needs `tick` TTL to
    differ between market-open and market-closed | upgrade: add a
    `market: str | None` param, port the `_is_market_open` table from
    cache-policy.md §"Trading-hours awareness" | ref: docs/loom/plans/
    2026-07-11-investing-toolkit-data-consolidation.md / Task 2 (see also
    investing-toolkit/docs/cache-policy.md §"Trading-hours awareness")
    """
    if cadence == "immutable":
        return 100 * 365 * 24 * 3600
    if cadence == "tick":
        return 60
    if cadence == "event":
        return 3600
    if cadence == "monthly":
        if staleness_days is None or staleness_days > 45:
            return 4 * 3600
        if staleness_days > 30:
            return 24 * 3600
        return 7 * 24 * 3600
    if cadence == "quarterly":
        if staleness_days is None or staleness_days > 100:
            return 4 * 3600
        if staleness_days > 90:
            return 24 * 3600
        return 30 * 24 * 3600
    if cadence == "weekly":
        if staleness_days is None or staleness_days > 10:
            return 2 * 3600
        if staleness_days > 7:
            return 12 * 3600
        return 5 * 24 * 3600
    if cadence == "daily":
        if staleness_days is None or staleness_days > 2:
            return 30 * 60
        if staleness_days > 1:
            return 3600
        return 4 * 3600
    if cadence == "annual":
        if staleness_days is None or staleness_days > 380:
            return 24 * 3600
        if staleness_days > 365:
            return 7 * 24 * 3600
        return 90 * 24 * 3600
    return 24 * 3600  # safe default — unknown cadence


def cache_path(source: str, key: str) -> Path:
    """`<resolved_cache_dir>/<source>/<key>.json`, with `key` sanitized.

    Sanitization replaces any character outside `[A-Za-z0-9_-]` (including
    `/`, `\\`, and `.`) with `_`, so a malicious/malformed key (e.g.
    containing `../`) can never escape the `<source>/` directory.

    `source` must be a trusted hardcoded literal (a client name), not
    external input; only `key` is sanitized.
    """
    sanitized = _UNSAFE_KEY_CHARS.sub("_", key) or "_"
    return resolve_cache_dir() / source / f"{sanitized}.json"


def load_cache(path: Path, ttl: int) -> dict | None:
    """Fail-open cache read: missing / corrupt / schema-mismatched /
    expired ⇒ None. Never raises.

    `ttl` is the caller-computed value (typically from `compute_ttl`);
    this function does not recompute TTL from cadence itself — callers
    that need cache-policy's "recompute on every load" behavior pass a
    freshly-computed `ttl` each call.
    """
    if not path.exists():
        return None
    try:
        envelope = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(envelope, dict):
        return None

    meta = envelope.get("_cache_meta") or {}
    if meta.get("version") != CACHE_SCHEMA_VERSION:
        return None  # schema drift / old format → miss

    fetched_at_str = meta.get("fetched_at")
    if not fetched_at_str:
        return None
    try:
        fetched_at = datetime.fromisoformat(fetched_at_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

    age = (datetime.now(timezone.utc) - fetched_at).total_seconds()
    if age > ttl:
        return None

    out = dict(envelope.get("data", {}))
    out["_cache"] = "hit"
    out["_cache_age_seconds"] = int(age)
    out["_cache_ttl_seconds"] = ttl
    return out


def save_cache(path: Path, data: dict) -> None:
    """Write a cache envelope atomically (tmp + rename).

    Write failure (unwritable dir, disk full, ...) is non-fatal: prints
    a single loud stderr warning naming `path` and returns — never a
    silent `except: pass`, and never raises.
    """
    now = datetime.now(timezone.utc)
    envelope = {
        "_cache_meta": {
            "version": CACHE_SCHEMA_VERSION,
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "data": data,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=str(path.parent),
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as f:
            json.dump(envelope, f, ensure_ascii=False, indent=2, default=str)
            tmp = Path(f.name)
        tmp.rename(path)
    except OSError as e:
        sys.stderr.write(f"WARNING: failed to write cache file '{path}': {e}\n")
        sys.stderr.flush()
