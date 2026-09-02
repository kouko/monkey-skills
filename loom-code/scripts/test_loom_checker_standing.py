"""Executable contract for `loom_checker.py standing <intent>` (plan W0-04).

The distinction under test is the one concept-model §8 is built on:
`standing-docs: waived` silences the three-line WARN and NOTHING else --
a product change with no ratified PRINCIPLES.md is still rejected, waiver
or no waiver.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")

INTENT = """# A change
originator: tester
kind: {kind}
needs-design: no — internal only
status: confirmed 2026-09-02

## Problem
People who use the nightly report wait ten minutes and give up.

## Proposed outcome
Make it fast.

## Acceptance
1. After this I can open the report in under a minute.

## Constraints
- Stay inside the existing tool.

## Out of scope
- Everything else.

## Open questions
- None yet.
"""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def make_repo(tmp_path: Path, *, kind: str = "engineering") -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    intent = repo / "docs/loom/intent/2026-09-02-a.md"
    intent.parent.mkdir(parents=True, exist_ok=True)
    intent.write_text(INTENT.format(kind=kind), encoding="utf-8")
    return repo, intent


def add_principles(repo: Path, *, ratified: bool = True) -> None:
    body = "# Principles\n"
    if ratified:
        body += "ratified-by: kouko 2026-09-02\n"
    body += "\n## P1\nShip the smallest thing that helps.\n"
    (repo / "PRINCIPLES.md").write_text(body, encoding="utf-8")


def add_design(repo: Path) -> None:
    (repo / "DESIGN.md").write_text(
        "# Design\nratified-by: kouko 2026-09-02\n", encoding="utf-8"
    )


def waive(repo: Path) -> None:
    path = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Kickoff Defaults\n\n- standing-docs: waived — tiny repo (2026-09-02)\n",
        encoding="utf-8",
    )


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def warn_lines(result: subprocess.CompletedProcess) -> list[str]:
    return [line for line in result.stderr.splitlines() if line.startswith("WARN")]


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


# --- standing.warn ---------------------------------------------------------


def test_missing_standing_docs_warn_in_exactly_three_lines(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr
    assert len(warn_lines(result)) == 3


def test_the_warn_names_what_is_missing(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    add_principles(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    text = "\n".join(warn_lines(result))
    assert "DESIGN.md" in text
    assert "PRINCIPLES.md" not in text


def test_the_warn_wording_is_fixed(tmp_path: Path) -> None:
    first_repo, first_intent = make_repo(tmp_path / "one")
    second_repo, second_intent = make_repo(tmp_path / "two")
    first = warn_lines(run_checker("standing", str(first_intent), cwd=first_repo))
    second = warn_lines(run_checker("standing", str(second_intent), cwd=second_repo))
    assert first == second


def test_a_warn_never_blocks(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    assert run_checker("standing", str(intent), cwd=repo).returncode == 0


def test_no_warn_when_both_documents_exist(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    add_principles(repo)
    add_design(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    assert warn_lines(result) == []
    assert result.returncode == 0


def test_principles_under_docs_loom_also_counts(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    add_design(repo)
    target = repo / "docs/loom/PRINCIPLES.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Principles\nratified-by: kouko 2026-09-02\n", encoding="utf-8")
    result = run_checker("standing", str(intent), cwd=repo)
    assert warn_lines(result) == []


# --- standing.product-principles-reject -----------------------------------


def test_product_without_principles_is_rejected(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="product")
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "standing.product-principles-reject" in blocked_rules(result)


def test_product_with_unratified_principles_is_rejected(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="product")
    add_principles(repo, ratified=False)
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "standing.product-principles-reject" in blocked_rules(result)
    assert "ratified-by" in result.stderr


def test_product_with_ratified_principles_passes(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="product")
    add_principles(repo)
    add_design(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr


def test_engineering_is_never_rejected_for_missing_principles(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="engineering")
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 0
    assert blocked_rules(result) == set()


def test_missing_design_never_rejects(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="product")
    add_principles(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- standing.silence ------------------------------------------------------


def test_waiver_silences_the_warn(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    waive(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    assert warn_lines(result) == []
    assert result.returncode == 0


def test_waiver_does_not_lift_the_product_rejection(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path, kind="product")
    waive(repo)
    result = run_checker("standing", str(intent), cwd=repo)
    assert result.returncode == 1
    assert "standing.product-principles-reject" in blocked_rules(result)
    assert warn_lines(result) == []


def test_an_unrelated_kickoff_key_does_not_silence(tmp_path: Path) -> None:
    repo, intent = make_repo(tmp_path)
    path = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Kickoff Defaults\n\n- second-vendor: none — solo (2026-09-02)\n", encoding="utf-8"
    )
    assert len(warn_lines(run_checker("standing", str(intent), cwd=repo))) == 3


# --- operands --------------------------------------------------------------


def test_a_missing_intent_path_exits_2(tmp_path: Path) -> None:
    repo, _ = make_repo(tmp_path)
    result = run_checker("standing", str(repo / "docs/loom/intent/none.md"), cwd=repo)
    assert result.returncode == 2
