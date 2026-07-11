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
  (c) pack_cn.build_pack() rejects an unknown pack name (self-contained
      build_pack behavior check).
  (d) pack_cn.SUPPORTED_PACKS matches the expected pack-type set
      (hardcoded — the legacy data-cn/scripts/pack.py this used to
      parity-check against is deleted; migration-fidelity for section-key
      shape was already verified pre-deletion).
"""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
from contextlib import redirect_stderr
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
NEW_DIR = ROOT / "skills" / "data-markets" / "scripts"

NEW_AKSHARE = NEW_DIR / "akshare_client.py"
NEW_NBS = NEW_DIR / "nbs_client.py"
NEW_PACK = NEW_DIR / "pack_cn.py"

SHIPPED_FILES = (NEW_AKSHARE, NEW_NBS, NEW_PACK)

TICKER = "600519.SS"

# Ground truth for (d) below — matches the old data-cn/scripts/pack.py:709-711
# `--pack` argparse choices.
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
def new_pack(monkeypatch):
    module = _load_module(NEW_PACK, "data_markets_pack_cn_for_migration_test")
    monkeypatch.setattr(module.subprocess, "run", _fake_subprocess_run)
    return module


# ---------------------------------------------------------------------------
# Pure-logic: _normalise_ticker auto-suffix heuristic (no network) —
# restored from the deleted tests/data/test_data_cn.py (round-1 gap: this
# offline unit test covered a still-live function, pack_cn._normalise_ticker,
# and was dropped along with the per-country skill deletion instead of
# migrating with the function).
# ---------------------------------------------------------------------------


def _load_pack_cn():
    return _load_module(NEW_PACK, "data_markets_pack_cn_for_normalise_test")


def test_cn_normalise_six_digit_starting_with_6_appends_ss():
    pack = _load_pack_cn()
    assert pack._normalise_ticker("600519") == "600519.SS"
    assert pack._normalise_ticker("601318") == "601318.SS"
    assert pack._normalise_ticker("603259") == "603259.SS"
    assert pack._normalise_ticker("688981") == "688981.SS"


def test_cn_normalise_six_digit_starting_with_0_appends_sz():
    pack = _load_pack_cn()
    assert pack._normalise_ticker("000858") == "000858.SZ"
    assert pack._normalise_ticker("000001") == "000001.SZ"
    assert pack._normalise_ticker("002594") == "002594.SZ"
    assert pack._normalise_ticker("300750") == "300750.SZ"


def test_cn_normalise_four_digit_appends_hk():
    pack = _load_pack_cn()
    assert pack._normalise_ticker("0700") == "0700.HK"
    assert pack._normalise_ticker("0005") == "0005.HK"


def test_cn_normalise_five_digit_appends_hk():
    """5-digit HK leading-zero form (e.g. 09988)."""
    pack = _load_pack_cn()
    assert pack._normalise_ticker("09988") == "09988.HK"
    assert pack._normalise_ticker("02318") == "02318.HK"
    assert pack._normalise_ticker("03690") == "03690.HK"


def test_cn_normalise_already_suffixed_passthrough():
    pack = _load_pack_cn()
    assert pack._normalise_ticker("600519.SS") == "600519.SS"
    assert pack._normalise_ticker("000858.SZ") == "000858.SZ"
    assert pack._normalise_ticker("0700.HK") == "0700.HK"
    # lowercase → uppercase
    assert pack._normalise_ticker("600519.ss") == "600519.SS"


def test_cn_normalise_bse_six_digit_warns_and_passthrough():
    """BSE codes (4xx/8xx 6-digit) — yfinance has no BSE; warn + passthrough."""
    pack = _load_pack_cn()
    buf = io.StringIO()
    with redirect_stderr(buf):
        out = pack._normalise_ticker("830799")
    assert out == "830799", "BSE ticker should pass through unchanged"
    assert "BSE" in buf.getvalue(), "expected stderr warning to mention BSE"


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


def test_build_pack_rejects_unknown_pack_name(new_pack):
    with pytest.raises(ValueError):
        new_pack.build_pack("not-a-real-pack", [TICKER])


# ---------------------------------------------------------------------------
# (d) SUPPORTED_PACKS matches data-cn/pack.py's --pack choices
# ---------------------------------------------------------------------------


def test_supported_packs_matches_legacy_cli_choices(new_pack):
    assert tuple(new_pack.SUPPORTED_PACKS) == EXPECTED_SUPPORTED_PACKS
