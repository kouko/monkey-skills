#!/usr/bin/env python3
"""Hostile-cwd probes for the packaged second-vendor policy CLI."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[5]
POLICY = REPO_ROOT / "loom-code" / "scripts" / "second_vendor_policy.py"
SIGNALS = (
    "security-or-privacy-boundary",
    "public-contract-or-persistent-format",
    "cross-system-or-provider-integration",
    "review-verification-or-publication-mechanism",
    "critical-behavior-not-fully-automated",
    "irreversible-data-or-architecture",
)


def _packet(**overrides: object) -> dict[str, object]:
    packet: dict[str, object] = {
        "contract_version": 1,
        "configured_mode": "suggest",
        "host_vendor": "codex",
        "lane": "full",
        "usable_vendors": ["gemini", "claude"],
        "risk_evidence": [],
        "review_started": False,
        "response": "pending",
    }
    packet.update(overrides)
    return packet


def _run(tmp_path: Path, packet: object) -> subprocess.CompletedProcess[str]:
    hostile = tmp_path / "hostile cwd"
    decoy = tmp_path / "decoy modules"
    installed = tmp_path / "unrelated plugin cache" / "loom-code" / "scripts"
    hostile.mkdir(exist_ok=True)
    decoy.mkdir(exist_ok=True)
    installed.mkdir(parents=True, exist_ok=True)
    installed_policy = installed / POLICY.name
    shutil.copy2(POLICY, installed_policy)
    (decoy / "json.py").write_text("raise RuntimeError('decoy imported')\n")
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env["PYTHONPATH"] = str(decoy)
    return subprocess.run(
        [sys.executable, "-I", str(installed_policy)],
        input=json.dumps(packet),
        text=True,
        capture_output=True,
        cwd=hostile,
        env=env,
        timeout=10,
    )


def _decision(tmp_path: Path, **overrides: object) -> dict[str, object]:
    proc = _run(tmp_path, _packet(**overrides))
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_full_lane_default_is_visible_nonblocking_and_order_independent(tmp_path):
    result = _decision(tmp_path)
    assert result == {
        "effective_vendor": None,
        "notice_vendor": "claude",
        "notice_kind": "availability",
        "recommendation_reasons": [],
        "opt_in_eligible": True,
        "wait_for_user": False,
        "reason_code": "full-lane-availability",
    }


def test_all_grounded_risks_strengthen_the_notice_in_canonical_order(tmp_path):
    evidence = [
        {"signal": signal, "anchors": [f"spec.md :: anchor for {signal}"]}
        for signal in reversed(SIGNALS)
    ]
    result = _decision(tmp_path, risk_evidence=evidence)
    assert result["notice_kind"] == "recommendation"
    assert [item["signal"] for item in result["recommendation_reasons"]] == list(SIGNALS)
    assert result["wait_for_user"] is False


@pytest.mark.parametrize(
    ("response", "review_started", "expected_kind", "expected_reason"),
    [
        ("pending", False, "availability", "small-lane-availability-only"),
        ("pending", True, "no-notice", "no-response"),
        ("decline", False, "no-notice", "small-lane-declined"),
        ("decline", True, "no-notice", "small-lane-declined"),
        ("accept", False, "next-change-only", "small-lane-no-opt-in"),
        ("accept", True, "next-change-only", "small-lane-no-opt-in"),
    ],
)
def test_small_lane_never_selects_a_reviewer(
    tmp_path, response, review_started, expected_kind, expected_reason
):
    extra = {"response_vendor": "claude"} if response == "accept" else {}
    result = _decision(
        tmp_path,
        lane="small",
        response=response,
        review_started=review_started,
        **extra,
    )
    assert result["notice_kind"] == expected_kind
    assert result["reason_code"] == expected_reason
    assert result["effective_vendor"] is None
    assert result["opt_in_eligible"] is False


def test_timely_accept_selects_but_late_accept_is_next_change_only(tmp_path):
    timely = _decision(tmp_path, response="accept", response_vendor="claude")
    late = _decision(
        tmp_path,
        response="accept",
        response_vendor="claude",
        review_started=True,
    )
    assert (timely["notice_kind"], timely["effective_vendor"]) == (
        "selection-confirmed",
        "claude",
    )
    assert (late["notice_kind"], late["effective_vendor"]) == (
        "next-change-only",
        None,
    )


@pytest.mark.parametrize("mode", ["ask", "fixed"])
def test_existing_modes_are_not_reinterpreted(tmp_path, mode):
    extra = {"fixed_vendor": "claude"} if mode == "fixed" else {}
    result = _decision(tmp_path, configured_mode=mode, **extra)
    assert result["reason_code"] == "mode-not-suggest"
    assert result["notice_kind"] == "no-notice"


@pytest.mark.parametrize(
    "mutation",
    [
        {"configured_mode": "none"},
        {"usable_vendors": ["codex"]},
        {"response": "accept"},
        {
            "risk_evidence": [
                {"signal": SIGNALS[0], "anchors": ["invented-without-separator"]}
            ]
        },
    ],
)
def test_removed_or_contradictory_inputs_fail_without_a_decision(tmp_path, mutation):
    proc = _run(tmp_path, _packet(**mutation))
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert proc.stderr.startswith("second-vendor-policy:")


def test_no_usable_vendor_returns_a_checkable_silent_reason(tmp_path):
    result = _decision(tmp_path, usable_vendors=[])
    assert result["notice_kind"] == "no-notice"
    assert result["reason_code"] == "no-usable-vendor"
    assert result["wait_for_user"] is False


def test_repository_default_adopts_suggest():
    defaults = (REPO_ROOT / "docs" / "loom" / "KICKOFF-DEFAULTS.md").read_text()
    assert "- second-vendor: suggest" in defaults
    assert "- second-vendor: ask" not in defaults
