"""Structural grep test guarding the `## Diagrams` fill-or-declare rewrite in
`brainstorming/references/handoff-brief-format.md` (Task 2 of
`docs/loom/plans/2026-08-11-visualization-trigger-layer.md`).

handoff-brief-format.md is a prompt/contract artifact, not executable code:
nothing importable observes whether a brief author actually discovers the
fill-or-declare contract for `## Diagrams`. This file IS the schema doc that
author reads, so its correctness condition is the PRESENCE of the pinned
phrases (Pin A / Pin B, transcribed verbatim from the plan) and the ABSENCE
of the old "delete the section" escape hatch.

Stdlib + pytest only (pathlib).
"""
from __future__ import annotations

import re
from pathlib import Path

HANDOFF_BRIEF_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
)

# Pin A's full line-prefix (transcribe VERBATIM from the plan's §Pinned wording).
PIN_A_PREFIX = "N/A — no flow/state/architecture-shaped content:"

# Pin B's load-bearing sentence (transcribed VERBATIM from the plan), narrowed
# to the full `## Diagrams`-specific clause: `## Alternatives Considered`
# (added in a later task, docs/loom/plans/2026-08-17-artifact-table-routing.md
# Task 2) legitimately shares the bare prefix "Do not delete the section
# heading — an absent heading or a bare section is a reviewable omission."
# via its own transcribed Pin B, so the short prefix is no longer unique in
# this file; the continuation below IS unique to `## Diagrams`.
PIN_B_HEADING_SENTENCE = (
    "Do not delete the section heading — an absent heading or a bare "
    "section is a reviewable omission, and an N/A whose reason does not "
    "hold against the artifact's own content is a reviewable claim."
)

# The old escape hatch this task must remove.
OLD_ESCAPE_PHRASE = "remove this section if no diagrams"


def _text() -> str:
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    return HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8")


def _normalized_text() -> str:
    # handoff-brief-format.md hard-wraps prose at ~80 columns, so a
    # multi-clause pinned sentence can span source lines; collapse runs of
    # whitespace (including newlines) to a single space before matching.
    return re.sub(r"\s+", " ", _text())


def test_diagrams_section_fill_or_declare_full_phrases() -> None:
    text = _text()

    # Pin A's line-prefix occurs exactly once: embedded in the spec entry's
    # transcribed Pin B block. The template copy only prose-references the
    # pinned N/A line ("write the pinned N/A line") rather than repeating
    # the literal, so this is a uniqueness assertion, not a bare-presence
    # one, per the plan's grep-pin-discipline note.
    assert text.count(PIN_A_PREFIX) == 1, (
        f"Pin A's full line-prefix {PIN_A_PREFIX!r} must appear exactly once "
        "in handoff-brief-format.md's `## Diagrams` fill-or-declare wording"
    )

    # Pin B's sentence is the shared fill-or-declare contract core; it
    # belongs in the spec entry exactly once (the template copy carries the
    # short form per the task, not the full Pin B block). Matched against
    # whitespace-normalized text since the source hard-wraps this sentence
    # across lines.
    normalized = _normalized_text()
    assert normalized.count(PIN_B_HEADING_SENTENCE) == 1, (
        f"Pin B's sentence {PIN_B_HEADING_SENTENCE!r} must appear exactly once "
        "(in the `## Diagrams` entry, whitespace-normalized)"
    )

    # The old "just delete it" escape hatch must be fully gone.
    assert OLD_ESCAPE_PHRASE not in text, (
        f"the old escape phrase {OLD_ESCAPE_PHRASE!r} must be removed from "
        "handoff-brief-format.md -- `## Diagrams` is fill-or-declare, not optional"
    )
