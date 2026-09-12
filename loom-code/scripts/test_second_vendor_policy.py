"""Contract tests for the pure second-vendor suggestion resolver."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

import second_vendor_policy  # noqa: E402


def packet(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "contract_version": 1,
        "configured_mode": "suggest",
        "host_vendor": "codex",
        "lane": "full",
        "usable_vendors": ["claude"],
        "risk_evidence": [],
        "review_started": False,
        "response": "pending",
    }
    value.update(overrides)
    return value


def risk(signal: str, *anchors: str) -> dict[str, object]:
    return {"signal": signal, "anchors": list(anchors)}


def test_resolve_full_lane_available_returns_nonblocking_notice() -> None:
    result = second_vendor_policy.resolve(packet())

    assert result == {
        "effective_vendor": None,
        "notice_vendor": "claude",
        "notice_kind": "availability",
        "recommendation_reasons": [],
        "opt_in_eligible": True,
        "wait_for_user": False,
        "reason_code": "full-lane-availability",
    }


def test_resolve_risks_returns_grounded_canonical_recommendation() -> None:
    evidence = [
        risk("irreversible-data-or-architecture", "spec.md :: irreversible"),
        risk("security-or-privacy-boundary", "intent.md :: privacy"),
    ]
    result = second_vendor_policy.resolve(packet(risk_evidence=evidence))

    assert result["notice_kind"] == "recommendation"
    assert result["reason_code"] == "full-lane-risk-recommendation"
    assert result["recommendation_reasons"] == [evidence[1], evidence[0]]


def test_resolve_provider_order_is_canonical_not_caller_order() -> None:
    result = second_vendor_policy.resolve(
        packet(host_vendor="gemini", usable_vendors=["codex", "claude"])
    )

    assert result["notice_vendor"] == "claude"


def test_resolve_without_usable_vendor_emits_no_notice() -> None:
    result = second_vendor_policy.resolve(packet(usable_vendors=[]))

    assert result["notice_kind"] == "no-notice"
    assert result["notice_vendor"] is None
    assert result["reason_code"] == "no-usable-vendor"


@pytest.mark.parametrize(
    ("response", "review_started", "notice_kind", "reason_code", "effective"),
    [
        ("pending", False, "availability", "small-lane-availability-only", None),
        ("pending", True, "no-notice", "no-response", None),
        ("decline", False, "no-notice", "small-lane-declined", None),
        ("decline", True, "no-notice", "small-lane-declined", None),
        ("accept", False, "next-change-only", "small-lane-no-opt-in", None),
        ("accept", True, "next-change-only", "small-lane-no-opt-in", None),
    ],
)
def test_resolve_small_lane_never_selects_vendor(
    response: str,
    review_started: bool,
    notice_kind: str,
    reason_code: str,
    effective: None,
) -> None:
    extra = {"response_vendor": "claude"} if response == "accept" else {}
    result = second_vendor_policy.resolve(
        packet(lane="small", response=response, review_started=review_started, **extra)
    )

    assert result["notice_kind"] == notice_kind
    assert result["reason_code"] == reason_code
    assert result["effective_vendor"] is effective
    assert result["opt_in_eligible"] is False
    assert result["wait_for_user"] is False


def test_resolve_full_lane_acceptance_obeys_review_cutoff() -> None:
    accepted = second_vendor_policy.resolve(
        packet(response="accept", response_vendor="claude")
    )
    late = second_vendor_policy.resolve(
        packet(response="accept", response_vendor="claude", review_started=True)
    )

    assert accepted["effective_vendor"] == "claude"
    assert accepted["notice_kind"] == "selection-confirmed"
    assert late["effective_vendor"] is None
    assert late["notice_kind"] == "next-change-only"


@pytest.mark.parametrize("mode", ["ask", "fixed"])
def test_resolve_existing_modes_are_not_reimplemented(mode: str) -> None:
    extra = {"fixed_vendor": "claude"} if mode == "fixed" else {}
    result = second_vendor_policy.resolve(packet(configured_mode=mode, **extra))

    assert result["reason_code"] == "mode-not-suggest"
    assert result["notice_kind"] == "no-notice"


@pytest.mark.parametrize(
    "overrides",
    [
        {"configured_mode": "none"},
        {"unknown": True},
        {"usable_vendors": ["codex"]},
        {"usable_vendors": ["claude", "claude"]},
        {"risk_evidence": [risk("security-or-privacy-boundary")]},
        {"risk_evidence": [risk("unknown", "spec.md :: risk")]},
        {"response": "accept"},
        {"response": "accept", "response_vendor": "gemini"},
    ],
)
def test_resolve_rejects_malformed_or_contradictory_input(
    overrides: dict[str, object],
) -> None:
    with pytest.raises(second_vendor_policy.InputError):
        second_vendor_policy.resolve(packet(**overrides))


def test_cli_emits_sorted_json_and_rejects_invalid_input() -> None:
    script = SCRIPTS / "second_vendor_policy.py"
    valid = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(packet()),
        text=True,
        capture_output=True,
        check=False,
    )
    invalid = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(packet(configured_mode="none")),
        text=True,
        capture_output=True,
        check=False,
    )

    assert valid.returncode == 0
    assert json.loads(valid.stdout) == second_vendor_policy.resolve(packet())
    assert invalid.returncode == 2
    assert invalid.stdout == ""
    assert invalid.stderr.startswith("second-vendor-policy: ")
