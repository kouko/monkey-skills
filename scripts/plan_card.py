#!/usr/bin/env python3
"""Render the plan-progress card from a plan file's progress headers.

Task 3 of docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md.
The card body format is pinned ONCE in that plan's N5 block
(`family-relay.md §(a2) Progress card`) and implemented ONCE here —
same spec, two surfaces; a future format change edits both in one
commit (plan Decision Log, 2026-08-06).

Input: argv = one plan-file path. The plan's header region (everything
before the first `## ` heading) must carry a `Goal:` line and a
`Stage:` line (indented continuation lines are folded into the value,
per N1's wrapped-schema shape); the body must carry at least one
`## Task N — <name>` heading, and every task must carry a
`- Status: <value>` bullet where <value> is one of:

    done(<sha>) | claimed(<who>) | pending | blocked[(<why>)]

Output (stdout), field order fixed by N5:

    🎯 <goal>
    tasks: ✅D ⏳C ⬜P 🚫B          (done/claimed/pending/blocked counts)
    <mark> T<N> <name>              (one row per task, file order)
    stage: <stage>
    next: T<N> <name>               (first not-done task; or `close-out`)

A plan missing `Goal:` or `Stage:`, having zero task headings, or
carrying a statusless / unrecognized-status task exits 1 with a
one-line loud message naming the offending field — a partial card is
never rendered. Pure stdlib; `build_card()` is a pure function of the
plan text (raises ValueError; the caller decides exit codes), mirroring
scripts/backlog_index.py's build/main convention.

Usage:
    python3 scripts/plan_card.py <plan-path>

Exit codes: 0 = card rendered, 1 = unreadable/unrenderable plan,
2 = usage error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_TASK_HEADING = re.compile(r"^## Task (\d+) — (.+?)\s*$", re.MULTILINE)
_STATUS_BULLET = re.compile(r"^- \*{0,2}Status\*{0,2}:\s*(\S.*?)\s*$", re.MULTILINE)

# Kind -> mark, in the N5-pinned counts-line order.
_MARKS = {"done": "✅", "claimed": "⏳", "pending": "⬜", "blocked": "🚫"}


def _header_value(header: str, key: str) -> str | None:
    """The value of a `<key>: ...` header line, with indented continuation
    lines folded in (N1 pins the wrapped shape: continuations are
    indented). None when the key line is absent; a present-but-empty
    value comes back as "" (callers treat both as missing)."""
    lines = header.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(f"{key}:"):
            continue
        parts = [line[len(key) + 1 :].strip()]
        for continuation in lines[i + 1 :]:
            if continuation[:1] in (" ", "\t") and continuation.strip():
                parts.append(continuation.strip())
            else:
                break
        return " ".join(part for part in parts if part)
    return None


def _classify(status: str) -> str | None:
    """One of the four kinds, or None for a value outside the vocabulary.
    Done/claimed carry a mandatory parenthesized payload (`done(<sha>)`,
    `claimed(<who>)` — plan Task 3 pins the `(`-anchored match); blocked
    may carry an optional `(<why>)`."""
    if status.startswith("done("):
        return "done"
    if status.startswith("claimed("):
        return "claimed"
    if status == "pending":
        return "pending"
    if status == "blocked" or status.startswith("blocked("):
        return "blocked"
    return None


def _parse_tasks(text: str) -> list[tuple[int, str, str]]:
    """Every `## Task N — <name>` as (number, name, kind), in file order.

    Raises ValueError on a statusless task (old-format plan) or a status
    outside the four kinds — never silently drops or miscounts a task.
    """
    tasks: list[tuple[int, str, str]] = []
    matches = list(_TASK_HEADING.finditer(text))
    for match in matches:
        number, name = int(match.group(1)), match.group(2)
        next_heading = text.find("\n## ", match.end())
        block = text[match.end() : next_heading if next_heading != -1 else len(text)]
        status_match = _STATUS_BULLET.search(block)
        if status_match is None:
            raise ValueError(
                f"task T{number} ({name}) has no '- Status:' line — "
                "either an old-format plan predating the default-on ledger, "
                "or a Status line the parser does not recognize"
            )
        kind = _classify(status_match.group(1))
        if kind is None:
            raise ValueError(
                f"task T{number} ({name}) has status "
                f"'{status_match.group(1)}', outside "
                "done(...)/claimed(...)/pending/blocked"
            )
        tasks.append((number, name, kind))
    return tasks


def build_card(text: str) -> str:
    """The card body per the N5-pinned field order (module docstring).

    Pure function of the plan text: no filesystem reads, no writes.
    Raises ValueError (never exits the process itself — the caller
    decides exit codes) when the plan cannot render a complete card.
    """
    header, _, _ = text.partition("\n## ")

    goal = _header_value(header, "Goal")
    if not goal:
        raise ValueError("plan has no 'Goal:' header line")
    stage = _header_value(header, "Stage")
    if not stage:
        raise ValueError("plan has no 'Stage:' header line")

    tasks = _parse_tasks(text)
    if not tasks:
        raise ValueError("plan has no '## Task N — <name>' headings")

    counts = {kind: 0 for kind in _MARKS}
    for _, _, kind in tasks:
        counts[kind] += 1

    lines = [
        f"🎯 {goal}",
        "tasks: "
        + " ".join(f"{mark}{counts[kind]}" for kind, mark in _MARKS.items()),
    ]
    lines.extend(f"{_MARKS[kind]} T{number} {name}" for number, name, kind in tasks)
    lines.append(f"stage: {stage}")

    next_task = next(
        (f"T{number} {name}" for number, name, kind in tasks if kind != "done"),
        "close-out",
    )
    lines.append(f"next: {next_task}")

    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/plan_card.py <plan-path>", file=sys.stderr)
        return 2

    plan_path = Path(sys.argv[1])
    if not plan_path.is_file():
        print(f"plan_card: FAIL — no plan file at {plan_path}")
        return 1

    try:
        card = build_card(plan_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        print(f"plan_card: FAIL — {exc}")
        return 1

    sys.stdout.write(card)
    return 0


if __name__ == "__main__":
    sys.exit(main())
