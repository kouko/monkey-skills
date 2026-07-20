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

THE CANONICAL SURFACE IS A *NORMALIZED* SURFACE — not the raw filed bytes. This
is the contract every downstream quote and offset depends on, so it is stated
explicitly: the anchor invariant ``canonical_text[start:end] == matched_token``
is defined against THIS surface, never against the original document. One
normalization policy is applied consistently to parsing, the quote, the offset,
and the substring gate:

  * HTML entity decoding (``convert_charrefs``, on by default);
  * alternate digit families folded to ASCII — full-width U+FF10-FF19 and
    Arabic-Indic U+0660-0669 — plus full-width comma / full stop;
  * smart quotes (U+2018/2019/201C/201D) folded to ASCII ``'`` and ``"``;
  * nbsp / thin-space THOUSANDS separators rewritten to commas;
  * whitespace runs collapsed, lines trimmed, blank lines dropped.

Every one of those folds is LENGTH-PRESERVING or applied before offsets are
taken, which is what keeps a downstream verbatim quote both faithful and
correctly indexed. A consumer that re-reads the raw filing and compares against
a stored quote must normalize it the same way first.

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


# Character folds applied to the raw text BEFORE grouping / tokenization,
# completing the spec's ONE normalization policy: full-width and Arabic-Indic
# digits and smart quotes here, separator handling below, HTML entity decoding
# via HTMLParser's ``convert_charrefs``.
#
# EVERY fold here is LENGTH-PRESERVING (one char -> one char). That property is
# load-bearing, not incidental: it is precisely why folding cannot shift a
# single char offset, so the downstream ``text[start:end] == token`` anchor
# stays valid over the folded surface — the same property that made the
# nbsp->comma rewrite safe. A fold that changed length (e.g. a ligature
# expansion) MUST NOT be added here; it would silently corrupt every offset.
#
# Full-width comma / full stop fold alongside the full-width digits so a
# full-width-formatted number normalizes COHERENTLY ("１２３，４５６" ->
# "123,456") instead of becoming an untokenizable half-converted hybrid.
_CHAR_FOLD = str.maketrans(
    {
        **{chr(0xFF10 + i): str(i) for i in range(10)},  # full-width digits
        "，": ",",  # full-width comma
        "．": ".",  # full-width full stop
        **{chr(0x0660 + i): str(i) for i in range(10)},  # Arabic-Indic digits
        "‘": "'", "’": "'",  # curly single quotes
        "“": '"', "”": '"',  # curly double quotes
    }
)


# A non-breaking (U+00A0) or thin (U+2009) space used as a THOUSANDS separator:
# a leading 1-3 digit group followed by one-or-more (separator + exactly-3-digit)
# groups, e.g. "3<nbsp>560<nbsp>000". Filers emit these unbreakable spaces
# specifically to keep a grouped number together, so — unlike an ASCII word
# space — they reliably mark a separator, letting us convert only genuine
# groupings and never a "in 2024 500 firms" word gap.
#
# BOTH ends are guarded, and the guards are mirror images of each other:
#   ``(?!\d)``  rejects a malformed TRAILING group (>3 digits);
#   ``(?<!\d)`` stops a match from STARTING INSIDE a longer (>=4-digit) run that
#               sits directly against the separator.
# Without the leading guard, "as of 2026<nbsp>560 holders" matched from the "026"
# and fused two independent numbers into the fabricated "2026,560" — and because
# the anchor ``text[start:end] == token`` holds BY CONSTRUCTION, such a token
# wears a VALID-looking source anchor while carrying a wrong value. A
# legitimately grouped number's lead group is always 1-3 digits, so the guard
# costs no true positives. Either guard failing degrades the run to plain digits
# (locating as separate numbers), which is the safe direction.
#
# KNOWN DEFERRED EDGE: an nbsp used as a plain non-breaking WORD separator whose
# preceding char is a COMMA, not a digit (e.g. "1,428<nbsp>500-mile trucks"), is
# not covered — the ``(?<!\d)`` lookbehind sees the comma. Declared deferral,
# tracked in the plan; not a silent gap.
_THOUSANDS_SEP = "\u00a0\u2009"
_SPACE_GROUPED_NUMBER_RE = re.compile(
    r"(?<!\d)\d{1,3}(?:[" + _THOUSANDS_SEP + r"]\d{3})+(?!\d)"
)


def _commaify_space_grouped(match: re.Match) -> str:
    """Rewrite the nbsp/thin-space separators inside one grouped-number run to
    commas, yielding the same canonical "3,560,000" form as a comma filing."""
    return re.sub("[" + _THOUSANDS_SEP + "]", ",", match.group())


def _normalize_whitespace(text: str) -> str:
    """Apply the canonical normalization policy: fold alternate digit families
    and smart quotes (``_CHAR_FOLD``), normalize nbsp/thin-space THOUSANDS
    separators to commas, strip nbsp (``\\xa0``, from ``&#160;``), collapse each
    run of whitespace to a single space, then trim each line and drop blank
    lines. ``convert_charrefs`` (default True on HTMLParser) has already decoded
    char refs into unicode before this runs.

    ORDER IS LOAD-BEARING, in two places:

    1. ``_CHAR_FOLD`` runs FIRST so a full-width-digit number can participate in
       grouping detection — "３<nbsp>５６０" must fold to ASCII digits before
       the grouping regex looks for digit runs, or it would never match.
    2. The grouping conversion runs BEFORE the nbsp->space collapse erases the
       separator signal — so "3<nbsp>560<nbsp>000" becomes "3,560,000" on the
       canonical surface and the downstream locator reads it as ONE number whose
       ``text[start:end] == token`` anchor holds (rather than splitting
       3/560/000)."""
    text = text.translate(_CHAR_FOLD)
    text = _SPACE_GROUPED_NUMBER_RE.sub(_commaify_space_grouped, text)
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
