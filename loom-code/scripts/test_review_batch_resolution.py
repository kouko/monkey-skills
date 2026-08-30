"""Contract matrix for aggregate reviewer-result resolution."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib.util
from pathlib import Path
import sys


SCRIPT = Path(__file__).with_name("review_batch.py")
SPEC = importlib.util.spec_from_file_location("review_batch_resolution", SCRIPT)
assert SPEC and SPEC.loader
review_batch = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review_batch
SPEC.loader.exec_module(review_batch)


def _packet(lane="full"):
    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1", "Task 2", "Task 3"),
        verdict_question="Does the capability satisfy its contract?",
        review_lane=lane,
        aggregate_verification="pytest aggregate",
        boundary="capability: aggregate; exclusions: none; consumable: yes",
    )
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    members = []
    for number in range(1, 4):
        task_id = f"Task {number}"
        sha = str(number) * 40
        path = f"src/{number}.py"
        files = (review_batch.ReviewedFile(path, task_id.encode()),)
        members.append(
            review_batch.MemberSnapshot(
                task_id=task_id,
                status=f"implemented({sha})",
                sha=sha,
                declared_files=(path,),
                files=files,
                owned_requirements=(f"REQ-{number}",),
                future_requirements=(f"FUTURE-{number}",),
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
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="authority:v1",
        source_digest="a" * 64,
    )
    ownership = issuer.issue_ownership(
        plan_identity="plan:batch",
        spec_identity="spec:REQ-106-107",
        records=tuple(
            review_batch.OwnershipRecord(
                member.task_id,
                member.owned_requirements,
                member.future_requirements,
                member.acceptance,
            )
            for member in members
        ),
    )
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(
            declaration.aggregate_verification
        ),
        argv=("python3", "-m", "pytest"),
        execution_scope=("src",),
        result="exit=0",
        scanner_receipt_identity="scanner:1",
        scanner_input_digest="d" * 64,
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="c" * 64,
    ).issue(approved)
    evidence = issuer.issue_verification(receipt)
    return review_batch.materialize_packet(
        declaration, members, ownership, evidence
    )


def _bindings(packet):
    return tuple(
        review_batch.ReviewerArmBinding(
            packet_identity=packet.identity,
            arm=arm,
            dispatch_identity=f"dispatch:{arm}",
            evidence_identity=f"dispatch-evidence:{arm}",
        )
        for arm in ("spec-reviewer", "code-quality-reviewer")
    )


def _result(packet, arm, *, verdict="PASS", findings=(), terminal="completed"):
    return review_batch.ReviewerTerminalResult(
        packet_identity=packet.identity,
        arm=arm,
        dispatch_identity=f"dispatch:{arm}",
        dispatch_evidence_identity=f"dispatch-evidence:{arm}",
        result_identity=f"result:{arm}:{verdict}",
        evidence_identity=f"result-evidence:{arm}:{verdict}",
        terminal=terminal,
        verdict=verdict,
        findings=findings,
    )


def _finding(packet, finding_id, owners, *, arm="spec-reviewer",
             ground="owned_requirement", ground_ref="REQ-1"):
    return review_batch.BlockingFinding(
        finding_id=finding_id,
        packet_identity=packet.identity,
        arm=arm,
        dispatch_identity=f"dispatch:{arm}",
        evidence_identity=f"result-evidence:{arm}:NEEDS_REVISION",
        owners=owners,
        blocking=True,
        ground=ground,
        ground_ref=ground_ref,
        location="src/1.py",
        severity="fatal",
        reason="the exact reviewed behavior violates its ground",
    )


def _resolve(packet, results, *, arms=None, bindings=None, lane="full"):
    return review_batch.resolve_aggregate_review(
        packet=packet,
        declared_lane=lane,
        expected_arms=("spec-reviewer", "code-quality-reviewer")
        if arms is None
        else arms,
        arm_bindings=_bindings(packet) if bindings is None else bindings,
        terminal_results=results,
    )


def _assert_arm_matrix(packet) -> None:
    for arms in ((), ("spec-reviewer", "spec-reviewer"),
                 ("spec-reviewer", "unknown-reviewer"), ["spec-reviewer"]):
        refused = _resolve(packet, (), arms=arms)
        assert refused.action == "wait_refuse"
        assert refused.ledger_mutation_allowed is False

    prose_packet = _packet("prose")
    prose_spec = _result(prose_packet, "spec-reviewer")
    prose_docs = _result(prose_packet, "docs-reviewer")
    prose_bindings = tuple(
        review_batch.ReviewerArmBinding(
            prose_packet.identity, arm, f"dispatch:{arm}",
            f"dispatch-evidence:{arm}",
        )
        for arm in ("spec-reviewer", "docs-reviewer")
    )
    prose = _resolve(
        prose_packet, (prose_docs, prose_spec), lane="prose",
        arms=("spec-reviewer", "docs-reviewer"), bindings=prose_bindings,
    )
    assert prose.action == "finalize"
    record_bindings = prose_bindings[:1]
    record = _resolve(
        prose_packet, (prose_spec,), lane="prose",
        arms=("spec-reviewer",), bindings=record_bindings,
    )
    assert record.action == "finalize"
    mechanical = _resolve(
        packet, (), lane="mechanical", arms=("spec-reviewer",),
        bindings=_bindings(packet)[:1],
    )
    assert mechanical.action == "wait_refuse"


def _assert_result_provenance_matrix(packet, spec_pass, quality_pass) -> None:
    incomplete_or_ambiguous = (
        (spec_pass,),
        (spec_pass, quality_pass, quality_pass),
        (spec_pass, quality_pass, replace(quality_pass, verdict="NEEDS_REVISION")),
        (replace(spec_pass, packet_identity="wrong"), quality_pass),
        (replace(spec_pass, dispatch_identity="wrong"), quality_pass),
        (replace(spec_pass, arm="code-quality-reviewer"), quality_pass),
        (replace(spec_pass, dispatch_evidence_identity="wrong"), quality_pass),
        (replace(spec_pass, terminal="timeout"), quality_pass),
        (replace(spec_pass, terminal="cancelled"), quality_pass),
        (replace(spec_pass, terminal="late"), quality_pass),
        (replace(spec_pass, terminal="replay"), quality_pass),
        (object(), quality_pass),
        ([spec_pass], quality_pass),
    )
    for results in incomplete_or_ambiguous:
        refused = _resolve(packet, results)
        assert refused.action == "wait_refuse"
        assert refused.ledger_mutation_allowed is False
        assert refused.reopen_owners == ()


def _assert_verdict_and_finding_matrix(packet, spec_pass, quality_pass) -> None:
    final = _resolve(packet, (quality_pass, spec_pass))
    assert final.action == "finalize"
    assert final.ledger_mutation_allowed is True
    assert final.reopen_owners == ()
    assert tuple(result.arm for result in final.terminal_results) == (
        "spec-reviewer", "code-quality-reviewer"
    )
    assert _resolve(packet, (spec_pass, quality_pass)) == final

    single = _finding(packet, "finding:1", ("Task 2",), ground_ref="REQ-2")
    spec_block = _result(
        packet, "spec-reviewer", verdict="NEEDS_REVISION", findings=(single,)
    )
    reopened = _resolve(packet, (quality_pass, spec_block))
    assert reopened.action == "reopen"
    assert reopened.reopen_owners == ("Task 2",)
    assert reopened.ledger_mutation_allowed is True
    assert reopened.terminal_results[0].findings[0] is single

    overlap_a = _finding(packet, "finding:a", ("Task 1", "Task 2"))
    overlap_b = _finding(
        packet, "finding:b", ("Task 3", "Task 2"),
        ground="stated_acceptance", ground_ref="accept-3",
    )
    multi = _result(
        packet, "spec-reviewer", verdict="NEEDS_REVISION",
        findings=(overlap_b, overlap_a),
    )
    reopened = _resolve(packet, (multi, quality_pass))
    assert reopened.reopen_owners == ("Task 1", "Task 2", "Task 3")

    unassignable = (
        replace(single, owners=()),
        replace(single, owners=("Task 99",)),
        replace(single, owners=("Task 1", "Task 1")),
        replace(single, ground="future_requirement", ground_ref="FUTURE-2"),
        replace(single, owners=["Task 2"]),
        replace(single, reason=""),
        object(),
    )
    for bad in unassignable:
        bad_result = replace(spec_block, findings=(bad,))
        fallback = _resolve(packet, (quality_pass, bad_result))
        assert fallback.action == "individual_fallback"
        assert fallback.reopen_owners == ()
        assert fallback.ledger_mutation_allowed is False

    mixed = replace(spec_block, findings=(single, replace(single, owners=())))
    fallback = _resolve(packet, (mixed, quality_pass))
    assert fallback.action == "individual_fallback"
    assert fallback.reopen_owners == ()
    assert fallback.ledger_mutation_allowed is False

    wrong_finding_provenance = replace(single, packet_identity="prior-packet")
    fallback = _resolve(
        packet,
        (replace(spec_block, findings=(wrong_finding_provenance,)), quality_pass),
    )
    assert fallback.action == "individual_fallback"


def _assert_immutable_resolution(packet) -> None:
    final = _resolve(
        packet,
        (
            _result(packet, "spec-reviewer"),
            _result(packet, "code-quality-reviewer"),
        ),
    )
    try:
        final.reopen_owners += ("Task 1",)
        raise AssertionError("resolution was mutable")
    except (FrozenInstanceError, AttributeError, TypeError):
        pass
    try:
        final.terminal_results[0].verdict = "NEEDS_REVISION"
        raise AssertionError("terminal provenance was mutable")
    except (FrozenInstanceError, AttributeError, TypeError):
        pass


def test_aggregate_resolution_matrix() -> None:
    packet = _packet()
    spec_pass = _result(packet, "spec-reviewer")
    quality_pass = _result(packet, "code-quality-reviewer")
    _assert_arm_matrix(packet)
    _assert_result_provenance_matrix(packet, spec_pass, quality_pass)
    _assert_verdict_and_finding_matrix(packet, spec_pass, quality_pass)
    _assert_immutable_resolution(packet)


def test_unassignable_finding_provenance_is_not_retained() -> None:
    packet = _packet()
    quality_pass = _result(packet, "code-quality-reviewer")
    finding = _finding(packet, "finding:bad-provenance", ("Task 1",))
    mismatches = (
        replace(finding, packet_identity="prior-packet"),
        replace(finding, arm="code-quality-reviewer"),
        replace(finding, dispatch_identity="prior-dispatch"),
        replace(finding, evidence_identity="prior-evidence"),
    )
    for mismatch in mismatches:
        spec_block = _result(
            packet,
            "spec-reviewer",
            verdict="NEEDS_REVISION",
            findings=(mismatch,),
        )
        fallback = _resolve(packet, (spec_block, quality_pass))
        assert fallback.action == "individual_fallback"
        assert fallback.ledger_mutation_allowed is False
        assert fallback.terminal_results == ()


def test_reviewer_resolution_requires_exact_builtin_strings() -> None:
    class TextSubclass(str):
        pass

    packet = _packet()
    bindings = _bindings(packet)
    results = (
        _result(packet, "spec-reviewer"),
        _result(packet, "code-quality-reviewer"),
    )
    binding_mutations = (
        replace(bindings[0], packet_identity=TextSubclass(packet.identity)),
        replace(bindings[0], arm=TextSubclass("spec-reviewer")),
        replace(
            bindings[0],
            dispatch_identity=TextSubclass("dispatch:spec-reviewer"),
        ),
        replace(
            bindings[0],
            evidence_identity=TextSubclass("dispatch-evidence:spec-reviewer"),
        ),
    )
    for bad_binding in binding_mutations:
        refused = _resolve(
            packet, results, bindings=(bad_binding, bindings[1])
        )
        assert refused.action == "wait_refuse"

    result_mutations = (
        replace(results[0], packet_identity=TextSubclass(packet.identity)),
        replace(results[0], arm=TextSubclass("spec-reviewer")),
        replace(
            results[0],
            dispatch_identity=TextSubclass("dispatch:spec-reviewer"),
        ),
        replace(
            results[0],
            dispatch_evidence_identity=TextSubclass(
                "dispatch-evidence:spec-reviewer"
            ),
        ),
        replace(results[0], result_identity=TextSubclass("result:spec-reviewer:PASS")),
        replace(
            results[0],
            evidence_identity=TextSubclass("result-evidence:spec-reviewer:PASS"),
        ),
        replace(results[0], terminal=TextSubclass("completed")),
        replace(results[0], verdict=TextSubclass("PASS")),
    )
    for bad_result in result_mutations:
        refused = _resolve(packet, (bad_result, results[1]))
        assert refused.action == "wait_refuse"

    refused = _resolve(packet, results, lane=TextSubclass("full"))
    assert refused.action == "wait_refuse"

    finding = _finding(packet, "finding:exact-text", ("Task 1",))
    finding_mutations = (
        replace(finding, packet_identity=TextSubclass(packet.identity)),
        replace(finding, arm=TextSubclass("spec-reviewer")),
        replace(
            finding,
            dispatch_identity=TextSubclass("dispatch:spec-reviewer"),
        ),
        replace(
            finding,
            evidence_identity=TextSubclass(
                "result-evidence:spec-reviewer:NEEDS_REVISION"
            ),
        ),
    )
    for bad_finding in finding_mutations:
        blocked = _result(
            packet,
            "spec-reviewer",
            verdict="NEEDS_REVISION",
            findings=(bad_finding,),
        )
        fallback = _resolve(packet, (blocked, results[1]))
        assert fallback.action == "individual_fallback"
        assert fallback.ledger_mutation_allowed is False
        assert fallback.terminal_results == ()


def test_regression_and_safety_ground_attribution() -> None:
    packet = _packet()
    quality_pass = _result(packet, "code-quality-reviewer")
    for number, ground in enumerate(("direct_regression", "safety_defect"), 1):
        finding = _finding(
            packet,
            f"finding:{ground}",
            (f"Task {number}",),
            ground=ground,
            ground_ref=f"src/{number}.py",
        )
        blocked = _result(
            packet,
            "spec-reviewer",
            verdict="NEEDS_REVISION",
            findings=(finding,),
        )
        reopened = _resolve(packet, (blocked, quality_pass))
        assert reopened.action == "reopen"
        assert reopened.reopen_owners == (f"Task {number}",)

    outside = _finding(
        packet,
        "finding:outside-scope",
        ("Task 1",),
        ground="direct_regression",
        ground_ref="src/outside.py",
    )
    blocked = _result(
        packet,
        "spec-reviewer",
        verdict="NEEDS_REVISION",
        findings=(outside,),
    )
    fallback = _resolve(packet, (blocked, quality_pass))
    assert fallback.action == "individual_fallback"
    assert fallback.ledger_mutation_allowed is False
    assert fallback.reopen_owners == ()
