"""Tests for check_files_touched.py — parse layer only (Task 2).

WHY these tests exist: the declared-vs-actual `Files touched` comparator
joins a plan's per-task declarations to real commits. If the parse layer
silently drops a field line it cannot read, the downstream verdict becomes
an unearned all-clear — the citation-checker empty-pass lesson (source
brief §Decision). Every test here pins either (a) that a declared token
reaches the parsed set in normalized form, or (b) that an unreadable field
line lands in `parse_errors` instead of vanishing.

Fixtures are inline plan-markdown corpus strings shaped like real plans in
docs/loom/plans/ (bolded `- **Field**:` schema form AND the plain
`- Field:` form real plans also use).
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_files_touched import parse_plan, parse_plan_text  # noqa: E402

BOLD_AND_PLAIN = """\
# Plan: fixture

## Task 1 — Bold schema form

- **Description**: first task
- **Files touched**: `src/a.py`, src/b.py
- **Status**: done(abc1234)

## Task 2 — Plain real-plan form

- Description: second task
- Files touched: src/c.py
- Status: done(def5678)

## Notes

- Not a task section; must be ignored.
"""


def test_parse_declared_files_bold_and_plain_forms():
    """Both field forms parse; backticked and bare tokens normalize to the
    same bare-path shape; each task joins to its done(<sha>) key."""
    result = parse_plan_text(BOLD_AND_PLAIN)

    assert set(result.tasks) == {1, 2}
    assert result.tasks[1].declared_paths == frozenset({"src/a.py", "src/b.py"})
    assert result.tasks[1].sha == "abc1234"
    assert result.tasks[2].declared_paths == frozenset({"src/c.py"})
    assert result.tasks[2].sha == "def5678"
    assert result.parse_errors == []


def _single_task(files_line: str, status_line: str = "- **Status**: done(abc1234)") -> str:
    return (
        "# Plan: fixture\n\n"
        "## Task 1 — Single fixture task\n\n"
        "- **Description**: fixture\n"
        f"{files_line}\n"
        f"{status_line}\n"
    )


def test_token_normalization_backticks_dotslash_whitespace():
    """Frozen-key cell-10 semantics: strip backticks, surrounding whitespace,
    and a leading `./` — the three declared spellings converge on bare paths."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: ./src/f.py, `src/g.py` , src/h.py "))

    assert result.tasks[1].declared_paths == frozenset(
        {"src/f.py", "src/g.py", "src/h.py"})
    assert result.parse_errors == []


def test_new_token_normalizes_to_proposed_path():
    """`NEW: <path>` (plan-format.md:79) declares the path itself — bare or
    backticked after the marker."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: NEW: `scripts/x.py`, NEW: scripts/y.py"))

    assert result.tasks[1].declared_paths == frozenset(
        {"scripts/x.py", "scripts/y.py"})
    assert result.parse_errors == []


def test_missing_status_field_yields_none_sha():
    """A task block with no Status line has no join key: sha is None, and
    that is NOT a parse error (Status is an optional runtime ledger field,
    plan-format.md:106) — loud handling of the un-joinable task is the
    verdict layer's job, not the parser's."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: src/a.py", status_line="- **Independent**: false"))

    assert result.tasks[1].declared_paths == frozenset({"src/a.py"})
    assert result.tasks[1].sha is None
    assert result.parse_errors == []


def test_non_done_status_vocabulary_yields_none_sha_without_error():
    """`pending` / `claimed(@x)` / `blocked` are valid ledger vocabulary
    (plan-format.md:106) that simply carry no sha."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: src/a.py", status_line="- **Status**: pending"))

    assert result.tasks[1].sha is None
    assert result.parse_errors == []


def test_malformed_files_touched_line_lands_in_parse_errors():
    """A line that matches the field name but has no parseable value must
    surface in parse_errors — never silently dropped (source brief
    §Decision, the citation-checker empty-pass lesson)."""
    result = parse_plan_text(_single_task("- **Files touched**:"))

    assert result.tasks[1].declared_paths == frozenset()
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]
    assert "Files touched" in result.parse_errors[0]


def test_malformed_status_value_lands_in_parse_errors():
    """A Status value outside the four-word ledger vocabulary is a parse
    error (sha stays None) — not a silent None."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: src/a.py", status_line="- **Status**: shipped!"))

    assert result.tasks[1].sha is None
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]
    assert "Status" in result.parse_errors[0]


def test_subheading_inside_task_block_does_not_split_the_task():
    """A `### ` subheading is INSIDE a `## Task` block (the block ends only
    at the next `## ` heading): field lines after the subheading still
    belong to the task. Known accepted limitation (copied idiom): a fenced
    code block containing `## `-prefixed lines would still split — fixture
    plans must not embed those."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — Task with a subsection\n\n"
        "- **Description**: fixture\n"
        "- **Files touched**: src/a.py\n\n"
        "### Design note\n\n"
        "Prose under a level-3 heading.\n\n"
        "- **Status**: done(abc1234)\n\n"
        "## Task 2 — Sibling task\n\n"
        "- **Files touched**: src/b.py\n"
        "- **Status**: done(def5678)\n"
    )
    result = parse_plan_text(corpus)

    assert set(result.tasks) == {1, 2}
    assert result.tasks[1].declared_paths == frozenset({"src/a.py"})
    assert result.tasks[1].sha == "abc1234"  # lost if `###` split the block
    assert result.tasks[2].declared_paths == frozenset({"src/b.py"})
    assert result.parse_errors == []


def test_duplicate_task_number_keeps_first_and_reports_error():
    """Two `## Task 1` headings: the first block wins, the collision is
    reported — a silent overwrite would drop declared paths."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — First\n\n"
        "- **Files touched**: src/a.py\n"
        "- **Status**: done(abc1234)\n\n"
        "## Task 1 — Duplicate\n\n"
        "- **Files touched**: src/b.py\n"
        "- **Status**: done(def5678)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].declared_paths == frozenset({"src/a.py"})
    assert result.tasks[1].sha == "abc1234"
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]


def test_parse_plan_reads_a_file(tmp_path):
    """The path-taking wrapper delegates to the text parser."""
    plan = tmp_path / "plan.md"
    plan.write_text(BOLD_AND_PLAIN, encoding="utf-8")

    result = parse_plan(plan)

    assert set(result.tasks) == {1, 2}
    assert result.tasks[1].sha == "abc1234"
