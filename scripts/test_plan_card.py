"""Tests for scripts/plan_card.py — the plan-progress card renderer.

Task 3 of docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md.
The card body format is pinned ONCE in that plan's N5 block and
implemented ONCE in scripts/plan_card.py — same spec, two surfaces; a
future format change edits both in one commit (plan Decision Log,
2026-08-06).

False-green discipline: every subprocess assertion pins content only a
REAL run produces (exact stdout bytes, or the `plan_card: FAIL —` line
naming the missing field) — never a bare "exit != 0", which a missing
script file also satisfies (exit 2, empty stdout).
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAN_CARD_SCRIPT = REPO_ROOT / "scripts" / "plan_card.py"


def _plan_text(
    *,
    goal: str | None = "Ship the widget pipeline end-to-end.",
    stage: str | None = "sdd:wave-1",
    tasks: list[tuple[str, str | None]] = (),
) -> str:
    """A minimal plan file in the shape writing-plans emits (header lines,
    `## Task N — <name>` headings, per-task `- Status:` bullets), plus a
    trailing non-task `## Notes` section so parsing must stop at section
    boundaries rather than swallowing the whole file."""
    lines = ["# Plan: widget fixture", "", "Source brief: docs/loom/specs/fixture.md"]
    if goal is not None:
        lines.append(f"Goal: {goal}")
    if stage is not None:
        lines.append(f"Stage: {stage}")
    lines.append("")
    for number, (name, status) in enumerate(tasks, start=1):
        lines.append(f"## Task {number} — {name}")
        lines.append("")
        lines.append("- Description: fixture task body.")
        if status is not None:
            lines.append(f"- Status: {status}")
        lines.append("")
    lines.extend(["## Notes", "", "Fixture notes — never a task.", ""])
    return "\n".join(lines)


def _run_card(plan_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLAN_CARD_SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
    )


def _write_plan(tmp_path: Path, text: str) -> Path:
    plan_path = tmp_path / "2026-08-06-fixture-plan.md"
    plan_path.write_text(text, encoding="utf-8")
    return plan_path


def test_happy_path_mixed_statuses_renders_the_exact_card(tmp_path):
    """(1) The full N5-variant field order, byte-exact: goal line, counts
    line, one row per task in file order, stage line, next = first
    not-done task."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                ("parser", "done(abc1234)"),
                ("renderer", "claimed(implementer)"),
                ("cli wiring", "pending"),
                ("docs", "blocked"),
            ]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "🎯 Ship the widget pipeline end-to-end.\n"
        "tasks: ✅1 ⏳1 ⬜1 🚫1\n"
        "✅ T1 parser\n"
        "⏳ T2 renderer\n"
        "⬜ T3 cli wiring\n"
        "🚫 T4 docs\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_all_done_plan_renders_next_close_out(tmp_path):
    """(2) When every task's status is done(...), the next line points at
    close-out, not at any task."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            stage="finishing",
            tasks=[("parser", "done(abc1234)"), ("renderer", "done(def5678)")],
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "🎯 Ship the widget pipeline end-to-end.\n"
        "tasks: ✅2 ⏳0 ⬜0 🚫0\n"
        "✅ T1 parser\n"
        "✅ T2 renderer\n"
        "stage: finishing\n"
        "next: close-out\n"
    )


def test_plan_missing_goal_header_exits_1_naming_goal(tmp_path):
    """(3) No `Goal:` header → exit 1 with a one-line loud message naming
    the missing field; never a partial card."""
    plan_path = _write_plan(
        tmp_path, _plan_text(goal=None, tasks=[("parser", "pending")])
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Goal" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "🎯" not in result.stdout, "must never render a partial card"


def test_plan_missing_stage_header_exits_1_naming_stage(tmp_path):
    """(3b) Same loud-failure contract for the other required header —
    `Stage:` is parsed by its own branch, so it needs its own pin."""
    plan_path = _write_plan(
        tmp_path, _plan_text(stage=None, tasks=[("parser", "pending")])
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Stage" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "🎯" not in result.stdout, "must never render a partial card"


def test_statusless_old_format_plan_exits_1_naming_status(tmp_path):
    """(4) A plan written before the default-on ledger carries Goal/Stage
    and task headings but no `- Status:` bullets — exit 1 naming Status
    (this is the branch the live-run acceptance exercises against THIS
    arc's own plan file)."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(tasks=[("parser", None), ("renderer", None)]),
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Status" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "🎯" not in result.stdout, "must never render a partial card"


def test_plan_with_no_task_headings_exits_1_loudly(tmp_path):
    """(5) Headers present but zero `## Task N — <name>` headings → exit 1
    naming the missing tasks."""
    plan_path = _write_plan(tmp_path, _plan_text(tasks=[]))

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "## Task" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "🎯" not in result.stdout, "must never render a partial card"


def test_bold_status_bullet_renders_same_card_as_plain_style(tmp_path):
    """(7) plan-format.md's per-task schema writes the Status bullet bold
    (`- **Status**: value`) — a schema-conformant plan must render the
    identical card as the plain `- Status:` style. Before the fix,
    _STATUS_BULLET only matched the plain spelling and a bold-style task
    misdiagnosed as an old-format (statusless) plan."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n\n"
        "- Description: fixture task body.\n"
        "- **Status**: done(abc1234)\n\n"
        "## Task 2 — renderer\n\n"
        "- Description: fixture task body.\n"
        "- **Status**: claimed(implementer)\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "🎯 Ship the widget pipeline end-to-end.\n"
        "tasks: ✅1 ⏳1 ⬜0 🚫0\n"
        "✅ T1 parser\n"
        "⏳ T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_status_value_outside_the_four_kinds_exits_1_naming_it(tmp_path):
    """Defensive edge beyond the five pinned cases: a status value that is
    none of done(/claimed(/pending/blocked must fail loud (naming the bogus
    value), never be silently miscounted into a rendered card."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "wip-maybe")])
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "wip-maybe" in result.stdout
    assert "🎯" not in result.stdout, "must never render a partial card"
