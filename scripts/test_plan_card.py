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
    tasks: list[tuple] = (),
    steps: list[str] | None = None,
) -> str:
    """A minimal plan file in the shape writing-plans emits (header lines,
    `## Task N — <name>` headings, per-task `- Status:` bullets), plus a
    trailing non-task `## Notes` section so parsing must stop at section
    boundaries rather than swallowing the whole file.

    Each task is (name, status) or (name, status, extra_bullet_lines) —
    the third element carries roadmap-arc bullets (`- Dependencies:`,
    `- Gloss:`) verbatim. `steps` adds the optional header `Steps:`
    block (numbered lines, two-space indent)."""
    lines = ["# Plan: widget fixture", "", "Source brief: docs/loom/specs/fixture.md"]
    if goal is not None:
        lines.append(f"Goal: {goal}")
    if stage is not None:
        lines.append(f"Stage: {stage}")
    if steps is not None:
        lines.append("Steps:")
        lines.extend(f"  {i}. {title}" for i, title in enumerate(steps, start=1))
    lines.append("")
    for number, task in enumerate(tasks, start=1):
        name, status, *rest = task
        extra_bullets = rest[0] if rest else []
        lines.append(f"## Task {number} — {name}")
        lines.append("")
        lines.append("- Description: fixture task body.")
        if status is not None:
            lines.append(f"- Status: {status}")
        lines.extend(extra_bullets)
        lines.append("")
    lines.extend(["## Notes", "", "Fixture notes — never a task.", ""])
    return "\n".join(lines)


def _run_card(plan_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PLAN_CARD_SCRIPT), str(plan_path), *extra_args],
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
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 1 pending / 1 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
        "[ ] T3 cli wiring\n"
        "[!] T4 docs\n"
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
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 2 done / 0 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[v] T2 renderer\n"
        "stage: finishing\n"
        "next: close-out\n"
    )


def test_next_follows_roadmap_order_not_file_order(tmp_path):
    """`next:` names the first not-done task in ROADMAP order (earliest
    dependency level, then file order within that level) — not the
    first not-done task in raw file order. Task 1 is written first in
    the file but depends on Task 2 (so it sits at level 2); Task 2 has
    no dependencies (level 1). The level-1 task is the true next step —
    naming Task 1 would tell the user to start on blocked work."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                (
                    "first-in-file",
                    "pending",
                    ["- Dependencies: Task 2 completes first"],
                ),
                ("second-in-file", "pending"),
            ]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "next: T2 second-in-file\n" in result.stdout, result.stdout


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
    assert "goal:" not in result.stdout, "must never render a partial card"


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
    assert "goal:" not in result.stdout, "must never render a partial card"


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
    assert "goal:" not in result.stdout, "must never render a partial card"


def test_plan_with_no_task_headings_exits_1_loudly(tmp_path):
    """(5) Headers present but zero `## Task N — <name>` headings → exit 1
    naming the missing tasks."""
    plan_path = _write_plan(tmp_path, _plan_text(tasks=[]))

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "## Task" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "goal:" not in result.stdout, "must never render a partial card"


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
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
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
    assert "goal:" not in result.stdout, "must never render a partial card"


# --- roadmap view: steps, glosses, --detail ---------------------------------
# Task 1 of docs/loom/plans/2026-08-06-progress-card-roadmap-view.md.


def test_titled_steps_with_glosses_render_the_exact_stepped_card(tmp_path):
    """Dependencies + a `Steps:` block + Gloss lines (plain and bold
    spelling — the regex mirrors _STATUS_BULLET's bold tolerance) render
    the A-layout byte-exact: titled separators directly above each
    level's rows with NO blank lines anywhere, the needs-list on the
    dependent level, and six-space gloss lines under their task rows."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                (
                    "parser",
                    "done(abc1234)",
                    ["- Gloss: turns the plan file into data the card can trust"],
                ),
                ("renderer", "pending"),
                (
                    "cli wiring",
                    "pending",
                    [
                        "- Dependencies: Tasks 1, 2 complete first",
                        "- **Gloss**: 讓卡片直接在終端機看得懂",
                    ],
                ),
            ],
            steps=["parse layer", "error handling"],
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 2 pending / 0 blocked\n"
        "-- step 1: parse layer --\n"
        "[v] T1 parser\n"
        "      turns the plan file into data the card can trust\n"
        "[ ] T2 renderer\n"
        "-- step 2: error handling (needs: T1 T2) --\n"
        "[ ] T3 cli wiring\n"
        "      讓卡片直接在終端機看得懂\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_deps_without_steps_render_untitled_separators(tmp_path):
    """A plan with Dependencies but no `Steps:` block steps its rows under
    untitled separators — `-- step <L> --`, needs-list inserted before
    the trailing `--` (plan spec's untitled example)."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                ("parser", "done(abc1234)"),
                (
                    "renderer",
                    "pending",
                    ["- Dependencies: Task 1 completes first"],
                ),
            ]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1 --\n"
        "[v] T1 parser\n"
        "-- step 2 (needs: T1) --\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_needs_list_sorts_ascending_and_parallel_form_parses(tmp_path):
    """The `Tasks <n>, <n>... parallel` grammar form is a prerequisite
    list identical to `complete first`, and the needs-list renders
    ascending by task number regardless of the order the plan wrote.

    Task numbers are 100/200/300 (not 1/2/3) deliberately: with small
    consecutive ints, CPython's set-iteration bucket order (bucket =
    hash(n) % table_size) happens to come out ascending even WITHOUT a
    sorted() call, so a `sorted(...)` -> `set(...)` mutation would
    still pass a 1/2/3 fixture — a false green. 100/200/300 collide in
    the small hash table (100 % 8 == 300 % 8 == 4) and are inserted out
    of order (300, 100, 200 per the Dependencies value below), so their
    raw set-iteration order is NOT ascending — only an actual sort
    produces "T100 T200 T300"."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 100 — parser\n\n"
            "- Description: fixture task body.\n"
            "- Status: done(abc1234)\n\n"
            "## Task 200 — renderer\n\n"
            "- Description: fixture task body.\n"
            "- Status: done(def5678)\n\n"
            "## Task 300 — docs\n\n"
            "- Description: fixture task body.\n"
            "- Status: done(fed9876)\n\n"
            "## Task 400 — cli wiring\n\n"
            "- Description: fixture task body.\n"
            "- Status: pending\n"
            "- Dependencies: Tasks 300, 100, 200 parallel\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 3 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1 --\n"
        "[v] T100 parser\n"
        "[v] T200 renderer\n"
        "[v] T300 docs\n"
        "-- step 2 (needs: T100 T200 T300) --\n"
        "[ ] T400 cli wiring\n"
        "stage: sdd:wave-1\n"
        "next: T400 cli wiring\n"
    )


def test_depless_glossless_plan_output_byte_identical_to_flat_card(tmp_path):
    """Backward compat (plan Decision Log 2026-08-06): a plan whose tasks
    all omit Dependencies and Gloss keeps the pre-roadmap flat card —
    byte-identical, no separators. Reuses the original fixture shape."""
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
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 1 pending / 1 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
        "[ ] T3 cli wiring\n"
        "[!] T4 docs\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_all_none_deps_without_steps_render_flat_no_separator(tmp_path):
    """Backward compat, explicit spelling: tasks that DECLARE
    `- Dependencies: none` (one derived level) still render the flat
    card with no separator — stepping is opted into by real deps or a
    `Steps:` block, never by the word none."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                ("parser", "done(abc1234)", ["- Dependencies: none"]),
                ("renderer", "pending", ["- Dependencies: none"]),
            ]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_all_none_deps_with_declared_one_line_steps_renders_titled_step(tmp_path):
    """Steps-opt-in exception (plan Decision Log 2026-08-06): an all-none
    plan that DECLARES a one-line `Steps:` block renders the single
    titled separator — declaring a title is an explicit request to see
    it. No needs-list (step 1 has no prerequisites)."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                ("parser", "done(abc1234)", ["- Dependencies: none"]),
                ("renderer", "pending", ["- Dependencies: none"]),
            ],
            steps=["single wave"],
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "goal: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1: single wave --\n"
        "[v] T1 parser\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
    )


def test_steps_count_mismatch_exits_1_loudly(tmp_path):
    """A declared `Steps:` block whose title count differs from the
    derived level count → exit 1 loud naming both counts; never a card
    with misattached titles."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[("parser", "pending"), ("renderer", "pending")],
            steps=["parse layer", "error handling"],
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Steps" in result.stdout
    assert "2" in result.stdout and "1" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "goal:" not in result.stdout, "must never render a partial card"


def test_inline_steps_declaration_fails_loud(tmp_path):
    """Task 2 of
    docs/loom/plans/2026-08-06-ledger-writer-and-plan-tooling-hardening.md:
    a header `Steps:` line with content after the colon (the inline form
    the 0.62.0 plan's author actually wrote) → exit 1 loud, with a
    message naming the correct format — a bare `Steps:` line followed by
    indented numbered titles. Before the fix, _parse_steps silently
    ignored the line and rendered a titleless card at exit 0."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n"
        "Steps: 核心條款 / 鄰居同步 / 版本收束\n\n"
        "## Task 1 — parser\n\n"
        "- Description: fixture task body.\n"
        "- Status: pending\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Steps" in result.stdout
    assert "bare" in result.stdout, "message must name the bare-line form"
    assert "numbered" in result.stdout, (
        "message must name the indented numbered-titles form"
    )
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "goal:" not in result.stdout, "must never render a partial card"


def test_steps_mention_in_task_prose_does_not_trigger_inline_guard(tmp_path):
    """Scope pin for the inline-Steps guard: a column-0 `Steps: ...` line
    inside a section AFTER the first `## ` heading (task-block / prose
    territory) is content, not a header declaration — the plan still
    renders its flat card at exit 0. The guard is bounded to the
    pre-first-`## ` header region, exactly like _parse_steps; a naive
    whole-file scan would wrongly fail this plan."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n\n"
        "- Description: fixture task body.\n"
        "- Status: pending\n\n"
        "## Notes\n\n"
        "Steps: a / b / c — a prose mention, never a declaration.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "goal: Ship the widget pipeline end-to-end.\n" in result.stdout
    assert "[ ] T1 parser\n" in result.stdout


def test_dependency_cycle_exits_1_naming_the_cycle(tmp_path):
    """T1 needs T2 and T2 needs T1 → no topological order exists; exit 1
    loud naming the cycle's tasks, never a hang or a partial card."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[
                ("parser", "pending", ["- Dependencies: Task 2 completes first"]),
                ("renderer", "pending", ["- Dependencies: Task 1 completes first"]),
            ]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "cycle" in result.stdout
    assert "T1" in result.stdout and "T2" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "goal:" not in result.stdout, "must never render a partial card"


def test_dependency_on_nonexistent_task_exits_1_naming_it(tmp_path):
    """A `Dependencies:` reference to a task number with no heading →
    exit 1 loud naming the phantom task."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(
            tasks=[("parser", "pending", ["- Dependencies: Task 5 completes first"])]
        ),
    )

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "T5" in result.stdout
    assert "nonexistent" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "goal:" not in result.stdout, "must never render a partial card"


def _detail_fixture_text() -> str:
    """A task block carrying every --detail field, with wrapped bullet
    lines so the transcription must fold continuations."""
    return (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n\n"
        "- Description: Extend the parser so wrapped bullet lines\n"
        "  fold into one value.\n"
        "- Acceptance:\n"
        "  - RED: new tests fail against current code.\n"
        "  - GREEN: `python3 -m pytest scripts/ -q` green; live run\n"
        "    renders the fixture plan.\n"
        "- Dependencies: none\n"
        "- Status: pending\n"
        "- Brief item covered: Smallest End State 1\n"
        "- Gloss: 使用者能一眼看懂 parser 的效果\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )


def test_detail_prints_one_tasks_fields_verbatim(tmp_path):
    """`--detail T<N>` (plan path first) prints the task line then
    description / why (brief item) / acceptance (RED+GREEN indented) /
    gloss, each transcribed from the task block with wrapped lines
    folded."""
    plan_path = _write_plan(tmp_path, _detail_fixture_text())

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser so wrapped bullet lines fold into one value.\n"
        "why (brief item): Smallest End State 1\n"
        "acceptance:\n"
        "  RED: new tests fail against current code.\n"
        "  GREEN: `python3 -m pytest scripts/ -q` green; live run renders the fixture plan.\n"
        "gloss: 使用者能一眼看懂 parser 的效果\n"
    )


def test_detail_omits_absent_fields(tmp_path):
    """--detail on a task with only Description + Status prints the task
    line and description — no empty why/acceptance/gloss placeholders."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "pending")])
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: fixture task body.\n"
    )


def test_detail_unknown_task_number_exits_1_naming_it(tmp_path):
    """--detail with a task number the plan has no heading for → exit 1
    loud naming the requested task."""
    plan_path = _write_plan(tmp_path, _detail_fixture_text())

    result = _run_card(plan_path, "--detail", "T9")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "T9" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"


# --- ledger writer: --set-status --------------------------------------------
# Task 1 of docs/loom/plans/2026-08-06-ledger-writer-and-plan-tooling-hardening.md.
# Status grammar (brief Smallest End State 1): exactly
# pending | claimed(@<agent>) | done(<sha>) | blocked — parenthetical
# REQUIRED for claimed/done, FORBIDDEN for pending/blocked.


def test_set_status_rewrites_in_place(tmp_path):
    """Happy path, done kind: `--set-status "T1=done(<sha>)"` rewrites the
    task's `- Status:` line (here directly after the heading — the real
    plans' dominant layout) in place, exits 0, and prints the old line
    then the new line. The file's only change is that one line."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n"
        "- Status: pending\n"
        "- Description: fixture task body.\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=done(abc1234)")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: - Status: pending\n"
        "new: - Status: done(abc1234)\n"
    )
    assert plan_path.read_text(encoding="utf-8") == text.replace(
        "- Status: pending", "- Status: done(abc1234)"
    )


def test_set_status_preserves_bold_field_markup(tmp_path):
    """(F1, whole-branch review fix round) plan-format.md's per-task
    schema writes the Status bullet bold (`- **Status**: value`) — the
    writer must PRESERVE that markup on rewrite, not silently de-bold a
    schema-conformant line. Before the fix, set_status always emitted
    the plain `- Status:` prefix regardless of the matched line's own
    markup; a bold-style plan lost its bold on the very first flip."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n"
        "- **Status**: pending\n"
        "- Description: fixture task body.\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=done(abc1234)")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: - **Status**: pending\n"
        "new: - **Status**: done(abc1234)\n"
    )
    assert plan_path.read_text(encoding="utf-8") == text.replace(
        "- **Status**: pending", "- **Status**: done(abc1234)"
    )


def test_set_status_pending_kind(tmp_path):
    """pending kind (bare word, no parenthetical) rewrites a done task
    back to pending."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "done(abc1234)")])
    )

    result = _run_card(plan_path, "--set-status", "T1=pending")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: - Status: done(abc1234)\n"
        "new: - Status: pending\n"
    )
    assert "- Status: pending" in plan_path.read_text(encoding="utf-8")


def test_set_status_claimed_kind(tmp_path):
    """claimed kind with its REQUIRED `(@<agent>)` parenthetical."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "pending")])
    )

    result = _run_card(plan_path, "--set-status", "T1=claimed(@implementer)")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: - Status: pending\n"
        "new: - Status: claimed(@implementer)\n"
    )
    assert "- Status: claimed(@implementer)" in plan_path.read_text(
        encoding="utf-8"
    )


def test_set_status_blocked_kind(tmp_path):
    """blocked kind (bare word — the writer's grammar FORBIDS a
    parenthetical here, unlike the renderer's blocked(<why>) tolerance)."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "claimed(@implementer)")])
    )

    result = _run_card(plan_path, "--set-status", "T1=blocked")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: - Status: claimed(@implementer)\n"
        "new: - Status: blocked\n"
    )
    assert "- Status: blocked" in plan_path.read_text(encoding="utf-8")


def test_set_status_task_not_found_exits_1_naming_it(tmp_path):
    """A task number with no `## Task <N>` heading → exit 1 loud naming
    the missing heading; the file is not modified."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T9=blocked")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "T9" in result.stdout
    assert "heading" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_wrong_kind_exits_1_naming_the_value(tmp_path):
    """Malformed status, wrong kind: a value outside the four kinds →
    exit 1 loud naming the bogus value; file untouched."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=wip-maybe")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "'wip-maybe'" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_missing_required_parenthetical_exits_1(tmp_path):
    """Malformed status, missing REQUIRED parenthetical: bare `done` →
    exit 1 loud naming the value and the parenthetical rule."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=done")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "'done'" in result.stdout
    assert "parenthetical" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_forbidden_parenthetical_exits_1(tmp_path):
    """Malformed status, FORBIDDEN parenthetical: `pending(oops)` →
    exit 1 loud naming the value and the parenthetical rule."""
    text = _plan_text(tasks=[("parser", "done(abc1234)")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=pending(oops)")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "'pending(oops)'" in result.stdout
    assert "parenthetical" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_zero_status_lines_exits_1(tmp_path):
    """A task block with no `- Status:` line at all → exit 1 loud naming
    the absence (nothing to rewrite; the writer never inserts)."""
    text = _plan_text(tasks=[("parser", None)])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=blocked")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "no '- Status:'" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_duplicate_status_lines_exits_1(tmp_path):
    """More than one `- Status:` line in the task block (the 0.62.0
    duplicate-field incident) → exit 1 loud; the writer refuses rather
    than repairs, and the file is untouched."""
    text = _plan_text(tasks=[("parser", "pending", ["- Status: pending"])])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=done(abc1234)")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "2 '- Status:' lines" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_rewrites_after_gloss_and_after_heading_layouts(tmp_path):
    """Positional tolerance mirroring the real plans' two layouts: T1's
    Status sits directly after its heading, T2's sits after its Gloss
    bullet — both rewrite in place, wherever the line sits in the block."""
    text = (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n"
        "- Status: pending\n"
        "- Description: fixture task body.\n\n"
        "## Task 2 — renderer\n"
        "- Description: fixture task body.\n"
        "- Gloss: 讓卡片直接在終端機看得懂\n"
        "- Status: pending\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )
    plan_path = _write_plan(tmp_path, text)

    first = _run_card(plan_path, "--set-status", "T1=done(abc1234)")
    second = _run_card(plan_path, "--set-status", "T2=claimed(@implementer)")

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert plan_path.read_text(encoding="utf-8") == (
        "# Plan: widget fixture\n\n"
        "Source brief: docs/loom/specs/fixture.md\n"
        "Goal: Ship the widget pipeline end-to-end.\n"
        "Stage: sdd:wave-1\n\n"
        "## Task 1 — parser\n"
        "- Status: done(abc1234)\n"
        "- Description: fixture task body.\n\n"
        "## Task 2 — renderer\n"
        "- Description: fixture task body.\n"
        "- Gloss: 讓卡片直接在終端機看得懂\n"
        "- Status: claimed(@implementer)\n\n"
        "## Notes\n\nFixture notes — never a task.\n"
    )


def test_set_status_file_byte_identical_outside_the_one_line(tmp_path):
    """Full before/after equality modulo the single rewritten line: on a
    multi-task plan, exactly ONE line differs after the flip, and every
    other line — other tasks' Status lines included — is byte-identical."""
    text = _plan_text(
        tasks=[
            ("parser", "done(abc1234)"),
            ("renderer", "pending", ["- Dependencies: Task 1 completes first"]),
            ("docs", "blocked"),
        ]
    )
    plan_path = _write_plan(tmp_path, text)
    before_lines = text.splitlines(keepends=True)

    result = _run_card(plan_path, "--set-status", "T2=claimed(@implementer)")

    assert result.returncode == 0, result.stdout + result.stderr
    after_lines = plan_path.read_text(encoding="utf-8").splitlines(keepends=True)
    assert len(after_lines) == len(before_lines)
    diffs = [
        i for i, (b, a) in enumerate(zip(before_lines, after_lines)) if b != a
    ]
    assert len(diffs) == 1, f"exactly one line may change, got {diffs}"
    assert before_lines[diffs[0]] == "- Status: pending\n"
    assert after_lines[diffs[0]] == "- Status: claimed(@implementer)\n"


def test_set_status_claimed_without_at_sign_exits_1(tmp_path):
    """(F2 axis 1, whole-branch review fix round) `claimed(implementer)`
    — missing the REQUIRED `@` sigil — must be refused. This test's RED
    is only against a WEAKENED grammar: the current
    `_SET_STATUS_GRAMMAR` already requires `claimed(@<agent>)`, so this
    assertion PASSES against current code unchanged; it pins that a
    future loosened grammar (dropping the `@` requirement) cannot
    silently regress this axis."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=claimed(implementer)")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "'claimed(implementer)'" in result.stdout
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_blocked_with_parenthetical_exits_1(tmp_path):
    """(F2 axis 2, whole-branch review fix round) `blocked(why)` — the
    writer's grammar FORBIDS a parenthetical on blocked, unlike the
    renderer's `blocked(<why>)` tolerance. This test's RED is only
    against a WEAKENED grammar: the current `_SET_STATUS_GRAMMAR`
    already excludes it, so this assertion PASSES against current code
    unchanged; it pins that a future loosened grammar cannot silently
    accept the renderer's tolerant form on the writer side."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=blocked(why)")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "'blocked(why)'" in result.stdout
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_and_detail_are_mutually_exclusive(tmp_path):
    """Passing both --detail and --set-status → usage error (exit 2) whose
    message names both flags; the file is not modified."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(
        plan_path, "--detail", "T1", "--set-status", "T1=blocked"
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "--set-status" in result.stderr
    assert "--detail" in result.stderr
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"
