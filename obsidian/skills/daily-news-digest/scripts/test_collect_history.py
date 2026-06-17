#!/usr/bin/env python3
"""Tests for collect_history.py — run: python3 test_collect_history.py"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("collect_history.py")


def _note(path: Path, body: str, title=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = f"---\ntitle: {title}\n---\n\n" if title else ""
    path.write_text(fm + body, encoding="utf-8")


def _run(*args):
    out = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_matches_keyword_in_range_sorted_by_date():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        _note(v / "references/finance/2026-05-01 早盤.md", "油價升至 104 美元，地緣風險。")
        _note(v / "references/finance/2026-06-01 早盤.md", "油價回落至 90 美元。")
        _note(v / "investing/2026-04-15 能源.md", "原油與通膨分析。")
        _note(v / "references/ai/2026-05-20 tutorial.md", "Claude Code 教學，與油無關主題。")
        m = _run("油價,原油", v, "--since", "2026-04-01", "--until", "2026-06-15")
        dates = [n["date"] for n in m["timeline"]]
        assert dates == ["2026-04-15", "2026-05-01", "2026-06-01"], dates
        assert m["counts"]["dates"] == 3, m["counts"]
        # snippet captures the number near the keyword
        may = next(n for n in m["timeline"] if n["date"] == "2026-05-01")
        assert "104" in may["snippet"], may["snippet"]
    print("PASS test_matches_keyword_in_range_sorted_by_date")


def test_until_excludes_later_dates():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        _note(v / "references/finance/2026-06-10 a.md", "美伊衝突升溫。")
        _note(v / "references/finance/2026-06-20 b.md", "美伊停戰。")
        m = _run("美伊", v, "--until", "2026-06-15")
        dates = [n["date"] for n in m["timeline"]]
        assert dates == ["2026-06-10"], dates
    print("PASS test_until_excludes_later_dates")


def test_per_day_cap_reports_dropped():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        for i in range(5):
            _note(v / f"references/finance/2026-06-10 note{i}.md", "美伊 事件。")
        m = _run("美伊", v, "--per-day", "2")
        assert m["counts"]["notes_kept"] == 2, m["counts"]
        assert m["counts"]["notes_dropped_by_cap"] == 3, m["counts"]
    print("PASS test_per_day_cap_reports_dropped")


if __name__ == "__main__":
    test_matches_keyword_in_range_sorted_by_date()
    test_until_excludes_later_dates()
    test_per_day_cap_reports_dropped()
    print("All tests passed.")
