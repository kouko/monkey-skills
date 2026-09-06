"""Adversarial probes for W1-01 (plan field caps) of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- written BEFORE the
implementer, against `loom_checker.py plan <path>` and the new
`plan.field-caps` rule described in the plan's W1-01 task line.

None of this exists yet at the commit these probes were written against, so
every test below is expected to FAIL or ERROR today (unknown sub-command
`plan`, `--list-rules` missing `plan.field-caps`, wrong exit codes). That is
the implementer's RED: turning every one of these green, without weakening
any assertion here, is the acceptance bar for W1-01.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_field_caps.py -q -k <name>
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
THIS_CHANGE_PLAN = (
    REPO / "docs" / "loom" / "2026-09-05-artifact-charter-boundaries-and-edit-rights" / "plan.md"
)


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=str(REPO), capture_output=True, text=True,
    )


def _run_plan(path: Path) -> subprocess.CompletedProcess:
    return _run("plan", str(path))


def _words(n: int, token: str = "alpha") -> str:
    """n distinct space-separated words -- exactly n by len(text.split())."""
    return " ".join(f"{token}{i}" for i in range(n))


def _files(n: int, prefix: str = "src/mod") -> str:
    return ", ".join(f"{prefix}{i}.py" for i in range(n))


def _build_plan(
    tmp_path: Path,
    *,
    charter_line: str | None = "charter: 1.0",
    task_files: str = "src/a.py, src/b.py",
    task_test: str = "the failing test passes",
    task_risk: str | None = "agent-decided -- low risk",
    cse_bullet: str = "Forward: some/path.py:1 names the current gap in one short bullet here.",
    risks_item: str = "Some small residual plan-wide risk, agent-decided and bounded to one line.",
    extra_task_lines: str = "",
) -> Path:
    """A minimal, otherwise-valid plan.md with every field controllable, so
    each test varies exactly one field and leaves every other field inside
    cap -- an over-cap failure never has more than one cause."""
    lines = [
        "# Probe plan -- plan",
        "intent: 2026-09-05-artifact-charter-boundaries-and-edit-rights@1b3f9a10",
    ]
    if charter_line is not None:
        lines.append(charter_line)
    lines.append("")
    lines.append("## Current State Evidence")
    lines.append(f"- {cse_bullet}")
    lines.append("")
    lines.append("## Task DAG")
    lines.append("")
    lines.append("**W0-01 Probe task**  after: --")
    lines.append(f"- Files: {task_files}")
    lines.append(f"- Test: {task_test}")
    if task_risk is not None:
        lines.append(f"- Risk: {task_risk}")
    if extra_task_lines:
        lines.append(extra_task_lines)
    lines.append("")
    lines.append("## Questions asked")
    lines.append("")
    lines.append("## Risks")
    lines.append(f"1. {risks_item}")
    plan_path = tmp_path / "plan.md"
    plan_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return plan_path


# ---------------------------------------------------------------------------
# Test / Risk word caps -- exactly at 40 passes, 41 blocks.
# ---------------------------------------------------------------------------

def test_plan_field_caps_test_field_at_forty_words_passes(tmp_path: Path) -> None:
    """A Test field of exactly 40 words -- the stated cap -- must pass, not
    just 'not obviously fail': exit 0 and no plan.field-caps line at all."""
    plan_path = _build_plan(tmp_path, task_test=_words(40))
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        f"40-word Test field should pass the cap; got exit {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert "plan.field-caps" not in result.stderr


def test_plan_field_caps_test_field_at_forty_one_words_blocks(tmp_path: Path) -> None:
    """One word past the Test cap must block, naming the rule id, task and
    field -- not merely a non-zero exit that could be anything."""
    plan_path = _build_plan(tmp_path, task_test=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"41-word Test field should block (exit 1); got {result.returncode}, "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr
    assert "W0-01" in result.stderr
    assert "Test" in result.stderr


def test_plan_field_caps_risk_field_at_forty_one_words_blocks(tmp_path: Path) -> None:
    """The Risk field is capped independently of Test -- an over-cap Risk
    line must be caught even though Test stays well inside its own cap."""
    plan_path = _build_plan(tmp_path, task_test=_words(5), task_risk=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"41-word Risk field should block; got {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr
    assert "Risk" in result.stderr


def test_plan_field_caps_risk_field_at_forty_words_passes(tmp_path: Path) -> None:
    """The Risk field's own boundary, mirroring the Test boundary test."""
    plan_path = _build_plan(tmp_path, task_test=_words(5), task_risk=_words(40))
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        f"40-word Risk field should pass; got {result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" not in result.stderr


# ---------------------------------------------------------------------------
# Files: entry-count cap (8), not a word cap.
# ---------------------------------------------------------------------------

def test_plan_field_caps_files_eight_entries_passes(tmp_path: Path) -> None:
    """Exactly 8 comma-separated Files entries -- the stated cap -- passes,
    even though each path is several 'words' long by whitespace alone
    (paths are capped by entry count, not by len(text.split()))."""
    plan_path = _build_plan(tmp_path, task_files=_files(8, prefix="src/some/long/module/path"))
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        f"8 Files entries should pass; got {result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" not in result.stderr


def test_plan_field_caps_files_nine_entries_blocks(tmp_path: Path) -> None:
    """One entry past the Files cap blocks, naming the Files field."""
    plan_path = _build_plan(tmp_path, task_files=_files(9))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"9 Files entries should block; got {result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr
    assert "Files" in result.stderr


def test_plan_field_caps_files_comma_inside_backticks_not_miscounted(tmp_path: Path) -> None:
    """A hostile Files line: 7 plain paths plus ONE path that legitimately
    contains a comma, written inside backticks (e.g. a generated fixture
    named with a comma) -- 8 real entries total. A naive `line.split(',')`
    parser would see 9 pieces and false-block a plan that is actually
    inside the cap. This pins the correct behaviour (respect the backticks,
    count 8) as a requirement; if the eventual implementation instead
    naive-splits, this test documents that as a real defect, not a matter
    of taste -- see the accompanying finding."""
    files_line = _files(7) + ", `docs/loom/evidence/fixture,with-comma.md`"
    plan_path = _build_plan(tmp_path, task_files=files_line)
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        "a backtick-quoted path containing a comma must count as ONE Files "
        f"entry (8 total, inside cap), not two (9, over cap); got exit "
        f"{result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" not in result.stderr


# ---------------------------------------------------------------------------
# `## Risks` numbered items and `## Current State Evidence` bullets.
# ---------------------------------------------------------------------------

def test_plan_field_caps_risks_item_forty_one_words_blocks(tmp_path: Path) -> None:
    """A plan-wide Risks numbered item over its own 40-word cap blocks,
    even though the offending line lives outside the Task DAG entirely."""
    plan_path = _build_plan(tmp_path, risks_item=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"41-word Risks item should block; got {result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr


def test_plan_field_caps_current_state_evidence_bullet_thirty_one_words_blocks(
    tmp_path: Path,
) -> None:
    """A Current State Evidence bullet over its 30-word cap blocks -- a
    different, tighter cap than Risks or Test/Risk task fields, so a
    31-word bullet must not slip through under the wider 40-word cap by
    mistake."""
    plan_path = _build_plan(tmp_path, cse_bullet=_words(31))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"31-word Current State Evidence bullet should block; got "
        f"{result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr


# ---------------------------------------------------------------------------
# Grandfathering: no `charter:` line at all skips the rule entirely.
# ---------------------------------------------------------------------------

def test_plan_field_caps_no_charter_line_skips_with_clean_exit(tmp_path: Path) -> None:
    """A plan with NO `charter:` frontmatter line is grandfathered -- even a
    grotesquely over-cap 200-word Test field must produce exit 0 and zero
    output, not merely 'not blocked'. A rule that still prints a WARN or
    partial message on a plan it claims to skip is not actually skipping
    it."""
    plan_path = _build_plan(tmp_path, charter_line=None, task_test=_words(200))
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        f"no charter: line should be a clean skip (exit 0); got "
        f"{result.returncode}, stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert result.stdout == ""
    assert result.stderr == ""


# ---------------------------------------------------------------------------
# `charter:` present with an odd value -- the rule reads presence, not value.
# ---------------------------------------------------------------------------

def test_plan_field_caps_charter_arbitrary_value_still_applies(tmp_path: Path) -> None:
    """`charter: yes` -- a value that is not a real charter version -- must
    still trigger the rule (per the plan's own wording: 'any value'), so an
    over-cap Test field on this plan still blocks rather than being
    silently grandfathered by an unrecognised value."""
    plan_path = _build_plan(tmp_path, charter_line="charter: yes", task_test=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"charter: yes should still apply the caps; got {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr


def test_plan_field_caps_charter_empty_value_still_applies(tmp_path: Path) -> None:
    """`charter:` with nothing after the colon is still a `charter:` line --
    the grandfathering test is presence of the line, not a non-empty
    value -- so this must apply the caps too."""
    plan_path = _build_plan(tmp_path, charter_line="charter:", task_test=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"charter: (empty value) should still apply the caps; got "
        f"{result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr


# ---------------------------------------------------------------------------
# A missing Files/Test/Risk line on a task is itself a failure.
# ---------------------------------------------------------------------------

def test_plan_field_caps_missing_risk_line_blocks(tmp_path: Path) -> None:
    """A task with Files and Test but no Risk line at all is a
    plan.field-caps failure per the charter's must column, not silently
    treated as zero words (which would trivially pass any word cap)."""
    plan_path = _build_plan(tmp_path, task_risk=None)
    result = _run_plan(plan_path)
    assert result.returncode == 1, (
        f"a task missing its Risk line should block; got {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert "plan.field-caps" in result.stderr
    assert "Risk" in result.stderr
    assert "W0-01" in result.stderr


# ---------------------------------------------------------------------------
# CJK: a run of non-ASCII characters with no spaces is one word.
# ---------------------------------------------------------------------------

def test_plan_field_caps_cjk_run_counted_as_one_word(tmp_path: Path) -> None:
    """60 CJK characters with no internal whitespace must count as exactly
    ONE word by len(text.split()) -- the documented (not 'fixed') behaviour
    -- so a Test field consisting only of this run passes the 40-word cap
    even though it is far longer than 40 characters."""
    cjk_run = "測" * 60
    plan_path = _build_plan(tmp_path, task_test=cjk_run)
    result = _run_plan(plan_path)
    assert result.returncode == 0, (
        f"a single spaceless CJK run should count as one word and pass; got "
        f"{result.returncode}, stderr={result.stderr!r}"
    )
    assert "plan.field-caps" not in result.stderr


# ---------------------------------------------------------------------------
# The BLOCK line's exact shape: names the task id and the field.
# ---------------------------------------------------------------------------

def test_plan_field_caps_block_line_names_task_id_and_field(tmp_path: Path) -> None:
    """The BLOCK line must be actionable: it names which task and which
    field overflowed, and both the actual word count and the cap -- a bare
    'plan.field-caps: too long' would pass a substring check but leaves the
    author guessing which of several tasks and fields to trim."""
    plan_path = _build_plan(tmp_path, task_test=_words(41))
    result = _run_plan(plan_path)
    assert result.returncode == 1
    combined = result.stdout + result.stderr
    pattern = re.compile(
        r"plan\.field-caps.*W0-01.*Test.*41.*(?:cap|40)", re.IGNORECASE | re.DOTALL
    )
    assert pattern.search(combined), (
        f"BLOCK line should name task W0-01, field Test, count 41 and the "
        f"cap 40; got: {combined!r}"
    )


# ---------------------------------------------------------------------------
# CLI surface: --list-rules count, missing path, and this change's own plan.
# ---------------------------------------------------------------------------

def test_list_rules_count_is_twenty_nine_and_names_plan_field_caps() -> None:
    """`--list-rules` must grow to exactly 30 lines (28 plus W1-01's
    `plan.field-caps` plus W1-02's `plan.edits-after-commit`, both landed
    after this probe was first written) and must list `plan.field-caps` --
    the rule table is the SSOT other stations trust, so a rule that runs
    but never registers here is invisible to anyone auditing the rule
    set. (Count updated 30 for W1-02, authorised by that task's own
    dispatch packet -- see the implementer's commit body. Count updated
    again to 31 for W1-03's review.round-append-only, same authorisation
    shape.)"""
    result = _run("--list-rules")
    assert result.returncode == 0, f"--list-rules should exit 0; got {result.returncode}"
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 31, f"expected 31 rule lines, got {len(lines)}:\n{result.stdout}"
    assert any(line.startswith("plan.field-caps") for line in lines), (
        f"plan.field-caps missing from --list-rules:\n{result.stdout}"
    )


def test_plan_subcommand_missing_path_exits_two_with_reason(tmp_path: Path) -> None:
    """A plan path that does not exist must fail closed at exit 2 with a
    message that actually says the path is missing -- not merely any exit 2
    (an unrelated 'unknown sub-command' error would also happen to be 2)."""
    missing = tmp_path / "no-such-plan.md"
    result = _run_plan(missing)
    assert result.returncode == 2, (
        f"a missing plan path should exit 2; got {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert re.search(r"no such|not found|does not exist|missing", result.stderr, re.IGNORECASE), (
        f"exit-2 message should explain the path is missing/unreadable, got: "
        f"{result.stderr!r}"
    )


def test_plan_subcommand_this_change_own_plan_passes() -> None:
    """This very change's plan.md -- which carries `charter: 1.0` and, per
    the plan's own W1-01 task line, keeps every field inside the caps --
    must pass the subcommand cleanly. If the plan that specifies the caps
    cannot itself satisfy them, the caps are wrong or the plan is."""
    assert THIS_CHANGE_PLAN.is_file(), f"expected plan at {THIS_CHANGE_PLAN}"
    result = _run_plan(THIS_CHANGE_PLAN)
    assert result.returncode == 0, (
        f"this change's own plan.md should pass plan.field-caps; got "
        f"{result.returncode}, stdout={result.stdout!r} stderr={result.stderr!r}"
    )
