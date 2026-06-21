"""Shared display-width primitive for terminal-cell measurement.

Width policy:
  - CJK Wide / Fullwidth characters       -> 2 cells
  - Ambiguous-width characters            -> 1 cell
  - Box-drawing characters (U+2500..257F) -> 1 cell
  - Control / zero-width characters       -> 0 cells
  - Everything else (narrow ASCII etc.)   -> 1 cell

Delegates to wcwidth.wcwidth, whose East_Asian_Width handling matches
this policy: Wide/Fullwidth report 2, Ambiguous report 1, box-drawing
report 1, and non-printable characters report -1 (mapped here to 0).
"""

from wcwidth import wcwidth


def char_width(c: str) -> int:
    """Return the terminal-cell width of a single character."""
    w = wcwidth(c)
    return 0 if w < 0 else w


def display_width(s: str) -> int:
    """Return the total terminal-cell width of a string."""
    return sum(char_width(c) for c in s)


def split_lines(label: str) -> list[str]:
    """Split a label into a list of >= 1 physical line, no embedded controls.

    Uses str.splitlines(), which breaks on \\n, \\r, \\r\\n (and \\v/\\f), so a
    CRLF or bare-CR label becomes real line breaks with NO embedded
    carriage-return left in any element. A bare \\r is a 0-width
    cursor-moving control char: left embedded it passes width checks yet
    silently corrupts terminal alignment, so it must become a real break.
    Empty input yields [""] (splitlines("") is [], normalized to one line).
    """
    return label.splitlines() or [""]
