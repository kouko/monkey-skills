"""Tests for `check_contract_citations.py` — see its module docstring for
the protocol-versus-record exemption rule this checker enforces.

The three pass/fail cases below are built entirely on fixtures under
`tmp_path`, never against the live tree — asserting against the live tree
would measure the repo's current state instead of the checker's logic
(plan `docs/loom/plans/2026-08-22-contracts-cite-only-what-ships.md` Task 1
Acceptance).
"""
from __future__ import annotations

from pathlib import Path

from check_contract_citations import (
    classify_citation,
    evaluate,
    extract_docs_candidates,
    scan_repo,
)


def _write_scoped_file(repo_root: Path, rel_path: str, text: str) -> Path:
    path = repo_root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_citation_outside_the_debt_list_fails(tmp_path: Path) -> None:
    _write_scoped_file(
        tmp_path,
        "loom-code/skills/some-skill/SKILL.md",
        "See `docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md` for the rule.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset())
    assert not ok
    assert any("some-skill/SKILL.md" in m for m in messages)


def test_a_listed_violator_passes(tmp_path: Path) -> None:
    rel = "loom-code/skills/some-skill/SKILL.md"
    _write_scoped_file(
        tmp_path,
        rel,
        "See `docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md` for the rule.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset({rel}))
    assert ok, messages


def test_a_listed_file_that_stopped_violating_also_fails(tmp_path: Path) -> None:
    rel = "loom-code/skills/some-skill/SKILL.md"
    _write_scoped_file(
        tmp_path,
        rel,
        "This contract no longer cites anything under docs/.\n",
    )
    actual = scan_repo(tmp_path)
    ok, messages = evaluate(set(actual.keys()), frozenset({rel}))
    assert not ok
    assert any("STALE" in m and rel in m for m in messages)


def test_checker_exits_0_against_the_current_tree() -> None:
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(repo_root / "loom-code/scripts/check_contract_citations.py"),
            "--repo-root",
            str(repo_root),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_store_directory_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/plans/") == "exempt"
    assert classify_citation("docs/loom/memory") == "exempt"
    assert classify_citation("docs/loom/spec/") == "exempt"


def test_protocol_filename_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/PRINCIPLES.md") == "exempt"
    assert classify_citation("docs/loom/backlog/README.md") == "exempt"
    assert classify_citation("docs/loom/spec/MODEL.md") == "exempt"
    assert classify_citation("docs/loom/queue-state.json") == "exempt"


def test_placeholder_shape_citation_is_exempt() -> None:
    assert classify_citation("docs/loom/specs/<date>-<topic>.md") == "exempt"
    assert (
        classify_citation("docs/loom/discovery/<date>-<slug>/evidence.md")
        == "exempt"
    )


def test_dated_record_citation_is_banned() -> None:
    assert (
        classify_citation("docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md")
        == "banned"
    )
    assert (
        classify_citation(
            "docs/loom/memory/a-number-in-prose-needs-a-test-that-recomputes-it.md"
        )
        == "banned"
    )


def test_only_backtick_delimited_candidates_are_extracted() -> None:
    text = "bare docs/loom/specs/2026-01-01-x.md is not a citation, but `docs/loom/specs/2026-01-01-x.md` is.\n"
    assert extract_docs_candidates(text) == [
        "docs/loom/specs/2026-01-01-x.md"
    ]
