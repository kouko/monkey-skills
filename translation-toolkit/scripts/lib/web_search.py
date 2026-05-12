"""Web search L4 tier — tool-abstraction wrapper.

Real runtime invocation happens in skill prompts (WebSearch tool / google_web_search /
browser API depending on runtime). This Python module is a STUB for build-time
testing of the lookup pipeline; it returns hardcoded candidates given a term.

For runtime: see scripts/canonical/glossary-resolution-spec.md.
"""
from __future__ import annotations

from typing import Callable, Optional


def web_search_term(
    *,
    term: str,
    target_lang: str,
    fetcher: Optional[Callable[[str, str], list[dict]]] = None,
    max_searches: int = 10,
) -> list[dict]:
    """Search for translation candidates for a term in the target language.

    Args:
        term: source term.
        target_lang: BCP-47 target locale.
        fetcher: callable that takes (term, target_lang) and returns a list of
                 candidate dicts: [{"translation": str, "url": str, "snippet": str}, ...].
                 Pass None for the build-time stub fallback.
        max_searches: cost cap (informational; caller responsible for global counter).

    Returns:
        list of candidate dicts. Empty list on no result.
    """
    if fetcher is None:
        return _stub_fetch(term, target_lang)
    return fetcher(term, target_lang)


def _stub_fetch(term: str, target_lang: str) -> list[dict]:
    """Build-time stub. Real runtime uses WebSearch (CC) / google_web_search (Gemini) / etc."""
    # Hardcoded responses for known fixture terms only
    fixtures = {
        ("Cancel", "ja-JP"): [
            {"translation": "キャンセル", "url": "https://example.com/cancel-ja", "snippet": "Cancel button..."},
        ],
        ("commit", "zh-TW"): [
            {"translation": "提交", "url": "https://example.com/commit-zh", "snippet": "git commit..."},
            {"translation": "送出", "url": "https://example.com/commit-zh-2", "snippet": "alternate"},
        ],
    }
    return fixtures.get((term, target_lang), [])
