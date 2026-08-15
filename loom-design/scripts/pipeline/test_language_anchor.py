"""Tests for loom-pipeline/hooks/language-anchor.py — PostToolUse tail
language anchor for tool_name "Skill".

Each test subprocess-runs the hook exactly as Claude Code would invoke
it: hook-event JSON (tool_name, transcript_path) on stdin, stdout JSON
(or nothing) as the effect, exit code 0 always (fail-open — this hook
never blocks). Mirrors loom-code/scripts/test_git_guard.py's
subprocess-driven pattern.

The zh/ja anchor strings are DIRECTIVE TEXT emitted for a DETECTED
language, not behavior selectors — the hook must never default to any
language absent a majority signal from lang_detect.conversation_language().
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "language-anchor.py"
HOOKS_JSON = Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"

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


def _write_transcript(path: Path, text: str, n: int = 3) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for _ in range(n):
            entry = {
                "type": "user",
                "isSidechain": False,
                "message": {"role": "user", "content": text},
            }
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_hook(payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def skill_event(transcript_path):
    return {"tool_name": "Skill", "transcript_path": str(transcript_path)}


def test_anchor_emits_in_detected_language(tmp_path):
    transcript = tmp_path / "zh.jsonl"
    _write_transcript(transcript, ZH_TEXT)
    result = run_hook(skill_event(transcript))
    assert result.returncode == 0
    out = json.loads(result.stdout)
    nested = out["hookSpecificOutput"]
    assert nested["hookEventName"] == "PostToolUse"
    assert "繁體中文" in nested["additionalContext"] or "會話語言" in nested["additionalContext"]


def test_anchor_ja(tmp_path):
    transcript = tmp_path / "ja.jsonl"
    _write_transcript(transcript, JA_TEXT)
    result = run_hook(skill_event(transcript))
    assert result.returncode == 0
    out = json.loads(result.stdout)
    nested = out["hookSpecificOutput"]
    assert nested["hookEventName"] == "PostToolUse"
    assert "日本語" in nested["additionalContext"]


def test_anchor_en_no_output(tmp_path):
    transcript = tmp_path / "en.jsonl"
    _write_transcript(transcript, EN_TEXT)
    result = run_hook(skill_event(transcript))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_anchor_missing_transcript_no_output(tmp_path):
    result = run_hook(skill_event(tmp_path / "does-not-exist.jsonl"))
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_anchor_malformed_stdin_no_output():
    result = run_hook("not json at all")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_anchor_wrong_tool_name_no_output(tmp_path):
    transcript = tmp_path / "zh.jsonl"
    _write_transcript(transcript, ZH_TEXT)
    result = run_hook({"tool_name": "Bash", "transcript_path": str(transcript)})
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_hooks_json_has_both_sessionstart_and_posttooluse():
    data = json.loads(HOOKS_JSON.read_text())
    assert "SessionStart" in data["hooks"]
    assert len(data["hooks"]["SessionStart"]) == 1

    post = data["hooks"]["PostToolUse"]
    assert len(post) == 1
    entry = post[0]
    assert entry["matcher"] == "Skill"
    hooks = entry["hooks"]
    assert len(hooks) == 1
    assert hooks[0]["type"] == "command"
    assert "language-anchor.py" in hooks[0]["command"]
