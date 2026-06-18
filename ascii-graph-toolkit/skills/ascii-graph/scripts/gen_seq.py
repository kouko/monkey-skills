"""Sequence-diagram generator (participant skeleton).

render_seq lays participant boxes side by side across the top, each with a
lifeline stub `┬` centered under its box and vertical lifelines `│` running
below:

    ┌──────┐   ┌──────────────┐   ┌────┐
    │ User │   │ API サービス │   │ DB │
    └──┬───┘   └──────┬───────┘   └─┬──┘
       │              │             │
       │              │             │

This task renders ONLY the participants-only skeleton — `messages` is accepted
for forward compatibility but NOT yet drawn (that is a later task). All widths
are measured in terminal cells via display_width, so CJK (2 cells) and ASCII
(1 cell) names align in a monospace terminal: the lifeline sits at each box's
TRUE display-center column, not its character-center.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

# Display-cell gap between adjacent participant boxes (boxes must not touch).
_GAP = 3
# Number of vertical-lifeline rows rendered below the box header.
_LIFELINE_ROWS = 2


def render_seq(participants: list[str], messages: list[dict]) -> str:
    """Render participant boxes + lifelines (skeleton; messages not yet drawn).

    `participants` is a list of name strings; `messages` is a list of
    {"from","to","label"} dicts (accepted but unused in this task). Returns the
    multi-line diagram as a single string (no trailing newline).
    """
    if not participants:
        return ""

    # Per-box interior width = name + one padding space on each side.
    interiors = [display_width(name) + 2 for name in participants]

    # Walk left to right, recording each box's start display-column and its
    # lifeline center display-column. A box occupies (interior + 2) cells (two
    # borders); adjacent boxes are separated by _GAP spaces. The lifeline sits
    # at the interior center: box_start + 1 (left border) + interior // 2.
    centers: list[int] = []
    col = 0
    for interior in interiors:
        centers.append(col + 1 + interior // 2)
        col += interior + 2 + _GAP
    total_width = col - _GAP  # trailing gap is not part of the diagram

    gap = " " * _GAP

    # Header rows are assembled as concatenated per-box segments joined by the
    # gap. Segments are built as STRINGS (not a char grid) so a 2-cell CJK glyph
    # stays a single contiguous character — a char-indexed grid would smear it.
    top = gap.join("┌" + "─" * iw + "┐" for iw in interiors)
    name = gap.join(
        "│ " + nm + " │" for nm in participants
    )

    # The bottom border carries the lifeline stub ┬ at each box's center. Built
    # per box: ─ across the interior with ┬ at the interior-local center.
    bottom_segs = []
    for iw in interiors:
        interior_chars = ["─"] * iw
        interior_chars[iw // 2] = "┬"  # local center mirrors centers[] math
        bottom_segs.append("└" + "".join(interior_chars) + "┘")
    bottom = gap.join(bottom_segs)

    lines = [top, name, bottom]

    # Vertical-lifeline rows hold only single-cell glyphs (│ / space), so a
    # display-column char grid is exact here.
    for _ in range(_LIFELINE_ROWS):
        row = [" "] * total_width
        for center in centers:
            row[center] = "│"
        lines.append("".join(row))

    return "\n".join(lines)
