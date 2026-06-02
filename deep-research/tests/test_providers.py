"""Tests for providers.py Protocol definitions.

Intent: verify that the three Protocols are runtime_checkable so that
mock/concrete implementations can be validated structurally (isinstance)
without importing concrete provider code into core.
"""

import pytest
from deep_research.providers import FetchProvider, LLMProvider, SearchProvider


class _MockLLM:
    async def complete(self, prompt: str, schema: dict) -> dict | None:
        return {"result": "ok"}


class _MockSearch:
    async def search(self, query: str) -> list[dict]:
        return [{"title": "t", "url": "u", "snippet": "s"}]


class _MockFetch:
    async def fetch(self, url: str) -> str | None:
        return "<html/>"


class _MissingComplete:
    """Does NOT implement complete() — should fail LLMProvider isinstance."""
    async def search(self, query: str) -> list[dict]:
        return []


class _MissingSearch:
    """Does NOT implement search() — should fail SearchProvider isinstance."""
    async def complete(self, prompt: str, schema: dict) -> dict | None:
        return None


class _MissingFetch:
    """Does NOT implement fetch() — should fail FetchProvider isinstance."""
    async def complete(self, prompt: str, schema: dict) -> dict | None:
        return None


def test_mock_conforms_llm_provider():
    """A class with complete() is structurally an LLMProvider."""
    assert isinstance(_MockLLM(), LLMProvider)


def test_mock_conforms_search_provider():
    """A class with search() is structurally a SearchProvider."""
    assert isinstance(_MockSearch(), SearchProvider)


def test_mock_conforms_fetch_provider():
    """A class with fetch() is structurally a FetchProvider."""
    assert isinstance(_MockFetch(), FetchProvider)


def test_missing_complete_not_llm_provider():
    """A class without complete() is NOT an LLMProvider."""
    assert not isinstance(_MissingComplete(), LLMProvider)


def test_missing_search_not_search_provider():
    """A class without search() is NOT a SearchProvider."""
    assert not isinstance(_MissingSearch(), SearchProvider)


def test_missing_fetch_not_fetch_provider():
    """A class without fetch() is NOT a FetchProvider."""
    assert not isinstance(_MissingFetch(), FetchProvider)
