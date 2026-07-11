"""test_cache_util.py — contract tests for cache_util.resolve_cache_dir().

Verifies the XDG/uv precedence ladder (explicit arg > INVESTING_TOOLKIT_CACHE
env var > XDG_CACHE_HOME/investing-toolkit > ~/.cache/investing-toolkit) and
the post-resolution writability gate that falls back to
<tempdir>/investing-toolkit when the resolved directory can't be written to
(e.g. INVESTING_TOOLKIT_CACHE=/cache on macOS — the live-reproduced bug this
module replaces the `or`-fallback in yfinance_client.py:32 for).

Never touches the real ~/.cache: the "nothing set" case redirects HOME to
tmp_path via monkeypatch so Path.home() resolves inside the pytest sandbox,
and assertions compare against the computed path rather than writing to it.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "data-markets" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cache_util import resolve_cache_dir  # noqa: E402


def _env_value(raw: str, tmp_path: Path) -> str:
    """Turn a bare name into an absolute path under tmp_path; pass through
    literal values (empty string, whitespace, absolute paths like /cache)."""
    if raw == "" or raw.strip() == "" or raw.startswith("/"):
        return raw
    return str(tmp_path / raw)


@pytest.mark.parametrize(
    "explicit_rel,env_cache_raw,xdg_rel,use_home,expect_rel,unwritable",
    [
        pytest.param("explicit-cache", "env-cache", "xdg-cache", False,
                      "explicit-cache", False, id="explicit_wins"),
        pytest.param(None, "env-cache", "xdg-cache", False,
                      "env-cache", False, id="env_wins_over_xdg_default"),
        pytest.param(None, "", "xdg-cache", False,
                      "xdg-cache/investing-toolkit", False, id="empty_env_falls_through"),
        pytest.param(None, "   ", "xdg-cache", False,
                      "xdg-cache/investing-toolkit", False, id="whitespace_env_falls_through"),
        pytest.param(None, None, "xdg-cache", False,
                      "xdg-cache/investing-toolkit", False, id="xdg_set_no_env"),
        pytest.param(None, None, None, True,
                      ".cache/investing-toolkit", False, id="nothing_set_default_home"),
        pytest.param(None, "/cache", None, False,
                      None, True, id="unwritable_env_falls_back_to_tempdir"),
    ],
)
def test_resolve_cache_dir_always_returns_writable_dir(
    monkeypatch, tmp_path, capsys,
    explicit_rel, env_cache_raw, xdg_rel, use_home, expect_rel, unwritable,
):
    monkeypatch.delenv("INVESTING_TOOLKIT_CACHE", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    if env_cache_raw is not None:
        monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", _env_value(env_cache_raw, tmp_path))
    if xdg_rel is not None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / xdg_rel))
    if use_home:
        monkeypatch.setenv("HOME", str(tmp_path))

    explicit_arg = str(tmp_path / explicit_rel) if explicit_rel is not None else None

    result = resolve_cache_dir(explicit_arg)

    # Contract: ALWAYS returns a writable directory, whichever branch fired.
    assert result.is_dir()
    assert os.access(result, os.W_OK)

    if unwritable:
        expected_fallback = Path(tempfile.gettempdir()) / "investing-toolkit"
        assert result == expected_fallback
        captured = capsys.readouterr()
        stderr_lines = [line for line in captured.err.strip().splitlines() if line]
        assert len(stderr_lines) == 1, f"expected a single-line warning, got: {captured.err!r}"
        assert "/cache" in captured.err
    else:
        assert result == tmp_path / expect_rel
