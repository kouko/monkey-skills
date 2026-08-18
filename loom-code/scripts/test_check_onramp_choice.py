"""Tests for check_onramp_choice.py — parses a handoff brief's
`## Design-side on-ramp` line (grammar SSOT:
`loom-code/skills/brainstorming/references/handoff-brief-format.md`
`### `## Design-side on-ramp``) and exits non-zero while the on-ramp
fired but was resolved by anything other than an explicit user choice.

Exercised as a CLI subprocess (the actual interface) — same convention
as `test_check_open_questions.py`.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from check_onramp_choice import build_question, resolve

SCRIPT = Path(__file__).parent / "check_onramp_choice.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(brief_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(brief_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_brief(tmp_path: Path, onramp_line: str | None) -> Path:
    brief = tmp_path / "brief.md"
    body = "# Brief: x\n\n"
    if onramp_line is not None:
        body += f"{onramp_line}\n\n"
    body += "## Problem\n\nsome job.\n"
    brief.write_text(body, encoding="utf-8")
    return brief


@pytest.mark.parametrize(
    "onramp_line,expected_exit",
    [
        ("Design-side on-ramp: pending", 2),
        (
            "Design-side on-ramp: offered — direct per repo precedent",
            2,
        ),
        (None, 2),
        (
            "Design-side on-ramp: fired: rows 1,3 — user chose direct",
            0,
        ),
        ("Design-side on-ramp: not fired — increment", 0),
    ],
    ids=["pending", "agent-default", "missing", "user-chose", "not-fired"],
)
def test_fired_without_user_choice_exits_2(tmp_path, onramp_line, expected_exit):
    brief = _write_brief(tmp_path, onramp_line)
    result = _run(brief)
    assert result.returncode == expected_exit, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    if expected_exit == 2:
        assert "user chose <detour|direct>" in result.stderr


@pytest.mark.parametrize(
    "onramp_body,expected_exit",
    [
        ("## Design-side on-ramp\n\npending\n", 2),
        (
            "## Design-side on-ramp\n\nfired: rows 1 — user chose direct\n",
            0,
        ),
    ],
    ids=["heading-pending", "heading-user-chose"],
)
def test_heading_form_locates_value_line(tmp_path, onramp_body, expected_exit):
    brief = tmp_path / "brief.md"
    brief.write_text(f"# Brief: x\n\n{onramp_body}\n## Problem\n\nsome job.\n",
                      encoding="utf-8")
    result = _run(brief)
    assert result.returncode == expected_exit, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_wrapped_blockquote_continuation_line_joined_before_grammar(tmp_path):
    """A soft-wrapped blockquote value — the value's own text continues
    onto a second `>` line, as CommonMark blockquote paragraphs do and
    as the real corpus (docs/loom/specs/2026-08-18-onramp-explicit-
    choice-gate.md) does for its `not fired` reason — must be joined
    into one value before the strict grammar is applied. Without the
    join, `user chose\\n> direct` truncates to `user chose`, which
    fails the grammar and wrongly reports unresolved."""
    brief = tmp_path / "brief.md"
    brief.write_text(
        "# Brief: x\n\n"
        "> Design-side on-ramp: fired: rows 1,3 — user chose\n"
        "> direct\n\n"
        "## Problem\n\nsome job.\n",
        encoding="utf-8",
    )
    result = _run(brief)
    assert result.returncode == 0, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_missing_brief_file_exits_1(tmp_path):
    result = _run(tmp_path / "does-not-exist.md")
    assert result.returncode == 1
    assert "not found" in result.stderr.lower()


def test_stderr_names_brief_path_on_unresolved(tmp_path):
    brief = _write_brief(tmp_path, "Design-side on-ramp: pending")
    result = _run(brief)
    assert result.returncode == 2
    assert str(brief) in result.stderr


def test_standing_choice_in_direction_resolves_listed_rows(tmp_path):
    """`load_standing` wiring: a `standing` on-ramp line resolves only
    when every cited row has a matching entry under DIRECTION.md's
    `## On-ramp standing choices` heading. Also covers the
    default-resolution path (`--repo-root` omitted, resolved via `git
    rev-parse --show-toplevel` from the brief's directory)."""
    direction_dir = tmp_path / "docs" / "loom"
    direction_dir.mkdir(parents=True)
    (direction_dir / "DIRECTION.md").write_text(
        "## On-ramp standing choices\n\n"
        "- row 1 (product-principles): standing direct — x (2026-08-18)\n",
        encoding="utf-8",
    )

    brief_ok = _write_brief(
        tmp_path,
        "Design-side on-ramp: fired: rows 1 — standing direct (DIRECTION.md)",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(brief_ok), "--repo-root", str(tmp_path)],
        capture_output=True, text=True, env=_ENV,
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    brief_extra_row = _write_brief(
        tmp_path,
        "Design-side on-ramp: fired: rows 1,3 — standing direct (DIRECTION.md)",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(brief_extra_row), "--repo-root", str(tmp_path)],
        capture_output=True, text=True, env=_ENV,
    )
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"
    assert "row 3" in result.stderr

    no_direction_root = tmp_path / "no-direction"
    no_direction_root.mkdir()
    brief_no_direction = _write_brief(
        no_direction_root,
        "Design-side on-ramp: fired: rows 1 — standing direct (DIRECTION.md)",
    )
    result = subprocess.run(
        [
            sys.executable, str(SCRIPT), str(brief_no_direction),
            "--repo-root", str(no_direction_root),
        ],
        capture_output=True, text=True, env=_ENV,
    )
    assert result.returncode == 2, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    # Default-resolution path: no `--repo-root`, resolved via `git
    # rev-parse --show-toplevel` of a real git-inited tmp repo.
    git_repo = tmp_path / "git-repo"
    git_repo.mkdir()
    subprocess.run(["git", "init"], cwd=git_repo, capture_output=True,
                    text=True, check=True)
    git_direction_dir = git_repo / "docs" / "loom"
    git_direction_dir.mkdir(parents=True)
    (git_direction_dir / "DIRECTION.md").write_text(
        "## On-ramp standing choices\n\n"
        "- row 1 (product-principles): standing direct — x (2026-08-18)\n",
        encoding="utf-8",
    )
    brief_git = _write_brief(
        git_repo,
        "Design-side on-ramp: fired: rows 1 — standing direct (DIRECTION.md)",
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(brief_git)],
        capture_output=True, text=True, env=_ENV,
    )
    assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"


def test_resolve_sets_missing_rows_for_standing_form():
    """`resolve()` itself knows which cited rows lack a standing entry —
    `main()` must not re-derive this by regex-matching the message."""
    brief_text = (
        "# Brief: x\n\n"
        "Design-side on-ramp: fired: rows 1,3 — standing direct "
        "(DIRECTION.md)\n\n"
        "## Problem\n\nsome job.\n"
    )
    result = resolve(brief_text, {1: "direct"})
    assert result.status == "unresolved"
    assert result.missing_rows == [3]


def test_resolve_missing_rows_empty_for_non_standing_forms():
    result = resolve(
        "# Brief: x\n\nDesign-side on-ramp: pending\n\n## Problem\n\nx.\n",
        {},
    )
    assert result.missing_rows == []


def test_build_question_names_missing_standing_row():
    brief_text = (
        "# Brief: x\n\n"
        "Design-side on-ramp: fired: rows 1,3 — standing direct "
        "(DIRECTION.md)\n\n"
        "## Problem\n\nsome job.\n"
    )
    result = resolve(brief_text, {1: "direct"})
    question = build_question(result)
    assert "row 3" in question


def test_real_spec_document_exits_0():
    repo_root = Path(__file__).resolve().parents[2]
    spec_path = (
        repo_root / "docs" / "loom" / "specs"
        / "2026-08-18-onramp-explicit-choice-gate.md"
    )
    assert spec_path.is_file(), f"fixture spec missing at {spec_path}"
    result = _run(spec_path)
    assert result.returncode == 0, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
