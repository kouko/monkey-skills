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

from adjudication_split import (
    iter_lines_outside_fences,
    split_document,
    split_verdict,
)

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
    """Unit count equals H2 section count, PLUS one when non-blank
    content precedes the first H2 (Fix 1, round-1 finding u1): FIXTURE
    has a title + intro paragraph before its first H2, so its preamble
    becomes u1. A fixture with no preamble keeps the original
    H2-count-only contract."""
    units = split_document(FIXTURE)
    assert len(units) == 4  # 3 H2 sections + 1 preamble unit
    for unit in units:
        assert unit["source_text"].strip() != ""

    no_preamble_text = "## Only Section\n\nBody text here.\n"
    no_preamble_units = split_document(no_preamble_text)
    assert len(no_preamble_units) == 1


def test_doc_mode_unit_ids_and_headings():
    """Unit ids are ordinal ("u1"...); u1 is the preamble (title text),
    remaining headings echo the H2 text."""
    units = split_document(FIXTURE)
    assert [u["id"] for u in units] == ["u1", "u2", "u3", "u4"]
    assert units[0]["heading"] == "Brief: sample feature"
    assert units[1]["heading"] == "Problem statement"
    assert units[2]["heading"] == "Smallest End State"
    assert units[3]["heading"] == "Out of Scope"


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
    assert "42" in units[1]["anchors"]


def test_anchor_extraction_backticked_term_lands_in_anchors():
    """A backticked term (verbatim carry-through, protocol §Verbatim
    carry-through) must land in anchors without its backtick
    delimiters."""
    units = split_document(FIXTURE)
    assert "adjudication_split.py" in units[1]["anchors"]


def test_anchor_extraction_snake_case_identifier_lands_in_anchors():
    """A snake_case identifier must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "snake_case_identifier" in units[2]["anchors"]


def test_anchor_extraction_camelcase_lands_in_anchors():
    """A CamelCase identifier must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "CamelCaseThing" in units[3]["anchors"]


def test_anchor_extraction_allcaps_lands_in_anchors():
    """An ALL-CAPS enum-style token must land in anchors verbatim."""
    units = split_document(FIXTURE)
    assert "ISSUE_42" in units[3]["anchors"]


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
    invariant). FENCE_FIXTURE's title-only preamble becomes u1 (Fix 1)."""
    units = split_document(FENCE_FIXTURE)
    assert len(units) == 3
    assert units[0]["heading"] == "Brief: sample feature"
    assert "## Not a real heading -- inside a fence" in units[1]["source_text"]
    assert units[2]["heading"] == "Out of Scope"


PLAN_FIXTURE = """# Plan: sample plan

Goal: ship the adjudication view.
Stage: implementation

## Task 1 — split

Do the split work.

## Task 2 — lint

Do the lint work.
"""


def test_doc_mode_preamble_before_first_h2_becomes_first_unit():
    """Fix 1 (round-1 finding u1): content before the first H2 (a
    plan's Goal/Stage header block) must not be silently dropped -- it
    becomes the first unit, heading = the H1 title text stripped of
    "# ", so the unit-1:1 rule's 'never silently dropped' clause holds
    for doc mode too."""
    units = split_document(PLAN_FIXTURE)
    assert len(units) == 3  # 2 H2 sections + 1 preamble unit
    assert units[0]["id"] == "u1"
    assert units[0]["heading"] == "Plan: sample plan"
    assert "Goal: ship the adjudication view." in units[0]["source_text"]
    assert "Stage: implementation" in units[0]["source_text"]
    assert units[1]["id"] == "u2"
    assert units[1]["heading"] == "Task 1 — split"
    assert units[2]["heading"] == "Task 2 — lint"


NO_TITLE_PREAMBLE_FIXTURE = """Date: 2026-08-12
Stage: draft

## Section A

Body text.
"""


def test_doc_mode_preamble_without_h1_title_gets_generic_heading():
    """A preamble that doesn't start with `# ` (a brief's Date/Stage
    lines, no title line) gets the generic "(preamble)" heading."""
    units = split_document(NO_TITLE_PREAMBLE_FIXTURE)
    assert units[0]["heading"] == "(preamble)"
    assert "Date: 2026-08-12" in units[0]["source_text"]
    assert "Stage: draft" in units[0]["source_text"]


def test_doc_mode_blank_preamble_produces_no_preamble_unit():
    """Empty/whitespace-only preamble -> no preamble unit (unchanged
    behavior) -- the blank lines before the H2 carry no content to
    lose."""
    text = "\n\n## Only Section\n\nBody.\n"
    units = split_document(text)
    assert len(units) == 1
    assert units[0]["heading"] == "Only Section"


# Verdict-mode fixture reproducing the T2 finding (round-1 finding u2):
# a `note: |` block-literal quoting `dimension:`/`where:` lines at
# deeper indent than the finding's own field column. Mirrors
# NESTED_NOTE_FIXTURE in test_adjudication_split_verdict.py.
NESTED_NOTE_VERDICT_FIXTURE = """findings:
  - severity: 🔴 fatal
    dimension: correctness
    where: adjudication_split.py:194
    note: |
      reviewer quoted the verdict schema example while explaining:
      dimension: omission
      where: SKILL.md:5
  - severity: 🟡 should-fix
    dimension: naming
    where: other.py:1
"""


def test_verdict_mode_note_block_literal_body_preserved_in_source_text():
    """Fix 2 (round-1 finding u2): `note: |` continuation lines (indent
    deeper than the sibling column) must not vanish from source_text --
    they are appended to the preceding field's value so the full note
    body survives, instead of being silently dropped."""
    units = split_verdict(NESTED_NOTE_VERDICT_FIXTURE)
    assert (
        "reviewer quoted the verdict schema example while explaining:"
        in units[0]["source_text"]
    )
    assert "dimension: omission" in units[0]["source_text"]
    assert "where: SKILL.md:5" in units[0]["source_text"]
    # Nested note content must still not override the real sibling
    # fields (regression guard shared with test_adjudication_split_verdict.py).
    assert units[0]["heading"] == "adjudication_split.py:194 correctness"


# --- the shared fence scan, and the two consumers it replaced ---

# Six CommonMark fence cases, each a shape the two former copies of this
# state machine had to agree on, held as (name, text, expected-prose-lines).
# Six separate fixtures rather than one blob: a single document exercising
# all six would let one misclassified case hide inside the others' output.
#
# The expected list is written out in full per case rather than derived from
# a marker token. The 4-space case is why: there the ```` ``` ```` line is
# itself ordinary content, so no rule of the form "lines tagged KEEP" can
# state the expectation without the fixture and the rule disagreeing about
# which lines those are.
_FENCE_CASES = (
    (
        "a nested SHORTER fence does not close a longer outer one",
        "a\n"
        "````\n"
        "inside\n"
        "```\n"
        "still inside — a shorter marker cannot close a longer fence\n"
        "````\n"
        "b\n",
        ["a", "b"],
    ),
    (
        "a ``` line does not close a ~~~ fence",
        "a\n"
        "~~~\n"
        "inside\n"
        "```\n"
        "still inside — wrong fence character\n"
        "~~~\n"
        "b\n",
        ["a", "b"],
    ),
    (
        "a fence indented up to 3 spaces is still a fence",
        "a\n"
        "   ```\n"
        "inside\n"
        "   ```\n"
        "b\n",
        ["a", "b"],
    ),
    (
        "4 spaces of indent is an indented code block, never a fence — so "
        "the marker line is content and nothing after it is hidden",
        "a\n"
        "    ```\n"
        "b\n",
        ["a", "    ```", "b"],
    ),
    (
        "an unterminated fence swallows the rest of the document",
        "a\n"
        "```\n"
        "inside\n"
        "to the end of the file\n",
        ["a"],
    ),
    (
        "a closing fence longer than its opener still closes",
        "a\n"
        "```\n"
        "inside\n"
        "`````\n"
        "b\n",
        ["a", "b"],
    ),
)


def test_fence_scan_across_commonmark_edge_cases():
    """`iter_lines_outside_fences` classifies every CommonMark fence edge
    case the two former copies of this scan had to agree on.

    This scan lived twice — here and verbatim in `check_scenario_
    coverage.py`, which also carried its own copy of `FENCE_RE`. The two
    were differential-tested across these six cases and found identical on
    all six, which is what made the duplication indefensible: there was no
    divergent tolerance to preserve, only two state machines to keep in
    step. The copies are now one import, and these cases are its test.

    Each case asserts the WHOLE prose-line set in order, not merely that a
    fenced line is absent: a scan that hid everything after the first fence
    would satisfy every absence assertion while destroying the document.
    """
    for name, text, expected in _FENCE_CASES:
        prose = [content for _offset, content in iter_lines_outside_fences(text)]
        assert prose == expected, (
            f"{name}: fence scan misclassified\n"
            f"expected: {expected}\ngot:      {prose}"
        )


def test_fence_scan_offsets_index_into_the_source():
    """The yielded offset is the line's start index into the source text —
    the coordinate `_iter_h2_matches` slices section bodies with, and the
    one `collect_brief_item_ids` counts newlines against for a line number.
    A generator yielding an ordinal of surviving lines instead would pass
    every classification assertion above and silently corrupt both.
    """
    text = _FENCE_CASES[0][1]
    for offset, content in iter_lines_outside_fences(text):
        assert text[offset:offset + len(content)] == content, (
            f"offset {offset} does not index to {content!r}"
        )
