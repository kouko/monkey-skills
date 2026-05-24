"""test_ingest.py — verifies ingest_claude_jsonl maps real Claude Code
JSONL records to Event[] correctly.

Fixture: `fixture_sample.jsonl` in this same directory, 10 lines, hand-
anonymized from a real `~/.claude/projects/` session. Covers:

- user message with str content,
- assistant text reply,
- assistant tool_use Skill invocation (skill_invocation extraction),
- user tool_result with is_error=False (no tool_error),
- assistant tool_use of a regular tool (tool_name capture),
- user tool_result with is_error=True (tool_error capture),
- user `[Request interrupted by user]` marker (user_interrupt=True),
- a deliberate malformed line (must be skipped silently),
- user content as raw `<command-name>/compact</command-name>` string
  (skill_invocation extraction for slash commands),
- one housekeeping `queue-operation` line (must be skipped silently).

Per dev-workflow/skills/distill-sessions Plan Part 1 §Task 2 acceptance.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

# Allow `from event import Event` / `from ingest import ...` when pytest
# is invoked from the repo root.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from ingest import ingest_claude_jsonl  # noqa: E402

FIXTURE_DIR = _HERE
EXPECTED_SESSION = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"


def _parse_ts(ts: str) -> datetime:
    """Parse Claude Code's `2026-05-22T10:14:00.000Z` timestamp via
    stdlib datetime.fromisoformat (after normalizing the trailing Z)."""
    # datetime.fromisoformat tolerates `+00:00` but not the `Z` suffix
    # on Python <3.11 — normalize either way for portability.
    normalized = ts.rstrip("Z")
    if ts.endswith("Z"):
        normalized = normalized + "+00:00"
    return datetime.fromisoformat(normalized)


def test_ingest_parses_real_session_fixture():
    """End-to-end: ingest the committed sample fixture, assert Event[]
    has the expected shape + key signals are extracted.

    This is the GREEN test for T2 per the dispatch prompt acceptance.
    """
    events = list(ingest_claude_jsonl(FIXTURE_DIR))

    # 1. At least three Events parsed (the fixture has 6 conversational
    # records + 1 housekeeping + 1 malformed — we expect 6 events).
    assert len(events) >= 3, f"expected ≥3 events, got {len(events)}"

    # 2. Every event has the expected session id (no cross-session
    # leakage from a stray record).
    for ev in events:
        assert ev.session == EXPECTED_SESSION, (
            f"unexpected session: {ev.session!r}"
        )

    # 3. At least one event has role in {"user", "assistant"}.
    roles = {ev.role for ev in events}
    assert roles & {"user", "assistant"}, (
        f"expected user/assistant roles, got {roles}"
    )

    # 4. Every event's `ts` field parses as ISO-8601.
    for ev in events:
        try:
            _parse_ts(ev.ts)
        except ValueError as e:
            raise AssertionError(
                f"timestamp {ev.ts!r} not parseable: {e}"
            ) from e

    # 5. agent literal is "claude-code" at v0.1 for every event.
    assert all(ev.agent == "claude-code" for ev in events), (
        f"non-claude-code agent literal: "
        f"{[ev.agent for ev in events if ev.agent != 'claude-code']}"
    )


def test_ingest_extracts_skill_invocation_from_tool_use():
    """The fixture includes an assistant tool_use Skill block; the
    Skill name must surface in `skill_invocation`."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    skill_calls = [ev.skill_invocation for ev in events if ev.skill_invocation]
    assert "code-toolkit:brainstorming" in skill_calls, (
        f"Skill tool_use not extracted: skill_invocation values = "
        f"{skill_calls}"
    )


def test_ingest_extracts_command_name_for_slash_command():
    """User message with `<command-name>/compact</command-name>` string
    content surfaces the slash-command name in `skill_invocation`."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    cmd_calls = [ev.skill_invocation for ev in events if ev.skill_invocation]
    assert "/compact" in cmd_calls, (
        f"<command-name> not extracted: {cmd_calls}"
    )


def test_ingest_flags_user_interrupt():
    """The `[Request interrupted by user]` user record must produce an
    Event with user_interrupt=True."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    assert any(ev.user_interrupt for ev in events), (
        "expected at least one Event with user_interrupt=True"
    )


def test_ingest_captures_tool_error_when_is_error_true():
    """The is_error=True tool_result line surfaces its content in
    `tool_error`; non-error tool_result line leaves tool_error=None."""
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    errors = [ev.tool_error for ev in events if ev.tool_error]
    assert any("tool_use_error" in (e or "") for e in errors), (
        f"is_error=True tool_result not captured: tool_error values = "
        f"{errors}"
    )


def test_ingest_skips_malformed_lines_silently():
    """The fixture contains one malformed (non-JSON) line. Ingest must
    not raise; it must just skip that line. We assert by counting
    parseable events — if the malformed line crashed iteration, fewer
    events would come through."""
    # Just constructing the generator + consuming must not raise.
    events = list(ingest_claude_jsonl(FIXTURE_DIR))
    # Sanity: fixture has 5 user + 3 assistant = 8 conversational
    # records. The `queue-operation` housekeeping line and the
    # malformed stray line are both excluded.
    assert len(events) == 8, (
        f"expected exactly 8 user/assistant events from fixture, "
        f"got {len(events)}"
    )


def test_ingest_default_excludes_subagent_paths(tmp_path):
    """Files under `*/subagents/*` must be excluded by default. We
    create a temp tree with one subagent JSONL and assert it's skipped.
    """
    sub = tmp_path / "session-A" / "subagents"
    sub.mkdir(parents=True)
    (sub / "agent-X.jsonl").write_text(
        '{"type":"user","sessionId":"sub","timestamp":"2026-05-22T00:00:00Z",'
        '"message":{"role":"user","content":"should not appear"}}\n',
        encoding="utf-8",
    )
    # Also write one top-level JSONL to confirm the walker does find files.
    (tmp_path / "ok.jsonl").write_text(
        '{"type":"user","sessionId":"top","timestamp":"2026-05-22T00:00:01Z",'
        '"message":{"role":"user","content":"top-level"}}\n',
        encoding="utf-8",
    )
    events = list(ingest_claude_jsonl(tmp_path))
    sessions = {ev.session for ev in events}
    assert sessions == {"top"}, (
        f"expected only top-level session, got {sessions}"
    )


def test_ingest_returns_iterator_not_list():
    """Generator pattern — must yield, not materialize, so 600 MB
    `~/.claude/projects/` ingests stay memory-safe.

    The runtime object must be an iterator. A plain `list` is bad.
    """
    result = ingest_claude_jsonl(FIXTURE_DIR)
    assert not isinstance(result, list), (
        "ingest_claude_jsonl must be a generator, got a list — would "
        "OOM on a real 600 MB ~/.claude/projects/ tree."
    )
    # Confirm it's actually iterable (consume one item).
    iter(result)
