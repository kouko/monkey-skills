#!/usr/bin/env python3
"""Tests for cot_mermaid.py — run: python3 -B test_cot_mermaid.py"""

import subprocess
import sys

import cot_mermaid as m


def _exits2(payload):
    """render(payload) must fail cleanly with SystemExit(2), not a traceback."""
    try:
        m.render(payload)
    except SystemExit as e:
        assert e.code == 2, e.code
        return
    raise AssertionError("expected SystemExit(2)")


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


def test_bad_input_exits_cleanly_not_traceback():
    # dangling edge → undefined node
    _exits2({"type": "web",
             "nodes": [{"id": "A", "title": "t", "bullets": ["x"], "role": "trigger"}],
             "edges": [{"from": "A", "to": "ZZ"}]})
    # node missing 'bullets'
    _exits2({"type": "chain", "nodes": [{"title": "a"}, {"title": "b", "bullets": ["x"]}]})
    # unknown type
    _exits2({"type": "pie", "nodes": []})
    # chain too short
    _exits2({"type": "chain", "nodes": [{"title": "a", "bullets": ["x"]}]})
    # bad role in web
    _exits2({"type": "web",
             "nodes": [{"id": "A", "title": "t", "bullets": ["x"], "role": "boom"}],
             "edges": []})
    print("PASS test_bad_input_exits_cleanly_not_traceback")


def test_invalid_json_stdin_exits_2():
    p = subprocess.run([sys.executable, "-B", m.__file__],
                       input="not json {{", capture_output=True, text=True)
    assert p.returncode == 2, p.returncode
    assert "invalid JSON" in p.stderr, p.stderr
    print("PASS test_invalid_json_stdin_exits_2")


if __name__ == "__main__":
    test_chain_3_colours_green_purple_cyan()
    test_chain_4_has_result_orange_second_to_last()
    test_node_paren_sanitised_and_bullets()
    test_web_roles_and_edges()
    test_bad_input_exits_cleanly_not_traceback()
    test_invalid_json_stdin_exits_2()
    print("All tests passed.")
