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
import subprocess
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
    receipt_path.write_text(_receipt_json(), encoding="utf-8")
    return plan_path, repo_root


def _receipt_json() -> str:
    return json.dumps({
        "argv": ["python3", "-m", "pytest"],
        "execution_scope": ["src"],
        "result": "exit=0",
        "scanner_receipt_identity": "scanner:fixture",
        "scanner_input_digest": "d" * 64,
    })


def _init_git_repo(repo_root: Path) -> None:
    repo_root.mkdir(parents=True)
    subprocess.run(["git", "-C", str(repo_root), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repo_root), "config", "user.email", "t@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_root), "config", "user.name", "T"], check=True,
    )


def _git_commit_file(repo_root: Path, rel_path: str, content: bytes) -> str:
    path = repo_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    subprocess.run(["git", "-C", str(repo_root), "add", rel_path], check=True)
    subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-q", "-m", f"add {rel_path}"],
        check=True,
    )
    return subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def _write_git_workspace(tmp_path: Path) -> tuple[Path, Path, str, str]:
    """Real git-backed repo: two commits; plan.md declares each member's
    actual commit sha — the shape build_packet must read committed bytes
    from (not the live worktree)."""
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    sha1 = _git_commit_file(repo_root, "src/1.py", b"member 1")
    sha2 = _git_commit_file(repo_root, "src/2.py", b"member 2")
    plan_path = repo_root / "plan.md"
    plan_path.write_text(
        _plan_text(f"implemented({sha1})", f"implemented({sha2})"),
        encoding="utf-8",
    )
    receipt_path = tmp_path / "verification-receipt.json"
    receipt_path.write_text(_receipt_json(), encoding="utf-8")
    return plan_path, repo_root, sha1, sha2


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
    # match proves shape equality. Every provenance value below is derived
    # independently of the CLI module (raw git subprocess calls / known
    # fixture bytes), not imported from it, so this also pins the actual
    # provenance values (T8 fatal fix), not just structural agreement.
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
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
    root_shas = sorted(subprocess.run(
        ["git", "-C", str(repo_root), "rev-list", "--max-parents=0", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.split())
    repository_identity = review_batch.text_digest(",".join(root_shas))
    members = []
    for number, sha, content in ((1, sha1, b"member 1"), (2, sha2, b"member 2")):
        path = f"src/{number}.py"
        tree_identity = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", f"{sha}^{{tree}}"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
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
                repository_identity=repository_identity,
                commit_sha=sha, tree_identity=tree_identity, files=files,
            ),
        ))
    members = tuple(members)
    records = tuple(review_batch.OwnershipRecord(
        member.task_id, member.owned_requirements,
        member.future_requirements, member.acceptance,
    ) for member in members)
    plan_identity, spec_identity = "plan:plan.md", "spec:plan.md"
    issuer = review_batch._trusted_proof_issuer(
        issuer="sdd:declared-first", source_identity="authority:v1",
        source_digest=review_batch.text_digest(plan_text),
    )
    ownership = issuer.issue_ownership(
        plan_identity=plan_identity, spec_identity=spec_identity,
        records=records,
        execution_projection=review_batch._issue_execution_projection_from_validated_plan(
            plan_text=plan_text, batch_id="capability",
            plan_identity=plan_identity, spec_identity=spec_identity,
            records=records, issuer="plan-card:validated-schema",
            source_identity="plan:current",
            source_digest=review_batch.text_digest(plan_text),
        ),
    )
    receipt_text = receipt_path.read_text(encoding="utf-8")
    receipt = review_batch._trusted_resolution_issuer(
        issuer="declared-first-resolver", source_identity="resolver:v1",
        source_digest=review_batch.text_digest(receipt_text),
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
        ["Task 1", sha1], ["Task 2", sha2],
    ]
    assert emitted["expected_arms"] == ["spec-reviewer", "code-quality-reviewer"]


def test_packet_reads_committed_bytes_not_worktree_edits(tmp_path, capsys) -> None:
    """A post-commit worktree edit to a member's declared file must not
    change the emitted packet identity — the packet seals the commit's
    content, never whatever currently sits in the working tree (T8 fatal)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    baseline = _packet_json(plan_path, repo_root, receipt_path, capsys)

    (repo_root / "src" / "2.py").write_bytes(b"tampered after commit")

    after_edit = _packet_json(plan_path, repo_root, receipt_path, capsys)
    assert after_edit["identity"] == baseline["identity"]


def test_packet_refuses_missing_committed_file(tmp_path, capsys) -> None:
    """A declared file absent from the member's commit refuses (T8 fatal)."""
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    sha1 = _git_commit_file(repo_root, "src/1.py", b"member 1")
    sha2 = _git_commit_file(repo_root, "src/2.py", b"member 2")
    plan_text = _plan_text(
        f"implemented({sha1})", f"implemented({sha2})",
    ).replace(
        "- **Files touched**: src/2.py",
        "- **Files touched**: src/2.py, src/missing.py",
    )
    plan_path = repo_root / "plan.md"
    plan_path.write_text(plan_text, encoding="utf-8")
    receipt_path = tmp_path / "verification-receipt.json"
    receipt_path.write_text(_receipt_json(), encoding="utf-8")
    code = cli.main([
        "packet", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["packet"] is None
    assert "missing.py" in " ".join(out["reasons"])


def test_packet_refuses_directory_path(tmp_path, capsys) -> None:
    """A declared 'file' that is actually a directory at <sha> must refuse,
    not be sealed as a blob — `git show <sha>:<dir>` exits 0 with a tree
    listing, which _committed_bytes would otherwise happily seal (T8 round-2
    🟡 hardening)."""
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    sha1 = _git_commit_file(repo_root, "src/1.py", b"member 1")
    sha2 = _git_commit_file(repo_root, "src/dir/inner.py", b"nested")
    plan_text = _plan_text(
        f"implemented({sha1})", f"implemented({sha2})",
    ).replace(
        "- **Files touched**: src/2.py",
        "- **Files touched**: src/dir",
    )
    plan_path = repo_root / "plan.md"
    plan_path.write_text(plan_text, encoding="utf-8")
    receipt_path = tmp_path / "verification-receipt.json"
    receipt_path.write_text(_receipt_json(), encoding="utf-8")
    code = cli.main([
        "packet", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["packet"] is None
    assert "not a committed blob" in " ".join(out["reasons"])


def test_git_timeout_refuses_instead_of_raising(tmp_path, capsys, monkeypatch) -> None:
    """A hung git subprocess must surface as a PacketRefused-driven CLI
    refusal, not an uncaught TimeoutExpired traceback (T8 round-2 🟢)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"

    def _hangs(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0] if args else "git", timeout=30)

    monkeypatch.setattr(cli.subprocess, "run", _hangs)
    code = cli.main([
        "packet", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["packet"] is None
    assert "timed out" in " ".join(out["reasons"]).lower()


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
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
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
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
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
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
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
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
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
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
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


def test_apply_result_writes_ledger_on_finalize(tmp_path, capsys) -> None:
    """After the fix, a finalize resolution writes done(<same sha>) for
    every member under the plan lock — today it leaves implemented(<sha>)
    and a human flips the ledger by hand (R11c)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
    ])
    capsys.readouterr()
    assert code == 0
    plan_text = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: done({sha1})" in plan_text
    assert f"- **Status**: done({sha2})" in plan_text
    assert f"implemented({sha1})" not in plan_text
    assert f"implemented({sha2})" not in plan_text


def test_apply_result_writes_ledger_on_reopen(tmp_path, capsys) -> None:
    """A reopen resolution flips only the owning member's status to
    pending; the non-owning member's implemented(<sha>) is unchanged."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path, reopen=True)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
    ])
    capsys.readouterr()
    assert code == 0
    plan_text = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: implemented({sha1})" in plan_text
    task_2_block = plan_text.split("## Task 2")[1].split("## Review Batches")[0]
    assert "- **Status**: pending" in task_2_block


def test_apply_result_wait_refuse_writes_nothing(tmp_path, capsys) -> None:
    """A wait_refuse resolution (incomplete result set) must not touch the
    plan file at all."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _incomplete_result_file(tmp_path)
    before = plan_path.read_text(encoding="utf-8")
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
    ])
    capsys.readouterr()
    assert code != 0
    assert plan_path.read_text(encoding="utf-8") == before


def _incomplete_result_file(tmp_path: Path) -> Path:
    """Only one of the two expected arms carries a terminal result —
    resolve_aggregate_review returns a non-mutating wait_refuse."""
    payload = {
        "arm_bindings": [
            {"arm": "spec-reviewer",
             "dispatch_identity": "dispatch:spec-reviewer",
             "evidence_identity": "dispatch-proof:spec-reviewer"},
            {"arm": "code-quality-reviewer",
             "dispatch_identity": "dispatch:code-quality-reviewer",
             "evidence_identity": "dispatch-proof:code-quality-reviewer"},
        ],
        "terminal_results": [
            {"arm": "spec-reviewer",
             "dispatch_identity": "dispatch:spec-reviewer",
             "dispatch_evidence_identity": "dispatch-proof:spec-reviewer",
             "result_identity": "result:spec-reviewer:only",
             "evidence_identity": "result-proof:spec-reviewer",
             "terminal": "completed", "verdict": "PASS", "findings": []},
        ],
    }
    path = tmp_path / "incomplete-reviewer-results.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_apply_result_does_not_flip_receipt_on_non_terminal_resolution(
    tmp_path, capsys,
) -> None:
    """apply-result's receipt flip must gate on
    resolution.ledger_mutation_allowed, not merely on reaching
    resolve_aggregate_review — a wait_refuse (non-terminal aggregate) must
    leave the dispatch receipt's result_applied unset (T9 spec gap)."""
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _incomplete_result_file(tmp_path)
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    assert cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]) == 0
    capsys.readouterr()
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["action"] == "wait_refuse"
    assert out["ledger_mutation_allowed"] is False
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored.get("result_applied", False) is False

def test_apply_result_recovers_receipt_stuck_after_ledger_crash(
    tmp_path, capsys, monkeypatch,
) -> None:
    """A crash between the ledger CAS write and the dispatch-receipt flip
    must not strand the receipt forever: once the plan already shows every
    member as done(<sha>) (the ledger side succeeded) but result_applied is
    still False, re-running apply-result --receipt must recover by flipping
    the receipt idempotently instead of failing readiness forever (code
    review round-1 finding)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path)
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    assert cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]) == 0
    capsys.readouterr()

    real_write_text = Path.write_text

    def _crash_on_receipt_write(self, *call_args, **call_kwargs):
        if self == dispatch_receipt:
            raise OSError("simulated crash before receipt flip")
        return real_write_text(self, *call_args, **call_kwargs)

    monkeypatch.setattr(Path, "write_text", _crash_on_receipt_write)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    capsys.readouterr()
    assert code != 0
    plan_after_crash = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: done({sha1})" in plan_after_crash
    assert f"- **Status**: done({sha2})" in plan_after_crash
    stored_after_crash = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored_after_crash.get("result_applied", False) is False

    monkeypatch.setattr(Path, "write_text", real_write_text)
    code2 = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    out2 = json.loads(capsys.readouterr().out)
    assert code2 == 0
    assert out2["ledger_written"] is True
    assert out2["recovered"] is True
    assert out2.get("transition_authority_present") is False
    stored_after_recovery = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored_after_recovery["result_applied"] is True
    assert plan_path.read_text(encoding="utf-8") == plan_after_crash


def _stuck_finalized_plan(plan_path: Path, sha1: str, sha2: str) -> None:
    """Rewrite plan.md as if the ledger CAS write already finalized both
    members (post-crash state) without going through a real crash."""
    plan_text = plan_path.read_text(encoding="utf-8")
    plan_text = plan_text.replace(f"implemented({sha1})", f"done({sha1})")
    plan_text = plan_text.replace(f"implemented({sha2})", f"done({sha2})")
    plan_path.write_text(plan_text, encoding="utf-8")


def test_apply_result_recovery_refuses_wrong_batch_receipt(tmp_path, capsys) -> None:
    """A stuck receipt for a DIFFERENT batch_id than the one apply-result
    resolves must not be flipped by borrowing this batch's done() statuses
    (round-2 quality fix: recovery must check batch identity)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    _stuck_finalized_plan(plan_path, sha1, sha2)
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    dispatch_receipt.write_text(json.dumps({
        "schema": "batch-dispatch-receipt-v1",
        "batch_id": "other-capability",
        "packet_identity": "packet:other",
        "arms": ["spec-reviewer"],
        "members": ["Task 1", "Task 2"],
        "member_shas": {"Task 1": sha1, "Task 2": sha2},
        "result_applied": False,
    }), encoding="utf-8")
    result_path = _result_file(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["action"] is None
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored["result_applied"] is False


def test_apply_result_recovery_refuses_sha_mismatch(tmp_path, capsys) -> None:
    """A stuck receipt whose recorded member sha doesn't match the plan's
    done(<sha>) must not be flipped — the receipt could be for a rebuilt
    packet on the same batch with a different member commit (round-2
    quality fix: recovery must check per-member sha)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    _stuck_finalized_plan(plan_path, sha1, sha2)
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    dispatch_receipt.write_text(json.dumps({
        "schema": "batch-dispatch-receipt-v1",
        "batch_id": "capability",
        "packet_identity": "packet:fixture",
        "arms": ["spec-reviewer"],
        "members": ["Task 1", "Task 2"],
        "member_shas": {"Task 1": sha1, "Task 2": "f" * 40},
        "result_applied": False,
    }), encoding="utf-8")
    result_path = _result_file(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["action"] is None
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored["result_applied"] is False


def test_record_dispatch_refuses_malformed_packet_missing_batch_id(
    tmp_path, capsys,
) -> None:
    """A malformed packet file (missing declaration.batch_id) must emit the
    JSON refusal, not an uncaught KeyError traceback (T8 quality fix)."""
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps({
        "identity": "packet:malformed", "declaration": {}, "members": [],
    }), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    code, out = _run([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ])
    capsys.readouterr()
    assert code != 0
    assert out["recorded"] is False
    assert not dispatch_receipt.exists()


def test_ready_reports_short_sha_message(tmp_path, capsys) -> None:
    """A short (non-40-hex) SHA in an implemented(...) status gets its own
    refusal message pointing at git rev-parse expansion (T8 quality fix)."""
    plan_path, repo_root = _write_workspace(tmp_path, status_2="implemented(abc123)")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code != 0
    reason = " ".join(out["reasons"])
    assert "40-hex" in reason
    assert "git rev-parse" in reason


def test_ready_reports_non_implemented_status_message(tmp_path, capsys) -> None:
    """A status that is not implemented(...) at all gets the other message,
    distinct from the short-SHA case (T8 quality fix)."""
    plan_path, repo_root = _write_workspace(tmp_path, status_2="pending")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code != 0
    reason = " ".join(out["reasons"])
    assert "40-hex" not in reason
    assert "not implemented" in reason


def test_ready_accepts_unbolded_status_field(tmp_path, capsys) -> None:
    """plan_card.py tolerates an unbolded `- Status:` line
    (`\\*{0,2}Status\\*{0,2}`); the CLI's own field parser must match that
    same tolerance (T8 quality fix)."""
    plan_path, repo_root = _write_workspace(tmp_path)
    unbolded = _plan_text(_IMPLEMENTED_1, _IMPLEMENTED_2).replace(
        "- **Status**:", "- Status:"
    )
    plan_path.write_text(unbolded, encoding="utf-8")
    code, out = _run(["ready", "--plan", str(plan_path)])
    capsys.readouterr()
    assert code == 0
    assert out["ready"] is True


def test_record_dispatch_refuses_same_batch_different_out_path(
    tmp_path, capsys,
) -> None:
    """The idempotency refusal must key off batch_id across the receipt
    directory, not off the exact --out path — a caller re-sending dispatch
    for the same batch under a different filename must still be refused
    (Task 18a)."""
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    first_out = tmp_path / "dispatch-receipt-first.json"
    assert cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(first_out),
    ]) == 0
    capsys.readouterr()
    second_out = tmp_path / "dispatch-receipt-second.json"
    code, out = _run([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(second_out),
    ])
    capsys.readouterr()
    assert code != 0
    assert out["recorded"] is False
    assert "re-collect" in " ".join(out["reasons"])
    assert not second_out.exists()


def test_apply_result_recovers_reopen_receipt_stuck_after_ledger_crash(
    tmp_path, capsys, monkeypatch,
) -> None:
    """Symmetric with the finalize crash recovery: a crash between the
    reopen ledger CAS write (owner Task 2 -> pending) and the
    dispatch-receipt flip must not strand the receipt either — re-running
    apply-result --receipt must recover the reopen action idempotently
    (Task 18b)."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    receipt_path = tmp_path / "verification-receipt.json"
    result_path = _result_file(tmp_path, reopen=True)
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    assert cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]) == 0
    capsys.readouterr()

    real_write_text = Path.write_text

    def _crash_on_receipt_write(self, *call_args, **call_kwargs):
        if self == dispatch_receipt:
            raise OSError("simulated crash before receipt flip")
        return real_write_text(self, *call_args, **call_kwargs)

    monkeypatch.setattr(Path, "write_text", _crash_on_receipt_write)
    code = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    capsys.readouterr()
    assert code != 0
    plan_after_crash = plan_path.read_text(encoding="utf-8")
    assert f"- **Status**: implemented({sha1})" in plan_after_crash
    task_2_block = plan_after_crash.split("## Task 2")[1].split(
        "## Review Batches"
    )[0]
    assert "- **Status**: pending" in task_2_block
    stored_after_crash = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored_after_crash.get("result_applied", False) is False

    monkeypatch.setattr(Path, "write_text", real_write_text)
    code2 = cli.main([
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(receipt_path),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ])
    out2 = json.loads(capsys.readouterr().out)
    assert code2 == 0
    assert out2["action"] == "reopen"
    assert out2["reopen_owners"] == ["Task 2"]
    assert out2["recovered"] is True
    stored_after_recovery = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored_after_recovery["result_applied"] is True
    assert plan_path.read_text(encoding="utf-8") == plan_after_crash


def test_repository_identity_anchored_on_member_sha_not_head(tmp_path) -> None:
    """_repository_identity must anchor on the member's own commit sha, not
    the repo's current HEAD — otherwise moving HEAD to an unrelated
    second-root branch changes the identity of an already-frozen member
    commit (Task 18c)."""
    repo_root = tmp_path / "repo"
    _init_git_repo(repo_root)
    sha = _git_commit_file(repo_root, "src/1.py", b"member 1")
    baseline = cli._repository_identity(repo_root, sha)

    subprocess.run(
        ["git", "-C", str(repo_root), "checkout", "-q", "--orphan", "second-root"],
        check=True,
    )
    (repo_root / "other.txt").write_bytes(b"unrelated second root")
    subprocess.run(
        ["git", "-C", str(repo_root), "add", "other.txt"], check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_root), "commit", "-q", "-m", "second root"],
        check=True,
    )

    after_head_moved = cli._repository_identity(repo_root, sha)
    assert after_head_moved == baseline


def _recorded_dispatch_receipt(
    tmp_path: Path, plan_path: Path, repo_root: Path, capsys,
) -> Path:
    """packet + record-dispatch for the current plan state; returns the
    dispatch receipt path bound to the members' current shas."""
    receipt_path = tmp_path / "verification-receipt.json"
    packet_file = tmp_path / "packet.json"
    packet_file.write_text(json.dumps(
        _packet_json(plan_path, repo_root, receipt_path, capsys)
    ), encoding="utf-8")
    dispatch_receipt = tmp_path / "dispatch-receipt.json"
    assert cli.main([
        "record-dispatch", "--packet-file", str(packet_file),
        "--out", str(dispatch_receipt),
    ]) == 0
    capsys.readouterr()
    return dispatch_receipt


def _apply_result_argv(
    plan_path: Path, repo_root: Path, tmp_path: Path,
    result_path: Path, dispatch_receipt: Path,
) -> list[str]:
    return [
        "apply-result", "--plan", str(plan_path),
        "--repo-root", str(repo_root),
        "--verification-receipt", str(tmp_path / "verification-receipt.json"),
        "--result-file", str(result_path),
        "--receipt", str(dispatch_receipt),
    ]


def test_apply_result_refuses_when_member_sha_drifted_after_dispatch(
    tmp_path, capsys,
) -> None:
    """F1: the reviewer saw member 2 at commit A (recorded in the dispatch
    receipt's member_shas). Re-pointing the ledger to a later commit B and
    applying the same PASS with the same receipt must refuse — the PASS was
    never given for B — naming the drifted member, with no ledger write and
    no receipt flip."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    dispatch_receipt = _recorded_dispatch_receipt(
        tmp_path, plan_path, repo_root, capsys,
    )
    sha2_b = _git_commit_file(repo_root, "src/2.py", b"member 2 rewritten")
    plan_path.write_text(
        plan_path.read_text(encoding="utf-8").replace(
            f"implemented({sha2})", f"implemented({sha2_b})"
        ),
        encoding="utf-8",
    )
    before = plan_path.read_text(encoding="utf-8")
    result_path = _result_file(tmp_path)
    code = cli.main(_apply_result_argv(
        plan_path, repo_root, tmp_path, result_path, dispatch_receipt,
    ))
    out = json.loads(capsys.readouterr().out)
    assert code != 0
    assert out["action"] is None
    assert "Task 2" in " ".join(out["reasons"])
    assert plan_path.read_text(encoding="utf-8") == before
    stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
    assert stored["result_applied"] is False


def test_apply_result_refuses_receipt_bound_to_another_batch(
    tmp_path, capsys,
) -> None:
    """F6: a receipt whose batch_id / packet_identity belong to another
    batch must not be usable to apply this batch's result, even when its
    member_shas happen to match."""
    plan_path, repo_root, sha1, sha2 = _write_git_workspace(tmp_path)
    before = plan_path.read_text(encoding="utf-8")
    result_path = _result_file(tmp_path)
    for foreign in (
        {"batch_id": "other-capability", "packet_identity": "packet:other"},
        {"batch_id": "capability", "packet_identity": "packet:other"},
    ):
        dispatch_receipt = tmp_path / "foreign-dispatch-receipt.json"
        dispatch_receipt.write_text(json.dumps({
            "schema": "batch-dispatch-receipt-v1",
            **foreign,
            "arms": ["spec-reviewer", "code-quality-reviewer"],
            "members": ["Task 1", "Task 2"],
            "member_shas": {"Task 1": sha1, "Task 2": sha2},
            "result_applied": False,
        }), encoding="utf-8")
        code = cli.main(_apply_result_argv(
            plan_path, repo_root, tmp_path, result_path, dispatch_receipt,
        ))
        out = json.loads(capsys.readouterr().out)
        assert code != 0, foreign
        assert out["action"] is None
        assert plan_path.read_text(encoding="utf-8") == before
        stored = json.loads(dispatch_receipt.read_text(encoding="utf-8"))
        assert stored["result_applied"] is False


def test_apply_result_requires_receipt_flag(tmp_path, capsys) -> None:
    """F3: apply-result without --receipt is an argparse usage error
    (exit 2) — there is nothing to bind the result to."""
    plan_path, repo_root, _sha1, _sha2 = _write_git_workspace(tmp_path)
    result_path = _result_file(tmp_path)
    with pytest.raises(SystemExit) as exc_info:
        cli.main([
            "apply-result", "--plan", str(plan_path),
            "--repo-root", str(repo_root),
            "--verification-receipt", str(tmp_path / "verification-receipt.json"),
            "--result-file", str(result_path),
        ])
    capsys.readouterr()
    assert exc_info.value.code == 2
