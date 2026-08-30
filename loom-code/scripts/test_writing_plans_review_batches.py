"""Contract tests for writing-plans' second-pass Review Batch authoring."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "writing-plans" / "SKILL.md"
FORMAT = ROOT / "skills" / "writing-plans" / "references" / "plan-format.md"
REVIEWER = (
    ROOT
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)
ORACLE = ROOT / "scripts" / "check_review_batches.py"


def _task(number: int, dependencies: str, disposition: str | None) -> str:
    disposition_line = (
        f"- **Review disposition**: {disposition}\n" if disposition is not None else ""
    )
    return (
        f"## Task {number} — atomic task {number}\n"
        f"- **Dependencies**: {dependencies}\n"
        f"{disposition_line}"
        "- **Status**: pending\n"
    )


def _run_oracle(tmp_path: Path, plan: str) -> subprocess.CompletedProcess[str]:
    plan_path = tmp_path / "plan.md"
    plan_path.write_text(plan, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(ORACLE), str(plan_path)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_second_pass_and_fail_closed_contract():
    """The planner derives review checkpoints only from a completed Task DAG."""
    skill = SKILL.read_text(encoding="utf-8")
    plan_format = FORMAT.read_text(encoding="utf-8")
    reviewer = REVIEWER.read_text(encoding="utf-8")
    combined = "\n".join((skill, plan_format, reviewer))
    flat = " ".join(combined.split()).lower()

    task_pos = skill.index("## Task 1")
    batch_pos = skill.index("## Review Batches")
    assert task_pos < batch_pos, "the copyable plan skeleton must author Tasks before Batches"
    assert "second pass" in flat or "second-pass" in flat
    assert "complete" in flat and "task dag" in flat
    assert "must not merge" in flat or "never merge" in flat

    assert "Review disposition" in plan_format
    assert "individual" in plan_format and "batch(<id>)" in plan_format
    for field in (
        "Review Batch: <id>",
        "Members",
        "Verdict question",
        "Review lane",
        "Aggregate verification",
        "Boundary",
    ):
        assert field in plan_format, f"plan schema is missing {field}"

    for exclusion in (
        "user decision",
        "external wait",
        "deferred test",
        "independent release",
        "failure boundary",
    ):
        assert exclusion in flat, f"eligibility contract is missing {exclusion}"
    assert "same review lane" in flat
    assert "end-to-end" in flat
    assert "closable" in flat
    assert "individual review" in flat
    assert "fail closed" in flat or "fail-closed" in flat

    oracle = "python3 loom-code/scripts/check_review_batches.py <plan-path>"
    assert oracle in skill
    assert skill.count(oracle) == 1, "writing-plans must have one mandatory gate execution point"
    assert oracle in reviewer
    assert "mandatory schema oracle" in flat

    assert "inert" in flat and "Aggregate verification" in combined
    assert "does not execute" in flat or "never executes" in flat
    assert "no batch queue" in flat or "there is no batch queue" in flat
    assert "batch ledger" in flat
    assert "batch lifecycle" in flat


def test_review_batch_oracle_accepts_grouped_and_individual_planner_outputs(tmp_path):
    """The documented new-plan outputs integrate with the mandatory schema oracle."""
    grouped = (
        _task(1, "none", "batch(capability)")
        + "\n"
        + _task(2, "Task 1 completes first", "batch(capability)")
        + "\n## Review Batches\n\n"
        + "### Review Batch: capability\n"
        + "- **Members**: Task 1, Task 2\n"
        + "- **Verdict question**: Does the capability work end to end?\n"
        + "- **Review lane**: full\n"
        + "- **Aggregate verification**: python3 -m pytest tests/test_capability.py -q && echo $?\n"
        + "- **Boundary**: capability: capability path; exclusions: none; consumable: yes\n"
    )
    result = _run_oracle(tmp_path, grouped)
    assert result.returncode == 0, result.stderr
    assert "2 Tasks, 1 Batches" in result.stdout

    fallback = (
        _task(1, "none", "individual")
        + "\n"
        + _task(2, "Task 1 completes first", "individual")
        + "\n## Review Batches\n"
    )
    result = _run_oracle(tmp_path, fallback)
    assert result.returncode == 0, result.stderr
    assert "2 Tasks, 0 Batches" in result.stdout


def test_review_batch_oracle_rejects_new_plan_without_disposition_metadata(tmp_path):
    """A new plan cannot silently inherit the pre-Batch review contract."""
    result = _run_oracle(tmp_path, _task(1, "none", None))
    assert result.returncode == 1
    assert "review disposition" in result.stderr
    assert "Review Batches second-pass section" in result.stderr
