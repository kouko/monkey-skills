"""test_sec_edgar_dimensional.py — OFFLINE regression tests for
`sec_edgar_client.extract_dimensional_revenue` and its two PURE helpers
(Task 5 revision 2, docs/loom/plans/2026-07-14-operational-kpi-companyfacts-pilot.md).

Two things this file closes:

1. (code-quality-reviewer 🟡) The "Apple false-negative lesson" — Apple's
   product-line axis moved from `us-gaap:ProductOrServiceAxis` (pre-2018) to
   `srt:ProductOrServiceAxis` (post-2018) across the 2018 revenue-recognition
   tagging-regime shift, so filtering a single namespace silently drops half
   the fact's history — had NO offline regression test; only the network-
   marked live anchor (test_sec_edgar_dimensional_live.py) exercised it.
   `_is_dimensional_revenue_axis` / `_is_revenue_concept` are pure string
   functions (no edgartools/network needed), so they are unit-tested directly
   here.

2. (spec-reviewer NEEDS_REVISION, plan amendment (a)) `extract_dimensional_revenue`
   must FAIL LOUD — raise `ValueError` naming `period_end` — when a dimensional
   revenue fact has no `period_end`, instead of silently appending a
   null-dated fact (fiscal_year=None). This mirrors the module's `edgar`
   sys.modules-stub mocking convention (test_sec_narrative.py's `sec_client`
   fixture) since `extract_dimensional_revenue` itself is not pure.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import datetime
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in
    sys.modules — same convention as test_sec_narrative.py's `sec_client`
    fixture (offline CI installs neither edgartools nor requests)."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    edgar_stub = mock.MagicMock(name="edgar")
    requests_stub = mock.MagicMock(name="requests")
    saved_edgar = sys.modules.get("edgar")
    saved_requests = sys.modules.get("requests")
    saved_client = sys.modules.get("sec_edgar_client")
    sys.modules["edgar"] = edgar_stub
    sys.modules["requests"] = requests_stub
    sys.modules.pop("sec_edgar_client", None)
    module = importlib.import_module("sec_edgar_client")
    module.edgar_stub = edgar_stub
    try:
        yield module
    finally:
        if saved_edgar is not None:
            sys.modules["edgar"] = saved_edgar
        else:
            sys.modules.pop("edgar", None)
        if saved_requests is not None:
            sys.modules["requests"] = saved_requests
        else:
            sys.modules.pop("requests", None)
        if saved_client is not None:
            sys.modules["sec_edgar_client"] = saved_client
        else:
            sys.modules.pop("sec_edgar_client", None)


# ---------------------------------------------------------------------------
# Pure-helper unit tests (no edgar/network) — the both-namespace lesson
# ---------------------------------------------------------------------------

def _load_helpers():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client
    return sec_edgar_client


def test_is_dimensional_revenue_axis_matches_both_namespaces():
    mod = _load_helpers()
    for local_name in (
        "ProductOrServiceAxis",
        "StatementBusinessSegmentsAxis",
        "StatementGeographicalAxis",
    ):
        assert mod._is_dimensional_revenue_axis(f"us-gaap:{local_name}") is True, (
            f"us-gaap:{local_name} must match (pre-2018 tagging regime)"
        )
        assert mod._is_dimensional_revenue_axis(f"srt:{local_name}") is True, (
            f"srt:{local_name} must match (post-2018 tagging regime) — "
            "the Apple false-negative lesson: filtering one namespace drops "
            "half the fact's history"
        )


def test_is_dimensional_revenue_axis_rejects_non_dimensional_axis():
    mod = _load_helpers()
    assert mod._is_dimensional_revenue_axis("us-gaap:StatementEquityComponentsAxis") is False
    assert mod._is_dimensional_revenue_axis(None) is False


def test_is_revenue_concept_matches_pre_and_post_2018_concepts():
    mod = _load_helpers()
    assert mod._is_revenue_concept("us-gaap:SalesRevenueNet") is True
    assert (
        mod._is_revenue_concept("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax")
        is True
    )
    assert mod._is_revenue_concept("us-gaap:CostOfGoodsSold") is False
    assert mod._is_revenue_concept(None) is False


# ---------------------------------------------------------------------------
# extract_dimensional_revenue — fail-loud on a null period_end
# ---------------------------------------------------------------------------

def _real_shape_filing(*, accession="0000320193-24-000123"):
    return SimpleNamespace(
        accession_no=accession,
        filing_date=datetime.date(2024, 11, 1),
    )


def test_extract_dimensional_revenue_raises_on_missing_period_end(sec_client, monkeypatch):
    """A dimensional revenue fact with no period_end must never enter the
    pack as a null-dated point — fail loud with a ValueError naming
    period_end, matching the module's anti-fabrication posture (plan
    amendment (a), spec-reviewer NEEDS_REVISION)."""
    filing = _real_shape_filing()
    xb = mock.MagicMock(name="xbrl")
    xb.facts.to_dataframe.return_value.to_dict.return_value = [
        {
            "is_dimensioned": True,
            "dimension": "srt:ProductOrServiceAxis",
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "member": "aapl:IPhoneMember",
            "numeric_value": 100.0,
            "period_type": "duration",
            "period_end": None,
            "period_instant": None,
        },
    ]
    filing.xbrl = lambda: xb

    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value.latest.return_value = filing
    sec_client.edgar_stub.Company.return_value = company

    with pytest.raises(ValueError, match="period_end"):
        sec_client.extract_dimensional_revenue("AAPL")
