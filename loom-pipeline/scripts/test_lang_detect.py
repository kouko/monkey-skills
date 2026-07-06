"""Tests for loom-pipeline/hooks/lang_detect.py.

Pure-stdlib language-detection helper: ``detect_script()`` is a
char-heuristic on raw text; ``conversation_language()`` majority-votes
over the last N user main-chain turns of a Claude Code transcript
JSONL file. Imported by path (same pattern as
legal-toolkit/tests/test_classify_path.py) since the module lives
under hooks/, not an installed package.

One test per behavior group (F.I.R.S.T Independent);
``test_detect_and_conversation_language`` stays as the thin
integration case the plan's RED/GREEN acceptance names.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "loom-pipeline" / "hooks" / "lang_detect.py"


def _load():
    spec = importlib.util.spec_from_file_location("lang_detect", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_transcript(path: Path, entries: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for entry in entries:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _user_entry(text, *, sidechain: bool = False) -> dict:
    return {
        "type": "user",
        "isSidechain": sidechain,
        "message": {"role": "user", "content": text},
    }


ZH_TEXT = (
    "請幫我看看今天的天氣預報，我想知道明天是不是還會下雨，"
    "順便查一下濕度和氣溫的變化趨勢。"
)
JA_TEXT = (
    "今日はとても良い天気ですね。明日の天気予報も確認してもらえますか、"
    "お願いします。"
)
EN_TEXT = (
    "Could you please check tomorrow's weather forecast and let me "
    "know if it will rain again."
)
ZH_WITH_ENGLISH_TERMS = (
    "這是一個測試，我想要呼叫 API 並解析 JSON 回傳的資料，"
    "看看能不能正常運作，麻煩幫我確認一下。"
)
# Predominantly-English prose quoting a couple of Japanese words —
# must NOT classify 'ja' (code-quality-review finding 1).
EN_QUOTING_JA_WORDS = (
    "The word yoroshiku (よろしく) is used a lot in Japanese business "
    "emails. Another common phrase is otsukaresama (おつかれさま) which "
    "you can say to coworkers at the end of the day."
)
# Unfenced pasted traceback — no triple backticks (finding 2).
UNFENCED_TRACEBACK = (
    "Traceback (most recent call last):\n"
    '  File "app.py", line 10, in <module>\n'
    "    result = process_the_request_data(payload)\n"
    "ValueError: invalid literal for int() with base 10: 'abc'"
)


# --- detect_script -----------------------------------------------------


def test_detect_script_table():
    mod = _load()
    assert mod.detect_script(JA_TEXT) == "ja"
    assert mod.detect_script(ZH_TEXT) == "zh"
    assert mod.detect_script(EN_TEXT) == "en"
    assert mod.detect_script("hi") is None       # too short
    assert mod.detect_script("") is None
    assert mod.detect_script(None) is None


def test_detect_script_mixed_cjk_with_english_terms():
    mod = _load()
    # Han still dominates the script-bearing chars -> zh
    assert mod.detect_script(ZH_WITH_ENGLISH_TERMS) == "zh"


def test_detect_script_english_quoting_japanese_words():
    """Regression (review finding 1): a few quoted kana words inside a
    predominantly-English turn must not flip the verdict to 'ja'."""
    mod = _load()
    assert mod.detect_script(EN_QUOTING_JA_WORDS) == "en"


# --- noise stripping in conversation_language --------------------------


def test_code_fence_stripping(tmp_path):
    mod = _load()
    # Unstripped, the ascii-heavy code block would tip the vote to 'en'.
    fenced = (
        ZH_TEXT
        + "\n```python\ndef handler(request, response, context):\n"
        "    return process(request)\n```"
    )
    transcript = tmp_path / "fenced.jsonl"
    _write_transcript(transcript, [_user_entry(fenced)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_unfenced_traceback_stripping(tmp_path):
    """Regression (review finding 2): a pasted traceback WITHOUT code
    fences must not outvote the CJK prose around it."""
    mod = _load()
    turn = ZH_TEXT + "\n" + UNFENCED_TRACEBACK
    transcript = tmp_path / "traceback.jsonl"
    _write_transcript(transcript, [_user_entry(turn)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- turn selection ----------------------------------------------------


def test_sidechain_exclusion(tmp_path):
    mod = _load()
    transcript = tmp_path / "sidechain.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(EN_TEXT, sidechain=True),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_wrapper_turns_skipped(tmp_path):
    # tool-result / system-reminder wrappers (text starts with '<') are
    # skipped and do not count toward the last-n window
    mod = _load()
    transcript = tmp_path / "wrapper.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(ZH_TEXT),
            _user_entry(
                "<system-reminder>some english wrapper content</system-reminder>"
            ),
            _user_entry(ZH_TEXT),
            _user_entry(ZH_TEXT),
        ],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_content_block_lists(tmp_path):
    # message.content as list of blocks: only type:"text" blocks count
    mod = _load()
    transcript = tmp_path / "blocks.jsonl"
    _write_transcript(
        transcript,
        [
            _user_entry(
                [
                    {"type": "tool_result", "text": "irrelevant tool payload"},
                    {"type": "text", "text": ZH_TEXT},
                ]
            )
        ]
        * 3,
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- majority rule ------------------------------------------------------


def test_majority_rule(tmp_path):
    mod = _load()
    transcript = tmp_path / "majority.jsonl"
    _write_transcript(
        transcript,
        [_user_entry(ZH_TEXT), _user_entry(ZH_TEXT), _user_entry(EN_TEXT)],
    )
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


def test_no_majority_tie(tmp_path):
    mod = _load()
    transcript = tmp_path / "tie.jsonl"
    _write_transcript(
        transcript,
        [_user_entry(ZH_TEXT), _user_entry(EN_TEXT), _user_entry(JA_TEXT)],
    )
    assert mod.conversation_language(transcript, n_turns=3) is None


# --- fail-open ----------------------------------------------------------


def test_fail_open(tmp_path):
    mod = _load()
    # missing file
    assert mod.conversation_language(tmp_path / "does-not-exist.jsonl") is None
    # malformed JSON lines
    malformed = tmp_path / "malformed.jsonl"
    malformed.write_text("not json at all\n{broken", encoding="utf-8")
    assert mod.conversation_language(malformed) is None
    # non-utf8 bytes
    binary_garbage = tmp_path / "binary.jsonl"
    binary_garbage.write_bytes(b"\xff\xfe\x00bad-bytes-not-utf8\x80\x81")
    assert mod.conversation_language(binary_garbage) is None


# --- thin integration case (plan's named RED/GREEN reference) -----------


def test_detect_and_conversation_language(tmp_path):
    mod = _load()
    assert mod.detect_script(ZH_TEXT) == "zh"
    transcript = tmp_path / "integration.jsonl"
    _write_transcript(transcript, [_user_entry(ZH_TEXT)] * 3)
    assert mod.conversation_language(transcript, n_turns=3) == "zh"


# --- public wrapper contract (stable cross-module surface) ---------------


def test_public_wrappers_exist_and_delegate():
    """Sibling hooks (language-stop-check.py) consume these PUBLIC names;
    they must exist and behave identically to the private helpers."""
    mod = _load()
    assert mod.is_kana("あ") is True and mod.is_kana("漢") is False
    assert mod.is_han("漢") is True and mod.is_han("あ") is False
    assert mod.extract_text([{"type": "text", "text": "hi"}]) == "hi"
    assert mod.extract_text("plain") == "plain"
    assert "code" not in mod.strip_noise("前置 `code` 後置")
