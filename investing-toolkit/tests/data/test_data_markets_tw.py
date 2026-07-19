"""test_data_markets_tw.py — migration contract tests for the TW clients +
pack_tw.py moved into skills/data-markets/scripts/ (Task 3c).

Coverage:
  (a) migrated files exist; none of them still define a local cache-helper
      (path/load/save/ttl) — they must delegate to cache_util instead.
      dgbas_client.py is a stricter special case: its cadence machinery
      (`_compute_ttl`, `CACHE_SCHEMA_VERSION`) must be gone entirely and it
      must call cache_util.compute_ttl.
  (b) pack_tw.build_pack(pack_name, tickers) preserves the `_tier` /
      `_partial` output-envelope semantics and section keys of the
      original data-tw/scripts/pack.py, exercised offline via a
      monkeypatched run_client (no subprocess / no network).
  (c) pack_tw.SUPPORTED_PACKS matches data-tw/scripts/pack.py's PACK_TYPES.

Offline only — no network marker needed (nothing here calls a live API).
"""
from __future__ import annotations

import ast
import importlib.util
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "data-markets" / "scripts"

# Ground truth for (c) below — matches the old data-tw/scripts/pack.py's
# module-level `PACK_TYPES` set (migration-fidelity already verified; that
# skill dir is now deleted, so this is a hardcoded expectation rather than a
# runtime parity parse).
EXPECTED_PACK_TYPES = {"snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack"}

MIGRATED_CLIENTS = [
    "cbc_client.py",
    "dgbas_client.py",
    "finmind_client.py",
    "mops_client.py",
    "ndc_client.py",
    "statgov_client.py",
    "twse_openapi_client.py",
]

# Low-level local cache primitives that must be gone from every migrated
# client (they must call cache_util's instead). Wrapper functions that
# merely *compose* cache_util calls with the HTTP fetch (e.g. mops's
# `_cached_post`, twse_openapi's `_cached_get`) are NOT forbidden — only
# the raw path/load/save/ttl primitives are.
FORBIDDEN_CACHE_HELPER_NAMES = {
    "get_cache_path",
    "load_cache",
    "save_cache",
    "cache_key",
    "_cache_path",
    "_load_cache",
    "_save_cache",
    "_compute_ttl",
}


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure-logic: latest_roc_quarter (no network) — restored from the deleted
# tests/data/test_data_tw.py (round-1 gap: this offline unit test covered a
# still-live function, pack_tw.latest_roc_quarter, and was dropped along with
# the per-country skill deletion instead of migrating with the function).
# ---------------------------------------------------------------------------


def test_tw_latest_roc_quarter_boundary_cases():
    """Filing-aware ROC quarter math — exact boundary days the spec calls out.

    Filing deadlines (TWSE/TPEx-listed, consolidated):
      Q4 (年報): by Mar 31 of next year → safe Apr 1+
      Q1:       by May 15 → safe May 16+
      Q2 (半年報): by Aug 14 → safe Aug 15+
      Q3:       by Nov 14 → safe Nov 15+

    Q1 not yet filed on May 1 → fall back to prior-year Q4 (114, 4).
    Q1 filed by May 16 onward → (115, 1).
    Q2 not yet filed on Aug 14 → still (115, 1).
    Q2 filed by Aug 15 onward → (115, 2).
    """
    pack_tw = _load_module(SCRIPTS_DIR / "pack_tw.py", "data_markets_pack_tw_roc")
    fn = pack_tw.latest_roc_quarter

    # 2026 = ROC 115. May 1 is before May 16 buffer → previous-year Q4.
    assert fn(date(2026, 5, 1)) == (114, 4), "Q1 not yet filed → prior-year Q4"

    # May 20 is past May 16 buffer → Q1 filed.
    assert fn(date(2026, 5, 20)) == (115, 1), "Q1 filed by May 16+"

    # Aug 14 still before Aug 15 buffer → Q2 not yet filed (stay at Q1).
    assert fn(date(2026, 8, 14)) == (115, 1), "Q2 not yet filed → stay at Q1"

    # Aug 15 deadline buffer → Q2 filed.
    assert fn(date(2026, 8, 15)) == (115, 2), "Q2 filed by Aug 15+"


def test_tw_migration_contract(monkeypatch):
    # ------------------------------------------------------------------
    # (a) files migrated + no local cache-helper definitions remain
    # ------------------------------------------------------------------
    for filename in MIGRATED_CLIENTS:
        path = SCRIPTS_DIR / filename
        assert path.exists(), f"{filename} not migrated to data-markets/scripts/"
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        defined_funcs = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        }
        leaked = defined_funcs & FORBIDDEN_CACHE_HELPER_NAMES
        assert not leaked, f"{filename} still defines local cache helper(s): {leaked}"
        assert "import cache_util" in source, f"{filename} must `import cache_util`"

    # yfinance was explicitly NOT part of this (TW) task's scope — the US
    # migration (T3a, commit 792936ef) owns the canonical copy and has
    # since landed it at SCRIPTS_DIR/yfinance_client.py, so its presence
    # here is expected, not a TW scope violation. TW's own scope
    # discipline was enforced at commit time: `git show 92ed1fb9 --stat`
    # contains no yfinance file. No assertion here — an existence check
    # would be testing T3a's landing, not TW's scope; that isn't this
    # test's responsibility to gate.

    # dgbas special case: cadence machinery fully deleted, delegates to
    # cache_util's compute_ttl / CACHE_SCHEMA_VERSION.
    dgbas_source = (SCRIPTS_DIR / "dgbas_client.py").read_text()
    assert "CACHE_SCHEMA_VERSION = " not in dgbas_source, (
        "dgbas_client.py must not redefine CACHE_SCHEMA_VERSION locally"
    )
    assert "cache_util.compute_ttl(" in dgbas_source, (
        "dgbas_client.py must call cache_util.compute_ttl instead of a local _compute_ttl"
    )

    # ------------------------------------------------------------------
    # (c) pack_tw.py exists + SUPPORTED_PACKS matches the expected pack-type
    # set (hardcoded — the legacy data-tw/scripts/pack.py this used to
    # parity-check against is deleted; migration-fidelity was already
    # verified pre-deletion).
    # ------------------------------------------------------------------
    pack_tw_path = SCRIPTS_DIR / "pack_tw.py"
    assert pack_tw_path.exists(), "pack_tw.py not created"
    pack_tw = _load_module(pack_tw_path, "data_markets_pack_tw")

    assert isinstance(pack_tw.SUPPORTED_PACKS, tuple)
    assert set(pack_tw.SUPPORTED_PACKS) == EXPECTED_PACK_TYPES

    assert hasattr(pack_tw, "build_pack")

    # ------------------------------------------------------------------
    # (b) build_pack preserves _tier/_partial semantics + section keys,
    # exercised offline via a monkeypatched run_client (no subprocess).
    # ------------------------------------------------------------------
    state = {"fail_mops_company_basic": False}

    def _fake_run_client(script, args, timeout=60):
        if (
            script == "mops_client.py"
            and "company-basic" in args
            and state["fail_mops_company_basic"]
        ):
            return {"_error": "exit_1", "_stderr": "boom"}
        return {"ok": True, "_echo": {"script": script, "args": args}}

    monkeypatch.setattr(pack_tw, "run_client", _fake_run_client)

    # snapshot — all-clear
    out = pack_tw.build_pack("snapshot", ["2330.TW"])
    assert out["pack"] == "snapshot"
    assert out["country"] == "TW"
    assert out["_partial"] is False
    for group in ("yfinance", "mops", "twse", "finmind"):
        assert group in out, f"snapshot missing {group} group"
    for entry in out["mops"].values():
        assert entry["_tier"] == "A"
    for entry in out["yfinance"].values():
        assert entry["_tier"] == "2"

    # snapshot — Tier A failure flips _partial + preserves _error
    state["fail_mops_company_basic"] = True
    out_partial = pack_tw.build_pack("snapshot", ["2330.TW"])
    assert out_partial["_partial"] is True
    assert "_error" in out_partial["mops"]["company_basic"]
    assert out_partial["mops"]["company_basic"]["_tier"] == "A"
    state["fail_mops_company_basic"] = False

    # regime-pack — tickers ignored, macro source groups present
    out_regime = pack_tw.build_pack("regime-pack", [])
    assert out_regime["pack"] == "regime-pack"
    assert out_regime["country"] == "TW"
    for group in ("cbc", "dgbas", "ndc", "statgov"):
        assert group in out_regime, f"regime-pack missing {group} group"
    assert "_partial" in out_regime

    # comps-multiples — batch dispatch
    out_comps = pack_tw.build_pack("comps-multiples", ["2330.TW", "2454.TW"])
    assert out_comps["pack"] == "comps-multiples"
    assert set(out_comps["tickers"].keys()) == {"2330.TW", "2454.TW"}


def test_cached_get_dict_payload_hit_matches_miss_shape(monkeypatch):
    """twse_openapi_client._cached_get: dict-payload endpoints (e.g.
    get_stock_day_history_month, which caches the raw TWSE /rwd/ response
    dict — not a list) must return the SAME shape on a cache hit as on a
    cache miss.

    cache_util.load_cache injects `_cache`/`_cache_age_seconds`/
    `_cache_ttl_seconds` bookkeeping keys into the dict it hands back on a
    hit. The list-payload path (`{"_rows": [...]}`) already unwraps clean
    of these by construction (`cached["_rows"]` only ever pulls out the
    original rows). The dict-payload path took the `else cached` branch
    and returned cache_util's dict AS-IS — bookkeeping keys and all — so
    a caller reading `get_stock_day_history_month`'s dict on a cache HIT
    would see extra `_cache*` keys that are absent on a MISS. Assert the
    hit path strips them so hit and miss are indistinguishable in shape.
    """
    pytest.importorskip(
        "requests",
        reason=(
            "twse_openapi_client.py imports requests/urllib3 at module load; "
            "CI installs only pytest+pyyaml — run with `uv run --with requests==2.33.1`"
        ),
    )
    pytest.importorskip("urllib3")

    sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        import twse_openapi_client as twse

        importlib.reload(twse)

        original_payload = {"stat": "OK", "date": "20260710", "data": [[1, 2, 3]]}
        hit_from_cache_util = {
            **original_payload,
            "_cache": "hit",
            "_cache_age_seconds": 5,
            "_cache_ttl_seconds": 1800,
        }
        monkeypatch.setattr(
            twse.cache_util, "load_cache", lambda path, ttl: dict(hit_from_cache_util)
        )

        data, status, cache_meta = twse._cached_get(
            "https://example.invalid/rwd/x", "some-cache-key", ttl=1800
        )

        assert status == "hit"
        assert cache_meta == {"cache_age_seconds": 5, "cache_ttl_seconds": 1800}, (
            "FINDING-005 fix: _cached_get now returns a 3rd cache_meta element "
            "carrying the age/ttl trio for envelope-level re-attachment"
        )
        assert data == original_payload, (
            "dict-payload cache hit must strip cache_util's _cache/"
            "_cache_age_seconds/_cache_ttl_seconds bookkeeping keys so the "
            f"hit shape matches the miss shape; got {data!r}"
        )
    finally:
        sys.path.remove(str(SCRIPTS_DIR))


def test_memo_fetch_wires_ixbrl_canonical(monkeypatch):
    """Task 6 — pack_memo_fetch wires the TW iXBRL client (twse_ixbrl.py,
    invoked via run_client) as the TW canonical source, replacing the
    deferred yfinance-based stub (_build_canonical_from_yf_financials_tw)
    for the memo-fetch canonical path. Exercised offline via a
    monkeypatched run_client (no subprocess / no network), mirroring
    test_tw_migration_contract's stubbing pattern.
    """
    pack_tw_path = SCRIPTS_DIR / "pack_tw.py"
    pack_tw = _load_module(pack_tw_path, "data_markets_pack_tw_ixbrl")

    fake_ixbrl_payload = {
        "canonical": {
            "income_statement": {
                "revenue": [594_000_000],
                "_meta": {
                    "revenue": {
                        "source_label": "ifrs-full:Revenue",
                        "concept": "ifrs-full:Revenue",
                        "accounting_standard": "tifrs",
                        "unit": "TWD",
                    },
                },
            },
            "balance_sheet": {"total_assets": [1_000_000]},
            "cash_flow": {"operating_cash_flow": [500_000]},
        },
        "notes": {
            "financial_assets_fvoci": {
                "value": 189_650_000_000, "concept": "ifrs-full:x", "period": "2024Q3",
            },
        },
        "_meta": {"co_id": "2330", "year": 2024, "season": 3, "report_id": "C", "fact_count": 2002},
    }

    calls: list[tuple[str, list[str]]] = []

    def _fake_run_client(script, args, timeout=60):
        calls.append((script, args))
        if script == "twse_ixbrl.py":
            return fake_ixbrl_payload
        return {"ok": True, "_echo": {"script": script, "args": args}}

    monkeypatch.setattr(pack_tw, "run_client", _fake_run_client)

    stub_calls: list[tuple] = []
    original_stub = pack_tw._build_canonical_from_yf_financials_tw

    def _spy_stub(*args, **kwargs):
        stub_calls.append((args, kwargs))
        return original_stub(*args, **kwargs)

    monkeypatch.setattr(pack_tw, "_build_canonical_from_yf_financials_tw", _spy_stub)

    out = pack_tw.build_pack("memo-fetch", ["2330.TW"])

    assert not stub_calls, (
        "deferred yfinance-based canonical stub must not run for the TW "
        "memo-fetch canonical path — it must be sourced from twse_ixbrl"
    )

    assert "twse_ixbrl" in out, "memo-fetch output missing twse_ixbrl group"
    ixbrl_group = out["twse_ixbrl"]
    assert isinstance(ixbrl_group, dict) and ixbrl_group, "twse_ixbrl group must be non-empty"
    ixbrl_entry = next(iter(ixbrl_group.values()))
    assert ixbrl_entry["_tier"] == "A"
    assert ixbrl_entry["_source"] == "twse_ixbrl"
    assert "_error" not in ixbrl_entry
    assert ixbrl_entry["data"]["canonical"]["income_statement"]["revenue"] == [594_000_000]

    # Top-level canonical (consumed by report-equity-memo / analysis-dcf
    # etc) is now sourced from iXBRL, not the yfinance stub.
    assert out["income_statement"]["revenue"] == [594_000_000]
    assert out["balance_sheet"]["total_assets"] == [1_000_000]
    assert out["cash_flow"]["operating_cash_flow"] == [500_000]

    ixbrl_calls = [args for script, args in calls if script == "twse_ixbrl.py"]
    assert len(ixbrl_calls) == 1, (
        "iXBRL client should be called exactly once when the first "
        f"attempt succeeds; got {len(ixbrl_calls)} calls: {ixbrl_calls}"
    )
    assert "--co-id" in ixbrl_calls[0] and "2330" in ixbrl_calls[0]
    assert "--report-id" in ixbrl_calls[0] and "C" in ixbrl_calls[0]


# Sibling contract cited per round-2 review grounding requirement: the
# twse_ixbrl.py CLI (--co-id/--year/--season/--report-id) is the Task 5
# contract this suite's fake_run_client mirrors (docs/loom/plans/
# 2026-07-19-tw-ixbrl-ingestion.md Task 5).
_FAKE_YF_FINANCIALS_TW = {
    "income_statement": {
        "2024-06-30": {
            "Total Revenue": 600_000_000,
            "Operating Income": 120_000_000,
            "Net Income": 90_000_000,
        },
    },
    "balance_sheet": {
        "2024-06-30": {
            "Long Term Debt": 50_000_000,
            "Current Debt": 10_000_000,
            "Cash And Cash Equivalents": 200_000_000,
        },
    },
    "cash_flow": {
        "2024-06-30": {
            "Operating Cash Flow": 150_000_000,
            "Capital Expenditure": -40_000_000,
            "Free Cash Flow": 110_000_000,
        },
    },
}


def test_memo_fetch_degrades_to_yf_stub_when_ixbrl_both_attempts_error(monkeypatch):
    """Round 2 fix (code-quality review 🟡) — when BOTH the latest-likely-
    filed quarter and the one-quarter-back retry come back `_error`, the
    top-level canonical must degrade to the retained yfinance stub
    (_build_canonical_from_yf_financials_tw), not silently `{}`. An empty
    canonical zeroes every DCF field (net_debt, ebit, fcf all read 0),
    which is a worse failure mode than a Tier-2 scraper-sourced canonical.
    """
    pack_tw_path = SCRIPTS_DIR / "pack_tw.py"
    pack_tw = _load_module(pack_tw_path, "data_markets_pack_tw_ixbrl_degrade")

    calls: list[tuple[str, list[str]]] = []

    def _fake_run_client(script, args, timeout=60):
        calls.append((script, args))
        if script == "twse_ixbrl.py":
            return {"_error": "not_found"}
        if script == "yfinance_client.py" and "financials" in args:
            return dict(_FAKE_YF_FINANCIALS_TW)
        return {"ok": True, "_echo": {"script": script, "args": args}}

    monkeypatch.setattr(pack_tw, "run_client", _fake_run_client)

    stub_calls: list[tuple] = []
    original_stub = pack_tw._build_canonical_from_yf_financials_tw

    def _spy_stub(*args, **kwargs):
        stub_calls.append((args, kwargs))
        return original_stub(*args, **kwargs)

    monkeypatch.setattr(pack_tw, "_build_canonical_from_yf_financials_tw", _spy_stub)

    out = pack_tw.build_pack("memo-fetch", ["2330.TW"])

    assert stub_calls, (
        "yfinance-based canonical stub must run when both iXBRL attempts "
        "error — degrade-to-stub, not silent {}"
    )

    ixbrl_calls = [args for script, args in calls if script == "twse_ixbrl.py"]
    assert len(ixbrl_calls) == 2, (
        "both the initial and the one-quarter-back retry must be attempted "
        f"before degrading; got {len(ixbrl_calls)} calls: {ixbrl_calls}"
    )

    expected = original_stub(_FAKE_YF_FINANCIALS_TW)
    assert out["income_statement"] == expected["income_statement"]
    assert out["balance_sheet"] == expected["balance_sheet"]
    assert out["cash_flow"] == expected["cash_flow"]

    # Spot-check the actual DCF-required fields trace through the stub
    # rather than reading as empty/zero.
    assert out["balance_sheet"]["total_debt"][0] == 60_000_000.0
    assert out["balance_sheet"]["cash"][0] == 200_000_000.0
    assert out["income_statement"]["ebit"][0] == 120_000_000.0
    assert out["cash_flow"]["capex"][0] == 40_000_000.0
    assert out["cash_flow"]["fcf"][0] == 110_000_000.0


def test_memo_fetch_ixbrl_retries_prior_quarter_then_succeeds(monkeypatch):
    """Round 2 fix — the 2-attempt prior-quarter fallback loop (pack_tw.py
    :480-490) must actually fire: first attempt `_error` (not yet filed),
    second attempt (one quarter back) succeeds -> canonical sourced from
    iXBRL, stub NOT called.
    """
    pack_tw_path = SCRIPTS_DIR / "pack_tw.py"
    pack_tw = _load_module(pack_tw_path, "data_markets_pack_tw_ixbrl_retry")

    fake_ixbrl_payload = {
        "canonical": {
            "income_statement": {"revenue": [111_000_000]},
            "balance_sheet": {"total_assets": [222_000_000]},
            "cash_flow": {"operating_cash_flow": [333_000_000]},
        },
    }

    calls: list[tuple[str, list[str]]] = []

    def _fake_run_client(script, args, timeout=60):
        calls.append((script, args))
        if script == "twse_ixbrl.py":
            ixbrl_calls_so_far = sum(1 for s, _ in calls if s == "twse_ixbrl.py")
            if ixbrl_calls_so_far == 1:
                return {"_error": "not_found"}
            return fake_ixbrl_payload
        return {"ok": True, "_echo": {"script": script, "args": args}}

    monkeypatch.setattr(pack_tw, "run_client", _fake_run_client)

    stub_calls: list[tuple] = []
    monkeypatch.setattr(
        pack_tw,
        "_build_canonical_from_yf_financials_tw",
        lambda *a, **k: stub_calls.append((a, k)) or {},
    )

    out = pack_tw.build_pack("memo-fetch", ["2330.TW"])

    assert not stub_calls, "iXBRL succeeded on retry — stub must not run"

    ixbrl_calls = [args for script, args in calls if script == "twse_ixbrl.py"]
    assert len(ixbrl_calls) == 2, (
        f"expected exactly 2 attempts (initial + one-quarter-back retry); "
        f"got {len(ixbrl_calls)}: {ixbrl_calls}"
    )
    assert ixbrl_calls[0] != ixbrl_calls[1], (
        "the retry must use the stepped-back quarter, not repeat the same args"
    )
    assert out["income_statement"]["revenue"] == [111_000_000]
