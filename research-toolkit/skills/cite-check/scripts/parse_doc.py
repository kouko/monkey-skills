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


def parse_doc(text):
    """Extract citation anchors from a markdown document.

    Returns a list of anchor dicts (see module docstring for shapes). Order
    follows document order; inline + footnote anchors come from the lines that
    carry them, and any remaining claim-bearing line is flagged `unsourced`.
    """
    lines = text.splitlines()
    refs, def_line_numbers = _build_reference_map(lines)

    anchors = []
    for idx, line in enumerate(lines):
        locator = idx + 1  # 1-based line number
        stripped = line.strip()

        # Reference-definition lines are not claims and not new citations.
        if idx in def_line_numbers:
            continue

        # Blank lines carry nothing.
        if not stripped:
            continue

        # Headings are not prose claims, so they are never flagged `unsourced` —
        # but they CAN carry citations (e.g. `# Section [src](url)`), and a
        # citation auditor must never silently drop a citation. So scan headings
        # for citations; just suppress the unsourced fallback for them.
        is_heading = stripped.startswith("#")

        line_has_citation = False

        # Inline links.
        for m in _INLINE_LINK.finditer(line):
            anchor_text, url = m.group(1), m.group(2)
            if not _is_url(url):
                continue
            anchors.append(
                {
                    "type": "inline",
                    "citedUrl": url,
                    "anchorText": anchor_text,
                    "locator": locator,
                }
            )
            line_has_citation = True

        # Footnote / bracket-number markers. Skip spans already consumed by an
        # inline link's [text] part by removing inline links from the scan text.
        scan = _INLINE_LINK.sub(" ", line)
        for m in _MARKER.finditer(scan):
            ref_id = m.group(1)
            anchors.append(
                {
                    "type": "footnote",
                    "citedRef": ref_id,
                    "citedUrl": refs.get(ref_id),
                    "locator": locator,
                }
            )
            line_has_citation = True

        # A prose claim-bearing line with no citation is reported (not audited).
        # Headings are never flagged unsourced (they carry no prose claim), but
        # any citations they DID carry were already extracted above.
        if not line_has_citation and not is_heading:
            anchors.append(
                {
                    "type": "unsourced",
                    "anchorText": stripped,
                    "locator": locator,
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
