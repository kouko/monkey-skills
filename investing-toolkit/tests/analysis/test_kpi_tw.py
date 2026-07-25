"""Tests for analysis-kpi/scripts/kpi_tw.py — TW iXBRL fact -> kpi_store
point adapter (TW-market kpi_store producer, Task 1).

kpi_tw.py is PURE-COMPUTE (stdlib only: re + datetime). It takes an
ALREADY-PARSED list of fact dicts (the twse_ixbrl_parser shape) as input —
it does NOT parse HTML and does NOT import any data-markets module (the
analysis↔data-markets layer boundary, per
[[durable-store-mirrors-cache-util-not-imports-it]]).

The TEST parses the real captured 1101 fixture through the production
twse_ixbrl_parser (test scaffolding only) and passes the facts in, so the
auth-date VALUE is empirically the fixture's, never a guessed format.

No `@req` tags: this dispatch's plan (docs/loom/plans/2026-07-25-tw-kpi-
store-producer.md) traces work by named plan Tasks, NOT by registered
loom-spec REQ-ids — so `@req` is omitted per the implementer contract.
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import ROOT, SKILLS

import pytest

KPI_TW_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_tw.py"
TWSE_PARSER_SCRIPT = SKILLS / "data-markets" / "scripts" / "twse_ixbrl_parser.py"
TWSE_CANONICAL_SCRIPT = SKILLS / "data-markets" / "scripts" / "twse_ixbrl_canonical.py"
TWSE_1101_FIXTURE = ROOT / "tests" / "data" / "fixtures" / "twse_ixbrl_1101_2026Q1_C.html"

AUTH_CONCEPT = (
    "tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements"
)

# Task 2 fixtures: a fixed non-wall-clock as_of (the 1101 fixture's board
# authorisation-for-issue date, Task 1) + a synthetic provenance envelope the
# caller (Task 3) will populate from the filing metadata.
AS_OF = "2026-05-13"
PROVENANCE = {
    "company": "1101",
    "source_accession": "twse:1101:2026Q1:C",
    "source_form": "TIFRS-Q",
    "source_kind": "xbrl-companyfacts",
}
# The write-side dedup key kpi_store.append enforces (kpi_store
# _DEDUP_KEY_FIELDS) — used here to prove a filing's comparatives never
# collapse to one key (which would silently drop the prior-period vintage).
_DEDUP_KEY_FIELDS = ("company", "kpi_id", "period", "as_of", "source_accession")


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_tw_module():
    return _load("kpi_tw_test", KPI_TW_SCRIPT)


@pytest.fixture(scope="module")
def fixture_1101_facts():
    parser = _load("twse_ixbrl_parser_test", TWSE_PARSER_SCRIPT)
    raw = TWSE_1101_FIXTURE.read_bytes()
    doc = parser.decode_ixbrl_document(raw)
    return parser.parse_ixbrl_facts(doc)


@pytest.fixture(scope="module")
def fixture_1101_canonical(fixture_1101_facts):
    # Scaffolding only: the TEST builds the canonical through the production
    # data-markets mapper (kpi_tw.py itself never imports data-markets — the
    # canonical is passed IN as a dict). This makes the field set + period
    # shape empirically the real 1101 filing's, never guessed.
    canonical_mod = _load("twse_ixbrl_canonical_test", TWSE_CANONICAL_SCRIPT)
    return canonical_mod.build_canonical(fixture_1101_facts)


def _dedup_key(point: dict) -> tuple:
    return tuple(point.get(f) for f in _DEDUP_KEY_FIELDS)


def test_extract_tw_authorisation_date(kpi_tw_module, fixture_1101_facts):
    # The 1101 fixture carries a ROC-era date (民國 115年5月13日) wrapped in
    # 董事會 procedure text: "本合併財務報告於115年5月13日經董事會通過。".
    # ROC 115 + 1911 = Gregorian 2026 → the as_of is 2026-05-13.
    assert (
        kpi_tw_module.extract_tw_authorisation_date(fixture_1101_facts)
        == "2026-05-13"
    )


def test_extract_tw_authorisation_date_gregorian(kpi_tw_module):
    # A filing whose auth-date fact carries a Gregorian date (with procedure
    # wording) parses to the same ISO shape — the value MAY be either era.
    facts = [
        {
            "concept": AUTH_CONCEPT,
            "raw_value": "本合併財務報告於2026-05-13經董事會通過。",
            "fact_type": "nonNumeric",
        }
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) == "2026-05-13"


def test_extract_tw_authorisation_date_gregorian_nian_form(kpi_tw_module):
    # A Gregorian date in 年-form ("2026年5月13日") must NOT be mis-read as
    # ROC "026年" (026 + 1911 = 1937). The 4-digit year is Gregorian → 2026,
    # never a silent wrong-century as_of.
    facts = [
        {
            "concept": AUTH_CONCEPT,
            "raw_value": "本財務報告於2026年5月13日經董事會通過。",
            "fact_type": "nonNumeric",
        }
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) == "2026-05-13"


def test_extract_tw_authorisation_date_absent_returns_none(kpi_tw_module):
    facts = [
        {"concept": "ifrs-full:CashAndCashEquivalents", "raw_value": 1000.0},
        {"concept": "tifrs-notes:PercentageOfOwnership4", "raw_value": 1.0},
    ]
    assert kpi_tw_module.extract_tw_authorisation_date(facts) is None


# --- Task 2: tw_canonical_to_points -----------------------------------------


def _points_by_kpi(points, kpi_id):
    return [p for p in points if p["kpi_id"] == kpi_id]


def test_tw_canonical_to_points(kpi_tw_module, fixture_1101_canonical):
    points = kpi_tw_module.tw_canonical_to_points(
        fixture_1101_canonical, basis="C", as_of=AS_OF, provenance=PROVENANCE
    )
    assert points, "expected KPI points from the 1101 canonical"

    # A duration KPI (income-statement revenue): kpi_id carries the basis
    # suffix, value is the raw base-scaled figure, period fields come straight
    # from the fact's duration period, provenance is the TW envelope.
    rev = _points_by_kpi(points, "revenue__basis-C")
    assert len(rev) == 2  # current quarter + prior-year comparative
    rev_current = next(p for p in rev if p["period_end"] == "2026-03-31")
    assert rev_current == {
        "company": "1101",
        "kpi_id": "revenue__basis-C",
        "period": "2026-01-01/2026-03-31",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "period_kind": "duration",
        "scale": 1,
        "value": 33168148000.0,
        "as_of": AS_OF,
        "source_accession": "twse:1101:2026Q1:C",
        "source_form": "TIFRS-Q",
        "source_table_id": "tw:ixbrl",
        "source_cell_ref": "ifrs-full:Revenue",
        "source_kind": "xbrl-companyfacts",
        "unit": "TWD",
    }

    # The canonical _meta[field] carries unit="TWD"; the mapper must copy it
    # onto every point (US producer does the same, kpi_xbrl.py:569-570) so the
    # market-agnostic tearsheet renders the TWD currency label. Dropping it
    # rendered correct amounts with NO currency (live 2330 dogfood finding).
    assert all(p["unit"] == "TWD" for p in points)

    # An instant KPI (balance-sheet total_assets): period_kind="instant",
    # period_start is None (an instant has no span), period_end is the date.
    ta = _points_by_kpi(points, "total_assets__basis-C")
    assert len(ta) == 3  # this quarter-end + two prior instants
    ta_current = next(p for p in ta if p["period_end"] == "2026-03-31")
    assert ta_current["period_kind"] == "instant"
    assert ta_current["period_start"] is None
    assert ta_current["period"] == "2026-03-31"
    assert ta_current["value"] == 597615286000.0
    assert ta_current["source_cell_ref"] == "ifrs-full:Assets"

    # A DERIVED KPI (fcf = ocf - capex) carries no single XBRL concept
    # (_meta concept is None) — source_cell_ref falls back to the field name
    # so the store's non-empty provenance guard still passes.
    fcf = _points_by_kpi(points, "fcf__basis-C")
    assert fcf and all(p["source_cell_ref"] == "fcf" for p in fcf)

    kpi_ids = {p["kpi_id"] for p in points}
    # ebit is a pure alias of operating_income (same concept/value) and
    # total_debt is a derived debt aggregate — neither is in the task's
    # KPI-worthy set, so neither is emitted as a redundant series.
    assert "ebit__basis-C" not in kpi_ids
    assert "total_debt__basis-C" not in kpi_ids
    assert "operating_income__basis-C" in kpi_ids

    # Every point is store-appendable: the store's required provenance /
    # as_of fields are all populated (non-empty).
    for p in points:
        assert p["source_accession"] and p["source_table_id"] and p["source_cell_ref"]
        assert p["as_of"]

    # Load-bearing: a filing's comparatives must NOT collapse under the
    # store's 5-tuple dedup key — every point has a DISTINCT dedup key, so
    # appending the whole filing keeps every period's vintage.
    keys = [_dedup_key(p) for p in points]
    assert len(set(keys)) == len(points)


def test_tw_canonical_to_points_c_and_a_distinct(kpi_tw_module, fixture_1101_canonical):
    # The consolidation basis (C=合併 / A=個體) is TW's only series
    # discriminator (no us-gaap dimensional axes). Two distinct series must
    # NOT collide/merge: every C kpi_id is disjoint from every A kpi_id.
    c_points = kpi_tw_module.tw_canonical_to_points(
        fixture_1101_canonical, basis="C", as_of=AS_OF, provenance=PROVENANCE
    )
    a_points = kpi_tw_module.tw_canonical_to_points(
        fixture_1101_canonical, basis="A", as_of=AS_OF, provenance=PROVENANCE
    )
    c_ids = {p["kpi_id"] for p in c_points}
    a_ids = {p["kpi_id"] for p in a_points}
    assert c_ids and a_ids
    assert c_ids.isdisjoint(a_ids)
    assert all(i.endswith("__basis-C") for i in c_ids)
    assert all(i.endswith("__basis-A") for i in a_ids)


def test_tw_canonical_to_points_kpi_id_collision_fails_loud(kpi_tw_module):
    # The injective guard (mirroring kpi_xbrl_ingest's collision guard):
    # the field-slug is a LOSSY lowercased normalization, so two DISTINCT
    # source fields that collapse to one kpi_id must fail loud rather than
    # silently merge two series. Here "revenue" and "Revenue" both slug to
    # "revenue__basis-C".
    dur = {"type": "duration", "start": "2026-01-01", "end": "2026-03-31"}
    canonical = {
        "income_statement": {
            "revenue": [1.0],
            "Revenue": [2.0],
            "_meta": {
                "revenue": {"concept": "ifrs-full:Revenue", "periods": [dur]},
                "Revenue": {"concept": "ifrs-full:RevenueAlt", "periods": [dur]},
            },
        }
    }
    with pytest.raises(ValueError):
        kpi_tw_module.tw_canonical_to_points(
            canonical, basis="C", as_of=AS_OF, provenance=PROVENANCE
        )
