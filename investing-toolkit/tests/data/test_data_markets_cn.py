"""test_data_markets_cn.py — migration contract for the CN data clients
moved into the merged `data-markets` skill (Task 3e of
docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md).

Verifies (offline, no network, no `uv run` subprocess spawned — all
subprocess.run calls are monkeypatched):
  (a) akshare_client.py / nbs_client.py drop their local cache
      boilerplate (`_CACHE_BASE`, `get_cache_path`/`load_cache`/
      `save_cache` defs) and import the shared `cache_util` module.
  (b) none of the 3 shipped files (akshare_client.py, nbs_client.py,
      pack_cn.py) carry a local copy of fred_client.py's or
      yfinance_client.py's fetch logic — CN does not own either
      canonical copy (both live under the US migration, Task 3a).
      Scoped to content markers rather than file-existence, since
      fred_client.py may or may not exist yet under data-markets/scripts
      depending on Task 3a's concurrent progress.
  (c) pack_cn.build_pack() produces the same top-level section-key shape
      as the current data-cn/scripts/pack.py builder functions, for all
      5 pack types.
  (d) pack_cn.SUPPORTED_PACKS matches the pack-type set data-cn/pack.py's
      CLI currently exposes via `--pack {choices}`.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LEGACY_DIR = ROOT / "skills" / "data-cn" / "scripts"
NEW_DIR = ROOT / "skills" / "data-markets" / "scripts"

LEGACY_PACK = LEGACY_DIR / "pack.py"
NEW_AKSHARE = NEW_DIR / "akshare_client.py"
NEW_NBS = NEW_DIR / "nbs_client.py"
NEW_PACK = NEW_DIR / "pack_cn.py"

SHIPPED_FILES = (NEW_AKSHARE, NEW_NBS, NEW_PACK)

TICKER = "600519.SS"

# data-cn/scripts/pack.py:709-711 `--pack` argparse choices — the ground
# truth SUPPORTED_PACKS must match.
EXPECTED_SUPPORTED_PACKS = (
    "snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack",
)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_subprocess_run(cmd, **kwargs):
    """Offline stand-in for subprocess.run — routes on the target script's
    basename (cmd[2], per `_run(["uv", "run", str(script), *args])`) and
    returns just enough shape for the pack builders to compose sections
    without raising."""
    script = Path(cmd[2]).name
    if script == "yfinance_client.py":
        action = cmd[cmd.index("--action") + 1] if "--action" in cmd else None
        if action == "info":
            payload = {
                "trailingPE": 10.5, "forwardPE": 9.5, "enterpriseToEbitda": 8.0,
                "priceToSalesTrailing12Months": 2.0, "priceToBook": 3.0,
                "sharesOutstanding": 1_000_000, "regularMarketPrice": 123.4,
            }
        elif action == "history":
            payload = {"data": [{"date": "20260101", "close": 100.0}]}
        elif action == "financials":
            payload = {"income_statement": {}, "balance_sheet": {}, "cash_flow": {}}
        else:
            payload = {}
    elif script == "nbs_client.py":
        payload = {"indicators": {
            "cpi-yoy": {"preset": "cpi-yoy",
                        "observations": [{"date": "20260101", "value": 1.0}]},
        }}
    elif script == "akshare_client.py":
        payload = {"indicators": {
            "shrzgm": {"preset": "shrzgm",
                       "observations": [{"date": "20260101", "value": 100.0}]},
        }}
    elif script == "fred_client.py":
        payload = {"series": {}}
    else:
        payload = {"_error": f"unmocked script in test double: {script}"}
    return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(payload), stderr="")


@pytest.fixture
def legacy_pack(monkeypatch):
    module = _load_module(LEGACY_PACK, "legacy_data_cn_pack_for_migration_test")
    monkeypatch.setattr(module.subprocess, "run", _fake_subprocess_run)
    return module


@pytest.fixture
def new_pack(monkeypatch):
    module = _load_module(NEW_PACK, "data_markets_pack_cn_for_migration_test")
    monkeypatch.setattr(module.subprocess, "run", _fake_subprocess_run)
    return module


# ---------------------------------------------------------------------------
# (a) no local cache boilerplate in migrated clients; cache_util imported
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", [NEW_AKSHARE, NEW_NBS])
def test_migrated_clients_drop_local_cache_helpers(path):
    assert path.exists(), f"{path} not migrated yet"
    src = path.read_text()
    assert "_CACHE_BASE" not in src, f"{path.name} still defines local _CACHE_BASE"
    assert "def get_cache_path(" not in src, f"{path.name} still defines local get_cache_path()"
    assert "def load_cache(" not in src, f"{path.name} still defines local load_cache()"
    assert "def save_cache(" not in src, f"{path.name} still defines local save_cache()"
    assert "import cache_util" in src, f"{path.name} does not import cache_util"


# ---------------------------------------------------------------------------
# (b) no local fred/yfinance client copy under the CN-owned file set
# ---------------------------------------------------------------------------


def test_shipped_files_carry_no_fred_or_yfinance_fetch_logic():
    for path in SHIPPED_FILES:
        assert path.exists(), f"{path} not migrated yet"
        src = path.read_text()
        assert "stlouisfed" not in src, (
            f"{path.name} contains a FRED-specific marker — CN must not "
            "own a local fred_client.py copy (canonical copy is Task 3a's)"
        )
        assert "yf.Ticker" not in src, (
            f"{path.name} contains a yfinance-specific marker — CN must not "
            "own a local yfinance_client.py copy (canonical copy is Task 3a's)"
        )


# ---------------------------------------------------------------------------
# (c) pack_cn.build_pack() section-key shape matches data-cn/pack.py
# ---------------------------------------------------------------------------


def test_build_pack_snapshot_matches_legacy_shape(legacy_pack, new_pack):
    legacy_out = legacy_pack.pack_snapshot(TICKER)
    new_out = new_pack.build_pack("snapshot", [TICKER])
    assert set(new_out.keys()) == set(legacy_out.keys())
    assert new_out["pack"] == "snapshot"
    assert new_out["country"] == "CN"


def test_build_pack_memo_fetch_matches_legacy_shape(legacy_pack, new_pack):
    legacy_out = legacy_pack.pack_memo_fetch(TICKER)
    new_out = new_pack.build_pack("memo-fetch", [TICKER])
    assert set(new_out.keys()) == set(legacy_out.keys())


def test_build_pack_comps_multiples_matches_legacy_batch_shape(legacy_pack, new_pack):
    legacy_out = legacy_pack.pack_comps_multiples_batch([TICKER])
    new_out = new_pack.build_pack("comps-multiples", [TICKER])
    assert set(new_out.keys()) == set(legacy_out.keys())
    assert "info" in new_out


def test_build_pack_screener_batch_matches_legacy_shape(legacy_pack, new_pack):
    tickers = [TICKER, "000858.SZ"]
    legacy_out = legacy_pack.pack_screener_batch(tickers)
    new_out = new_pack.build_pack("screener-batch", tickers)
    assert set(new_out.keys()) == set(legacy_out.keys())


def test_build_pack_regime_pack_matches_legacy_shape(legacy_pack, new_pack):
    legacy_out = legacy_pack.pack_regime_pack()
    new_out = new_pack.build_pack("regime-pack", [])
    assert set(new_out.keys()) == set(legacy_out.keys())
    for source in ("nbs", "akshare", "fred", "markets"):
        assert source in new_out


def test_build_pack_rejects_unknown_pack_name(new_pack):
    with pytest.raises(ValueError):
        new_pack.build_pack("not-a-real-pack", [TICKER])


# ---------------------------------------------------------------------------
# (d) SUPPORTED_PACKS matches data-cn/pack.py's --pack choices
# ---------------------------------------------------------------------------


def test_supported_packs_matches_legacy_cli_choices(new_pack):
    assert tuple(new_pack.SUPPORTED_PACKS) == EXPECTED_SUPPORTED_PACKS
