#!/usr/bin/env python3
"""Check that a writing-plans plan's `- **Seam**:` fields cover every
incoming `- **Dependencies**:` edge, per
`loom-code/skills/writing-plans/references/plan-format.md`
`#### Seam (v0.100.0+)`.

Inputs (positional CLI arg):

    check_seam_coverage.py <plan-path>

Per that grammar, a task (a `## Task <N> — ...` block) whose `Dependencies`
value is not "none" MUST carry a `Seam` field with one bullet per incoming
dependency edge — `Dependencies: Task 1 completes first` is one edge (from
Task 1); `Dependencies: Tasks 3, 4, 5 complete first` is three edges. Each
bullet is one of exactly two forms:

    - from Task <N>: payload: none
    - from Task <N>: payload: <shape>; owner: Task <M>; probe: <name>

This script checks four things mechanically, exiting 1 with one
agent-actionable stderr line per finding:

    (i)   a task with Dependencies != "none" has no `Seam` field at all.
    (ii)  an incoming Dependencies edge has no matching `from Task <N>`
          bullet in that task's Seam field.
    (iii) a payload-bearing bullet (payload != none) is missing `owner:`
          or `probe:`.
    (iv)  a `probe:` value does not appear (substring match) in that
          task's own `- **Acceptance**:` block.

Whether the named probe is actually adequate is NOT checked here — per
plan-format.md, that stays the reviewers' judgment. This script only
checks presence and the owner/probe cross-reference.

exit 0 — every Dependencies edge is covered by a matching Seam bullet, or
         the plan declares zero tasks with Dependencies != "none"
         (vacuous — nothing to check).
exit 1 — one or more of the four checks above fails; each finding is
         printed on stderr, one per line.

A missing or unreadable plan file fails loud: nonzero exit, no raw
traceback, the unreadable/missing path named on stderr.

Stdlib only.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
import re

# Any level-2 heading — used to slice the plan into task blocks. A task
# block runs from its own `## Task <N> — ...` header to the next `^##\s`
# heading (whether another task or a non-task section like `## Notes`), or
# EOF for the last one.
_H2 = re.compile(r"^##\s+\S.*$", re.MULTILINE)
_TASK_HDR = re.compile(r"^##\s+Task\s+(\d+)\b")

_DEP_LINE = re.compile(r"^-\s*\*\*Dependencies\*\*:\s*(.+)$", re.MULTILINE)
_SEAM_HDR = re.compile(r"^-\s*\*\*Seam\*\*:", re.MULTILINE)

# One `Seam` sub-bullet: `  - from Task <N>: payload: <rest>`. The `<rest>`
# is split further below into shape / owner / probe, since a shape may
# itself legally contain no semicolons while owner/probe are `; key: value`
# suffixes per the grammar.
_SEAM_BULLET = re.compile(
    r"^\s+-\s*from Task\s+(?P<from>\d+):\s*payload:\s*(?P<rest>.+)$",
    re.MULTILINE,
)
_OWNER_PART = re.compile(r"^owner:\s*Task\s*(\d+)\s*$", re.IGNORECASE)
_PROBE_PART = re.compile(r"^probe:\s*(.+)$", re.IGNORECASE)

# The `- **Acceptance**:` field's own indented body (its `- **RED**:` /
# `- **GREEN**:` sub-bullets and anything nested under them) — everything
# indented immediately following the header line, stopping at the first
# line back at column 0 (the next top-level task field).
_ACCEPTANCE_SECTION = re.compile(
    r"^-\s*\*\*Acceptance\*\*:\s*\n((?:^[ \t]+.*\n?)*)", re.MULTILINE
)


@dataclass
class _SeamBullet:
    from_task: int
    payload_none: bool
    owner: int | None
    probe: str | None


@dataclass
class _TaskBlock:
    number: int
    dep_edges: set[int] = field(default_factory=set)
    has_seam_field: bool = False
    seam_by_from: dict[int, _SeamBullet] = field(default_factory=dict)
    acceptance_text: str = ""


def _parse_dependencies(value: str) -> set[int]:
    """Every task number named by a `Dependencies` value. `"none"`
    (case-insensitive) names none; every other legal form (`Task N
    completes first`, `Tasks N, M complete first`, `Tasks N, M parallel`)
    names its task numbers as the only digit runs in the value."""
    if value.strip().lower() == "none":
        return set()
    return {int(n) for n in re.findall(r"\d+", value)}


def _parse_seam_bullets(block_text: str) -> dict[int, _SeamBullet]:
    bullets: dict[int, _SeamBullet] = {}
    for m in _SEAM_BULLET.finditer(block_text):
        from_task = int(m.group("from"))
        rest = m.group("rest").strip()
        parts = [p.strip() for p in rest.split(";")]
        shape = parts[0]
        if shape.lower() == "none":
            bullets[from_task] = _SeamBullet(from_task, True, None, None)
            continue
        owner: int | None = None
        probe: str | None = None
        for part in parts[1:]:
            owner_m = _OWNER_PART.match(part)
            if owner_m is not None:
                owner = int(owner_m.group(1))
                continue
            probe_m = _PROBE_PART.match(part)
            if probe_m is not None:
                probe = probe_m.group(1).strip()
        bullets[from_task] = _SeamBullet(from_task, False, owner, probe)
    return bullets


def _parse_task_block(number: int, block_text: str) -> _TaskBlock:
    task = _TaskBlock(number=number)
    dep_match = _DEP_LINE.search(block_text)
    if dep_match is not None:
        task.dep_edges = _parse_dependencies(dep_match.group(1).strip())
    task.has_seam_field = bool(_SEAM_HDR.search(block_text))
    task.seam_by_from = _parse_seam_bullets(block_text)
    accept_match = _ACCEPTANCE_SECTION.search(block_text)
    task.acceptance_text = accept_match.group(1) if accept_match else ""
    return task


def parse_tasks(plan_text: str) -> dict[int, _TaskBlock]:
    """Every `## Task <N> — ...` block in `plan_text`, keyed by task
    number."""
    h2_matches = list(_H2.finditer(plan_text))
    tasks: dict[int, _TaskBlock] = {}
    for i, m in enumerate(h2_matches):
        title_line = m.group(0)
        task_hdr = _TASK_HDR.match(title_line)
        if task_hdr is None:
            continue
        number = int(task_hdr.group(1))
        block_start = m.end()
        block_end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(plan_text)
        block_text = plan_text[block_start:block_end]
        tasks[number] = _parse_task_block(number, block_text)
    return tasks


def check_seam_coverage(plan_text: str) -> list[str]:
    """One message per finding among the four mechanical checks (see
    module docstring). Empty list means every Dependencies edge is
    covered."""
    tasks = parse_tasks(plan_text)
    errors: list[str] = []
    for number in sorted(tasks):
        task = tasks[number]
        if not task.dep_edges:
            continue
        if not task.has_seam_field:
            errors.append(
                f"Error: Task {number} has Dependencies "
                f"{sorted(task.dep_edges)} but no 'Seam' field — every "
                f"task whose Dependencies is not 'none' must carry one "
                f"bullet per incoming edge."
            )
            continue
        for from_task in sorted(task.dep_edges):
            if from_task not in task.seam_by_from:
                errors.append(
                    f"Error: Task {number}'s 'Seam' field has no "
                    f"'from Task {from_task}' bullet for its Dependencies "
                    f"edge from Task {from_task}."
                )
        for from_task in sorted(task.seam_by_from):
            bullet = task.seam_by_from[from_task]
            if bullet.payload_none:
                continue
            missing = []
            if bullet.owner is None:
                missing.append("owner:")
            if bullet.probe is None:
                missing.append("probe:")
            if missing:
                errors.append(
                    f"Error: Task {number}'s 'Seam' bullet 'from Task "
                    f"{from_task}' is payload-bearing but missing "
                    f"{' and '.join(missing)}."
                )
                continue
            if bullet.probe not in task.acceptance_text:
                errors.append(
                    f"Error: Task {number}'s 'Seam' bullet 'from Task "
                    f"{from_task}' names probe {bullet.probe!r}, which does "
                    f"not appear in Task {number}'s own 'Acceptance' block."
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check that a writing-plans plan's 'Seam' fields cover "
                    "every incoming 'Dependencies' edge; exit 1 naming "
                    "every uncovered or malformed seam."
    )
    parser.add_argument("plan_path", help="path to the writing-plans plan file")
    args = parser.parse_args(argv)

    plan_path = Path(args.plan_path)
    try:
        if not plan_path.is_file():
            print(f"Error: plan file not found at {plan_path}.", file=sys.stderr)
            return 1
        plan_text = plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error: could not read plan file at {plan_path}: {exc}", file=sys.stderr)
        return 1

    tasks = parse_tasks(plan_text)
    dependents = [t for t in tasks.values() if t.dep_edges]
    if not dependents:
        print(
            f"No task in {plan_path} declares Dependencies other than "
            f"'none' — vacuously covered (nothing to check)."
        )
        return 0

    errors = check_seam_coverage(plan_text)
    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    print(
        f"Full seam coverage: every Dependencies edge in {plan_path} has a "
        f"matching 'Seam' bullet."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
