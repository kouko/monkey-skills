"""Tests for loom-code/hooks/ask-triage.py — the PreToolUse ask-triage card.

Each test subprocess-runs the hook exactly as Claude Code would invoke
it: hook-event JSON on stdin, additionalContext JSON on stdout, exit 0.
Subprocess (not import) is required — ``ask-triage.py`` is a hyphenated
filename and is not importable as a Python module (Kickoff decision,
docs/loom/plans/2026-07-14-mid-task-ask-layered-defense.md ## Notes).

External surfaces grounded (per
loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md):

- Claude Code PreToolUse hook contract (JSON event on stdin;
  ``hookSpecificOutput.hookEventName`` + ``.additionalContext`` on
  stdout; exit 0 = allow): source-(d) in-repo evidence — the identical
  shape is emitted by ``loom-code/hooks/session-start`` (SessionStart)
  and consumed via the same PreToolUse contract by
  ``loom-code/hooks/git-guard.py``, both registered in
  ``loom-code/hooks/hooks.json``.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "ask-triage.py"
HOOKS_JSON = Path(__file__).resolve().parent.parent / "hooks" / "hooks.json"

# Distinctive stable fragments of the pinned card (plan ## Notes
# §Pinned card text) — substring matches, not full-string equality, so
# incidental rewording elsewhere in the card doesn't break the test.
ARM1_LOOKUP = "look it up instead of asking"
ARM2_CONFIRM = "confirmation of an irreversible/outward-facing action"
ARM3_RESEARCH = "design/approach fork that industry practice could inform"
CLEARANCE = "never a reason to avoid or delay such asks"
RECOMMENDATION = "cited recommendation"


def run_hook(payload):
    """Run the hook with `payload` (dict → JSON, str → raw) on stdin."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def test_emits_valid_json_on_ask_user_question_input():
    result = run_hook({"tool_name": "AskUserQuestion", "tool_input": {}})
    assert result.returncode == 0
    json.loads(result.stdout)  # must not raise


def test_hook_event_name_is_pre_tool_use():
    result = run_hook({"tool_name": "AskUserQuestion", "tool_input": {}})
    payload = json.loads(result.stdout)
    assert payload["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_additional_context_contains_all_three_triage_arms_and_clearance():
    result = run_hook({"tool_name": "AskUserQuestion", "tool_input": {}})
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert ARM1_LOOKUP in context
    assert ARM2_CONFIRM in context
    assert ARM3_RESEARCH in context
    assert CLEARANCE in context
    assert RECOMMENDATION in context


@pytest.mark.parametrize(
    "stdin_payload",
    ["", "not json {{{"],
    ids=["empty-stdin", "non-json-stdin"],
)
def test_fail_open_on_bad_stdin_still_emits_card(stdin_payload):
    """ask-triage.py:62-64 fail-open path: malformed/absent stdin must
    still exit 0 and emit the same card, never crash the session."""
    result = run_hook(stdin_payload)
    assert result.returncode == 0
    payload = json.loads(result.stdout)  # must not raise
    assert payload["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert ARM1_LOOKUP in payload["hookSpecificOutput"]["additionalContext"]


def test_hooks_json_parses_and_has_ask_user_question_matcher():
    data = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    pre_tool_use = data["hooks"]["PreToolUse"]
    matchers = [entry.get("matcher") for entry in pre_tool_use]
    assert "AskUserQuestion" in matchers
