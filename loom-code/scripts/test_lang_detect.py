"""Tests for loom-code/hooks/lang_detect.py — shared language-detection helper.

Loaded by path exactly as ``hooks/language-anchor.py`` does
(``importlib.util.spec_from_file_location``) because ``hooks/`` is not
on ``scripts/``'s import path (precedent: test_git_guard.py subprocess-
drives its hook; this module instead loads lang_detect's pure
functions in-process since they have no CLI/stdin surface of their
own).
"""

import importlib.util
import json
from pathlib import Path

import pytest

_HOOKS_DIR = Path(__file__).resolve().parent.parent / "hooks"
_LANG_DETECT_PATH = _HOOKS_DIR / "lang_detect.py"


def _load_lang_detect():
    spec = importlib.util.spec_from_file_location("lang_detect", _LANG_DETECT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def lang_detect():
    return _load_lang_detect()


# --- detect_script ---------------------------------------------------


def test_detect_script_ja(lang_detect):
    # Kana-bearing CJK text (kana ratio + CJK share both clear the
    # ja thresholds) must classify as 'ja'.
    text = "これはテストです。日本語の文章をここに書きます。"
    assert lang_detect.detect_script(text) == "ja"


def test_detect_script_zh(lang_detect):
    # Han-only CJK text (no kana) must classify as 'zh'.
    text = "这是一段测试文字，用来确认繁体或简体中文可以被正确侦测出来。"
    assert lang_detect.detect_script(text) == "zh"


def test_detect_script_en(lang_detect):
    text = "This is a plain English sentence long enough to be detected."
    assert lang_detect.detect_script(text) == "en"


def test_detect_script_empty_returns_none(lang_detect):
    assert lang_detect.detect_script("") is None
    assert lang_detect.detect_script(None) is None


# --- is_harness_injection ---------------------------------------------


def test_is_harness_injection_true_for_known_prefix(lang_detect):
    text = "Base directory for this skill: /some/path\nrest of body..."
    assert lang_detect.is_harness_injection(text) is True


def test_is_harness_injection_false_for_plain_prose(lang_detect):
    assert lang_detect.is_harness_injection("幫我看一下這段程式碼") is False


# --- majority_language --------------------------------------------------


def test_majority_language_two_of_three_rule(lang_detect):
    ja_text = "これはテストです。日本語の文章をここに書きます。"
    en_text = "This is a plain English sentence long enough to be detected."
    # 2 ja turns vs 1 en turn among the sampled n_turns=3 window ->
    # majority is 'ja'.
    texts = [en_text, ja_text, ja_text]
    assert lang_detect.majority_language(texts, n_turns=3) == "ja"


# --- conversation_language ----------------------------------------------


def test_conversation_language_majority_ja(tmp_path):
    lang_detect = _load_lang_detect()
    ja_text = "これはテストです。日本語の文章をここに書きます。"
    lines = []
    for _ in range(3):
        lines.append(
            json.dumps(
                {
                    "type": "user",
                    "message": {"role": "user", "content": ja_text},
                }
            )
        )
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert lang_detect.conversation_language(transcript) == "ja"


def test_conversation_language_skips_malformed_line(tmp_path):
    lang_detect = _load_lang_detect()
    ja_text = "これはテストです。日本語の文章をここに書きます。"
    lines = [
        "{this is not valid json",
        json.dumps({"type": "user", "message": {"role": "user", "content": ja_text}}),
        json.dumps({"type": "user", "message": {"role": "user", "content": ja_text}}),
    ]
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # The malformed line is skipped rather than raising; the remaining
    # two detectable ja turns still form a majority.
    assert lang_detect.conversation_language(transcript) == "ja"


def test_conversation_language_missing_file_returns_none(tmp_path):
    lang_detect = _load_lang_detect()
    missing = tmp_path / "does_not_exist.jsonl"
    assert lang_detect.conversation_language(missing) is None
