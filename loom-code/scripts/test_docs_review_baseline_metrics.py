"""Tests for population-accounted docs-review baseline metrics."""
from __future__ import annotations

import pytest

from docs_review_baseline_metrics import (
    BaselineReportRegistry,
    PopulationManifestRegistry,
    calculate_population_report,
    calculate_quality_metrics,
    classify_population_boundaries,
    freeze_baseline_report,
)
from docs_review_baseline_store import RecordConflictError


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
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "false_positive",
                "oracle_matches": [],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "unknown",
                "oracle_matches": [],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
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
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "false_positive",
                "oracle_matches": [],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "unknown",
                "oracle_matches": [],
            },
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "disputed",
                "oracle_matches": [],
            },
        ],
        attempts=[
            {"attempt_id": "attempt-success", "outcome": "success"},
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

    invalid_bound = calculate_population_report(
        oracle={
            "kind": "ratified_oracle",
            "status": "ratified",
            "findings": [{"finding_id": "expected-risk", "load_bearing": True}],
        },
        attributions=[
            {
                "attempt_id": "attempt-success",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-success",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            },
            *[
                {
                    "attempt_id": attempt_id,
                    "kind": "attribution_revision",
                    "observation_attempt_id": attempt_id,
                    "status": "ratified",
                    "human_verdict": "false_positive",
                    "oracle_matches": [],
                }
                for attempt_id in (
                    "attempt-failed",
                    "attempt-malformed",
                    "attempt-unparseable",
                    "attempt-unscoreable",
                )
            ],
        ],
        attempts=[
            {"attempt_id": "attempt-success", "outcome": "success"},
            {"attempt_id": "attempt-failed", "outcome": "failed"},
            {"attempt_id": "attempt-malformed", "outcome": "malformed"},
            {"attempt_id": "attempt-unparseable", "outcome": "unparseable"},
            {"attempt_id": "attempt-unscoreable", "outcome": "unscoreable_model"},
        ],
    )

    assert invalid_bound["quality_metrics"]["false_alarm_rate"] == {
        "availability": "available",
        "denominator": 1,
        "exclusion_reasons": [],
        "formula_version": "docs-review-baseline-metrics-v1",
        "numerator": 0,
        "value": 0.0,
    }
    assert invalid_bound["population_counts"] == {
        "disputed_attributions": 0,
        "failed_attempts": 1,
        "interrupted_attempts": 0,
        "malformed_attempts": 1,
        "unknown_attributions": 0,
        "unparseable_attempts": 1,
        "unscoreable_model_attempts": 1,
    }

    unbound = calculate_population_report(
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
            }
        ],
        attempts=[
            {"attempt_id": "attempt-success", "outcome": "success"},
            {"attempt_id": "attempt-failed", "outcome": "failed"},
        ],
    )
    assert {
        name: metric["availability"]
        for name, metric in unbound["quality_metrics"].items()
    } == {"finding_rate": "unavailable", "false_alarm_rate": "unavailable"}
    assert unbound["population_counts"]["failed_attempts"] == 1

    duplicate_arguments = {
        "oracle": {
            "kind": "ratified_oracle",
            "status": "ratified",
            "findings": [{"finding_id": "expected-risk", "load_bearing": True}],
        },
        "attributions": [
            {
                "attempt_id": "attempt-duplicate",
                "kind": "attribution_revision",
                "observation_attempt_id": "attempt-duplicate",
                "status": "ratified",
                "human_verdict": "true_positive",
                "oracle_matches": ["expected-risk"],
            }
        ],
    }
    for attempts in (
        [
            {"attempt_id": "attempt-duplicate", "outcome": "success"},
            {"attempt_id": "attempt-duplicate", "outcome": "success"},
        ],
        [
            {"attempt_id": "attempt-duplicate", "outcome": "success"},
            {"attempt_id": "attempt-duplicate", "outcome": "failed"},
        ],
        [
            {"attempt_id": "attempt-duplicate", "outcome": "failed"},
            {"attempt_id": "attempt-duplicate", "outcome": "success"},
        ],
    ):
        with pytest.raises(ValueError, match="duplicate attempt_id"):
            calculate_population_report(**duplicate_arguments, attempts=attempts)


def test_req_108_baseline_reports_are_revision_bound(tmp_path) -> None:
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

    persisted = BaselineReportRegistry(tmp_path).freeze(baseline)
    assert BaselineReportRegistry(tmp_path).freeze(baseline).record == baseline
    assert persisted.record == baseline
    conflicting = {
        **baseline,
        "metrics": {**partial_metrics, "finding_rate": {**partial_metrics["finding_rate"], "value": 0.5}},
    }
    with pytest.raises(RecordConflictError):
        BaselineReportRegistry(tmp_path).freeze(conflicting)
    corrected_persisted = BaselineReportRegistry(tmp_path).freeze(corrected)
    assert corrected_persisted.record["report_id"] == "baseline-r2"
    assert corrected_persisted.record["parent_report_digest"]


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
    with pytest.raises(ValueError, match="outcome IDs"):
        classify_population_boundaries(
            expected_findings=["expected-a", "expected-b"],
            negative_control=None,
            normalization_state="valid_empty",
            expected_outcomes=[
                {"finding_id": "expected-a", "outcome": "missed"},
                {"finding_id": "expected-a", "outcome": "missed"},
            ],
        )
    with pytest.raises(ValueError, match="duplicate expected"):
        classify_population_boundaries(
            expected_findings=["expected-a", "expected-a"],
            negative_control=None,
            normalization_state="valid_empty",
            expected_outcomes=[
                {"finding_id": "expected-a", "outcome": "missed"},
            ],
        )


def test_req_117_report_population_is_frozen_before_calculation(tmp_path) -> None:
    # @req: REQ-117
    """One report id accepts one exact population, with incomplete cohorts partial."""
    registry = PopulationManifestRegistry(tmp_path)
    arguments = {
        "runs": [{"record_id": "run-1", "digest": "a" * 64}],
        "observations": [{"record_id": "observation-1", "digest": "b" * 64}],
        "attribution_revisions": [
            {"record_id": "attribution-1", "digest": "c" * 64}
        ],
        "parser_revision": "parser-r1",
        "metric_definition_revision": "metrics-r1",
        "cohorts": {
            "claude": {"valid_repeats": 1},
            "codex": {"valid_repeats": 2},
        },
        "repeat_target": 2,
    }

    first = registry.freeze("report-r1", **arguments)

    assert PopulationManifestRegistry(tmp_path).freeze("report-r1", **arguments) == first
    assert first["runs"] == arguments["runs"]
    assert first["observations"] == arguments["observations"]
    assert first["attribution_revisions"] == arguments["attribution_revisions"]
    assert first["cohort_availability"] == {
        "claude": {"availability": "unavailable", "valid_repeats": 1},
        "codex": {"availability": "available", "valid_repeats": 2},
    }
    assert first["cross_host_conclusion"] == {
        "availability": "unavailable",
        "exclusion_reasons": ["incomplete_repeat_cohorts:claude"],
    }
    assert first["status"] == "partial"

    with pytest.raises(RecordConflictError):
        PopulationManifestRegistry(tmp_path).freeze(
            "report-r1",
            **{**arguments, "attribution_revisions": [{"record_id": "attribution-2", "digest": "d" * 64}]},
        )

    corrected = PopulationManifestRegistry(tmp_path).freeze(
        "report-r2",
        **{**arguments, "attribution_revisions": [{"record_id": "attribution-2", "digest": "d" * 64}]},
        parent_report_id="report-r1",
    )

    assert corrected["parent_manifest_digest"] == first["manifest_digest"]
    assert corrected["lineage_root_report_id"] == "report-r1"
    assert first["attribution_revisions"] == arguments["attribution_revisions"]
