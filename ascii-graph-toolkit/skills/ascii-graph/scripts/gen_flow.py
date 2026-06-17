"""Linear flow-diagram generator.

render_flow stacks labelled boxes vertically on a common trunk column,
joined by a centered down-arrow:

    ┌──────────┐
    │  収到訂單  │
    └──────────┘
         │
         ▼
    ┌──────────┐
    │ 驗證ユーザー │
    └──────────┘
         ...

All boxes share one interior width (= max label display width), so the
borders line up vertically and the trunk (│ / ▼) sits at one constant
display-column. Widths are measured in terminal cells via
display_width, so CJK (2 cells) and ASCII (1 cell) labels align.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width


def _center(label: str, interior: int) -> str:
    """Pad label to `interior` display cells, label roughly centered.

    Padding is computed in display cells (not characters) so CJK labels
    are not over-padded. Extra odd cell goes to the right.
    """
    slack = interior - display_width(label)
    left = slack // 2
    right = slack - left
    return " " * left + label + " " * right


def render_flow(steps: list[str]) -> str:
    """Render steps as vertically-stacked boxes joined by a down-arrow.

    Each box interior is one space + label + one space, with all boxes
    sized to the widest label so the trunk is straight. Returns the
    multi-line diagram as a single string (no trailing newline).
    """
    if not steps:
        return ""

    # Interior width = widest label + one padding space on each side.
    interior = max(display_width(s) for s in steps) + 2

    # Trunk column = the box's center display-column. Boxes start at
    # column 0; the left border "│" occupies column 0, interior starts
    # at column 1, so the interior center is at 1 + interior // 2.
    trunk_col = 1 + interior // 2
    trunk_pad = " " * trunk_col

    top = "┌" + "─" * interior + "┐"
    bottom = "└" + "─" * interior + "┘"

    blocks = []
    for step in steps:
        body = "│" + _center(step, interior) + "│"
        blocks.append([top, body, bottom])

    lines: list[str] = []
    for i, block in enumerate(blocks):
        lines.extend(block)
        if i != len(blocks) - 1:
            lines.append(trunk_pad + "│")
            lines.append(trunk_pad + "▼")

    return "\n".join(lines)
