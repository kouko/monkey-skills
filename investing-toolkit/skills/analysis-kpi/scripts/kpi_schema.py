#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
KPI schema propose-then-confirm lifecycle (operational-kpi capability, slice 3).

Layer 2 (Analysis) internal persistence — NOT external I/O. A file-per-company
JSON holds every schema VERSION ever proposed for that company (a durable,
versioned envelope under the same DATA dir as `kpi_store.py` / `review_queue.py`),
so a later confirm/amend transitions an existing version in place rather than
overwriting history.

The module surface:
- `propose(company, kpi_defs, review_item_id)` writes a new PROPOSED version
  (version 1 on a first propose), storing the caller-supplied `kpi_defs`
  verbatim (the LLM produces them upstream — NOT this module's job), AND
  enqueues a `subject_type="kpi-schema"` review-item via `review_queue.enqueue`
  so a human can later confirm it (reused seam, not reimplemented).
- `confirm(company, adjudicated_by, adjudicated_at=None)` locates the latest
  PROPOSED version and its OPEN review-item, adjudicates it through
  `review_queue.adjudicate` (the reused human-confirm seam, auth boundary
  included) BEFORE flipping the schema to CONFIRMED — a rejected identity
  leaves the schema PROPOSED — and supersedes any prior CONFIRMED version so
  only one is CONFIRMED at a time.
- `amend(company, new_kpi_defs, review_item_id)` proposes a new version through
  the same path; `confirmed_kpi_ids` / `is_kpi_in_confirmed_schema` expose the
  schema-scoped extraction boundary (only a CONFIRMED schema's kpi_ids are
  extractable; PROPOSED-only and SUPERSEDED-only yield none).
- a thin argparse CLI (`propose` / `confirm` / `status`) wraps the above with
  the same fail-loud exit-code convention as `review_queue.py`'s CLI (0 success
  / 1 ValueError / 2 malformed or malshaped input).

Durable-dir resolution, atomic tmp+rename write, and series locking are ALL
REUSED from the shared `_store_fs.py` module (same-dir import below), NOT
re-implemented and NOT sourced from cache_util: a KPI schema is durable,
human-in-the-loop-gated state that must survive cache eviction, so it roots
under the same DATA dir as the KPI store and review queue.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` /
# `import review_queue` work both under `uv run --script` and under
# importlib test loading (mirrors kpi_store.py's / review_queue.py's own
# same-dir import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402
import review_queue  # noqa: E402

# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_store.STORE_SCHEMA_VERSION / review_queue.QUEUE_SCHEMA_VERSION).
SCHEMA_ENVELOPE_VERSION = "1.0"

SCHEMA_FILENAME_SUFFIX = ".kpi-schema.json"


def _schema_path(company: str) -> Path:
    """One file per company, sanitized the same way as kpi_store's
    `_series_key` (every char outside `[A-Za-z0-9_-]` -> `_`) so a malicious
    or malformed company name can never escape the store dir via `../` or a
    path separator.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{SCHEMA_FILENAME_SUFFIX}"


def _load_schema_file(path: Path) -> dict:
    """Read the existing per-company schema envelope, or return a fresh
    empty one. `versions` holds every version ever proposed for this
    company, oldest first — never overwritten, only appended/mutated in
    place by confirm/amend (Tasks 3/5).
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("versions", [])
        return envelope
    return {
        "_kpi_schema_meta": {"version": SCHEMA_ENVELOPE_VERSION},
        "versions": [],
    }


def propose(company: str, kpi_defs: list, review_item_id: str) -> dict:
    """Propose a new KPI schema version for `company`.

    On a company's FIRST propose, writes version 1 with status "PROPOSED",
    storing `kpi_defs` (a list of dicts like `{kpi_id, label, unit,
    locate_hint}`, produced upstream by the LLM) verbatim — this module
    interprets nothing about their content. `confirmed_by`/`confirmed_at`
    start `None` (only `confirm`, Task 3, sets them).

    The read-modify-write of the per-company schema file is guarded by
    `_store_fs._acquire_series_lock`, mirroring `kpi_store.append` /
    `review_queue.enqueue`'s locking so a concurrent propose never tears or
    loses an update.

    AFTER the schema file is durably written, enqueues a
    `subject_type="kpi-schema"` review-item (via `review_queue.enqueue`)
    referencing the new schema's `schema_id` as `subject_id`, carrying the
    caller-supplied `review_item_id` — this is what a human will later
    confirm through the review queue's existing human-confirm seam (reused,
    not reimplemented).

    KNOWN LIMITATION (cross-store non-atomic seam): the schema write and the
    review-item enqueue touch two independent JSON files under separate locks,
    so a hard process crash BETWEEN them can leave a durable PROPOSED version
    with no review-item to confirm it. It is not a permanent block — a
    subsequent propose creates a fresh, review-item-backed version (the
    orphaned one lingers as dead weight), and `confirm` (Task 3) targets the
    latest PROPOSED version. True cross-file atomicity needs a transaction log
    (a DB the spec deliberately excludes); a lighter reconciliation — re-enqueue
    for a review-item-less PROPOSED head on retry instead of bumping the
    version — is a documented next-touch, not built this slice.

    Returns the newly-created version record.
    """
    path = _schema_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_schema_file(path)
        next_version = len(envelope["versions"]) + 1
        schema_id = f"{company}:v{next_version}"
        record = {
            "schema_id": schema_id,
            "company": company,
            "version": next_version,
            "status": "PROPOSED",
            "kpi_defs": kpi_defs,
            "confirmed_by": None,
            "confirmed_at": None,
        }
        envelope["versions"].append(record)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    review_queue.enqueue({
        "review_item_id": review_item_id,
        "subject_type": "kpi-schema",
        "subject_id": schema_id,
        "reason": (
            f"KPI schema proposed for {company!r} (version {next_version}) "
            "pending human confirmation before extraction can rely on it"
        ),
    })

    return record


def amend(company: str, new_kpi_defs: list, review_item_id: str) -> dict:
    """Propose a NEW schema version for a company that already has one —
    the evolve-a-schema path.

    Delegates entirely to `propose`: `propose` already computes
    `next_version = len(envelope["versions"]) + 1` from the company's
    EXISTING versions list, so calling it again for a company with prior
    versions naturally proposes version 2, 3, ... through the exact same
    locked store-write + review-queue-enqueue mechanism — no separate
    version-bumping logic to keep in sync. `confirm`'s supersede-prior-
    CONFIRMED step is what later retires the version this amend supersedes,
    once the new one is confirmed.
    """
    return propose(company, new_kpi_defs, review_item_id)


def confirm(company: str, adjudicated_by: str, adjudicated_at=None) -> dict:
    """Confirm the LATEST PROPOSED schema version for `company` through the
    review queue's existing human-confirm seam (reused, not reimplemented).

    Steps:
      1. Load the company's schema envelope; the latest PROPOSED version is
         the head of the (append-only) `versions` list. No versions at all,
         or a head that is not PROPOSED (already CONFIRMED — confirm-once),
         is rejected loud (ValueError), nothing written.
      2. Find that version's OPEN review-item via `review_queue.list_open`,
         matching `subject_id == schema_id`. No matching OPEN item is
         rejected loud.
      3. Adjudicate it via `review_queue.adjudicate(..., "approve",
         adjudicated_by=adjudicated_by, adjudicated_at=adjudicated_at)`
         BEFORE flipping the schema. This call IS the auth boundary — an
         empty/whitespace/pipeline `adjudicated_by` is rejected there
         (ValueError), and since it happens before this function mutates the
         in-memory envelope or writes it back, a rejected identity leaves
         the schema PROPOSED and the review-item still OPEN.
      4. Only after the adjudicate call succeeds: set the version's `status`
         to "CONFIRMED", `confirmed_by=adjudicated_by`,
         `confirmed_at=adjudicated_at` (caller-supplied — this module never
         reads the wall clock), and write back.

    The schema-file read-modify-write is guarded by
    `_store_fs._acquire_series_lock`, mirroring `propose`.

    Returns the now-CONFIRMED version record.
    """
    path = _schema_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_schema_file(path)
        versions = envelope["versions"]
        if not versions:
            raise ValueError(
                f"kpi_schema.confirm: no schema proposed for {company!r} — "
                "nothing to confirm"
            )

        latest = versions[-1]
        if latest["status"] != "PROPOSED":
            raise ValueError(
                f"kpi_schema.confirm: latest schema version for {company!r} "
                f"is not PROPOSED (status={latest['status']!r}) — nothing "
                "to confirm"
            )

        # Only ONE version may be CONFIRMED at a time. Any pre-existing
        # CONFIRMED version (from an earlier propose/confirm cycle, before
        # this amend) is superseded IN THE SAME locked read-modify-write as
        # the new confirm below — never a second unlocked pass.
        prior_confirmed = [v for v in versions if v is not latest and v["status"] == "CONFIRMED"]
        for version in prior_confirmed:
            version["status"] = "SUPERSEDED"

        schema_id = latest["schema_id"]
        review_item = next(
            (
                item for item in review_queue.list_open()
                if item.get("subject_id") == schema_id
            ),
            None,
        )
        if review_item is None:
            raise ValueError(
                f"kpi_schema.confirm: no OPEN review-item found for schema "
                f"{schema_id!r} — nothing to confirm"
            )

        # Auth boundary lives in review_queue.adjudicate — reused, not
        # reimplemented. Runs BEFORE the schema is mutated/written, so a
        # rejection here (empty/whitespace/pipeline identity) leaves the
        # schema PROPOSED and the review-item OPEN.
        review_queue.adjudicate(
            review_item["review_item_id"], "approve",
            adjudicated_by=adjudicated_by, adjudicated_at=adjudicated_at,
        )

        latest["status"] = "CONFIRMED"
        latest["confirmed_by"] = adjudicated_by
        latest["confirmed_at"] = adjudicated_at
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    return latest


def _confirmed_version(company: str) -> dict | None:
    """Locate the company's CONFIRMED schema version, or None if none
    exists (no schema proposed yet, still PROPOSED, or only SUPERSEDED
    versions with no CONFIRMED successor — Task 5's supersede-blocks
    scenario). Read-only, no lock needed (a single read of a file that is
    only ever replaced atomically).

    Only one version is ever CONFIRMED at a time (Task 5's confirm flips
    any prior CONFIRMED version to SUPERSEDED in the same locked write as
    the new confirm), so the first CONFIRMED match found is sufficient.
    """
    envelope = _load_schema_file(_schema_path(company))
    for version in envelope["versions"]:
        if version["status"] == "CONFIRMED":
            return version
    return None


def confirmed_kpi_ids(company: str) -> list:
    """The kpi_ids of `company`'s CONFIRMED schema version — the
    schema-scoped extraction boundary. A PROPOSED (unconfirmed) or
    SUPERSEDED-only schema yields `[]` (extraction blocked), matching
    `confirm`'s confirm-once / human-in-the-loop gate: nothing may be
    extracted against a schema a human has not confirmed.
    """
    confirmed = _confirmed_version(company)
    if confirmed is None:
        return []
    return [kpi_def["kpi_id"] for kpi_def in confirmed["kpi_defs"]]


def is_kpi_in_confirmed_schema(company: str, kpi_id: str) -> bool:
    """True only if `kpi_id` is listed under `company`'s CONFIRMED schema
    version. Delegates to `confirmed_kpi_ids` so the two functions can
    never disagree about what "confirmed" means.
    """
    return kpi_id in confirmed_kpi_ids(company)


def _cli_propose(args: argparse.Namespace) -> int:
    """`propose` subcommand: read `kpi_defs` as a JSON array from `--file`
    (or stdin when omitted), call `propose(company, kpi_defs,
    review_item_id)`. Mirrors review_queue._cli_enqueue's exit-code
    contract: malformed JSON or a non-array body -> 2 (nothing written); a
    rejection (ValueError) -> 1; success -> 0, prints the new version
    record as JSON to stdout.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        kpi_defs = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_schema propose: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(kpi_defs, list):
        print(
            "kpi_schema propose: expected a JSON array (kpi_defs), got "
            f"{type(kpi_defs).__name__} — nothing written",
            file=sys.stderr,
        )
        return 2

    try:
        record = propose(args.company, kpi_defs, args.review_item_id)
    except ValueError as exc:
        print(f"kpi_schema propose: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_confirm(args: argparse.Namespace) -> int:
    """`confirm` subcommand: call `confirm(company, adjudicated_by=by,
    adjudicated_at=at)`. Every fail-loud guard (no PROPOSED schema, an
    already-CONFIRMED head, a rejected identity) surfaces as ValueError ->
    exit 1; argparse itself handles a missing required flag with its own
    exit 2.
    """
    try:
        record = confirm(args.company, adjudicated_by=args.by, adjudicated_at=args.at)
    except ValueError as exc:
        print(f"kpi_schema confirm: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_status(args: argparse.Namespace) -> int:
    """`status` subcommand: print the company's schema versions (version +
    status only) plus `confirmed_kpi_ids` as JSON. A company with no schema
    proposed yet reads as an empty/blocked status (`versions: []`,
    `confirmed_kpi_ids: []`) rather than an error — "nothing proposed yet"
    is a normal starting state, mirroring review_queue.list_open's
    missing-file -> [] convention. Always exits 0 (read-only, no fail-loud
    guard to trip).
    """
    envelope = _load_schema_file(_schema_path(args.company))
    status = {
        "company": args.company,
        "versions": [
            {"version": v["version"], "status": v["status"]}
            for v in envelope["versions"]
        ],
        "confirmed_kpi_ids": confirmed_kpi_ids(args.company),
    }
    json.dump(status, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="KPI schema propose-then-confirm lifecycle CLI (propose / confirm / status)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose_parser = subparsers.add_parser(
        "propose", help="Propose a new KPI schema version for a company."
    )
    propose_parser.add_argument("--company", required=True)
    propose_parser.add_argument("--review-item-id", required=True, dest="review_item_id")
    propose_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the kpi_defs array (default: read stdin).",
    )
    propose_parser.set_defaults(func=_cli_propose)

    confirm_parser = subparsers.add_parser(
        "confirm", help="Confirm the latest PROPOSED schema version for a company."
    )
    confirm_parser.add_argument("--company", required=True)
    confirm_parser.add_argument("--by", required=True, dest="by")
    confirm_parser.add_argument("--at", default=None, dest="at")
    confirm_parser.set_defaults(func=_cli_confirm)

    status_parser = subparsers.add_parser(
        "status", help="Print a company's schema versions + confirmed_kpi_ids as JSON."
    )
    status_parser.add_argument("--company", required=True)
    status_parser.set_defaults(func=_cli_status)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
