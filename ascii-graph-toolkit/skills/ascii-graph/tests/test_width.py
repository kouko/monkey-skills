"""Contract tests for the shared display-width primitive.

Width policy (from the brief): CJK Wide/Fullwidth = 2, Ambiguous = 1,
box-drawing = 1, control/zero-width = 0. Expectations verified against
the wcwidth package before being asserted here.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import char_width, display_width


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
