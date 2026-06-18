"""Contract tests for the sequence-diagram generator (participant skeleton).

render_seq lays participant boxes side by side across the top, each with a
lifeline stub `┬` centered under its box and vertical lifelines `│` running
below. Task 1 renders ONLY the participants-only skeleton (messages are
accepted but not yet drawn). Correctness is verified by display_width, not
len: every rendered line MUST occupy the same number of terminal cells, and
each lifeline MUST sit at its participant box's TRUE display-center column so
CJK (2-cell) names stay aligned in a monospace terminal.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from gen_seq import render_seq


def _col_of_char(line: str, target: str) -> list[int]:
    """Display-columns (not char indices) of every `target` on the line."""
    return [
        display_width(line[:i]) for i, ch in enumerate(line) if ch == target
    ]


def test_participants_render_boxes_and_lifelines():
    """3 participants (incl. CJK) render boxes + display-centered lifelines.

    A char-count layout silently drifts under a wide (2-cell) name: the
    lifeline `│` computed by string index instead of display-column lands one
    cell off. We assert three observable consequences:

      1. each participant name appears inside a box,
      2. EVERY rendered line shares one display width (rectangularity), and
      3. each lifeline `│` on the lifeline rows sits at its box's TRUE
         display-center column — computed independently here, not read back.
    """
    participants = ["User", "API サービス", "DB"]
    messages = []  # Task 1: skeleton only, messages not yet rendered.

    out = render_seq(participants, messages)
    lines = out.splitlines()

    # 1. Each participant name appears in the output (inside its box).
    for name in participants:
        assert name in out, f"participant {name!r} missing from output"

    # 2. Rectangular: one shared display width across every line. len-based
    #    padding would leave CJK lines short and skew the lifelines.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"

    # Independently compute each box's expected center display-column.
    # Box interior = name display width + 2 (one pad space each side); the
    # left border "│" occupies the box's first column, so the interior center
    # sits at box_start + 1 + interior // 2. Boxes are laid out left to right
    # with a fixed gap; the gap is whatever separates the first two box top
    # corners "┌". We derive box_start from the actual "┌" positions so the
    # test does not hard-code the gap width (only that centers are consistent).
    top = lines[0]
    box_starts = _col_of_char(top, "┌")
    assert len(box_starts) == len(participants), (
        f"expected {len(participants)} box tops, got {len(box_starts)}"
    )
    expected_centers = [
        start + 1 + (display_width(name) + 2) // 2
        for start, name in zip(box_starts, participants)
    ]

    # 3. The lifeline-stub row (the box's "└──┬─┘" line) carries one ┬ per box,
    #    each at its expected center column.
    stub_row = next(ln for ln in lines if "┬" in ln)
    stub_cols = _col_of_char(stub_row, "┬")
    assert stub_cols == expected_centers, (
        f"lifeline stubs {stub_cols} not at box centers {expected_centers}"
    )

    # ...and the vertical-lifeline rows below carry one │ per box at the SAME
    # columns (and nothing else but spaces).
    lifeline_rows = [
        ln for ln in lines if set(ln) <= {"│", " "} and "│" in ln
    ]
    assert lifeline_rows, "expected at least one vertical-lifeline row"
    for row in lifeline_rows:
        assert _col_of_char(row, "│") == expected_centers, (
            f"lifeline │ columns {_col_of_char(row, '│')} "
            f"not at box centers {expected_centers}"
        )


def _box_centers(top_line: str, participants: list[str]) -> list[int]:
    """Independently recompute each box's lifeline display-center column.

    Mirrors the test-1 derivation: interior = name width + 2 pads, the left
    border occupies the box's first column, so the center sits at
    box_start + 1 + interior // 2. box_start is read from actual "┌" columns.
    """
    box_starts = _col_of_char(top_line, "┌")
    return [
        start + 1 + (display_width(name) + 2) // 2
        for start, name in zip(box_starts, participants)
    ]


def test_message_arrow_direction_and_landing():
    """Each message renders a centered label row + a directional arrow row.

    Three messages exercise the geometry that a naive char-index layout gets
    wrong:

      1. a LEFT→RIGHT message: the arrowhead ► must land EXACTLY on the
         target lifeline's display-center column, shaft is ─;
      2. a RIGHT→LEFT message: the arrowhead ◄ must land EXACTLY on the
         target (leftward) column;
      3. a NON-ADJACENT span (skips a middle participant): on the arrow row
         the shaft CROSSES the intermediate lifeline column (that cell is a
         shaft glyph, not the preserved │);

    plus the two invariants the whole diagram must keep: every line shares one
    display width, and each label is centered over its arrow's span.
    """
    participants = ["A", "B", "C"]
    messages = [
        {"from": "A", "to": "B", "label": "go"},   # left -> right, adjacent
        {"from": "B", "to": "A", "label": "ok"},   # right -> left, adjacent
        {"from": "A", "to": "C", "label": "skip"},  # left -> right, non-adjacent
    ]

    out = render_seq(participants, messages)
    lines = out.splitlines()

    # Shared display width across every line (rectangularity).
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"

    centers = _box_centers(lines[0], participants)
    col_a, col_b, col_c = centers

    # Arrow rows are the lines carrying a horizontal arrowhead glyph.
    arrow_rows = [ln for ln in lines if "►" in ln or "◄" in ln]
    assert len(arrow_rows) == len(messages), (
        f"expected {len(messages)} arrow rows, got {len(arrow_rows)}"
    )
    row_go, row_ok, row_skip = arrow_rows

    # 1. A -> B : single ► head landing on B's column; rightward shaft.
    assert _col_of_char(row_go, "►") == [col_b], (
        f"L->R head at {_col_of_char(row_go, '►')}, expected B col {col_b}"
    )
    assert "◄" not in row_go
    # Shaft cell immediately right of the source is a horizontal glyph.
    assert row_go[col_a + 1] == "─", "L->R shaft should start with ─"

    # 2. B -> A : single ◄ head landing on A's (leftward) column.
    assert _col_of_char(row_ok, "◄") == [col_a], (
        f"R->L head at {_col_of_char(row_ok, '◄')}, expected A col {col_a}"
    )
    assert "►" not in row_ok

    # 3. A -> C : head on C; the intermediate lifeline column B is CROSSED by
    #    the shaft on this row (a horizontal glyph, NOT the preserved │).
    assert _col_of_char(row_skip, "►") == [col_c], (
        f"non-adjacent head at {_col_of_char(row_skip, '►')}, expected C col {col_c}"
    )
    crossing_cell = row_skip[col_b]
    assert crossing_cell != "│", (
        f"intermediate lifeline at col {col_b} should be crossed, got {crossing_cell!r}"
    )
    assert crossing_cell == "─", (
        f"crossing cell should be shaft ─, got {crossing_cell!r}"
    )

    # Label rows: the line directly ABOVE each arrow row carries its label,
    # centered over the arrow's [min, max] column span.
    for arrow_row, msg in zip(arrow_rows, messages):
        idx = lines.index(arrow_row)
        label_row = lines[idx - 1]
        label = msg["label"]
        assert label in label_row, f"label {label!r} missing above its arrow"
        # Centered: the label's midpoint sits within 1 cell of the span midpoint.
        start_col = display_width(label_row[: label_row.index(label)])
        label_mid = start_col + display_width(label) / 2
        lo = min(centers[participants.index(msg["from"])],
                 centers[participants.index(msg["to"])])
        hi = max(centers[participants.index(msg["from"])],
                 centers[participants.index(msg["to"])])
        span_mid = (lo + hi) / 2
        assert abs(label_mid - span_mid) <= 1, (
            f"label {label!r} mid {label_mid} not centered over span "
            f"mid {span_mid}"
        )


def test_long_cjk_label_widens_gap():
    """A CJK label wider than the default lifeline gap widens its span.

    Two adjacent participants (`A`, `B`) carry a message whose CJK label is
    far wider than the default box-to-box gap. Before column-widening, the
    label would clamp/overflow past the target lifeline and shear the
    rectangle. We assert three things a correct widening keeps true:

      1. the FULL label appears on its label row, fitting WITHIN its arrow's
         [src, dst] span — it does not overflow past the target lifeline
         column and is not truncated;
      2. EVERY rendered line shares one display width (rectangularity);
      3. each lifeline `│` sits at consistent display-columns across every
         lifeline row (lifelines stay vertical after the widening shift).
    """
    participants = ["A", "B"]
    # 6 CJK glyphs = 12 display cells, far wider than the default _GAP (3) plus
    # the two 1-cell box interiors: the gap MUST widen to fit this label.
    label = "送信処理開始要"
    messages = [{"from": "A", "to": "B", "label": label}]

    out = render_seq(participants, messages)
    lines = out.splitlines()

    # 2. Rectangular: one shared display width across every line.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"

    centers = _box_centers(lines[0], participants)
    col_a, col_b = centers
    lo, hi = min(col_a, col_b), max(col_a, col_b)

    # Locate the arrow row and its label row (line directly above).
    arrow_rows = [ln for ln in lines if "►" in ln or "◄" in ln]
    assert len(arrow_rows) == 1, f"expected 1 arrow row, got {len(arrow_rows)}"
    arrow_row = arrow_rows[0]
    # Arrowhead lands exactly on B's lifeline column.
    assert _col_of_char(arrow_row, "►") == [col_b], (
        f"arrowhead at {_col_of_char(arrow_row, '►')}, expected B col {col_b}"
    )
    label_row = lines[lines.index(arrow_row) - 1]

    # 1. Full label present and fitting WITHIN the [lo, hi] arrow span.
    assert label in label_row, f"label {label!r} missing / truncated"
    start_col = display_width(label_row[: label_row.index(label)])
    end_col = start_col + display_width(label)
    assert start_col >= lo, (
        f"label starts at col {start_col}, overflows left past span start {lo}"
    )
    assert end_col <= hi + 1, (
        f"label ends at col {end_col}, overflows past target lifeline {hi}"
    )

    # 3. Lifelines vertical: every lifeline row carries │ at the same columns.
    lifeline_rows = [
        ln for ln in lines if set(ln) <= {"│", " "} and "│" in ln
    ]
    assert lifeline_rows, "expected at least one vertical-lifeline row"
    for row in lifeline_rows:
        assert _col_of_char(row, "│") == centers, (
            f"lifeline │ columns {_col_of_char(row, '│')} "
            f"drifted from box centers {centers}"
        )


def test_label_fitting_default_span_does_not_widen():
    """A label that EXACTLY fits the default span must NOT widen the gap.

    Column-widening must add only the deficit between the label width and the
    TRUE inclusive lifeline span (center[dst] - center[src] + 1). If the span
    primitive miscounts (off-by-one), a label that already fits gets a
    spuriously wider gap — the diagram is wider than necessary. We pin this by
    comparing against the messages-less skeleton: a label whose display width
    equals the true default span produces a diagram of the SAME total width as
    the participants-only skeleton (no widening).
    """
    participants = ["A", "B"]

    # Baseline width with no messages = the un-widened skeleton.
    skeleton = render_seq(participants, [])
    base_width = display_width(skeleton.splitlines()[0])

    # True default inclusive span between A's and B's lifelines, computed from
    # the skeleton's own header (independent of render_seq internals).
    centers = _box_centers(skeleton.splitlines()[0], participants)
    default_span = centers[1] - centers[0] + 1

    # A label exactly as wide as that span fits without any widening.
    label = "x" * default_span
    out = render_seq(participants, [{"from": "A", "to": "B", "label": label}])
    out_width = display_width(out.splitlines()[0])

    assert out_width == base_width, (
        f"label of width {default_span} (== true span) over-widened: diagram "
        f"width {out_width} vs minimal {base_width}"
    )
    # And the full label still fits within the (unchanged) span.
    label_row = next(ln for ln in out.splitlines() if label in ln)
    start_col = display_width(label_row[: label_row.index(label)])
    assert start_col >= centers[0] and start_col + default_span <= centers[1] + 1, (
        f"label not within span [{centers[0]}, {centers[1]}]"
    )


def test_self_message_rejected():
    """A message with from == to (self-message) is rejected with ValueError."""
    import pytest

    participants = ["A", "B"]
    messages = [{"from": "A", "to": "A", "label": "loop"}]
    with pytest.raises(ValueError):
        render_seq(participants, messages)
