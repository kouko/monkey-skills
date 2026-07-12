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


def test_tw_mops_nested_error_now_detected_directly(monkeypatch, capsys):
    """Round-2 upgrade: mops.balance_sheet._error sits exactly ONE level
    below the "mops" section, so the one-level dict-walk now trips "mops"
    directly -- the kr/tw dialect's synthetic "_partial" fallback is no
    longer needed for this shape (this is the LOOM-SIMPLIFY ceiling that
    got lifted; see pack.py). Was
    test_kr_tw_whole_pack_partial_dialect_exit_2 asserting
    failed_sections == ["_partial"]; now asserts the real section name."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "tw",
            "ticker": tickers[0],
            "yfinance": {"info": {"ok": True}},
            "mops": {"balance_sheet": {"_error": "now visible via one-level walk"}},
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
    assert payload["_status"]["failed_sections"] == ["mops"]


def test_kr_tw_partial_fallback_when_nested_two_levels_deep(monkeypatch, capsys):
    """A failure nested TWO levels below a section (source -> field ->
    subfield carrying "_error") is still invisible to the one-level walk;
    the whole-pack `_partial: true` flag remains the only signal -- this is
    the LOOM-SIMPLIFY ceiling that stays in place after the Round-2
    upgrade (see pack.py)."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "snapshot",
            "country": "tw",
            "ticker": tickers[0],
            "yfinance": {"info": {"ok": True}},
            "mops": {
                "balance_sheet": {
                    "rows": {"assets": {"_error": "two levels below mops, still invisible"}}
                }
            },
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


# ---------------------------------------------------------------------------
# Round-2 regression: realistic per-market TOTAL-failure shapes that the
# shallow (direct-key-only) classifier misclassified as ('ok', []) -- exit 0
# -- because each market's failure marker is nested one level below the
# section (or inside a list item), invisible to a top-level-only scan.
# Shapes are copied verbatim from the cited code paths, not idealized.
# ---------------------------------------------------------------------------


def test_us_single_ticker_comps_multiples_total_failure_real_shape(monkeypatch, capsys):
    """pack_us.py:599-616: run_client's non-zero-exit branch returns
    {"error": "client_failed", ...}; filter_fields (pack_us.py:227-236)
    preserves that "error" key alongside None-valued whitelisted fields, so
    both "tickers" and "info" carry the SAME per-ticker dict with a direct
    "error" key one level below the section."""

    def fake_build_pack(pack_name, tickers):
        failed_ticker = {
            "trailingPE": None,
            "forwardPE": None,
            "priceToSales": None,
            "priceToBook": None,
            "enterpriseToEbitda": None,
            "enterpriseToRevenue": None,
            "marketCap": None,
            "enterpriseValue": None,
            "sector": None,
            "industry": None,
            "error": "client_failed",
        }
        return {
            "pack": "comps-multiples",
            "fetched_at": "2026-07-11T00:00:00+00:00",
            "tickers": {"AAPL": failed_ticker},
            "info": {"AAPL": failed_ticker},
        }

    rc, payload = _call_main_capture(
        monkeypatch, capsys, ["--ticker", "AAPL", "--pack", "comps-multiples"], fake_build_pack
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


def test_kr_single_ticker_comps_multiples_total_failure_real_shape(monkeypatch, capsys):
    """pack_kr.py:445-464: _run's empty-stdout branch (pack_kr.py:183-189)
    returns {"error": ..., "stderr": ..., "returncode": ..., "_partial":
    True} stored directly as info_by_ticker[ticker] -- no top-level
    `_partial` is ever set on the RESULT dict itself, it only lives inside
    the per-ticker error dict, one level below "info"."""

    def fake_build_pack(pack_name, tickers):
        failed = {
            "error": "empty stdout from yfinance_client.py",
            "stderr": "",
            "returncode": 1,
            "_partial": True,
        }
        return {
            "pack": "comps-multiples",
            "country": "kr",
            "tickers": tickers,
            "info": {tickers[0]: failed},
            "_provenance": {"tier": "Tier 2 (yfinance unofficial)"},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "005930.KS", "--pack", "comps-multiples"],
        fake_build_pack,
        market_module_name="pack_kr",
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


def test_jp_comps_multiples_total_failure_real_shape(monkeypatch, capsys):
    """pack_jp.py:514-561: "tickers" is a LIST of per-ticker dicts where the
    batch-level error is nested one level inside each item's "multiples"
    sub-dict (_filter_multiples, pack_jp.py:493-499, propagates "error"
    through unchanged); "info" stays an entirely empty dict since only
    non-error multiples get promoted into it."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "comps-multiples",
            "fetched_at": "2026-07-11T00:00:00+00:00",
            "tickers": [
                {
                    "ticker": "7203",
                    "yf_ticker": "7203.T",
                    "multiples": {"error": "ticker missing from batch response"},
                }
            ],
            "_provenance": {"tier": "tier_1"},
            "info": {},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "7203.T", "--pack", "comps-multiples"],
        fake_build_pack,
        market_module_name="pack_jp",
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


def test_cn_comps_multiples_total_failure_real_shape(monkeypatch, capsys):
    """pack_cn.py:365-436: pack_comps_multiples_batch's "tickers" is a LIST
    of per-ticker dicts whose error lives inside "_yfinance_info" (_run's
    non-zero-exit branch, pack_cn.py:154-168, returns {"_error": ...});
    "multiples"/"info" on the item stay empty dicts (no direct
    "error"/"_error" key on the item itself); the outer "info" aggregate
    stays an entirely empty dict too since a failed ticker's falsy
    `multiples` is never promoted into it."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "comps-multiples",
            "country": "CN",
            "tickers": [
                {
                    "ticker": "600519.SS",
                    "country": "CN",
                    "multiples": {},
                    "_yfinance_info": {
                        "_error": "client exited rc=1",
                        "_cmd": "uv run yfinance_client.py --ticker 600519.SS --action info",
                        "_stderr": "",
                    },
                    "info": {},
                }
            ],
            "info": {},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "600519.SS", "--pack", "comps-multiples"],
        fake_build_pack,
        market_module_name="pack_cn",
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


def test_tw_comps_multiples_total_failure_real_shape(monkeypatch, capsys):
    """pack_tw.py:510-539: wrap() (pack_tw.py:172-186) nests the client's
    raw "_error" directly onto the wrapped dict stored at
    out["tickers"][ticker]; "info" stays entirely empty since only a
    truthy `multiples` gets promoted. Neither this function nor
    pack_screener_batch ever sets a top-level `_partial` flag (verified:
    grep _partial pack_tw.py only hits pack_snapshot/pack_memo_fetch/
    pack_regime)."""

    def fake_build_pack(pack_name, tickers):
        return {
            "pack": "comps-multiples",
            "country": "TW",
            "tickers": {
                "2330.TW": {
                    "_tier": "2",
                    "_source": "yfinance",
                    "_action": "info-multiples",
                    "_error": "exit_1",
                    "_stderr": "",
                    "_cmd": "uv run yfinance_client.py --ticker 2330.TW --action info",
                }
            },
            "info": {},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "2330.TW", "--pack", "comps-multiples"],
        fake_build_pack,
        market_module_name="pack_tw",
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


def test_tw_screener_batch_total_failure_real_shape(monkeypatch, capsys):
    """pack_tw.py:541-568: both "yfinance" sub-fetches AND the per-ticker
    "mops" fetch are wrap()-wrapped with a direct "_error" key when every
    underlying client call fails; no top-level `_partial` flag is set by
    this function."""

    def fake_build_pack(pack_name, tickers):
        info_err = {
            "_tier": "2", "_source": "yfinance", "_action": "info-batch",
            "_error": "exit_1", "_stderr": "", "_cmd": "uv run yfinance_client.py ...",
        }
        hist_err = {**info_err, "_action": "history-batch"}
        mops_err = {
            "_tier": "A", "_source": "mops", "_action": "company-basic",
            "_error": "exit_1", "_stderr": "", "_cmd": "uv run mops_client.py ...",
        }
        return {
            "pack": "screener-batch",
            "country": "TW",
            "yfinance": {"info_batch": info_err, "history_batch": hist_err},
            "mops": {"2330.TW": mops_err},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "2330.TW", "--pack", "screener-batch"],
        fake_build_pack,
        market_module_name="pack_tw",
    )
    assert rc == 1, f"stdout={payload}"
    assert payload["_status"]["status"] == "failed"


# ---------------------------------------------------------------------------
# Task 4: a section may self-declare `_status`, overriding inference. This
# is what makes a LIST-nested failure (structurally invisible to the
# one-level dict-only walk) visible: the producer that KNOWS it degraded
# says so directly, and the declaration wins over the classifier's own
# inference -- exercised straight against `_classify_result`, per the
# dispatch's acceptance criteria (no subprocess / no main() needed since
# there is no network-touching branch cache involved here).
# ---------------------------------------------------------------------------


def test_classify_honors_self_declared_status():
    pack = importlib.import_module("pack")

    # Per-item errors live inside a LIST ("sections") -- invisible to
    # _dict_section_status's dict-only sub-field walk, which only inspects
    # non-empty DICT-valued sub-fields. Without a self-declared `_status`,
    # this section has no dict-valued sub-fields at all and infers "ok".
    result = {
        "pack": "memo-fetch",
        "sec_narrative": {
            "_status": "partial",
            "sections": [
                {"item": "2.02-Q1", "error": "fetch failed"},
                {"item": "2.02-Q2", "ok": True},
            ],
        },
    }
    status, failed_sections = pack._classify_result(result)
    assert status == "partial"
    assert failed_sections == ["sec_narrative"]


def test_classify_self_declared_status_failed_and_ok():
    pack = importlib.import_module("pack")

    failed_result = {
        "sec_narrative": {"_status": "failed", "sections": [{"error": "x"}]},
    }
    status, failed_sections = pack._classify_result(failed_result)
    assert status == "failed"
    assert failed_sections == ["sec_narrative"]

    ok_result = {
        "sec_narrative": {"_status": "ok", "sections": [{"ok": True}]},
    }
    status, failed_sections = pack._classify_result(ok_result)
    assert status == "ok"
    assert failed_sections == []


def test_classify_self_declared_status_unknown_value_fails_closed():
    """An invalid/unknown `_status` value must not silently pass as ok --
    fail-closed choice: treat it as "failed" so an untrusted declaration
    cannot masquerade as a clean section."""
    pack = importlib.import_module("pack")

    result = {"sec_narrative": {"_status": "bogus-value", "sections": []}}
    status, failed_sections = pack._classify_result(result)
    assert status == "failed"
    assert failed_sections == ["sec_narrative"]


def test_classify_no_status_key_inference_unchanged():
    """Regression guard: a section with NO `_status` key must be classified
    EXACTLY as before -- the other four market packs never set `_status`
    and depend on this inference path being byte-for-byte unchanged."""
    pack = importlib.import_module("pack")

    # direct error marker -> failed
    assert pack._classify_result({"info": {"error": "boom"}}) == ("failed", ["info"])

    # all non-empty sub-dicts erroring -> failed
    assert pack._classify_result(
        {"mops": {"balance_sheet": {"_error": "x"}, "income": {"_error": "y"}}}
    ) == ("failed", ["mops"])

    # some non-empty sub-dicts erroring -> partial
    assert pack._classify_result(
        {"mops": {"balance_sheet": {"_error": "x"}, "income": {"ok": True}}}
    ) == ("partial", ["mops"])

    # none erroring -> ok
    assert pack._classify_result(
        {"mops": {"balance_sheet": {"ok": True}, "income": {"ok": True}}}
    ) == ("ok", [])

    # empty dict -> not classified (contributes no signal either way)
    assert pack._classify_result({"info": {}}) == ("ok", [])


def test_tw_screener_batch_partial_mops_only_real_shape(monkeypatch, capsys):
    """Same dialect as the total-failure case above, but only the
    per-ticker mops fetch fails while both yfinance batch fetches succeed
    -- exercises the SOME-but-not-all partial-contribution path per
    section, still with no top-level `_partial` flag anywhere in the
    result."""

    def fake_build_pack(pack_name, tickers):
        ok_info = {
            "_tier": "2", "_source": "yfinance", "_action": "info-batch",
            "data": {"mode": "batch", "tickers": {"2330.TW": {"trailingPE": 15.2}}},
        }
        ok_hist = {
            "_tier": "2", "_source": "yfinance", "_action": "history-batch",
            "data": {"mode": "batch", "tickers": {"2330.TW": {"data": []}}},
        }
        mops_err = {
            "_tier": "A", "_source": "mops", "_action": "company-basic",
            "_error": "exit_1", "_stderr": "", "_cmd": "uv run mops_client.py ...",
        }
        return {
            "pack": "screener-batch",
            "country": "TW",
            "yfinance": {"info_batch": ok_info, "history_batch": ok_hist},
            "mops": {"2330.TW": mops_err},
        }

    rc, payload = _call_main_capture(
        monkeypatch,
        capsys,
        ["--ticker", "2330.TW", "--pack", "screener-batch"],
        fake_build_pack,
        market_module_name="pack_tw",
    )
    assert rc == 2, f"stdout={payload}"
    assert payload["_status"]["status"] == "partial"
    assert "mops" in payload["_status"]["failed_sections"]
    assert "yfinance" not in payload["_status"]["failed_sections"]
