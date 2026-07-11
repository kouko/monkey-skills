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
