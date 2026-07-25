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

import datetime
import importlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_helpers():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import sec_edgar_client
    return sec_edgar_client


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in
    sys.modules — same convention as test_sec_edgar_dimensional.py's
    `sec_client` fixture (offline CI installs neither edgartools nor a
    pinned requests build; `extract_dimensional_revenue` lazily
    `import edgar`s at call time, so a bare `_load_helpers()` import is not
    enough once the function actually runs)."""
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


def _make_topline_filing(
    *, accession, form, filing_date, period_of_report, revenue_rows,
    fiscal_year_end, include_dei=True,
):
    """Build a fake edgartools Filing whose `.xbrl()` yields exactly
    `revenue_rows` (+ dei cover rows) — the shape
    `extract_dimensional_revenue`'s per-filing loop reads (Task 2, docs/
    loom/plans/2026-07-25-company-total-revenue.md)."""
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    rows = list(revenue_rows)
    if include_dei:
        rows += [
            {"concept": "dei:DocumentFiscalPeriodFocus", "value": "FY"},
            {"concept": "dei:CurrentFiscalYearEndDate", "value": fiscal_year_end},
            {"concept": "dei:DocumentFiscalYearFocus", "value": "2026"},
        ]
    xb.facts.to_dataframe.return_value.to_dict.return_value = rows
    filing = SimpleNamespace(
        accession_no=accession, filing_date=filing_date, form=form,
        period_of_report=period_of_report,
    )
    filing.xbrl = lambda bound=xb: bound
    return filing


def _flat_revenue_row(concept: str, sample: dict) -> dict:
    """A synthetic flat (is_dimensioned=False) revenue fact row in the
    module's real record shape, built entirely from a captured probe
    `sample` — never hand-typed values."""
    return {
        "is_dimensioned": False,
        "concept": concept,
        "numeric_value": sample["value"],
        "unit_ref": "usd",
        "currency": "USD",
        "period_type": "duration",
        "period_start": sample["period_start"],
        "period_end": sample["period_end"],
        "period_instant": None,
    }


def _dimensioned_revenue_row(concept: str, sample: dict) -> dict:
    """A synthetic DIMENSIONED (is_dimensioned=True) revenue fact row
    carrying a `srt:ConsolidationItemsAxis` qualifier member — the shape
    `_dimension_signature` reads (`dim_srt_ConsolidationItemsAxis`, real
    key convention per test_sec_edgar_dimensional.py's
    `test_build_fact_consolidated_entities_axis_promoted_to_consolidation`).
    Built entirely from a captured probe `B_qualifier_only` sample — never
    hand-typed values. `sample["consolidation"]` is the bare member local
    name (e.g. "OperatingSegmentsMember"); the dim_ column carries the
    namespace-prefixed form real edgartools rows use."""
    row = _flat_revenue_row(concept, sample)
    row["is_dimensioned"] = True
    row["dim_srt_ConsolidationItemsAxis"] = f"us-gaap:{sample['consolidation']}"
    return row


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


# ---------------------------------------------------------------------------
# Task 2 — extract_dimensional_revenue also emits the filing's ONE winning
# flat top-line fact into the SAME `facts` list (dimensions == {}).
# ---------------------------------------------------------------------------

def test_extractor_emits_one_flat_top_line_per_filing(sec_client):
    """Captured NVDA shape (non-December FYE, probe hazard-free — its only
    flat candidate is `us-gaap:Revenues`): the pack contains exactly ONE
    flat top-line fact, `dimensions == {}`, and it carries a non-None
    `fiscal_year` / `fiscal_quarter` / `period_start` derived from the
    filing's own dei calendar — RED today, `extract_dimensional_revenue`
    does not look at flat facts at all."""
    nvda = _filer(_probe(), "NVDA")
    sample = nvda["A_flat"]["us-gaap:Revenues"]["sample"]
    filing = _make_topline_filing(
        accession=nvda["accession"], form="10-K",
        filing_date=datetime.date(2026, 2, 20),
        period_of_report=nvda["period_of_report"],
        revenue_rows=[_flat_revenue_row("us-gaap:Revenues", sample)],
        fiscal_year_end="--01-25",
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("NVDA", form="10-K")

    assert "error" not in pack, pack
    top_line_facts = [f for f in pack["facts"] if f["dimensions"] == {}]
    assert len(top_line_facts) == 1, pack["facts"]
    fact = top_line_facts[0]
    assert fact["concept"] == "us-gaap:Revenues"
    assert fact["value"] == sample["value"]
    assert fact["accession"] == nvda["accession"]
    assert fact["fiscal_year"] is not None
    assert fact["fiscal_quarter"] is not None
    assert fact["period_start"] == sample["period_start"]
    assert pack["coverage"]["top_line_gaps"] == []


def test_extractor_records_coverage_gap_when_filing_has_no_top_line_candidate(sec_client):
    """A filing whose only revenue facts are JPM's non-allowlist flat
    COMPONENTS (InvestmentBankingRevenue etc. — no `Revenues` /
    `RevenuesNetOfInterestExpense` / RFCC row present) yields ZERO flat
    top-line facts and ONE named `coverage` gap entry naming the
    accession — never fabricated, never silently dropped."""
    jpm = _filer(_probe(), "JPM")
    component_rows = [
        _flat_revenue_row(concept, jpm["A_flat"][concept]["sample"])
        for concept in _JPM_COMPONENT_CONCEPTS
    ]
    filing = _make_topline_filing(
        accession=jpm["accession"], form="10-K",
        filing_date=datetime.date(2026, 2, 20),
        period_of_report=jpm["period_of_report"],
        revenue_rows=component_rows,
        fiscal_year_end="--12-31",
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 19617
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("JPM", form="10-K")

    assert "error" not in pack, pack
    top_line_facts = [f for f in pack["facts"] if f["dimensions"] == {}]
    assert top_line_facts == [], pack["facts"]

    gaps = pack["coverage"]["top_line_gaps"]
    assert len(gaps) == 1, gaps
    assert gaps[0]["accessions"] == [jpm["accession"]]
    assert gaps[0]["reason"]


def test_extractor_emits_only_allowlist_order_winner_when_two_concepts_present(sec_client):
    """A WMT-shaped filing carries TWO flat top-line candidates —
    `us-gaap:Revenues` (713,163M) AND `RevenueFromContractWithCustomer
    ExcludingAssessedTax` (706,413M). Exactly ONE top-line fact must be
    emitted, and it must be the allowlist-ORDER winner (`Revenues`), not
    merely 'some one of the two' — pins the plan's §Notes 'one winner per
    filing' rule at the extractor level (code-quality-reviewer 🟡: this was
    previously untested, so dropping the `== winning_top_line_concept`
    match — admitting every `_is_top_line_revenue_fact`-passing fact —
    would still pass a single-candidate fixture)."""
    wmt = _filer(_probe(), "WMT")
    revenues_sample = wmt["A_flat"]["us-gaap:Revenues"]["sample"]
    rfcc_sample = wmt["A_flat"][
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    ]["sample"]
    assert revenues_sample["value"] != rfcc_sample["value"], (
        "test-setup sanity: the two candidates must be genuinely distinct "
        "values, or emitting the wrong one would go unnoticed"
    )
    filing = _make_topline_filing(
        accession=wmt["accession"], form="10-K",
        filing_date=datetime.date(2026, 3, 20),
        period_of_report=wmt["period_of_report"],
        revenue_rows=[
            _flat_revenue_row("us-gaap:Revenues", revenues_sample),
            _flat_revenue_row(
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                rfcc_sample,
            ),
        ],
        fiscal_year_end="--01-31",
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 104169
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("WMT", form="10-K")

    assert "error" not in pack, pack
    top_line_facts = [f for f in pack["facts"] if f["dimensions"] == {}]
    assert len(top_line_facts) == 1, (
        "exactly ONE winner per filing — never both candidates: "
        f"{top_line_facts}"
    )
    assert top_line_facts[0]["concept"] == "us-gaap:Revenues"
    assert top_line_facts[0]["value"] == revenues_sample["value"]


def test_extractor_rejects_dimensioned_fact_sharing_the_winning_concept_name(sec_client):
    """An XOM-shaped filing carries flat `us-gaap:Revenues` (332,238M, the
    true consolidated total) PLUS a DIMENSIONED `us-gaap:Revenues` fact
    under `ConsolidationItemsAxis=OperatingSegmentsMember` (452,209M, the
    segment/pre-elimination view) — probe hazard #2. Only the flat fact may
    be admitted as the top-line total; the emitted VALUE is asserted so the
    test fails if the dimensioned fact wins instead (code-quality-reviewer
    🟡: this was previously untested, so dropping the
    `_is_top_line_revenue_fact(fact)` call from `is_winning_top_line` —
    admitting any fact whose concept name matches the winner, regardless of
    `is_dimensioned` — would still pass a fixture with no such fact)."""
    xom = _filer(_probe(), "XOM")
    flat_sample = xom["A_flat"]["us-gaap:Revenues"]["sample"]
    dimensioned_sample = xom["B_qualifier_only"]["us-gaap:Revenues"]["sample"]
    assert flat_sample["value"] != dimensioned_sample["value"], (
        "test-setup sanity: the segment-view value must actually differ "
        "from the true flat total, or this test proves nothing"
    )
    filing = _make_topline_filing(
        accession=xom["accession"], form="10-K",
        filing_date=datetime.date(2026, 2, 20),
        period_of_report=xom["period_of_report"],
        revenue_rows=[
            _flat_revenue_row("us-gaap:Revenues", flat_sample),
            _dimensioned_revenue_row("us-gaap:Revenues", dimensioned_sample),
        ],
        fiscal_year_end="--12-31",
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 34088
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("XOM", form="10-K")

    assert "error" not in pack, pack
    top_line_facts = [f for f in pack["facts"] if f["dimensions"] == {}]
    assert len(top_line_facts) == 1, (
        "the dimensioned segment-view fact must never be admitted as a "
        f"top-line total: {top_line_facts}"
    )
    assert top_line_facts[0]["value"] == flat_sample["value"], (
        "the emitted top-line value must be the flat consolidated total "
        "(332,238M), never the dimensioned segment-view value (452,209M)"
    )
