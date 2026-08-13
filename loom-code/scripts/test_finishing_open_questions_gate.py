"""Structural grep-test guarding the open-questions close-out checkpoint in
finishing-a-development-branch/SKILL.md.

Origin: plan `docs/loom/plans/2026-08-13-open-question-dispatch-gate.md`
Task 5. A plan's `## Open Questions` section (added by that plan's Task 1)
can hold an unresolved `[OPEN]` entry born DURING execution — after the
plan-write gate (Task 4) already passed and has nothing left to catch. This
is the close-out leg: a Step 8 sub-check running `check_open_questions.py`
against the branch's plan before the close-out commit, mirroring the
`check_loom_memory_integrity.py` row and the `backlog_index.py --write` row
already in that table.

These checks assert on load-bearing PHRASES scoped to the row's OWN
physical line — a table row in this file is one long physical line, same
as every sibling row — mirroring `test_finishing_memory_store_integrity.py`'s
`_integrity_row` extraction. Line-scoping matters here specifically: the
sibling rows in the same table also use the words "STOP", "before the
close-out commit", and "Step 1", so an unscoped whole-file `in` check would
stay green even if THIS row's own STOP clause were deleted, satisfied by a
neighboring row's copy instead. Mutation-tested on a scratch copy: deleting
the row, and separately rewording it to drop the STOP clause, each turn
the relevant assertion below red.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _open_questions_row(text: str) -> str:
    """The Open-questions check table ROW — line-scoped extraction, so an
    assertion on this string can only be satisfied by THIS row, never by a
    neighboring row in the same Step 8 table that happens to share
    vocabulary (STOP / before the close-out commit / Step 1)."""
    row_start = text.find("| Open-questions check |")
    assert row_start != -1, (
        'no line matching the literal anchor "| Open-questions check |" '
        "— the table row is either absent, renamed, or the Check-cell "
        "label changed; check which before editing the tests"
    )
    return text[row_start:].splitlines()[0]


def test_step8_table_names_open_questions_check():
    """RED before the row is added — SKILL.md today has zero occurrences
    of `check_open_questions.py`, so this fails with the anchor assertion
    inside `_open_questions_row`."""
    row = _open_questions_row(_text())
    assert "check_open_questions.py" in row, \
        "the Step 8 row must name the checker script"


def test_open_questions_row_names_full_invocation_path():
    """Full invocation, not a bare basename — same reasoning as the
    memory-store integrity row's own test: a bare basename is satisfiable
    by any path prefix (loom-pipeline/scripts/, tools/scripts/, ../scripts/),
    so the assertion must pin the full repo-root-relative path."""
    row = _open_questions_row(_text())
    assert "python3 loom-code/scripts/check_open_questions.py" in row, \
        "must name the full repo-root-relative invocation, admitting no path prefix"


def test_open_questions_row_specifies_stop_on_nonzero():
    """The row must say what NOT to do on a violation, not only what
    passing looks like — the same gap `test_memory_integrity_step_states_
    the_failure_action` guards on the sibling row."""
    row = _open_questions_row(_text())
    assert "STOP" in row, \
        "must specify STOP on a nonzero exit, not just the pass condition"
    assert "nonzero" in row.lower() or "non-zero" in row.lower(), \
        "must name the failure condition explicitly"


def test_open_questions_row_runs_before_the_close_out_commit():
    row = _open_questions_row(_text())
    assert "before the close-out commit" in row, \
        "must place the check before the close-out commit, matching the sibling rows"


def test_open_questions_row_reuses_step_1s_plan_not_a_new_discovery_rule():
    """Judgment call: the row must name WHICH plan to check by pointing at
    the plan Step 1 already read/rendered (`plan_card.py <plan-path>`,
    SKILL.md Step 1), not invent a second plan-discovery mechanism.

    Cell-sliced to the plan-identification cell (`row.split("|")[2]`), not
    the whole row: the row also carries a trailing "per Step 1's
    entry-card rules" phrase in the skip-case cell, so an unscoped
    `"Step 1" in row` check stays green even if THIS cell's own reuse
    clause were replaced with an invented discovery rule (e.g. "find it
    by globbing docs/loom/plans/ and taking the newest file") -- the
    exact defect this test exists to catch."""
    row = _open_questions_row(_text())
    plan_identification_cell = row.split("|")[2]
    assert plan_identification_cell.count("Step 1") == 1, \
        "must point at the plan Step 1 already identified, not a fresh discovery rule"


def test_open_questions_row_states_no_plan_skip_case():
    """A conditional row that never says when it is N/A gets run as a
    ritual or skipped silently — same rule the sibling `test_memory_
    integrity_step_states_when_it_does_not_fire` guards."""
    row = _open_questions_row(_text())
    assert "skip" in row.lower(), \
        "must state the no-plan skip case explicitly"
