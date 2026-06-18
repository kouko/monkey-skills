"""Sequence-diagram generator (participants + message rows).

render_seq lays participant boxes side by side across the top, each with a
lifeline stub `┬` centered under its box and vertical lifelines `│` running
below, then renders each message as a label row + a directional arrow row:

    ┌──────┐   ┌──────────────┐   ┌────┐
    │ User │   │ API サービス │   │ DB │
    └──┬───┘   └──────┬───────┘   └─┬──┘
       │              │             │
          fetch
       │──────────────►             │
                          read
       │              │─────────────►

Each message `{"from","to","label"}` renders TWO rows below the lifeline
header, in list order: a label row (label centered over the source→target
span) and an arrow row (`────►` rightward / `◄────` leftward, the arrowhead
landing EXACTLY on the target lifeline column). Arrows spanning non-adjacent
participants CROSS the intermediate lifeline columns on the arrow row (the
shaft occupies those cells). On non-arrow rows every lifeline shows `│` at its
fixed column. A self-message (from == to) is rejected.

All widths are measured in terminal cells via display_width, so CJK (2 cells)
and ASCII (1 cell) names align in a monospace terminal: the lifeline sits at
each box's TRUE display-center column, not its character-center.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

# Source the directional arrowheads from the canonical taxonomy rather than
# hardcoding, so the glyph set stays single-sourced with the check modules.
from glyphs import ARROWS

_ARROW_RIGHT = "►"
_ARROW_LEFT = "◄"
assert {_ARROW_RIGHT, _ARROW_LEFT} <= ARROWS  # taxonomy guard, not behaviour
_SHAFT = "─"

# Display-cell gap between adjacent participant boxes (boxes must not touch).
_GAP = 3
# Number of vertical-lifeline rows rendered below the box header.
_LIFELINE_ROWS = 2


def render_seq(participants: list[str], messages: list[dict]) -> str:
    """Render a sequence diagram: participant boxes + lifelines + message rows.

    `participants` is a list of name strings; `messages` is a list of
    {"from","to","label"} dicts. Each message is drawn as a label row + a
    directional arrow row (see module docstring). Raises ValueError on a
    self-message (from == to). Returns the multi-line diagram as a single
    string (no trailing newline).
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

    # A bare lifeline row: │ at each center, spaces elsewhere. All cells are
    # single display-cell glyphs, so a column-indexed char grid is exact.
    def _lifeline_row() -> list[str]:
        row = [" "] * total_width
        for center in centers:
            row[center] = "│"
        return row

    # Vertical-lifeline rows between the header and the first message.
    for _ in range(_LIFELINE_ROWS):
        lines.append("".join(_lifeline_row()))

    # Name -> lifeline display-column lookup for message endpoints.
    center_of = {nm: c for nm, c in zip(participants, centers)}

    for msg in messages:
        src, dst = msg["from"], msg["to"]
        if src == dst:
            raise ValueError(
                f"self-message not supported: {src!r} -> {dst!r}"
            )
        src_col, dst_col = center_of[src], center_of[dst]

        # Label row: a lifeline row with the label centered over the arrow's
        # [lo, hi] column span. Overwrite the span cells with the label chars
        # (label glyphs may be wide, so place by display-column accumulation).
        lo, hi = min(src_col, dst_col), max(src_col, dst_col)
        label = msg["label"]
        label_row = _lifeline_row()
        span_mid = (lo + hi) / 2
        start = int(round(span_mid - display_width(label) / 2))
        start = max(0, min(start, total_width - display_width(label)))
        col = start
        for ch in label:
            label_row[col] = ch
            col += display_width(ch)
            # A wide glyph consumes two columns; blank the trailing cell so the
            # join keeps one char per occupied display-column.
            for pad in range(col - display_width(ch) + 1, col):
                label_row[pad] = ""
        lines.append("".join(label_row))

        # Arrow row: shaft ─ across [lo, hi], with the arrowhead on dst_col and
        # the source endpoint kept as │. Intermediate lifelines are CROSSED by
        # the shaft (overwritten), not preserved.
        arrow_row = [" "] * total_width
        for c in range(lo, hi + 1):
            arrow_row[c] = _SHAFT
        arrow_row[src_col] = "│"
        arrow_row[dst_col] = _ARROW_RIGHT if dst_col > src_col else _ARROW_LEFT
        lines.append("".join(arrow_row))

    return "\n".join(lines)
