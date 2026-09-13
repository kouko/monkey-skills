"""Ticket claim and blocker mutations inside the caller-owned writer lock.

Shared revision, journal, and filesystem guards come from the explicit facade
dependency so existing fault-injection seams continue to exercise these writes.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING

import map_store

if TYPE_CHECKING:
    from map_transaction import StoreRevision, MutationResult


def _replace_frontmatter_field(
    transaction: ModuleType,
    text: str, field: str, value: str | None
) -> str:
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError as exc:
        raise transaction.CloseTransactionError("ticket has invalid frontmatter") from exc
    matches = [index for index in range(1, end) if lines[index].startswith(f"{field}:")]
    if len(matches) > 1:
        raise transaction.CloseTransactionError(f"ticket has duplicate {field!r} frontmatter")
    replacement = f"{field}: {value}" if value is not None else None
    if matches and replacement is None:
        lines.pop(matches[0])
    elif matches:
        assert replacement is not None
        lines[matches[0]] = replacement
    elif replacement is not None:
        lines.insert(end, replacement)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def _claim_ticket_locked(
    transaction: ModuleType,
    map_dir: Path,
    ticket_slug: str,
    *,
    owner: str,
    claimed_on: str,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Claim after the caller acquires the Map writer lock."""
    map_dir = Path(map_dir)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", ticket_slug):
        raise transaction.CloseTransactionError("ticket_slug is not a safe slug")
    if (
        not owner.strip()
        or "," in owner
        or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", claimed_on)
    ):
        raise transaction.CloseTransactionError("claim requires an owner and YYYY-MM-DD date")
    intent = {
        "version": 1,
        "kind": "claim",
        "ticket_slug": ticket_slug,
        "owner": owner.strip(),
        "claimed_on": claimed_on,
    }
    operation = transaction._operation_path(map_dir, operation_id)
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    operation_prepared = transaction._load_operation(operation, intent)
    if operation_prepared:
        ticket = map_store.read_ticket(ticket_path)
        desired = f"{owner.strip()}, {claimed_on}"
        if ticket.frontmatter.status == "claimed" and ticket.frontmatter.claim == desired:
            transaction._require_valid_store(map_dir)
            return transaction.MutationResult(False, True)
    transaction._require_revision(map_dir, expected_revision)
    try:
        ticket = map_store.require_ticket_mutable(map_dir, ticket_slug, "claim")
        code, message = map_store.validate(map_dir)
    except (map_store.MapStoreError, map_store.SchemaViolation) as exc:
        raise transaction.CloseTransactionError(str(exc)) from exc
    if code != 0:
        raise transaction.CloseTransactionError(f"cannot claim from broken Map: {message}")
    if ticket.frontmatter.status != "open":
        raise transaction.CloseTransactionError("ticket must be open before claim")
    statuses = {
        path.stem: map_store.read_ticket(path).frontmatter.status
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    unclosed = [
        slug for slug in ticket.frontmatter.blocked_by if statuses.get(slug) != "closed"
    ]
    if unclosed:
        raise transaction.CloseTransactionError("ticket is blocked by " + ", ".join(unclosed))
    original = ticket_path.read_bytes()
    updated = _replace_frontmatter_field(transaction, original.decode("utf-8"), "status", "claimed")
    updated = _replace_frontmatter_field(
        transaction,
        updated, "claim", f"{owner.strip()}, {claimed_on}"
    )
    if operation_prepared:
        transaction._assert_supported_filesystem(map_dir)
        transaction._require_revision(map_dir, expected_revision)
    else:
        transaction._prepare_mutation(map_dir, operation_id, intent, expected_revision)
        transaction._require_revision(map_dir, expected_revision)
    try:
        map_store.atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise transaction.CloseTransactionError(str(exc)) from exc
    transaction._require_valid_store(map_dir)
    return transaction.MutationResult(True, False)


def _update_blockers_locked(
    transaction: ModuleType,
    map_dir: Path,
    ticket_slug: str,
    blockers: list[str],
    *,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Replace blocker edges after the caller acquires the writer lock."""
    map_dir = Path(map_dir)
    intent = {
        "version": 1,
        "kind": "update-blockers",
        "ticket_slug": ticket_slug,
        "blockers": blockers,
    }
    operation = transaction._operation_path(map_dir, operation_id)
    ticket_path = map_dir / "tickets" / f"{ticket_slug}.md"
    desired_value = ", ".join(blockers)
    operation_prepared = transaction._load_operation(operation, intent)
    if operation_prepared:
        current = map_store.read_ticket(ticket_path)
        if current.frontmatter.blocked_by == blockers:
            transaction._require_valid_store(map_dir)
            return transaction.MutationResult(False, True)
    transaction._require_revision(map_dir, expected_revision)
    try:
        map_store.require_ticket_mutable(map_dir, ticket_slug, "edit")
    except (map_store.MapStoreError, map_store.SchemaViolation) as exc:
        raise transaction.CloseTransactionError(str(exc)) from exc
    graph = {
        path.stem: map_store.read_ticket(path).frontmatter.blocked_by
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    graph[ticket_slug] = blockers
    try:
        map_store._check_blocked_by(graph, map_dir / "tickets")
    except map_store.SchemaViolation as exc:
        raise transaction.CloseTransactionError(str(exc)) from exc
    statuses = {
        path.stem: map_store.read_ticket(path).frontmatter.status
        for path in sorted((map_dir / "tickets").glob("*.md"))
    }
    if statuses.get(ticket_slug) == "claimed":
        unclosed = [slug for slug in blockers if statuses.get(slug) != "closed"]
        if unclosed:
            raise transaction.CloseTransactionError(
                "claimed ticket requires closed blockers: " + ", ".join(unclosed)
            )
    original = ticket_path.read_bytes()
    updated = _replace_frontmatter_field(
        transaction,
        original.decode("utf-8"), "blocked-by", desired_value or None
    )
    if operation_prepared:
        transaction._assert_supported_filesystem(map_dir)
        transaction._require_revision(map_dir, expected_revision)
    else:
        transaction._prepare_mutation(map_dir, operation_id, intent, expected_revision)
        transaction._require_revision(map_dir, expected_revision)
    try:
        map_store.atomic_write(ticket_path, updated, expected=original)
    except (OSError, map_store.SchemaViolation) as exc:
        raise transaction.CloseTransactionError(str(exc)) from exc
    transaction._require_valid_store(map_dir)
    return transaction.MutationResult(True, False)
