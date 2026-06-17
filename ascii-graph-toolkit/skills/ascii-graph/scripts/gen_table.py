"""CJK-aligned ASCII/Unicode table generator.

Column widths and cell padding are computed with display_width (terminal
cells), not str len, so CJK/JP wide-character cells align in a monospace
terminal. Unicode box-drawing characters are used by default; ascii_only
falls back to +, -, | so the output survives ASCII-only contexts.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

_UNICODE = {
    "tl": "┌", "tm": "┬", "tr": "┐",
    "ml": "├", "mm": "┼", "mr": "┤",
    "bl": "└", "bm": "┴", "br": "┘",
    "h": "─", "v": "│",
}

_ASCII = {
    "tl": "+", "tm": "+", "tr": "+",
    "ml": "+", "mm": "+", "mr": "+",
    "bl": "+", "bm": "+", "br": "+",
    "h": "-", "v": "|",
}


def _pad(cell: str, width: int) -> str:
    """Left-align cell, right-pad with spaces to `width` display cells."""
    return cell + " " * (width - display_width(cell))


def render_table(
    headers: list[str],
    rows: list[list[str]],
    ascii_only: bool = False,
) -> str:
    g = _ASCII if ascii_only else _UNICODE

    all_rows = [headers, *rows]
    col_widths = [
        max(display_width(row[i]) for row in all_rows)
        for i in range(len(headers))
    ]

    def border(left: str, mid: str, right: str) -> str:
        segments = [g["h"] * (w + 2) for w in col_widths]
        return left + mid.join(segments) + right

    def data_line(cells: list[str]) -> str:
        padded = [" " + _pad(cells[i], col_widths[i]) + " "
                  for i in range(len(col_widths))]
        return g["v"] + g["v"].join(padded) + g["v"]

    lines = [
        border(g["tl"], g["tm"], g["tr"]),
        data_line(headers),
        border(g["ml"], g["mm"], g["mr"]),
        *[data_line(row) for row in rows],
        border(g["bl"], g["bm"], g["br"]),
    ]
    return "\n".join(lines)
