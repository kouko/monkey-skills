#!/usr/bin/env python3
"""Tests for cot_mermaid.py — run: python3 test_cot_mermaid.py"""

import cot_mermaid as m


def test_chain_3_colours_green_purple_cyan():
    out = m.render({"type": "chain", "nodes": [
        {"title": "觸發", "bullets": ["a", "b"]},
        {"title": "機制", "bullets": ["c"]},
        {"title": "結論", "bullets": ["d"]},
    ]})
    assert "flowchart LR" in out
    assert "style N0 fill:#d3f9d8" in out   # trigger 綠
    assert "style N1 fill:#e5dbff" in out   # mech 紫
    assert "style N2 fill:#c5f6fa" in out   # concl 青
    assert "result" not in out and "#ffe8cc" not in out  # 3 hops → no 橙
    print("PASS test_chain_3_colours_green_purple_cyan")


def test_chain_4_has_result_orange_second_to_last():
    out = m.render({"type": "chain", "nodes": [
        {"title": "t", "bullets": ["x"]}, {"title": "m", "bullets": ["x"]},
        {"title": "r", "bullets": ["x"]}, {"title": "c", "bullets": ["x"]},
    ]})
    assert "style N2 fill:#ffe8cc" in out    # second-to-last = result 橙
    assert "style N3 fill:#c5f6fa" in out    # last = concl 青
    print("PASS test_chain_4_has_result_orange_second_to_last")


def test_node_paren_sanitised_and_bullets():
    out = m.render({"type": "chain", "nodes": [
        {"title": "升息(1%)", "bullets": ["0.75%→1%", "31年首見"]},
        {"title": "結論", "bullets": ["x"]},
    ]})
    assert "升息「1%」" in out and "(1%)" not in out
    assert out.count("• ") >= 3
    assert "<div style='text-align:left'>" in out
    print("PASS test_node_paren_sanitised_and_bullets")


def test_web_roles_and_edges():
    out = m.render({"type": "web",
        "nodes": [
            {"id": "A", "title": "事件", "bullets": ["x"], "role": "trigger"},
            {"id": "B", "title": "傳導", "bullets": ["y"], "role": "mech"},
            {"id": "F", "title": "結論", "bullets": ["z"], "role": "concl"},
        ],
        "edges": [
            {"from": "A", "to": "B", "label": "因果"},
            {"from": "B", "to": "F", "arrow": "-.->"},
        ]})
    assert "flowchart TD" in out
    assert "-->|因果|" in out
    assert "-.->" in out
    assert "style A fill:#d3f9d8" in out and "style F fill:#c5f6fa" in out
    # A defined inline once, then bare ref allowed
    assert out.count('A["') == 1
    print("PASS test_web_roles_and_edges")


if __name__ == "__main__":
    test_chain_3_colours_green_purple_cyan()
    test_chain_4_has_result_orange_second_to_last()
    test_node_paren_sanitised_and_bullets()
    test_web_roles_and_edges()
    print("All tests passed.")
