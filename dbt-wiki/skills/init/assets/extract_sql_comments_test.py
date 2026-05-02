#!/usr/bin/env python3
"""Smoke test for extract_sql_comments.py.

Run from this directory:

    python3 extract_sql_comments_test.py

Pure stdlib — no sqlglot needed (regex-only extractor).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parent / "extract_sql_comments.py"

# (sql, expected_subset_of_comments)
# expected = list of {line, kind, text} the script should produce (subset
# allowed — extras are OK as long as required ones are present).
CASES: list[tuple[str, list[dict]]] = [
    # 1. Simple line comment
    (
        """-- header comment
SELECT a FROM t
""",
        [{"line": 1, "kind": "line", "text": "header comment"}],
    ),
    # 2. Block comment spanning lines
    (
        """/* multi
   line block */
SELECT a FROM t
""",
        [{"line": 1, "kind": "block", "text": "multi | line block"}],
    ),
    # 3. Jinja comment
    (
        """{# WHY: incremental partition by date #}
SELECT a FROM {{ ref('t') }}
""",
        [{"line": 1, "kind": "jinja", "text": "WHY: incremental partition by date"}],
    ),
    # 4. Multiple comments mixed
    (
        """-- file header
{# warn: requires var('start_date') #}
WITH base AS (
    /* dedup logic — see ticket #1234 */
    SELECT * FROM t
)
SELECT a -- inline column note
FROM base
""",
        [
            {"line": 1, "kind": "line", "text": "file header"},
            {"line": 2, "kind": "jinja", "text": "warn: requires var('start_date')"},
            {"line": 4, "kind": "block", "text": "dedup logic — see ticket #1234"},
            {"line": 7, "kind": "line", "text": "inline column note"},
        ],
    ),
    # 5. Empty / whitespace-only comments are filtered
    (
        """--
/*  */
{#  #}
-- actual content
SELECT 1
""",
        [{"line": 4, "kind": "line", "text": "actual content"}],
    ),
    # 6. Chinese / multibyte content preserved
    (
        """-- 這個 model 處理 FSD 內部管報的 base layer
SELECT a FROM t
""",
        [{"line": 1, "kind": "line", "text": "這個 model 處理 FSD 內部管報的 base layer"}],
    ),
]


def run_script(sql: str) -> dict:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode != 0:
            return {"_test_error": f"exit={proc.returncode}: {proc.stderr[:200]}"}
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            return {"_test_error": f"non-JSON: {e}; raw={proc.stdout[:200]}"}
    finally:
        Path(path).unlink(missing_ok=True)


def check(actual: dict, expected_subset: list[dict]) -> tuple[bool, str]:
    if "_test_error" in actual:
        return False, actual["_test_error"]
    if "_error" in actual:
        return False, f"script reported _error: {actual['_error']}"
    actual_comments = actual.get("comments", [])
    # For each expected comment, find a matching one in actual
    for exp in expected_subset:
        match = next(
            (
                c
                for c in actual_comments
                if c["line"] == exp["line"]
                and c["kind"] == exp["kind"]
                and c["text"] == exp["text"]
            ),
            None,
        )
        if match is None:
            return False, f"missing expected {exp!r} (got: {actual_comments})"
    return True, "ok"


def main() -> int:
    failures = 0
    for i, (sql, expected) in enumerate(CASES, 1):
        actual = run_script(sql)
        ok, msg = check(actual, expected)
        status = "OK  " if ok else "FAIL"
        sql_oneline = " ".join(sql.split())[:60]
        print(f"[{i}/{len(CASES)}] {status} {sql_oneline}")
        if not ok:
            print(f"         {msg}")
            failures += 1
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
