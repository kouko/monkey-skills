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

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = ROOT / "skills" / "data-markets" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from cache_util import (  # noqa: E402
    CACHE_SCHEMA_VERSION,
    cache_path,
    compute_ttl,
    load_cache,
    resolve_cache_dir,
    save_cache,
)


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


# ---------------------------------------------------------------------------
# compute_ttl / cache_path / load_cache / save_cache
#
# Band values below are transcribed from cache-policy.md §"TTL bands" —
# the SSOT this module's compute_ttl generalizes dgbas_client.py's
# _compute_ttl against. One discrepancy found and documented: cache-policy
# describes `tick` as trading-hours-aware (60s open / 1h closed), but
# compute_ttl's (cadence, staleness_days) signature has no market/wall-
# clock input to do that split — same flat-60s shortcut dgbas_client.py's
# _compute_ttl already takes (it has no tick presets). Marked LOOM-SIMPLIFY
# in cache_util.py at the compute_ttl docstring.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "cadence,staleness_days,expected_seconds",
    [
        # tick — flat 60s (see module discrepancy note above)
        pytest.param("tick", 0, 60, id="tick_flat"),
        pytest.param("tick", None, 60, id="tick_flat_unknown_staleness"),
        # event — always 1h
        pytest.param("event", 0, 3600, id="event_always_1h"),
        pytest.param("event", 999, 3600, id="event_always_1h_stale"),
        # immutable — ~100 years
        pytest.param("immutable", None, 100 * 365 * 24 * 3600, id="immutable_100y"),
        # daily: fresh <=1 -> 4h, imminent >1 -> 1h, overdue >2 -> 30min
        pytest.param("daily", None, 30 * 60, id="daily_overdue_unknown"),
        pytest.param("daily", 3, 30 * 60, id="daily_overdue"),
        pytest.param("daily", 2, 3600, id="daily_imminent_boundary"),
        pytest.param("daily", 1, 4 * 3600, id="daily_fresh_boundary"),
        pytest.param("daily", 0, 4 * 3600, id="daily_fresh"),
        # weekly: fresh <=7 -> 5d, imminent >7 -> 12h, overdue >10 -> 2h
        pytest.param("weekly", None, 2 * 3600, id="weekly_overdue_unknown"),
        pytest.param("weekly", 11, 2 * 3600, id="weekly_overdue"),
        pytest.param("weekly", 8, 12 * 3600, id="weekly_imminent_boundary"),
        pytest.param("weekly", 7, 5 * 24 * 3600, id="weekly_fresh_boundary"),
        # monthly: fresh <=30 -> 7d, imminent >30 -> 1d, overdue >45 -> 4h
        pytest.param("monthly", None, 4 * 3600, id="monthly_overdue_unknown"),
        pytest.param("monthly", 46, 4 * 3600, id="monthly_overdue"),
        pytest.param("monthly", 31, 24 * 3600, id="monthly_imminent_boundary"),
        pytest.param("monthly", 30, 7 * 24 * 3600, id="monthly_fresh_boundary"),
        # quarterly: fresh <=90 -> 30d, imminent >90 -> 1d, overdue >100 -> 4h
        pytest.param("quarterly", None, 4 * 3600, id="quarterly_overdue_unknown"),
        pytest.param("quarterly", 101, 4 * 3600, id="quarterly_overdue"),
        pytest.param("quarterly", 91, 24 * 3600, id="quarterly_imminent_boundary"),
        pytest.param("quarterly", 90, 30 * 24 * 3600, id="quarterly_fresh_boundary"),
        # annual: fresh <=365 -> 90d, imminent >365 -> 7d, overdue >380 -> 1d
        pytest.param("annual", None, 24 * 3600, id="annual_overdue_unknown"),
        pytest.param("annual", 381, 24 * 3600, id="annual_overdue"),
        pytest.param("annual", 366, 7 * 24 * 3600, id="annual_imminent_boundary"),
        pytest.param("annual", 365, 90 * 24 * 3600, id="annual_fresh_boundary"),
        # unknown cadence -> safe default (matches dgbas_client.py fallback)
        pytest.param("bogus-cadence", 0, 24 * 3600, id="unknown_cadence_default"),
    ],
)
def test_compute_ttl_matches_cache_policy_bands(cadence, staleness_days, expected_seconds):
    assert compute_ttl(cadence, staleness_days) == expected_seconds


def test_cache_schema_version_constant():
    # Must match the envelope schema cache-policy.md documents ("2.0"),
    # and the value dgbas_client.py's synced block already carries —
    # bumping this without a coordinated policy-doc bump invalidates
    # every existing cache file (all reads schema-mismatch to miss).
    assert CACHE_SCHEMA_VERSION == "2.0"


def test_cache_path_sanitizes_unsafe_key(monkeypatch, tmp_path):
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache-root"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    path = cache_path("dgbas", "../../etc/passwd")

    # A malicious/malformed key must never escape <cache_root>/<source>/.
    assert path.parent == tmp_path / "cache-root" / "dgbas"
    assert path.suffix == ".json"
    assert "/" not in path.stem
    assert ".." not in path.stem


def test_ttl_and_roundtrip_contract(monkeypatch, tmp_path):
    """Primary RED test for Task 2: cache_path + save_cache + load_cache +
    compute_ttl composed the way a real client would use them."""
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache-root"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    path = cache_path("dgbas", "cpi-yoy")
    assert path == tmp_path / "cache-root" / "dgbas" / "cpi-yoy.json"

    ttl = compute_ttl("monthly", staleness_days=8)
    assert ttl == 7 * 24 * 3600  # fresh band

    # miss: nothing written yet
    assert load_cache(path, ttl) is None

    save_cache(path, {"preset": "cpi-yoy", "observations": [{"date": "202603", "value": 101.2}]})
    assert path.exists()

    cached = load_cache(path, ttl)
    assert cached is not None
    assert cached["preset"] == "cpi-yoy"
    assert cached["observations"][0]["value"] == 101.2
    assert cached["_cache"] == "hit"
    assert cached["_cache_ttl_seconds"] == ttl

    # negative ttl == always expired regardless of clock resolution
    assert load_cache(path, ttl=-1) is None


def test_load_cache_preserves_caller_provenance_on_hit(monkeypatch, tmp_path):
    """Task 3d requires _provenance.primary_source_status to survive a
    save -> load(hit) roundtrip. save_cache(path, data) never writes a
    top-level envelope _provenance — it only ever nests whatever the
    caller put in `data`. load_cache must not clobber a caller-supplied
    `data["_provenance"]` with `{}` on a cache hit."""
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path / "cache-root"))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    path = cache_path("dgbas", "cpi-provenance")
    data = {
        "observations": [{"date": "202603", "value": 101.2}],
        "_provenance": {"primary_source_status": "real"},
    }

    save_cache(path, data)
    cached = load_cache(path, ttl=3600)

    assert cached is not None
    assert cached["_provenance"] == {"primary_source_status": "real"}


def test_load_cache_missing_file_returns_none(tmp_path):
    assert load_cache(tmp_path / "does-not-exist.json", ttl=3600) is None


def test_load_cache_corrupt_json_returns_none(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json")
    assert load_cache(path, ttl=3600) is None


def test_load_cache_schema_version_mismatch_returns_none(tmp_path):
    path = tmp_path / "old-schema.json"
    save_cache(path, {"foo": "bar"})
    envelope = json.loads(path.read_text())
    envelope["_cache_meta"]["version"] = "1.0"
    path.write_text(json.dumps(envelope))

    assert load_cache(path, ttl=3600) is None


def test_save_cache_write_failure_warns_not_raises(monkeypatch, tmp_path, capsys):
    path = tmp_path / "sub" / "key.json"

    def _raise(*args, **kwargs):
        raise OSError("simulated disk-full")

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", _raise)

    save_cache(path, {"foo": "bar"})  # must not raise

    captured = capsys.readouterr()
    assert "WARNING" in captured.err
    assert str(path) in captured.err
    assert not path.exists()


def test_disposability_survives_deleted_cache_dir(monkeypatch, tmp_path):
    """XDG disposability: deleting the cache dir between calls must only
    slow the next call, never break it."""
    cache_root = tmp_path / "cache-root"
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(cache_root))
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    path = cache_path("dgbas", "cpi")
    save_cache(path, {"value": 1})
    assert load_cache(path, ttl=3600) is not None

    shutil.rmtree(cache_root)
    assert not cache_root.exists()

    # dir gone -> file gone -> fail-open miss, never an exception
    assert load_cache(path, ttl=3600) is None

    # save must recreate the dir and succeed
    save_cache(path, {"value": 2})
    assert path.exists()
    cached = load_cache(path, ttl=3600)
    assert cached is not None
    assert cached["value"] == 2


def test_resolve_cache_dir_fallback_mkdir_failure_raises_named_runtimeerror(
    monkeypatch, tmp_path, capsys,
):
    """Reviewer-debt fix (Task 1 code-quality review): resolve_cache_dir's
    last-resort fallback.mkdir() (cache_util.py) was unguarded — if the
    tempdir itself is unwritable this must raise a named, explicit
    RuntimeError (never a bare traceback), naming both rejected paths."""
    monkeypatch.delenv("INVESTING_TOOLKIT_CACHE", raising=False)
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

    def _raise_mkdir(self, *args, **kwargs):
        raise OSError("simulated: tempdir itself is unwritable")

    monkeypatch.setattr(Path, "mkdir", _raise_mkdir)

    rejected_candidate = str(tmp_path / "rejected-candidate")

    with pytest.raises(RuntimeError) as exc_info:
        resolve_cache_dir(rejected_candidate)

    assert rejected_candidate in str(exc_info.value)
    assert "investing-toolkit" in str(exc_info.value)  # fallback path named too

    captured = capsys.readouterr()
    assert "FATAL" in captured.err
