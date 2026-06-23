#!/usr/bin/env python3
"""Extract living-spec tag-comments from a source snippet.

A tag is a line comment of the form ``@req: <id>`` or
``@invariant-ref: <id>`` carried in a line comment (comment prefixes
``#``, ``//``, ``--``). Each tag attaches to the *nearest enclosing
test-function above it* — a line matching ``def test_...`` (the fixture
form for slice 1).

The importable entry point is ``extract_tags(text) -> list[dict]``,
returning one dict per test-function that carries >=1 tag, in source
order::

    [{"test": <name>, "reqs": [...], "invariant_refs": [...]}]

Pure stdlib (``re``).
"""
from __future__ import annotations

import re

# `def test_<name>(` — capture the function name. Leading whitespace
# allowed (nested test defs still attach by nearest-above).
_TEST_DEF_RE = re.compile(r"^\s*def\s+(test_\w*)\s*\(")

# A tag line: a line comment (`#`, `//`, `--`) carrying `@req:` or
# `@invariant-ref:` followed by an id token. The comment prefix must
# precede the `@tag`, so the line is genuinely a comment.
_TAG_RE = re.compile(
    r"(?:#|//|--)\s*@(req|invariant-ref):\s*(\S+)"
)

# A `@req:` binding line specifically (the drift lane ignores
# `@invariant-ref`). Captures the requirement id. The comment marker
# must start the line (after optional leading whitespace only) so the
# line genuinely IS a dedicated comment — an `@req:` buried inside a
# code line or a string literal (e.g. a test fixture's
# `"    # @req: REQ-1\n"`) is NOT a binding.
_REQ_TAG_RE = re.compile(r"^\s*(?:#|//|--)\s*@req:\s*(\S+)")

# Marker presence: a line comment carrying the `@req`/`@invariant-ref`
# marker, regardless of whether a `: <id>` follows. A line that hits
# this but NOT `_TAG_RE` is malformed (missing colon, or empty id).
_TAG_MARKER_RE = re.compile(
    r"(?:#|//|--)\s*@(?:req|invariant-ref)\b"
)


def extract_tags(text: str) -> list[dict]:
    """Return one dict per test-function carrying >=1 tag, source order.

    Each tag (``@req`` / ``@invariant-ref``) attaches to the nearest
    preceding ``def test_...`` line. Multiple tags under one test
    accumulate into that test's ``reqs`` / ``invariant_refs`` lists in
    encounter order.
    """
    results: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        def_match = _TEST_DEF_RE.match(line)
        if def_match:
            current = {
                "test": def_match.group(1),
                "reqs": [],
                "invariant_refs": [],
            }
            results.append(current)
            continue
        if current is None:
            # Tag before any test-function has no enclosing test; skip.
            continue
        tag_match = _TAG_RE.search(line)
        if tag_match:
            kind, tag_id = tag_match.group(1), tag_match.group(2)
            if kind == "req":
                current["reqs"].append(tag_id)
            else:
                current["invariant_refs"].append(tag_id)
    # Only test-functions that actually carry a tag are returned.
    return [
        r for r in results if r["reqs"] or r["invariant_refs"]
    ]


def find_malformed_tags(text: str) -> list[str]:
    """Return raw (stripped) comment lines carrying a malformed tag.

    A malformed tag is a ``@req`` / ``@invariant-ref`` marker that
    appears after a comment prefix but lacks a ``: <non-empty-id>``
    value — e.g. ``# @req:`` (colon, empty id) or ``# @req REQ-1``
    (no colon). Well-formed ``# @req: REQ-1`` lines are NOT reported.
    Lines are returned in source order.
    """
    malformed: list[str] = []
    for line in text.splitlines():
        if _TAG_MARKER_RE.search(line) and not _TAG_RE.search(line):
            malformed.append(line.strip())
    return malformed


def locate_bindings(text: str) -> list[dict]:
    """Return one record per ``@req`` binding with its line positions.

    Each record::

        {"test", "req", "body_start", "body_end", "binding_line"}

    All line numbers are 1-based. ``body_start`` is the line of the
    enclosing ``def test_...(``; ``body_end`` is the last line of the
    test's body, determined by INDENTATION: the body runs from the
    ``def test_...`` line down to (but not including) the first
    subsequent non-blank line whose indentation is <= the ``def`` line's
    indentation (a dedent to a sibling / module-level statement, e.g.
    the next ``def`` or a top-level line), or the last line of ``text``
    if no such dedent follows. Blank lines never end the body, and
    nested ``def`` helpers (more-indented) stay INSIDE the range — so an
    assertion below a nested helper is correctly covered for a later
    ``git log -L``. ``binding_line`` is the line of that ``@req:``
    comment. A test carrying two ``@req`` lines yields two records
    sharing test + body range but differing in binding_line/req.

    Only ``@req`` bindings are located; ``@invariant-ref`` is ignored
    (out of scope for the drift lane).
    """
    lines = text.splitlines()
    total = len(lines)

    def _indent(line: str) -> int:
        # Leading-whitespace width, counting raw leading chars (matching
        # the existing `\s*`-anchored parsing — no tab expansion).
        return len(line) - len(line.lstrip())

    def body_end_for(start: int) -> int:
        # `start` is 1-based; lines[start-1] is the `def test_...` line.
        def_indent = _indent(lines[start - 1])
        for idx in range(start, total):  # 0-based lines AFTER the def
            line = lines[idx]
            if not line.strip():
                continue  # blank lines never end the body
            if _indent(line) <= def_indent:
                return idx  # 1-based line before this dedent (idx == lineno-1)
        return total

    records: list[dict] = []
    current_test: str | None = None
    current_start = 0
    current_end = 0
    for idx, line in enumerate(lines):
        lineno = idx + 1
        def_match = _TEST_DEF_RE.match(line)
        if def_match:
            current_test = def_match.group(1)
            current_start = lineno
            current_end = body_end_for(lineno)
            continue
        if current_test is None:
            # A @req before any enclosing test has no body range; skip.
            continue
        req_match = _REQ_TAG_RE.match(line)
        if req_match:
            records.append(
                {
                    "test": current_test,
                    "req": req_match.group(1),
                    "body_start": current_start,
                    "body_end": current_end,
                    "binding_line": lineno,
                }
            )
    return records
