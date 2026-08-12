#!/usr/bin/env python3
"""Split an English artifact into units-JSON per the adjudication-view
protocol (loom-code/skills/using-loom-code/protocols/adjudication-view.md).

The split is mechanical (regex/line-based over markdown, stdlib only —
no markdown library) so the unit-1:1 rule holds by construction: unit
count equals source-unit count, never a judgment call.

Doc mode (this task): splits on H2 sections (`## `). A plan's H2s are
already `## Task N — …` blocks, so the same H2 split handles both
briefs and plans without special-casing. Non-blank content before the
first H2 (a plan's Goal/Stage header block, a brief's Date/Stage
lines) becomes the FIRST unit — heading is the H1 title text (stripped
of `# `) when the preamble starts with one, else "(preamble)" — so it
is never silently dropped, per the unit-1:1 rule. An empty or
whitespace-only preamble produces no extra unit.

Verdict mode splits a reviewer's structured verdict block instead: one
unit per `- severity: ...` finding item (code-arm and docs-arm finding
shapes both tolerated — see `_iter_finding_blocks`), heading = that
finding's `where` + `dimension`, source_text = the finding's field
block reassembled verbatim from its parsed key/value lines.

CLI:
    python3 adjudication_split.py doc <markdown-file>
    python3 adjudication_split.py verdict <verdict-text-file>

Emits units-JSON (a JSON array) to stdout. Each unit:
    id           ordinal identifier ("u1", "u2", ...)
    heading      doc mode: the H2 heading text.
                 verdict mode: "<where> <dimension>" (the semantic
                 unit key — same finding, same heading, across a
                 regenerated rendition).
    source_text  doc mode: the section body, verbatim.
                 verdict mode: the finding's field block, verbatim
                 (each `key: value` line as parsed, in source order).
    anchors      verbatim tokens extracted from source_text (numbers,
                 ALL-CAPS enum tokens, backticked terms, CamelCase /
                 snake_case identifiers) — order = first-occurrence
                 position in source_text, deduplicated.
                 verdict mode additionally appends the finding's
                 severity emoji and its `where` value verbatim (both
                 must survive translation even when neither matches
                 an anchor pattern above).
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

# Verdict mode: a finding item starts with `- severity: ...` at some
# indent; its subsequent field lines (`dimension:`, `where:`, `note:`,
# `class:`, code-arm's `source:`/`origin:`, docs-arm's `quote:`, ...)
# are indented deeper than the item's own `-`. Matching on
# `- severity:` specifically (not a bare `- `) means unrelated `-`
# list items elsewhere in a verdict block (simplification_ledger,
# summary, read_context_findings) are never mistaken for findings —
# no separate "findings:" section boundary tracking is needed.
FINDING_ITEM_RE = re.compile(r"^([ \t]*)-\s*severity:\s*(.+)$")
FIELD_LINE_RE = re.compile(r"^([ \t]*)([A-Za-z][A-Za-z_-]*):\s*(.*)$")
SEVERITY_EMOJI_RE = re.compile(r"[🔴🟡🟢]")

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
    list of unit dicts in source order; unit count == H2 count, plus
    one more when non-blank content precedes the first H2 (see module
    docstring — the preamble unit, ordinal u1, never silently dropped).
    H2 lines inside fenced code blocks don't count — see
    `_iter_h2_matches`."""
    matches = list(_iter_h2_matches(text))
    units = []
    offset = 0
    if matches:
        preamble = text[: matches[0][0]].strip("\n")
        if preamble.strip():
            heading = (
                preamble.splitlines()[0][2:].strip()
                if preamble.startswith("# ")
                else "(preamble)"
            )
            units.append(
                {
                    "id": "u1",
                    "heading": heading,
                    "source_text": preamble,
                    "anchors": extract_anchors(preamble),
                    "rendition": "",
                }
            )
            offset = 1
    for i, (_start, end, heading) in enumerate(matches):
        body_start = end
        body_end = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        source_text = text[body_start:body_end].strip("\n")
        units.append(
            {
                "id": f"u{i + 1 + offset}",
                "heading": heading,
                "source_text": source_text,
                "anchors": extract_anchors(source_text),
                "rendition": "",
            }
        )
    return units


def _iter_finding_blocks(text):
    """Yield an ordered field dict (severity first, then each field in
    source order) per `- severity: ...` finding item found in `text`,
    tolerating both the code-arm and docs-arm finding shapes (the
    field set differs — code-arm has `source:`/`origin:`, docs-arm has
    `quote:` instead — this only requires `severity:` to start an
    item and reads whatever fields follow it).

    A sibling field must sit at the SAME COLUMN as the item's first
    non-blank line — never at any deeper indent. A line nested deeper
    (e.g. inside a `note: |` block-literal that quotes `dimension:`/
    `where:` from a pasted verdict-schema example, which reviewers
    really do write) is that field's value content, not a sibling
    field, and must not be read as one — instead it is appended
    (space-joined) to the PRECEDING sibling field's value, so a
    multi-line `note: |`/`note: >` body is preserved in source_text
    rather than silently dropped. Mirrors the column rule in
    loom-code/scripts/loom_gate_markers.py's `_iter_findings`."""
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        start_match = FINDING_ITEM_RE.match(lines[i])
        if start_match is None:
            i += 1
            continue
        item_indent = len(start_match.group(1))
        fields = {"severity": start_match.group(2).strip()}
        block_start = i + 1
        j = block_start
        while j < n:
            line = lines[j]
            if line.strip():
                line_indent = len(line) - len(line.lstrip(" \t"))
                if line_indent <= item_indent:
                    break  # dedent to the item's own level: block ends
            j += 1
        block_end = j
        column = None
        for line in lines[block_start:block_end]:
            if line.strip():
                column = len(line) - len(line.lstrip(" \t"))
                break
        if column is not None:
            current_key = None
            for line in lines[block_start:block_end]:
                if not line.strip():
                    continue
                line_indent = len(line) - len(line.lstrip(" \t"))
                if line_indent == column:
                    field_match = FIELD_LINE_RE.match(line)
                    if field_match:
                        key = field_match.group(2)
                        fields[key] = field_match.group(3).strip()
                        current_key = key
                elif line_indent > column and current_key is not None:
                    fields[current_key] = f"{fields[current_key]} {line.strip()}".strip()
        yield fields
        i = block_end


def split_verdict(text):
    """Split `text` (a reviewer's structured verdict block) into
    units-JSON, one unit per finding. Unit count == finding count (the
    unit-1:1 rule — see `_iter_finding_blocks`)."""
    units = []
    for i, fields in enumerate(_iter_finding_blocks(text)):
        severity = fields.get("severity", "")
        dimension = fields.get("dimension", "")
        where = fields.get("where", "")
        source_text = "\n".join(f"{key}: {value}" for key, value in fields.items())
        anchors = extract_anchors(source_text)
        emoji_match = SEVERITY_EMOJI_RE.search(severity)
        if emoji_match and emoji_match.group(0) not in anchors:
            anchors.append(emoji_match.group(0))
        if where and where not in anchors:
            anchors.append(where)
        units.append(
            {
                "id": f"u{i + 1}",
                "heading": f"{where} {dimension}".strip(),
                "source_text": source_text,
                "anchors": anchors,
                "rendition": "",
            }
        )
    return units


# Mode dispatch — "doc" is document mode (Task 1), "verdict" is
# findings mode (Task 2).
MODES = {"doc": split_document, "verdict": split_verdict}


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
