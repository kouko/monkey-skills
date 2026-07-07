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
# CJK-aware detectability floor: the 20-visible-char minimum is
# calibrated for ASCII prose, but CJK packs far more signal per char —
# a short zh/ja turn like 「我合併了 幫我跑跑 comms 稽核」 (the dominant
# real style of CJK users) is unambiguous well under 20 visible chars.
# A text is detectable when visible >= 20 OR it carries >= 8 CJK
# (kana+han) chars; a tiny quoted CJK fragment inside a short English
# turn stays below this and remains undetectable.
_MIN_CJK_CHARS_DETECTABLE = 8
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

# Harness-injected user-role turns: Claude Code writes a skill
# invocation's ENTIRE (English) SKILL.md body into the transcript as a
# user-role turn beginning with this literal prefix, and an interrupted
# turn is recorded as a fixed marker string — neither is the user's own
# narration, so both must be excluded from language voting (live repro:
# a Traditional-Chinese conversation was misdetected as undetermined
# because one skill-body turn plus one interrupt marker flooded the
# last-n-turns window with English/no-signal text).
_HARNESS_INJECTION_PREFIXES = (
    "Base directory for this skill:",
    "[Request interrupted",
)
# Slash-command / skill-invocation echoes ('Run the "<name>" workflow.'
# followed by the skill's own English description) are the same failure
# family — the harness writing machine text into a user-role turn.
# Matched as the full quoted-name shape, NOT a bare "Run the" prefix,
# so a genuine user typing "Run the tests" is never filtered.
_WORKFLOW_ECHO_RE = re.compile(r'^Run the "[^"]+" workflow\.')


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
    non-whitespace characters AND <8 CJK chars — see
    ``_MIN_CJK_CHARS_DETECTABLE``: short-but-unambiguous CJK turns stay
    detectable) or has no clear script majority.
    """
    if not text:
        return None
    kana = sum(1 for c in text if _is_kana(c))
    han = sum(1 for c in text if _is_han(c))
    cjk = kana + han

    visible = [c for c in text if not c.isspace()]
    if len(visible) < _MIN_VISIBLE_CHARS and cjk < _MIN_CJK_CHARS_DETECTABLE:
        return None

    ascii_letters = sum(1 for c in text if c.isascii() and c.isalpha())
    script_total = cjk + ascii_letters
    if script_total == 0:
        return None

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


def _is_harness_injection(stripped_text: str) -> bool:
    return stripped_text.startswith(_HARNESS_INJECTION_PREFIXES) or bool(
        _WORKFLOW_ECHO_RE.match(stripped_text)
    )


def _iter_user_turns(transcript_path):
    """Yield narration text for eligible user main-chain turns, in file order.

    Excludes ``isSidechain: true`` turns, turns whose text starts with
    ``<`` (tool-result / command-wrapper / system-reminder XML — not
    user narration), and harness-injection turns (see
    ``_HARNESS_INJECTION_PREFIXES`` — skill-body payloads and interrupt
    markers arrive as user-role turns but are machine artifacts, not
    the user's own language).
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
            if not stripped or stripped.startswith("<") or _is_harness_injection(stripped):
                continue
            yield text


# --- public wrappers -----------------------------------------------------
# Stable cross-module contract for sibling hooks (e.g.
# language-stop-check.py): thin one-line delegations to the private
# helpers above. Consumers must use THESE names, never the underscored
# implementations — the private bodies may change; these signatures
# will not.


def is_kana(ch: str) -> bool:
    """Public wrapper for :func:`_is_kana` (stable cross-module contract)."""
    return _is_kana(ch)


def is_han(ch: str) -> bool:
    """Public wrapper for :func:`_is_han` (stable cross-module contract)."""
    return _is_han(ch)


def extract_text(message_content) -> str:
    """Public wrapper for :func:`_extract_text` (stable cross-module contract)."""
    return _extract_text(message_content)


def strip_noise(text: str) -> str:
    """Public wrapper for :func:`_strip_noise` (stable cross-module contract)."""
    return _strip_noise(text)


def is_harness_injection(stripped_text: str) -> bool:
    """Public wrapper for :func:`_is_harness_injection` (stable cross-module contract)."""
    return _is_harness_injection(stripped_text)


def _majority_language(texts, n_turns: int = 3) -> Optional[str]:
    """Majority language over the last ``n_turns`` DETECTABLE texts.

    Shared building block for both a whole-file vote
    (``conversation_language``) and a rolling, point-in-time vote
    (loom-pipeline/scripts/comms_metrics.py): turns whose script can't
    be determined (too short, or no script majority) are dropped
    BEFORE sampling rather than counted as a diluting non-vote — a run
    of short confirmations ("好" / "修", <20 visible chars) must not
    outvote a real, sustained-language signal. Requires an outright
    majority among the sampled detectable texts; otherwise None.
    """
    if n_turns <= 0:
        return None
    detectable = [
        lang
        for lang in (detect_script(_strip_noise(t)) for t in texts)
        if lang is not None
    ]
    sampled = detectable[-n_turns:]
    if not sampled:
        return None
    lang, count = Counter(sampled).most_common(1)[0]
    if count > len(sampled) / 2:
        return lang
    return None


def majority_language(texts, n_turns: int = 3) -> Optional[str]:
    """Public wrapper for :func:`_majority_language` (stable cross-module contract)."""
    return _majority_language(texts, n_turns)


def conversation_language(transcript_path, n_turns: int = 3) -> Optional[str]:
    """Majority conversation language over the last ``n_turns``
    DETECTABLE USER main-chain turns of a Claude Code transcript JSONL
    file (turns whose script can't be determined, e.g. short
    confirmations, are skipped rather than diluting the vote — see
    :func:`_majority_language`).

    Returns 'ja' / 'zh' / 'en' only when a majority of the sampled
    turns agree; otherwise None. Fail-open: a missing file, an
    unreadable file, or malformed content resolves to None — this
    never raises (mirrors the repo's hook fail-open convention).
    """
    try:
        turns = list(_iter_user_turns(transcript_path))
    except Exception:
        return None
    return _majority_language(turns, n_turns)
