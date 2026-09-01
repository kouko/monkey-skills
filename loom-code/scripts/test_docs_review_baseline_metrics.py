"""Tests for population-accounted docs-review baseline metrics."""
from __future__ import annotations

from docs_review_baseline_metrics import calculate_quality_metrics


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
