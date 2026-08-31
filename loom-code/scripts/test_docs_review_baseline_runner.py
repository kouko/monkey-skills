"""Tests for the docs-review historical replay runner boundaries."""
from __future__ import annotations

import pytest

import docs_review_baseline_runner as runner
from docs_review_baseline_store import read_record


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


def _run(run_id: str, host: str, model: str) -> dict[str, object]:
    return {
        "run_id": run_id,
        "valid": True,
        "scoreable": True,
        "corpus_digest": "sha256:corpus-r1",
        "artifact_digest": "sha256:artifact-r1",
        "contract_digest": "sha256:contract-r1",
        "runtime_digest": "sha256:runtime-r1",
        "configuration_fingerprint": "sha256:configuration-r1",
        "host": host,
        "model": model,
        "tier": "economy",
        "requested_effort": "low",
    }


def test_req_105_repeat_cohorts_never_mix_execution_identities() -> None:
    # @req: REQ-105
    codex = runner.build_repeat_cohorts(
        [_run("codex-1", "codex", "gpt-5.6-luna"),
         _run("codex-2", "codex", "gpt-5.6-luna")]
    )
    assert len(codex["cohorts"]) == 1
    assert codex["cohorts"][0]["run_ids"] == ["codex-1", "codex-2"]
    assert codex["insufficient"] == []

    split = runner.build_repeat_cohorts(
        [_run("claude-1", "claude-code", "haiku"),
         _run("codex-1", "codex", "gpt-5.6-luna")]
    )
    assert split["cohorts"] == []
    assert [item["run_ids"] for item in split["insufficient"]] == [
        ["claude-1"],
        ["codex-1"],
    ]
    assert all(item["reason"] == "repeat cohort requires at least two runs"
               for item in split["insufficient"])

    excluded = runner.build_repeat_cohorts([
        {**_run("bad-1", "codex", "gpt-5.6-luna"), "scoreable": False},
        _run("codex-2", "codex", "gpt-5.6-luna"),
    ])
    assert excluded["excluded"] == [
        {"run_id": "bad-1", "reason": "run is not valid and scoreable"}
    ]
    assert excluded["insufficient"][0]["run_ids"] == ["codex-2"]


def test_req_110_contract_and_runtime_are_independent_inputs(tmp_path) -> None:
    # @req: REQ-110
    contract = runner.freeze_reviewer_revision(
        tmp_path,
        record_id="contract-r1",
        kind="reviewer_contract_revision",
        content=b"Review the whole artifact.\n",
        owner="maintainer:contract",
        parent_revision_id=None,
        change_reason="Initial frozen contract.",
    )
    runtime_1 = runner.freeze_reviewer_revision(
        tmp_path,
        record_id="runtime-r1",
        kind="reviewer_runtime_revision",
        content=b"skill package bytes r1",
        owner="maintainer:runtime",
        parent_revision_id=None,
        change_reason="Initial frozen runtime.",
    )
    runtime_2 = runner.freeze_reviewer_revision(
        tmp_path,
        record_id="runtime-r2",
        kind="reviewer_runtime_revision",
        content=b"skill package bytes r2",
        owner="maintainer:runtime",
        parent_revision_id="runtime-r1",
        change_reason="Package behavior changed.",
    )

    assert contract.record["content_digest"] != runtime_1.record["content_digest"]
    assert runtime_2.record["parent_revision_id"] == runtime_1.record_id
    assert read_record(tmp_path, "runtime-r1") == runtime_1

    base = _run("run-1", "codex", "gpt-5.6-luna")
    separated = runner.build_repeat_cohorts([
        {**base, "contract_digest": contract.digest,
         "runtime_digest": runtime_1.digest},
        {**base, "run_id": "run-2", "contract_digest": contract.digest,
         "runtime_digest": runtime_2.digest},
    ])
    assert separated["cohorts"] == []
    assert len(separated["insufficient"]) == 2

    with pytest.raises(ValueError, match="parent kind"):
        runner.freeze_reviewer_revision(
            tmp_path,
            record_id="runtime-bad-parent",
            kind="reviewer_runtime_revision",
            content=b"bad lineage",
            owner="maintainer:runtime",
            parent_revision_id="contract-r1",
            change_reason="Wrong lineage.",
        )
