"""test_twse_ixbrl_fetch.py — OFFLINE tests for twse_ixbrl_fetch.py
(Task 2, docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md).

`requests` is stubbed via sys.modules — mirrors test_sec_edgar_dimensional.py's
`sec_client` fixture (:44-60) — no live network, no `network` marker.

Run offline (part of the default "not network" suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fetch_mod(tmp_path, monkeypatch):
    """Import twse_ixbrl_fetch with `requests` stubbed in sys.modules and
    the cache dir redirected to tmp_path (no real cache-dir writes)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path))
    requests_stub = mock.MagicMock(name="requests")
    saved_requests = sys.modules.get("requests")
    saved_mod = sys.modules.get("twse_ixbrl_fetch")
    sys.modules["requests"] = requests_stub
    sys.modules.pop("twse_ixbrl_fetch", None)
    module = importlib.import_module("twse_ixbrl_fetch")
    module.requests_stub = requests_stub
    monkeypatch.setattr(module.time, "sleep", lambda *_a, **_k: None)
    try:
        yield module
    finally:
        if saved_requests is not None:
            sys.modules["requests"] = saved_requests
        else:
            sys.modules.pop("requests", None)
        if saved_mod is not None:
            sys.modules["twse_ixbrl_fetch"] = saved_mod
        else:
            sys.modules.pop("twse_ixbrl_fetch", None)


def _fake_response(status_code: int, content: bytes):
    resp = mock.MagicMock(name="response")
    resp.status_code = status_code
    resp.content = content
    return resp


def test_fetch_url_and_notfound(fetch_mod):
    # 1. URL builder — exact t164sb01 endpoint shape, tier-agnostic.
    url = fetch_mod.build_t164sb01_url(co_id="2330", year=2024, season=3, report_id="C")
    assert url == (
        "https://mopsov.twse.com.tw/server-java/t164sb01"
        "?step=1&CO_ID=2330&SYEAR=2024&SSEASON=3&REPORT_ID=C"
    )

    # 2. Not-found sentinel (98-byte fixture body) -> absence, not raw content.
    notfound_bytes = (FIXTURES / "twse_ixbrl_notfound.html").read_bytes()
    notfound_text = notfound_bytes.decode("big5hkscs")
    assert fetch_mod.is_not_found_body(notfound_text) is True

    fetch_mod.requests_stub.get.return_value = _fake_response(200, notfound_bytes)
    body = fetch_mod.fetch_ixbrl_body(
        co_id="2330", year=2024, season=3, report_id="C", use_cache=False,
    )
    assert body is None  # sentinel -> absence sentinel, never the raw 92-byte text

    # 3. HTTP 502-then-200 retry — fetch retries and returns the decoded body.
    fetch_mod.requests_stub.get.reset_mock()
    real_bytes = "<html><body>真實內容</body></html>".encode("big5hkscs")
    fetch_mod.requests_stub.get.side_effect = [
        _fake_response(502, b""),
        _fake_response(200, real_bytes),
    ]
    body2 = fetch_mod.fetch_ixbrl_body(
        co_id="2317", year=2024, season=3, report_id="C", use_cache=False,
    )
    assert body2 == real_bytes.decode("big5hkscs")
    assert fetch_mod.requests_stub.get.call_count == 2


def test_season_fallback_skips_absent_seasons(fetch_mod):
    calls = []

    def fake_fetch(co_id, year, season, report_id, **kwargs):
        calls.append(season)
        if season == 4:
            return None  # not filed that season
        return f"body-Q{season}"

    body, season = fetch_mod.fetch_with_season_fallback(
        "2330", 2024, "C",
        season_order=fetch_mod.DEFAULT_SEASON_ORDER,
        fetch_fn=fake_fetch,
    )
    assert season == 3
    assert body == "body-Q3"
    assert calls == [4, 3]  # stopped at first success, never tried Q2/Q1


def test_season_fallback_all_absent_returns_none(fetch_mod):
    body, season = fetch_mod.fetch_with_season_fallback(
        "2330", 2024, "C",
        season_order=(4, 3),
        fetch_fn=lambda *a, **k: None,
    )
    assert body is None
    assert season is None


def test_emerging_board_season_order_prioritizes_q2_q4(fetch_mod):
    assert fetch_mod.EMERGING_BOARD_SEASON_ORDER[:2] == (2, 4)
