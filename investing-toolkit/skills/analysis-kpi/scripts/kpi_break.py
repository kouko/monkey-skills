#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Break-event detection + human adjudication lifecycle (operational-kpi
capability, slice 6).

The module surface:
- `detect_breaks(prev_summary, curr_summary)` — PURE COMPUTE, no
  persistence. Compares two consecutive-period KPI summaries and returns a
  list of candidate break-events `[{"trigger": ..., "detail": ...}]`:
    * `resegmentation` — the SET of segment names changed (added/removed/
      count-changed) between prev and curr.
    * `relabel` — a kpi_id present in BOTH summaries' `kpi_labels` whose
      label text differs.
    * `arithmetic-mismatch` — a kpi_id in curr's `reconciliation` whose
      `parts` don't sum to `total` within a 1% relative tolerance
      (`math.isclose(rel_tol=0.01)`).
  Identical summaries -> []. A summary with no `reconciliation` key simply
  cannot raise arithmetic-mismatch (N/A, not an error — `.get` throughout).
- `flag_break(company, schema_version, candidate, review_item_id)` persists
  a new FLAGGED break-event record to a per-company durable file (distinct
  `.kpi-breaks.json` suffix, lock-guarded RMW via `_store_fs`, mirroring
  `kpi_schema.propose`) AND enqueues a `subject_type="break-event"`
  review-item via `review_queue.enqueue` (reused seam, not reimplemented).
  `get_break`/`list_breaks` are read-only queries over that store.
- `confirm_break(company, break_id, adjudicated_by, mapping,
  adjudicated_at=None)` / `dismiss_break(company, break_id, adjudicated_by,
  adjudicated_at=None)` adjudicate the break's review-item through
  `review_queue.adjudicate` (REUSING its human-confirm auth boundary — an
  empty/whitespace/pipeline identity is rejected THERE, not reimplemented)
  BEFORE flipping the record — FLAGGED -> CONFIRMED (with `mapping`
  required, non-empty) or FLAGGED -> DISMISSED. A rejected identity leaves
  the break FLAGGED and its review-item OPEN; adjudicating an
  already-resolved break, or an unknown break_id, is rejected loud.
- a thin argparse CLI (`detect` / `flag` / `confirm` / `dismiss` / `list`)
  wraps the above with the same fail-loud exit-code convention as
  `kpi_schema.py`'s CLI (0 success / 1 ValueError / 2 malformed or
  malshaped input).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# Resolve same-dir modules without a package, so `import _store_fs` /
# `import review_queue` work both under `uv run --script` and under
# importlib test loading (mirrors kpi_schema.py's / kpi_gate.py's own
# same-dir import shim).
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import _store_fs  # noqa: E402
import review_queue  # noqa: E402


def detect_breaks(prev_summary: dict, curr_summary: dict) -> list:
    """Compare two consecutive-period KPI summaries and return candidate
    break-events. Pure compute — no side effects, no store/queue writes.

    Each summary is a dict with:
      - `segments`: a list/set of segment names.
      - `kpi_labels`: a dict kpi_id -> label.
      - `reconciliation` (optional): a dict kpi_id -> {"parts": [...],
        "total": ...}.
    """
    candidates = []

    prev_segments = set(prev_summary.get("segments", []))
    curr_segments = set(curr_summary.get("segments", []))
    if prev_segments != curr_segments:
        candidates.append({
            "trigger": "resegmentation",
            "detail": {
                "prev_segments": sorted(prev_segments),
                "curr_segments": sorted(curr_segments),
            },
        })

    prev_labels = prev_summary.get("kpi_labels", {})
    curr_labels = curr_summary.get("kpi_labels", {})
    for kpi_id, curr_label in curr_labels.items():
        if kpi_id in prev_labels and prev_labels[kpi_id] != curr_label:
            candidates.append({
                "trigger": "relabel",
                "detail": {
                    "kpi_id": kpi_id,
                    "prev_label": prev_labels[kpi_id],
                    "curr_label": curr_label,
                },
            })

    reconciliation = curr_summary.get("reconciliation", {})
    for kpi_id, recon in reconciliation.items():
        parts = recon.get("parts", [])
        total = recon.get("total")
        if total is not None and not math.isclose(sum(parts), total, rel_tol=0.01):
            candidates.append({
                "trigger": "arithmetic-mismatch",
                "detail": {
                    "kpi_id": kpi_id,
                    "parts": parts,
                    "sum_parts": sum(parts),
                    "total": total,
                },
            })

    return candidates


# A record-shape change here is a detectable migration, not a silent misread
# (mirrors kpi_schema.SCHEMA_ENVELOPE_VERSION's rationale).
BREAK_ENVELOPE_VERSION = "1.0"

# Distinct from kpi_schema's ".kpi-schema.json", review_queue's shared
# "review-queue.json", and kpi_store's/kpi_gate's own per-company suffixes —
# each durable store under the same DATA dir owns its own filename so a
# collision can never silently merge two stores' records.
BREAK_FILENAME_SUFFIX = ".kpi-breaks.json"


def _break_path(company: str) -> Path:
    """One file per company, sanitized the same way as kpi_schema's
    `_schema_path` (every char outside `[A-Za-z0-9_-]` -> `_`) so a
    malicious or malformed company name can never escape the store dir via
    `../` or a path separator.
    """
    company_key = _store_fs._UNSAFE_KEY_CHARS.sub("_", str(company)) or "_"
    return _store_fs.resolve_store_dir() / f"{company_key}{BREAK_FILENAME_SUFFIX}"


def _load_break_file(path: Path) -> dict:
    """Read the existing per-company break-event envelope, or return a
    fresh empty one. Mirrors kpi_schema._load_schema_file.
    """
    if path.exists():
        envelope = json.loads(path.read_text(encoding="utf-8"))
        envelope.setdefault("breaks", [])
        return envelope
    return {
        "_kpi_break_meta": {"version": BREAK_ENVELOPE_VERSION},
        "breaks": [],
    }


def flag_break(company: str, schema_version: str, candidate: dict, review_item_id: str) -> dict:
    """Persist a new FLAGGED break-event record for `company` and enqueue a
    `subject_type="break-event"` review-item referencing it.

    `candidate` is one of `detect_breaks`'s returned dicts
    (`{"trigger": ..., "detail": ...}`) — `flag_break` interprets nothing
    about its content beyond copying `trigger`/`detail` verbatim into the
    durable record. `break_id` is derived from the count of this company's
    existing break records (`f"{company}:{schema_version}:{n}"`), so it is
    stable and unique per company without a separate counter file.

    The read-modify-write of the per-company break-event file is guarded by
    `_store_fs._acquire_series_lock` (reused, not reimplemented), mirroring
    `kpi_schema.propose`'s locking exactly.

    AFTER the break-event file is durably written, enqueues the review-item
    via `review_queue.enqueue` (reused human-confirm seam, not
    reimplemented) — this is what Task 3's `confirm_break`/`dismiss_break`
    will later adjudicate through.

    Returns the newly-created break-event record.
    """
    path = _break_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_break_file(path)
        break_id = f"{company}:{schema_version}:{len(envelope['breaks'])}"
        record = {
            "break_id": break_id,
            "company": company,
            "schema_version": schema_version,
            "trigger": candidate["trigger"],
            "detail": candidate["detail"],
            "status": "FLAGGED",
            "mapping": None,
        }
        envelope["breaks"].append(record)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    review_queue.enqueue({
        "review_item_id": review_item_id,
        "subject_type": "break-event",
        "subject_id": break_id,
        "reason": (
            f"Break-event flagged for {company!r} (schema {schema_version!r}, "
            f"trigger={record['trigger']!r}) pending human adjudication"
        ),
    })

    return record


def get_break(company: str, break_id: str) -> dict | None:
    """Return the break-event record matching `break_id` for `company`, or
    `None` if no such record exists. Read-only, no lock needed (a single
    read of a file that is only ever replaced atomically).
    """
    envelope = _load_break_file(_break_path(company))
    for record in envelope["breaks"]:
        if record["break_id"] == break_id:
            return record
    return None


def list_breaks(company: str) -> list:
    """Return all break-event records for `company` (`[]` if none flagged
    yet — not an error, mirrors `review_queue.list_open`'s missing-file
    convention). Read-only.
    """
    return _load_break_file(_break_path(company))["breaks"]


def _find_break(envelope: dict, break_id: str) -> dict | None:
    """Locate a break-event record by `break_id` within an already-loaded
    envelope (in-memory, no re-read) — shared by confirm_break/dismiss_break
    so both mutate the SAME record object the caller later writes back.
    """
    for record in envelope["breaks"]:
        if record["break_id"] == break_id:
            return record
    return None


def _adjudicate_and_flip(
    company: str, break_id: str, adjudicated_by: str, decision: str,
    new_status: str, adjudicated_at, extra_fields: dict,
) -> dict:
    """Shared confirm_break/dismiss_break body: locate the FLAGGED break,
    adjudicate its review-item through `review_queue.adjudicate` (REUSING
    the auth boundary — empty/whitespace/pipeline identity rejected there)
    BEFORE flipping the record, then transition it to `new_status`.

    Mirrors `kpi_schema.confirm`'s adjudicate-before-flip ordering: the
    adjudicate call runs before any mutation of `record`/write-back, so a
    rejected identity raises with the in-memory envelope untouched on disk
    and the break-event still FLAGGED, its review-item still OPEN.
    """
    path = _break_path(company)
    lock_file = _store_fs._acquire_series_lock(path)
    try:
        envelope = _load_break_file(path)
        record = _find_break(envelope, break_id)
        if record is None:
            raise ValueError(
                f"kpi_break: unknown break_id {break_id!r} for {company!r} — "
                "nothing to adjudicate"
            )
        if record["status"] != "FLAGGED":
            raise ValueError(
                f"kpi_break: break {break_id!r} is not FLAGGED "
                f"(status={record['status']!r}) — illegal transition, "
                "nothing written"
            )

        review_item = next(
            (
                item for item in review_queue.list_open()
                if item.get("subject_id") == break_id
            ),
            None,
        )
        if review_item is None:
            raise ValueError(
                f"kpi_break: no OPEN review-item found for break {break_id!r} "
                "— nothing to adjudicate"
            )

        # Auth boundary lives in review_queue.adjudicate — reused, not
        # reimplemented. Runs BEFORE `record` is mutated/written, so a
        # rejection here (empty/whitespace/pipeline identity) leaves the
        # break FLAGGED and the review-item OPEN.
        review_queue.adjudicate(
            review_item["review_item_id"], decision,
            adjudicated_by=adjudicated_by, adjudicated_at=adjudicated_at,
        )

        record["status"] = new_status
        record.update(extra_fields)
        _store_fs._atomic_write(path, envelope)
    finally:
        _store_fs._release_series_lock(lock_file)

    return record


def confirm_break(
    company: str, break_id: str, adjudicated_by: str, mapping: dict,
    adjudicated_at=None,
) -> dict:
    """Confirm a FLAGGED break-event for `company`, transitioning it
    FLAGGED -> CONFIRMED and recording the old->new `mapping` (e.g. a
    resegmentation's prior-segment -> new-segment correspondence).

    `mapping` MUST be a non-empty value — rejected loud (ValueError) BEFORE
    any adjudicate call or write, so a missing/empty mapping never even
    reaches the review-queue seam.

    The review-item adjudication (auth boundary + adjudicate-before-flip
    ordering) is fully shared with `dismiss_break` via `_adjudicate_and_flip`
    — see that function's docstring for the reused-seam contract.
    """
    if not mapping:
        raise ValueError(
            "kpi_break.confirm_break: mapping is required (missing/empty) — "
            "nothing adjudicated, nothing written"
        )

    return _adjudicate_and_flip(
        company, break_id, adjudicated_by, decision="approve",
        new_status="CONFIRMED", adjudicated_at=adjudicated_at,
        extra_fields={"mapping": mapping},
    )


def dismiss_break(
    company: str, break_id: str, adjudicated_by: str, adjudicated_at=None,
) -> dict:
    """Dismiss a FLAGGED break-event for `company` as a false positive,
    transitioning it FLAGGED -> DISMISSED. No mapping is recorded (there is
    nothing to map — the flagged drift was never real).

    Shares the reused review-queue seam + adjudicate-before-flip ordering
    with `confirm_break` via `_adjudicate_and_flip`.
    """
    return _adjudicate_and_flip(
        company, break_id, adjudicated_by, decision="reject",
        new_status="DISMISSED", adjudicated_at=adjudicated_at,
        extra_fields={},
    )


def _read_json_arg(args) -> object:
    """Read the CLI body from `--file` (or stdin when omitted) and parse it
    as JSON. Raises `json.JSONDecodeError` on malformed input — every
    caller below catches that and exits 2, mirroring
    `kpi_schema._cli_propose`'s exit-code contract.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    return json.loads(raw)


def _cli_detect(args: argparse.Namespace) -> int:
    """`detect` subcommand: read `{"prev": ..., "curr": ...}` as JSON from
    `--file` (or stdin when omitted), call `detect_breaks(prev, curr)` and
    print the candidate list. PURE COMPUTE — no ValueError path, only
    malformed/malshaped input can fail (exit 2).
    """
    try:
        payload = _read_json_arg(args)
    except json.JSONDecodeError as exc:
        print(f"kpi_break detect: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict) or "prev" not in payload or "curr" not in payload:
        print(
            "kpi_break detect: expected a JSON object with 'prev' and "
            f"'curr' summaries, got {payload!r}",
            file=sys.stderr,
        )
        return 2

    candidates = detect_breaks(payload["prev"], payload["curr"])
    json.dump(candidates, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_flag(args: argparse.Namespace) -> int:
    """`flag` subcommand: read ONE candidate as a JSON object from `--file`
    (or stdin when omitted), call `flag_break(company, schema_version,
    candidate, review_item_id)`. Malformed JSON or a non-object body -> 2
    (nothing written); a rejection (ValueError, or a candidate missing
    `trigger`/`detail` -> KeyError) -> 1; success -> 0, prints the new
    break-event record as JSON.
    """
    try:
        candidate = _read_json_arg(args)
    except json.JSONDecodeError as exc:
        print(f"kpi_break flag: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(candidate, dict):
        print(
            "kpi_break flag: expected a JSON object (candidate), got "
            f"{type(candidate).__name__} — nothing written",
            file=sys.stderr,
        )
        return 2

    try:
        record = flag_break(args.company, args.schema_version, candidate, args.review_item_id)
    except (ValueError, KeyError) as exc:
        print(f"kpi_break flag: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_confirm(args: argparse.Namespace) -> int:
    """`confirm` subcommand: read `mapping` as JSON from `--file` (or stdin
    when omitted), call `confirm_break(company, break_id,
    adjudicated_by=by, mapping=mapping, adjudicated_at=at)`. Malformed JSON
    -> 2 (nothing written); every fail-loud guard (unknown break_id,
    non-FLAGGED status, missing/empty mapping, or the reused review-queue
    auth boundary) is a ValueError -> 1; success -> 0.
    """
    try:
        mapping = _read_json_arg(args)
    except json.JSONDecodeError as exc:
        print(f"kpi_break confirm: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    try:
        record = confirm_break(
            args.company, args.break_id, adjudicated_by=args.by,
            mapping=mapping, adjudicated_at=args.at,
        )
    except ValueError as exc:
        print(f"kpi_break confirm: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_dismiss(args: argparse.Namespace) -> int:
    """`dismiss` subcommand: call `dismiss_break(company, break_id,
    adjudicated_by=by, adjudicated_at=at)`. No request body. Every
    fail-loud guard is a ValueError -> exit 1; a missing required flag is
    handled by argparse itself and exits 2.
    """
    try:
        record = dismiss_break(args.company, args.break_id, adjudicated_by=args.by, adjudicated_at=args.at)
    except ValueError as exc:
        print(f"kpi_break dismiss: {exc}", file=sys.stderr)
        return 1

    json.dump(record, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _cli_list(args: argparse.Namespace) -> int:
    """`list` subcommand: print all break-event records for a company as a
    JSON array. Always exits 0 (read-only; no company having any breaks
    yet reads as `[]`, not an error).
    """
    json.dump(list_breaks(args.company), sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Break-event detection + human adjudication lifecycle CLI "
            "(detect / flag / confirm / dismiss / list)."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect_parser = subparsers.add_parser(
        "detect", help="Compare two consecutive-period KPI summaries and print candidate break-events."
    )
    detect_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding {prev, curr} summaries (default: read stdin).",
    )
    detect_parser.set_defaults(func=_cli_detect)

    flag_parser = subparsers.add_parser(
        "flag", help="Persist a FLAGGED break-event and enqueue its review-item."
    )
    flag_parser.add_argument("--company", required=True)
    flag_parser.add_argument("--schema-version", required=True, dest="schema_version")
    flag_parser.add_argument("--review-item-id", required=True, dest="review_item_id")
    flag_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the candidate (default: read stdin).",
    )
    flag_parser.set_defaults(func=_cli_flag)

    confirm_parser = subparsers.add_parser(
        "confirm", help="Confirm a FLAGGED break-event through the review-queue human-confirm seam."
    )
    confirm_parser.add_argument("--company", required=True)
    confirm_parser.add_argument("--break-id", required=True, dest="break_id")
    confirm_parser.add_argument("--by", required=True, dest="by")
    confirm_parser.add_argument("--at", default=None, dest="at")
    confirm_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the mapping (default: read stdin).",
    )
    confirm_parser.set_defaults(func=_cli_confirm)

    dismiss_parser = subparsers.add_parser(
        "dismiss", help="Dismiss a FLAGGED break-event through the review-queue human-confirm seam."
    )
    dismiss_parser.add_argument("--company", required=True)
    dismiss_parser.add_argument("--break-id", required=True, dest="break_id")
    dismiss_parser.add_argument("--by", required=True, dest="by")
    dismiss_parser.add_argument("--at", default=None, dest="at")
    dismiss_parser.set_defaults(func=_cli_dismiss)

    list_parser = subparsers.add_parser(
        "list", help="Print all break-event records for a company as a JSON array."
    )
    list_parser.add_argument("--company", required=True)
    list_parser.set_defaults(func=_cli_list)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
