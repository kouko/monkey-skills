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
# Task 2 — revenue-concept allow/deny + $-unit gate (folds a scope-A bug)
# (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md). The shipped
# `_is_revenue_concept` substring test ("Revenue" in local_name) is too
# permissive across sectors — live evidence (docs/loom/references/
# xbrl-verification-universe.md, Filter-bug findings section) reproduced
# dimensioned CostOfRevenue (CAT) being emitted AS revenue, percentage-valued
# `*Revenue*Percentage` concepts (BA/HON) being emitted with a % as if it were
# a dollar value, and deferred-revenue LIABILITY concepts (SBUX) being
# emitted as earned revenue. Fixtures are MACHINE-CAPTURED (never hand-typed)
# — see fixtures/xbrl_concept_filter_cases.json's `_provenance`.
#
# No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-16-
# operational-kpi-quarterly.md) traces work by named plan Tasks, NOT by
# registered loom-spec REQ-ids — so `@req` is omitted per the implementer
# contract.
# ---------------------------------------------------------------------------

def _concept_filter_fixture() -> dict:
    return json.loads((FIXTURES / "xbrl_concept_filter_cases.json").read_text())


def test_is_revenue_concept_allow_list_checked_before_deny_list(monkeypatch):
    """Revision round 1, Finding 3 (spec-reviewer 🟡): all five real entries
    in `_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES` are admitted by the general
    "Revenue"-substring path anyway, so statically the allow-list looks like
    dead weight. Its REAL (defensive) purpose is ORDERING: it is checked
    FIRST, so a future deny substring can never accidentally swallow a
    named-legitimate concept. That property was unpinned — this test pins
    it directly.

    No real allow-list entry today also happens to contain a deny substring
    (verified: none of the 5 names contain "CostOf"/"Percent"/etc.), so this
    monkeypatches ONE SYNTHETIC entry onto the allow-list for the duration
    of this test only — the shipped tuple is never modified. This tests
    `_is_revenue_concept`'s ORDERING LOGIC directly, per the dispatch's
    synthetic-concept allowance, not a claimed real-filing value."""
    mod = _load_helpers()
    synthetic_local_name = "RevenuesWithCostOfSomethingSynthetic"
    assert any(deny in synthetic_local_name for deny in mod._REVENUE_DENY_SUBSTRINGS), (
        "test setup bug: the synthetic name must actually collide with a "
        "deny substring, or this test proves nothing"
    )
    monkeypatch.setattr(
        mod,
        "_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES",
        mod._REVENUE_ALLOW_CONCEPT_LOCAL_NAMES + (synthetic_local_name,),
    )
    assert mod._is_revenue_concept(f"us-gaap:{synthetic_local_name}") is True, (
        "an allow-listed concept must be KEPT even when its local name also "
        "matches a deny substring — the allow-list must be checked BEFORE "
        "the deny-list"
    )


def test_revenue_concept_filter_deny_allow_unit():
    """The three RED scenarios named in the plan/spec, over the machine-
    captured real-filing fixture:
      1. a dimensioned CostOfRevenue fact (CAT) is EXCLUDED — deny-list.
      2. a *RevenuePercentage fact (BA/HON) is REJECTED — via the "Percent"
         DENY SUBSTRING at the concept layer (both local names literally
         contain "Percent"), NOT the $-unit guard. CORRECTED 2026-07-17
         (revision round 1, code-quality-reviewer 🔴 fatal, mutation-proved:
         deleting the `_is_currency_amount_fact` call-site left the suite
         fully green because these two fixtures never reach the guard — the
         concept-level deny already shorts them out first). The $-unit
         guard's own direct coverage is
         `test_is_currency_amount_fact_direct_unit_coverage` /
         `test_is_dimensional_revenue_fact_rejects_noncurrency_unit_synthetic`
         below.
      3. a RevenueNotFromContractWithCustomer fact (XOM) is KEPT — allow-list.
    Exercised at BOTH layers: the pure `_is_revenue_concept` (concept-string
    only) and the full `_is_dimensional_revenue_fact` predicate."""
    mod = _load_helpers()
    fixture = _concept_filter_fixture()

    # 1. CAT dimensioned CostOfRevenue — excluded by the deny-list, at both
    # layers (the concept alone is enough to deny it, regardless of unit).
    cat_fact = fixture["cat_cost_of_revenue_dimensioned"]["raw_fact"]
    assert mod._is_revenue_concept(cat_fact["concept"]) is False, (
        "us-gaap:CostOfRevenue must be denied — a cost is not revenue"
    )
    assert mod._is_dimensional_revenue_fact(cat_fact) is False, (
        "a dimensioned CostOfRevenue fact must never be emitted as revenue "
        "(the CAT reproducer — 20 bogus facts on the shipped substring test)"
    )

    # 2. BA / HON percentage-valued *Revenue*Percentage — denied at the
    # CONCEPT layer by the "Percent" deny substring (both local names
    # literally contain "Percent"); the $-unit guard is never reached for
    # these two fixtures specifically (CORRECTED 2026-07-17 — see this
    # function's docstring). Pinning value=1.0 (=100%) / 0.49 (=49%) here
    # only as readability evidence that these are NOT dollar amounts, not
    # because this assertion exercises the guard on them.
    ba_fact = fixture["ba_revenue_percentage"]["raw_fact"]
    assert ba_fact["numeric_value"] == 1.0
    assert mod._is_dimensional_revenue_fact(ba_fact) is False, (
        "ba:RevenuefromContractwithCustomerexcludingassessedtaxPercentage "
        "must be rejected — denied at the concept layer by the 'Percent' "
        "substring"
    )

    hon_fact = fixture["hon_revenue_percentage"]["raw_fact"]
    assert hon_fact["numeric_value"] == 0.49
    assert mod._is_dimensional_revenue_fact(hon_fact) is False, (
        "hon:RevenueFromContractWithCustomerPercentage must be rejected — "
        "denied at the concept layer by the 'Percent' substring"
    )

    # 3. XOM RevenueNotFromContractWithCustomer — a legitimate energy-sector
    # non-RFCC concept, currency-denominated. Must be KEPT at both layers.
    xom_fact = fixture["xom_revenue_not_from_contract"]["raw_fact"]
    assert mod._is_revenue_concept(xom_fact["concept"]) is True, (
        "RevenueNotFromContractWithCustomer is legitimate operating revenue "
        "(energy/utilities) and must stay allowed"
    )
    assert mod._is_dimensional_revenue_fact(xom_fact) is True, (
        "the XOM dimensioned RevenueNotFromContractWithCustomer fact is a "
        "real, currency-denominated revenue fact and must be KEPT"
    )
    assert xom_fact["numeric_value"] == 26295000000.0  # exemplar value, pinned exact


def test_is_currency_amount_fact_direct_unit_coverage():
    """Revision round 1, Finding 2 (code-quality-reviewer 🔴 fatal,
    mutation-proved): deleting the `_is_currency_amount_fact` call-site in
    `_is_dimensional_revenue_fact` left the full suite green (688 passed,
    identical) because BA/HON's fixtures both contain "Percent" — a deny
    substring — so `_is_revenue_concept` already returns False before the
    guard is ever reached; no test exercised the guard itself.

    Route 2 (per the dispatch): a live search across BA/HON/IBM/ADI/AMAT/
    NOW/WDAY/SNOW/CAT/WFC/SBUX/PFE/MRK/SO/XOM/PLD/O/AAPL/MSFT/NFLX
    (2026-07-17, edgartools 5.42.0, latest 10-Q/10-K each) for a REAL
    numeric `*Revenue*`-named concept without "Percent" in the name and a
    non-currency unit found NONE — every non-currency Revenue-named fact in
    that sweep was a TextBlock/Policy/enum/duration-string disclosure
    concept with no numeric value, never a live case that would reach the
    guard through the deny-list today. So this is a DIRECT unit test of the
    guard's own logic (no real-filing fixture claims a value here)."""
    mod = _load_helpers()
    assert mod._is_currency_amount_fact({"currency": "USD"}) is True
    assert mod._is_currency_amount_fact({"currency": "usd"}) is True
    # BA/HON real shape: unit_ref="number", currency=None/NaN.
    assert mod._is_currency_amount_fact({"unit_ref": "number", "currency": None}) is False
    assert mod._is_currency_amount_fact({"unit_ref": "number"}) is False  # missing-unit case
    assert mod._is_currency_amount_fact({}) is False
    assert mod._is_currency_amount_fact({"currency": ""}) is False


def test_is_dimensional_revenue_fact_rejects_noncurrency_unit_synthetic():
    """Integration-level companion to the direct unit test above: proves the
    $-unit guard is actually WIRED INTO `_is_dimensional_revenue_fact`, not
    just correct in isolation. This is the test that fails if the guard's
    CALL SITE (not just its body) is deleted — the mutation the reviewer
    actually ran.

    SYNTHETIC fact — deliberately NOT a real-filing fixture (Route 2,
    Finding 2: the real-filing search above found no qualifying real case).
    Mirrors Finding 3's sanctioned synthetic-concept allowance: this tests
    `_is_dimensional_revenue_fact`'s OWN LOGIC directly, not a claimed real
    filing value. Every other gate is satisfied (dimensioned, duration,
    allow-listed concept, numeric value) so the currency guard is the ONLY
    thing standing between this fact and being wrongly emitted."""
    mod = _load_helpers()
    synthetic_fact = {
        "concept": "us-gaap:Revenues",  # on the allow-list; unambiguously "real revenue"
        "is_dimensioned": True,
        "dim_us-gaap_ProductOrServiceAxis": "test:SyntheticMember",
        "numeric_value": 42.0,
        "unit_ref": "shares",  # NOT a currency unit
        "currency": None,
        "period_type": "duration",
    }
    assert mod._is_dimensional_revenue_fact(synthetic_fact) is False, (
        "a dimensioned, duration, allow-listed revenue concept with a "
        "non-currency unit (shares, currency=None) must still be rejected "
        "by the $-unit guard wired into _is_dimensional_revenue_fact"
    )
    # Sanity: flip the unit to currency and confirm it WOULD be kept —
    # proves the rejection above is caused by the unit, not some other gate.
    currency_fact = dict(synthetic_fact, unit_ref="usd", currency="USD")
    assert mod._is_dimensional_revenue_fact(currency_fact) is True, (
        "the same fact with a currency unit must be kept — isolates the "
        "guard as the cause of the non-currency rejection above"
    )


def test_revenue_concept_filter_deny_list_additional_cases():
    """The additional deny cases named in the plan beyond the 3 RED
    scenarios: OtherCostOfOperatingRevenue (the "Operating" infix that
    defeats a literal "CostOfRevenue" substring check — WFC), *ChangePercent
    ratio concepts (AMAT), RemainingPerformanceObligation (RPO/backlog — BA),
    deferred-revenue liabilities (SBUX, at the concept layer independent of
    the instant/duration gate), and non-operating CollaborativeArrangement
    revenue (PFE). Every concept string here is REAL — live-verified
    2026-07-17 against each filer's latest 10-Q (see inline accessions),
    never a fabricated/pattern-matched name."""
    mod = _load_helpers()
    fixture = _concept_filter_fixture()

    denied_real_concepts = [
        # WFC 10-Q 0000072971-26-000217 (2026-04-29): the "Operating" infix
        # defeats a literal "CostOfRevenue" substring check.
        "us-gaap:OtherCostOfOperatingRevenue",
        # AMAT 10-Q 0001628280-26-037227 (2026-05-21): *ChangePercent-shaped
        # ratio concept.
        "amat:ChangeInRevenuePercentage",
        # BA 10-Q 0001628280-26-026458 (2026-04-22): RPO/backlog, not
        # recognized revenue.
        "us-gaap:RevenueRemainingPerformanceObligation",
        # PFE 10-Q 0000078003-26-000054 (2026-05-05): non-operating
        # collaborative-arrangement revenue.
        "us-gaap:RevenueFromCollaborativeArrangementExcludingRevenueFromContractWithCustomer",
    ]
    for concept in denied_real_concepts:
        assert mod._is_revenue_concept(concept) is False, (
            f"{concept} must be denied (not operating revenue)"
        )

    # SBUX dimensioned DeferredRevenueCurrent (deny at the concept layer,
    # independent of the instant/duration gate that would also exclude it).
    sbux_fact = fixture["sbux_deferred_revenue_dimensioned"]["raw_fact"]
    assert mod._is_revenue_concept(sbux_fact["concept"]) is False, (
        "DeferredRevenueCurrent is a balance-sheet liability, not earned "
        "revenue — must be denied even before the instant-context gate"
    )


def test_revenue_concept_filter_denies_reit_class6_artifacts():
    """Revision round 1, Finding 1 (code-quality-reviewer 🔴 fatal): class 6
    of the six false-positive classes named in
    docs/loom/references/xbrl-verification-universe.md:198-213 — 'REIT
    artifacts — PLD ladder-schedule, O pro-forma-M&A revenue' — had no deny
    coverage. Reviewer live-reproduced both as ADMITTED by the landed
    predicate. Real concepts, machine-captured 2026-07-17:
      - O's `us-gaap:BusinessAcquisitionsProFormaRevenue` — HYPOTHETICAL
        revenue as if a business acquisition had closed at period start;
        admitting it double-counts against actual revenue for the period.
      - PLD's `pld:NetIncreaseDecreaseToRentalRevenueNextTwelveMonths` — a
        forward-looking lease-ladder roll-forward figure, not revenue
        recognized in the period.
    Both must now be DENIED at the concept layer."""
    mod = _load_helpers()
    fixture = _concept_filter_fixture()

    o_fact = fixture["o_pro_forma_revenue_dimensioned"]["raw_fact"]
    assert mod._is_revenue_concept(o_fact["concept"]) is False, (
        "BusinessAcquisitionsProFormaRevenue is hypothetical pro-forma "
        "M&A revenue, not actual recognized revenue — must be denied"
    )

    pld_fact = fixture["pld_rental_revenue_ladder"]["raw_fact"]
    assert mod._is_revenue_concept(pld_fact["concept"]) is False, (
        "NetIncreaseDecreaseToRentalRevenue* is a lease-ladder schedule "
        "roll-forward, not recognized revenue — must be denied"
    )

    # PLD's real (non-ladder) revenue concept must stay allowed — the new
    # deny substring is deliberately the LONGER "NetIncreaseDecreaseTo
    # RentalRevenue" fragment, not the bare "RentalRevenue" substring, so it
    # cannot over-deny the actual revenue line.
    assert mod._is_revenue_concept("pld:RentalRevenue") is True, (
        "pld:RentalRevenue (the real revenue concept, not the ladder "
        "schedule) must stay allowed — the class-6 deny substring must not "
        "over-deny it"
    )


def test_revenue_concept_filter_unbilled_revenue_not_double_denied():
    """Revision round 1, Finding 1 judgment call on `so:UnbilledRevenuesCurrent`
    (judged on merit per the dispatch, NOT added to the deny-list): a
    contract-asset receivable (revenue earned but not yet billed), real
    filing shape is instant-context and non-dimensioned (machine-captured
    2026-07-17, SO 10-Q). `_is_revenue_concept` legitimately stays True
    (no deny substring matches "UnbilledRevenuesCurrent" — it is not
    fabricated/hypothetical/liability-shaped like the other classes); the
    existing is_dimensioned + period_type=='duration' gates in
    `_is_dimensional_revenue_fact` already exclude it, so a concept-level
    deny would be redundant. This test pins that existing-gate protection so
    a future accidental addition of an "Unbilled"/"Current" deny substring
    is caught as an unnecessary over-denial regression."""
    mod = _load_helpers()
    fixture = _concept_filter_fixture()
    so_fact = fixture["so_unbilled_revenue_current"]["raw_fact"]

    assert mod._is_revenue_concept(so_fact["concept"]) is True, (
        "so:UnbilledRevenuesCurrent is not one of the six false-positive "
        "classes — it must NOT be concept-denied"
    )
    assert mod._is_dimensional_revenue_fact(so_fact) is False, (
        "so:UnbilledRevenuesCurrent's real filing shape is instant-context "
        "and non-dimensioned — already excluded by the existing "
        "is_dimensioned/period_type gates, without needing a concept-level "
        "deny"
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
            "unit_ref": "usd",
            "currency": "USD",
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
        "period_start": "2025-01-01",
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
        "period_start": "2024-09-29",
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
        "period_start": "2016-09-25",
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
        "period_start": "2025-01-01",
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
            "unit_ref": "usd",
            "currency": "USD",
            "period_type": "duration",
            "period_start": (filing_date - datetime.timedelta(days=365)).isoformat(),
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


# ---------------------------------------------------------------------------
# Task 1 — duration_months per fact (docs/loom/plans/2026-07-16-operational-
# kpi-quarterly.md, "Period duration is emitted per fact"). Driven by the
# MACHINE-CAPTURED xbrl_quarterly_msft.json fixture: a real MSFT 10-Q
# (accession 0001193125-26-191507, period_of_report 2026-03-31) tags BOTH a
# 3-month quarter AND a 9-month YTD cumulative for the SAME concept +
# dimensions + period_end — the dual-duration collision this task exists to
# de-conflate. The 12-month case is a real MSFT 10-K (accession
# 0000950170-25-100235) for the SAME segment axis.
# ---------------------------------------------------------------------------

def test_extract_emits_duration_months():
    """`_build_dimensional_revenue_fact` emits `duration_months` derived from
    period_start->period_end for a duration-context fact — 3 for a 3-month
    quarter, 9 for a 9-month YTD, 12 for an annual fact, all over the
    machine-captured MSFT fixture (real accessions, real integers, never
    hand-typed). `_is_dimensional_revenue_fact` excludes an instant-context
    fact from the duration-flow output entirely (revenue is a duration-flow
    concept). A missing/malformed period_start on a duration-context fact
    raises loud instead of guessing — never a fabricated/defaulted duration
    (docs/loom/memory/fail-closed-default-must-be-enforced-not-emergent.md)."""
    mod = _load_helpers()
    fixture = json.loads((FIXTURES / "xbrl_quarterly_msft.json").read_text())
    raw = fixture["raw_facts"]
    q_accession = fixture["quarterly_filing"]["accession"]
    q_filed = fixture["quarterly_filing"]["filing_date"]

    # 3-month quarter fact.
    q3_fact = mod._build_dimensional_revenue_fact(
        raw["three_month"], "MSFT", q_accession, q_filed,
    )
    assert q3_fact["duration_months"] == 3
    assert q3_fact["value"] == 35013000000.0  # exemplar value, pinned exact

    # 9-month YTD fact — SAME period_end as the 3-month fact above (the
    # dual-duration collision duration_months exists to de-conflate).
    ytd9_fact = mod._build_dimensional_revenue_fact(
        raw["nine_month_ytd"], "MSFT", q_accession, q_filed,
    )
    assert ytd9_fact["duration_months"] == 9
    assert ytd9_fact["period_end"] == q3_fact["period_end"] == "2026-03-31", (
        "the 3-month and 9-month facts must share the SAME period_end — "
        "exactly the collision duration_months exists to de-conflate"
    )
    assert ytd9_fact["value"] == 102149000000.0

    # 12-month annual fact (real MSFT FY2025 10-K, same segment axis).
    annual_fact = mod._build_dimensional_revenue_fact(
        raw["annual"], "MSFT",
        fixture["annual_filing"]["accession"], fixture["annual_filing"]["filing_date"],
    )
    assert annual_fact["duration_months"] == 12
    assert annual_fact["value"] == 120810000000.0

    # An instant-context fact is EXCLUDED from the duration-flow output —
    # tested at the `_is_dimensional_revenue_fact` predicate that filters
    # extract_dimensional_revenue's returned facts list. Same shape as a
    # real dimensioned revenue-concept row, only period_type flipped to
    # "instant" (revenue is never actually tagged instant in real filings —
    # this proves the filter, not a captured shape).
    instant_row = dict(raw["three_month"])
    instant_row["period_type"] = "instant"
    assert mod._is_dimensional_revenue_fact(instant_row) is False, (
        "an instant-context fact must be excluded from the duration-flow "
        "output, never assigned a duration_months"
    )

    # A missing period_start on a duration-context fact raises loud — never
    # a silently defaulted/fabricated duration.
    missing_start_row = dict(raw["three_month"])
    missing_start_row["period_start"] = None
    with pytest.raises(ValueError, match="period_start"):
        mod._build_dimensional_revenue_fact(missing_start_row, "MSFT", "acc", "filed")

    # A malformed (non-ISO) period_start also raises loud.
    malformed_start_row = dict(raw["three_month"])
    malformed_start_row["period_start"] = "not-a-date"
    with pytest.raises(ValueError, match="period_start"):
        mod._build_dimensional_revenue_fact(malformed_start_row, "MSFT", "acc", "filed")


# ---------------------------------------------------------------------------
# code-quality-reviewer 🟡 (Task 1 follow-up) — `_duration_months`'s day-span
# -> month-integer mapping pinned across the realistic bands the review
# brief itself named as risk (52/53-week filers, 13-week vs 14-week
# quarters, 371-day FY): test_extract_emits_duration_months above only
# exercises MSFT's ordinary calendar-aligned 3/9/12-month spans, leaving the
# heuristic with zero regression protection on exactly the axis a future
# `_AVG_DAYS_PER_MONTH`/rounding change could silently drift. Exact integer
# assertions (never a range) — see RED-evidence perturbation in the SDD
# dispatch report.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "period_start,period_end,expected_months",
    [
        # ordinary quarter, 89/90/92 days.
        ("2026-01-01", "2026-03-31", 3),
        ("2026-01-01", "2026-04-01", 3),
        ("2026-01-01", "2026-04-03", 3),
        # 13-week quarter = 91 days.
        ("2026-01-01", "2026-04-02", 3),
        # 14-week quarter (52/53-week filer's extra week) = 98 days.
        ("2026-01-01", "2026-04-09", 3),
        # H1 half-year, 180/182/184 days.
        ("2026-01-01", "2026-06-30", 6),
        ("2026-01-01", "2026-07-02", 6),
        ("2026-01-01", "2026-07-04", 6),
        # three-quarter YTD, 271/273/275 days.
        ("2026-01-01", "2026-09-29", 9),
        ("2026-01-01", "2026-10-01", 9),
        ("2026-01-01", "2026-10-03", 9),
        # ordinary FY, 364/365 days.
        ("2026-01-01", "2026-12-31", 12),
        ("2026-01-01", "2027-01-01", 12),
        # 53-week FY = 371 days.
        ("2026-01-01", "2027-01-07", 12),
    ],
)
def test_duration_months_pins_realistic_span_bands(period_start, period_end, expected_months):
    mod = _load_helpers()
    fact = {"period_start": period_start}
    assert mod._duration_months(fact, "TEST", period_end) == expected_months


# ---------------------------------------------------------------------------
# Task 3 — fiscal calendar read per-filing from dei tags, never cached per
# ticker (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md). Real NVDA
# dei values, MACHINE-CAPTURED 2026-07-17 (edgartools 5.42.0, live
# `filing.xbrl().facts.to_dataframe()` -- both are real filed 10-Ks, not
# hand-typed):
#   accession 0001045810-21-000010 (period_of_report 2021-01-31)
#     -> dei:DocumentFiscalPeriodFocus="FY", dei:CurrentFiscalYearEndDate="--01-31"
#   accession 0001045810-26-000021 (period_of_report 2026-01-25)
#     -> dei:DocumentFiscalPeriodFocus="FY", dei:CurrentFiscalYearEndDate="--01-25"
# This drift (NVDA is a 52/53-week filer, docs/loom/references/
# xbrl-verification-universe.md:49) is the load-bearing evidence the whole
# task exists to protect: a per-ticker cache would apply ONE filing's
# calendar to the other's facts and silently mislabel its quarters.
# ---------------------------------------------------------------------------

def _make_dei_filing(*, accession, form, filing_date, period_of_report,
                      fiscal_period_focus, fiscal_year_end):
    """Fake edgartools Filing whose `.xbrl()` yields one dimensional-revenue
    row PLUS the filing's own dei cover-page rows -- same shape as a real
    filing's facts dataframe (dei rows and us-gaap rows share ONE records
    list; live-verified in the module docstring above `extract_dimensional_revenue`,
    and directly in this task's live capture)."""
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    xb.facts.to_dataframe.return_value.to_dict.return_value = [
        {
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "nvda:ComputeMember",
            "concept": "us-gaap:Revenues",
            "numeric_value": 1000.0,
            "unit_ref": "usd",
            "currency": "USD",
            "period_type": "duration",
            "period_start": (filing_date - datetime.timedelta(days=365)).isoformat(),
            "period_end": filing_date.isoformat(),
            "period_instant": None,
        },
        {"concept": "dei:DocumentFiscalPeriodFocus", "value": fiscal_period_focus},
        {"concept": "dei:CurrentFiscalYearEndDate", "value": fiscal_year_end},
    ]
    filing = SimpleNamespace(
        accession_no=accession, filing_date=filing_date, form=form,
        period_of_report=period_of_report,
    )
    filing.xbrl = lambda bound=xb: bound
    return filing


def test_extract_emits_dei_fiscal_calendar(sec_client):
    """Two filings from the SAME 52/53-week filer (NVDA) with DIFFERING real
    dei:CurrentFiscalYearEndDate (--01-31 vs --01-25) must each keep their OWN
    value in the pack's `fiscal_calendars` -- never one cached/shared value
    applied uniformly across both. This is the heart of Task 3: it must
    genuinely fail if a per-ticker cache were introduced (see the SDD
    dispatch report for the RED-under-cache proof)."""
    filing_2021 = _make_dei_filing(
        accession="0001045810-21-000010", form="10-K",
        filing_date=datetime.date(2021, 2, 26), period_of_report="2021-01-31",
        fiscal_period_focus="FY", fiscal_year_end="--01-31",
    )
    filing_2026 = _make_dei_filing(
        accession="0001045810-26-000021", form="10-K",
        filing_date=datetime.date(2026, 2, 25), period_of_report="2026-01-25",
        fiscal_period_focus="FY", fiscal_year_end="--01-25",
    )

    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.return_value = [filing_2021, filing_2026]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("NVDA", since_year=2021, until_year=2026)

    assert "error" not in pack, pack
    calendars = pack["fiscal_calendars"]
    assert calendars["0001045810-21-000010"] == {
        "fiscal_period_focus": "FY", "fiscal_year_end": "--01-31",
    }, calendars
    assert calendars["0001045810-26-000021"] == {
        "fiscal_period_focus": "FY", "fiscal_year_end": "--01-25",
    }, calendars
    assert (
        calendars["0001045810-21-000010"]["fiscal_year_end"]
        != calendars["0001045810-26-000021"]["fiscal_year_end"]
    ), (
        "the two filings' fiscal-year-end must differ -- proves each filing's "
        "OWN dei value is retained, not one cached value applied to both"
    )


def test_extract_dei_fiscal_calendar_absent_tag_is_none_not_fabricated(sec_client):
    """A filing whose facts_records carry no dei rows at all (a test-double
    gap -- every real 10-K/10-Q carries both per SEC dei taxonomy
    requirements) must record `None`, never a guessed/fabricated value. Uses
    the existing amendment-skip fixture builder (`_make_dimensional_filing`),
    which carries no dei rows, to prove the absence path doesn't raise or
    invent a value."""
    filing = _make_dimensional_filing(
        accession="0000320193-24-000123", form="10-K",
        filing_date=datetime.date(2024, 11, 1), revenue_value=100.0,
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("AAPL")

    assert "error" not in pack, pack
    assert pack["fiscal_calendars"]["0000320193-24-000123"] == {
        "fiscal_period_focus": None, "fiscal_year_end": None,
    }
