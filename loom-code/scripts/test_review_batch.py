"""Contract tests for immutable aggregate Review Packets."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import importlib.util
from pathlib import Path
import sys

import pytest


SCRIPT = Path(__file__).with_name("review_batch.py")
SPEC = importlib.util.spec_from_file_location("review_batch", SCRIPT)
assert SPEC and SPEC.loader
review_batch = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = review_batch
SPEC.loader.exec_module(review_batch)


def _member(task_id: str, sha: str, path: str, requirement: str):
    content = f"{task_id} bytes".encode()
    reviewed = (review_batch.ReviewedFile(path=path, content=content),)
    scope = _scope_issuer().issue(
        repository_identity="e" * 64,
        commit_sha=sha,
        tree_identity=sha,
        files=reviewed,
    )
    return review_batch.MemberSnapshot(
        task_id=task_id,
        status=f"implemented({sha})",
        sha=sha,
        declared_files=(path,),
        files=reviewed,
        owned_requirements=(requirement,),
        future_requirements=(),
        acceptance=(f"accept-{task_id}",),
        scope_proof=scope,
    )


def _issuer(*, source_identity="authority:v1", source_digest="a" * 64):
    return review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity=source_identity,
        source_digest=source_digest,
    )


def _scope_issuer(*, source_identity="git:sha1:v1"):
    return review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity=source_identity,
        hash_algorithm="sha1",
    )


def _tamper(receipt, **changes):
    forged = object.__new__(type(receipt))
    for name in receipt.__dataclass_fields__:
        object.__setattr__(forged, name, changes.get(name, getattr(receipt, name)))
    return forged


def _resnapshot(member, *, sha=None, path=None, content=None):
    sha = sha or member.sha
    path = path or member.files[0].path
    content = content if content is not None else member.files[0].content
    reviewed = (review_batch.ReviewedFile(path, content),)
    scope = _scope_issuer().issue(
        repository_identity="e" * 64,
        commit_sha=sha,
        tree_identity=sha,
        files=reviewed,
    )
    return replace(
        member,
        sha=sha,
        status=f"implemented({sha})",
        declared_files=(path,),
        files=reviewed,
        scope_proof=scope,
    )


def _authority_plan(declaration, records) -> str:
    tasks = []
    for index, (task_id, record) in enumerate(
        zip(declaration.members, records, strict=True)
    ):
        number = int(task_id.split()[1])
        path = "src/one.py" if number == 1 else "src/two.py"
        dependency = (
            "none" if index == 0 else f"{declaration.members[index - 1]} completes first"
        )
        tasks.append(
            f"## Task {number} — fixture\n\n"
            "- **Description**: fixture\n"
            f"- **Dependencies**: {dependency}\n"
            f"- **Files touched**: {path}\n"
            f"- **Acceptance**: {record.acceptance[0]}\n"
            f"- **Brief item covered**: {record.owned_requirements[0]}\n"
            f"- **Review-weight**: {declaration.review_lane}\n"
            f"- **Review disposition**: batch({declaration.batch_id})\n"
            "- **Status**: pending\n"
        )
    return (
        "# Plan\n\nGoal: fixture.\nStage: sdd:wave-1\n\n"
        + "\n".join(tasks)
        + "\n## Review Batches\n\n"
        + f"### Review Batch: {declaration.batch_id}\n"
        + f"- **Members**: {', '.join(declaration.members)}\n"
        + f"- **Verdict question**: {declaration.verdict_question}\n"
        + f"- **Review lane**: {declaration.review_lane}\n"
        + f"- **Aggregate verification**: {declaration.aggregate_verification}\n"
        + f"- **Boundary**: {declaration.boundary}\n"
    )


def _ownership(
    records, declaration,
    *,
    plan="plan:task-batch-review",
    source="authority:v1",
    source_digest="a" * 64,
):
    return _issuer(
        source_identity=source, source_digest=source_digest
    ).issue_ownership(
        plan_identity=plan,
        spec_identity="spec:REQ-105",
        records=records,
        execution_projection=_execution_projection(records, declaration, plan=plan),
    )


def _execution_projection(records, declaration, *, plan="plan:task-batch-review"):
    return review_batch._issue_execution_projection_from_validated_plan(
        plan_text=_authority_plan(declaration, records),
        batch_id=declaration.batch_id,
        plan_identity=plan,
        spec_identity="spec:REQ-105",
        records=records,
        issuer="plan-card:validated-schema",
        source_identity="plan:current",
        source_digest="8" * 64,
    )


def _verification(declaration, *, source="resolver:v1", safety="receipt:1", argv=None,
                  scope=None, result="exit=0"):
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(
            declaration.aggregate_verification
        ),
        argv=argv or ("python3", "-m", "pytest", "tests", "-q"),
        execution_scope=scope or ("src/one.py", "src/two.py", "tests"),
        result=result,
        scanner_receipt_identity=safety,
        scanner_input_digest="d" * 64,
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity=source,
        source_digest="c" * 64,
    ).issue(approved)
    return _issuer(source_identity="packet-authority:v1").issue_verification(receipt)


def _inputs():
    sha_1, sha_2 = "1" * 40, "2" * 40
    members = (
        _member("Task 1", sha_1, "src/one.py", "REQ-1"),
        _member("Task 2", sha_2, "src/two.py", "REQ-2"),
    )
    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1", "Task 2"),
        verdict_question="Does the aggregate behavior satisfy its contract?",
        review_lane="full",
        aggregate_verification="python3 -m pytest tests -q",
        boundary="capability: aggregate behavior; exclusions: none; consumable: yes",
    )
    records = tuple(
            review_batch.OwnershipRecord(
                task_id=member.task_id,
                owned_requirements=member.owned_requirements,
                future_requirements=member.future_requirements,
                acceptance=member.acceptance,
            )
            for member in members
    )
    authority = _ownership(records, declaration)
    evidence = _verification(declaration, safety="resolver-safety-receipt:1")
    return declaration, members, authority, evidence


_DEFAULT = object()


def _packet(
    *, declaration=_DEFAULT, members=_DEFAULT, authority=_DEFAULT, evidence=_DEFAULT
):
    defaults = _inputs()
    return review_batch.materialize_packet(
        defaults[0] if declaration is _DEFAULT else declaration,
        defaults[1] if members is _DEFAULT else members,
        defaults[2] if authority is _DEFAULT else authority,
        defaults[3] if evidence is _DEFAULT else evidence,
    )


def _assert_identity_matrix() -> None:
    declaration, members, authority, evidence = _inputs()
    packet = _packet()

    assert review_batch.validate_packet(packet) == ()
    assert packet.member_shas == (("Task 1", "1" * 40), ("Task 2", "2" * 40))
    assert packet.members[0].files[0].content == b"Task 1 bytes"
    assert packet.declaration.aggregate_verification == "python3 -m pytest tests -q"
    assert _packet().identity == packet.identity

    identity_drifts = (
        replace(declaration, verdict_question="Is the shared outcome correct?"),
        replace(declaration, review_lane="prose"),
        replace(declaration, boundary="invariant: aggregate; exclusions: none; consumable: yes"),
        replace(declaration, boundary_proof_identity="boundary:amended-plan"),
    )
    for changed in identity_drifts:
        assert _packet(declaration=changed).identity != packet.identity
    reversed_declaration = replace(declaration, members=("Task 2", "Task 1"))
    reversed_authority = _ownership(
        tuple(reversed(authority.records)), reversed_declaration
    )
    assert review_batch.materialize_packet(
        reversed_declaration,
        tuple(reversed(members)),
        reversed_authority,
        evidence,
    ).identity != packet.identity

    changed_sha = _resnapshot(members[0], sha="3" * 40)
    changed_bytes = _resnapshot(members[0], content=b"changed")
    changed_scope = _resnapshot(members[0], path="src/renamed.py")
    for changed in (changed_sha, changed_bytes):
        assert _packet(members=(changed, members[1])).identity != packet.identity
    with pytest.raises(review_batch.PacketRefused, match="execution authority"):
        _packet(members=(changed_scope, members[1]))

    changed_owner = replace(
        authority.records[0], owned_requirements=("REQ-3",)
    )
    changed_member = replace(members[0], owned_requirements=("REQ-3",))
    assert _packet(
        members=(changed_member, members[1]),
        authority=_ownership((changed_owner, authority.records[1]), declaration),
    ).identity != packet.identity

    aggregate_changed = replace(
        declaration, aggregate_verification="trusted alias: aggregate"
    )
    assert _packet(
        declaration=aggregate_changed,
        evidence=_verification(aggregate_changed),
    ).identity != packet.identity

    evidence_drifts = (
        _verification(declaration, source="resolver:v2"),
        _verification(declaration, argv=(*evidence.resolution.argv, "--strict")),
        _verification(
            declaration, scope=(*evidence.resolution.execution_scope, "docs")
        ),
        _verification(declaration, result="exit=0; tests=18"),
        _verification(declaration, safety="receipt:amended"),
    )
    for changed in evidence_drifts:
        assert _packet(evidence=changed).identity != packet.identity

    for changed_authority in (
        _ownership(authority.records, declaration, source="authority:v2"),
        _ownership(authority.records, declaration, plan="plan:amended"),
        _ownership(authority.records, declaration, source_digest="b" * 64),
    ):
        assert _packet(authority=changed_authority).identity != packet.identity

    scope = members[0].scope_proof
    changed_scope_proof = _scope_issuer(source_identity="git-authority:v2").issue(
        repository_identity=scope.repository_identity,
        commit_sha=scope.commit_sha,
        tree_identity=scope.tree_identity,
        files=members[0].files,
    )
    assert _packet(
        members=(replace(members[0], scope_proof=changed_scope_proof), members[1])
    ).identity != packet.identity


def _assert_readiness_matrix() -> None:
    declaration, members, _, _ = _inputs()
    unready = (
        replace(members[0], status="claimed(@worker)"),
        replace(members[0], status=f"done({members[0].sha})"),
        replace(members[0], status=f"implemented({'9' * 40})"),
    )
    for member in unready:
        with pytest.raises(review_batch.PacketRefused, match="not exactly implemented"):
            _packet(members=(member, members[1]))
    with pytest.raises(review_batch.PacketRefused, match="declaration"):
        _packet(declaration=replace(declaration, boundary_proof_identity=""))


def _assert_scope_matrix() -> None:
    _, members, _, _ = _inputs()
    proof = members[0].scope_proof
    entry = proof.entries[0]
    unsafe_scope = (
        _tamper(proof, entries=(_tamper(entry, path="/src/one.py"),)),
        _tamper(proof, entries=(_tamper(entry, path="../src/one.py"),)),
        _tamper(proof, entries=(_tamper(entry, blob_identity="0" * 40),)),
        _tamper(proof, entries=(_tamper(entry, content_digest="4" * 64),)),
        _tamper(proof, source_digest="4" * 64),
    )
    for bad_proof in unsafe_scope:
        with pytest.raises(review_batch.PacketRefused, match="committed scope"):
            _packet(
                members=(replace(members[0], scope_proof=bad_proof), members[1])
            )
    with pytest.raises(review_batch.PacketRefused, match="member"):
        _packet(members=(replace(members[0], files=()), members[1]))
    with pytest.raises(review_batch.PacketRefused, match="member"):
        _packet(
            members=(
                replace(
                    members[0],
                    declared_files=("src/one.py", "src/missing.py"),
                ),
                members[1],
            )
        )


def _assert_ownership_matrix() -> None:
    _, _, authority, _ = _inputs()
    bad_authorities = (
        None,
        object(),
        _tamper(authority, records=authority.records[:1]),
        _tamper(authority, records=(*authority.records, authority.records[0])),
        _tamper(authority, records=(
            replace(authority.records[0], task_id="Task 99"), authority.records[1],
        )),
        _tamper(authority, records=(
            replace(authority.records[0], owned_requirements=("REQ-2",)), authority.records[1],
        )),
    )
    for bad in bad_authorities:
        with pytest.raises(review_batch.PacketRefused, match="ownership proof"):
            _packet(authority=bad)


def _assert_evidence_matrix() -> None:
    declaration, _, _, evidence = _inputs()
    packet = _packet()
    incomplete_evidence = (
        None,
        object(),
        {"safe": True},
        _verification(replace(declaration, aggregate_verification="different")),
    )
    for bad in incomplete_evidence:
        with pytest.raises(review_batch.PacketRefused, match="verification proof"):
            _packet(evidence=bad)

    secret = "credential-do-not-persist"
    with pytest.raises(review_batch.PacketRefused) as refusal:
        _packet(evidence={"safe": True, "argv": ("tool", "--token", secret)})
    assert secret not in str(refusal.value)
    assert secret not in packet.identity


def _assert_publication_and_mutation_matrix() -> None:
    _, members, _, _ = _inputs()
    packet = _packet()
    partial = {
        "identity": packet.identity,
        "declaration": packet.declaration,
        "members": packet.members,
    }
    assert review_batch.validate_packet(partial) == ("packet is incomplete",)

    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        packet.identity = "replacement"
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        packet.members += (members[0],)
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        packet.members[0].files[0].content = b"replacement"


def test_packet_readiness_and_immutability_matrix() -> None:
    # @req: REQ-105
    _assert_identity_matrix()
    _assert_readiness_matrix()
    _assert_scope_matrix()
    _assert_ownership_matrix()
    _assert_evidence_matrix()
    _assert_publication_and_mutation_matrix()


def test_packet_rejects_forged_or_mutable_authority_inputs() -> None:
    """Authority is a sealed receipt, never a caller-supplied truthy flag."""
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="resolver:v1",
        source_digest="a" * 64,
    )
    reviewed = (review_batch.ReviewedFile("src/one.py", b"Task 1 bytes"),)
    scope = _scope_issuer().issue(
        repository_identity="e" * 64,
        commit_sha="1" * 40,
        tree_identity="2" * 40,
        files=reviewed,
    )
    record = review_batch.OwnershipRecord(
        task_id="Task 1",
        owned_requirements=("REQ-1",),
        future_requirements=(),
        acceptance=("accept-Task 1",),
    )
    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1",),
        verdict_question="Does it satisfy the contract?",
        review_lane="full",
        aggregate_verification="python3 -m pytest tests -q",
        boundary="capability: aggregate; exclusions: none; consumable: yes",
    )
    ownership = issuer.issue_ownership(
        plan_identity="plan:task-batch-review",
        spec_identity="spec:REQ-105",
        records=(record,),
        execution_projection=_execution_projection((record,), declaration),
    )
    with pytest.raises(review_batch.PacketRefused):
        review_batch.ExecutionAuthorityProjection()

    class ProjectionSubclass(review_batch.ExecutionAuthorityProjection):
        pass

    for fake in (None, {"projection": "literal"}, "literal", ProjectionSubclass):
        with pytest.raises(review_batch.PacketRefused):
            issuer.issue_ownership(
                plan_identity="plan:task-batch-review",
                spec_identity="spec:REQ-105",
                records=(record,),
                execution_projection=fake,
            )
    with pytest.raises(TypeError):
        issuer.issue_ownership(
            plan_identity="plan:task-batch-review",
            spec_identity="spec:REQ-105",
            records=(record,),
        )
    projection = ownership.execution_projection
    for plan_identity, spec_identity, records in (
        ("plan:amended", "spec:REQ-105", (record,)),
        ("plan:task-batch-review", "spec:amended", (record,)),
        (
            "plan:task-batch-review",
            "spec:REQ-105",
            (replace(record, owned_requirements=("REQ-2",)),),
        ),
    ):
        with pytest.raises(review_batch.PacketRefused):
            issuer.issue_ownership(
                plan_identity=plan_identity,
                spec_identity=spec_identity,
                records=records,
                execution_projection=projection,
            )
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest("python3 -m pytest tests -q"),
        argv=("python3", "-m", "pytest", "tests", "-q"),
        execution_scope=("src/one.py", "tests"),
        result="exit=0",
        scanner_receipt_identity="resolver-safety-receipt:1",
        scanner_input_digest="b" * 64,
    )
    resolution = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="c" * 64,
    ).issue(approved)
    verification = issuer.issue_verification(resolution)
    member = review_batch.MemberSnapshot(
        task_id="Task 1",
        status=f"implemented({'1' * 40})",
        sha="1" * 40,
        declared_files=("src/one.py",),
        files=reviewed,
        owned_requirements=record.owned_requirements,
        future_requirements=record.future_requirements,
        acceptance=record.acceptance,
        scope_proof=scope,
    )
    packet = review_batch.materialize_packet(
        declaration, (member,), ownership, verification
    )
    assert review_batch.validate_packet(packet) == ()
    assert review_batch.validate_packet(
        replace(packet, ownership=_tamper(ownership, execution_projection=None))
    ) == ("packet authority is invalid",)
    assert review_batch.resolve_aggregate_review(
        packet=replace(packet, ownership=_tamper(ownership, execution_projection=None)),
        declared_lane="full",
        expected_arms=(),
        arm_bindings=(),
        terminal_results=(),
    ).action == "wait_refuse"

    # Old self-attested booleans and arbitrary objects are not API inputs.
    assert "tracked" not in review_batch.ReviewedFile.__dataclass_fields__
    assert "verified" not in review_batch.OwnershipProof.__dataclass_fields__
    secret = "credential-do-not-persist"
    forged = {"safe": True, "argv": ("tool", "--token", secret)}
    for bad in (None, object(), forged):
        with pytest.raises(review_batch.PacketRefused) as refusal:
            review_batch.materialize_packet(declaration, (member,), ownership, bad)
        assert secret not in str(refusal.value)

    for field, value in (
        ("members", ["Task 1"]),
        ("members", ("Task 1", 7)),
        ("boundary_proof_identity", True),
    ):
        with pytest.raises(review_batch.PacketRefused):
            review_batch.materialize_packet(
                replace(declaration, **{field: value}),
                (member,),
                ownership,
                verification,
            )
    for bad_members in ([member], (object(),), None):
        with pytest.raises(review_batch.PacketRefused):
            review_batch.materialize_packet(
                declaration, bad_members, ownership, verification
            )

    for bad_member in (
        replace(member, declared_files=["src/one.py"]),
        replace(member, files=[member.files[0]]),
        replace(member, owned_requirements=["REQ-1"]),
        replace(member, future_requirements=["future-REQ-1"]),
        replace(member, acceptance=["accept-Task 1"]),
    ):
        with pytest.raises(review_batch.PacketRefused):
            review_batch.materialize_packet(
                declaration, (bad_member,), ownership, verification
            )

    for path in ("", "/src/one.py", "../src/one.py", "src/../one.py"):
        with pytest.raises(review_batch.PacketRefused):
            _scope_issuer().issue(
                repository_identity="e" * 64,
                commit_sha="1" * 40,
                tree_identity="2" * 40,
                files=(review_batch.ReviewedFile(path, b"Task 1 bytes"),),
            )

    bad_digest_scope = _tamper(
        scope,
        entries=(_tamper(scope.entries[0], content_digest="b" * 64),),
    )
    with pytest.raises(review_batch.PacketRefused):
        review_batch.materialize_packet(
            declaration,
            (replace(member, scope_proof=bad_digest_scope),),
            ownership,
            verification,
        )

    assert issuer.issue_ownership(
        plan_identity="plan:amended",
        spec_identity="spec:REQ-105",
        records=(record,),
        execution_projection=_execution_projection(
            (record,), declaration, plan="plan:amended"
        ),
    ) != ownership
    assert _verification(declaration, safety="resolver-safety-receipt:2") != verification

    # Exact tuples only: no list can enter a frozen proof or Packet.
    with pytest.raises(review_batch.PacketRefused):
        _scope_issuer().issue(
            repository_identity="e" * 64,
            commit_sha="1" * 40,
            tree_identity="2" * 40,
            files=[reviewed[0]],
        )
    with pytest.raises(review_batch.PacketRefused):
        issuer.issue_verification(["python3"])
    with pytest.raises(review_batch.PacketRefused):
        issuer.issue_ownership(
            plan_identity="plan:task-batch-review",
            spec_identity="spec:REQ-105",
            records=[record],
            execution_projection=ownership.execution_projection,
        )

    malformed = object.__new__(review_batch.VerificationProof)
    with pytest.raises(review_batch.PacketRefused):
        review_batch.materialize_packet(
            declaration, (member,), ownership, malformed
        )

    malformed_entry = object.__new__(review_batch.ScopeEntryProof)
    malformed_scope = _tamper(scope, entries=(malformed_entry,))
    with pytest.raises(review_batch.PacketRefused):
        review_batch.materialize_packet(
            declaration,
            (replace(member, scope_proof=malformed_scope),),
            ownership,
            verification,
        )

    class ForgedVerification(review_batch.VerificationProof):
        pass

    forged_subclass = object.__new__(ForgedVerification)
    with pytest.raises(review_batch.PacketRefused):
        review_batch.materialize_packet(
            declaration, (member,), ownership, forged_subclass
        )


def test_verification_and_scope_issuers_hide_raw_authority_inputs() -> None:
    secret = "credential-must-never-cross-packet-issuer"
    packet_issuer = _issuer()
    with pytest.raises(review_batch.PacketRefused) as refusal:
        packet_issuer.issue_verification(
            {"safe": True, "argv": ("tool", "--token", secret)}
        )
    assert secret not in str(refusal.value)

    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1",),
        verdict_question="Does it satisfy the contract?",
        review_lane="full",
        aggregate_verification="python3 -m pytest tests -q",
        boundary="capability: aggregate; exclusions: none; consumable: yes",
    )
    approved = review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(
            declaration.aggregate_verification
        ),
        argv=("python3", "-m", "pytest", "tests", "-q"),
        execution_scope=("src/one.py", "tests"),
        result="exit=0",
        scanner_receipt_identity="scanner:receipt:1",
        scanner_input_digest="b" * 64,
    )
    resolver = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="c" * 64,
    )
    receipt = resolver.issue(approved)
    verification = packet_issuer.issue_verification(receipt)
    assert verification.resolution is receipt

    for forged in (
        {"safe": True, "argv": ("tool", "--token", secret)},
        object(),
        None,
    ):
        with pytest.raises(review_batch.PacketRefused) as refusal:
            packet_issuer.issue_verification(forged)
        assert secret not in str(refusal.value)

    class ForgedReceipt(review_batch.SafeResolutionReceipt):
        pass

    with pytest.raises(review_batch.PacketRefused):
        packet_issuer.issue_verification(object.__new__(ForgedReceipt))
    with pytest.raises(review_batch.PacketRefused):
        packet_issuer.issue_verification(
            _tamper(receipt, _receipt_seal=object())
        )

    content = b"Task 1 bytes"
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    reviewed = (review_batch.ReviewedFile("src/one.py", content),)
    scope = scope_issuer.issue(
        repository_identity="e" * 64,
        commit_sha="1" * 40,
        tree_identity="2" * 40,
        files=reviewed,
    )
    expected_blob = review_batch.git_blob_identity(content, "sha1")
    assert scope.entries[0].blob_identity == expected_blob
    assert scope.entries[0].content_digest == review_batch.content_digest(content)
    assert scope.source_digest == review_batch.scope_source_digest(scope)

    with pytest.raises(TypeError):
        scope_issuer.issue(
            repository_identity="e" * 64,
            commit_sha="1" * 40,
            tree_identity="2" * 40,
            files=reviewed,
            blob_identity="forged",
        )
    drifted = scope_issuer.issue(
        repository_identity="e" * 64,
        commit_sha="1" * 40,
        tree_identity="3" * 40,
        files=reviewed,
    )
    assert drifted.source_digest != scope.source_digest


def test_execution_projection_accepts_quote_and_bi_referents() -> None:
    """R11a: a validated plan whose members cite brief quotes / BI-<n>
    ids (no REQ- id) must still be able to seal an execution-authority
    projection — plan-format.md's four referent kinds are all legal
    here, non-empty is the only rule."""
    quote = '"the CSV export button appears on Settings"'
    record_quote = review_batch.OwnershipRecord(
        task_id="Task 1", owned_requirements=(quote,),
        future_requirements=(), acceptance=("accept-Task 1",),
    )
    record_bi = review_batch.OwnershipRecord(
        task_id="Task 2", owned_requirements=("BI-7",),
        future_requirements=(), acceptance=("accept-Task 2",),
    )
    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1", "Task 2"),
        verdict_question="Does the aggregate behavior satisfy its contract?",
        review_lane="full",
        aggregate_verification="python3 -m pytest tests -q",
        boundary="capability: aggregate behavior; exclusions: none; consumable: yes",
    )
    projection = _execution_projection((record_quote, record_bi), declaration)
    assert projection.members[0].owned_requirements == (quote,)
    assert projection.members[1].owned_requirements == ("BI-7",)


def test_execution_projection_still_refuses_empty_owned_requirements() -> None:
    """Widening the accepted referent grammar must not widen past
    non-empty: a task whose only referent is the `none — <reason>`
    release-administration value projects zero owned requirements and
    stays refused for batching."""
    record_none = review_batch.OwnershipRecord(
        task_id="Task 1", owned_requirements=(),
        future_requirements=(), acceptance=("accept-Task 1",),
    )
    declaration = review_batch.BatchDeclaration(
        batch_id="batch-a",
        members=("Task 1",),
        verdict_question="Does the aggregate behavior satisfy its contract?",
        review_lane="full",
        aggregate_verification="python3 -m pytest tests -q",
        boundary="capability: aggregate behavior; exclusions: none; consumable: yes",
    )
    with pytest.raises(review_batch.PacketRefused, match="execution authority member is malformed"):
        review_batch._validate_execution_projection(
            review_batch._sealed(
                review_batch.ExecutionAuthorityProjection,
                seal=review_batch._SEAL,
                issuer="plan-card:validated-schema",
                source_identity="plan:current",
                source_digest="8" * 64,
                plan_identity="plan:task-batch-review",
                spec_identity="spec:REQ-105",
                ownership_digest=review_batch._ownership_records_digest((record_none,)),
                declaration=declaration,
                members=(
                    review_batch.ExecutionMemberProjection(
                        task_id="Task 1",
                        dependencies=(),
                        review_disposition="batch(batch-a)",
                        review_lane="full",
                        acceptance=("accept-Task 1",),
                        declared_files=("src/one.py",),
                        brief_references=("none — release administration only",),
                        owned_requirements=(),
                        future_requirements=(),
                    ),
                ),
                _receipt_seal=review_batch._SEAL,
            )
        )
