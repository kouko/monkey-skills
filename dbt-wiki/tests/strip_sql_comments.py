"""Literal-aware SQL comment stripper (G1 Task 1).

Removes `--` line comments and `/* */` block comments from a SQL string
without reformatting anything else: every byte outside a removed comment
span is preserved verbatim. Comment tokens that appear *inside* a
single-quoted string literal are left alone, since there they are data,
not comments.

This deliberately avoids sqlglot's `.sql(comments=False)` render path,
which re-renders (and thus reformats) the whole statement — that would
confound an ablation whose whole point is to change only the comments.
"""
from __future__ import annotations


def strip_sql_comments(sql_text: str) -> str:
    out: list[str] = []
    i = 0
    n = len(sql_text)

    while i < n:
        ch = sql_text[i]

        if ch == "'":
            # Copy the whole single-quoted literal verbatim, treating ''
            # as an escaped quote that stays inside the literal.
            out.append(ch)
            i += 1
            while i < n:
                c = sql_text[i]
                if c == "'":
                    if i + 1 < n and sql_text[i + 1] == "'":
                        out.append("''")
                        i += 2
                        continue
                    out.append(c)
                    i += 1
                    break
                out.append(c)
                i += 1
            continue

        if ch == "-" and i + 1 < n and sql_text[i + 1] == "-":
            # Line comment: drop through end of line, keep the newline.
            j = sql_text.find("\n", i)
            i = n if j == -1 else j
            continue

        if ch == "/" and i + 1 < n and sql_text[i + 1] == "*":
            # Block comment: drop through the closing */ (inclusive).
            j = sql_text.find("*/", i + 2)
            i = n if j == -1 else j + 2
            continue

        out.append(ch)
        i += 1

    return "".join(out)
