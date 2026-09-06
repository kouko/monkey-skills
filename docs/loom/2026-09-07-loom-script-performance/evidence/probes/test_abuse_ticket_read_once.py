#!/usr/bin/env python3
"""Adversarial probes for W1-05 (single ticket read in validate / update-blockers).

Every literal here is an oracle pinned against TODAY's behaviour of
`loom-workflow/skills/decision-map/scripts/map_store.py` and
`map_transaction.py`, run BEFORE the read-once fix lands. A future
implementation that reads each ticket once must not change: which
error message surfaces first when several tickets are simultaneously
broken, the bytes written by `update-blockers`, or the behaviour on
empty/absent ticket directories. Where today's call count is worse
than the plan's own "2N" estimate, that gap is recorded as a finding
rather than silently re-derived by the implementer.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = (
    Path(__file__).resolve().parents[5] / "loom-workflow" / "skills"
    / "decision-map" / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))

import map_store  # noqa: E402
import map_transaction  # noqa: E402

MAP_MD_ACTIVE = """---
map-id: outcome
schema_version: 3
state: active
---

## Destination

Improve the outcome.
user-ratified: kouko, 2026-08-30
- DA-1: Slice works | state: open | kind: objective

## Notes

Keep charting.

## Decisions-so-far

## Not-yet-specified (fog)

## Out-of-scope
"""

MAP_MD_REUSED_FOG = """---
map-id: outcome
schema_version: 3
state: active
---

## Destination

Improve the outcome.
user-ratified: kouko, 2026-08-30
- DA-1: Slice works | state: open | kind: objective

## Notes

Keep charting.

## Decisions-so-far

## Not-yet-specified (fog)

- F-1: reused fog id

## Out-of-scope

- F-1: already handled elsewhere
"""

TICKET_VALID = """---
type: research
status: open
claim: null
graduated-from: null
---

Ticket body.
"""

TICKET_BAD_TYPE = """---
type: bogus
status: open
claim: null
graduated-from: null
---

Ticket body.
"""

TICKET_UNPARSABLE = "not even frontmatter at all, no dashes here\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_map(base: Path, map_md: str, tickets: dict[str, str]) -> Path:
    map_dir = base / "docs" / "loom" / "maps" / "outcome"
    _write(map_dir / "MAP.md", map_md)
    for name, text in tickets.items():
        _write(map_dir / "tickets" / name, text)
    return map_dir


def _valid_map_n_tickets(base: Path, n: int) -> Path:
    tickets = {f"t{i}.md": TICKET_VALID for i in range(n)}
    return _build_map(base, MAP_MD_ACTIVE, tickets)


# --- 1. call count -------------------------------------------------------


def test_validate_n_open_tickets_read_ticket_count_equals_n(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """validate() on a 6-ticket valid map must call read_ticket exactly
    N times, not 2N — today it double-reads every ticket (once in
    _check_tickets, once again in _check_monotonic_relations)."""
    n = 6
    map_dir = _valid_map_n_tickets(tmp_path, n)
    calls: list[Path] = []
    original = map_store.read_ticket

    def counting_wrapper(path: Path):
        calls.append(Path(path))
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", counting_wrapper)
    code, message = map_store.validate(map_dir)
    assert code == 0, message
    # RED today: len(calls) == 2 * n == 12, not n == 6.
    assert len(calls) == n


def test_update_blockers_locked_n_tickets_read_ticket_count_equals_n(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The public update-blockers entry point on a 6-ticket valid map
    must call read_ticket exactly N times.

    RED today, and worse than the plan's own "2N" estimate: measured
    4N + 1 = 25 for N=6 (1 for require_ticket_mutable's own read, N
    for the blocked-by graph pass, N for the status pass, then a
    *nested* map_store.validate() call inside _require_valid_store
    that alone re-reads every ticket 2N more times). A fix that only
    dedupes validate()'s own 2N->N does not by itself bring this call
    site down to N; _update_blockers_locked's own two N-length passes
    (graph, statuses) must also share one read. Recorded as a finding,
    not silently re-derived.
    """
    n = 6
    map_dir = _valid_map_n_tickets(tmp_path, n)
    rev = map_transaction.capture_revision(map_dir)
    calls: list[Path] = []
    original = map_store.read_ticket

    def counting_wrapper(path: Path):
        calls.append(Path(path))
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", counting_wrapper)
    result = map_transaction.update_blockers(
        map_dir, "t0", ["t1"], operation_id="op-1", expected_revision=rev
    )
    assert result.applied is True
    assert len(calls) == n


# --- 2. error precedence --------------------------------------------------


def test_validate_bad_type_and_reused_fog_together_reports_check_tickets_first(
    tmp_path: Path,
) -> None:
    """When ticket a.md has an invalid type (_check_tickets) AND the
    Map separately reuses fog id F-1 (_check_monotonic_relations),
    today's validate() raises the _check_tickets error first because
    _check_monotonic_relations never runs once _check_tickets raises."""
    map_dir = _build_map(
        tmp_path,
        MAP_MD_REUSED_FOG,
        {"a.md": TICKET_BAD_TYPE, "b.md": TICKET_VALID},
    )
    code, message = map_store.validate(map_dir)
    assert code == 2
    assert "type 'bogus' is not one of" in message
    assert "reused" not in message


def test_validate_reused_fog_only_reports_monotonic_message(
    tmp_path: Path,
) -> None:
    """With no per-ticket schema error, validate() surfaces the
    monotonic-relations reused-fog-id message verbatim."""
    map_dir = _build_map(
        tmp_path,
        MAP_MD_REUSED_FOG,
        {"a.md": TICKET_VALID, "b.md": TICKET_VALID},
    )
    code, message = map_store.validate(map_dir)
    assert code == 2
    assert message == (
        "partial fog graduation or fog id reused from graduated or "
        "Out-of-scope history: F-1"
    )


def test_validate_unparsable_a_before_bad_type_z_reports_parse_error(
    tmp_path: Path,
) -> None:
    """a.md (sorted first) has unparsable frontmatter; z.md (sorted
    later) has a semantic type error. Today's per-ticket loop reads
    a.md first and raises its parse error before z.md is ever read —
    sort order, not error kind, decides precedence. A shared pre-read
    must preserve this: it must not parse all tickets structurally
    before running semantic checks in a different order."""
    map_dir = _build_map(
        tmp_path,
        MAP_MD_ACTIVE,
        {"a.md": TICKET_UNPARSABLE, "z.md": TICKET_BAD_TYPE},
    )
    code, message = map_store.validate(map_dir)
    assert code == 2
    assert "missing frontmatter opening" in message
    assert "z.md" not in message


def test_validate_bad_type_a_before_unparsable_z_reports_a_type_error(
    tmp_path: Path,
) -> None:
    """Reverse of the above: a.md (sorted first) has a semantic type
    error; z.md (sorted later) is unparsable. a.md's error surfaces
    first purely because of sort order — z.md is never even opened."""
    map_dir = _build_map(
        tmp_path,
        MAP_MD_ACTIVE,
        {"a.md": TICKET_BAD_TYPE, "z.md": TICKET_UNPARSABLE},
    )
    code, message = map_store.validate(map_dir)
    assert code == 2
    assert "type 'bogus' is not one of" in message
    assert "a.md" in message


# --- 3. update-blockers write identity ------------------------------------


def test_update_blockers_valid_edge_writes_only_target_ticket_bytes(
    tmp_path: Path,
) -> None:
    """A successful update-blockers call rewrites only the target
    ticket's bytes; every other ticket file stays byte-identical."""
    map_dir = _valid_map_n_tickets(tmp_path, 4)
    tickets_dir = map_dir / "tickets"
    before = {p.name: p.read_bytes() for p in sorted(tickets_dir.glob("*.md"))}
    rev = map_transaction.capture_revision(map_dir)
    result = map_transaction.update_blockers(
        map_dir, "t0", ["t1"], operation_id="op-a", expected_revision=rev
    )
    assert result.applied is True
    after_target = (tickets_dir / "t0.md").read_bytes()
    assert b"blocked-by: t1" in after_target
    for name in ("t1.md", "t2.md", "t3.md"):
        assert (tickets_dir / name).read_bytes() == before[name]


def test_update_blockers_self_edge_refuses_and_writes_nothing(
    tmp_path: Path,
) -> None:
    """A self-blocker edge is refused with today's exact message and
    the ticket file is left byte-identical (no partial write)."""
    map_dir = _valid_map_n_tickets(tmp_path, 2)
    ticket_path = map_dir / "tickets" / "t0.md"
    before = ticket_path.read_bytes()
    rev = map_transaction.capture_revision(map_dir)
    with pytest.raises(map_transaction.CloseTransactionError) as excinfo:
        map_transaction.update_blockers(
            map_dir, "t0", ["t0"], operation_id="op-self", expected_revision=rev
        )
    assert "blocked-by self edge is forbidden" in str(excinfo.value)
    assert ticket_path.read_bytes() == before


def test_update_blockers_nonexistent_blocker_refuses_and_writes_nothing(
    tmp_path: Path,
) -> None:
    """A blocker slug naming no sibling ticket file is refused with
    today's exact message and no file is written."""
    map_dir = _valid_map_n_tickets(tmp_path, 2)
    ticket_path = map_dir / "tickets" / "t0.md"
    before = ticket_path.read_bytes()
    rev = map_transaction.capture_revision(map_dir)
    with pytest.raises(map_transaction.CloseTransactionError) as excinfo:
        map_transaction.update_blockers(
            map_dir, "t0", ["ghost"], operation_id="op-ghost", expected_revision=rev
        )
    assert "blocked-by missing target" in str(excinfo.value)
    assert "'ghost'" in str(excinfo.value)
    assert ticket_path.read_bytes() == before


# --- 4. empty / absent ------------------------------------------------------


def test_validate_absent_tickets_dir_passes_with_no_ticket_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No tickets/ directory at all: _check_tickets short-circuits and
    validate() passes cleanly with zero read_ticket calls."""
    map_dir = tmp_path / "docs" / "loom" / "maps" / "outcome"
    _write(map_dir / "MAP.md", MAP_MD_ACTIVE)
    calls: list[Path] = []
    original = map_store.read_ticket

    def counting_wrapper(path: Path):
        calls.append(Path(path))
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", counting_wrapper)
    code, message = map_store.validate(map_dir)
    assert code == 0, message
    assert calls == []


def test_validate_empty_tickets_dir_passes_with_no_ticket_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """tickets/ exists but is empty: same clean pass, zero reads."""
    map_dir = tmp_path / "docs" / "loom" / "maps" / "outcome"
    _write(map_dir / "MAP.md", MAP_MD_ACTIVE)
    (map_dir / "tickets").mkdir(parents=True)
    calls: list[Path] = []
    original = map_store.read_ticket

    def counting_wrapper(path: Path):
        calls.append(Path(path))
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", counting_wrapper)
    code, message = map_store.validate(map_dir)
    assert code == 0, message
    assert calls == []


def test_validate_non_markdown_file_in_tickets_dir_is_silently_ignored(
    tmp_path: Path,
) -> None:
    """A non-.md file sitting in tickets/ is invisible to the *.md
    glob and does not affect validate()'s outcome."""
    map_dir = tmp_path / "docs" / "loom" / "maps" / "outcome"
    _write(map_dir / "MAP.md", MAP_MD_ACTIVE)
    _write(map_dir / "tickets" / "notes.txt", "not a ticket file at all")
    code, message = map_store.validate(map_dir)
    assert code == 0, message


# --- 5. concurrency-ish: file vanishes between glob and read ---------------


def test_validate_ticket_deleted_mid_scan_raises_deterministic_read_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Simulate a ticket file disappearing between the sorted glob and
    its own read: today's per-ticket loop already froze the file list
    at glob time, so the later file (c.md) still gets attempted and
    fails with a deterministic MapStoreError / exit 1 — not a crash,
    not a silently-skipped ticket. A shared pre-read that instead
    globs once and reads everything up front must preserve this exact
    outcome (freeze order, then fail loudly on the missing file) — if
    it instead skips the vanished file or reorders remaining tickets,
    that is a behaviour change worth a finding, not a silent pass."""
    map_dir = _valid_map_n_tickets(tmp_path, 3)
    tickets_dir = map_dir / "tickets"
    # rename t0/t1/t2 -> a/b/c so "c.md" sorts last and is the victim.
    for old, new in (("t0.md", "a.md"), ("t1.md", "b.md"), ("t2.md", "c.md")):
        (tickets_dir / old).rename(tickets_dir / new)

    victim = tickets_dir / "c.md"
    original = map_store.read_ticket
    call_n = {"n": 0}

    def unlinking_wrapper(path: Path):
        call_n["n"] += 1
        if call_n["n"] == 1:
            victim.unlink()
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", unlinking_wrapper)
    code, message = map_store.validate(map_dir)
    assert code == 1
    assert "cannot read" in message
    assert "c.md" in message


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
