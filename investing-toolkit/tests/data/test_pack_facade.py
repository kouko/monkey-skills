"""test_pack_facade.py — Task 4: unified pack.py facade contract.

Covers market auto-detection, the fail-loud exit contract (0/1/2/64), and
the `_status` block the facade injects at the top level of its output.

Test strategy (documented per the dispatch's "your choice, document it"):

- Suffix -> market detection (`detect_market`) is a pure function with no
  I/O — exercised by importing `pack.py` directly and calling it. No
  subprocess, no network.
- The three usage-error (exit 64) paths — regime-pack without --market,
  a --tickers list spanning more than one market, and an unknown --pack
  value routed through build_pack's ValueError — are all rejected before
  any client/network call, so they are exercised via a REAL subprocess
  invocation of pack.py (the actual CLI contract under test), which stays
  offline-safe.
- The exit 0/1/2 section-classification contract requires controlling
  build_pack's return value without touching the network. build_pack()
  itself does live I/O, so these are exercised in-process: monkeypatch
  `pack_us.build_pack` (the module object pack.py's MARKET_MODULES["us"]
  points at) to return a crafted dict, then call `pack.main(argv)`
  directly and inspect the captured stdout + return code.

Offline: no network calls anywhere in this file.
"""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK_PY = ROOT / "skills" / "data-markets" / "scripts" / "pack.py"
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))


def _run_pack_py(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Invoke pack.py via the current interpreter (stdlib-only facade;
    no `uv run` needed to exercise argument-validation-only paths)."""
    return subprocess.run(
        [sys.executable, str(PACK_PY), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(ROOT),
    )


# ---------------------------------------------------------------------------
# Market auto-detection — pure function, no I/O
# ---------------------------------------------------------------------------

DETECTION_CASES = [
    ("2330.TW", "tw", True),
    ("1101.TWO", "tw", True),
    ("005930.KS", "kr", True),
    ("005930.KQ", "kr", True),
    ("600519.SS", "cn", True),
    ("000001.SZ", "cn", True),
    ("0700.HK", "cn", True),
    ("7203.T", "jp", True),
    ("7203", "jp", True),  # bare 4-digit
    ("AAPL", "us", False),  # default-us-with-warning
    ("MSFT", "us", False),  # default-us-with-warning
]


@pytest.mark.parametrize(
    "ticker,expected_market,expected_matched",
    DETECTION_CASES,
    ids=[c[0] for c in DETECTION_CASES],
)
def test_detect_market_suffix_table(ticker, expected_market, expected_matched):
    pack = importlib.import_module("pack")
    market, matched = pack.detect_market(ticker)
    assert market == expected_market, f"{ticker!r} -> {market!r}, expected {expected_market!r}"
    assert matched is expected_matched, (
        f"{ticker!r} matched={matched}, expected {expected_matched} "
        f"(False means it fell through to the us default)"
    )


# ---------------------------------------------------------------------------
# Usage-error exit contract (exit 64) — real subprocess, offline-safe
# ---------------------------------------------------------------------------


def test_regime_pack_without_market_exits_64():
    proc = _run_pack_py("--pack", "regime-pack")
    assert proc.returncode == 64, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    payload = json.loads(proc.stdout)
    status = payload["_status"]
    assert status["status"] == "usage_error"
    assert "market" in status["message"] or "regime-pack" in status["message"]


def test_mixed_market_tickers_exits_64():
    proc = _run_pack_py("--tickers", "AAPL,2330.TW", "--pack", "comps-multiples")
    assert proc.returncode == 64, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    payload = json.loads(proc.stdout)
    status = payload["_status"]
    assert status["status"] == "usage_error"
    assert "us" in status["message"] and "tw" in status["message"]


def test_unknown_pack_value_error_exits_64_usage_error():
    proc = _run_pack_py("--ticker", "AAPL", "--pack", "not-a-real-pack")
    assert proc.returncode == 64, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    payload = json.loads(proc.stdout)
    status = payload["_status"]
    assert status["status"] == "usage_error"
    assert status["market"] == "us"
    assert "not-a-real-pack" in status["message"]


# ---------------------------------------------------------------------------
# Section-classification exit contract (0 / 1 / 2) — in-process, mocked
# build_pack, no network
# ---------------------------------------------------------------------------


def _call_main_capture(monkeypatch, capsys, argv, fake_build_pack, market_module_name="pack_us"):
    pack = importlib.import_module("pack")
    market_module = importlib.import_module(market_module_name)
    monkeypatch.setattr(market_module, "build_pack", fake_build_pack)
    rc = pack.main(argv)
    out = capsys.readouterr().out
    return rc, json.loads(out)


def test_market_override_skips_detection_no_warning(monkeypatch, capsys):
    """--market explicitly overrides autodetection: (a) regime-pack +
    --market bypasses the 'missing --market' usage error (no exit 64),
    and (b) a ticker that would otherwise trigger the default-us warning
    produces no detection warning, since detection never ran.

    build_pack itself does live I/O, so it is monkeypatched here too —
    this test is about the facade's own arg-resolution logic, not about
    what a real regime-pack fetch returns.
    """

    def fake_build_pack(pack_name, tickers):
        return {"pack": pack_name, "market_override_reached": True}

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--pack", "regime-pack", "--market", "us"],
        fake_build_pack,
    )
    assert rc == 0
    assert payload["_status"]["status"] == "ok"
    assert payload["_status"]["warnings"] == []


def test_clean_pack_exit_0_status_ok(monkeypatch, capsys):
    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "us",
            "ticker": tickers[0],
            "info": {"ok": True},
            "history": {"ok": True},
        }

    rc, payload = _call_main_capture(
        monkeypatch, capsys, ["--ticker", "AAPL", "--pack", "snapshot"], fake_build_pack
    )
    assert rc == 0
    assert payload["_status"]["status"] == "ok"
    assert payload["_status"]["failed_sections"] == []


def test_one_section_failed_exit_2_status_partial_named(monkeypatch, capsys):
    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "us",
            "ticker": tickers[0],
            "info": {"error": "boom"},
            "history": {"ok": True},
        }

    rc, payload = _call_main_capture(
        monkeypatch, capsys, ["--ticker", "AAPL", "--pack", "snapshot"], fake_build_pack
    )
    assert rc == 2
    assert payload["_status"]["status"] == "partial"
    assert payload["_status"]["failed_sections"] == ["info"]


def test_all_sections_failed_exit_1_status_failed(monkeypatch, capsys):
    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "us",
            "ticker": tickers[0],
            "info": {"error": "boom"},
            "history": {"_error": "boom2"},
        }

    rc, payload = _call_main_capture(
        monkeypatch, capsys, ["--ticker", "AAPL", "--pack", "snapshot"], fake_build_pack
    )
    assert rc == 1
    assert payload["_status"]["status"] == "failed"
    assert set(payload["_status"]["failed_sections"]) == {"info", "history"}


def test_unexpected_exception_exit_1_status_failed_with_traceback(monkeypatch, capsys):
    def fake_build_pack(pack_name, tickers):
        raise RuntimeError("boom-unexpected")

    rc, payload = _call_main_capture(
        monkeypatch, capsys, ["--ticker", "AAPL", "--pack", "snapshot"], fake_build_pack
    )
    assert rc == 1
    status = payload["_status"]
    assert status["status"] == "failed"
    assert "traceback" in status
    assert "RuntimeError" in status["traceback"]
    assert "boom-unexpected" in status["traceback"]


def test_kr_tw_whole_pack_partial_dialect_exit_2(monkeypatch, capsys):
    """kr/tw dialect: failures nest two levels deep and are invisible to a
    top-level scan; the whole-pack `_partial: true` flag is the only signal
    a shallow top-level scan can see (see LOOM-SIMPLIFY in pack.py)."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "tw",
            "ticker": tickers[0],
            "yfinance": {"info": {"ok": True}},
            "mops": {"balance_sheet": {"_error": "nested, invisible to top-level scan"}},
            "_partial": True,
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "2330.TW", "--pack", "snapshot"],
        fake_build_pack,
        market_module_name="pack_tw",
    )
    assert rc == 2
    assert payload["_status"]["status"] == "partial"
    assert payload["_status"]["failed_sections"] == ["_partial"]
