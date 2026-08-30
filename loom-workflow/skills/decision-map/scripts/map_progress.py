#!/usr/bin/env python3
"""Resolve read-only delivery progress from Ticket to Brief to Plan."""

from __future__ import annotations

import argparse
import errno
import os
import re
import stat
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


def _raise_source_error(exc: OSError, label: str, relative: str) -> None:
    if exc.errno == errno.ELOOP:
        raise ProgressError(
            f"{label} path contains a symlink: {relative}"
        ) from exc
    raise ProgressUnavailable(f"cannot read {label} {relative}: {exc}") from exc


def _read_source(root: Path, path: Path, label: str) -> tuple[str, str]:
    relative = _relative(root, path, label)
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise ProgressUnavailable(
            "platform cannot safely read progress sources without O_NOFOLLOW"
        )
    root_fd = -1
    directory_fd = -1
    source_fd = -1
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        directory_fd = root_fd
        parts = Path(relative).parts
        for part in parts[:-1]:
            metadata = os.stat(part, dir_fd=directory_fd, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise ProgressError(f"{label} path contains a symlink: {relative}")
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=directory_fd,
            )
            if directory_fd != root_fd:
                os.close(directory_fd)
            directory_fd = next_fd
        metadata = os.stat(parts[-1], dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISLNK(metadata.st_mode):
            raise ProgressError(f"{label} path contains a symlink: {relative}")
        source_fd = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd
        )
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode):
            raise ProgressUnavailable(
                f"{label} is not a regular file: {relative}"
            )
        with os.fdopen(source_fd, "r", encoding="utf-8") as handle:
            source_fd = -1
            return relative, handle.read()
    except ProgressError:
        raise
    except OSError as exc:
        _raise_source_error(exc, label, relative)
    finally:
        if source_fd >= 0:
            os.close(source_fd)
        if directory_fd >= 0 and directory_fd != root_fd:
            os.close(directory_fd)
        if root_fd >= 0:
            os.close(root_fd)


def _ticket_fields(root: Path, ticket: Path) -> dict[str, str]:
    try:
        relative, text = _read_source(root, ticket, "Ticket")
        fields, _ = map_store.parse_frontmatter(text)
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
        _, text = _read_source(root, candidate, "Plan")
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
    fields = _ticket_fields(root, ticket)
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
    current = root
    for part in ("docs", "loom", "maps"):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            return [], []
        except OSError as exc:
            raise ProgressUnavailable(f"cannot inspect Maps path: {exc}") from exc
        if stat.S_ISLNK(mode):
            raise ProgressError(f"Maps path contains a symlink: {_relative(root, current, 'Maps')}")
        if not stat.S_ISDIR(mode):
            raise ProgressUnavailable(f"Maps path is not a directory: {current}")
    live: list[Path] = []
    broken: list[Path] = []
    try:
        entries = sorted(os.scandir(maps_root), key=lambda entry: entry.name)
    except OSError as exc:
        raise ProgressUnavailable(f"cannot enumerate Maps: {exc}") from exc
    for entry in entries:
        candidate = Path(entry.path)
        if entry.is_symlink():
            raise ProgressError(
                f"Map path contains a symlink: {_relative(root, candidate, 'Map')}"
            )
        if not entry.is_dir(follow_symlinks=False):
            continue
        map_path = candidate / "MAP.md"
        if not map_path.exists():
            continue
        try:
            _, text = _read_source(root, map_path, "Map")
            doc = map_store.parse_map_document(text, map_path)
        except (ProgressUnavailable, map_store.SchemaViolation):
            broken.append(candidate)
            continue
        if doc.frontmatter.state not in map_store.LIVE_MAP_STATES:
            continue
        result = map_store.is_live_map(candidate, repo_root=root)
        if result is map_store.LiveMapResult.LIVE:
            live.append(candidate)
        else:
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


def _select_reentry_map(
    root: Path, map_id: str | None
) -> tuple[Path | None, ReentryReport | None]:
    """Select one live Map or return the terminal selection report."""
    live, broken = _live_maps(root)
    if map_id is not None:
        selected = root / "docs" / "loom" / "maps" / map_id
        if selected in broken:
            return None, ReentryReport(
                "broken",
                f"docs/loom/maps/{map_id}/MAP.md",
                "repair the Map validation error before resuming",
                map_id=map_id,
            )
        live = [path for path in live if path.name == map_id]
        if not live:
            return None, ReentryReport(
                "absent",
                "docs/loom/maps",
                "chart a new Outcome Map",
            )
    elif broken:
        selected = broken[0]
        return None, ReentryReport(
            "broken",
            f"docs/loom/maps/{selected.name}/MAP.md",
            "repair the Map validation error before resuming",
            map_id=selected.name,
        )
    if not live:
        return None, ReentryReport(
            "absent", "docs/loom/maps", "chart a new Outcome Map"
        )
    if len(live) > 1:
        return None, ReentryReport(
            "ambiguous-live",
            "docs/loom/maps",
            "select one live Outcome Map by map-id",
        )
    return live[0], None


def _read_frontier_tickets(
    root: Path, map_dir: Path
) -> list[map_store.TicketDocument]:
    tickets_dir = map_dir / "tickets"
    if not tickets_dir.exists():
        return []
    if tickets_dir.is_symlink() or not tickets_dir.is_dir():
        raise ProgressError("Ticket directory is not a contained regular directory")
    tickets: list[map_store.TicketDocument] = []
    try:
        candidates = sorted(tickets_dir.glob("*.md"))
    except OSError as exc:
        raise ProgressUnavailable(f"cannot enumerate Tickets: {exc}") from exc
    for path in candidates:
        _, text = _read_source(root, path, "Ticket")
        try:
            tickets.append(map_store.parse_ticket_document(text, path))
        except map_store.SchemaViolation as exc:
            raise ProgressError(f"Ticket {path.name} is invalid: {exc}") from exc
    return tickets


def _blocked_reentry(
    map_dir: Path,
    tickets: list[map_store.TicketDocument],
    statuses: dict[str, str],
) -> ReentryReport | None:
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
            blocker
            for ticket in blocked_open
            for blocker in ticket.frontmatter.blocked_by
            if statuses.get(blocker) != "closed"
        )
        return ReentryReport(
            "blocked",
            ", ".join(
                f"docs/loom/maps/{map_dir.name}/tickets/{slug}.md"
                for slug in owners
            ),
            "resolve blockers or resume their current owners",
            map_id=map_dir.name,
        )
    return None


def _owned_or_frontier_reentry(
    root: Path,
    map_dir: Path,
    tickets: list[map_store.TicketDocument],
    statuses: dict[str, str],
) -> ReentryReport | None:
    claimed = [ticket for ticket in tickets if ticket.frontmatter.status == "claimed"]
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
        and all(
            statuses.get(blocker) == "closed"
            for blocker in ticket.frontmatter.blocked_by
        )
    ]
    if not frontier:
        return None
    ticket = frontier[0]
    relative = ticket.path.relative_to(root).as_posix()
    return ReentryReport(
        "live",
        relative,
        f"claim frontier ticket {ticket.path.stem}",
        map_id=map_dir.name,
        ticket=relative,
    )


def _ticket_frontier_reentry(
    root: Path, map_dir: Path
) -> ReentryReport | None:
    tickets = _read_frontier_tickets(root, map_dir)
    statuses = {ticket.path.stem: ticket.frontmatter.status for ticket in tickets}
    return _blocked_reentry(map_dir, tickets, statuses) or _owned_or_frontier_reentry(
        root, map_dir, tickets, statuses
    )


def _acceptance_reentry(
    doc: map_store.MapDocument, map_owner: str
) -> ReentryReport:
    open_da = [
        criterion
        for criterion in doc.destination_acceptance
        if criterion.state == "open"
    ]
    if open_da:
        return ReentryReport(
            "da-gap",
            map_owner + "#Destination",
            f"satisfy Destination acceptance {open_da[0].id}",
            map_id=doc.frontmatter.map_id,
        )
    return ReentryReport(
        "live",
        map_owner,
        "assess Map clear or re-chart the next unknown",
        map_id=doc.frontmatter.map_id,
    )


def assess_reentry(repo_root: Path, map_id: str | None = None) -> ReentryReport:
    """Report one Map's authoritative re-entry owner without writing sources."""
    root = Path(os.path.abspath(repo_root))
    map_dir, selection = _select_reentry_map(root, map_id)
    if selection is not None:
        return selection
    assert map_dir is not None
    _, map_text = _read_source(root, map_dir / "MAP.md", "Map")
    try:
        doc = map_store.parse_map_document(map_text, map_dir / "MAP.md")
    except map_store.SchemaViolation as exc:
        raise ProgressError(f"Map became invalid during re-entry: {exc}") from exc
    map_owner = f"docs/loom/maps/{map_dir.name}/MAP.md"
    if doc.frontmatter.state == "charting":
        return ReentryReport(
            "live",
            map_owner,
            "ratify the Destination and activate the Map",
            map_id=map_dir.name,
        )
    ticket_report = _ticket_frontier_reentry(root, map_dir)
    return ticket_report or _acceptance_reentry(doc, map_owner)


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
            _, plan_text = _read_source(absolute_root, target, "Plan")
            map_id, part, state = derive_progress(plan_text)
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
