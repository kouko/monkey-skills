"""Prose-pin test for Task 1 (plan-level `## Open Questions` slot).

Plan: docs/loom/plans/2026-08-13-open-question-dispatch-gate.md, Task 1.

plan-format.md is a prompt/contract artifact, not executable code — the
correctness condition is PRESENCE of the load-bearing phrases a plan
author/reviewer would read, same convention as the sibling pin test on
this file's precedent, test_plan_diagram_slot.py.

Pins all six acceptance criteria (a)-(f) from the plan's Task 1:
  (a) fill-or-declare — entries, or the pinned N/A line with a reason;
      deleting the heading is a reviewable omission
  (b) entry form `- OQ-<n> [<TOKEN>] — <question text>`, OQ-<n> authored /
      monotonic / never renumbered / never reused (mirroring the `BI-<n>`
      rules in handoff-brief-format.md)
  (c) exactly two status tokens: [OPEN] and [RESOLVED]
  (d) a [RESOLVED] entry must carry how it was resolved, on the same entry
  (e) no owner / deadline / routing / per-task-linkage field, each named
      as deliberately absent
  (f) the text points at judgment-rubrics.md §3 rather than restating it
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_FORMAT_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)
WRITING_PLANS_SKILL_MD = (
    REPO_ROOT / "loom-code" / "skills" / "writing-plans" / "SKILL.md"
)
CHECK_OPEN_QUESTIONS = Path(__file__).parent / "check_open_questions.py"

SECTION_HEADING = "## Open Questions"

# Pin (a) — fill-or-declare wording, mirrored from the ## Diagrams precedent
# (handoff-brief-format.md:110-116 / this file's own ## Task-flow diagram
# slot). Full sentence including the trailing N/A-reviewability clause —
# matches the precedent's PIN_B_ANCHOR_SENTENCE in test_plan_diagram_slot.py
# in full, not truncated.
FILL_OR_DECLARE_ANCHOR = (
    "Do not delete the section heading — an absent heading or a bare "
    "section is a reviewable omission, and an N/A whose reason does not "
    "hold against the artifact's own content is a reviewable claim."
)
NA_LINE = "N/A — no unresolved question: <one-line reason>"

# The sentence pinned by FILL_OR_DECLARE_ANCHOR is shared verbatim with the
# ## Diagrams precedent (### Plan-level diagram slot) and appears TWICE in
# plan-format.md — once there, once in this task's own Open-Questions slot.
# An unscoped whole-file membership check on that sentence can't tell which
# copy it saw, so it stays green even if the Open-Questions copy is deleted
# (docs/loom/memory/assertion-must-encode-the-property-it-claims.md). Scope
# the check to the Open-Questions block itself, the same way clause (c)
# below is already scoped to its own block.
OPEN_QUESTIONS_SECTION_START = "### Plan-level open-questions slot"
OPEN_QUESTIONS_SECTION_END = "### Per-task block (required, repeats N times)"

# Pin (b) — entry form + OQ-<n> authoring rules
ENTRY_FORM = "- OQ-<n> [<TOKEN>] — <question text>"
AUTHORED_PHRASE = "authored, never derived"
MONOTONIC_PHRASE = "never renumbered, never reused"

# Pin (c) — exactly two status tokens. This is an EXCLUSIVITY claim (not
# mere existence), so it needs a relational predicate, not two membership
# checks: scope to the entry-form bullet block (where the token rule is
# stated) and assert the *set* of bracketed all-caps tokens found there is
# exactly {[OPEN], [RESOLVED]} — a third token added alongside the two
# required ones (e.g. `[BLOCKED]`) must flip this to FAIL.
OPEN_TOKEN = "[OPEN]"
RESOLVED_TOKEN = "[RESOLVED]"
BRACKETED_TOKEN_PATTERN = re.compile(r"\[[A-Z]+\]")
ENTRY_FORM_BLOCK_START = "Entry form:"
ENTRY_FORM_BLOCK_END = "This section deliberately carries no owner field"
TOKEN_EXACTNESS_SENTENCE = (
    "is exactly one of two values: `[OPEN]` or `[RESOLVED]`.** No third "
    "status exists."
)

# Pin (d) — resolution required on a RESOLVED entry, same entry
RESOLUTION_PHRASE = "carries how it was resolved"

# Pin (e) — deliberately-absent fields, each named
NO_OWNER = "no owner field"
NO_DEADLINE = "no deadline field"
NO_ROUTING = "no routing field"
NO_LINKAGE = "no per-task linkage field"

# Pin (f) — pointer, not restatement
JUDGMENT_RUBRICS_POINTER = "~/.claude/rules/judgment-rubrics.md"


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def _normalize(s: str) -> str:
    return " ".join(s.split())


def test_plan_format_declares_open_questions_fill_or_declare_slot():
    """RED on current file: plan-format.md has zero occurrences of "Open
    Question" before this task's edit, so every assertion below fails."""
    text = _text()
    normalized = _normalize(text)

    # (a) fill-or-declare
    assert SECTION_HEADING in text, f"missing required section heading {SECTION_HEADING!r}"

    # Scope to the Open-Questions block before checking the shared sentence
    # — an unscoped whole-file check can't distinguish this section's copy
    # from the ## Diagrams precedent's copy (see comment on the anchors
    # above). Both boundary strings must be unique in the file or the slice
    # is ambiguous.
    assert text.count(OPEN_QUESTIONS_SECTION_START) == 1, (
        f"expected exactly one {OPEN_QUESTIONS_SECTION_START!r} heading"
    )
    assert text.count(OPEN_QUESTIONS_SECTION_END) == 1, (
        f"expected exactly one {OPEN_QUESTIONS_SECTION_END!r} heading"
    )
    oq_start = text.index(OPEN_QUESTIONS_SECTION_START)
    oq_end = text.index(OPEN_QUESTIONS_SECTION_END)
    oq_section = _normalize(text[oq_start:oq_end])
    # Soft-wrapped in the source file (same convention as the ## Diagrams
    # precedent) — compare on normalized whitespace.
    assert _normalize(FILL_OR_DECLARE_ANCHOR) in oq_section, (
        "missing fill-or-declare / reviewable-omission wording in the "
        "Open-Questions section specifically"
    )
    assert NA_LINE in text, f"missing pinned N/A line {NA_LINE!r}"

    # (b) entry form + identifier rules
    assert ENTRY_FORM in text, f"missing entry form {ENTRY_FORM!r}"
    assert AUTHORED_PHRASE in text, "missing 'authored, never derived' identifier rule"
    assert MONOTONIC_PHRASE in text, (
        "missing 'never renumbered, never reused' identifier rule"
    )

    # (c) exactly two status tokens
    assert OPEN_TOKEN in text, f"missing status token {OPEN_TOKEN!r}"
    assert RESOLVED_TOKEN in text, f"missing status token {RESOLVED_TOKEN!r}"
    entry_form_start = text.index(ENTRY_FORM_BLOCK_START)
    entry_form_end = text.index(ENTRY_FORM_BLOCK_END)
    entry_form_block = text[entry_form_start:entry_form_end]
    found_tokens = set(BRACKETED_TOKEN_PATTERN.findall(entry_form_block))
    assert found_tokens == {OPEN_TOKEN, RESOLVED_TOKEN}, (
        "expected exactly the status tokens "
        f"{{{OPEN_TOKEN!r}, {RESOLVED_TOKEN!r}}} in the entry-form block, "
        f"found {found_tokens!r} — a third bracketed token means the "
        "'exactly two' exclusivity claim no longer holds"
    )
    assert _normalize(TOKEN_EXACTNESS_SENTENCE) in normalized, (
        "missing 'is exactly one of two values ... No third status exists' "
        "sentence"
    )

    # (d) resolution required on a RESOLVED entry
    assert RESOLUTION_PHRASE in text, "missing 'carries how it was resolved' rule"

    # (e) deliberately-absent fields, each named
    assert NO_OWNER in text, f"missing {NO_OWNER!r}"
    assert NO_DEADLINE in text, f"missing {NO_DEADLINE!r}"
    assert NO_ROUTING in text, f"missing {NO_ROUTING!r}"
    assert NO_LINKAGE in text, f"missing {NO_LINKAGE!r}"

    # (f) pointer, not restatement — judgment-rubrics.md §3's own boolean
    # grouping / thresholds must NOT be copied into the Open-Questions
    # slot. The two RESTATEMENT negatives below are claims about what
    # THIS slot says, not about the whole file, so — same convention as
    # pin (a) above, which scopes to oq_section for the identical reason
    # — both are scoped to oq_section rather than the whole document. An
    # unscoped whole-file check would false-accuse an unrelated part of
    # plan-format.md that happens to use either word for a different
    # purpose (e.g. an anti-pattern row about marking an irreversible
    # task, which restates nothing) of restating §3's content. The
    # POINTER presence check stays whole-file: it is a positive claim
    # ("the pointer exists somewhere relevant"), not a negative one, so
    # it carries no false-accusation risk from unrelated content
    # elsewhere in the document.
    assert JUDGMENT_RUBRICS_POINTER in text, "missing pointer to judgment-rubrics.md"
    assert "irreversible" not in oq_section.lower(), (
        "the Open-Questions slot restates judgment-rubrics.md §3's content "
        "instead of pointing at it"
    )
    assert "30 min" not in oq_section, (
        "the Open-Questions slot restates judgment-rubrics.md §3's content "
        "instead of pointing at it"
    )


def test_plan_open_questions_slot_placed_before_per_task_block():
    """Sits among the plan-level required sections, after the diagram slot
    and before Task 1 — mirroring where §Plan-level diagram slot sits."""
    text = _text()
    diagram_idx = text.index("### Plan-level diagram slot")
    section_idx = text.index(SECTION_HEADING)
    per_task_idx = text.index("### Per-task block (required, repeats N times)")

    assert diagram_idx < section_idx < per_task_idx


# Task 2 — Decision Log narrows its jurisdiction to decisions and points an
# unresolved question at ## Open Questions instead.
#
# `## Decision Log` (as a bare string) appears 5 times in plan-format.md:
# a backticked mention in the Open-Questions slot's own prose (line 76), two
# more backticked mentions in the schema-description paragraph, and two
# literal `## Decision Log` headings inside markdown code fences (the schema
# stub and its worked example) — none of which is the section's own
# descriptive prose. An unscoped whole-file `in` check can't tell which of
# these it matched (docs/loom/memory/assertion-must-encode-the-property-it-claims.md),
# so this test scopes to the section's own descriptive block, the same way
# the Open-Questions pin above scopes to its block.
DECISION_LOG_SECTION_START = "#### `Decision Log` plan section (v0.29.0+, optional)"
DECISION_LOG_SECTION_END = "## Worked example"
DECISION_LOG_DISCLAIMER = (
    "This section's jurisdiction is decisions, not open forks: an "
    "unresolved question does not belong here — it belongs in "
    "`## Open Questions` instead."
)


def test_decision_log_disclaims_unresolved_questions():
    """Task 2: the Decision Log section states its own jurisdiction is
    decisions only, and that an unresolved question belongs in
    `## Open Questions` instead — closing the second-home gap Task 1's
    §Plan-level open-questions slot already names from the other side."""
    text = _text()

    assert text.count(DECISION_LOG_SECTION_START) == 1, (
        f"expected exactly one {DECISION_LOG_SECTION_START!r} heading"
    )
    assert text.count(DECISION_LOG_SECTION_END) == 1, (
        f"expected exactly one {DECISION_LOG_SECTION_END!r} heading"
    )
    start = text.index(DECISION_LOG_SECTION_START)
    end = text.index(DECISION_LOG_SECTION_END)
    decision_log_section = _normalize(text[start:end])

    assert _normalize(DECISION_LOG_DISCLAIMER) in decision_log_section, (
        "Decision Log section does not state that an unresolved question "
        "belongs in `## Open Questions` instead, scoped to its own "
        "descriptive block"
    )


# Review-fix — every template a plan author copies must actually SHOW the
# slot: the two tests above only pin plan-format.md's own schema PROSE
# (the rule text), never whether a template built from that schema
# conforms to its own rule. That gap is exactly how both worked examples
# below, and writing-plans/SKILL.md's own "Minimum structure" schema
# template, shipped with zero '## Open Questions' section: an author
# following the schema-prose-conformant instructions would still produce
# a plan the schema's own gate rejects.
#
# These tests extract each template's fenced plan body and run it through
# the REAL check_open_questions.py grammar (subprocess, same convention
# as test_check_open_questions.py — not a re-implementation of the
# grammar) rather than re-checking for a bare substring, so a future edit
# that adds the heading back with a malformed or absent body still fails
# here, closing exactly the gap this task's dispatch named.

_ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")


def _extract_fenced_markdown_block(text: str, anchor: str) -> str:
    """Body of the fenced ```markdown code block that contains `anchor` —
    the nearest ```markdown fence opening before `anchor`, up to its
    matching closing fence. `anchor` must be a substring unique to one
    fenced block in `text` (callers verify this via `text.count`)."""
    anchor_idx = text.index(anchor)
    fence_marker = "```markdown\n"
    fence_start = text.rindex(fence_marker, 0, anchor_idx) + len(fence_marker)
    fence_end = text.index("\n```", fence_start)
    return text[fence_start:fence_end]


def _run_open_questions_checker(
    plan_text: str, tmp_path: Path
) -> subprocess.CompletedProcess:
    plan_path = tmp_path / "extracted-plan.md"
    plan_path.write_text(plan_text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(CHECK_OPEN_QUESTIONS), str(plan_path)],
        capture_output=True,
        text=True,
        env=_ENV,
    )


CSV_EXPORT_EXAMPLE_ANCHOR = "# Plan: CSV export query param"
DOCSTRING_BACKFILL_EXAMPLE_ANCHOR = "# Plan: backfill renderer module docstrings"


@pytest.mark.parametrize(
    "anchor",
    [CSV_EXPORT_EXAMPLE_ANCHOR, DOCSTRING_BACKFILL_EXAMPLE_ANCHOR],
)
def test_plan_format_worked_example_passes_real_open_questions_checker(
    anchor, tmp_path
):
    """Extract each of plan-format.md's two worked examples and run the
    REAL check_open_questions.py against the extracted body — must exit
    0. This is the check the orchestrator ran by hand to find the
    original defect (both examples exited 1: no section found)."""
    text = PLAN_FORMAT_MD.read_text(encoding="utf-8")
    assert text.count(anchor) == 1, f"expected exactly one {anchor!r} anchor"
    plan_body = _extract_fenced_markdown_block(text, anchor)
    result = _run_open_questions_checker(plan_body, tmp_path)
    assert result.returncode == 0, (
        f"worked example at {anchor!r} fails check_open_questions.py "
        f"(exit {result.returncode}): {result.stderr}"
    )


WRITING_PLANS_MINIMUM_STRUCTURE_ANCHOR = "# Plan: <topic>"


def test_writing_plans_minimum_structure_template_passes_real_checker(tmp_path):
    """writing-plans/SKILL.md's own 'Output contract — the plan ...
    Minimum structure' template is the block writing-plans follows when
    emitting a plan — it must also carry a checker-valid '## Open
    Questions' slot, not just plan-format.md's worked examples. The
    checker only scans the '## Open Questions' section itself (see
    check_open_questions.py's own docstring), so it does not matter that
    every other field in this block is a `<placeholder>` token rather
    than concrete content."""
    text = WRITING_PLANS_SKILL_MD.read_text(encoding="utf-8")
    assert text.count(WRITING_PLANS_MINIMUM_STRUCTURE_ANCHOR) == 1, (
        f"expected exactly one {WRITING_PLANS_MINIMUM_STRUCTURE_ANCHOR!r} anchor"
    )
    plan_body = _extract_fenced_markdown_block(
        text, WRITING_PLANS_MINIMUM_STRUCTURE_ANCHOR
    )
    result = _run_open_questions_checker(plan_body, tmp_path)
    assert result.returncode == 0, (
        "writing-plans/SKILL.md's Minimum structure template fails "
        f"check_open_questions.py (exit {result.returncode}): {result.stderr}"
    )
