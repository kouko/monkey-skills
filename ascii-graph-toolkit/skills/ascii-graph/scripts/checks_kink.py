"""Kink + arrowhead-landing checks for ASCII connector seams.

Catches what the plain seam check misses:

1. Seam-straightness — in a vertical run of connectors (│ ┬ ┴ ▼ ▲ on
   consecutive lines), a connector whose display-column shifts between
   adjacent lines WITHOUT a junction glyph to justify the bend is a kink
   (the off-by-one case where a box's ┬ sat at col 9 but the trunk │ at
   col 10).

2. Arrowhead-into-box — a ▼ (or ▲) whose display-column is not within the
   horizontal span of the box it points into (next line for ▼, previous
   line for ▲) is flagged as a misaimed arrowhead.

Heuristics stay conservative: shifts justified by a junction glyph
(┬ ┴ ├ ┤ ┼ └ ┘ ┌ ┐) on either endpoint are never flagged.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width  # noqa: E402

# Connectors that participate in a vertical seam run.
CONNECTORS = frozenset("│┬┴▼▲")
# Arrowheads and the direction (line offset) of the box they point into.
ARROW_TARGET_OFFSET = {"▼": +1, "▲": -1}
# Junction glyphs that legitimately justify a column shift in a seam.
JUNCTIONS = frozenset("┬┴├┤┼└┘┌┐")
# Glyphs that form a box's horizontal border / corners.
BOX_BORDER = frozenset("─┼┬┴├┤└┘┌┐")


def _connector_columns(line: str) -> dict:
    """Map display-column -> connector glyph for each connector on the line."""
    cols = {}
    col = 0
    for ch in line:
        if ch in CONNECTORS:
            cols[col] = ch
        col += display_width(ch)
    return cols


def _box_span(line: str):
    """Return (start_col, end_col) display-column span of box border on a line.

    Returns None when the line has no box-border glyphs. The span covers the
    leftmost to the rightmost border cell — the horizontal extent an
    arrowhead must land within to be considered aimed into the box.
    """
    start = None
    end = None
    col = 0
    for ch in line:
        if ch in BOX_BORDER:
            if start is None:
                start = col
            end = col
        col += display_width(ch)
    if start is None:
        return None
    return (start, end)


def find_issues(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return [(line_no_1based, display_col_0based, message), ...]."""
    issues = []
    per_line = [_connector_columns(ln) for ln in lines]

    for idx, cols in enumerate(per_line):
        below = per_line[idx + 1] if idx + 1 < len(per_line) else {}

        for col, glyph in cols.items():
            # --- Arrowhead-into-box ---------------------------------------
            if glyph in ARROW_TARGET_OFFSET:
                tgt = idx + ARROW_TARGET_OFFSET[glyph]
                if 0 <= tgt < len(lines):
                    span = _box_span(lines[tgt])
                    if span is not None and not (span[0] <= col <= span[1]):
                        issues.append(
                            (
                                idx + 1,
                                col,
                                f"arrowhead '{glyph}' at col {col} misses target "
                                f"box span {span[0]}..{span[1]}",
                            )
                        )

            # --- Seam-straightness ----------------------------------------
            # A plain connector continued below at a shifted column, with no
            # junction glyph on either endpoint to justify the bend, is a kink.
            if not below or glyph in JUNCTIONS:
                continue
            if col in below:
                continue  # straight continuation
            for bcol, bglyph in below.items():
                if bglyph in JUNCTIONS:
                    continue  # the shift is justified downstream
                if abs(bcol - col) >= 1:
                    issues.append(
                        (
                            idx + 2,
                            bcol,
                            f"seam kink: connector drifts from col {col} to "
                            f"col {bcol} with no junction glyph",
                        )
                    )

    return issues
