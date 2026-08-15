#!/usr/bin/env python3
"""Stop hook: language-consistency validator.

Detects the conversation language from the transcript (via
``lang_detect.conversation_language()``, reused by path — no target
language is ever hardcoded as a default) and, only when that detector
returns a majority 'ja' or 'zh' signal, checks the FINAL assistant
main-chain message: if it is long (>=200 visible chars) and its
target-script character COUNT is below max(10, 0.05 × visible_len),
block with a corrective reason written in the expected language.

Why an absolute count, not a ratio: genuine English-narration drift
has near-ZERO CJK characters, while a legitimate zh/ja reply dense
with English identifiers (PostToolUse, EventHandler, …) can have a
target-script RATIO well under any sane cutoff yet still contain
dozens of CJK chars — a ratio rule false-positives on exactly the
technical replies this repo produces. The absolute floor (10) catches
token CJK sprinkles in an otherwise-English reply; the 5%-of-length
term scales the bar up for longer replies.

'en' / None conversations, short replies, and malformed input all
resolve to no output, exit 0 — this hook never blocks on its own
initiative and never selects a language.

Loop guard: ``stop_hook_active`` true means a previous Stop-hook block
already re-ran Claude for this turn — MUST exit 0 immediately or the
hook loops forever.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
_LANG_DETECT_PATH = _HOOKS_DIR / "lang_detect.py"

_MIN_REPLY_CHARS = 200
# Block only when target-script COUNT < max(_MIN_TARGET_COUNT,
# _TARGET_COUNT_LEN_FACTOR * visible_len) — see module docstring.
_MIN_TARGET_COUNT = 10
_TARGET_COUNT_LEN_FACTOR = 0.05

# Markdown table rows (``| a | b |``) — not stripped by
# lang_detect.strip_noise (that helper targets code/URLs/paths, not
# table syntax), so this hook adds its own line filter on top rather
# than editing the shared module.
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")

# Corrective reason written in the DETECTED language — emitted
# content, not a behavior selector (brief Non-goals: no hardcoded
# output language).
_BLOCK_REASON = {
    "zh": (
        "你剛才的回覆主要使用英文，但這次會話語言是繁體中文。"
        "請將使用者可見的敘述部分改用繁體中文重新回覆。"
    ),
    "ja": (
        "直前の返信は主に英語でしたが、今回の会話言語は日本語です。"
        "ユーザー向けの説明部分は日本語で書き直してください。"
    ),
}


def _load_lang_detect():
    spec = importlib.util.spec_from_file_location("lang_detect", _LANG_DETECT_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _final_assistant_text(transcript_path, lang_detect) -> str:
    """Text of the LAST main-chain assistant message (raw, unstripped).

    Mirrors lang_detect._iter_user_turns's eligibility filtering
    (exclude isSidechain) but for assistant turns, keeping only the
    last entry that actually has visible text (tool-only turns are
    skipped).
    """
    text = ""
    with open(transcript_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict):
                continue
            if entry.get("type") != "assistant":
                continue
            if entry.get("isSidechain"):
                continue
            message = entry.get("message")
            if not isinstance(message, dict):
                continue
            candidate = lang_detect.extract_text(message.get("content"))
            if candidate.strip():
                text = candidate
    return text


def _strip_table_rows(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n") if not _TABLE_ROW_RE.match(line)
    )


def _target_script_count(visible_chars, expected: str, lang_detect) -> int:
    if expected == "ja":
        return sum(
            1
            for c in visible_chars
            if lang_detect.is_kana(c) or lang_detect.is_han(c)
        )
    # "zh"
    return sum(1 for c in visible_chars if lang_detect.is_han(c))


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("stop_hook_active"):
        return 0
    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        return 0

    try:
        lang_detect = _load_lang_detect()
        expected = lang_detect.conversation_language(transcript_path)
        if expected not in ("ja", "zh"):
            return 0
        reply = _final_assistant_text(transcript_path, lang_detect)
        cleaned = lang_detect.strip_noise(reply)
        cleaned = _strip_table_rows(cleaned)
        visible = [c for c in cleaned if not c.isspace()]
    except Exception:
        return 0

    if len(visible) < _MIN_REPLY_CHARS:
        return 0

    count = _target_script_count(visible, expected, lang_detect)
    if count >= max(_MIN_TARGET_COUNT, _TARGET_COUNT_LEN_FACTOR * len(visible)):
        return 0

    reason = _BLOCK_REASON.get(expected)
    if not reason:
        return 0

    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
