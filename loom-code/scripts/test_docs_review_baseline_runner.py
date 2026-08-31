"""Tests for the docs-review historical replay runner boundaries."""
from __future__ import annotations

import pytest

import docs_review_baseline_runner as runner


def _binding(host: str, model: str) -> dict[str, str]:
    return {
        "host": host,
        "model": model,
        "tier": "economy",
        "requested_effort": "low",
        "contract_revision_id": "docs-review-contract-r1",
        "runtime_revision_id": "docs-review-runtime-r1",
        "configuration_fingerprint": "sha256:configuration-r1",
    }


def test_req_102_scored_replay_uses_explicit_weak_bindings() -> None:
    # @req: REQ-102
    claude = runner.resolve_scored_execution_profile(
        _binding("claude-code", "haiku")
    )
    codex = runner.resolve_scored_execution_profile(
        _binding("codex", "gpt-5.6-luna")
    )

    assert claude["scoreable"] is True
    assert codex["scoreable"] is True
    assert claude["identity"] != codex["identity"]
    assert claude["resolved"] == {
        **_binding("claude-code", "haiku"),
        "execution_profile": "economy",
    }
    assert codex["resolved"] == {
        **_binding("codex", "gpt-5.6-luna"),
        "execution_profile": "economy",
    }

    unknown = _binding("codex", "")
    result = runner.resolve_scored_execution_profile(unknown)
    assert result["scoreable"] is False
    assert result["reason"] == "exact model identity is unavailable"
    assert result["resolved"]["model"] is None

    with pytest.raises(ValueError, match="outside the economy profile"):
        runner.resolve_scored_execution_profile(
            _binding("codex", "gpt-5.6-sol")
        )
    with pytest.raises(ValueError, match="outside the economy profile"):
        runner.resolve_scored_execution_profile(
            {**_binding("codex", "gpt-5.6-luna"), "tier": "standard"}
        )
    with pytest.raises(ValueError, match="unknown replay host"):
        runner.resolve_scored_execution_profile(_binding("other", "tiny"))
