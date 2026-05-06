"""Tests for the L4 web-search tool-abstraction wrapper.

The Python module is a build-time stub for pipeline tests; real runtime
uses WebSearch (CC) / google_web_search (Gemini) / browser (Codex) per
the skill prompts. See scripts/canonical/glossary-resolution-spec.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.web_search import web_search_term  # noqa: E402


def test_web_search_stub_returns_known_fixture():
    out = web_search_term(term="Cancel", target_lang="ja-JP")
    assert len(out) == 1
    assert out[0]["translation"] == "キャンセル"


def test_web_search_unknown_term_returns_empty():
    out = web_search_term(term="zxqwerty", target_lang="ja-JP")
    assert out == []


def test_web_search_uses_provided_fetcher():
    fake_fetcher_calls = []

    def fake(t, tl):
        fake_fetcher_calls.append((t, tl))
        return [{"translation": "test", "url": "https://x", "snippet": "y"}]

    out = web_search_term(term="anything", target_lang="ja-JP", fetcher=fake)
    assert out[0]["translation"] == "test"
    assert fake_fetcher_calls == [("anything", "ja-JP")]
