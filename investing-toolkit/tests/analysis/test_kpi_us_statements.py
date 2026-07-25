"""Tests for analysis-kpi/scripts/kpi_us_statements.py — US as-reported
statement-pack -> kpi_store point mapper (pure-compute, plan Task 3,
docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md).

kpi_us_statements.py is PURE-COMPUTE (stdlib only). It takes the ## Notes
PIN'd statement-pack envelope (a dict) as input and does NOT import any
data-markets module (the analysis<->data-markets layer boundary, mirroring
kpi_tw.py:1-13).

The load-bearing identity rule under test: `kpi_id` is the filer's OWN
qname VERBATIM (namespace preserved, no slug/lowercase/digest) — so two
distinct concepts the filer used across a tag switch become two distinct
kpi_ids/series, never one collapsed series.

No `@req` tags: this dispatch carries no registered loom-spec REQ-ids (the
work is tracked by named plan Task 3), so `@req` is omitted per the
implementer contract.
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import SKILLS

import pytest

KPI_US_STATEMENTS_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_us_statements.py"
KPI_STORE_SCRIPT = SKILLS / "analysis-kpi" / "scripts" / "kpi_store.py"


def _load(name: str, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def kpi_us_statements_module():
    return _load("kpi_us_statements_test", KPI_US_STATEMENTS_SCRIPT)


@pytest.fixture(scope="module")
def kpi_store_module():
    return _load("kpi_store_test", KPI_STORE_SCRIPT)


def _pack(facts):
    # PIN shape (plan ## Notes — "PIN — statement pack envelope").
    return {
        "pack": "statement-backfill",
        "ticker": "AAPL",
        "fetched_at": "2026-07-26T00:00:00Z",
        "source_kind": "xbrl-companyfacts",
        "company": "Apple Inc.",
        "facts": facts,
        "coverage": {"skipped_rows": []},
    }


def _duration_fact(
    concept: str,
    start: str,
    end: str,
    value: float,
    accession: str = "0000320193-25-000079",
    filed: str = "2025-10-31",
) -> dict:
    return {
        "concept": concept,
        "period_start": start,
        "period_end": end,
        "period_kind": "duration",
        "value": value,
        "unit": "USD",
        "accession": accession,
        "filed": filed,
        "form": "10-K",
    }


def _instant_fact(concept: str, instant: str, value: float) -> dict:
    return {
        "concept": concept,
        "period_start": None,
        "period_end": instant,
        "period_kind": "instant",
        "value": value,
        "unit": "USD",
        "accession": "0000320193-25-000079",
        "filed": "2025-10-31",
        "form": "10-K",
    }


def _points_by_kpi(points, kpi_id):
    return [p for p in points if p["kpi_id"] == kpi_id]


def test_two_revenue_concepts_become_two_series(kpi_us_statements_module):
    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _duration_fact(
                "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                "2024-01-01",
                "2024-12-31",
                2000.0,
            ),
        ]
    )
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)

    kpi_ids = {p["kpi_id"] for p in points}
    # Load-bearing identity rule: the id IS the filer's qname verbatim,
    # namespace preserved — no slug, no lowercasing, no digest.
    assert kpi_ids == {
        "us-gaap:Revenues",
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
    }

    rev = _points_by_kpi(points, "us-gaap:Revenues")
    assert len(rev) == 1
    assert rev[0] == {
        "company": "Apple Inc.",
        "kpi_id": "us-gaap:Revenues",
        "period": "2023-01-01/2023-12-31",
        "period_start": "2023-01-01",
        "period_end": "2023-12-31",
        "period_kind": "duration",
        "scale": 1,
        "value": 1000.0,
        "as_of": "2025-10-31",
        "source_accession": "0000320193-25-000079",
        "source_form": "10-K",
        "source_table_id": "xbrl:companyfacts-statement",
        "source_cell_ref": "us-gaap:Revenues",
        "source_kind": "xbrl-companyfacts",
        "unit": "USD",
    }


def test_instant_period_labeled_by_date_not_slash_form(kpi_us_statements_module):
    pack = _pack([_instant_fact("us-gaap:Assets", "2024-12-31", 500.0)])
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)

    assert len(points) == 1
    point = points[0]
    assert point["kpi_id"] == "us-gaap:Assets"
    assert point["period_kind"] == "instant"
    assert point["period_start"] is None
    assert point["period_end"] == "2024-12-31"
    # An instant's period label is its own date, never a "<start>/<end>" pair.
    assert point["period"] == "2024-12-31"


def test_two_comparative_periods_of_one_concept_get_distinct_period_labels(
    kpi_us_statements_module,
):
    # kpi_store dedups on (company, kpi_id, period, as_of, source_accession)
    # (kpi_store._DEDUP_KEY_FIELDS) — a filing's current + comparative period
    # share every OTHER field, so their `period` labels must differ or the
    # comparative silently collapses into the current period's key.
    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _duration_fact("us-gaap:Revenues", "2022-01-01", "2022-12-31", 900.0),
        ]
    )
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)

    assert len(points) == 2
    periods = {p["period"] for p in points}
    assert periods == {"2023-01-01/2023-12-31", "2022-01-01/2022-12-31"}


def test_same_concept_period_accession_different_value_raises(
    kpi_us_statements_module,
):
    # Two facts coincide on the store's FULL dedup key (company, kpi_id,
    # period, as_of, source_accession) — same filing, same concept, same
    # period. A value mismatch here means one parse is wrong, not a
    # restatement: mirrors kpi_xbrl_ingest._require_no_stored_disagreement's
    # same-accession-different-value -> RAISE polarity (kpi_xbrl_ingest.py:446).
    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 999.0),
        ]
    )
    with pytest.raises(ValueError, match="us-gaap:Revenues"):
        kpi_us_statements_module.us_statement_pack_to_points(pack)


def test_same_concept_period_different_accession_different_value_both_emitted(
    kpi_us_statements_module,
):
    # DIFFERENT source_accession -> the dedup key does NOT coincide -> this
    # is a legitimate restatement across filings, not a disagreement. Both
    # points must be emitted (mirrors kpi_xbrl_ingest's same-polarity
    # different-accession -> APPEND, never raise) — this is the bitemporal
    # history the store exists to preserve; the fix must not touch it.
    pack = _pack(
        [
            _duration_fact(
                "us-gaap:Revenues",
                "2023-01-01",
                "2023-12-31",
                1000.0,
                accession="0000320193-25-000079",
                filed="2025-10-31",
            ),
            _duration_fact(
                "us-gaap:Revenues",
                "2023-01-01",
                "2023-12-31",
                1050.0,
                accession="0000320193-26-000012",
                filed="2026-02-15",
            ),
        ]
    )
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)
    assert len(points) == 2
    values = {p["value"] for p in points}
    assert values == {1000.0, 1050.0}


def test_same_concept_period_accession_same_value_both_pass_through(
    kpi_us_statements_module,
):
    # A harmless exact duplicate (same full dedup key AND same value) is a
    # no-op at kpi_store.append. This module documents (module docstring)
    # that it does NOT dedupe this case itself — it passes both points
    # through unchanged and leaves idempotency to the store.
    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
        ]
    )
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)
    assert len(points) == 2
    # "unchanged" is half the claim, so pin it: an implementation that
    # deduped-then-re-emitted, or that mutated a field on the way through,
    # would satisfy the count alone.
    assert points[0] == points[1]


def test_points_satisfy_kpi_store_append_guards(
    kpi_us_statements_module, kpi_store_module
):
    pack = _pack(
        [
            _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0),
            _instant_fact("us-gaap:Assets", "2023-12-31", 500.0),
        ]
    )
    points = kpi_us_statements_module.us_statement_pack_to_points(pack)
    assert points
    for point in points:
        # Exercise the REAL store guards (not a restated field list) — a
        # point that would be rejected by kpi_store.append is not a valid
        # point. Neither guard returns a value; raising is the failure mode.
        kpi_store_module._require_provenance(point)
        kpi_store_module._require_accession_derived_as_of(point)
