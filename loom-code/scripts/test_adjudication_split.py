"""Tests for the adjudication-view splitter — document mode.

Task 1 of docs/loom/plans/2026-08-12-adjudication-view.md. Doc mode
splits a markdown artifact on H2 sections into units-JSON per the
protocol schema (loom-code/skills/using-loom-code/protocols/
adjudication-view.md): unit id / heading / source_text / anchors /
rendition. Unit count == H2 count by construction (the unit-1:1 rule)
— this is a mechanical split, not a summarization, so the count must
be exact and each unit's source_text must be verbatim and non-empty.

Fixture below is brief-shaped: 3 H2 sections carrying a number, a
backticked term, and a snake_case identifier — the anchor kinds the
protocol names (numbers / enum tokens / backticked terms / CamelCase
or snake_case identifiers).
"""

from adjudication_split import split_document

FIXTURE = """# Brief: sample feature

Intro paragraph before any H2 section — not part of any unit.

## Problem statement

We have 42 open issues to resolve. Use `adjudication_split.py` for the
split step; the source_text field must remain verbatim.

## Smallest End State

v1 ships 3 deliverables. A snake_case_identifier appears in this
section for anchor extraction.

## Out of Scope

Anything involving CamelCaseThing is out of scope. See ISSUE_42 for
tracking.
"""


def test_doc_mode_unit_count_matches_h2_count():
    """Unit count must equal H2 section count (3) — the unit-1:1 rule
    holds by construction because the split is mechanical, not judged."""
    units = split_document(FIXTURE)
    assert len(units) == 3
    for unit in units:
        assert unit["source_text"].strip() != ""


def test_doc_mode_unit_ids_and_headings():
    """Unit ids are ordinal ("u1"...) and headings echo the H2 text."""
    units = split_document(FIXTURE)
    assert [u["id"] for u in units] == ["u1", "u2", "u3"]
    assert units[0]["heading"] == "Problem statement"
    assert units[1]["heading"] == "Smallest End State"
    assert units[2]["heading"] == "Out of Scope"


def test_doc_mode_rendition_starts_empty():
    """`rendition` is filled later by the orchestrator-side translate
    step, never by the deterministic splitter — must start empty."""
    units = split_document(FIXTURE)
    for unit in units:
        assert unit["rendition"] == ""


def test_anchor_extraction_number_lands_in_anchors():
    """A number from source_text must be echoed verbatim in anchors —
    this is what the lint step later checks the rendition against."""
    units = split_document(FIXTURE)
    assert "42" in units[0]["anchors"]


def test_anchor_extraction_backticked_term_lands_in_anchors():
    """A backticked term (verbatim carry-through, protocol §Verbatim
    carry-through) must land in anchors without its backtick
    delimiters."""
    units = split_document(FIXTURE)
    assert "adjudication_split.py" in units[0]["anchors"]


def test_anchor_extraction_snake_case_identifier_lands_in_anchors():
    """A snake_case identifier must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "snake_case_identifier" in units[1]["anchors"]


def test_anchor_extraction_camelcase_lands_in_anchors():
    """A CamelCase identifier must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "CamelCaseThing" in units[2]["anchors"]


def test_anchor_extraction_allcaps_lands_in_anchors():
    """An ALL-CAPS enum-style token must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "ISSUE_42" in units[2]["anchors"]


def test_anchor_extraction_dedup_repeated_token():
    """A repeated anchor candidate must appear once in anchors (the
    documented seen-set dedup)."""
    text = "## Repeats\n\nSee ISSUE_42 again: ISSUE_42 is the same issue.\n"
    units = split_document(text)
    assert units[0]["anchors"].count("ISSUE_42") == 1


FENCE_FIXTURE = """# Brief: sample feature

## Problem statement

Example command:

```
## Not a real heading -- inside a fence
echo hello
```

More text after the fence.

## Out of Scope

Nothing here.
"""


def test_h2_inside_fence_is_not_a_section_boundary():
    """A `## `-prefixed line inside a fenced code block must not create
    a spurious unit boundary -- the fence content stays inside the
    enclosing unit's source_text (protocol's unit-1:1-by-construction
    invariant)."""
    units = split_document(FENCE_FIXTURE)
    assert len(units) == 2
    assert "## Not a real heading -- inside a fence" in units[0]["source_text"]
    assert units[1]["heading"] == "Out of Scope"
