"""Tests for dedup.py — norm_url, filter_novel, and the __main__ CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from dedup import filter_novel, norm_url

_DEDUP = str(Path(__file__).parent / "dedup.py")


def test_norm_and_budget() -> None:
    # norm_url: strip www., strip trailing slash, lowercase
    assert norm_url("https://www.x.com/a/") == "x.com/a"

    # norm_url: no www., no trailing slash
    assert norm_url("https://example.com/path") == "example.com/path"

    # norm_url: parse failure falls back to lowercased raw string
    assert norm_url("not a url AT ALL") == "not a url at all"

    # filter_novel: duplicate URL goes to dupes
    seen: dict = {"x.com/a": True}
    results = [{"url": "https://www.x.com/a/", "title": "X", "relevance": "high"}]
    novel, dupes, budget_dropped, slots = filter_novel(results, seen, fetch_slots=5)
    assert novel == []
    assert len(dupes) == 1
    assert dupes[0]["dupOf"] == "x.com/a"
    assert budget_dropped == []
    assert slots == 5  # not decremented for a dupe

    # filter_novel: novel high-relevance decrements fetch_slots and lands in novel
    seen2: dict = {}
    results2 = [{"url": "https://example.com/page", "title": "P", "relevance": "high"}]
    novel2, dupes2, dropped2, slots2 = filter_novel(results2, seen2, fetch_slots=3)
    assert len(novel2) == 1
    assert novel2[0]["url"] == "https://example.com/page"
    assert dupes2 == []
    assert dropped2 == []
    assert slots2 == 2  # decremented

    # filter_novel: low-relevance result when fetch_slots<=0 goes to budget_dropped
    seen3: dict = {}
    results3 = [{"url": "https://low.com/", "title": "L", "relevance": "low"}]
    novel3, dupes3, dropped3, slots3 = filter_novel(results3, seen3, fetch_slots=0)
    assert novel3 == []
    assert dupes3 == []
    assert len(dropped3) == 1
    assert dropped3[0]["url"] == "https://low.com/"
    assert slots3 == 0  # unchanged

    # filter_novel: high-relevance is NEVER budget-dropped even when fetch_slots<=0
    seen4: dict = {}
    results4 = [{"url": "https://high.com/article", "title": "H", "relevance": "high"}]
    novel4, dupes4, dropped4, slots4 = filter_novel(results4, seen4, fetch_slots=0)
    assert len(novel4) == 1
    assert dropped4 == []
    assert slots4 == -1  # decremented below zero


def test_filter_novel_missing_key_raises() -> None:
    """filter_novel must raise ValueError (not KeyError) for malformed LLM result dicts."""
    # missing "url"
    with pytest.raises(ValueError, match="url"):
        filter_novel([{"title": "No URL", "relevance": "high"}], {}, fetch_slots=5)

    # missing "relevance"
    with pytest.raises(ValueError, match="relevance"):
        filter_novel([{"url": "https://example.com/", "title": "No rel"}], {}, fetch_slots=5)

    # non-enum relevance value
    with pytest.raises(ValueError, match="bogus"):
        filter_novel(
            [{"url": "https://example.com/page", "title": "Bad rel", "relevance": "bogus"}],
            {},
            fetch_slots=5,
        )


def test_filter_novel_medium_budget_dropped() -> None:
    """medium-relevance result must land in budget_dropped when fetch_slots is exhausted."""
    seen: dict = {}
    results = [{"url": "https://medium.com/article", "title": "M", "relevance": "medium"}]
    novel, dupes, budget_dropped, slots = filter_novel(results, seen, fetch_slots=0)
    assert novel == []
    assert dupes == []
    assert len(budget_dropped) == 1
    assert budget_dropped[0]["url"] == "https://medium.com/article"
    assert slots == 0


def _run_cli(payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, _DEDUP],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_cli_dedupes_www_and_trailing_slash() -> None:
    """CLI: www.X.com/a/ and x.com/a normalize to one seen key; the dupe is filtered out."""
    out = _run_cli(
        {
            "results": [
                {"url": "https://x.com/a", "title": "first", "relevance": "high"},
                {"url": "https://www.x.com/a/", "title": "dupe", "relevance": "high"},
            ],
            "seen": {},
            "fetch_slots": 5,
        }
    )
    assert len(out["novel"]) == 1
    assert out["novel"][0]["url"] == "https://x.com/a"
    assert out["seen"] == {"x.com/a": True}
    assert out["slots"] == 4  # one novel result decremented the budget


def test_cli_fetch_budget_caps_novel_count() -> None:
    """CLI: fetch_slots caps how many medium/low results survive as novel."""
    out = _run_cli(
        {
            "results": [
                {"url": "https://a.com/1", "title": "1", "relevance": "medium"},
                {"url": "https://b.com/2", "title": "2", "relevance": "medium"},
                {"url": "https://c.com/3", "title": "3", "relevance": "medium"},
            ],
            "seen": {},
            "fetch_slots": 2,
        }
    )
    assert len(out["novel"]) == 2  # budget caps novel count at 2
    assert out["slots"] == 0
