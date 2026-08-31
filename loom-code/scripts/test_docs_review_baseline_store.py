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


_CAMPAIGN_ACTION_ROLES = {
    "nominate_historical_case": "case_nominator",
    "ratify_oracle": "oracle_ratifier",
    "ratify_attribution": "attribution_ratifier",
    "ratify_defect_origin": "attribution_ratifier",
    "dispatch_review": "run_dispatcher",
    "adjudicate_finding": "dispute_adjudicator",
    "freeze_evidence_population": "evidence_freezer",
    "invalidate_run": "run_invalidator",
    "inspect_raw_evidence": "raw_evidence_inspector",
    "publish_metric_report": "report_publisher",
}


def _campaign_roles() -> dict[str, str]:
    return {
        "execution_actor": "executor:weak-runner",
        "document_author": "author:writer",
        "oracle_author": "author:oracle-drafter",
        "oracle_ratifier": "maintainer:oracle-ratifier",
        "attribution_ratifier": "maintainer:attribution-ratifier",
        "reviewer_output_author": "model:weak-reviewer",
        "policy_owner": "maintainer:campaign-owner",
        "case_nominator": "maintainer:case-nominator",
        "run_dispatcher": "operator:run-dispatcher",
        "dispute_adjudicator": "maintainer:dispute-adjudicator",
        "evidence_freezer": "maintainer:evidence-freezer",
        "run_invalidator": "operator:run-invalidator",
        "raw_evidence_inspector": "auditor:raw-evidence-inspector",
        "report_publisher": "maintainer:report-publisher",
    }


def _campaign_action_authorities(roles: dict[str, str]) -> dict[str, list[str]]:
    return {
        action: [roles[role]]
        for action, role in _CAMPAIGN_ACTION_ROLES.items()
    }


def _bootstrap_dispatch_authority(store_root):
    roles = _campaign_roles()
    _authority, capability = store.bootstrap_campaign_authority(
        store_root,
        "authority-dispatch-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities=_campaign_action_authorities(roles),
        allowed_self_ratification=[],
    )
    return roles, capability


def _authorize_dispatch(store_root, attempt_id: str):
    roles, capability = _bootstrap_dispatch_authority(store_root)
    actor = roles["run_dispatcher"]
    receipt = store.authorize_governed_action_with_capability(
        store_root,
        capability=capability,
        action="dispatch_review",
        actor=actor,
        target=attempt_id,
    )
    return actor, receipt


def test_req_99_historical_case_admission(tmp_path) -> None:
    # @req: REQ-99
    """Governed nomination admits only explicit bytes or named missing evidence."""
    roles = _campaign_roles()
    _authority, capability = store.bootstrap_campaign_authority(
        tmp_path,
        "authority-case-admission-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities=_campaign_action_authorities(roles),
        allowed_self_ratification=[],
    )
    actor = roles["case_nominator"]
    snapshot = b"# Historical draft\n\nThe original document bytes.\n"
    candidate_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=actor,
        target="case-2026-08-27",
    )
    candidate = admit_historical_case(
        tmp_path,
        "case-2026-08-27",
        authorization_receipt=candidate_receipt,
        actor=actor,
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

    unscoreable_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=actor,
        target="case-narrative-only",
    )
    unscoreable = admit_historical_case(
        tmp_path,
        "case-narrative-only",
        authorization_receipt=unscoreable_receipt,
        actor=actor,
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

    records_before_refusal = sorted((tmp_path / "records").glob("case-*.json"))
    with pytest.raises(TypeError, match="authorization_receipt"):
        admit_historical_case(
            tmp_path,
            "case-direct",
            actor=actor,
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    forged_receipt = object.__new__(store.AuthorizationReceipt)
    with pytest.raises((TypeError, ValueError), match="receipt"):
        admit_historical_case(
            tmp_path,
            "case-forged",
            authorization_receipt=forged_receipt,
            actor=actor,
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    wrong_target_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=actor,
        target="case-other",
    )
    with pytest.raises(ValueError, match="target"):
        admit_historical_case(
            tmp_path,
            "case-wrong-target",
            authorization_receipt=wrong_target_receipt,
            actor=actor,
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    wrong_actor_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=actor,
        target="case-wrong-actor",
    )
    with pytest.raises(ValueError, match="actor"):
        admit_historical_case(
            tmp_path,
            "case-wrong-actor",
            authorization_receipt=wrong_actor_receipt,
            actor="maintainer:intruder",
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    other_action_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="dispatch_review",
        actor=roles["run_dispatcher"],
        target="case-other-action",
    )
    with pytest.raises(ValueError, match="action"):
        admit_historical_case(
            tmp_path,
            "case-other-action",
            authorization_receipt=other_action_receipt,
            actor=roles["run_dispatcher"],
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    other_store = tmp_path / "other-store"
    other_roles = _campaign_roles()
    _other_authority, other_capability = store.bootstrap_campaign_authority(
        other_store,
        "authority-other-store-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=other_roles,
        action_authorities=_campaign_action_authorities(other_roles),
        allowed_self_ratification=[],
    )
    other_store_receipt = store.authorize_governed_action_with_capability(
        other_store,
        capability=other_capability,
        action="nominate_historical_case",
        actor=other_roles["case_nominator"],
        target="case-other-store",
    )
    with pytest.raises(ValueError, match="different store"):
        admit_historical_case(
            tmp_path,
            "case-other-store",
            authorization_receipt=other_store_receipt,
            actor=other_roles["case_nominator"],
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    with pytest.raises(ValueError, match="consumed|stale"):
        admit_historical_case(
            tmp_path,
            "case-2026-08-27",
            authorization_receipt=candidate_receipt,
            actor=actor,
            snapshot_bytes=snapshot,
            source_locator="git:abc123:docs/example.md",
            evidence_locators=["review:2026-08-27#finding-4"],
        )
    assert sorted((tmp_path / "records").glob("case-*.json")) == records_before_refusal


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
    assert oracle.record["status"] == "ratified"
    assert oracle.record["governance_status"] == "unbound"
    assert oracle.record["eligible_for_official_metrics"] is False
    assert "authority_revision_id" not in oracle.record
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
    assert correction.record["status"] == "ratified"
    assert correction.record["governance_status"] == "unbound"
    assert correction.record["eligible_for_official_metrics"] is False
    assert "authority_revision_id" not in correction.record
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
    roles = _campaign_roles()
    authority, capability = store.bootstrap_campaign_authority(
        tmp_path,
        "authority-corpus-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities=_campaign_action_authorities(roles),
        allowed_self_ratification=[],
    )
    case_receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=roles["case_nominator"],
        target="case-1",
    )
    case = admit_historical_case(
        tmp_path,
        "case-1",
        authorization_receipt=case_receipt,
        actor=roles["case_nominator"],
        snapshot_bytes=b"# Exact historical draft\n",
        source_locator="git:abc123:docs/strategy.md",
        evidence_locators=["review:abc123#finding-1"],
    )
    snapshot_digest = case.record["snapshot"]["digest"]
    oracle = store.ratify_governed_oracle(
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
        ratifier="maintainer:oracle-ratifier",
        capability=capability,
    )
    bindings = [("case-1", snapshot_digest, oracle.record_id)]

    manifest = store.freeze_corpus_manifest(
        tmp_path,
        bindings,
        capability=capability,
    )
    frozen_bytes = manifest.path.read_bytes()

    assert manifest.record == {
        "bindings": [
            {
                "authority_revision_digest": authority.digest,
                "case_id": "case-1",
                "oracle_revision_id": "oracle-case-1-r1",
                "snapshot_digest": snapshot_digest,
            }
        ],
        "kind": "corpus_manifest",
        "schema_version": 1,
        "trusted_authority_revision_digests": [authority.digest],
    }
    assert manifest.record_id == f"corpus-{manifest.digest}"
    assert store.freeze_corpus_manifest(
        tmp_path,
        bindings,
        capability=capability,
    ) == manifest
    assert manifest.path.read_bytes() == frozen_bytes

    with pytest.raises(ValueError, match="non-empty"):
        store.freeze_corpus_manifest(
            tmp_path, [], capability=capability
        )
    with pytest.raises(ValueError, match="latest"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", snapshot_digest, "latest")],
            capability=capability,
        )
    with pytest.raises(ValueError, match="ratified"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", snapshot_digest, case.record_id)],
            capability=capability,
        )
    with pytest.raises(ValueError, match="snapshot digest"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", "b" * 64, oracle.record_id)],
            capability=capability,
        )

    unbound = ratify_oracle(
        tmp_path,
        "oracle-case-1-unbound-r1",
        case_id="case-1",
        snapshot_digest=snapshot_digest,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic requests for detail.",
        ratifier="maintainer:oracle-ratifier",
    )
    with pytest.raises(ValueError, match="governance"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", snapshot_digest, unbound.record_id)],
            capability=capability,
        )

    ineligible_record = dict(oracle.record)
    ineligible_record["eligible_for_official_metrics"] = False
    ineligible = store.publish_record(
        tmp_path, "oracle-case-1-ineligible-r1", ineligible_record
    )
    with pytest.raises(ValueError, match="official metrics"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", snapshot_digest, ineligible.record_id)],
            capability=capability,
        )

    forged_record = dict(oracle.record)
    forged_record.update(
        {
            "ratifier": "maintainer:intruder",
            "governance_status": "bound",
            "independence_evidence": {
                "allowed_exceptions": [],
                "conflicting_roles": [],
                "ratifier_role": "oracle_ratifier",
                "rule": "distinct-role-identity-v1",
                "status": "satisfied",
            },
            "eligible_for_official_metrics": True,
        }
    )
    forged = store.publish_record(
        tmp_path, "oracle-case-1-forged-governance-r1", forged_record
    )
    with pytest.raises(ValueError, match="authority does not authorize ratifier"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-1", snapshot_digest, forged.record_id)],
            capability=capability,
        )


def test_req_103_attempt_ledger_preserves_failures(tmp_path) -> None:
    # @req: REQ-103
    """Every dispatch is counted even when it never yields usable findings."""
    actor, receipt = _authorize_dispatch(tmp_path, "attempt-1")
    prepared = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-1",
        authorization_receipt=receipt,
        actor=actor,
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

    actor_2, receipt_2 = _authorize_dispatch(tmp_path, "attempt-2")
    usable = store.record_dispatch_outcome(
        tmp_path,
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-2",
            authorization_receipt=receipt_2,
            actor=actor_2,
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

    actor_3, receipt_3 = _authorize_dispatch(tmp_path, "attempt-3")
    retry = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-3",
        authorization_receipt=receipt_3,
        actor=actor_3,
        sequence=3,
        profile_id="codex:gpt-5.6-luna:economy",
        corpus_id="corpus-abc",
        case_id="case-1",
    )
    assert retry.record_id != prepared.record_id
    conflict_actor, conflict_receipt = _authorize_dispatch(tmp_path, "attempt-1")
    with pytest.raises(RecordConflictError):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-1",
            authorization_receipt=conflict_receipt,
            actor=conflict_actor,
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
        attempt_id = f"attempt-{sequence}"
        attempt_actor, attempt_receipt = _authorize_dispatch(tmp_path, attempt_id)
        attempt = store.prepare_dispatch_attempt(
            tmp_path,
            attempt_id,
            authorization_receipt=attempt_receipt,
            actor=attempt_actor,
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


def test_req_103_req_112_dispatch_requires_one_exact_authorization(tmp_path) -> None:
    # @req: REQ-103
    # @req: REQ-112
    """Attempt publication consumes one trust-root-bound dispatch receipt."""
    actor, receipt = _authorize_dispatch(tmp_path, "attempt-authorized")
    authorized = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-authorized",
        authorization_receipt=receipt,
        actor=actor,
        sequence=1,
        profile_id="codex:gpt-5.6-luna:economy",
        corpus_id="corpus-abc",
        case_id="case-1",
    )
    assert authorized.record["status"] == "prepared"

    stale_actor, stale_receipt = _authorize_dispatch(tmp_path, "attempt-stale")
    store.consume_authorization_receipt(
        tmp_path,
        stale_receipt,
        action="dispatch_review",
        actor=stale_actor,
        target="attempt-stale",
    )
    with pytest.raises(ValueError, match="consumed|stale"):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-stale",
            authorization_receipt=stale_receipt,
            actor=stale_actor,
            sequence=1,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "attempt-stale")

    with pytest.raises(TypeError, match="authorization_receipt"):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-missing-receipt",
            actor=actor,
            sequence=1,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "attempt-missing-receipt")

    roles, capability = _bootstrap_dispatch_authority(tmp_path)
    cases = []
    wrong_target = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="dispatch_review",
        actor=actor,
        target="some-other-attempt",
    )
    cases.append(("attempt-wrong-target", wrong_target, actor, "target"))
    wrong_actor = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="dispatch_review",
        actor=actor,
        target="attempt-wrong-actor",
    )
    cases.append(("attempt-wrong-actor", wrong_actor, "operator:intruder", "actor"))
    wrong_action = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=roles["case_nominator"],
        target="attempt-wrong-action",
    )
    cases.append(
        ("attempt-wrong-action", wrong_action, roles["case_nominator"], "action")
    )
    for attempt_id, bad_receipt, supplied_actor, error in cases:
        with pytest.raises(ValueError, match=error):
            store.prepare_dispatch_attempt(
                tmp_path,
                attempt_id,
                authorization_receipt=bad_receipt,
                actor=supplied_actor,
                sequence=2,
                profile_id="codex:gpt-5.6-luna:economy",
                corpus_id="corpus-abc",
                case_id="case-1",
            )
        with pytest.raises(ValueError, match="does not exist"):
            read_record(tmp_path, attempt_id)

    with pytest.raises(TypeError, match="receipt"):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-forged",
            authorization_receipt=object(),
            actor=actor,
            sequence=3,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "attempt-forged")

    other_store = tmp_path / "other-store"
    other_actor, other_receipt = _authorize_dispatch(
        other_store, "attempt-wrong-store"
    )
    with pytest.raises(ValueError, match="different store"):
        store.prepare_dispatch_attempt(
            tmp_path,
            "attempt-wrong-store",
            authorization_receipt=other_receipt,
            actor=other_actor,
            sequence=4,
            profile_id="codex:gpt-5.6-luna:economy",
            corpus_id="corpus-abc",
            case_id="case-1",
        )
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "attempt-wrong-store")

def test_req_104_observation_and_attribution_are_separate(tmp_path) -> None:
    # @req: REQ-104
    """Model claims stay lossless; only named humans ratify judgments."""
    actor, receipt = _authorize_dispatch(tmp_path, "attempt-observation-1")
    attempt = store.prepare_dispatch_attempt(
        tmp_path,
        "attempt-observation-1",
        authorization_receipt=receipt,
        actor=actor,
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


def test_req_112_authority_and_independence_are_explicit(tmp_path) -> None:
    # @req: REQ-112
    """Official human judgments bind authority and fail closed on conflicts."""
    roles = _campaign_roles()
    authority, capability = store.bootstrap_campaign_authority(
        tmp_path,
        "authority-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities=_campaign_action_authorities(roles),
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
        capability=capability,
    )

    assert oracle.record["authority_revision_id"] == authority.record_id
    assert oracle.record["authority_revision_digest"] == authority.digest
    assert oracle.record["authority_trust"] == {
        "rule": "campaign-bootstrap-digest-v1",
        "trusted_authority_revision_digest": authority.digest,
    }
    assert oracle.record["role_identities"] == roles
    assert oracle.record["independence_evidence"]["status"] == "satisfied"
    assert oracle.record["eligible_for_official_metrics"] is True
    assert oracle.record["status"] == "ratified"
    manifest = store.freeze_corpus_manifest(
        tmp_path,
        [("case-governed", "a" * 64, oracle.record_id)],
        capability=capability,
    )
    assert manifest.record["bindings"] == [
        {
            "authority_revision_digest": authority.digest,
            "case_id": "case-governed",
            "oracle_revision_id": oracle.record_id,
            "snapshot_digest": "a" * 64,
        }
    ]

    legacy_oracle = store.ratify_oracle(
        tmp_path,
        "oracle-unbound-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier="maintainer:oracle-ratifier",
    )
    assert legacy_oracle.record["governance_status"] == "unbound"
    assert legacy_oracle.record["eligible_for_official_metrics"] is False
    with pytest.raises(ValueError, match="governance is not bound and satisfied"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-governed", "a" * 64, legacy_oracle.record_id)],
            capability=capability,
        )

    denied = store.ratify_governed_oracle(
        tmp_path,
        "oracle-unauthorized-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier="maintainer:intruder",
        capability=capability,
    )
    assert denied.record["kind"] == "governance_audit_event"
    assert denied.record["outcome"] == "refused_unauthorized"
    assert denied.record["actor"] == "maintainer:intruder"
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "oracle-unauthorized-r1")

    assert store.GOVERNED_ACTION_ROLES == _CAMPAIGN_ACTION_ROLES
    assert authority.record["action_authorities"] == (
        _campaign_action_authorities(roles)
    )
    for action, role in _CAMPAIGN_ACTION_ROLES.items():
        audit = store.authorize_governed_action(
            tmp_path,
            authority_revision_id=authority.record_id,
            action=action,
            actor=roles[role],
            target=f"probe-{action}",
            trusted_authority_revision_digest=authority.digest,
        )
        assert audit.record["outcome"] == "authorized"
        assert audit.record["action"] == action
    with pytest.raises(ValueError, match="unsupported governed action"):
        store.authorize_governed_action(
            tmp_path,
            authority_revision_id=authority.record_id,
            action="delete_campaign",
            actor=roles["policy_owner"],
            target="campaign-r1",
            trusted_authority_revision_digest=authority.digest,
        )

    authorized_dispatch = store.authorize_governed_action(
        tmp_path,
        authority_revision_id=authority.record_id,
        action="dispatch_review",
        actor=roles["run_dispatcher"],
        target="run-not-created-yet",
        trusted_authority_revision_digest=authority.digest,
    )
    assert authorized_dispatch.record == {
        "action": "dispatch_review",
        "actor": roles["run_dispatcher"],
        "authority_revision_digest": authority.digest,
        "authority_revision_id": authority.record_id,
        "campaign_policy_revision_id": "policy-r1",
        "kind": "governance_audit_event",
        "outcome": "authorized",
        "schema_version": 1,
        "target": "run-not-created-yet",
    }
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "run-not-created-yet")

    refused_dispatch = store.authorize_governed_action(
        tmp_path,
        authority_revision_id=authority.record_id,
        action="dispatch_review",
        actor="operator:intruder",
        target="run-still-not-created",
        trusted_authority_revision_digest=authority.digest,
    )
    assert refused_dispatch.record["outcome"] == "refused_unauthorized"
    assert refused_dispatch.record["campaign_policy_revision_id"] == "policy-r1"
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "run-still-not-created")

    conflicted_roles = dict(roles)
    conflicted_roles["oracle_ratifier"] = conflicted_roles["document_author"]
    conflicted_store = tmp_path / "conflicted"
    conflicted, conflicted_capability = store.bootstrap_campaign_authority(
        conflicted_store,
        "authority-conflicted-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=conflicted_roles,
        action_authorities={
            **_campaign_action_authorities(conflicted_roles),
            "ratify_oracle": [conflicted_roles["oracle_ratifier"]],
        },
        allowed_self_ratification=[],
    )
    disputed = store.ratify_governed_oracle(
        conflicted_store,
        "oracle-conflicted-r1",
        case_id="case-governed",
        snapshot_digest="a" * 64,
        findings=oracle.record["findings"],
        negative_control_intent="Do not reward generic detail requests.",
        ratifier=conflicted_roles["oracle_ratifier"],
        capability=conflicted_capability,
    )
    assert disputed.record["status"] == "disputed"
    assert disputed.record["excluded_from_affected_denominators"] is True
    assert disputed.record["eligible_for_official_metrics"] is False
    assert disputed.record["independence_evidence"]["status"] == "insufficient"
    with pytest.raises(ValueError, match="oracle revision is not ratified"):
        store.freeze_corpus_manifest(
            conflicted_store,
            [("case-governed", "a" * 64, disputed.record_id)],
            capability=conflicted_capability,
        )

    forged_roles = dict(roles)
    forged_roles["oracle_author"] = "maintainer:self-authorizer"
    forged_roles["oracle_ratifier"] = "maintainer:self-authorizer"
    forged_authority = store.publish_authority_assignment(
        tmp_path,
        "authority-self-authored-r1",
        campaign_policy_revision_id="policy-forged-r1",
        role_identities=forged_roles,
        action_authorities={
            **_campaign_action_authorities(forged_roles),
            "ratify_oracle": ["maintainer:self-authorizer"],
        },
        allowed_self_ratification=["oracle_ratifier=oracle_author"],
    )
    records_before_refusal = sorted(
        path.name for path in (tmp_path / "records").iterdir()
    )
    with pytest.raises((TypeError, ValueError), match="capability"):
        store.ratify_governed_oracle(
            tmp_path,
            "oracle-self-authorized-r1",
            case_id="case-governed",
            snapshot_digest="a" * 64,
            findings=oracle.record["findings"],
            negative_control_intent="Do not reward generic detail requests.",
            ratifier="maintainer:self-authorizer",
            capability=forged_authority.digest,
        )
    assert sorted(path.name for path in (tmp_path / "records").iterdir()) == (
        records_before_refusal
    )
    with pytest.raises((TypeError, ValueError), match="capability"):
        store.freeze_corpus_manifest(
            tmp_path,
            [("case-governed", "a" * 64, oracle.record_id)],
            capability=forged_authority.digest,
        )

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


def test_req_112_bootstrap_capability_and_single_purpose_receipt(tmp_path) -> None:
    # @req: REQ-112
    """Only the campaign trust root can authorize a bound mutation."""
    roles = _campaign_roles()
    action_authorities = _campaign_action_authorities(roles)
    authority, capability = store.bootstrap_campaign_authority(
        tmp_path,
        "authority-bootstrap-r1",
        campaign_policy_revision_id="policy-r1",
        role_identities=roles,
        action_authorities=action_authorities,
        allowed_self_ratification=[],
    )

    assert authority.record["trust_root_digest"] == capability.trust_root_digest
    assert capability.authority_revision_digest == authority.digest
    assert (tmp_path / "campaign-trust-root.json").is_file()
    assert not (tmp_path / "records" / "campaign-trust-root.json").exists()

    receipt = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=roles["case_nominator"],
        target="case-bootstrap",
    )
    assert receipt.trust_root_digest == capability.trust_root_digest
    assert receipt.authority_revision_digest == authority.digest
    audit = read_record(tmp_path, receipt.audit_record_id)
    assert audit.record["outcome"] == "authorized"
    assert audit.record["actor"] == roles["case_nominator"]
    assert audit.record["target"] == "case-bootstrap"

    store.consume_authorization_receipt(
        tmp_path,
        receipt,
        action="nominate_historical_case",
        actor=roles["case_nominator"],
        target="case-bootstrap",
    )
    with pytest.raises(ValueError, match="consumed|stale"):
        store.consume_authorization_receipt(
            tmp_path,
            receipt,
            action="nominate_historical_case",
            actor=roles["case_nominator"],
            target="case-bootstrap",
        )

    fresh = store.authorize_governed_action_with_capability(
        tmp_path,
        capability=capability,
        action="nominate_historical_case",
        actor=roles["case_nominator"],
        target="case-other",
    )
    with pytest.raises(ValueError, match="target"):
        store.consume_authorization_receipt(
            tmp_path,
            fresh,
            action="nominate_historical_case",
            actor=roles["case_nominator"],
            target="case-bootstrap",
        )
    with pytest.raises(ValueError, match="action"):
        store.consume_authorization_receipt(
            tmp_path,
            fresh,
            action="dispatch_review",
            actor=roles["case_nominator"],
            target="case-other",
        )

    forged_authority = store.publish_authority_assignment(
        tmp_path,
        "authority-self-published-r1",
        campaign_policy_revision_id="policy-forged-r1",
        role_identities=roles,
        action_authorities=action_authorities,
        allowed_self_ratification=[],
    )
    with pytest.raises((TypeError, ValueError), match="capability"):
        store.authorize_governed_action_with_capability(
            tmp_path,
            capability=forged_authority.digest,
            action="nominate_historical_case",
            actor=roles["case_nominator"],
            target="case-forged",
        )
    with pytest.raises((TypeError, ValueError), match="receipt"):
        store.consume_authorization_receipt(
            tmp_path,
            object(),
            action="nominate_historical_case",
            actor=roles["case_nominator"],
            target="case-forged",
        )
    with pytest.raises(PermissionError, match="not authorized"):
        store.authorize_governed_action_with_capability(
            tmp_path,
            capability=capability,
            action="nominate_historical_case",
            actor="maintainer:intruder",
            target="case-denied",
        )
    denied = [
        path
        for path in (tmp_path / "records").glob("audit-*.json")
        if b'"target":"case-denied"' in path.read_bytes()
    ]
    assert len(denied) == 1
    assert b'"outcome":"refused_unauthorized"' in denied[0].read_bytes()
    with pytest.raises(ValueError, match="does not exist"):
        read_record(tmp_path, "case-denied")

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
