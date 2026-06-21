#!/usr/bin/env python3
"""Tests for collect_sources.py — run with: python3 -B test_collect_sources.py

No test framework dependency; plain asserts so it runs anywhere Python 3 does.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("collect_sources.py")
DATE = "2026-06-15"


def _note(path: Path, title: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\ntitle: {title}\ntags: [news]\n---\n\n"
        "This is a substantive lead paragraph long enough to be a real snippet.\n",
        encoding="utf-8",
    )


def _run(vault: Path, *extra):
    out = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), DATE, str(vault), *extra],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def test_wide_net_collects_all_folders_and_depths():
    """Every dated note is a candidate regardless of folder/depth — the model
    triages later. No folder layout is assumed."""
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        _note(v / f"{DATE}-root.md", "root level")
        _note(v / "references" / "ai" / f"{DATE} ref.md", "in references")
        _note(v / "references" / "playlist" / "s" / f"{DATE} deep.md", "nested deep")
        _note(v / "investing" / f"{DATE} own.md", "in investing")
        _note(v / "inbox" / f"{DATE} drop.md", "in inbox")
        _note(v / "projects" / "x" / f"{DATE} proj.md", "in projects")
        _note(v / "references" / "ai" / "2026-01-01 old.md", "wrong date")

        m = _run(v)
        titles = {c["title"] for c in m["candidates"]}
        assert m["counts"]["candidates"] == 6, m["counts"]
        assert {"root level", "in references", "nested deep",
                "in investing", "in inbox", "in projects"} == titles, titles
    print("PASS test_wide_net_collects_all_folders_and_depths")


def test_excludes_wiki_news_templates_and_dotfolders():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        _note(v / "wiki" / f"{DATE} entity.md", "wiki page")
        _note(v / "news" / f"{DATE} 每日新聞.md", "prior digest")
        _note(v / "_templates" / f"{DATE} tmpl.md", "template")
        _note(v / ".obsidian" / f"{DATE} cfg.md", "config")
        _note(v / "references" / f"{DATE} keep.md", "kept")

        m = _run(v)
        titles = {c["title"] for c in m["candidates"]}
        assert titles == {"kept"}, titles
        assert m["excluded_folders"] == ["_templates", "news", "wiki"], m["excluded_folders"]
    print("PASS test_excludes_wiki_news_templates_and_dotfolders")


def test_exclude_flag_overrides():
    with tempfile.TemporaryDirectory() as tmp:
        v = Path(tmp)
        _note(v / "archive" / f"{DATE} a.md", "archived")
        _note(v / "references" / f"{DATE} r.md", "ref")
        # custom exclude: drop archive AND references, keep nothing here
        m = _run(v, "--exclude", "archive,references")
        assert m["counts"]["candidates"] == 0, m["counts"]
    print("PASS test_exclude_flag_overrides")


def test_empty_day_returns_zero():
    with tempfile.TemporaryDirectory() as tmp:
        m = _run(Path(tmp))
        assert m["counts"]["candidates"] == 0
    print("PASS test_empty_day_returns_zero")


if __name__ == "__main__":
    test_wide_net_collects_all_folders_and_depths()
    test_excludes_wiki_news_templates_and_dotfolders()
    test_exclude_flag_overrides()
    test_empty_day_returns_zero()
    print("All tests passed.")
