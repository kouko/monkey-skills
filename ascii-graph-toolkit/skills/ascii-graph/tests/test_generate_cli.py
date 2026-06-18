"""Contract tests for the generate.py dispatch CLI.

render(shape, payload) is the testable seam (no subprocess); it routes
to the matching generator and returns the rendered diagram. Each shape
is exercised with a CJK/JP fixture so we prove the dispatch preserves
the underlying generator's CJK behavior, not just that it returns text.
"""

import io
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from width import display_width

from generate import main, render


def test_table_dispatch_preserves_display_width_alignment():
    payload = {
        "headers": ["項目", "狀態", "數量"],
        "rows": [["使用者ログイン", "完了", "123"]],
    }
    out = render("table", payload)
    lines = out.splitlines()
    widths = {display_width(line) for line in lines}
    # WHY: a single shared display-width across every line is the only
    # observable proof that dispatch reached the real CJK-aware table
    # renderer (not a len-based stand-in that would skew wide cells).
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"


def test_flow_dispatch_contains_cjk_labels_and_is_multiline():
    payload = {"steps": ["収到訂單", "驗證ユーザー", "完了"]}
    out = render("flow", payload)
    assert out
    assert "収到訂單" in out and "驗證ユーザー" in out
    assert "\n" in out


def test_tree_dispatch_contains_cjk_labels_and_is_multiline():
    payload = {
        "node": {
            "label": "訂單系統",
            "children": [{"label": "庫存サービス"}],
        }
    }
    out = render("tree", payload)
    assert out
    assert "訂單系統" in out and "庫存サービス" in out
    assert "\n" in out


def test_bar_dispatch_contains_cjk_labels_and_renders_bars():
    payload = {"pairs": [["売上", 100], ["成本", 40]], "width": 20}
    out = render("bar", payload)
    assert out
    assert "売上" in out and "成本" in out
    assert "█" in out


def test_arch_shape_routes():
    payload = {
        "layers": [
            {"name": "Presentation", "components": ["Web App", "モバイル"]},
            {"name": "資料層", "components": ["DB"]},
        ]
    }
    out = render("arch", payload)
    lines = out.splitlines()
    assert out
    assert "\n" in out
    # WHY: a single shared display-width across every line is the only
    # observable proof that dispatch reached the real CJK-aware arch
    # renderer (boxes stack to one shared interior width).
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"
    assert "モバイル" in out and "資料層" in out


def test_seq_shape_routes():
    payload = {"participants": ["User", "API サービス", "DB"], "messages": []}
    out = render("seq", payload)
    lines = out.splitlines()
    assert out
    assert "\n" in out
    # WHY: a shared display-width across the lifeline rows is the only
    # observable proof that dispatch reached the real CJK-aware seq
    # renderer (lifelines align under display-centered participant boxes,
    # not character-centered ones).
    assert "API サービス" in out and "User" in out and "DB" in out
    widths = {display_width(line) for line in lines}
    assert len(widths) == 1, f"lines misaligned: {sorted(widths)}"


def test_main_seq_returns_0(monkeypatch, capsys):
    payload = '{"participants":["A","B"],"messages":[]}'
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))
    assert main(["seq"]) == 0
    out = capsys.readouterr().out
    assert out.strip()


def test_main_arch_returns_0(monkeypatch, capsys):
    payload = '{"layers":[{"name":"L1","components":["a","b"]}]}'
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))
    assert main(["arch"]) == 0
    out = capsys.readouterr().out
    assert out.strip()


def test_unknown_shape_raises():
    try:
        render("bogus", {})
    except (ValueError, KeyError):
        return
    raise AssertionError("render did not reject an unknown shape")


def test_main_unknown_shape_returns_2():
    # WHY: the CLI contract promises a clean exit code 2 (not a crash)
    # for an unknown shape so callers can branch on the status.
    assert main(["bogus"]) == 2
