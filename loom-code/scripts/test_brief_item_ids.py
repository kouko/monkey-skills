"""Structural pin for the `## Brief item identifiers` section of
`brainstorming/references/handoff-brief-format.md` (Task 1 of
`docs/loom/plans/2026-08-13-brief-item-addressability.md`).

handoff-brief-format.md is a prompt/contract artifact, not executable code:
nothing importable observes whether a brief author learns how to name an
item. This file IS the schema the author reads, so its correctness
condition is that the four declared identifier properties (form,
authored-not-derived, monotonic-never-reused, any-outcome-section scope),
their two rationales, and the declaration shape are all stated INSIDE the
`## Brief item identifiers` section.

Every assertion runs against a SLICE of that section, never the whole file:
a whole-file substring search would pass on a stray mention elsewhere in the
document (a recorded defect class in this repo), which would make the pin
report a convention the author never actually reads in context.

Stdlib + pytest only (pathlib, re).
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

SECTION_HEADING = "## Brief item identifiers"


def _identifier_section() -> str:
    """Return the body of `## Brief item identifiers`, heading excluded.

    The slice ends at the next level-2 heading (or EOF), so nothing outside
    the section can satisfy the assertions below.
    """
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    lines = HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8").splitlines()

    starts = [i for i, line in enumerate(lines) if line.strip() == SECTION_HEADING]
    assert len(starts) == 1, (
        f"handoff-brief-format.md must carry exactly one {SECTION_HEADING!r} "
        f"section; found {len(starts)}"
    )
    start = starts[0] + 1

    end = len(lines)
    for i in range(start, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    return "\n".join(lines[start:end])


def test_schema_declares_the_identifier_convention() -> None:
    section = _identifier_section()

    # (1) Form. Negating the form (e.g. to `BI<n>` or `<n>-BI`) drops this
    # literal, so the assertion pins the shape, not merely the letters "BI".
    assert "`BI-<n>`" in section, (
        "the identifier section must state the form literally as `BI-<n>`"
    )

    # (2) Authored, never derived. Negating the property ("derived from the
    # item's heading") removes the phrase this asserts.
    assert "never derived" in section, (
        "the identifier section must state that an id is authored, "
        "never derived from the item's heading or text"
    )

    # (3) Monotonic, never renumbered, never reused. Negating either half
    # ("may be renumbered" / "may be reused") removes the asserted phrase.
    assert "never renumbered" in section, (
        "the identifier section must state that ids are never renumbered"
    )
    assert "never reused" in section, (
        "the identifier section must state that a deleted item's number is "
        "never reused"
    )

    # (4) Scope: any outcome-declaring section. Narrowing the scope to
    # `## Smallest End State` alone removes the "not only" phrasing.
    assert "every section that declares an outcome" in section, (
        "the identifier section must scope ids to every outcome-declaring "
        "section of the brief"
    )
    assert "not only `## Smallest End State`" in section, (
        "the identifier section must say the scope is NOT only "
        "`## Smallest End State`"
    )

    # (5) Rationale A — monotonic-never-reused buys immutability under
    # insertion.
    assert "keeps the id immutable" in section, (
        "the identifier section must state why monotonic-never-reused "
        "exists: it keeps the id immutable when an item is inserted"
    )

    # (6) Rationale B — authored-not-derived stops the id desyncing on a
    # reword.
    assert "desyncing" in section and "reworded" in section, (
        "the identifier section must state why authored-not-derived exists: "
        "a derived id desyncs when the item's text is reworded"
    )

    # (7) Declaration shape: the id, then the human-readable item text, on
    # the SAME line. Splitting the example across two lines fails this.
    assert re.search(r"^- BI-\d+ — \S.*$", section, flags=re.MULTILINE), (
        "the identifier section must show a declaration whose id is followed "
        "by the human-readable item text on the same line"
    )
