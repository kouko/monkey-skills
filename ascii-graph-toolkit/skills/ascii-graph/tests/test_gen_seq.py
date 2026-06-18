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
