"""Contract tests for the table-block equal-width check.

A "table block" is a maximal run of consecutive lines that each start
and end with a box vertical (│ as the first and last non-space glyph),
optionally bracketed by ┌─┐ / ├─┤ / └─┘ border lines. find_issues flags
any line in a block whose display_width differs from the block's
modal/border display_width — the classic mistake of sizing a CJK table
by character count instead of terminal-cell width.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from checks_table import find_issues


def test_cjk_row_sized_by_char_count_is_flagged():
    # Borders + first row are display-width 12. The second content row was
    # sized to the SAME character count (4 interior chars) but those chars
    # are CJK (2 cells each) vs ASCII, so its display width is wider.
    #   "│中文ab│" -> 1 + 2 + 2 + 1 + 1 + 1 = 8 display cells
    #   "│中文中文│" -> 1 + 2 + 2 + 2 + 2 + 1 = 10 display cells
    # Both have 6 characters, so a naive char-count check sees them as
    # aligned; a display-width check catches the mismatch.
    lines = [
        "┌──────┐",     # top border, width 8
        "│中文ab│",     # width 8
        "│中文中文│",   # width 10 -- wider than the block
        "└──────┘",     # bottom border, width 8
    ]
    issues = find_issues(lines)
    assert len(issues) >= 1
    flagged_line_numbers = {ln for ln, _col, _msg in issues}
    assert 3 in flagged_line_numbers


def test_display_width_aligned_table_has_no_issues():
    # Every line is display-width 8: borders, an ASCII row, and a CJK row
    # whose two wide chars + spacing land on the same terminal width.
    #   "│ ab  │" -> 1+1+1+1+2+1 = wait, build explicitly below.
    # Interior is 6 cells wide on every line.
    lines = [
        "┌──────┐",     # 1 + 6 + 1 = 8
        "│ abcd │",     # 1 + 6 + 1 = 8
        "│ 中文 │",     # 1 + 1 + 2 + 2 + 1 + 1 = 8
        "└──────┘",     # 8
    ]
    assert find_issues(lines) == []
