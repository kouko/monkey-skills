"""Prose-pin test for Task 6 (visual-companion diagram-semantics section).

Plan: docs/loom/plans/2026-08-17-artifact-table-routing.md, Task 6, Pin D.

visual-companion.md is a prompt/contract artifact, not executable code —
the correctness condition is PRESENCE of the load-bearing phrases a
brief-writer/reviewer would read, same convention as the sibling pin
tests (test_plan_diagram_slot.py).

Pins:
  1. Pin D's new heading `## Diagram semantics — edges say why, nodes
     carry their reason` is present exactly once, and sits before
     `## Anti-patterns`.
  2. Pin D's distinctive load-bearing phrases ("Edge labels state the
     relation's why", "Node text is two-layer", "may stay bare") are
     each present exactly once (transcribed verbatim, not paraphrased).
  3. The Flowchart (Axis 4) example's fenced mermaid block carries no
     bare `-- Yes -->` / `-- No -->` edges and uses `-->|"` why-labels
     instead.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VISUAL_COMPANION_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "brainstorming"
    / "references"
    / "visual-companion.md"
)

DIAGRAM_SEMANTICS_HEADING = (
    "## Diagram semantics — edges say why, nodes carry their reason"
)
ANTI_PATTERNS_HEADING = "## Anti-patterns"

EDGE_LABELS_PHRASE = "Edge labels state the relation's why"
NODE_TEXT_PHRASE = "Node text is two-layer"
MAY_STAY_BARE_PHRASE = "may stay bare"


def _text() -> str:
    assert VISUAL_COMPANION_MD.is_file(), (
        f"visual-companion.md is absent at {VISUAL_COMPANION_MD}"
    )
    return VISUAL_COMPANION_MD.read_text(encoding="utf-8")


def test_diagram_semantics_section_present():
    """RED on current file: the new Pin D section does not exist yet."""
    text = _text()

    assert text.count(DIAGRAM_SEMANTICS_HEADING) == 1, (
        f"expected exactly one {DIAGRAM_SEMANTICS_HEADING!r} heading"
    )
    assert text.count(EDGE_LABELS_PHRASE) == 1, (
        f"expected exactly one occurrence of {EDGE_LABELS_PHRASE!r}"
    )
    assert text.count(NODE_TEXT_PHRASE) == 1, (
        f"expected exactly one occurrence of {NODE_TEXT_PHRASE!r}"
    )
    assert text.count(MAY_STAY_BARE_PHRASE) == 1, (
        f"expected exactly one occurrence of {MAY_STAY_BARE_PHRASE!r}"
    )

    semantics_idx = text.index(DIAGRAM_SEMANTICS_HEADING)
    anti_patterns_idx = text.index(ANTI_PATTERNS_HEADING)
    assert semantics_idx < anti_patterns_idx, (
        "§Diagram semantics must sit before §Anti-patterns"
    )


def test_flowchart_example_has_no_bare_edges():
    """RED on current file: the Axis-4 flowchart example still has bare
    `-- Yes -->` / `-- No -->` edges instead of why-labelled ones."""
    text = _text()

    flowchart_heading = "### Flowchart (Axis 4 — alternatives + decision tree)"
    next_heading = "### Before / after architecture (Axis 5"
    start = text.index(flowchart_heading)
    end = text.index(next_heading, start)
    section = text[start:end]

    fence_start = section.index("```mermaid")
    fence_end = section.index("```", fence_start + len("```mermaid"))
    block = section[fence_start : fence_end + 3]

    assert "-- Yes -->" not in block, "bare '-- Yes -->' edge still present"
    assert "-- No -->" not in block, "bare '-- No -->' edge still present"
    assert '-->|"' in block, "expected at least one why-labelled edge '-->|\"'"
