"""Structural pin for the `## Brief item identifiers` section of
`brainstorming/references/handoff-brief-format.md` (Task 1 of
`docs/loom/plans/2026-08-13-brief-item-addressability.md`).

handoff-brief-format.md is a prompt/contract artifact, not executable code:
nothing importable observes whether a brief author learns how to name an
item. This file IS the schema the author reads, so its correctness
condition is that the declared identifier properties (form,
authored-not-derived, monotonic-never-reused, the named in-scope sections,
the prose-form declaration site, split/merge), their rationales, and the
declaration shape are all stated INSIDE the `## Brief item identifiers`
section — and that the rest of the document composes with them rather than
contradicting them: the `## Template` skeleton demonstrates the convention,
the per-section format entries point at it, and `## Anti-patterns` names its
failure modes.

Every assertion runs against a SLICE of one section, never the whole file:
a whole-file substring search would pass on a stray mention elsewhere in the
document (a recorded defect class in this repo), which would make the pin
report a convention the author never actually reads in context. Slicing
reuses `adjudication_split.split_document` rather than re-deriving a second
H2 scanner — this document nests `## `-prefixed lines inside fenced blocks,
which a fence-blind scan truncates silently (see
`test_section_slicer_is_fence_aware`).

Stdlib + pytest only (pathlib, re) plus the sibling `adjudication_split`.
"""
from __future__ import annotations

import re
from pathlib import Path

from adjudication_split import split_document

HANDOFF_BRIEF_FORMAT_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
)

SECTION_HEADING_TEXT = "Brief item identifiers"
SECTION_HEADING = f"## {SECTION_HEADING_TEXT}"


def _section_body(text: str, heading_text: str) -> str:
    """Return the body of the `## <heading_text>` section, heading excluded.

    The slice ends at the next level-2 heading (or EOF), so nothing outside
    the section can satisfy the assertions below. Boundary detection is
    delegated to `adjudication_split.split_document`, whose H2 scan is
    fence-aware per CommonMark close rules — this document nests `## `-
    prefixed lines inside fenced blocks (`## Template` holds a whole brief
    skeleton), and a fence-blind scan truncates those slices silently.
    """
    units = [u for u in split_document(text) if u["heading"] == heading_text]
    assert len(units) == 1, (
        f"the document must carry exactly one '## {heading_text}' section; "
        f"found {len(units)}"
    )
    return units[0]["source_text"]


def _brief_format_section(heading_text: str) -> str:
    """Return one section body of the real handoff-brief-format.md."""
    assert HANDOFF_BRIEF_FORMAT_MD.is_file(), (
        f"handoff-brief-format.md is absent at {HANDOFF_BRIEF_FORMAT_MD}"
    )
    return _section_body(
        HANDOFF_BRIEF_FORMAT_MD.read_text(encoding="utf-8"), heading_text
    )


def _identifier_section() -> str:
    return _brief_format_section(SECTION_HEADING_TEXT)


# A fenced block whose body carries `## `-prefixed lines is this file's own
# convention (`## Template` nests a whole brief skeleton in a fence), so a
# fence-blind boundary scan truncates a slice silently and the pins below
# would then run against a fragment while still reporting green.
FENCED_H2_FIXTURE = """\
## Target

before the fence

```markdown
## Problem

## Users
```

after the fence

## Next section

body of the next section
"""


def test_section_slicer_is_fence_aware() -> None:
    body = _section_body(FENCED_H2_FIXTURE, "Target")

    # The `## Problem` line inside the fence is content, not a boundary:
    # everything up to the REAL next H2 stays in the slice.
    assert "after the fence" in body, (
        "the slicer truncated the section at a `## ` line nested inside a "
        "fenced code block"
    )
    # The real boundary still holds — the slice is not the whole document.
    assert "body of the next section" not in body, (
        "the slicer must still stop at the next unfenced level-2 heading"
    )


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


def test_scope_names_the_known_in_scope_sections() -> None:
    """Scope is satisfiable by matching a section name, not by judgment."""
    section = _identifier_section()

    # The measured in-scope set is named, so an author matches rather than
    # adjudicates. Dropping any one of the three fails here.
    for heading in (
        "`## Smallest End State`",
        "`## What Becomes Obsolete`",
        "`## Decision`",
    ):
        assert heading in section, (
            f"the identifier section must name {heading} as a known "
            "in-scope section"
        )

    # The satisfaction rule itself. Negating it ("by adjudicating whether the
    # section declares an outcome") removes this phrase.
    assert "by matching a section name" in section, (
        "the identifier section must say the scope rule is satisfied by "
        "matching a section name"
    )

    # The general rule survives as an EXTENSION clause, not as a replacement:
    # a section outside the list is added to it, never treated as exempt. Who
    # extends it, and what the author does meanwhile, is pinned by
    # `test_unlisted_in_scope_section_states_an_actionable_mechanism`.
    assert "Extending the list above" in section, (
        "the identifier section must keep the general rule as an extension "
        "clause for sections not on the known list"
    )


def _scope_bullet() -> str:
    """Return the single `- **Scope: …**` bullet line of the identifier section.

    The mechanism below is asserted against ONE bullet, not the whole
    section: `## Open Questions` and the word "maintainer" could each appear
    somewhere else in the section while the scope rule itself still leaves an
    author with nothing to do, which is the defect this slice exists to
    prevent. Each bullet of this section is a single (long) source line, so
    the bullet's own first line IS its full body.
    """
    section = _identifier_section()
    bullets = [
        line for line in section.splitlines() if line.startswith("- **Scope:")
    ]
    assert len(bullets) == 1, (
        f"the identifier section must carry exactly one `- **Scope:` bullet; "
        f"found {len(bullets)}"
    )
    return bullets[0]


def test_unlisted_in_scope_section_states_an_actionable_mechanism() -> None:
    """An author meeting an unlisted outcome section can act without deciding.

    Three parts must be stated in the scope bullet itself. Each assertion
    below is worded so that NEGATING its part — not merely deleting it —
    removes the pinned text: "the author extends the list themselves"
    displaces the maintainer clause, an exemption displaces "never an
    exemption", and deferring the identifiers displaces "assign that
    section's identifiers now".
    """
    bullet = _scope_bullet()

    # Anti-exemption force, retained from the clause this supersedes.
    assert "never an exemption" in bullet, (
        "the scope bullet must state that a section's absence from the list "
        "is never an exemption from carrying identifiers"
    )

    # Part 1 — assign now, in this brief. Nothing about the unlisted section
    # defers the identifiers or blocks the brief.
    assert "assign that section's identifiers now" in bullet, (
        "the scope bullet must tell the author to assign the unlisted "
        "section's identifiers immediately, in their own brief"
    )

    # Part 2 — extending the canonical list is a maintainer action against
    # this shared file, NOT an author's mid-session edit. Negating this
    # ("the author extends the list themselves") removes both phrases.
    assert "a maintainer's edit to this file" in bullet, (
        "the scope bullet must say that extending the list is a maintainer's "
        "edit to this shared file"
    )
    assert "not something a brief's author makes mid-session" in bullet, (
        "the scope bullet must say the author does not make that edit "
        "mid-session"
    )

    # Part 3 — the unlisted section is recorded in the author's OWN brief, so
    # the pending extension is visible instead of silently absent. It is
    # recorded AS A QUESTION, which is what `## Open Questions` accepts (its
    # entry: "specific enough to answer in one round").
    assert (
        "record the unlisted section as an open question in this brief's own "
        "`## Open Questions`"
    ) in bullet, (
        "the scope bullet must tell the author where to record the unlisted "
        "section: this brief's own `## Open Questions`"
    )


def test_prose_form_sections_state_how_they_carry_an_identifier() -> None:
    """A section whose declared format is prose has a stated declaration site."""
    section = _identifier_section()

    assert "directly beneath the prose" in section, (
        "the identifier section must state where a prose-form section's "
        "identifiers are declared"
    )
    # Negating the property ("a prose-form section is exempt") removes this.
    assert "is not exempt" in section, (
        "the identifier section must state that a prose-form section is not "
        "exempt from carrying identifiers"
    )
    # Negating the property ("its prose is restructured into bullets")
    # removes this.
    assert "is not restructured" in section, (
        "the identifier section must state that a prose-form section's prose "
        "is not restructured"
    )
    assert "a single umbrella outcome gets a single line" in section, (
        "the identifier section must state the single-outcome case for a "
        "prose-form section"
    )


def test_split_and_merge_are_specified() -> None:
    """`never renumbered, never reused` is disambiguated for both cases."""
    section = _identifier_section()

    # Split. Negating the property ("one half keeps the original number")
    # removes both phrases.
    assert "split into two" in section, (
        "the identifier section must state what happens when one item is "
        "split into two"
    )
    assert "both halves take new numbers" in section, (
        "the identifier section must state that both halves of a split take "
        "new numbers"
    )
    assert "neither half inherits it" in section, (
        "the identifier section must state that neither half of a split "
        "inherits the original number"
    )

    # Merge. Negating the property ("the merged item keeps the lower number")
    # removes both phrases.
    assert "merged into one" in section, (
        "the identifier section must state what happens when two items are "
        "merged into one"
    )
    assert "both numbers are retired" in section, (
        "the identifier section must state that a merge retires both numbers"
    )
    assert "the merged item takes a new number" in section, (
        "the identifier section must state that the merged item takes a new "
        "number"
    )


def _template_skeleton() -> str:
    """Return the copy-paste brief skeleton inside `## Template`'s fence."""
    template = _brief_format_section("Template")
    fenced = re.search(r"^```markdown\n(.*?)^```", template, flags=re.S | re.M)
    assert fenced, "`## Template` must hold the skeleton in a ```markdown fence"
    return fenced.group(1)


def test_template_demonstrates_the_identifier_convention() -> None:
    """The skeleton an author copies obeys the convention it is governed by."""
    skeleton = _template_skeleton()

    # Placement: each outcome-declaring section of the skeleton carries at
    # least one declaration, in the declaration shape.
    for heading in ("Smallest End State", "Decision", "What Becomes Obsolete"):
        body = _section_body(skeleton, heading)
        assert re.search(r"^- BI-\d+ — ", body, flags=re.MULTILINE), (
            f"the Template's `## {heading}` placeholder must carry a "
            "`- BI-<n> — …` declaration"
        )

    ids = [
        int(n) for n in re.findall(r"^- BI-(\d+) — ", skeleton, flags=re.MULTILINE)
    ]
    assert len(ids) >= 4, (
        "the Template must demonstrate at least four declarations (one per "
        "outcome placeholder)"
    )
    # Monotonic across the whole brief, never restarted per section, never
    # duplicated. Negating the property (numbering restarting at BI-1 in the
    # second outcome section) breaks the strictly-increasing check.
    assert ids == sorted(set(ids)) and len(ids) == len(set(ids)), (
        f"the Template's identifiers must ascend monotonically across the "
        f"whole skeleton and never repeat; found {ids}"
    )


def test_section_entries_point_at_the_identifier_convention() -> None:
    """The per-section format entries do not contradict the new convention."""
    pointer = "Each outcome declared here takes a brief item identifier"

    # `## Smallest End State` and `## Decision` live under Required sections.
    required = _brief_format_section("Required sections")
    assert required.count(pointer) == 2, (
        "both outcome-declaring entries under `## Required sections` "
        "(`## Smallest End State`, `## Decision`) must point at the "
        f"identifier convention; found {required.count(pointer)}"
    )

    # `## What Becomes Obsolete` lives under Optional sections.
    optional = _brief_format_section("Optional sections")
    assert optional.count(pointer) == 1, (
        "the `## What Becomes Obsolete` entry under `## Optional sections` "
        f"must point at the identifier convention; found {optional.count(pointer)}"
    )


def test_anti_patterns_cover_the_identifier_failure_modes() -> None:
    """Every convention in this file carries ❌ entries; so does this one."""
    anti_patterns = _brief_format_section("Anti-patterns")

    for entry in (
        "Skipping the identifier on an in-scope item",
        "Renumbering on insert",
        "Reusing a retired number",
        "Deriving the identifier from the heading",
    ):
        assert f"❌ **{entry}" in anti_patterns, (
            f"the anti-pattern list must carry an ❌ entry for {entry!r}"
        )
