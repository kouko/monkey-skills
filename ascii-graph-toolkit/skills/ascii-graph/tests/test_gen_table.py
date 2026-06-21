"""Contract tests for the CJK-aligned table generator.

Alignment correctness is verified by display_width, not len: every
rendered line MUST occupy the same number of terminal cells so that
CJK/JP/EN-mixed cells line up in a monospace terminal.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from gen_table import render_table

_BOX_CHARS = set("┌┬┐│├┼┤└┴┘─")


def test_mixed_cjk_jp_en_table_lines_share_one_display_width():
    headers = ["項目", "狀態", "數量"]
    rows = [["使用者ログイン", "完了", "123"]]

    out = render_table(headers, rows)
    lines = out.splitlines()

    widths = {display_width(line) for line in lines}
    # WHY: a single shared cell-width across every line is the only
    # observable proof that CJK/JP cells were padded by display width
    # (not byte/char len) — len-based padding would make wide-char
    # lines come up short and the columns would skew.
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"


def test_multiline_cell():
    # One CJK cell spans 2 physical lines; its neighbor is single-line.
    headers = ["項目", "說明"]
    rows = [["使用者", "登入\n登出"]]

    out = render_table(headers, rows)
    lines = out.splitlines()

    # WHY: a 2-line cell must make its whole row 2 physical lines tall, so
    # both labels are visible — collapsing to 1 line would lose "登出".
    # Layout: top border, header (1 line), separator, data (2 lines),
    # bottom border = 6 lines.
    assert len(lines) == 6, f"expected 6 lines, got {len(lines)}: {lines}"

    data_lines = lines[3:5]
    # WHY: the short cell ("使用者") is top-aligned — its text sits on the
    # first physical line and the second physical line is blank-padded, so
    # the column stays rectangular instead of repeating the label.
    assert "使用者" in data_lines[0]
    assert "使用者" not in data_lines[1]
    assert "登入" in data_lines[0]
    assert "登出" in data_lines[1]

    # WHY: every output line sharing one display width is the only proof
    # that the multi-line row was padded by display width (not char len)
    # and that the blank-padded short cell kept the table rectangular.
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"


def test_ascii_only_output_has_no_box_drawing_chars():
    headers = ["項目", "狀態"]
    rows = [["使用者ログイン", "完了"]]

    out = render_table(headers, rows, ascii_only=True)

    offenders = _BOX_CHARS & set(out)
    assert not offenders, f"ascii_only output leaked box chars: {offenders}"
    assert "+" in out and "-" in out and "|" in out
