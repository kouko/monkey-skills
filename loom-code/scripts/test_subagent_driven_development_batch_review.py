"""Executable contract for SDD's derived Review Batch checkpoint.

The SDD skill is orchestration data rather than an importable runtime.  These
pins keep the Batch path closed and ordered: Task-local work reaches
``implemented`` first, one immutable aggregate packet is reviewed, and every
uncertain case reuses the existing individual loop without inventing Batch
state.
"""

from __future__ import annotations

from dataclasses import replace
import importlib.util
import re
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SDD_ROOT = REPO_ROOT / "loom-code" / "skills" / "subagent-driven-development"
SCRIPTS = REPO_ROOT / "loom-code" / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


review_batch = _load("review_batch", "review_batch.py")
plan_card = _load("plan_card_t6_contract", "plan_card.py")


def _normalized(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8")).strip()


def _window(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    return text[begin : text.index(end, begin)]


def test_batch_dispatch_and_fallback_contract() -> None:
    # @req: REQ-106
    skill = _normalized(SDD_ROOT / "SKILL.md")
    ledger = _normalized(SDD_ROOT / "references" / "plan-ledger-notes.md")
    conditional = _normalized(
        SDD_ROOT / "references" / "conditional-operations.md"
    )

    # The normal Task loop must branch only after Task-local mechanical proof.
    batch = _window(skill, "Batch review checkpoint", "Progress ledger")
    assert batch.index("implemented(<sha>)") < batch.index("Batch-ready")
    assert "same-batch dependencies may consume `implemented`; cross-batch dependencies require `done`" in batch.lower()
    assert "one reviewer fan-out for the whole Batch" in batch
    assert "full lane" in batch and "spec-reviewer" in batch and "code-quality-reviewer" in batch
    assert "prose lane" in batch and "record-class" in batch and "docs-reviewer" in batch
    assert "mechanical lane never receives an aggregate full review" in batch

    # Aggregate verification is resolved from a trusted executable surface;
    # the plan's prose is only declaration identity and is never a command.
    for phrase in (
        "mandatory `check_review_batches.py` checker",
        "ExecutionAuthorityProjection",
        "checker → projection issuance → Packet → reviewer dispatch",
        "declared-first verification resolver",
        "SafeResolutionReceipt",
        "immutable `ReviewPacket`",
        "never execute the plan's `Aggregate verification` text",
        "no Packet, no reviewer dispatch, and no status mutation",
        "existing verification recovery path",
    ):
        assert phrase in batch

    # Result reduction has a closed mapping onto existing ledger verbs.
    assert "`finalize`" in batch and "atomic Batch status update" in batch
    assert "`reopen`" in batch and "owner union" in batch
    assert "fresh mechanical verification" in batch and "fresh Packet" in batch
    assert "`individual_fallback`" in batch
    assert "zero Batch ledger mutation" in batch
    assert "fresh per-Task immutable packet" in batch
    assert "existing individual reviewer loop" in batch
    assert "SDD orchestrator is the only ledger writer" in batch
    assert "reviewers and implementers never mutate the ledger" in batch

    # R9: whole-branch review entry after Batch finalize / individual
    # resolution is an unconditional sequence step — no interactive-mode
    # exception.
    assert "necessarily proceeds to the existing whole-branch review" in batch
    assert "no mode exception" in batch

    # The durable ledger contract describes implemented as a Task state, not a
    # second Batch lifecycle, and keeps owner-only repair atomic.
    for phrase in (
        "locally committed and mechanically verified",
        "not a Batch status",
        "complete validated Batch member set",
        "unchanged members remain `implemented(<sha>)`",
        "participating Loom writer lock",
    ):
        assert phrase in ledger

    # Trigger-point details are centralized in the conditional reference so
    # the main loop does not grow a second implementation of lane/fallback
    # policy.
    operations = _window(
        conditional, "Batch review and individual fallback", "Orchestrator command hygiene"
    )
    assert "ordered fail-closed sequence" in operations
    assert "mandatory `check_review_batches.py` checker" in operations
    assert "caller-created, missing, or context-mismatched projection" in operations
    assert "Aggregate verification" in operations and "inert" in operations
    assert "checker, projection issuance, resolution, execution, evidence" in operations
    assert "individual fallback" in operations
    assert "does not create Batch state" in operations
    assert "park the implemented member" in operations
    assert "next runnable Task in the same Batch" in operations
    assert "temporary incompleteness is not individual fallback" in operations.lower()


def _plan(statuses: tuple[str, str], *, lane: str = "full") -> str:
    return f"""# Plan

Goal: prove exact decision CAS.
Stage: sdd:wave-1

## Task 1 — first

- **Description**: fixture
- **Dependencies**: none
- **Files touched**: src/1.py
- **Acceptance**: accept-1
- **Brief item covered**: REQ-1
- **Review-weight**: {lane}
- **Review disposition**: batch(capability)
- **Status**: {statuses[0]}

## Task 2 — second

- **Description**: fixture
- **Dependencies**: Task 1 completes first
- **Files touched**: src/2.py
- **Acceptance**: accept-2
- **Brief item covered**: REQ-2
- **Review-weight**: {lane}
- **Review disposition**: batch(capability)
- **Status**: {statuses[1]}

## Review Batches

### Review Batch: capability
- **Members**: Task 1, Task 2
- **Verdict question**: Does the capability work?
- **Review lane**: {lane}
- **Aggregate verification**: package test suite
- **Boundary**: capability: fixture; exclusions: none; consumable: yes
"""


def _actual_batch_packet():
    plan_path = REPO_ROOT / "docs" / "loom" / "plans" / "2026-08-30-task-batch-review.md"
    plan_text = plan_path.read_text(encoding="utf-8")
    fields = review_batch._review_batch_oracle().execution_projection_fields(
        plan_text, "sdd-review-loop"
    )
    declaration = review_batch.BatchDeclaration(**fields["declaration"])
    members = []
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    for index, projected in enumerate(fields["members"], 6):
        sha = str(index) * 40
        files = tuple(
            review_batch.ReviewedFile(path, f"{projected['task_id']}:{path}".encode())
            for path in projected["declared_files"]
        )
        members.append(review_batch.MemberSnapshot(
            task_id=projected["task_id"],
            status=f"implemented({sha})",
            sha=sha,
            declared_files=projected["declared_files"],
            files=files,
            owned_requirements=projected["owned_requirements"],
            future_requirements=projected["future_requirements"],
            acceptance=projected["acceptance"],
            scope_proof=scope_issuer.issue(
                repository_identity="e" * 64,
                commit_sha=sha,
                tree_identity=sha,
                files=files,
            ),
        ))
    members = tuple(members)
    records = tuple(review_batch.OwnershipRecord(
        member.task_id,
        member.owned_requirements,
        member.future_requirements,
        member.acceptance,
    ) for member in members)
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="authority:v1",
        source_digest="c" * 64,
    )
    ownership = issuer.issue_ownership(
        plan_identity="plan:actual-t6-t7",
        spec_identity="spec:task-batch-review",
        records=records,
        execution_projection=review_batch._issue_execution_projection_from_validated_plan(
            plan_text=plan_text,
            batch_id="sdd-review-loop",
            plan_identity="plan:actual-t6-t7",
            spec_identity="spec:task-batch-review",
            records=records,
            issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest="8" * 64,
        ),
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="f" * 64,
    ).issue(review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(declaration.aggregate_verification),
        argv=("python3", "-m", "pytest"),
        execution_scope=("loom-code",),
        result="exit=0",
        scanner_receipt_identity="scanner:actual-t6-t7",
        scanner_input_digest="d" * 64,
    ))
    packet = review_batch.materialize_packet(
        declaration, members, ownership, issuer.issue_verification(receipt)
    )
    return plan_text, fields, packet


def test_actual_t6_t7_projection_is_packet_ready_and_acceptance_drifts_cas(tmp_path) -> None:
    plan_text, fields, packet = _actual_batch_packet()
    task6, task7 = fields["members"]
    assert task6["declared_files"][0] == (
        "loom-code/skills/subagent-driven-development/SKILL.md"
    )
    assert task7["declared_files"] == (
        "loom-code/skills/subagent-driven-development/SKILL.md",
        "loom-code/scripts/test_sdd_new_plan_intake.py",
    )
    assert task6["owned_requirements"] == (
        "REQ-103", "REQ-104", "REQ-105", "REQ-106", "REQ-107", "REQ-108",
    )
    assert task6["future_requirements"] == ()
    assert "**RED**:" in task6["acceptance"][0]
    assert any("**GREEN**:" in line for line in task6["acceptance"])
    assert review_batch.validate_packet(packet) == ()

    for bad_plan in (
        plan_text.replace(
            "- **Files touched**: `loom-code/skills/subagent-driven-development/SKILL.md`",
            "- **Files touched**: loom-code/skills/subagent-driven-development/SKILL.md",
            1,
        ),
        plan_text.replace(
            "`loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/skills/subagent-driven-development/references/plan-ledger-notes.md`",
            "`../unsafe.py`, `loom-code/skills/subagent-driven-development/references/plan-ledger-notes.md`",
            1,
        ),
        plan_text.replace(
            "`loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/skills/subagent-driven-development/references/plan-ledger-notes.md`",
            "`loom-code/skills/subagent-driven-development/SKILL.md, `loom-code/skills/subagent-driven-development/references/plan-ledger-notes.md`",
            1,
        ),
    ):
        with pytest.raises(ValueError):
            review_batch._review_batch_oracle().execution_projection_fields(
                bad_plan, "sdd-review-loop"
            )

    records = packet.ownership.records
    ownership_mismatches = (
        records[:1],
        records + (records[0],),
        tuple(reversed(records)),
        (replace(records[0], owned_requirements=records[0].owned_requirements[:-1]), records[1]),
        (replace(records[0], owned_requirements=records[0].owned_requirements + ("REQ-999",)), records[1]),
        (replace(records[0], future_requirements=("REQ-109",)), records[1]),
    )
    for mismatch in ownership_mismatches:
        with pytest.raises(review_batch.PacketRefused):
            review_batch._issue_execution_projection_from_validated_plan(
                plan_text=plan_text,
                batch_id="sdd-review-loop",
                plan_identity="plan:actual-t6-t7",
                spec_identity="spec:task-batch-review",
                records=mismatch,
                issuer="plan-card:validated-schema",
                source_identity="plan:current",
                source_digest="8" * 64,
            )

    passing = _resolution(packet)
    assert passing.transition_authority is not None
    implemented = {
        int(member.task_id.split()[1]): member.status for member in packet.members
    }
    done = {
        number: status.replace("implemented(", "done(")
        for number, status in implemented.items()
    }
    for condition in task6["acceptance"]:
        stale = plan_text.replace(condition, condition + " amended", 1)
        assert stale != plan_text
        path = tmp_path / "plan.md"
        path.write_text(stale, encoding="utf-8")
        assert not plan_card.atomic_batch_status_update(
            path,
            "sdd-review-loop",
            implemented,
            done,
            transition_authority=passing.transition_authority,
        )
        assert path.read_bytes() == stale.encode()


def _packet():
    declaration = review_batch.BatchDeclaration(
        batch_id="capability",
        members=("Task 1", "Task 2"),
        verdict_question="Does the capability work?",
        review_lane="full",
        aggregate_verification="package test suite",
        boundary="capability: fixture; exclusions: none; consumable: yes",
    )
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    members = []
    for number, sha in ((1, "a" * 40), (2, "b" * 40)):
        path = f"src/{number}.py"
        files = (review_batch.ReviewedFile(path, f"member {number}".encode()),)
        members.append(
            review_batch.MemberSnapshot(
                task_id=f"Task {number}",
                status=f"implemented({sha})",
                sha=sha,
                declared_files=(path,),
                files=files,
                owned_requirements=(f"REQ-{number}",),
                future_requirements=(),
                acceptance=(f"accept-{number}",),
                scope_proof=scope_issuer.issue(
                    repository_identity="e" * 64,
                    commit_sha=sha,
                    tree_identity=sha,
                    files=files,
                ),
            )
        )
    members = tuple(members)
    proof_issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="authority:v1",
        source_digest="c" * 64,
    )
    records = tuple(
        review_batch.OwnershipRecord(
            member.task_id,
            member.owned_requirements,
            member.future_requirements,
            member.acceptance,
        )
        for member in members
    )
    ownership = proof_issuer.issue_ownership(
        plan_identity="plan:fixture",
        spec_identity="spec:fixture",
        records=records,
        execution_projection=review_batch._issue_execution_projection_from_validated_plan(
            plan_text=_plan((f"implemented({'a' * 40})", f"implemented({'b' * 40})")),
            batch_id="capability",
            plan_identity="plan:fixture",
            spec_identity="spec:fixture",
            records=records,
            issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest="8" * 64,
        ),
    )
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(
            declaration.aggregate_verification
        ),
        argv=("python3", "-m", "pytest"),
        execution_scope=("src",),
        result="exit=0",
        scanner_receipt_identity="scanner:fixture",
        scanner_input_digest="d" * 64,
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="f" * 64,
    ).issue(approved)
    return review_batch.materialize_packet(
        declaration, members, ownership, proof_issuer.issue_verification(receipt)
    )


def _resolution(packet, *, reopen: bool = False):
    arms = ("spec-reviewer", "code-quality-reviewer")
    bindings = tuple(
        review_batch.ReviewerArmBinding(
            packet.identity, arm, f"dispatch:{arm}", f"dispatch-proof:{arm}"
        )
        for arm in arms
    )
    finding = review_batch.BlockingFinding(
        finding_id="finding:task-2",
        packet_identity=packet.identity,
        arm="spec-reviewer",
        dispatch_identity="dispatch:spec-reviewer",
        evidence_identity="result-proof:spec-reviewer",
        owners=("Task 2",),
        blocking=True,
        ground="owned_requirement",
        ground_ref="REQ-2",
        location="src/2.py",
        severity="fatal",
        reason="fixture regression",
    )
    results = tuple(
        review_batch.ReviewerTerminalResult(
            packet_identity=packet.identity,
            arm=arm,
            dispatch_identity=f"dispatch:{arm}",
            dispatch_evidence_identity=f"dispatch-proof:{arm}",
            result_identity=f"result:{arm}:{'reopen' if reopen else 'pass'}",
            evidence_identity=f"result-proof:{arm}",
            terminal="completed",
            verdict="NEEDS_REVISION" if reopen and arm == arms[0] else "PASS",
            findings=(finding,) if reopen and arm == arms[0] else (),
        )
        for arm in arms
    )
    return review_batch.resolve_aggregate_review(
        packet=packet,
        declared_lane="full",
        expected_arms=arms,
        arm_bindings=bindings,
        terminal_results=results,
    )


def test_transition_authority_rejects_stale_packet_decisions(tmp_path) -> None:
    packet = _packet()
    implemented = {
        1: f"implemented({'a' * 40})",
        2: f"implemented({'b' * 40})",
    }
    done = {
        1: f"done({'a' * 40})",
        2: f"done({'b' * 40})",
    }
    passing = _resolution(packet)
    reopening = _resolution(packet, reopen=True)
    assert passing.action == "finalize"
    assert reopening.action == "reopen"
    assert passing.transition_authority is not None
    assert reopening.transition_authority is not None

    path = tmp_path / "plan.md"
    original = _plan(tuple(implemented.values()))
    path.write_text(original, encoding="utf-8")
    assert plan_card.atomic_batch_status_update(
        path, "capability", implemented, done,
        transition_authority=passing.transition_authority,
    )
    after = path.read_bytes()
    assert plan_card.atomic_batch_status_update(
        path, "capability", implemented, done,
        transition_authority=passing.transition_authority,
    )
    assert path.read_bytes() == after

    stale_plans = (
        original.replace("capability: fixture", "capability: amended"),
        _plan(tuple(implemented.values()), lane="prose"),
        original.replace(
            "- **Status**: implemented(" + "a" * 40 + ")",
            "- **Status**: implemented(" + "9" * 40 + ")",
        ),
        original.replace("- **Members**: Task 1, Task 2", "- **Members**: Task 1")
        .replace(
            "- **Review disposition**: batch(capability)\n"
            "- **Status**: implemented(" + "b" * 40 + ")",
            "- **Review disposition**: individual\n"
            "- **Status**: implemented(" + "b" * 40 + ")",
        ),
        original.replace("- **Dependencies**: Task 1 completes first", "- **Dependencies**: none", 1),
        original.replace("- **Acceptance**: accept-2", "- **Acceptance**: amended", 1),
        original.replace("- **Files touched**: src/2.py", "- **Files touched**: src/amended.py", 1),
        original.replace("- **Brief item covered**: REQ-2", "- **Brief item covered**: REQ-200", 1),
        original.replace("- **Review disposition**: batch(capability)", "- **Review disposition**: individual", 1),
        original.replace("- **Review-weight**: full", "- **Review-weight**: prose", 1),
    )
    for stale in stale_plans:
        path.write_text(stale, encoding="utf-8")
        assert not plan_card.atomic_batch_status_update(
            path, "capability", implemented, done,
            transition_authority=passing.transition_authority,
        )
        assert path.read_text(encoding="utf-8") == stale

        path.write_text(stale, encoding="utf-8")
        assert not plan_card.atomic_batch_status_update(
            path, "capability", implemented, {2: "pending"},
            transition_authority=reopening.transition_authority,
        )
        assert path.read_text(encoding="utf-8") == stale

    path.write_text(original, encoding="utf-8")
    assert not plan_card.atomic_batch_status_update(
        path, "capability", implemented, {2: "pending"},
        transition_authority=passing.transition_authority,
    )
    assert path.read_text(encoding="utf-8") == original
    assert plan_card.atomic_batch_status_update(
        path, "capability", implemented, {2: "pending"},
        transition_authority=reopening.transition_authority,
    )
    reopened_bytes = path.read_bytes()
    assert plan_card.atomic_batch_status_update(
        path, "capability", implemented, {2: "pending"},
        transition_authority=reopening.transition_authority,
    )
    assert path.read_bytes() == reopened_bytes
    assert f"- **Status**: implemented({'a' * 40})" in path.read_text(
        encoding="utf-8"
    )
    assert "- **Status**: pending" in path.read_text(encoding="utf-8")
