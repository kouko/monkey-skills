"""Regression contract for git-memory when loom delegates close-out."""

from __future__ import annotations

import re
from pathlib import Path


_GIT_MEMORY_ROOT = Path(__file__).parents[1]
_COMMIT_PROTOCOL = _GIT_MEMORY_ROOT / "protocols" / "compose-commit.md"
_PR_PROTOCOL = _GIT_MEMORY_ROOT / "protocols" / "compose-pr.md"
_PRIVACY_SPEC = _GIT_MEMORY_ROOT / "protocols" / "privacy-judge-spec.md"


def test_loom_closeout_delegation_does_not_reconfirm_authorized_publish() -> None:
    """A close-out authorization is consumed by the orchestrator, not re-asked.

    This deliberately verifies the documented behavioral contract because the
    protocols, rather than executable code, decide whether an agent pauses.
    """
    commit_protocol = _COMMIT_PROTOCOL.read_text(encoding="utf-8")
    pr_protocol = _PR_PROTOCOL.read_text(encoding="utf-8")

    for protocol, direct_heading in (
        (commit_protocol, "### All other calls — confirm before finalizing"),
        (pr_protocol, "### All other calls — confirm before opening"),
    ):
        delegated_heading = "### Delegated loom close-out exception"
        assert delegated_heading in protocol
        assert protocol.index(delegated_heading) < protocol.index(direct_heading)
        assert re.search(r"does\s+not\s+re-confirm", protocol)
        assert "initiating request" in protocol
        assert "privacy gate PASS" in protocol
        assert "Privacy BLOCK remains a required human stop" in protocol
        assert "Otherwise" in protocol

    # Every non-delegated or non-authorized route still pauses for consent.
    assert "direct git-memory invocation" in commit_protocol
    assert "direct git-memory invocation" in pr_protocol


def test_privacy_judge_only_runs_for_ambiguous_private_party_text() -> None:
    spec = _PRIVACY_SPEC.read_text(encoding="utf-8")
    assert re.search(r"public repository,\s+PR, issue, task, or vendor identifiers", spec)
    assert "do not dispatch" in spec
    assert "ambiguous private-party" in spec
    assert "Privacy-Bypass-Reason:" in spec


def test_bypass_never_applies_to_deterministic_secret_findings() -> None:
    for path in (_COMMIT_PROTOCOL, _PR_PROTOCOL):
        text = path.read_text(encoding="utf-8")
        assert "Privacy-Bypass-Reason:" in text
        assert "never bypasses a layer-1 secret finding" in text
