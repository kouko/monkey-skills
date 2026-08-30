#!/usr/bin/env python3
"""Conservative recovery for observably stale schema-v3 ticket claims."""

from __future__ import annotations

import re
import subprocess
from datetime import date, datetime
from pathlib import Path

import map_store


class ClaimRecoveryError(ValueError):
    """A reclaim request lacks safe, unambiguous staleness evidence."""


_CLAIM = re.compile(
    r"^claim:\s*(?P<owner>[^,\n]+),\s*(?P<date>\d{4}-\d{2}-\d{2})\s*$",
    re.MULTILINE,
)
_OWNER = re.compile(r"^[^,\n]+$")


def _parse_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ClaimRecoveryError(f"{label} must be a valid YYYY-MM-DD date") from exc


def _git(repo_root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ClaimRecoveryError(
            "repository evidence is unavailable; preserving the current owner"
        ) from exc
    return completed.stdout.strip()


def reclaim(
    ticket_path: Path,
    *,
    new_owner: str,
    takeover_date: str,
    stale_before: str,
    repo_root: Path,
) -> None:
    """Replace one stale claim only when repository history proves inactivity."""
    ticket_path = Path(ticket_path)
    repo_root = Path(repo_root)
    if not _OWNER.fullmatch(new_owner.strip()):
        raise ClaimRecoveryError("new owner must be a non-empty name without commas")
    takeover = _parse_date(takeover_date, "takeover date")
    cutoff = _parse_date(stale_before, "stale-before date")
    for path in (repo_root, ticket_path.parent, ticket_path):
        try:
            map_store._assert_no_symlink_components(path)
            map_store._assert_contained(repo_root, path)
        except map_store.SchemaViolation as exc:
            raise ClaimRecoveryError(str(exc)) from exc
    try:
        text = ticket_path.read_text(encoding="utf-8")
        ticket = map_store.parse_ticket_document(text, ticket_path)
    except (OSError, map_store.SchemaViolation) as exc:
        raise ClaimRecoveryError(f"cannot read a valid ticket: {exc}") from exc
    if ticket.frontmatter.status != "claimed":
        raise ClaimRecoveryError("ticket must remain claimed before reclaim")
    claims = list(_CLAIM.finditer(text))
    if len(claims) != 1:
        raise ClaimRecoveryError(
            "reclaim requires exactly one dated claim; preserving the current owner"
        )
    old_owner = claims[0].group("owner").strip()
    claim_value = claims[0].group("date")
    claimed_on = _parse_date(claim_value, "claim date")
    if claimed_on > cutoff:
        raise ClaimRecoveryError("claim is not observably stale at the requested cutoff")
    if takeover < cutoff:
        raise ClaimRecoveryError("takeover date cannot precede the stale cutoff")

    relative = ticket_path.resolve(strict=True).relative_to(
        repo_root.resolve(strict=True)
    ).as_posix()
    if _git(repo_root, "status", "--porcelain", "--", relative):
        raise ClaimRecoveryError(
            "ticket has uncommitted post-claim evidence; preserving the current owner"
        )
    last_change = _git(repo_root, "log", "-1", "--format=%cI", "--", relative)
    if not last_change:
        raise ClaimRecoveryError(
            "repository evidence is unavailable; preserving the current owner"
        )
    try:
        last_change_at = datetime.fromisoformat(last_change)
    except ValueError as exc:
        raise ClaimRecoveryError(
            "precise Git timestamp is unavailable; preserving the current owner"
        ) from exc
    if last_change_at.date() >= claimed_on:
        raise ClaimRecoveryError(
            f"ticket has a post-claim or same-day ambiguous Git change at "
            f"{last_change_at.isoformat()}; "
            "preserving the current owner"
        )

    replacement = f"claim: {new_owner.strip()}, {takeover.isoformat()}"
    updated = text[: claims[0].start()] + replacement + text[claims[0].end() :]
    history = (
        f"- takeover: {old_owner} -> {new_owner.strip()} | "
        f"{takeover.isoformat()} | basis: claim dated {claimed_on.isoformat()}; "
        "no post-claim Git change"
    )
    if "## Claim history" in updated:
        updated = updated.rstrip() + "\n" + history + "\n"
    else:
        updated = updated.rstrip() + "\n\n## Claim history\n\n" + history + "\n"
    map_store._atomic_write(ticket_path, updated)
