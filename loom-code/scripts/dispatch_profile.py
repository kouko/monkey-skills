#!/usr/bin/env python3
"""Pure host-neutral resolver for Loom subagent dispatch profiles.

Read one observed-state JSON object from stdin and write one deterministic JSON
decision to stdout.  Product model names and provider calls belong to the host
adapter; this module operates only on portable tiers and verified capabilities.
"""

from __future__ import annotations

import json
import sys
from typing import Any


MODELS = ("economy", "standard", "frontier")
EFFORTS = ("low", "medium", "high", "xhigh", "max")
MECHANICAL_FIELDS = ("exact_transformation", "bounded_targets", "mechanical_oracle")
COMPLEX_FIELDS = (
    "changed_consumed_interface",
    "multiple_plausible_causes",
    "trust_boundary",
    "irreversible_decision",
    "inconsistent_evidence",
)
HIGH_TRIGGERS = {
    "blocker-survived-substantive-fix",
    "mutually-exclusive-conclusions",
    "high-risk-decision-unsettled",
    "round-3-redesign-adjudication",
    "unresolved-multi-step-security-chain",
}
XHIGH_TRIGGERS = {
    "same-high-risk-blocker-with-artifact",
    "mutually-exclusive-frontier-high-conclusions",
}
NON_ROUTING_FAILURES = {
    "host-unavailable", "timeout", "malformed-response", "missing-input",
    "transient-executor",
}
FAILURE_KINDS = {"capability-quality", "reasoning-depth", *NON_ROUTING_FAILURES}


class InputError(ValueError):
    """The observed-state packet is malformed rather than merely unsupported."""


def _require_object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{name} must be an object")
    return value


def _fallback(reason: str, inheritance_guaranteed: bool, *, outcome: str = "dispatch",
              count: int = 0, task_class: str | None = None,
              uncertainty: str | None = None) -> dict[str, Any]:
    return {
        "task_class": task_class,
        "uncertainty": uncertainty,
        "requested_profile": None,
        "overrides": None,
        "effective_profile": (
            "inherited" if inheritance_guaranteed else "host-default/unverified"
        ),
        "outcome": outcome,
        "reason": reason,
        "completed_redispatches": count,
    }


def _classify(evidence: Any) -> tuple[str, str | None]:
    if evidence is None:
        return "ordinary", "insufficient-task-evidence"
    evidence = _require_object(evidence, "task_evidence")
    allowed = set(MECHANICAL_FIELDS + COMPLEX_FIELDS)
    if set(evidence) - allowed:
        raise InputError("task_evidence contains unknown fields")
    if any(type(value) is not bool for value in evidence.values()):
        raise InputError("task evidence values must be booleans")
    if all(evidence.get(field, False) for field in MECHANICAL_FIELDS):
        return "mechanical", None
    if any(evidence.get(field, False) for field in COMPLEX_FIELDS):
        return "complex", None
    return "ordinary", None


def _capabilities(packet: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    raw = _require_object(packet.get("capabilities"), "capabilities")
    result: dict[str, tuple[str, ...]] = {}
    for model, efforts in raw.items():
        if model not in MODELS or not isinstance(efforts, list):
            raise InputError("capabilities must map portable model tiers to effort arrays")
        if not efforts or any(not isinstance(effort, str) or not effort for effort in efforts):
            raise InputError("capability efforts must be non-empty strings")
        if len(efforts) != len(set(efforts)):
            raise InputError("capability efforts must be unique")
        result[model] = tuple(efforts)
    return result


def _supported(profile: dict[str, str], capabilities: dict[str, tuple[str, ...]]) -> bool:
    return profile["model"] in capabilities and profile["effort"] in capabilities[profile["model"]]


def _decision(profile: dict[str, str], capabilities: dict[str, tuple[str, ...]],
              inheritance_guaranteed: bool, *, reason: str, count: int,
              task_class: str | None = None, uncertainty: str | None = None) -> dict[str, Any]:
    if not _supported(profile, capabilities):
        result = _fallback(
            "unsupported-profile", inheritance_guaranteed, count=count,
            task_class=task_class, uncertainty=uncertainty,
        )
        result["requested_profile"] = profile
        return result
    return {
        "task_class": task_class,
        "uncertainty": uncertainty,
        "requested_profile": profile,
        "overrides": profile.copy(),
        "effective_profile": profile.copy(),
        "outcome": "dispatch",
        "reason": reason,
        "completed_redispatches": count,
    }


def _initial(packet: dict[str, Any], capabilities: dict[str, tuple[str, ...]],
             inheritance_guaranteed: bool, count: int) -> dict[str, Any]:
    task_class, uncertainty = _classify(packet.get("task_evidence"))
    main = _require_object(packet.get("main_profile"), "main_profile")
    if set(main) != {"model", "effort"}:
        raise InputError("main_profile must contain exactly model and effort")
    model, effort = main.get("model"), main.get("effort")
    if model not in MODELS or not isinstance(effort, str):
        return _fallback(
            "unobservable-main-profile", inheritance_guaranteed, count=count,
            task_class=task_class, uncertainty=uncertainty,
        )
    # A non-portable effort is observable only when the host verified it for
    # the main model.  It may be preserved but never participates in arithmetic.
    if effort not in EFFORTS and effort not in capabilities.get(model, ()):
        return _fallback(
            "unobservable-main-profile", inheritance_guaranteed, count=count,
            task_class=task_class, uncertainty=uncertainty,
        )

    model_index = MODELS.index(model)
    target_model = model
    target_effort = effort
    if task_class == "mechanical":
        target_model = MODELS[max(0, model_index - 1)]
    elif task_class == "complex" and model != "frontier":
        target_model = MODELS[model_index + 1]
    elif task_class == "complex" and effort in ("low", "medium"):
        target_effort = "medium"
    # high, xhigh, max, and verified host-native values are inherited unchanged.
    profile = {"model": target_model, "effort": target_effort}
    return _decision(
        profile, capabilities, inheritance_guaranteed, reason=f"initial-{task_class}",
        count=count, task_class=task_class, uncertainty=uncertainty,
    )


def _after_execution(packet: dict[str, Any], capabilities: dict[str, tuple[str, ...]],
                     inheritance_guaranteed: bool, count: int) -> dict[str, Any]:
    attempt = _require_object(packet.get("last_attempt"), "last_attempt")
    required = {"completed", "success", "conforming", "profile"}
    if not required.issubset(attempt) or any(type(attempt[key]) is not bool for key in required - {"profile"}):
        raise InputError("last_attempt lacks typed execution observations")
    profile = _require_object(attempt["profile"], "last_attempt.profile")
    if set(profile) != {"model", "effort"} or profile["model"] not in MODELS:
        raise InputError("last_attempt.profile is not a portable model-effort pair")
    actual = {"model": profile["model"], "effort": profile["effort"]}
    if attempt["completed"] and attempt["success"] and attempt["conforming"]:
        return {
            "task_class": None, "uncertainty": None, "requested_profile": actual,
            "overrides": actual.copy(), "effective_profile": actual,
            "outcome": "routed", "reason": "execution-succeeded",
            "completed_redispatches": count,
        }
    kind = attempt.get("failure_kind")
    if kind is not None and kind not in FAILURE_KINDS:
        raise InputError("last_attempt.failure_kind is unknown")
    if not attempt["completed"] or count >= 2:
        return {
            "task_class": None, "uncertainty": None, "requested_profile": None,
            "overrides": None, "effective_profile": actual,
            "outcome": "execution-failed", "reason": "no-legal-redispatch",
            "completed_redispatches": count,
        }
    if not attempt["conforming"]:
        if kind == "malformed-response":
            result = _decision(
                actual, capabilities, inheritance_guaranteed,
                reason="nonconforming-output-redispatch", count=count,
            )
            result["next_redispatch"] = count + 1
            return result
        return {
            "task_class": None, "uncertainty": None, "requested_profile": None,
            "overrides": None, "effective_profile": actual,
            "outcome": "execution-failed",
            "reason": (
                "non-routing-failure"
                if kind in NON_ROUTING_FAILURES else "no-legal-redispatch"
            ),
            "completed_redispatches": count,
        }

    if kind not in FAILURE_KINDS:
        raise InputError("last_attempt.failure_kind is unknown")
    if kind in NON_ROUTING_FAILURES:
        return {
            "task_class": None, "uncertainty": None, "requested_profile": None,
            "overrides": None, "effective_profile": actual,
            "outcome": "execution-failed", "reason": "non-routing-failure",
            "completed_redispatches": count,
        }
    model, effort = actual["model"], actual["effort"]
    next_profile: dict[str, str] | None = None
    if kind == "capability-quality" and model != "frontier":
        next_profile = {"model": MODELS[MODELS.index(model) + 1], "effort": effort}
    elif effort == "low" and (
        kind == "reasoning-depth"
        or (kind == "capability-quality" and model == "frontier")
    ):
        next_profile = {"model": model, "effort": "medium"}
    elif model == "frontier" and effort == "medium" and attempt.get("failure_trigger") in HIGH_TRIGGERS:
        next_profile = {"model": model, "effort": "high"}
    elif model == "frontier" and effort == "high" and attempt.get("failure_trigger") in XHIGH_TRIGGERS:
        next_profile = {"model": model, "effort": "xhigh"}

    if next_profile is None:
        return {
            "task_class": None, "uncertainty": None, "requested_profile": None,
            "overrides": None, "effective_profile": actual,
            "outcome": "execution-failed", "reason": "no-legal-escalation",
            "completed_redispatches": count,
        }
    result = _decision(
        next_profile, capabilities, inheritance_guaranteed,
        reason=f"{kind}-redispatch", count=count,
    )
    result["next_redispatch"] = count + 1
    return result


def resolve(packet: dict[str, Any]) -> dict[str, Any]:
    """Resolve one observed dispatch state without I/O or persistent state."""
    packet = _require_object(packet, "input")
    allowed = {
        "event", "main_profile", "task_evidence", "capabilities",
        "inheritance_guaranteed", "completed_redispatches", "last_attempt",
        "rejection_retried", "failure_kind",
    }
    if set(packet) - allowed:
        raise InputError("input contains unknown fields")
    event = packet.get("event")
    if event not in {"initial", "after-execution", "host-rejection"}:
        raise InputError("event must be initial, after-execution, or host-rejection")
    inheritance_guaranteed = packet.get("inheritance_guaranteed")
    if type(inheritance_guaranteed) is not bool:
        raise InputError("inheritance_guaranteed must be a boolean")
    count = packet.get("completed_redispatches")
    if type(count) is not int or not 0 <= count <= 2:
        raise InputError("completed_redispatches must be an integer from 0 through 2")
    if event == "host-rejection":
        retried = packet.get("rejection_retried", False)
        if type(retried) is not bool:
            raise InputError("rejection_retried must be a boolean")
        if retried:
            result = _fallback(
                "host-rejection-repeated", inheritance_guaranteed,
                outcome="execution-failed", count=count,
            )
            result["effective_profile"] = "host-default/unverified"
            return result
        return _fallback(
            "host-rejection-replacement", inheritance_guaranteed, count=count,
        )
    capabilities = _capabilities(packet)
    if event == "initial":
        return _initial(packet, capabilities, inheritance_guaranteed, count)
    return _after_execution(packet, capabilities, inheritance_guaranteed, count)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = resolve(payload)
    except (json.JSONDecodeError, InputError) as exc:
        print(f"dispatch-profile: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
