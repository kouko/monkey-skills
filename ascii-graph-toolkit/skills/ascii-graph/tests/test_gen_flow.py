"""Contract tests for the linear-flow generator (render_flow).

render_flow stacks each step as a box (┌─┐ │ label │ └─┘) on a common
trunk column, joined by a centered down-arrow. The two invariants that
make the diagram look right on a terminal are:

  (a) every box-border line shares the same display_width -- so the
      left/right borders line up vertically regardless of CJK/ASCII
      label width;
  (b) the connector │ and arrow ▼ sit at one constant display-column
      across the whole output -- so the trunk is straight.

Both are measured with width.display_width (terminal cells), never
character count, because the labels mix CJK (2 cells) and ASCII (1).
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from gen_flow import render_flow


def _display_col_of(line: str, glyph: str) -> int:
    """Display-column (0-based, in terminal cells) of glyph in line.

    Returns -1 if the glyph is absent. Uses display_width of the prefix
    so wide characters before the glyph advance the column by 2.
    """
    idx = line.find(glyph)
    if idx < 0:
        return -1
    return display_width(line[:idx])


def test_all_box_borders_share_one_display_width():
    out = render_flow(["收到訂單", "驗證ユーザー", "完了"])
    border_lines = [
        ln for ln in out.splitlines() if ln.lstrip().startswith(("┌", "└"))
    ]
    # Two borders per box, three boxes.
    assert len(border_lines) == 6
    widths = {display_width(ln) for ln in border_lines}
    assert len(widths) == 1, f"box borders differ in display width: {widths}"


def test_connector_and_arrow_share_one_trunk_column():
    out = render_flow(["收到訂單", "驗證ユーザー", "完了"])
    cols = []
    for ln in out.splitlines():
        for glyph in ("│", "▼"):
            if glyph in ln and ln.strip() in (glyph, "│", "▼"):
                cols.append(_display_col_of(ln, glyph))
    # Linear flow of 3 steps -> 2 connectors, each "│" then "▼".
    assert len(cols) >= 2, f"expected connector/arrow lines, got {cols}"
    assert len(set(cols)) == 1, f"trunk column not constant: {cols}"
