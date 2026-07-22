"""RED-first tests for the same-period identity predicate (Slice C, Task 3).

`kpi_store.same_period(a, b)` decides whether two stored observations describe
the SAME real period, over the raw `(period_start, period_end)` identity fields
T2 added to the point. The contract (brief §Period model):
  - EXACT match first: byte-identical `(period_start, period_end)` pair.
  - Snap FALLBACK (only when exact fails): `period_end` snapped to its calendar
    month-end is equal AND the duration-in-quarters (`qtrs`; 0=instant, 1..4)
    is equal — this absorbs the ~1% boundary drift without merging two
    genuinely different periods.
  - No false merge: same snapped end-date but different `qtrs` (the event-style
    instant-vs-annual case) must NOT match.
`_period_sort_key(point)` orders by `period_end`, then a `qtrs` tiebreak.

No `@req` tag: this dispatch's plan (docs/loom/plans/2026-07-22-kpi-observation-
history.md) binds tasks by "Brief item covered", not registered loom-spec
REQ-ids, so there is no id in the living-spec namespace to bind to (same
convention as test_kpi_store_enumerate.py).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPT = (
    _TESTS_DIR.parent
    / "skills"
    / "analysis-kpi"
    / "scripts"
    / "kpi_store.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("kpi_store_period_identity", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_store_period_identity"] = module
    spec.loader.exec_module(module)
    return module


def _pt(start, end, kind):
    """A minimal point carrying only the period-identity fields the predicate
    reads — same_period is pure logic over these three, no store I/O.
    """
    return {"period_start": start, "period_end": end, "period_kind": kind}


def test_same_period_exact_and_snap():
    """One predicate, three cases of its contract:
      (a) byte-identical (start, end) -> match (exact);
      (b) end differs by 1 day but snaps to the same month-end AND shares qtrs
          -> match (snap fallback);
      (c) same end-date but different qtrs (instant vs annual) -> NO match
          (the no-false-merge guard); plus a different-month-end no-match.
    """
    module = _load_module()

    # (a) EXACT: identical raw (start, end) pair.
    a1 = _pt("2024-01-01", "2024-12-31", "duration")
    a2 = _pt("2024-01-01", "2024-12-31", "duration")
    assert module.same_period(a1, a2) is True

    # (b) SNAP FALLBACK: end 2024-12-30 vs 2024-12-31 (1-day drift) both snap to
    # the Dec month-end, same start -> same qtrs (4). Exact fails (ends differ),
    # fallback fires.
    b1 = _pt("2024-01-01", "2024-12-31", "duration")
    b2 = _pt("2024-01-01", "2024-12-30", "duration")
    assert module.same_period(b1, b2) is True

    # (c) NO FALSE MERGE — same end-date, different qtrs: an instant balance
    # (qtrs 0) vs a full-year duration (qtrs 4), both ending 2024-12-31. Snapped
    # ends match but qtrs differ -> must NOT merge.
    c_instant = _pt(None, "2024-12-31", "instant")
    c_annual = _pt("2024-01-01", "2024-12-31", "duration")
    assert module.same_period(c_instant, c_annual) is False

    # (c') NO FALSE MERGE — different month-end, same qtrs: two annuals ending
    # in different months snap to different month-ends -> must NOT merge.
    d1 = _pt("2024-01-01", "2024-12-31", "duration")
    d2 = _pt("2023-12-01", "2024-11-30", "duration")
    assert module.same_period(d1, d2) is False


def test_same_period_missing_identity_dates_returns_false():
    """Defensive contract: a point lacking a period_end (older points, or the
    None case T2 allows) cannot match by date -> same_period returns False,
    never crashes.
    """
    module = _load_module()

    has_dates = _pt("2024-01-01", "2024-12-31", "duration")
    no_end = _pt("2024-01-01", None, "duration")
    both_none = _pt(None, None, "duration")

    assert module.same_period(no_end, has_dates) is False
    assert module.same_period(has_dates, no_end) is False
    assert module.same_period(both_none, both_none) is False


def test_same_period_refuses_false_merge_vectors():
    """Two false-merge holes the exact and snap paths must BOTH close:
      (F1) a None-start (dateless) duration vs an instant sharing an end-date —
           the EXACT path must NOT merge on the bare (None, end) tuple; a
           dateless span has no evidence it covers the same period as anything.
      (F2) a 15-month transition span vs a 12-month FY sharing a month-end —
           the transition's out-of-[1,4] quarter count must NOT be clamped into
           the bucket to coincide with a real annual.
    Both would silently combine two DIFFERENT fiscal periods, hiding the very
    disagreement `history` exists to surface.
    """
    module = _load_module()

    # (F1) EXACT path: an instant (start None) and a dateless duration (start
    # None — T2 allows an unfinished extraction) share end 2024-12-31, so their
    # raw (start, end) tuples are byte-identical (None, "2024-12-31") — yet they
    # are NOT the same period and must not merge.
    instant = _pt(None, "2024-12-31", "instant")
    degenerate_duration = _pt(None, "2024-12-31", "duration")
    assert module.same_period(instant, degenerate_duration) is False

    # (F2) SNAP path: a 15-month transition FY (2023-10-01 -> 2024-12-31, 457d,
    # ~5 quarters) vs a normal 12-month FY (2024-01-01 -> 2024-12-31, 366d, 4
    # quarters). Both snap to the Dec month-end; the transition's 5-quarter span
    # is out of the 1..4 range and must be refused, not clamped down to 4.
    transition = _pt("2023-10-01", "2024-12-31", "duration")
    normal_fy = _pt("2024-01-01", "2024-12-31", "duration")
    assert module.same_period(transition, normal_fy) is False


def test_same_period_genuine_matches_survive_the_fix():
    """Regression guard: the legitimate exact + snap merges must still fire
    after the false-merge fixes — the fixes remove wrong merges only, never
    weaken a right one.
    """
    module = _load_module()

    # Fully-dated identical (start, end) -> EXACT match survives the fix.
    p1 = _pt("2024-01-01", "2024-12-31", "duration")
    p2 = _pt("2024-01-01", "2024-12-31", "duration")
    assert module.same_period(p1, p2) is True

    # +/-1-day boundary drift, both in-range 4-quarter spans -> SNAP fallback
    # still merges (equal month-end, equal in-range qtrs).
    drift_a = _pt("2024-01-01", "2024-12-31", "duration")
    drift_b = _pt("2024-01-01", "2024-12-30", "duration")
    assert module.same_period(drift_a, drift_b) is True


def test_period_sort_key_orders_by_end_then_qtrs():
    """`_period_sort_key` sorts by period_end (ISO strings sort chronologically),
    with qtrs as the tiebreak when two observations share an end-date.
    """
    module = _load_module()

    earlier = _pt("2024-01-01", "2024-03-31", "duration")
    later_instant = _pt(None, "2024-12-31", "instant")      # end same, qtrs 0
    later_annual = _pt("2024-01-01", "2024-12-31", "duration")  # end same, qtrs 4

    ordered = sorted(
        [later_annual, earlier, later_instant], key=module._period_sort_key
    )
    # earlier end sorts first; on the shared 2024-12-31 end, qtrs 0 before qtrs 4.
    assert ordered == [earlier, later_instant, later_annual]
