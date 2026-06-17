"""Table-block equal-width check.

Detect table blocks -- maximal runs of consecutive lines that each start
and end with a box vertical (│ as the first and last non-space glyph),
optionally bracketed by border lines (┌─┐ / ├─┤ / └─┘) -- and flag any
line in a block whose display_width differs from the block's reference
display_width. The reference is the border width when a border is
present, otherwise the modal (most common) line width. This catches CJK
tables sized by character count instead of terminal-cell width.
"""

import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

_VERTICAL = "│"
_BORDER_FIRST = "┌├└"
_BORDER_LAST = "┐┤┘"


def _is_content_line(line: str) -> bool:
    """True if the line's first and last non-space glyph are both │."""
    stripped = line.strip()
    return len(stripped) >= 2 and stripped[0] == _VERTICAL and stripped[-1] == _VERTICAL


def _is_border_line(line: str) -> bool:
    """True if the line is a box border (┌─┐ / ├─┤ / └─┘ family)."""
    stripped = line.strip()
    return (
        len(stripped) >= 2
        and stripped[0] in _BORDER_FIRST
        and stripped[-1] in _BORDER_LAST
    )


def _is_block_line(line: str) -> bool:
    return _is_content_line(line) or _is_border_line(line)


def find_issues(lines: list[str]) -> list[tuple[int, int, str]]:
    """Flag table-block lines whose display width breaks the block.

    Returns (1-based line number, display column or 0, message) tuples.
    """
    issues: list[tuple[int, int, str]] = []
    i = 0
    n = len(lines)
    while i < n:
        if not _is_block_line(lines[i]):
            i += 1
            continue
        start = i
        while i < n and _is_block_line(lines[i]):
            i += 1
        block = list(range(start, i))
        issues.extend(_check_block(lines, block))
    return issues


def _check_block(
    lines: list[str], block: list[int]
) -> list[tuple[int, int, str]]:
    # A lone border or single line cannot disagree with itself.
    if len(block) < 2:
        return []

    widths = {idx: display_width(lines[idx]) for idx in block}
    border_widths = [widths[idx] for idx in block if _is_border_line(lines[idx])]
    if border_widths:
        reference = Counter(border_widths).most_common(1)[0][0]
    else:
        reference = Counter(widths.values()).most_common(1)[0][0]

    issues: list[tuple[int, int, str]] = []
    for idx in block:
        w = widths[idx]
        if w != reference:
            issues.append(
                (
                    idx + 1,
                    reference,
                    f"table line display width {w} differs from block width {reference}",
                )
            )
    return issues
