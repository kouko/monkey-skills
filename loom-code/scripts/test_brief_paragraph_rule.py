"""Structural grep test guarding the paragraph-length rule + narrative-
declaration syntax in `brainstorming/references/handoff-brief-format.md`
(Task 8 of `docs/loom/plans/2026-08-19-field-value-microstructure.md`).

handoff-brief-format.md is a prompt/contract artifact, not executable code:
nothing importable observes whether a brief author actually discovers the
600-character paragraph rule or the pinned `<!-- narrative: ... -->` escape.
This file IS the schema doc that author reads, so its correctness condition
is the PRESENCE of the pinned declaration form, the 600-character
threshold, both exempt-section names, and the "no checker classifies"
sentence that stops a later edit from quietly turning the declaration into
a machine-classified category.

Stdlib + pytest only (pathlib).
"""
from __future__ import annotations

from pathlib import Path

HANDOFF_BRIEF_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
)

# The declaration's pinned form (BI-6 / plan Task 8 §The rule you are
# writing).
NARRATIVE_DECLARATION_PREFIX = "<!-- narrative:"

# The measured threshold (OQ-1, resolved in the source spec).
THRESHOLD_PHRASE = "600 characters"

# The two exempt sections, named verbatim as headings.
EXEMPT_SECTION_EVIDENCE = "## Current State Evidence"
EXEMPT_SECTION_ALTERNATIVES = "## Alternatives Considered"

# The load-bearing sentence that stops a later edit from quietly turning
# the declaration into a machine-classified category.
NO_CHECKER_SENTENCE = (
    "No checker classifies a paragraph as narrative; the author declares, "
    "the reviewer checks the declaration."
)


def _text() -> str:
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    return HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8")


def test_brief_format_pins_narrative_declaration() -> None:
    text = _text()

    assert NARRATIVE_DECLARATION_PREFIX in text, (
        f"the narrative-declaration form {NARRATIVE_DECLARATION_PREFIX!r} "
        "must appear verbatim in handoff-brief-format.md"
    )

    assert THRESHOLD_PHRASE in text, (
        f"the {THRESHOLD_PHRASE!r} paragraph-length threshold must appear "
        "in handoff-brief-format.md"
    )

    assert EXEMPT_SECTION_EVIDENCE in text, (
        f"the exempt section {EXEMPT_SECTION_EVIDENCE!r} must be named in "
        "handoff-brief-format.md's paragraph-length rule"
    )

    assert EXEMPT_SECTION_ALTERNATIVES in text, (
        f"the exempt section {EXEMPT_SECTION_ALTERNATIVES!r} must be named "
        "in handoff-brief-format.md's paragraph-length rule"
    )


def test_brief_format_pins_no_checker_classifies_sentence() -> None:
    text = _text()

    # Pinned so a later edit cannot quietly turn the declaration into a
    # machine-classified category — a classifier would reintroduce the
    # judgment this rule exists to remove.
    assert NO_CHECKER_SENTENCE in text, (
        f"the sentence {NO_CHECKER_SENTENCE!r} must appear verbatim in "
        "handoff-brief-format.md -- no checker may classify a paragraph as "
        "narrative; only the declaration is checked"
    )
