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


def test_unit_guard_backstop_synthetic(sec_client):
    """T21 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md) — the
    spec's own backstop scenario ('the $-unit guard backstops a non-currency
    fact that passes the name gates'): a SYNTHETIC `*Revenue*` concept —
    no real filer case exists in the verification universe today, per the
    spec's note — that clears BOTH the ALLOW/DENY name gates (contains
    "Revenue", matches none of `_REVENUE_DENY_SUBSTRINGS` — no "Percent",
    "CostOf", etc.) but carries a ratio/pure XBRL unit, not a currency
    amount.

    Unlike `test_is_dimensional_revenue_fact_rejects_noncurrency_unit_
    synthetic` above (which calls the pure `_is_dimensional_revenue_fact`
    predicate directly), this drives the FULL `extract_dimensional_revenue`
    path end-to-end over an in-test staged filing (the `_make_dimensional_
    filing` convention, T6/T13-era) carrying TWO dimensioned *Revenue*-named
    rows on the SAME accession: a legitimate currency-unit control fact and
    the synthetic ratio-unit backstop target — proving the guard is wired
    into the real extraction output, not just correct in isolation."""
    mod = sec_client
    synthetic_concept = "xyz:SyntheticServiceRevenueYield"

    # Fixture-sanity / RED-premise check: the synthetic concept must clear
    # the name gate ON ITS OWN MERITS — otherwise this test would not
    # isolate the $-unit guard as the thing doing the rejecting below.
    assert mod._is_revenue_concept(synthetic_concept) is True, (
        "fixture sanity: the synthetic concept must pass the ALLOW/DENY "
        "name gate by itself (no deny substring hits) — if this fails, "
        "the concept string needs picking again, not the unit guard"
    )

    accession = "0000320193-24-000555"
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    rows = [
        {  # control: a legitimate currency-unit revenue fact, proving
            # extraction actually runs and isolating the rejection below.
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "aapl:IPhoneMember",
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "numeric_value": 50000000000.0,
            "unit_ref": "usd",
            "currency": "USD",
            "period_type": "duration",
            "period_start": "2023-10-01",
            "period_end": "2024-09-28",
            "period_instant": None,
        },
        {  # SYNTHETIC backstop target: clears both name gates, non-currency
            # unit (ratio/"pure", currency=None) — must be rejected by the
            # $-unit guard alone.
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "aapl:IPhoneMember",
            "concept": synthetic_concept,
            "numeric_value": 0.85,
            "unit_ref": "pure",
            "currency": None,
            "period_type": "duration",
            "period_start": "2023-10-01",
            "period_end": "2024-09-28",
            "period_instant": None,
        },
        {"concept": "dei:DocumentFiscalPeriodFocus", "value": "FY"},
        {"concept": "dei:CurrentFiscalYearEndDate", "value": "--09-28"},
        {"concept": "dei:DocumentFiscalYearFocus", "value": "2024"},
    ]
    xb.facts.to_dataframe.return_value.to_dict.return_value = rows
    filing = SimpleNamespace(
        accession_no=accession, filing_date=datetime.date(2024, 11, 1), form="10-K",
    )
    filing.xbrl = lambda: xb

    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value = [filing]
    mod.edgar_stub.Company.return_value = company

    result = mod.extract_dimensional_revenue("AAPL")

    assert "error" not in result
    concepts = {fact["concept"] for fact in result["facts"]}
    assert synthetic_concept not in concepts, (
        "the synthetic ratio-unit *Revenue* fact cleared the name gates but "
        "must still be rejected by the $-unit guard — never emitted"
    )
    values = {fact["value"] for fact in result["facts"]}
    assert 0.85 not in values, (
        "the synthetic non-currency 'value' must never reach the emitted "
        "fact-pack, even disguised as a plausible number"
    )
    # Control: the legitimate fact IS emitted — isolates the synthetic row's
    # rejection above as caused by the $-unit guard, not a broken fixture.
    assert 50000000000.0 in values, (
        "the legitimate control fact must be emitted — proves extraction "
        "ran and the backstop rejection above is real"
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
    # Task 13: the builder derives parallel period labels against the
    # filing's dei calendar, so every direct call supplies one (real-shaped
    # `--MM-DD` / focus values for each filer's known fiscal year end).
    fact = mod._build_dimensional_revenue_fact(
        nflx_row, "NFLX", "0001065280-26-000034", "2026-01-23",
        {"fiscal_period_focus": "FY", "fiscal_year_end": "--12-31",
         "fiscal_year_focus": "2025"},
    )
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
    fact2 = mod._build_dimensional_revenue_fact(
        aapl_row, "AAPL", "0000320193-25-000079", "2025-10-31",
        {"fiscal_period_focus": "FY", "fiscal_year_end": "--09-27",
         "fiscal_year_focus": "2025"},
    )
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
    fact3 = mod._build_dimensional_revenue_fact(
        pre2018_row, "AAPL", "acc", "filed",
        {"fiscal_period_focus": "FY", "fiscal_year_end": "--09-30",
         "fiscal_year_focus": "2017"},
    )
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
    fact = mod._build_dimensional_revenue_fact(
        row, "JNJ", "0000200406-26-000012", "2026-02-01",
        {"fiscal_period_focus": "FY", "fiscal_year_end": "--12-31",
         "fiscal_year_focus": "2025"},
    )
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

def _make_dimensional_filing(*, accession, form, filing_date, revenue_value,
                              include_dei=True):
    """Build a fake edgartools Filing whose `.xbrl()` yields exactly one
    dimensional-revenue fact row, so a wrong filing pick is visible in the
    returned fact-pack's accession/value. Task 13: a selected filing's
    facts are fiscally labeled against its own dei calendar, so the stub
    carries real-shaped AAPL dei cover rows by default; `include_dei=False`
    builds the dei-less filing the fail-loud path is tested with."""
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    rows = [
        {
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": "aapl:IPhoneMember",
            "concept": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
            "numeric_value": revenue_value,
            "unit_ref": "usd",
            "currency": "USD",
            "period_type": "duration",
            # 12-month window aligned to the staged dei fiscal-year-end
            # (--09-28): the annual path carries the same boundary tolerance
            # as the sub-annual paths (Task 16 round-2), so a realistic FY
            # fact must end at the declared year-end — never at filing_date
            # (a 10-K files weeks AFTER its fiscal year ends).
            "period_start": "2023-10-01",
            "period_end": "2024-09-28",
            "period_instant": None,
        },
    ]
    if include_dei:
        rows += [
            {"concept": "dei:DocumentFiscalPeriodFocus", "value": "FY"},
            {"concept": "dei:CurrentFiscalYearEndDate", "value": "--09-28"},
            {"concept": "dei:DocumentFiscalYearFocus", "value": "2024"},
        ]
    xb.facts.to_dataframe.return_value.to_dict.return_value = rows
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
    # Task 13: direct builder calls supply the filing's dei calendar
    # (MSFT's real June-30 fiscal year end, per-filing focus values).
    q_dei = {
        "fiscal_period_focus": "Q3", "fiscal_year_end": "--06-30",
        "fiscal_year_focus": "2026",
    }
    annual_dei = {
        "fiscal_period_focus": "FY", "fiscal_year_end": "--06-30",
        "fiscal_year_focus": "2025",
    }

    # 3-month quarter fact.
    q3_fact = mod._build_dimensional_revenue_fact(
        raw["three_month"], "MSFT", q_accession, q_filed, q_dei,
    )
    assert q3_fact["duration_months"] == 3
    assert q3_fact["value"] == 35013000000.0  # exemplar value, pinned exact

    # 9-month YTD fact — SAME period_end as the 3-month fact above (the
    # dual-duration collision duration_months exists to de-conflate).
    ytd9_fact = mod._build_dimensional_revenue_fact(
        raw["nine_month_ytd"], "MSFT", q_accession, q_filed, q_dei,
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
        annual_dei,
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
        mod._build_dimensional_revenue_fact(
            missing_start_row, "MSFT", "acc", "filed", q_dei,
        )

    # A malformed (non-ISO) period_start also raises loud.
    malformed_start_row = dict(raw["three_month"])
    malformed_start_row["period_start"] = "not-a-date"
    with pytest.raises(ValueError, match="period_start"):
        mod._build_dimensional_revenue_fact(
            malformed_start_row, "MSFT", "acc", "filed", q_dei,
        )


def test_extract_emits_duration_weeks():
    """Task 1 (docs/loom/plans/2026-07-18-52-53-week-filer-support.md) —
    `_build_dimensional_revenue_fact` emits `duration_weeks` alongside
    `duration_months` for EVERY duration-context fact (week-count honesty
    rides the per-point field on every fact, independent of which lane
    classifies it — plan Notes, class-lane precedence; Q4-derivation
    arithmetic needs FY_weeks - YTD_weeks regardless of classification).

    The pure `_week_lane_class` span->band mapper is the single shared
    primitive (docs/loom/memory/shared-classifier-over-open-dialects-
    needs-allowlist.md) both Gate P and Gate C will decide through: a
    251-day span (36wk-ish) classifies to the YTD-through-Q3 band, a
    111-day span (16wk-ish) classifies to the week-Q4 band, and an
    ordinary ~365-day calendar-year span (month-lane territory) makes NO
    week-lane claim — the allowlist is narrow observed-week clusters with
    gaps, never one wide contiguous range that would swallow month-lane
    spans (fail-closed unchanged)."""
    mod = _load_helpers()
    fixture = json.loads((FIXTURES / "xbrl_quarterly_msft.json").read_text())
    raw = fixture["raw_facts"]
    q_accession = fixture["quarterly_filing"]["accession"]
    q_filed = fixture["quarterly_filing"]["filing_date"]
    q_dei = {
        "fiscal_period_focus": "Q3", "fiscal_year_end": "--06-30",
        "fiscal_year_focus": "2026",
    }

    # 251-day synthetic span (36wk-ish YTD-through-Q3 week band), period_end
    # on a real fiscal quarter boundary (Mar 31) so Gate P's label
    # derivation does not raise — only the dates are overridden on the
    # real fixture row (existing test-file convention, e.g. the
    # missing/malformed period_start rows above).
    ytd3q_row = dict(raw["three_month"])
    ytd3q_row["period_start"] = "2025-07-23"
    ytd3q_row["period_end"] = "2026-03-31"
    ytd3q_fact = mod._build_dimensional_revenue_fact(
        ytd3q_row, "TEST", q_accession, q_filed, q_dei,
    )
    assert ytd3q_fact["duration_weeks"] == 36

    # 111-day synthetic span (16wk-ish week-Q4 band), period_end on the
    # fiscal year end (Jun 30).
    weekq4_row = dict(raw["three_month"])
    weekq4_row["period_start"] = "2026-03-11"
    weekq4_row["period_end"] = "2026-06-30"
    weekq4_fact = mod._build_dimensional_revenue_fact(
        weekq4_row, "TEST", q_accession, q_filed, q_dei,
    )
    assert weekq4_fact["duration_weeks"] == 16

    # Ordinary ~365-day calendar-year span (month-lane territory, NOT a
    # 52/53-week filer) still gets a duration_weeks count — week-count
    # honesty on EVERY fact — but the pure mapper below must make no
    # week-lane claim for it.
    fy_row = dict(raw["three_month"])
    fy_row["period_start"] = "2025-06-30"
    fy_row["period_end"] = "2026-06-30"
    fy_fact = mod._build_dimensional_revenue_fact(
        fy_row, "TEST", q_accession, q_filed, q_dei,
    )
    assert fy_fact["duration_weeks"] == 52
    assert fy_fact["duration_months"] == 12

    # The pure span -> week-lane-class mapper, exercised directly.
    assert mod._week_lane_class(251) == "YTD-through-Q3"
    assert mod._week_lane_class(111) == "week-Q4"
    assert mod._week_lane_class(365) is None, (
        "an ordinary ~365d calendar-year span must make NO week-lane "
        "claim — the allowlist is narrow week-multiple clusters with "
        "gaps, never a wide range that swallows month-lane spans"
    )


@pytest.mark.parametrize(
    ("span_days", "expected"),
    [
        # Every _WEEK_BANDS cluster at both edges ([weeks*7 - 1, weeks*7]).
        (83, "quarter"), (84, "quarter"),                   # 12wk
        (90, "quarter"), (91, "quarter"),                   # 13wk
        (111, "week-Q4"), (112, "week-Q4"),                 # 16wk
        (118, "week-Q4"), (119, "week-Q4"),                 # 17wk
        (167, "H1"), (168, "H1"),                           # 24wk
        (181, "H1"), (182, "H1"),                           # 26wk
        (251, "YTD-through-Q3"), (252, "YTD-through-Q3"),   # 36wk
        (272, "YTD-through-Q3"), (273, "YTD-through-Q3"),   # 39wk
        (363, "FY"), (364, "FY"),                           # 52wk
        (370, "FY"), (371, "FY"),                           # 53wk
        # Gap / out-of-band spans make NO claim (fail-closed).
        (82, None), (85, None), (110, None), (120, None),
        (166, None), (169, None), (250, None), (274, None),
        (362, None), (365, None), (369, None), (372, None),
    ],
)
def test_week_lane_class_pins_every_band_boundary(span_days, expected):
    """code-quality-reviewer 🟡 (52/53-week Task 1) — pin the shared
    `_WEEK_BANDS` table at EVERY band's cluster edges plus the gaps
    between clusters, so a mistyped week count in the allowlist fails a
    test instead of silently reclassifying (the FY band — the arc's
    namesake — was previously unpinned at 364/371)."""
    mod = _load_helpers()
    assert mod._week_lane_class(span_days) == expected


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
# Task 13 extends the read with the THIRD cover tag, dei:DocumentFiscalYearFocus
# ("2021" / "2026" respectively — re-captured live from the same two real
# accessions 2026-07-18, never hand-typed).
# This drift (NVDA is a 52/53-week filer, docs/loom/references/
# xbrl-verification-universe.md:49) is the load-bearing evidence the whole
# task exists to protect: a per-ticker cache would apply ONE filing's
# calendar to the other's facts and silently mislabel its quarters.
# ---------------------------------------------------------------------------

def _make_dei_filing(*, accession, form, filing_date, period_of_report,
                      fiscal_period_focus, fiscal_year_end, fiscal_year_focus):
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
            # 12-month window aligned to the filing's OWN period_of_report
            # (its declared fiscal year end) — never filing_date, which
            # sits weeks past the year end and lands outside
            # FISCAL_BOUNDARY_TOLERANCE_DAYS (T16 round-2 hygiene,
            # mirrors _make_dimensional_filing's d2e421e8 fix).
            "period_start": (
                datetime.date.fromisoformat(period_of_report)
                - datetime.timedelta(days=364)
            ).isoformat(),
            "period_end": period_of_report,
            "period_instant": None,
        },
        {"concept": "dei:DocumentFiscalPeriodFocus", "value": fiscal_period_focus},
        {"concept": "dei:CurrentFiscalYearEndDate", "value": fiscal_year_end},
        {"concept": "dei:DocumentFiscalYearFocus", "value": fiscal_year_focus},
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
        fiscal_year_focus="2021",
    )
    filing_2026 = _make_dei_filing(
        accession="0001045810-26-000021", form="10-K",
        filing_date=datetime.date(2026, 2, 25), period_of_report="2026-01-25",
        fiscal_period_focus="FY", fiscal_year_end="--01-25",
        fiscal_year_focus="2026",
    )

    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.return_value = [filing_2021, filing_2026]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("NVDA", since_year=2021, until_year=2026)

    assert "error" not in pack, pack
    assert pack["coverage"]["unclassifiable_periods"] == [], (
        "the staged annual facts must be FYE-aligned (T16 round-2 hygiene, "
        "mirrors d2e421e8): a helper window ending at filing_date instead "
        "of the declared year-end silently quarantines the very facts the "
        "stub stages -- got "
        f"{pack['coverage']['unclassifiable_periods']}"
    )
    calendars = pack["fiscal_calendars"]
    assert calendars["0001045810-21-000010"] == {
        "fiscal_period_focus": "FY", "fiscal_year_end": "--01-31",
        "fiscal_year_focus": "2021",
    }, calendars
    assert calendars["0001045810-26-000021"] == {
        "fiscal_period_focus": "FY", "fiscal_year_end": "--01-25",
        "fiscal_year_focus": "2026",
    }, calendars
    assert (
        calendars["0001045810-21-000010"]["fiscal_year_end"]
        != calendars["0001045810-26-000021"]["fiscal_year_end"]
    ), (
        "the two filings' fiscal-year-end must differ -- proves each filing's "
        "OWN dei value is retained, not one cached value applied to both"
    )


def test_extract_dei_fiscal_calendar_absent_tag_is_none_not_fabricated(sec_client):
    """Absent dei tags are `None` at the pure per-filing read — never a
    guessed/fabricated value (Task 3's invariant, unchanged). Task 19
    UPDATE at the extract path (was Task 13's "propagates out of extract"):
    the fail-loud property MOVES to the quarantine flag — the unlabelable
    filing's facts are excluded and the DQC flag surfaces loudly under
    `coverage.unlabelable_filings`, never a silent labeled pack (still
    never `period_end[:4]` emitted as fiscal_year, never a fabricated
    calendar value; the run continues instead of aborting)."""
    # Pure read: no dei rows -> all three tags None, never fabricated.
    assert sec_client._extract_dei_calendar(
        [{"concept": "us-gaap:Revenues", "value": 1.0}]
    ) == {
        "fiscal_period_focus": None, "fiscal_year_end": None,
        "fiscal_year_focus": None,
    }

    # Extract path: dei-less filing with facts in hand -> quarantined loud
    # (Task 19 justification: the fail-loud property moves from a whole-run
    # UnreadableFiscalCalendarError abort to the quarantine flag — the
    # error stays loud in coverage, never silent, and never a labeled pack).
    filing = _make_dimensional_filing(
        accession="0000320193-24-000123", form="10-K",
        filing_date=datetime.date(2024, 11, 1), revenue_value=100.0,
        include_dei=False,
    )
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value = [filing]
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue("AAPL")
    assert "error" not in pack, pack
    assert pack["facts"] == [], (
        "an unlabelable filing's facts are EXCLUDED from labeled output -- "
        f"{pack['facts']}"
    )
    quarantined = pack["coverage"]["unlabelable_filings"]
    assert len(quarantined) == 1, pack["coverage"]
    assert quarantined[0]["type"] == "unreadable_fiscal_calendar", quarantined
    assert "0000320193-24-000123" in quarantined[0]["accessions"], quarantined


# ---------------------------------------------------------------------------
# Task 4 (2026-07-16-operational-kpi-quarterly) — ADR/20-F foreign-private-
# issuer regime: a quarterly request for a ticker with no 10-Q must return an
# EXPLICIT N/A with reason, never a silently-empty fact-pack. Detected from
# the REAL submissions form histogram (`fetch_submissions`), never a
# hardcoded ticker list.
#
# Histogram MACHINE-CAPTURED 2026-07-17 against the real SEC submissions API
# (never hand-typed):
#   curl -s -A "monkeyskills research kouko.d@gmail.com" \
#     https://data.sec.gov/submissions/CIK0001046179.json
# `filings.recent.form` (1002 rows) counts: 20-F=15, 6-K=750, 6-K/A=6, 4=136,
# 3=42, 3/A=3, SD=13, SC 13G/A=17, SC 13G=8, S-8=1, 424B2=2, FWP=2, 424B5=2,
# F-3ASR=1, UPLOAD=2, CORRESP=1 — ZERO 10-Q, ZERO 10-K anywhere in the window.
# ---------------------------------------------------------------------------

def _tsm_submissions_stub() -> dict:
    """Rebuilds the real captured `filings.recent.form` array from TSM's
    live counts (only `.form` is read by the regime detector, so the other
    parallel arrays — filingDate/accessionNumber/etc — are omitted; a real
    submissions response always carries them, but the detector never reads
    them, so adding them here would be unused clutter)."""
    forms = (
        ["20-F"] * 15
        + ["6-K"] * 750
        + ["6-K/A"] * 6
        + ["4"] * 136
        + ["3"] * 42
        + ["SD"] * 13
    )
    return {"data": {"filings": {"recent": {"form": forms}}}}


def test_quarterly_foreign_filer_returns_na(sec_client, monkeypatch):
    """A ticker whose submissions history has 20-F + 6-K but NO 10-Q (TSM,
    live-verified above) must return an explicit 'no quarterly XBRL (foreign
    20-F/6-K regime)' N/A carrying a reason, distinguishable from BOTH the
    generic form-not-available error and a real empty result — never a
    silently-empty fact-pack (spec: 'A foreign/ADR filer with no 10-Q is
    detected and returned N/A, never silently empty')."""
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1046179
    # No 10-Q filings at all -- matches TSM's real filing history.
    company.get_filings.return_value = []
    sec_client.edgar_stub.Company.return_value = company
    monkeypatch.setattr(
        sec_client, "fetch_submissions", lambda cik: _tsm_submissions_stub()
    )

    result = sec_client.extract_dimensional_revenue("TSM", form="10-Q")

    assert "error" in result, "must be an explicit N/A slot, not a silent success"
    assert "facts" not in result, (
        "must not ALSO carry a facts key (a silently-empty facts=[] alongside "
        "the error would let a facts-or-empty caller mis-read this as a real "
        "empty result)"
    )
    assert result["error_class"] == "foreign_private_issuer_no_quarterly_xbrl", (
        "must carry a DISTINCT error_class from the generic "
        "'dimensional_revenue_extraction_failed' (fetch-error/out-of-range) "
        "class, so a caller can tell the regime-N/A apart without re-deriving it"
    )
    assert result["reason"] == (
        "no quarterly XBRL (foreign 20-F/6-K regime) — submissions history "
        "shows 20-F + 6-K filings, no '10-Q'"
    ), result["reason"]
    assert result["identifier"] == "TSM"


# ---------------------------------------------------------------------------
# Task 10 (2026-07-16-operational-kpi-quarterly) — per-filing/per-quarter
# coverage honesty. Extends scope-A's year-level coverage clamp
# (_dimensional_revenue_coverage) with a `quarterly_coverage` per-fiscal-year
# breakdown: 10-K + up to 3 standalone 10-Qs = 4 expected filings per year
# (Q4 has no standalone 10-Q — derived downstream, Task 8). A missing
# filing's absence is classified into one of FOUR EXPLICIT, mutually
# exclusive reasons (never inferred from a bare absence — docs/loom/memory/
# fail-closed-default-must-be-enforced-not-emergent.md; the 4th,
# "unclassified", was added in revision round 1 finding 3 — see below):
#   not_yet_filed | fetch_error (reserved) | out_of_requested_range | unclassified
# A dimensional signature present in the 10-K but absent from every 10-Q of
# its fiscal year is flagged "no_quarterly_coverage" — never zero-filled.
#
# Revision round 1 fixed a FATAL finding: year grouping was calendar-based
# (`period_of_report[:4]`), not fiscal — for a non-December fiscal year end
# a 10-Q's calendar year and fiscal year diverge (AAPL FY2025 Q1 ends
# 2024-12-28, calendar 2024, fiscal 2025), fabricating a `fetch_error`/
# `unclassified` for a filing already in hand plus a phantom prior-year
# record. The tests below are driven by a MACHINE-CAPTURED real AAPL filing
# set (fixtures/xbrl_quarterly_completeness_aapl.json, edgartools 5.42.0,
# captured 2026-07-17) — chosen BECAUSE AAPL's September fiscal year end
# exposes exactly this bug, unlike the prior hand-typed December-FYE MSFT
# double (which accidentally hid it — the single FYE where calendar-year
# grouping happens to equal fiscal-year grouping).
# ---------------------------------------------------------------------------

def _make_quarterly_filing(*, accession, form, filing_date, period_of_report,
                            concept, dim_member, revenue_value):
    """Fake edgartools Filing carrying one dimensional-revenue row, with
    `period_of_report` set (unlike `_make_dimensional_filing`, which omits
    it) — Task 10's per-quarter matching reads `period_of_report`, not
    `filing_date`, to place a filing on the fiscal calendar. Task 13: a
    selected filing's facts are fiscally labeled per-fact, so the stub
    carries AAPL's real September fiscal-year-end dei tag (--09-27, the
    FY2025 value; the 27-vs-28 per-year drift sits well inside
    FISCAL_BOUNDARY_TOLERANCE_DAYS). A real filing carries all three dei
    cover tags; the completeness tests read none, and the labeling
    derivation requires only this one."""
    xb = mock.MagicMock(name=f"xbrl-{accession}")
    xb.facts.to_dataframe.return_value.to_dict.return_value = [
        {
            "is_dimensioned": True,
            "dim_srt_ProductOrServiceAxis": dim_member,
            "concept": concept,
            "numeric_value": revenue_value,
            "unit_ref": "usd",
            "currency": "USD",
            "period_type": "duration",
            "period_start": (filing_date - datetime.timedelta(days=90)).isoformat(),
            "period_end": period_of_report,
            "period_instant": None,
        },
        {"concept": "dei:CurrentFiscalYearEndDate", "value": "--09-27"},
    ]
    filing = SimpleNamespace(
        accession_no=accession, filing_date=filing_date, form=form,
        period_of_report=period_of_report,
    )
    filing.xbrl = lambda bound=xb: bound
    return filing


def _load_aapl_quarterly_fixture():
    return json.loads(
        (FIXTURES / "xbrl_quarterly_completeness_aapl.json").read_text()
    )


def _filing_from_quarterly_fixture_record(record):
    """Build a fake edgartools Filing + one dimensional-revenue fact from a
    MACHINE-CAPTURED record in xbrl_quarterly_completeness_aapl.json (real
    accession/filing_date/period_of_report, never hand-typed)."""
    return _make_quarterly_filing(
        accession=record["accession"], form=record["form"],
        filing_date=datetime.date.fromisoformat(record["filing_date"]),
        period_of_report=record["period_of_report"],
        concept="us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        dim_member="us-gaap:ProductMember", revenue_value=1.0,
    )


def _aapl_company_stub(sec_client, filings):
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 320193
    company.get_filings.return_value = filings
    sec_client.edgar_stub.Company.return_value = company
    return company


def test_coverage_per_quarter_completeness_all_present_no_phantom_year(sec_client):
    """FATAL regression (Task 10 revision round 1): AAPL's real FY2025 10-K
    + Q1 + Q2 + Q3 are ALL present in EDGAR. AAPL's FYE is 2025-09-27
    (September) — Q1's real period_of_report is 2024-12-28, CALENDAR year
    2024, one year off from its FISCAL year 2025. The buggy calendar-year
    grouping (`period[:4]`) put Q1 in a phantom bucket year 2024 (fabricating
    a fetch_error for a filing already in hand) while FY2025 fell to 3/4
    with Q1 wrongly reported missing. The fix must report exactly ONE
    fiscal-year record (2025), full 4/4, no phantom 2024 entry."""
    fixture = _load_aapl_quarterly_fixture()
    filings = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in ("fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2025_q3")
    ]
    _aapl_company_stub(sec_client, filings)

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2024, until_year=2025,
        as_of=datetime.date(2026, 1, 1),
    )
    assert "error" not in pack, pack
    quarterly = pack["coverage"]["quarterly_coverage"]
    assert quarterly is not None, "form='10-Q' must populate quarterly_coverage"
    fiscal_years = {r["fiscal_year"] for r in quarterly}
    assert fiscal_years == {2025}, (
        f"no phantom fiscal-year record — got {fiscal_years}"
    )

    year_record = next(r for r in quarterly if r["fiscal_year"] == 2025)
    assert year_record["status"] == "full", year_record
    assert year_record["present_count"] == 4, year_record
    assert year_record["missing"] == [], year_record

    present_by_label = {p["filing"]: p for p in year_record["present"]}
    assert present_by_label.keys() == {"10-K", "Q1", "Q2", "Q3"}, present_by_label
    assert present_by_label["Q1"]["accession"] == fixture["fy2025_q1"]["accession"], (
        "Q1 (period_of_report 2024-12-28, calendar year 2024) must be "
        f"grouped into FISCAL year 2025 — got {present_by_label['Q1']}"
    )
    assert present_by_label["Q1"]["period_of_report"] == "2024-12-28"
    assert present_by_label["Q2"]["accession"] == fixture["fy2025_q2"]["accession"]
    assert present_by_label["Q3"]["accession"] == fixture["fy2025_q3"]["accession"]


def test_coverage_per_quarter_completeness_partial_missing_quarter(sec_client):
    """A covered year with a 10-K + Q1 + Q2 but no Q3 reports partial
    (3/4, Q3 missing + reason) — the AAPL fixture's real Q1 (calendar year
    2024, fiscal year 2025) must still land correctly in FY2025, proving
    the grouping fix under a partial-year scenario too (not just the
    all-present case above)."""
    fixture = _load_aapl_quarterly_fixture()
    filings = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in ("fy2025_10k", "fy2025_q1", "fy2025_q2")
    ]  # Q3 (expected ~2025-06-27) never filed in this scenario.
    _aapl_company_stub(sec_client, filings)

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2025,
        as_of=datetime.date(2026, 1, 1),
    )
    assert "error" not in pack, pack
    quarterly = pack["coverage"]["quarterly_coverage"]
    year_record = next(r for r in quarterly if r["fiscal_year"] == 2025)

    assert year_record["status"] == "partial", year_record
    assert year_record["present_count"] == 3, year_record
    assert year_record["expected_count"] == 4, year_record
    present_labels = {p["filing"] for p in year_record["present"]}
    assert present_labels == {"10-K", "Q1", "Q2"}, present_labels
    missing_labels = {m["filing"] for m in year_record["missing"]}
    assert missing_labels == {"Q3"}, (
        f"Q3 must be the ONLY missing filing (3/4 present) — got {missing_labels}"
    )
    missing_q3 = year_record["missing"][0]
    assert missing_q3["reason"] == "unclassified", (
        "Q3's expected period end is already due and within the requested "
        f"[2025,2025] range, with no positive fetch-failure evidence — got "
        f"{missing_q3['reason']!r}"
    )
    assert missing_q3["detail"], "the missing entry must carry a human-readable reason string"


def test_coverage_per_quarter_completeness_no_10k_returns_honest_error(sec_client):
    """Task 13 UPDATE (was `..._no_10k_reports_unclassified`, written
    against the OLD calendar-year selection — the root defect): a filer
    with NO 10-K ANYWHERE has no fiscal calendar to derive OR project a
    quarterly filing's declared-fiscal-year candidate from, so a
    fiscal-year range request now returns a LOUD error slot naming that
    reason — never the old behaviour of calendar-bucketing the 10-Q into
    the range (`period_of_report[:4]`, trap 1 of docs/loom/memory/
    fiscal-year-derive-per-fact-against-filing-calendar.md; the old test
    asserted a pack keyed on fiscal_year=2024 for a FISCAL-2025 filing).
    The in-hand-filing coverage honesty this test used to carry moves to
    Task 18's rebuilt index-universe coverage (index-visible-but-not-
    selected), per the plan."""
    fixture = _load_aapl_quarterly_fixture()
    q1 = _filing_from_quarterly_fixture_record(fixture["fy2025_q1"])
    _aapl_company_stub(sec_client, [q1])  # no 10-K at all, ever

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2024, until_year=2024,
        as_of=datetime.date(2026, 1, 1),
    )
    assert "error" in pack, (
        f"a filer with no annual filing has no derivable fiscal-year "
        f"candidate — the request must fail loud, never calendar-bucket "
        f"-- {pack.get('coverage')}"
    )
    assert "no derivable fiscal calendar" in pack["error"], pack["error"]
    assert "never calendar-bucketed" in pack["error"], pack["error"]


def test_coverage_per_quarter_completeness_in_progress_fy_projects_forward(sec_client):
    """FATAL regression (Task 10 revision round 2): every filer's CURRENT
    in-progress fiscal year has NO 10-K yet -- real AAPL FY2026 (10-K not
    due until ~Oct 2026) already has TWO real 10-Qs in hand: Q1 (period
    2025-12-27) and Q2 (period 2026-03-28). The pre-fix calendar-year
    fallback put FY2026-Q1 into FY2025's bucket (both share CALENDAR year
    2025) where it silently rotted in FY2025's `remaining`, and minted a
    phantom FY2026 record with fiscal_year_end=None reporting BOTH
    filings absent -- 'two filings in hand, reported absent', the exact
    bug this task exists to remove, reinstated on the in-progress-year
    path. The fix projects FY2026's fiscal year end forward from FY2025's
    real 10-K (`_subtract_months(fye, -12)`) and window-matches against
    the projection, so a projected year's not-yet-due 10-K/Q3 report
    `not_yet_filed` (never `unclassified`)."""
    fixture = _load_aapl_quarterly_fixture()
    filings = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in (
            "fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2025_q3",
            "fy2026_q1", "fy2026_q2",
        )
    ]
    _aapl_company_stub(sec_client, filings)

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2026,
        as_of=datetime.date(2026, 6, 1),
    )
    assert "error" not in pack, pack
    quarterly = pack["coverage"]["quarterly_coverage"]
    by_year = {r["fiscal_year"]: r for r in quarterly}
    assert set(by_year) == {2025, 2026}, (
        f"no phantom fiscal year -- got {set(by_year)}"
    )

    fy2025 = by_year[2025]
    assert fy2025["status"] == "full", fy2025
    assert fy2025["present_count"] == 4, fy2025
    assert fy2025["missing"] == [], (
        f"FY2026's quarters must not be misfiled into FY2025's bucket -- {fy2025}"
    )

    fy2026 = by_year[2026]
    present_by_label = {p["filing"]: p for p in fy2026["present"]}
    assert present_by_label.keys() == {"Q1", "Q2"}, (
        f"both real in-hand FY2026 quarters must be PRESENT, never absent -- {fy2026}"
    )
    assert present_by_label["Q1"]["accession"] == fixture["fy2026_q1"]["accession"]
    assert present_by_label["Q2"]["accession"] == fixture["fy2026_q2"]["accession"]

    missing_by_label = {m["filing"]: m["reason"] for m in fy2026["missing"]}
    assert missing_by_label == {"10-K": "not_yet_filed", "Q3": "not_yet_filed"}, (
        f"10-K and Q3 aren't due yet under the projected FYE (~2026-09-27, "
        f"as_of=2026-06-01) -- must be not_yet_filed, never unclassified -- {fy2026}"
    )


def test_coverage_per_quarter_completeness_unfiled_q1_never_matches_q3s_filing(sec_client):
    """Q1 unfiled, Q3 filed: the greedy first-match-in-tolerance walk
    (`_match_quarter_filing`, label order Q1→Q2→Q3) must never let Q3's
    real filing get consumed by an earlier label. Task 10 revision round 1
    finding 5: reviewer's mutation widening `_QUARTER_MATCH_TOLERANCE_DAYS`
    to 100000 does exactly that (Q1 greedily grabs Q3's filing, leaving Q3
    reported missing) while the full suite stays green at the shipped
    tolerance — pin the correct Q1-missing/Q3-present assignment directly."""
    fixture = _load_aapl_quarterly_fixture()
    tenk = _filing_from_quarterly_fixture_record(fixture["fy2025_10k"])
    q3 = _filing_from_quarterly_fixture_record(fixture["fy2025_q3"])
    _aapl_company_stub(sec_client, [tenk, q3])  # Q1, Q2 never filed

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2025,
        as_of=datetime.date(2026, 1, 1),
    )
    assert "error" not in pack, pack
    year_record = next(
        r for r in pack["coverage"]["quarterly_coverage"] if r["fiscal_year"] == 2025
    )
    present_by_label = {p["filing"]: p for p in year_record["present"]}
    missing_labels = {m["filing"] for m in year_record["missing"]}
    assert missing_labels == {"Q1", "Q2"}, missing_labels
    assert "Q3" in present_by_label, present_by_label
    assert present_by_label["Q3"]["accession"] == fixture["fy2025_q3"]["accession"], (
        present_by_label["Q3"]
    )


def test_missing_quarter_reason_pairwise_distinct_states(sec_client):
    """The explicit `_missing_quarter_reason` states are distinguished —
    pure classifier, each proven independently, never collapsed into one
    silent 'gap'. Covers finding 4 (Task 10 revision round 1): the
    `until_year`-EXCEEDS branch is a distinct code path from the
    `since_year`-PRECEDES branch and must be pinned separately — reviewer's
    mutation collapsing 'exceeds' into the catch-all left the suite green.

    Task 18 UPDATE (was written against the calendar-basis signature): the
    range verdict now rides the quarter's FISCAL year, never
    `expected_end.year` (trap 1 of docs/loom/memory/fiscal-year-derive-
    per-fact-against-filing-calendar.md), and it is checked FIRST — an
    out-of-range future quarter is out_of_requested_range, never
    not_yet_filed."""
    reason_not_yet, _ = sec_client._missing_quarter_reason(
        datetime.date(2026, 6, 30), fiscal_year=2026,
        since_year=2026, until_year=2026, as_of=datetime.date(2026, 1, 1),
    )
    reason_unclassified, _ = sec_client._missing_quarter_reason(
        datetime.date(2025, 9, 30), fiscal_year=2025,
        since_year=2025, until_year=2025, as_of=datetime.date(2026, 1, 1),
    )
    reason_precedes_since, _ = sec_client._missing_quarter_reason(
        datetime.date(2019, 9, 30), fiscal_year=2019,
        since_year=2025, until_year=2025, as_of=datetime.date(2026, 1, 1),
    )
    reason_exceeds_until, detail_exceeds_until = sec_client._missing_quarter_reason(
        datetime.date(2030, 3, 31), fiscal_year=2030,
        since_year=2025, until_year=2028, as_of=datetime.date(2032, 1, 1),
    )
    assert reason_not_yet == "not_yet_filed", reason_not_yet
    assert reason_unclassified == "unclassified", reason_unclassified
    assert reason_precedes_since == "out_of_requested_range", reason_precedes_since
    assert reason_exceeds_until == "out_of_requested_range", reason_exceeds_until
    assert "exceeds" in detail_exceeds_until, detail_exceeds_until
    assert len({reason_not_yet, reason_unclassified, reason_precedes_since}) == 3, (
        "the three DISTINCT VALUES must be pairwise distinct — a design "
        "that lets two collapse to the same value would silently conflate "
        "them (precedes/exceeds share the 'out_of_requested_range' value "
        "by design — same meaning to the caller — but must fire from "
        "genuinely separate code paths, asserted above via the detail text)"
    )

    # Fiscal-vs-calendar trap pin (Task 18): AAPL FY2025-Q1's expected end
    # 2024-12-27 has CALENDAR year 2024 — under the old expected_end.year
    # basis a [2025, 2025] request misclassified it out_of_requested_range;
    # its FISCAL year 2025 is squarely in range.
    reason_fiscal_in_range, _ = sec_client._missing_quarter_reason(
        datetime.date(2024, 12, 27), fiscal_year=2025,
        since_year=2025, until_year=2025, as_of=datetime.date(2026, 1, 1),
    )
    assert reason_fiscal_in_range == "unclassified", (
        "the range verdict must ride the FISCAL year (2025, in range) — "
        f"never the calendar year of the expected end (2024) -- got "
        f"{reason_fiscal_in_range!r}"
    )

    # Precedence pin (Task 18): a future quarter of a year the caller
    # never asked for is out_of_requested_range, never not_yet_filed —
    # the window verdict is independent of the clock.
    reason_future_out_of_range, _ = sec_client._missing_quarter_reason(
        datetime.date(2026, 6, 27), fiscal_year=2026,
        since_year=2025, until_year=2025, as_of=datetime.date(2026, 1, 1),
    )
    assert reason_future_out_of_range == "out_of_requested_range", (
        reason_future_out_of_range
    )


def test_dimension_quarterly_absence_flags_10k_only_dimension(sec_client):
    """A dimension present in the 10-K but absent from every 10-Q of its
    fiscal year is flagged 'no_quarterly_coverage' by
    `_dimension_quarterly_absence`, never zero-filled (no synthesized
    'value' key on the flag)."""
    annual_facts = [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "ProductivityMember"},
            "consolidation": None, "fiscal_year": 2025, "value": 500.0,
        },
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "DiscontinuedSegmentMember"},
            "consolidation": None, "fiscal_year": 2025, "value": 20.0,
        },
    ]
    quarterly_facts = [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "ProductivityMember"},
            "consolidation": None, "fiscal_year": 2025, "value": 100.0,
        },
    ]
    flags = sec_client._dimension_quarterly_absence(annual_facts, quarterly_facts)
    assert len(flags) == 1, flags
    assert flags[0]["dimensions"] == {"ProductOrService": "DiscontinuedSegmentMember"}
    assert flags[0]["flag"] == "no_quarterly_coverage"
    assert "value" not in flags[0], (
        "the absence flag must never carry a synthesized/zero-filled 'value'"
    )


def test_dimension_quarterly_absence_january_fye_no_false_flag(sec_client):
    """Task 10 revision round 2, finding 2: `_dimension_quarterly_absence`
    keyed on `fact['fiscal_year']` (the CALENDAR year of `period_end`) —
    the same defect class the filing-level grouping fix (round 1/round 2)
    removed. For a January-FYE filer (real example: NVDA, FYE ~01-26)
    EVERY quarter's `period_end` calendar year is one behind its fiscal
    year (FY2025 ends 2025-01-26; Q1/Q2/Q3 period ends fall in calendar
    2024) — reviewer's live probe measured a 100% false-flag rate: full
    quarterly coverage of both real NVDA dimensions, still flagged
    'no_quarterly_coverage'. Synthetic facts here mirror that exact shape
    (annual fact period_end/fiscal_year=2025-01-26/2025; quarterly facts
    period_end in 2024 tagged fiscal_year=2024, calendar-correct but
    fiscal-wrong) — the fix must window-match each quarterly fact against
    the annual fact's fiscal calendar (mirrors `_assign_quarterly_filings_
    to_fiscal_years` at fact granularity), not trust its own tagged
    'fiscal_year', so full coverage produces ZERO flags."""
    annual_facts = [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "Datacenter"},
            "consolidation": None, "fiscal_year": 2025,
            "period_end": "2025-01-26", "value": 1000.0,
        },
    ]
    quarterly_facts = [
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "Datacenter"},
            "consolidation": None, "fiscal_year": 2024,
            "period_end": "2024-04-27", "value": 200.0,
        },
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "Datacenter"},
            "consolidation": None, "fiscal_year": 2024,
            "period_end": "2024-07-27", "value": 250.0,
        },
        {
            "concept": "us-gaap:Revenues",
            "dimensions": {"ProductOrService": "Datacenter"},
            "consolidation": None, "fiscal_year": 2024,
            "period_end": "2024-10-26", "value": 260.0,
        },
    ]
    flags = sec_client._dimension_quarterly_absence(annual_facts, quarterly_facts)
    assert flags == [], (
        f"full quarterly coverage of a January-FYE dimension must not be "
        f"false-flagged just because the quarters' own tagged fiscal_year "
        f"(calendar year of period_end) diverges from the fiscal year -- {flags}"
    )


# ---------------------------------------------------------------------------
# Task 13 (2026-07-16-operational-kpi-quarterly REBUILD) — P0: fix the fiscal
# primitive + emit parallel calendar/fiscal labels. RED LINES
# (docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md):
# a fact's fiscal year derives from its OWN period_end measured against the
# filing's dei calendar — NEVER `period_end[:4]` (trap 1: the calendar year)
# and NEVER the filing's DocumentFiscalYearFocus stamped on every fact
# (trap 2: mislabels prior-year comparatives). Driven by MACHINE-CAPTURED
# fixtures: xbrl_quarterly_nvda_range.json (real NVDA FY2026 10-Qs whose
# period_of_report all fall in CALENDAR 2025 + the FY2027-Q1 10-Q a FY2026
# request must NOT touch + the 10-K index anchors),
# xbrl_multifiling_aapl.json (real AAPL FY2019 10-K carrying FY2017/FY2018
# comparatives + live-captured dei cover rows), and
# xbrl_filings_index_cat.json (fixed December-FYE filer — the regime where
# calendar selection was accidentally right and must stay byte-identical).
# ---------------------------------------------------------------------------

def _metadata_only_filing(record, *, reason):
    """Filing stub carrying ONLY filings-index metadata: any `.xbrl()` call
    fails the test with `reason`. Encodes the pre-fetch selection contract —
    selection may read index metadata (form / period_of_report / filing
    date), never a filing body it did not select."""
    filing = SimpleNamespace(
        accession_no=record["accession"],
        filing_date=datetime.date.fromisoformat(record["filing_date"]),
        form=record["form"],
        period_of_report=record["period_of_report"],
    )

    def _never_fetch(_reason=reason):
        raise AssertionError(_reason)

    filing.xbrl = _never_fetch
    return filing


def _nvda_range_company(sec_client):
    """Wire the NVDA range fixture behind a mocked edgartools Company:
    `get_filings(form='10-Q')` returns the three real FY2026 10-Qs (with
    captured raw facts) PLUS the FY2027-Q1 10-Q as metadata-only (fetching
    it fails the test); `get_filings(form='10-K')` returns the metadata-only
    annual index anchors."""
    fixture = json.loads((FIXTURES / "xbrl_quarterly_nvda_range.json").read_text())
    tenqs = [_filing_from_fixture(r) for r in fixture["filings"]]
    tenqs.append(_metadata_only_filing(
        fixture["out_of_range_filing"],
        reason="the FY2027 10-Q (period 2026-04-26) is outside the requested "
               "fiscal range [2026, 2026] and must never be fetched",
    ))
    tenks = [
        _metadata_only_filing(
            r, reason="10-K index anchors serve pre-fetch selection from "
                      "metadata only; their xbrl must never be fetched here",
        )
        for r in fixture["annual_filings_index"]
    ]
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.side_effect = (
        lambda form=None, **_kw: {"10-Q": tenqs, "10-K": tenks}.get(form, [])
    )
    sec_client.edgar_stub.Company.return_value = company
    return fixture


def test_fiscal_range_selects_declared_years(sec_client):
    """A fiscal-year range request selects filings by their DECLARED fiscal
    year (pre-fetch: the sanctioned filings-index derivation, window-matched
    against the 10-K index), never by the calendar year of
    `period_of_report` — the root-cause defect of the scope-B rebuild.

    NVDA (late-January FYE): every FY2026 10-Q period_of_report falls in
    CALENDAR 2025, and the FY2027-Q1 10-Q falls in calendar 2026 — the old
    `int(period_of_report[:4])` selection returned 0 of 3 real FY2026
    quarters plus the one FY2027 filing (live-verified,
    docs/loom/memory/fiscal-year-derive-per-fact-against-filing-calendar.md).
    A fixed-December-FYE filer (CAT) is the one regime where calendar
    selection was accidentally correct — there the fiscal guess must be
    byte-identical to the calendar behaviour."""
    fixture = _nvda_range_company(sec_client)

    pack = sec_client.extract_dimensional_revenue(
        "NVDA", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 7, 18),
    )
    assert "error" not in pack, pack
    fy2026_accessions = {r["accession"] for r in fixture["filings"]}
    got = {f["accession"] for f in pack["facts"]}
    assert got == fy2026_accessions, (
        f"all three real FY2026 10-Qs (period ends in calendar 2025) must be "
        f"selected for the fiscal range [2026, 2026] -- expected "
        f"{fy2026_accessions}, got {got}"
    )
    assert fixture["out_of_range_filing"]["accession"] not in got, (
        "the FY2027 10-Q (period 2026-04-26, CALENDAR 2026) must not be "
        "selected for fiscal [2026, 2026]"
    )

    # Fixed December-FYE filer: the declared-fiscal-year guess equals the
    # old calendar year for EVERY captured 10-Q, so any range selection is
    # byte-identical to the previous calendar behaviour (including the
    # in-progress FY2026 quarter, matched via the projected fiscal window).
    cat = json.loads((FIXTURES / "xbrl_filings_index_cat.json").read_text())
    cat_annual = [
        _metadata_only_filing(r, reason="index metadata only")
        for r in cat["annual_filings"]
    ]
    cat_quarterly = [
        _metadata_only_filing(r, reason="index metadata only")
        for r in cat["quarterly_filings"]
    ]
    guesses = sec_client._quarterly_fiscal_year_guesses(cat_annual, cat_quarterly)
    for record in cat["quarterly_filings"]:
        calendar_year = int(record["period_of_report"][:4])
        assert guesses.get(record["accession"]) == calendar_year, (
            f"December-FYE selection must be byte-identical to the previous "
            f"calendar behaviour: {record['accession']} "
            f"(period {record['period_of_report']}) must guess "
            f"{calendar_year}, got {guesses.get(record['accession'])}"
        )


def test_parallel_period_labels(sec_client):
    """Every emitted fact carries PARALLEL calendar and fiscal period
    labels, honestly named (spec requirement, user-ratified 2026-07-17 —
    mirrors Compustat DATADATE/DATACQTR/DATAFQTR): `calendar_year` +
    `calendar_quarter` mechanically from period_end, AND `fiscal_year` +
    `fiscal_quarter` derived per-fact from the fact's OWN period_end
    measured against that filing's dei fiscal calendar. Both red-line traps
    asserted (docs/loom/memory/fiscal-year-derive-per-fact-against-filing-
    calendar.md): never `period_end[:4]` as fiscal, never the filing's
    DocumentFiscalYearFocus stamped on comparatives."""
    # (2) Comparatives derive from their OWN period, never the filing focus
    # stamped: real AAPL FY2019 10-K (dei:DocumentFiscalYearFocus=2019, dei
    # rows live-captured 2026-07-18) carries FY2017/FY2018 comparatives.
    fixture = _multifiling_company(sec_client)
    del fixture  # selection asserted elsewhere; this test reads labels
    pack19 = sec_client.extract_dimensional_revenue(
        "AAPL", since_year=2019, until_year=2019
    )
    assert "error" not in pack19, pack19
    facts19 = [
        f for f in pack19["facts"] if f["accession"] == "0000320193-19-000119"
    ]
    assert facts19, "the FY2019 10-K must be selected for [2019, 2019]"
    by_end = {}
    for f in facts19:
        by_end.setdefault(f["period_end"], f)
    comparative_2018 = by_end["2018-09-29"]
    assert comparative_2018["fiscal_year"] == 2018, (
        f"a FY2018 comparative in the FY2019 10-K derives its fiscal label "
        f"from its OWN period_end (2018-09-29), never the filing's "
        f"DocumentFiscalYearFocus=2019 stamped -- got {comparative_2018}"
    )
    comparative_2017 = by_end["2017-09-30"]
    assert comparative_2017["fiscal_year"] == 2017, comparative_2017
    current_2019 = by_end["2019-09-28"]
    assert current_2019["fiscal_year"] == 2019, current_2019
    # (3) A 12-month fact carries fiscal_quarter=FY, never a bare Q4 —
    # distinguishable by construction from any reported/derived Q4 point.
    for fact in (comparative_2018, comparative_2017, current_2019):
        assert fact["duration_months"] == 12
        assert fact["fiscal_quarter"] == "FY", (
            f"a 12-month fact must be labeled FY, never a bare Q4 -- {fact}"
        )
    # Calendar labels ride in PARALLEL (mechanical, from period_end).
    assert current_2019["calendar_year"] == 2019
    assert current_2019["calendar_quarter"] == "Q3"

    # (1) Diverging calendar/fiscal labels at a non-December-FYE filer:
    # the real NVDA FY2026-Q3 fact ends 2025-10-26 (calendar 2025-Q4).
    _nvda_range_company(sec_client)
    pack = sec_client.extract_dimensional_revenue(
        "NVDA", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 7, 18),
    )
    assert "error" not in pack, pack
    q3 = next(f for f in pack["facts"] if f["period_end"] == "2025-10-26")
    assert q3["calendar_year"] == 2025 and q3["calendar_quarter"] == "Q4", q3
    assert q3["fiscal_year"] == 2026 and q3["fiscal_quarter"] == "Q3", (
        f"NVDA FY2026-Q3 (period_end 2025-10-26) must carry fiscal 2026-Q3 "
        f"in PARALLEL with calendar 2025-Q4 -- got {q3}"
    )
    q1 = next(f for f in pack["facts"] if f["period_end"] == "2025-04-27")
    assert q1["calendar_year"] == 2025 and q1["calendar_quarter"] == "Q2", q1
    assert q1["fiscal_year"] == 2026 and q1["fiscal_quarter"] == "Q1", q1

    # (4) An unreadable dei fiscal calendar fails loud with a DISTINCT
    # DQC-schema error naming the filing — NEVER period_end[:4] emitted as
    # fiscal_year (trap 1, the root-cause fallback).
    revenue_row = {
        "is_dimensioned": True,
        "dim_srt_ProductOrServiceAxis": "nvda:ComputeMember",
        "concept": "us-gaap:Revenues",
        "numeric_value": 43028000000.0,
        "unit_ref": "usd",
        "currency": "USD",
        "period_type": "duration",
        "period_start": "2025-07-28",
        "period_end": "2025-10-26",
        "period_instant": None,
    }
    absent_calendar = {
        "fiscal_period_focus": None, "fiscal_year_end": None,
        "fiscal_year_focus": None,
    }
    with pytest.raises(sec_client.UnreadableFiscalCalendarError) as exc_info:
        sec_client._build_dimensional_revenue_fact(
            revenue_row, "NVDA", "0001045810-25-000230", "2025-11-19",
            absent_calendar,
        )
    dqc = exc_info.value.dqc
    assert dqc["type"] == "unreadable_fiscal_calendar", dqc
    assert "0001045810-25-000230" in dqc["accessions"], dqc
    assert dqc["reason"], dqc

    malformed_calendar = {
        "fiscal_period_focus": "Q3", "fiscal_year_end": "--13-45",
        "fiscal_year_focus": "2026",
    }
    with pytest.raises(sec_client.UnreadableFiscalCalendarError):
        sec_client._build_dimensional_revenue_fact(
            revenue_row, "NVDA", "0001045810-25-000230", "2025-11-19",
            malformed_calendar,
        )


# ---------------------------------------------------------------------------
# Task 14 (2026-07-16-operational-kpi-quarterly REBUILD) — post-fetch
# reconciliation of the selection guess. The pre-fetch index derivation is a
# GUESS; the fetched filing's own dei:DocumentFiscalYearFocus is the TRUTH
# (spec: 'range membership MUST be re-checked post-fetch against the declared
# fiscal year; on disagreement the declaration wins and the correction is
# surfaced — never silent in either direction'). Fixture: COPIES of the
# machine-captured NVDA range records (xbrl_quarterly_nvda_range.json,
# freshly parsed per test — the file is never touched), with ONLY the
# dei:DocumentFiscalYearFocus row mutated in-test to stage the two
# reconciliation premises (a counterfactual declaration / an absent
# declaration); every other value stays exactly as captured.
# ---------------------------------------------------------------------------

def test_selection_guess_reconciled_post_fetch(sec_client):
    """After fetch, each guess-selected filing's range membership is
    re-checked against its DECLARED `dei:DocumentFiscalYearFocus`:

    - a filing guess-selected for FY2026 whose fetched declaration says
      FY2027 is EXCLUDED from the FY2026 result AND the guess/declaration
      mismatch is surfaced (the ONE DQC schema: type/old/new/accessions/
      reason) — never silently kept, never silently dropped;
    - a fetched filing with an unreadable (absent/malformed) declaration
      gets a DISTINCT flag naming the filing and is never calendar-bucketed:
      its period_of_report[:4] is 2025 (outside [2026, 2026]), so surviving
      in the result on its pre-fetch fiscal guess is direct proof the
      membership decision never fell back to `period_of_report[:4]`."""
    fixture = json.loads((FIXTURES / "xbrl_quarterly_nvda_range.json").read_text())
    records = fixture["filings"]  # freshly parsed copies; file never touched

    # Case 1 — Q1 filing (0001045810-25-000116, guessed FY2026 from the
    # 10-K index windows): its fetched declaration is staged as FY2027.
    mismatch_rec = records[0]
    for row in mismatch_rec["raw_facts"]:
        if row["concept"] == "dei:DocumentFiscalYearFocus":
            row["value"] = "2027"  # staged counterfactual declaration

    # Case 2 — Q2 filing (0001045810-25-000209): its declaration row is
    # removed entirely (unreadable DocumentFiscalYearFocus); the
    # CurrentFiscalYearEndDate row stays so fiscal LABELS remain derivable.
    unreadable_rec = records[1]
    unreadable_rec["raw_facts"] = [
        row for row in unreadable_rec["raw_facts"]
        if row["concept"] != "dei:DocumentFiscalYearFocus"
    ]

    # Case 3 — Q3 filing (0001045810-25-000230) untouched: declaration
    # '2026' confirms the guess (no flag).
    confirmed_rec = records[2]

    tenqs = [_filing_from_fixture(r) for r in records]
    tenks = [
        _metadata_only_filing(
            r, reason="10-K index anchors serve pre-fetch selection from "
                      "metadata only; their xbrl must never be fetched here",
        )
        for r in fixture["annual_filings_index"]
    ]
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.side_effect = (
        lambda form=None, **_kw: {"10-Q": tenqs, "10-K": tenks}.get(form, [])
    )
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue(
        "NVDA", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 7, 18),
    )
    assert "error" not in pack, pack
    got = {f["accession"] for f in pack["facts"]}

    # Out-of-range declaration: excluded from the FY2026 result...
    assert mismatch_rec["accession"] not in got, (
        f"a filing whose fetched declaration says FY2027 must be excluded "
        f"from the fiscal [2026, 2026] result (the declaration is the "
        f"truth; the guess was only a candidate) -- got accessions {got}"
    )
    # ...while the confirmed filing stays.
    assert confirmed_rec["accession"] in got, got

    # Unreadable declaration: NEVER silently dropped, NEVER calendar-
    # bucketed — period_of_report[:4] == 2025 would have thrown it out of
    # [2026, 2026], so its presence proves membership stands on the fiscal
    # guess, not on a calendar fallback.
    assert unreadable_rec["period_of_report"][:4] == "2025"  # fixture sanity
    assert unreadable_rec["accession"] in got, (
        f"a filing with an unreadable DocumentFiscalYearFocus must not be "
        f"silently dropped, and must not be re-bucketed by "
        f"period_of_report[:4] (=2025, outside the range) -- got {got}"
    )

    flags = pack["coverage"]["fiscal_year_reconciliation"]
    assert isinstance(flags, list), pack["coverage"]
    for flag in flags:
        assert set(flag) == {"type", "old", "new", "accessions", "reason"}, (
            f"every reconciliation flag follows the ONE DQC schema "
            f"(plan kickoff decision: no per-class variants) -- {flag}"
        )

    mismatch_flags = [
        f for f in flags if f["type"] == "fiscal_year_guess_mismatch"
    ]
    assert len(mismatch_flags) == 1, flags
    mismatch_flag = mismatch_flags[0]
    assert mismatch_flag["accessions"] == [mismatch_rec["accession"]], mismatch_flag
    assert mismatch_flag["old"] == 2026, (  # the pre-fetch guess
        f"the mismatch flag records the guess as `old` -- {mismatch_flag}"
    )
    assert mismatch_flag["new"] == 2027, (  # the fetched declaration
        f"the mismatch flag records the declaration as `new` -- {mismatch_flag}"
    )
    assert mismatch_flag["reason"], mismatch_flag

    unreadable_flags = [
        f for f in flags if f["type"] == "unreadable_fiscal_year_declaration"
    ]
    assert len(unreadable_flags) == 1, flags
    unreadable_flag = unreadable_flags[0]
    assert unreadable_flag["accessions"] == [unreadable_rec["accession"]], (
        f"the unreadable-declaration flag must NAME the filing -- "
        f"{unreadable_flag}"
    )
    assert unreadable_flag["new"] is None, unreadable_flag
    assert unreadable_flag["reason"], unreadable_flag

    # The confirmed filing produced NO flag (a clean reconciliation is not
    # noise), and no flag class beyond the two staged premises appeared.
    flagged_accessions = {a for f in flags for a in f["accessions"]}
    assert confirmed_rec["accession"] not in flagged_accessions, flags
    assert len(flags) == 2, flags


# ---------------------------------------------------------------------------
# Task 16 (2026-07-16-operational-kpi-quarterly REBUILD) — boundary tolerance
# + projection derivation basis. (a) A period_end beyond
# FISCAL_BOUNDARY_TOLERANCE_DAYS of EVERY fiscal-quarter boundary is
# UNCLASSIFIABLE: flagged via the ONE DQC schema and QUARANTINED (the fact is
# excluded from fiscal-labeled output, the run continues) — never
# nearest-guessed onto the closest boundary, never a whole-run abort for one
# transition/stub period. (b) Every fiscal label records its derivation
# basis: "dei-declared" (the year-end tag/declaration in hand — per-fact
# labels always rest on their OWN filing's in-hand dei calendar) or
# "projected" (the coverage layer's +12mo forward projection of the prior
# declared FYE for an in-progress fiscal year whose declaration does not yet
# exist — sanctioned FALLBACK only), so an auditor can separate
# authority-confirmed labels/verdicts from projection-grounded ones.
# Fixture: a freshly-parsed COPY of the machine-captured NVDA range records
# (T14 precedent — the file is never touched) with ONLY the one revenue
# row's period_start/period_end mutated to stage the transition-stub
# premise; the AAPL completeness fixture drives the projected-basis leg
# through the same wiring as the in-progress-FY test above.
# ---------------------------------------------------------------------------

def test_label_tolerance_and_projection_basis(sec_client):
    """(a) An out-of-tolerance (transition/stub) period_end is flagged
    unclassifiable (DQC schema) and quarantined — no nearest-boundary guess,
    no extraction abort; sibling filings' facts still emit. (b) Per-fact
    fiscal labels carry derivation_basis="dei-declared"; a coverage record
    for an in-progress fiscal year grounded on the +12mo projected FYE
    carries derivation_basis="projected" (its not_yet_filed verdicts are
    thereby marked projection-grounded), while a 10-K-anchored year carries
    "dei-declared" — never indistinguishable."""
    # --- (a) tolerance: staged stub period on the Q2 filing ----------------
    fixture = json.loads((FIXTURES / "xbrl_quarterly_nvda_range.json").read_text())
    records = fixture["filings"]  # freshly parsed copies; file never touched
    stub_rec = records[1]
    mutated = [
        row for row in stub_rec["raw_facts"] if row["concept"] == "us-gaap:Revenues"
    ]
    assert len(mutated) == 1, "fixture sanity: exactly one revenue row to stage"
    # Counterfactual stub window (documented, T14 precedent — only these two
    # values change): period_end 2025-06-15 sits 51/40/132/224 days from the
    # FY2026 Q1/Q2/Q3/Q4 nominal boundaries (2025-04-25 / 2025-07-25 /
    # 2025-10-25 / 2026-01-25 per the captured --01-25 declaration) — beyond
    # FISCAL_BOUNDARY_TOLERANCE_DAYS=10 from every one; the ~3.5-month span
    # keeps it a sub-annual duration fact.
    mutated[0]["period_start"] = "2025-03-01"
    mutated[0]["period_end"] = "2025-06-15"

    tenqs = [_filing_from_fixture(r) for r in records]
    tenks = [
        _metadata_only_filing(
            r, reason="10-K index anchors serve pre-fetch selection from "
                      "metadata only; their xbrl must never be fetched here",
        )
        for r in fixture["annual_filings_index"]
    ]
    company = mock.MagicMock(name="Company")
    company.not_found = False
    company.cik = 1045810
    company.get_filings.side_effect = (
        lambda form=None, **_kw: {"10-Q": tenqs, "10-K": tenks}.get(form, [])
    )
    sec_client.edgar_stub.Company.return_value = company

    pack = sec_client.extract_dimensional_revenue(
        "NVDA", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 7, 18),
    )
    assert "error" not in pack, (
        f"one stub period must QUARANTINE the fact, never abort the whole "
        f"extraction -- {pack}"
    )
    got = {f["accession"] for f in pack["facts"]}
    assert records[0]["accession"] in got and records[2]["accession"] in got, (
        f"sibling filings' facts still emit (quarantine, not abort) -- {got}"
    )
    assert not any(f["period_end"] == "2025-06-15" for f in pack["facts"]), (
        "the stub fact must be excluded from fiscal-labeled output, never "
        "nearest-guessed onto the 40-days-away Q2 boundary"
    )
    for fact in pack["facts"]:
        assert fact["derivation_basis"] == "dei-declared", (
            f"a per-fact fiscal label rests on its own filing's IN-HAND dei "
            f"calendar -- {fact}"
        )

    flags = pack["coverage"]["unclassifiable_periods"]
    assert isinstance(flags, list), pack["coverage"]
    assert len(flags) == 1, flags
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, (
        f"the unclassifiable flag follows the ONE DQC schema (plan kickoff "
        f"decision: no per-class variants) -- {flag}"
    )
    assert flag["type"] == "unclassifiable_period", flag
    assert flag["accessions"] == [stub_rec["accession"]], (
        f"the flag must NAME the filing -- {flag}"
    )
    assert "2025-06-15" in flag["reason"], flag
    assert "never nearest-guessed" in flag["reason"], flag

    # --- (b) derivation basis: projected vs dei-declared coverage ----------
    fixture_aapl = _load_aapl_quarterly_fixture()
    filings = [
        _filing_from_quarterly_fixture_record(fixture_aapl[key])
        for key in (
            "fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2025_q3",
            "fy2026_q1", "fy2026_q2",
        )
    ]
    _aapl_company_stub(sec_client, filings)

    pack2 = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2026,
        as_of=datetime.date(2026, 6, 1),
    )
    assert "error" not in pack2, pack2
    assert pack2["coverage"]["unclassifiable_periods"] == [], (
        "no stub period staged here — an empty list means 'ran, none "
        "found', never a missing key"
    )
    by_year = {r["fiscal_year"]: r for r in pack2["coverage"]["quarterly_coverage"]}
    assert set(by_year) == {2025, 2026}, by_year

    fy2025 = by_year[2025]
    assert fy2025["derivation_basis"] == "dei-declared", (
        f"FY2025's fiscal calendar is anchored by its own filed 10-K (the "
        f"declaration in hand) -- {fy2025}"
    )
    fy2026 = by_year[2026]
    assert fy2026["derivation_basis"] == "projected", (
        f"FY2026 is in progress (no 10-K/declaration yet): its fiscal "
        f"calendar rests on the +12mo projection of FY2025's declared FYE "
        f"and MUST say so — never indistinguishable from a dei-declared "
        f"read -- {fy2026}"
    )
    # The projection-grounded not_yet_filed verdicts live under (and are
    # thereby marked by) the projected-basis record.
    missing_by_label = {m["filing"]: m["reason"] for m in fy2026["missing"]}
    assert missing_by_label == {"10-K": "not_yet_filed", "Q3": "not_yet_filed"}, (
        fy2026
    )
    # Per-fact labels in the same pack stay tag-grounded ("dei-declared"):
    # every FETCHED filing carries its own in-hand dei calendar, including
    # the in-progress year's 10-Qs.
    for fact in pack2["facts"]:
        assert fact["derivation_basis"] == "dei-declared", fact


def test_annual_out_of_tolerance_unclassifiable(sec_client):
    """The never-guess property covers ANNUAL facts too (Task 16 round-2
    fix): a 12-month fact whose period_end lands beyond
    FISCAL_BOUNDARY_TOLERANCE_DAYS of the filing's nominal fiscal-year-end
    (an old-FYE comparative inside an FYE-change/transition filing) is
    QUARANTINED with the unclassifiable DQC flag — never silently labeled
    FY by the first at-or-after nominal year-end. A 12-month fact WITHIN
    tolerance still labels FY (regression guard)."""

    def _staged_pack(period_start, period_end):
        # T14/T16 counterfactual-row convention: freshly-parsed COPY of the
        # machine-captured NVDA range records (file never touched); ONLY the
        # Q2 filing's one revenue row's period window is mutated in-test.
        fixture = json.loads(
            (FIXTURES / "xbrl_quarterly_nvda_range.json").read_text()
        )
        records = fixture["filings"]
        staged = [
            row for row in records[1]["raw_facts"]
            if row["concept"] == "us-gaap:Revenues"
        ]
        assert len(staged) == 1, "fixture sanity: exactly one revenue row"
        staged[0]["period_start"] = period_start
        staged[0]["period_end"] = period_end

        tenqs = [_filing_from_fixture(r) for r in records]
        tenks = [
            _metadata_only_filing(
                r, reason="10-K index anchors serve pre-fetch selection "
                          "from metadata only; their xbrl must never be "
                          "fetched here",
            )
            for r in fixture["annual_filings_index"]
        ]
        company = mock.MagicMock(name="Company")
        company.not_found = False
        company.cik = 1045810
        company.get_filings.side_effect = (
            lambda form=None, **_kw: {"10-Q": tenqs, "10-K": tenks}.get(form, [])
        )
        sec_client.edgar_stub.Company.return_value = company
        pack = sec_client.extract_dimensional_revenue(
            "NVDA", form="10-Q", since_year=2026, until_year=2026,
            as_of=datetime.date(2026, 7, 18),
        )
        assert "error" not in pack, pack
        return pack, records[1]["accession"]

    # --- out of tolerance: 12-month window ending 2025-06-15, which is
    # 141/224 days from the FY2025/FY2026 nominal year-ends (2025-01-25 /
    # 2026-01-25 per the captured --01-25 declaration) — beyond
    # FISCAL_BOUNDARY_TOLERANCE_DAYS=10 of every nominal FYE. 364-day span
    # -> duration_months == 12 (the annual early-return path).
    pack, staged_accession = _staged_pack("2024-06-16", "2025-06-15")
    assert not any(f["period_end"] == "2025-06-15" for f in pack["facts"]), (
        "a 12-month fact ending beyond tolerance of the nominal "
        "fiscal-year-end must be quarantined, never silently FY-labeled by "
        "the first at-or-after nominal year-end"
    )
    flags = pack["coverage"]["unclassifiable_periods"]
    assert len(flags) == 1, flags
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["type"] == "unclassifiable_period", flag
    assert flag["accessions"] == [staged_accession], flag
    assert "2025-06-15" in flag["reason"], flag

    # --- within tolerance (regression guard): 12-month window ending
    # 2025-01-26, 1 day from the FY2025 nominal year-end 2025-01-25 —
    # still labels FY2025/FY, no flag.
    pack, _ = _staged_pack("2024-01-28", "2025-01-26")
    assert pack["coverage"]["unclassifiable_periods"] == [], (
        "a 12-month fact WITHIN tolerance of the nominal fiscal-year-end "
        "is classifiable — no quarantine"
    )
    annual = [f for f in pack["facts"] if f["period_end"] == "2025-01-26"]
    assert len(annual) == 1, pack["facts"]
    assert annual[0]["duration_months"] == 12, annual[0]
    assert (annual[0]["fiscal_year"], annual[0]["fiscal_quarter"]) == (2025, "FY"), (
        annual[0]
    )


# ---------------------------------------------------------------------------
# Task 18 (2026-07-16-operational-kpi-quarterly REBUILD, supersedes old T10)
# — coverage rebuilt on the corrected fiscal primitive: the report's
# comparison universe is the FULL filings INDEX (never just the selected
# set), index-level absences classify into three PAIRWISE-DISTINGUISHED
# states (not_yet_filed / out_of_requested_range / unclassified — the range
# check on the quarter's FISCAL year, never the calendar year of its
# expected period end: AAPL FY2025-Q1 ends 2024-12-28), and a filing
# present in the index that the pre-fetch selection derivation could not
# place reports as index-visible-but-not-selected — POSITIVE index evidence
# that beats every inferred state, never not_yet_filed, never
# calendar-bucketed (the old reporting-layer calendar fallback is gone).
# Fixtures: the machine-captured AAPL completeness set; the selection-missed
# premise is a counterfactual staged period_of_report on the real FY2026-Q1
# record (T14/T16 staged-row convention — one value changes in a parsed
# copy, the fixture file untouched), wired METADATA-ONLY so any fetch of
# the unselected filing fails the test.
# ---------------------------------------------------------------------------

def test_coverage_per_quarter_completeness(sec_client):
    """(1) A covered year with 10-K+Q1+Q2 but no Q3 reports partial (3/4,
    Q3 + reason). (2) The three index-absence states are pairwise
    distinguished, with the range verdict on the quarter's FISCAL year
    (the same quarter flips unclassified -> out_of_requested_range when the
    request window moves, and an out-of-range year still appears in the
    report — full-index comparison universe). (3) A fiscal-boundary 10-Q
    present in the index that the pre-fetch derivation failed to select
    reports as index_visible_not_selected — named in the year record AND in
    `coverage.selection_gaps` (ONE DQC schema) — never not_yet_filed even
    when its expected quarter end is still in the future."""
    fixture = _load_aapl_quarterly_fixture()
    filings = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in ("fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2026_q2")
    ]  # FY2025's Q3 is absent from the index entirely (scenario 1).
    # Counterfactual staged row (T14/T16 convention; only period_of_report
    # changes): the real FY2026-Q1 10-Q shifted 30 days early — beyond
    # _QUARTER_MATCH_TOLERANCE_DAYS of every known/projected quarter
    # window, so the pre-fetch derivation cannot place it and selection
    # misses it. Metadata-only: fetching the unselected filing = failure.
    staged_q1 = dict(fixture["fy2026_q1"], period_of_report="2025-11-27")
    filings.append(_metadata_only_filing(
        staged_q1,
        reason="the selection-missed boundary 10-Q was never selected and "
               "must never be fetched",
    ))
    _aapl_company_stub(sec_client, filings)

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2026,
        as_of=datetime.date(2026, 6, 1),
    )
    assert "error" not in pack, pack
    by_year = {r["fiscal_year"]: r for r in pack["coverage"]["quarterly_coverage"]}
    assert set(by_year) == {2025, 2026}, by_year

    # (1) Partial year: 3/4, Q3 the one missing filing, reason attached.
    fy2025 = by_year[2025]
    assert fy2025["status"] == "partial", fy2025
    assert (fy2025["present_count"], fy2025["expected_count"]) == (3, 4), fy2025
    assert {p["filing"] for p in fy2025["present"]} == {"10-K", "Q1", "Q2"}
    assert [m["filing"] for m in fy2025["missing"]] == ["Q3"], fy2025
    fy2025_q3_reason = fy2025["missing"][0]["reason"]
    assert fy2025_q3_reason == "unclassified", (
        "FY2025-Q3 is due, in range, absent from the index, with no "
        f"positive evidence of why -- got {fy2025_q3_reason!r}"
    )
    assert fy2025["missing"][0]["detail"], fy2025["missing"][0]

    # (3) Selection gap: the staged boundary Q1 is index-visible but was
    # never selected — its quarter says so by name, never an inferred state.
    fy2026 = by_year[2026]
    assert {p["filing"] for p in fy2026["present"]} == {"Q2"}, fy2026
    missing_2026 = {m["filing"]: m for m in fy2026["missing"]}
    assert set(missing_2026) == {"10-K", "Q1", "Q3"}, fy2026
    gap_entry = missing_2026["Q1"]
    assert gap_entry["reason"] == "index_visible_not_selected", (
        "an index-visible filing the pre-fetch derivation missed must "
        f"surface as a SELECTION gap, never an index absence -- {gap_entry}"
    )
    assert gap_entry["accession"] == staged_q1["accession"], (
        f"the selection-gap entry must NAME the index filing -- {gap_entry}"
    )
    assert "2025-11-27" in gap_entry["detail"], gap_entry
    # The in-progress year's genuinely-unfiled slots stay date-inferred.
    assert missing_2026["10-K"]["reason"] == "not_yet_filed", fy2026
    assert missing_2026["Q3"]["reason"] == "not_yet_filed", fy2026

    # The gap also surfaces at coverage level under the ONE DQC schema.
    gaps = pack["coverage"]["selection_gaps"]
    assert isinstance(gaps, list) and len(gaps) == 1, pack["coverage"]
    assert set(gaps[0]) == {"type", "old", "new", "accessions", "reason"}, (
        f"selection-gap flags follow the ONE DQC schema (plan kickoff "
        f"decision: no per-class variants) -- {gaps[0]}"
    )
    assert gaps[0]["type"] == "index_visible_not_selected", gaps[0]
    assert gaps[0]["accessions"] == [staged_q1["accession"]], gaps[0]
    assert gaps[0]["reason"], gaps[0]

    # (3b) NEVER not_yet_filed: with as_of BEFORE the expected FY2026-Q1
    # end (2025-12-27), date inference alone would say not_yet_filed — but
    # the filing is VISIBLE in the index, and positive evidence beats
    # inference (spec: 'never as not-yet-filed').
    _aapl_company_stub(sec_client, filings)
    pack_early = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2026,
        as_of=datetime.date(2025, 12, 10),
    )
    assert "error" not in pack_early, pack_early
    early_2026 = next(
        r for r in pack_early["coverage"]["quarterly_coverage"]
        if r["fiscal_year"] == 2026
    )
    early_q1 = next(m for m in early_2026["missing"] if m["filing"] == "Q1")
    assert early_q1["reason"] == "index_visible_not_selected", (
        "an index-VISIBLE filing must never be reported not_yet_filed just "
        f"because its expected quarter end postdates as_of -- {early_q1}"
    )

    # (2) Range states on the FISCAL basis + full-index universe: narrow
    # the request to [2026, 2026] — FY2025 (out of range) STILL appears
    # (comparison universe is the index, not the request), its index-present
    # filings stay listed, and the SAME absent Q3 flips its reason to
    # out_of_requested_range on its FISCAL year (2025) — even though its
    # expected period end 2025-06-27 says nothing calendar-wise about 2026.
    _aapl_company_stub(sec_client, filings)
    pack_narrow = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 6, 1),
    )
    assert "error" not in pack_narrow, pack_narrow
    narrow_by_year = {
        r["fiscal_year"]: r for r in pack_narrow["coverage"]["quarterly_coverage"]
    }
    assert 2025 in narrow_by_year, (
        f"the comparison universe is the FULL filings index — an "
        f"out-of-range year with index filings must still be reported -- "
        f"{set(narrow_by_year)}"
    )
    narrow_2025 = narrow_by_year[2025]
    assert {p["filing"] for p in narrow_2025["present"]} == {"10-K", "Q1", "Q2"}
    narrow_q3 = next(m for m in narrow_2025["missing"] if m["filing"] == "Q3")
    assert narrow_q3["reason"] == "out_of_requested_range", (
        "the range verdict rides the quarter's FISCAL year (2025 outside "
        f"[2026, 2026]), never the calendar year of its expected end -- "
        f"{narrow_q3}"
    )

    # Pairwise distinct: all four observed states are distinct values.
    assert len({
        fy2025_q3_reason, missing_2026["10-K"]["reason"],
        gap_entry["reason"], narrow_q3["reason"],
    }) == 4, "absence states must never collapse into one 'gap'"


# ---------------------------------------------------------------------------
# Task 19 (2026-07-16-operational-kpi-quarterly REBUILD) — the two OBSERVED
# failure states + quarantine blast radius. Both are grounded by in-hand
# evidence (never inferred from index absence — that is T18's lane):
# `attempted_fetch_failed` (a download/XBRL-parse RAISED at the fetch site;
# the caught exception is the ground, retryable) and `filed_but_unlabelable`
# (fetched fine, the fail-loud fiscal derivation rejected the filing —
# quarantined at FILING granularity, the run continues). Fixtures: the
# machine-captured AAPL completeness set; both failure premises are
# counterfactual staged rows per the T14/T16/T18 convention (a parsed copy
# mutated in-test — a raising `.xbrl()` / a stripped dei calendar row; the
# fixture file untouched).
# ---------------------------------------------------------------------------

def test_coverage_observed_failure_states(sec_client):
    """(a) An index-present 10-Q whose download/XBRL parse raises reports
    attempted-fetch-failed — retryable, grounded by the in-hand exception
    (class + message recorded in the ONE DQC schema) — never 'unclassified'
    and never silently covered, and the run continues. (b) A multi-year
    build with exactly ONE dei-unreadable filing completes: the other
    filings' series emit normally, the bad filing's facts are excluded from
    fiscal-labeled output, and coverage reports that quarter
    filed-but-unlabelable (DQC schema) — one bad filing never aborts the
    whole run (spec: 'Coverage honesty extends to per-filing
    completeness')."""
    fixture = _load_aapl_quarterly_fixture()

    # ------------------------------------------------------------------
    # (a) attempted-fetch-failed: FY2025's Q3 is IN the index but its
    # fetch raises (staged: the filing's `.xbrl()` raises ConnectionError).
    # ------------------------------------------------------------------
    filings = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in ("fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2025_q3")
    ]
    q3_accession = fixture["fy2025_q3"]["accession"]

    def _raise_fetch(*args, **kwargs):
        raise ConnectionError("simulated: connection reset during SEC download")

    filings[3].xbrl = _raise_fetch
    _aapl_company_stub(sec_client, filings)

    pack = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2025,
        as_of=datetime.date(2026, 1, 1),
    )
    assert "error" not in pack, (
        f"one fetch failure must never abort the whole run -- {pack}"
    )
    got = {f["accession"] for f in pack["facts"]}
    assert fixture["fy2025_q1"]["accession"] in got, (
        f"the other filings' facts must still emit -- {got}"
    )
    assert fixture["fy2025_q2"]["accession"] in got, got
    assert q3_accession not in got, (
        f"the failed filing has no fetched facts to emit -- {got}"
    )

    # Coverage-level flag: ONE DQC schema, grounded by the caught exception.
    failures = pack["coverage"]["fetch_failures"]
    assert isinstance(failures, list) and len(failures) == 1, pack["coverage"]
    flag = failures[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, (
        f"fetch-failure flags follow the ONE DQC schema -- {flag}"
    )
    assert flag["type"] == "attempted_fetch_failed", flag
    assert flag["accessions"] == [q3_accession], flag
    assert "ConnectionError" in flag["reason"], (
        f"the flag must record the in-hand exception CLASS -- {flag}"
    )
    assert "connection reset during SEC download" in flag["reason"], (
        f"the flag must record the in-hand exception MESSAGE -- {flag}"
    )
    assert "retryable" in flag["reason"], (
        f"attempted-fetch-failed is the one RETRYABLE state -- {flag}"
    )

    # The quarter itself reports attempted_fetch_failed — never
    # 'unclassified' (T18's no-positive-evidence state) and never silently
    # counted covered on index presence alone.
    fy2025 = next(
        r for r in pack["coverage"]["quarterly_coverage"]
        if r["fiscal_year"] == 2025
    )
    assert all(p.get("accession") != q3_accession for p in fy2025["present"]), (
        f"a fetch-failed filing must never be silently covered -- {fy2025}"
    )
    q3_entry = next(m for m in fy2025["missing"] if m["filing"] == "Q3")
    assert q3_entry["reason"] == "attempted_fetch_failed", (
        "an in-hand fetch failure is POSITIVE evidence and must classify "
        f"attempted_fetch_failed, never 'unclassified' -- {q3_entry}"
    )
    assert q3_entry["accession"] == q3_accession, q3_entry
    assert "ConnectionError" in q3_entry["detail"], q3_entry
    assert fy2025["status"] == "partial", fy2025
    assert fy2025["present_count"] == 3, fy2025
    # Always-list convention (mirrors unclassifiable_periods): ran, none found.
    assert pack["coverage"]["unlabelable_filings"] == [], pack["coverage"]

    # ------------------------------------------------------------------
    # (b) filed-but-unlabelable: a multi-year build where exactly ONE
    # filing's dei fiscal calendar is unreadable (staged: the FY2026-Q1
    # copy's dei row stripped). FAILS TODAY: UnreadableFiscalCalendarError
    # propagates out of extract and aborts the whole run.
    # ------------------------------------------------------------------
    filings_b = [
        _filing_from_quarterly_fixture_record(fixture[key])
        for key in (
            "fy2025_10k", "fy2025_q1", "fy2025_q2", "fy2025_q3",
            "fy2026_q1", "fy2026_q2",
        )
    ]
    bad_accession = fixture["fy2026_q1"]["accession"]
    bad_xb = filings_b[4].xbrl()
    staged_rows = [
        r for r in bad_xb.facts.to_dataframe.return_value.to_dict.return_value
        if r.get("concept") != "dei:CurrentFiscalYearEndDate"
    ]
    bad_xb.facts.to_dataframe.return_value.to_dict.return_value = staged_rows
    _aapl_company_stub(sec_client, filings_b)

    pack_b = sec_client.extract_dimensional_revenue(
        "AAPL", form="10-Q", since_year=2025, until_year=2026,
        as_of=datetime.date(2026, 6, 1),
    )
    assert "error" not in pack_b, (
        f"ONE unlabelable filing must never abort the multi-year run -- {pack_b}"
    )
    got_b = {f["accession"] for f in pack_b["facts"]}
    for key in ("fy2025_q1", "fy2025_q2", "fy2025_q3", "fy2026_q2"):
        assert fixture[key]["accession"] in got_b, (
            f"the OTHER filings' series must emit normally ({key}) -- {got_b}"
        )
    assert bad_accession not in got_b, (
        "the quarantined filing's facts are EXCLUDED from fiscal-labeled "
        f"output (never calendar-fallback-labeled) -- {got_b}"
    )

    # The quarantine surfaces loudly at coverage level — the fail-loud
    # property moves here, it never vanishes into silence.
    quarantined = pack_b["coverage"]["unlabelable_filings"]
    assert isinstance(quarantined, list) and len(quarantined) == 1, (
        pack_b["coverage"]
    )
    qflag = quarantined[0]
    assert set(qflag) == {"type", "old", "new", "accessions", "reason"}, (
        f"quarantine flags follow the ONE DQC schema -- {qflag}"
    )
    assert qflag["type"] == "unreadable_fiscal_calendar", qflag
    assert qflag["accessions"] == [bad_accession], qflag
    assert qflag["reason"], qflag

    # The quarter reports filed-but-unlabelable — filed (index+fetch fine),
    # but its data is honestly absent from labeled output.
    fy2026 = next(
        r for r in pack_b["coverage"]["quarterly_coverage"]
        if r["fiscal_year"] == 2026
    )
    assert all(p.get("accession") != bad_accession for p in fy2026["present"]), (
        f"a quarantined filing must never count as covered -- {fy2026}"
    )
    q1_entry = next(m for m in fy2026["missing"] if m["filing"] == "Q1")
    assert q1_entry["reason"] == "filed_but_unlabelable", (
        "the quarter's state is filed_but_unlabelable — positive in-hand "
        f"evidence, never an inferred index-absence state -- {q1_entry}"
    )
    assert q1_entry["accession"] == bad_accession, q1_entry
    assert pack_b["coverage"]["fetch_failures"] == [], pack_b["coverage"]


# ---------------------------------------------------------------------------
# Task 17 (RE-SCOPED 2026-07-18) — no-cache-aliasing regression
# ---------------------------------------------------------------------------

_T17_POISON_MARKER = "T17-SENTINEL-POISON-A-CACHE-VALUE-THAT-MUST-NEVER-SURFACE"


def _t17_poisoned_payload(key_label: str) -> dict:
    """A pre-rebuild-era payload for cache key `key_label`: an old-shape
    labeled-fact dict (calendar-valued `fiscal_year`, no parallel
    calendar_year/calendar_quarter/fiscal_quarter/derivation_basis fields —
    the exact pre-revision shape spec constraint (d) describes) plus a
    unique sentinel accession/value that could never come from the real
    NVDA range fixture, so any accidental read is unmistakable."""
    return {
        "cached_under": key_label,
        "facts": [
            {
                "concept": "us-gaap:Revenues",
                "value": -999999999.0,
                "period_end": "1999-12-31",
                "accession": f"{_T17_POISON_MARKER}-{key_label}",
                "fiscal_year": 1999,  # OLD SHAPE: calendar-valued, no pair
            }
        ],
    }


def test_cache_schema_version_no_alias(sec_client, monkeypatch, tmp_path):
    """T17 re-scope (spec constraint (d) / docs/loom/memory/cache-key-
    collision-across-migration.md): implementation recon found the
    labeled-fact layer is UNCACHED — `extract_dimensional_revenue` calls
    `filing.xbrl()` directly and never consults `cache_util`. The
    obligation is therefore negative: poison EVERY existing raw-source
    cache key family (tickers / facts_{cik} / concept_{cik}_{concept} /
    submissions_{cik} / narrative_sections_{accession}) with a
    pre-rebuild-era old-shape payload and prove none of it reaches the
    parallel-label output. This also pins the future-cache constraint
    documented on the function's docstring."""
    monkeypatch.setenv("INVESTING_TOOLKIT_CACHE", str(tmp_path))
    cache_util = sec_client.cache_util

    nvda_cik = 1045810
    poisoned_keys = {
        "tickers": cache_util.cache_path("sec_edgar", "tickers"),
        "facts_cik": cache_util.cache_path("sec_edgar", f"facts_{nvda_cik:010d}"),
        "concept_cik": cache_util.cache_path(
            "sec_edgar", f"concept_{nvda_cik:010d}_us-gaap:Revenues"
        ),
        "submissions_cik": cache_util.cache_path(
            "sec_edgar", f"submissions_{nvda_cik:010d}"
        ),
        "narrative_sections": cache_util.cache_path(
            "sec_edgar", "narrative_sections_0001045810-25-000101"
        ),
    }
    for label, path in poisoned_keys.items():
        cache_util.save_cache(path, _t17_poisoned_payload(label))
        assert path.exists(), f"poison for {label!r} must actually land on disk"

    fixture = _nvda_range_company(sec_client)
    pack = sec_client.extract_dimensional_revenue(
        "NVDA", form="10-Q", since_year=2026, until_year=2026,
        as_of=datetime.date(2026, 7, 18),
    )
    assert "error" not in pack, pack
    assert pack["facts"], "the real fixture facts must still be emitted"

    required = {"calendar_year", "calendar_quarter", "fiscal_year", "fiscal_quarter"}
    for fact in pack["facts"]:
        assert required <= fact.keys(), (
            f"every emitted fact must carry the parallel labels, freshly "
            f"derived — a poisoned cache must never short-circuit this -- {fact}"
        )
        assert _T17_POISON_MARKER not in str(fact.get("accession", "")), fact
        assert fact.get("fiscal_year") != 1999, fact
        assert fact.get("value") != -999999999.0, fact

    real_accessions = {r["accession"] for r in fixture["filings"]}
    got_accessions = {f["accession"] for f in pack["facts"]}
    assert got_accessions == real_accessions, (
        f"only the real fixture-backed accessions may appear -- got "
        f"{got_accessions}"
    )

    serialized = json.dumps(pack, default=str)
    assert _T17_POISON_MARKER not in serialized, (
        "no planted sentinel value may appear anywhere in the emitted pack "
        "-- the labeled-fact layer must stay uncached (spec constraint (d))"
    )

    doc = sec_client.extract_dimensional_revenue.__doc__ or ""
    assert "schema-versioned distinct key" in doc, (
        "the function's docstring must document the future-cache "
        "constraint: any cache of this labeled payload MUST use a "
        "schema-versioned distinct key (spec constraint (d))"
    )
