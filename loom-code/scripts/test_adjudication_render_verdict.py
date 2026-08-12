#!/usr/bin/env python3
"""Tests for adjudication_render.py (verdict mode).

Per loom-code TDD iron law: written first against not-yet-existing
render_verdict / render_verdict_html; first run is RED (ImportError).

Fixture mirrors adjudication_split.py's split_verdict() output shape:
source_text is a field block ("key: value" lines, severity first).
severity/where must be extracted from source_text verbatim -- never
recomputed -- per the adjudication-view protocol's carry-through rule.
"""

from adjudication_render import render_doc, render_verdict, render_verdict_html

FIXTURE_UNITS = [
    {
        "id": "u1",
        "heading": "file_a.py:12 security",
        "source_text": "severity: 🔴\ndimension: security\nwhere: file_a.py:12\n"
        "note: SQL injection risk",
        "anchors": ["🔴", "file_a.py:12"],
        "rendition": "SQL 注入風險。",
    },
    {
        "id": "u2",
        "heading": "file_b.py:40 naming",
        "source_text": "severity: 🟡\ndimension: naming\nwhere: file_b.py:40\n"
        "note: ambiguous name",
        "anchors": ["🟡", "file_b.py:40"],
        "rendition": "命名含糊 | 建議重新命名。",
    },
    {
        "id": "u3",
        "heading": "file_c.py:1 tests",
        "source_text": "severity: 🟢\ndimension: tests\nwhere: file_c.py:1\n"
        "note: nit, optional",
        "anchors": ["🟢", "file_c.py:1"],
        "rendition": "小建議，可選。",
    },
]


def _field(source_text, name):
    for line in source_text.splitlines():
        if line.startswith(f"{name}:"):
            return line.split(": ", 1)[1]
    raise AssertionError(f"fixture missing field {name!r}")


def test_verdict_table_rows_equal_findings_and_severity_verbatim():
    """RED anchor. Markdown table has exactly 3 data rows, each row's
    severity cell byte-equal to the source unit's severity field and
    錨點 cell byte-equal to its where field -- severity is copied,
    never recomputed -- and row order matches input order (never
    re-sorted)."""
    table = render_verdict(FIXTURE_UNITS)
    lines = table.strip("\n").split("\n")
    assert lines[0] == "| # | severity | 摘述 | 錨點 |"
    data_lines = lines[2:]
    assert len(data_lines) == 3
    for line, unit in zip(data_lines, FIXTURE_UNITS):
        assert unit["id"] in line
        severity = _field(unit["source_text"], "severity")
        assert f"| {severity} |" in line
        where = _field(unit["source_text"], "where")
        assert line.rstrip().endswith(f"| {where} |")


def test_verdict_table_row_order_matches_input_order():
    """Row order is source order, never re-sorted -- u2 (🟡, mid
    severity) sits between u1 (🔴) and u3 (🟢) in the fixture; a
    severity-bucketing bug would move it, this pins it stays put."""
    table = render_verdict(FIXTURE_UNITS)
    lines = table.strip("\n").split("\n")[2:]
    ids = [line.split("|")[1].strip() for line in lines]
    assert ids == ["u1", "u2", "u3"]


def test_verdict_table_escapes_pipe_in_rendition():
    """u2's rendition contains a literal `|` -- it must be escaped as
    `\\|` so the markdown table isn't broken into a phantom extra
    column (each data row keeps exactly 4 columns == 5 pipe chars)."""
    table = render_verdict(FIXTURE_UNITS)
    assert "命名含糊 \\| 建議重新命名。" in table
    lines = table.strip("\n").split("\n")[2:]
    assert len(lines) == 3
    for line in lines:
        # strip escaped pipes first -- an unescaped stray `|` would
        # inflate this to 6, splitting the row into a phantom 5th cell
        assert line.replace("\\|", "").count("|") == 5


def test_verdict_html_escapes_content_and_has_three_data_rows():
    """--html rendition: html.escape everything (rendition may carry
    attacker-reachable content from a translated finding), and exactly
    3 data rows (`<tr><td>` distinguishes a data row from the
    `<tr><th>` header row)."""
    evil_units = [dict(FIXTURE_UNITS[0], rendition="<script>alert(1)</script>")]
    evil_units += FIXTURE_UNITS[1:]
    html_out = render_verdict_html(evil_units)
    assert html_out.count("<tr><td>") == 3
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert "<script>alert(1)</script>" not in html_out
    assert "<style>" in html_out


def test_verdict_html_severity_and_where_verbatim_per_row():
    """Same byte-verbatim requirement as the markdown table, checked
    on the HTML rendition: severity and where cells must not be
    recomputed or normalized -- html.escape is the only transform."""
    html_out = render_verdict_html(FIXTURE_UNITS)
    for unit in FIXTURE_UNITS:
        severity = _field(unit["source_text"], "severity")
        where = _field(unit["source_text"], "where")
        assert f"<td>{severity}</td>" in html_out
        assert f"<td>{where}</td>" in html_out


def test_doc_mode_sanity_unaffected():
    """Sanity: verdict mode's addition must not disturb doc mode's
    existing render_doc export."""
    assert callable(render_doc)
