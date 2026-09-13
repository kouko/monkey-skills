#!/usr/bin/env python3
"""Recoverable schema-v3 Map transactions.

REQ-84 defines ordered close-and-rechart. REQ-87 extends the same atomic
primitives with full-read-set conflicts, idempotent retries, and safe recovery.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import delivery_evidence
import map_lifecycle
import map_lock
import map_store
import map_persistence
import map_ticket_mutations
import map_close_transaction


class CloseTransactionError(ValueError):
    """The requested close conflicts with the authoritative map state."""


@dataclass(frozen=True)
class UnknownRoute:
    text: str
    destination: str
    ticket_slug: str | None = None
    ticket_type: str | None = None


@dataclass(frozen=True)
class CloseResult:
    routed: int
    map_clear_eligible: bool


@dataclass(frozen=True)
class StoreRevision:
    entries: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class MutationResult:
    applied: bool
    reused: bool


@dataclass(frozen=True)
class DeliveryClosureInputs:
    """Current authoritative inputs re-evaluated immediately before close."""

    brief_text: str
    plan_text: str
    acceptance_satisfied: bool
    review_head: str
    verification_head: str
    pr: str
    pr_roles: tuple[delivery_evidence.PRRole, ...] | None = None
    pr_owners: dict[str, str] | None = None
    ownership_complete: bool = False
    artifact_probe: delivery_evidence.ArtifactProbeEvidence | None = None
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run


def _before_terminalize() -> None:
    """Test seam immediately before the final, terminal ticket write."""


def capture_revision(map_dir: Path) -> StoreRevision:
    """Digest the complete Map-and-Ticket topology read set."""
    map_dir = Path(map_dir)
    paths = [map_dir / "MAP.md"]
    tickets_dir = map_dir / "tickets"
    try:
        tickets_mode = tickets_dir.lstat().st_mode
    except OSError as exc:
        raise CloseTransactionError(
            f"cannot read transaction revision for {tickets_dir}: {exc}"
        ) from exc
    if not stat.S_ISDIR(tickets_mode):
        raise CloseTransactionError(
            f"transaction read set contains a non-regular tickets directory: "
            f"{tickets_dir}"
        )
    paths.extend(sorted(tickets_dir.glob("*.md")))
    entries: list[tuple[str, str]] = []
    for path in paths:
        try:
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode):
                raise CloseTransactionError(
                    f"transaction read set contains a non-regular file: {path}"
                )
            payload = path.read_bytes()
        except OSError as exc:
            raise CloseTransactionError(
                f"cannot read transaction revision for {path}: {exc}"
            ) from exc
        entries.append(
            (
                path.relative_to(map_dir).as_posix(),
                hashlib.sha256(payload).hexdigest(),
            )
        )
    return StoreRevision(tuple(entries))


def _require_revision(map_dir: Path, expected: StoreRevision) -> None:
    if capture_revision(map_dir) != expected:
        raise CloseTransactionError(
            "transaction conflict: the authoritative Map or Ticket read set "
            "changed; re-read before retry"
        )


def _require_valid_store(map_dir: Path) -> None:
    code, message = map_store.validate(map_dir)
    if code != 0:
        raise CloseTransactionError(
            f"transaction final validation failed: {message}"
        )


@contextmanager
def _transaction_lock(map_dir: Path):
    """Translate the shared lock's refusal into this operation's domain."""
    try:
        with map_lock.map_writer_lock(map_dir):
            yield
    except map_lock.MapLockError as exc:
        raise CloseTransactionError(str(exc)) from exc


@contextmanager
def serialize_map_mutation(map_dir: Path):
    """Expose the shared writer boundary to map_store topology mutations."""
    with _transaction_lock(map_dir):
        yield


def _assert_supported_filesystem(directory: Path) -> None:
    """Probe the same directory's atomic exchange before artifact mutation."""
    descriptors: list[int] = []
    paths: list[Path] = []
    try:
        for prefix in (".map-cas-probe-a.", ".map-cas-probe-b."):
            descriptor, name = tempfile.mkstemp(prefix=prefix, dir=directory)
            descriptors.append(descriptor)
            paths.append(Path(name))
        for descriptor in descriptors:
            os.close(descriptor)
        descriptors.clear()
        map_persistence.exchange_paths(paths[0], paths[1])
        map_persistence.fsync_directory(directory)
    except (OSError, map_store.SchemaViolation) as exc:
        raise CloseTransactionError(
            f"unsupported atomic-replacement assumption for {directory}: {exc}"
        ) from exc
    finally:
        for descriptor in descriptors:
            try:
                os.close(descriptor)
            except OSError:
                pass
        for path in paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass


def _exclusive_write(path: Path, text: str) -> None:
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        map_persistence.fsync_directory(path.parent)
    except FileExistsError as exc:
        raise CloseTransactionError(
            f"transaction conflict: {path} already exists; re-read before retry"
        ) from exc
    except OSError as exc:
        raise CloseTransactionError(
            f"cannot create transaction artifact {path}: {exc}"
        ) from exc


def _operation_path(map_dir: Path, operation_id: str) -> Path:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", operation_id):
        raise CloseTransactionError("operation_id must be a safe lowercase slug")
    path = map_dir / ".transactions" / f"{operation_id}.json"
    _assert_no_symlink_components(path)
    _assert_contained(map_dir, path)
    return path


def _load_operation(path: Path, intent: dict[str, object]) -> bool:
    if not path.exists():
        return False
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CloseTransactionError(f"cannot recover operation record: {exc}") from exc
    if saved != intent:
        raise CloseTransactionError(
            "operation retry conflicts with the authoritative operation record"
        )
    return True


def _prepare_mutation(
    map_dir: Path,
    operation_id: str,
    intent: dict[str, object],
    expected_revision: StoreRevision,
) -> tuple[Path, bool]:
    _require_revision(map_dir, expected_revision)
    _assert_supported_filesystem(map_dir)
    operation = _operation_path(map_dir, operation_id)
    if _load_operation(operation, intent):
        return operation, True
    operation.parent.mkdir(mode=0o700, exist_ok=True)
    _require_revision(map_dir, expected_revision)
    _exclusive_write(operation, json.dumps(intent, indent=2, sort_keys=True) + "\n")
    return operation, False


def claim_ticket(
    map_dir: Path,
    ticket_slug: str,
    *,
    owner: str,
    claimed_on: str,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Claim one unblocked frontier ticket under the Map writer lock."""
    with _transaction_lock(map_dir):
        return map_ticket_mutations._claim_ticket_locked(
            sys.modules[__name__],
            map_dir,
            ticket_slug,
            owner=owner,
            claimed_on=claimed_on,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )


def update_blockers(
    map_dir: Path,
    ticket_slug: str,
    blockers: list[str],
    *,
    operation_id: str,
    expected_revision: StoreRevision,
) -> MutationResult:
    """Replace blocker edges under the Map writer lock."""
    with _transaction_lock(map_dir):
        return map_ticket_mutations._update_blockers_locked(
            sys.modules[__name__],
            map_dir,
            ticket_slug,
            blockers,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )


def _atomic_write(
    path: Path, text: str, *, expected: bytes | None = None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        map_store.atomic_write(path, text, expected=expected)
    except map_store.SchemaViolation as exc:
        raise CloseTransactionError(str(exc)) from exc


def _assert_no_symlink_components(path: Path) -> None:
    map_lock.assert_no_symlink_components(path, error=CloseTransactionError)


def _assert_contained(map_dir: Path, candidate: Path) -> None:
    try:
        candidate.resolve(strict=False).relative_to(map_dir.resolve(strict=True))
    except (OSError, ValueError) as exc:
        raise CloseTransactionError(
            f"path escapes the map directory: {candidate}"
        ) from exc


def _intent(
    ticket_slug: str,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    fog_ids: list[str | None],
) -> dict[str, object]:
    routes = []
    for route, fog_id in zip(unknowns, fog_ids, strict=True):
        item = asdict(route)
        item["fog_id"] = fog_id
        routes.append(item)
    return {
        "version": 1,
        "ticket_slug": ticket_slug,
        "gist": gist,
        "resolution": resolution,
        "routes": routes,
        "prepared": True,
    }


def _load_or_prepare_intent(
    map_dir: Path,
    ticket_slug: str,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    map_doc: map_store.MapDocument,
) -> tuple[Path, dict[str, object]]:
    journal = map_dir / ".transactions" / f"close-{ticket_slug}.json"
    if journal.exists():
        try:
            saved = json.loads(journal.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CloseTransactionError(f"cannot recover close operation: {exc}") from exc
        saved_fog_ids = [route.get("fog_id") for route in saved.get("routes", [])]
        expected = _intent(ticket_slug, gist, resolution, unknowns, saved_fog_ids)
        if saved != expected:
            raise CloseTransactionError(
                "close retry conflicts with the prepared operation record"
            )
        return journal, saved

    next_fog = max((entry.number for entry in map_doc.fog_entries), default=0) + 1
    fog_ids: list[str | None] = []
    for route in unknowns:
        if route.destination == "fog":
            fog_ids.append(f"F-{next_fog}")
            next_fog += 1
        else:
            fog_ids.append(None)
    prepared = _intent(ticket_slug, gist, resolution, unknowns, fog_ids)
    journal.parent.mkdir(mode=0o700, exist_ok=True)
    _exclusive_write(
        journal, json.dumps(prepared, indent=2, sort_keys=True) + "\n"
    )
    return journal, prepared


RetirementReadiness = map_lifecycle.RetirementReadiness


def prepare_retirement(map_dir: Path, repo_root: Path) -> RetirementReadiness:
    """Validate retirement through the independent lifecycle orchestrator."""
    try:
        return map_lifecycle.prepare_retirement(map_dir, repo_root)
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def archive_map_transition(map_dir: Path, *, repo_root: Path) -> None:
    """Archive a clear Map through the shared lifecycle orchestrator."""
    try:
        map_lifecycle.archive_map_transition(map_dir, repo_root=repo_root)
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def retire_map(
    map_dir: Path,
    *,
    ratified_by: str,
    ratified_on: str,
    reason: str,
    repo_root: Path,
) -> None:
    """Retire a Map through the shared lifecycle orchestrator."""
    try:
        map_lifecycle.retire_map(
            map_dir,
            ratified_by=ratified_by,
            ratified_on=ratified_on,
            reason=reason,
            repo_root=repo_root,
        )
    except map_lifecycle.LifecycleError as exc:
        raise CloseTransactionError(str(exc)) from exc


def close_and_rechart(
    map_dir: Path,
    ticket_slug: str,
    *,
    gist: str,
    resolution: str,
    unknowns: list[UnknownRoute],
    delivery_closure: DeliveryClosureInputs | None = None,
) -> CloseResult:
    """Close and re-chart under the Map writer lock."""
    with _transaction_lock(map_dir):
        return map_close_transaction._close_and_rechart_locked(
            sys.modules[__name__],
            map_dir,
            ticket_slug,
            gist=gist,
            resolution=resolution,
            unknowns=unknowns,
            delivery_closure=delivery_closure,
        )
