"""Stdlib-only markdown frontmatter parser.

parse_frontmatter(text) parses a leading ``---`` … ``---`` block of simple
``key: value`` lines into a dict and returns the remaining body. It is NOT a
full YAML parser: values stay strings (no coercion), and malformed blocks
fail loud with ValueError. See specs/frontmatter/spec.md for the binding
acceptance scenarios.
"""

_FENCE = "---"


def _is_fence(line: str) -> bool:
    """A fence line is exactly ``---`` (trailing whitespace allowed)."""
    return line.rstrip() == _FENCE


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse a leading ``---``…``---`` frontmatter block.

    Returns (metadata, body). When the text does not open with a fence on the
    first line, returns ({}, text) unchanged. Raises TypeError on non-str
    input and ValueError on a malformed (opened-but-broken) block.
    """
    if not isinstance(text, str):
        raise TypeError(
            f"parse_frontmatter expects str, got {type(text).__name__}"
        )

    if text == "":
        return {}, ""

    # Normalize CRLF to LF so line endings are handled uniformly.
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")

    # No opening fence on the first line -> not frontmatter, pass through
    # the ORIGINAL text unchanged.
    if not _is_fence(lines[0]):
        return {}, text

    metadata: dict[str, str] = {}
    for index in range(1, len(lines)):
        line = lines[index]

        if _is_fence(line):
            # Closing fence found. Body is everything after this line's
            # newline; the trailing newline after the fence is consumed.
            body = "\n".join(lines[index + 1:])
            return metadata, body

        if line.strip() == "":
            # Blank line inside the block is skipped, not an error.
            continue

        if ":" not in line:
            raise ValueError(
                f"malformed frontmatter line (no ':'): {line!r}"
            )

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "":
            raise ValueError(
                f"malformed frontmatter line (empty key): {line!r}"
            )
        metadata[key] = value  # duplicate key -> last wins

    # Opened a block but never found a closing fence -> fail loud.
    raise ValueError("unclosed frontmatter block: no closing '---' fence")
