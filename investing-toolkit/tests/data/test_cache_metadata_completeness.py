"""test_cache_metadata_completeness.py — FINDING-005 regression coverage.

SKILL.md's "Cache-hit metadata" contract says every payload served from
cache carries the full trio: `_cache: "hit"`, `_cache_age_seconds`,
`_cache_ttl_seconds` (see skills/data-markets/SKILL.md §Cache-hit
metadata). yfinance/finmind get this for free because their envelope IS
cache_util.load_cache's return dict.

twse_openapi_client.py does not: `_cached_get` deliberately STRIPS the
bookkeeping keys cache_util.load_cache injects (see
`_CACHE_BOOKKEEPING_KEYS`, added in cff427ed to fix a dict-payload
hit/miss shape-parity bug — ADR-0009) so the inner `data` payload's shape
stays identical between hit and miss. But stripping discarded the trio
entirely instead of re-attaching it at the envelope's top level, so
`_envelope()` only ever sets `_cache` (the "hit"/"miss" string) and never
`_cache_age_seconds` / `_cache_ttl_seconds` — violating the declared
contract on every twse leaf.

Offline only: `cache_util.load_cache` (and `_get` for the miss case) are
monkeypatched, so no live network call happens. requests/urllib3 skip
gracefully if unavailable in the pytest sandbox (see this module's
sibling test_cached_get_dict_payload_hit_matches_miss_shape for the
shared skip rationale).
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "data-markets" / "scripts"


def _import_twse():
    pytest.importorskip(
        "requests",
        reason=(
            "twse_openapi_client.py imports requests/urllib3 at module load; "
            "CI installs only pytest+pyyaml — run with `uv run --with requests==2.33.1`"
        ),
    )
    pytest.importorskip("urllib3")

    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location(
        "twse_openapi_client_cache_meta", SCRIPTS_DIR / "twse_openapi_client.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_twse_cache_hit_envelope_carries_full_trio(monkeypatch):
    """A cache-hit `daily-price-all` envelope must carry `_cache_age_seconds`
    + `_cache_ttl_seconds` alongside `_cache: "hit"` (SKILL.md's declared
    3-key contract), and `data` must stay exactly the underlying rows —
    no bookkeeping-key leakage into `data` (ADR-0009 shape parity)."""
    twse = _import_twse()
    try:
        rows = [{"Code": "2330", "ClosingPrice": "1000"}]
        hit_from_cache_util = {
            "_rows": rows,
            "_cache": "hit",
            "_cache_age_seconds": 42,
            "_cache_ttl_seconds": 86400,
        }
        monkeypatch.setattr(
            twse.cache_util, "load_cache", lambda path, ttl: dict(hit_from_cache_util)
        )

        result = twse._run_action(
            argparse.Namespace(action="daily-price-all", ticker=None)
        )

        assert result["_cache"] == "hit"
        assert result["_cache_age_seconds"] == 42, (
            "cache-hit envelope missing _cache_age_seconds — trio not "
            f"propagated; got keys {sorted(result.keys())}"
        )
        assert result["_cache_ttl_seconds"] == 86400, (
            "cache-hit envelope missing _cache_ttl_seconds — trio not "
            f"propagated; got keys {sorted(result.keys())}"
        )
        assert result["data"] == rows, (
            "cache bookkeeping keys must not leak into `data`"
        )
    finally:
        sys.path.remove(str(SCRIPTS_DIR))


def test_twse_cache_miss_envelope_has_no_trio_keys(monkeypatch):
    """A cache-MISS envelope must not carry `_cache_age_seconds` /
    `_cache_ttl_seconds` — those only describe a hit. Guards against a
    naive fix that always sets the trio and breaks hit/miss shape parity
    (ADR-0009)."""
    twse = _import_twse()
    try:
        rows = [{"Code": "2330", "ClosingPrice": "999"}]
        monkeypatch.setattr(twse.cache_util, "load_cache", lambda path, ttl: None)
        monkeypatch.setattr(twse.cache_util, "save_cache", lambda path, data: None)
        monkeypatch.setattr(twse, "_get", lambda url, timeout=30: rows)

        result = twse._run_action(
            argparse.Namespace(action="daily-price-all", ticker=None)
        )

        assert result["_cache"] == "miss"
        assert "_cache_age_seconds" not in result
        assert "_cache_ttl_seconds" not in result
        assert result["data"] == rows
    finally:
        sys.path.remove(str(SCRIPTS_DIR))
