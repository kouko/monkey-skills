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
