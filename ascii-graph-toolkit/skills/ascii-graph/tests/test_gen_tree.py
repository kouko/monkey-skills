"""Contract tests for the Unicode tree/hierarchy generator.

Branch glyphs (├─ └─ │) precede the labels, so the columns at which
those glyphs appear are constant regardless of CJK label width — that
column-stability is the observable proof the tree was rendered with a
correct per-ancestor continuation prefix.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from gen_tree import render_tree


def _tree():
    return {
        "label": "訂單系統",
        "children": [
            {"label": "訂單服務"},
            {"label": "庫存サービス", "children": [{"label": "預扣"}]},
        ],
    }


def test_root_label_is_first_line():
    out = render_tree(_tree())
    lines = out.splitlines()
    assert lines[0] == "訂單系統"


def test_branch_glyphs_at_expected_columns():
    out = render_tree(_tree())
    lines = out.splitlines()

    # WHY: branch glyphs precede the CJK labels, so their columns are
    # constant. A first-level child's connector must start at column 0;
    # if continuation prefixes were computed with len()-vs-display-width
    # confusion or off-by-one indentation, these columns would drift.
    first_child = lines[1]
    assert first_child.startswith("├─ "), first_child
    assert first_child[3:] == "訂單服務"

    last_top_child = lines[2]
    # WHY: the LAST top-level child must use └─, not ├─ — proves the
    # renderer distinguishes last-sibling from the rest.
    assert last_top_child.startswith("└─ "), last_top_child
    assert last_top_child[3:] == "庫存サービス"


def test_grandchild_under_last_sibling_uses_space_continuation():
    out = render_tree(_tree())
    lines = out.splitlines()

    # The grandchild "預扣" sits under the LAST top-level child, so its
    # ancestor continuation column is spaces ("   "), not "│  ".
    grandchild = lines[3]
    # WHY: under a last-sibling the vertical bar must NOT be drawn;
    # leaking "│" here is the classic continuation-prefix bug.
    assert grandchild.startswith("   └─ "), repr(grandchild)
    assert grandchild[6:] == "預扣"
    assert "│" not in grandchild


def test_grandchild_under_non_last_sibling_uses_bar_continuation():
    tree = {
        "label": "root",
        "children": [
            {"label": "first", "children": [{"label": "deep"}]},
            {"label": "second"},
        ],
    }
    out = render_tree(tree)
    lines = out.splitlines()

    # "deep" sits under "first", which is NOT the last sibling, so the
    # ancestor continuation column must keep the vertical bar "│  ".
    grandchild = lines[2]
    assert grandchild.startswith("│  └─ "), repr(grandchild)
    assert grandchild[6:] == "deep"
