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

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

# The script under test ships beside this file in loom-code/scripts/
# (inside the plugin — Task 1 of
# docs/loom/plans/2026-08-10-ship-progress-tooling.md).
PLAN_CARD_SCRIPT = Path(__file__).resolve().parent / "plan_card.py"

# Direct import (not subprocess) so the fix-round ordering test below can
# monkeypatch build_card — a subprocess call cannot be monkeypatched.
_SPEC = importlib.util.spec_from_file_location("plan_card", PLAN_CARD_SCRIPT)
plan_card = importlib.util.module_from_spec(_SPEC)
sys.modules["plan_card"] = plan_card
_SPEC.loader.exec_module(plan_card)

import loom_gate_markers


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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 1 pending / 1 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
        "[ ] T3 cli wiring\n"
        "[!] T4 docs\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
    )


def test_card_labels_the_goal_field_end_state(tmp_path):
    """The rendered card's first line names the field `end-state:`, not
    `goal:` — the plan schema field keeps the name `Goal:`, only the
    rendered label changes (collision with the host's built-in `/goal`
    session-scoped directive; `end-state:` names the field's own
    provenance per plan-format.md's Smallest End State)."""
    plan_path = _write_plan(tmp_path, _plan_text(tasks=[("parser", "pending")]))

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    first_line = result.stdout.splitlines()[0]
    assert first_line.startswith("end-state: "), first_line
    assert not any(line.startswith("goal: ") for line in result.stdout.splitlines())


def test_card_renders_safety_bearing_header_and_na_when_absent(tmp_path):
    """(Task 6) An optional `Safety-bearing: yes|no — <reason>` header
    line renders on the card as `safety-bearing: <value>` verbatim; its
    absence renders `safety-bearing: N/A — header absent` (every other
    existing fixture in this file omits the header and already pins
    this N/A line). A value outside the `yes — `/`no — ` grammar raises
    ValueError naming the accepted forms, and the pure `safety_bearing()`
    helper (Task 10's consumer) returns the parsed (kind, reason) pair."""
    text = _plan_text(tasks=[("parser", "pending")])
    text = text.replace(
        "Stage: sdd:wave-1\n",
        "Stage: sdd:wave-1\nSafety-bearing: yes — touches git-guard\n",
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "safety-bearing: yes — touches git-guard\n" in result.stdout
    assert plan_card.safety_bearing(text) == ("yes", "touches git-guard")

    absent_dir = tmp_path / "absent"
    absent_dir.mkdir()
    absent_text = _plan_text(tasks=[("parser", "pending")])
    absent_plan_path = _write_plan(absent_dir, absent_text)

    absent_result = _run_card(absent_plan_path)

    assert absent_result.returncode == 0, absent_result.stdout + absent_result.stderr
    assert "safety-bearing: N/A — header absent\n" in absent_result.stdout
    assert plan_card.safety_bearing(absent_text) is None

    with pytest.raises(ValueError, match="Safety-bearing"):
        plan_card.safety_bearing(
            absent_text.replace("Stage: sdd:wave-1\n", "Stage: sdd:wave-1\nSafety-bearing: maybe\n")
        )


def test_safety_bearing_line_outside_header_or_miscased_fails_loud(tmp_path):
    """(review-driven fix, live adversarial audit) A `Safety-bearing:`
    line written OUTSIDE the header block (e.g. under a later `## `
    section) or with a miscased key inside the header block must never
    silently render `safety-bearing: N/A — header absent` at exit 0 —
    that is a self-exemption vector for a safety-relevant field. Both
    forms fail loud, naming the offending line, from both the CLI card
    render and the pure `safety_bearing()` helper directly."""
    misplaced_text = _plan_text(tasks=[("parser", "pending")]).replace(
        "## Notes\n\nFixture notes — never a task.\n",
        "## Notes\n\nFixture notes — never a task.\n"
        "Safety-bearing: yes — touches git-guard\n",
    )
    misplaced_path = _write_plan(tmp_path, misplaced_text)

    misplaced_result = _run_card(misplaced_path)

    assert misplaced_result.returncode == 1, misplaced_result.stdout + misplaced_result.stderr
    assert misplaced_result.stdout.startswith("plan_card: FAIL —"), misplaced_result.stdout
    assert "Safety-bearing: yes — touches git-guard" in misplaced_result.stdout
    assert "header" in misplaced_result.stdout
    assert misplaced_result.stdout.count("\n") == 1, "message must be one line"
    with pytest.raises(ValueError, match="header"):
        plan_card.safety_bearing(misplaced_text)

    miscased_dir = tmp_path / "miscased"
    miscased_dir.mkdir()
    miscased_text = _plan_text(tasks=[("parser", "pending")]).replace(
        "Stage: sdd:wave-1\n",
        "Stage: sdd:wave-1\nsafety-bearing: yes — touches git-guard\n",
    )
    miscased_path = _write_plan(miscased_dir, miscased_text)

    miscased_result = _run_card(miscased_path)

    assert miscased_result.returncode == 1, miscased_result.stdout + miscased_result.stderr
    assert miscased_result.stdout.startswith("plan_card: FAIL —"), miscased_result.stdout
    assert "Safety-bearing:" in miscased_result.stdout
    assert miscased_result.stdout.count("\n") == 1, "message must be one line"
    with pytest.raises(ValueError, match="Safety-bearing:"):
        plan_card.safety_bearing(miscased_text)


def test_indented_safety_bearing_line_in_header_fails_loud(tmp_path):
    """(review round 2, live adversarial audit) A `Safety-bearing:` line
    written INDENTED inside the header block — e.g. directly under
    `Stage:` — is `_header_value`'s continuation shape (N1's folded
    convention), so it used to be silently swallowed into the preceding
    field's value instead of being read as its own field, rendering
    `safety-bearing: N/A — header absent` at exit 0. A header-region
    continuation line whose stripped text starts with a known header key
    (Safety-bearing:/Goal:/Stage:/Steps:, case-insensitive) is malformed
    and must fail loud, naming the line, from both the CLI card render
    and the pure `safety_bearing()` helper directly."""
    indented_text = _plan_text(tasks=[("parser", "pending")]).replace(
        "Stage: sdd:wave-1\n",
        "Stage: sdd:wave-1\n  Safety-bearing: yes — touches git-guard\n",
    )
    plan_path = _write_plan(tmp_path, indented_text)

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Safety-bearing:" in result.stdout
    assert "continuation" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    with pytest.raises(ValueError, match="continuation"):
        plan_card.safety_bearing(indented_text)


def test_safety_bearing_mention_inside_fenced_block_is_ignored(tmp_path):
    """(review round 2, live adversarial audit) A `Safety-bearing:` line
    quoted inside a fenced code block (triple backtick) in the plan body
    — e.g. documentation showing the grammar — is content, not a
    misplaced header declaration; the outside-header scan must skip
    fenced lines and the plan still renders its normal card (N/A here,
    since no real header is present)."""
    text = _plan_text(tasks=[("parser", "pending")]).replace(
        "## Notes\n\nFixture notes — never a task.\n",
        "## Notes\n\nFixture notes — never a task.\n"
        "\n```\nSafety-bearing: yes — touches git-guard\n```\n",
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "safety-bearing: N/A — header absent\n" in result.stdout
    assert plan_card.safety_bearing(text) is None


def test_unclosed_fence_before_misplaced_header_fails_loud(tmp_path):
    """(review round 3, live adversarial audit) A fenced code block
    opened in the plan body and never closed used to leave the scan's
    `in_fence` state True through EOF, so a genuine misplaced
    `Safety-bearing:` line written after the opening fence marker was
    silently treated as fenced content and skipped — exit 0, N/A. An
    unclosed fence is itself malformed: it must fail loud naming the
    opening line, never silently swallow the rest of the document."""
    text = _plan_text(tasks=[("parser", "pending")]).replace(
        "## Notes\n\nFixture notes — never a task.\n",
        "## Notes\n\nFixture notes — never a task.\n"
        "\n```\nSafety-bearing: yes — touches git-guard\n",
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "unclosed" in result.stdout.lower()
    assert result.stdout.count("\n") == 1, "message must be one line"
    with pytest.raises(ValueError, match="unclosed"):
        plan_card.safety_bearing(text)


def test_tilde_fenced_safety_bearing_mention_is_ignored(tmp_path):
    """(review round 3, live adversarial audit) `~~~` is markdown's
    other fence delimiter, alongside triple-backtick — a
    `Safety-bearing:` line quoted inside a properly closed `~~~` fence
    is content, not a misplaced header declaration, same as the
    backtick case."""
    text = _plan_text(tasks=[("parser", "pending")]).replace(
        "## Notes\n\nFixture notes — never a task.\n",
        "## Notes\n\nFixture notes — never a task.\n"
        "\n~~~\nSafety-bearing: yes — touches git-guard\n~~~\n",
    )
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "safety-bearing: N/A — header absent\n" in result.stdout
    assert plan_card.safety_bearing(text) is None


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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 2 done / 0 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[v] T2 renderer\n"
        "stage: finishing\n"
        "next: close-out\n"
        "safety-bearing: N/A — header absent\n"
    )


def test_implemented_status_renders_as_review_pending(tmp_path):
    """A locally verified Batch member is visible but not terminal."""
    plan_path = _write_plan(
        tmp_path,
        _plan_text(tasks=[("parser", "implemented(abc1234)")]),
    )

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "tasks: 0 done / 1 implemented / 0 claimed / 0 pending / 0 blocked\n" in result.stdout
    assert "[i] T1 parser\n" in result.stdout
    assert "next: T1 parser\n" in result.stdout


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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
    assert "end-state:" not in result.stdout, "must never render a partial card"


def test_plan_with_no_task_headings_exits_1_loudly(tmp_path):
    """(5) Headers present but zero `## Task N — <name>` headings → exit 1
    naming the missing tasks."""
    plan_path = _write_plan(tmp_path, _plan_text(tasks=[]))

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "## Task" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
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
    assert "end-state:" not in result.stdout, "must never render a partial card"


@pytest.mark.parametrize(
    "malformed",
    [
        "done(abc1234)junk",
        "done()",
        "done((abc1234))",
        "implemented(abc1234)junk",
        "implemented()",
        "implemented(a b)",
        "claimed(@main)junk",
        "claimed()",
    ],
)
def test_renderer_rejects_malformed_payload_statuses(tmp_path, malformed):
    """Renderer status recognition is exact, not startswith-based."""
    plan_path = _write_plan(tmp_path, _plan_text(tasks=[("parser", malformed)]))

    result = _run_card(plan_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert malformed in result.stdout
    assert "end-state:" not in result.stdout


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
        "end-state: Ship the widget pipeline end-to-end.\n"
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
        "safety-bearing: N/A — header absent\n"
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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1 --\n"
        "[v] T1 parser\n"
        "-- step 2 (needs: T1) --\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 3 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1 --\n"
        "[v] T100 parser\n"
        "[v] T200 renderer\n"
        "[v] T300 docs\n"
        "-- step 2 (needs: T100 T200 T300) --\n"
        "[ ] T400 cli wiring\n"
        "stage: sdd:wave-1\n"
        "next: T400 cli wiring\n"
        "safety-bearing: N/A — header absent\n"
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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 1 claimed / 1 pending / 1 blocked\n"
        "[v] T1 parser\n"
        "[~] T2 renderer\n"
        "[ ] T3 cli wiring\n"
        "[!] T4 docs\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
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
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 1 pending / 0 blocked\n"
        "-- step 1: single wave --\n"
        "[v] T1 parser\n"
        "[ ] T2 renderer\n"
        "stage: sdd:wave-1\n"
        "next: T2 renderer\n"
        "safety-bearing: N/A — header absent\n"
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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
    assert "end-state: Ship the widget pipeline end-to-end.\n" in result.stdout
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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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
    assert "end-state:" not in result.stdout, "must never render a partial card"


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


def test_detail_preserves_nested_description_bullets(tmp_path):
    """--detail on a task whose Description is one sentence plus two
    nested bullets emits three lines, not one space-joined line —
    `_bullet_value`'s ``" ".join(...)`` fold is bypassed for
    Description inside build_detail only."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "  - Nested bullet one.\n"
            "  - Nested bullet two.\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "  Nested bullet one.\n"
        "  Nested bullet two.\n"
    )


def test_detail_preserves_star_and_plus_marker_nested_bullets(tmp_path):
    """--detail on a Description whose nested bullets use `*` and `+`
    markers (both accepted by check_field_microstructure.py's
    `_NESTED_BULLET_LINE`) emits them as separate bullet lines, not
    folded into the description sentence — `_fold_sub_bullets` only
    recognised `-`, so a `*`/`+` nested bullet fell through to the
    `elif items:` continuation branch (no bullet open yet) and landed
    in the `pre` branch, later joined into prose by the Description
    loop in build_detail."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "  * A star-marker nested bullet.\n"
            "  + A plus-marker nested bullet.\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "  A star-marker nested bullet.\n"
        "  A plus-marker nested bullet.\n"
    )


def test_detail_star_marker_continuation_not_treated_as_bullet(tmp_path):
    """A continuation line beginning with markdown emphasis (`*word*`,
    no space after the leading `*`) must NOT be mistaken for a
    `*`-marker nested bullet — it has to keep folding into the
    LAST-opened bullet's prose, same as any other continuation line."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "  - Nested bullet one.\n"
            "  *emphasised* continuation text.\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "  Nested bullet one. *emphasised* continuation text.\n"
    )


def test_detail_preserves_acceptance_table_rows(tmp_path):
    """--detail on a task whose Acceptance body is a three-row markdown
    table (no `- ` sub-bullet at all) emits all three rows — table rows
    arriving before the first sub-bullet used to match neither the
    sub-bullet branch nor the continuation branch and were silently
    dropped."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "- Acceptance:\n"
            "  | Field | Rule |\n"
            "  | --- | --- |\n"
            "  | Description | one sentence |\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "acceptance:\n"
        "  | Field | Rule |\n"
        "  | --- | --- |\n"
        "  | Description | one sentence |\n"
    )


def test_detail_preserves_acceptance_table_row_after_bullet(tmp_path):
    """--detail on a task whose Acceptance body opens a `- ` sub-bullet
    and is then followed by a table row: the table row must not be
    space-joined into the open bullet's prose (the `elif items:`
    continuation branch) — it is emitted verbatim on its own line,
    the same corruption as the pre-bullet case reached through the
    other branch."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "- Acceptance: first\n"
            "  - RED: some test\n"
            "  | Field | Rule |\n"
            "  | --- | --- |\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "acceptance: first\n"
        "  RED: some test\n"
        "  | Field | Rule |\n"
        "  | --- | --- |\n"
    )


def test_detail_preserves_order_of_table_between_two_bullets(tmp_path):
    """--detail on an Acceptance body whose table row sits BETWEEN two
    sub-bullets: the three segments come out in source order.

    This is the shape `_fold_sub_bullets` exists for. A design that
    appended table rows immediately and flushed accumulated bullets at
    the end would emit the table before both bullets and still pass
    every other table test in this file, because those fixtures put the
    table at one end of the body. Both reviewers verified this ordering
    by hand; nothing pinned it until this test.
    """
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "- Acceptance: first\n"
            "  - RED: some test\n"
            "  | Field | Rule |\n"
            "  - GREEN: it passes\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "acceptance: first\n"
        "  RED: some test\n"
        "  | Field | Rule |\n"
        "  GREEN: it passes\n"
    )


def test_detail_preserves_description_table_row_before_bullet(tmp_path):
    """--detail on a task whose Description body has a table row before
    its first nested bullet: the table row must not be space-joined
    into the Description sentence (the loop's own `else` branch) —
    the mirror-image gap of the Acceptance case."""
    plan_path = _write_plan(
        tmp_path,
        (
            "# Plan: widget fixture\n\n"
            "Source brief: docs/loom/specs/fixture.md\n"
            "Goal: Ship the widget pipeline end-to-end.\n"
            "Stage: sdd:wave-1\n\n"
            "## Task 1 — parser\n\n"
            "- Description: Extend the parser.\n"
            "  | Field | Rule |\n"
            "  | --- | --- |\n"
            "  - Nested bullet.\n"
            "- Status: pending\n\n"
            "## Notes\n\nFixture notes — never a task.\n"
        ),
    )

    result = _run_card(plan_path, "--detail", "T1")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "T1 parser\n"
        "description: Extend the parser.\n"
        "  | Field | Rule |\n"
        "  | --- | --- |\n"
        "  Nested bullet.\n"
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
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "stage: sdd:wave-1\n"
        "next: close-out\n"
        "safety-bearing: N/A — header absent\n"
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
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 1 done / 0 claimed / 0 pending / 0 blocked\n"
        "[v] T1 parser\n"
        "stage: sdd:wave-1\n"
        "next: close-out\n"
        "safety-bearing: N/A — header absent\n"
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
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 0 done / 0 claimed / 1 pending / 0 blocked\n"
        "[ ] T1 parser\n"
        "stage: sdd:wave-1\n"
        "next: T1 parser\n"
        "safety-bearing: N/A — header absent\n"
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
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 0 done / 1 claimed / 0 pending / 0 blocked\n"
        "[~] T1 parser\n"
        "stage: sdd:wave-1\n"
        "next: T1 parser\n"
        "safety-bearing: N/A — header absent\n"
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
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 0 done / 0 claimed / 0 pending / 1 blocked\n"
        "[!] T1 parser\n"
        "stage: sdd:wave-1\n"
        "next: T1 parser\n"
        "safety-bearing: N/A — header absent\n"
    )
    assert "- Status: blocked" in plan_path.read_text(encoding="utf-8")


def test_set_status_stdout_includes_card_body_after_new_line(tmp_path):
    """The rendered card follows old:/new: and a blank line — goal line,
    a task row, and stage line must all be present, proving build_card's
    own output (not a drifted second renderer) rides the flip."""
    plan_path = _write_plan(
        tmp_path, _plan_text(tasks=[("parser", "pending")])
    )

    result = _run_card(plan_path, "--set-status", "T1=done(abc1234)")

    assert result.returncode == 0, result.stdout + result.stderr
    stdout = result.stdout
    marker = "new: - Status: done(abc1234)\n"
    assert marker in stdout
    after_new = stdout.split(marker, 1)[1]
    assert after_new.startswith("\n"), "blank line must separate new: from the card"
    assert "end-state: Ship the widget pipeline end-to-end." in after_new
    assert "[v] T1 parser" in after_new
    assert "stage: sdd:wave-1" in after_new


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


def _init_tmp_git_repo(tmp_path: Path) -> tuple[Path, str]:
    """A fresh git repo (under `tmp_path`) with one commit; returns the
    repo dir and that commit's full 40-hex SHA."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "f.txt"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    return repo, sha


def test_set_status_expands_short_sha_to_forty_hex(tmp_path):
    """(R11b) `implemented(<short>)` is expanded to the ref's full
    40-hex SHA via `git rev-parse` at write time, so the ledger already
    satisfies batch_review_cli's 40-hex-only `_IMPLEMENTED` rule — no
    operator hand-expansion between plan_card and the batch CLI."""
    repo, sha = _init_tmp_git_repo(tmp_path)
    plan_path = _write_plan(repo, _plan_text(tasks=[("parser", "pending")]))
    short = sha[:7]

    result = _run_card(plan_path, "--set-status", f"T1=implemented({short})")

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"new: - Status: implemented({sha})\n" in result.stdout
    written = plan_path.read_text(encoding="utf-8")
    assert f"- Status: implemented({sha})" in written
    assert f"implemented({short})" not in written


def test_set_status_full_forty_hex_sha_passes_through_unchanged(tmp_path):
    """A status already carrying a 40-hex SHA is written verbatim —
    already conformant, no git call needed to leave it unchanged."""
    repo, sha = _init_tmp_git_repo(tmp_path)
    plan_path = _write_plan(repo, _plan_text(tasks=[("parser", "pending")]))

    result = _run_card(plan_path, "--set-status", f"T1=done({sha})")

    assert result.returncode == 0, result.stdout + result.stderr
    assert f"new: - Status: done({sha})\n" in result.stdout
    assert f"- Status: done({sha})" in plan_path.read_text(encoding="utf-8")


def test_set_status_bogus_ref_exits_1_naming_it(tmp_path):
    """A ref that does not resolve to a commit in the plan's own repo
    refuses loud, naming the ref; the file is never partially written."""
    repo, _sha = _init_tmp_git_repo(tmp_path)
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(repo, text)

    result = _run_card(plan_path, "--set-status", "T1=implemented(deadbee)")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "deadbee" in result.stdout
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


# --- ledger writer: --set-stage ----------------------------------------------
# Task 1 of docs/loom/plans/2026-08-08-progress-display-hardening.md.
# Free-text value (stage vocabulary evolves) — no enum validation.


def test_set_stage_happy_path_rewrites_and_prints_card(tmp_path):
    """`--set-stage "<text>"` replaces the Stage: header's value, prints
    old:/new: (the Stage header line before/after), then a blank line and
    the full card."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "sdd:wave-2")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (
        "old: Stage: sdd:wave-1\n"
        "new: Stage: sdd:wave-2\n"
        "\n"
        "end-state: Ship the widget pipeline end-to-end.\n"
        "tasks: 0 done / 0 claimed / 1 pending / 0 blocked\n"
        "[ ] T1 parser\n"
        "stage: sdd:wave-2\n"
        "next: T1 parser\n"
        "safety-bearing: N/A — header absent\n"
    )
    assert plan_path.read_text(encoding="utf-8") == text.replace(
        "Stage: sdd:wave-1", "Stage: sdd:wave-2"
    )


def test_set_stage_replaces_wrapped_continuation_lines(tmp_path):
    """(Finding 2, fix round) A wrapped `Stage:` value — an indented
    continuation line, N1's folded shape — must have its ENTIRE span
    replaced: the `Stage:` line plus every continuation line. Replacing
    only the `Stage:` line leaves a stale orphan continuation, which
    `_header_value` would fold back into a stale-merged value on the
    next render even though `new:` echoes the correct one."""
    text = _plan_text(tasks=[("parser", "pending")])
    wrapped = text.replace(
        "Stage: sdd:wave-1\n", "Stage: sdd:wave-1\n  continued detail\n"
    )
    plan_path = _write_plan(tmp_path, wrapped)

    result = _run_card(plan_path, "--set-stage", "sdd:wave-2")

    assert result.returncode == 0, result.stdout + result.stderr
    after = plan_path.read_text(encoding="utf-8")
    stage_lines = [line for line in after.splitlines() if line.startswith("Stage:")]
    assert stage_lines == ["Stage: sdd:wave-2"], stage_lines
    assert "continued detail" not in after
    assert "stage: sdd:wave-2\n" in result.stdout, result.stdout


def test_set_stage_and_detail_are_mutually_exclusive(tmp_path):
    """(Finding 3 reviewer note, fix round) Passing both --set-stage and
    --detail → usage error (exit 2) whose message names both flags; the
    file is not modified."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "sdd:wave-2", "--detail", "T1")

    assert result.returncode == 2, result.stdout + result.stderr
    assert "--set-stage" in result.stderr
    assert "--detail" in result.stderr
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_stage_and_set_status_are_mutually_exclusive(tmp_path):
    """(Finding 3 reviewer note, fix round) Passing both --set-stage and
    --set-status → usage error (exit 2) whose message names both flags;
    the file is not modified."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(
        plan_path, "--set-stage", "sdd:wave-2", "--set-status", "T1=blocked"
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "--set-stage" in result.stderr
    assert "--set-status" in result.stderr
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_stage_missing_header_exits_1(tmp_path):
    """A plan with no `Stage:` header line → exit 1 loud naming the
    missing field; the file is not modified."""
    text = _plan_text(stage=None, tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "sdd:wave-2")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert "Stage" in result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_stage_empty_value_exits_1(tmp_path):
    """A whitespace-only value → exit 1 loud; the file is not modified."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "   ")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_stage_newline_value_exits_1(tmp_path):
    """A value containing a newline must not be accepted — it would
    inject a second physical line into the header block, silently
    corrupting the plan's structure. Exit 1 loud; file untouched."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "review:round-1\nGoal: hacked")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_stage_carriage_return_value_exits_1(tmp_path):
    """A value containing a bare `\\r` must not be accepted either — the
    `"\\n" in new_value` guard misses it, but plan_card's own readers
    fold text via splitlines(), which treats `\\r` as a line boundary
    too — so the injected text would re-materialize as a second header
    line on the next read. Exit 1 loud; file untouched."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "review:round-1\rGoal: hacked")

    assert result.returncode == 1, result.stdout + result.stderr
    assert result.stdout.startswith("plan_card: FAIL —"), result.stdout
    assert result.stdout.count("\n") == 1, "message must be one line"
    assert plan_path.read_text(encoding="utf-8") == text, "file must be untouched"


def test_set_status_degrades_to_card_unavailable_when_goal_missing(tmp_path):
    """The flip runs and succeeds even when the resulting plan cannot
    render a card (no Goal: header) — the render runs AFTER the write,
    and a raise there degrades to one line rather than reporting the
    successful flip as a failure."""
    text = _plan_text(goal=None, tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-status", "T1=done(abc1234)")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "old: - Status: pending\n" in result.stdout
    assert "new: - Status: done(abc1234)\n" in result.stdout
    assert "plan_card: card unavailable —" in result.stdout
    assert "- Status: done(abc1234)" in plan_path.read_text(encoding="utf-8")


def test_set_status_write_lands_before_render_on_non_valueerror(tmp_path, monkeypatch):
    """(Finding 3, fix round) The "render runs AFTER the write" claim
    above is unfalsifiable on the ValueError-only path (a write-after-
    render implementation is indistinguishable there — both orders
    degrade to the same one-line message). This test distinguishes the
    two orderings directly: monkeypatch build_card to raise a
    NON-ValueError, call main() in-process (subprocess can't be
    monkeypatched), and require BOTH that the flip already landed on
    disk AND that the exception propagates uncaught (only ValueError is
    a controlled degrade — _print_card_or_degrade doesn't catch this).
    A write-after-render implementation would fail the file assertion:
    build_card raises before the write ever runs."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    def _boom(_text):
        raise RuntimeError("boom")

    monkeypatch.setattr(plan_card, "build_card", _boom)
    monkeypatch.setattr(
        sys,
        "argv",
        ["plan_card.py", str(plan_path), "--set-status", "T1=done(abc1234)"],
    )

    with pytest.raises(RuntimeError, match="boom"):
        plan_card.main()

    assert "- Status: done(abc1234)" in plan_path.read_text(encoding="utf-8")


def test_set_stage_degrades_to_card_unavailable_when_goal_missing(tmp_path):
    """Same degradation guarantee on the --set-stage path: a valid flip
    is never reported as a failure just because the resulting plan can't
    render."""
    text = _plan_text(goal=None, tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path, "--set-stage", "sdd:wave-2")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "old: Stage: sdd:wave-1\n" in result.stdout
    assert "new: Stage: sdd:wave-2\n" in result.stdout
    assert "plan_card: card unavailable —" in result.stdout
    assert "Stage: sdd:wave-2" in plan_path.read_text(encoding="utf-8")


def test_plan_card_oracle_keeps_name_and_exception_type(monkeypatch):
    """`_review_batch_oracle` delegates to `sibling_import.load_sibling`
    (Task 11 of docs/loom/plans/2026-08-31-loom-code-script-helper-extraction.md)
    while preserving two pre-existing contracts: an `ImportError` from
    the loader surfaces as `ValueError` (callers only ever catch
    ValueError, per the module's own docstring), and the module still
    registers in `sys.modules` under the unique name
    `"plan_card_review_batch_oracle"` (other code keys off that name)."""
    import sibling_import

    def _boom(filename, *, name=None, anchor=None):
        raise ImportError(f"cannot load {filename}")

    monkeypatch.setattr(sibling_import, "load_sibling", _boom)

    with pytest.raises(ValueError) as exc_info:
        plan_card._review_batch_oracle()
    assert isinstance(exc_info.value.__cause__, ImportError)

    monkeypatch.undo()

    sys.modules.pop("plan_card_review_batch_oracle", None)
    plan_card._review_batch_oracle()
    assert "plan_card_review_batch_oracle" in sys.modules


# ---------------------------------------------------------------------------
# F1/C1 — the header/body split anchors on ANY `^## ` line, including the
# document's very first line; an indented body-line mention is not invisible
# either. F4/C6 — fence scanning shares loom_gate_markers' toggle rules.
# ---------------------------------------------------------------------------


def test_plan_starting_with_h2_heading_has_empty_header_misplaced_line_raises():
    """(F1, whole-branch review) `plan_text.partition("\\n## ")` needs a
    LEADING newline before `## `, so a plan whose very first line IS a
    `## ` heading was never split there — the whole first section was
    read as `header`, and a `Safety-bearing:` line inside it rendered
    N/A instead of raising. After the fix the header is EMPTY (the
    split happens at position 0) and the line is scanned as body content
    — outside the header block — so it must raise as misplaced, never
    silently render N/A."""
    text = (
        "## Context\n\n"
        "Safety-bearing: no — routine docs touch-up\n\n"
        "## Task 1 — t\n\n- Status: pending\n"
    )
    with pytest.raises(ValueError, match="outside the plan's header block"):
        plan_card.safety_bearing(text)


def test_normal_plan_header_split_is_unchanged(tmp_path):
    """A plan with a real preamble before the first `## ` still renders
    its normal card — the F1 fix must not disturb the common case."""
    text = _plan_text(tasks=[("parser", "pending")])
    plan_path = _write_plan(tmp_path, text)

    result = _run_card(plan_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "safety-bearing: N/A — header absent\n" in result.stdout


def test_indented_safety_bearing_line_in_body_fails_loud():
    """(C1, whole-branch review) An INDENTED `Safety-bearing:` line
    written in the plan BODY (outside the header block, e.g. under a
    later `## ` section) used to be invisible to the outside-header scan
    — `re.match(r"^safety-bearing:", line, ...)` never matches a line
    with leading whitespace — so it rendered N/A silently, the same
    self-exemption class this module pins three other ways."""
    text = _plan_text(tasks=[("parser", "pending")]).replace(
        "## Notes\n\nFixture notes — never a task.\n",
        "## Notes\n\nFixture notes — never a task.\n"
        "\n  Safety-bearing: no — trivial\n",
    )
    with pytest.raises(ValueError, match="outside the plan's header block"):
        plan_card.safety_bearing(text)


def test_tilde_horizontal_rule_is_not_a_fence():
    """(F4/C6, whole-branch review) Pin the shared
    `loom_gate_markers._FENCED_CODE_DELIMITER_RE`/`_fence_toggle`
    behaviour for a lone `~~~~~~~~~~` line, rather than assuming it: the
    shared regex matches ANY run of 3+ of the same fence character at
    line start regardless of what (if anything) follows, so a bare run
    of tildes IS read as a fence-open delimiter — same as a genuine
    ```/~~~ opener. Left unclosed, it fails loud naming the opening
    line, exactly like any other unclosed fence (never silently hides
    the rest of the document)."""
    text = "## Notes\n\nFixture notes.\n\n~~~~~~~~~~\n\nMore text.\n"
    with pytest.raises(ValueError, match="unclosed"):
        plan_card._find_misplaced_safety_bearing_line(text)


def test_fence_scanning_matches_loom_gate_markers_behaviour():
    """plan_card._fence_toggle is a deliberate byte-for-byte duplicate of
    loom_gate_markers._fence_toggle (plan_card.py has no sibling-script
    imports — it ships as a standalone copy, per
    test_plan_card_batch_states.py's `_standalone_plan_card_copy`). This
    differential guard is the substitute for importing one from the
    other: run the SAME cases through both and require identical
    results, so a future edit that re-forks the two fails here."""
    cases = [
        ("```", None),
        ("~~~", None),
        ("````", ("`", 3)),
        ("~~~~~~~~~~", None),
        ("plain text", ("`", 3)),
        ("   ```", ("`", 3)),
        ("``` info-string", None),
    ]
    for line, fence_in in cases:
        assert plan_card._fence_toggle(line, fence_in) == (
            loom_gate_markers._fence_toggle(line, fence_in)
        )
