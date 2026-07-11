"""test_data_markets_us.py — Task 3a migration contract.

Verifies the US client + pack-builder migration into
skills/data-markets/scripts/:

  (a) migrated client files (yfinance_client.py, fred_client.py,
      sec_edgar_client.py) define no local cache-helper boilerplate
      (_CACHE_BASE / CACHE_DIR / CACHE_TTL_* constants,
      get_cache_path / load_cache / save_cache or underscore-variant
      defs) — source-scan check, no execution — and `import cache_util`.
  (b) pack_us.build_pack("snapshot", ["AAPL"]) produces a dict whose
      top-level section keys match the current data-us fixture sample
      (fixture-fed / mocked subprocess — offline, no network).
  (c) pack_us.SUPPORTED_PACKS matches data-us/scripts/pack.py's current
      --pack choices.

Offline: no network calls. The subprocess boundary (run_client) is
mocked in test (b).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = ROOT / "tests" / "data" / "fixtures"

CLIENT_FILES = ["yfinance_client.py", "fred_client.py", "sec_edgar_client.py"]

# Local cache boilerplate being deleted per Task 3a — module-level
# constants and function definitions, matched at line start (so a mention
# inside a comment/docstring sentence doesn't false-positive, but an
# actual definition/assignment does).
_LOCAL_CACHE_HELPER_PATTERNS = [
    r"^_CACHE_BASE\s*=",
    r"^CACHE_DIR\s*=",
    r"^CACHE_TTL_\w*\s*=",
    r"^\s*def get_cache_path\(",
    r"^\s*def load_cache\(",
    r"^\s*def save_cache\(",
    r"^\s*def _load_cache\(",
    r"^\s*def _save_cache\(",
    r"^\s*def _cache_path\(",
]


def test_us_migration_contract():
    # --- (a) migrated clients: no local cache boilerplate, cache_util imported ---
    for fname in CLIENT_FILES:
        path = MARKETS_SCRIPTS / fname
        assert path.exists(), f"missing migrated client: {fname}"
        text = path.read_text()

        for pattern in _LOCAL_CACHE_HELPER_PATTERNS:
            assert not re.search(pattern, text, re.MULTILINE), (
                f"{fname} still defines local cache boilerplate matching {pattern!r}"
            )

        assert re.search(r"^import cache_util\s*$", text, re.MULTILINE), (
            f"{fname} does not `import cache_util`"
        )

    pack_us_path = MARKETS_SCRIPTS / "pack_us.py"
    assert pack_us_path.exists(), "missing pack_us.py"

    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402  (path-dependent import, must follow sys.path insert)

    # --- (c) SUPPORTED_PACKS matches data-us/scripts/pack.py's --pack choices ---
    assert pack_us.SUPPORTED_PACKS == (
        "snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack",
    ), f"SUPPORTED_PACKS diverges from data-us pack.py --pack choices: {pack_us.SUPPORTED_PACKS}"

    # --- (b) build_pack("snapshot", ...) section keys match fixture (fixture-fed, mocked subprocess) ---
    fixture = json.loads((FIXTURES / "data-us-snapshot-sample.json").read_text())
    expected_keys = set(fixture.keys())

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = [
            fixture["company_info"],
            fixture["price_history"],
        ]
        result = pack_us.build_pack("snapshot", ["AAPL"])

    assert mock_run_client.call_count == 2, (
        "pack_snapshot should shell out exactly twice (info, history) via run_client"
    )
    assert set(result.keys()) == expected_keys, (
        f"pack_us snapshot section keys diverge from data-us fixture: "
        f"missing={expected_keys - set(result.keys())} "
        f"extra={set(result.keys()) - expected_keys}"
    )
    assert result["ticker"] == "AAPL"
    assert result["company_info"] == fixture["company_info"]
    assert result["price_history"] == fixture["price_history"]


def _mock_run_client_for_memo_fetch(fixture: dict):
    """Route mocked run_client calls to fixture sections by script + args,
    so pack_memo_fetch's ~40 DCF-concept sub-calls (one per XBRL concept in
    DCF_CONCEPT_MAPPING) don't need individually-ordered side_effect entries.
    Concept-fetch calls return {} (no `observations`) — pack_us._fetch_dcf_concepts
    drops those, so income_statement/cash_flow/balance_sheet still assemble
    (as empty-series dicts) without asserting on their inner values here.
    """
    import pack_us  # noqa: E402  (module under test, already on sys.path)

    def _side_effect(script, extra_args, timeout=pack_us.CLIENT_TIMEOUT_SECONDS):
        if script == pack_us.YF:
            if "info" in extra_args:
                return fixture["company_info"]
            return fixture["price_history"]
        if script == pack_us.SEC:
            if "filings" in extra_args:
                return fixture["sec_filings"]
            if "--concept" in extra_args:
                return {}
            return fixture["sec_facts"]
        raise AssertionError(f"unexpected run_client script: {script}")

    return _side_effect


def test_us_migration_memo_fetch_section_keys():
    """pack_us.build_pack("memo-fetch", ...) top-level section keys match
    the data-us memo-fetch fixture (fixture-fed / mocked subprocess —
    offline, no network). Separate from the snapshot test above for
    F.I.R.S.T independence (one pack type's assertion failing must not
    hide the other's)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import pack_us  # noqa: E402  (path-dependent import, must follow sys.path insert)

    fixture = json.loads((FIXTURES / "data-us-memo-fetch-sample.json").read_text())
    expected_keys = set(fixture.keys())

    with mock.patch.object(pack_us, "run_client") as mock_run_client:
        mock_run_client.side_effect = _mock_run_client_for_memo_fetch(fixture)
        result = pack_us.build_pack("memo-fetch", ["AAPL"])

    assert set(result.keys()) == expected_keys, (
        f"pack_us memo-fetch section keys diverge from data-us fixture: "
        f"missing={expected_keys - set(result.keys())} "
        f"extra={set(result.keys()) - expected_keys}"
    )
    assert result["ticker"] == "AAPL"
    assert result["company_info"] == fixture["company_info"]
    assert result["sec_filings"] == fixture["sec_filings"]
