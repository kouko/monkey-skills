"""Tests for loom-code/hooks/language-anchor.py — the PostToolUse
language-anchor hook (legacy backfill; hook was already live in
hooks.json with zero tests).

Each test subprocess-runs the hook exactly as Claude Code would invoke
it: hook-event JSON (with a ``transcript_path`` pointing at a temp
JSONL transcript) on stdin, output on stdout, exit 0. Subprocess (not
import) is required — ``language-anchor.py`` is a hyphenated filename
and is not importable as a Python module, same constraint documented
for ``ask-triage.py`` in ``test_ask_triage_hook.py``.

External surfaces grounded (per
loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md):

- Claude Code PostToolUse hook contract (JSON event with
  ``tool_name``/``transcript_path`` on stdin; ``hookSpecificOutput``
  JSON on stdout when emitting, empty stdout otherwise; exit 0): the
  hook is registered under ``PostToolUse`` (matcher ``Skill``) in
  ``loom-code/hooks/hooks.json``, source-(d) in-repo evidence.
- Transcript JSONL turn shape (``{"type": "user", "isSidechain":
  false, "message": {"content": <str>}}``): read directly from
  ``loom-code/hooks/lang_detect.py`` ``_iter_user_turns`` /
  ``_extract_text`` — the parser this hook's ``conversation_language``
  call reads through.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "language-anchor.py"

# Distinctive stable fragments of the pinned directive text
# (language-anchor.py:26-35) — substring matches, not full-string
# equality, so incidental rewording elsewhere doesn't break the test.
ZH_FRAGMENT = "會話語言（繁體中文）"
JA_FRAGMENT = "会話言語（日本語）"

# zh sample: well over the 20-visible-char / majority-Han floor
# (lang_detect.detect_script _MIN_VISIBLE_CHARS / _MAJORITY_SCRIPT_RATIO).
ZH_TURN = "請幫我確認這個修改是否符合原本的設計規範，並且說明理由。"
# ja sample: kana ratio + CJK share both clear the ja thresholds
# (lang_detect.py _KANA_SIGNAL_RATIO / _MIN_CJK_SHARE_FOR_JA).
JA_TURN = "この変更が仕様に合っているかどうかを確認してください。よろしくお願いします。"
# en sample: ascii-letter majority, no CJK — resolves to 'en', for
# which language-anchor.py has no _ANCHOR_TEXT entry (stays silent).
EN_TURN = "Please confirm this change matches the original design specification and explain why."


def _write_transcript(turns):
    """Write a JSONL transcript with one main-chain user turn per text
    in ``turns`` and return its path."""
    fh = tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    for text in turns:
        fh.write(
            json.dumps(
                {
                    "type": "user",
                    "isSidechain": False,
                    "message": {"content": text},
                }
            )
            + "\n"
        )
    fh.close()
    return fh.name


def run_hook(payload):
    """Run the hook with `payload` (dict → JSON, str → raw) on stdin."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_zh_majority_emits_zh_directive():
    transcript = _write_transcript([ZH_TURN, ZH_TURN, ZH_TURN])
    result = run_hook(
        {"tool_name": "Skill", "transcript_path": transcript}
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert ZH_FRAGMENT in payload["hookSpecificOutput"]["additionalContext"]


def test_ja_majority_emits_ja_directive():
    transcript = _write_transcript([JA_TURN, JA_TURN, JA_TURN])
    result = run_hook(
        {"tool_name": "Skill", "transcript_path": transcript}
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert JA_FRAGMENT in payload["hookSpecificOutput"]["additionalContext"]


def test_en_majority_stays_silent():
    transcript = _write_transcript([EN_TURN, EN_TURN, EN_TURN])
    result = run_hook(
        {"tool_name": "Skill", "transcript_path": transcript}
    )
    assert result.returncode == 0
    assert result.stdout == ""


def test_malformed_stdin_stays_silent():
    """language-anchor.py:47-50 fail-open path: malformed stdin must
    exit 0 and emit nothing, never crash the PostToolUse hook chain."""
    result = run_hook("not json {{{")
    assert result.returncode == 0
    assert result.stdout == ""


def test_empty_stdin_stays_silent():
    result = run_hook("")
    assert result.returncode == 0
    assert result.stdout == ""


def test_non_skill_tool_name_stays_silent():
    """tool_name gate (language-anchor.py:53-54): even a transcript
    with a clear zh majority must not fire outside a Skill PostToolUse
    invocation."""
    transcript = _write_transcript([ZH_TURN, ZH_TURN, ZH_TURN])
    result = run_hook(
        {"tool_name": "Bash", "transcript_path": transcript}
    )
    assert result.returncode == 0
    assert result.stdout == ""
