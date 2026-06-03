"""Stdlib markdown heading/chapter chunker for deep-read.

Splits a markdown document into ordered chunks on its ATX headings
(`#`..`######`), using only the standard library (`re`, `json`, `sys`).
No third-party dependency.

Chunking happens at the document's SECTION LEVEL ``L`` — not at every
heading. ``L`` is chosen so the most common document shape (one ``#`` title
followed by several ``##`` sections) splits into one chunk per ``##``
section instead of collapsing into a single chunk:

- ``L`` = the SHALLOWEST heading level that appears at least twice (the
  repeated level — these are the document's sibling sections);
- if no level repeats, ``L`` = the shallowest heading level present.

A new chunk STARTS at every heading whose level is ``<= L``. Headings
deeper than ``L`` are absorbed into the current chunk (e.g. ``###``
subsections fold into their parent ``##`` section).

Chunk model — each chunk is a dict ``{heading, text, ordinal}``:

- ``heading``: the markdown heading line that starts the chunk
  (e.g. ``"## Background"``), or ``""`` for any preamble before the
  first level-``<=L`` heading.
- ``text``: the chunk body — the lines from this heading up to (but not
  including) the next heading of level ``<= L``. The heading line itself
  IS included in ``text``.
- ``ordinal``: 0-based index of the chunk in document order.

Edge cases:
- A heading-less document → ONE chunk (``heading == ""``, whole text,
  ordinal 0).
- Empty input → no chunks (``[]``).

Future option (NOT implemented in v1): for very long heading-less docs (or
a single oversized section) add a size-based fallback split on blank-line
paragraph boundaries with a max-char budget per chunk.

CLI: ``chunker.py`` reads markdown from stdin and prints the JSON chunk array
to stdout.
"""
import json
import re
import sys

# ATX heading: 1–6 leading '#', then a space, then the heading text.
# (Setext "===" / "---" underline headings are intentionally not handled;
# the deep-read corpus is agent-produced ATX markdown.)
_HEADING_RE = re.compile(r"^(#{1,6})\s")


def _heading_level(line):
    """Return the heading level (1–6) for an ATX heading line, else None."""
    match = _HEADING_RE.match(line)
    if match is None:
        return None
    return len(match.group(1))


def _chunk_level(levels):
    """Pick the section level ``L`` to chunk at, given heading levels.

    ``L`` = the shallowest (smallest) level that appears at least twice; if no
    level repeats, ``L`` = the shallowest level present. ``levels`` must be
    non-empty.
    """
    counts = {}
    for level in levels:
        counts[level] = counts.get(level, 0) + 1
    repeated = [level for level, count in counts.items() if count >= 2]
    if repeated:
        return min(repeated)
    return min(counts)


def chunk_markdown(text):
    """Split ``text`` into ordered ``{heading, text, ordinal}`` chunks.

    A new chunk starts at every heading whose level is ``<= L`` (the section
    level chosen by :func:`_chunk_level`); deeper headings are absorbed into
    the current chunk. Text before the first level-``<=L`` heading becomes a
    leading chunk with ``heading == ""``.
    """
    if text == "":
        return []

    lines = text.splitlines()

    # Find every heading's (line_index, level).
    headings = []
    for i, line in enumerate(lines):
        level = _heading_level(line)
        if level is not None:
            headings.append((i, level))

    # No headings at all -> one chunk for the whole document.
    if not headings:
        return [{"heading": "", "text": text, "ordinal": 0}]

    # Section level: only headings at this level (or shallower) start chunks.
    section_level = _chunk_level([level for _, level in headings])

    # Line indices where a new chunk begins: each level-<=L heading.
    starts = [line_index for line_index, level in headings
              if level <= section_level]

    chunks = []
    ordinal = 0

    # Leading preamble: any text before the first chunk-starting heading. This
    # includes deeper headings that precede the first level-<=L heading.
    if starts[0] > 0:
        preamble = "\n".join(lines[:starts[0]])
        chunks.append({"heading": "", "text": preamble, "ordinal": ordinal})
        ordinal += 1

    # Each level-<=L heading runs until the next level-<=L heading.
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        body = "\n".join(lines[start:end])
        chunks.append({
            "heading": lines[start],
            "text": body,
            "ordinal": ordinal,
        })
        ordinal += 1

    return chunks


def main():
    text = sys.stdin.read()
    chunks = chunk_markdown(text)
    json.dump(chunks, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
