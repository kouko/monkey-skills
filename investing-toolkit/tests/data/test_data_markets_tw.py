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
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "skills" / "data-markets" / "scripts"
OLD_PACK_PATH = ROOT / "skills" / "data-tw" / "scripts" / "pack.py"

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
    # (c) pack_tw.py exists + SUPPORTED_PACKS matches data-tw/pack.py
    # ------------------------------------------------------------------
    pack_tw_path = SCRIPTS_DIR / "pack_tw.py"
    assert pack_tw_path.exists(), "pack_tw.py not created"
    pack_tw = _load_module(pack_tw_path, "data_markets_pack_tw")

    assert isinstance(pack_tw.SUPPORTED_PACKS, tuple)
    old_pack = _load_module(OLD_PACK_PATH, "data_tw_pack_orig")
    assert set(pack_tw.SUPPORTED_PACKS) == old_pack.PACK_TYPES

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

        data, status = twse._cached_get(
            "https://example.invalid/rwd/x", "some-cache-key", ttl=1800
        )

        assert status == "hit"
        assert data == original_payload, (
            "dict-payload cache hit must strip cache_util's _cache/"
            "_cache_age_seconds/_cache_ttl_seconds bookkeeping keys so the "
            f"hit shape matches the miss shape; got {data!r}"
        )
    finally:
        sys.path.remove(str(SCRIPTS_DIR))
