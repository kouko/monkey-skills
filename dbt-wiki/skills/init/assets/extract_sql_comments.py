#!/usr/bin/env python3
"""Extract SQL + jinja comments from a dbt model's raw_code, preserving line numbers.

dbt-wiki ships this script as a plugin asset alongside extract_column_lineage.py.
Whereas the lineage script reads `target/compiled/*.sql` (jinja already expanded),
this script reads the **raw model file** (e.g. `dbt/models/marts/fct_orders.sql`)
to preserve jinja comments (`{# ... #}`) which `dbt compile` strips.

Captured comment forms:
- `-- single line` — to end of line
- `/* multi-line block */` — across lines
- `{# jinja comment #}` — across lines (raw_code only; gone in compiled)

Usage
-----
    python3 extract_sql_comments.py <raw_sql_path>
    python3 extract_sql_comments.py --batch <models_dir>

Output (single mode, JSON):
    {
        "path": "models/marts/fct_orders.sql",
        "comments": [
            {"line": 1, "kind": "line", "text": "joins Shopify webhook with customer table"},
            {"line": 8, "kind": "block", "text": "ADR-2024-03: materialization decision"},
            {"line": 14, "kind": "jinja", "text": "WARNING: incremental hash must include event_at"}
        ]
    }

Output (batch mode, JSONL — one record per .sql under <models_dir>):
    {"path": "...", "comments": [...]}

Implementation notes
--------------------
- Pure regex; no sqlglot dependency (so works on jinja-laden raw_code).
- We process the file as a string with running line counter; multi-line
  comments use the line of their opening token (typical convention).
- We DO NOT classify comments by structural position (header / pre-CTE
  / inline) — that requires AST analysis sqlglot can't do reliably on
  jinja-laden SQL. Line number + raw text is enough for LLM query.
- We strip the comment markers (`-- `, `/* */`, `{# #}`) and trim
  whitespace; output `text` is the user's actual prose.
- Strings containing comment-like syntax are NOT excluded (e.g. `'-- not a comment'`
  inside a string literal could false-match). For v1, this is acceptable —
  dbt SQL rarely embeds comment syntax in string literals; the cost of a
  proper tokenizer outweighs the rare false positive.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

# Order matters: jinja first (most specific), then block, then line.
# Each pattern captures the comment body (group 1) for `text` field.
PATTERNS = [
    ("jinja", re.compile(r"\{#(.*?)#\}", re.DOTALL)),
    ("block", re.compile(r"/\*(.*?)\*/", re.DOTALL)),
    ("line", re.compile(r"--([^\n]*)")),
]


def extract_comments(sql: str) -> list[dict[str, Any]]:
    """Return list of {line, kind, text} entries, sorted by line then kind."""
    comments: list[dict[str, Any]] = []
    seen_spans: list[tuple[int, int]] = []  # (start, end) of already-claimed regions

    for kind, pat in PATTERNS:
        for m in pat.finditer(sql):
            start, end = m.span()
            # Skip if this match overlaps with a previously-claimed comment
            # (handles e.g. `-- {# something #}` where line wins, or
            # `/* {# nested #} */` where block wins because it ran first
            # — but jinja runs first per PATTERNS order, so jinja inside
            # block becomes its own entry. Edge cases like that are rare;
            # we err toward overcounting, not undercounting.)
            if any(s <= start < e or s < end <= e for s, e in seen_spans):
                continue
            seen_spans.append((start, end))

            line_num = sql.count("\n", 0, start) + 1
            text = m.group(1).strip()
            if not text:
                continue
            # Collapse internal whitespace runs to single spaces but
            # preserve newlines as " | " so multi-line comments stay readable.
            # Order matters: convert newlines first, THEN collapse spaces, so
            # leading whitespace on continuation lines doesn't bleed into "  ".
            text = re.sub(r"\s*\n\s*", " | ", text)
            text = re.sub(r"[ \t]+", " ", text).strip(" |")
            comments.append({"line": line_num, "kind": kind, "text": text})

    # Sort by line, then by kind for deterministic output
    comments.sort(key=lambda c: (c["line"], c["kind"]))
    return comments


def _run_single(path: str) -> int:
    try:
        sql = Path(path).read_text()
    except FileNotFoundError:
        print(json.dumps({"_error": f"file not found: {path}"}))
        return 1
    result = {"path": path, "comments": extract_comments(sql)}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def _run_batch(directory: str) -> int:
    root = Path(directory)
    if not root.is_dir():
        print(json.dumps({"_error": f"not a directory: {directory}"}))
        return 1
    for sql_path in sorted(root.rglob("*.sql")):
        try:
            sql = sql_path.read_text()
            comments = extract_comments(sql)
        except Exception as e:
            print(
                json.dumps(
                    {
                        "path": str(sql_path.relative_to(root)),
                        "_error": f"{type(e).__name__}: {e}",
                    },
                    ensure_ascii=False,
                )
            )
            continue
        print(
            json.dumps(
                {
                    "path": str(sql_path.relative_to(root)),
                    "comments": comments,
                },
                ensure_ascii=False,
            )
        )
    return 0


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if args[0] == "--batch":
        if len(args) < 2:
            print(json.dumps({"_error": "usage: --batch <dir>"}))
            return 1
        return _run_batch(args[1])
    return _run_single(args[0])


if __name__ == "__main__":
    sys.exit(main())
