"""Contract tests for the CJK-aligned horizontal bar chart generator.

Label-column alignment is verified by display_width, not len: every
row's label segment MUST occupy the same number of terminal cells so
that CJK/JP/EN-mixed labels line up before the bar starts. Bar lengths
are verified to scale proportionally to the values.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from gen_bar import render_bar


def _label_segment(line: str) -> str:
    # WHY: the label column ends at the first bar/space boundary. The
    # label is right-padded with spaces then a single space separator,
    # so the label segment is everything up to (but not including) the
    # first '█'. Measuring this substring by display_width is the only
    # observable proof the padding used cell-width, not char-len.
    bar_start = line.index("█")
    return line[:bar_start]


def test_label_column_shares_one_display_width_across_rows():
    pairs = [("使用者", 120), ("注文", 80), ("AirPods", 40)]

    out = render_bar(pairs)
    lines = out.splitlines()

    widths = {display_width(_label_segment(line)) for line in lines}
    # WHY: a single shared label-segment cell-width across every row is
    # the only observable proof CJK/JP labels were padded by display
    # width — len-based padding would make the wide-char rows come up
    # short and the bars would not start at a common column.
    assert len(widths) == 1, f"label column misaligned: {sorted(widths)}"


def test_bar_lengths_are_proportional_to_values():
    pairs = [("使用者", 120), ("注文", 80), ("AirPods", 40)]
    width = 20

    out = render_bar(pairs, width=width)
    lines = out.splitlines()

    bar_runs = [line.count("█") for line in lines]

    # WHY: encodes the scaling intent — the max value maps to `width`
    # cells, and a half-value row maps to ~half. Without proportional
    # scaling these asserts cannot hold.
    assert bar_runs[0] == width, f"max row should fill width: {bar_runs[0]}"
    assert bar_runs[0] == max(bar_runs), "max-value row must have longest bar"
    # 40 is one-third of 120 -> ~width/3; 80 is two-thirds -> ~2*width/3.
    assert bar_runs[2] == round(40 / 120 * width)
    assert bar_runs[1] == round(80 / 120 * width)


def test_empty_input_returns_empty_string():
    # WHY: empty input must not crash (max() on an empty sequence raises).
    # Parity with gen_flow's empty-steps guard.
    assert render_bar([]) == ""


def test_newline_in_label_rejected():
    # WHY: a bar row is inherently one line. A label containing '\n'
    # would silently split one row into two and corrupt the chart
    # alignment, so it must fail loud (ValueError) rather than render.
    import pytest

    with pytest.raises(ValueError):
        render_bar([("a\nb", 10)])

    # A normal bar still renders — the guard must not block valid input.
    assert render_bar([("ok", 10)]) != ""
