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
        [--batch <id>] [--receipt <dispatch-receipt.json>]

``ready --receipt`` (repeatable) reports not-ready when a member also sits in
another batch whose dispatch receipt has no terminal result applied yet;
``apply-result --receipt`` marks that receipt's result applied, which unblocks
both the next ``ready`` and a fresh dispatch cycle.  ``record-dispatch`` refuses
(fail-loud) a second dispatch for a batch whose receipt exists without an
applied terminal result — re-collect instead of re-send, keyed on the
batch_id across every receipt file in ``--out``'s directory, not merely the
exact ``--out`` path.  A crash between the ledger write and the receipt flip
inside one ``apply-result --receipt`` run does not strand the receipt: for
either resolution shape (finalize or reopen), re-running the same command
recognizes every member already sitting at its resolution's settled status
(finalize: every member ``done(<sha>)``; reopen: owners ``pending``,
non-owners still ``implemented(<sha>)``) and flips the receipt idempotently
instead of re-running the ledger write (see ``_recover_settled_receipt``).

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
import subprocess
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
plan_card = _load("plan_card_for_batch_review_cli", "plan_card.py")

_GIT_TIMEOUT_SECONDS = 30


_TASK_HEADING = re.compile(r"^## Task (\d+)\b.*$", re.MULTILINE)
_H2_HEADING = re.compile(r"^##\s+", re.MULTILINE)
# `\*{0,2}` mirrors plan_card.py's own `_STATUS_BULLET` tolerance for both a
# bolded `- **Status**:` and a plain `- Status:` line.
_STATUS_FIELD = re.compile(r"^\s*-\s*\*{0,2}Status\*{0,2}:\s*(.+?)\s*$", re.MULTILINE)
_IMPLEMENTED = re.compile(r"^implemented\(([0-9a-f]{40})\)$")
_IMPLEMENTED_ANY_SHA = re.compile(r"^implemented\((.*)\)$")
_DONE = re.compile(r"^done\(([0-9a-f]{40})\)$")


def _run_subprocess(args: list[str], *, text: bool = True) -> subprocess.CompletedProcess:
    """Shared subprocess.run wrapper: one place translates a hung external
    process into the fail-loud PacketRefused every git call in this module
    must surface as (Task 18d — folds what were three separate
    TimeoutExpired->PacketRefused copies)."""
    try:
        return subprocess.run(
            args, capture_output=True, text=text, timeout=_GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise rb.PacketRefused(f"{' '.join(args)} timed out")


def _run_git(repo_root: Path, *args: str) -> str:
    """Run git in repo_root; fail loud with stderr on any non-zero exit."""
    result = _run_subprocess(["git", "-C", str(repo_root), *args])
    if result.returncode != 0:
        raise rb.PacketRefused(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout


def _committed_bytes(repo_root: Path, sha: str, path: str) -> bytes:
    """Read one declared file's exact committed bytes at <sha> — never the
    live worktree, so a post-commit edit cannot change what gets sealed.

    Grounding (external-surface category 4, CLI flag): the `git cat-file
    -t <sha>:<path>` type check mirrors the in-repo idiom documented at
    `loom-code/scripts/loom_gate_markers.py` (`_show_committed_file`,
    lines 159-240) — a directory, a submodule gitlink, or an unresolvable
    sha can each make `git show <sha>:<path>` exit 0 without returning
    real blob content, so the type must be checked as `blob` first."""
    if not rb._safe_repo_path(path):
        raise rb.PacketRefused(f"{path} is not a safe repo-relative path")
    kind = _run_subprocess(
        ["git", "-C", str(repo_root), "cat-file", "-t", f"{sha}:{path}"]
    )
    if kind.returncode != 0 or kind.stdout.strip() != "blob":
        raise rb.PacketRefused(f"{path} is not a committed blob at {sha}")
    result = _run_subprocess(
        ["git", "-C", str(repo_root), "show", f"{sha}:{path}"], text=False,
    )
    if result.returncode != 0:
        raise rb.PacketRefused(f"{path} is not present at commit {sha}")
    return result.stdout


def _tree_identity(repo_root: Path, sha: str) -> str:
    return _run_git(repo_root, "rev-parse", f"{sha}^{{tree}}").strip()


def _repository_identity(repo_root: Path, sha: str) -> str:
    """Deterministic repository identity: a sha256 digest over the sorted
    root-commit sha(s) reachable from <sha> (git rev-list --max-parents=0
    <sha>) — anchored on the frozen member commit, NOT the repo's current
    HEAD, so moving HEAD to an unrelated second-root branch after a member
    was committed cannot change that member's already-issued identity
    (Task 18c). A repo with one linear history has exactly one root commit,
    so this is stable across invocations without depending on a remote URL
    or local config.

    Grounding (external-surface category 4, CLI flag): `git rev-list
    --max-parents=0 <rev>` lists commits with no parents, i.e. the root
    commit(s) reachable from <rev> — git-rev-list(1) §Commit Limiting
    ("--max-parents=<number>: show only commits which have at most that
    many parent commits"), verified live in-session (`git rev-list --max-parents=0 HEAD` → this repo's single root)
    2026-08-31; the same idiom already backs review_batch's repository
    binding tests."""
    roots = sorted(_run_git(repo_root, "rev-list", "--max-parents=0", sha).split())
    if not roots:
        raise rb.PacketRefused("repository has no root commit")
    return rb.text_digest(",".join(roots))


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return Path(path).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except ValueError:
        return Path(path).name


def _plan_identity(plan_path: Path, repo_root: Path) -> str:
    """Derived from the repo-relative plan path so packet/apply-result on
    the same --plan/--repo-root pair always reconstruct the same identity."""
    return f"plan:{_repo_relative(plan_path, repo_root)}"


def _spec_identity(plan_path: Path, repo_root: Path) -> str:
    return f"spec:{_repo_relative(plan_path, repo_root)}"


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
        status = member["status"]
        if _IMPLEMENTED.fullmatch(status) is not None:
            continue
        if _IMPLEMENTED_ANY_SHA.fullmatch(status) is not None:
            reasons.append(
                f"{member['task_id']} implemented SHA is not the 40-hex form "
                "review_batch requires; expand it with git rev-parse"
            )
        else:
            reasons.append(
                f"{member['task_id']} status is not implemented(<sha>)"
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
    receipt_text: str,
    repo_root: Path,
    plan_path: Path,
) -> rb.ReviewPacket:
    """Materialize the sealed packet via review_batch's own trusted chain."""
    declaration = rb.BatchDeclaration(**fields["declaration"])
    root = Path(repo_root)
    plan_identity = _plan_identity(plan_path, root)
    spec_identity = _spec_identity(plan_path, root)
    scope_issuer = rb._trusted_scope_issuer(
        issuer="git-scope-resolver",
        source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    statuses = _member_statuses(
        plan_text, tuple(projected["task_id"] for projected in fields["members"])
    )
    members = []
    for projected in fields["members"]:
        match = _IMPLEMENTED.fullmatch(statuses[projected["task_id"]])
        if match is None:
            raise rb.PacketRefused(
                f"{projected['task_id']} is not exactly implemented(<sha>)"
            )
        sha = match.group(1)
        files = tuple(
            rb.ReviewedFile(path, _committed_bytes(root, sha, path))
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
                repository_identity=_repository_identity(root, sha),
                commit_sha=sha,
                tree_identity=_tree_identity(root, sha),
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
        plan_identity=plan_identity,
        spec_identity=spec_identity,
        records=records,
        execution_projection=rb._issue_execution_projection_from_validated_plan(
            plan_text=plan_text,
            batch_id=declaration.batch_id,
            plan_identity=plan_identity,
            spec_identity=spec_identity,
            records=records,
            issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest=rb.text_digest(plan_text),
        ),
    )
    receipt_sealed = rb._trusted_resolution_issuer(
        issuer="declared-first-resolver",
        source_identity="resolver:v1",
        source_digest=rb.text_digest(receipt_text),
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
    _, members, reasons = _readiness(plan_text, fields)
    for receipt_path in args.receipt or []:
        try:
            other = _read_dispatch_receipt(receipt_path)
        except (OSError, ValueError) as exc:
            return _fail({"ready": False, "reasons": [str(exc)]})
        if other["batch_id"] == batch_id or other["result_applied"]:
            continue
        for member_id in fields["declaration"]["members"]:
            if member_id in other["members"]:
                reasons.append(
                    f"{member_id} is in another non-terminal batch "
                    f"{other['batch_id']}"
                )
    ready = not reasons
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
        receipt_text=Path(args.verification_receipt).read_text(encoding="utf-8"),
        repo_root=Path(args.repo_root),
        plan_path=Path(args.plan),
    )


def _cmd_packet(args) -> int:
    try:
        packet = _build_from_args(args)
    except (OSError, ValueError, rb.PacketRefused, KeyError) as exc:
        return _fail({"packet": None, "reasons": [str(exc)]})
    print(json.dumps(_packet_payload(packet), sort_keys=True))
    return 0


def _read_dispatch_receipt(receipt_path: str) -> dict:
    """Parse and validate a batch-dispatch-receipt-v1 file, fail loud."""
    stored = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    if not (
        type(stored) is dict
        and stored.get("schema") == "batch-dispatch-receipt-v1"
        and type(stored.get("batch_id")) is str
        and type(stored.get("packet_identity")) is str
        and type(stored.get("members")) is list
        and all(type(item) is str for item in stored["members"])
    ):
        raise ValueError(f"{receipt_path} is not a batch-dispatch-receipt-v1")
    stored.setdefault("result_applied", False)
    return stored


def _sibling_unapplied_receipt(out_path: Path, batch_id: str) -> dict | None:
    """Scan ``out_path``'s parent directory for any other
    batch-dispatch-receipt-v1 file carrying the same batch_id with no
    terminal result applied yet (Task 18a). The idempotency refusal must
    key off batch_id, not off the exact ``--out`` path — a caller
    re-sending dispatch for the same batch under a different filename must
    still be refused."""
    parent = out_path.parent
    if not parent.is_dir():
        return None
    for candidate in sorted(parent.iterdir()):
        if not candidate.is_file() or candidate == out_path:
            continue
        try:
            stored = _read_dispatch_receipt(str(candidate))
        except (OSError, ValueError):
            continue
        if stored["batch_id"] == batch_id and not stored["result_applied"]:
            return stored
    return None


def _cmd_record_dispatch(args) -> int:
    try:
        packet = json.loads(Path(args.packet_file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail({"recorded": False, "reasons": [str(exc)]})
    if not (type(packet) is dict and packet.get("identity")):
        return _fail({"recorded": False, "reasons": ["packet file is malformed"]})
    out_path = Path(args.out)
    if out_path.exists():
        try:
            existing = _read_dispatch_receipt(args.out)
        except (OSError, ValueError) as exc:
            return _fail({"recorded": False, "reasons": [str(exc)]})
        if not existing["result_applied"]:
            return _fail({"recorded": False, "reasons": [
                f"batch {existing['batch_id']} already has a dispatch receipt "
                "with no terminal result yet; re-collect the reviewer result "
                "(apply-result) instead of re-sending the dispatch"
            ]})
    declaration = packet.get("declaration")
    batch_id = declaration.get("batch_id") if type(declaration) is dict else None
    if batch_id and _sibling_unapplied_receipt(out_path, batch_id) is not None:
        return _fail({"recorded": False, "reasons": [
            f"batch {batch_id} already has a dispatch receipt "
            "with no terminal result yet; re-collect the reviewer result "
            "(apply-result) instead of re-sending the dispatch"
        ]})
    try:
        receipt = {
            "schema": "batch-dispatch-receipt-v1",
            "batch_id": packet["declaration"]["batch_id"],
            "packet_identity": packet["identity"],
            "arms": packet.get("expected_arms", []),
            "members": [
                member["task_id"] for member in packet.get("members", [])
            ],
            "member_shas": {
                task_id: sha for task_id, sha in packet.get("member_shas", [])
            },
        }
    except (KeyError, TypeError) as exc:
        return _fail({"recorded": False, "reasons": [
            f"packet file is malformed: {exc}"
        ]})
    out_path.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")
    print(json.dumps({**receipt, "recorded": True}, sort_keys=True))
    return 0


def _ledger_expected_and_replacements(
    packet: rb.ReviewPacket, resolution: rb.AggregateReviewResolution,
) -> tuple[dict[int, str], dict[int, str]]:
    """Build plan_card's expected_statuses/replacements from the Packet's
    member snapshot and the resolution action (finalize -> every member
    SHA-preserving done(<sha>); reopen -> owners only -> pending)."""
    expected_statuses = {
        int(member.task_id.split()[1]): member.status
        for member in packet.members
    }
    if resolution.action == "finalize":
        replacements = {
            int(member.task_id.split()[1]): f"done({member.sha})"
            for member in packet.members
        }
    else:
        replacements = {
            int(owner.split()[1]): "pending"
            for owner in resolution.reopen_owners
        }
    return expected_statuses, replacements


def _recover_settled_receipt(args) -> dict | None:
    """Crash-window recovery for `apply-result --receipt`: the ledger CAS
    write (`plan_card.atomic_batch_status_update`) and the dispatch-receipt
    flip are two separate writes, in that order. A crash between them
    leaves every batch member already at the resolution's replacement
    status on the plan but the receipt's `result_applied` still False —
    re-running `apply-result` then fails at `_readiness` (no member is
    `implemented(<sha>)` any more), so the receipt is stuck forever and
    `ready --receipt` refuses any other batch sharing a member. Both
    resolution shapes are recovered, symmetrically (Task 18b):

    - finalize: every declared member's CURRENT plan status is `done(<sha>)`
      — the only replacement a finalize resolution ever produces.
    - reopen: every reopen owner's CURRENT plan status is `pending` and
      every non-owner is still `implemented(<sha>)` — the only replacement
      a reopen resolution ever produces.

    Either shape additionally requires the receipt is present and
    unapplied, AND the receipt's own identity matches: `batch_id` equals
    the batch this call resolves to, `members` is set-equal to the
    declaration's members, and the receipt's `member_shas` (required for
    recovery — an older receipt written before this field existed cannot
    be recovered) has each non-owner member's sha equal to the sha the
    plan's `implemented(<sha>)`/`done(<sha>)` status actually recorded.
    Without this check a stale receipt for an unrelated batch could be
    flipped using this batch's already-settled statuses, with no ledger
    write ever happening for the batch the receipt claims to cover.

    Returns None (caller re-raises the original readiness error) for
    every other case, including a genuine not-ready plan (no member
    reaches either settled shape above) and a plan that just happens to
    have every member `pending` for an unrelated reason (no reopen owner
    found), which this recovery does not attempt to distinguish from a
    recovered reopen with zero owners — an impossible resolution shape, so
    it is refused rather than guessed at."""
    receipt_path = getattr(args, "receipt", None)
    if not receipt_path or not Path(receipt_path).exists():
        return None
    try:
        stored = _read_dispatch_receipt(receipt_path)
        plan_text = _load_plan(args.plan)
        fields = _projection_fields(plan_text, args.batch)
        batch_id = _batch_id(args, fields)
    except (OSError, ValueError):
        return None
    if stored["result_applied"]:
        return None
    if stored["batch_id"] != batch_id:
        return None
    declared_members = tuple(fields["declaration"]["members"])
    if set(stored["members"]) != set(declared_members):
        return None
    member_shas = stored.get("member_shas")
    if not (type(member_shas) is dict and set(member_shas) == set(declared_members)):
        return None
    statuses = _member_statuses(plan_text, declared_members)
    if not statuses:
        return None

    if all(
        _DONE.fullmatch(status) is not None
        and _DONE.fullmatch(status).group(1) == member_shas[member_id]
        for member_id, status in statuses.items()
    ):
        action, reopen_owners = "finalize", []
    else:
        # Reopen recovery, symmetric with finalize (Task 18b): every owner
        # is already `pending` (the replacement `atomic_batch_status_update`
        # would have written) and every non-owner is still `implemented(<sha>)`
        # matching the receipt's recorded sha, unchanged by the reopen. A
        # crash between that CAS write and the receipt flip is otherwise
        # indistinguishable from this recovered state, so this is the only
        # signal available to recognize it.
        reopen_owners = [
            member_id for member_id, status in statuses.items()
            if status == "pending"
        ]
        non_owners_settled = all(
            member_id in reopen_owners or (
                _IMPLEMENTED.fullmatch(status) is not None
                and _IMPLEMENTED.fullmatch(status).group(1) == member_shas[member_id]
            )
            for member_id, status in statuses.items()
        )
        if not reopen_owners or not non_owners_settled:
            return None
        action = "reopen"

    stored["result_applied"] = True
    Path(receipt_path).write_text(
        json.dumps(stored, sort_keys=True), encoding="utf-8"
    )
    return {
        "action": action,
        "reopen_owners": reopen_owners,
        "ledger_mutation_allowed": True,
        "ledger_written": True,
        "reasons": [
            f"recovered: ledger already {action}d before an earlier crash; "
            "receipt now applied",
        ],
        "recovered": True,
        "transition_authority_present": False,  # not computed on the recovery path (see recovered: true)
    }


def _bind_receipt_to_packet(receipt_path: str, packet: rb.ReviewPacket) -> dict:
    """Refuse unless the dispatch receipt is the one issued for THIS packet:
    same batch_id, same member set, every member's rebuilt sha equal to the
    receipt's recorded `member_shas[member]`, and the same `packet_identity`.
    Raises ValueError naming the first drifted member (the audit's F1 shape:
    a PASS given for commit A applied after the ledger moved to commit B)
    or the foreign identity (F6: a receipt from another batch flipped).

    Ordering: this runs after the packet is rebuilt and BEFORE the reviewer
    result file is parsed, so an unbound receipt is refused without reading
    the result at all — the same batch_id -> members -> member_shas check
    order `_recover_settled_receipt` already uses on the crash-recovery
    path; the two paths must never disagree about what "this receipt
    belongs to this batch" means."""
    stored = _read_dispatch_receipt(receipt_path)
    batch_id = packet.declaration.batch_id
    if stored["batch_id"] != batch_id:
        raise ValueError(
            f"dispatch receipt {receipt_path} belongs to batch "
            f"{stored['batch_id']!r}, not {batch_id!r}"
        )
    rebuilt = dict(packet.member_shas)
    if set(stored["members"]) != set(rebuilt):
        raise ValueError(
            f"dispatch receipt {receipt_path} members {sorted(stored['members'])} "
            f"do not match batch {batch_id!r} members {sorted(rebuilt)}"
        )
    member_shas = stored.get("member_shas")
    if type(member_shas) is not dict:
        raise ValueError(
            f"dispatch receipt {receipt_path} has no member_shas; re-send the "
            "dispatch (record-dispatch) so the result can be bound to it"
        )
    for member_id, sha in rebuilt.items():
        if member_shas.get(member_id) != sha:
            raise ValueError(
                f"{member_id} drifted after dispatch: receipt recorded "
                f"{member_shas.get(member_id)}, ledger now {sha}; the reviewer "
                "never saw this commit — re-send the dispatch"
            )
    if stored["packet_identity"] != packet.identity:
        raise ValueError(
            f"dispatch receipt {receipt_path} packet_identity does not match "
            "the rebuilt packet; re-send the dispatch"
        )
    return stored


def _cmd_apply_result(args) -> int:
    try:
        try:
            packet = _build_from_args(args)
        except ValueError:
            recovered = _recover_settled_receipt(args)
            if recovered is not None:
                print(json.dumps(recovered, sort_keys=True))
                return 0
            raise
        _bind_receipt_to_packet(args.receipt, packet)
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
        ledger_written = True
        if resolution.ledger_mutation_allowed:
            # Only finalize/reopen (the mutating actions) touch the ledger;
            # a wait_refuse resolution writes nothing.
            expected_statuses, replacements = _ledger_expected_and_replacements(
                packet, resolution
            )
            ledger_written = plan_card.atomic_batch_status_update(
                Path(args.plan),
                packet.declaration.batch_id,
                expected_statuses,
                replacements,
                transition_authority=resolution.transition_authority,
            )
        if resolution.ledger_mutation_allowed and ledger_written:
            # Only a successfully-written ledger transition may flip the
            # dispatch receipt; a wait_refuse resolution, or a CAS decline,
            # must leave it unset so a fresh dispatch cycle stays possible.
            stored = _read_dispatch_receipt(args.receipt)
            stored["result_applied"] = True
            Path(args.receipt).write_text(
                json.dumps(stored, sort_keys=True), encoding="utf-8"
            )
    except (OSError, ValueError, rb.PacketRefused, KeyError, TypeError) as exc:
        return _fail({"action": None, "reasons": [str(exc)]})
    print(json.dumps({
        "action": resolution.action,
        "reopen_owners": list(resolution.reopen_owners),
        "ledger_mutation_allowed": resolution.ledger_mutation_allowed,
        "ledger_written": ledger_written,
        "reasons": list(resolution.reasons),
        "transition_authority_present": resolution.transition_authority is not None,
    }, sort_keys=True))
    return 0 if resolution.ledger_mutation_allowed and ledger_written else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="batch_review_cli.py")
    sub = parser.add_subparsers(dest="command", required=True)

    ready = sub.add_parser("ready")
    ready.add_argument("--plan", required=True)
    ready.add_argument("--batch")
    ready.add_argument("--receipt", action="append")
    ready.set_defaults(handler=_cmd_ready)

    packet = sub.add_parser("packet")
    packet.add_argument("--plan", required=True)
    packet.add_argument("--repo-root", required=True)
    packet.add_argument("--verification-receipt", required=True)
    packet.add_argument("--batch")
    packet.set_defaults(handler=_cmd_packet)

    record = sub.add_parser("record-dispatch")
    record.add_argument("--packet-file", required=True)
    record.add_argument("--out", required=True, help=(
        "dispatch receipt path; the idempotency refusal keys off batch_id "
        "across every receipt file in this path's directory, so an unapplied "
        "receipt for the same batch blocks a re-send regardless of filename"
    ))
    record.set_defaults(handler=_cmd_record_dispatch)

    apply_result = sub.add_parser("apply-result")
    apply_result.add_argument("--plan", required=True)
    apply_result.add_argument("--repo-root", required=True)
    apply_result.add_argument("--verification-receipt", required=True)
    apply_result.add_argument("--result-file", required=True)
    apply_result.add_argument("--receipt", required=True, help=(
        "dispatch receipt written by record-dispatch; the result is applied "
        "only if the rebuilt packet still matches its packet_identity and "
        "every member sha it recorded"
    ))
    apply_result.add_argument("--batch")
    apply_result.set_defaults(handler=_cmd_apply_result)

    args = parser.parse_args(argv if argv is not None else None)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())