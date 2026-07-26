"""test_sec_edgar_statements.py — RED/GREEN tests for
`build_statement_backfill` (Task 5, docs/loom/plans/2026-07-26-us-as-
reported-statement-lane.md): the as-reported ANNUAL statement lane, which
keeps the filer's OWN us-gaap concepts for the 14 spine fields rather than
resolving them to a canonical name at write time.

FIXTURE GROUNDING. Every dollar figure below is a REAL captured value from
a committed probe fixture — never hand-invented (repo memory
`hand-authored-fixture-is-a-fabrication-risk`):

  - `fixtures/topline_probe_2026-07-25.json`, AAPL entry: accession
    `0000320193-25-000079`, period_of_report `2025-09-27`, concept
    `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax`,
    window `2024-09-29`->`2025-09-27`, value 416,161,000,000.
  - `fixtures/us_statement_shapes_probe_2026-07-26.json`, AAPL entry:
    `identity.assets` = 359,241,000,000 at the `2025-09-27` instant (the
    balance-sheet date of that same 10-K), CIK 320193, entity name
    "Apple Inc."; `fields.revenue` records AAPL's ASC-606 tag switch
    (naive winner `Revenues` ending 2018-09-29 vs chain-best RFCC ending
    2025-09-27, 7 stale years) — the per-period-resolution case.

Only the period WINDOW is mutated per row, to hit specific classification
boundaries (annual vs quarterly span, instant vs duration) — the same
"freshly-parsed COPY... ONLY the period window is mutated in-test"
convention `test_sec_edgar_top_line_backfill.py` states and this repo
already uses.

Rows are shaped as RAW `companyfacts` `units.<unit>[]` entries — i.e.
`summarize_concept`'s INPUT shape (`start`/`end`/`val`/`accn`/`form`/
`fy`/`fp`/`filed`), read back off `summarize_concept`'s own body rather
than assumed from what the consumer wants.

Split into focused, independently-failing tests (this module's stated
convention: a single bundled test gives zero signal on which behavior
broke).

No `@req` tags: this plan registers no REQ-ids in the loom-spec
namespace, so there is no id to bind these tests to (never a minted one).

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


@pytest.fixture
def sec_client():
    """Import sec_edgar_client with `edgar` AND `requests` stubbed in
    sys.modules — same convention as `test_sec_edgar_top_line_backfill.py`'s
    `sec_client` fixture. `build_statement_backfill` never touches edgar
    (companyfacts is a plain REST fetch via `fetch_facts`), but the
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


# --- Real captured AAPL values (see this module's FIXTURE GROUNDING).
_AAPL_CIK = 320193
_AAPL_ENTITY = "Apple Inc."
_AAPL_ACCN = "0000320193-25-000079"
_AAPL_FORM = "10-K"
# The `filed` date the plan's own PIN records for this accession
# (## Notes, "PIN — statement pack envelope": `"filed": "2025-10-31"`).
_AAPL_FILED = "2025-10-31"

_AAPL_FY25_START = "2024-09-29"
_AAPL_FY25_END = "2025-09-27"
_AAPL_RFCC = "RevenueFromContractWithCustomerExcludingAssessedTax"
_AAPL_RFCC_VALUE = 416161000000.0
_AAPL_ASSETS_VALUE = 359241000000.0

# AAPL's pre-ASC-606 era, tagged `Revenues`: the probe records its naive
# winner ending 2018-09-29 (`fields.revenue.winner_newest_10k_end`). The
# VALUE is not captured by either probe, and no assertion below reads it —
# the pre-switch rows exist only to prove the later era is not truncated
# away. Openly declared as a placeholder, never presented as captured.
_PLACEHOLDER_EARLY_REVENUE_VALUE = 1.0
_AAPL_FY18_START = "2017-10-01"
_AAPL_FY18_END = "2018-09-29"

# A SYNTHETIC accession for rows whose carrying filing must be DISTINCT
# from AAPL's real 10-K (one accession is one filing with one form, so a
# 20-F row cannot honestly reuse a 10-K's accession). An IDENTIFIER, never
# financial data; the `-25-000999` serial is outside AAPL's real filing
# series so it can never be mistaken for a citable accession.
_SYNTHETIC_OTHER_ACCN = "0000320193-25-000999"
# Its `filed` date, likewise synthetic and likewise an identifier: a
# restatement is carried by a LATER filing than the one it revises, and
# `kpi_xbrl._reduce_window_group`'s downstream collapse is newest-filed-
# wins, so two vintages that shared one `filed` date would be a fixture
# that cannot exercise the rule this lane defers to.
_SYNTHETIC_OTHER_FILED = "2026-10-30"

# The SECOND vintage of AAPL's FY25 revenue window. Neither probe captured
# a restatement PAIR, so this is an openly-declared PLACEHOLDER, never
# presented as captured — no assertion reads it as a financial figure. It
# only has to DIFFER from the first vintage's value, so that an
# implementation collapsing by value could not hide inside the test.
_PLACEHOLDER_RESTATED_VALUE = 2.0

# --- WMT's captured DOUBLE-TAG, the one real conflict case in the corpus
# (`fixtures/topline_probe_2026-07-25.json`, WMT entry, accession
# `0000104169-26-000055`): the SAME window `2025-02-01`->`2026-01-31` is
# tagged BOTH `us-gaap:Revenues` = 713,163,000,000 (its own "Total
# revenues" line) AND `us-gaap:RevenueFromContractWithCustomerExcluding
# AssessedTax` = 706,413,000,000 (which excludes membership/other). Both
# concepts are members of the pinned `revenue` chain, so chain order alone
# WOULD pick one — which is exactly what must not happen.
_WMT_ACCN = "0000104169-26-000055"
_WMT_FY26_START = "2025-02-01"
_WMT_FY26_END = "2026-01-31"
_WMT_REVENUES_VALUE = 713163000000.0
_WMT_RFCC_VALUE = 706413000000.0

# --- WMT's captured STRAY-UNIT case, the one that made the unit-selection
# rule's "first key" fallback a data-correctness defect. CAPTURED LIVE
# 2026-07-26 from `companyconcept` CIK 104169 `us-gaap:
# EarningsPerShareBasic`: the payload's unit keys arrive in the order
# `['pure', 'USD/shares']`, and there is NO `USD` key at all, so the
# USD-preference branch never fires and the fallback decides the series.
#
#   'pure'       ->   3 rows, ALL 10-Q
#   'USD/shares' -> 303 rows, 131 of them 10-K
#
# Three stray rows mis-tagged `pure` therefore outrank 303 correct ones on
# nothing but dict order — and because all three are 10-Q, the annual lane
# then skips every one and emits ZERO EPS facts for WMT. COST (CIK 909832)
# is the same shape with a different outcome: 11 `pure` 10-K rows vs 295
# `USD/shares`, so it emits the WRONG series rather than none.
_WMT_EPS_STRAY_UNIT = "pure"
_WMT_EPS_REAL_UNIT = "USD/shares"
# The first row of each captured series, verbatim.
_WMT_EPS_STRAY_ACCN = "0001193125-10-202779"
_WMT_EPS_STRAY_FILED = "2010-09-01"
_WMT_EPS_STRAY_START = "2009-02-01"
_WMT_EPS_STRAY_END = "2009-07-31"
_WMT_EPS_STRAY_VALUE = 1.66
_WMT_EPS_REAL_ACCN = "0001193125-10-071652"
_WMT_EPS_REAL_FILED = "2010-03-30"
_WMT_EPS_REAL_START = "2007-02-01"
_WMT_EPS_REAL_END = "2008-01-31"
_WMT_EPS_REAL_VALUE = 3.13
# The next annual window of that same captured 10-K, so a fixture can carry
# a real MAJORITY (two `USD/shares` rows against one `pure`) rather than a
# 1-vs-1 tie, which the first-seen tie-break would resolve to the stray.
_WMT_EPS_REAL_START_2 = "2008-02-01"
_WMT_EPS_REAL_END_2 = "2009-01-31"
_WMT_EPS_REAL_VALUE_2 = 3.4

# --- TSLA's captured EQUITY PAIR, the `total_equity` chain's two members.
# CAPTURED LIVE 2026-07-26 from `companyfacts` CIK 1318605 via this lane's
# own pack (`pack.py --pack statement-backfill --ticker TSLA`), accession
# `0001628280-26-003952` (FY2025 10-K), instant `2025-12-31`.
#
# These two are NOT competing answers to one question — they are
# COMPLEMENTARY SUBTOTALS of the balance sheet, and their difference IS the
# non-controlling interest (82,807 - 82,137 = 670M, TSLA's NCI). A rule that
# reads their disagreement as a contradiction therefore fires on precisely
# the filers that report BOTH correctly: cross-tabbed against
# `fixtures/us_statement_shapes_probe_2026-07-26.json`, 17 filers of the
# 47-filer corpus tag both at the same Assets instant (CVX, PSX, WFC, C, MS,
# IBM, QCOM, COST, PEP, JNJ, PFE, UNH, BA, GE, F, GM, TSLA).
_TSLA_ACCN = "0001628280-26-003952"
_TSLA_FY25_INSTANT = "2025-12-31"
_TSLA_EQUITY_PARENT_ONLY = 82137000000.0
_TSLA_EQUITY_INCL_NCI = 82807000000.0
_EQUITY_INCL_NCI_CONCEPT = (
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
)

# --- XOM's measured DECOY CIK, the Task 6 case
# (`fixtures/us_statement_shapes_probe_2026-07-26.json`, XOM entry: `cik`
# 2115436, `entity_name` "EXXON MOBIL CORP", `us_gaap_tags` 0 — the ONE
# filer of the 47-ticker corpus with zero us-gaap concepts, and the reason
# `_summary.n_filers_zero_us_gaap_concepts` is 1). The real 1994-2025
# operating history sits under a DIFFERENT CIK (34088, repo memory
# `ticker-to-cik-can-resolve-to-a-decoy-entity`) — which this lane must
# never stitch in: predecessor and successor are legally distinct filers,
# so a stitched series conflates two entities. Surfacing the
# discontinuity, not repairing it, is the whole behaviour under test.
_XOM_DECOY_CIK = 2115436
_XOM_DECOY_ENTITY = "EXXON MOBIL CORP"


def _row(
    *,
    end: str,
    start: str | None,
    val: float,
    form: str | None = _AAPL_FORM,
    accn: str | None = _AAPL_ACCN,
    filed: str = _AAPL_FILED,
) -> dict:
    """One raw `companyfacts` `units.<unit>[]` row — `summarize_concept`'s
    input shape. `start=None` models an INSTANT row: SEC omits `start`
    entirely on instant facts, and `summarize_concept` reads it with a bare
    `.get`, so `None` is exactly what a balance-sheet row surfaces as.

    `fy`/`fp` are stamped 2025/FY on EVERY row — the live-confirmed trap
    (a filing stamps its OWN focus onto every comparative it carries);
    `build_statement_backfill` must never read either."""
    return {
        "start": start, "end": end, "val": val, "accn": accn,
        "form": form, "fy": 2025, "fp": "FY", "filed": filed,
    }


def _concept_obj(rows: list[dict], *, unit: str = "USD") -> dict:
    """One `companyfacts` per-tag object: `{label, description, units:
    {<unit>: [rows]}}` — the shape `summarize_concept` /
    `build_companyfacts_pack` already parse."""
    return {"label": "probe row", "units": {unit: rows}}


def _stub_companyfacts(sec_client, us_gaap: dict, *, entity: str = _AAPL_ENTITY):
    """Patch `resolve_cik` + `fetch_facts` so `build_statement_backfill`
    sees ONE companyfacts payload — mirrors `test_sec_xval.py`'s
    `mock.patch.object(sec_client, "fetch_facts", ...)` convention. The
    full-companyfacts call is `fetch_facts(cik, None)` (concept=None), the
    single endpoint this lane reads."""

    def _fetch(cik, concept):
        assert cik == _AAPL_CIK
        assert concept is None, (
            "the statement lane reads the FULL companyfacts payload once, "
            f"not per-concept companyconcept calls (got {concept!r})"
        )
        return {
            "cik": cik,
            "fetched_at": "2026-07-26T00:00:00Z",
            "data": {"entityName": entity, "facts": {"us-gaap": us_gaap}},
        }

    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _AAPL_CIK, "ticker": "AAPL"},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts", side_effect=_fetch,
    )
    return resolve_patch, fetch_patch


def _build(sec_client, us_gaap: dict, *, ticker: str = "AAPL") -> dict:
    resolve_patch, fetch_patch = _stub_companyfacts(sec_client, us_gaap)
    with resolve_patch, fetch_patch:
        return sec_client.build_statement_backfill(ticker)


def test_emits_one_fact_per_concept_per_annual_period(sec_client):
    """THE PINNED PACK (Task 5 acceptance). An income-statement duration
    row and a balance-sheet instant row from the same 10-K each become
    exactly ONE fact, carrying the plan's pinned per-fact fields — and the
    envelope carries the pinned top-level keys."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
        )]),
        "Assets": _concept_obj([_row(
            start=None, end=_AAPL_FY25_END, val=_AAPL_ASSETS_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["pack"] == "statement-backfill", pack
    assert pack["ticker"] == "AAPL", pack
    assert pack["source_kind"] == "xbrl-companyfacts", pack
    assert pack["company"] == _AAPL_ENTITY, pack
    assert pack["fetched_at"], pack
    assert pack["coverage"]["skipped_rows"] == [], pack["coverage"]

    by_concept = {f["concept"]: f for f in pack["facts"]}
    assert set(by_concept) == {
        f"us-gaap:{_AAPL_RFCC}", "us-gaap:Assets",
    }, pack["facts"]

    revenue = by_concept[f"us-gaap:{_AAPL_RFCC}"]
    assert revenue == {
        "concept": f"us-gaap:{_AAPL_RFCC}",
        "period_start": _AAPL_FY25_START,
        "period_end": _AAPL_FY25_END,
        "period_kind": "duration",
        "value": _AAPL_RFCC_VALUE,
        "unit": "USD",
        "accession": _AAPL_ACCN,
        "filed": _AAPL_FILED,
        "form": _AAPL_FORM,
    }, revenue


def test_two_accessions_for_one_window_stay_two_facts(sec_client):
    """THE LANE'S CARDINALITY IS (concept, period, ACCESSION), NOT
    (concept, period). Two rows of ONE concept for ONE window carried by
    DIFFERENT accessions are a RESTATEMENT — the later filing revising the
    earlier's figure — and both vintages must survive this lane intact.

    Load-bearing, not incidental. The brief's job story asks for "every
    vintage preserved"; the store's dedup key is a 5-tuple INCLUDING
    `source_accession`; and collapsing a window to one number is
    `kpi_xbrl._reduce_window_group`'s job downstream (overlap policy C,
    newest-filed wins), which cannot run on history this lane already
    threw away. `_resolve_concept_per_period` passes same-window rows of
    one concept through untouched by design, and this test is the pin that
    keeps a future "dedup by (concept, period)" from looking harmless.

    Characterization test (Feathers 2004 Ch.13): the behaviour is already
    correct and had NO test in either direction. Confirmed discriminating
    by the Iron Law's false-green diagnostic rather than by a first-run
    RED — see this task's report for the mutation used and its revert."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([
            _row(start=_AAPL_FY25_START, end=_AAPL_FY25_END,
                 val=_AAPL_RFCC_VALUE),
            _row(start=_AAPL_FY25_START, end=_AAPL_FY25_END,
                 val=_PLACEHOLDER_RESTATED_VALUE,
                 accn=_SYNTHETIC_OTHER_ACCN, filed=_SYNTHETIC_OTHER_FILED),
        ]),
    })

    assert "error" not in pack, pack
    assert pack["coverage"]["skipped_rows"] == [], pack["coverage"]
    assert [
        (f["concept"], f["period_start"], f["period_end"],
         f["accession"], f["filed"])
        for f in pack["facts"]
    ] == [
        (f"us-gaap:{_AAPL_RFCC}", _AAPL_FY25_START, _AAPL_FY25_END,
         _AAPL_ACCN, _AAPL_FILED),
        (f"us-gaap:{_AAPL_RFCC}", _AAPL_FY25_START, _AAPL_FY25_END,
         _SYNTHETIC_OTHER_ACCN, _SYNTHETIC_OTHER_FILED),
    ], (
        "both restatement vintages must reach the pack, each carrying its "
        "OWN accession and filed date — the downstream newest-filed-wins "
        f"collapse has nothing to choose between otherwise: {pack['facts']}"
    )


def test_balance_sheet_instant_is_kept_as_an_annual_observation(sec_client):
    """INSTANT ROWS ARE IN SCOPE. `Assets`/`Liabilities`/`StockholdersEquity`
    /cash are spine fields carried by INSTANT facts, which have no `start`
    at all — a duration test written for income-statement rows must not
    reject them (and `_duration_months` would RAISE on the missing
    `period_start`, killing the whole pack).

    An instant carried by an allowlisted 10-K IS this lane's annual
    balance-sheet observation — the same rule the committed probe measures
    the balance identity under (`capture_us_statement_shapes_probe.py::
    _latest_instant`: `start is None` rows of 10-K-carried facts)."""
    pack = _build(sec_client, {
        "Assets": _concept_obj([_row(
            start=None, end=_AAPL_FY25_END, val=_AAPL_ASSETS_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 1, pack["facts"]
    fact = pack["facts"][0]
    assert fact["period_kind"] == "instant", fact
    assert fact["period_start"] is None, fact
    assert fact["period_end"] == _AAPL_FY25_END, fact
    assert fact["value"] == _AAPL_ASSETS_VALUE, fact
    assert pack["coverage"]["skipped_rows"] == [], pack["coverage"]


def test_resolves_a_spine_chain_per_period(sec_client):
    """CHAIN RESOLUTION IS PER PERIOD, not per company — the rule
    `_resolve_concept_per_period` (Task 2) already encodes, reused here
    rather than re-implemented. AAPL's measured ASC-606 switch: its early
    years are tagged `Revenues` and its later years RFCC; a per-company
    first-present pick would keep only the pre-switch era (probe:
    `fields.revenue.stale_years` = 7)."""
    pack = _build(sec_client, {
        "Revenues": _concept_obj([_row(
            start=_AAPL_FY18_START, end=_AAPL_FY18_END,
            val=_PLACEHOLDER_EARLY_REVENUE_VALUE,
        )]),
        _AAPL_RFCC: _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    by_end = {f["period_end"]: f["concept"] for f in pack["facts"]}
    assert by_end == {
        _AAPL_FY18_END: "us-gaap:Revenues",
        _AAPL_FY25_END: f"us-gaap:{_AAPL_RFCC}",
    }, (
        "a mid-history tag switch must not truncate the series at the "
        f"switch, and each era must carry its OWN concept: {pack['facts']}"
    )


def test_skips_a_non_10k_carrier_before_any_period_arithmetic(sec_client):
    """GATE ORDER: identity before arithmetic. A 20-F carries a whole
    annual history too (`_TOP_LINE_ANNUAL_CARRIER_FORMS`'s live capture:
    47 annual-span 20-F rows + 8 on 20-F/A across two us-gaap-tagging
    foreign private issuers), and stamping one as a 10-K would be a lie.

    The row below is BOTH non-allowlisted AND non-annual (a 3-month span).
    It must report the ONE actionable reason — its carrier — rather than a
    period-shaped one, so a filer this lane cannot serve at all gets one
    consistent explanation per row."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([_row(
            start="2025-06-29", end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
            form="20-F", accn=_SYNTHETIC_OTHER_ACCN,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["facts"] == [], pack["facts"]
    skipped = pack["coverage"]["skipped_rows"]
    assert [f["type"] for f in skipped] == ["carrier_form_not_allowlisted"], (
        "the carrier gate runs BEFORE the annual-span gate: a non-10-K row "
        f"must never be reported as merely non-annual — {skipped}"
    )
    flag = skipped[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_SYNTHETIC_OTHER_ACCN], flag
    assert "20-F" in flag["reason"], flag


def test_skips_a_non_annual_duration_span_with_a_named_reason(sec_client):
    """ANNUAL SPAN IS CLASSIFIED FROM THE ROW'S OWN start->end via
    `_duration_months` — NEVER its `fy`/`fp`. A 10-K tags its Q4 and
    year-to-date disaggregations alongside the annual figure, and every one
    of them is stamped with the FILING's `fp: FY` (both rows below carry
    `fp: FY`), so `fp` cannot discriminate annual from quarterly."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([
            _row(start=_AAPL_FY25_START, end=_AAPL_FY25_END,
                 val=_AAPL_RFCC_VALUE),
            # Same period END, one quarter wide — the disaggregated Q4.
            _row(start="2025-06-29", end=_AAPL_FY25_END,
                 val=_PLACEHOLDER_EARLY_REVENUE_VALUE),
        ]),
    })

    assert "error" not in pack, pack
    assert [f["period_start"] for f in pack["facts"]] == [
        _AAPL_FY25_START,
    ], pack["facts"]
    skipped = pack["coverage"]["skipped_rows"]
    assert [f["type"] for f in skipped] == ["non_annual_row_skipped"], skipped
    assert set(skipped[0]) == {
        "type", "old", "new", "accessions", "reason",
    }, skipped[0]


def test_skips_a_row_that_cannot_identify_its_carrying_filing(sec_client):
    """GATE 1. A row carrying no `form`/`accn` cannot be traced to a
    filing, so it is skipped rather than defaulted — this lane never
    emits a fact whose provenance it cannot state."""
    pack = _build(sec_client, {
        "Assets": _concept_obj([_row(
            start=None, end=_AAPL_FY25_END, val=_AAPL_ASSETS_VALUE,
            form=None, accn=None,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["facts"] == [], pack["facts"]
    skipped = pack["coverage"]["skipped_rows"]
    assert [f["type"] for f in skipped] == [
        "source_filing_unidentifiable",
    ], skipped
    assert set(skipped[0]) == {
        "type", "old", "new", "accessions", "reason",
    }, skipped[0]


def test_skips_a_row_with_no_period_at_all_with_a_named_reason(sec_client):
    """A row carrying no `end` has NO period — neither an instant date nor
    a duration window. It is skipped with a named reason rather than
    emitted with a null `period_end`, which is the field the store keys a
    point on (plan PIN: `period` = the instant date, or `<start>/<end>`).

    The instant branch makes this reachable: a duration row's missing dates
    still fail loud inside `_duration_span_days`, but an instant's period
    IS its `end`, so nothing downstream of a null one would notice."""
    pack = _build(sec_client, {
        "Assets": _concept_obj([_row(
            start=None, end=None, val=_AAPL_ASSETS_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["facts"] == [], pack["facts"]
    skipped = pack["coverage"]["skipped_rows"]
    assert [f["type"] for f in skipped] == ["row_period_unclassifiable"], skipped
    assert set(skipped[0]) == {
        "type", "old", "new", "accessions", "reason",
    }, skipped[0]


def test_fetches_the_identity_only_concepts_as_ordinary_facts(sec_client):
    """The three balance-identity components are NOT spine fields, but
    Task 7's identity (`A - (L + mezzanine + E)`) cannot be computed
    without them and nothing else fetches them — measured, TSLA's entire
    residual was exactly its redeemable NCI. They are emitted as ORDINARY
    facts, each under its OWN concept: they are alternatives for Task 7 to
    choose between, never a first-present chain to collapse here."""
    mezzanine = (
        "TemporaryEquityCarryingAmountIncludingPortionAttributableTo"
        "NoncontrollingInterests"
    )
    us_gaap = {
        concept: _concept_obj([_row(
            start=None, end=_AAPL_FY25_END, val=_AAPL_ASSETS_VALUE,
        )])
        for concept in (
            mezzanine,
            "RedeemableNoncontrollingInterestEquityCarryingAmount",
            "MinorityInterest",
        )
    }
    pack = _build(sec_client, us_gaap)

    assert "error" not in pack, pack
    assert {f["concept"] for f in pack["facts"]} == {
        f"us-gaap:{concept}" for concept in us_gaap
    }, pack["facts"]
    assert pack["coverage"]["skipped_rows"] == [], pack["coverage"]


def test_two_concepts_disagreeing_on_one_period_both_survive(sec_client):
    """TWO CHAIN CONCEPTS ON ONE PERIOD ARE TWO SERIES, NOT A CONTRADICTION
    (brief §Smallest End State #1, verbatim: `us-gaap:Revenues` and
    `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` are "two
    series, not one resolved series").

    Replays WMT's captured double-tag: the SAME window is tagged BOTH
    `Revenues` = 713,163M (its own "Total revenues" line, which INCLUDES
    membership and other income) AND RFCC = 706,413M (contract revenue
    only). Those figures SHOULD differ — they measure different things —
    so this lane has no tie to break and MUST emit both, each under its
    OWN concept. Selection between them is the read-side view's job
    (`kpi_spine_view._resolve_field`, first-present per period), which
    cannot run on a period this lane already discarded.

    REPLACES `test_a_conflicted_period_reaches_coverage_as_a_named_skip`,
    which asserted the opposite (both concepts skipped under a
    `statement_concept_value_conflict` flag). That test encoded a DEFECT,
    not a requirement: the live 2026-07-26 six-filer dogfood measured 366
    rows skipped under that flag for WMT alone, taking `revenue`,
    `net_income` AND `eps_basic` out of WMT's spine entirely. The rule it
    pinned belongs to the TOP-LINE lane (`build_top_line_backfill`), which
    must produce ONE `total_revenue` series and therefore has a genuine
    ambiguity to fail loud on; that lane's own conflict tests are
    untouched."""
    pack = _build(sec_client, {
        "Revenues": _concept_obj([_row(
            start=_WMT_FY26_START, end=_WMT_FY26_END,
            val=_WMT_REVENUES_VALUE, accn=_WMT_ACCN,
        )]),
        _AAPL_RFCC: _concept_obj([_row(
            start=_WMT_FY26_START, end=_WMT_FY26_END,
            val=_WMT_RFCC_VALUE, accn=_WMT_ACCN,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["coverage"]["skipped_rows"] == [], (
        "a period reported under two chain concepts is not a rejected row "
        f"— nothing about it is skippable: {pack['coverage']}"
    )
    assert {
        (f["concept"], f["period_start"], f["period_end"], f["value"])
        for f in pack["facts"]
    } == {
        ("us-gaap:Revenues", _WMT_FY26_START, _WMT_FY26_END,
         _WMT_REVENUES_VALUE),
        (f"us-gaap:{_AAPL_RFCC}", _WMT_FY26_START, _WMT_FY26_END,
         _WMT_RFCC_VALUE),
    }, (
        "both concepts must reach the pack as their own series — dropping "
        "the period under BOTH is how an entire spine field vanished for "
        f"WMT: {pack['facts']}"
    )


def test_both_equity_totals_at_one_instant_both_survive(sec_client):
    """THE `total_equity` CHAIN IS THE WORSE VICTIM OF THE SAME ROOT CAUSE,
    and it fails in the opposite direction from an edge case: its two
    members are COMPLEMENTARY SUBTOTALS — `StockholdersEquity` is
    parent-only and `...IncludingPortionAttributableToNoncontrollingInterest`
    is whole equity — so they are SUPPOSED to differ whenever a
    non-controlling interest exists. Their difference is the NCI itself
    (see the TSLA constants: 82,807M - 82,137M = 670M).

    A rule reading that as a contradiction therefore drops `total_equity`
    on exactly the filers that report both CORRECTLY — 17 of the 47-filer
    probe corpus. The knock-on reached the read side: with no equity there
    is no balance-sheet identity, so `kpi_spine_view._minority_interest_
    term`'s `parent_only` branch and its `nci_is_asserted` exception were
    UNREACHABLE through the shipped producer, despite an earlier review
    round calling that "the MAJORITY case, not an edge case".

    Distinct from `test_two_concepts_disagreeing_on_one_period_both_survive`
    on three axes worth separate signal: INSTANT rows rather than duration,
    a chain whose disagreement is structural rather than definitional, and
    the read-side path this unblocks. Task 7's own tests fed hand-built
    store dumps carrying both concepts — an input the producer could not
    actually emit — so this is the first test that pins the producer end."""
    pack = _build(sec_client, {
        "StockholdersEquity": _concept_obj([_row(
            start=None, end=_TSLA_FY25_INSTANT,
            val=_TSLA_EQUITY_PARENT_ONLY, accn=_TSLA_ACCN,
        )]),
        _EQUITY_INCL_NCI_CONCEPT: _concept_obj([_row(
            start=None, end=_TSLA_FY25_INSTANT,
            val=_TSLA_EQUITY_INCL_NCI, accn=_TSLA_ACCN,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["coverage"]["skipped_rows"] == [], (
        "two complementary equity subtotals are not a data-quality "
        f"problem — neither row is rejectable: {pack['coverage']}"
    )
    assert {
        (f["concept"], f["period_kind"], f["period_end"], f["value"])
        for f in pack["facts"]
    } == {
        ("us-gaap:StockholdersEquity", "instant", _TSLA_FY25_INSTANT,
         _TSLA_EQUITY_PARENT_ONLY),
        (f"us-gaap:{_EQUITY_INCL_NCI_CONCEPT}", "instant",
         _TSLA_FY25_INSTANT, _TSLA_EQUITY_INCL_NCI),
    }, (
        "the read-side view needs BOTH totals to know whether an equity "
        "figure includes NCI; keeping only one — or neither — makes the "
        f"balance identity uncheckable: {pack['facts']}"
    )


def test_a_row_with_no_value_is_a_named_skip_not_a_crash(sec_client):
    """A NULL `val` IS A ROW REJECTION, NOT A PACK KILLER.
    `summarize_concept` reads `val` with a bare `.get`, so a row whose
    value is absent surfaces as `value: None` — and `float(None)` raises
    `TypeError` out of `build_statement_backfill`, destroying all 17
    concepts' history for the ticker over ONE bad row. That is also the
    THIRD outcome `_statement_row_to_fact`'s own contract excludes
    ("(fact, None) ... or (None, flag) — never both, never neither").

    That the null is reachable is not hypothetical: `_resolve_concept_per_
    period` already guards its conflict DIAGNOSTIC against exactly this
    case, on exactly these stated grounds.

    The good `Assets` row rides along to pin the blast radius: the
    rejection must cost its own row and nothing else."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=None,
        )]),
        "Assets": _concept_obj([_row(
            start=None, end=_AAPL_FY25_END, val=_AAPL_ASSETS_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    assert [f["concept"] for f in pack["facts"]] == ["us-gaap:Assets"], (
        "one value-less row must not take the rest of the pack with it: "
        f"{pack}"
    )
    skipped = pack["coverage"]["skipped_rows"]
    assert [f["type"] for f in skipped] == ["row_value_missing"], skipped
    flag = skipped[0]
    assert set(flag) == {"type", "old", "new", "accessions", "reason"}, flag
    assert flag["accessions"] == [_AAPL_ACCN], flag


def test_a_per_share_concept_keeps_its_own_unit(sec_client):
    """`unit` is read from the concept's OWN companyfacts unit key, never
    hardcoded to USD: `eps_basic` is a spine field and SEC carries it under
    `USD/shares`. The value here is an openly-declared PLACEHOLDER (no
    captured AAPL EPS exists in either probe) and no assertion reads it —
    this test is about the unit."""
    pack = _build(sec_client, {
        "EarningsPerShareBasic": _concept_obj(
            [_row(
                start=_AAPL_FY25_START, end=_AAPL_FY25_END,
                val=_PLACEHOLDER_EARLY_REVENUE_VALUE,
            )],
            unit="USD/shares",
        ),
    })

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 1, pack["facts"]
    assert pack["facts"][0]["unit"] == "USD/shares", pack["facts"][0]


def test_a_stray_minority_unit_never_beats_the_majority_series(sec_client):
    """`_companyfacts_unit_key` picks the unit key carrying the MOST rows,
    not whichever key `dict` iteration happens to yield first.

    The units dict below is WMT's real captured key ORDER (`pure` first,
    `USD/shares` second — see this module's WMT STRAY-UNIT block), which is
    what makes the two rules disagree: first-key answers `pure`, majority
    answers `USD/shares`. Only the majority answer names the series a
    reader of `EarningsPerShareBasic` means, so this is a WRONG-VALUE guard,
    not a formatting preference."""
    units = {
        _WMT_EPS_STRAY_UNIT: [_row(
            start=_WMT_EPS_STRAY_START, end=_WMT_EPS_STRAY_END,
            val=_WMT_EPS_STRAY_VALUE, form="10-Q",
            accn=_WMT_EPS_STRAY_ACCN, filed=_WMT_EPS_STRAY_FILED,
        )],
        _WMT_EPS_REAL_UNIT: [_row(
            start=_WMT_EPS_REAL_START, end=_WMT_EPS_REAL_END,
            val=_WMT_EPS_REAL_VALUE,
            accn=_WMT_EPS_REAL_ACCN, filed=_WMT_EPS_REAL_FILED,
        )] * 2,
    }
    assert list(units) == [_WMT_EPS_STRAY_UNIT, _WMT_EPS_REAL_UNIT], (
        "the fixture only exercises the defect while the stray key is "
        "iterated FIRST — a reordered dict would silently pass"
    )

    assert sec_client._companyfacts_unit_key(units) == _WMT_EPS_REAL_UNIT


def test_usd_is_still_preferred_over_a_larger_non_usd_unit(sec_client):
    """The USD preference is UNCHANGED by the majority rule and outranks
    it: a concept carrying USD rows reads USD even when another key carries
    more rows. This is the pin that keeps the fix a strict addition — for
    every USD-carrying concept (which is every concept the revenue lane and
    the Source-B pack care about) behaviour is byte-identical to before."""
    units = {
        _WMT_EPS_STRAY_UNIT: [_row(
            start=_WMT_EPS_STRAY_START, end=_WMT_EPS_STRAY_END,
            val=_WMT_EPS_STRAY_VALUE,
        )] * 5,
        "USD": [_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
        )],
    }

    assert sec_client._companyfacts_unit_key(units) == "USD"


def test_a_row_count_tie_resolves_to_the_first_key_deterministically(sec_client):
    """Two non-USD keys carrying EQUALLY many rows must resolve the same way
    on every run — otherwise the same payload could label the same fact two
    different ways across fetches, which is the mislabelling the shared
    helper exists to prevent. First-seen is the tie-break."""
    row = [_row(
        start=_WMT_EPS_STRAY_START, end=_WMT_EPS_STRAY_END,
        val=_WMT_EPS_STRAY_VALUE,
    )]
    assert sec_client._companyfacts_unit_key({"EUR": row, "CAD": row}) == "EUR"
    assert sec_client._companyfacts_unit_key({"CAD": row, "EUR": row}) == "CAD"


def test_a_stray_unit_does_not_erase_a_filers_whole_eps_history(sec_client):
    """The defect END TO END, at the shape that produced it live: WMT's
    three stray `pure` rows are all 10-Q, so once first-key selection hands
    the lane the `pure` series, the annual gate skips every row and the pack
    emits ZERO `eps_basic` facts — one spine field silently missing for the
    filer. Reading the majority series instead recovers the 10-K history and
    labels it `USD/shares`."""
    pack = _build(sec_client, {
        "EarningsPerShareBasic": {
            "label": "probe row",
            "units": {
                _WMT_EPS_STRAY_UNIT: [_row(
                    start=_WMT_EPS_STRAY_START, end=_WMT_EPS_STRAY_END,
                    val=_WMT_EPS_STRAY_VALUE, form="10-Q",
                    accn=_WMT_EPS_STRAY_ACCN, filed=_WMT_EPS_STRAY_FILED,
                )],
                _WMT_EPS_REAL_UNIT: [
                    _row(
                        start=_WMT_EPS_REAL_START, end=_WMT_EPS_REAL_END,
                        val=_WMT_EPS_REAL_VALUE,
                        accn=_WMT_EPS_REAL_ACCN, filed=_WMT_EPS_REAL_FILED,
                    ),
                    _row(
                        start=_WMT_EPS_REAL_START_2, end=_WMT_EPS_REAL_END_2,
                        val=_WMT_EPS_REAL_VALUE_2,
                        accn=_WMT_EPS_REAL_ACCN, filed=_WMT_EPS_REAL_FILED,
                    ),
                ],
            },
        },
    })

    assert "error" not in pack, pack
    assert len(pack["facts"]) == 2, (
        "the filer's 10-K EPS history must survive the stray `pure` rows: "
        f"{pack}"
    )
    assert {f["unit"] for f in pack["facts"]} == {_WMT_EPS_REAL_UNIT}, pack["facts"]
    assert [f["value"] for f in pack["facts"]] == [
        _WMT_EPS_REAL_VALUE, _WMT_EPS_REAL_VALUE_2,
    ], pack["facts"]
    assert pack["coverage"]["skipped_rows"] == [], (
        "the stray `pure` series is not selected at all, so its 10-Q rows "
        f"never reach the annual gate: {pack['coverage']}"
    )


def test_coverage_records_the_observed_statement_history_span(sec_client):
    """A TRUNCATED history must be VISIBLE to the caller (Task 6). The pack
    reports the first and last statement period it actually observed, so a
    filer whose CIK simply does not hold its earlier years shows up as a
    SHORT span rather than as a full history — measured, GOOGL's facts under
    Alphabet's post-2015-reorg CIK 1652044 start 2012-12-31 and DIS's under
    the 2019 holdco CIK 1744489 start 2016-10-01 (probe fixture, `history.
    earliest_fact_end`). The lane reports that; it never repairs it by
    stitching a predecessor CIK.

    Truncation is NOT an error — the years that ARE here are real, so the
    pack is built and the span is merely reported. That is the whole
    difference from the zero-concept case below.

    The two windows are AAPL's own captured tag-switch eras (see FIXTURE
    GROUNDING), reused here so the span is measured across a filer whose
    earliest and latest facts come from two DIFFERENT concepts — the span
    is the pack's, not one chain's."""
    pack = _build(sec_client, {
        "Revenues": _concept_obj([_row(
            start=_AAPL_FY18_START, end=_AAPL_FY18_END,
            val=_PLACEHOLDER_EARLY_REVENUE_VALUE,
        )]),
        _AAPL_RFCC: _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
        )]),
    })

    assert "error" not in pack, pack
    coverage = pack["coverage"]
    assert coverage["earliest_fact_end"] == _AAPL_FY18_END, coverage
    assert coverage["latest_fact_end"] == _AAPL_FY25_END, coverage
    assert coverage["skipped_rows"] == [], coverage


def test_an_observed_span_is_never_claimed_when_no_fact_survived(sec_client):
    """The span describes the facts the pack ACTUALLY emits, so a pack whose
    every row was skipped reports NO span rather than a fabricated one — the
    same posture as every other rejection in this lane (name what happened,
    never fill in a plausible value). The row below is skipped by its
    carrier form, so the pack is still a success with an empty `facts`."""
    pack = _build(sec_client, {
        _AAPL_RFCC: _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
            form="20-F", accn=_SYNTHETIC_OTHER_ACCN,
        )]),
    })

    assert "error" not in pack, pack
    assert pack["facts"] == [], pack["facts"]
    coverage = pack["coverage"]
    assert coverage["earliest_fact_end"] is None, coverage
    assert coverage["latest_fact_end"] is None, coverage


def test_cik_without_statement_history_is_a_loud_error(sec_client):
    """THE DECOY CIK (Task 6, repo memory
    `ticker-to-cik-can-resolve-to-a-decoy-entity`). A ticker's CURRENT
    ticker->CIK mapping can point at a holding shell minted by a reorg,
    whose `companyfacts` carries ZERO us-gaap concepts while the operating
    history sits under a different CIK — measured, XOM resolves to CIK
    2115436 with 0 tags. That must be a LOUD, typed error slot naming the
    ticker, the RESOLVED CIK and the RESOLVED entity name (the three facts a
    human needs to recognise the decoy and go look up the real filer), never
    an empty-but-successful pack.

    It is a DIFFERENT condition from `test_a_filer_with_no_spine_rows_...`
    below and must not be reported as that one: "this filer tags none of the
    concepts this lane wants" invites a chain fix, whereas "this CIK holds
    no us-gaap facts at all" is a CIK-identity problem no chain edit can
    reach. Hence the check runs BEFORE any row work and says so by name.

    The predecessor CIK is deliberately NOT stitched in — predecessor and
    successor are legally distinct filers."""
    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _XOM_DECOY_CIK, "ticker": "XOM"},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts",
        return_value={
            "cik": _XOM_DECOY_CIK,
            "fetched_at": "2026-07-26T00:00:00Z",
            "data": {
                "entityName": _XOM_DECOY_ENTITY,
                "facts": {"us-gaap": {}},
            },
        },
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_statement_backfill("XOM")

    assert "facts" not in pack, pack
    assert pack["error_class"] == "statement_backfill_failed", pack
    assert "XOM" in pack["error"], pack
    assert str(_XOM_DECOY_CIK) in pack["error"], pack
    assert _XOM_DECOY_ENTITY in pack["error"], pack
    # The CONDITION itself, not just the identifiers: a reader must be able
    # to tell this apart from "no row for the concepts this lane fetches".
    assert "0 us-gaap concepts" in pack["error"], pack


def test_a_filer_with_no_spine_rows_is_a_loud_error_slot(sec_client):
    """TOTAL FAILURE IS LOUD, never an empty-but-successful pack: a payload
    where no spine concept (nor identity concept) appears returns a typed
    error slot with NO `facts` key at all, so a caller cannot mistake
    "fetched nothing" for "this filer reports nothing"."""
    pack = _build(sec_client, {
        "SomeUnrelatedDisclosureTag": _concept_obj([_row(
            start=_AAPL_FY25_START, end=_AAPL_FY25_END, val=_AAPL_RFCC_VALUE,
        )]),
    })

    assert "facts" not in pack, pack
    assert pack["error_class"] == "statement_backfill_failed", pack
    assert "AAPL" in pack["error"], pack


def test_a_companyfacts_fetch_error_is_a_loud_error_slot(sec_client):
    """A failed companyfacts fetch is likewise a typed error slot with no
    `facts` key — mirrors `_companyfacts_pack_error_slot`'s posture, never
    a fabricated pack."""
    resolve_patch = mock.patch.object(
        sec_client, "resolve_cik",
        return_value={"cik": _AAPL_CIK, "ticker": "AAPL"},
    )
    fetch_patch = mock.patch.object(
        sec_client, "fetch_facts", return_value={"error": "HTTP 503"},
    )
    with resolve_patch, fetch_patch:
        pack = sec_client.build_statement_backfill("AAPL")

    assert "facts" not in pack, pack
    assert pack["error_class"] == "statement_backfill_failed", pack
    assert "HTTP 503" in pack["error"], pack
