"""test_capture_us_statement_shapes_legacy_selector.py — pins the FROZEN
pre-Task-2 top-line concept selector (`_legacy_top_line_winner` +
`_shipped_lane_truncation` in
`fixtures/capture_us_statement_shapes_probe.py`) against a synthetic
companyfacts payload, so the M4 measurement's selection algorithm stays
under test even though the capture script itself is never pytest-collected
(it is not a `test_*` module and hits `data.sec.gov` live).

WHY THIS EXISTS. `_legacy_top_line_winner` is a frozen reproduction of
`build_top_line_backfill`'s per-company "first allowlist concept that
returns any rows wins, then break" rule as it stood at the pre-Task-2
baseline commit `3ee2fcd3` — see that function's docstring for why it must
never be wired to the live import. A frozen copy with no test exercising
it can rot silently (drift from what it claims to reproduce with nothing
catching it), so this file pins its one load-bearing behavior: given a
filer whose revenue tag SWITCHED mid-history (the ASC-606 migration
shape), the naive selector must still pick the FIRST chain concept with
any rows and stop — even when a later chain concept carries the filer's
more recent history — because that stale pick is exactly the bug M4
measures.

Offline: synthetic companyfacts payload, no network marker, part of the
default `not network` suite:
  PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_MARKETS_SCRIPTS = _ROOT / "skills" / "data-markets" / "scripts"
_FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def probe_module():
    """Import `capture_us_statement_shapes_probe` with `edgar` AND
    `requests` stubbed in `sys.modules` — same convention
    `test_sec_edgar_top_line_backfill.py::sec_client` uses — because the
    probe script's module-level `import sec_edgar_client as sec` pulls in
    `sec_edgar_client`'s own module-level `import requests`/`edgartools`,
    neither of which the offline suite installs."""
    for path in (str(_MARKETS_SCRIPTS), str(_FIXTURES_DIR)):
        if path not in sys.path:
            sys.path.insert(0, path)
    import importlib

    edgar_stub = mock.MagicMock(name="edgar")
    requests_stub = mock.MagicMock(name="requests")
    saved_edgar = sys.modules.get("edgar")
    saved_requests = sys.modules.get("requests")
    saved_sec = sys.modules.get("sec_edgar_client")
    saved_probe = sys.modules.get("capture_us_statement_shapes_probe")
    sys.modules["edgar"] = edgar_stub
    sys.modules["requests"] = requests_stub
    sys.modules.pop("sec_edgar_client", None)
    sys.modules.pop("capture_us_statement_shapes_probe", None)
    module = importlib.import_module("capture_us_statement_shapes_probe")
    try:
        yield module
    finally:
        for name, saved in (
            ("edgar", saved_edgar),
            ("requests", saved_requests),
            ("sec_edgar_client", saved_sec),
            ("capture_us_statement_shapes_probe", saved_probe),
        ):
            if saved is not None:
                sys.modules[name] = saved
            else:
                sys.modules.pop(name, None)


def _facts_with_rows(tag: str, ends: list[str]) -> dict:
    return {
        "units": {
            "USD": [
                {"start": f"{end[:4]}-01-01", "end": end, "form": "10-K",
                 "filed": f"{end[:4]}-03-01", "val": 1.0, "accn": f"acc-{end}"}
                for end in ends
            ]
        }
    }


def test_legacy_selector_picks_first_chain_hit_even_when_stale(probe_module):
    """A filer that switched revenue tags mid-history (ASC-606 migration):
    `Revenues` (chain position 0) only ever carried the OLD, pre-switch
    years; `RevenueFromContractWithCustomerExcludingAssessedTax` (chain
    position 2) carries the filer's full, more recent history. The naive
    per-company selector must still return `Revenues` — the first chain
    concept with ANY row — reproducing the exact staleness this M4
    measurement exists to catch, not the chain-wide best concept."""
    facts = {
        "us-gaap": {
            "Revenues": _facts_with_rows("Revenues", ["2009-12-31", "2010-12-31"]),
            "RevenueFromContractWithCustomerExcludingAssessedTax": _facts_with_rows(
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                ["2024-12-31", "2025-12-31"],
            ),
        }
    }
    assert probe_module._legacy_top_line_winner(facts) == "Revenues"


def test_legacy_selector_returns_none_when_no_chain_concept_has_rows(probe_module):
    assert probe_module._legacy_top_line_winner({"us-gaap": {}}) is None


def test_shipped_lane_truncation_reports_years_lost_against_chain_best(probe_module):
    facts = {
        "us-gaap": {
            "Revenues": _facts_with_rows("Revenues", ["2009-12-31", "2010-12-31"]),
            "RevenueFromContractWithCustomerExcludingAssessedTax": _facts_with_rows(
                "RevenueFromContractWithCustomerExcludingAssessedTax",
                ["2024-12-31", "2025-12-31"],
            ),
        }
    }
    field_coverage = {"revenue": {"best_newest_10k_end": "2025-12-31"}}
    result = probe_module._shipped_lane_truncation(facts, field_coverage)
    assert result["legacy_winning_concept"] == "Revenues"
    assert result["last_period_end"] == "2010-12-31"
    assert result["years_lost_vs_chain_best"] == 15


def test_shipped_lane_truncation_errors_loud_when_no_concept_matches(probe_module):
    result = probe_module._shipped_lane_truncation({"us-gaap": {}}, {"revenue": {}})
    assert "error" in result
