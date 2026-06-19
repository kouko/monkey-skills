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

from width import display_width, split_lines

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

    # Multi-line sequence diagrams are DEFERRED: ANY line break (\n, \r, \r\n)
    # in a name or label would split a row across lines and silently corrupt
    # the diagram. A bare \r is especially insidious — a 0-width cursor-moving
    # control char that passes width checks yet shears alignment at exit 0.
    # split_lines(x) != [x] is true for every line break, so reject loudly
    # here, BEFORE any layout, so the failure is a clear ValueError.
    for nm in participants:
        if split_lines(nm) != [nm]:
            raise ValueError(
                f"line break not supported in participant name: {nm!r}"
            )
    for msg in messages:
        if split_lines(msg["label"]) != [msg["label"]]:
            raise ValueError(
                f"line break not supported in message label: {msg['label']!r}"
            )

    # Per-box interior width = name + one padding space on each side.
    interiors = [display_width(name) + 2 for name in participants]

    # Index-of lookup for message endpoints, used both to size gaps below and
    # to resolve lifeline columns when drawing arrows.
    index_of = {nm: i for i, nm in enumerate(participants)}

    # Per-gap width between adjacent boxes. Default to _GAP, then WIDEN any gap
    # so each message's label fits WITHIN its arrow span. A message spanning
    # participants i..j lands on the two lifeline columns; the inclusive span is
    # (center[j] - center[i] + 1) cells, and must be >= display_width(label).
    # The span is a deterministic function of the interiors (fixed) and the gaps
    # in between, so widening reduces to: ensure the gaps spanned by a message
    # supply enough extra cells. We add any deficit to the LAST gap in the span
    # (deterministic, keeps every prior gap minimal) so a wide label never
    # overflows past its target lifeline.
    gaps = [_GAP] * (len(participants) - 1)

    def _span_cells(i: int, j: int) -> int:
        """Inclusive display-cell span between lifeline columns of boxes i..j.

        Equals (center[hi_j] - center[lo_i] + 1), where center[k] is the column
        the layout walk below assigns: a box occupies (interior + 2) cells (two
        borders) plus gaps[k] before the next box, and its lifeline sits at
        local offset (1 + interior // 2). Computed here by mirroring that walk
        EXACTLY so the sized span equals the final rendered span (no off-by-one).
        """
        lo_i, hi_j = min(i, j), max(i, j)
        # Display-column distance from box lo_i's start to box hi_j's start:
        # each box in between contributes its full width (interior + 2) and the
        # gap that follows it.
        start_delta = sum(
            interiors[k] + 2 + gaps[k] for k in range(lo_i, hi_j)
        )
        # center[k] - box_start[k] = 1 (left border) + interior[k] // 2.
        center_delta = (
            start_delta
            + (1 + interiors[hi_j] // 2)
            - (1 + interiors[lo_i] // 2)
        )
        return center_delta + 1  # inclusive

    for msg in messages:
        i, j = index_of[msg["from"]], index_of[msg["to"]]
        if i == j:
            continue  # self-message is rejected later; skip sizing
        lo_i, hi_j = min(i, j), max(i, j)
        need = display_width(msg["label"])
        deficit = need - _span_cells(i, j)
        if deficit > 0:
            gaps[hi_j - 1] += deficit  # widen the last gap in the span

    # Walk left to right, recording each box's start display-column and its
    # lifeline center display-column. A box occupies (interior + 2) cells (two
    # borders); box k and k+1 are separated by gaps[k] spaces. The lifeline sits
    # at the interior center: box_start + 1 (left border) + interior // 2.
    centers: list[int] = []
    col = 0
    for idx, interior in enumerate(interiors):
        centers.append(col + 1 + interior // 2)
        col += interior + 2
        if idx < len(gaps):
            col += gaps[idx]
    total_width = col

    # Header rows are assembled as concatenated per-box segments joined by the
    # PER-GAP spacing (gaps may differ after widening). Segments are built as
    # STRINGS (not a char grid) so a 2-cell CJK glyph stays a single contiguous
    # character — a char-indexed grid would smear it.
    def _join_segments(segs: list[str]) -> str:
        out = segs[0]
        for k, seg in enumerate(segs[1:]):
            out += " " * gaps[k] + seg
        return out

    top = _join_segments(["┌" + "─" * iw + "┐" for iw in interiors])
    name = _join_segments(["│ " + nm + " │" for nm in participants])

    # The bottom border carries the lifeline stub ┬ at each box's center. Built
    # per box: ─ across the interior with ┬ at the interior-local center.
    bottom_segs = []
    for iw in interiors:
        interior_chars = ["─"] * iw
        interior_chars[iw // 2] = "┬"  # local center mirrors centers[] math
        bottom_segs.append("└" + "".join(interior_chars) + "┘")
    bottom = _join_segments(bottom_segs)

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
