"""Executable contract for the batch review adapter CLI (repair R7).

The CLI is a thin wiring layer over review_batch.py's sealed-packet and
resolve functions: one assembly-free orchestration path for SDD's batch
checkpoint.  These pins drive all four subcommands on a synthetic validated
plan.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "loom-code" / "scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cli = _load("batch_review_cli", "batch_review_cli.py")
review_batch = _load("review_batch_cli_lib", "review_batch.py")


_IMPLEMENTED_1 = "implemented(" + "a" * 40 + ")"
_IMPLEMENTED_2 = "implemented(" + "b" * 40 + ")"


def _plan_text(status_1: str = _IMPLEMENTED_1, status_2: str = _IMPLEMENTED_2) -> str:
    return f"""# Plan

Goal: prove the adapter CLI chain.
Stage: sdd:wave-1

## Task 1 — first

- **Description**: fixture
- **Dependencies**: none
- **Files touched**: src/1.py
- **Acceptance**: accept-1
- **Brief item covered**: REQ-1
- **Review-weight**: full
- **Review disposition**: batch(capability)
- **Status**: {status_1}

## Task 2 — second

- **Description**: fixture
- **Dependencies**: Task 1 completes first
- **Files touched**: src/2.py
- **Acceptance**: accept-2
- **Brief item covered**: REQ-2
- **Review-weight**: full
- **Review disposition**: batch(capability)
- **Status**: {status_2}

## Review Batches

### Review Batch: capability
- **Members**: Task 1, Task 2
- **Verdict question**: Does the capability work?
- **Review lane**: full
- **Aggregate verification**: package test suite
- **Boundary**: capability: fixture; exclusions: none; consumable: yes
"""


def _write_workspace(tmp_path: Path, *, status_2: str = _IMPLEMENTED_2) -> tuple[Path, Path]:
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "src" / "1.py").write_bytes(b"member 1")
    (repo_root / "src" / "2.py").write_bytes(b"member 2")
    plan_path = repo_root / "plan.md"
    plan_path.write_text(_plan_text(_IMPLEMENTED_1, status_2), encoding="utf-8")
    receipt_path = tmp_path / "verification-receipt.json"
    receipt_path.write_text(json.dumps({
        "argv": ["python3", "-m", "pytest"],
        "execution_scope": ["src"],
        "result": "exit=0",
        "scanner_receipt_identity": "scanner:fixture",
        "scanner_input_digest": "d" * 64,
    }), encoding="utf-8")
    return plan_path, repo_root


def _run(main_argv: list[str]) -> tuple[int, dict]:
    code = cli.main(main_argv)
    raw = sys.stdout.getvalue().strip() if hasattr(sys.stdout, "getvalue") else ""
    return code, json.loads(raw) if raw else {}


def _packet_json(plan_path: Path, repo_root: Path, receipt_path: Path, capsys) -> dict:
    code = cli.main([
        "packet", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
    ])
    assert code == 0
    return json.loads(capsys.readouterr().out)


def _result_file(tmp_path: Path, *, reopen: bool = False) -> Path:
    arms = ("spec-reviewer", "code-quality-reviewer")
    finding = {
        "finding_id": "finding:task-2",
        "arm": "spec-reviewer",
        "dispatch_identity": "dispatch:spec-reviewer",
        "evidence_identity": "result-proof:spec-reviewer",
        "owners": ["Task 2"],
        "blocking": True,
        "ground": "owned_requirement",
        "ground_ref": "REQ-2",
        "location": "src/2.py",
        "severity": "fatal",
        "reason": "fixture regression",
    }
    payload = {
        "arm_bindings": [
            {"arm": arm,
             "dispatch_identity": f"dispatch:{arm}",
             "evidence_identity": f"dispatch-proof:{arm}"}
            for arm in arms
        ],
        "terminal_results": [
            {"arm": arm,
             "dispatch_identity": f"dispatch:{arm}",
             "dispatch_evidence_identity": f"dispatch-proof:{arm}",
             "result_identity": f"result:{arm}:{'reopen' if reopen else 'pass'}",
             "evidence_identity": "result-proof:" + arm,
             "terminal": "completed",
             "verdict": "NEEDS_REVISION" if reopen and arm == arms[0] else "PASS",
             "findings": [finding] if reopen and arm == arms[0] else []}
            for arm in arms
        ],
    }
    path = tmp_path / "reviewer-results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_ready_fails_loud_on_unreadable_plan(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    (repo_root / "plan.md").chmod(0o000)
    try:
        (repo_root / "plan.md").read_text(encoding="utf-8")
    except PermissionError:
        pass
    else:
        (repo_root / "plan.md").chmod(0o644)
        pytest.skip("unreadable files still readable under this privilege")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code != 0
    assert out["ready"] is False
    assert out["reasons"]
    (repo_root / "plan.md").chmod(0o644)


def test_ready_reports_batch_readiness(tmp_path, capsys) -> None:
    plan_path, repo_root, = _write_workspace(tmp_path)
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code == 0
    assert out["batch_id"] == "capability"
    assert out["ready"] is True
    assert out["members"] == [
        {"task_id": "Task 1", "status": _IMPLEMENTED_1},
        {"task_id": "Task 2", "status": _IMPLEMENTED_2},
    ]


def test_ready_refuses_unimplemented_member(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path, status_2="pending")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code != 0
    assert out["ready"] is False


def test_ready_refuses_schema_invalid_plan(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    plan_path.write_text(_plan_text().replace("## Review Batches", "## Batches"), encoding="utf-8")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code != 0
    assert out["ready"] is False
    assert out["reasons"]


def test_packet_is_sealed_and_library_shaped(tmp_path, capsys) -> None:
    # The CLI's packet must equal the library's own chain on the same inputs;
    # identity is the digest of the entire authority payload, so an identity
    # match proves shape equality.
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    emitted = _packet_json(plan_path, repo_root, receipt_path, capsys)

    oracle = review_batch._review_batch_oracle()
    plan_text = plan_path.read_text(encoding="utf-8")
    fields = oracle.execution_projection_fields(plan_text, "capability")
    declaration = review_batch.BatchDeclaration(**fields["declaration"])
    scope_issuer = review_batch._trusted_scope_issuer(
        issuer="git-scope-resolver", source_identity="git:sha1:v1",
        hash_algorithm="sha1",
    )
    members = []
    for number, sha, content in ((1, "a" * 40, b"member 1"), (2, "b" * 40, b"member 2")):
        path = f"src/{number}.py"
        files = (review_batch.ReviewedFile(path, content),)
        members.append(review_batch.MemberSnapshot(
            task_id=f"Task {number}",
            status=f"implemented({sha})",
            sha=sha,
            declared_files=(path,),
            files=files,
            owned_requirements=(f"REQ-{number}",),
            future_requirements=(),
            acceptance=(f"accept-{number}",),
            scope_proof=scope_issuer.issue(
                repository_identity=cli.REPOSITORY_IDENTITY,
                commit_sha=sha, tree_identity=sha, files=files,
            ),
        ))
    members = tuple(members)
    records = tuple(review_batch.OwnershipRecord(
        member.task_id, member.owned_requirements,
        member.future_requirements, member.acceptance,
    ) for member in members)
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first", source_identity="authority:v1",
        source_digest=review_batch.text_digest(plan_text),
    )
    ownership = issuer.issue_ownership(
        plan_identity=cli.PLAN_IDENTITY, spec_identity=cli.SPEC_IDENTITY,
        records=records,
        execution_projection=review_batch._issue_execution_projection_from_validated_plan(
            plan_text=plan_text, batch_id="capability",
            plan_identity=cli.PLAN_IDENTITY, spec_identity=cli.SPEC_IDENTITY,
            records=records, issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest=review_batch.text_digest(plan_text),
        ),
    )
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver", source_identity="resolver:v1",
        source_digest="f" * 64,
    ).issue(review_batch._approved_safe_resolution(
        declaration_digest=review_batch.text_digest(declaration.aggregate_verification),
        argv=("python3", "-m", "pytest"),
        execution_scope=("src",),
        result="exit=0",
        scanner_receipt_identity="scanner:fixture",
        scanner_input_digest="d" * 64,
    ))
    packet = review_batch.materialize_packet(
        declaration, members, ownership, issuer.issue_verification(receipt),
    )
    assert review_batch.validate_packet(packet) == ()
    assert emitted["identity"] == packet.identity
    assert emitted["member_shas"] == [
        ["Task 1", "a" * 40], ["Task 2", "b" * 40],
    ]
    assert emitted["expected_arms"] == ["spec-reviewer", "code-quality-reviewer"]


def test_packet_refuses_when_not_ready(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path, status_2="pending")
    receipt_path = tmp_path / "verification-receipt.json"
    code = cli.main([
        "packet", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
    ])
    capsys.readouterr()
    assert code != 0


def test_record_dispatch_writes_receipt(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    code = cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ])
    capsys.readouterr()
    assert code == 0
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored["packet_identity"] == json.loads(
        packet_file.read_text(encoding="utf-8")
    )["identity"]
    assert stored["batch_id"] == "capability"
    assert stored["arms"] == ["spec-reviewer", "code-quality-reviewer"]


def test_record_dispatch_refuses_second_dispatch_without_terminal_result(
    tmp_path, capsys,
) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    argv = [
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]
    assert cli.main(argv) == 0
    capsys.readouterr()
    code, out = _run(argv)
    capsys.readouterr()
    assert code != 0
    assert out["recorded"] is False
    assert "re-collect" in " ".join(out["reasons"])


def test_record_dispatch_allows_new_cycle_after_result_applied(
    tmp_path, capsys,
) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path)
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    argv = [
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]
    assert cli.main(argv) == 0
    capsys.readouterr()
    apply_code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    capsys.readouterr()
    assert apply_code == 0
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored["result_applied"] is True
    code, out = _run(argv)
    capsys.readouterr()
    assert code == 0
    assert out["recorded"] is True


def _other_batch_receipt(tmp_path: Path, *, applied: bool) -> Path:
    receipt = {
        "schema": "batch-dispatch-receipt-v1",
        "batch_id": "other-capability",
        "packet_identity": "packet:other",
        "arms": ["spec-reviewer"],
        "members": ["Task 2"],
    }
    if applied:
        receipt["result_applied"] = True
    path = tmp_path / "other-dispatch-receipt.json"
    path.write_text(json.dumps(receipt), encoding="utf-8")
    return path


def test_ready_refuses_member_in_second_non_terminal_batch(
    tmp_path, capsys,
) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    other = _other_batch_receipt(tmp_path, applied=False)
    code, out = _run([
        "ready", "--plan", str(plan_path), "--receipt", str(other),
    ])
    capsys.readouterr()
    assert code != 0
    assert out["ready"] is False
    reason = " ".join(out["reasons"])
    assert "Task 2" in reason
    assert "other-capability" in reason


def test_ready_is_ready_for_clean_batch(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    other = _other_batch_receipt(tmp_path, applied=True)
    code, out = _run([
        "ready", "--plan", str(plan_path), "--receipt", str(other),
    ])
    capsys.readouterr()
    assert code == 0
    assert out["ready"] is True
    assert out["reasons"] == []


def test_apply_result_finalizes(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["action"] == "finalize"
    assert out["reopen_owners"] == []
    assert out["ledger_mutation_allowed"] is True


def test_apply_result_reopens_with_owner_union(tmp_path, capsys) -> None:
    plan_path, repo_root = _write_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path, reopen=True)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code == 0
    assert out["action"] == "reopen"
    assert out["reopen_owners"] == ["Task 2"]