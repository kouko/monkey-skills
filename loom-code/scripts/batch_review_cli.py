#!/usr/bin/env python3
"""Batch review adapter CLI — the executable SDD batch checkpoint path (R7).

One assembly-free orchestration entrypoint over ``review_batch.py``'s sealed
functions.  Subcommands:

- ``ready``            — batch readiness check (checker-valid plan, every
                        member exactly ``implemented(<sha>)``).
- ``packet``           — build the sealed immutable ``ReviewPacket``.
- ``record-dispatch``  — write the reviewer dispatch receipt file.
- ``apply-result``     — feed the terminal verdicts through
                        ``resolve_aggregate_review`` unchanged.

Usage:
    python3 batch_review_cli.py ready --plan <plan-path> [--batch <id>]
    python3 batch_review_cli.py packet --plan <plan-path> --repo-root <root> \
        --verification-receipt <json> [--batch <id>]
    python3 batch_review_cli.py record-dispatch --packet-file <json> --out <json>
    python3 batch_review_cli.py apply-result --plan <plan-path> \
        --repo-root <root> --verification-receipt <json> --result-file <json> \
        [--batch <id>]

The plan's ``Aggregate verification`` prose is declaration identity only and
is never executed; the verification receipt file is the declared-first
resolver's trusted output.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys


def _load(name: str, filename: str):
    """Load a sibling script module without cwd or sys.path coupling."""
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rb = _load("review_batch_for_batch_review_cli", "review_batch.py")


PLAN_IDENTITY = "plan:batch-review-cli"
SPEC_IDENTITY = "spec:batch-review-cli"
REPOSITORY_IDENTITY = "e" * 64

_TASK_HEADING = re.compile(r"^## Task (\d+)\b.*$", re.MULTILINE)
_H2_HEADING = re.compile(r"^##\s+", re.MULTILINE)
_STATUS_FIELD = re.compile(r"^\s*-\s*\*\*Status\*\*:\s*(.+?)\s*$", re.MULTILINE)
_IMPLEMENTED = re.compile(r"^implemented\(([0-9a-f]{40})\)$")


def _fail(payload: dict) -> int:
    print(json.dumps(payload, sort_keys=True))
    return 1


def _load_plan(plan_path: Path) -> str:
    return Path(plan_path).read_text(encoding="utf-8")


def _batch_id(args, fields: dict) -> str:
    if getattr(args, "batch", None):
        return args.batch
    return fields["declaration"]["batch_id"]


def _projection_fields(plan_text: str, batch_id: str | None) -> dict:
    """Return checker-validated projection fields, refusing invalid plans."""
    oracle = rb._review_batch_oracle()
    errors = oracle.validate_plan(plan_text)
    if errors:
        raise ValueError("; ".join(errors))
    if batch_id is None:
        batches = oracle._BATCH_HEADING.findall(plan_text)
        if not batches:
            raise ValueError("plan declares no Review Batch")
        batch_id = batches[0].strip()
    return oracle.execution_projection_fields(plan_text, batch_id)


def _member_statuses(plan_text: str, member_ids: tuple[str, ...]) -> dict[str, str]:
    """Return each member's Status line keyed by task id."""
    blocks: dict[int, str] = {}
    matches = list(_TASK_HEADING.finditer(plan_text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(plan_text)
        blocks[int(match.group(1))] = plan_text[match.end():end]
    statuses = {}
    for member_id in member_ids:
        number = int(member_id.split()[1])
        values = _STATUS_FIELD.findall(blocks.get(number, ""))
        statuses[member_id] = values[0] if len(values) == 1 else ""
    return statuses


def _readiness(plan_text: str, fields: dict) -> tuple[bool, list[dict], list[str]]:
    member_ids = fields["declaration"]["members"]
    statuses = _member_statuses(plan_text, tuple(member_ids))
    members = [
        {"task_id": member_id, "status": statuses[member_id]}
        for member_id in member_ids
    ]
    reasons = []
    for member in members:
        if _IMPLEMENTED.fullmatch(member["status"]) is None:
            reasons.append(
                f"{member['task_id']} is not exactly implemented(<sha>)"
            )
    # Multi-batch membership is already refused by the schema oracle; there is
    # no member participating in another non-terminal batch on a valid plan.
    return not reasons, members, reasons


def _read_receipt(receipt_path: str) -> dict:
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    if not (
        set(receipt) == {
            "argv", "execution_scope", "result",
            "scanner_receipt_identity", "scanner_input_digest",
        }
        and type(receipt["argv"]) is list
        and type(receipt["execution_scope"]) is list
    ):
        raise ValueError("verification receipt is malformed")
    return receipt


def build_packet(
    *,
    plan_text: str,
    fields: dict,
    receipt: dict,
    repo_root: Path,
) -> rb.ReviewPacket:
    """Materialize the sealed packet via review_batch's own trusted chain."""
    declaration = rb.BatchDeclaration(**fields["declaration"])
    root = Path(repo_root)
    scope_issuer = rb._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    members = []
    for projected in fields["members"]:
        match = _IMPLEMENTED.fullmatch(
            _member_statuses(plan_text, (projected["task_id"],))[projected["task_id"]]
        )
        if match is None:
            raise rb.PacketRefused(
                f"{projected['task_id']} is not exactly implemented(<sha>)"
            )
        sha = match.group(1)
        files = tuple(
            rb.ReviewedFile(path, (root / path).read_bytes())
            for path in projected["declared_files"]
        )
        members.append(rb.MemberSnapshot(
            task_id=projected["task_id"],
            status=f"implemented({sha})",
            sha=sha,
            declared_files=projected["declared_files"],
            files=files,
            owned_requirements=projected["owned_requirements"],
            future_requirements=projected["future_requirements"],
            acceptance=projected["acceptance"],
            scope_proof=scope_issuer.issue(
                repository_identity=REPOSITORY_IDENTITY,
                commit_sha=sha,
                tree_identity=sha,
                files=files,
            ),
        ))
    members = tuple(members)
    records = tuple(
        rb.OwnershipRecord(
            member.task_id, member.owned_requirements,
            member.future_requirements, member.acceptance,
        )
        for member in members
    )
    issuer = rb._trusted_proof_issuer(
        issuer="sdd:declared-first",
        source_identity="authority:v1",
        source_digest=rb.text_digest(plan_text),
    )
    ownership = issuer.issue_ownership(
        plan_identity=PLAN_IDENTITY,
        spec_identity=SPEC_IDENTITY,
        records=records,
        execution_projection=rb._issue_execution_projection_from_validated_plan(
            plan_text=plan_text,
            batch_id=declaration.batch_id,
            plan_identity=PLAN_IDENTITY,
            spec_identity=SPEC_IDENTITY,
            records=records,
            issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest=rb.text_digest(plan_text),
        ),
    )
    receipt_sealed = rb._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest="f" * 64,
    ).issue(rb._approved_safe_resolution(
        declaration_digest=rb.text_digest(declaration.aggregate_verification),
        argv=tuple(receipt["argv"]),
        execution_scope=tuple(receipt["execution_scope"]),
        result=receipt["result"],
        scanner_receipt_identity=receipt["scanner_receipt_identity"],
        scanner_input_digest=receipt["scanner_input_digest"],
    ))
    return rb.materialize_packet(
        declaration, members, ownership, issuer.issue_verification(receipt_sealed)
    )


def _packet_payload(packet: rb.ReviewPacket) -> dict:
    return {
        "identity": packet.identity,
        "declaration": rb._canonical(packet.declaration),
        "members": rb._canonical(packet.members),
        "ownership": rb._canonical(packet.ownership),
        "evidence": rb._canonical(packet.evidence),
        "member_shas": [list(pair) for pair in packet.member_shas],
        "expected_arms": list(rb.expected_reviewer_arms(
            packet.declaration.review_lane
        )),
    }


def _cmd_ready(args) -> int:
    try:
        plan_text = _load_plan(args.plan)
        fields = _projection_fields(plan_text, args.batch)
        batch_id = _batch_id(args, fields)
    except (OSError, ValueError) as exc:
        return _fail({"ready": False, "reasons": [str(exc)]})
    ready, members, reasons = _readiness(plan_text, fields)
    print(json.dumps({
        "batch_id": batch_id, "ready": ready,
        "members": members, "reasons": reasons,
    }, sort_keys=True))
    return 0 if ready else 1


def _build_from_args(args):
    plan_text = _load_plan(args.plan)
    fields = _projection_fields(plan_text, args.batch)
    ready, _, reasons = _readiness(plan_text, fields)
    if not ready:
        raise ValueError("; ".join(reasons))
    return build_packet(
        plan_text=plan_text,
        fields=fields,
        receipt=_read_receipt(args.verification_receipt),
        repo_root=Path(args.repo_root),
    )


def _cmd_packet(args) -> int:
    try:
        packet = _build_from_args(args)
    except (OSError, ValueError, rb.PacketRefused, KeyError) as exc:
        return _fail({"packet": None, "reasons": [str(exc)]})
    print(json.dumps(_packet_payload(packet), sort_keys=True))
    return 0


def _cmd_record_dispatch(args) -> int:
    try:
        packet = json.loads(Path(args.packet_file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail({"recorded": False, "reasons": [str(exc)]})
    if not (type(packet) is dict and packet.get("identity")):
        return _fail({"recorded": False, "reasons": ["packet file is malformed"]})
    # Task 9 adds refusal/idempotency semantics; this subcommand only writes it.
    receipt = {
        "schema": "batch-dispatch-receipt-v1",
        "batch_id": packet["declaration"]["batch_id"],
        "packet_identity": packet["identity"],
        "arms": packet.get("expected_arms", []),
    }
    Path(args.out).write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")
    print(json.dumps({**receipt, "recorded": True}, sort_keys=True))
    return 0


def _cmd_apply_result(args) -> int:
    try:
        packet = _build_from_args(args)
        payload = json.loads(Path(args.result_file).read_text(encoding="utf-8"))
        if not (type(payload) is dict and set(payload) == {
            "arm_bindings", "terminal_results",
        }):
            raise ValueError("reviewer result file is malformed")
        expected_arms = rb.expected_reviewer_arms(packet.declaration.review_lane)
        bindings = tuple(
            rb.ReviewerArmBinding(
                packet.identity, binding["arm"],
                binding["dispatch_identity"], binding["evidence_identity"],
            )
            for binding in payload["arm_bindings"]
        )
        results = tuple(
            rb.ReviewerTerminalResult(
                packet_identity=packet.identity,
                arm=result["arm"],
                dispatch_identity=result["dispatch_identity"],
                dispatch_evidence_identity=result["dispatch_evidence_identity"],
                result_identity=result["result_identity"],
                evidence_identity=result["evidence_identity"],
                terminal=result["terminal"],
                verdict=result["verdict"],
                findings=tuple(
                    rb.BlockingFinding(
                        finding_id=finding["finding_id"],
                        packet_identity=packet.identity,
                        arm=result["arm"],
                        dispatch_identity=result["dispatch_identity"],
                        evidence_identity=result["evidence_identity"],
                        owners=tuple(finding["owners"]),
                        blocking=finding["blocking"],
                        ground=finding["ground"],
                        ground_ref=finding["ground_ref"],
                        location=finding["location"],
                        severity=finding["severity"],
                        reason=finding["reason"],
                    )
                    for finding in result["findings"]
                ),
            )
            for result in payload["terminal_results"]
        )
        resolution = rb.resolve_aggregate_review(
            packet=packet,
            declared_lane=packet.declaration.review_lane,
            expected_arms=expected_arms,
            arm_bindings=bindings,
            terminal_results=results,
        )
    except (OSError, ValueError, rb.PacketRefused, KeyError, TypeError) as exc:
        return _fail({"action": None, "reasons": [str(exc)]})
    print(json.dumps({
        "action": resolution.action,
        "reopen_owners": list(resolution.reopen_owners),
        "ledger_mutation_allowed": resolution.ledger_mutation_allowed,
        "reasons": list(resolution.reasons),
        "transition_authority_present": resolution.transition_authority is not None,
    }, sort_keys=True))
    return 0 if resolution.ledger_mutation_allowed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="batch_review_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    ready = sub.add_parser("ready")
    ready.add_argument("--plan", required=True)
    ready.add_argument("--batch")
    ready.set_defaults(handler=_cmd_ready)

    packet = sub.add_parser("packet")
    packet.add_argument("--plan", required=True)
    packet.add_argument("--repo-root", required=True)
    packet.add_argument("--verification-receipt", required=True)
    packet.add_argument("--batch")
    packet.set_defaults(handler=_cmd_packet)

    record = sub.add_parser("record-dispatch")
    record.add_argument("--packet-file", required=True)
    record.add_argument("--out", required=True)
    record.set_defaults(handler=_cmd_record_dispatch)

    apply_result = sub.add_parser("apply-result")
    apply_result.add_argument("--plan", required=True)
    apply_result.add_argument("--repo-root", required=True)
    apply_result.add_argument("--verification-receipt", required=True)
    apply_result.add_argument("--result-file", required=True)
    apply_result.add_argument("--batch")
    apply_result.set_defaults(handler=_cmd_apply_result)

    args = parser.parse_args(argv if argv is not None else None)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())