import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from checks_kink import find_issues  # noqa: E402

# --- Fixtures -------------------------------------------------------------
# Display columns are 0-based. Box-drawing glyphs are 1 cell wide (width.py).

# Off-by-one connector kink: the box's ┬ sits at col 9, but the trunk │
# directly below it drifts to col 10 with no junction glyph to justify it.
#                  0123456789012
KINK_SEAM = [
    "┌───────┐",        # box top
    "│  box  │",
    "└───┬───┘",        # ┬ at col 4 (exit point)
    "    │",            # │ at col 4 — straight so far
    "     │",           # │ drifts to col 5 — KINK, no junction
]

# Straight vertical seam: connector column is stable across the run.
STRAIGHT_SEAM = [
    "┌───────┐",
    "│  box  │",
    "└───┬───┘",        # ┬ at col 4
    "    │",            # │ at col 4
    "    │",            # │ at col 4
    "    ▼",            # ▼ at col 4
]

# Justified bend: the column shift is explained by a corner junction glyph,
# so it must NOT be flagged as a kink.
JUSTIFIED_BEND = [
    "    │",            # │ at col 4
    "    └──┐",         # └ at col 4 (junction justifies the turn)
    "       │",         # │ at col 7 — shift justified by the corner above
]

# Arrowhead landing inside the target box's horizontal span (cols 8..16).
ARROW_INTO_BOX = [
    "        │",        # │ at col 8
    "        ▼",        # ▼ at col 8
    "┌───────────────┐",  # box spans cols 0..16 — 8 is inside
    "│     target    │",
    "└───────────────┘",
]

# Arrowhead pointing OUTSIDE the target box's horizontal span.
ARROW_MISSES_BOX = [
    "                      │",   # │ at col 22
    "                      ▼",   # ▼ at col 22 — to the right of the box
    "┌───────────────┐",         # box spans cols 0..16 — 22 is outside
    "│     target    │",
    "└───────────────┘",
]

# Display-width-aligned nested box: the outer │ at each side terminates at a
# corner on the line below, and inner boxes sit fully inside. No connector
# bends, so there must be no kink flagged.
NESTED_BOX = [
    "┌────────────────────┐",
    "│  データ層          │",
    "│  ┌────┐  ┌────┐    │",
    "│  │ PG │  │RDS │    │",
    "│  └────┘  └────┘    │",
    "└────────────────────┘",
]

# Two boxes side by side on one row: each │ terminates at a corner directly
# below it. No seam bends, so there must be no kink flagged.
TWO_SIDE_BY_SIDE_BOXES = [
    "┌──┐ ┌──┐",
    "│a │ │b │",
    "└──┘ └──┘",
]

# Correctly-aligned ROUNDED box. ╭╮╰╯ are corners (junctions): each │ side
# terminates at a rounded corner directly below. No bend, no kink flagged.
ROUNDED_BOX = [
    "╭──────╮",
    "│ 中文 │",
    "╰──────╯",
]

# Correctly-aligned HEAVY box. ┏┓┗┛ are corners; ┃ is a vertical connector.
# Width-correct, so each ┃ side terminates at a heavy corner directly below.
HEAVY_BOX = [
    "┏━━━━┓",
    "┃ 中 ┃",
    "┗━━━━┛",
]

# Corrupted DOUBLE-line box: a double-line trunk ║ exits via a ╦ tee, runs
# straight one line, then drifts one column with no junction to justify it —
# the off-by-one kink mirror of KINK_SEAM but built from double-line glyphs.
# Proves ║ is now actually checked as a vertical connector (it was skipped —
# silently clean — before the glyphs.py taxonomy refactor).
DOUBLE_BOX_CORRUPTED = [
    "╔═══╗",
    "║ X ║",
    "╚═╦═╝",            # ╦ tee at col 2 (exit point)
    "  ║",              # ║ at col 2 — straight so far
    "   ║",             # ║ drifts to col 3 — KINK, no junction
]


# --- Seam-straightness tests ---------------------------------------------


def test_off_by_one_kink_flagged():
    issues = find_issues(KINK_SEAM)
    assert len(issues) >= 1


def test_straight_seam_clean():
    assert find_issues(STRAIGHT_SEAM) == []


def test_justified_bend_not_flagged():
    assert find_issues(JUSTIFIED_BEND) == []


def test_nested_box_no_false_kink():
    assert find_issues(NESTED_BOX) == []


def test_two_side_by_side_boxes_no_false_kink():
    assert find_issues(TWO_SIDE_BY_SIDE_BOXES) == []


def test_rounded_box_no_false_kink():
    assert find_issues(ROUNDED_BOX) == []


def test_heavy_box_no_false_kink():
    assert find_issues(HEAVY_BOX) == []


def test_double_box_corrupted_is_caught():
    assert find_issues(DOUBLE_BOX_CORRUPTED) != []


# --- Arrowhead-into-box tests --------------------------------------------


def test_arrow_into_box_clean():
    assert find_issues(ARROW_INTO_BOX) == []


def test_arrow_missing_box_flagged():
    issues = find_issues(ARROW_MISSES_BOX)
    assert len(issues) >= 1


# --- Contract shape ------------------------------------------------------


def test_issue_tuple_shape():
    issues = find_issues(KINK_SEAM)
    ln, col, msg = issues[0]
    assert isinstance(ln, int) and ln >= 1
    assert isinstance(col, int) and col >= 0
    assert isinstance(msg, str) and msg
