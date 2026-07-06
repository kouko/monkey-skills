"""Language-detection helper for loom-pipeline hooks.

Pure-stdlib heuristic script/majority-language detector. No target
language is ever hardcoded here — callers get back whatever code was
detected ('ja' / 'zh' / 'en') or None when the signal is too weak;
nothing in this module selects a language to prefer.

Limitation (Han-only-Japanese): zh vs ja is discriminated purely by
kana (hiragana/katakana) presence. Japanese prose normally mixes kanji
(Han) with kana particles/okurigana, so a non-trivial kana ratio in a
CJK-dominated text is treated as a strong ja signal (the CJK-share
floor keeps English prose that merely QUOTES a few Japanese words
classified as en); Han characters WITHOUT kana are classified as zh.
A genuine Japanese sample that happens to contain no kana at all
(rare — e.g. an all-kanji technical term list) will be misclassified
as zh. There is no vocabulary/grammar disambiguation.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Optional

_MIN_VISIBLE_CHARS = 20
# Kana at or above this ratio (of script-bearing chars) is a strong
# Japanese signal — a single stray kana in a mostly-Han sample stays
# below this and is not enough to flip the verdict.
_KANA_SIGNAL_RATIO = 0.02
# ...but the kana rule only applies when CJK chars (kana + Han) are a
# meaningful share of the text. A predominantly-English turn QUOTING a
# couple of Japanese words (e.g. "yoroshiku (よろしく) means ...") must
# stay 'en': its kana ratio clears 0.02 but its CJK share stays far
# below this floor.
_MIN_CJK_SHARE_FOR_JA = 0.3
# zh / en require an outright majority of script-bearing chars.
_MAJORITY_SCRIPT_RATIO = 0.5

# Non-greedy pair-matching: an UNCLOSED fence leaves its content in
# place (counted), and backticks nested inside a fenced block simply
# end the match early — acceptable noise for a heuristic; do not
# over-engineer full CommonMark fence parsing here.
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_URL_RE = re.compile(r"https?://\S+")
_PATH_TOKEN_RE = re.compile(r"(?<!\S)/\S*")
# Unfenced pasted logs/tracebacks (very common in chat) — drop whole
# lines shaped like: a Python traceback header, a frame line
# (`  File "..."`), any 2+-space-indented code/continuation line, or an
# exception-message line ("ValueError: ...", "Exception: ...").
_LOG_LINE_RE = re.compile(
    r"^(?:"
    r"Traceback \(most recent call last\):"
    r'|\s+File "'
    r"|\s{2,}\S"
    r"|\s*\w+(?:Error|Exception)\s*:"
    r")"
)


def _is_kana(ch: str) -> bool:
    cp = ord(ch)
    return 0x3040 <= cp <= 0x309F or 0x30A0 <= cp <= 0x30FF


def _is_han(ch: str) -> bool:
    cp = ord(ch)
    return 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0xF900 <= cp <= 0xFAFF


def detect_script(text: Optional[str]) -> Optional[str]:
    """Guess the dominant script of ``text``: ``'ja'|'zh'|'en'|None``.

    Heuristic only — see module docstring for the Han-only-Japanese
    limitation. Returns None when the text is too short (<20 visible,
    non-whitespace characters) or has no clear script majority.
    """
    if not text:
        return None
    visible = [c for c in text if not c.isspace()]
    if len(visible) < _MIN_VISIBLE_CHARS:
        return None

    kana = sum(1 for c in text if _is_kana(c))
    han = sum(1 for c in text if _is_han(c))
    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    script_total = kana + han + ascii_letters
    if script_total == 0:
        return None

    cjk = kana + han
    if (
        kana / script_total >= _KANA_SIGNAL_RATIO
        and cjk / script_total >= _MIN_CJK_SHARE_FOR_JA
    ):
        return "ja"
    if han > 0 and han / script_total > _MAJORITY_SCRIPT_RATIO:
        return "zh"
    if ascii_letters / script_total > _MAJORITY_SCRIPT_RATIO:
        return "en"
    return None


def _extract_text(message_content) -> str:
    """Pull visible text out of a transcript ``message.content`` value.

    Accepts either a plain string or a list of content blocks (only
    ``type: "text"`` blocks are counted — tool_use/tool_result/image
    blocks are not narration).
    """
    if isinstance(message_content, str):
        return message_content
    if isinstance(message_content, list):
        parts = []
        for block in message_content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "\n".join(parts)
    return ""


def _strip_noise(text: str) -> str:
    """Strip quoted machine text before counting scripts.

    Removes fenced code blocks, then whole lines shaped like pasted
    logs/tracebacks (``_LOG_LINE_RE`` — unfenced pastes are common),
    then inline code, URLs, and /path/like tokens. Line filtering runs
    after fence removal but before token stripping so a frame line like
    ``  File "/x/y.py", line 3`` is dropped intact.
    """
    text = _CODE_FENCE_RE.sub(" ", text)
    text = "\n".join(
        line for line in text.split("\n") if not _LOG_LINE_RE.match(line)
    )
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _PATH_TOKEN_RE.sub(" ", text)
    return text


def _iter_user_turns(transcript_path):
    """Yield narration text for eligible user main-chain turns, in file order.

    Excludes ``isSidechain: true`` turns and turns whose text starts
    with ``<`` (tool-result / command-wrapper / system-reminder XML —
    not user narration).
    """
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
            if entry.get("type") != "user":
                continue
            if entry.get("isSidechain"):
                continue
            message = entry.get("message")
            if not isinstance(message, dict):
                continue
            text = _extract_text(message.get("content"))
            stripped = text.strip()
            if not stripped or stripped.startswith("<"):
                continue
            yield text


def conversation_language(transcript_path, n_turns: int = 3) -> Optional[str]:
    """Majority conversation language over the last ``n_turns`` eligible
    USER main-chain turns of a Claude Code transcript JSONL file.

    Returns 'ja' / 'zh' / 'en' only when a majority of the sampled
    turns agree; otherwise None. Fail-open: a missing file, an
    unreadable file, or malformed content resolves to None — this
    never raises (mirrors the repo's hook fail-open convention).
    """
    try:
        turns = list(_iter_user_turns(transcript_path))
    except Exception:
        return None

    if n_turns <= 0:
        return None
    sampled = turns[-n_turns:]
    if not sampled:
        return None

    langs = [detect_script(_strip_noise(t)) for t in sampled]
    counts = Counter(lang for lang in langs if lang is not None)
    if not counts:
        return None
    lang, count = counts.most_common(1)[0]
    if count > len(sampled) / 2:
        return lang
    return None
