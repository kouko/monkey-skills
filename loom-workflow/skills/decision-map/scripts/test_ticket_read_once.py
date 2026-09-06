#!/usr/bin/env python3
"""W1-05: validate() and update-blockers must read each ticket once.

Two cases from the plan (docs/loom/2026-09-07-loom-script-performance/
plan.md, task W1-05):

- A5 positive (`validate-findings-identical`): on an N-ticket store
  whose only violation is caught by `_check_monotonic_relations`,
  `validate()` must report the exact same finding text as today, while
  calling `map_store.read_ticket` exactly N times, not 2N (today's
  `_check_tickets` pass plus `_check_monotonic_relations`'s own
  re-read).
- A5 negative (`update-blockers-files-identical`): a successful
  `update_blockers()` call must write exactly the same bytes as today
  (target ticket rewritten, every sibling byte-identical), while the
  call's own two N-length passes (blocked-by graph, statuses) collapse
  into one shared read — the nested `map_store.validate()` inside
  `_require_valid_store` still contributes its own N reads, so the
  measured total is 2N + 1, not 4N + 1 (plan amendment dfbdfdf9).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_store  # noqa: E402
import map_transaction  # noqa: E402

MAP_MD_ACTIVE_REUSED_FOG = """---
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

TICKET_VALID = """---
type: research
status: open
claim: null
graduated-from: null
---

Ticket body.
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_map(base: Path, map_md: str, n: int) -> Path:
    map_dir = base / "docs" / "loom" / "maps" / "outcome"
    _write(map_dir / "MAP.md", map_md)
    for i in range(n):
        _write(map_dir / "tickets" / f"t{i}.md", TICKET_VALID)
    return map_dir


def _count_read_ticket(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    calls: list[Path] = []
    original = map_store.read_ticket

    def counting_wrapper(path: Path):
        calls.append(Path(path))
        return original(path)

    monkeypatch.setattr(map_store, "read_ticket", counting_wrapper)
    return calls


def test_validate_findings_identical_read_ticket_count_is_n(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """N=6 all-valid tickets, a Map-level reused-fog-id violation that
    only `_check_monotonic_relations` can catch: the finding text must
    be exactly today's message, and `read_ticket` must be called N
    times (6), not 2N (12)."""
    n = 6
    map_dir = _build_map(tmp_path, MAP_MD_ACTIVE_REUSED_FOG, n)
    calls = _count_read_ticket(monkeypatch)

    code, message = map_store.validate(map_dir)

    assert code == 2
    assert message == (
        "partial fog graduation or fog id reused from graduated or "
        "Out-of-scope history: F-1"
    )
    assert len(calls) == n


def test_update_blockers_files_identical_own_pass_plus_nested_validate_is_2n_plus_1(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """N=6 all-valid tickets: a successful `update_blockers()` call
    rewrites only the target ticket's bytes — every sibling stays
    byte-identical — while the total `read_ticket` call count drops
    from today's 4N + 1 (25) to 2N + 1 (13): the function's own
    blocked-by-graph and status passes now share one read (N), plus
    `require_ticket_mutable`'s own read of the target (1), plus the
    nested `map_store.validate()` inside `_require_valid_store` (its
    own N, unchanged by this task per the plan amendment)."""
    n = 6
    map_dir = _build_map(tmp_path, MAP_MD_ACTIVE, n)
    tickets_dir = map_dir / "tickets"
    before = {p.name: p.read_bytes() for p in sorted(tickets_dir.glob("*.md"))}
    rev = map_transaction.capture_revision(map_dir)
    calls = _count_read_ticket(monkeypatch)

    result = map_transaction.update_blockers(
        map_dir, "t0", ["t1"], operation_id="op-1", expected_revision=rev
    )

    assert result.applied is True
    after_target = (tickets_dir / "t0.md").read_bytes()
    assert b"blocked-by: t1" in after_target
    for name in (f"t{i}.md" for i in range(1, n)):
        assert (tickets_dir / name).read_bytes() == before[name]
    assert len(calls) == 2 * n + 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
