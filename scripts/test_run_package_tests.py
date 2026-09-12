"""fix:W1-05 — the package-tests runner runs one pytest session per group."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "scripts" / "run_package_tests.py"
sys.path.insert(0, str(RUNNER.parent))
from run_package_tests import loom_family_commands, split_groups  # noqa: E402


def test_split_groups_separates_on_double_dash() -> None:
    assert split_groups(["a/", "-q", "--then", "b/", "-q"]) == [["a/", "-q"], ["b/", "-q"]]
    assert split_groups(["a/"]) == [["a/"]]
    assert split_groups(["--then", "b/"]) == [["b/"]]


def test_runner_exit_code_is_nonzero_when_a_later_group_fails(tmp_path: Path) -> None:
    ok = tmp_path / "ok"; ok.mkdir()
    (ok / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    bad = tmp_path / "bad"; bad.mkdir()
    (bad / "test_bad.py").write_text("def test_bad():\n    assert False\n")
    good = subprocess.run([sys.executable, str(RUNNER), str(ok), "-q", "-p", "no:cacheprovider"], capture_output=True)
    assert good.returncode == 0, good.stdout
    mixed = subprocess.run([sys.executable, str(RUNNER), str(ok), "-q", "-p", "no:cacheprovider", "--then", str(bad), "-q", "-p", "no:cacheprovider"], capture_output=True)
    assert mixed.returncode != 0


def test_runner_with_no_groups_exits_nonzero() -> None:
    for argv in ([], ["--then"]):
        result = subprocess.run([sys.executable, str(RUNNER), *argv], capture_output=True)
        assert result.returncode == 2, argv


def test_loom_family_only_requires_a_group_name() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--loom-family", "--only"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--only needs a group" in result.stderr


def test_loom_family_preset_covers_every_ci_test_surface() -> None:
    commands = loom_family_commands(REPO, verbosity="-q")
    rendered = [" ".join(command) for command in commands]

    assert any("loom-code/scripts/ scripts/ .claude/hooks/" in command for command in rendered)
    assert any("loom-design/scripts/" in command for command in rendered)
    assert any("loom-workflow/tests/test_cot_explain_scripts.py" in command for command in rendered)
    assert any("loom-workflow/tests/test-privacy-gate-compose-commit.sh" in command for command in rendered)

    expected_skill_dirs = sorted(
        path.as_posix() for path in (REPO / "loom-workflow/skills").glob("*/scripts")
        if any(path.glob("test_*.py"))
    )
    actual_skill_dirs = sorted(
        command[3] for command in commands
        if command[:3] == [sys.executable, "-m", "pytest"]
        and "/loom-workflow/skills/" in command[3]
    )
    assert actual_skill_dirs == expected_skill_dirs


def test_loom_family_preset_discovers_relocated_memory_skill_tests() -> None:
    commands = loom_family_commands(REPO, verbosity="-q")
    rendered = [" ".join(command) for command in commands]
    assert any("loom-workflow/skills/loom-memory/scripts" in command for command in rendered)


def test_relocated_memory_skill_tests_pass_through_the_workflow_python_command() -> None:
    commands = loom_family_commands(REPO, verbosity="-q", only="workflow-python")
    memory_command = next(
        command for command in commands
        if "loom-workflow/skills/loom-memory/scripts" in command[3]
    )
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(memory_command, capture_output=True, text=True, cwd=REPO, env=env)
    assert result.returncode == 0, result.stdout + result.stderr


def test_loom_family_preset_is_the_only_test_command_named_by_ci_and_kickoff() -> None:
    kickoff = (REPO / "docs/loom/KICKOFF-DEFAULTS.md").read_text(encoding="utf-8")
    assert "scripts/run_package_tests.py --loom-family" in kickoff

    for workflow in (
        REPO / ".github/workflows/loom-code-ci.yml",
        REPO / ".github/workflows/loom-design-ci.yml",
        REPO / ".github/workflows/loom-workflow-ci.yml",
    ):
        text = workflow.read_text(encoding="utf-8")
        assert "scripts/run_package_tests.py --loom-family" in text
