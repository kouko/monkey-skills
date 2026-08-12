#!/usr/bin/env python3
"""Split an English artifact into units-JSON per the adjudication-view
protocol (loom-code/skills/using-loom-code/protocols/adjudication-view.md).

The split is mechanical (regex/line-based over markdown, stdlib only —
no markdown library) so the unit-1:1 rule holds by construction: unit
count equals source-unit count, never a judgment call.

Doc mode (this task): splits on H2 sections (`## `). A plan's H2s are
already `## Task N — …` blocks, so the same H2 split handles both
briefs and plans without special-casing. Content before the first H2
(title, intro) is not a unit.

Verdict mode (Task 2) will add a second unit source (structured
findings, not H2 sections) — `MODES` below is the extension point:
add a `"verdict": split_verdict` entry, no change to `main()`.

CLI:
    python3 adjudication_split.py doc <markdown-file>

Emits units-JSON (a JSON array) to stdout. Each unit:
    id           ordinal identifier ("u1", "u2", ...)
    heading      the H2 heading text
    source_text  the section body, verbatim
    anchors      verbatim tokens extracted from source_text (numbers,
                 ALL-CAPS enum tokens, backticked terms, CamelCase /
                 snake_case identifiers) — order = first-occurrence
                 position in source_text, deduplicated
    rendition    empty string; filled later by the orchestrator-side
                 LLM translate step (this script never fills it)
"""

import argparse
import json
import re
import sys
from pathlib import Path

H2_LINE_RE = re.compile(r"^## (.+)$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
BACKTICK_RE = re.compile(r"`([^`]+)`")
NUMBER_RE = re.compile(r"\b\d[\d.]*\b")
ALLCAPS_RE = re.compile(r"\b[A-Z]{2,}(?:_[A-Z0-9]+)*\b")
SNAKE_CASE_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
CAMEL_CASE_RE = re.compile(r"\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b")

# Anchor kinds in extraction-priority order. Backticked terms are
# captured whole (group 1 — the content, without the backtick
# delimiters); the rest capture their full match.
_ANCHOR_PATTERNS = (BACKTICK_RE, NUMBER_RE, ALLCAPS_RE, SNAKE_CASE_RE, CAMEL_CASE_RE)


def extract_anchors(text):
    """Return verbatim anchor tokens from `text`, deduplicated, ordered
    by first-occurrence position (not by pattern)."""
    candidates = []
    for pattern in _ANCHOR_PATTERNS:
        for match in pattern.finditer(text):
            token = match.group(1) if pattern is BACKTICK_RE else match.group(0)
            candidates.append((match.start(), token))
    candidates.sort(key=lambda c: c[0])

    anchors = []
    seen = set()
    for _, token in candidates:
        if token not in seen:
            seen.add(token)
            anchors.append(token)
    return anchors


def _iter_h2_matches(text):
    """Yield (start, end, heading) for H2 lines that are NOT inside a
    fenced code block. `start`/`end` mirror `re.Match.start()`/`.end()`
    for a `^## (.+)$` match: `end` is right after the heading text,
    before the line's newline.

    Fence tracking is a line-scanner state machine (stdlib only, no
    markdown library): a ``` or ~~~ line (indented up to 3 spaces per
    CommonMark) toggles fence state; a fence only closes on the same
    character with length >= the opening length (also per CommonMark —
    a longer nested fence of the other character does not close it).
    While inside a fence, `## `-prefixed lines are ordinary content,
    never section boundaries.
    """
    fence_char = None
    fence_min_len = 0
    pos = 0
    for line in text.splitlines(keepends=True):
        content = line.rstrip("\n").rstrip("\r")
        fence_match = FENCE_RE.match(content)
        if fence_match:
            marker = fence_match.group(1)
            char, length = marker[0], len(marker)
            if fence_char is None:
                fence_char, fence_min_len = char, length
            elif char == fence_char and length >= fence_min_len:
                fence_char, fence_min_len = None, 0
        elif fence_char is None:
            h2_match = H2_LINE_RE.match(content)
            if h2_match:
                yield pos, pos + len(content), h2_match.group(1).strip()
        pos += len(line)


def split_document(text):
    """Split `text` on H2 (`## `) sections into units-JSON. Returns a
    list of unit dicts in source order; unit count == H2 count (H2
    lines inside fenced code blocks don't count — see
    `_iter_h2_matches`)."""
    matches = list(_iter_h2_matches(text))
    units = []
    for i, (_start, end, heading) in enumerate(matches):
        body_start = end
        body_end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        source_text = text[body_start:body_end].strip("\n")
        units.append(
            {
                "id": f"u{i + 1}",
                "heading": heading,
                "source_text": source_text,
                "anchors": extract_anchors(source_text),
                "rendition": "",
            }
        )
    return units


# Mode dispatch — Task 2 adds "verdict": split_verdict here.
MODES = {"doc": split_document}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES), help="split mode")
    parser.add_argument("path", help="path to the source markdown file")
    args = parser.parse_args(argv)

    text = Path(args.path).read_text(encoding="utf-8")
    units = MODES[args.mode](text)
    json.dump(units, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
