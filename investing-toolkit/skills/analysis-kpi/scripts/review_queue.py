#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Review-item queue + human-confirm seam (operational-kpi capability, slice 2).

Layer 2 (Analysis) internal persistence — NOT external I/O. A single durable
append-only queue file (`review-queue.json`) under the store root holds the
review items that need human adjudication before a flagged KPI point is
trusted. The queue file is the single source of pending work: enqueue appends
an OPEN item; later slices list the OPEN items, adjudicate them (carrying an
immutable append-only adjudicator identity), and reopen resolved items.

This slice ships the full library surface (enqueue / list_open / adjudicate /
reopen / the confirm-seam authorization boundary) plus a thin `enqueue` /
`list` / `adjudicate` CLI (plan
docs/loom/plans/2026-07-14-operational-kpi-review-queue.md, Tasks 1-7).

Durable-dir resolution, atomic tmp+rename write, and series locking are ALL
REUSED from the shared `_store_fs.py` module (same-dir import below,
Rule-of-Three extract out of kpi_store.py triggered by a third durable
store), NOT re-implemented and NOT sourced from cache_util: a review queue
is durable, human-in-the-loop state that must survive cache eviction, so
it roots under the same DATA dir as the KPI store.

A review-item's `created_at` is a RUNTIME event (caller-supplied) and is
preserved verbatim — it is NOT held to slice-1's accession-derived `as_of`
guard.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` works both
# under `uv run --script` and under importlib test loading (mirrors
# analysis-comps/scripts/comps_compute.py's sector_classifier import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402

# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION's rationale).
QUEUE_SCHEMA_VERSION = "1.0"

QUEUE_FILENAME = "review-queue.json"


def _queue_path() -> Path:
    """The single durable queue file under the reused slice-1 store root."""
    return _store_fs.resolve_store_dir() / QUEUE_FILENAME


def _load_queue(path: Path) -> dict:
    """Read the existing queue envelope, or return a fresh empty one.

    Append-only: an existing file's `items` list is preserved and never
    overwritten. A fresh queue starts with a versioned `_review_queue_meta`
    envelope and an empty `items` list.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("items", [])
        return envelope
    return {
        "_review_queue_meta": {"version": QUEUE_SCHEMA_VERSION},
        "items": [],
    }


def enqueue(item: dict) -> None:
    """Append one review-item to the durable append-only queue file.

    An item is a dict `{review_item_id, subject_type, subject_id, reason}`.
    `status` DEFAULTS to `"OPEN"` if absent (a freshly enqueued item is
    pending work); a caller-supplied `created_at` is preserved verbatim (a
    review-item's created_at is a runtime event — NOT slice-1's
    accession-derived as_of). The item is otherwise stored unchanged so a
    later list/adjudicate reads back exactly what was queued.

    Concurrency: unlike kpi_store's file-per-series layout, EVERY enqueue
    targets the SAME single shared queue file, so an unlocked
    load->append->write cycle would lose concurrent writers' items (atomic
    tmp+rename prevents a torn file, not a lost update). The full
    read-modify-write cycle is guarded by kpi_store's existing per-path
    `fcntl.flock` lock (reused, not reimplemented — same-skill import),
    mirroring kpi_store.append's try/finally structure exactly.
    """
    stored = dict(item)
    stored.setdefault("status", "OPEN")

    path = _queue_path()
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_queue(path)
        envelope["items"].append(stored)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)


def list_open() -> list:
    """Return all review-items whose `status == "OPEN"`.

    Read-only: never mutates or reorders the stored items. A missing queue
    file (nothing enqueued yet) returns `[]` — not an error, since "no
    pending work" is the normal starting state.
    """
    path = _queue_path()
    if not path.exists():
        return []
    envelope = _load_queue(path)
    return [item for item in envelope["items"] if item.get("status") == "OPEN"]


# decision -> resolved status. Unknown decisions are rejected loud in
# `adjudicate` rather than silently falling through.
_DECISION_TO_STATUS = {
    "approve": "APPROVED",
    "reject": "REJECTED",
    "edit": "EDITED",
}


def adjudicate(
    review_item_id: str,
    decision: str,
    adjudicated_by: str,
    resolution=None,
    adjudicated_at=None,
    actor_is_pipeline: bool = False,
) -> None:
    """Move an OPEN item to a resolved status per `decision`, storing
    `resolution` on the item and APPENDING an adjudication record to its
    append-only `adjudications` list.

    `decision` maps to a resolved status: "approve" -> APPROVED, "reject"
    -> REJECTED, "edit" -> EDITED; any other value is rejected loud
    (ValueError), nothing written. Adjudicating an unknown `review_item_id`,
    or an item that is NOT currently OPEN (an already-resolved item needs
    `reopen` first — Task 6), is also rejected loud, nothing written.

    Immutable adjudicator identity (Task 4): every call APPENDS a record
    `{adjudicated_by, adjudicated_at, decision}` to the item's `adjudications`
    list (created on first adjudication). A later re-adjudication (after
    reopen) appends a NEW record — it never overwrites or drops prior ones.
    `adjudicated_at` is a caller-supplied RUNTIME event (the module never
    reads the wall clock — pass a timestamp in, or omit it for None).

    Confirm-seam authorization boundary (Task 5): `adjudicated_by` MUST be a
    non-empty human identity. A call with an empty/None `adjudicated_by`, or
    an explicit `actor_is_pipeline=True`, is a self-confirm attempt by the
    pipeline and is rejected loud (ValueError) BEFORE the lock/write — the
    item's state and adjudications are untouched. This is the seam that
    keeps an automated pipeline from confirming its own flagged KPI point;
    only a real human adjudicator identity may resolve a review item.

    Concurrency: mirrors `enqueue`'s locking — the full read-modify-write
    cycle (load -> find -> mutate -> write) is guarded by kpi_store's
    per-path `fcntl.flock` lock on the SAME shared queue file, so a
    concurrent adjudicate/enqueue never tears or loses an update.
    """
    if actor_is_pipeline or not (adjudicated_by and adjudicated_by.strip()):
        raise ValueError(
            "review_queue.adjudicate: adjudicated_by must be a non-empty "
            "human identity — pipeline self-confirmation is rejected, "
            "nothing written"
        )

    if decision not in _DECISION_TO_STATUS:
        raise ValueError(
            f"review_queue.adjudicate: unknown decision {decision!r} — "
            f"expected one of {sorted(_DECISION_TO_STATUS)}, nothing written"
        )

    path = _queue_path()
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_queue(path)
        target = None
        for existing in envelope["items"]:
            if existing.get("review_item_id") == review_item_id:
                target = existing
                break

        if target is None:
            raise ValueError(
                f"review_queue.adjudicate: unknown review_item_id "
                f"{review_item_id!r} — nothing written"
            )
        if target.get("status") != "OPEN":
            raise ValueError(
                f"review_queue.adjudicate: review_item_id {review_item_id!r} "
                f"is not OPEN (status={target.get('status')!r}) — illegal "
                f"transition, reopen it first, nothing written"
            )

        target["status"] = _DECISION_TO_STATUS[decision]
        target["resolution"] = resolution
        target.setdefault("adjudications", []).append({
            "adjudicated_by": adjudicated_by,
            "adjudicated_at": adjudicated_at,
            "decision": decision,
        })
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)


def reopen(review_item_id: str) -> None:
    """Move a RESOLVED item (APPROVED/REJECTED/EDITED) back to status OPEN,
    so it can be re-adjudicated (Task 4's re-adjudication depends on this).

    Reopening an item that is already OPEN, or an unknown `review_item_id`,
    is rejected loud (ValueError), nothing written — mirrors `adjudicate`'s
    illegal-transition guard.

    Concurrency: mirrors `adjudicate`'s locking — the full read-modify-write
    cycle is guarded by kpi_store's per-path `fcntl.flock` lock on the SAME
    shared queue file.
    """
    path = _queue_path()
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_queue(path)
        target = None
        for existing in envelope["items"]:
            if existing.get("review_item_id") == review_item_id:
                target = existing
                break

        if target is None:
            raise ValueError(
                f"review_queue.reopen: unknown review_item_id "
                f"{review_item_id!r} — nothing written"
            )
        if target.get("status") == "OPEN":
            raise ValueError(
                f"review_queue.reopen: review_item_id {review_item_id!r} "
                f"is already OPEN — illegal transition, nothing written"
            )

        target["status"] = "OPEN"
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)


def _cli_enqueue(args: argparse.Namespace) -> int:
    """`enqueue` subcommand: read ONE item as JSON from `--file` (or stdin
    when omitted), call `enqueue(item)`. Mirrors kpi_store._cli_append's
    exit-code contract: malformed JSON or a non-object -> 2 (nothing
    written); a rejection (ValueError) -> 1; success -> 0.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        item = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"review_queue enqueue: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(item, dict):
        print(
            "review_queue enqueue: expected a JSON object (item), got "
            f"{type(item).__name__} — nothing written",
            file=sys.stderr,
        )
        return 2

    try:
        enqueue(item)
    except ValueError as exc:
        print(f"review_queue enqueue: {exc}", file=sys.stderr)
        return 1
    return 0


def _cli_list(args: argparse.Namespace) -> int:
    """`list` subcommand: print the OPEN items as a JSON array to stdout."""
    json.dump(list_open(), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_adjudicate(args: argparse.Namespace) -> int:
    """`adjudicate` subcommand: call `adjudicate(id, decision,
    adjudicated_by=by, resolution=..., adjudicated_at=...)`. A rejection
    (unknown id, illegal transition, or the confirm-seam auth guard) is a
    ValueError -> exit 1; argparse itself handles missing required args
    with its own exit 2.
    """
    try:
        adjudicate(
            args.id, args.decision, adjudicated_by=args.by,
            resolution=args.resolution, adjudicated_at=args.at,
        )
    except ValueError as exc:
        print(f"review_queue adjudicate: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Review-item queue CLI (enqueue / list / adjudicate)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    enqueue_parser = subparsers.add_parser(
        "enqueue", help="Append one review-item (JSON) to the queue."
    )
    enqueue_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the item (default: read stdin).",
    )
    enqueue_parser.set_defaults(func=_cli_enqueue)

    list_parser = subparsers.add_parser(
        "list", help="Print the OPEN review-items as a JSON array."
    )
    list_parser.set_defaults(func=_cli_list)

    adjudicate_parser = subparsers.add_parser(
        "adjudicate", help="Resolve an OPEN review-item."
    )
    adjudicate_parser.add_argument("--id", required=True, dest="id")
    adjudicate_parser.add_argument("--decision", required=True)
    adjudicate_parser.add_argument("--by", required=True, dest="by")
    adjudicate_parser.add_argument("--resolution", default=None)
    adjudicate_parser.add_argument("--at", default=None, dest="at")
    adjudicate_parser.set_defaults(func=_cli_adjudicate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
