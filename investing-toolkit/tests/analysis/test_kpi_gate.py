"""Tests for analysis-kpi/scripts/kpi_gate.py — the reliability-gate
ground-truth label-set store (operational-kpi capability, slice 5).

This slice's Task 1 ships the module scaffold + `add_labels(company, labels)`
/ `get_labels(company)`: a durable, per-company, append-only label-set store
reusing `_store_fs` (dir resolution, lock-guarded read-modify-write, atomic
write) exactly like kpi_schema.py — NOT a new fs impl, NOT cache_util.

The store dir is redirected to a tmp path via the `KPI_STORE_DIR` env
override (shared by kpi_store/review_queue/kpi_schema/kpi_gate — same
durable DATA dir).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Ground-truth label set is a first-class
object"), NOT by registered loom-spec REQ-ids — so `@req` is omitted per
the implementer contract (mirrors test_kpi_schema.py's rationale).
"""
from __future__ import annotations

import importlib.util
import sys

from conftest import KPI_GATE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_gate_module():
    """Load kpi_gate.py as an importable module for unit tests of its
    library surface (add_labels/get_labels) before evaluate/gate_verdict/
    is_trusted/CLI are added (Tasks 2-4).
    """
    spec = importlib.util.spec_from_file_location("kpi_gate_test", KPI_GATE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_gate_test"] = module
    spec.loader.exec_module(module)
    return module


def test_add_labels_persists_and_reads_back(kpi_gate_module, tmp_path, monkeypatch):
    """add_labels(company, labels) must durably persist labeled ground-truth
    entries so get_labels(company) round-trips them; a second add_labels
    call must APPEND (both calls' labels survive), not overwrite — the
    label set is a first-class, accumulating object, not a single snapshot.

    Why this matters: the reliability gate (Task 2) evaluates extracted
    values against this label set — if a second add_labels silently
    clobbered the first, prior human-labeled ground truth would be lost
    and the gate's accuracy computation would be evaluated against a
    smaller-than-intended sample without anyone noticing.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    first_batch = [
        {"kpi_id": "iphone_units", "period": "2024-Q1", "value": 61_600_000},
        {"kpi_id": "services_revenue", "period": "2024-Q1", "value": 23_900_000_000},
    ]
    kpi_gate_module.add_labels("AAPL", first_batch)

    labels = kpi_gate_module.get_labels("AAPL")
    assert labels == first_batch

    second_batch = [
        {"kpi_id": "iphone_units", "period": "2024-Q2", "value": 45_900_000},
    ]
    kpi_gate_module.add_labels("AAPL", second_batch)

    labels = kpi_gate_module.get_labels("AAPL")
    assert labels == first_batch + second_batch, (
        "a second add_labels call must APPEND, not overwrite prior labels"
    )

    # A company with no labels at all reads as an empty list, not an error.
    assert kpi_gate_module.get_labels("MSFT") == []


def test_evaluate_verdict_by_accuracy_and_samples(kpi_gate_module, tmp_path, monkeypatch):
    """evaluate(company, schema_version, extracted_values, threshold,
    min_samples, evaluated_at) computes cell-level accuracy against the
    company's labeled ground truth and returns a fail-closed verdict.

    Why this matters: a gate that could be TRUSTED from a handful of lucky
    cells, or TRUSTED with no calibrated bar at all, would certify
    extraction quality nobody actually checked — the whole point of the
    reliability gate is that TRUSTED means something.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    labels = [
        {"kpi_id": f"kpi_{i}", "period": "2024-Q1", "value": 100 + i}
        for i in range(20)
    ]
    kpi_gate_module.add_labels("EVALCO", labels)

    all_correct = [dict(label) for label in labels]

    # (a) all 20/20 correct, threshold 0.95 -> TRUSTED.
    record_a = kpi_gate_module.evaluate(
        "EVALCO", "v-a", all_correct, threshold=0.95, min_samples=5,
        evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record_a["verdict"] == "TRUSTED"
    assert record_a["metric"] == pytest.approx(1.0)
    assert record_a["sample_size"] == 20
    assert record_a["company"] == "EVALCO"
    assert record_a["schema_version"] == "v-a"
    assert record_a["evaluated_at"] == "2026-07-14T00:00:00Z"

    # (b) exactly 19/20 correct = 0.95 == threshold -> TRUSTED (inclusive).
    nineteen_correct = [dict(label) for label in labels]
    nineteen_correct[19]["value"] = labels[19]["value"] + 1_000_000
    record_b = kpi_gate_module.evaluate(
        "EVALCO", "v-b", nineteen_correct, threshold=0.95, min_samples=5,
        evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record_b["verdict"] == "TRUSTED"
    assert record_b["metric"] == pytest.approx(0.95)
    assert record_b["sample_size"] == 20

    # (c) 18/20 correct = 0.90 < threshold 0.95 -> WITHHELD.
    eighteen_correct = [dict(label) for label in labels]
    eighteen_correct[18]["value"] = labels[18]["value"] + 1_000_000
    eighteen_correct[19]["value"] = labels[19]["value"] + 1_000_000
    record_c = kpi_gate_module.evaluate(
        "EVALCO", "v-c", eighteen_correct, threshold=0.95, min_samples=5,
        evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record_c["verdict"] == "WITHHELD"
    assert record_c["metric"] == pytest.approx(0.90)
    assert record_c["sample_size"] == 20

    # (d) fewer than min_samples labeled cells -> NOT_EVALUATED regardless
    # of accuracy (all 3 correct here), because too few samples can never
    # earn a verdict.
    few_labels = [
        {"kpi_id": f"few_kpi_{i}", "period": "2024-Q1", "value": 1 + i}
        for i in range(3)
    ]
    kpi_gate_module.add_labels("EVALCO_FEW", few_labels)
    record_d = kpi_gate_module.evaluate(
        "EVALCO_FEW", "v-d", [dict(label) for label in few_labels],
        threshold=0.95, min_samples=5, evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record_d["verdict"] == "NOT_EVALUATED"
    assert record_d["sample_size"] == 3

    # (e) threshold=None (deferred calibration) with a full-samples,
    # all-correct set -> NOT_EVALUATED, never TRUSTED without a calibrated
    # bar — but the metric is still recorded.
    record_e = kpi_gate_module.evaluate(
        "EVALCO", "v-e", all_correct, threshold=None, min_samples=5,
        evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record_e["verdict"] == "NOT_EVALUATED"
    assert record_e["metric"] == pytest.approx(1.0)
    assert record_e["sample_size"] == 20


def test_evaluate_no_labels_min_samples_zero_not_trusted(kpi_gate_module, tmp_path, monkeypatch):
    """A company with ZERO ground-truth labels must never be TRUSTED, even
    if a caller passes `min_samples=0` and `threshold=0.0`.

    Why this matters: the verdict ladder gates on `sample_size < min_samples`
    — with `min_samples=0`, `0 < 0` is False, so the ladder falls through to
    the threshold comparison: `accuracy (0.0, from `0/0` guarded to 0.0)
    >= threshold (0.0)` is True -> TRUSTED, with NO ground truth ever
    checked. Task 4's CLI exposes `--min-samples`, so an operator could pass
    0 (accidentally or adversarially) and get a fabricated TRUSTED verdict
    on a company that was never evaluated at all. The gate must refuse to
    call anything TRUSTED without at least one real labeled cell.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    record = kpi_gate_module.evaluate(
        "NOLABELS", "v1", {}, threshold=0.0, min_samples=0,
        evaluated_at="2024-01-01",
    )
    assert record["verdict"] == "NOT_EVALUATED", (
        "zero labels must never earn TRUSTED, regardless of min_samples/threshold"
    )
    assert record["sample_size"] == 0


def test_missing_extraction_counts_incorrect(kpi_gate_module, tmp_path, monkeypatch):
    """A labeled `(kpi_id, period)` cell with NO matching entry in
    `extracted_values` must count as INCORRECT, not be skipped from the
    denominator — otherwise a partial extraction (fewer cells extracted
    than labeled) would inflate accuracy by shrinking the sample instead
    of penalizing the gap, letting an incomplete extractor slip past the
    gate as TRUSTED-by-omission.

    3 labeled cells, only 1 present in extracted_values (and correct) ->
    accuracy must be 1/3 (missing cells count as wrong), not 1/1.
    """
    monkeypatch.setenv("KPI_STORE_DIR", str(tmp_path))

    labels = [
        {"kpi_id": "revenue", "period": "2024-Q1", "value": 100},
        {"kpi_id": "revenue", "period": "2024-Q2", "value": 110},
        {"kpi_id": "revenue", "period": "2024-Q3", "value": 120},
    ]
    kpi_gate_module.add_labels("PARTIALCO", labels)

    # Only the first cell is present in extracted_values (and correct);
    # the other two labeled cells were never extracted at all.
    extracted_values = [
        {"kpi_id": "revenue", "period": "2024-Q1", "value": 100},
    ]

    record = kpi_gate_module.evaluate(
        "PARTIALCO", "v-partial", extracted_values, threshold=0.95, min_samples=3,
        evaluated_at="2026-07-14T00:00:00Z",
    )
    assert record["metric"] == pytest.approx(1 / 3), (
        "missing extractions must count as incorrect cells, not be skipped"
    )
    assert record["verdict"] == "WITHHELD", (
        "1/3 accuracy is well below a 0.95 threshold -> WITHHELD, never TRUSTED"
    )
    assert record["sample_size"] == 3
