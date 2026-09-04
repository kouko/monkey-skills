"""RED test: the stale open-questions checker and its references are gone.

Task: W1-01 (change 2026-09-04-checker-seams).
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_check_open_questions_script_absent():
    assert not (REPO_ROOT / "loom-code/scripts/check_open_questions.py").exists()


def test_check_open_questions_test_absent():
    assert not (REPO_ROOT / "loom-code/scripts/test_check_open_questions.py").exists()


def test_no_stale_references_to_check_open_questions():
    result = subprocess.run(
        [
            "git",
            "grep",
            "-n",
            "check_open_questions",
            "--",
            ":!docs/loom",
            ":!*CHANGELOG*",
            ":!loom-code/scripts/test_no_stale_open_questions_script.py",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0, f"stale references found:\n{result.stdout}"


def test_loom_checker_lists_27_rules():
    result = subprocess.run(
        ["python3", "loom-code/scripts/loom_checker.py", "--list-rules"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rule lines, got {len(lines)}:\n{result.stdout}"
