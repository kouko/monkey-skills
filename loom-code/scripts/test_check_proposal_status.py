"""Tests for check_proposal_status.py — refuses a plan whose source
proposal carries a non-ratified `Status:` line (repair R2).

Exercised as a CLI subprocess (the actual interface) — same convention
as `test_check_onramp_choice.py`.

Stdlib only (subprocess + pathlib).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "check_proposal_status.py"

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _run(proposal_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(proposal_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


def _write_proposal(tmp_path: Path, status_line: str | None) -> Path:
    proposal = tmp_path / "proposal.md"
    body = "# Some proposal\n\n"
    if status_line is not None:
        body += f"{status_line}\n\n"
    body += "## USM backbone\n\nsome content.\n"
    proposal.write_text(body, encoding="utf-8")
    return proposal


@pytest.mark.parametrize(
    "status_line,expected_exit",
    [
        ("Status: exploration", 2),
        ("Status: draft", 2),
        (None, 2),
        ("Status: ratified — kouko, 2026-08-31", 0),
        ("Status: ratified", 2),
        ("Status: ratified - kouko, 2026-08-31", 2),
    ],
    ids=[
        "exploration",
        "draft",
        "missing",
        "ratified",
        "ratified-bare",
        "ratified-hyphen",
    ],
)
def test_non_ratified_status_exits_2(tmp_path, status_line, expected_exit):
    proposal = _write_proposal(tmp_path, status_line)
    result = _run(proposal)
    assert result.returncode == expected_exit, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    if expected_exit == 2:
        assert "Status" in result.stderr


def test_missing_proposal_file_exits_1(tmp_path):
    result = _run(tmp_path / "does-not-exist.md")
    assert result.returncode == 1
    assert "not found" in result.stderr


def test_real_outcome_map_v3_proposal_resolves(tmp_path):
    """The real-world green case: docs/loom/outcome-map-v3/proposal.md
    was ratified by Task 1 of this same arc."""
    repo_root = Path(__file__).resolve().parents[2]
    proposal = repo_root / "docs" / "loom" / "outcome-map-v3" / "proposal.md"
    result = _run(proposal)
    assert result.returncode == 0, (
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
