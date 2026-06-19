"""Contract tests for the shared display-width primitive.

Width policy (from the brief): CJK Wide/Fullwidth = 2, Ambiguous = 1,
box-drawing = 1, control/zero-width = 0. Expectations verified against
the wcwidth package before being asserted here.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import char_width, display_width, split_lines


def test_display_width_cjk_is_two_per_char():
    assert display_width("中文") == 4


def test_display_width_japanese_kana_and_kanji_are_wide():
    # Hiragana, katakana, kanji each render Wide = 2.
    assert display_width("あア漢") == 6


def test_display_width_fullwidth_forms_are_two():
    # U+3000 ideographic space and U+FF21 fullwidth Latin A are Wide = 2.
    assert display_width("　") == 2
    assert display_width("Ａ") == 2


def test_display_width_ascii_is_one_per_char():
    assert display_width("abc123") == 6


def test_display_width_empty_string_is_zero():
    assert display_width("") == 0


def test_char_width_box_drawing_is_one():
    assert char_width("─") == 1
    assert char_width("│") == 1
    assert char_width("┌") == 1


def test_char_width_ascii_is_one():
    assert char_width("a") == 1


def test_char_width_cjk_is_two():
    assert char_width("中") == 2


def test_char_width_ambiguous_is_one():
    # Ambiguous East-Asian width resolves to 1 under the policy.
    assert char_width("·") == 1
    assert char_width("§") == 1


def test_char_width_control_and_zero_width_is_zero():
    # The only house logic on top of wcwidth: w < 0 (and zero-width) -> 0.
    assert char_width("\x00") == 0          # NUL control char
    assert char_width("​") == 0        # zero-width space
    assert char_width("́") == 0        # combining acute accent


def test_split_lines():
    # Always >= 1 element; a bare label is a single-element list.
    assert split_lines("abc") == ["abc"]
    assert split_lines("a\nb") == ["a", "b"]
    assert split_lines("a\n\nb") == ["a", "", "b"]
    assert split_lines("") == [""]


def test_split_lines_handles_cr_crlf():
    # WHY: a carriage-return (\r) is a 0-width cursor-moving control char.
    # A naive label.split("\n") leaves \r embedded ("a\r\nb" -> ["a\r","b"])
    # or fails to split a \r-only label, so the \r passes width checks (0
    # cells) yet CORRUPTS terminal alignment silently at exit 0. splitlines()
    # treats \r, \n and \r\n as real line breaks, so no element retains an
    # embedded control char.
    assert split_lines("a\r\nb") == ["a", "b"]
    assert split_lines("a\rb") == ["a", "b"]
    # No element of any split result may retain an embedded \r.
    for label in ("a\r\nb", "a\rb", "x\r\ny\rz"):
        for piece in split_lines(label):
            assert "\r" not in piece, f"\\r leaked into {piece!r}"


def test_render_flow_crlf_label_leaks_no_carriage_return():
    # WHY: split_lines feeds the render generators. A CRLF label must produce
    # output with NO raw \r byte — a \r is a 0-width cursor-moving control
    # char that passes width checks yet corrupts terminal alignment at exit 0.
    # Encoding the rendered string to bytes proves the leak is closed at the
    # generator boundary (the flow generator stands in for all four render
    # generators that route through split_lines).
    from gen_flow import render_flow

    out = render_flow(["a\r\nb"])
    assert b"\r" not in out.encode("utf-8"), (
        "carriage-return leaked into rendered flow output"
    )
