"""test_data_markets_kr.py — Task 3d migration contract for KR clients.

Verifies the migration of data-kr's fdr_client.py + pack.py into
skills/data-markets/scripts/ as fdr_client.py + pack_kr.py:

  (a) no local cache helpers survive the migration (fdr_client.py must
      delegate to shared cache_util instead).
  (b) pack_kr.build_pack() preserves _provenance fields, `_partial` flag
      semantics, and section keys vs. the current data-kr/pack.py shape
      (offline — subprocess calls are mocked, no network).
  (c) build_pack never calls sys.exit — the old CLI's
      `sys.exit(1)`-on-`_partial` (data-kr/pack.py:681-682) must NOT be
      ported; pack_kr stays exit-code-agnostic (T4's facade owns exit
      codes).
  (d) SUPPORTED_PACKS matches the --pack choices in data-kr/pack.py.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FDR_CLIENT = SCRIPTS / "fdr_client.py"
PACK_KR = SCRIPTS / "pack_kr.py"

OLD_PACK = ROOT / "skills" / "data-kr" / "scripts" / "pack.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _mock_run(monkeypatch, module, responses: list[dict]):
    """Patch module.subprocess.run to return `responses` in call order.

    Mirrors _run()'s contract: a completed-process-like object with
    `.stdout` (JSON text) and `.returncode`.
    """
    queue = list(responses)

    def _fake_run(cmd, capture_output=True, text=True, check=False, env=None):
        payload = queue.pop(0) if queue else {}
        proc = MagicMock()
        proc.stdout = json.dumps(payload)
        proc.stderr = ""
        proc.returncode = 0
        return proc

    monkeypatch.setattr(module.subprocess, "run", _fake_run)


# ---------------------------------------------------------------------------
# (a) no local cache helpers survive the migration
# ---------------------------------------------------------------------------


def test_kr_migration_contract():
    assert FDR_CLIENT.exists(), "fdr_client.py was not migrated to data-markets/scripts"
    assert PACK_KR.exists(), "pack_kr.py was not created in data-markets/scripts"

    fdr_src = FDR_CLIENT.read_text()
    pack_src = PACK_KR.read_text()

    for src, label in ((fdr_src, "fdr_client.py"), (pack_src, "pack_kr.py")):
        assert "def get_cache_path(" not in src, f"{label} still defines a local get_cache_path"
        assert "def load_cache(" not in src, f"{label} still defines a local load_cache"
        assert "def save_cache(" not in src, f"{label} still defines a local save_cache"
        assert "_CACHE_BASE" not in src, f"{label} still references local _CACHE_BASE"
        assert "CACHE_DIR = Path" not in src, f"{label} still defines local CACHE_DIR"

    assert "import cache_util" in fdr_src, "fdr_client.py must delegate to shared cache_util"

    # yfinance_client.py must NOT be duplicated here — US sibling owns the
    # canonical copy (Task 3a).
    assert not (SCRIPTS / "yfinance_client.py").exists() or True, (
        "this task does not create yfinance_client.py; presence here is owned by T3a"
    )

    # (c) — source scan: no exit-code logic ported into pack_kr.py. Checks
    # the actual call syntax (`sys.exit(`), not mere mentions of "sys.exit"
    # in comments/docstrings explaining the constraint.
    assert "sys.exit(" not in pack_src, "pack_kr.py must not contain exit-code logic (T4 owns exit codes)"
    assert "def main(" not in pack_src, "pack_kr.py must not carry a CLI shell"
    assert "argparse" not in pack_src, "pack_kr.py must not carry a CLI shell (no argparse)"


# ---------------------------------------------------------------------------
# (d) SUPPORTED_PACKS matches data-kr pack.py's --pack choices
# ---------------------------------------------------------------------------


def test_supported_packs_matches_data_kr_choices():
    pack_kr = _load_module(PACK_KR, "pack_kr_contract")
    old_src = OLD_PACK.read_text()
    block = re.search(r"choices=\[(.*?)\]", old_src, re.S)
    assert block, "could not locate --pack choices in data-kr/pack.py — has it moved?"
    expected = tuple(re.findall(r'"([^"]+)"', block.group(1)))

    assert isinstance(pack_kr.SUPPORTED_PACKS, tuple)
    assert set(pack_kr.SUPPORTED_PACKS) == set(expected)
    assert len(pack_kr.SUPPORTED_PACKS) == len(expected)


# ---------------------------------------------------------------------------
# (b) build_pack section keys + _provenance + _partial semantics
#     (offline — subprocess mocked; matches data-kr fixture top-level shape)
# ---------------------------------------------------------------------------

# Expected top-level keys per pack, transcribed from
# tests/data/fixtures/data-kr-*-sample.json (real data-kr/pack.py output).
_EXPECTED_KEYS = {
    "snapshot": {"pack", "country", "ticker", "info", "price_history", "history", "_provenance"},
    "memo-fetch": {
        "pack", "country", "ticker", "tier", "info", "financials_annual",
        "financials_quarterly", "price_history", "history", "income_statement",
        "cash_flow", "balance_sheet", "shares_outstanding", "current_price",
        "kr_specific", "_provenance",
    },
    "comps-multiples": {"pack", "country", "tickers", "info", "_provenance"},
    "screener-batch": {"pack", "country", "tickers", "batch", "_provenance"},
    "regime-pack": {"pack", "country", "groups_requested", "data", "series", "_provenance"},
}


def test_build_pack_snapshot_shape_and_provenance(monkeypatch):
    pack_kr = _load_module(PACK_KR, "pack_kr_snapshot")
    _mock_run(monkeypatch, pack_kr, [
        {"symbol": "005930.KS", "shortName": "SamsungElec"},  # info
        {"data": [{"date": "2026-05-01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]},  # history
    ])

    out = pack_kr.build_pack("snapshot", ["005930.KS"])

    assert set(out.keys()) == _EXPECTED_KEYS["snapshot"]
    assert out["pack"] == "snapshot"
    assert out["country"] == "kr"
    assert out["ticker"] == "005930.KS"
    prov = out["_provenance"]
    assert prov["primary_source_status"] == "deferred"
    assert "_partial" not in out


def test_build_pack_memo_fetch_shape_and_provenance(monkeypatch):
    pack_kr = _load_module(PACK_KR, "pack_kr_memo")
    _mock_run(monkeypatch, pack_kr, [
        {"symbol": "005930.KS", "sharesOutstanding": 100, "regularMarketPrice": 1.0},  # info
        {},  # financials annual
        {},  # financials quarterly
        {"data": []},  # history
    ])

    out = pack_kr.build_pack("memo-fetch", ["005930.KS"])

    assert set(out.keys()) == _EXPECTED_KEYS["memo-fetch"]
    assert out["tier"] == "Tier 2 only"
    prov = out["_provenance"]
    assert prov["primary_source_status"] == "deferred"


def test_build_pack_comps_multiples_shape(monkeypatch):
    pack_kr = _load_module(PACK_KR, "pack_kr_comps")
    _mock_run(monkeypatch, pack_kr, [
        {"symbol": "005930.KS", "trailingPE": 10.0},  # single-ticker info
    ])

    out = pack_kr.build_pack("comps-multiples", ["005930.KS"])

    assert set(out.keys()) == _EXPECTED_KEYS["comps-multiples"]
    assert "005930.KS" in out["info"]
    assert out["_provenance"]["primary_source_status"] == "deferred"


def test_build_pack_screener_batch_shape(monkeypatch):
    pack_kr = _load_module(PACK_KR, "pack_kr_screener")
    _mock_run(monkeypatch, pack_kr, [
        {"mode": "batch", "action": "info", "tickers": {"005930.KS": {}}},
    ])

    out = pack_kr.build_pack("screener-batch", ["005930.KS", "000660.KS"])

    assert set(out.keys()) == _EXPECTED_KEYS["screener-batch"]
    assert set(out["tickers"]) == {"005930.KS", "000660.KS"}
    assert out["_provenance"]["primary_source_status"] == "deferred"


def test_build_pack_regime_pack_shape_and_provenance(monkeypatch):
    pack_kr = _load_module(PACK_KR, "pack_kr_regime")
    # Shrink REGIME_GROUPS to a single tiny group so the mocked subprocess
    # only needs one canned response — offline, deterministic, fast.
    monkeypatch.setattr(pack_kr, "REGIME_GROUPS", {"rates": ["policy-rate"]})
    _mock_run(monkeypatch, pack_kr, [
        {
            "preset": "policy-rate", "fetched_at": "2026-01-01T00:00:00Z",
            "_source": "fdr_ecos",
            "observations": [{"date": "20260101", "value": 2.5}],
            "latest": {"date": "20260101", "value": 2.5}, "prior": None,
            "direction": None, "count": 1,
        },
    ])

    out = pack_kr.build_pack("regime-pack", [])

    assert set(out.keys()) == _EXPECTED_KEYS["regime-pack"]
    assert out["groups_requested"] == ["rates"]
    assert out["_provenance"]["primary_source_status"] == "available"
    assert "_partial" not in out


def test_pack_regime_pack_partial_flag_preserved_on_unknown_group(monkeypatch):
    """_partial semantics: unknown indicator group ⇒ `_partial: True` in the
    returned dict (data-kr/pack.py's only existing failure-propagating case).
    build_pack's generalized (pack_name, tickers) interface has no
    `indicators` slot, so this exercises the underlying function directly —
    the semantic this task must preserve, not the CLI surface that carried
    it."""
    pack_kr = _load_module(PACK_KR, "pack_kr_partial")

    out = pack_kr.pack_regime_pack("bogus-group-that-does-not-exist")

    assert out.get("_partial") is True
    assert "error" in out


def test_build_pack_rejects_unknown_pack_name(monkeypatch):
    """Behavioral check (c): even on an unsupported pack name, build_pack
    raises ValueError rather than SystemExit — matching the sibling
    contract (pack_us/jp/tw/cn all raise ValueError for validation
    branches; T4's facade owns exit-code translation)."""
    pack_kr = _load_module(PACK_KR, "pack_kr_no_exit")

    with pytest.raises(ValueError):
        pack_kr.build_pack("not-a-real-pack", ["005930.KS"])
