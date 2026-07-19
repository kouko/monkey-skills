#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
exhibit_prose.py — investing-toolkit canonical PROSE surface producer.

The inverse of Route B's ``exhibit_tables.py``: where that walker EXTRACTS the
``<table>`` content, this one EXCLUDES it, flattening a raw 8-K earnings-exhibit
HTML document (e.g. a shareholder-letter EX-99.1) into ONE named canonical
prose-text surface — the letter/narrative text with well-formed ``<table>``
regions removed. The downstream prose-KPI producer indexes this single surface
with substring offsets, so it must be deterministic: the same input bytes always
yield the same text.

Pure stdlib ``html.parser`` — NO third-party dependency (matching
``exhibit_tables.py``). Table exclusion is done by tracking ``<table>`` nesting
depth on the same tag stream, so a table's cell text never leaks into the prose.

This is a TEXT-SURFACE layer only. It performs ZERO number tokenization /
parsing — that is the number-extraction layer (Task 2). It emits the flattened
non-table text verbatim (whitespace-normalized), preserving the filed precision
of any prose figures for the downstream anti-fabrication confirm gate.

Usage:
  uv run exhibit_prose.py --html path/to/ex991.htm --out prose.txt
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# Tags whose boundaries introduce a semantic break in the rendered prose. Without
# a separator here, adjacent block text would concatenate into a single token
# (e.g. "</p><p>" merging two sentences), corrupting the substring surface.
_BLOCK_TAGS = frozenset(
    {
        "p", "div", "br", "li", "ul", "ol", "tr", "hr", "section", "article",
        "header", "footer", "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "pre", "table",
    }
)


def _normalize_whitespace(text: str) -> str:
    """Strip nbsp (``\\xa0``, from ``&#160;``) and collapse each run of
    whitespace to a single space, then trim each line and drop blank lines.
    ``convert_charrefs`` (default True on HTMLParser) has already decoded char
    refs into unicode before this runs."""
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


class _ProseWalker(HTMLParser):
    """Collect document text in order, suppressing everything inside any
    ``<table>``. A nesting DEPTH counter (not a boolean) is used so a table
    nested inside another table stays suppressed until the OUTERMOST table
    closes — the mirror of ``exhibit_tables.py``'s open-table stack."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._table_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            # The excised table is itself a block boundary: emit the same break
            # block tags produce so prose flanking the outermost table cannot
            # concatenate. Nested tables need no break (already suppressed).
            if self._table_depth == 0:
                self._parts.append("\n")
            self._table_depth += 1
        elif tag in _BLOCK_TAGS and self._table_depth == 0:
            self._parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        # Self-closing block tag (e.g. ``<br/>``) is still a prose break.
        if tag in _BLOCK_TAGS and self._table_depth == 0:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "table":
            if self._table_depth > 0:
                self._table_depth -= 1
                # Break at the outermost table's close boundary too, so text
                # following an excised table cannot merge with the last prose.
                if self._table_depth == 0:
                    self._parts.append("\n")
        elif tag in _BLOCK_TAGS and self._table_depth == 0:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._table_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def prose_surface(html: str) -> str:
    """Flatten raw exhibit HTML into the canonical prose-text surface: the
    document's non-table text, whitespace-normalized (see module docstring).

    Deterministic: every character derives only from the input bytes and the
    fixed tag-handling rules, so re-flattening the same HTML yields an identical
    surface — the invariant the downstream substring-offset index depends on."""
    walker = _ProseWalker()
    walker.feed(html)
    walker.close()
    return _normalize_whitespace(walker.text())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flatten raw 8-K exhibit HTML into the canonical prose-text "
        "surface (non-table text) — text layer, no number parsing."
    )
    parser.add_argument("--html", required=True, help="Path to raw exhibit HTML")
    parser.add_argument("--out", required=True, help="Path to write prose text")
    args = parser.parse_args(argv)

    html = Path(args.html).read_text(encoding="utf-8")
    prose = prose_surface(html)
    Path(args.out).write_text(prose, encoding="utf-8")
    print(f"flattened prose surface: {len(prose)} char(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
