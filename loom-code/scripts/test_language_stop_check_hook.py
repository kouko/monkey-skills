"""Tests for loom-code/hooks/language-stop-check.py — the Stop hook
that blocks a language-drifted final assistant reply.

Each test subprocess-runs the hook exactly as Claude Code would invoke
it: Stop-hook JSON (``{"transcript_path": ...}``) on stdin, either a
``{"decision": "block", "reason": ...}`` JSON line on stdout (block) or
no output at all (silent, exit 0). Subprocess (not import) is required
— ``language-stop-check.py`` is a hyphenated filename and is not
importable as a Python module, matching the sibling technique in
``loom-code/scripts/test_ask_triage_hook.py``.

Threshold pinned from the hook's own module docstring: block only when
target-script char count < ``max(10, 0.05 × visible_len)``. At
visible_len == 200 that ceiling is exactly 10 (0.05 × 200 == 10 ==
the floor), giving a clean boundary pair: 9 target-script chars →
below → block; 10 → at → silent.

External surfaces grounded (per
loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md):
Claude Code Stop hook contract (JSON event on stdin; a JSON
``{"decision": "block", ...}`` line on stdout blocks; exit 0 with no
output allows) — source-(d) in-repo evidence: the identical shape is
read from ``loom-code/hooks/language-stop-check.py`` itself and
registered as a ``Stop`` hook in ``loom-code/hooks/hooks.json``.
"""

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "language-stop-check.py"

# A short, unambiguous zh user turn: all-Han, well past the 8-CJK-char
# detectability floor (lang_detect._MIN_CJK_CHARS_DETECTABLE), so
# lang_detect.conversation_language() votes 'zh' for the transcript.
ZH_USER_TURN = "這是測試訊息偵測語言使用中文內容範例文字"

# A short, unambiguous en user turn.
EN_USER_TURN = "This is a plain English test message used to detect the conversation language for this transcript file."


def _write_transcript(tmp_path, user_text, assistant_text=None):
    """Write a minimal Claude Code transcript JSONL: one user turn,
    optionally one final assistant turn. Returns the file path."""
    lines = [
        json.dumps({"type": "user", "message": {"content": user_text}}),
    ]
    if assistant_text is not None:
        lines.append(
            json.dumps(
                {"type": "assistant", "message": {"content": assistant_text}}
            )
        )
    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_hook(payload):
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_zh_transcript_below_threshold_blocks_with_zh_reason():
    """visible_len == 200, han count == 9 < max(10, 0.05*200=10) → block."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        assistant_text = "字" * 9 + "x" * 191
        assert sum(1 for c in assistant_text if not c.isspace()) == 200
        transcript = _write_transcript(tmp_path, ZH_USER_TURN, assistant_text)

        result = run_hook({"transcript_path": str(transcript)})

        assert result.returncode == 0
        payload = json.loads(result.stdout)
        assert payload["decision"] == "block"
        assert "繁體中文" in payload["reason"]


def test_threshold_boundary_at_max_10_or_5pct_is_silent():
    """visible_len == 200, han count == 10 == max(10, 0.05*200) → silent, exit 0."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        assistant_text = "字" * 10 + "x" * 190
        assert sum(1 for c in assistant_text if not c.isspace()) == 200
        transcript = _write_transcript(tmp_path, ZH_USER_TURN, assistant_text)

        result = run_hook({"transcript_path": str(transcript)})

        assert result.returncode == 0
        assert result.stdout == ""


def test_short_reply_under_200_visible_chars_is_silent():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        assistant_text = "x" * 50  # well under _MIN_REPLY_CHARS, 0 han chars
        transcript = _write_transcript(tmp_path, ZH_USER_TURN, assistant_text)

        result = run_hook({"transcript_path": str(transcript)})

        assert result.returncode == 0
        assert result.stdout == ""


def test_en_transcript_is_silent_even_for_long_all_english_reply():
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        assistant_text = "x" * 250  # long, but conversation language is 'en'
        transcript = _write_transcript(tmp_path, EN_USER_TURN, assistant_text)

        result = run_hook({"transcript_path": str(transcript)})

        assert result.returncode == 0
        assert result.stdout == ""


def test_malformed_stdin_json_is_silent_exit_0():
    result = run_hook("not json {{{")

    assert result.returncode == 0
    assert result.stdout == ""


def test_missing_transcript_path_field_is_silent_exit_0():
    result = run_hook({"stop_hook_active": False})

    assert result.returncode == 0
    assert result.stdout == ""


def test_stop_hook_active_true_short_circuits_even_with_blockable_transcript():
    """Loop guard: stop_hook_active must exit 0 immediately, before any
    transcript reading, or the hook would loop forever on its own block."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        assistant_text = "字" * 9 + "x" * 191  # would block if evaluated
        transcript = _write_transcript(tmp_path, ZH_USER_TURN, assistant_text)

        result = run_hook(
            {"transcript_path": str(transcript), "stop_hook_active": True}
        )

        assert result.returncode == 0
        assert result.stdout == ""
