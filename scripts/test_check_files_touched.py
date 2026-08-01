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


# --- Task 3: verdict engine (pure — no git) -------------------------------
#
# WHY these tests exist: the three rule variants are only worth measuring if
# they can DISAGREE on the fixture corpus — an input on which all variants
# return the same verdict cannot discriminate them, and a test built on such
# an input cannot fail when a variant's semantics drift
# (docs/loom/memory/a-test-can-be-correct-and-still-unable-to-fail.md).
# Each divergence test below constructs an input where the variants MUST
# split by the frozen key's semantics
# (docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md,
# §Rule variants + cells 5 and 10).

from check_files_touched import (  # noqa: E402
    NO_JOIN, OK, OVER, UNDER, VARIANTS,
    evaluate_task, verdict_r1, verdict_r2, verdict_r3,
    TaskDeclaration,
)

PLAN_PATH = "docs/loom/plans/fixture-plan.md"


def test_rule_variants_diverge_on_over_declaration():
    """Frozen-key cell 5: a declared-but-never-touched path makes R1 flag
    OVER while R2/R3 return OK — the variants diverge BY CONSTRUCTION.
    If any variant's direction-sensitivity regresses, this fails."""
    declared = frozenset({"src/b.py", "src/never_touched.py"})
    actual = frozenset({"src/b.py"})

    r1 = verdict_r1(declared, actual)
    r2 = verdict_r2(declared, actual)
    r3 = verdict_r3(declared, actual, PLAN_PATH)

    assert r1.verdict == OVER
    assert r1.over == ("src/never_touched.py",)
    assert r1.under == ()
    assert r2.verdict == OK
    assert r3.verdict == OK
    # The divergence itself, stated once: not all three agree.
    assert len({r1.verdict, r2.verdict, r3.verdict}) == 2


def test_r1_reports_both_directions_simultaneously():
    """R1 on a mixed input carries BOTH offending lists; the dominant
    verdict token is UNDER. UNDER-dominance is this module's convention,
    chosen to match the frozen key's dangerous-direction rationale (brief
    §Rule variants, R2 row); no key cell exercises a mixed-direction
    input, so the convention is pinned here, not there."""
    declared = frozenset({"src/a.py", "src/declared_only.py"})
    actual = frozenset({"src/a.py", "src/undeclared.py"})

    r1 = verdict_r1(declared, actual)

    assert r1.verdict == UNDER
    assert r1.under == ("src/undeclared.py",)
    assert r1.over == ("src/declared_only.py",)


def test_r2_and_r3_diverge_on_standing_excludes():
    """Frozen-key cell 10: the actual set carries the two standing-exclude
    classes (the plan file under check + a `__pycache__/` artifact). R2 must
    flag them UNDER; R3 removes them from the ACTUAL set and returns OK —
    the R2↔R3 divergence exists BY CONSTRUCTION. Without this cell R3 ≡ R2
    corpus-wide and the measurement could not tell them apart."""
    declared = frozenset({"src/f.py"})
    actual = frozenset({
        "src/f.py",
        PLAN_PATH,  # the plan file itself
        "src/__pycache__/f.cpython-312.pyc",
    })

    r2 = verdict_r2(declared, actual)
    r3 = verdict_r3(declared, actual, PLAN_PATH)

    assert r2.verdict == UNDER
    assert set(r2.under) == {PLAN_PATH, "src/__pycache__/f.cpython-312.pyc"}
    assert r3.verdict == OK
    assert r3.under == ()


def test_r3_plan_file_exclude_compares_normalized_paths():
    """The plan-file exclude must survive spelling drift: a `./`-prefixed
    plan_path still excludes the bare-path form the actual set carries
    (same normalization family as the cell-10 token rules)."""
    declared = frozenset({"src/f.py"})
    actual = frozenset({"src/f.py", PLAN_PATH})

    r3 = verdict_r3(declared, actual, "./" + PLAN_PATH)

    assert r3.verdict == OK
    assert r3.under == ()


def test_r3_excludes_only_the_two_standing_classes():
    """R3's exclude list is EXACTLY two classes — a regenerated functional
    copy (frozen-key cell 3's under-declaration TARGET) must NOT be
    absorbed by the excludes."""
    declared = frozenset({"canonical/checklists/spec.md"})
    actual = frozenset({
        "canonical/checklists/spec.md",
        "mirror/checklists/spec.md",  # functional copy — a target, not noise
    })

    r3 = verdict_r3(declared, actual, PLAN_PATH)

    assert r3.verdict == UNDER
    assert r3.under == ("mirror/checklists/spec.md",)


def test_no_join_on_missing_sha_under_every_variant():
    """Frozen-key cell 7: a task with no `done(<sha>)` join key yields
    NO_JOIN under EVERY variant — never OK, even when the declared set
    happens to look clean (the silent-all-clear lesson)."""
    decl = TaskDeclaration(declared_paths=frozenset({"src/c.py"}), sha=None)

    verdicts = evaluate_task(decl, None, PLAN_PATH)

    assert set(verdicts) == set(VARIANTS)
    for variant in VARIANTS:
        assert verdicts[variant].verdict == NO_JOIN
        assert verdicts[variant].under == ()
        assert verdicts[variant].over == ()


def test_evaluate_task_runs_all_three_variants_on_joined_task():
    """With a join key present, evaluate_task returns one verdict per
    variant, each computed by that variant's own rule (cell-5 shape so the
    dict is visibly not three copies of one verdict)."""
    decl = TaskDeclaration(
        declared_paths=frozenset({"src/b.py", "src/never_touched.py"}),
        sha="abc1234")

    verdicts = evaluate_task(decl, frozenset({"src/b.py"}), PLAN_PATH)

    assert verdicts["R1"].verdict == OVER
    assert verdicts["R2"].verdict == OK
    assert verdicts["R3"].verdict == OK


def test_double_done_status_is_loud_and_keeps_last():
    """Two `Status: done(<sha>)` lines in one task block: the join is
    ambiguous. The parser keeps the LAST sha (existing behavior) but must
    say so in parse_errors — a silently-picked join key could compare a
    task against the wrong commit and render an unearned verdict."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — Double ledger line\n\n"
        "- **Files touched**: src/a.py\n"
        "- **Status**: done(abc1234)\n"
        "- **Status**: done(def5678)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].sha == "def5678"
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]
    assert "done(" in result.parse_errors[0]
