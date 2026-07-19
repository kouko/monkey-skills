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

import json
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


def test_locate_returns_token_span_quote():
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The number locator returns each candidate with a verbatim token and a
    # char_offset_span [start, end] into the canonical text. The load-bearing
    # invariant is the anchor the anti-fabrication gate verifies against:
    # text[start:end] must equal the token EXACTLY (byte-for-byte substring).
    import exhibit_prose

    text = "...the company had 1,576,000 employees at year end..."
    candidates = exhibit_prose.locate_numbers(text)

    match = [c for c in candidates if c["token"] == "1,576,000"]
    assert match, f"expected a 1,576,000 candidate, got {candidates!r}"
    cand = match[0]
    start, end = cand["start"], cand["end"]
    # Exact-substring invariant, asserted explicitly.
    assert text[start:end] == "1,576,000"
    assert text[start:end] == cand["token"]


def test_locate_cli_emits_located_numbers_json(tmp_path):
    # No living-spec REQ-id: this plan traces tasks by Task item, not REQ-ids.
    # The --locate CLI mode is the SUBPROCESS surface analysis-kpi crosses to
    # reach this data-markets locator (the analysis->data-markets boundary is
    # crossed by process, never in-process import). It reads the already-
    # canonical prose text from --text and emits a JSON list of located numbers
    # ({token,start,end}) to --out, mirroring exhibit_tables.py's --out JSON.
    # Because it runs locate_numbers on the given text WITHOUT re-flattening,
    # the char offsets stay relative to the input — the anchor the downstream
    # anti-fabrication gate verifies against.
    import exhibit_prose

    text = "The company had 1,576,000 employees and 3.56 diluted EPS."
    text_file = tmp_path / "canonical.txt"
    out_file = tmp_path / "located.json"
    text_file.write_text(text, encoding="utf-8")

    rc = exhibit_prose.main(
        ["--locate", "--text", str(text_file), "--out", str(out_file)]
    )
    assert rc == 0

    located = json.loads(out_file.read_text(encoding="utf-8"))
    tokens = [item["token"] for item in located]
    assert "1,576,000" in tokens
    assert "3.56" in tokens
    # Offset invariant preserved end-to-end through the CLI: text[start:end]
    # equals the token byte-for-byte for every located number.
    for item in located:
        assert text[item["start"]:item["end"]] == item["token"]
