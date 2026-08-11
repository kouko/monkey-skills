"""Prose-pin test for Task 3 (plan-level `## Task-flow diagram` slot).

Plan: docs/loom/plans/2026-08-11-visualization-trigger-layer.md, Task 3.

plan-format.md is a prompt/contract artifact, not executable code — the
correctness condition is PRESENCE of the load-bearing phrases a plan
author/reviewer would read, same convention as the sibling pin tests on
this file (test_plan_format_prose_weight.py, test_plan_format_progress_fields.py).

Pins:
  1. the new `### Plan-level diagram slot` subsection heading exists
  2. the required top-level section name `## Task-flow diagram` is named
     inside that subsection (as literal schema text, not just present
     somewhere incidental)
  3. Pin B's fill-or-declare contract (transcribed VERBATIM from the plan's
     §Pinned wording) is present, anchored on its distinctive
     "Do not delete the section heading" sentence

Note: `## Task-flow diagram` legitimately appears TWICE in the finished
file — once as the schema-defining literal in the new subsection, once as
the actual worked-example heading. Any uniqueness assertion below is
scoped to avoid over-fitting a count that is deliberately >= 2.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_FORMAT_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)

SUBSECTION_HEADING = "### Plan-level diagram slot"

TASK_FLOW_SECTION_LITERAL = "## Task-flow diagram"

# Pin B, transcribed VERBATIM from the plan's §Pinned wording.
PIN_B_ANCHOR_SENTENCE = (
    "Do not delete the section heading — an absent heading or a bare "
    "section is a reviewable omission, and an N/A whose reason does not "
    "hold against the artifact's own content is a reviewable claim."
)

NOT_PER_TASK_PHRASE = "Per-task diagrams are"


def _text() -> str:
    assert PLAN_FORMAT_MD.is_file(), f"plan-format.md is absent at {PLAN_FORMAT_MD}"
    return PLAN_FORMAT_MD.read_text(encoding="utf-8")


def _normalize(s: str) -> str:
    return " ".join(s.split())


def test_plan_level_diagram_slot_defined():
    """RED on current file: none of these three phrases exist yet."""
    text = _text()
    normalized = _normalize(text)

    assert SUBSECTION_HEADING in text, (
        f"missing subsection heading {SUBSECTION_HEADING!r}"
    )
    assert TASK_FLOW_SECTION_LITERAL in text, (
        f"missing required section literal {TASK_FLOW_SECTION_LITERAL!r}"
    )
    assert _normalize(PIN_B_ANCHOR_SENTENCE) in normalized, (
        "Pin B's fill-or-declare contract sentence is missing or was "
        "paraphrased instead of transcribed verbatim"
    )


def test_plan_level_diagram_slot_placed_before_per_task_block():
    """The new subsection must sit between §Top-level header and
    §Per-task block (Task 3 Description: 'immediately after §Top-level
    header ... before §Per-task block')."""
    text = _text()
    top_level_idx = text.index("### Top-level header (required)")
    subsection_idx = text.index(SUBSECTION_HEADING)
    per_task_idx = text.index("### Per-task block (required, repeats N times)")

    assert top_level_idx < subsection_idx < per_task_idx


def test_plan_level_diagram_slot_not_per_task():
    """Task 3: per-task diagrams are explicitly NOT required — must be
    stated inside the new subsection."""
    text = _text()
    start = text.index(SUBSECTION_HEADING)
    end = text.index("### Per-task block (required, repeats N times)")
    subsection_body = text[start:end]

    assert NOT_PER_TASK_PHRASE in subsection_body


def test_worked_example_carries_task_flow_diagram_line():
    """§Worked example plan stays schema-conformant: it must carry its own
    `## Task-flow diagram` heading with a one-line mermaid placeholder."""
    text = _text()
    worked_example_start = text.index("## Worked example")
    worked_example_end = text.index(
        "### Wide-but-shallow example", worked_example_start
    )
    worked_example_body = text[worked_example_start:worked_example_end]

    assert TASK_FLOW_SECTION_LITERAL in worked_example_body
    assert "mermaid" in worked_example_body.lower()

    # The literal now legitimately occurs twice file-wide: once as the
    # schema-defining text in the new subsection, once in the worked
    # example. Assert >= 2 deliberately (not ==) so a THIRD unrelated
    # occurrence elsewhere doesn't silently pass this test by accident
    # of the >= comparison while still catching regressions to < 2.
    assert text.count(TASK_FLOW_SECTION_LITERAL) >= 2


def test_visual_companion_pointer_sentence_present():
    """Task 3 Description: append the loom-code-local pointer sentence
    AFTER Pin B, pointing at visual-companion.md via a relative path
    resolvable from this file's directory."""
    text = _text()
    pointer_sentence = (
        "When-to-draw judgment: see "
        "[`../../brainstorming/references/visual-companion.md`]"
        "(../../brainstorming/references/visual-companion.md)."
    )
    assert pointer_sentence in text
