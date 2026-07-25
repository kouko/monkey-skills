"""test_sec_edgar_top_line.py — RED/GREEN tests for the top-line
(company total) revenue identification primitives (Task 1, docs/loom/
plans/2026-07-25-company-total-revenue.md): `_TOP_LINE_REVENUE_CONCEPTS`,
`_is_top_line_revenue_fact`, `select_top_line_concept`.

Every asserted concept/value below is READ from the captured live-probe
fixture `fixtures/topline_probe_2026-07-25.json` (8 filers, real SEC fetch,
2026-07-25) — never hand-typed, per repo memory
`hand-authored-fixture-is-a-fabrication-risk`.

Split into focused, independently-failing functions (code-quality-reviewer
round 1, F.I.R.S.T "Independent" — a single ~106-line function bundling five
behaviours meant one failed assertion gave zero signal on the other four);
parametrized wherever the cases are genuinely data-driven so each filer's
case fails independently and names itself in pytest's output.

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_helpers():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client
    return sec_edgar_client


def _probe() -> list[dict]:
    return json.loads((FIXTURES / "topline_probe_2026-07-25.json").read_text())


def _filer(probe: list[dict], ticker: str) -> dict:
    for entry in probe:
        if entry["ticker"] == ticker:
            return entry
    raise KeyError(ticker)


def _fact(concept: str, sample: dict, *, is_dimensioned: bool) -> dict:
    """Build a synthetic fact dict in the module's real record shape
    (mirrors the `raw_fact` shape in `fixtures/xbrl_concept_filter_cases.json`
    and `test_sec_edgar_dimensional.py`'s fixtures) from one probe `sample` —
    every value comes from the captured probe JSON, never hand-typed."""
    return {
        "concept": concept,
        "is_dimensioned": is_dimensioned,
        "period_type": "duration",
        "currency": "USD",
        "unit_ref": "usd",
        "numeric_value": sample["value"],
        "period_start": sample["period_start"],
        "period_end": sample["period_end"],
    }


# JPM's non-allowlist flat revenue COMPONENTS — probe hazard #1: 7 flat
# revenue-shaped concepts, only 2 of which are the top-line total.
_JPM_COMPONENT_CONCEPTS = (
    "us-gaap:InvestmentBankingRevenue",
    "us-gaap:PrincipalTransactionsRevenue",
    "us-gaap:BrokerageCommissionsRevenue",
    "jpm:InvestmentBankingAdvisoryFeeRevenue",
    "jpm:AdministrativeServicesRevenue1",
)


def test_top_line_allowlist_is_closed_and_distinct():
    """(a) the allowlist is closed, ORDERED, and a DISTINCT tuple from the
    existing (broader) dimensional allow-list — never reused/extended."""
    mod = _load_helpers()
    assert mod._TOP_LINE_REVENUE_CONCEPTS == (
        "Revenues",
        "RevenuesNetOfInterestExpense",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
    )
    assert mod._TOP_LINE_REVENUE_CONCEPTS != mod._REVENUE_ALLOW_CONCEPT_LOCAL_NAMES, (
        "the top-line allowlist must be its own closed list, not a reuse or "
        "extension of the dimensional allow-list"
    )


@pytest.mark.parametrize("concept", _JPM_COMPONENT_CONCEPTS)
def test_top_line_rejects_component_concepts(concept):
    """JPM's non-allowlist flat revenue COMPONENTS are REJECTED even though
    they are flat (is_dimensioned=False) and revenue-shaped."""
    mod = _load_helpers()
    jpm = _filer(_probe(), "JPM")["A_flat"]
    fact = _fact(concept, jpm[concept]["sample"], is_dimensioned=False)
    assert mod._is_top_line_revenue_fact(fact) is False, (
        f"{concept} is an income-statement COMPONENT, not the top-line "
        "total — must be REJECTED even though it is flat and revenue-shaped"
    )


@pytest.mark.parametrize("ticker", ["JPM", "NVDA"])
def test_top_line_accepts_flat_revenue_totals(ticker):
    """JPM's and NVDA's flat `us-gaap:Revenues` are ACCEPTED."""
    mod = _load_helpers()
    flat = _filer(_probe(), ticker)["A_flat"]
    fact = _fact("us-gaap:Revenues", flat["us-gaap:Revenues"]["sample"], is_dimensioned=False)
    assert mod._is_top_line_revenue_fact(fact) is True


def test_top_line_rejects_dimensioned_qualifier_only_fact():
    """XOM's `us-gaap:Revenues` carrying a consolidation qualifier
    (segment view, is_dimensioned=True) is REJECTED — hazard #2: a
    qualifier-only fact is not the consolidated total."""
    mod = _load_helpers()
    xom_entry = _filer(_probe(), "XOM")
    xom_segment_sample = xom_entry["B_qualifier_only"]["us-gaap:Revenues"]["sample"]
    xom_segment_fact = _fact("us-gaap:Revenues", xom_segment_sample, is_dimensioned=True)
    assert mod._is_top_line_revenue_fact(xom_segment_fact) is False, (
        "a dimensioned (qualifier-only) us-gaap:Revenues fact — the "
        "segment/pre-elimination view — must never be treated as the "
        "top-line total"
    )
    xom_true_total = xom_entry["A_flat"]["us-gaap:Revenues"]["sample"]["value"]
    assert xom_segment_sample["value"] != xom_true_total, (
        "test-setup sanity: the rejected segment value must actually differ "
        "from the true flat total, or this test proves nothing"
    )


@pytest.mark.parametrize(
    "ticker,expected_concept",
    [
        ("JPM", "Revenues"),
        ("WMT", "Revenues"),
        ("AAPL", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ],
)
def test_select_top_line_concept_first_present_ordering(ticker, expected_concept):
    """`select_top_line_concept` picks the first-present allowlist entry
    among a filing's flat candidates, per-filer."""
    mod = _load_helpers()
    flat = _filer(_probe(), ticker)["A_flat"]
    facts = [
        _fact(concept, entry["sample"], is_dimensioned=False)
        for concept, entry in flat.items()
    ]
    if ticker == "JPM":
        assert len(facts) == 7, "test-setup sanity: JPM probe carries 7 flat concepts"
    elif ticker == "WMT":
        assert (
            flat["us-gaap:Revenues"]["sample"]["value"]
            > flat["us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"]["sample"]["value"]
        ), "test-setup sanity: WMT's Revenues must be the larger figure per the probe"
    elif ticker == "AAPL":
        assert len(facts) == 1, "test-setup sanity: AAPL has only one flat candidate"

    assert mod.select_top_line_concept(facts) == expected_concept


@pytest.mark.parametrize("case", ["empty_list", "components_only"])
def test_select_top_line_concept_returns_none_for_components_only(case):
    """None when there are no qualifying candidates: either no facts at all,
    or every fact is a non-allowlist component."""
    mod = _load_helpers()
    if case == "empty_list":
        facts: list[dict] = []
    else:
        jpm = _filer(_probe(), "JPM")["A_flat"]
        facts = [
            _fact(concept, jpm[concept]["sample"], is_dimensioned=False)
            for concept in _JPM_COMPONENT_CONCEPTS
        ]
    assert mod.select_top_line_concept(facts) is None
