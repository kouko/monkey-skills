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
ALWAYS returns a writable directory Path.
"""
from __future__ import annotations

import os
import sys
import tempfile
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
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback
