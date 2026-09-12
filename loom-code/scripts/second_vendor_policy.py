#!/usr/bin/env python3
"""Resolve one host-neutral second-vendor suggestion decision."""
from __future__ import annotations

import json
import sys
from typing import Any


VENDORS = ("claude", "codex", "gemini")
MODES = {"ask", "suggest", "fixed"}
LANES = {"small", "full"}
RESPONSES = {"pending", "decline", "accept"}
RISK_SIGNALS = (
    "security-or-privacy-boundary",
    "public-contract-or-persistent-format",
    "cross-system-or-provider-integration",
    "review-verification-or-publication-mechanism",
    "critical-behavior-not-fully-automated",
    "irreversible-data-or-architecture",
)


class InputError(ValueError):
    """The observed-state packet is malformed or contradictory."""


def _result(
    *,
    notice_kind: str = "no-notice",
    reason_code: str,
    effective_vendor: str | None = None,
    notice_vendor: str | None = None,
    reasons: list[dict[str, object]] | None = None,
    eligible: bool = False,
) -> dict[str, object]:
    return {
        "effective_vendor": effective_vendor,
        "notice_vendor": notice_vendor,
        "notice_kind": notice_kind,
        "recommendation_reasons": reasons or [],
        "opt_in_eligible": eligible,
        "wait_for_user": False,
        "reason_code": reason_code,
    }


def _require_string(value: object, name: str, allowed: set[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise InputError(f"{name} must be one of {', '.join(sorted(allowed))}")
    return value


def _vendors(value: object, host_vendor: str) -> list[str]:
    if not isinstance(value, list) or any(v not in VENDORS for v in value):
        raise InputError("usable_vendors must be an array of known vendors")
    if len(value) != len(set(value)):
        raise InputError("usable_vendors must be unique")
    if host_vendor in value:
        raise InputError("usable_vendors must exclude host_vendor")
    return [vendor for vendor in VENDORS if vendor in value]


def _risks(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise InputError("risk_evidence must be an array")
    by_signal: dict[str, dict[str, object]] = {}
    for item in value:
        if not isinstance(item, dict) or set(item) != {"signal", "anchors"}:
            raise InputError("risk evidence must contain exactly signal and anchors")
        signal = item["signal"]
        anchors = item["anchors"]
        if signal not in RISK_SIGNALS:
            raise InputError("risk evidence contains an unknown signal")
        if signal in by_signal:
            raise InputError("risk evidence signals must be unique")
        if (
            not isinstance(anchors, list)
            or not anchors
            or any(
                not isinstance(anchor, str)
                or " :: " not in anchor
                or not all(part.strip() for part in anchor.split(" :: ", 1))
                for anchor in anchors
            )
            or len(anchors) != len(set(anchors))
        ):
            raise InputError("risk evidence anchors must be unique path :: anchor strings")
        by_signal[signal] = {"signal": signal, "anchors": anchors.copy()}
    return [by_signal[signal] for signal in RISK_SIGNALS if signal in by_signal]


def resolve(packet: dict[str, Any]) -> dict[str, object]:
    """Resolve one decision without I/O, persistence, or provider execution."""
    if not isinstance(packet, dict):
        raise InputError("input must be an object")
    allowed = {
        "contract_version", "configured_mode", "fixed_vendor", "host_vendor",
        "lane", "usable_vendors", "risk_evidence", "review_started",
        "response", "response_vendor",
    }
    if set(packet) - allowed:
        raise InputError("input contains unknown fields")
    if packet.get("contract_version") != 1 or type(packet.get("contract_version")) is not int:
        raise InputError("contract_version must be integer 1")
    mode = _require_string(packet.get("configured_mode"), "configured_mode", MODES)
    host_vendor = _require_string(packet.get("host_vendor"), "host_vendor", set(VENDORS))
    lane = _require_string(packet.get("lane"), "lane", LANES)
    response = _require_string(packet.get("response"), "response", RESPONSES)
    review_started = packet.get("review_started")
    if type(review_started) is not bool:
        raise InputError("review_started must be a boolean")
    vendors = _vendors(packet.get("usable_vendors"), host_vendor)
    risks = _risks(packet.get("risk_evidence"))

    fixed_vendor = packet.get("fixed_vendor")
    if mode == "fixed":
        _require_string(fixed_vendor, "fixed_vendor", set(VENDORS))
    elif fixed_vendor is not None:
        raise InputError("fixed_vendor is valid only for fixed mode")

    response_vendor = packet.get("response_vendor")
    if response == "accept":
        accepted = _require_string(response_vendor, "response_vendor", set(VENDORS))
        if accepted not in vendors:
            raise InputError("response_vendor must identify a usable vendor")
    elif response_vendor is not None:
        raise InputError("response_vendor is valid only for accept")

    if mode != "suggest":
        return _result(reason_code="mode-not-suggest")
    if not vendors:
        return _result(reason_code="no-usable-vendor")

    candidate = vendors[0]
    if lane == "small":
        if response == "accept":
            return _result(
                notice_kind="next-change-only",
                notice_vendor=response_vendor,
                reason_code="small-lane-no-opt-in",
            )
        if response == "decline":
            return _result(reason_code="small-lane-declined")
        if review_started:
            return _result(reason_code="no-response")
        return _result(
            notice_kind="availability",
            notice_vendor=candidate,
            reason_code="small-lane-availability-only",
        )

    if response == "accept":
        if review_started:
            return _result(
                notice_kind="next-change-only",
                notice_vendor=response_vendor,
                reason_code="response-too-late",
            )
        return _result(
            notice_kind="selection-confirmed",
            effective_vendor=response_vendor,
            notice_vendor=response_vendor,
            reason_code="selection-accepted",
        )
    if response == "decline":
        return _result(reason_code="selection-declined")
    if review_started:
        return _result(reason_code="no-response")
    if risks:
        return _result(
            notice_kind="recommendation",
            notice_vendor=candidate,
            reasons=risks,
            eligible=True,
            reason_code="full-lane-risk-recommendation",
        )
    return _result(
        notice_kind="availability",
        notice_vendor=candidate,
        eligible=True,
        reason_code="full-lane-availability",
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = resolve(payload)
    except (json.JSONDecodeError, InputError) as exc:
        print(f"second-vendor-policy: {exc}", file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
