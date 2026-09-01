"""Population-accounted quality metrics for the docs-review baseline."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json


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
            attributions=attribution_records,
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
