"""Anti-cheat probe for check_field_microstructure.py — Task 4 of
docs/loom/plans/2026-08-19-field-value-microstructure.md.

Why this file exists: docs/loom/memory/a-mechanical-check-can-go-green-by-skipping.md
documents that a pair-check has three outcomes, not two — agree,
disagree, and "one side stopped being findable" — and a check that
goes blind still exits 0. This arc produced its own sharper instance
of exactly that shape: `check_brief_paragraphs` originally split lines
on `\n` only, so on CRLF input every physical line became its own
one-line block, multi-line paragraphs were never merged, never
measured, and the checker reported clean. A green run meant "found
nothing", and nothing distinguished that from "there was nothing to
find". The tests below make that indistinguishability impossible for
all three checks plus the CLI's empty-input path: one canary per
check proves it still fires on an engineered violator, and two CLI
tests prove a structurally empty input (no `## Task` headings for
plan mode, no `## ` sections for `--brief` mode) is reported as an
input error (exit 2) rather than silently accepted as clean (exit 0).
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_SCRIPT = Path(__file__).parent / "check_field_microstructure.py"
_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

_spec = importlib.util.spec_from_file_location(
    "check_field_microstructure", _SCRIPT
)
check_field_microstructure = importlib.util.module_from_spec(_spec)
sys.modules["check_field_microstructure"] = check_field_microstructure
_spec.loader.exec_module(check_field_microstructure)

check_plan_fields = check_field_microstructure.check_plan_fields
check_goal = check_field_microstructure.check_goal
check_brief_paragraphs = check_field_microstructure.check_brief_paragraphs


# --- canaries: one per check, each engineered to violate it ----------


def test_check_plan_fields_canary_fires_on_overlong_description():
    text = (
        "Goal: keep it short\n"
        "Stage: sdd:wave-1\n"
        "\n"
        "## Task 1 — canary\n"
        "\n"
        "- **Description**: " + ("x" * 301) + "\n"
        "- **Status**: pending\n"
    )
    problems = check_plan_fields(text)
    assert len(problems) >= 1, (
        "check_plan_fields reported no problems on a Description first "
        "line engineered to exceed the 300-char cap — the check has "
        "gone blind, not clean"
    )


def test_check_goal_canary_fires_on_nested_body():
    # `Goal:` carries no length ceiling as of 2026-08-19 (Decision Log,
    # docs/loom/plans/2026-08-19-field-value-microstructure.md) — the
    # surviving rule is the no-nested-body one, so the canary must
    # engineer THAT violation to still prove check_goal has not gone
    # blind.
    text = (
        "Goal: keep it short\n"
        "  - a nested bullet under Goal\n"
        "Stage: sdd:wave-1\n\n## Task 1 — t\n"
    )
    problems = check_goal(text)
    assert len(problems) >= 1, (
        "check_goal reported no problems on a Goal: header engineered "
        "with a nested bullet body — the check has gone blind, not "
        "clean"
    )


def test_check_brief_paragraphs_canary_fires_on_overlong_paragraph():
    text = "## Decision\n\n" + ("z" * 601) + "\n"
    problems = check_brief_paragraphs(text)
    assert len(problems) >= 1, (
        "check_brief_paragraphs reported no problems on a 601-char "
        "prose paragraph with no narrative declaration — the check "
        "has gone blind, not clean"
    )


# --- empty-input is an input error, not a silent pass ----------------


def test_empty_plan_exits_2_not_0(tmp_path):
    plan_path = tmp_path / "empty-plan.md"
    plan_path.write_text("# Not a plan\n\nJust some prose, no task headings.\n")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 2, (
        f"expected exit 2 on a plan with no '## Task' headings, got "
        f"{result.returncode}; stderr: {result.stderr!r}"
    )
    assert "## Task" in result.stderr


def test_empty_brief_exits_2_not_0(tmp_path):
    brief_path = tmp_path / "empty-brief.md"
    brief_path.write_text("Just prose. No H2 sections at all.\n")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--brief", str(brief_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 2, (
        f"expected exit 2 on a brief with no '## ' sections, got "
        f"{result.returncode}; stderr: {result.stderr!r}"
    )
    assert "## " in result.stderr


def test_plan_violation_still_exits_1_not_2(tmp_path):
    # The empty-input path (exit 2) must stay distinct from the
    # ordinary violation path (exit 1) — a plan WITH task headings but
    # a real violation is not "structurally empty".
    plan_path = tmp_path / "violating-plan.md"
    plan_path.write_text(
        "Goal: g\nStage: sdd:wave-1\n\n"
        "## Task 1 — canary\n\n"
        "- **Description**: " + ("x" * 301) + "\n"
        "- **Status**: pending\n"
    )
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 1


def test_brief_violation_still_exits_1_not_2(tmp_path):
    brief_path = tmp_path / "violating-brief.md"
    brief_path.write_text("## Decision\n\n" + ("z" * 601) + "\n")
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--brief", str(brief_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )
    assert result.returncode == 1
