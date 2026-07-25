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
        # The TICKER, not the SEC entityName the envelope also carries: this
        # is the store/dump key, and it must be the same key every other
        # lane writes under (kpi_xbrl_ingest.py:530) or one filer's history
        # splits across two keys and no single `dump --company` sees both.
        # This assertion previously read "Apple Inc." and so encoded the
        # split; see `kpi_us_statements.store_company`.
        "company": "AAPL",
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


def test_fact_missing_accession_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    # `source_accession` derives from the fact's `accession`. A bare
    # `.get("accession")` would emit a point carrying None there — which
    # kpi_store.append rejects INSIDE its per-point loop, after the pack's
    # EARLIER points already committed (a partial write into an append-only
    # store). The invariant must hold at BUILD time instead: mirrors
    # kpi_xbrl.facts_to_points' `_require_field(fact, "accession")`
    # (kpi_xbrl.py:507).
    fact = _duration_fact("us-gaap:Assets", "2023-01-01", "2023-12-31", 1000.0)
    del fact["accession"]
    with pytest.raises(ValueError, match="accession") as excinfo:
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))
    # The offending fact must be identifiable from the message alone.
    assert "us-gaap:Assets" in str(excinfo.value)


def test_fact_missing_concept_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    # `concept` feeds BOTH `kpi_id` and `source_cell_ref`, so an absent one
    # is the same partial-write hole as a missing accession — and it would
    # additionally key the series file on a None kpi_id.
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    fact["concept"] = None
    with pytest.raises(ValueError, match="concept"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))


def test_fact_missing_value_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    # `value` reaches the store today via a bare `fact.get("value")` —
    # absent/None/non-numeric values ride through unchecked and land
    # DURABLY in the append-only store, contradicting this module's own
    # "never fabricated" framing. Mirrors kpi_xbrl._require_value
    # (kpi_xbrl.py:435-449), same shape, same polarity.
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    del fact["value"]
    with pytest.raises(ValueError, match="value"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))


def test_fact_with_none_value_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    fact["value"] = None
    with pytest.raises(ValueError, match="value"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))


def test_fact_with_non_numeric_value_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    fact["value"] = "1000"
    with pytest.raises(ValueError, match="non-numeric"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))


def test_fact_with_bool_value_is_rejected_at_build_time(
    kpi_us_statements_module,
):
    # In Python `True`/`False` are instances of `int` — a naive
    # `isinstance(value, (int, float))` check would silently admit a bool
    # as a legitimate numeric figure. Must be excluded explicitly (recorded
    # incident precedent: a one-sided numeric check that let a bool pass).
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    fact["value"] = True
    with pytest.raises(ValueError, match="non-numeric"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))


def test_fact_with_zero_value_passes_through(
    kpi_us_statements_module,
):
    # Zero is a legitimate reported figure (e.g. zero preferred dividends),
    # not an absence — a falsy check (`if not value`) would wrongly reject
    # it. Recorded incident precedent: kpi_store once rejected a legitimate
    # integer 0 via exactly that falsy check.
    fact = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 0.0)
    points = kpi_us_statements_module.us_statement_pack_to_points(_pack([fact]))
    assert points[0]["value"] == 0.0


def test_a_later_malformed_fact_rejects_the_whole_pack(kpi_us_statements_module):
    # The ordering claim, at the mapper seam: an EARLIER valid fact must not
    # survive a LATER malformed one. Nothing is returned at all, so the
    # driver's append loop never runs on a half-built pack.
    good = _duration_fact("us-gaap:Revenues", "2023-01-01", "2023-12-31", 1000.0)
    bad = _duration_fact("us-gaap:Assets", "2024-01-01", "2024-12-31", 2000.0)
    del bad["accession"]
    with pytest.raises(ValueError, match="accession"):
        kpi_us_statements_module.us_statement_pack_to_points(_pack([good, bad]))


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
