"""Deterministic citation-anchor pre-extractor for cite-check (stdlib only).

Stage 1 scaffold: given a markdown document, extract the *structure* of its
citations — inline links, footnote markers resolved to their reference-list
URLs, and lines that make a claim but cite nothing (unsourced). This is purely
deterministic (`re` / `urllib`); the LLM claim<->citation binding lives in the
SKILL.md, not here.

Anchor shapes returned by `parse_doc`:
  inline:    {type:"inline",    citedUrl, anchorText, locator}
  footnote:  {type:"footnote",  citedRef, citedUrl(or None), locator}
  unsourced: {type:"unsourced", anchorText, locator}

`locator` is a 1-based line number — stable and human-checkable against the doc.
"""

import json
import re
import sys
from urllib.parse import urlparse

# [text](url) — inline markdown link. URL stops at the first whitespace or ')'.
_INLINE_LINK = re.compile(r"\[([^\]]+)\]\((\S+?)\)")

# A footnote/reference DEFINITION line: `[^1]: url` or `[1] ... url`.
_FOOTNOTE_DEF = re.compile(r"^\s*\[\^?([0-9]+)\]:?\s+(.*)$")

# A footnote/reference MARKER inside prose: `[^1]` or `[1]`.
_MARKER = re.compile(r"\[\^?([0-9]+)\]")

# First http(s) URL appearing anywhere in a string.
_URL_IN_TEXT = re.compile(r"https?://\S+")


def _first_url(text):
    """Return the first http(s) URL in `text`, trimmed of trailing punctuation."""
    m = _URL_IN_TEXT.search(text)
    if not m:
        return None
    return m.group(0).rstrip(".,;)]")


def _is_url(token):
    """True if `token` parses as an http(s) URL (inline-link target check)."""
    parsed = urlparse(token)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _build_reference_map(lines):
    """Map footnote/reference id -> URL from definition lines.

    A definition line looks like `[^1]: <url>` or `[1] Author. <url>`. We resolve
    the id to the first URL on that line (None if the line carries no URL).
    """
    refs = {}
    def_line_numbers = set()
    for idx, line in enumerate(lines):
        m = _FOOTNOTE_DEF.match(line)
        if not m:
            continue
        ref_id, rest = m.group(1), m.group(2)
        refs[ref_id] = _first_url(rest)
        def_line_numbers.add(idx)
    return refs, def_line_numbers


def _group_paragraphs(lines, def_line_numbers):
    """Group physical lines into paragraph blocks (blank line = separator).

    A claim that wraps across ~80-col lines is one logical unit, but its
    citation may land on a continuation line. Scanning line-by-line would flag
    the leading line(s) `unsourced` even though the paragraph is cited, so the
    paragraph — not the physical line — is the unit of sourcing.

    Reference-definition lines (`[^1]: url`, `[1] ... url`) are excluded from
    blocks: they are not prose claims and must not be flagged unsourced. An
    excluded line also acts as a block boundary (like a blank line) so a
    definition cannot glue two surrounding paragraphs together.

    Yields (line_indices, block_text) where line_indices are 0-based indices of
    the lines composing the block, in document order.
    """
    block = []
    for idx, line in enumerate(lines):
        is_boundary = (not line.strip()) or (idx in def_line_numbers)
        if is_boundary:
            if block:
                yield block, "\n".join(lines[i] for i in block)
                block = []
            continue
        block.append(idx)
    if block:
        yield block, "\n".join(lines[i] for i in block)


def parse_doc(text):
    """Extract citation anchors from a markdown document.

    Returns a list of anchor dicts (see module docstring for shapes). Order
    follows document order. Inline + footnote anchors are extracted from each
    paragraph block (consecutive non-blank, non-reference lines); a block that
    carries no citation at all is flagged `unsourced`. Operating on blocks (not
    physical lines) means a wrapped claim whose citation sits on a continuation
    line is correctly treated as sourced.

    `locator` stays a 1-based line number: for a citation it is the line the
    citation actually appears on; for an unsourced block it is the block's
    first line.
    """
    lines = text.splitlines()
    refs, def_line_numbers = _build_reference_map(lines)

    anchors = []
    for line_indices, block in _group_paragraphs(lines, def_line_numbers):
        first_locator = line_indices[0] + 1  # 1-based line of block start

        # Headings are not prose claims, so a heading-only block is never
        # flagged `unsourced` — but headings CAN carry citations
        # (e.g. `# Section [src](url)`), and a citation auditor must never
        # silently drop one. So we still scan the block for citations; we only
        # suppress the unsourced fallback when every line is a heading.
        all_headings = all(
            lines[i].lstrip().startswith("#") for i in line_indices
        )

        block_has_citation = False

        # Inline links — locate each on the physical line it appears on.
        for m in _INLINE_LINK.finditer(block):
            anchor_text, url = m.group(1), m.group(2)
            if not _is_url(url):
                continue
            locator = first_locator + block[: m.start()].count("\n")
            anchors.append(
                {
                    "type": "inline",
                    "citedUrl": url,
                    "anchorText": anchor_text,
                    "locator": locator,
                }
            )
            block_has_citation = True

        # Footnote / bracket-number markers. Remove inline links first so a
        # link's `[text]` part is not misread as a numeric marker.
        scan = _INLINE_LINK.sub(lambda m: " " * len(m.group(0)), block)
        for m in _MARKER.finditer(scan):
            ref_id = m.group(1)
            locator = first_locator + scan[: m.start()].count("\n")
            anchors.append(
                {
                    "type": "footnote",
                    "citedRef": ref_id,
                    "citedUrl": refs.get(ref_id),
                    "locator": locator,
                }
            )
            block_has_citation = True

        # A claim-bearing block with no citation anywhere in it is reported
        # (not audited). Heading-only blocks are never flagged; any citations
        # they carried were already extracted above. The locator is the block's
        # first line; anchorText is the block text.
        if not block_has_citation and not all_headings:
            anchors.append(
                {
                    "type": "unsourced",
                    "anchorText": block.strip(),
                    "locator": first_locator,
                }
            )

    return anchors


def main():
    """Read markdown from stdin, print the JSON anchors array to stdout."""
    text = sys.stdin.read()
    json.dump(parse_doc(text), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
