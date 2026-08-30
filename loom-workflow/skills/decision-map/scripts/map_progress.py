#!/usr/bin/env python3
"""Resolve read-only delivery progress from Ticket to Brief to Plan."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
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
_LEGACY_STATUS = re.compile(
    r"^- \*{0,2}Status\*{0,2}:\s*"
    r"(?P<status>done\([^()\s]+\)|claimed\(@[^()\s]+\)|pending|blocked"
    r"(?:\([^()\n]*\))?)\s*$",
    re.MULTILINE,
)


class ProgressError(Exception):
    """Structural delivery-arc error — exit 2."""


class ProgressUnavailable(Exception):
    """Unreadable delivery source — exit 1."""


@dataclass(frozen=True)
class ReentryReport:
    state: str
    owner: str
    next_cta: str
    map_id: str | None = None
    ticket: str | None = None
    phase: str | None = None


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
        status = _LEGACY_STATUS.search(block)
        if status is None:
            raise ProgressError("plan task has no recognized '- Status:' line")
        states.append(status.group("status"))
    if any(state.startswith("blocked") for state in states):
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
    current = root
    for part in ("docs", "loom", "plans"):
        current = current / part
        if current.is_symlink():
            raise ProgressError(f"plans path contains a symlink component: {_relative(root, current, 'plans')}")
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
        relative_candidate = candidate.relative_to(plans_dir)
        component = plans_dir
        if candidate.is_symlink() or any(
            (component := component / part).is_symlink()
            for part in relative_candidate.parts
        ):
            raise ProgressError(f"Plan path contains a symlink: {_relative(root, candidate, 'Plan')}")
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            raise ProgressUnavailable(f"cannot read Plan {candidate}: {exc}") from exc
        source_lines = [line for line in text.splitlines() if line.startswith("**Source brief")]
        source_matches = [match for match in _SOURCE_BRIEF.finditer(text)]
        matching = [match for match in source_matches if match.group("brief") == brief]
        if not matching:
            # Legacy plans with no Source brief (and plans bound to a
            # different Brief) are not candidates for this delivery arc.
            continue
        if len(source_lines) != 1 or len(source_matches) != 1:
            raise ProgressError(
                f"Plan {_relative(root, candidate, 'Plan')} must contain exactly one '**Source brief**:' declaration"
            )
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


def _live_maps(root: Path) -> tuple[list[Path], list[Path]]:
    maps_root = root / "docs" / "loom" / "maps"
    if not maps_root.exists():
        return [], []
    if not maps_root.is_dir() or maps_root.is_symlink():
        return [], [maps_root]
    live: list[Path] = []
    broken: list[Path] = []
    for candidate in sorted(path for path in maps_root.iterdir() if path.is_dir()):
        result = map_store.is_live_map(candidate, repo_root=root)
        if result is map_store.LiveMapResult.LIVE:
            live.append(candidate)
        elif (candidate / "MAP.md").exists():
            try:
                doc = map_store.read_map(candidate)
            except (map_store.MapStoreError, map_store.SchemaViolation):
                broken.append(candidate)
            else:
                if doc.frontmatter.state in map_store.LIVE_MAP_STATES:
                    broken.append(candidate)
    return live, broken


def _delivery_reentry(
    root: Path, map_id: str, ticket_path: Path
) -> ReentryReport:
    ticket, brief, plan, phase = resolve_progress(ticket_path, root)
    ctas = {
        "unbriefed": (ticket, "start delivery and bind its Brief"),
        "briefed": (brief or ticket, "create the one owning Plan from the Brief"),
        "planning": (plan or brief or ticket, "finish planning in the owning Plan"),
        "implementing": (plan or ticket, "resume implementation in the owning Plan"),
        "reviewing": (plan or ticket, "resume whole-branch review in the owning Plan"),
        "finishing": (plan or ticket, "resume finishing and exact-head checks"),
        "repair-required": (plan or ticket, "repair the owning Plan and re-verify"),
        "delivered": (ticket, "re-enter charting from the closed delivery gist"),
    }
    owner, cta = ctas[phase]
    return ReentryReport(
        "claimed" if phase != "delivered" else "live",
        owner or ticket,
        cta,
        map_id=map_id,
        ticket=ticket,
        phase=phase,
    )


def assess_reentry(repo_root: Path, map_id: str | None = None) -> ReentryReport:
    """Report one Map's authoritative re-entry owner without writing sources."""
    root = Path(os.path.abspath(repo_root))
    live, broken = _live_maps(root)
    if map_id is not None:
        selected = root / "docs" / "loom" / "maps" / map_id
        if selected in broken:
            return ReentryReport(
                "broken",
                f"docs/loom/maps/{map_id}/MAP.md",
                "repair the Map validation error before resuming",
                map_id=map_id,
            )
        live = [path for path in live if path.name == map_id]
        if not live:
            return ReentryReport(
                "absent",
                "docs/loom/maps",
                "chart a new Outcome Map",
            )
    elif broken:
        selected = broken[0]
        return ReentryReport(
            "broken",
            f"docs/loom/maps/{selected.name}/MAP.md",
            "repair the Map validation error before resuming",
            map_id=selected.name,
        )
    if not live:
        return ReentryReport(
            "absent", "docs/loom/maps", "chart a new Outcome Map"
        )
    if len(live) > 1:
        return ReentryReport(
            "ambiguous-live",
            "docs/loom/maps",
            "select one live Outcome Map by map-id",
        )
    map_dir = live[0]
    doc = map_store.read_map(map_dir)
    map_owner = f"docs/loom/maps/{map_dir.name}/MAP.md"
    if doc.frontmatter.state == "charting":
        return ReentryReport(
            "live",
            map_owner,
            "ratify the Destination and activate the Map",
            map_id=map_dir.name,
        )
    tickets = [
        map_store.read_ticket(path)
        for path in sorted((map_dir / "tickets").glob("*.md"))
    ]
    statuses = {ticket.path.stem: ticket.frontmatter.status for ticket in tickets}
    claimed = [ticket for ticket in tickets if ticket.frontmatter.status == "claimed"]
    blocked_open = [
        ticket
        for ticket in tickets
        if ticket.frontmatter.status == "open"
        and any(
            statuses.get(blocker) != "closed"
            for blocker in ticket.frontmatter.blocked_by
        )
    ]
    if blocked_open:
        owners = sorted(
            {
                blocker
                for ticket in blocked_open
                for blocker in ticket.frontmatter.blocked_by
                if statuses.get(blocker) != "closed"
            }
        )
        return ReentryReport(
            "blocked",
            ", ".join(f"docs/loom/maps/{map_dir.name}/tickets/{slug}.md" for slug in owners),
            "resolve blockers or resume their current owners",
            map_id=map_dir.name,
        )
    if claimed:
        ticket = claimed[0]
        if ticket.frontmatter.type == "delivery":
            return _delivery_reentry(root, map_dir.name, ticket.path)
        relative = ticket.path.relative_to(root).as_posix()
        return ReentryReport(
            "claimed",
            relative,
            f"resume {ticket.frontmatter.type} ticket {ticket.path.stem}",
            map_id=map_dir.name,
            ticket=relative,
        )
    frontier = [
        ticket
        for ticket in tickets
        if ticket.frontmatter.status == "open"
        and all(statuses.get(blocker) == "closed" for blocker in ticket.frontmatter.blocked_by)
    ]
    if frontier:
        ticket = frontier[0]
        relative = ticket.path.relative_to(root).as_posix()
        return ReentryReport(
            "live",
            relative,
            f"claim frontier ticket {ticket.path.stem}",
            map_id=map_dir.name,
            ticket=relative,
        )
    open_da = [
        criterion for criterion in doc.destination_acceptance if criterion.state == "open"
    ]
    if open_da:
        return ReentryReport(
            "da-gap",
            map_owner + "#Destination",
            f"satisfy Destination acceptance {open_da[0].id}",
            map_id=map_dir.name,
        )
    return ReentryReport(
        "live",
        map_owner,
        "assess Map clear or re-chart the next unknown",
        map_id=map_dir.name,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve a delivery Ticket's read-only progress.")
    parser.add_argument("target", help="repository root, delivery Ticket, or Plan path")
    parser.add_argument("--repo-root", help="repository root")
    parser.add_argument("--map-id", help="select one live Outcome Map for re-entry")
    args = parser.parse_args(argv)
    target = Path(args.target)
    root = Path(args.repo_root) if args.repo_root else map_store.resolve_repo_root(None, target.parent)
    try:
        absolute_root = Path(os.path.abspath(root))
        if Path(os.path.abspath(target)) == absolute_root:
            report = assess_reentry(absolute_root, map_id=args.map_id)
            print(f"state: {report.state}")
            if report.map_id is not None:
                print(f"map-id: {report.map_id}")
            print(f"owner: {report.owner}")
            if report.ticket is not None:
                print(f"ticket: {report.ticket}")
            if report.phase is not None:
                print(f"phase: {report.phase}")
            print(f"next-cta: {report.next_cta}")
            return 0
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
