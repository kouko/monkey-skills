#!/usr/bin/env python3
"""Resolve read-only delivery progress from Ticket to Brief to Plan."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import delivery_binding
import map_store


_SOURCE_BRIEF = re.compile(r"^\*\*Source brief\*\*:\s*(?P<brief>\S+)\s*$", re.MULTILINE)
_STAGE = re.compile(r"^Stage:\s*(?P<stage>\S.*?)\s*$", re.MULTILINE)
_NOTES_HEADING = re.compile(r"^## Notes\s*$", re.MULTILINE)
_NEXT_HEADING = re.compile(r"^## ", re.MULTILINE)
_BINDING = re.compile(
    r"^Map part:\s*(?P<map_id>[^/\n]+?)\s*/\s*Part:\s*(?P<part>[^\n]+?)\s*$",
    re.MULTILINE,
)
_TASK_HEADING = re.compile(r"^## Task \d+ — .+?$", re.MULTILINE)
_STATUS = re.compile(
    r"^- \*{0,2}Status\*{0,2}:\s*"
    r"(?P<status>done\([^()\s]+\)|claimed\(@[^()\s]+\)|pending|blocked)\s*$",
    re.MULTILINE,
)


class ProgressError(Exception):
    """Structural delivery-arc error — exit 2."""


class ProgressUnavailable(Exception):
    """Unreadable delivery source — exit 1."""


def _notes_section(text: str) -> str:
    match = _NOTES_HEADING.search(text)
    if match is None:
        raise ProgressError("plan has no '## Notes' section")
    next_heading = _NEXT_HEADING.search(text, match.end())
    return text[match.end() : next_heading.start() if next_heading else len(text)]


def derive_progress(text: str) -> tuple[str, str, str]:
    """Return legacy (map_id, part, ledger state) for one plan binding."""
    matches = list(_BINDING.finditer(_notes_section(text)))
    if len(matches) != 1:
        raise ProgressError("plan Notes must contain exactly one 'Map part:' delivery binding")
    task_matches = list(_TASK_HEADING.finditer(text))
    if not task_matches:
        raise ProgressError("plan has no task headings")
    states: list[str] = []
    for task in task_matches:
        next_heading = _NEXT_HEADING.search(text, task.end())
        block = text[task.end() : next_heading.start() if next_heading else len(text)]
        status = _STATUS.search(block)
        if status is None:
            raise ProgressError("plan task has no recognized '- Status:' line")
        states.append(status.group("status"))
    if "blocked" in states:
        return matches[0].group("map_id").strip(), matches[0].group("part").strip(), "blocked"
    if any(state.startswith("claimed(") for state in states):
        state = "claimed"
    elif "pending" in states:
        state = "pending"
    else:
        state = "done"
    return matches[0].group("map_id").strip(), matches[0].group("part").strip(), state


def _relative(root: Path, path: Path, label: str) -> str:
    try:
        return Path(os.path.abspath(path)).relative_to(root).as_posix()
    except ValueError as exc:
        raise ProgressError(f"{label} escapes repository: {path}") from exc


def _ticket_fields(ticket: Path) -> dict[str, str]:
    try:
        fields, _ = map_store.parse_frontmatter(ticket.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProgressUnavailable(f"cannot read ticket {ticket}: {exc}") from exc
    except map_store.SchemaViolation as exc:
        raise ProgressError(f"ticket has invalid frontmatter: {exc}") from exc
    return fields


def _sole_plan(root: Path, brief: str) -> tuple[str, str] | None:
    plans_dir = root / "docs" / "loom" / "plans"
    if not plans_dir.exists():
        return None
    if not plans_dir.is_dir():
        raise ProgressUnavailable(f"plans directory is not a directory: {plans_dir}")
    matches: list[tuple[str, str]] = []
    try:
        candidates = sorted(plans_dir.rglob("*.md"))
    except OSError as exc:
        raise ProgressUnavailable(f"cannot enumerate plans directory {plans_dir}: {exc}") from exc
    for candidate in candidates:
        if candidate.is_symlink():
            raise ProgressError(f"Plan path contains a symlink: {_relative(root, candidate, 'Plan')}")
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProgressUnavailable(f"cannot read Plan {candidate}: {exc}") from exc
        source = _SOURCE_BRIEF.search(text)
        if source is not None and source.group("brief") == brief:
            matches.append((_relative(root, candidate, "Plan"), text))
    if len(matches) > 1:
        raise ProgressError(
            f"delivery Brief {brief} has multiple Plans: "
            + ", ".join(path for path, _ in matches)
        )
    return matches[0] if matches else None


def _plan_phase(text: str) -> str:
    stage = _STAGE.search(text)
    if stage is None:
        raise ProgressError("Plan has no 'Stage:' header line")
    task_matches = list(_TASK_HEADING.finditer(text))
    if not task_matches:
        raise ProgressError("Plan has no task headings")
    statuses: list[str] = []
    for task in task_matches:
        next_heading = _TASK_HEADING.search(text, task.end())
        block = text[task.end() : next_heading.start() if next_heading else len(text)]
        status = _STATUS.search(block)
        if status is None:
            raise ProgressError("Plan task has no recognized '- Status:' line")
        statuses.append(status.group("status"))
    if "blocked" in statuses:
        return "repair-required"
    value = stage.group("stage")
    if value == "planning":
        return "planning"
    if value.startswith("sdd:"):
        return "implementing"
    if value.startswith("review:"):
        return "reviewing"
    if value == "finishing":
        return "finishing"
    raise ProgressError(f"Plan has unsupported Stage for delivery progress: {value!r}")


def resolve_progress(ticket_path: Path, repo_root: Path | None = None) -> tuple[str, str | None, str | None, str]:
    """Return (ticket, brief, plan, derived phase), without writing sources."""
    root = Path(os.path.abspath(repo_root if repo_root is not None else map_store.resolve_repo_root(None, ticket_path.parent)))
    ticket = Path(os.path.abspath(ticket_path))
    ticket_relative = _relative(root, ticket, "Ticket")
    code, message = delivery_binding.validate(ticket, repo_root=root)
    if code == 1:
        raise ProgressUnavailable(message)
    if code == 2:
        raise ProgressError(message)
    fields = _ticket_fields(ticket)
    if fields.get("type") != "delivery":
        raise ProgressError("progress is available only for delivery tickets")
    brief = fields.get("brief")
    if brief is None:
        if fields.get("status") == "closed":
            raise ProgressError("closed delivery ticket has no Brief binding")
        return ticket_relative, None, None, "unbriefed"
    plan = _sole_plan(root, brief)
    if plan is None:
        if fields.get("status") == "closed":
            raise ProgressError("closed delivery ticket has no Plan")
        return ticket_relative, brief, None, "briefed"
    plan_relative, plan_text = plan
    if fields.get("status") == "closed":
        return ticket_relative, brief, plan_relative, "delivered"
    return ticket_relative, brief, plan_relative, _plan_phase(plan_text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve a delivery Ticket's read-only progress.")
    parser.add_argument("target", help="delivery Ticket path")
    parser.add_argument("--repo-root", help="repository root")
    args = parser.parse_args(argv)
    target = Path(args.target)
    root = Path(args.repo_root) if args.repo_root else map_store.resolve_repo_root(None, target.parent)
    try:
        relative = _relative(Path(os.path.abspath(root)), target, "target")
        parts = Path(relative).parts
        if target.is_symlink():
            raise ProgressError(f"target path contains a symlink: {relative}")
        if len(parts) == 6 and parts[:3] == ("docs", "loom", "maps") and parts[4] == "tickets":
            ticket, brief, plan, phase = resolve_progress(target, root)
            print(f"ticket: {ticket}")
            if brief is not None:
                print(f"brief: {brief}")
            if plan is not None:
                print(f"plan: {plan}")
            print(f"phase: {phase}")
            return 0
        if len(parts) >= 4 and parts[:3] == ("docs", "loom", "plans"):
            try:
                text = target.read_text(encoding="utf-8")
            except OSError as exc:
                raise ProgressUnavailable(f"cannot read {target}: {exc}") from exc
            map_id, part, state = derive_progress(text)
            print(f"map delivery-progress: {map_id} / {part}")
            print(f"plan: {target.name}")
            print(f"state: {state}")
            return 0
        raise ProgressError("target must be a delivery Ticket or a plan under docs/loom/plans")
    except ProgressUnavailable as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ProgressError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
