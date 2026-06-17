"""Contract tests for the layered-architecture diagram generator.

render_arch stacks one INDEPENDENT box per layer, all sharing one outer
interior width. Correctness is verified by display_width, not len: every
rendered line MUST occupy the same number of terminal cells, and the two
layer boxes MUST share one outer width, so the diagram reads as a clean
vertical stack in a monospace terminal.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from gen_arch import render_arch


def test_two_layers_share_outer_width():
    layers = [
        {
            "name": "Presentation",
            "components": ["Web App", "Mobile App", "Desktop"],
        },
        {
            "name": "Business Logic",
            "components": ["OrderService", "InventoryService"],
        },
    ]

    out = render_arch(layers)
    lines = out.splitlines()

    # Locate each box's top border (the first line of every box starts
    # with "┌"). There are exactly two layers, hence two top borders.
    top_borders = [ln for ln in lines if ln.startswith("┌")]
    assert len(top_borders) == 2, f"expected 2 boxes, got {len(top_borders)}"

    # 1. Both boxes share ONE outer width — the only observable proof that
    #    every layer was sized to the shared max interior, not to its own
    #    natural component-row width.
    w0, w1 = display_width(top_borders[0]), display_width(top_borders[1])
    assert w0 == w1, f"layer boxes differ in outer width: {w0} vs {w1}"

    # 2. EVERY line shares that one display width — len-based padding would
    #    leave some lines short and skew the stack; a single shared cell
    #    width is the rectangularity guarantee.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"

    # 3. Each box's separator junctions (┬) land at the SAME display-columns
    #    as the component-row seams (│). This is the file's central claim
    #    ("legitimate junctions keep align.py's kink check happy") and its
    #    most intricate logic — a one-column junction shift keeps every line
    #    width equal (passing assertion 2 silently), so seam alignment needs
    #    its own assertion. We check the first box: rows are
    #    [top, name, separator, row, bottom] repeating every 5 lines.
    def seam_columns(line: str, seam_char: str) -> list[int]:
        return [
            display_width(line[:i])
            for i, ch in enumerate(line)
            if ch == seam_char
        ]

    separator, row_line = lines[2], lines[3]
    sep_junctions = seam_columns(separator, "┬")
    row_seams = seam_columns(row_line, "│")
    # The row's │ includes the two outer borders; the inner seams are the
    # ones that must coincide with the separator's ┬.
    inner_row_seams = row_seams[1:-1]
    assert sep_junctions == inner_row_seams, (
        f"separator ┬ columns {sep_junctions} do not align with "
        f"row │ seams {inner_row_seams}"
    )
    assert sep_junctions, "expected at least one inter-cell junction"
