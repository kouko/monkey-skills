"""Structural grep test guarding the paragraph-length rule + narrative-
declaration syntax in `brainstorming/references/handoff-brief-format.md`
(Task 8 of `docs/loom/plans/2026-08-19-field-value-microstructure.md`).

handoff-brief-format.md is a prompt/contract artifact, not executable code:
nothing importable observes whether a brief author actually discovers the
600-character paragraph rule or the pinned `<!-- narrative: ... -->` escape.
This file IS the schema doc that author reads, so its correctness condition
is the PRESENCE of the pinned declaration form, the 600-character
threshold, both exempt sections' bullets (name AND reason clause, so a
reworded-away reason fails loudly), the sentence explaining why the
narrative declaration uses a comment instead of a visible `N/A —` line,
and the "no checker classifies" sentence that stops a later edit from
quietly turning the declaration into a machine-classified category.

The assertions are scoped to the `## Paragraph length` section's own
extent (heading to next `## ` heading) rather than the whole document, so
they fail if that section — or an exemption bullet inside it — is deleted,
even though the exempt section names also occur elsewhere in the doc as
real headings.

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

# The exempt sections, pinned as their full bullet line (name + reason),
# not just the bare heading name -- the heading name alone also occurs
# elsewhere in the doc as a real section heading, so a bare-name pin
# would still pass with the exemption bullet deleted or its reason
# dropped.
EXEMPT_BULLET_EVIDENCE = (
    "- `## Current State Evidence` — a citation appendix, not narrative "
    "prose."
)
EXEMPT_BULLET_ALTERNATIVES = (
    "- `## Alternatives Considered` — already table-routed by "
    "`loom-code/hooks/family-relay.md §(b) Visual defaults`."
)

# Why the declaration is an HTML comment (invisible) rather than the
# visible `N/A — <reason>` form every other fill-or-declare slot uses --
# stated so a future maintainer syncing the declare vocabulary can tell
# this is a deliberate second convention, not drift to fix.
COMMENT_SYNTAX_RATIONALE_SENTENCE = (
    "This declaration uses an HTML comment instead of the "
    "`N/A — <reason>` form the other fill-or-declare slots use, because "
    "a visible `N/A —` line would break the narrative paragraph's own "
    "reading flow — staying readable prose is the whole point of the "
    "paragraph the declaration sits beneath."
)

# The load-bearing sentence that stops a later edit from quietly turning
# the declaration into a machine-classified category.
NO_CHECKER_SENTENCE = (
    "No checker classifies a paragraph as narrative; the author declares, "
    "the reviewer checks the declaration."
)

SECTION_HEADING = "## Paragraph length"


def _text() -> str:
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    return HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8")


def _paragraph_length_section(text: str) -> str:
    """Return the `## Paragraph length` section's own extent: from its
    heading up to (not including) the next `## ` heading. Scoping to
    this slice -- rather than searching the whole document -- is what
    makes the pins fail when the section, or a bullet inside it, is
    deleted: the exempt section names also occur elsewhere in the doc
    as real headings, so an unscoped `in text` check would keep passing
    even with the section gone.
    """
    start = text.index(SECTION_HEADING)
    rest = text[start + len(SECTION_HEADING) :]
    next_heading = rest.find("\n## ")
    end = start + len(SECTION_HEADING) + (
        next_heading if next_heading != -1 else len(rest)
    )
    return text[start:end]


def test_brief_format_pins_narrative_declaration() -> None:
    section = _paragraph_length_section(_text())

    assert NARRATIVE_DECLARATION_PREFIX in section, (
        f"the narrative-declaration form {NARRATIVE_DECLARATION_PREFIX!r} "
        "must appear verbatim in the `## Paragraph length` section"
    )

    assert THRESHOLD_PHRASE in section, (
        f"the {THRESHOLD_PHRASE!r} paragraph-length threshold must appear "
        "in the `## Paragraph length` section"
    )

    assert EXEMPT_BULLET_EVIDENCE in section, (
        f"the exemption bullet {EXEMPT_BULLET_EVIDENCE!r} (name AND "
        "reason) must appear verbatim in the `## Paragraph length` "
        "section"
    )

    assert EXEMPT_BULLET_ALTERNATIVES in section, (
        f"the exemption bullet {EXEMPT_BULLET_ALTERNATIVES!r} (name AND "
        "reason) must appear verbatim in the `## Paragraph length` "
        "section"
    )


def test_brief_format_pins_comment_syntax_rationale() -> None:
    section = _paragraph_length_section(_text())

    assert COMMENT_SYNTAX_RATIONALE_SENTENCE in section, (
        "the sentence explaining why the narrative declaration is an "
        "HTML comment rather than a visible `N/A —` line must appear "
        "verbatim in the `## Paragraph length` section: "
        f"{COMMENT_SYNTAX_RATIONALE_SENTENCE!r}"
    )


def test_brief_format_pins_no_checker_classifies_sentence() -> None:
    section = _paragraph_length_section(_text())

    # Pinned so a later edit cannot quietly turn the declaration into a
    # machine-classified category -- a classifier would reintroduce the
    # judgment this rule exists to remove.
    assert NO_CHECKER_SENTENCE in section, (
        f"the sentence {NO_CHECKER_SENTENCE!r} must appear verbatim in "
        "the `## Paragraph length` section -- no checker may classify a "
        "paragraph as narrative; only the declaration is checked"
    )
