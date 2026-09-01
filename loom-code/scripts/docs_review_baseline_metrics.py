"""Population-accounted quality metrics for the docs-review baseline."""
from __future__ import annotations

from collections.abc import Iterable, Mapping


FORMULA_VERSION = "docs-review-baseline-metrics-v1"


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
