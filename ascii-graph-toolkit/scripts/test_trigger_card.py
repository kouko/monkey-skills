"""Tests for the ascii-graph-toolkit SessionStart trigger-card hook.

Task 1 (this file, first test only): pins the hook's emitted JSON shape
and content. Mirrors loom-pipeline/scripts/test_family_relay.py's style
(mechanical marker-grep + subprocess execution over the real hook
script, not a mock).

test_description_is_action_moment (Task 2): pins SKILL.md's frontmatter
description as an action-moment sentence (per
docs/loom/memory/skill-triggering-diagnose-listing-before-text.md, at
most one CJK trigger-phrase segment — CJK keyword stuffing is
A/B-refuted).
"""

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "ascii-graph-toolkit"
SESSION_START = PLUGIN_ROOT / "hooks" / "session-start"
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"
TRIGGER_CARD = PLUGIN_ROOT / "hooks" / "trigger-card.md"
SKILL_MD = PLUGIN_ROOT / "skills" / "ascii-graph" / "SKILL.md"

# Matches a run of CJK codepoints (CJK Unified Ideographs + Hiragana/Katakana)
# as one "phrase segment" for the at-most-one-CJK-phrase check.
CJK_RUN_RE = re.compile(r"[一-鿿぀-ヿ]+")


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


def test_description_is_action_moment():
    """
    skills/ascii-graph/SKILL.md frontmatter `description:` must:
      - start with "Use BEFORE" (action-moment framing, not a noun phrase)
      - contain the action-moment trigger condition ("CJK" + "boxes")
      - be <=1024 chars (skill-listing budget margin; house cap is 1536)
      - contain AT MOST ONE CJK trigger-phrase segment (A/B-refuted
        stuffing — docs/loom/memory/skill-triggering-diagnose-listing-before-text.md)
    """
    assert SKILL_MD.exists(), f"missing SKILL.md: {SKILL_MD}"
    text = SKILL_MD.read_text(encoding="utf-8")

    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert frontmatter_match, "SKILL.md missing frontmatter block"
    frontmatter = frontmatter_match.group(1)

    desc_match = re.search(
        r"^description:\s*\|?\s*\n(.*?)(?=^\S|\Z)", frontmatter, re.DOTALL | re.MULTILINE
    )
    assert desc_match, "SKILL.md frontmatter missing description: field"
    description = desc_match.group(1).strip()

    assert description.startswith("Use BEFORE"), (
        f"description must start with 'Use BEFORE', got: {description[:40]!r}"
    )
    assert "CJK" in description
    assert "boxes" in description
    assert len(description) <= 1024, f"description too long: {len(description)} chars"

    cjk_segments = CJK_RUN_RE.findall(description)
    assert len(cjk_segments) <= 1, (
        f"expected at most one CJK trigger-phrase segment, found {cjk_segments}"
    )
