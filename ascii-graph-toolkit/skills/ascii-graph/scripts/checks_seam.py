"""checks_seam.py — vertical-seam connect check for ASCII/Unicode diagrams.

Verification-class scaffolding: the model draws, this measures and reports
drift, the model fixes. It does NOT lay out and does NOT edit the diagram.

Check: every box vertical (│ ┃ ║ and other line styles) must connect to a
structural glyph (a vertical, corner / junction, or arrowhead) directly above
or below at the SAME display column. A CJK label padded by char-count (the
common model error) pushes its row's right vertical to a column no border
reaches -> flagged, with the exact line + display column.

Display columns are measured via the shared width primitive (UAX #11):
CJK Wide = 2 cells, Ambiguous / box-drawing = 1 cell.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from glyphs import JUNCTIONS, VERTICALS
from width import char_width

# Glyphs that can anchor a vertical seam: a vertical of any line style, any
# corner / tee / cross, or a vertical arrowhead. Derived from the canonical
# glyph taxonomy so every line style (light / heavy / double / dashed) is
# covered uniformly.
ANCHORS = VERTICALS | JUNCTIONS | frozenset("▼▲↑↓")


def _columns(line: str) -> list[tuple[int, str]]:
    """Return (display-column, char) for each char in the line."""
    out, col = [], 0
    for ch in line:
        out.append((col, ch))
        col += char_width(ch)
    return out


def find_issues(lines: list[str]) -> list[tuple[int, int, str]]:
    """Find box-vertical '│' glyphs with no structural anchor above or below.

    Returns one (1-based line number, display-column, message) tuple per
    violation.
    """
    anchor_cols = [
        {col for col, ch in _columns(line) if ch in ANCHORS} for line in lines
    ]
    issues: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        above = anchor_cols[i - 1] if i > 0 else set()
        below = anchor_cols[i + 1] if i + 1 < len(lines) else set()
        for col, ch in _columns(line):
            if ch in VERTICALS and col not in above and col not in below:
                issues.append(
                    (
                        i + 1,
                        col,
                        f"'{ch}' at display-col {col} connects to nothing vertically",
                    )
                )
    return issues
