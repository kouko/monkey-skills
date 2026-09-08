import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github/workflows/conventional-pr-title.yml"
STRUCTURE_WORKFLOW = ROOT / ".github/workflows/skill-structure.yml"


def conventional_job() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("  conventional-commits:")
    return text[start:]


def run_title_check(title: str) -> subprocess.CompletedProcess:
    match = re.search(r"python3 - <<'PY'\n(?P<body>.*?)\n\s+PY", conventional_job(), re.S)
    assert match
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(match.group("body"))],
        capture_output=True, text=True, env={**os.environ, "PR_TITLE": title},
    )


def test_job_rechecks_when_pr_title_is_edited() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "types: [opened, synchronize, reopened, edited]" in workflow


def test_title_edits_do_not_rerun_the_large_structure_workflow() -> None:
    assert "conventional-commits:" not in STRUCTURE_WORKFLOW.read_text(encoding="utf-8")


def test_job_validates_only_environment_bound_pr_title() -> None:
    job = conventional_job()
    assert "PR_TITLE: ${{ github.event.pull_request.title }}" in job
    assert "actions/checkout" not in job
    assert "git log" not in job
    assert "BASE_SHA" not in job
    assert "HEAD_SHA" not in job


def test_job_keeps_required_check_name_and_useful_errors() -> None:
    job = conventional_job()
    assert "name: Conventional Commits" in job
    assert "Rejected PR title:" in job
    assert "<type>(<scope>): <subject>" in job
    assert "subject ends with a period" in job


def test_title_program_accepts_valid_final_title() -> None:
    result = run_title_check("feat(loom-code): publish once")
    assert result.returncode == 0
    assert "Accepted PR title" in result.stdout


def test_title_program_rejects_missing_scope_and_period() -> None:
    missing_scope = run_title_check("docs: temporary checkpoint")
    trailing_period = run_title_check("docs(loom): final title.")
    assert missing_scope.returncode == 1
    assert "does not match" in missing_scope.stdout
    assert trailing_period.returncode == 1
    assert "subject ends with a period" in trailing_period.stdout
