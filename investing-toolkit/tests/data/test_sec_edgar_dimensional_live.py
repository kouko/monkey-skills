"""test_sec_edgar_dimensional_live.py — live-API anchor for
`sec_edgar_client.extract_dimensional_revenue` (Task 5,
docs/loom/plans/2026-07-14-operational-kpi-companyfacts-pilot.md; fact
shape updated to the full-signature model by Task 4,
docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md).

Fetches AAPL's latest 10-K XBRL via real edgartools and asserts the
extractor's normalized full-signature dimensional-revenue fact-pack (the
shape tests/analysis/fixtures/xbrl_signature_factpack.json declares)
contains a real ProductOrService=IPhoneMember revenue fact — proving BOTH
the srt:* namespace path is reachable AND the full declared key set is
emitted. The 2018 tagging-regime shift moved Apple's product-line axis from
us-gaap:ProductOrServiceAxis to srt:ProductOrServiceAxis (the "Apple
false-negative lesson" the plan names) — a single-namespace filter would
silently drop this fact; `dimensions` collapses both namespaces to the same
axis-local-name key ("ProductOrService"), so this test no longer needs to
assert the raw axis string.

Marked @pytest.mark.network (registered in tests/data/conftest.py) so the
offline suite (`pytest -m "not network"`) stays green; `edgar` /
`sec_edgar_client` are imported inside the test body so offline collection
stays clean when edgartools is not installed. Run live:
  uv run --with pytest --with edgartools==5.42.0 --with requests \
    pytest investing-toolkit/tests/data/test_sec_edgar_dimensional_live.py \
    -m network
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

_FACT_PACK_KEYS = {
    "concept", "dimensions", "consolidation", "value",
    "period_end", "fiscal_year", "accession", "filed",
}


@pytest.mark.network
def test_extract_dimensional_revenue_aapl_live():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    pack = sec_edgar_client.extract_dimensional_revenue("AAPL")

    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "AAPL"
    facts = pack["facts"]
    assert isinstance(facts, list) and facts, "expected a non-empty facts list"

    for fact in facts:
        assert _FACT_PACK_KEYS <= set(fact), (
            f"fact missing a declared fact-pack key: {sorted(fact)}"
        )

    # The srt:* namespace path is reachable: Apple's post-2018 iPhone
    # product-line revenue is tagged srt:ProductOrServiceAxis /
    # aapl:IPhoneMember, NOT the pre-2018 us-gaap:ProductOrServiceAxis —
    # filtering a single namespace would silently drop this fact. `dimensions`
    # collapses both namespaces to the same axis-local-name key.
    iphone_facts = [
        f for f in facts
        if f["dimensions"].get("ProductOrService") == "IPhoneMember"
    ]
    assert iphone_facts, (
        "expected a real ProductOrService=IPhoneMember revenue fact; got "
        f"dimensions={[f['dimensions'] for f in facts]}"
    )
    assert any(f["value"] > 100e9 for f in iphone_facts), (
        f"expected an iPhone revenue value > 100e9: {iphone_facts}"
    )

    # fiscal_year must be DERIVED from period_end (the year the fiscal
    # period ENDS), never taken from edgartools' raw `fiscal_year` column —
    # that column is unreliable for prior-year comparatives: in AAPL's 2025
    # 10-K, the iPhone fact with period_end 2024-09-28 is column-labeled
    # fiscal_year=2025 but is really FY2024. A prior-year comparative fact
    # (period_end starting "2024") must be labeled fiscal_year == 2024.
    prior_year_iphone_facts = [
        f for f in iphone_facts
        if f["period_end"] and f["period_end"].startswith("2024")
    ]
    assert prior_year_iphone_facts, (
        "expected a prior-year (period_end starting '2024') iPhone "
        f"comparative fact; got period_ends="
        f"{sorted({f['period_end'] for f in iphone_facts})}"
    )
    assert all(f["fiscal_year"] == 2024 for f in prior_year_iphone_facts), (
        "fiscal_year must derive from period_end, not edgartools' raw "
        f"fiscal_year column: {prior_year_iphone_facts}"
    )


@pytest.mark.network
def test_extract_dimensional_revenue_tsla_skips_amendment_live():
    """TSLA's `company.get_filings(form="10-K").latest()` returns a
    "10-K/A" amendment (edgartools' form filter is a loose/prefix match,
    live-verified 2026-07-15: TSLA's most recent filing by date is a
    10-K/A, which carries 0 dimensional-revenue facts) — Task 6,
    docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md.
    `extract_dimensional_revenue` must select the latest filing whose
    form is EXACTLY "10-K" (never an amendment), so the amendment never
    shadows the real annual report.
    """
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    pack = sec_edgar_client.extract_dimensional_revenue("TSLA")

    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "TSLA"
    facts = pack["facts"]
    assert isinstance(facts, list) and facts, (
        "expected a non-empty facts list from the exact 10-K (not the "
        "0-dimensional 10-K/A amendment)"
    )

    for fact in facts:
        assert _FACT_PACK_KEYS <= set(fact), (
            f"fact missing a declared fact-pack key: {sorted(fact)}"
        )

    accessions = {f["accession"] for f in facts}
    assert len(accessions) == 1, (
        f"expected all facts from a single filing: {accessions}"
    )
    (accession,) = accessions

    # Directly resolve the filing edgartools selected for this accession and
    # assert its form is exactly "10-K", never "10-K/A".
    import edgar

    edgar.set_identity(sec_edgar_client.USER_AGENT)
    company = edgar.Company("TSLA")
    matching_filings = [
        f for f in company.get_filings(form="10-K") if f.accession_no == accession
    ]
    assert matching_filings, f"could not resolve filing for accession {accession}"
    assert matching_filings[0].form == "10-K", (
        f"extract_dimensional_revenue selected a non-exact-10-K filing: "
        f"{matching_filings[0].form!r} (accession {accession})"
    )


@pytest.mark.network
def test_extract_dimensional_revenue_multifiling_live_aapl():
    """Live shape-anchor for the `since_year` multi-filing path (Task 6,
    docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md). Guards the
    REAL edgartools multi-filing shape at the boundary offline fixtures can
    drift from (loom-memory `fixtures-mirror-producer-shape` — a live anchor
    caught edgartools grounding wrong 3x historically): concatenating facts
    from every in-range exact-form 10-K must actually span more than one
    filing's worth of fiscal years, across more than one distinct accession,
    each fact still carrying a non-null dimensional signature.
    """
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    pack = sec_edgar_client.extract_dimensional_revenue("AAPL", since_year=2015)

    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "AAPL"
    facts = pack["facts"]
    assert isinstance(facts, list) and facts, "expected a non-empty facts list"

    for fact in facts:
        assert _FACT_PACK_KEYS <= set(fact), (
            f"fact missing a declared fact-pack key: {sorted(fact)}"
        )
        assert fact["dimensions"], (
            f"expected a non-null dimensional signature: {fact}"
        )

    accessions = {f["accession"] for f in facts}
    assert len(accessions) > 1, (
        f"expected facts drawn from more than one filing (accession): {accessions}"
    )

    fiscal_years = {f["fiscal_year"] for f in facts}
    assert len(fiscal_years) > 3, (
        f"expected facts spanning more than 3 distinct fiscal years: "
        f"{sorted(fiscal_years)}"
    )


@pytest.mark.network
def test_quarterly_dual_duration_live():
    """Live shape-anchor for the T13 parallel-label rebuild (Task 12,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md), grounding the
    fixtures-mirror-producer-shape practice (docs/loom/memory/fixtures-
    mirror-producer-shape.md — a live anchor caught wrong edgartools/dei
    grounding 3x historically on a prior branch).

    Fetches MSFT's latest 10-Q (form="10-Q", no range — the default
    latest-only path) via the REAL `extract_dimensional_revenue` path and
    asserts the REAL producer shape T13-T19 assume:
    (a) at least one dimensional-revenue signature+period_end carries BOTH
        a duration_months=3 (single-quarter) and a duration_months=9
        (YTD) fact — a Q3 10-Q tags both the quarter and the
        year-to-date for the same line item;
    (b) the pack's `fiscal_calendars` entry for that filing's accession
        carries all three dei cover tags (fiscal_period_focus,
        fiscal_year_end, fiscal_year_focus), each non-null;
    (c) every emitted fact carries the parallel label group —
        calendar_year, calendar_quarter, fiscal_year, fiscal_quarter.
    """
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    pack = sec_edgar_client.extract_dimensional_revenue("MSFT", form="10-Q")

    assert "error" not in pack, f"extract_dimensional_revenue failed: {pack}"
    assert pack["company"] == "MSFT"
    facts = pack["facts"]
    assert isinstance(facts, list) and facts, "expected a non-empty facts list"

    # (c) every emitted fact carries the parallel label group.
    _label_keys = {"calendar_year", "calendar_quarter", "fiscal_year", "fiscal_quarter"}
    for fact in facts:
        assert _label_keys <= set(fact), (
            f"fact missing a parallel label key: {sorted(fact)}"
        )

    # (a) at least one signature+period_end carries both a 3-month and a
    # 9-month duration fact (a Q3 10-Q tags the quarter AND the YTD).
    by_signature_period: dict[tuple, set[int]] = {}
    for fact in facts:
        duration = fact.get("duration_months")
        if duration is None:
            continue
        signature = (
            fact["concept"],
            tuple(sorted(fact["dimensions"].items())),
            fact["consolidation"],
            fact["period_end"],
        )
        by_signature_period.setdefault(signature, set()).add(duration)

    dual_duration_signatures = [
        sig for sig, durations in by_signature_period.items()
        if {3, 9} <= durations
    ]
    assert dual_duration_signatures, (
        "expected at least one signature+period_end carrying both a "
        "duration_months=3 and a duration_months=9 fact; got durations="
        f"{ {sig: sorted(d) for sig, d in by_signature_period.items()} }"
    )

    # (b) all three dei cover tags present (non-null) for the accession(s)
    # backing the dual-duration signature.
    example_signature = dual_duration_signatures[0]
    example_accessions = {
        f["accession"] for f in facts
        if (
            f["concept"], tuple(sorted(f["dimensions"].items())),
            f["consolidation"], f["period_end"],
        ) == example_signature
    }
    assert example_accessions, "could not resolve an accession for the dual-duration fact"
    fiscal_calendars = pack["fiscal_calendars"]
    _dei_keys = {"fiscal_period_focus", "fiscal_year_end", "fiscal_year_focus"}
    for accession in example_accessions:
        calendar = fiscal_calendars.get(accession)
        assert calendar is not None, (
            f"expected a fiscal_calendars entry for accession {accession!r}: "
            f"{sorted(fiscal_calendars)}"
        )
        assert _dei_keys <= set(calendar), (
            f"fiscal_calendars entry missing a dei cover tag key: {sorted(calendar)}"
        )
        for key in _dei_keys:
            assert calendar[key] is not None, (
                f"dei cover tag {key!r} is null for accession {accession!r}: {calendar}"
            )
