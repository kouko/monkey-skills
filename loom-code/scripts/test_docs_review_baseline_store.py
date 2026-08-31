"""Tests for immutable, content-addressed docs-review baseline records."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import os
import stat

import pytest

import docs_review_baseline_store as store
from docs_review_baseline_store import (
    RecordConflictError,
    admit_historical_case,
    append_revision,
    canonical_json_bytes,
    correct_oracle,
    publish_record,
    ratify_oracle,
    read_record,
    record_digest,
)


def test_req_99_historical_case_admission(tmp_path) -> None:
    # @req: REQ-99
    """Only explicit snapshot bytes can admit a scoreable replay candidate."""
    snapshot = b"# Historical draft\n\nThe original document bytes.\n"
    candidate = admit_historical_case(
        tmp_path,
        "case-2026-08-27",
        snapshot_bytes=snapshot,
        source_locator="git:abc123:docs/example.md",
        evidence_locators=["review:2026-08-27#finding-4"],
    )

    assert candidate.record == {
        "case_id": "case-2026-08-27",
        "evidence_locators": ["review:2026-08-27#finding-4"],
        "kind": "historical_case",
        "schema_version": 1,
        "snapshot": {
            "bytes_base64": "IyBIaXN0b3JpY2FsIGRyYWZ0CgpUaGUgb3JpZ2luYWwgZG9jdW1lbnQgYnl0ZXMuCg==",
            "digest": "2c30de42ffe3d2b9ecd4b8d0e87c2e88f7b837fd0f5429365b2e5aff5a09b29d",
        },
        "source_locator": "git:abc123:docs/example.md",
        "status": "candidate",
    }
    assert candidate.digest == record_digest(candidate.record)
    assert read_record(tmp_path, candidate.record_id) == candidate

    unscoreable = admit_historical_case(
        tmp_path,
        "case-narrative-only",
        snapshot_bytes=None,
        source_locator="issue:2026-08-27-incident",
        evidence_locators=["issue:2026-08-27-incident#description"],
    )

    assert unscoreable.record == {
        "case_id": "case-narrative-only",
        "evidence_locators": ["issue:2026-08-27-incident#description"],
        "kind": "historical_case",
        "missing_replay_evidence": ["snapshot_bytes"],
        "schema_version": 1,
        "source_locator": "issue:2026-08-27-incident",
        "status": "unscoreable",
    }
    assert "snapshot" not in unscoreable.record


def test_req_100_oracle_ratification_is_immutable(tmp_path) -> None:
    # @req: REQ-100
    """Ratification freezes a named oracle; corrections form reasoned children."""
    oracle = ratify_oracle(
        tmp_path,
        "oracle-case-1-r1",
        case_id="case-1",
        snapshot_digest="a" * 64,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the unbounded migration risk.",
                "rationale": "The rollout has no limiting condition.",
                "evidence_locator": "git:abc123:docs/strategy.md#rollout",
            }
        ],
        negative_control_intent="Do not reward generic requests for more detail.",
        ratifier="maintainer:kuku",
    )
    frozen_bytes = oracle.path.read_bytes()

    assert oracle.record["ratifier"] == "maintainer:kuku"
    assert oracle.record["negative_control_intent"] == (
        "Do not reward generic requests for more detail."
    )
    assert oracle.digest == record_digest(oracle.record)
    with pytest.raises(RecordConflictError):
        ratify_oracle(
            tmp_path,
            "oracle-case-1-r1",
            case_id="case-1",
            snapshot_digest="a" * 64,
            findings=[
                {
                    "finding_id": "missing-risk",
                    "expectation": "Changed in place.",
                    "rationale": "This remains structurally complete.",
                    "evidence_locator": "git:abc123:docs/strategy.md#rollout",
                }
            ],
            negative_control_intent="Changed in place.",
            ratifier="maintainer:kuku",
        )

    correction = correct_oracle(
        tmp_path,
        oracle.record_id,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the bounded migration risk.",
                "rationale": "The rollout is limited to one cohort.",
                "evidence_locator": "git:def456:docs/strategy.md#rollout",
            }
        ],
        negative_control_intent="Do not reward generic requests for more detail.",
        reason="The original snapshot interpretation ignored the cohort limit.",
        ratifier="maintainer:kuku",
    )

    assert correction.record["parent_revision_id"] == oracle.record_id
    assert correction.record["parent_digest"] == oracle.digest
    assert correction.record["correction_reason"]
    assert correction.digest != oracle.digest
    assert correction.record_id != oracle.record_id
    assert oracle.path.read_bytes() == frozen_bytes
    assert read_record(tmp_path, oracle.record_id) == oracle

    with pytest.raises(ValueError, match="reason"):
        correct_oracle(
            tmp_path,
            oracle.record_id,
            findings=correction.record["findings"],
            negative_control_intent=correction.record["negative_control_intent"],
            reason="",
            ratifier="maintainer:kuku",
        )


def test_req_101_corpus_manifest_is_exact_and_immutable(tmp_path) -> None:
    # @req: REQ-101
    """A run-facing corpus ID freezes exact, ratified snapshot bindings."""
    case = admit_historical_case(
        tmp_path,
        "case-1",
        snapshot_bytes=b"# Exact historical draft\n",
        source_locator="git:abc123:docs/strategy.md",
        evidence_locators=["review:abc123#finding-1"],
    )
    snapshot_digest = case.record["snapshot"]["digest"]
    oracle = ratify_oracle(
        tmp_path,
        "oracle-case-1-r1",
        case_id="case-1",
        snapshot_digest=snapshot_digest,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the rollout risk.",
                "rationale": "The rollout lacks a limiting condition.",
                "evidence_locator": "git:abc123:docs/strategy.md#rollout",
            }
        ],
        negative_control_intent="Do not reward generic requests for detail.",
        ratifier="maintainer:kuku",
    )
    bindings = [("case-1", snapshot_digest, oracle.record_id)]

    manifest = store.freeze_corpus_manifest(tmp_path, bindings)
    frozen_bytes = manifest.path.read_bytes()

    assert manifest.record == {
        "bindings": [
            {
                "case_id": "case-1",
                "oracle_revision_id": "oracle-case-1-r1",
                "snapshot_digest": snapshot_digest,
            }
        ],
        "kind": "corpus_manifest",
        "schema_version": 1,
    }
    assert manifest.record_id == f"corpus-{manifest.digest}"
    assert store.freeze_corpus_manifest(tmp_path, bindings) == manifest
    assert manifest.path.read_bytes() == frozen_bytes

    with pytest.raises(ValueError, match="non-empty"):
        store.freeze_corpus_manifest(tmp_path, [])
    with pytest.raises(ValueError, match="latest"):
        store.freeze_corpus_manifest(
            tmp_path, [("case-1", snapshot_digest, "latest")]
        )
    with pytest.raises(ValueError, match="ratified"):
        store.freeze_corpus_manifest(
            tmp_path, [("case-1", snapshot_digest, case.record_id)]
        )
    with pytest.raises(ValueError, match="snapshot digest"):
        store.freeze_corpus_manifest(
            tmp_path, [("case-1", "b" * 64, oracle.record_id)]
        )


def test_req_103_attempt_ledger_preserves_failures(tmp_path) -> None:
    # @req: REQ-103
    """Every dispatch is counted even when it never yields usable findings."""
    prepared = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-1",
        sequence=1,
        profile_id="codex:gpt-5.6-luna:economy",
        corpus_id="corpus-abc",
        case_id="case-1",
    )
    prepared_bytes = prepared.path.read_bytes()

    failed = store.record_dispatch_outcome(
        tmp_path,
        prepared.record_id,
        outcome="timeout",
        resource_telemetry={"elapsed_ms": 30_000, "dispatches": 1},
        failure="reviewer exceeded the deadline",
    )

    assert prepared.record == {
        "attempt_id": "attempt-1",
        "case_id": "case-1",
        "corpus_id": "corpus-abc",
        "kind": "dispatch_attempt",
        "profile_id": "codex:gpt-5.6-luna:economy",
        "schema_version": 1,
        "sequence": 1,
        "status": "prepared",
    }
    assert prepared.path.read_bytes() == prepared_bytes
    assert failed.record["parent_digest"] == prepared.digest
    assert failed.record["parent_attempt_id"] == prepared.record_id
    assert failed.record["outcome"] == "timeout"
    assert failed.record["failure"] == "reviewer exceeded the deadline"
    assert failed.record["resource_telemetry"]["dispatches"] == 1
    assert "findings" not in failed.record

    usable = store.record_dispatch_outcome(
        tmp_path,
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-2",
            sequence=2,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        ).record_id,
        outcome="success",
        raw_response_bytes=b'{"findings":[{"summary":"missing risk"}]}',
        resource_telemetry={"elapsed_ms": 412, "dispatches": 1},
    )
    assert usable.record["raw_response"]["digest"] == (
        "48d146824f72a74ad3edcbcb7f1672542634f0b9e0b4f135b297db499c3980b5"
    )
    assert "findings" not in usable.record

    retry = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-3",
        sequence=3,
        profile_id="codex:gpt-5.6-luna:economy",
        corpus_id="corpus-abc",
        case_id="case-1",
    )
    assert retry.record_id != prepared.record_id
    with pytest.raises(RecordConflictError):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-1",
            sequence=4,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )

    cancelled = store.record_dispatch_outcome(
        tmp_path,
        retry.record_id,
        outcome="cancelled",
        resource_telemetry={"elapsed_ms": 9, "dispatches": 1},
        failure="operator interruption",
    )
    assert cancelled.record["outcome"] == "cancelled"
    assert "findings" not in cancelled.record

    with pytest.raises(RecordConflictError):
        store.record_dispatch_outcome(
            tmp_path,
            retry.record_id,
            outcome="interruption",
            resource_telemetry={"elapsed_ms": 11, "dispatches": 1},
            failure="second terminal result must not replace the first",
        )

    for sequence, outcome in enumerate(
        ("transport_failure", "interruption", "quota_exhaustion", "parse_failure"),
        start=4,
    ):
        attempt = store.prepare_dispatch_attempt(
            tmp_path,
            f"attempt-{sequence}",
            sequence=sequence,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )
        terminal = store.record_dispatch_outcome(
            tmp_path,
            attempt.record_id,
            outcome=outcome,
            raw_response_bytes=b"not-json" if outcome == "parse_failure" else None,
            resource_telemetry={"elapsed_ms": sequence, "dispatches": 1},
            failure=f"recorded {outcome}",
        )
        assert terminal.record["outcome"] == outcome
        assert terminal.record["resource_telemetry"]["dispatches"] == 1
        assert "findings" not in terminal.record

    with pytest.raises(ValueError, match="raw_response_bytes"):
        store.record_dispatch_outcome(
            tmp_path,
            retry.record_id,
            outcome="parse_failure",
            resource_telemetry={"elapsed_ms": 10, "dispatches": 1},
            failure="malformed JSON",
        )


def test_req_104_observation_and_attribution_are_separate(tmp_path) -> None:
    # @req: REQ-104
    """Model claims stay lossless; only named humans ratify judgments."""
    attempt = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-observation-1",
        sequence=1,
        profile_id="codex:gpt-5.6-luna:economy",
        corpus_id="corpus-abc",
        case_id="case-1",
    )
    outcome = store.record_dispatch_outcome(
        tmp_path,
        attempt.record_id,
        outcome="success",
        raw_response_bytes=b'{"finding":"Missing bounded rollout","severity":"high"}',
        resource_telemetry={"dispatches": 1},
    )
    observation = store.capture_finding_observation(
        tmp_path,
        "observation-1",
        outcome_record_id=outcome.record_id,
        finding_identity="finding:missing-bounded-rollout",
        raw_span=b'Missing bounded rollout',
        payload_hash="b" * 64,
        wording="Missing bounded rollout",
        location="docs/strategy.md#rollout",
        severity="high",
        reviewer_verdict="must_fix",
    )
    observation_bytes = observation.path.read_bytes()

    assert observation.record == {
        "finding_identity": "finding:missing-bounded-rollout",
        "kind": "finding_observation",
        "location": "docs/strategy.md#rollout",
        "attempt_digest": attempt.digest,
        "attempt_record_id": attempt.record_id,
        "outcome_digest": outcome.digest,
        "outcome_record_id": outcome.record_id,
        "payload_hash": "b" * 64,
        "raw_span": {
            "bytes_base64": "TWlzc2luZyBib3VuZGVkIHJvbGxvdXQ=",
            "digest": "43eb032f346b33891a7fdd7e037e91bc65a2b1f82d9059ddb2c8fe33a6a6cd9f",
        },
        "reviewer_verdict": "must_fix",
        "schema_version": 1,
        "severity": "high",
        "wording": "Missing bounded rollout",
    }
    assert "human_verdict" not in observation.record

    corrected_observation = store.correct_finding_observation(
        tmp_path,
        observation.record_id,
        finding_identity="finding:missing-bounded-rollout",
        raw_span=b'Missing bounded rollout',
        payload_hash="c" * 64,
        wording="Missing bounded rollout",
        location="docs/strategy.md#bounded-rollout",
        severity="high",
        reviewer_verdict="must_fix",
        reason="The parser selected the containing section instead of the line.",
    )
    assert corrected_observation.record["parent_observation_id"] == observation.record_id
    assert corrected_observation.record["parent_digest"] == observation.digest
    assert corrected_observation.record["attempt_record_id"] == attempt.record_id
    assert corrected_observation.record["outcome_record_id"] == outcome.record_id
    assert observation.path.read_bytes() == observation_bytes

    unknown = store.ratify_attribution(
        tmp_path,
        "attribution-observation-1-r1",
        observation_id=observation.record_id,
        oracle_revision_id="oracle-case-1-r1",
        oracle_matches=[],
        human_verdict="unknown",
        defect_origin="unknown",
        rationale="The historical evidence is insufficient to adjudicate it.",
        dispute_evidence=[],
        ratifier="maintainer:kuku",
    )
    assert unknown.record["human_verdict"] == "unknown"
    assert unknown.record["observation_digest"] == observation.digest
    assert unknown.record["status"] == "ratified"
    assert unknown.record["ratifier"] == "maintainer:kuku"
    assert unknown.record["oracle_matches"] == []
    assert unknown.record["excluded_from_false_alarm_denominator"] is True

    corrected = store.correct_attribution(
        tmp_path,
        unknown.record_id,
        oracle_matches=["oracle-finding:missing-risk"],
        human_verdict="true_positive",
        defect_origin="initial_writing",
        rationale="The located claim matches the ratified expected finding.",
        dispute_evidence=[],
        reason="The missing historical review comment was recovered.",
        ratifier="human:second-rater",
    )
    assert corrected.record["parent_revision_id"] == unknown.record_id
    assert corrected.record["parent_digest"] == unknown.digest
    assert corrected.record["observation_id"] == observation.record_id
    assert corrected.record["observation_digest"] == observation.digest
    assert corrected.record["human_verdict"] == "true_positive"
    assert corrected.record["excluded_from_false_alarm_denominator"] is False
    assert observation.path.read_bytes() == observation_bytes
    assert read_record(tmp_path, unknown.record_id) == unknown

    with pytest.raises(ValueError, match="human ratifier"):
        store.ratify_attribution(
            tmp_path,
            "attribution-model-self-rating",
            observation_id=observation.record_id,
            oracle_revision_id="oracle-case-1-r1",
            oracle_matches=[],
            human_verdict="false_positive",
            defect_origin="unknown",
            rationale="The model tried to grade its own finding.",
            dispute_evidence=[],
            ratifier="model:gpt-5.6-luna",
        )

    disputed = store.ratify_attribution(
        tmp_path,
        "attribution-observation-1-disputed",
        observation_id=observation.record_id,
        oracle_revision_id="oracle-case-1-r1",
        oracle_matches=[],
        human_verdict="disputed",
        defect_origin="unknown",
        rationale="Two human interpretations conflict.",
        dispute_evidence=["review-note:first-rater", "review-note:second-rater"],
        ratifier="human:tie-breaker",
    )
    assert disputed.record["excluded_from_false_alarm_denominator"] is True
    assert disputed.record["dispute_evidence"] == [
        "review-note:first-rater",
        "review-note:second-rater",
    ]


def test_req_109_origin_requires_document_revision_evidence(tmp_path) -> None:
    # @req: REQ-109
    """Origin uses recoverable before/after bytes, never narrative alone."""
    parent = store.publish_document_revision(
        tmp_path,
        "document-case-1-r1",
        snapshot_bytes=b"# Rollout\n\nShip to one bounded cohort.\n",
        event_locator="git:aaa111:docs/strategy.md",
        responsible_stage="initial_authoring",
    )
    parent_bytes = parent.path.read_bytes()
    child = store.correct_document_revision(
        tmp_path,
        parent.record_id,
        snapshot_bytes=b"# Rollout\n\nShip globally without a rollback trigger.\n",
        event_locator="review-fix:round-2",
        responsible_stage="remediation",
    )

    introduced = store.ratify_defect_origin(
        tmp_path,
        "origin-case-1-risk-r1",
        observable_revision_id=child.record_id,
        defect_evidence=b"without a rollback trigger",
        evidence_locator="git:bbb222:docs/strategy.md#rollout",
        claimed_origin="fix_introduced",
        ratifier="human:maintainer",
    )

    assert introduced.record["defect_origin"] == "fix_introduced"
    assert introduced.record["observable_revision_digest"] == child.digest
    assert introduced.record["parent_revision_id"] == parent.record_id
    assert introduced.record["parent_revision_digest"] == parent.digest
    assert introduced.record["remediation_event_locator"] == "review-fix:round-2"
    assert introduced.record["responsible_stage"] == "remediation"
    assert introduced.record["diff_digest"] == child.record["diff"]["digest"]
    assert introduced.record["excluded_from_origin_rates"] is False
    assert parent.path.read_bytes() == parent_bytes

    empty = store.publish_document_revision(
        tmp_path,
        "document-case-2-empty",
        snapshot_bytes=b"",
        event_locator="workspace:new-file",
        responsible_stage="pre_authoring",
    )
    first_draft = store.correct_document_revision(
        tmp_path,
        empty.record_id,
        snapshot_bytes=b"# Strategy\n\nLaunch with no rollback trigger.\n",
        event_locator="git:ccc333:docs/strategy.md",
        responsible_stage="initial_authoring",
    )
    initial = store.ratify_defect_origin(
        tmp_path,
        "origin-case-2-risk-r1",
        observable_revision_id=first_draft.record_id,
        defect_evidence=b"no rollback trigger",
        evidence_locator="git:ccc333:docs/strategy.md#strategy",
        claimed_origin="initial_writing",
        ratifier="human:maintainer",
    )
    assert initial.record["defect_origin"] == "initial_writing"
    assert initial.record["parent_revision_id"] == empty.record_id
    assert initial.record["responsible_stage"] == "initial_authoring"
    assert initial.record["excluded_from_origin_rates"] is False

    final_only = store.publish_document_revision(
        tmp_path,
        "document-final-only",
        snapshot_bytes=b"# Final\n\nAn observable consequential defect.\n",
        event_locator="archive:final-only",
        responsible_stage="unknown",
        lineage_available=False,
    )
    unknown = store.ratify_defect_origin(
        tmp_path,
        "origin-final-only-r1",
        observable_revision_id=final_only.record_id,
        defect_evidence=b"consequential defect",
        evidence_locator="archive:final-only#defect",
        claimed_origin="initial_writing",
        ratifier="human:maintainer",
    )

    assert unknown.record["defect_origin"] == "unknown"
    assert unknown.record["missing_revision_evidence"] == [
        "parent_revision",
        "inspectable_diff",
    ]
    assert unknown.record["excluded_from_origin_rates"] is True
    assert "parent_revision_id" not in unknown.record


def test_req_112_authority_and_ratifier_independence(tmp_path) -> None:
    # @req: REQ-112
    """Official human judgments bind authority and fail closed on conflicts."""
    roles = {
        "execution_actor": "executor:weak-runner",
        "document_author": "author:writer",
        "oracle_author": "author:oracle-drafter",
        "oracle_ratifier": "maintainer:oracle-ratifier",
        "attribution_ratifier": "maintainer:attribution-ratifier",
        "reviewer_output_author": "model:weak-reviewer",
        "policy_owner": "maintainer:campaign-owner",
    }
    authority = store.publish_authority_assignment(
        tmp_path,
        "authority-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities={
            "ratify_oracle": ["maintainer:oracle-ratifier"],
            "ratify_attribution": ["maintainer:attribution-ratifier"],
            "ratify_defect_origin": ["maintainer:attribution-ratifier"],
        },
        allowed_self_ratification=[],
    )
    oracle = store.ratify_governed_oracle(
        tmp_path,
        "oracle-governed-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=[
            {
                "finding_id": "missing-risk",
                "expectation": "The review names the risk.",
                "rationale": "The risk changes the decision.",
                "evidence_locator": "git:abc:docs/strategy.md#risk",
            }
        ],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier="maintainer:oracle-ratifier",
        authority_revision_id=authority.record_id,
    )

    assert oracle.record["authority_revision_id"] == authority.record_id
    assert oracle.record["authority_revision_digest"] == authority.digest
    assert oracle.record["role_identities"] == roles
    assert oracle.record["independence_evidence"]["status"] == "satisfied"
    assert oracle.record["eligible_for_official_metrics"] is True
    assert oracle.record["status"] == "ratified"

    denied = store.ratify_governed_oracle(
        tmp_path,
        "oracle-unauthorized-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier="maintainer:intruder",
        authority_revision_id=authority.record_id,
    )
    assert denied.record["kind"] == "governance_audit_event"
    assert denied.record["outcome"] == "refused_unauthorized"
    assert denied.record["actor"] == "maintainer:intruder"
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "oracle-unauthorized-r1")

    conflicted_roles = dict(roles)
    conflicted_roles["oracle_ratifier"] = conflicted_roles["document_author"]
    conflicted = store.publish_authority_assignment(
        tmp_path,
        "authority-conflicted-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=conflicted_roles,
        action_authorities={"ratify_oracle": [conflicted_roles["oracle_ratifier"]]},
        allowed_self_ratification=[],
    )
    disputed = store.ratify_governed_oracle(
        tmp_path,
        "oracle-conflicted-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier=conflicted_roles["oracle_ratifier"],
        authority_revision_id=conflicted.record_id,
    )
    assert disputed.record["status"] == "disputed"
    assert disputed.record["excluded_from_affected_denominators"] is True
    assert disputed.record["eligible_for_official_metrics"] is False
    assert disputed.record["independence_evidence"]["status"] == "insufficient"

    revised = store.revise_authority_assignment(
        tmp_path,
        authority.record_id,
        role_identities={**roles, "execution_actor": "executor:replacement"},
        action_authorities=authority.record["action_authorities"],
        allowed_self_ratification=[],
        reason="The original executor rotated out of the campaign.",
    )
    assert revised.record["parent_revision_id"] == authority.record_id
    assert revised.record["parent_digest"] == authority.digest
    assert revised.record["revision_reason"]
    assert read_record(tmp_path, authority.record_id) == authority

def test_canonical_record_publish_is_atomic_and_content_addressed(tmp_path) -> None:
    """A record ID chooses one canonical payload without rewriting history."""
    first = {"kind": "oracle", "labels": ["a"], "version": 1}
    equivalent = {"version": 1, "labels": ["a"], "kind": "oracle"}
    conflicting = {"kind": "oracle", "labels": ["b"], "version": 1}

    assert canonical_json_bytes(first) == canonical_json_bytes(equivalent)
    assert record_digest(first) == record_digest(equivalent)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(publish_record, tmp_path, "oracle-1", record)
            for record in (first, conflicting)
        ]
    results = [future.exception() or future.result() for future in futures]
    published = [result for result in results if not isinstance(result, Exception)]
    conflicts = [result for result in results if isinstance(result, RecordConflictError)]

    assert len(published) == 1
    assert len(conflicts) == 1
    winner = published[0]
    assert winner.digest in {record_digest(first), record_digest(conflicting)}
    assert publish_record(tmp_path, "oracle-1", winner.record) == winner
    with pytest.raises(RecordConflictError):
        publish_record(tmp_path, "oracle-1", conflicting if winner.record == first else first)

    revision = append_revision(tmp_path, "oracle-1", {"status": "corrected"})
    assert revision.record["parent_digest"] == winner.digest
    assert revision.record_id != winner.record_id


def test_publish_refuses_symlinked_store_root(tmp_path) -> None:
    """A caller cannot redirect publication by replacing the store root."""
    actual_store = tmp_path / "actual-store"
    actual_store.mkdir()
    store_alias = tmp_path / "store-alias"
    store_alias.symlink_to(actual_store, target_is_directory=True)

    with pytest.raises(OSError):
        publish_record(store_alias, "oracle-1", {"kind": "oracle"})

    assert not (actual_store / "records").exists()


def test_publish_refuses_symlinked_records_directory(tmp_path) -> None:
    """The records component cannot redirect a descriptor-anchored write."""
    outside = tmp_path / "outside"
    outside.mkdir()
    store_root = tmp_path / "store"
    store_root.mkdir()
    (store_root / "records").symlink_to(outside, target_is_directory=True)

    with pytest.raises(OSError):
        publish_record(store_root, "oracle-1", {"kind": "oracle"})

    assert list(outside.iterdir()) == []


def test_record_operations_refuse_final_symlink(tmp_path) -> None:
    """Neither idempotent publish nor read may follow a substituted record."""
    records = tmp_path / "records"
    records.mkdir()
    payload = canonical_json_bytes({"kind": "oracle"})
    outside = tmp_path / "outside.json"
    outside.write_bytes(payload)
    (records / "oracle-1.json").symlink_to(outside)

    with pytest.raises(OSError):
        read_record(tmp_path, "oracle-1")
    with pytest.raises(OSError):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})

    assert outside.read_bytes() == payload


def test_record_operations_refuse_non_regular_existing_record(tmp_path) -> None:
    """A directory at a record name is invalid evidence, not a record."""
    record_path = tmp_path / "records" / "oracle-1.json"
    record_path.mkdir(parents=True)

    with pytest.raises(ValueError, match="not a regular file"):
        read_record(tmp_path, "oracle-1")
    with pytest.raises(ValueError, match="not a regular file"):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})


def test_publish_fsyncs_directory_after_link_and_unlink(tmp_path, monkeypatch) -> None:
    """Each publication metadata change is followed by a directory sync."""
    (tmp_path / "records").mkdir()
    events: list[str] = []
    real_fsync = os.fsync
    real_link = os.link
    real_unlink = os.unlink

    def recording_fsync(fd: int) -> None:
        events.append("dir-fsync" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file-fsync")
        real_fsync(fd)

    def recording_link(*args, **kwargs) -> None:
        events.append("link")
        real_link(*args, **kwargs)

    def recording_unlink(*args, **kwargs) -> None:
        events.append("unlink")
        real_unlink(*args, **kwargs)

    monkeypatch.setattr(store.os, "fsync", recording_fsync)
    monkeypatch.setattr(store.os, "link", recording_link)
    monkeypatch.setattr(store.os, "unlink", recording_unlink)

    publish_record(tmp_path, "oracle-1", {"kind": "oracle"})

    assert events == ["file-fsync", "link", "dir-fsync", "unlink", "dir-fsync"]


def test_publish_fails_loud_when_directory_fsync_fails(tmp_path, monkeypatch) -> None:
    """A record is not reported durable when directory durability is absent."""
    real_fsync = os.fsync

    def unavailable_for_directories(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("directory fsync unavailable")
        real_fsync(fd)

    monkeypatch.setattr(store.os, "fsync", unavailable_for_directories)

    with pytest.raises(OSError, match="directory fsync unavailable"):
        publish_record(tmp_path, "oracle-1", {"kind": "oracle"})


def test_append_revision_preserves_parent_bytes_and_value(tmp_path) -> None:
    """A child revision cannot mutate the parent bytes or decoded value."""
    parent = publish_record(tmp_path, "oracle-1", {"kind": "oracle", "version": 1})
    parent_bytes = parent.path.read_bytes()
    parent_value = read_record(tmp_path, parent.record_id)

    append_revision(tmp_path, parent.record_id, {"status": "corrected"})

    assert parent.path.read_bytes() == parent_bytes
    assert read_record(tmp_path, parent.record_id) == parent_value
