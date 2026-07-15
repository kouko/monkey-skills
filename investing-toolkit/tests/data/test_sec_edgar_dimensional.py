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
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


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


def test_is_revenue_concept_excludes_deferred_revenue():
    """Deferred-revenue / contract-liability rollforward concepts merely
    CONTAIN "Revenue" but are NOT operating revenue — plan Task 5
    (docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md).
    Real operating-revenue concepts across tagging regimes must stay True;
    the ContractWithCustomerLiabilityRevenue* reconciliation family must be
    excluded."""
    mod = _load_helpers()

    for real_concept in (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:SalesRevenueNet",
        "us-gaap:Revenues",
        "us-gaap:RevenuesNetOfInterestExpense",
        "us-gaap:AdvertisingRevenue",
    ):
        assert mod._is_revenue_concept(real_concept) is True, (
            f"{real_concept} is real operating revenue and must stay True"
        )

    for deferred_concept in (
        "us-gaap:ContractWithCustomerLiabilityRevenueRecognized",
        "us-gaap:ContractWithCustomerLiabilityRevenueRecognizedExcludingOpeningBalance",
    ):
        assert mod._is_revenue_concept(deferred_concept) is False, (
            f"{deferred_concept} is a deferred-revenue/contract-liability "
            "reconciliation item, not operating revenue — must be excluded"
        )


# ---------------------------------------------------------------------------
# extract_dimensional_revenue — fail-loud on a null period_end
# ---------------------------------------------------------------------------

def _real_shape_filing(*, accession="0000320193-24-000123", form="10-K"):
    return SimpleNamespace(
        accession_no=accession,
        filing_date=datetime.date(2024, 11, 1),
        form=form,
    )


def test_extract_dimensional_revenue_raises_on_missing_period_end(sec_client, monkeypatch):
    """A dimensional revenue fact with no period_end must never enter the
    pack as a null-dated point — fail loud with a ValueError naming
    period_end, matching the module's anti-fabrication posture (plan
    amendment (a), spec-reviewer NEEDS_REVISION).

    Uses the full-signature `dim_<axis>` per-row column shape (Task 4,
    docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md)
    — NOT the retired singular `dimension`/`member` convenience columns."""
    filing = _real_shape_filing()
    xb = mock.MagicMock(name="xbrl")
    xb.facts.to_dataframe.return_value.to_dict.return_value = [
        {
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "aapl:IPhoneMember",
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
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
    # Task 6 exact-form-match selection (docs/loom/plans/2026-07-15-
    # operational-kpi-full-dimensional-signature.md) iterates
    # `get_filings(...)` and filters to an EXACT form match rather than
    # calling the loose-matching `.latest()` — the mock must be iterable.
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    with pytest.raises(ValueError, match="period_end"):
        sec_client.extract_dimensional_revenue("AAPL")


# ---------------------------------------------------------------------------
# Task 4 — full-signature fact-pack: `dimensions` map (ALL real breakdown
# axes) + separate `consolidation` qualifier, replacing single {axis, member}
# ---------------------------------------------------------------------------

def test_build_fact_full_signature():
    """`_build_dimensional_revenue_fact` builds `dimensions` from the ROW'S
    per-axis `dim_<namespace>_<AxisLocalName>` columns (a single row/context
    can carry MULTIPLE populated dim_<axis> columns at once — live-verified
    on a real NFLX 10-K row 2026-07-15: `dim_srt_ProductOrServiceAxis` AND
    `dim_srt_StatementGeographicalAxis` both populated on the SAME row) —
    never from the singular `dimension`/`member` convenience columns (the
    wrong-layer trap: those expose only ONE axis)."""
    mod = _load_helpers()

    # NFLX-shaped row: two REAL breakdown axes on one row, no consolidation
    # qualifier — matches the committed fixture's US&Canada streaming slice.
    nflx_row = {
        "concept": "us-gaap:Revenues",
        "dim_srt_ProductOrServiceAxis": "nflx:StreamingMember",
        "dim_srt_StatementGeographicalAxis": "nflx:UnitedStatesAndCanadaMember",
        "numeric_value": 19957152000.0,
        "period_type": "duration",
        "period_end": "2025-12-31",
    }
    fact = mod._build_dimensional_revenue_fact(nflx_row, "NFLX", "0001065280-26-000034", "2026-01-23")
    assert fact["dimensions"] == {
        "ProductOrService": "StreamingMember",
        "StatementGeographical": "UnitedStatesAndCanadaMember",
    }
    assert fact["consolidation"] is None
    assert "axis" not in fact and "member" not in fact

    # AAPL-shaped row: a segment breakdown QUALIFIED by
    # srt:ConsolidationItemsAxis — the qualifier is captured separately as
    # `consolidation`, never folded into `dimensions` as a second axis.
    aapl_row = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dim_us-gaap_StatementBusinessSegmentsAxis": "aapl:AmericasSegmentMember",
        "dim_srt_ConsolidationItemsAxis": "us-gaap:OperatingSegmentsMember",
        "numeric_value": 178353000000.0,
        "period_type": "duration",
        "period_end": "2025-09-27",
    }
    fact2 = mod._build_dimensional_revenue_fact(aapl_row, "AAPL", "0000320193-25-000079", "2025-10-31")
    assert fact2["dimensions"] == {"StatementBusinessSegments": "AmericasSegmentMember"}
    assert fact2["consolidation"] == "OperatingSegmentsMember"

    # Both-namespace matching (the Apple pre/post-2018 lesson) stays intact
    # for the dim_<axis> per-row columns too: a us-gaap:-namespaced
    # ProductOrServiceAxis column resolves the same as srt:-namespaced.
    pre2018_row = {
        "concept": "us-gaap:SalesRevenueNet",
        "dim_us-gaap_ProductOrServiceAxis": "aapl:IPhoneMember",
        "numeric_value": 1000.0,
        "period_type": "duration",
        "period_end": "2017-09-30",
    }
    fact3 = mod._build_dimensional_revenue_fact(pre2018_row, "AAPL", "acc", "filed")
    assert fact3["dimensions"] == {"ProductOrService": "IPhoneMember"}


def test_build_fact_includes_subsegments_axis():
    """`SubsegmentsAxis` (srt namespace) was added to
    `_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES` but had no offline test exercising
    it (whole-branch review 🟡, feat-operational-kpi-xbrl-pilot) — a mocked
    row carrying `dim_srt_SubsegmentsAxis` alongside another real breakdown
    axis (`dim_us-gaap_StatementBusinessSegmentsAxis`) must fold BOTH into
    `dimensions`, proving SubsegmentsAxis is recognized as a real breakdown
    axis (not dropped, and not mistaken for the `ConsolidationItemsAxis`
    qualifier). Mirrors test_build_fact_full_signature's mock shape."""
    mod = _load_helpers()

    row = {
        "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "dim_us-gaap_StatementBusinessSegmentsAxis": "jnj:ConsumerHealthSegmentMember",
        "dim_srt_SubsegmentsAxis": "jnj:SomeSubsegmentMember",
        "numeric_value": 500000000.0,
        "period_type": "duration",
        "period_end": "2025-12-31",
    }
    fact = mod._build_dimensional_revenue_fact(row, "JNJ", "0000200406-26-000012", "2026-02-01")
    assert fact["dimensions"] == {
        "StatementBusinessSegments": "ConsumerHealthSegmentMember",
        "Subsegments": "SomeSubsegmentMember",
    }, "SubsegmentsAxis must be folded into dimensions alongside the other real breakdown axis"
    assert fact["consolidation"] is None


# ---------------------------------------------------------------------------
# extract_dimensional_revenue — Task 6 exact-form-match filing selection
# (offline guard; code-quality-reviewer 🟡 on Task 6: the amendment-skip
# filter — exact `f.form == form` + max-by-filing_date, rejecting a 10-K/A —
# was asserted ONLY by the network-marked live test, so a regression to
# `.latest()` (loose/prefix form match, single most-recent filing) would
# leave the offline suite green)
# ---------------------------------------------------------------------------

def _make_dimensional_filing(*, accession, form, filing_date, revenue_value):
    """Build a fake edgartools Filing whose `.xbrl()` yields exactly one
    dimensional-revenue fact row, so a wrong filing pick is visible in the
    returned fact-pack's accession/value."""
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    xb.facts.to_dataframe.return_value.to_dict.return_value = [
        {
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "aapl:IPhoneMember",
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "numeric_value": revenue_value,
            "period_type": "duration",
            "period_end": filing_date.isoformat(),
            "period_instant": None,
        },
    ]
    filing = SimpleNamespace(accession_no=accession, filing_date=filing_date, form=form)
    filing.xbrl = lambda: xb
    return filing


def test_extract_dimensional_revenue_skips_amendment_offline(sec_client):
    """`extract_dimensional_revenue` must select the exact-form "10-K"
    filing, never a "10-K/A" amendment — even when the amendment's
    `filing_date` is MORE RECENT than the real 10-K's. A regression to
    `.latest()` (a loose/prefix form match that just takes the single
    most-recent filing) would pick the amendment here, since it postdates
    the 10-K and carries its own usable dimensional-revenue row. This is the
    offline counterpart to test_sec_edgar_dimensional_live.py's network-only
    anchor for the same invariant."""
    amendment = _make_dimensional_filing(
        accession="0000320193-24-000200",
        form="10-K/A",
        filing_date=datetime.date(2024, 11, 15),  # more recent than the 10-K
        revenue_value=999.0,
    )
    real_10k = _make_dimensional_filing(
        accession="0000320193-24-000123",
        form="10-K",
        filing_date=datetime.date(2024, 11, 1),  # earlier, but the exact form
        revenue_value=100.0,
    )

    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    # List order must not matter — the exact-form filter + max-by-date must
    # find the 10-K regardless of position.
    company.get_filings.return_value = [amendment, real_10k]
    sec_client.edgar_stub.Company.return_value = company

    result = sec_client.extract_dimensional_revenue("AAPL")

    assert "error" not in result
    assert result["facts"], "expected at least one dimensional revenue fact"
    accessions = {fact["accession"] for fact in result["facts"]}
    assert accessions == {"0000320193-24-000123"}, (
        "must select the exact-form 10-K (0000320193-24-000123), not the "
        f"more-recent 10-K/A amendment (0000320193-24-000200) — got {accessions}"
    )
    values = {fact["value"] for fact in result["facts"]}
    assert 999.0 not in values, "the amendment's revenue value leaked into the fact-pack"


# ---------------------------------------------------------------------------
# Task 1 — range-bounded consecutive multi-filing fetch (since_year/until_year)
# (docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md). Default (both
# None) preserves latest-only; since_year opts into a consecutive multi-filing
# concatenation. Driven by the MACHINE-CAPTURED multi-filing fixture
# (fixtures/xbrl_multifiling_aapl.json — 3 historical AAPL 10-Ks, distinct
# accessions, verified live 2026-07-15), NOT hand-typed facts.
# ---------------------------------------------------------------------------

def _filing_from_fixture(record):
    """Build a fake edgartools Filing from one captured fixture filing record.
    Carries per-filing selection metadata (`form`, `filing_date`,
    `period_of_report`) plus a `.xbrl()` yielding the captured raw fact rows —
    so the range selection can key on filings-list metadata WITHOUT fetching
    every `.xbrl()` first (the plan's kickoff decision)."""
    xb = mock.MagicMock(name=f"xbrl-{record['accession']}")
    xb.facts.to_dataframe.return_value.to_dict.return_value = list(record["raw_facts"])
    year, month, day = (int(part) for part in record["filing_date"].split("-"))
    filing = SimpleNamespace(
        accession_no=record["accession"],
        filing_date=datetime.date(year, month, day),
        form=record["form"],
        period_of_report=record["period_of_report"],
    )
    filing.xbrl = lambda bound=xb: bound
    return filing


def _multifiling_company(sec_client):
    """Wire the captured multi-filing fixture behind a mocked edgartools
    Company whose `get_filings` returns the fake Filings. Returns the parsed
    fixture for the test to assert against."""
    fixture = json.loads((FIXTURES / "xbrl_multifiling_aapl.json").read_text())
    filings = [_filing_from_fixture(r) for r in fixture["filings"]]
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value = filings
    sec_client.edgar_stub.Company.return_value = company
    return fixture


def test_extract_dimensional_revenue_since_year_spans_multiple_filings(sec_client):
    """`extract_dimensional_revenue` with `since_year` set concatenates facts
    from EVERY in-range exact-form 10-K (>1 distinct accession), while the
    default call (no `since_year`) preserves today's latest-only behavior
    (facts from exactly one — the latest — accession). This un-collapses the
    single-filing seam without regressing the default path."""
    fixture = _multifiling_company(sec_client)
    all_accessions = {r["accession"] for r in fixture["filings"]}
    latest_accession = max(
        fixture["filings"], key=lambda r: r["filing_date"]
    )["accession"]

    # Default (both bounds None) → latest filing only: facts from exactly one
    # accession, unchanged from the pre-range behavior.
    default_pack = sec_client.extract_dimensional_revenue("AAPL")
    assert "error" not in default_pack, default_pack
    default_accessions = {f["accession"] for f in default_pack["facts"]}
    assert default_accessions == {latest_accession}, (
        "default (no since_year) must return facts from exactly the latest "
        f"filing ({latest_accession}); got {default_accessions}"
    )

    # since_year set → consecutive multi-filing fetch: facts drawn from >1
    # distinct accession, one per in-range exact-form 10-K.
    multi_pack = sec_client.extract_dimensional_revenue("AAPL", since_year=2019)
    assert "error" not in multi_pack, multi_pack
    multi_accessions = {f["accession"] for f in multi_pack["facts"]}
    assert len(multi_accessions) > 1, (
        "since_year must span multiple filings; got a single accession "
        f"{multi_accessions}"
    )
    assert multi_accessions == all_accessions, (
        "every in-range filing's facts must be concatenated (consecutive, "
        f"not strided); expected {all_accessions}, got {multi_accessions}"
    )
    # Concatenation is additive — the multi-filing pack carries strictly more
    # facts than the single latest filing.
    assert len(multi_pack["facts"]) > len(default_pack["facts"])


def test_extract_dimensional_revenue_until_year_without_since_year_raises(sec_client):
    """`until_year` set WITHOUT `since_year` is unsupported and must fail loud:
    with no lower bound the call would silently fall to latest-only and could
    return a filing NEWER than the stated upper bound (silent-wrong is the
    enemy). The Decision Log defines only both-None (latest-only) and
    `since_year`-alone (`[since_year, latest]`) — an upper-bound-only call is
    rejected with a ValueError, not silently reinterpreted. The raise must
    precede any network I/O, so no edgartools mock is needed."""
    with pytest.raises(ValueError, match="until_year requires since_year"):
        sec_client.extract_dimensional_revenue("AAPL", until_year=2021)


def test_extract_dimensional_revenue_until_year_excludes_later_filing(sec_client):
    """The INCLUSIVE upper bound is honored: `since_year=2019, until_year=2021`
    selects the 2019 + 2021 filings and EXCLUDES the 2023 one (whose fiscal
    period year 2023 > until_year). Proves the `year <= until_year` branch of
    the range predicate, using the machine-captured 2019/2021/2023 fixture."""
    fixture = _multifiling_company(sec_client)
    by_year = {r["period_of_report"][:4]: r["accession"] for r in fixture["filings"]}

    pack = sec_client.extract_dimensional_revenue("AAPL", since_year=2019, until_year=2021)
    assert "error" not in pack, pack
    accessions = {f["accession"] for f in pack["facts"]}
    assert accessions == {by_year["2019"], by_year["2021"]}, (
        "inclusive upper bound: [2019, 2021] must include the 2019 + 2021 "
        f"filings and exclude the 2023 one ({by_year['2023']}); got {accessions}"
    )
    assert by_year["2023"] not in accessions, (
        f"the 2023 filing (fiscal year > until_year=2021) leaked in: {accessions}"
    )


# ---------------------------------------------------------------------------
# Task 2 — coverage report + availability clamp (DQC honesty)
# (docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md). When the
# requested range exceeds the real availability floor/ceiling (the fixture's
# earliest/latest exact-form filing is 2019/2023), the pack still returns
# whatever facts DO exist AND reports the clamp — never a silent truncation.
# ---------------------------------------------------------------------------

def test_extract_dimensional_revenue_reports_coverage_clamp(sec_client):
    """`since_year` earlier than the earliest available filing (2019, per the
    fixture) is clamped: the facts stop at the real floor (no filing older
    than 2019 exists to fetch) and `coverage.clamp_reason` records why. An
    in-availability request over the SAME selected filings records no clamp
    — isolating clamp-reason logic from the returned-facts range, which is
    identical in both calls."""
    fixture = _multifiling_company(sec_client)

    # since_year=2010 precedes the earliest available filing (2019) ->
    # clamped. until_year=2021 is within availability (max is 2023) -> the
    # 2019 + 2021 filings are selected, same as the in-availability call below.
    clamped_pack = sec_client.extract_dimensional_revenue(
        "AAPL", since_year=2010, until_year=2021
    )
    assert "error" not in clamped_pack, clamped_pack
    clamped_coverage = clamped_pack["coverage"]
    assert clamped_coverage["requested"] == {"since": 2010, "until": 2021}
    assert clamped_coverage["actual"] == {"min_year": 2017, "max_year": 2021}, (
        "actual must reflect the real floor the facts stop at (2017, the "
        "earliest comparative year reported inside the selected 2019 filing) "
        f"— got {clamped_coverage['actual']}"
    )
    assert clamped_coverage["clamp_reason"], (
        "since_year=2010 precedes the earliest available filing (2019) and "
        "must record why the facts stop short of the request"
    )
    assert "2010" in clamped_coverage["clamp_reason"]
    assert "2019" in clamped_coverage["clamp_reason"]

    # since_year=2019 is exactly the earliest available filing -> no clamp,
    # even though the returned facts span is identical to the clamped call.
    inrange_pack = sec_client.extract_dimensional_revenue(
        "AAPL", since_year=2019, until_year=2021
    )
    assert "error" not in inrange_pack, inrange_pack
    inrange_coverage = inrange_pack["coverage"]
    assert inrange_coverage["requested"] == {"since": 2019, "until": 2021}
    assert inrange_coverage["actual"] == {"min_year": 2017, "max_year": 2021}
    assert inrange_coverage["clamp_reason"] is None, (
        f"in-availability request must record no clamp; got {inrange_coverage['clamp_reason']!r}"
    )

    # never a silent truncation: the clamped call's facts must be the exact
    # same set as the in-availability call's (both select the 2019 + 2021
    # filings) — the clamp is REPORTED, not hidden by returning fewer facts.
    clamped_accessions = {f["accession"] for f in clamped_pack["facts"]}
    inrange_accessions = {f["accession"] for f in inrange_pack["facts"]}
    assert clamped_accessions == inrange_accessions
