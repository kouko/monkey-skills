#!/usr/bin/env python3
"""Deterministic bookkeeping CLI for loom-pipeline batch mode.

Parses the human-editable ``QUEUE.toml`` (array-of-tables ``[[change]]``)
that lives in the target project's ``docs/loom/`` directory. Intent
(QUEUE.toml) is separate from state (machine-owned ``queue-state.json``,
loaded/written via ``load_state``/``save_state`` below and merged onto
queue entries by ``effective_entries``) — see
docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
§Settled open questions 1.

Pure stdlib (``tomllib``, Python 3.11+). Paths are resolved by the
caller; this module does not depend on cwd.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, NoReturn, Sequence

# Status a queue entry has when no state record exists for its id yet.
QUEUED = "QUEUED"

# changeId becomes a path segment (docs/loom/<id>/...) — allow-list rather
# than deny-list, same reasoning as driver_10_guard.js's guardArgs():
# scripts/driver_10_guard.js:112-123.
_CHANGE_ID_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")

# Form-B freeze gate: the plan header's reviewer-verdict line. Anchored to
# the START of a line (a header FIELD, not a whole-body substring — prose
# that merely quotes the phrase mid-sentence must not count as frozen).
# Tolerant of the markdown bold markers the plan format uses
# (`**Plan-document-reviewer verdict**: PASS (…)`) and of the plain form
# real consumer plans use. PENDING never matches.
_PLAN_REVIEWER_PASS_PATTERN = re.compile(
    r"^\*{0,2}Plan-document-reviewer verdict\*{0,2}\s*:\s*\*{0,2}\s*PASS\b",
    re.MULTILINE,
)

FAIL_LOUD_NOTICE = (
    "fail-loud: refusing to improvise a missing or invalid queue entry — "
    "no defaults, no silent skip; load_queue FAILS rather than guessing."
)


def _test_rmw_sleep() -> None:
    """Widen a read-modify-write window for concurrency tests. No-op in prod.

    Sleeps ``LOOM_BATCH_QUEUE_TEST_RMW_SLEEP`` seconds (float) when that env
    var is set; otherwise does nothing. Lets
    test_pipeline_batch_queue.py force two subprocesses' read-modify-write
    spans to overlap deterministically instead of racing on process-start
    timing — proving the lock (not luck) prevents the lost update.
    """
    delay = os.environ.get("LOOM_BATCH_QUEUE_TEST_RMW_SLEEP")
    if delay:
        time.sleep(float(delay))


class QueueError(Exception):
    """Raised when QUEUE.toml is missing, unparseable, or malformed.

    Mirrors driver_10_guard.js's guardArgs() no-improvised-defaults stance.
    """


def _fail(msg: str, *, fn: str = "load_queue") -> NoReturn:
    """Raise QueueError in the house fail-loud shape (single message site).

    ``fn`` names the failing function in the message prefix — callers other
    than ``load_queue`` (e.g. ``load_state``) pass their own name.
    """
    raise QueueError(f"{fn}: {msg} {FAIL_LOUD_NOTICE}")


def load_queue(queue_path: Path) -> list[dict]:
    """Parse ``[[change]]`` entries from queue_path, in file order.

    Each returned dict carries at least ``id``, ``plan``
    (project-relative path string), and ``budgets`` (dict with ``run``
    and optionally ``perStation``); ``models`` is included when present
    in the source entry. Resolves nothing (no filesystem checks beyond
    reading queue_path itself).

    Raises ``QueueError`` naming the offending entry (its ``id``, or its
    index when ``id`` is absent or not a string) and the specific problem
    when: the file is missing or not valid TOML; an entry is missing
    ``id``, ``plan``, or ``budgets.run``; ``id`` is not a string, violates
    the changeId allow-list ``^[A-Za-z0-9._-]+$``, or contains ``..``; or
    two entries share an ``id``. No improvised defaults — see
    FAIL_LOUD_NOTICE.
    """
    if not queue_path.is_file():
        _fail(f'queue file not found at "{queue_path}".')

    try:
        with queue_path.open("rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        _fail(f'"{queue_path}" is not valid TOML ({e}).')

    entries = list(data.get("change", []))
    seen_ids: set[str] = set()
    for index, entry in enumerate(entries):
        entry_id = entry.get("id")
        index_label = f"<entry at index {index}>"
        label = entry_id if isinstance(entry_id, str) and entry_id else index_label

        for field in ("id", "plan"):
            if not entry.get(field):
                _fail(f'entry "{label}" is missing required field "{field}".')

        budgets = entry.get("budgets")
        if not isinstance(budgets, dict) or not budgets.get("run"):
            _fail(f'entry "{label}" is missing required field "budgets.run".')

        if not isinstance(entry_id, str):
            _fail(
                f'entry "{index_label}" has "id" of wrong type — must be a '
                f"TOML string; received {entry_id!r} "
                f"({type(entry_id).__name__})."
            )

        _assert_valid_change_id(entry_id, fn="load_queue")

        if entry_id in seen_ids:
            _fail(f'duplicate "id" {entry_id!r} in "{queue_path}".')
        seen_ids.add(entry_id)

    return entries


def load_state(state_path: Path) -> dict:
    """Load the machine-owned state file (``queue-state.json`` by convention).

    A missing file is a fresh batch and returns ``{}`` — this is not an
    error (unlike a missing QUEUE.toml, which is human-authored and
    required). Malformed JSON, or valid JSON whose top level is not an
    object (the state file is an object keyed by change id), fails loud
    with ``QueueError``, mirroring ``load_queue``'s
    no-improvised-defaults stance (FAIL_LOUD_NOTICE).
    """
    if not state_path.is_file():
        return {}

    try:
        with state_path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        _fail(f'"{state_path}" is not valid JSON ({e}).', fn="load_state")

    if not isinstance(state, dict):
        _fail(
            f'"{state_path}" has wrong top-level JSON type — must be an '
            f"object keyed by change id; received {type(state).__name__}.",
            fn="load_state",
        )
    return state


def save_state(state_path: Path, state: dict) -> None:
    """Write state to state_path atomically (tmp file + ``os.replace``).

    The tmp file is created in state_path's own directory so the rename
    is same-filesystem and therefore atomic; it is cleaned up on failure.
    Precondition: ``state_path.parent`` must already exist (``docs/loom/``
    by convention) — this function does not create directories.
    """
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{state_path.name}.", suffix=".tmp", dir=state_path.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp_name, state_path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


@contextlib.contextmanager
def _state_lock(state_path: Path) -> Iterator[None]:
    """Hold an exclusive ``flock`` across a subcommand's full state R-M-W span.

    Locks the sidecar ``<state_path>.lock`` file — never ``state_path``
    itself: an exclusive open of the state file in a truncating mode would
    clear its contents before the lock is even held (macOS
    truncating-open-before-flock trap; plan Kickoff decision). The lock
    file is opened ``"a"`` (create-if-absent, never truncates existing
    content) and locked with ``LOCK_EX`` requested directly — never
    acquired as ``LOCK_SH`` and upgraded, which is not atomic.

    Callers must enter this **before** their own ``load_state`` call and
    keep the whole read-modify-``save_state`` span inside the ``with``
    block, so a concurrent process's read is forced to happen after this
    process's write completes (closes the pre-existing lost-update race
    where two processes each read stale state, then each overwrite the
    whole file with only their own change applied).
    """
    lock_path = state_path.with_name(state_path.name + ".lock")
    with open(lock_path, "a") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def effective_entries(entries: list[dict], state: dict) -> list[dict]:
    """Merge ``load_queue`` entries with recorded ``load_state`` statuses.

    Returns a new list of shallow-copied entry dicts (inputs are not
    mutated), each augmented with ``status`` (``QUEUED`` when the entry's
    id has no state record) and, when present in the record, ``runId``,
    ``branch``, ``worktree``, ``reason``.
    """
    merged = []
    for entry in entries:
        record = state.get(entry["id"], {})
        effective = dict(entry)
        effective["status"] = record.get("status", QUEUED)
        for field in ("runId", "branch", "worktree", "reason"):
            if field in record:
                effective[field] = record[field]
        merged.append(effective)
    return merged


def check_frozen(entry: dict, project_path: Path, skills_root: Path) -> tuple[bool, str]:
    """Freeze predicate — two accepted forms, both requiring the plan file.

    Form A (change-folder): ``docs/loom/<id>/`` exists → it must pass the
    loom-spec validator (``python3 <skills_root>/loom-spec/scripts/
    validate_spec_output.py <project_path>/docs/loom/<id>``, invocation
    convention driver_40_seg2.js:106-127). This is the original v1.1
    Decision §"Freeze predicate = loom-spec validator exit-0 + plan
    written" (docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
    Task 4).

    Form B (brief+plan): ``docs/loom/<id>/`` does NOT exist → the plan
    file itself must carry a ``Plan-document-reviewer verdict: PASS``
    line. Real interactive work (observed live 2026-07-03 on
    komado-Viewfinder) produces brainstorm-brief + reviewer-PASSed plan
    with no OpenSpec change folder; rejecting that form forced ceremony
    the pipeline does not need. A change folder that EXISTS but fails the
    validator is still a hard reject — a broken change folder is a red
    flag, never a fallback to Form B.

    Returns ``(eligible, reason)`` — **never raises for ineligibility**,
    including a path-traversal attempt in ``entry["plan"]``: the resolved
    plan path is guarded to stay inside ``project_path`` (``Path.resolve()``
    + ``relative_to`` check), and a traversal is reported as an eligibility
    failure via the return tuple, not a raised ``QueueError``. This keeps
    one failure channel for this function (contrast ``load_queue``, which
    raises ``QueueError`` for structural defects at parse time — this
    function runs later, per-entry, and its whole contract is "tell me why
    not" rather than "refuse to load").
    """
    project_path = Path(project_path).resolve()
    entry_id = entry["id"]

    # Trust-boundary re-assertion: entry["id"] is trusted-by-contract
    # (load_queue already validated it) — re-check here so the boundary is
    # explicit rather than emergent.
    _assert_valid_change_id(entry_id, fn="check_frozen")

    plan_path = (project_path / entry["plan"]).resolve()
    try:
        plan_path.relative_to(project_path)
    except ValueError:
        return (
            False,
            f'entry "{entry_id}" plan "{entry["plan"]}" resolves to '
            f'"{plan_path}", outside project_path "{project_path}" '
            "(path traversal).",
        )

    if not plan_path.is_file():
        return (False, f'entry "{entry_id}" plan not found at "{plan_path}".')

    change_dir = project_path / "docs" / "loom" / entry_id
    if not change_dir.is_dir():
        # Form B: no change folder — the plan's reviewer verdict is the gate.
        if _PLAN_REVIEWER_PASS_PATTERN.search(
            plan_path.read_text(encoding="utf-8")
        ):
            return (
                True,
                f'entry "{entry_id}" is frozen — brief+plan form (no change '
                "folder; plan carries Plan-document-reviewer verdict: PASS).",
            )
        return (
            False,
            f'entry "{entry_id}" has no change folder at "{change_dir}" and '
            'its plan carries no "Plan-document-reviewer verdict: PASS" '
            "line — not frozen under either form.",
        )

    validator_script = Path(skills_root) / "loom-spec" / "scripts" / "validate_spec_output.py"
    result = subprocess.run(
        ["python3", str(validator_script), str(change_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return (
            False,
            f'entry "{entry_id}" failed the freeze predicate — validator '
            f"exited {result.returncode} for \"{change_dir}\" (ran: python3 "
            f'{validator_script} {change_dir}).',
        )

    return (True, f'entry "{entry_id}" is frozen — change-folder form (validator exit 0), plan present.')


def ensure_worktree(project_path: Path, change_id: str) -> tuple[Path, str]:
    """Create (or reuse) the worktree + branch for ``change_id``.

    Branch ``loom/<change_id>``, worktree
    ``<project_path>/.worktrees/loom-<change_id>`` — the house convention
    (using-git-worktrees/SKILL.md §The ``.worktrees/`` convention). Creates
    via ``git -C <project_path> worktree add -b <branch> <worktree_path>``
    from current HEAD (list-form subprocess args, no shell=True).

    Idempotent: if the worktree directory already exists and is checked
    out on ``branch``, returns it without error — no second ``git
    worktree add``.

    Fails loud with ``QueueError`` on any conflict this call did not
    create: the branch exists without the worktree directory, the
    directory exists but isn't checked out on ``branch`` (or isn't a git
    checkout at all), or the ``git worktree add`` command itself fails
    (git's stderr is included in the message).
    """
    # Trust-boundary re-assertion: change_id is trusted-by-contract
    # (callers derive it from load_queue's already-validated entries) —
    # re-check here so the boundary is explicit rather than emergent.
    _assert_valid_change_id(change_id, fn="ensure_worktree")

    project_path = Path(project_path)
    branch = f"loom/{change_id}"
    worktree_path = project_path / ".worktrees" / f"loom-{change_id}"

    if worktree_path.is_dir():
        head = subprocess.run(
            ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
        )
        if head.returncode == 0 and head.stdout.strip() == branch:
            return worktree_path, branch
        found = head.stdout.strip() if head.returncode == 0 else head.stderr.strip()
        _fail(
            f'worktree path "{worktree_path}" already exists but is not '
            f'checked out on branch "{branch}" (found {found!r}) — refusing '
            "to touch a conflict this call did not create.",
            fn="ensure_worktree",
        )

    branch_check = subprocess.run(
        ["git", "-C", str(project_path), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        capture_output=True,
        text=True,
    )
    if branch_check.returncode == 0:
        _fail(
            f'branch "{branch}" already exists in "{project_path}" but its '
            f'worktree "{worktree_path}" does not — refusing to touch a '
            "conflict this call did not create.",
            fn="ensure_worktree",
        )

    add_result = subprocess.run(
        ["git", "-C", str(project_path), "worktree", "add", "-b", branch, str(worktree_path)],
        capture_output=True,
        text=True,
    )
    if add_result.returncode != 0:
        _fail(
            f'"git worktree add -b {branch} {worktree_path}" failed in '
            f'"{project_path}" (exit {add_result.returncode}): '
            f"{add_result.stderr.strip()}",
            fn="ensure_worktree",
        )

    return worktree_path, branch


def _resolve_paths_and_validate_id(
    args: argparse.Namespace, verb: str
) -> tuple[Path, Path] | int:
    """Shared queue-load + unknown-id preamble for the four state-mutating
    subcommands (``mark``, ``mark-running``, ``reset``, ``force-fail``).

    Resolves ``queue_path``/``state_path`` from ``args.project`` and loads
    the queue to validate ``args.change_id`` against it. On success returns
    ``(queue_path, state_path)``. On failure — a ``load_queue`` error, or
    ``args.change_id`` not present in the queue — prints the caller-facing
    error to stderr (prefixed with ``verb``, matching each subcommand's
    prior wording) and returns the process exit code ``1`` instead, so
    callers can do ``result = _resolve_paths_and_validate_id(args, "mark");
    if isinstance(result, int): return result``.
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = load_queue(queue_path)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    known_ids = {entry["id"] for entry in entries}
    if args.change_id not in known_ids:
        print(
            f'{verb}: unknown change id "{args.change_id}" — not present in '
            f'"{queue_path}".',
            file=sys.stderr,
        )
        return 1

    return queue_path, state_path


def _cmd_mark(args: argparse.Namespace) -> int:
    """Implements the ``mark`` subcommand — see ``main``'s subparser setup.

    Writes/updates the state record for ``args.change_id`` and returns a
    process exit code (0 on success, 1 on a caller-facing error such as an
    unknown change id — printed to stderr, never raised as an exception,
    since this is the CLI boundary). Status is stored uppercase (DONE /
    FAILED) to match ``effective_entries``'s vocabulary.
    """
    resolved = _resolve_paths_and_validate_id(args, "mark")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with _state_lock(state_path):
        state = load_state(state_path)
        record = dict(state.get(args.change_id, {}))
        record["status"] = args.status.upper()
        if args.run_id:
            record["runId"] = args.run_id
        if args.reason:
            record["reason"] = args.reason
        state[args.change_id] = record

        _test_rmw_sleep()
        save_state(state_path, state)
    return 0


def _cmd_mark_running(args: argparse.Namespace) -> int:
    """Implements the ``mark-running`` subcommand — see ``main``'s subparser
    setup.

    Records ``runId`` + ``sessionDir`` on the state record for
    ``args.change_id``, called by the dispatcher immediately after
    ``Workflow()`` returns (design SSOT §4c Fix 1 revised design point 1 —
    closes the no-runId-at-RUNNING-write blocker; ``_dispatch_entry``
    itself has no runId yet at RUNNING-write time). Requires the entry's
    CURRENT recorded status to be ``RUNNING``: an unknown change id or an
    entry not in ``RUNNING`` (already terminal, or never dispatched) is a
    caller-facing error — printed to stderr, exit 1, no state mutation —
    mirroring ``_cmd_mark``'s error-reporting shape.
    """
    resolved = _resolve_paths_and_validate_id(args, "mark-running")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with _state_lock(state_path):
        state = load_state(state_path)
        existing = state.get(args.change_id, {})
        if existing.get("status") != "RUNNING":
            print(
                f'mark-running: entry "{args.change_id}" is not RUNNING '
                f'(status={existing.get("status", "QUEUED")!r}) — refusing '
                "to record runId/sessionDir without mutation.",
                file=sys.stderr,
            )
            return 1

        record = dict(existing)
        record["runId"] = args.run_id
        record["sessionDir"] = args.session_dir
        state[args.change_id] = record
        save_state(state_path, state)
    return 0


def _append_audit_line(record: dict, verb: str, reason: str | None) -> None:
    """Append one ``{verb, timestamp, reason}`` line to ``record["audit"]``.

    Append-only: a shallow copy of any existing ``audit`` list is extended,
    never truncated or rewritten (design SSOT §4c — "never silently lose
    the audit trail of why a human intervened"). The schema is uniform —
    every line carries all three keys; ``reason`` is ``""`` when not given
    (``reset``'s ``--reason`` is optional) rather than a dropped key, so a
    consumer can always read ``line["reason"]`` without a membership check.
    """
    audit = list(record.get("audit", []))
    line = {
        "verb": verb,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason or "",
    }
    audit.append(line)
    record["audit"] = audit


_WF_TERMINAL_STATUSES = frozenset({"completed", "failed", "killed"})


def _read_wf_terminal_status(run_id: str, session_dir: Path | str | None) -> str | None:
    """Opportunistically read a terminal ``status`` from a Workflow wf-record.

    Looks for ``<session_dir>/workflows/wf_<run_id>.json`` and returns its
    ``status`` field ONLY when it is one of ``completed``/``failed``/
    ``killed`` (design SSOT §4c — the only statuses observed; presence of
    the file is treated as definitively terminal). This file format is
    **undocumented host internals** (§4c), so every other outcome —
    absent file, unreadable (permission/IO error), invalid UTF-8,
    unparseable JSON, non-object JSON, missing ``status``, or an
    unrecognized ``status`` value — returns ``None`` rather than raising:
    fail-safe, opportunistic evidence only, never a hard dependency.

    ``run_id`` also gets a path-traversal guard (Rule 8/allow-list
    reasoning, same as ``_assert_valid_change_id``): it lands directly in
    a filename, so any ``run_id`` containing ``/``, ``\\``, or ``..``
    returns ``None`` instead of being interpolated into a path.

    ``session_dir`` may legitimately be ``None`` (or any other non-path
    type) — a RUNNING entry with a ``runId`` but no ``sessionDir`` recorded
    yet (``mark-running`` has not run) is exactly Task 12 reconcile's
    "no evidence yet" case, not a crash: ``Path(None)`` raises ``TypeError``,
    so this is guarded the same fail-safe way as the other undocumented-
    format cases above.
    """
    if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
        return None
    if not isinstance(session_dir, (str, Path)):
        return None

    wf_path = Path(session_dir) / "workflows" / f"wf_{run_id}.json"
    try:
        data = json.loads(wf_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None

    if not isinstance(data, dict):
        return None

    status = data.get("status")
    return status if status in _WF_TERMINAL_STATUSES else None


_STALE_NO_RUNID_GRACE_SECONDS = 10 * 60
_STALE_NO_EVIDENCE_GRACE_SECONDS = 2 * 60 * 60


def _parse_iso_timestamp(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp string; ``None`` on missing/unparseable input.

    Fail-safe, mirroring ``_read_wf_terminal_status``: a record with no
    ``dispatched_at`` (or a value that isn't a parseable ISO string) is
    treated by ``_classify_running_entry`` as having no freshness evidence
    at all, not as an exception. Naive timestamps (no ``tzinfo``) are
    assumed UTC, matching how ``_dispatch_entry``/``_append_audit_line``
    emit them.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _classify_running_entry(record: dict) -> tuple[str, str]:
    """Classify one RUNNING entry's record for ``reconcile`` (design SSOT
    §4c Fix 1 revised design point 3).

    Returns ``(category, evidence)``. ``category`` is one of:
    ``"AUTO-FAILED"`` (definitive ``failed``/``killed`` wf-record —
    caller force-transitions to FAILED), ``"SUSPECT-COMPLETE"`` (wf-record
    says ``completed`` but the entry was never marked done — no
    transition, human confirms via ``mark``), ``"SUSPECT"`` (no definitive
    evidence and ``dispatched_at`` is beyond its grace window — no
    transition), or ``""`` (no evidence yet, but not stale — normal
    in-flight state, nothing to report).

    Grace window is 10 minutes when no ``runId`` is recorded yet
    (``mark-running`` hasn't run — the dispatch-to-mark-running gap is
    normally seconds), else 2 hours (legitimate station runtime is
    unbounded, so a longer window is required once a run is confirmed
    started). A missing/unparseable ``dispatched_at`` is treated as
    unknown age — fail-safe to SUSPECT rather than silently skipped,
    mirroring ``_read_wf_terminal_status``'s "unreadable = no evidence,
    never a hard dependency" stance applied to the loud-not-silent side.
    """
    run_id = record.get("runId")
    session_dir = record.get("sessionDir")
    wf_status = (
        _read_wf_terminal_status(run_id, session_dir) if run_id else None
    )

    if wf_status in ("failed", "killed"):
        return "AUTO-FAILED", f"wf-record status={wf_status!r}"
    if wf_status == "completed":
        return (
            "SUSPECT-COMPLETE",
            "wf-record status='completed' but entry was never marked done "
            "via `mark` — confirm before treating as finished",
        )

    dispatched_at = _parse_iso_timestamp(record.get("dispatched_at"))
    if run_id:
        grace_seconds = _STALE_NO_EVIDENCE_GRACE_SECONDS
        grace_label = "no wf-record evidence"
    else:
        grace_seconds = _STALE_NO_RUNID_GRACE_SECONDS
        grace_label = "no runId recorded yet"

    if dispatched_at is None:
        return (
            "SUSPECT",
            f"{grace_label}, dispatched_at missing/unparseable (fail-safe)",
        )

    age_seconds = (datetime.now(timezone.utc) - dispatched_at).total_seconds()
    if age_seconds > grace_seconds:
        return (
            "SUSPECT",
            f"{grace_label}, dispatched_at age={age_seconds:.0f}s "
            f"(grace={grace_seconds}s)",
        )

    return "", ""


def _reconcile_running_entries(entries: list[dict], state: dict) -> list[str]:
    """Core reconcile logic (Task 12) shared by the ``reconcile`` subcommand
    and the top of ``next`` — never called from ``status`` (stays a pure
    query, per its own contract).

    Mutates ``state`` IN PLACE for ``AUTO-FAILED`` transitions (status ->
    FAILED + a ``{verb: "reconcile", timestamp, reason}`` audit line naming
    the wf status — counted by ``_check_circuit_breaker`` naturally, same
    as ``force-fail``). ``SUSPECT-COMPLETE``/``SUSPECT`` never mutate.
    Every transition gates on the entry's CURRENT effective status being
    ``RUNNING``, so re-running this against unchanged on-disk state is
    idempotent (a just-force-failed entry is no longer RUNNING on the next
    pass). Returns one human-readable line per FLAGGED entry (id, category,
    evidence) in queue order; non-flagged RUNNING entries (fresh, no
    evidence, not yet stale) produce no line.

    Caller owns ``load_state``/``save_state``/the ``_state_lock`` span —
    this function does neither, so it can be invoked from inside a lock
    already held by ``_cmd_next`` without a same-process flock deadlock.
    """
    merged = effective_entries(entries, state)
    lines: list[str] = []
    for entry in merged:
        if entry["status"] != "RUNNING":
            continue
        record = dict(state.get(entry["id"], {}))
        category, evidence = _classify_running_entry(record)
        if category == "AUTO-FAILED":
            record["status"] = "FAILED"
            _append_audit_line(record, "reconcile", evidence)
            state[entry["id"]] = record
        if category:
            lines.append(f'{entry["id"]}  {category}  {evidence}')
    return lines


def _cmd_reconcile(args: argparse.Namespace) -> int:
    """Implements the ``reconcile`` subcommand — see ``main``'s subparser
    setup. Also invoked at the top of ``next`` (never in ``status``).

    Loads the queue + state, runs ``_reconcile_running_entries`` under the
    same ``_state_lock`` span as every other state-mutating subcommand, and
    prints the resulting listing lines to stdout (one per flagged entry).
    Returns a process exit code (0 on success, 1 when the queue file is
    missing/malformed — printed to stderr, mirroring ``_cmd_status``).
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = load_queue(queue_path)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with _state_lock(state_path):
        state = load_state(state_path)
        lines = _reconcile_running_entries(entries, state)
        save_state(state_path, state)

    for line in lines:
        print(line)
    return 0


def _cmd_reset(args: argparse.Namespace) -> int:
    """Implements the ``reset`` subcommand — see ``main``'s subparser setup.

    Requeues an entry currently ``RUNNING`` or ``FAILED`` back to
    ``QUEUED`` (design SSOT §4c Fix-1 point 4 — the Airflow
    clear/Temporal reset analog): ``attempts`` increments (initialized to
    0 when absent) and an audit line is appended. Any other current
    status (including unknown-id) is a caller-facing error — printed to
    stderr, exit 1, zero mutation — mirroring ``_cmd_mark_running``.

    Also pops ``runId``/``sessionDir``/``dispatched_at`` from the record:
    those name the crashed attempt's now-dead run, and a QUEUED entry has
    no live run — carrying them forward would leave a stale ``runId``
    sitting next to a terminal wf-record once Task 12's reconcile ships,
    which would misread the freshly re-dispatched attempt as the
    already-finished one and force-FAIL it.
    """
    resolved = _resolve_paths_and_validate_id(args, "reset")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with _state_lock(state_path):
        state = load_state(state_path)
        existing = state.get(args.change_id, {})
        current_status = existing.get("status", QUEUED)
        if current_status not in ("RUNNING", "FAILED"):
            print(
                f'reset: entry "{args.change_id}" is not RUNNING or FAILED '
                f"(status={current_status!r}) — refusing to requeue "
                "without mutation.",
                file=sys.stderr,
            )
            return 1

        record = dict(existing)
        record["status"] = QUEUED
        record["attempts"] = record.get("attempts", 0) + 1
        for stale_field in ("runId", "sessionDir", "dispatched_at"):
            record.pop(stale_field, None)
        _append_audit_line(record, "reset", args.reason)
        state[args.change_id] = record
        save_state(state_path, state)
    return 0


def _cmd_force_fail(args: argparse.Namespace) -> int:
    """Implements the ``force-fail`` subcommand — see ``main``'s subparser
    setup.

    Transitions an entry currently ``RUNNING`` to ``FAILED`` (design SSOT
    §4c Fix-1 point 4 — the mark-failed/terminate analog): an audit line
    is appended; the resulting FAILED status counts toward
    ``_check_circuit_breaker`` naturally (no separate breaker logic — it
    reads ``effective_entries`` status the same as any other FAILED
    entry). Any status other than RUNNING (including unknown-id) is a
    caller-facing error — printed to stderr, exit 1, zero mutation.
    """
    resolved = _resolve_paths_and_validate_id(args, "force-fail")
    if isinstance(resolved, int):
        return resolved
    _, state_path = resolved

    with _state_lock(state_path):
        state = load_state(state_path)
        existing = state.get(args.change_id, {})
        if existing.get("status") != "RUNNING":
            print(
                f'force-fail: entry "{args.change_id}" is not RUNNING '
                f'(status={existing.get("status", QUEUED)!r}) — refusing '
                "to transition without mutation.",
                file=sys.stderr,
            )
            return 1

        record = dict(existing)
        record["status"] = "FAILED"
        _append_audit_line(record, "force-fail", args.reason)
        state[args.change_id] = record
        save_state(state_path, state)
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    """Implements the ``status`` subcommand — see ``main``'s subparser setup.

    Prints a one-screen plain-text overview to stdout: one line per queue
    entry, in queue order (``effective_entries`` preserves ``load_queue``'s
    file order), carrying id + effective status + ``runId`` (when recorded)
    + ``reason`` (only for SKIPPED/FAILED — a record re-marked done can
    retain a stale ``reason`` field, so this guard is deliberate, not
    incidental), followed by a final totals line (count per status). This
    is the first thing a fresh session reads to take over a batch, so the
    format is kept grep-friendly and stable: one ``key=value`` per field
    after the id and status columns.

    Returns a process exit code (0 on success, 1 when the queue file is
    missing/malformed — printed to stderr, mirroring ``_cmd_mark``).
    """
    project_path = Path(args.project)
    queue_path = project_path / "docs" / "loom" / "QUEUE.toml"
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = load_queue(queue_path)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with _state_lock(state_path):
        state = load_state(state_path)
        merged = effective_entries(entries, state)

        totals: dict[str, int] = {}
        for entry in merged:
            status = entry["status"]
            totals[status] = totals.get(status, 0) + 1

            fields = [entry["id"], status]
            if "runId" in entry:
                fields.append(f'runId={entry["runId"]}')
            if status in ("SKIPPED", "FAILED") and "reason" in entry:
                fields.append(f'reason={entry["reason"]}')
            print("  ".join(fields))

        totals_fields = " ".join(
            f"{status}={count}" for status, count in sorted(totals.items())
        )
        print(f"total={len(merged)} {totals_fields}".rstrip())
    return 0


def _skip_entry(state: dict, state_path: Path, change_id: str, reason: str) -> None:
    """Record ``SKIPPED`` + ``reason`` for change_id, persist, notice to stderr.

    Shared by ``_cmd_next``'s two skip sites (freeze-predicate failure and
    the post-worktree uncommitted-plan check) — never silent: every skip
    writes state AND prints one line to stderr. Record shape matches
    ``_cmd_mark``'s ``failed``/``done`` records.
    """
    record = dict(state.get(change_id, {}))
    record["status"] = "SKIPPED"
    record["reason"] = reason
    state[change_id] = record
    save_state(state_path, state)
    print(f"next: skipping {change_id!r} — {reason}", file=sys.stderr)


def _teardown_worktree(project_path: Path, worktree_path: Path, branch: str) -> None:
    """Remove a worktree + branch that ``_cmd_next`` just created.

    Used only on the uncommitted-plan skip path: ``SKIPPED`` has no
    automatic path back to ``QUEUED`` and ``status`` does not surface the
    worktree field, so a leftover worktree/branch would be undiscoverable
    by an operator — tear both down so a later re-queue starts clean.
    Fails loud with ``QueueError`` (git stderr included) if either git
    command fails; a half-done teardown must not be swallowed.
    """
    removal = subprocess.run(
        ["git", "-C", str(project_path), "worktree", "remove", str(worktree_path)],
        capture_output=True,
        text=True,
    )
    if removal.returncode != 0:
        _fail(
            f'"git worktree remove {worktree_path}" failed in '
            f'"{project_path}" (exit {removal.returncode}): '
            f"{removal.stderr.strip()}",
            fn="_teardown_worktree",
        )
    deletion = subprocess.run(
        ["git", "-C", str(project_path), "branch", "-D", branch],
        capture_output=True,
        text=True,
    )
    if deletion.returncode != 0:
        _fail(
            f'"git branch -D {branch}" failed in "{project_path}" '
            f"(exit {deletion.returncode}): {deletion.stderr.strip()}",
            fn="_teardown_worktree",
        )


def _uncommitted_plan_reason(change_id: str, plan_path: Path) -> str:
    """Skip reason for a plan the worktree cannot see (never committed)."""
    return (
        f'entry "{change_id}" plan not found in its worktree at '
        f'"{plan_path}" — present in the main checkout but never '
        "committed, so the worktree (branched from HEAD) does not "
        "see it (plan §Branch base note)."
    )


def _dispatch_entry(
    state: dict,
    state_path: Path,
    entry: dict,
    worktree_path: Path,
    plan_path: Path,
    skills_root: Path,
    branch: str,
) -> None:
    """Record ``RUNNING`` for entry and print its Workflow args to stdout.

    Payload field names match ``driver_10_guard.js``'s ``guardArgs``
    REQUIRED_FIELDS, ``driver_50_seg3.js``'s ``planPath`` guard, and
    ``runSegment3``'s optional ``args.branch`` (whole-branch review
    station). ``projectPath`` is the worktree path (not the main checkout)
    and ``planPath`` is resolved *inside* that worktree.

    Also records ``dispatched_at`` — a wall-clock ISO-8601 UTC timestamp
    (design SSOT §4c Fix 1 revised design point 1). This CLI is a
    fresh process per invocation, so it is exempt from Workflow
    determinism rules; the timestamp seeds ``reconcile``'s staleness
    grace-window checks (Task 12) and is not itself part of the
    dispatch payload.
    """
    record = dict(state.get(entry["id"], {}))
    record["status"] = "RUNNING"
    record["branch"] = branch
    record["worktree"] = str(worktree_path)
    record["dispatched_at"] = datetime.now(timezone.utc).isoformat()
    state[entry["id"]] = record
    save_state(state_path, state)

    payload = {
        "segment": 3,
        "changeId": entry["id"],
        "projectPath": str(worktree_path.resolve()),
        "planPath": str(plan_path),
        "budgets": entry["budgets"],
        "models": entry.get("models", {}),
        "skillsRoot": str(skills_root),
        "branch": branch,
    }
    print(json.dumps(payload))


def _check_circuit_breaker(entries: list[dict]) -> tuple[str, str] | None:
    """Task 10 circuit breaker: two most recent terminal entries both FAILED.

    ``entries`` is queue-order ``effective_entries`` output. Only ``DONE``
    and ``FAILED`` count as terminal — ``SKIPPED`` and ``QUEUED``/``RUNNING``
    do not (plan §Settled open questions 3). Returns the halting pair's ids
    ``(older, newer)`` when the two most recent terminal entries are both
    ``FAILED`` and adjacent in that terminal-only sequence; else ``None``.

    "Most recent" is measured by QUEUE.toml file position — a positional
    proxy for recency that is sound only under v1.1's sequential-only,
    no-retry dispatch model (hand-editing queue-state.json to retry an
    earlier entry out of turn breaks the equivalence).
    """
    terminal = [e for e in entries if e["status"] in ("DONE", "FAILED")]
    if len(terminal) < 2:
        return None
    older, newer = terminal[-2], terminal[-1]
    if older["status"] == "FAILED" and newer["status"] == "FAILED":
        return older["id"], newer["id"]
    return None


def _halt_notice_if_tripped(entries: list[dict], override_halt: bool) -> bool:
    """Print the HALT notice and return True iff the breaker should fire.

    Wraps ``_check_circuit_breaker`` with the print-and-decide shell so
    ``_cmd_next`` stays a plain ``if _halt_notice_if_tripped(...): return 3``
    — keeps the caller's body short (house 50-line function ceiling).
    ``override_halt`` short-circuits to False without evaluating the
    predicate.
    """
    if override_halt:
        return False
    halt_pair = _check_circuit_breaker(entries)
    if halt_pair is None:
        return False
    older_id, newer_id = halt_pair
    print(
        "next: HALT — circuit breaker tripped: two consecutive FAILED "
        f"entries ({older_id!r} then {newer_id!r}); refusing to select a "
        "next entry (systemic-failure signal). Pass --override-halt to "
        "proceed anyway.",
        file=sys.stderr,
    )
    return True


_TERMINAL_STATUSES = frozenset({"DONE", "FAILED", "SKIPPED"})


def _describe_non_terminal_entry(entry: dict, state: dict) -> dict:
    """Build one loud enumeration record for an entry blocking ``next``'s
    ``done`` verdict (Task 13, design SSOT §4c Fix 1 revised design point 5).

    RUNNING entries reuse ``_classify_running_entry`` so the same
    SUSPECT/SUSPECT-COMPLETE evidence ``reconcile`` already prints to stderr
    also lands here, in the machine-readable stdout payload. A QUEUED entry
    should never reach this point in practice — the scan above dispatches or
    SKIPs every QUEUED entry it sees in the same invocation — but gets a
    generic description rather than being assumed impossible, since this
    function's whole job is to never let ``done`` go silent.
    """
    record = state.get(entry["id"], {})
    if entry["status"] == "RUNNING":
        _category, evidence = _classify_running_entry(record)
        reason = evidence or "in flight, no staleness evidence yet"
    else:
        reason = f'status={entry["status"]!r}, not selected by this scan'
    return {"id": entry["id"], "status": entry["status"], "reason": reason}


def _cmd_next(args: argparse.Namespace) -> int:
    """Implements the ``next`` subcommand — see ``main``'s subparser setup.

    Runs ``_reconcile_running_entries`` first (Task 12 — reconcile's logic,
    never ``_cmd_status``'s), so a stranded RUNNING entry with definitive
    wf-record evidence is force-FAILED (freeing up the circuit breaker /
    done check) before this scan below ever runs. Reconcile notices go to
    stderr, same channel as the skip/HALT notices below.

    Scans effective entries in queue order for the first one that is both
    ``QUEUED`` and eligible. An entry that fails ``check_frozen``
    (validator non-zero, or plan missing in the main checkout) is recorded
    ``SKIPPED`` with the predicate's reason, a one-line notice goes to
    stderr, and the scan advances to the next ``QUEUED`` entry — Task 9 of
    docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md
    ("ineligible entries are marked SKIPPED loudly, never silently").
    Nothing is ever silent and one bad entry never blocks the queue.

    **Invariant** (plan §Branch base note): ``ensure_worktree`` branches
    from the project's current HEAD, so freezing implies the change-folder
    + plan are committed — the worktree sees them too. That invariant can
    be violated by a plan edited/created after the freeze check ran but
    never committed, so a defensive re-check runs *between*
    ``ensure_worktree`` and recording ``RUNNING``: if
    ``<worktree_path>/<entry["plan"]>`` is not a file, this entry is ALSO
    recorded ``SKIPPED`` (reason names the uncommitted-plan cause) instead
    of ``RUNNING``, with the same notice-and-advance semantics as the
    freeze-predicate skip above — and the worktree + branch this call just
    created are torn down (``_teardown_worktree``), so a later re-queue
    starts clean instead of leaving an undiscoverable leftover.

    On the first entry that clears both checks: ``_dispatch_entry`` records
    ``RUNNING`` (+ ``branch``, ``worktree``) in state and prints ONE JSON
    object to stdout carrying the driver's ready-to-use Workflow args (see
    its docstring for the field contract). When no entry gets dispatched
    (empty queue, or every remaining ``QUEUED`` entry got skipped), ``done``
    is derived from ``terminal_count == total`` (Task 13, design SSOT §4c
    Fix 1 revised design point 5) rather than assumed: DONE/FAILED/SKIPPED
    are the terminal set (SKIPPED has no automatic path back to QUEUED, so
    it counts as final here the same way it already does for dispatch
    purposes). If any entry is still QUEUED or RUNNING, ``{"done": false}``
    is printed alongside a ``non_terminal`` list (id + status + reason per
    entry, via ``_describe_non_terminal_entry``) instead of silently
    claiming the batch is finished. Exits 0 either way.

    **Circuit breaker** (Task 10, plan §Settled open questions 3): before
    selecting, ``_halt_notice_if_tripped`` scans for two consecutive FAILED
    entries among the most recent terminal (DONE/FAILED) outcomes. If
    tripped, this exits 3 with a HALT message naming both ids instead of
    scanning at all — unless ``args.override_halt`` is set, which bypasses
    the check entirely.

    Only machine-readable JSON goes to stdout (the dispatch payload, or
    ``{"done": true}``); all human-facing notices (skip reasons, the HALT
    message) go to stderr, mirroring ``_cmd_mark``/``_cmd_status``. A
    ``QueueError`` raised mid-scan by ``ensure_worktree``/
    ``_teardown_worktree`` is not caught here — ``main`` catches it at the
    dispatch level so it exits 1 like a ``load_queue`` failure, instead of
    propagating as a raw traceback.
    """
    project_path = Path(args.project).resolve()
    skills_root = Path(args.skills_root).resolve()
    queue_path = (
        Path(args.queue) if args.queue else project_path / "docs" / "loom" / "QUEUE.toml"
    )
    state_path = project_path / "docs" / "loom" / "queue-state.json"

    try:
        entries = load_queue(queue_path)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1

    with _state_lock(state_path):
        state = load_state(state_path)

        # Task 12: reconcile RUNNING entries against wf-record evidence
        # BEFORE the normal scan (never inside _cmd_status — that stays a
        # pure query). Mutates `state` in place for any AUTO-FAILED
        # transitions; must be saved here since a `{"done": true}` or
        # skip-only run below may otherwise never call save_state again.
        reconcile_lines = _reconcile_running_entries(entries, state)
        if reconcile_lines:
            save_state(state_path, state)
            for line in reconcile_lines:
                print(line, file=sys.stderr)

        merged = effective_entries(entries, state)

        if _halt_notice_if_tripped(merged, args.override_halt):
            return 3

        for entry in merged:
            if entry["status"] != QUEUED:
                continue

            eligible, reason = check_frozen(entry, project_path, skills_root)
            if not eligible:
                _skip_entry(state, state_path, entry["id"], reason)
                continue

            worktree_path, branch = ensure_worktree(project_path, entry["id"])
            plan_path = (worktree_path / entry["plan"]).resolve()

            if not plan_path.is_file():
                _teardown_worktree(project_path, worktree_path, branch)
                _skip_entry(
                    state,
                    state_path,
                    entry["id"],
                    _uncommitted_plan_reason(entry["id"], plan_path),
                )
                continue

            _dispatch_entry(
                state, state_path, entry, worktree_path, plan_path, skills_root, branch
            )
            return 0

        final_merged = effective_entries(entries, state)
        non_terminal = [
            e for e in final_merged if e["status"] not in _TERMINAL_STATUSES
        ]
        if non_terminal:
            payload = {
                "done": False,
                "non_terminal": [
                    _describe_non_terminal_entry(e, state) for e in non_terminal
                ],
            }
        else:
            payload = {"done": True}
        print(json.dumps(payload))
        return 0


def _assert_valid_change_id(id_value: str, *, fn: str) -> None:
    """Trust-boundary re-assertion of the changeId allow-list.

    Shared by ``load_queue``, ``check_frozen``, ``ensure_worktree`` — the
    same check was copy-pasted at all three sites (Rule of Three), so it is
    extracted here and routed through ``_fail(fn=...)``. Raises
    ``QueueError`` when ``id_value`` fails ``_CHANGE_ID_ALLOWED_PATTERN`` or
    contains ``".."``.
    """
    if not _CHANGE_ID_ALLOWED_PATTERN.match(id_value) or ".." in id_value:
        _fail(
            f'"{id_value}" must match {_CHANGE_ID_ALLOWED_PATTERN.pattern} '
            f'(letters, digits, dot, underscore, hyphen only; no ".."); '
            f"received {id_value!r}.",
            fn=fn,
        )


def _build_parser() -> argparse.ArgumentParser:
    """Top-level argparse setup: ``mark``, ``mark-running``, ``reset``,
    ``force-fail``, ``status``, ``reconcile``, ``next`` subcommands."""
    parser = argparse.ArgumentParser(
        prog="batch_queue.py", description="loom-pipeline batch mode bookkeeping"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    mark_parser = subparsers.add_parser(
        "mark", help="record done/failed status for a queue entry"
    )
    mark_parser.add_argument("change_id")
    mark_parser.add_argument("status", choices=["done", "failed"])
    mark_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    mark_parser.add_argument("--run-id", dest="run_id")
    mark_parser.add_argument("--reason")
    mark_parser.set_defaults(func=_cmd_mark)

    mark_running_parser = subparsers.add_parser(
        "mark-running",
        help="record runId + session-dir on an entry currently RUNNING",
    )
    mark_running_parser.add_argument("change_id")
    mark_running_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    mark_running_parser.add_argument(
        "--run-id", dest="run_id", required=True
    )
    mark_running_parser.add_argument(
        "--session-dir", dest="session_dir", required=True
    )
    mark_running_parser.set_defaults(func=_cmd_mark_running)

    reset_parser = subparsers.add_parser(
        "reset",
        help="requeue a RUNNING or FAILED entry back to QUEUED (attempts+=1, audit line)",
    )
    reset_parser.add_argument("change_id")
    reset_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    reset_parser.add_argument("--reason", help="optional operator note for the audit line")
    reset_parser.set_defaults(func=_cmd_reset)

    force_fail_parser = subparsers.add_parser(
        "force-fail",
        help="transition a RUNNING entry to FAILED (audit line; counts toward the circuit breaker)",
    )
    force_fail_parser.add_argument("change_id")
    force_fail_parser.add_argument(
        "--reason", required=True, help="operator note for the audit line"
    )
    force_fail_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    force_fail_parser.set_defaults(func=_cmd_force_fail)

    status_parser = subparsers.add_parser(
        "status", help="print a one-screen overview of the queue"
    )
    status_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    status_parser.set_defaults(func=_cmd_status)

    reconcile_parser = subparsers.add_parser(
        "reconcile",
        help="scan RUNNING entries against wf-record evidence: auto-FAIL on "
        "failed/killed, flag SUSPECT-COMPLETE/SUSPECT otherwise (also run "
        "at the top of `next`; never in `status`)",
    )
    reconcile_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    reconcile_parser.set_defaults(func=_cmd_reconcile)

    _add_next_subparser(subparsers)

    return parser


def _add_next_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``next`` subcommand's arguments (split out of
    ``_build_parser`` to keep that function under the house length ceiling).
    """
    next_parser = subparsers.add_parser(
        "next",
        help="pick the next QUEUED entry, ready its worktree, print its Workflow args as JSON",
    )
    next_parser.add_argument(
        "--project", required=True, help="target project root"
    )
    next_parser.add_argument(
        "--skills-root",
        dest="skills_root",
        required=True,
        help="absolute path to the monkey-skills checkout / plugin source root",
    )
    next_parser.add_argument(
        "--queue",
        help="override path to QUEUE.toml (default: <project>/docs/loom/QUEUE.toml)",
    )
    next_parser.add_argument(
        "--override-halt",
        dest="override_halt",
        action="store_true",
        default=False,
        help="bypass the consecutive-FAILED circuit breaker (Task 10)",
    )
    next_parser.set_defaults(func=_cmd_next)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse argv and dispatch to the selected subcommand's ``func``.

    Catches ``QueueError`` at this single dispatch site: ``mark``/``status``
    already catch their own ``load_queue`` failures internally (so this is a
    no-op for them), but ``next`` can raise ``QueueError`` mid-scan via
    ``ensure_worktree``/``_teardown_worktree`` — this ensures that exits 1
    with a stderr message instead of propagating as a raw traceback.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except QueueError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
