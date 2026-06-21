"""Table-block equal-width check.

Detect table blocks and flag any row whose display_width differs from
the block's reference width. This catches CJK tables sized by character
count instead of terminal-cell width.

A table block is a maximal run of consecutive lines that share the same
LEFT frame column -- the display-column of the leftmost box vertical (│)
for a content row, or the leftmost bracket (┌├└) for a border. Sharing a
left frame column is what distinguishes a real table from a flowchart:
a branch connector such as "│    │" hangs at a different column than the
box it descends from, so it forms its own (non-table) group.

A group is treated as a table -- and therefore width-checked -- only when
it has >=2 content rows (a real multi-row table), OR exactly one content
row bracketed by a border at the SAME right frame column (a framed single
row). A lone box whose content row does not line up with its border, and
a stray branch connector, are diagram elements, not tables.

The reference width is the border width when a border is present,
otherwise the modal (most common) row width.
"""

import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import char_width, display_width

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


def _frame_columns(line: str) -> tuple[int, int]:
    """Return (left, right) display-columns of the line's frame glyphs.

    For a content row these are the leftmost/rightmost │; for a border
    they are the leftmost/rightmost bracket. Assumes _is_block_line(line).
    """
    if _is_content_line(line):
        anchors = _VERTICAL
    else:
        anchors = _BORDER_FIRST + _BORDER_LAST
    col = 0
    positions: list[int] = []
    for ch in line:
        if ch in anchors:
            positions.append(col)
        col += char_width(ch)
    return positions[0], positions[-1]


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
        left = _frame_columns(lines[i])[0]
        i += 1
        # Extend the group only while the left frame column stays the same.
        while i < n and _is_block_line(lines[i]) and _frame_columns(lines[i])[0] == left:
            i += 1
        block = list(range(start, i))
        issues.extend(_check_block(lines, block))
    return issues


def _is_table(lines: list[str], block: list[int]) -> bool:
    """True if the line group is a real table, not a stray diagram element."""
    content = [idx for idx in block if _is_content_line(lines[idx])]
    borders = [idx for idx in block if _is_border_line(lines[idx])]
    if len(content) >= 2:
        return True
    if len(content) == 1 and borders:
        content_right = _frame_columns(lines[content[0]])[1]
        return any(_frame_columns(lines[b])[1] == content_right for b in borders)
    return False


def _check_block(
    lines: list[str], block: list[int]
) -> list[tuple[int, int, str]]:
    if not _is_table(lines, block):
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
