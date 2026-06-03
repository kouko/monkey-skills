"""Stdlib markdown heading/chapter chunker for deep-read.

Splits a markdown document into ordered chunks on its ATX headings
(`#`..`######`), using only the standard library (`re`, `json`, `sys`).
No third-party dependency.

Chunk model — each chunk is a dict ``{heading, text, ordinal}``:

- ``heading``: the markdown heading line that starts the chunk
  (e.g. ``"## Background"``), or ``""`` for any preamble before the
  first heading.
- ``text``: the chunk body — the lines from this heading up to (but not
  including) the next heading of the SAME OR HIGHER level. A ``##`` chunk
  therefore swallows nested ``###``/``####`` subsections; a following
  ``##`` or ``#`` ends it. The heading line itself IS included in ``text``.
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


def chunk_markdown(text):
    """Split ``text`` into ordered ``{heading, text, ordinal}`` chunks.

    A chunk runs from its heading line up to (not including) the next
    heading of the same-or-higher level. Preamble before the first heading
    becomes a leading chunk with ``heading == ""``.
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

    chunks = []
    ordinal = 0

    # Leading preamble: text before the first heading (or whole doc if none).
    first_heading_index = headings[0][0] if headings else len(lines)
    if first_heading_index > 0:
        preamble = "\n".join(lines[:first_heading_index])
        chunks.append({"heading": "", "text": preamble, "ordinal": ordinal})
        ordinal += 1

    # Walk headings in document order. Each heading that is NOT already
    # swallowed by a previously-emitted chunk starts a new chunk; that chunk
    # extends until the next heading of the SAME OR HIGHER level (a
    # smaller-or-equal '#'-count). Deeper headings inside that range are
    # swallowed, so we skip past them via the ``consumed`` cursor.
    consumed = 0  # line index up to which output chunks already cover
    for idx, (line_index, level) in enumerate(headings):
        if line_index < consumed:
            continue  # this heading is nested inside an already-emitted chunk
        end = len(lines)
        for next_index, next_level in headings[idx + 1:]:
            if next_level <= level:
                end = next_index
                break
        body = "\n".join(lines[line_index:end])
        chunks.append({
            "heading": lines[line_index],
            "text": body,
            "ordinal": ordinal,
        })
        ordinal += 1
        consumed = end

    return chunks


def main():
    text = sys.stdin.read()
    chunks = chunk_markdown(text)
    json.dump(chunks, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
