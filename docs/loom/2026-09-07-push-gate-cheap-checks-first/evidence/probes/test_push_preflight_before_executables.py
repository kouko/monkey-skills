"""Adversarial phase-boundary probes for W0-01.

These tests use the push checker's existing real-git fixture.  Executable
commands write only below ``.git`` so their call order is observable without
creating an unrelated working-tree mutation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


SCRIPTS = Path(__file__).resolve().parents[5] / "loom-code" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import test_loom_checker_push as push_fixture  # noqa: E402


def _package_command(label: str, *, exit_code: int = 0, mutate: bool = False) -> str:
    suffix = " mutate" if mutate else ""
    return f"python3 .git/adversary_runner.py {label} {exit_code}{suffix}"


def _adversarial_commands() -> list[str]:
    return [
        f"python3 evidence/abuse_{name}.py adversarial-{index}"
        for index, name in enumerate(push_fixture.ABUSE_CASES, start=1)
    ]


def _review_with_commands(repo: Path, package: str, adversarial: list[str]) -> dict:
    reviewed_sha = push_fixture.git(repo, "rev-parse", "HEAD")
    body = push_fixture.review_body(reviewed_sha)
    body["probes"][0]["command"] = package
    for record, command in zip(body["probes"][1:], adversarial, strict=True):
        record["command"] = command
    return body


def _set_package_default(repo: Path, command: str) -> None:
    push_fixture.git(repo, "reset", "-q", "--hard", "HEAD~1")
    runner = repo / ".git/adversary_runner.py"
    runner.write_text(
        "import subprocess\n"
        "import sys\n"
        "from pathlib import Path\n"
        "Path('.git/execution.log').open('a').write(sys.argv[1] + '\\n')\n"
        "if len(sys.argv) > 3 and sys.argv[3] == 'mutate':\n"
        "    subprocess.run(['git', 'config', 'loom.adversary', 'changed'], check=True)\n"
        "raise SystemExit(int(sys.argv[2]))\n",
        encoding="utf-8",
    )
    for index, name in enumerate(push_fixture.ABUSE_CASES, start=1):
        (repo / f"evidence/abuse_{name}.py").write_text(
            "from pathlib import Path\n"
            f"Path('.git/execution.log').open('a').write('adversarial-{index}\\n')\n",
            encoding="utf-8",
        )
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.write_text(
        "# Kickoff Defaults\n\n"
        f"- package-tests: {command} — adversary fixture (2026-09-07)\n",
        encoding="utf-8",
    )
    push_fixture.git(repo, "add", "docs/loom/KICKOFF-DEFAULTS.md", "evidence")
    push_fixture.git(repo, "commit", "-q", "--amend", "--no-edit")


def _rebuild_checkpoint(repo: Path, body: dict) -> None:
    push_fixture.write_review(repo, body)
    push_fixture.git(repo, "add", push_fixture.REVIEW)
    push_fixture.git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


def _execution_log(repo: Path) -> list[str]:
    path = repo / ".git/execution.log"
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def test_push_lateblocker_noexecutables(tmp_path: Path) -> None:
    """A deterministic dispatch blocker must prevent every executable start."""
    repo = push_fixture.build_repo(tmp_path)
    package = _package_command("package")
    adversarial = _adversarial_commands()
    _set_package_default(repo, package)
    body = _review_with_commands(repo, package, adversarial)
    body["dispatch"][1]["agent_id"] = body["dispatch"][0]["agent_id"]
    body["verdicts"][0]["reviewer"] = body["dispatch"][0]["agent_id"]
    _rebuild_checkpoint(repo, body)

    result = push_fixture.run_checker("push", cwd=repo)

    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in push_fixture.blocked_rules(result)
    assert _execution_log(repo) == [], (
        "deterministic BLOCK was known before execution, but commands started: "
        f"{_execution_log(repo)}"
    )


def test_push_validpath_onceinorder(tmp_path: Path) -> None:
    """A valid push runs package once, then each adversarial probe once."""
    repo = push_fixture.build_repo(tmp_path)
    package = _package_command("package")
    adversarial = _adversarial_commands()
    _set_package_default(repo, package)
    _rebuild_checkpoint(repo, _review_with_commands(repo, package, adversarial))

    result = push_fixture.run_checker("push", cwd=repo)

    assert result.returncode == 0, result.stderr
    assert _execution_log(repo) == [
        "package",
        "adversarial-1",
        "adversarial-2",
        "adversarial-3",
    ]


def test_push_packageskip_adversarialruns(tmp_path: Path) -> None:
    """The explicit package skip still retains all adversarial execution."""
    repo = push_fixture.build_repo(tmp_path)
    package = _package_command("package")
    adversarial = _adversarial_commands()
    _set_package_default(repo, package)
    _rebuild_checkpoint(repo, _review_with_commands(repo, package, adversarial))

    result = push_fixture.run_checker("push", "--skip-package-tests", cwd=repo)

    assert result.returncode == 0, result.stderr
    assert _execution_log(repo) == [
        "adversarial-1",
        "adversarial-2",
        "adversarial-3",
    ]


def test_push_failedmutation_blockpreserved(tmp_path: Path) -> None:
    """A failing executable that mutates Git config preserves both blockers."""
    repo = push_fixture.build_repo(tmp_path)
    package = _package_command("package-failed", exit_code=7, mutate=True)
    adversarial = _adversarial_commands()
    _set_package_default(repo, package)
    _rebuild_checkpoint(repo, _review_with_commands(repo, package, adversarial))

    result = push_fixture.run_checker("push", cwd=repo)

    assert result.returncode == 1
    assert {
        "push.probes-package-tests",
        "push.reviewed-sha",
    }.issubset(push_fixture.blocked_rules(result))
    assert "effective Git config changed" in result.stderr
    assert _execution_log(repo) == [
        "package-failed",
        "adversarial-1",
        "adversarial-2",
        "adversarial-3",
    ]
