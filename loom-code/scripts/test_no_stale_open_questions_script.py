"""RED test: the stale open-questions checker and its references are gone.

Task: W1-02 (change 2026-09-04-checker-seams), fix round 2. The removed
script's name is assembled from parts at runtime so this file itself
carries no literal occurrence of it — the grep in
`test_no_stale_references_exist` needs no self-exclusion to pass.
"""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_REMOVED_MODULE_NAME = "check_open" + "_questions"
_REMOVED_SCRIPT = f"loom-code/scripts/{_REMOVED_MODULE_NAME}.py"
_REMOVED_SCRIPT_TEST = f"loom-code/scripts/test_{_REMOVED_MODULE_NAME}.py"


def test_removed_script_absent():
    assert not (REPO_ROOT / _REMOVED_SCRIPT).exists()


def test_removed_script_test_absent():
    assert not (REPO_ROOT / _REMOVED_SCRIPT_TEST).exists()


def test_no_stale_references_exist():
    result = subprocess.run(
        [
            "git",
            "grep",
            "-n",
            _REMOVED_MODULE_NAME,
            "--",
            ":!docs/loom",
            ":!*CHANGELOG*",
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
