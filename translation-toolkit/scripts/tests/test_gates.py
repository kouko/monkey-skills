"""Tests for scripts/lib/gates.py — M1 placeholder + M2 glossary gates.

Covers Task C4 of translation-toolkit v0.1.0 plan (lines 1326-1420).
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.gates import m1_check, m2_check  # noqa: E402


# --------------------------------------------------------------------------- #
# M1 — placeholder integrity                                                   #
# --------------------------------------------------------------------------- #


def test_m1_placeholder_count_match():
    """M1 PASS: target has same ⟦P:*⟧ set as source."""
    source_token_map = {"⟦P:01⟧": "{name}", "⟦P:02⟧": "{count}"}
    target = "你好 ⟦P:01⟧, 你有 ⟦P:02⟧ 條訊息"
    result = m1_check(target, source_token_map)
    assert result["verdict"] == "PASS"
    assert result["diff"] is None


def test_m1_placeholder_missing():
    source_token_map = {"⟦P:01⟧": "{name}", "⟦P:02⟧": "{count}"}
    target = "你好 ⟦P:01⟧, 你有訊息"
    result = m1_check(target, source_token_map)
    assert result["verdict"] == "FAIL"
    assert "⟦P:02⟧" in result["diff"]


def test_m1_placeholder_extra():
    source_token_map = {"⟦P:01⟧": "{name}"}
    target = "你好 ⟦P:01⟧ ⟦P:99⟧"
    result = m1_check(target, source_token_map)
    assert result["verdict"] == "FAIL"
    assert "⟦P:99⟧" in result["diff"]


# --------------------------------------------------------------------------- #
# M2 — project glossary compliance                                             #
# --------------------------------------------------------------------------- #


def test_m2_project_glossary_compliance_pass():
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Click cancel"
    target = "點選取消"
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "PASS"


def test_m2_project_glossary_violation():
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Click cancel"
    target = "點擊取り消す"
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "FAIL"
    assert "cancel" in result["diff"]


def test_m2_context_dependent_exempt():
    project_glossary = {("cancel", "ui"): "取消"}
    notes = {("cancel", "ui"): "context-dependent"}
    source = "Click cancel"
    target = "點擊取り消す"  # would normally violate
    result = m2_check(source, target, project_glossary, domain="ui", notes=notes)
    assert result["verdict"] == "PASS_ADVISORY"
    assert result["diff"] is not None
    assert "cancel" in result["diff"]
    assert result["details"]["advisory"]  # non-empty


def test_m2_term_not_in_source_no_check():
    """M2 only checks terms that ACTUALLY appear in source."""
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Click submit"  # no 'cancel' in source
    target = "點選送出"
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "PASS"


def test_m2_domain_filter():
    """M2 only checks entries in the active domain."""
    project_glossary = {
        ("cancel", "ui"): "取消",
        ("cancel", "tech.crypto"): "撤銷",
    }
    source = "Click cancel"
    target = "點擊取り消す"  # neither matches
    # Active domain ui → flagged on ui rule, not crypto rule.
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "FAIL"
    assert "取消" in result["diff"]
    assert "撤銷" not in result["diff"]


def test_m2_word_boundary_ascii_no_partial_match():
    """ASCII terms must match whole words only — 'cancel' must NOT trigger on 'cancellation'."""
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Cancellation policy applies"
    target = "適用取消政策"  # has expected translation, but term not actually in source
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "PASS"  # 'cancel' as a word is not in source


def test_m2_cjk_substring_match_works():
    """CJK terms (no word boundaries) match by substring — '取消' in '取消按鈕' is a hit."""
    project_glossary = {("取消", "ui"): "Cancel"}  # ZH→EN
    source = "點擊取消按鈕"
    target = "Click Cancel button"
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "PASS"
