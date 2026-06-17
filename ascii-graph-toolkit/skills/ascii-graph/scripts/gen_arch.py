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


def _cell(label: str) -> str:
    """A component cell: one pad space + label + one pad space."""
    return " " + label + " "


def _row_natural_width(components: list[str]) -> int:
    """Interior display width of a component row with no extra slack.

    Each cell is ` label ` (label + 2 pad cells); adjacent cells are
    joined by a single `│` seam, so N cells contribute (N - 1) seam
    columns.
    """
    cells_width = sum(display_width(_cell(c)) for c in components)
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
    interior = max(
        max(_row_natural_width(layer["components"]), display_width(layer["name"]))
        for layer in layers
    )

    lines: list[str] = []
    for layer in layers:
        components = layer["components"]
        cells = [_cell(c) for c in components]

        # Distribute the difference between this layer's natural row width and
        # the shared interior EVENLY across the cells: each cell gets a `base`
        # number of extra spaces, and the integer `remainder` is spread one
        # cell at a time so the per-cell widths differ by at most one. The
        # leftover (the remainder) lands on the trailing cells — keeping the
        # last cell as the tie-break sink, deterministic for a given input.
        # This replaces dumping all slack on the last cell, which left skinny
        # cells beside one bloated tail.
        slack = interior - _row_natural_width(components)
        if cells:
            base, remainder = divmod(slack, len(cells))
            n = len(cells)
            cells = [
                cell + " " * (base + (1 if i >= n - remainder else 0))
                for i, cell in enumerate(cells)
            ]
        else:
            # Degenerate empty-row case: pad the single empty cell to interior.
            cells = [" " * interior]

        # Top border + bottom border: ─ across the whole interior, with ┬
        # / ┴ junctions at each inter-cell seam so the column seams are
        # legitimate corners.
        seam_cols = []
        col = 0
        for c in cells[:-1]:
            col += display_width(c)
            seam_cols.append(col)
            col += 1  # the seam character itself

        def border(left: str, junction: str, right: str) -> str:
            chars = ["─"] * interior
            for sc in seam_cols:
                chars[sc] = junction
            return left + "".join(chars) + right

        top = "┌" + "─" * interior + "┐"
        name_line = "│" + _center(layer["name"], interior) + "│"
        separator = border("├", "┬", "┤")
        row_line = "│" + "│".join(cells) + "│"
        bottom = border("└", "┴", "┘")

        lines.extend([top, name_line, separator, row_line, bottom])

    return "\n".join(lines)
