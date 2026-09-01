"""Population-accounted quality metrics for the docs-review baseline."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json
from pathlib import Path
from threading import Lock

from docs_review_baseline_store import PublishedRecord, publish_record, read_record


FORMULA_VERSION = "docs-review-baseline-metrics-v1"

_REPORT_REVISION_KEYS = (
    "corpus",
    "oracle",
    "attribution",
    "reviewer_contract",
    "reviewer_runtime",
    "parser",
    "execution_profile",
    "metric_definition",
)

_NORMALIZATION_BOUNDARY_STATES = {
    "explicit_no_findings",
    "valid_empty",
    "suspicious_empty",
    "extraction_failure",
    "mixed_parse",
    "partial_output",
}


def _canonical_digest(value: object) -> str:
    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    return value


def _metric(
    *,
    numerator: int | None,
    denominator: int | None,
    exclusion_reasons: list[str],
) -> dict[str, object]:
    """Return one metric with its complete arithmetic population."""
    available = denominator is not None and denominator > 0
    return {
        "availability": "available" if available else "unavailable",
        "denominator": denominator if available else None,
        "exclusion_reasons": exclusion_reasons,
        "formula_version": FORMULA_VERSION,
        "numerator": numerator if available else None,
        "value": numerator / denominator if available else None,
    }


def _ratified_attributions(
    attributions: Iterable[Mapping[str, object]],
) -> list[Mapping[str, object]]:
    return [
        attribution
        for attribution in attributions
        if attribution.get("kind") == "attribution_revision"
        and attribution.get("status") == "ratified"
    ]


def calculate_quality_metrics(
    *,
    oracle: Mapping[str, object],
    attributions: Iterable[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    """Calculate finding and false-alarm rates from frozen input records.

    Only ratified oracle findings and ratified human attributions form the
    reported populations. Unknown and disputed observations stay visible as
    explicit false-alarm exclusions instead of entering that denominator.
    """
    findings = oracle.get("findings")
    if (
        oracle.get("kind") != "ratified_oracle"
        or oracle.get("status") != "ratified"
        or not isinstance(findings, list)
    ):
        findings = []

    expected = [
        finding["finding_id"]
        for finding in findings
        if isinstance(finding, Mapping)
        and finding.get("load_bearing", True) is True
        and isinstance(finding.get("finding_id"), str)
    ]
    non_load_bearing = sum(
        1
        for finding in findings
        if isinstance(finding, Mapping) and finding.get("load_bearing") is False
    )
    ratified = _ratified_attributions(attributions)

    finding_exclusions = []
    if non_load_bearing:
        finding_exclusions.append(
            f"non_load_bearing_expected_findings:{non_load_bearing}"
        )
    if not expected:
        finding_exclusions.append("expected_load_bearing_population_unavailable")
        finding_rate = _metric(
            numerator=None,
            denominator=None,
            exclusion_reasons=finding_exclusions,
        )
    else:
        matched = {
            match
            for attribution in ratified
            if attribution.get("human_verdict") == "true_positive"
            for match in attribution.get("oracle_matches", [])
            if isinstance(match, str) and match in expected
        }
        finding_rate = _metric(
            numerator=len(matched),
            denominator=len(expected),
            exclusion_reasons=finding_exclusions,
        )

    false_alarm_population = [
        attribution
        for attribution in ratified
        if attribution.get("human_verdict") in {"true_positive", "false_positive"}
    ]
    false_alarm_exclusions = [
        f"{verdict}_observations:{sum(1 for attribution in ratified if attribution.get('human_verdict') == verdict)}"
        for verdict in ("unknown", "disputed")
        if any(attribution.get("human_verdict") == verdict for attribution in ratified)
    ]
    if not false_alarm_population:
        false_alarm_exclusions.append("ratified_false_alarm_population_unavailable")
        false_alarm_rate = _metric(
            numerator=None,
            denominator=None,
            exclusion_reasons=false_alarm_exclusions,
        )
    else:
        false_alarm_rate = _metric(
            numerator=sum(
                attribution.get("human_verdict") == "false_positive"
                for attribution in false_alarm_population
            ),
            denominator=len(false_alarm_population),
            exclusion_reasons=false_alarm_exclusions,
        )

    return {
        "finding_rate": finding_rate,
        "false_alarm_rate": false_alarm_rate,
    }


_INVALID_OUTCOMES = {
    "failed": "failed_attempts",
    "interrupted": "interrupted_attempts",
    "malformed": "malformed_attempts",
    "unparseable": "unparseable_attempts",
    "unscoreable_model": "unscoreable_model_attempts",
}


def _usage_populations(
    attempts: Iterable[Mapping[str, object]],
) -> dict[str, dict[str, object]]:
    populations: dict[str, dict[str, object]] = {}
    for attempt in attempts:
        usage = attempt.get("usage")
        if not isinstance(usage, Mapping):
            continue
        provider = usage.get("provider")
        unit = usage.get("unit")
        value = usage.get("value")
        if (
            not isinstance(provider, str)
            or not isinstance(unit, str)
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            continue
        key = f"{provider}:{unit}"
        population = populations.setdefault(
            key,
            {
                "availability": "available",
                "count": 0,
                "provider": provider,
                "total": 0,
                "unit": unit,
            },
        )
        population["count"] += 1
        population["total"] += value
    return populations


def _quality_eligible_attributions(
    attributions: list[Mapping[str, object]],
    attempts: list[Mapping[str, object]],
) -> list[Mapping[str, object]]:
    """Keep quality rates bound to successful, observation-matched attempts."""
    outcomes = {
        attempt["attempt_id"]: attempt.get("outcome")
        for attempt in attempts
        if isinstance(attempt.get("attempt_id"), str)
    }
    bound = any(
        "attempt_id" in attribution or "observation_attempt_id" in attribution
        for attribution in attributions
    )
    if not bound:
        return attributions
    return [
        attribution
        for attribution in attributions
        if isinstance(attribution.get("attempt_id"), str)
        and attribution.get("attempt_id")
        == attribution.get("observation_attempt_id")
        and outcomes.get(attribution["attempt_id"]) == "success"
    ]


def calculate_population_report(
    *,
    oracle: Mapping[str, object],
    attributions: Iterable[Mapping[str, object]],
    attempts: Iterable[Mapping[str, object]],
) -> dict[str, object]:
    """Report quality metrics beside every excluded run and usage population."""
    attribution_records = list(attributions)
    attempt_records = list(attempts)
    ratified = _ratified_attributions(attribution_records)
    population_counts = {
        count_name: sum(
            attempt.get("outcome") == outcome for attempt in attempt_records
        )
        for outcome, count_name in _INVALID_OUTCOMES.items()
    }
    population_counts.update(
        {
            "unknown_attributions": sum(
                attribution.get("human_verdict") == "unknown"
                for attribution in ratified
            ),
            "disputed_attributions": sum(
                attribution.get("human_verdict") == "disputed"
                for attribution in ratified
            ),
        }
    )
    return {
        "quality_metrics": calculate_quality_metrics(
            oracle=oracle,
            attributions=_quality_eligible_attributions(
                attribution_records, attempt_records
            ),
        ),
        "population_counts": dict(sorted(population_counts.items())),
        "usage_populations": _usage_populations(attempt_records),
    }


def freeze_baseline_report(
    *,
    report_id: str,
    metrics: Mapping[str, Mapping[str, object]],
    revisions: Mapping[str, str],
    limitations: list[str],
    parent: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Freeze one revision-bound report without mutating any earlier report."""
    report_id = _required_text(report_id, "report_id")
    frozen_revisions = {
        key: _required_text(revisions.get(key), f"{key} revision")
        for key in _REPORT_REVISION_KEYS
    }
    if not isinstance(limits := limitations, list) or any(
        not isinstance(limit, str) or not limit.strip() for limit in limits
    ):
        raise ValueError("limitations must be a list of non-empty strings")
    frozen_metrics = json.loads(json.dumps(metrics, ensure_ascii=False))
    unavailable = [
        name
        for name, metric in frozen_metrics.items()
        if isinstance(metric, Mapping)
        and metric.get("availability") == "unavailable"
    ]
    for name in unavailable:
        metric = frozen_metrics[name]
        if (
            metric.get("value") is not None
            or metric.get("denominator") is not None
            or not isinstance(metric.get("exclusion_reasons"), list)
            or not metric["exclusion_reasons"]
        ):
            raise ValueError(f"unavailable metric {name} lacks explicit population")
    if unavailable and not limits:
        raise ValueError("partial report requires limitations")

    parent_digest: str | None = None
    lineage_root = report_id
    if parent is not None:
        parent_id = _required_text(parent.get("report_id"), "parent report_id")
        if report_id == parent_id:
            raise ValueError("revision changes require a new report_id")
        parent_digest = _canonical_digest(parent)
        lineage_root = _required_text(
            parent.get("lineage_root_report_id"), "parent lineage_root_report_id"
        )

    return {
        "kind": "baseline_metric_report",
        "limitations": list(limits),
        "lineage_root_report_id": lineage_root,
        "metrics": frozen_metrics,
        "parent_report_digest": parent_digest,
        "report_id": report_id,
        "revisions": frozen_revisions,
        "schema_version": 1,
        "status": "partial" if unavailable else "complete",
    }


class BaselineReportRegistry:
    """Persist frozen report bytes through the shared append-only store."""

    def __init__(self, store_root: Path) -> None:
        self._store_root = Path(store_root)

    def freeze(self, report: Mapping[str, object]) -> PublishedRecord:
        """Publish one report ID once; equal retries succeed, drift is refused."""
        if report.get("kind") != "baseline_metric_report":
            raise ValueError("report must be a baseline_metric_report")
        report_id = _required_text(report.get("report_id"), "report_id")
        parent_digest = report.get("parent_report_digest")
        lineage_root = _required_text(
            report.get("lineage_root_report_id"), "lineage_root_report_id"
        )
        if report_id == lineage_root and parent_digest is not None:
            raise ValueError("root report must not bind a parent digest")
        if report_id != lineage_root and not isinstance(parent_digest, str):
            raise ValueError("corrected report requires a parent digest")
        return publish_record(self._store_root, report_id, report)


def classify_population_boundaries(
    *,
    expected_findings: list[str],
    negative_control: Mapping[str, object] | None,
    normalization_state: str,
    expected_outcomes: list[Mapping[str, str]],
) -> dict[str, object]:
    """Keep zero, empty, partial, and unmatched finding populations distinct."""
    if normalization_state not in _NORMALIZATION_BOUNDARY_STATES:
        raise ValueError(f"unsupported normalization state: {normalization_state}")
    if any(not isinstance(finding, str) or not finding.strip() for finding in expected_findings):
        raise ValueError("expected findings must be non-empty strings")
    expected = set(expected_findings)
    if len(expected) != len(expected_findings):
        raise ValueError("duplicate expected finding IDs are not allowed")
    frozen_outcomes: list[dict[str, str]] = []
    outcome_ids: set[str] = set()
    for outcome in expected_outcomes:
        finding_id = outcome.get("finding_id")
        status = outcome.get("outcome")
        if finding_id not in expected or status not in {"missed", "not_assessable"}:
            raise ValueError("expected finding outcome must be missed or not_assessable")
        if finding_id in outcome_ids:
            raise ValueError("duplicate expected outcome IDs are not allowed")
        outcome_ids.add(finding_id)
        frozen_outcomes.append({"finding_id": finding_id, "outcome": status})
    if outcome_ids != expected:
        raise ValueError("expected outcome IDs must exactly equal expected finding IDs")

    if not expected:
        if negative_control is None:
            population_state = "unlabeled_zero_expected"
            availability = "unavailable"
            exclusion_reasons = ["zero_expected_findings_not_ratified_negative_control"]
        else:
            if (
                negative_control.get("status") != "ratified"
                or not isinstance(negative_control.get("rationale"), str)
                or not negative_control["rationale"].strip()
                or not isinstance(negative_control.get("scope"), str)
                or not negative_control["scope"].strip()
            ):
                raise ValueError("negative control requires ratified rationale and scope")
            population_state = "negative_control"
            availability = "not_applicable"
            exclusion_reasons = ["ratified_negative_control_zero_expected"]
        return {
            "expected_finding_outcomes": frozen_outcomes,
            "finding_rate": {
                "availability": availability,
                "denominator": 0,
                "exclusion_reasons": exclusion_reasons,
                "formula_version": FORMULA_VERSION,
                "numerator": None,
                "value": None,
            },
            "normalization_state": normalization_state,
            "population_state": population_state,
        }

    return {
        "expected_finding_outcomes": frozen_outcomes,
        "finding_rate": {
            "availability": "unavailable",
            "denominator": len(expected),
            "exclusion_reasons": [f"normalization_state:{normalization_state}"],
            "formula_version": FORMULA_VERSION,
            "numerator": None,
            "value": None,
        },
        "normalization_state": normalization_state,
        "population_state": normalization_state,
    }


def _identity_records(
    records: list[Mapping[str, str]], name: str
) -> list[dict[str, str]]:
    frozen: list[dict[str, str]] = []
    identities: set[str] = set()
    for record in records:
        record_id = _required_text(record.get("record_id"), f"{name} record_id")
        digest = _required_text(record.get("digest"), f"{name} digest")
        if record_id in identities:
            raise ValueError(f"duplicate {name} record_id: {record_id}")
        identities.add(record_id)
        frozen.append({"record_id": record_id, "digest": digest})
    return frozen


class PopulationManifestRegistry:
    """Atomically freeze one exact input population in the append-only store."""

    def __init__(self, store_root: Path) -> None:
        self._store_root = Path(store_root)
        self._lock = Lock()

    def freeze(
        self,
        report_id: str,
        *,
        runs: list[Mapping[str, str]],
        observations: list[Mapping[str, str]],
        attribution_revisions: list[Mapping[str, str]],
        parser_revision: str,
        metric_definition_revision: str,
        cohorts: Mapping[str, Mapping[str, int]],
        repeat_target: int,
        parent_report_id: str | None = None,
    ) -> dict[str, object]:
        """Return the single accepted manifest, or refuse different bytes."""
        report_id = _required_text(report_id, "report_id")
        if not isinstance(repeat_target, int) or repeat_target < 1:
            raise ValueError("repeat_target must be a positive integer")
        if not cohorts:
            raise ValueError("cohorts are required")
        cohort_availability: dict[str, dict[str, object]] = {}
        incomplete: list[str] = []
        for cohort, evidence in sorted(cohorts.items()):
            cohort = _required_text(cohort, "cohort")
            repeats = evidence.get("valid_repeats")
            if not isinstance(repeats, int) or repeats < 0:
                raise ValueError("valid_repeats must be a non-negative integer")
            available = repeats >= repeat_target
            cohort_availability[cohort] = {
                "availability": "available" if available else "unavailable",
                "valid_repeats": repeats,
            }
            if not available:
                incomplete.append(cohort)

        candidate: dict[str, object] = {
            "attribution_revisions": _identity_records(
                attribution_revisions, "attribution revision"
            ),
            "cohort_availability": cohort_availability,
            "cross_host_conclusion": {
                "availability": "unavailable" if incomplete else "available",
                "exclusion_reasons": [
                    f"incomplete_repeat_cohorts:{','.join(incomplete)}"
                ]
                if incomplete
                else [],
            },
            "kind": "report_population_manifest",
            "lineage_root_report_id": report_id,
            "metric_definition_revision": _required_text(
                metric_definition_revision, "metric_definition_revision"
            ),
            "observations": _identity_records(observations, "observation"),
            "parent_manifest_digest": None,
            "parser_revision": _required_text(parser_revision, "parser_revision"),
            "report_id": report_id,
            "runs": _identity_records(runs, "run"),
            "schema_version": 1,
            "status": "partial" if incomplete else "complete",
        }
        with self._lock:
            if parent_report_id is not None:
                parent_report_id = _required_text(parent_report_id, "parent_report_id")
                if parent_report_id == report_id:
                    raise ValueError("corrected population requires a new report_id")
                try:
                    parent = read_record(self._store_root, parent_report_id)
                except ValueError as error:
                    raise ValueError("parent report manifest does not exist") from error
                if parent.record.get("kind") != "report_population_manifest":
                    raise ValueError("parent record is not a population manifest")
                candidate["lineage_root_report_id"] = parent.record[
                    "lineage_root_report_id"
                ]
                candidate["parent_manifest_digest"] = parent.record["manifest_digest"]
            candidate_digest = _canonical_digest(candidate)
            candidate["manifest_digest"] = candidate_digest
            published = publish_record(self._store_root, report_id, candidate)
            return json.loads(json.dumps(published.record))
