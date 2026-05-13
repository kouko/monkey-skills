"""Tests for legal-incident-response/scripts/classify_path.py.

classify_path.py is a deterministic helper: reads incident description
+ keyword table, returns matched signals (per-path lists). LLM owns
confidence judgement separately (in classify-path.md protocol).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "scripts"
KEYWORDS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "assets" / "path-classifier-keywords.yml"


def _load():
    spec = importlib.util.spec_from_file_location("classify_path", SCRIPTS / "classify_path.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pii_breach_keywords_matched():
    classify = _load()
    desc = "今天早上發現有 8000 筆客戶資料被異常存取"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "pii-breach" in result.matched_paths
    assert any(kw in result.signals["pii-breach"] for kw in ["客戶資料", "異常存取"])


def test_authority_letter_keywords_matched():
    classify = _load()
    desc = "金管會來函要 7 日內回覆關於資安事件"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "authority-letter" in result.matched_paths
    assert any(kw in result.signals["authority-letter"] for kw in ["金管會", "函", "日內"])


def test_contract_breach_keywords_matched():
    classify = _load()
    desc = "對方違約沒付款已經 60 天，要不要催告解除合約"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "contract-breach" in result.matched_paths
    assert any(kw in result.signals["contract-breach"] for kw in ["違約", "催告", "解除合約"])


def test_multi_path_match_returns_all_matched():
    """When incident description matches multiple paths' keywords,
    classifier returns all of them; LLM (in protocol) handles primary selection."""
    classify = _load()
    desc = "金管會來函說我們公司有客戶資料外洩，要 7 日內說明"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "authority-letter" in result.matched_paths
    assert "pii-breach" in result.matched_paths


def test_no_keyword_match_returns_empty():
    classify = _load()
    desc = "天氣很好"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert result.matched_paths == []
    assert all(sigs == [] for sigs in result.signals.values())
