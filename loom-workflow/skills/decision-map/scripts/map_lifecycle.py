#!/usr/bin/env python3
"""Stable-read-set retirement orchestration without transaction imports."""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path

import delivery_binding
import map_lock
import map_store


class LifecycleError(RuntimeError):
    """A Map retirement or archive transition refused safely."""


def _before_stability_check() -> None:
    """Test seam after validation and before stable-read-set comparison."""


def _before_transition() -> None:
    """Test seam after readiness and before the terminal transition."""


def _before_state_replace() -> None:
    """Test seam immediately before the MAP compare-and-swap."""


def _after_state_replace() -> None:
    """Test seam before post-write validation and possible rollback."""


def _atomic_write(path: Path, text: str, *, expected: bytes | None = None) -> None:
    try:
        map_store._atomic_write(path, text, expected=expected)
    except map_store.SchemaViolation as exc:
        raise LifecycleError(str(exc)) from exc


def _store_snapshot(map_dir: Path) -> dict[str, bytes]:
    snapshot: dict[str, bytes] = {}
    for root, directories, files in os.walk(map_dir, followlinks=False):
        root_path = Path(root)
        for name in directories:
            candidate = root_path / name
            if stat.S_ISLNK(candidate.lstat().st_mode):
                raise LifecycleError(f"retirement read set contains a symlink: {candidate}")
        for name in files:
            candidate = root_path / name
            if not stat.S_ISREG(candidate.lstat().st_mode):
                raise LifecycleError(
                    f"retirement read set contains a non-regular file: {candidate}"
                )
            snapshot[candidate.relative_to(map_dir).as_posix()] = candidate.read_bytes()
    return snapshot


def _retirement_snapshot(map_dir: Path, repo_root: Path) -> dict[str, bytes]:
    snapshot = {
        str((map_dir / relative).resolve(strict=False)): content
        for relative, content in _store_snapshot(map_dir).items()
    }
    for ticket_path in sorted((map_dir / "tickets").glob("*.md")):
        try:
            fields, _ = map_store.parse_frontmatter(ticket_path.read_text(encoding="utf-8"))
        except (OSError, map_store.SchemaViolation) as exc:
            raise LifecycleError(f"cannot snapshot ticket binding: {exc}") from exc
        brief = fields.get("brief")
        if brief is None:
            continue
        brief_path = repo_root / brief
        try:
            map_store._assert_no_symlink_components(brief_path)
            map_store._assert_contained(repo_root, brief_path)
            snapshot[str(brief_path.resolve(strict=True))] = brief_path.read_bytes()
        except (OSError, map_store.SchemaViolation) as exc:
            raise LifecycleError(f"cannot snapshot reciprocal Brief: {exc}") from exc
    return snapshot


def _routed_ticket_text(route: dict[str, object]) -> str:
    return (
        "---\n"
        f"type: {route['ticket_type']}\n"
        "status: open\nclaim: null\ngraduated-from: null\n---\n\n"
        f"{route['text']}\n"
    )


def _operation_is_complete(map_dir: Path, journal: Path) -> bool:
    try:
        intent = json.loads(journal.read_text(encoding="utf-8"))
        if intent.get("kind") == "claim":
            ticket = map_store.read_ticket(
                map_dir / "tickets" / f"{intent['ticket_slug']}.md"
            )
            return (
                intent.get("version") == 1
                and ticket.frontmatter.status == "claimed"
                and ticket.frontmatter.claim
                == f"{intent['owner']}, {intent['claimed_on']}"
            )
        if intent.get("kind") == "update-blockers":
            ticket = map_store.read_ticket(
                map_dir / "tickets" / f"{intent['ticket_slug']}.md"
            )
            return (
                intent.get("version") == 1
                and ticket.frontmatter.blocked_by == intent.get("blockers")
            )
        slug, gist = intent["ticket_slug"], intent["gist"]
        resolution, routes = intent["resolution"], intent["routes"]
        if (
            intent.get("version") != 1
            or intent.get("prepared") is not True
            or not all(isinstance(value, str) for value in (slug, gist, resolution))
            or not isinstance(routes, list)
            or journal.name != f"close-{slug}.json"
        ):
            return False
        ticket = map_store.read_ticket(map_dir / "tickets" / f"{slug}.md")
        if ticket.frontmatter.status != "closed" or (ticket.resolution or "").strip() != resolution.strip():
            return False
        map_text = (map_dir / "MAP.md").read_text(encoding="utf-8")
        if f"- {gist.strip()} (tickets/{slug}.md)" not in map_text:
            return False
        return all(_route_is_complete(map_dir, map_text, route) for route in routes)
    except (KeyError, OSError, json.JSONDecodeError, map_store.MapStoreError, map_store.SchemaViolation):
        return False


def _route_is_complete(
    map_dir: Path, map_text: str, route: object
) -> bool:
    if not isinstance(route, dict) or not isinstance(route.get("text"), str):
        return False
    destination, text = route.get("destination"), route["text"]
    if destination == "fog":
        return f"- {route.get('fog_id')}: {text}" in map_text
    if destination == "out-of-scope":
        return f"- {text}" in map_text
    if destination == "ticket":
        path = map_dir / "tickets" / f"{route.get('ticket_slug')}.md"
        return path.is_file() and path.read_text(encoding="utf-8") == _routed_ticket_text(route)
    return False


def _validate_retirement_snapshot(map_dir: Path, repo_root: Path) -> None:
    import check_map_links

    transaction_dir = map_dir / ".transactions"
    if transaction_dir.exists():
        incomplete = [
            path.name
            for path in sorted(transaction_dir.iterdir())
            if path.name != ".map.lock"
            if not path.is_file() or not _operation_is_complete(map_dir, path)
        ]
        if incomplete:
            raise LifecycleError(
                "retirement refuses incomplete recoverable operation(s) "
                + ", ".join(incomplete)
                + "; repair them first"
            )
    code, message = map_store.validate(map_dir, repo_root=repo_root)
    if code != 0:
        raise LifecycleError(f"retirement refuses broken Map invariants: {message}")
    link_code, link_message = check_map_links.check_links(map_dir)
    if link_code != 0:
        raise LifecycleError(f"retirement refuses broken gist relationships: {link_message}")
    _validate_ticket_history(map_dir, repo_root)


def _validate_ticket_history(map_dir: Path, repo_root: Path) -> None:
    doc = map_store.read_map(map_dir)
    fog_ids = {entry.id for entry in doc.fog_entries}
    graduated: dict[str, list[str]] = {}
    closed_links: dict[str, int] = {}
    for decision in doc.decisions:
        closed_links[decision.ticket_link] = closed_links.get(decision.ticket_link, 0) + 1
    for ticket_path in sorted((map_dir / "tickets").glob("*.md")):
        ticket = map_store.read_ticket(ticket_path)
        if ticket.frontmatter.graduated_from:
            graduated.setdefault(ticket.frontmatter.graduated_from, []).append(ticket_path.name)
        if ticket.frontmatter.status == "closed":
            link = f"tickets/{ticket_path.name}"
            if closed_links.get(link, 0) != 1:
                raise LifecycleError(
                    f"retirement requires exactly one gist for closed ticket {ticket_path.name}"
                )
        if ticket.frontmatter.type == "delivery":
            code, message = delivery_binding.validate(ticket_path, repo_root=repo_root)
            if code != 0:
                raise LifecycleError(f"retirement refuses broken delivery binding: {message}")
    overlap = sorted(fog_ids.intersection(graduated))
    if overlap:
        raise LifecycleError("retirement refuses partial fog graduation for " + ", ".join(overlap))
    duplicates = sorted(key for key, owners in graduated.items() if len(owners) != 1)
    if duplicates:
        raise LifecycleError("retirement refuses duplicated fog graduation for " + ", ".join(duplicates))


@dataclass(frozen=True)
class RetirementReadiness:
    map_dir: Path
    repo_root: Path
    snapshot: tuple[tuple[str, bytes], ...]


def prepare_retirement(map_dir: Path, repo_root: Path) -> RetirementReadiness:
    map_dir, repo_root = Path(map_dir), Path(repo_root)
    for path in (repo_root, map_dir, map_dir / "MAP.md", map_dir / "tickets"):
        map_store._assert_no_symlink_components(path)
        try:
            path.resolve(strict=False).relative_to(repo_root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise LifecycleError(f"retirement path escapes repository: {path}") from exc
    initial = _retirement_snapshot(map_dir, repo_root)
    _validate_retirement_snapshot(map_dir, repo_root)
    _before_stability_check()
    if _retirement_snapshot(map_dir, repo_root) != initial:
        raise LifecycleError("retirement requires one stable snapshot; a read-set file changed")
    return RetirementReadiness(map_dir, repo_root, tuple(sorted(initial.items())))


def _commit_retirement(
    readiness: RetirementReadiness,
    *,
    ratified_by: str | None,
    ratified_on: str | None,
    reason: str | None,
) -> None:
    map_dir, repo_root = readiness.map_dir, readiness.repo_root
    _before_transition()
    doc = map_store.read_map(map_dir)
    expected = dict(readiness.snapshot)
    if _retirement_snapshot(map_dir, repo_root) != expected:
        raise LifecycleError("retirement requires one stable snapshot at the transition boundary")
    map_path = map_dir / "MAP.md"
    original = map_path.read_text(encoding="utf-8")
    try:
        candidate = (
            map_store.archive_candidate(original)
            if doc.frontmatter.state == "clear"
            else map_store.retirement_candidate(
                original,
                current_state=doc.frontmatter.state,
                ratified_by=ratified_by or "",
                ratified_on=ratified_on or "",
                reason=reason or "",
            )
        )
    except map_store.SchemaViolation as exc:
        raise LifecycleError(str(exc)) from exc
    _before_state_replace()
    _atomic_write(map_path, candidate, expected=original.encode("utf-8"))
    try:
        _after_state_replace()
        committed = dict(readiness.snapshot)
        committed[str(map_path.resolve(strict=True))] = candidate.encode("utf-8")
        if _retirement_snapshot(map_dir, repo_root) != committed:
            raise LifecycleError("retirement read set changed during state replacement")
        _validate_retirement_snapshot(map_dir, repo_root)
    except Exception as exc:
        _rollback_retirement(map_dir, map_path, original, candidate, exc)


def _rollback_retirement(
    map_dir: Path,
    map_path: Path,
    original: str,
    candidate: str,
    cause: Exception,
) -> None:
    try:
        _atomic_write(map_path, original, expected=candidate.encode("utf-8"))
    except Exception as rollback_exc:
        evidence = {
            "action": "recovery-required",
            "cause": str(cause),
            "map_path": "MAP.md",
            "rollback_error": str(rollback_exc),
            "status": "BROKEN",
        }
        evidence_path = map_dir / ".transactions" / "retirement-recovery.json"
        try:
            map_store._atomic_write(
                evidence_path, json.dumps(evidence, indent=2, sort_keys=True) + "\n"
            )
            suffix = f"; evidence: {evidence_path}"
        except Exception as evidence_exc:
            suffix = f"; durable evidence unavailable: {evidence_exc}"
        raise LifecycleError(
            "BROKEN recovery-required: archive state could not be rolled back" + suffix
        ) from rollback_exc
    if isinstance(cause, LifecycleError):
        raise cause
    raise LifecycleError(
        f"archive post-write validation failed; MAP state restored: {cause}"
    ) from cause


def archive_map_transition(map_dir: Path, *, repo_root: Path) -> None:
    try:
        with map_lock.map_writer_lock(map_dir):
            readiness = prepare_retirement(map_dir, repo_root)
            if map_store.read_map(map_dir).frontmatter.state != "clear":
                raise LifecycleError("archive transition requires a clear schema-v3 Map")
            _commit_retirement(
                readiness, ratified_by=None, ratified_on=None, reason=None
            )
    except LifecycleError:
        raise
    except (
        map_lock.MapLockError,
        map_store.MapStoreError,
        map_store.SchemaViolation,
        OSError,
    ) as exc:
        raise LifecycleError(str(exc)) from exc


def retire_map(
    map_dir: Path,
    *,
    ratified_by: str,
    ratified_on: str,
    reason: str,
    repo_root: Path,
) -> None:
    try:
        with map_lock.map_writer_lock(map_dir):
            readiness = prepare_retirement(map_dir, repo_root)
            _commit_retirement(
                readiness,
                ratified_by=ratified_by,
                ratified_on=ratified_on,
                reason=reason,
            )
    except LifecycleError:
        raise
    except (
        map_lock.MapLockError,
        map_store.MapStoreError,
        map_store.SchemaViolation,
        OSError,
    ) as exc:
        raise LifecycleError(str(exc)) from exc
