"""Tests for check_files_touched.py — parse layer, verdict engine (R1/R2/R3),
git layer, CLI exit contract, and parser hardening (wrapped values,
trailing annotations, frozen-key cells 1-10).

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


# --- Task 6: continuation-line (wrapped) `Files touched` values ------------
#
# WHY these tests exist: two REAL plans in this repo wrap the `Files
# touched` value across indented continuation lines (trailing-comma form:
# docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md:48-49;
# no-value form: docs/loom/plans/2026-07-26-as-filed-statement-
# reconstruction.md Task 10). A parser blind to continuation lines sees a
# truncated declared set and renders FALSE UNDER verdicts on honest plans
# (brief §Addendum).


def test_wrapped_files_touched_value_spans_continuation_lines():
    """Mirror of the 07-11 shape: plain field form ending in a trailing
    comma, one indented continuation path, immediately followed by a
    `- Context paths:` bullet whose nested items must NOT be swallowed
    into the declared set."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — wrapped declaration\n\n"
        "- Description: fixture\n"
        "- Files touched: skills/data-markets/scripts/cache_util.py,\n"
        "  tests/data/test_cache_util.py\n"
        "- Context paths:\n"
        "  - skills/data-us/scripts/yfinance_client.py (reference)\n"
        "- Status: done(abc1234)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].declared_paths == frozenset({
        "skills/data-markets/scripts/cache_util.py",
        "tests/data/test_cache_util.py",  # the continuation path
    })
    assert result.parse_errors == []


def test_wrapped_files_touched_no_value_all_paths_on_continuation_lines():
    """Mirror of the as-filed Task-10 shape: bolded field line carries NO
    value at all; every path sits on an indented continuation line. The
    trailing comma on the first continuation line is list syntax, not an
    empty token."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — no-value wrapped declaration\n\n"
        "- **Description**: fixture\n"
        "- **Files touched**:\n"
        "  tests/analysis/test_fidelity.py,\n"
        "  tests/data/fixtures/ko_fy2017.json\n"
        "- **Context paths**:\n"
        "  - /abs/path/kpi_us_statement_shape.py\n"
        "- **Status**: done(abc1234)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].declared_paths == frozenset({
        "tests/analysis/test_fidelity.py",
        "tests/data/fixtures/ko_fy2017.json",
    })
    assert result.parse_errors == []


def test_trailing_comma_on_final_continuation_line_is_list_syntax():
    """The wrapped value's FINAL continuation line may itself end in a
    trailing comma — list syntax, not an empty token. Pins the
    continuation-present branch of the trailing-comma rule: deleting the
    `removesuffix(",")` makes this red (empty-token parse_error)."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — wrapped, comma on last continuation line\n\n"
        "- Files touched: src/a.py,\n"
        "  src/b.py,\n"
        "- Status: done(abc1234)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].declared_paths == frozenset(
        {"src/a.py", "src/b.py"})
    assert result.parse_errors == []


def test_trailing_comma_with_no_continuation_stays_a_parse_error():
    """A genuinely empty final token with NO continuation line is still a
    parse_error (current behavior preserved, plan Task 6 GREEN). Pins the
    OTHER side of the rule: making the trailing-comma strip unconditional
    makes this red (the error vanishes)."""
    result = parse_plan_text(_single_task("- Files touched: src/a.py,"))

    assert result.tasks[1].declared_paths == frozenset({"src/a.py"})
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]
    assert "Files touched" in result.parse_errors[0]


def test_real_wrapped_plan_task1_parses_full_declared_set():
    """INTEGRATION guard against a COMMITTED repo file (real producer
    output, docs/loom/memory/fixtures-mirror-producer-shape.md): the 07-11
    plan's Task 1 wraps its declaration at lines 48-49; both paths must
    reach the declared set with zero Files-touched parse errors for that
    task."""
    repo_root = Path(__file__).resolve().parent.parent
    plan = (repo_root / "docs" / "loom" / "plans"
            / "2026-07-11-investing-toolkit-data-consolidation.md")

    result = parse_plan(plan)

    declared = result.tasks[1].declared_paths
    assert ("investing-toolkit/skills/data-markets/scripts/cache_util.py"
            in declared)
    assert "investing-toolkit/tests/data/test_cache_util.py" in declared
    assert not [e for e in result.parse_errors
                if "Task 1" in e and "Files touched" in e]


# --- Task 7: trailing parenthetical annotation is not a path token ---------
#
# WHY these tests exist: a REAL plan (docs/loom/plans/2026-07-26-us-as-
# reported-statement-lane.md:24) ends its `Files touched` value with a
# post-PASS amendment note `(added in the review round … — see §Post-PASS
# amendment note)` after the final backticked path. A parser blind to the
# annotation contaminates the final token (false UNDER/OVER on an honest
# plan). Rule (plan Task 7): after a backtick-closed FINAL token, a
# parenthesized tail at END of value is an annotation — stripped, no
# parse_error; a NON-parenthetical tail after a backtick-closed token stays
# a parse_error; bare (unbackticked) tokens keep current behavior.

_LINE24_ANNOTATION = ("(added in the review round that froze the pre-fix "
                      "selector — see §Post-PASS amendment note)")
_LINE24_PATHS = frozenset({
    "investing-toolkit/tests/data/fixtures/capture_us_statement_shapes_probe.py",
    "investing-toolkit/tests/data/fixtures/us_statement_shapes_probe_2026-07-26.json",
    "investing-toolkit/tests/data/test_us_statement_probe_fixture.py",
    "investing-toolkit/tests/data/test_capture_us_statement_shapes_legacy_selector.py",
})


def test_trailing_parenthetical_annotation_not_a_token():
    """The line-24 shape: four backticked paths, the last followed by the
    real annotation text. The annotation is plan prose, not a path — the
    declared set is exactly the four paths, with zero parse errors."""
    files_value = ", ".join(f"`{p}`" for p in sorted(_LINE24_PATHS))
    result = parse_plan_text(_single_task(
        f"- **Files touched**: {files_value} {_LINE24_ANNOTATION}"))

    assert result.tasks[1].declared_paths == _LINE24_PATHS
    assert result.parse_errors == []


def test_non_parenthetical_tail_after_backticked_token_is_parse_error():
    """A NON-parenthetical tail after a backtick-closed token is not an
    annotation — it must land in parse_errors, never contaminate the path
    and never vanish (plan Task 7 Description, pinned)."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: `src/a.py`, `src/b.py` stray trailing prose"))

    assert result.tasks[1].declared_paths == frozenset({"src/a.py"})
    assert len(result.parse_errors) == 1
    assert "Task 1" in result.parse_errors[0]
    assert "src/b.py" in result.parse_errors[0]


def test_comma_inside_annotation_does_not_fragment_the_value():
    """The strip happens at VALUE level BEFORE comma-split, so a comma
    inside the annotation is prose, not a token separator — a per-token
    refactor of the strip would break exactly this shape (reviewer 🟡,
    2026-08-01: the real line-24 annotation is comma-free, so nothing
    else pins the ordering)."""
    result = parse_plan_text(_single_task(
        "- **Files touched**: `src/a.py`, `src/b.py` (amended, see note)"))

    assert result.tasks[1].declared_paths == frozenset(
        {"src/a.py", "src/b.py"})
    assert result.parse_errors == []


def test_annotation_on_final_continuation_line_of_wrapped_value_strips():
    """Task 6 × Task 7 interaction: concatenation happens FIRST, so an
    annotation ending the final continuation line of a wrapped value is the
    end of the (joined) value — stripped, no parse_error."""
    corpus = (
        "# Plan: fixture\n\n"
        "## Task 1 — wrapped, annotated last continuation line\n\n"
        "- Files touched: `src/a.py`,\n"
        f"  `src/b.py` {_LINE24_ANNOTATION}\n"
        "- Status: done(abc1234)\n"
    )
    result = parse_plan_text(corpus)

    assert result.tasks[1].declared_paths == frozenset(
        {"src/a.py", "src/b.py"})
    assert result.parse_errors == []


def test_real_annotated_plan_task1_parses_exact_declared_set():
    """INTEGRATION guard against the COMMITTED repo file whose line 24 IS
    the real annotation shape (real producer output,
    docs/loom/memory/fixtures-mirror-producer-shape.md): Task 1's declared
    set is exactly the four backticked paths — the annotation reaches
    neither the set nor parse_errors."""
    repo_root = Path(__file__).resolve().parent.parent
    plan = (repo_root / "docs" / "loom" / "plans"
            / "2026-07-26-us-as-reported-statement-lane.md")
    assert plan.is_file(), f"committed fixture plan missing: {plan}"

    result = parse_plan(plan)

    assert result.tasks[1].declared_paths == _LINE24_PATHS
    assert not [e for e in result.parse_errors
                if "Task 1" in e and "Files touched" in e]


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


# --- Task 4: git layer, CLI, ten-cell corpus end-to-end --------------------
#
# WHY these tests exist: cells 1-10 and their expected verdicts were FROZEN
# in docs/loom/audits/2026-08-01-declared-vs-actual-check-measurement.md
# BEFORE this layer existed. The sandbox repos below are real git producers
# (git init/add/commit — never hand-typed diffs, per
# docs/loom/memory/fixtures-mirror-producer-shape.md). On any disagreement
# the comparator is wrong, never the key. Fixture plans embed no fenced
# blocks containing `## Task` lines (parser limitation, frozen key §Frozen
# answer key preamble).

import subprocess  # noqa: E402

import pytest  # noqa: E402

from check_files_touched import actual_files, main  # noqa: E402

SCRIPT = HERE / "check_files_touched.py"
_GIT_ID = ("-c", "user.email=t@t", "-c", "user.name=t")


def _git(repo, *args) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *_GIT_ID, *args],
        check=True, capture_output=True, text=True).stdout


def _write(repo, rel, content="x\n"):
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path, baseline=()):
    """Sandbox repo; baseline files land in a first commit so the measured
    commit can EDIT them (the frozen key's cells say 'edits', not 'adds')."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    for rel in baseline:
        _write(repo, rel)
    if baseline:
        _git(repo, "add", "--", *baseline)
        _git(repo, "commit", "-q", "-m", "baseline")
    return repo


def _commit(repo, paths, msg="measured"):
    _git(repo, "add", "--", *paths)
    _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD").strip()


def _edit(repo, *rels):
    for rel in rels:
        _write(repo, rel, "edited\n")


def _task_lines(files_line, status_line=None):
    lines = ["- **Description**: fixture", files_line]
    if status_line:
        lines.append(status_line)
    return lines


def _bold(files_value, sha):
    return _task_lines(
        f"- **Files touched**: {files_value}",
        f"- **Status**: done({sha})" if sha else None)


def _write_plan(repo, rel, task_line_groups):
    out = ["# Plan: fixture", ""]
    for i, lines in enumerate(task_line_groups, 1):
        out += [f"## Task {i} — fixture", "", *lines, ""]
    _write(repo, rel, "\n".join(out) + "\n")


_OK3 = {"R1": OK, "R2": OK, "R3": OK}
_UNDER3 = {"R1": UNDER, "R2": UNDER, "R3": UNDER}
_NOJOIN3 = {"R1": NO_JOIN, "R2": NO_JOIN, "R3": NO_JOIN}


def _build_cell(cell, tmp_path):
    """Construct one frozen-key cell in a sandbox git repo.

    Returns (repo, plan_rel, expected) with expected mapping
    task_no -> {variant: frozen verdict token}. Construction specs are the
    SSOT rows of the frozen key (audit doc §Frozen answer key)."""
    if cell == 1:  # clean exact match
        repo = _repo(tmp_path, ["src/a.py", "tests/test_a.py"])
        _edit(repo, "src/a.py", "tests/test_a.py")
        sha = _commit(repo, ["src/a.py", "tests/test_a.py"])
        _write_plan(repo, "plan.md", [_bold("src/a.py, tests/test_a.py", sha)])
        return repo, "plan.md", {1: _OK3}
    if cell == 2:  # under-declaration, guard-test shape
        repo = _repo(tmp_path, ["src/limits.py", "tests/test_limits_guard.py"])
        _edit(repo, "src/limits.py", "tests/test_limits_guard.py")
        sha = _commit(repo, ["src/limits.py", "tests/test_limits_guard.py"])
        _write_plan(repo, "plan.md", [_bold("src/limits.py", sha)])
        return repo, "plan.md", {1: _UNDER3}
    if cell == 3:  # under-declaration, SSOT-functional-copy shape
        repo = _repo(tmp_path, ["canonical/checklists/spec.md",
                                "mirror/checklists/spec.md"])
        _edit(repo, "canonical/checklists/spec.md", "mirror/checklists/spec.md")
        sha = _commit(repo, ["canonical/checklists/spec.md",
                             "mirror/checklists/spec.md"])
        _write_plan(repo, "plan.md",
                    [_bold("canonical/checklists/spec.md", sha)])
        return repo, "plan.md", {1: _UNDER3}
    if cell == 4:  # under-declaration, manifest-mirror shape
        repo = _repo(tmp_path, ["plugin/plugin.json",
                                "plugin/.codex-plugin/plugin.json"])
        _edit(repo, "plugin/plugin.json", "plugin/.codex-plugin/plugin.json")
        sha = _commit(repo, ["plugin/plugin.json",
                             "plugin/.codex-plugin/plugin.json"])
        _write_plan(repo, "plan.md", [_bold("plugin/plugin.json", sha)])
        return repo, "plan.md", {1: _UNDER3}
    if cell == 5:  # over-declaration — the R1 vs R2/R3 discriminator
        repo = _repo(tmp_path, ["src/b.py", "src/never_touched.py"])
        _edit(repo, "src/b.py")
        sha = _commit(repo, ["src/b.py"])
        _write_plan(repo, "plan.md",
                    [_bold("src/b.py, src/never_touched.py", sha)])
        return repo, "plan.md", {1: {"R1": OVER, "R2": OK, "R3": OK}}
    if cell == 6:  # NEW: <path> token — commit CREATES the file
        repo = _repo(tmp_path)
        _write(repo, "src/new_module.py")
        sha = _commit(repo, ["src/new_module.py"])
        _write_plan(repo, "plan.md", [_bold("NEW: src/new_module.py", sha)])
        return repo, "plan.md", {1: _OK3}
    if cell == 7:  # missing done(<sha>) — a commit exists, nothing joins
        repo = _repo(tmp_path, ["src/c.py"])
        _edit(repo, "src/c.py")
        _commit(repo, ["src/c.py"])
        _write_plan(repo, "plan.md", [_bold("src/c.py", None)])
        return repo, "plan.md", {1: _NOJOIN3}
    if cell == 8:  # rename — --no-renames yields BOTH paths
        repo = _repo(tmp_path, ["src/old_name.py"])
        _git(repo, "mv", "src/old_name.py", "src/new_name.py")
        _write(repo, "src/new_name.py", "edited after move\n")
        sha = _commit(repo, ["src/new_name.py"])
        _write_plan(repo, "plan.md", [_bold("src/new_name.py", sha)])
        return repo, "plan.md", {1: _UNDER3}
    if cell == 9:  # field-form variance — one plan, two tasks, both clean
        repo = _repo(tmp_path, ["src/d.py", "src/e.py"])
        _edit(repo, "src/d.py")
        sha_a = _commit(repo, ["src/d.py"], "task A")
        _edit(repo, "src/e.py")
        sha_b = _commit(repo, ["src/e.py"], "task B")
        _write_plan(repo, "plan.md", [
            _bold("src/d.py", sha_a),
            ["- Description: plain real-plan form",
             "- Files touched: src/e.py",
             f"- Status: done({sha_b})"],
        ])
        return repo, "plan.md", {1: _OK3, 2: _OK3}
    if cell == 10:  # path normalization + the two standing excludes
        repo = _repo(tmp_path, ["src/f.py", "src/g.py", "src/h.py"])
        plan_rel = "plans/cell10.md"
        _edit(repo, "src/f.py", "src/g.py", "src/h.py")
        _write(repo, "src/__pycache__/f.cpython-312.pyc", "bytecode\n")
        declared = "./src/f.py, `src/g.py` , src/h.py "
        # The plan file itself is IN the measured commit, but the commit's
        # sha cannot be known before committing — commit the plan with a
        # sha-less ledger, then rewrite the working-tree plan with the real
        # join key. The comparator reads the working tree; the actual set
        # carries the committed PATH either way.
        _write_plan(repo, plan_rel, [_task_lines(
            f"- **Files touched**: {declared}", "- **Status**: pending")])
        # -f: a machine-global gitignore may ignore __pycache__; the frozen
        # key REQUIRES the artifact in the commit (it is what R3's exclude
        # class absorbs), so force it past any inherited ignore rule.
        _git(repo, "add", "-f", "--", "src/__pycache__/f.cpython-312.pyc")
        sha = _commit(repo, ["src/f.py", "src/g.py", "src/h.py", plan_rel])
        _write_plan(repo, plan_rel, [_bold(declared, sha)])
        return repo, plan_rel, {1: {"R1": UNDER, "R2": UNDER, "R3": OK}}
    raise AssertionError(f"unknown cell {cell}")


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("cell", range(1, 11))
def test_cells_match_frozen_answer_key(cell, variant, tmp_path):
    """Every frozen-key cell produces exactly its frozen verdict under this
    variant (audit doc §Frozen answer key, rows 1-10). The key predates the
    comparator, so a mismatch here means the comparator drifted — the test
    can fail on any semantic regression in parse, git, or verdict layers."""
    repo, plan_rel, expected = _build_cell(cell, tmp_path)

    parse = parse_plan(repo / plan_rel)

    assert parse.parse_errors == []
    assert set(parse.tasks) == set(expected)
    for task_no, decl in sorted(parse.tasks.items()):
        actual = actual_files(repo, decl.sha) if decl.sha else None
        verdicts = evaluate_task(decl, actual, plan_rel)
        assert verdicts[variant].verdict == expected[task_no][variant], (
            f"cell {cell} task {task_no} variant {variant}: got "
            f"{verdicts[variant].verdict}, frozen key says "
            f"{expected[task_no][variant]}")


def test_actual_files_no_renames_returns_both_rename_sides(tmp_path):
    """Kickoff decision (plan §Notes): `--no-renames` makes a rename
    contribute BOTH old and new paths — a sibling task touching the old
    path collides with this task's deletion of it (frozen key cell 8).
    With default rename detection git prints only the new path."""
    repo = _repo(tmp_path, ["src/old_name.py"])
    _git(repo, "mv", "src/old_name.py", "src/new_name.py")
    _write(repo, "src/new_name.py", "edited\n")
    sha = _commit(repo, ["src/new_name.py"])

    assert actual_files(repo, sha) == frozenset(
        {"src/old_name.py", "src/new_name.py"})


# --- CLI-level tests (subprocess — the real entry point) -------------------

def _run_cli(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_cli_exit_0_on_clean_plan(tmp_path):
    """All tasks OK under every variant -> exit 0."""
    repo, plan_rel, _ = _build_cell(1, tmp_path)

    res = _run_cli(str(repo / plan_rel), "--repo", str(repo))

    assert res.returncode == 0, res.stdout + res.stderr
    assert "OK" in res.stdout


def test_cli_exit_1_on_under_and_names_offending_path(tmp_path):
    """An UNDER verdict must exit 1 AND name the offending path — a flag
    without the path is unactionable."""
    repo, plan_rel, _ = _build_cell(2, tmp_path)

    res = _run_cli(str(repo / plan_rel), "--repo", str(repo))

    assert res.returncode == 1
    assert "UNDER" in res.stdout
    assert "tests/test_limits_guard.py" in res.stdout


def test_cli_exit_2_on_zero_tasks_names_what_was_empty(tmp_path):
    """Loud-empty duty (source brief §Decision): a plan that parses to no
    tasks must exit 2 with a message NAMING the emptiness — never an
    all-clear (the citation-checker empty-pass lesson)."""
    repo = _repo(tmp_path, ["src/a.py"])
    _write(repo, "plan.md", "# Plan: fixture\n\nNo task sections at all.\n")

    res = _run_cli(str(repo / "plan.md"), "--repo", str(repo))

    assert res.returncode == 2
    assert "0 tasks" in res.stderr


def test_cli_exit_2_on_zero_join_keys_names_what_was_empty(tmp_path):
    """Frozen-key cell 7 at CLI level: a task exists but NO task anywhere
    carries done(<sha>) — 0 join keys, exit 2, named."""
    repo, plan_rel, _ = _build_cell(7, tmp_path)

    res = _run_cli(str(repo / plan_rel), "--repo", str(repo))

    assert res.returncode == 2
    assert "0 join keys" in res.stderr


def test_cli_absolute_plan_path_still_hits_r3_plan_file_exclude(tmp_path):
    """Task-3 reviewer seam: an ABSOLUTE plan-path argument must be
    reconciled to its repo-relative spelling before evaluate_task —
    otherwise the R3 plan-file exclude silently no-ops and cell 10's
    committed plan file renders UNDER instead of excluded."""
    repo, plan_rel, _ = _build_cell(10, tmp_path)
    absolute = str((repo / plan_rel).resolve())

    res = _run_cli(absolute, "--repo", str(repo), "--variant", "R3")

    assert res.returncode == 0, res.stdout + res.stderr
    assert "OK" in res.stdout


def test_parse_errors_gate_an_otherwise_clean_exit(tmp_path):
    """Post-review fix (2026-08-01 whole-branch finding): one clean done()
    task (all variants OK) plus one task whose Status line carries the
    space typo `done (sha)` — a parse error and no join key. The corrupt
    ledger must gate: exit 1 with the parse-error line reported. An
    all-clear here would leave that task's commit silently uncompared
    (the escape path: parse_error -> sha None -> non-gating NO_JOIN)."""
    repo, plan_rel, _ = _build_cell(1, tmp_path)
    sha = _git(repo, "rev-parse", "HEAD").strip()
    _write_plan(repo, plan_rel, [
        _bold("src/a.py, tests/test_a.py", sha),
        ["- **Description**: corrupt ledger line",
         "- **Files touched**: src/a.py",
         "- **Status**: done (abc1234)"],  # space typo — outside vocabulary
    ])

    res = _run_cli(str(repo / plan_rel), "--repo", str(repo))

    assert res.returncode == 1, res.stdout + res.stderr
    assert "parse-error" in res.stderr
    assert "Status" in res.stderr


def test_zero_join_keys_with_parse_errors_still_exits_2(tmp_path):
    """Precedence pin (named explicitly per the same finding): loud-empty
    exit 2 WINS over the parse-error gate — a plan whose only task has the
    corrupt `done (sha)` line carries parse errors AND 0 join keys; the
    louder empty-verdict must not be downgraded to 1 by the new rule."""
    repo = _repo(tmp_path, ["src/a.py"])
    _write_plan(repo, "plan.md", [
        ["- **Files touched**: src/a.py",
         "- **Status**: done (abc1234)"],
    ])

    res = _run_cli(str(repo / "plan.md"), "--repo", str(repo))

    assert res.returncode == 2, res.stdout + res.stderr
    assert "0 join keys" in res.stderr
    assert "parse-error" in res.stderr


def test_cli_unresolvable_join_key_fails_loud(tmp_path):
    """A done(<sha>) that does not resolve in --repo must not vanish into
    an all-clear: exit 1 with the sha named (fail-loud, Rule 12)."""
    repo, plan_rel, _ = _build_cell(1, tmp_path)
    _write_plan(repo, plan_rel, [_bold("src/a.py", "deadbeefcafe1234")])

    res = _run_cli(str(repo / plan_rel), "--repo", str(repo))

    assert res.returncode == 1
    assert "deadbeefcafe1234" in res.stderr
