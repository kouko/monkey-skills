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
import json
from pathlib import PurePosixPath
import re
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


_CANONICAL_TYPES = (
    ReviewedFile,
    ScopeEntryProof,
    OwnershipRecord,
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
