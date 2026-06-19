"""Layered-architecture diagram generator.

render_arch stacks one INDEPENDENT box per layer, vertically, with no
connector arrows between them. Each box is:

    ┌────────────────────────────────────┐   top border
    │            Presentation            │   centered layer name
    ├──────────┬────────────┬────────────┤   separator (┬ per cell seam)
    │ Web App  │ Mobile App │ Desktop    │   component-cell row
    └──────────┴────────────┴────────────┘   bottom border (┴ per seam)

All layer boxes share ONE outer interior width = max over all layers of
(that layer's natural component-row width, and the layer-name display
width). The component seams use ├ … ┬ … ┤ / └ … ┴ … ┘ junctions so the
vertical column seams are legitimate (keeps align.py's kink check happy).

Widths are measured in terminal cells via display_width, so CJK (2 cells)
and ASCII (1 cell) labels align in a monospace terminal.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width, split_lines


def _center(label: str, interior: int) -> str:
    """Pad label to `interior` display cells, label roughly centered.

    Padding is computed in display cells (not characters) so CJK labels
    are not over-padded. Extra odd cell goes to the right.
    """
    slack = interior - display_width(label)
    left = slack // 2
    right = slack - left
    return " " * left + label + " " * right


def _cell_width(label: str) -> int:
    """Display width of a (possibly multi-line) cell: one pad space each
    side of the WIDEST physical line + that widest line."""
    return max(display_width(ln) for ln in split_lines(label)) + 2


def _cell_height(label: str) -> int:
    """Number of physical lines in a (possibly multi-line) cell."""
    return len(split_lines(label))


def _row_natural_width(components: list[str]) -> int:
    """Interior display width of a component row with no extra slack.

    Each cell is sized to its widest physical line + 2 pad cells; adjacent
    cells are joined by a single `│` seam, so N cells contribute (N - 1)
    seam columns.
    """
    cells_width = sum(_cell_width(c) for c in components)
    seams = max(len(components) - 1, 0)
    return cells_width + seams


def render_arch(layers: list[dict]) -> str:
    """Render layers as vertically-stacked independent boxes.

    `layers` is [{"name": str, "components": [str, ...]}, ...]. Returns
    the multi-line diagram as a single string (no trailing newline).
    """
    if not layers:
        return ""

    # Shared outer interior width = max over all layers of the layer's
    # natural component-row width and its name display width.
    def _name_width(name: str) -> int:
        return max(display_width(ln) for ln in split_lines(name))

    interior = max(
        max(_row_natural_width(layer["components"]), _name_width(layer["name"]))
        for layer in layers
    )

    lines: list[str] = []
    for layer in layers:
        components = layer["components"]

        # Distribute the difference between this layer's natural row width and
        # the shared interior EVENLY across the cells: each cell gets a `base`
        # number of extra spaces, and the integer `remainder` is spread one
        # cell at a time so the per-cell widths differ by at most one. The
        # leftover (the remainder) lands on the trailing cells — keeping the
        # last cell as the tie-break sink, deterministic for a given input.
        # This replaces dumping all slack on the last cell, which left skinny
        # cells beside one bloated tail.
        #
        # We compute each cell's final DISPLAY WIDTH (not its rendered text):
        # a cell may be multi-line, so a single padded string can't represent
        # it. The widths drive both the per-row line rendering and the seam
        # placement, which stay constant across every physical row line.
        if components:
            slack = interior - _row_natural_width(components)
            base, remainder = divmod(slack, len(components))
            n = len(components)
            cell_widths = [
                _cell_width(c) + base + (1 if i >= n - remainder else 0)
                for i, c in enumerate(components)
            ]
            # Row height = the tallest cell's physical line count; all cells
            # TOP-align into this many rows (blank-padded below).
            row_height = max(_cell_height(c) for c in components)
        else:
            # Degenerate empty-row case: one empty cell padded to interior.
            components = [""]
            cell_widths = [interior]
            row_height = 1

        # Pre-split each cell into top-aligned physical lines, each padded
        # (one pad space + line + filler) to its cell width.
        def _pad_line(line: str, width: int) -> str:
            # interior width = width; one leading pad space, label, then
            # trailing spaces to fill. Mirrors the old ` label ` + slack.
            return " " + line + " " * (width - display_width(line) - 1)

        cell_line_grids = []
        for comp, width in zip(components, cell_widths):
            phys = split_lines(comp)
            padded = [_pad_line(ln, width) for ln in phys]
            blank = " " * width
            padded += [blank] * (row_height - len(padded))
            cell_line_grids.append(padded)

        # Top border + bottom border: ─ across the whole interior, with ┬
        # / ┴ junctions at each inter-cell seam so the column seams are
        # legitimate corners. Seam columns derive from cell WIDTHS, constant
        # across every physical row line.
        seam_cols = []
        col = 0
        for width in cell_widths[:-1]:
            col += width
            seam_cols.append(col)
            col += 1  # the seam character itself

        def border(left: str, junction: str, right: str) -> str:
            chars = ["─"] * interior
            for sc in seam_cols:
                chars[sc] = junction
            return left + "".join(chars) + right

        top = "┌" + "─" * interior + "┐"
        name_lines = [
            "│" + _center(nl, interior) + "│"
            for nl in split_lines(layer["name"])
        ]
        separator = border("├", "┬", "┤")
        row_lines = [
            "│" + "│".join(grid[r] for grid in cell_line_grids) + "│"
            for r in range(row_height)
        ]
        bottom = border("└", "┴", "┘")

        lines.append(top)
        lines.extend(name_lines)
        lines.append(separator)
        lines.extend(row_lines)
        lines.append(bottom)

    return "\n".join(lines)
