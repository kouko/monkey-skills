"""Tests for the ascii-graph-toolkit SessionStart trigger-card hook.

Task 1 (this file, first test only): pins the hook's emitted JSON shape
and content. Mirrors loom-pipeline/scripts/test_family_relay.py's style
(mechanical marker-grep + subprocess execution over the real hook
script, not a mock).

test_description_is_action_moment (Task 2) is added by a LATER task to
this same file — do not add it here.
"""

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "ascii-graph-toolkit"
SESSION_START = PLUGIN_ROOT / "hooks" / "session-start"
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"
TRIGGER_CARD = PLUGIN_ROOT / "hooks" / "trigger-card.md"


def test_session_start_emits_trigger_card():
    """
    hooks/session-start must:
      - exit 0
      - print JSON with hookSpecificOutput.hookEventName == "SessionStart"
        (omitting this key silently disables the hook — see machine memory
        feedback_hook_specific_output_requires_hookeventname)
      - hookSpecificOutput.additionalContext must contain "ascii-graph",
        "CJK", and the trivial-ASCII exemption phrase
        ("Trivial all-ASCII sketches")

    Also asserts hooks.json parses as JSON and wires the SessionStart
    matcher "startup|clear|compact" to hooks/session-start.
    """
    assert SESSION_START.exists(), f"missing hook script: {SESSION_START}"
    assert TRIGGER_CARD.exists(), f"missing trigger card: {TRIGGER_CARD}"

    result = subprocess.run(
        [str(SESSION_START)],
        cwd=str(PLUGIN_ROOT),
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"session-start exited non-zero: {result.stderr}"

    payload = json.loads(result.stdout)
    hook_output = payload["hookSpecificOutput"]
    assert hook_output["hookEventName"] == "SessionStart"

    context = hook_output["additionalContext"]
    assert "ascii-graph" in context
    assert "CJK" in context
    assert "Trivial all-ASCII sketches" in context

    hooks_config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    session_start_entries = hooks_config["hooks"]["SessionStart"]
    matchers = [entry["matcher"] for entry in session_start_entries]
    assert "startup|clear|compact" in matchers

    matched_entry = next(
        entry for entry in session_start_entries
        if entry["matcher"] == "startup|clear|compact"
    )
    commands = [h["command"] for h in matched_entry["hooks"]]
    assert any("hooks/session-start" in cmd for cmd in commands)
