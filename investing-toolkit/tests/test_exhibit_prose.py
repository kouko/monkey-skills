"""test_exhibit_prose.py — canonical PROSE surface (exhibit_prose.py).

Offline unit tests for `exhibit_prose.prose_surface`, the stdlib
`html.parser`-based flattener that turns a raw 8-K earnings-exhibit HTML
document into ONE canonical prose-text surface: the flattened non-table text
that the downstream prose-KPI producer indexes with substring offsets. It is
the inverse of Route B's exhibit_tables.py — that walker EXTRACTS `<table>`
content; this one EXCLUDES it, keeping only the letter/narrative prose.

This is a text-surface layer only: NO number tokenization / parsing (that is
Task 2). Deterministic — the same input bytes always yield the same surface.

@req: this dispatch traces work by the plan's Task items, NOT registered
loom-spec REQ-ids, so per the implementer contract @req tags are omitted on
every test here (see report). No id is minted to fill the gap. Mirrors sibling
test_exhibit_tables.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"

if str(MARKETS_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(MARKETS_SCRIPTS))


def test_prose_surface_excludes_table_text():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    import exhibit_prose

    html = (
        "<html><body>"
        "<p>employees 1,576,000</p>"
        "<table><tr><td>999</td></tr></table>"
        "</body></html>"
    )
    prose = exhibit_prose.prose_surface(html)
    assert "employees 1,576,000" in prose
    assert "999" not in prose


def test_table_boundary_separates_flanking_prose():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # An excised <table> must leave a break so the prose runs on either side
    # cannot concatenate into one corrupt token — the substring surface the
    # downstream anti-fabrication confirm gate depends on.
    import exhibit_prose

    html = "<div>revenue of<table><tr><td>9</td></tr></table>$5.2B</div>"
    prose = exhibit_prose.prose_surface(html)
    # The two runs stay separated (no merged token) and the cell is excised.
    assert "revenue of$5.2B" not in prose
    assert "9" not in prose
    tokens = prose.split()
    assert "revenue" in tokens
    assert "of" in tokens
    assert "$5.2B" in tokens


def test_nested_table_stays_suppressed_until_outermost_closes():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # A boolean flag would un-suppress "C" once the INNER table closes; the
    # depth counter keeps every cell (A, B, C) suppressed until the OUTERMOST
    # table closes. This test FAILS under a boolean-depth regression.
    import exhibit_prose

    html = (
        "<p>outer prose</p>"
        "<table><tr><td>A<table><tr><td>B</td></tr></table>C</td></tr></table>"
        "<p>tail prose</p>"
    )
    prose = exhibit_prose.prose_surface(html)
    assert "outer prose" in prose
    assert "tail prose" in prose
    assert "A" not in prose
    assert "B" not in prose
    assert "C" not in prose


def test_self_closing_block_break_separates_flanking_prose():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # A self-closing block tag (<br/>) between two runs is a prose break, so
    # the flanking text cannot concatenate into one token.
    import exhibit_prose

    html = "<div>first run<br/>second run</div>"
    prose = exhibit_prose.prose_surface(html)
    assert "first runsecond run" not in prose
    tokens = prose.split()
    assert "first" in tokens
    assert "second" in tokens
