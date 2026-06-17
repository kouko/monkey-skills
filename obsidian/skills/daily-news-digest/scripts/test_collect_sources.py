#!/usr/bin/env python3
"""Tests for collect_sources.py — run with: python3 test_collect_sources.py

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


def _run(vault: Path):
    out = subprocess.run(
        [sys.executable, str(SCRIPT), DATE, str(vault)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def test_references_collected_at_all_depths():
    """references/ notes at root, one-level, and nested depths must all be
    collected — the date prefix is the relevance filter, not folder depth."""
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        _note(vault / "references" / f"{DATE}-root.md", "root level")
        _note(vault / "references" / "ai" / f"{DATE} sub.md", "one level")
        _note(vault / "references" / "playlist" / "series" / f"{DATE} deep.md", "nested")
        # a non-matching date must be excluded
        _note(vault / "references" / "ai" / "2026-01-01 old.md", "old")

        manifest = _run(vault)
        titles = {c["title"] for c in manifest["news_candidates"]}

        assert manifest["counts"]["news_candidates"] == 3, manifest["counts"]
        assert {"root level", "one level", "nested"} == titles, titles
    print("PASS test_references_collected_at_all_depths")


def test_research_collected_recursively():
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp)
        _note(vault / "research" / f"{DATE} tool eval.md", "research note")
        manifest = _run(vault)
        assert manifest["counts"]["research"] == 1, manifest["counts"]
    print("PASS test_research_collected_recursively")


def test_empty_day_returns_zero():
    with tempfile.TemporaryDirectory() as tmp:
        manifest = _run(Path(tmp))
        assert manifest["counts"]["news_candidates"] == 0
        assert manifest["counts"]["research"] == 0
    print("PASS test_empty_day_returns_zero")


if __name__ == "__main__":
    test_references_collected_at_all_depths()
    test_research_collected_recursively()
    test_empty_day_returns_zero()
    print("All tests passed.")
