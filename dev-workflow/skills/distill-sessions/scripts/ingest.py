"""ingest.py — Claude Code session JSONL → Event[] adapter.

External surface (memory project_external_surface_grounding_discipline.md):
Claude Code stores per-session transcripts as JSONL files under
`~/.claude/projects/<project-encoded>/<sessionId>.jsonl`. This is an
**undocumented 1st-party Anthropic internal format**; verified against
Claude Code v2.1.144 on 2026-05-22.

Observed line shape (deviations from the research-memo quoted schema
are recorded in the implementer status output, not silently patched):

- Top-level records may carry `type` ∈
  {`user`, `assistant`, `attachment`, `queue-operation`,
  `permission-mode`, `file-history-snapshot`, `last-prompt`, ...}.
  Only `user` and `assistant` carry conversational content; the others
  are housekeeping records and are skipped silently.
- `user` / `assistant` records carry:
  - `parentUuid`, `uuid`, `sessionId`, `timestamp`, `cwd`, `version`,
    `gitBranch`, `userType`, `entrypoint`
  - `message.role` (`user` / `assistant`)
  - `message.content` — either a `str` (legacy / slash-command shape) or
    a `list[dict]` with items typed `text`, `tool_use`, `tool_result`,
    `thinking` (assistant only).

Per the plan, this adapter:

- Walks `~/.claude/projects/**/*.jsonl` by default (caller may override
  `root`).
- Excludes paths matching any glob in `exclude_globs` (default
  `["**/subagents/**"]`).
- Parses each line as JSON; non-JSON / non-conformant lines are skipped
  silently (line-by-line resilience — JSONL files in production
  occasionally have stray bad lines and we don't want one bad byte to
  crash a multi-hour ingest).
- Yields one Event per `user` / `assistant` record (generator pattern;
  do NOT materialize the full list — sessions can exceed 100 MB).

Per Plan Part 1 §Task 2.
"""

from __future__ import annotations

import fnmatch
import json
import re
from collections.abc import Iterator
from pathlib import Path

from event import Event

# Default JSONL traversal root — overridable for tests / cross-host use.
DEFAULT_ROOT = Path.home() / ".claude" / "projects"

# Default exclusion: subagent transcripts (own session tree, not the
# orchestrator's first-person trajectory we want to mine).
DEFAULT_EXCLUDE_GLOBS: list[str] = ["**/subagents/**"]

# Layer-A agent literal at v0.1. Future adapters set their own.
_AGENT_LITERAL = "claude-code"

# `Skill(skill: "...")` form sometimes appears in transcript text (when
# the harness echoes the call into a text node rather than a tool_use
# block). Capture both that AND `<command-name>...</command-name>` for
# slash-commands.
_SKILL_CALL_RE = re.compile(r'Skill\s*\(\s*skill\s*:\s*"([^"]+)"')
_COMMAND_NAME_RE = re.compile(r"<command-name>([^<]+)</command-name>")

# Interrupt marker — Claude Code emits this exact literal in a user
# text content item when the user hits the interrupt key.
_INTERRUPT_MARKER = "[Request interrupted by user]"


def _path_excluded(path: Path, exclude_globs: list[str]) -> bool:
    """True iff `path` matches any glob in `exclude_globs`.

    Uses POSIX-style `as_posix()` so the same globs work across OSes.
    """
    posix = path.as_posix()
    return any(fnmatch.fnmatch(posix, glob) for glob in exclude_globs)


def _extract_text_and_skill(
    content: object,
) -> tuple[str, str | None, str | None, str | None, bool]:
    """Pull (text, tool_name, tool_error, skill_invocation, interrupt)
    out of a `message.content` field.

    `content` may be a plain string (legacy / slash-command shape) or a
    list of typed dicts. Both shapes coexist in real fixtures (see
    test_ingest.py / fixture_sample.jsonl).
    """
    tool_name: str | None = None
    tool_error: str | None = None
    skill_invocation: str | None = None
    interrupt = False

    if isinstance(content, str):
        text = content
        if _INTERRUPT_MARKER in text:
            interrupt = True
        # Slash-command echo or skill-call echo embedded in text:
        m_cmd = _COMMAND_NAME_RE.search(text)
        if m_cmd:
            skill_invocation = m_cmd.group(1).strip()
        else:
            m_skill = _SKILL_CALL_RE.search(text)
            if m_skill:
                skill_invocation = m_skill.group(1).strip()
        return text, tool_name, tool_error, skill_invocation, interrupt

    if not isinstance(content, list):
        return "", tool_name, tool_error, skill_invocation, interrupt

    text_parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "text":
            t = item.get("text", "")
            if isinstance(t, str):
                text_parts.append(t)
                if _INTERRUPT_MARKER in t:
                    interrupt = True
                m_cmd = _COMMAND_NAME_RE.search(t)
                if m_cmd and skill_invocation is None:
                    skill_invocation = m_cmd.group(1).strip()
                else:
                    m_skill = _SKILL_CALL_RE.search(t)
                    if m_skill and skill_invocation is None:
                        skill_invocation = m_skill.group(1).strip()
        elif item_type == "tool_use":
            name = item.get("name")
            if isinstance(name, str):
                tool_name = name
            inp = item.get("input")
            # Detect Skill tool_use shape: {name: "Skill", input: {skill: "..."}}
            if (
                name == "Skill"
                and isinstance(inp, dict)
                and isinstance(inp.get("skill"), str)
                and skill_invocation is None
            ):
                skill_invocation = inp["skill"].strip()
            # Capture tool_use input as text for downstream pattern
            # matching (compact JSON, no whitespace).
            try:
                text_parts.append(json.dumps(inp, separators=(",", ":")))
            except (TypeError, ValueError):
                pass
        elif item_type == "tool_result":
            is_err = bool(item.get("is_error"))
            result_content = item.get("content")
            if isinstance(result_content, str):
                text_parts.append(result_content)
                if is_err:
                    tool_error = result_content
            elif isinstance(result_content, list):
                # tool_result content can itself be a list of dicts
                # carrying text items — flatten for pattern matching.
                joined: list[str] = []
                for ri in result_content:
                    if isinstance(ri, dict):
                        t = ri.get("text") or ri.get("content")
                        if isinstance(t, str):
                            joined.append(t)
                joined_text = "\n".join(joined)
                if joined_text:
                    text_parts.append(joined_text)
                if is_err and joined_text:
                    tool_error = joined_text
        # `thinking` items are skipped — they're internal CoT, not
        # observable user-facing content. Including them would noise up
        # friction-signal detection in Stage 2.

    return (
        "\n".join(text_parts),
        tool_name,
        tool_error,
        skill_invocation,
        interrupt,
    )


def _record_to_event(record: dict, is_subagent: bool) -> Event | None:
    """Map one JSONL record dict → Event, or None to skip.

    Skips:
    - Records without `type` ∈ {`user`, `assistant`} (housekeeping).
    - Records missing `sessionId` or `timestamp` (malformed).
    """
    rec_type = record.get("type")
    if rec_type not in ("user", "assistant"):
        return None

    session = record.get("sessionId")
    timestamp = record.get("timestamp")
    if not isinstance(session, str) or not isinstance(timestamp, str):
        return None

    message = record.get("message")
    if not isinstance(message, dict):
        return None

    role = message.get("role")
    if not isinstance(role, str):
        role = rec_type  # fall back to top-level type as role

    content = message.get("content")
    (
        text,
        tool_name,
        tool_error,
        skill_invocation,
        interrupt,
    ) = _extract_text_and_skill(content)

    return Event(
        agent=_AGENT_LITERAL,
        session=session,
        ts=timestamp,
        role=role,
        text=text,
        tool_name=tool_name,
        tool_error=tool_error,
        user_interrupt=interrupt,
        is_subagent=is_subagent,
        skill_invocation=skill_invocation,
    )


def ingest_claude_jsonl(
    root: Path | None = None,
    exclude_globs: list[str] | None = None,
) -> Iterator[Event]:
    """Walk `root/**/*.jsonl` and yield one Event per user/assistant record.

    Args:
        root: directory to walk. Defaults to `~/.claude/projects`.
            For testing, point at the directory holding
            `fixture_sample.jsonl`.
        exclude_globs: list of glob patterns matched against each file's
            POSIX path. Defaults to `["**/subagents/**"]`.

    Yields:
        Event records, one per parseable `user` / `assistant` JSONL line.
        Non-JSON lines, malformed records, and housekeeping records
        (queue-operation / attachment / permission-mode / etc.) are
        skipped silently.

    Memory note: this is a generator. Do not wrap with `list(...)` on
    untrusted-size inputs — real `~/.claude/projects/` trees can exceed
    600 MB.
    """
    if root is None:
        root = DEFAULT_ROOT
    if exclude_globs is None:
        exclude_globs = list(DEFAULT_EXCLUDE_GLOBS)

    root = Path(root).expanduser()
    if not root.exists():
        return

    for path in sorted(root.rglob("*.jsonl")):
        if not path.is_file():
            continue
        if _path_excluded(path, exclude_globs):
            continue
        is_subagent = "/subagents/" in path.as_posix()
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        # Stray bad line — skip silently per docstring.
                        continue
                    if not isinstance(record, dict):
                        continue
                    event = _record_to_event(record, is_subagent)
                    if event is not None:
                        yield event
        except OSError:
            # Permission / IO error on one file shouldn't kill the
            # whole ingest.
            continue
