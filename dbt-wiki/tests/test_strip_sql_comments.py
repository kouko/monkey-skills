"""Tests for the literal-aware SQL comment stripper (G1 Task 1).

`strip_sql_comments` must drop `--` line comments and `/* */` block
comments while leaving string-literal contents untouched, and must not
reformat the surrounding SQL — every byte outside a removed comment span
is preserved verbatim.
"""
from __future__ import annotations

from pathlib import Path

from strip_sql_comments import strip_sql_comments

FIXTURE_MODEL = (
    Path(__file__).parent
    / "fixtures"
    / "l2-harness"
    / "models"
    / "marts"
    / "fct_avg_ratio_trap.sql"
)


def test_strips_comments_but_preserves_string_literals():
    sql = (
        "/* header block */\n"
        "select\n"
        "    '-- not a comment' as note,  -- real trailing comment\n"
        "    '/* also literal */' as tag,\n"
        "    col1\n"
        "from tbl  /* inline block */\n"
    )
    expected = (
        "\n"
        "select\n"
        "    '-- not a comment' as note,  \n"
        "    '/* also literal */' as tag,\n"
        "    col1\n"
        "from tbl  \n"
    )
    assert strip_sql_comments(sql) == expected


def test_preserves_escaped_quote_inside_literal():
    # '' is an escaped single quote inside a SQL literal; the -- after it
    # is still inside the string, not a comment.
    sql = "select 'it''s -- fine' as x  -- drop me\n"
    expected = "select 'it''s -- fine' as x  \n"
    assert strip_sql_comments(sql) == expected


def test_line_comment_without_trailing_newline():
    sql = "select 1 -- trailing eof comment"
    assert strip_sql_comments(sql) == "select 1 "


def test_non_comment_sql_is_unchanged():
    sql = "select a, b, c\nfrom t\nwhere a > 3\n"
    assert strip_sql_comments(sql) == sql


def test_strips_real_fixture_model():
    original = FIXTURE_MODEL.read_text()
    stripped = strip_sql_comments(original)

    # No comment tokens remain outside literals (this model has none).
    assert "--" not in stripped
    assert "/*" not in stripped
    assert "*/" not in stripped

    # The load-bearing SQL survives, non-empty.
    assert "sum(numerator) / sum(denominator) as weighted_ratio" in stripped
    assert "seed_avg_ratio" in stripped
    assert stripped.strip() != ""
