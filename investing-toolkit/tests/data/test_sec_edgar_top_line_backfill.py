"""test_sec_edgar_top_line_backfill.py — RED/GREEN tests for
`build_top_line_backfill` (Task 3, docs/loom/plans/2026-07-25-company-
total-revenue.md): Lane A, the annual-only companyconcept backfill.

Every row below is a COUNTERFACTUAL-WINDOW mutation of NVDA's REAL captured
Task-1 probe fact (`fixtures/topline_probe_2026-07-25.json`: concept
`us-gaap:Revenues`, value 215,938,000,000, accession
`0001045810-26-000021`, filed 2026-02-25 per the plan's live-confirmed
§Notes) — never a hand-invented value. Only the `start`/`end` period
window is mutated per row, to hit specific classification boundaries
(annual vs quarterly span, New-Year-boundary tolerance); this is the SAME
"freshly-parsed COPY... ONLY the period window is mutated in-test"
convention `test_sec_edgar_dimensional.py::test_annual_out_of_tolerance_
unclassifiable` already uses in this repo, per repo memory
`hand-authored-fixture-is-a-fabrication-risk` (fabrication risk is about
inventing VALUES, not about constructing a boundary-condition date).

The two FY2024/FY2025 comparative period-end dates (2024-01-28,
2025-01-26) and the accession/filed pair are the exact values the plan's
§Notes records as LIVE-CONFIRMED 2026-07-25 (memory `fiscal-year-derive-
per-fact-against-filing-calendar` trap #2: every row from NVDA's FY2026
filing is stamped `fy=2026`, including those two comparatives). The
New-Year-boundary row's end date (2025-01-03) is the plan's own worked
example (Amendment note 5(b)).

Split into focused, independently-failing tests (mirrors
`test_sec_edgar_top_line.py`'s post-review split — a single bundled test
gives zero signal on which behavior broke).

Run offline (no network marker; part of the default `not network` suite):
  PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' \
    pytest investing-toolkit/tests/ -m "not network" -q --tb=short
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
ANALYSIS_KPI_SCRIPTS = ROOT / "skills" / "analysis-kpi" / "scripts"


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in
    sys.modules — same convention as test_sec_edgar_top_line.py's
    `sec_client` fixture. `build_top_line_backfill` never touches edgar
    (companyconcept is a plain REST fetch via `fetch_facts`), but the
    module-level `import requests as _requests` still needs a stub
    offline."""
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import importlib
    edgar_stub = mock.MagicMock(name="edgar")
    requests_stub = mock.MagicMock(name="requests")
    saved_edgar = sys.modules.get("edgar")
    saved_requests = sys.modules.get("requests")
    saved_client = sys.modules.get("sec_edgar_client")
    sys.modules["edgar"] = edgar_stub
    sys.modules["requests"] = requests_stub
    sys.modules.pop("sec_edgar_client", None)
    module = importlib.import_module("sec_edgar_client")
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


@pytest.fixture
def kpi_xbrl():
    if str(ANALYSIS_KPI_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(ANALYSIS_KPI_SCRIPTS))
    import importlib
    sys.modules.pop("kpi_xbrl", None)
    return importlib.import_module("kpi_xbrl")


# --- Real captured Task-1 probe values (topline_probe_2026-07-25.json,
# NVDA entry) -- the ONLY dollar value and accession/filed pair used below.
_NVDA_CIK = 1045810
_NVDA_CONCEPT = "Revenues"
_NVDA_ACCN = "0001045810-26-000021"
_NVDA_FILED = "2026-02-25"
_NVDA_VALUE = 215938000000.0
_NVDA_FORM = "10-K"

# A SYNTHETIC accession, deliberately not a real one: the second-filing
# tests below need a row whose carrying filing is DISTINCT from
# `_NVDA_ACCN` (one accession is one filing with one form, so a non-10-K
# row cannot honestly reuse NVDA's real 10-K accession). It is an
# IDENTIFIER, never financial data -- the fabrication risk repo memory
# `hand-authored-fixture-is-a-fabrication-risk` guards is inventing
# VALUES, and no value here is invented: every row still carries the real
# captured `_NVDA_VALUE`. The `-25-000999` serial is outside NVDA's real
# filing series so it can never be mistaken for a citable accession.
_SYNTHETIC_OTHER_ACCN = "0001045810-25-000999"


def _row(
    start: str,
    end: str,
    *,
    fy: int = 2026,
    fp: str = "FY",
    form: str | None = _NVDA_FORM,
    accn: str = _NVDA_ACCN,
) -> dict:
    """One raw companyconcept `units.USD[]` row (`summarize_concept`'s
    input shape) -- a counterfactual-window copy of NVDA's real captured
    fact: only `start`/`end` vary per call; `val`/`accn`/`form`/`filed` are
    the SAME real captured values every time. `fy`/`fp` are stamped 2026/FY
    on every row by default -- the live-confirmed trap (every row from
    NVDA's FY2026 filing carries the FILING's own fy/fp, not the fact's
    own) -- `build_top_line_backfill` must never read either.

    `form` is overridable (and `accn` with it, since one accession is one
    filing with one form) for the source-form honesty tests below: a
    non-10-K carrier is a real companyconcept shape, not a hypothetical --
    `summarize_concept` passes `form` through verbatim from SEC's own row,
    which carries 20-F / 40-F / 8-K / 10-K/A alongside 10-K. `form=None`
    models the absent-field case the same way `_extract_dei_calendar`
    models an absent dei tag."""
    return {
        "start": start, "end": end, "val": _NVDA_VALUE, "accn": accn,
        "form": form, "fy": fy, "fp": fp, "filed": _NVDA_FILED,
    }


def _raw_companyconcept_payload(rows: list[dict]) -> dict:
    return {"units": {"USD": rows}}


def _stub_fetch(sec_client, *, winning_concept: str, rows: list[dict]):
    """Patch `resolve_cik` + `fetch_facts` so `build_top_line_backfill`
    sees `rows` under `winning_concept` and an error (no data) for every
    OTHER allowlist concept -- mirrors `test_sec_xval.py`'s
    `mock.patch.object(sec_client, "fetch_facts", ...)` convention, with a
    `side_effect` keyed on the `concept` argument since the real function
    is called once per allowlist concept."""

    def _fetch(cik, concept):
        assert cik == _NVDA_CIK
        if concept == winning_concept:
            return {"data": _raw_companyconcept_payload(rows)}
        return {"error": f"no data for {concept}"}

    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _NVDA_CIK, "ticker": "NVDA"},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts", side_effect=_fetch,
    )
    return resolve_patch, fetch_patch


# --- Real captured Task-1 probe values for the TWO-CONCEPT filers
# (`fixtures/topline_probe_2026-07-25.json`), the only place in this repo
# where one period is covered by two allowlist concepts at once -- which is
# precisely the per-period tie the Task-2 merge has to resolve.
#
# COST reports `Revenues` and `RevenueFromContractWithCustomerExcluding
# AssessedTax` at the SAME value for the same period (the AGREEMENT case).
# WMT reports them at DIFFERENT values -- 713,163M is its own "Total
# revenues" line, 706,413M excludes membership/other (the CONFLICT case,
# already named in `_TOP_LINE_REVENUE_CONCEPTS`'s own comment).
#
# CIKs are the accession prefixes (Costco 909832, Walmart 104169). Windows
# other than each filer's real captured one are COUNTERFACTUAL-WINDOW
# mutations, per this module's stated convention.
_COST_CIK = 909832
_COST_ACCN = "0000909832-25-000101"
_COST_VALUE = 275235000000.0

_WMT_CIK = 104169
_WMT_ACCN = "0000104169-26-000055"
_WMT_REVENUES_VALUE = 713163000000.0
_WMT_RFCC_VALUE = 706413000000.0

# `filed` is NOT recorded in the probe fixture, and no assertion below reads
# it. These rows therefore carry the probe's own CAPTURE date as an openly
# declared PLACEHOLDER -- never passed off as the filing's real acceptance
# date. (The fabrication risk repo memory `hand-authored-fixture-is-a-
# fabrication-risk` guards is presenting an INVENTED value as a captured
# one; every dollar figure above is captured, and this field is declared.)
_PROBE_CAPTURE_DATE = "2026-07-25"


def _two_concept_row(start: str, end: str, *, accn: str, value: float) -> dict:
    """One raw companyconcept row for the two-concept filers above -- same
    `summarize_concept` input shape as `_row`, with the value and carrying
    accession supplied per filer instead of NVDA's."""
    return {
        "start": start, "end": end, "val": value, "accn": accn,
        "form": _NVDA_FORM, "fy": 2026, "fp": "FY",
        "filed": _PROBE_CAPTURE_DATE,
    }


def _cost_row(start: str, end: str) -> dict:
    return _two_concept_row(start, end, accn=_COST_ACCN, value=_COST_VALUE)


def _wmt_row(start: str, end: str, *, value: float) -> dict:
    return _two_concept_row(start, end, accn=_WMT_ACCN, value=value)


def _stub_fetch_by_concept(
    sec_client, rows_by_concept: dict[str, list[dict]], *, cik: int, ticker: str,
):
    """The multi-concept sibling of `_stub_fetch` (Task 2,
    docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md): each
    allowlist concept returns its OWN row list, so a filer that carries two
    concepts at once -- or one concept per era -- is representable. A
    concept absent from the mapping returns the same `{"error": ...}` slot
    `_stub_fetch` gives a concept with no history."""

    def _fetch(fetch_cik, concept):
        assert fetch_cik == cik
        rows = rows_by_concept.get(concept)
        if rows is None:
            return {"error": f"no data for {concept}"}
        return {"data": _raw_companyconcept_payload(rows)}

    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik", return_value={"cik": cik, "ticker": ticker},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts", side_effect=_fetch,
    )
    return resolve_patch, fetch_patch


def test_backfill_spans_a_mid_history_concept_switch(sec_client):
    """THE TRUNCATION FIX (Task 2). A filer whose EARLY years are tagged
    `Revenues` and whose LATER years are tagged
    `RevenueFromContractWithCustomerExcludingAssessedTax` -- the ASC-606
    tag switch -- must yield ONE CONTINUOUS annual series spanning both
    eras, each fact stamped with the concept its OWN period was reported
    under.

    The shipped 2.36.0 behaviour returns only the FIRST allowlist concept
    that has any rows and `break`s, so such a filer keeps only its
    pre-switch years: measured live 2026-07-26, MSFT returned 3 annual
    facts spanning 2008-06-30..2010-06-30 and AAPL 3 spanning
    2016-09-24..2018-09-29, while NVDA (never switched) returned 42
    spanning 2008..2026. 10 of the 47-filer corpus are silently short.

    Concept resolution is therefore PER PERIOD, not per company."""
    early_era = [
        _cost_row("2022-08-29", "2023-09-03"),
        _cost_row("2023-09-04", "2024-09-01"),
    ]
    late_era = [
        _cost_row("2024-09-02", "2025-08-31"),  # the real captured window
        _cost_row("2025-09-01", "2026-08-30"),
    ]
    resolve_patch, fetch_patch = _stub_fetch_by_concept(sec_client, {
        "Revenues": early_era,
        "RevenueFromContractWithCustomerExcludingAssessedTax": late_era,
    }, cik=_COST_CIK, ticker="COST")
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("COST")

    assert "error" not in pack, pack
    by_end = {f["period_end"]: f for f in pack["facts"]}
    assert set(by_end) == {
        "2023-09-03", "2024-09-01", "2025-08-31", "2026-08-30",
    }, (
        "a mid-history tag switch must not truncate the series at the "
        f"switch: got {sorted(by_end)}"
    )
    assert by_end["2023-09-03"]["concept"] == "us-gaap:Revenues"
    assert by_end["2024-09-01"]["concept"] == "us-gaap:Revenues"
    for period_end in ("2025-08-31", "2026-08-30"):
        assert by_end[period_end]["concept"] == (
            "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
        ), by_end[period_end]


def test_backfill_breaks_a_same_period_tie_by_allowlist_order_when_values_agree(
    sec_client,
):
    """COST's REAL captured double-tagging (probe fixture
    `topline_probe_2026-07-25.json`): for the SAME period it reports both
    `Revenues` and `RevenueFromContractWithCustomerExcludingAssessedTax` at
    the SAME value (275,235,000,000). The values agree, so the period is
    supplied by the ALLOWLIST-ORDER winner (`Revenues`, index 0) -- exactly
    one fact, no duplicate, and nothing skipped."""
    window = ("2024-09-02", "2025-08-31")
    resolve_patch, fetch_patch = _stub_fetch_by_concept(sec_client, {
        "Revenues": [_cost_row(*window)],
        "RevenueFromContractWithCustomerExcludingAssessedTax": [
            _cost_row(*window),
        ],
    }, cik=_COST_CIK, ticker="COST")
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("COST")

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 1, pack["facts"]
    assert pack["facts"][0]["concept"] == "us-gaap:Revenues", pack["facts"]
    assert pack["facts"][0]["value"] == _COST_VALUE
    assert pack["coverage"]["skipped_rows"] == [], pack["coverage"]


def test_backfill_skips_a_period_whose_two_concepts_disagree_on_value(sec_client):
    """WMT's REAL captured conflict (same probe fixture): for the SAME
    period it reports `Revenues` = 713,163,000,000 (its own "Total
    revenues" line) and `RevenueFromContractWithCustomerExcludingAssessedTax`
    = 706,413,000,000 (which excludes membership/other). Two allowlist tags,
    one period, DIFFERENT totals.

    Lane A never guesses which tag is right: that period is SKIPPED with the
    named `top_line_concept_value_conflict` reason, and the filer's other
    periods are unaffected. (`select_top_line_concept`'s allowlist order is
    a tie-break for AGREEING values, never a licence to pick a number.)"""
    conflicted = ("2025-02-01", "2026-01-31")
    clean = ("2024-02-01", "2025-01-31")
    resolve_patch, fetch_patch = _stub_fetch_by_concept(sec_client, {
        "Revenues": [
            _wmt_row(*conflicted, value=_WMT_REVENUES_VALUE),
            _wmt_row(*clean, value=_WMT_REVENUES_VALUE),
        ],
        "RevenueFromContractWithCustomerExcludingAssessedTax": [
            _wmt_row(*conflicted, value=_WMT_RFCC_VALUE),
        ],
    }, cik=_WMT_CIK, ticker="WMT")
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("WMT")

    assert "error" not in pack, pack
    assert {f["period_end"] for f in pack["facts"]} == {"2025-01-31"}, (
        "a period where two allowlist concepts disagree must never be "
        f"emitted under either tag: {pack['facts']}"
    )

    skipped = pack["coverage"]["skipped_rows"]
    flags = [
        f for f in skipped if f["type"] == "top_line_concept_value_conflict"
    ]
    assert len(flags) == 1, skipped
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_WMT_ACCN], flag
    assert "2026-01-31" in flag["reason"], flag
    for value in (_WMT_REVENUES_VALUE, _WMT_RFCC_VALUE):
        assert str(value) in flag["reason"], flag


def test_backfill_keeps_annual_rows_with_period_derived_fiscal_year(sec_client):
    """Annual rows (12-month start->end span) survive; each carries
    `fiscal_year` from its OWN `end` year (never the row's `fy`, which is
    stamped 2026 -- the filing's focus -- on every row here), plus
    `fiscal_quarter == "FY"` and a `duration_months` of 12."""
    rows = [
        _row("2025-01-27", "2026-01-25"),  # real NVDA FY2026 window
        _row("2024-01-29", "2025-01-26"),  # live-confirmed FY2025 comparative
    ]
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=rows,
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    ends = {f["period_end"]: f for f in pack["facts"]}
    assert set(ends) == {"2026-01-25", "2025-01-26"}, pack["facts"]
    assert ends["2026-01-25"]["fiscal_year"] == 2026, ends["2026-01-25"]
    assert ends["2025-01-26"]["fiscal_year"] == 2025, ends["2025-01-26"]
    for fact in ends.values():
        assert fact["fiscal_quarter"] == "FY", fact
        assert fact["duration_months"] == 12, fact
        assert fact["dimensions"] == {}, fact
        assert fact["period_start"] and fact["accession"] == _NVDA_ACCN
        assert fact["filed"] == _NVDA_FILED
    # Both lanes feed the ONE `total_revenue` series (kickoff correction,
    # round 2): calendar_year/calendar_quarter must be present here too,
    # computed with the EXACT SAME expression `_build_dimensional_revenue_
    # fact` uses (sec_edgar_client.py:3216-3217) -- never re-derived --
    # so a future consumer never sees inconsistent field presence across
    # one durable series depending on which lane wrote a given fiscal year.
    assert ends["2026-01-25"]["calendar_year"] == 2026, ends["2026-01-25"]
    assert ends["2026-01-25"]["calendar_quarter"] == "Q1", ends["2026-01-25"]
    assert ends["2025-01-26"]["calendar_year"] == 2025, ends["2025-01-26"]
    assert ends["2025-01-26"]["calendar_quarter"] == "Q1", ends["2025-01-26"]


def test_backfill_ignores_fy_field_when_it_disagrees_with_period_end(sec_client):
    """The FY2024 comparative (live-confirmed period_end 2024-01-28) is
    stamped `fy=2026` on the row (the filing's OWN focus, per the trap) --
    `fiscal_year` must still derive to 2024 from the row's own `end`,
    proving `fy` is never read."""
    rows = [_row("2023-01-30", "2024-01-28", fy=2026, fp="FY")]
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=rows,
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 1, pack["facts"]
    fact = pack["facts"][0]
    assert fact["period_end"] == "2024-01-28"
    assert fact["fiscal_year"] == 2024, (
        "fiscal_year must derive from period_end (2024), never the row's "
        f"stamped fy=2026: got {fact['fiscal_year']!r}"
    )


def test_backfill_skips_quarterly_row_with_named_coverage_reason(sec_client):
    """A quarterly row (3-month span, still tagged `fp: FY` -- the SAME
    disaggregated-quarterly-under-FY shape `summarize_concept`'s own
    docstring documents) is excluded from `facts` and recorded under
    `coverage` with a named, non-guessed reason."""
    annual = _row("2025-01-27", "2026-01-25")
    quarterly = _row("2025-10-27", "2026-01-25", fy=2026, fp="FY")
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=[annual, quarterly],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 1, pack["facts"]
    assert pack["facts"][0]["duration_months"] == 12

    skipped = pack["coverage"]["skipped_rows"]
    quarterly_flags = [f for f in skipped if f["type"] == "non_annual_row_skipped"]
    assert len(quarterly_flags) == 1, skipped
    flag = quarterly_flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_NVDA_ACCN]
    assert "2026-01-25" in flag["reason"]


def test_backfill_excludes_new_year_boundary_row_with_named_reason(sec_client):
    """An annual (12-month) row whose `end` has CROSSED INTO January --
    within `FISCAL_BOUNDARY_TOLERANCE_DAYS` AFTER Jan 1 (the plan's own
    worked example, 2025-01-03) -- is EXCLUDED, never labelled by the
    period-end-year rule, because Lane A has no dei calendar to
    disambiguate a 52/53-week filer whose year-end crosses New Year; the
    exclusion is recorded under `coverage` by name.

    THE HAZARD IS ONE-SIDED, and that asymmetry is a FACT about the two
    lanes' rules, not a tolerance to be applied symmetrically. Lane B's
    `_derive_fiscal_label` walks to the first nominal fiscal-year end
    at-or-after `period_end`, so a January period end resolves to the
    PRECEDING calendar year (2025-01-03 -> FY2024) while Lane A's
    period-end-year rule answers 2025 -- they diverge, and only Lane B
    can settle it. On the before-New-Year side both rules answer the
    period end's own calendar year (see
    `test_backfill_keeps_december_year_end_row_both_lanes_label_alike`),
    so there is nothing to disambiguate and a skip there would cost the
    whole lane for every December-FYE filer."""
    near_new_year = _row("2024-01-05", "2025-01-03")
    normal_annual = _row("2025-01-27", "2026-01-25")
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT,
        rows=[normal_annual, near_new_year],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    kept_ends = {f["period_end"] for f in pack["facts"]}
    assert kept_ends == {"2026-01-25"}, pack["facts"]

    skipped = pack["coverage"]["skipped_rows"]
    boundary_flags = [f for f in skipped if f["type"] == "new_year_boundary_ambiguous"]
    assert len(boundary_flags) == 1, skipped
    flag = boundary_flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert "2025-01-03" in flag["reason"]


def test_backfill_keeps_december_year_end_row_both_lanes_label_alike(sec_client):
    """The OTHER side of Jan 1, which the guard must NOT fire on: a
    December year-end (here 2024-12-28, 4 days BEFORE Jan 1 and so inside
    `FISCAL_BOUNDARY_TOLERANCE_DAYS` of it) is KEPT and labelled by the
    period-end-year rule.

    WHY THIS IS THE CORRECT BEHAVIOUR, not a loosened guard. Lane B's
    `_derive_fiscal_label` walks to the first nominal fiscal-year end
    at-or-after `period_end`; for a December FYE that is the SAME calendar
    year the period ends in, so Lane B answers 2024 and Lane A answers
    2024 -- the divergence the skip exists to prevent cannot arise here.
    Skipping it anyway silently drops the ENTIRE Lane A backfill of every
    December-fiscal-year-end filer (JPM, XOM, INTC, most of the US
    market), which is the regression this test pins."""
    december_year_end = _row("2024-01-02", "2024-12-28")
    normal_annual = _row("2025-01-27", "2026-01-25")
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT,
        rows=[normal_annual, december_year_end],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    kept = {f["period_end"]: f for f in pack["facts"]}
    assert set(kept) == {"2026-01-25", "2024-12-28"}, pack["facts"]
    assert kept["2024-12-28"]["fiscal_year"] == 2024, kept["2024-12-28"]
    assert kept["2024-12-28"]["fiscal_quarter"] == "FY", kept["2024-12-28"]

    skipped = pack["coverage"]["skipped_rows"]
    assert [f for f in skipped if f["type"] == "new_year_boundary_ambiguous"] == [], (
        "a December year-end is not the New-Year-crossing hazard: both "
        f"lanes label it by the period end's own year; got {skipped}"
    )


def test_backfill_picks_first_allowlist_concept_with_data(sec_client):
    """`Revenues` (index 0) has no data for this (synthetic) filer but
    `RevenueFromContractWithCustomerExcludingAssessedTax` (index 2) does --
    the backfill must pick the first-present concept BY DATA AVAILABILITY,
    mirroring `select_top_line_concept`'s ordering.

    AMENDED BY TASK 2 (docs/loom/plans/2026-07-26-us-as-reported-statement-
    lane.md): this test used to also pin "never fetch concepts past the
    first hit". That short-circuit IS the shipped truncation defect -- a
    filer's post-switch years live under a concept the scan stopped before
    reaching, which cost 10 of the 47-filer corpus their later history. The
    `calls` assertion is therefore inverted rather than dropped: ALL FOUR
    allowlist concepts must be fetched, in order, so per-period resolution
    has every era's rows to resolve from. What this test still pins
    unchanged is the WINNER: index 2 supplies the period because it is the
    only concept with data for it."""
    rows = [_row("2025-01-27", "2026-01-25")]
    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _NVDA_CIK, "ticker": "NVDA"},
    )
    calls = []

    def _fetch(cik, concept):
        calls.append(concept)
        if concept == "RevenueFromContractWithCustomerExcludingAssessedTax":
            return {"data": _raw_companyconcept_payload(rows)}
        return {"error": f"no data for {concept}"}

    fetch_patch = mock.patch.object(sec_client, "fetch_facts", side_effect=_fetch)
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert pack["facts"][0]["concept"] == (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax"
    ), pack["facts"]
    assert calls == list(sec_client._TOP_LINE_REVENUE_CONCEPTS), calls


def test_backfill_returns_loud_error_when_no_allowlist_concept_has_data(sec_client):
    """A ticker where NO allowlist concept returns rows yields a LOUD
    error slot -- never an empty-but-successful pack."""
    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _NVDA_CIK, "ticker": "NVDA"},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts",
        side_effect=lambda cik, concept: {"error": f"no data for {concept}"},
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" in pack, pack
    assert pack.get("error_class") == "top_line_backfill_failed", pack
    assert "facts" not in pack, "an error slot must never carry a facts list"


def test_backfill_carries_fiscal_calendars_so_facts_reach_the_store(
    sec_client, kpi_xbrl,
):
    """THE SEAM. `kpi_xbrl.facts_to_points` derives every point's
    `source_form` from the PACK's `fiscal_calendars[accession]
    ["fiscal_period_focus"]` (`_require_source_form`, kpi_xbrl.py:289-309)
    and RAISES when the pack carries none -- so a Lane A pack without that
    map reaches the store with ZERO points, however well-shaped its facts
    are. This drives the REAL consumer over the REAL producer's return
    value (no hand-built envelope, which is exactly what every prior test
    on both sides of this seam did) and pins the round-trip:
    10-K row -> `fiscal_period_focus: "FY"` -> `source_form: "10-K"`."""
    rows = [
        _row("2025-01-27", "2026-01-25"),
        _row("2024-01-29", "2025-01-26"),
    ]
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=rows,
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert pack["fiscal_calendars"] == {
        _NVDA_ACCN: {
            "fiscal_period_focus": "FY",
            # Neither dei tag is READABLE from a companyconcept row, so
            # neither is fabricated -- the same `None` `_extract_dei_calendar`
            # emits for a tag absent from a filing's records.
            "fiscal_year_end": None,
            "fiscal_year_focus": None,
        },
    }, pack["fiscal_calendars"]

    points = kpi_xbrl.facts_to_points(
        pack,
        "total_revenue",
        {"concept": f"us-gaap:{_NVDA_CONCEPT}", "dimensions": {},
         "consolidation": None},
        "NVDA",
        "xbrl-companyfacts",
    )
    assert len(points) == 2, points
    for point in points:
        assert point["source_form"] == "10-K", point


@pytest.mark.parametrize(
    "carrier_form",
    [
        # OBSERVED live on annual-span rows (fixtures/companyconcept_form_
        # domain_2026-07-25.json): TM and HMC, us-gaap-tagging foreign
        # private issuers, carry their whole top line on these two.
        pytest.param("20-F", id="observed-20-F"),
        pytest.param("20-F/A", id="observed-20-F-A"),
        # NOT observed in that sample -- pinned as plausible-but-unverified
        # carriers so a future widening of the allowlist has to argue with
        # a red test rather than with a comment.
        pytest.param("10-K/A", id="unobserved-10-K-A"),
        pytest.param("40-F", id="unobserved-40-F"),
        pytest.param("8-K", id="unobserved-8-K"),
    ],
)
def test_backfill_skips_row_whose_carrier_form_is_not_allowlisted(
    sec_client, carrier_form,
):
    """A 12-month row is EXCLUDED unless its carrier `form` is in
    `_TOP_LINE_ANNUAL_CARRIER_FORMS`, whatever the period arithmetic says.

    Why it cannot simply ride along: the store's form vocabulary reaches
    Lane A only through `_SOURCE_FORM_BY_FOCUS` (kpi_xbrl.py:231-233),
    whose ONLY annual key `"FY"` maps to the literal `"10-K"`. Declaring
    `fiscal_period_focus: "FY"` for any of these would stamp
    `source_form: "10-K"` on a point whose filing was not one.

    THE TWO CASES ARE NOT THE SAME, and `10-K/A` is the pointed one.
    A 20-F / 20-F/A / 40-F is a WRONG-REGIME carrier: a different annual
    report on a different disclosure regime, refused outright. A `10-K/A`
    is SAME-REGIME -- its dei `DocumentFiscalPeriodFocus` genuinely IS
    "FY", so only the literal form distinguishes it, and widening the
    allowlist to `{"10-K": "FY", "10-K/A": "FY"}` is exactly the change a
    maintainer would reach for. This test is what that change has to
    answer to.

    Excluding `10-K/A` is a deferral with a real cost, and the cost is
    VALUE STALENESS, not merely coverage: a 10-K/A is the canonical
    carrier of a RESTATED annual figure, so Lane A keeps the ORIGINAL
    number for an amended year and never learns the correction. Recorded
    here rather than silently accepted (tracked as a follow-up)."""
    ten_k = _row("2025-01-27", "2026-01-25")
    other = _row(
        "2024-01-29", "2025-01-26",
        form=carrier_form, accn=_SYNTHETIC_OTHER_ACCN,
    )
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=[ten_k, other],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert {f["period_end"] for f in pack["facts"]} == {"2026-01-25"}, (
        pack["facts"]
    )
    # The skipped filing must not leak a calendar entry either -- a map
    # entry for an accession with no fact is an unfounded FY declaration.
    assert set(pack["fiscal_calendars"]) == {_NVDA_ACCN}, (
        pack["fiscal_calendars"]
    )

    skipped = pack["coverage"]["skipped_rows"]
    flags = [f for f in skipped if f["type"] == "carrier_form_not_allowlisted"]
    assert len(flags) == 1, skipped
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_SYNTHETIC_OTHER_ACCN], flag
    assert carrier_form in flag["reason"], flag


@pytest.mark.parametrize(
    "form, accn, missing",
    [
        pytest.param(None, _SYNTHETIC_OTHER_ACCN, "form", id="no-form"),
        pytest.param(_NVDA_FORM, None, "accession", id="no-accession"),
        pytest.param(None, None, "form", id="neither"),
    ],
)
def test_backfill_skips_row_that_identifies_no_filing(
    sec_client, form, accn, missing,
):
    """A row must identify its carrying filing by BOTH `form` and `accn`
    before it can contribute a calendar entry.

    `form` is what the focus is derived from. `accn` is the map KEY, and
    an unguarded `None` key is the nastier of the two: `_require_source_
    form` looks the fact's accession up with a bare `fact.get("accession")`
    (kpi_xbrl.py:296), so a `None`-keyed entry MATCHES a `None`-accession
    fact and stamps it `source_form: "10-K"` -- a point traceable to no
    filing at all, which is the fabrication this lane exists to refuse.

    Both fields were present on all 447 rows of the live capture
    (`companyconcept_form_domain_2026-07-25.json`, `n_rows_missing_accn`/
    `n_rows_missing_form` are 0 everywhere), so this guard is DEFENSIVE
    against a shape not observed -- `summarize_concept` reads both with a
    bare `.get`, so `None` is representable regardless."""
    ten_k = _row("2025-01-27", "2026-01-25")
    broken = _row("2024-01-29", "2025-01-26", form=form, accn=accn)
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=[ten_k, broken],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert {f["period_end"] for f in pack["facts"]} == {"2026-01-25"}, (
        pack["facts"]
    )
    # The key assertion: no `None` key, and no extra key of any kind.
    assert set(pack["fiscal_calendars"]) == {_NVDA_ACCN}, (
        pack["fiscal_calendars"]
    )

    skipped = pack["coverage"]["skipped_rows"]
    flags = [f for f in skipped if f["type"] == "source_filing_unidentifiable"]
    assert len(flags) == 1, skipped
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert missing in flag["reason"], flag


def test_backfill_skips_row_with_no_value_is_a_named_skip_not_a_crash(
    sec_client,
):
    """A NULL `val` IS A ROW REJECTION, NOT A PACK KILLER -- the SAME
    defect Task 5's `_statement_row_to_fact` GATE 4 fixed in the sibling
    statement lane (`test_sec_edgar_statements.py::test_a_row_with_no_
    value_is_a_named_skip_not_a_crash`), mirrored here because this lane
    builds its fact dict inline rather than through that gate helper.
    `summarize_concept` reads `val` with a bare `.get`, so a row whose
    value is absent surfaces as `value: None` -- and `float(None)` raises
    `TypeError` out of `build_top_line_backfill`, destroying the ticker's
    WHOLE top-line revenue history over one bad row.

    The good row rides along to pin the BLAST RADIUS: the rejection must
    cost its own row and nothing else."""
    good = _row("2025-01-27", "2026-01-25")
    bad = _row("2024-01-29", "2025-01-26", accn=_SYNTHETIC_OTHER_ACCN)
    bad["val"] = None
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=[good, bad],
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert {f["period_end"] for f in pack["facts"]} == {"2026-01-25"}, (
        pack["facts"]
    )
    # The skipped filing must not leak a calendar entry either -- a map
    # entry for an accession with no fact is an unfounded FY declaration.
    assert set(pack["fiscal_calendars"]) == {_NVDA_ACCN}, (
        pack["fiscal_calendars"]
    )

    skipped = pack["coverage"]["skipped_rows"]
    flags = [f for f in skipped if f["type"] == "row_value_missing"]
    assert len(flags) == 1, skipped
    flag = flags[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_SYNTHETIC_OTHER_ACCN], flag


def test_backfill_facts_are_classifiable_by_kpi_xbrl(sec_client, kpi_xbrl):
    """Round-trip proof: every kept fact carries the exact label group
    `kpi_xbrl.classify_fact_period` hard-requires (fiscal_year,
    fiscal_quarter, duration_months) and it does not raise unclassifiable."""
    rows = [
        _row("2025-01-27", "2026-01-25"),
        _row("2024-01-29", "2025-01-26"),
    ]
    resolve_patch, fetch_patch = _stub_fetch(
        sec_client, winning_concept=_NVDA_CONCEPT, rows=rows,
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_top_line_backfill("NVDA")

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 2, pack["facts"]
    for fact in pack["facts"]:
        classification = kpi_xbrl.classify_fact_period(fact)
        assert classification["period_type"] == "FY", classification
        assert classification["duration_class"] == "12mo-FY", classification
