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
  # Flatten mode: raw exhibit HTML -> canonical prose text
  uv run exhibit_prose.py --html path/to/ex991.htm --out prose.txt
  # Locate mode: canonical prose text -> JSON list of located numbers
  uv run exhibit_prose.py --locate --text prose.txt --out located.json
"""
from __future__ import annotations

import argparse
import json
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


# A numeric token: an integer optionally with thousands separators (commas)
# and an optional decimal fraction — e.g. "1,576,000", "480,126", "3.56", "0" —
# with an OPTIONAL trailing word-scale magnitude word ABSORBED into the token
# when present (Part 2 scope). ``\d+`` cannot cross a comma, so each
# ``(?:,\d{3})`` only attaches a well-formed 3-digit group; malformed groupings
# degrade to their plain-digit runs rather than mis-spanning.
#
# Word-scale magnitude parsing: a trailing thousand/million/billion/trillion
# (case-insensitive, whitespace-separated) is pulled into the SAME match so the
# anchor spans the whole phrase — "3.56 billion" tokenizes as "3.56 billion",
# not "3.56" (which dropped META's 1e9 multiplier). ``\b`` after the alternation
# keeps "billionaire" from being read as "billion"; a NON-magnitude following
# word (e.g. "warehouses") is not in the alternation, so it is never absorbed —
# the number then tokenizes plain. This part changes only the TOKEN/span; the
# value multiplier is the sibling task. Percentages, qualifiers, and ranges are
# still deferred to later parts. IGNORECASE affects only the word alternation;
# digits and commas are case-neutral.
_MAGNITUDE_WORDS = ("thousand", "million", "billion", "trillion")
_NUMBER_RE = re.compile(
    r"\d+(?:,\d{3})*(?:\.\d+)?"
    r"(?:\s+(?:" + "|".join(_MAGNITUDE_WORDS) + r")\b)?",
    re.IGNORECASE,
)


def locate_numbers(text: str) -> list[dict]:
    """Locate numeric tokens in the canonical prose surface, each with a
    verbatim token and a ``char_offset_span`` into ``text``.

    Returns one dict per candidate: ``{"token", "start", "end"}`` where
    ``token`` is the matched substring and ``[start, end]`` is its half-open
    offset span. The load-bearing invariant — the anchor the downstream
    anti-fabrication gate verifies against — is ``text[start:end] == token``
    exactly, which holds by construction because both derive from the same
    regex match. Deterministic and left-to-right ordered.

    A trailing word-scale magnitude word (thousand/million/billion/trillion,
    case-insensitive) is ABSORBED into the token when present, so the anchor
    spans the whole "3.56 billion" phrase (see ``_NUMBER_RE``); the value
    multiplier is applied downstream. Percentages and ranges are deferred to
    later parts."""
    return [
        {"token": m.group(), "start": m.start(), "end": m.end()}
        for m in _NUMBER_RE.finditer(text)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Canonical prose-text surface producer for 8-K exhibits. "
        "Flatten mode (--html): raw exhibit HTML -> non-table prose text. "
        "Locate mode (--locate --text): canonical prose text -> JSON located "
        "numbers. Text/number layer only — no semantic interpretation."
    )
    parser.add_argument("--html", help="Path to raw exhibit HTML (flatten mode)")
    parser.add_argument(
        "--text", help="Path to canonical prose text (locate mode input)"
    )
    parser.add_argument("--out", required=True, help="Path to write output")
    parser.add_argument(
        "--locate",
        action="store_true",
        help="Locate mode: emit a JSON list of located numbers "
        "({token, start, end}) from --text instead of flattening prose.",
    )
    args = parser.parse_args(argv)

    if args.locate:
        if not args.text:
            parser.error("--locate requires --text (path to canonical prose text)")
        # Locate mode runs locate_numbers on the given text VERBATIM (no
        # re-flatten via prose_surface): the input is already the canonical
        # surface, so re-flattening would shift offsets. Running the locator
        # directly keeps each char_offset_span relative to the input bytes —
        # the anchor the downstream anti-fabrication gate verifies against.
        text = Path(args.text).read_text(encoding="utf-8")
        located = locate_numbers(text)
        Path(args.out).write_text(
            json.dumps(located, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"located {len(located)} number(s) -> {args.out}")
        return 0

    if not args.html:
        parser.error("flatten mode requires --html (path to raw exhibit HTML)")
    html = Path(args.html).read_text(encoding="utf-8")
    prose = prose_surface(html)
    Path(args.out).write_text(prose, encoding="utf-8")
    print(f"flattened prose surface: {len(prose)} char(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
