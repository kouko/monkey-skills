#!/usr/bin/env python3
"""skill-telemetry.py — append skill invocation events to a JSONL telemetry log.

Optional Layer-0 infrastructure for the skill-evolution architecture
(see dev-workflow/docs/skill-evolution-architecture.md §6 H4 horizon).

This script is **opt-in** and **per-user**. The telemetry log is
not committed to any repo; each user runs it locally for their
own usage tracking. Privacy considerations are documented inline
and in dev-workflow/docs/telemetry-setup.md.

Two modes of invocation:

1. **As a Claude Code hook** — wired in user's settings.json hook
   configuration; runs on each skill invocation event. The user
   provides hook event data via stdin or environment variables;
   this script translates to the telemetry schema and appends.

2. **Manual logging** — invoked from a terminal session to record
   a skill use observation outside the hook system (e.g.,
   retroactive logging, post-session annotation).

JSONL entry schema:
    {
        "schema_version": 1,
        "timestamp": "ISO8601 UTC",
        "user_id": "<user identifier; default 'local-user'>",
        "session_id": "<session identifier; optional>",
        "event_type": "skill_invoke" | "skill_complete" | "skill_error",
        "skill_name": "<skill identifier>",
        "plugin": "<plugin name; e.g. dev-workflow>",
        "prompt_hash": "<sha256 of user prompt; do NOT log raw prompt by default>",
        "prompt_summary": "<optional, user-confirmed summary; default null>",
        "duration_ms": <optional integer>,
        "outcome": "<optional: success | error | abort | rerun>",
        "user_reaction": "<optional: rerun | edit | accept | abandon>",
        "notes": "<optional free-form>"
    }

Privacy / data handling:

- Default behavior records `prompt_hash` (sha256), NOT raw prompt.
  Raw prompts can contain PII; hashes preserve "did the same prompt
  get used twice" signal without storing content.
- `prompt_summary` is optional and only set if the user explicitly
  provides one (manual mode) or if a hook is configured to extract
  a non-sensitive summary.
- Telemetry log lives at user-chosen path (see --log argument);
  default `~/.claude/skill-telemetry.jsonl`.
- The script does NOT cross network. All processing is local file
  append.
- Sharing telemetry across users / installations requires explicit
  export step (not provided in this scaffold; out-of-scope until
  a real federation use case emerges).

Operations:
    log     — append a single event (manual or hook-driven)
    summarize — per-skill aggregate from local log
    export — write a sanitized copy with optional redaction

Usage:
    python3 scripts/skill-telemetry.py log \
        --log ~/.claude/skill-telemetry.jsonl \
        --skill complexity-critique \
        --plugin dev-workflow \
        --event-type skill_invoke

    python3 scripts/skill-telemetry.py summarize \
        --log ~/.claude/skill-telemetry.jsonl \
        [--skill X]

    python3 scripts/skill-telemetry.py export \
        --log ~/.claude/skill-telemetry.jsonl \
        --out /tmp/sanitized.jsonl \
        [--strip-prompt-summary]

Future extensions (not implemented in v1.9.0 scaffold):
- Hook event translation (read JSON from stdin formatted by Claude
  Code's hook protocol; map to schema)
- User-reaction inference (detect re-runs by hash matching within
  short time window)
- Cross-skill correlation (which skills are invoked in sequence)
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any

DEFAULT_LOG_PATH = Path(os.path.expanduser("~/.claude/skill-telemetry.jsonl"))
SCHEMA_VERSION = 1
DEFAULT_USER = "local-user"


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def hash_prompt(text: str | None) -> str | None:
    if text is None:
        return None
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def append_entry(log_path: Path, entry: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_entries(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    entries = []
    with log_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"warning: malformed line {lineno}: {e}", file=sys.stderr)
    return entries


def op_log(args: argparse.Namespace) -> int:
    entry = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": now_iso(),
        "user_id": args.user_id or DEFAULT_USER,
        "session_id": args.session_id or str(uuid.uuid4())[:8],
        "event_type": args.event_type,
        "skill_name": args.skill,
        "plugin": args.plugin,
    }
    if args.prompt:
        entry["prompt_hash"] = hash_prompt(args.prompt)
    if args.prompt_summary:
        entry["prompt_summary"] = args.prompt_summary
    if args.duration_ms is not None:
        entry["duration_ms"] = args.duration_ms
    if args.outcome:
        entry["outcome"] = args.outcome
    if args.user_reaction:
        entry["user_reaction"] = args.user_reaction
    if args.notes:
        entry["notes"] = args.notes

    append_entry(args.log, entry)
    print(f"appended to {args.log}: skill={args.skill} event={args.event_type}")
    return 0


def op_summarize(args: argparse.Namespace) -> int:
    entries = load_entries(args.log)
    if args.skill:
        entries = [e for e in entries if e.get("skill_name") == args.skill]

    by_skill: dict[str, dict[str, Any]] = {}
    for e in entries:
        s = e.get("skill_name", "<unknown>")
        bucket = by_skill.setdefault(s, {"invokes": 0, "completes": 0, "errors": 0, "rerun": 0})
        evt = e.get("event_type")
        if evt == "skill_invoke":
            bucket["invokes"] += 1
        elif evt == "skill_complete":
            bucket["completes"] += 1
        elif evt == "skill_error":
            bucket["errors"] += 1
        if e.get("user_reaction") == "rerun":
            bucket["rerun"] += 1

    output = {
        "log_path": str(args.log),
        "filter_skill": args.skill,
        "total_entries": len(entries),
        "by_skill": by_skill,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


def op_export(args: argparse.Namespace) -> int:
    entries = load_entries(args.log)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with args.out.open("w", encoding="utf-8") as f:
        for entry in entries:
            sanitized = dict(entry)
            if args.strip_prompt_summary:
                sanitized.pop("prompt_summary", None)
            if args.strip_user_id:
                sanitized.pop("user_id", None)
            if args.strip_notes:
                sanitized.pop("notes", None)
            f.write(json.dumps(sanitized, ensure_ascii=False) + "\n")
            written += 1

    print(f"exported {written} entries to {args.out} (sanitization applied)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="append a single event")
    p_log.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH)
    p_log.add_argument("--skill", required=True)
    p_log.add_argument("--plugin", required=True)
    p_log.add_argument(
        "--event-type",
        required=True,
        choices=["skill_invoke", "skill_complete", "skill_error"],
    )
    p_log.add_argument("--user-id", default=None)
    p_log.add_argument("--session-id", default=None)
    p_log.add_argument("--prompt", help="Raw prompt; will be hashed not stored")
    p_log.add_argument("--prompt-summary", help="User-confirmed non-sensitive summary")
    p_log.add_argument("--duration-ms", type=int, default=None)
    p_log.add_argument(
        "--outcome", choices=["success", "error", "abort", "rerun"], default=None
    )
    p_log.add_argument(
        "--user-reaction",
        choices=["rerun", "edit", "accept", "abandon"],
        default=None,
    )
    p_log.add_argument("--notes")

    p_sum = sub.add_parser("summarize", help="per-skill aggregate from local log")
    p_sum.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH)
    p_sum.add_argument("--skill", default=None)

    p_exp = sub.add_parser("export", help="sanitized export")
    p_exp.add_argument("--log", type=Path, default=DEFAULT_LOG_PATH)
    p_exp.add_argument("--out", type=Path, required=True)
    p_exp.add_argument("--strip-prompt-summary", action="store_true")
    p_exp.add_argument("--strip-user-id", action="store_true")
    p_exp.add_argument("--strip-notes", action="store_true")

    args = parser.parse_args()
    if args.cmd == "log":
        return op_log(args)
    if args.cmd == "summarize":
        return op_summarize(args)
    if args.cmd == "export":
        return op_export(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
