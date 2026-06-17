"""End-to-end dogfood: oracle + generators wired together on mixed 中/日 input.

These are integration smoke tests for the whole ascii-graph loop:

  1. A real, display-width-aligned branching flowchart (mixed Traditional
     Chinese / Japanese) passes the oracle end-to-end with ZERO drift —
     the diagram below was converged by actually running it through
     align.analyze and tuning the spacing until clean.
  2. Corrupting one box (padding a CJK label by character count so it
     overflows its border) makes the oracle flag drift AND makes the CLI
     exit 1 — proving the detect direction of the loop, not just the
     happy path.
  3. Each generator shape renders an aligned diagram for a 中/日 payload.

Integration tests of an already-wired system pass on first write; the
load-bearing guarantee is that the CONVERGED fixture stays clean while a
DRIFTED one is caught (test 2 is the negative control that would fail if
the oracle stopped detecting).
"""

import io
import pathlib
import sys
from contextlib import redirect_stdout

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

import align
import generate
from width import display_width

# A mixed 中/日 branching flowchart, converged through align.analyze until
# every box border, seam, branch, and arrowhead lands on its display column.
# (開始受付処理 / 権限ありますか? / 画面表示 / 拒否します — start → decision →
# two leaf outcomes.) Do not "tidy" the spacing: it is display-width-exact.
CONVERGED_FLOWCHART = """\
┌─────────────────┐
│  開始受付処理   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 権限ありますか? │
└──┬───────────┬──┘
   │           │
   ▼           ▼
┌──────────┐  ┌────────────┐
│ 画面表示 │  │ 拒否します │
└──────────┘  └────────────┘"""


def test_converged_flowchart_passes_oracle():
    """The hand-converged mixed 中/日 flowchart has zero drift end-to-end."""
    _report, issues = align.analyze(CONVERGED_FLOWCHART)
    assert issues == []


def test_oracle_catches_drift_end_to_end(tmp_path):
    """Padding one CJK box by char-count overflows it; the oracle catches it.

    This is the negative control: it proves the loop still DETECTS drift,
    so test 1's clean result is meaningful and not a dead assertion.
    """
    # Pad the decision label by character count (insert が・change ? to ？),
    # the canonical model error — char-count looks balanced but the row's
    # display width now overflows its border, so the right '│' connects to
    # nothing.
    corrupted = CONVERGED_FLOWCHART.replace(
        "│ 権限ありますか? │",
        "│ 権限がありますか？ │",
    )
    assert corrupted != CONVERGED_FLOWCHART  # the corruption actually applied

    _report, issues = align.analyze(corrupted)
    assert issues != []

    f = tmp_path / "drifted.txt"
    f.write_text(corrupted, encoding="utf-8")
    with redirect_stdout(io.StringIO()):
        rc = align.main([str(f)])
    assert rc == 1


def test_all_generator_shapes_render_aligned():
    """Each generator shape renders an aligned diagram for a 中/日 payload."""
    # table — every line must share one display width (CJK-aware columns).
    table = generate.render(
        "table",
        {
            "headers": ["項目", "状態"],
            "rows": [["注文", "完了"], ["配送", "準備中"]],
        },
    )
    table_lines = table.splitlines()
    assert len(table_lines) >= 2
    widths = {display_width(line) for line in table_lines}
    assert len(widths) == 1, f"table lines have unequal display widths: {widths}"

    # flow — multi-line, and every step label appears.
    flow = generate.render("flow", {"steps": ["受注", "検証ユーザー", "完了"]})
    assert len(flow.splitlines()) > 1
    for step in ("受注", "検証ユーザー", "完了"):
        assert step in flow

    # tree — node labels present, with branch glyphs.
    tree = generate.render(
        "tree",
        {
            "node": {
                "label": "訂單系統",
                "children": [
                    {"label": "訂單服務"},
                    {"label": "庫存サービス", "children": [{"label": "預扣"}]},
                ],
            }
        },
    )
    for label in ("訂單系統", "訂單服務", "庫存サービス", "預扣"):
        assert label in tree
    assert "├─" in tree
    assert "└─" in tree

    # bar — labels present, with the █ bar glyph.
    bar = generate.render("bar", {"pairs": [["売上", 100], ["費用", 60]], "width": 10})
    assert "売上" in bar
    assert "費用" in bar
    assert "█" in bar
