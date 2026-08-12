"""Tests for the adjudication-view splitter — verdict mode.

Task 2 of docs/loom/plans/2026-08-12-adjudication-view.md. Verdict mode
splits a reviewer's structured verdict block (loom-code/skills/
requesting-code-review/SKILL.md §Verdict structure; docs-arm variant
adds `quote:` per requesting-docs-review/SKILL.md) into units-JSON: one
unit per finding (the unit-1:1 rule from adjudication-view.md applies
to findings the same way it applies to document sections).

Fixture below carries 3 findings, mixed severities (🔴/🟡/🟢), the last
one docs-arm shaped (`quote:` field, no `source:`/`origin:`) — the two
finding shapes the protocol says verdict mode must tolerate.
"""

from adjudication_split import split_verdict

FIXTURE = """standards_version: "1.2.3"

verdict: NEEDS_REVISION

dimension_scores:
  correctness: NEEDS_REVISION
  naming: PASS_WITH_NOTES
  ambiguity: PASS_WITH_NOTES

findings:
  - severity: 🔴 fatal
    dimension: correctness
    where: adjudication_split.py:42
    source: rubrics/quality-gate.md
    note: off-by-one in loop bound
    origin: none
    class: instruction
  - severity: 🟡 should-fix
    dimension: naming
    where: adjudication_split.py:10
    source: standards/naming-and-functions.md
    note: variable name `x` is unclear
    origin: none
    class: instruction
  - severity: 🟢 nit
    dimension: ambiguity
    where: SKILL.md:5
    class: instruction
    quote: "the widget may glow"
    note: modal verb ambiguous without support

summary:
  - branch touches one module
"""


def test_verdict_mode_parses_findings_with_where_and_severity():
    """3 findings -> 3 units, ordinal ids, verbatim severity/where/
    dimension carried through per the unit-1:1 rule."""
    units = split_verdict(FIXTURE)
    assert len(units) == 3
    assert [u["id"] for u in units] == ["u1", "u2", "u3"]

    assert units[0]["heading"] == "adjudication_split.py:42 correctness"
    assert "🔴" in units[0]["anchors"]
    assert "adjudication_split.py:42" in units[0]["anchors"]

    assert units[1]["heading"] == "adjudication_split.py:10 naming"
    assert "🟡" in units[1]["anchors"]

    assert units[2]["heading"] == "SKILL.md:5 ambiguity"
    assert "🟢" in units[2]["anchors"]
    assert "SKILL.md:5" in units[2]["anchors"]


def test_verdict_mode_renditions_start_empty():
    """`rendition` is filled later by the orchestrator-side translate
    step, never by the deterministic splitter — must start empty."""
    units = split_verdict(FIXTURE)
    for unit in units:
        assert unit["rendition"] == ""


def test_verdict_mode_docs_variant_quote_field_carried_in_source_text():
    """The docs-arm finding shape (`quote:`, no `source:`/`origin:`)
    must be tolerated — its `quote:` field lands verbatim in
    source_text so the lint step can later check it."""
    units = split_verdict(FIXTURE)
    assert "quote: \"the widget may glow\"" in units[2]["source_text"]
    # docs-arm finding has no source:/origin: fields — must not be
    # fabricated into the parsed block.
    assert "source:" not in units[2]["source_text"]
    assert "origin:" not in units[2]["source_text"]


def test_verdict_mode_source_text_is_nonempty_and_note_carried():
    """Every unit's source_text carries its note field verbatim."""
    units = split_verdict(FIXTURE)
    assert "off-by-one in loop bound" in units[0]["source_text"]
    assert units[0]["source_text"] != ""


NESTED_NOTE_FIXTURE = """findings:
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


def test_verdict_mode_note_block_literal_nested_fields_do_not_override_real_fields():
    """A `note: |` block-literal that quotes `dimension:`/`where:` lines at
    deeper indent (reviewers really do this when explaining an offending
    excerpt) must NOT be read as sibling fields — only lines at the same
    column as the finding's first field line are siblings. Real bug
    reproduced live by spec-reviewer: finding 1's heading came out as
    "SKILL.md:5 omission" (the nested note content) instead of
    "adjudication_split.py:194 correctness" (the finding's own fields)."""
    units = split_verdict(NESTED_NOTE_FIXTURE)
    assert len(units) == 2
    assert units[0]["heading"] == "adjudication_split.py:194 correctness"
    assert units[1]["heading"] == "other.py:1 naming"
