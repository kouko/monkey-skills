"""Collect living-spec ``@req`` bindings across a source tree.

`collect_bindings(root, patterns)` globs test files under ``root``,
runs `living_spec_tags.locate_bindings` on each, and tags every
returned binding with its file path RELATIVE to ``root`` under the
``"file"`` key — so the downstream git adapter can pass it to
``git -C root log -L <range>:<file>``.

Files are processed in sorted order, so the flat result list is
deterministic. Only files matching ``patterns`` are read; everything
else (including non-test files carrying ``@req``-looking comments) is
ignored. Pure file I/O plus the locator — no git here.

Stdlib only (pathlib, re, io, tokenize).
"""
from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path

from living_spec_tags import locate_bindings

# ANCHORED malformed-tag detection — mirrors `living_spec_tags`'
# `_REQ_TAG_RE` anchoring (`^\s*(?:#|//|--)\s*...`) rather than the
# NON-anchored `find_malformed_tags`. The comment marker must START
# the line (after optional indent only), so a malformed `@req` buried
# inside a string literal (a test fixture's `"# @req"`) is NOT flagged
# over the real repo. A line is malformed iff it hits the MARKER form
# but NOT the VALID form (`@(req|invariant-ref): <non-empty-id>`).
_ANCHORED_MARKER_RE = re.compile(
    r"^\s*(?:#|//|--)\s*@(?:req|invariant-ref)\b"
)
_ANCHORED_VALID_RE = re.compile(
    r"^\s*(?:#|//|--)\s*@(?:req|invariant-ref):\s*(\S+)"
)

# Directory names that hold vendored / generated code we must not walk
# into — a `git log -L` per test file there is wasted work.
_VENDOR_DIRS = frozenset(
    {"node_modules", "site-packages", "__pycache__", "venv", ".eggs"}
)


def _real_comment_lines(text: str) -> set[int]:
    """1-based line numbers carrying a genuine ``#`` comment token.

    Tokenizes ``text`` and returns every line number that hosts a
    ``tokenize.COMMENT`` token. A ``# @req:`` buried inside a string
    literal (a test fixture's triple-quoted source) is part of a STRING
    token, NOT a COMMENT token, so its line is absent from the set —
    that is what lets the structural collectors below reject it even
    though it sits at column 0 on its own line, where the anchored
    line-regex alone cannot.

    A malformed ``.py`` fixture (one that does not tokenize) yields an
    empty set rather than crashing the walk: ``tokenize.TokenError``
    and ``IndentationError`` are caught and treated as "no real
    comments". Partial tokens emitted before a mid-stream failure are
    discarded so the result reflects only a cleanly tokenizable file.
    """
    lines: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                lines.add(tok.start[0])
    except (tokenize.TokenError, IndentationError):
        return set()
    return lines


def _is_vendored(relative_parts: tuple[str, ...]) -> bool:
    """True if any directory component is a dot-dir or a vendor dir."""
    # The last part is the file name; only directory components count.
    for part in relative_parts[:-1]:
        if part.startswith(".") or part in _VENDOR_DIRS:
            return True
    return False


def collect_bindings(
    root: Path,
    patterns: tuple[str, ...] = ("test_*.py", "*_test.py"),
) -> list[dict]:
    """Return all ``@req`` bindings under ``root``, tagged with ``file``.

    Recursively globs every test file matching any of ``patterns``,
    runs `locate_bindings` on its text, and stamps each binding with
    its path relative to ``root`` under ``"file"``. Files are sorted
    (and de-duplicated across overlapping patterns) before processing,
    so the flat list is deterministic. Non-matching files are ignored.
    """
    root = Path(root)
    matched = {
        path
        for pattern in patterns
        for path in root.rglob(pattern)
        if path.is_file()
        and not _is_vendored(path.relative_to(root).parts)
    }

    bindings: list[dict] = []
    for path in sorted(matched):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        for binding in locate_bindings(text):
            binding["file"] = relative
            bindings.append(binding)
    return bindings


def collect_structural_records(
    root: Path,
    patterns: tuple[str, ...] = ("test_*.py", "*_test.py"),
) -> list[dict]:
    """Return one ``extract_tags``-shaped record per tagged test.

    Regroups `collect_bindings` output — one record per ``@req``
    binding — by ``(file, test)`` into the structural shape that
    `find_structural_violations` and `generate_index` consume::

        [{"test": <name>, "reqs": [...], "invariant_refs": []}]

    Reusing `collect_bindings` means the ANCHORED `locate_bindings`
    path does the parsing, so a ``@req:`` buried in a string literal
    (a test fixture) is NOT a binding and never reaches the index —
    unlike a naive `extract_tags` over the tree, whose non-anchored
    ``.search`` would mistake the fixture string for a real binding.

    ``invariant_refs`` is always ``[]``: the drift lane's locator
    tracks only ``@req``, and the structural-violation + index
    consumers read only ``reqs`` + ``test``. Records preserve
    sorted-by-file order, so the result is deterministic.

    Anchoring alone (``locate_bindings``) rejects an ``@req:`` sharing a
    line with code, but NOT one sitting at column 0 of its own line
    *inside* a triple-quoted string literal — the shape a fixture in a
    test that exercises the ``@req`` parser carries. So for ``.py``
    files this re-reads each file's text and drops any binding whose
    ``binding_line`` is not a real ``#``-comment line per
    `_real_comment_lines` (token-aware). Non-``.py`` files pass through
    unchanged (no Python tokenization applies).
    """
    root = Path(root)
    records: list[dict] = []
    by_key: dict[tuple[str, str], dict] = {}
    matched = {
        path
        for pattern in patterns
        for path in root.rglob(pattern)
        if path.is_file()
        and not _is_vendored(path.relative_to(root).parts)
    }
    for path in sorted(matched):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        comment_lines = (
            _real_comment_lines(text)
            if path.suffix == ".py"
            else None
        )
        for binding in locate_bindings(text):
            if (
                comment_lines is not None
                and binding["binding_line"] not in comment_lines
            ):
                continue  # @req lives inside a string literal, not a comment
            key = (relative, binding["test"])
            record = by_key.get(key)
            if record is None:
                record = {
                    "test": binding["test"],
                    "reqs": [],
                    "invariant_refs": [],
                }
                by_key[key] = record
                records.append(record)
            record["reqs"].append(binding["req"])
    return records


def collect_malformed(
    root: Path,
    patterns: tuple[str, ...] = ("test_*.py", "*_test.py"),
) -> list[str]:
    """Return raw malformed ``@req`` / ``@invariant-ref`` comment lines.

    Walks the same test files as `collect_bindings` (same patterns +
    vendored-dir exclusion) and returns each stripped line that carries
    an ANCHORED ``@req`` / ``@invariant-ref`` marker but lacks a usable
    ``: <id>`` value — e.g. ``# @req`` (no colon) or ``# @req:`` (empty
    id). Detection is ANCHORED (the comment marker must start the line
    after optional indent), so a malformed marker that shares a line
    with code is NOT reported. But an anchored malformed marker sitting
    at column 0 of its own line *inside* a triple-quoted string literal
    (a fixture in a test that exercises the parser) still matches the
    anchored regex — so for ``.py`` files this additionally requires the
    line to be a real ``#``-comment line per `_real_comment_lines`
    (token-aware). Non-``.py`` files keep the anchored-only check (no
    Python tokenization applies). Unlike the non-anchored
    `living_spec_tags.find_malformed_tags`, this is safe over the real
    repo. Files are processed in sorted order, so the flat list is
    deterministic. `find_structural_violations` consumes this as its
    ``malformed`` argument.
    """
    root = Path(root)
    matched = {
        path
        for pattern in patterns
        for path in root.rglob(pattern)
        if path.is_file()
        and not _is_vendored(path.relative_to(root).parts)
    }

    malformed: list[str] = []
    for path in sorted(matched):
        text = path.read_text(encoding="utf-8")
        comment_lines = (
            _real_comment_lines(text)
            if path.suffix == ".py"
            else None
        )
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not (
                _ANCHORED_MARKER_RE.match(line)
                and not _ANCHORED_VALID_RE.match(line)
            ):
                continue
            if comment_lines is not None and lineno not in comment_lines:
                continue  # marker is inside a string literal, not a comment
            malformed.append(line.strip())
    return malformed
