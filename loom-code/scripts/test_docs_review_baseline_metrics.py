"""Tests for population-accounted docs-review baseline metrics."""
from __future__ import annotations

import pytest

from docs_review_baseline_metrics import (
    calculate_population_report,
    calculate_quality_metrics,
    classify_population_boundaries,
    freeze_baseline_report,
)


def test_req_106_every_metric_carries_its_population() -> None:
    # @req: REQ-106
    """Quality rates retain their arithmetic and never turn absent populations into zero."""
    complete = calculate_quality_metrics(
        oracle={
            "kind": "ratified_oracle",
            "status": "ratified",
            "findings": [
                {"finding_id": "expected-risk", "load_bearing": True},
                {"finding_id": "expected-style", "load_bearing": False},
            ],
        },
        attributions=[
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "false_positive",
                "oracle_matches": [],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "unknown",
                "oracle_matches": [],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "disputed",
                "oracle_matches": [],
            },
        ],
    )

    assert complete == {
        "finding_rate": {
            "availability": "available",
            "denominator": 1,
            "exclusion_reasons": ["non_load_bearing_expected_findings:1"],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": 1,
            "value": 1.0,
        },
        "false_alarm_rate": {
            "availability": "available",
            "denominator": 2,
            "exclusion_reasons": [
                "unknown_observations:1",
                "disputed_observations:1",
            ],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": 1,
            "value": 0.5,
        },
    }

    unavailable = calculate_quality_metrics(
        oracle={"kind": "ratified_oracle", "status": "ratified", "findings": []},
        attributions=[],
    )

    assert unavailable == {
        "finding_rate": {
            "availability": "unavailable",
            "denominator": None,
            "exclusion_reasons": ["expected_load_bearing_population_unavailable"],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": None,
            "value": None,
        },
        "false_alarm_rate": {
            "availability": "unavailable",
            "denominator": None,
            "exclusion_reasons": ["ratified_false_alarm_population_unavailable"],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": None,
            "value": None,
        },
    }


def test_req_107_invalid_and_unknown_populations_stay_visible() -> None:
    # @req: REQ-107
    """Invalid runs and incompatible usage stay outside, but visible beside, rates."""
    report = calculate_population_report(
        oracle={
            "kind": "ratified_oracle",
            "status": "ratified",
            "findings": [{"finding_id": "expected-risk", "load_bearing": True}],
        },
        attributions=[
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "false_positive",
                "oracle_matches": [],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "unknown",
                "oracle_matches": [],
            },
            {
                "kind": "attribution_revision",
                "status": "ratified",
                "human_verdict": "disputed",
                "oracle_matches": [],
            },
        ],
        attempts=[
            {"outcome": "failed", "usage": {"provider": "codex", "unit": "tokens", "value": 13}},
            {"outcome": "interrupted"},
            {"outcome": "malformed"},
            {"outcome": "unparseable"},
            {"outcome": "unscoreable_model", "usage": {"provider": "claude", "unit": "seconds", "value": 4}},
        ],
    )

    assert report["quality_metrics"] == {
        "finding_rate": {
            "availability": "available",
            "denominator": 1,
            "exclusion_reasons": [],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": 1,
            "value": 1.0,
        },
        "false_alarm_rate": {
            "availability": "available",
            "denominator": 2,
            "exclusion_reasons": [
                "unknown_observations:1",
                "disputed_observations:1",
            ],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": 1,
            "value": 0.5,
        },
    }
    assert report["population_counts"] == {
        "disputed_attributions": 1,
        "failed_attempts": 1,
        "interrupted_attempts": 1,
        "malformed_attempts": 1,
        "unknown_attributions": 1,
        "unparseable_attempts": 1,
        "unscoreable_model_attempts": 1,
    }
    assert report["usage_populations"] == {
        "claude:seconds": {
            "availability": "available",
            "count": 1,
            "provider": "claude",
            "total": 4,
            "unit": "seconds",
        },
        "codex:tokens": {
            "availability": "available",
            "count": 1,
            "provider": "codex",
            "total": 13,
            "unit": "tokens",
        },
    }


def test_req_108_baseline_reports_are_revision_bound() -> None:
    # @req: REQ-108
    """A frozen baseline names every input revision and corrections make a child."""
    revisions = {
        "attribution": "attribution-r1",
        "corpus": "corpus-r1",
        "execution_profile": "profile-r1",
        "metric_definition": "metrics-r1",
        "oracle": "oracle-r1",
        "parser": "parser-r1",
        "reviewer_contract": "contract-r1",
        "reviewer_runtime": "runtime-r1",
    }
    partial_metrics = {
        "finding_rate": {
            "availability": "available",
            "denominator": 1,
            "exclusion_reasons": [],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": 1,
            "value": 1.0,
        },
        "elapsed_time": {
            "availability": "unavailable",
            "denominator": None,
            "exclusion_reasons": ["elapsed_telemetry_unavailable"],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": None,
            "value": None,
        },
    }

    baseline = freeze_baseline_report(
        report_id="baseline-r1",
        metrics=partial_metrics,
        revisions=revisions,
        limitations=["elapsed telemetry unavailable for one valid run"],
    )

    assert baseline == {
        "kind": "baseline_metric_report",
        "limitations": ["elapsed telemetry unavailable for one valid run"],
        "lineage_root_report_id": "baseline-r1",
        "metrics": partial_metrics,
        "parent_report_digest": None,
        "report_id": "baseline-r1",
        "revisions": revisions,
        "schema_version": 1,
        "status": "partial",
    }

    with pytest.raises(ValueError, match="parser"):
        freeze_baseline_report(
            report_id="baseline-missing-parser",
            metrics=partial_metrics,
            revisions={key: value for key, value in revisions.items() if key != "parser"},
            limitations=["elapsed telemetry unavailable for one valid run"],
        )

    corrected = freeze_baseline_report(
        report_id="baseline-r2",
        metrics=partial_metrics,
        revisions={**revisions, "oracle": "oracle-r2"},
        limitations=["elapsed telemetry unavailable for one valid run"],
        parent=baseline,
    )

    assert corrected["parent_report_digest"]
    assert corrected["lineage_root_report_id"] == "baseline-r1"
    assert corrected["revisions"]["oracle"] == "oracle-r2"
    assert baseline["revisions"]["oracle"] == "oracle-r1"
    with pytest.raises(ValueError, match="new report_id"):
        freeze_baseline_report(
            report_id="baseline-r1",
            metrics=partial_metrics,
            revisions={**revisions, "oracle": "oracle-r2"},
            limitations=["elapsed telemetry unavailable for one valid run"],
            parent=baseline,
        )


def test_req_116_zero_and_partial_populations_have_explicit_meaning() -> None:
    # @req: REQ-116
    """No empty, partial, or unmatched population becomes a zero-percent rate."""
    negative_control = classify_population_boundaries(
        expected_findings=[],
        negative_control={
            "rationale": "A deliberately clean document checks generic alarms.",
            "scope": "case-negative-control",
            "status": "ratified",
        },
        normalization_state="valid_empty",
        expected_outcomes=[],
    )
    unlabeled_zero_expected = classify_population_boundaries(
        expected_findings=[],
        negative_control=None,
        normalization_state="valid_empty",
        expected_outcomes=[],
    )
    response_states = {
        state: classify_population_boundaries(
            expected_findings=["expected-risk"],
            negative_control=None,
            normalization_state=state,
            expected_outcomes=[
                {"finding_id": "expected-risk", "outcome": "missed"}
            ],
        )
        for state in (
            "explicit_no_findings",
            "valid_empty",
            "suspicious_empty",
            "extraction_failure",
            "mixed_parse",
            "partial_output",
        )
    }
    not_assessable = classify_population_boundaries(
        expected_findings=["expected-risk"],
        negative_control=None,
        normalization_state="partial_output",
        expected_outcomes=[
            {"finding_id": "expected-risk", "outcome": "not_assessable"}
        ],
    )

    assert negative_control == {
        "expected_finding_outcomes": [],
        "finding_rate": {
            "availability": "not_applicable",
            "denominator": 0,
            "exclusion_reasons": ["ratified_negative_control_zero_expected"],
            "formula_version": "docs-review-baseline-metrics-v1",
            "numerator": None,
            "value": None,
        },
        "normalization_state": "valid_empty",
        "population_state": "negative_control",
    }
    assert unlabeled_zero_expected["population_state"] == "unlabeled_zero_expected"
    assert unlabeled_zero_expected["finding_rate"]["denominator"] == 0
    assert unlabeled_zero_expected["finding_rate"]["value"] is None
    assert set(response_states) == {
        "explicit_no_findings",
        "valid_empty",
        "suspicious_empty",
        "extraction_failure",
        "mixed_parse",
        "partial_output",
    }
    assert all(
        result["population_state"] == state
        and result["finding_rate"]["value"] is None
        and result["finding_rate"]["numerator"] is None
        for state, result in response_states.items()
    )
    assert response_states["valid_empty"]["expected_finding_outcomes"] == [
        {"finding_id": "expected-risk", "outcome": "missed"}
    ]
    assert not_assessable["expected_finding_outcomes"] == [
        {"finding_id": "expected-risk", "outcome": "not_assessable"}
    ]
