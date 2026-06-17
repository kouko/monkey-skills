"""Tests for the canonical box-drawing glyph taxonomy (scripts/glyphs.py).

These assert representative membership across ALL line styles (light /
rounded / heavy / double / dashed) so a future deletion of any style from a
frozenset is caught here rather than silently weakening a downstream check.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import glyphs


def test_rounded_corners_in_corners_and_junctions():
    assert "╭" in glyphs.CORNERS
    assert "╭" in glyphs.JUNCTIONS
    assert "╰" in glyphs.CORNERS
    assert "╰" in glyphs.JUNCTIONS


def test_double_style_members():
    assert "║" in glyphs.VERTICALS
    assert "╔" in glyphs.CORNERS
    assert "╬" in glyphs.TEES


def test_heavy_style_members():
    assert "┃" in glyphs.VERTICALS
    assert "┏" in glyphs.CORNERS
    assert "╋" in glyphs.TEES


def test_dashed_style_members():
    assert "┆" in glyphs.VERTICALS
    assert "┄" in glyphs.HORIZONTALS


def test_cross_and_arrow_membership():
    assert "┼" in glyphs.TEES
    assert "┼" in glyphs.JUNCTIONS
    assert "▼" in glyphs.ARROWS
    assert "▼" in glyphs.VERTICAL_CONNECTORS


def test_derived_sets_are_supersets():
    assert glyphs.JUNCTIONS >= glyphs.CORNERS
    assert glyphs.JUNCTIONS >= glyphs.TEES
    assert glyphs.STRUCTURAL >= glyphs.VERTICALS
    assert glyphs.STRUCTURAL >= glyphs.ARROWS


def test_horizontal_in_horizontals_and_box_border():
    assert "─" in glyphs.HORIZONTALS
    assert "─" in glyphs.BOX_BORDER
