#!/usr/bin/env python3
"""Tests for Task 3's fail-loud postcondition: a rendered `doc` page whose
`<div class="rendition">` region still carries an unconverted markdown
marker (a surviving `**bold**` pair, or a literal ``` fence) must make
`main()` return non-zero and write no output file at all.

What this check catches, precisely: a FUTURE regression in a
CURRENT-format page -- a page whose rendition IS wrapped in today's
`<div class="rendition">` marker, but whose text was not actually run
through markdown-it conversion. It does NOT catch a genuinely stale
pre-markdown-it copy of this script: that copy wraps a rendition in
`<p class="rendition">...</p>`, never `<div class="rendition">`, so
`_iter_rendition_regions` finds zero regions on that page and this
check is structurally silent on it. This is by design, not a gap to
close here -- a stale copy carries no postcondition of its own to run
in the first place, so the version stamp (Task 1/2), not this check,
is what surfaces it. The brief's own Alternatives-Considered table
says this plainly: "No (stale copy lacks the check) -- catches future
conversion regressions" is this row's own "Catches THIS bug?" answer.

Two binding memory entries shape every test here:
- a-mutation-test-must-run-the-production-assertion.md: every test drives
  the PRODUCTION entry point `main(argv)`, never the helper in isolation,
  so a future revert of the call site (not just the helper) fails these
  tests -- not just leaves them decoratively green.
- a-mechanical-check-can-go-green-by-skipping.md: a scan keyed on a
  literal marker (`<div class="rendition">`) can go green by matching
  NOTHING if that marker's shape drifts -- which is exactly what
  happens, by design, against a stale `<p class="rendition">` page (see
  above). test_no_skip_probe below proves the scan is actually anchored
  to the marker `_assert_rendition_converted` depends on, for the
  current-format case this check DOES own, not merely "raised no
  exception".

Per loom-code TDD iron law: written FIRST against the not-yet-existing
postcondition, so the first run is RED.
"""

import json

import adjudication_render
from adjudication_render import _assert_rendition_converted, main

# `** bold **` -- space-flanked on both sides of the delimiter run -- is a
# CommonMark case markdown-it deliberately does NOT convert to <strong>:
# left/right-flanking rules require the delimiter to hug non-whitespace.
# It survives to the rendered page as literal text: a CURRENT-format
# page (`<div class="rendition">`) whose rendition text was never
# properly converted -- the future-regression shape this check exists
# to catch. It is NOT a stand-in for a genuinely stale pre-markdown-it
# copy's output, which wraps its rendition in `<p class="rendition">`
# instead and is therefore invisible to this check by design (see the
# module docstring).
UNCONVERTED_UNITS = [
    {
        "id": "u1",
        "heading": "Task 3 — postcondition",
        "source_text": "plain source text, no markers here.",
        "anchors": [],
        "rendition": "some text ** bold ** and more",
    },
]

CODE_SPAN_UNITS = [
    {
        "id": "u1",
        "heading": "Task 3 — postcondition",
        "source_text": "plain source text, no markers here.",
        "anchors": [],
        "rendition": "an example of the bug: `**bold**` shown inline",
    },
]

SOURCE_TEXT_BOLD_UNITS = [
    {
        "id": "u1",
        "heading": "Task 3 — postcondition",
        "source_text": "The rule requires **bold** emphasis in English.",
        "anchors": [],
        "rendition": "converted rendition text, nothing to flag here.",
    },
]

# An unmatched ` ```mermaid ` fence -- no closing ``` -- never becomes a
# `<div class="mermaid">`; markdown-it leaves the whole line literal
# inside a `<p>`. Same severity as the bold-pair case (OQ-2): one
# marker kind or the other, same exit code.
FENCE_UNITS = [
    {
        "id": "u1",
        "heading": "Task 3 — postcondition",
        "source_text": "plain source text, no markers here.",
        "anchors": [],
        "rendition": "unmatched fence ```mermaid graph LR only one run",
    },
]


def _write_units(tmp_path, units):
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(units, ensure_ascii=False), encoding="utf-8")
    return units_path


def test_unconverted_rendition_exits_nonzero_and_writes_no_file(tmp_path, capsys):
    units_path = _write_units(tmp_path, UNCONVERTED_UNITS)
    out_path = tmp_path / "out.html"

    result = main(["doc", str(units_path), "-o", str(out_path)])

    assert result != 0
    assert not out_path.exists()
    err = capsys.readouterr().err
    assert "u1" in err
    assert "**" in err


def test_code_span_bold_is_not_flagged(tmp_path):
    units_path = _write_units(tmp_path, CODE_SPAN_UNITS)
    out_path = tmp_path / "out.html"

    result = main(["doc", str(units_path), "-o", str(out_path)])

    assert result == 0
    assert out_path.exists()


def test_source_text_bold_in_原文_block_is_not_flagged(tmp_path):
    units_path = _write_units(tmp_path, SOURCE_TEXT_BOLD_UNITS)
    out_path = tmp_path / "out.html"

    result = main(["doc", str(units_path), "-o", str(out_path)])

    assert result == 0
    assert out_path.exists()


def test_unmatched_fence_exits_nonzero_and_writes_no_file(tmp_path, capsys):
    units_path = _write_units(tmp_path, FENCE_UNITS)
    out_path = tmp_path / "out.html"

    result = main(["doc", str(units_path), "-o", str(out_path)])

    assert result != 0
    assert not out_path.exists()
    err = capsys.readouterr().err
    assert "u1" in err
    assert "```" in err


def test_no_skip_probe(tmp_path, capsys):
    """Proves the scan actually matched a rendition region rather than
    passing by matching nothing.

    Part 1 drives the production entry point on a genuine violation --
    the same shape the RED test proves fails today -- so a future revert
    of main()'s call site (per the mutation-test memory) still fails this
    test, not just a helper-level assertion.

    Part 2 calls the helper directly on a minimal
    `<div class="rendition">...</div>` region containing a violation and
    asserts it returns a non-None `(unit_id, marker)` violation --
    proving the scan engine itself engages on that literal marker shape
    (per the no-skip-by-shape-drift memory), independent of the rest of
    the page template.
    """
    units_path = _write_units(tmp_path, UNCONVERTED_UNITS)
    out_path = tmp_path / "out.html"
    assert main(["doc", str(units_path), "-o", str(out_path)]) != 0
    assert not out_path.exists()

    violation = _assert_rendition_converted(
        '<div class="rendition">some text ** bold ** and more</div>'
    )
    assert violation is not None
