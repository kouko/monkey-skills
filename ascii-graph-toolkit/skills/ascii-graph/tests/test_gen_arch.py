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

from align import analyze
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


def _seam_columns(line: str, seam_char: str) -> list[int]:
    """Display-columns (not char indices) of every `seam_char` on the line."""
    return [
        display_width(line[:i]) for i, ch in enumerate(line) if ch == seam_char
    ]


def test_cjk_layers_align_and_pass_oracle():
    """Mixed 中/英/日 labels stay rectangular AND clear the alignment oracle.

    Wide (2-cell) labels are the case where a char-count layout silently
    drifts: a separator ┬ computed by list-index instead of display-column
    lands one cell off under CJK, and the seam check (checks_seam) flags the
    orphaned vertical. We assert BOTH observable consequences:

      1. every rendered line has the SAME display width (rectangularity), and
      2. analyze() — the seam + table + kink oracle — finds zero issues,

    so junctions must be placed in DISPLAY cells, not character positions.
    """
    layers = [
        {
            "name": "展示層 Presentation",
            "components": ["網頁 Web", "モバイル App", "Desktop"],
        },
        {
            "name": "ビジネス Logic",
            "components": ["訂單 Service", "Inventory"],
        },
    ]

    out = render_arch(layers)
    lines = out.splitlines()

    # 1. Rectangular: one shared display width across every line.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"CJK lines misaligned: {sorted(widths)}"

    # 2. The oracle is clean — no seam drift, no table-width drift, no kink.
    _report, issues = analyze(out)
    assert issues == [], f"oracle found drift under CJK: {issues}"

    # 3. Every box's separator ┬ still lands under the row │ in DISPLAY cells.
    #    A list-index junction would shift under the wide chars while keeping
    #    widths equal, so seam alignment needs its own CJK assertion.
    for box_start in range(0, len(lines), 5):
        separator, row_line = lines[box_start + 2], lines[box_start + 3]
        sep_junctions = _seam_columns(separator, "┬")
        inner_row_seams = _seam_columns(row_line, "│")[1:-1]
        assert sep_junctions == inner_row_seams, (
            f"box at line {box_start + 1}: separator ┬ {sep_junctions} "
            f"misaligned with row │ {inner_row_seams} under CJK"
        )


def test_slack_distributed_evenly():
    """Extra outer width is shared across a layer's cells, not dumped on one.

    When a layer's natural component-row is narrower than the shared outer
    interior, the leftover cells are spread EVENLY (remainder, then last cell)
    so the box reads as proportioned columns — not three skinny cells beside
    one bloated tail. We measure each cell's display width between the row's │
    seams; the max and min interior-cell widths must differ by at most one
    cell (the integer remainder).
    """
    layers = [
        # A long layer name forces ~26 cells of slack onto the 3-cell layer.
        {
            "name": "WideLayerNameForcesLotsOfSlackHere",
            "components": ["a", "b", "c"],
        },
        {"name": "x", "components": ["q"]},
    ]

    out = render_arch(layers)
    lines = out.splitlines()
    row_line = lines[3]  # the a/b/c component row of the first box

    # Split the interior (between the outer │…│) on the inner │ seams to get
    # each cell's rendered text, and measure its display width.
    interior_text = row_line[1:-1]
    cell_widths = [display_width(cell) for cell in interior_text.split("│")]
    assert len(cell_widths) == 3, f"expected 3 cells, got {cell_widths}"

    spread = max(cell_widths) - min(cell_widths)
    assert spread <= 1, (
        f"slack not distributed evenly across cells: widths {cell_widths} "
        f"(spread {spread} > 1 cell)"
    )


def test_single_layer_single_component():
    """A single-layer, single-component diagram is a clean rectangular box.

    Degenerate inputs (one component, one layer) must still render a box with
    a top, name, separator, row, and bottom — all the same display width — and
    pass the alignment oracle. With one component there are no inner seams, so
    the separator is a plain ├──┤ rule.
    """
    out = render_arch([{"name": "Only", "components": ["Solo"]}])
    lines = out.splitlines()

    assert len(lines) == 5, f"expected a 5-line single box, got {len(lines)}"
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"degenerate box not rectangular: {sorted(widths)}"

    _report, issues = analyze(out)
    assert issues == [], f"oracle found drift in degenerate box: {issues}"

    # No inner component seam: the separator has no ┬ junctions.
    assert "┬" not in lines[2], "single-component separator should have no ┬"


def test_multiline_component():
    """A layer with a `\n` component and a `\n` layer name grows taller.

    The band's row height = max line-count among its component cells, and a
    multi-line layer NAME renders as multiple centered name lines. Cells
    TOP-align: the taller cell's text fills the upper rows, with blank padding
    below for shorter cells. The shared outer width still spans all bands, and
    every output line keeps one equal display width.
    """
    layers = [
        {
            "name": "資料層\nData Layer",  # two name lines
            "components": ["快取\nCache", "DB"],  # 2-line CJK cell + 1-line cell
        },
        {
            "name": "Single",
            "components": ["Plain"],
        },
    ]

    out = render_arch(layers)
    lines = out.splitlines()

    # 1. Rectangular: one shared display width across every line.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"multiline lines misaligned: {sorted(widths)}"

    # 2. The first band gains extra rows. Single-line band = 5 lines
    #    [top, name, separator, row, bottom]. The first band has a 2-line name
    #    (+1 name line) and a 2-line tallest cell (+1 row line), so it is
    #    5 + 1 + 1 = 7 lines. Total = 7 + 5 = 12 lines.
    assert len(lines) == 12, f"expected 12 lines (7 + 5), got {len(lines)}"

    # 3. The multi-line NAME renders across two centered lines. Both name
    #    fragments must appear as their own lines.
    name_lines = [ln for ln in lines[:7] if "資料層" in ln or "Data Layer" in ln]
    assert any("資料層" in ln for ln in name_lines), "first name line missing"
    assert any("Data Layer" in ln for ln in name_lines), "second name line missing"
    # They are on distinct lines (not concatenated onto one).
    assert not any(
        "資料層" in ln and "Data Layer" in ln for ln in name_lines
    ), "name lines should not be concatenated"

    # 4. The multi-line CELL top-aligns: "快取" appears on the first row line,
    #    "Cache" on the second; the single-line "DB" sits beside "快取" on the
    #    first row line and the blank below it on the second.
    #    Band layout: [top, name0, name1, separator, row0, row1, bottom].
    row0, row1 = lines[4], lines[5]
    assert "快取" in row0 and "DB" in row0, f"row0 missing top cell text: {row0!r}"
    assert "Cache" in row1, f"row1 missing continuation text: {row1!r}"
    assert "DB" not in row1, f"single-line DB should not repeat on row1: {row1!r}"

    # 5. The oracle stays clean under the taller band.
    _report, issues = analyze(out)
    assert issues == [], f"oracle found drift in multiline band: {issues}"
