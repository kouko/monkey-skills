#!/usr/bin/env python3
"""Pure construction and validation of immutable aggregate Review Packets.

This module accepts receipts issued at existing trusted boundaries; it does
not read Git, execute plan text, dispatch reviewers, or mutate Task state.
The private ``_trusted_proof_issuer`` is the narrow integration seam for SDD
and the declared-first resolver. Callers invoke it only after independently
verifying source authority and excluding unsafe raw values. Python is not an
authorization sandbox: sealed types prevent accidental self-attestation,
while the orchestrator owns roles.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Mapping


_SHA = re.compile(r"^[0-9a-f]{40}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_SEAL = object()


class PacketRefused(ValueError):
    """Authority inputs cannot produce one complete safe Packet."""


def content_digest(content: bytes) -> str:
    """Return the canonical digest for exact reviewed bytes."""
    if type(content) is not bytes:
        raise PacketRefused("reviewed content has an invalid type")
    return hashlib.sha256(content).hexdigest()


def text_digest(text: str) -> str:
    """Return the canonical UTF-8 digest for inert declared text."""
    if type(text) is not str:
        raise PacketRefused("declared text has an invalid type")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _exact_text(value: object) -> bool:
    return type(value) is str and bool(value)


def _exact_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _exact_text_tuple(value: object, *, nonempty: bool = True) -> bool:
    return (
        type(value) is tuple
        and (bool(value) or not nonempty)
        and all(_exact_text(item) for item in value)
    )


def _complete_instance(value: object, cls: type) -> bool:
    return type(value) is cls and all(
        hasattr(value, field.name) for field in fields(cls)
    )


def _safe_repo_path(path: object) -> bool:
    if not _exact_text(path) or "\\" in path or "\x00" in path:
        return False
    if any(piece in {"", ".", ".."} for piece in path.split("/")):
        return False
    parsed = PurePosixPath(path)
    return not parsed.is_absolute() and parsed.as_posix() == path


@dataclass(frozen=True)
class ReviewedFile:
    path: str
    content: bytes


@dataclass(frozen=True)
class ScopeEntryProof:
    path: str
    blob_identity: str
    content_digest: str


@dataclass(frozen=True)
class OwnershipRecord:
    task_id: str
    owned_requirements: tuple[str, ...]
    future_requirements: tuple[str, ...]
    acceptance: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionMemberProjection:
    task_id: str
    dependencies: tuple[str, ...]
    review_disposition: str
    review_lane: str
    acceptance: tuple[str, ...]
    declared_files: tuple[str, ...]
    brief_references: tuple[str, ...]
    owned_requirements: tuple[str, ...]
    future_requirements: tuple[str, ...]


@dataclass(frozen=True, init=False)
class ExecutionAuthorityProjection:
    issuer: str
    source_identity: str
    source_digest: str
    plan_identity: str
    spec_identity: str
    ownership_digest: str
    declaration: "BatchDeclaration"
    members: tuple[ExecutionMemberProjection, ...]
    _receipt_seal: object

    def __new__(cls, *args: object, **kwargs: object):
        raise PacketRefused("execution authority projection is issuer-only")


@dataclass(frozen=True, init=False)
class CommittedScopeProof:
    issuer: str
    source_identity: str
    source_digest: str
    hash_algorithm: str
    repository_identity: str
    commit_sha: str
    tree_identity: str
    entries: tuple[ScopeEntryProof, ...]


@dataclass(frozen=True, init=False)
class OwnershipProof:
    issuer: str
    source_identity: str
    source_digest: str
    plan_identity: str
    spec_identity: str
    records: tuple[OwnershipRecord, ...]
    execution_projection: ExecutionAuthorityProjection


@dataclass(frozen=True, init=False)
class VerificationProof:
    issuer: str
    source_identity: str
    source_digest: str
    resolution: SafeResolutionReceipt


@dataclass(frozen=True, init=False)
class ApprovedSafeResolution:
    declaration_digest: str
    argv: tuple[str, ...]
    execution_scope: tuple[str, ...]
    result: str
    scanner_receipt_identity: str
    scanner_input_digest: str
    _receipt_seal: object


@dataclass(frozen=True, init=False)
class SafeResolutionReceipt:
    issuer: str
    source_identity: str
    source_digest: str
    declaration_digest: str
    argv: tuple[str, ...]
    execution_scope: tuple[str, ...]
    result: str
    scanner_receipt_identity: str
    scanner_input_digest: str
    _receipt_seal: object


def _sealed(cls: type, seal: object, **values: object):
    if seal is not _SEAL:
        raise PacketRefused("proof receipt issuer is invalid")
    instance = object.__new__(cls)
    for name, value in values.items():
        object.__setattr__(instance, name, value)
    return instance


def _ownership_records_digest(records: tuple[OwnershipRecord, ...]) -> str:
    payload = [
        [record.task_id, list(record.owned_requirements),
         list(record.future_requirements), list(record.acceptance)]
        for record in records
    ]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()


def _valid_execution_projection_receipt(value: object) -> bool:
    return (
        _complete_instance(value, ExecutionAuthorityProjection)
        and value._receipt_seal is _SEAL
        and _exact_text(value.issuer)
        and _exact_text(value.source_identity)
        and _exact_digest(value.source_digest)
        and _exact_text(value.plan_identity)
        and _exact_text(value.spec_identity)
        and _exact_digest(value.ownership_digest)
    )


@dataclass(frozen=True, init=False)
class ExecutionProjectionIssuer:
    """Trusted seam entered only after the mandatory plan schema checker."""

    issuer: str
    source_identity: str
    source_digest: str

    def issue(
        self, *, plan_identity: str, spec_identity: str,
        records: tuple[OwnershipRecord, ...], projection_fields: object,
    ) -> ExecutionAuthorityProjection:
        """Seal only checker-derived current-plan projection fields."""
        if not (
            _complete_instance(self, ExecutionProjectionIssuer)
            and _exact_text(self.issuer) and _exact_text(self.source_identity)
            and _exact_digest(self.source_digest) and _exact_text(plan_identity)
            and _exact_text(spec_identity) and type(records) is tuple and bool(records)
            and all(type(record) is OwnershipRecord for record in records)
        ):
            raise PacketRefused("execution projection issuance input is invalid")
        try:
            if not (
                type(projection_fields) is dict
                and set(projection_fields) == {"declaration", "members"}
                and type(projection_fields["declaration"]) is dict
                and type(projection_fields["members"]) is tuple
                and all(type(member) is dict for member in projection_fields["members"])
            ):
                raise TypeError
            declaration = BatchDeclaration(**projection_fields["declaration"])
            members = tuple(
                ExecutionMemberProjection(**member)
                for member in projection_fields["members"]
            )
        except (KeyError, TypeError, ValueError):
            raise PacketRefused("execution projection is not checker-derived") from None
        receipt = _sealed(
            ExecutionAuthorityProjection, seal=_SEAL, issuer=self.issuer,
            source_identity=self.source_identity, source_digest=self.source_digest,
            plan_identity=plan_identity, spec_identity=spec_identity,
            ownership_digest=_ownership_records_digest(records),
            declaration=declaration, members=members, _receipt_seal=_SEAL,
        )
        receipt = _validate_execution_projection(receipt)
        if not _projection_matches_ownership_records(receipt, records):
            raise PacketRefused("execution projection conflicts with ownership records")
        return receipt


def _trusted_execution_projection_issuer(
    *, issuer: str, source_identity: str, source_digest: str,
) -> ExecutionProjectionIssuer:
    if not (_exact_text(issuer) and _exact_text(source_identity) and _exact_digest(source_digest)):
        raise PacketRefused("trusted execution projection provenance is invalid")
    return _sealed(
        ExecutionProjectionIssuer, seal=_SEAL, issuer=issuer,
        source_identity=source_identity, source_digest=source_digest,
    )


def _review_batch_oracle():
    """Load the mandatory sibling checker without cwd or sys.path coupling."""
    path = Path(__file__).with_name("check_review_batches.py")
    spec = importlib.util.spec_from_file_location("review_batch_schema_oracle", path)
    if spec is None or spec.loader is None:
        raise PacketRefused("Review Batch schema oracle cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _issue_execution_projection_from_validated_plan(
    *,
    plan_text: str,
    batch_id: str,
    plan_identity: str,
    spec_identity: str,
    records: tuple[OwnershipRecord, ...],
    issuer: str,
    source_identity: str,
    source_digest: str,
) -> ExecutionAuthorityProjection:
    """Trusted plan/schema boundary for the required sealed projection."""
    if not (type(plan_text) is str and _exact_text(batch_id)):
        raise PacketRefused("current plan projection input is invalid")
    try:
        fields = _review_batch_oracle().execution_projection_fields(plan_text, batch_id)
    except (OSError, ValueError):
        raise PacketRefused("current plan cannot issue an execution projection") from None
    return _trusted_execution_projection_issuer(
        issuer=issuer, source_identity=source_identity, source_digest=source_digest,
    ).issue(
        plan_identity=plan_identity,
        spec_identity=spec_identity,
        records=records,
        projection_fields=fields,
    )


@dataclass(frozen=True, init=False)
class ProofIssuer:
    """Sealed role receipt used only at an already-trusted SDD boundary."""

    issuer: str
    source_identity: str
    source_digest: str

    def issue_ownership(
        self,
        *,
        plan_identity: str,
        spec_identity: str,
        records: tuple[OwnershipRecord, ...],
        execution_projection: ExecutionAuthorityProjection,
    ) -> OwnershipProof:
        if not (
            _complete_instance(self, ProofIssuer)
            and _exact_text(self.issuer)
            and _exact_text(self.source_identity)
            and _exact_digest(self.source_digest)
            and _exact_text(plan_identity)
            and _exact_text(spec_identity)
            and type(records) is tuple
            and bool(records)
            and all(type(record) is OwnershipRecord for record in records)
            and _valid_execution_projection_receipt(execution_projection)
            and execution_projection.plan_identity == plan_identity
            and execution_projection.spec_identity == spec_identity
            and execution_projection.ownership_digest == _ownership_records_digest(records)
            and _projection_matches_ownership_records(execution_projection, records)
        ):
            raise PacketRefused("ownership proof input is invalid")
        return _sealed(
            OwnershipProof,
            seal=_SEAL,
            issuer=self.issuer,
            source_identity=self.source_identity,
            source_digest=self.source_digest,
            plan_identity=plan_identity,
            spec_identity=spec_identity,
            records=records,
            execution_projection=execution_projection,
        )

    def issue_verification(self, resolution: object) -> VerificationProof:
        """Bind one exact sealed resolver receipt without reopening its data."""
        if not (
            _complete_instance(self, ProofIssuer)
            and _exact_text(self.issuer)
            and _exact_text(self.source_identity)
            and _exact_digest(self.source_digest)
            and _valid_resolution_receipt(resolution)
        ):
            raise PacketRefused("verification proof input is invalid")
        return _sealed(
            VerificationProof,
            seal=_SEAL,
            issuer=self.issuer,
            source_identity=self.source_identity,
            source_digest=self.source_digest,
            resolution=resolution,
        )


def _trusted_proof_issuer(
    *, issuer: str, source_identity: str, source_digest: str
) -> ProofIssuer:
    """Bind verified provenance at the private trusted-boundary seam."""
    if not (
        _exact_text(issuer)
        and _exact_text(source_identity)
        and _exact_digest(source_digest)
    ):
        raise PacketRefused("trusted proof issuer provenance is invalid")
    return _sealed(
        ProofIssuer,
        seal=_SEAL,
        issuer=issuer,
        source_identity=source_identity,
        source_digest=source_digest,
    )


def _valid_approved_resolution(value: object) -> bool:
    return (
        _complete_instance(value, ApprovedSafeResolution)
        and value._receipt_seal is _SEAL
        and _exact_digest(value.declaration_digest)
        and _exact_text_tuple(value.argv)
        and _exact_text_tuple(value.execution_scope)
        and _exact_text(value.result)
        and _exact_text(value.scanner_receipt_identity)
        and _exact_digest(value.scanner_input_digest)
    )


def _approved_safe_resolution(
    *,
    declaration_digest: str,
    argv: tuple[str, ...],
    execution_scope: tuple[str, ...],
    result: str,
    scanner_receipt_identity: str,
    scanner_input_digest: str,
) -> ApprovedSafeResolution:
    """Trusted resolver seam for values already approved as persistable."""
    candidate = _sealed(
        ApprovedSafeResolution,
        seal=_SEAL,
        declaration_digest=declaration_digest,
        argv=argv,
        execution_scope=execution_scope,
        result=result,
        scanner_receipt_identity=scanner_receipt_identity,
        scanner_input_digest=scanner_input_digest,
        _receipt_seal=_SEAL,
    )
    if not _valid_approved_resolution(candidate):
        raise PacketRefused("approved resolution record is invalid")
    return candidate


def _valid_resolution_receipt(value: object) -> bool:
    return (
        _complete_instance(value, SafeResolutionReceipt)
        and value._receipt_seal is _SEAL
        and _exact_text(value.issuer)
        and _exact_text(value.source_identity)
        and _exact_digest(value.source_digest)
        and _exact_digest(value.declaration_digest)
        and _exact_text_tuple(value.argv)
        and _exact_text_tuple(value.execution_scope)
        and _exact_text(value.result)
        and _exact_text(value.scanner_receipt_identity)
        and _exact_digest(value.scanner_input_digest)
    )


@dataclass(frozen=True, init=False)
class ResolutionIssuer:
    issuer: str
    source_identity: str
    source_digest: str

    def issue(self, approved: object) -> SafeResolutionReceipt:
        if not (
            _complete_instance(self, ResolutionIssuer)
            and _exact_text(self.issuer)
            and _exact_text(self.source_identity)
            and _exact_digest(self.source_digest)
            and _valid_approved_resolution(approved)
        ):
            raise PacketRefused("safe resolution receipt input is invalid")
        return _sealed(
            SafeResolutionReceipt,
            seal=_SEAL,
            issuer=self.issuer,
            source_identity=self.source_identity,
            source_digest=self.source_digest,
            declaration_digest=approved.declaration_digest,
            argv=approved.argv,
            execution_scope=approved.execution_scope,
            result=approved.result,
            scanner_receipt_identity=approved.scanner_receipt_identity,
            scanner_input_digest=approved.scanner_input_digest,
            _receipt_seal=_SEAL,
        )


def _trusted_resolution_issuer(
    *, issuer: str, source_identity: str, source_digest: str
) -> ResolutionIssuer:
    if not (
        _exact_text(issuer)
        and _exact_text(source_identity)
        and _exact_digest(source_digest)
    ):
        raise PacketRefused("trusted resolution issuer provenance is invalid")
    return _sealed(
        ResolutionIssuer,
        seal=_SEAL,
        issuer=issuer,
        source_identity=source_identity,
        source_digest=source_digest,
    )


def git_blob_identity(content: bytes, hash_algorithm: str) -> str:
    """Compute a Git blob object identity for the explicitly bound format."""
    if type(content) is not bytes or hash_algorithm != "sha1":
        raise PacketRefused("Git blob identity input is invalid")
    framed = f"blob {len(content)}\0".encode("ascii") + content
    return hashlib.sha1(framed, usedforsecurity=False).hexdigest()


def _scope_digest_payload(proof: CommittedScopeProof) -> dict[str, object]:
    return {
        "issuer": proof.issuer,
        "source_identity": proof.source_identity,
        "hash_algorithm": proof.hash_algorithm,
        "repository_identity": proof.repository_identity,
        "commit_sha": proof.commit_sha,
        "tree_identity": proof.tree_identity,
        "entries": [
            {
                "path": entry.path,
                "blob_identity": entry.blob_identity,
                "content_digest": entry.content_digest,
            }
            for entry in proof.entries
        ],
    }


def scope_source_digest(proof: CommittedScopeProof) -> str:
    if not (
        _complete_instance(proof, CommittedScopeProof)
        and type(proof.entries) is tuple
        and all(_complete_instance(entry, ScopeEntryProof) for entry in proof.entries)
    ):
        raise PacketRefused("committed scope proof has an invalid type")
    encoded = json.dumps(
        _scope_digest_payload(proof), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, init=False)
class ScopeIssuer:
    issuer: str
    source_identity: str
    hash_algorithm: str

    def issue(
        self,
        *,
        repository_identity: str,
        commit_sha: str,
        tree_identity: str,
        files: tuple[ReviewedFile, ...],
    ) -> CommittedScopeProof:
        if not (
            _complete_instance(self, ScopeIssuer)
            and _exact_text(self.issuer)
            and _exact_text(self.source_identity)
            and self.hash_algorithm == "sha1"
            and _exact_digest(repository_identity)
            and type(commit_sha) is str
            and _SHA.fullmatch(commit_sha) is not None
            and type(tree_identity) is str
            and _SHA.fullmatch(tree_identity) is not None
            and type(files) is tuple
            and bool(files)
            and all(_complete_instance(file, ReviewedFile) for file in files)
            and all(_safe_repo_path(file.path) for file in files)
            and all(type(file.content) is bytes for file in files)
        ):
            raise PacketRefused("committed scope issuance input is invalid")
        entries = tuple(
            ScopeEntryProof(
                path=file.path,
                blob_identity=git_blob_identity(file.content, self.hash_algorithm),
                content_digest=content_digest(file.content),
            )
            for file in files
        )
        provisional = _sealed(
            CommittedScopeProof,
            seal=_SEAL,
            issuer=self.issuer,
            source_identity=self.source_identity,
            source_digest="0" * 64,
            hash_algorithm=self.hash_algorithm,
            repository_identity=repository_identity,
            commit_sha=commit_sha,
            tree_identity=tree_identity,
            entries=entries,
        )
        return _sealed(
            CommittedScopeProof,
            seal=_SEAL,
            issuer=self.issuer,
            source_identity=self.source_identity,
            source_digest=scope_source_digest(provisional),
            hash_algorithm=self.hash_algorithm,
            repository_identity=repository_identity,
            commit_sha=commit_sha,
            tree_identity=tree_identity,
            entries=entries,
        )


def _trusted_scope_issuer(
    *, issuer: str, source_identity: str, hash_algorithm: str
) -> ScopeIssuer:
    if not (
        _exact_text(issuer)
        and _exact_text(source_identity)
        and hash_algorithm == "sha1"
    ):
        raise PacketRefused("trusted scope issuer provenance is invalid")
    return _sealed(
        ScopeIssuer,
        seal=_SEAL,
        issuer=issuer,
        source_identity=source_identity,
        hash_algorithm=hash_algorithm,
    )


@dataclass(frozen=True)
class MemberSnapshot:
    task_id: str
    status: str
    sha: str
    declared_files: tuple[str, ...]
    files: tuple[ReviewedFile, ...]
    owned_requirements: tuple[str, ...]
    future_requirements: tuple[str, ...]
    acceptance: tuple[str, ...]
    scope_proof: CommittedScopeProof


@dataclass(frozen=True)
class BatchDeclaration:
    batch_id: str
    members: tuple[str, ...]
    verdict_question: str
    review_lane: str
    aggregate_verification: str
    boundary: str
    boundary_proof_identity: str = "boundary:validated-plan"


@dataclass(frozen=True)
class ReviewPacket:
    identity: str
    declaration: BatchDeclaration
    members: tuple[MemberSnapshot, ...]
    ownership: OwnershipProof
    evidence: VerificationProof
    member_shas: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ReviewerArmBinding:
    """One expected reviewer arm bound to one exact Packet dispatch."""

    packet_identity: str
    arm: str
    dispatch_identity: str
    evidence_identity: str


@dataclass(frozen=True)
class BlockingFinding:
    """Reviewer-owned finding provenance; the reducer never rewrites it."""

    finding_id: str
    packet_identity: str
    arm: str
    dispatch_identity: str
    evidence_identity: str
    owners: tuple[str, ...]
    blocking: bool
    ground: str
    ground_ref: str
    location: str
    severity: str
    reason: str


@dataclass(frozen=True)
class ReviewerTerminalResult:
    """One terminal result returned by a dispatch-bound reviewer arm."""

    packet_identity: str
    arm: str
    dispatch_identity: str
    dispatch_evidence_identity: str
    result_identity: str
    evidence_identity: str
    terminal: str
    verdict: str
    findings: tuple[BlockingFinding, ...]


@dataclass(frozen=True)
class AggregateReviewResolution:
    """Closed reducer output consumed by the later SDD integration."""

    action: str
    reopen_owners: tuple[str, ...]
    ledger_mutation_allowed: bool
    terminal_results: tuple[ReviewerTerminalResult, ...]
    reasons: tuple[str, ...]
    transition_authority: TransitionAuthority | None


@dataclass(frozen=True, init=False)
class TransitionAuthority:
    """Sealed authority for one exact reducer-owned ledger transition."""

    packet_identity: str
    batch_id: str
    execution_authority_digest: str
    authority_context: tuple[str, ...]
    execution_projection: ExecutionAuthorityProjection
    member_statuses: tuple[tuple[str, str], ...]
    action: str
    reopen_owners: tuple[str, ...]
    outcome_digest: str
    decision_identity: str
    _receipt_seal: object

    def _validate_for_plan_card(
        self,
        *,
        execution_projection_fields: dict[str, object],
        member_statuses: object,
        action: object,
        reopen_owners: object,
    ) -> bool:
        """Keep validation in the exact issuer module across host adapters."""
        try:
            projection = _validate_execution_projection(self.execution_projection)
            declaration = BatchDeclaration(**execution_projection_fields["declaration"])
            members = tuple(
                ExecutionMemberProjection(**member)
                for member in execution_projection_fields["members"]
            )
        except (KeyError, TypeError, ValueError, PacketRefused):
            return False
        if projection.declaration != declaration or projection.members != members:
            return False
        return validate_transition_authority(
            self,
            execution_projection=projection,
            member_statuses=member_statuses,
            action=action,
            reopen_owners=reopen_owners,
        )


_LANE_ARMS = {
    "full": ("spec-reviewer", "code-quality-reviewer"),
    "prose": ("spec-reviewer", "docs-reviewer"),
}


def expected_reviewer_arms(review_lane: object) -> tuple[str, ...]:
    """Resolve the existing non-mechanical review-lane substitutions."""
    if type(review_lane) is not str or review_lane not in _LANE_ARMS:
        return ()
    return _LANE_ARMS[review_lane]


def _arms_apply_to_lane(lane: object, arms: object) -> bool:
    if lane == "full":
        return arms == _LANE_ARMS["full"]
    if lane == "prose":
        # Existing record-class narrowing occupies the code-quality slot with
        # N/A, leaving only the spec arm; authored prose uses docs-reviewer.
        return arms in (_LANE_ARMS["prose"], ("spec-reviewer",))
    return False


def _resolution(
    action: str,
    *,
    packet: ReviewPacket | None = None,
    results: tuple[ReviewerTerminalResult, ...] = (),
    owners: tuple[str, ...] = (),
    reasons: tuple[str, ...] = (),
) -> AggregateReviewResolution:
    authority = None
    if action in {"finalize", "reopen"}:
        if packet is None:
            raise PacketRefused("a mutating resolution requires its exact Packet")
        authority = _issue_transition_authority(
            packet=packet,
            action=action,
            results=results,
            owners=owners,
        )
    return AggregateReviewResolution(
        action=action,
        reopen_owners=owners,
        ledger_mutation_allowed=action in {"finalize", "reopen"},
        terminal_results=results,
        reasons=reasons,
        transition_authority=authority,
    )


def execution_authority_digest(
    projection: ExecutionAuthorityProjection, context: tuple[str, ...]
) -> str:
    encoded = json.dumps(
        {"projection": _canonical(projection), "context": _canonical(context)},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _finding_authority_payload(finding: BlockingFinding) -> dict[str, object]:
    return {
        "finding_id": finding.finding_id,
        "packet_identity": finding.packet_identity,
        "arm": finding.arm,
        "dispatch_identity": finding.dispatch_identity,
        "evidence_identity": finding.evidence_identity,
        "owners": finding.owners,
        "blocking": finding.blocking,
        "ground": finding.ground,
        "ground_ref": finding.ground_ref,
        "location": finding.location,
        "severity": finding.severity,
        "reason": finding.reason,
    }


def _outcome_digest(results: tuple[ReviewerTerminalResult, ...]) -> str:
    payload = [
        {
            "packet_identity": result.packet_identity,
            "arm": result.arm,
            "dispatch_identity": result.dispatch_identity,
            "dispatch_evidence_identity": result.dispatch_evidence_identity,
            "result_identity": result.result_identity,
            "evidence_identity": result.evidence_identity,
            "terminal": result.terminal,
            "verdict": result.verdict,
            "findings": [
                _finding_authority_payload(finding) for finding in result.findings
            ],
        }
        for result in results
    ]
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _authority_identity(fields: dict[str, object]) -> str:
    encoded = json.dumps(
        {key: _canonical(value) for key, value in fields.items()},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _issue_transition_authority(
    *,
    packet: ReviewPacket,
    action: str,
    results: tuple[ReviewerTerminalResult, ...],
    owners: tuple[str, ...],
) -> TransitionAuthority:
    if action not in {"finalize", "reopen"} or not results:
        raise PacketRefused("transition authority input is incomplete")
    members = tuple((member.task_id, member.status) for member in packet.members)
    projection = packet.ownership.execution_projection
    if projection is None:
        raise PacketRefused("mutating review requires Packet-bound execution authority")
    context = (
        projection.issuer,
        projection.source_identity,
        projection.source_digest,
        packet.ownership.plan_identity,
        packet.ownership.spec_identity,
        packet.ownership.execution_projection.ownership_digest,
    )
    fields: dict[str, object] = {
        "packet_identity": packet.identity,
        "batch_id": packet.declaration.batch_id,
        "execution_authority_digest": execution_authority_digest(projection, context),
        "authority_context": context,
        "execution_projection": projection,
        "member_statuses": members,
        "action": action,
        "reopen_owners": owners,
        "outcome_digest": _outcome_digest(results),
    }
    return _sealed(
        TransitionAuthority,
        seal=_SEAL,
        **fields,
        decision_identity=_authority_identity(fields),
        _receipt_seal=_SEAL,
    )


def validate_transition_authority(
    authority: object,
    *,
    execution_projection: object,
    member_statuses: object,
    action: object,
    reopen_owners: object,
) -> bool:
    """Validate one sealed reducer decision against a current plan snapshot."""
    if not (
        _complete_instance(authority, TransitionAuthority)
        and authority._receipt_seal is _SEAL
        and _exact_text(authority.packet_identity)
        and _exact_text(authority.batch_id)
        and _exact_digest(authority.execution_authority_digest)
        and type(authority.authority_context) is tuple
        and len(authority.authority_context) == 6
        and all(_exact_text(value) for value in (
            authority.authority_context[0], authority.authority_context[1],
            authority.authority_context[3], authority.authority_context[4]))
        and _exact_digest(authority.authority_context[2])
        and _exact_digest(authority.authority_context[5])
        and _valid_execution_projection_receipt(authority.execution_projection)
        and type(authority.member_statuses) is tuple
        and bool(authority.member_statuses)
        and all(
            type(item) is tuple
            and len(item) == 2
            and _exact_text(item[0])
            and _exact_text(item[1])
            for item in authority.member_statuses
        )
        and authority.action in {"finalize", "reopen"}
        and type(authority.reopen_owners) is tuple
        and all(_exact_text(owner) for owner in authority.reopen_owners)
        and _exact_digest(authority.outcome_digest)
        and _exact_digest(authority.decision_identity)
    ):
        return False
    try:
        current = _validate_execution_projection(execution_projection)
    except PacketRefused:
        return False
    fields = {
        "packet_identity": authority.packet_identity,
        "batch_id": authority.batch_id,
        "execution_authority_digest": authority.execution_authority_digest,
        "authority_context": authority.authority_context,
        "execution_projection": authority.execution_projection,
        "member_statuses": authority.member_statuses,
        "action": authority.action,
        "reopen_owners": authority.reopen_owners,
        "outcome_digest": authority.outcome_digest,
    }
    return (
        authority.decision_identity == _authority_identity(fields)
        and authority.batch_id == current.declaration.batch_id
        and authority.execution_projection == current
        and authority.execution_authority_digest
        == execution_authority_digest(current, authority.authority_context)
        and member_statuses == authority.member_statuses
        and action == authority.action
        and reopen_owners == authority.reopen_owners
    )


def _valid_binding(
    binding: object, packet_identity: str, arm: str
) -> bool:
    return (
        _complete_instance(binding, ReviewerArmBinding)
        and _exact_text(binding.packet_identity)
        and binding.packet_identity == packet_identity
        and _exact_text(binding.arm)
        and binding.arm == arm
        and _exact_text(binding.dispatch_identity)
        and _exact_text(binding.evidence_identity)
    )


def _result_matches_binding(
    result: object, binding: ReviewerArmBinding
) -> bool:
    return (
        _complete_instance(result, ReviewerTerminalResult)
        and _exact_text(result.packet_identity)
        and result.packet_identity == binding.packet_identity
        and _exact_text(result.arm)
        and result.arm == binding.arm
        and _exact_text(result.dispatch_identity)
        and result.dispatch_identity == binding.dispatch_identity
        and _exact_text(result.dispatch_evidence_identity)
        and result.dispatch_evidence_identity == binding.evidence_identity
        and _exact_text(result.result_identity)
        and _exact_text(result.evidence_identity)
        and _exact_text(result.terminal)
        and result.terminal == "completed"
        and _exact_text(result.verdict)
        and result.verdict in {"PASS", "PASS_WITH_NOTES", "NEEDS_REVISION"}
        and type(result.findings) is tuple
    )


def _finding_attributable(
    finding: object,
    *,
    packet: ReviewPacket,
    result: ReviewerTerminalResult,
) -> bool:
    if not (
        _complete_instance(finding, BlockingFinding)
        and _exact_text(finding.finding_id)
        and _exact_text(finding.packet_identity)
        and finding.packet_identity == packet.identity
        and _exact_text(finding.arm)
        and finding.arm == result.arm
        and _exact_text(finding.dispatch_identity)
        and finding.dispatch_identity == result.dispatch_identity
        and _exact_text(finding.evidence_identity)
        and finding.evidence_identity == result.evidence_identity
        and type(finding.owners) is tuple
        and bool(finding.owners)
        and all(_exact_text(owner) for owner in finding.owners)
        and len(set(finding.owners)) == len(finding.owners)
        and type(finding.blocking) is bool
        and _exact_text(finding.ground)
        and _exact_text(finding.ground_ref)
        and _exact_text(finding.location)
        and _exact_text(finding.severity)
        and _exact_text(finding.reason)
    ):
        return False
    members = {member.task_id: member for member in packet.members}
    if any(owner not in members for owner in finding.owners):
        return False
    owner_members = tuple(members[owner] for owner in finding.owners)
    if finding.ground == "owned_requirement":
        return any(
            finding.ground_ref in member.owned_requirements
            for member in owner_members
        )
    if finding.ground == "stated_acceptance":
        return any(
            finding.ground_ref in member.acceptance for member in owner_members
        )
    if finding.ground in {"direct_regression", "safety_defect"}:
        return any(
            finding.ground_ref in member.declared_files
            for member in owner_members
        )
    return False


def resolve_aggregate_review(
    *,
    packet: object,
    declared_lane: object,
    expected_arms: object,
    arm_bindings: object,
    terminal_results: object,
) -> AggregateReviewResolution:
    """Reduce exact Packet-bound terminal results without side effects."""
    if validate_packet(packet) != ():
        return _resolution("wait_refuse", reasons=("invalid_packet",))
    if not (
        _exact_text(declared_lane)
        and declared_lane == packet.declaration.review_lane
        and type(expected_arms) is tuple
        and bool(expected_arms)
        and all(_exact_text(arm) for arm in expected_arms)
        and len(set(expected_arms)) == len(expected_arms)
        and _arms_apply_to_lane(declared_lane, expected_arms)
        and type(arm_bindings) is tuple
        and len(arm_bindings) == len(expected_arms)
    ):
        return _resolution("wait_refuse", reasons=("invalid_expected_arms",))

    bindings: dict[str, ReviewerArmBinding] = {}
    for arm, binding in zip(expected_arms, arm_bindings, strict=True):
        if not _valid_binding(binding, packet.identity, arm):
            return _resolution("wait_refuse", reasons=("invalid_arm_binding",))
        bindings[arm] = binding
    if (
        len({binding.dispatch_identity for binding in bindings.values()})
        != len(bindings)
        or len({binding.evidence_identity for binding in bindings.values()})
        != len(bindings)
    ):
        return _resolution("wait_refuse", reasons=("ambiguous_arm_binding",))
    if type(terminal_results) is not tuple:
        return _resolution("wait_refuse", reasons=("invalid_results",))

    by_arm: dict[str, list[object]] = {arm: [] for arm in expected_arms}
    for result in terminal_results:
        if not _complete_instance(result, ReviewerTerminalResult):
            return _resolution("wait_refuse", reasons=("invalid_result",))
        if result.arm not in by_arm:
            return _resolution("wait_refuse", reasons=("unexpected_result_arm",))
        by_arm[result.arm].append(result)
    if any(len(results) != 1 for results in by_arm.values()):
        return _resolution("wait_refuse", reasons=("non_authoritative_results",))

    ordered = tuple(by_arm[arm][0] for arm in expected_arms)
    if not all(
        _result_matches_binding(result, bindings[result.arm])
        for result in ordered
    ):
        return _resolution("wait_refuse", reasons=("invalid_result_provenance",))
    if (
        len({result.result_identity for result in ordered}) != len(ordered)
        or len({result.evidence_identity for result in ordered}) != len(ordered)
    ):
        return _resolution("wait_refuse", reasons=("ambiguous_result_identity",))

    finding_ids: set[str] = set()
    blocking: list[BlockingFinding] = []
    unassignable = False
    unsafe_provenance = False
    for result in ordered:
        for finding in result.findings:
            if not _complete_instance(finding, BlockingFinding):
                unassignable = True
                unsafe_provenance = True
                continue
            if type(finding.owners) is not tuple:
                unsafe_provenance = True
            if finding.finding_id in finding_ids:
                unassignable = True
            finding_ids.add(finding.finding_id)
            if not _finding_attributable(finding, packet=packet, result=result):
                unassignable = True
                unsafe_provenance = True
            elif finding.blocking:
                blocking.append(finding)
        if result.verdict == "NEEDS_REVISION" and not any(
            _complete_instance(finding, BlockingFinding) and finding.blocking
            for finding in result.findings
        ):
            unassignable = True
        if result.verdict != "NEEDS_REVISION" and any(
            _complete_instance(finding, BlockingFinding) and finding.blocking
            for finding in result.findings
        ):
            unassignable = True

    if unassignable:
        return _resolution(
            "individual_fallback",
            results=() if unsafe_provenance else ordered,
            reasons=("unassignable_finding",),
        )
    if blocking:
        owner_set = {owner for finding in blocking for owner in finding.owners}
        owners = tuple(
            member.task_id for member in packet.members
            if member.task_id in owner_set
        )
        return _resolution(
            "reopen", packet=packet, results=ordered, owners=owners
        )
    if all(result.verdict in {"PASS", "PASS_WITH_NOTES"} for result in ordered):
        return _resolution("finalize", packet=packet, results=ordered)
    return _resolution("wait_refuse", results=ordered, reasons=("invalid_verdict_set",))


_CANONICAL_TYPES = (
    ReviewedFile,
    ScopeEntryProof,
    OwnershipRecord,
    ExecutionMemberProjection,
    ExecutionAuthorityProjection,
    CommittedScopeProof,
    OwnershipProof,
    ApprovedSafeResolution,
    SafeResolutionReceipt,
    VerificationProof,
    MemberSnapshot,
    BatchDeclaration,
)


def _canonical(value: object) -> object:
    if type(value) is bytes:
        return {"bytes_sha256": content_digest(value), "length": len(value)}
    if type(value) in _CANONICAL_TYPES:
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in fields(value)
            if field.name != "_receipt_seal"
        }
    if type(value) is tuple:
        return [_canonical(item) for item in value]
    if type(value) in (str, bool, int) or value is None:
        return value
    raise PacketRefused("Packet authority contains an unsupported value")


def _validate_declaration(declaration: object) -> BatchDeclaration:
    if not _complete_instance(declaration, BatchDeclaration):
        raise PacketRefused("Batch declaration has an invalid type")
    if not (
        _exact_text(declaration.batch_id)
        and _exact_text_tuple(declaration.members)
        and len(set(declaration.members)) == len(declaration.members)
        and _exact_text(declaration.verdict_question)
        and _exact_text(declaration.review_lane)
        and _exact_text(declaration.aggregate_verification)
        and _exact_text(declaration.boundary)
        and _exact_text(declaration.boundary_proof_identity)
    ):
        raise PacketRefused("Batch declaration is incomplete or malformed")
    return declaration


def _validate_execution_projection(projection: object) -> ExecutionAuthorityProjection:
    if not _valid_execution_projection_receipt(projection):
        raise PacketRefused("execution authority projection has an invalid type")
    declaration = _validate_declaration(projection.declaration)
    if not (
        type(projection.members) is tuple
        and tuple(member.task_id for member in projection.members) == declaration.members
    ):
        raise PacketRefused("execution authority members do not match Batch")
    for member in projection.members:
        if not (
            _complete_instance(member, ExecutionMemberProjection)
            and _exact_text(member.task_id)
            and _exact_text_tuple(member.dependencies, nonempty=False)
            and _exact_text(member.review_disposition)
            and member.review_disposition == f"batch({declaration.batch_id})"
            and member.review_lane == declaration.review_lane
            and _exact_text_tuple(member.acceptance)
            and _exact_text_tuple(member.declared_files)
            and _exact_text_tuple(member.brief_references)
            and _exact_text_tuple(member.owned_requirements)
            and _exact_text_tuple(member.future_requirements, nonempty=False)
            and len(set(member.owned_requirements)) == len(member.owned_requirements)
            and len(set(member.future_requirements)) == len(member.future_requirements)
            and not set(member.owned_requirements) & set(member.future_requirements)
            and all(
                _exact_text(reference) and reference.startswith("REQ-")
                for reference in member.owned_requirements
            )
        ):
            raise PacketRefused("execution authority member is malformed")
    return projection


def _projection_matches_ownership_records(
    projection: ExecutionAuthorityProjection,
    records: tuple[OwnershipRecord, ...],
) -> bool:
    """Require the plan-derived receipt and trusted ownership boundary agree."""
    if len(records) != len(projection.members):
        return False
    for member, record in zip(projection.members, records, strict=True):
        if not (
            record.task_id == member.task_id
            and record.acceptance == member.acceptance
            and record.owned_requirements == member.owned_requirements
            and record.future_requirements == member.future_requirements
        ):
            return False
    return True


def _validate_scope(member: MemberSnapshot) -> None:
    proof = member.scope_proof
    if not _complete_instance(proof, CommittedScopeProof):
        raise PacketRefused("committed scope proof has an invalid type")
    if not (
        _exact_text(proof.issuer)
        and _exact_text(proof.source_identity)
        and _exact_digest(proof.source_digest)
        and proof.source_digest == scope_source_digest(proof)
        and proof.hash_algorithm == "sha1"
        and _exact_digest(proof.repository_identity)
        and proof.commit_sha == member.sha
        and type(proof.commit_sha) is str
        and _SHA.fullmatch(proof.commit_sha) is not None
        and type(proof.tree_identity) is str
        and _SHA.fullmatch(proof.tree_identity) is not None
        and type(proof.entries) is tuple
        and bool(proof.entries)
        and all(_complete_instance(entry, ScopeEntryProof) for entry in proof.entries)
        and len(proof.entries) == len(member.files)
    ):
        raise PacketRefused("committed scope proof is incomplete or mismatched")
    proof_paths: list[str] = []
    for reviewed, entry in zip(member.files, proof.entries, strict=True):
        if not (
            _complete_instance(reviewed, ReviewedFile)
            and _safe_repo_path(reviewed.path)
            and type(reviewed.content) is bytes
            and _safe_repo_path(entry.path)
            and reviewed.path == entry.path
            and entry.blob_identity
            == git_blob_identity(reviewed.content, proof.hash_algorithm)
            and _exact_digest(entry.content_digest)
            and content_digest(reviewed.content) == entry.content_digest
        ):
            raise PacketRefused("committed scope proof does not match reviewed bytes")
        proof_paths.append(entry.path)
    if tuple(proof_paths) != member.declared_files:
        raise PacketRefused("declared scope does not exactly match committed proof")


def _validate_members(
    declaration: BatchDeclaration, members: object
) -> tuple[MemberSnapshot, ...]:
    if type(members) is not tuple or not members:
        raise PacketRefused("Packet members must be one immutable ordered tuple")
    if not all(_complete_instance(member, MemberSnapshot) for member in members):
        raise PacketRefused("Packet member has an invalid type")
    if tuple(member.task_id for member in members) != declaration.members:
        raise PacketRefused("Packet members do not exactly match the Batch declaration")
    for member in members:
        if not (
            _exact_text(member.task_id)
            and type(member.sha) is str
            and _SHA.fullmatch(member.sha) is not None
            and type(member.status) is str
            and member.status == f"implemented({member.sha})"
            and _exact_text_tuple(member.declared_files)
            and len(set(member.declared_files)) == len(member.declared_files)
            and type(member.files) is tuple
            and len(member.files) == len(member.declared_files)
            and _exact_text_tuple(member.owned_requirements)
            and _exact_text_tuple(member.future_requirements, nonempty=False)
            and _exact_text_tuple(member.acceptance)
        ):
            raise PacketRefused("Packet member is malformed or not exactly implemented")
        _validate_scope(member)
    return members


def _validate_ownership(
    members: tuple[MemberSnapshot, ...], proof: object
) -> OwnershipProof:
    if not _complete_instance(proof, OwnershipProof):
        raise PacketRefused("ownership proof has an invalid type")
    if not (
        _exact_text(proof.issuer)
        and _exact_text(proof.source_identity)
        and _exact_digest(proof.source_digest)
        and _exact_text(proof.plan_identity)
        and _exact_text(proof.spec_identity)
        and type(proof.records) is tuple
        and len(proof.records) == len(members)
        and all(_complete_instance(record, OwnershipRecord) for record in proof.records)
        and _valid_execution_projection_receipt(proof.execution_projection)
    ):
        raise PacketRefused("ownership proof is incomplete")
    requirements: list[str] = []
    for member, record in zip(members, proof.records, strict=True):
        expected = (
            member.task_id,
            member.owned_requirements,
            member.future_requirements,
            member.acceptance,
        )
        actual = (
            record.task_id,
            record.owned_requirements,
            record.future_requirements,
            record.acceptance,
        )
        if actual != expected or not (
            _exact_text(record.task_id)
            and _exact_text_tuple(record.owned_requirements)
            and _exact_text_tuple(record.future_requirements, nonempty=False)
            and _exact_text_tuple(record.acceptance)
        ):
            raise PacketRefused("ownership proof conflicts with member authority")
        requirements.extend(record.owned_requirements)
        requirements.extend(record.future_requirements)
    if len(set(requirements)) != len(requirements):
        raise PacketRefused("ownership proof contains duplicate requirement authority")
    projection = _validate_execution_projection(proof.execution_projection)
    if (
        projection.plan_identity != proof.plan_identity
        or projection.spec_identity != proof.spec_identity
        or projection.ownership_digest != _ownership_records_digest(proof.records)
        or not _projection_matches_ownership_records(projection, proof.records)
    ):
        raise PacketRefused("execution authority context conflicts with ownership")
    for member, projected in zip(members, projection.members, strict=True):
        if (
            projected.task_id != member.task_id
            or projected.acceptance != member.acceptance
            or projected.declared_files != member.declared_files
            or projected.owned_requirements != member.owned_requirements
            or projected.future_requirements != member.future_requirements
        ):
            raise PacketRefused("execution authority conflicts with member authority")
    return proof


def _validate_verification(
    declaration: BatchDeclaration, proof: object
) -> VerificationProof:
    # Exact-type rejection occurs before reading attacker-controlled fields.
    if not _complete_instance(proof, VerificationProof):
        raise PacketRefused("verification proof has an invalid type")
    if not (
        _exact_text(proof.issuer)
        and _exact_text(proof.source_identity)
        and _exact_digest(proof.source_digest)
        and _valid_resolution_receipt(proof.resolution)
        and proof.resolution.declaration_digest
        == text_digest(declaration.aggregate_verification)
    ):
        raise PacketRefused("verification proof is incomplete or mismatched")
    return proof


def _identity(
    declaration: BatchDeclaration,
    members: tuple[MemberSnapshot, ...],
    ownership: OwnershipProof,
    evidence: VerificationProof,
) -> str:
    encoded = json.dumps(
        {
            "schema": "review-packet-v2",
            "declaration": _canonical(declaration),
            "members": _canonical(members),
            "ownership": _canonical(ownership),
            "evidence": _canonical(evidence),
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def materialize_packet(
    declaration: BatchDeclaration,
    members: tuple[MemberSnapshot, ...],
    ownership: OwnershipProof,
    evidence: VerificationProof,
) -> ReviewPacket:
    """Return one complete immutable Packet, or refuse without publication."""
    declaration = _validate_declaration(declaration)
    members = _validate_members(declaration, members)
    ownership = _validate_ownership(members, ownership)
    evidence = _validate_verification(declaration, evidence)
    return ReviewPacket(
        identity=_identity(declaration, members, ownership, evidence),
        declaration=declaration,
        members=members,
        ownership=ownership,
        evidence=evidence,
        member_shas=tuple((member.task_id, member.sha) for member in members),
    )


def validate_packet(packet: object) -> tuple[str, ...]:
    """Validate a complete frozen Packet; partial mappings are unusable."""
    if isinstance(packet, Mapping):
        if set(packet) != {field.name for field in fields(ReviewPacket)}:
            return ("packet is incomplete",)
        return ("packet must be a frozen ReviewPacket",)
    if not _complete_instance(packet, ReviewPacket):
        return ("packet must be a frozen ReviewPacket",)
    try:
        declaration = _validate_declaration(packet.declaration)
        members = _validate_members(declaration, packet.members)
        ownership = _validate_ownership(members, packet.ownership)
        evidence = _validate_verification(declaration, packet.evidence)
        shas = tuple((member.task_id, member.sha) for member in members)
        identity = _identity(declaration, members, ownership, evidence)
    except PacketRefused:
        return ("packet authority is invalid",)
    if packet.member_shas != shas or packet.identity != identity:
        return ("packet identity does not match its authority inputs",)
    return ()
