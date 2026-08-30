"""New-plan-only intake contract for subagent-driven-development."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
CHECKER = Path(__file__).with_name("check_review_batches.py")
SKILL = ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"
ACTIVE_PLAN = ROOT / "docs/loom/plans/2026-08-30-task-batch-review.md"


def _check(plan: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(plan)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_historical_plan_is_refused(tmp_path: Path) -> None:
    historical = tmp_path / "historical-plan.md"
    historical.write_text(
        """# Historical plan

## Task 1 — Ship one change

- **Dependencies**: none
- **Status**: pending
""",
        encoding="utf-8",
    )

    refused = _check(historical)
    assert refused.returncode == 1
    assert "Review Batches" in refused.stderr
    assert "review disposition" in refused.stderr

    accepted = _check(ACTIVE_PLAN)
    assert accepted.returncode == 0, accepted.stderr
    assert "9 Tasks, 1 Batches" in accepted.stdout

    skill = SKILL.read_text(encoding="utf-8")
    intake_start = skill.index("## Mandatory new-plan intake")
    process_start = skill.index("## Process — per-task triad")
    task_loop_start = skill.index("For each atomic task in the plan:")
    assert intake_start < process_start < task_loop_start

    intake = " ".join(skill[intake_start:process_start].split())
    required_contract = (
        "exact current plan bytes",
        "check_review_batches.py",
        "before any Task claim",
        "implementer dispatch",
        "Packet construction",
        "reviewer dispatch",
        "status mutation",
        "unsupported",
        "zero side effects",
        "missing `## Review Batches`",
        "duplicate",
        "contradictory",
        "dangling",
        "unreadable",
        "non-zero",
        "never infer",
        "individual",
        "checker → trusted projection → Packet → reviewer dispatch",
        "one reviewer fan-out",
        "existing per-Task reviewer loop",
    )
    for phrase in required_contract:
        assert phrase in intake, f"missing intake contract: {phrase}"
