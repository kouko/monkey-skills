#!/usr/bin/env python3
"""Read a plan's decision-map delivery progress without writing MAP.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


_NOTES_HEADING = re.compile(r"^## Notes\s*$", re.MULTILINE)
_NEXT_HEADING = re.compile(r"^## ", re.MULTILINE)
_BINDING = re.compile(
    r"^Map part:\s*(?P<map_id>[^/\n]+?)\s*/\s*Part:\s*"
    r"(?P<part>[^\n]+?)\s*$",
    re.MULTILINE,
)
_TASK_HEADING = re.compile(r"^## Task \d+ — .+?$", re.MULTILINE)
_STATUS = re.compile(
    r"^- \*{0,2}Status\*{0,2}:\s*"
    r"(?P<status>done\([^()\s]+\)|claimed\(@[^()\s]+\)|pending|blocked"
    r"(?:\([^()\n]*\))?)\s*$",
    re.MULTILINE,
)


class ProgressError(Exception):
    """Structural plan/binding error — exit 2."""


def _notes_section(text: str) -> str:
    match = _NOTES_HEADING.search(text)
    if match is None:
        raise ProgressError("plan has no '## Notes' section")
    next_heading = _NEXT_HEADING.search(text, match.end())
    return text[match.end() : next_heading.start() if next_heading else len(text)]


def _bound_part(text: str) -> tuple[str, str]:
    matches = list(_BINDING.finditer(_notes_section(text)))
    if len(matches) != 1:
        raise ProgressError(
            "plan Notes must contain exactly one 'Map part:' delivery binding"
        )
    return matches[0].group("map_id").strip(), matches[0].group("part").strip()


def _ledger_state(text: str) -> str:
    task_matches = list(_TASK_HEADING.finditer(text))
    if not task_matches:
        raise ProgressError("plan has no task headings")
    states = []
    for task in task_matches:
        next_heading = _NEXT_HEADING.search(text, task.end())
        block = text[task.end() : next_heading.start() if next_heading else len(text)]
        status = _STATUS.search(block)
        if status is None:
            raise ProgressError("plan task has no recognized '- Status:' line")
        states.append(status.group("status"))
    if any(state.startswith("blocked") for state in states):
        return "blocked"
    if any(state.startswith("claimed(") for state in states):
        return "claimed"
    if any(state == "pending" for state in states):
        return "pending"
    return "done"


def derive_progress(text: str) -> tuple[str, str, str]:
    """Return (map_id, part, derived ledger state) for one plan's binding."""
    map_id, part = _bound_part(text)
    return map_id, part, _ledger_state(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read a plan's decision-map delivery progress."
    )
    parser.add_argument("target", help="plan path carrying the Notes binding")
    parser.add_argument("--repo-root", help="accepted for command-surface parity")
    args = parser.parse_args(argv)
    plan_path = Path(args.target)
    try:
        text = plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: cannot read {plan_path}: {exc}", file=sys.stderr)
        return 1
    try:
        map_id, part, state = derive_progress(text)
    except ProgressError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"map delivery-progress: {map_id} / {part}")
    print(f"plan: {plan_path.name}")
    print(f"state: {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
