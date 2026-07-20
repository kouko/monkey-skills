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
  * newlines INSIDE a source text run folded to spaces, EXCEPT inside the
    render-significant-whitespace family (``pre``/``xmp``/``listing``/
    ``plaintext``/``textarea``, see ``_PRE_TAGS``) where the newline IS the
    rendered break. A ``\n`` on the finished surface therefore means A RENDERED
    BREAK, in both directions: every one is a real break, and every real break
    reaches the surface as one. That biconditional is what lets a downstream
    guard distinguish "two blocks" from "one hard-wrapped sentence" exactly;
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
        # The render-significant-whitespace family below: their boundaries are
        # rendered breaks too, so prose flanking one cannot be adjacent prose.
        "xmp", "listing", "plaintext", "textarea",
    }
)


# Elements whose content renders with WHITESPACE PRESERVED, so a newline inside
# them IS the rendered line break rather than incidental source formatting.
#
# `handle_data` folds source-run newlines to spaces everywhere else, which makes
# a surface "\n" mean "a rendered break" — but that design also relies on the
# CONVERSE, that every rendered break REACHES the surface as a "\n". Inside this
# family there is no tag marking the break, so the fold erased it and let a block
# boundary's two sides fuse: "<pre>45,000\nMillion Air deliveries</pre>"
# tokenized as "45,000 Million" (4.5e10) while ``text[start:end] == token`` kept
# holding BY CONSTRUCTION — the same fabrication-wearing-a-valid-anchor class as
# the grouping and compound-joiner guards above.
#
# Exempting these from the fold preserves the break, so the `[^\S\n]` absorption
# guard sees it and declines to fuse. `textarea` belongs here despite being a
# form control: `html.parser` treats only `script`/`style` as CDATA elements, so
# textarea content arrives through `handle_data` like any other text.
_PRE_TAGS = frozenset({"pre", "xmp", "listing", "plaintext", "textarea"})


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
#   ``(?!\d)``     rejects a malformed TRAILING group (>3 digits);
#   ``(?<![\d,])`` stops a match from STARTING INSIDE a longer (>=4-digit) run
#                  that sits directly against the separator, OR directly after a
#                  COMMA that already grouped a preceding number.
# Without the leading guard, "as of 2026<nbsp>560 holders" matched from the "026"
# and fused two independent numbers into the fabricated "2026,560" — and because
# the anchor ``text[start:end] == token`` holds BY CONSTRUCTION, such a token
# wears a VALID-looking source anchor while carrying a wrong value. A
# legitimately grouped number's lead group is always 1-3 digits, so the guard
# costs no true positives. Either guard failing degrades the run to plain digits
# (locating as separate numbers), which is the safe direction.
#
# The COMMA in that lookbehind closes the nbsp-as-plain-WORD-separator case: in
# "1,428<nbsp>500-mile trucks" the nbsp joins two independently meaningful
# numbers, and a digit-only lookbehind saw the comma, matched from "428", and
# canonicalized "1,428,500" — a fabricated value wearing a valid anchor. It costs
# no true positive: a legitimately grouped number's LEAD group is never preceded
# by a comma (that comma would be the SAME number's separator, and ``\d{1,3}``
# cannot start mid-group). A SENTENCE comma is not this case — in "In 2024,
# 428<nbsp>500 units" the char adjacent to the digit run is the SPACE, so the
# genuine grouping still normalizes.
_THOUSANDS_SEP = "\u00a0\u2009"
_SPACE_GROUPED_NUMBER_RE = re.compile(
    r"(?<![\d,])\d{1,3}(?:[" + _THOUSANDS_SEP + r"]\d{3})+(?!\d)"
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
        self._pre_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            # The excised table is itself a block boundary: emit the same break
            # block tags produce so prose flanking the outermost table cannot
            # concatenate. Nested tables need no break (already suppressed).
            if self._table_depth == 0:
                self._parts.append("\n")
            self._table_depth += 1
            return
        if tag in _PRE_TAGS:
            # DEPTH, not a boolean — mirroring `_table_depth`: text following an
            # INNER close is still inside the outer element, so its newlines are
            # still rendered breaks.
            self._pre_depth += 1
        if tag in _BLOCK_TAGS and self._table_depth == 0:
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
            return
        if tag in _PRE_TAGS and self._pre_depth > 0:
            self._pre_depth -= 1
        if tag in _BLOCK_TAGS and self._table_depth == 0:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._table_depth == 0:
            if self._pre_depth:
                # Inside the render-significant-whitespace family the newline IS
                # the rendered break (there is no tag marking it), so it is kept
                # verbatim — the very break the fold would otherwise erase. See
                # `_PRE_TAGS`.
                self._parts.append(data)
                return
            # Elsewhere, collapse newlines INSIDE a source text run to spaces at
            # the point the text enters. This is what makes the separator
            # UNAMBIGUOUS: without it a "\n" on the finished surface had two
            # possible origins — a rendered break, or a newline that merely sat
            # inside one run of source text — and downstream guards had to treat
            # every "\n" as possibly-a-boundary. EDGAR HTML is hard-wrapped, so
            # "3.56\nbillion" inside one paragraph is a realistic shape, and that
            # conservatism dropped the magnitude word off a figure whose scale
            # the source states plainly. With the fold here and the `_PRE_TAGS`
            # exemption above, a "\n" on the canonical surface means A RENDERED
            # BREAK and nothing else — in BOTH directions, which is what makes
            # the `[^\S\n]` guards EXACT rather than conservative.
            #
            # ONLY "\n" is folded, deliberately: `_normalize_whitespace` splits
            # lines on "\n" alone, so no other whitespace character can create
            # the ambiguity. A blanket `\s` fold would ALSO eat the nbsp / thin
            # space that `_SPACE_GROUPED_NUMBER_RE` reads as a THOUSANDS
            # separator, destroying the signal that keeps "3<nbsp>560<nbsp>000"
            # one number. This fold is not length-preserving, but it runs on the
            # raw text BEFORE any offset is taken, which is the same reason
            # `_normalize_whitespace`'s own collapse is safe: every offset is
            # computed against the finished surface these parts produce.
            self._parts.append(data.replace("\n", " "))

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
# (case-insensitive, separated by SAME-LINE whitespace only — see the block-
# separator guard below) is pulled into the SAME match so the
# anchor spans the whole phrase — "3.56 billion" tokenizes as "3.56 billion",
# not "3.56" (which dropped META's 1e9 multiplier). ``\b`` after the alternation
# keeps "billionaire" from being read as "billion"; a NON-magnitude following
# word (e.g. "warehouses") is not in the alternation, so it is never absorbed —
# the number then tokenizes plain. This part changes only the TOKEN/span; the
# value multiplier is the sibling task. Percentages, qualifiers, and ranges are
# still deferred to later parts. IGNORECASE affects only the word alternation;
# digits and commas are case-neutral.
#
# HYPHEN GUARD (``_COMPOUND_JOINERS``): ``\b`` alone is satisfied by a HYPHEN, so
# "3.56 billion-dollar program" absorbed "billion" — but in a hyphenated compound
# the magnitude word is ADJECTIVAL ("billion-dollar", "million-unit"): it modifies
# the following noun, it does not scale the figure. Absorbing it mis-spans the
# anchor AND makes the downstream multiplier invent a value ~1e9 too large, while
# ``text[start:end] == token`` keeps holding BY CONSTRUCTION — the same
# fabrication-wearing-a-valid-anchor class as the grouping guards above.
#
# The guard applies to the three hyphen joiners — ASCII hyphen-minus, U+2010
# HYPHEN, U+2011 NON-BREAKING HYPHEN. It deliberately does NOT touch the DASHES
# (U+2012 figure dash .. U+2015 horizontal bar): a dash after a magnitude word is
# a RANGE or parenthetical mark ("3 billion–5 billion"), where the word IS the
# figure's scale and must still be absorbed. Nor does it reject punctuation
# generally: a sentence-final "3.56 billion." and a mid-clause "500 million,"
# are ordinary true positives.
#
# But ASCII hyphen-minus is ALSO the commonest RANGE mark in an ASCII-encoded
# filing, so rejecting on the joiner ALONE broke "2 billion-3 billion users":
# the first bound lost its scale and read as a bare 2 — the compound defect
# INVERTED (an under-scaled value wearing the same valid-looking anchor). The
# guard therefore discriminates on the character AFTER the joiner: a RANGE
# continues with a DIGIT ("billion-3"), a COMPOUND with a LETTER
# ("billion-dollar"). Only the letter case blocks absorption.
#
# RESIDUAL, stated because a guard's comment must claim only what it does: the
# discriminator reads exactly ONE character past the joiner. A range whose upper
# bound is not written digit-first ("2 billion-$3 billion") still reads as a
# compound, and a joiner at end-of-text likewise blocks. Both degrade the token
# to plain digits — the same lossy direction as a failed guard, not a fabrication.
_MAGNITUDE_WORDS = ("thousand", "million", "billion", "trillion")
_COMPOUND_JOINERS = "-‐‑"
# BLOCK-SEPARATOR guard on the absorption whitespace: `_ProseWalker` inserts a
# "\n" at every block boundary precisely so adjacent blocks cannot fuse (see
# `_BLOCK_TAGS`), but `\s` matches that "\n", so a block merely BEGINNING with a
# magnitude word fused into the previous block's trailing number —
# "45,000</li><li>Million Air..." tokenized as "45,000\nMillion" (4.5e10), and
# the fusion could even span an EXCISED TABLE, joining prose the source never
# made adjacent. Requiring SAME-LINE whitespace (`[^\S\n]`) closes it.
#
# The guard is EXACT, not conservative, because the separator it reads is
# unambiguous IN BOTH DIRECTIONS. Every "\n" reaching this regex is a rendered
# break: `_ProseWalker.handle_data` folds newlines INSIDE a source text run to
# spaces as they enter, so a hard SOURCE LINE WRAP — the ordinary shape of EDGAR
# HTML, and the one that would otherwise have cost "3.56\nbillion" its scale —
# arrives as same-line whitespace and absorbs normally. And every rendered break
# reaches here AS a "\n": the walker emits one at each block boundary, and
# exempts `_PRE_TAGS` from the fold so a break carried by the newline ITSELF is
# not erased. Losing that second direction is what let "<pre>45,000\nMillion Air
# deliveries</pre>" fuse. So this guard blocks exactly cross-break fusion and
# nothing else; it costs no true positive.
_NUMBER_RE = re.compile(
    r"\d+(?:,\d{3})*(?:\.\d+)?"
    r"(?:[^\S\n]+(?:" + "|".join(_MAGNITUDE_WORDS) + r")\b"
    r"(?![" + _COMPOUND_JOINERS + r"](?!\d)))?",
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
