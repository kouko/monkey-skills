"""event.py — unified Event dataclass for skill-log-mining v0.1.

Layer-A future-proof: `agent` field defaults to "claude-code" at v0.1;
later adapters (codex / gemini) populate the same shape with their own
agent literal so downstream Stage 2-5 code stays adapter-agnostic.

Schema is the contract between scripts/ingest.py (writer) and Stage 2-5
consumers (facets.py / friction_signals.py / aggregate.py — landed in
T3-T5 of Part 1).

Per dev-workflow/skills/skill-log-mining Plan Part 1 §Task 2.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Event:
    """One normalized log record from a Claude Code session JSONL.

    Fields (all required; optional ones have explicit None / False defaults
    so downstream consumers can treat missing-info uniformly):

    - agent: literal "claude-code" at v0.1; "codex" / "gemini" at v1+.
    - session: source sessionId string (UUID at v0.1 — Claude Code shape).
    - ts: ISO-8601 timestamp string (parseable via datetime.fromisoformat
      after the trailing 'Z' is replaced with '+00:00').
    - role: "user" / "assistant" / "system" / "tool" — straight from the
      JSONL `type` (which Claude Code uses as role) or `message.role`.
    - text: best-effort textual content of the event for downstream
      pattern matching. For tool_use / tool_result, this captures the
      JSON of the input / result.
    - tool_name: name of the tool when role is "assistant" with a
      tool_use block; None otherwise.
    - tool_error: when a tool_result block has is_error=True, the error
      string content; None otherwise.
    - user_interrupt: True when content text contains
      `[Request interrupted by user]` (Claude Code interrupt marker).
    - is_subagent: True when the JSONL path matches `*/subagents/*`
      (transcripts of dispatched subagents). v0.1 default-excludes these
      via ingest's `exclude_globs`, so under default ingest this stays
      False — kept for explicit-include callers.
    - skill_invocation: when an assistant invokes a Skill via
      `Skill(skill: "<name>")` tool_use OR a user message wraps a slash
      command in `<command-name>...</command-name>`, the parsed skill /
      command name; None otherwise.
    """

    agent: str
    session: str
    ts: str
    role: str
    text: str
    tool_name: str | None = None
    tool_error: str | None = None
    user_interrupt: bool = False
    is_subagent: bool = False
    skill_invocation: str | None = None
