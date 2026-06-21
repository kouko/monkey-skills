"""test_aggregate.py — tests for per-skill aggregation + reusability + fingerprint.

Per Plan Part 1 §Task 5 acceptance:
1. test_aggregate_by_skill_groups_correctly — target_pattern glob filters
   to matching skills; sessions are grouped.
2. test_reusability_score_matches_crune_formula — 4-signal weighted sum.
3. test_fingerprint_count_returns_distinct_project_count — sha256 fingerprint
   counts distinct project paths.
4. test_min_session_count_filters_low_signal_skills — < 3 sessions dropped.
5. test_rank_top_n_returns_sorted_desc — top-N sorted by reusability_score.
6. test_aggregate_dedups_T4_overlapping_cluster_signals — T4 🟡 carry-forward:
   N overlapping tool_error_cluster signals from one cluster collapse to 1
   after dedup at aggregate layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from event import Event
from friction_signals import Signal, detect_tool_error_clusters

from aggregate import (
    AGGREGATE_THRESHOLDS,
    AggregateRecord,
    aggregate_by_skill,
    dedup_signals,
    fingerprint_count,
    rank_top_n,
    reusability_score,
    severity_score_for_session,
    signal_fingerprint,
)


def _ev(
    ts: str,
    *,
    session: str = "S1",
    role: str = "user",
    text: str = "",
    skill_invocation: str | None = None,
    tool_error: str | None = None,
) -> Event:
    return Event(
        agent="claude-code",
        session=session,
        ts=ts,
        role=role,
        text=text,
        skill_invocation=skill_invocation,
        tool_error=tool_error,
    )


# ---------------------------------------------------------------------------
# AGGREGATE_THRESHOLDS module constant (Q5)
# ---------------------------------------------------------------------------


def test_aggregate_thresholds_are_q5_defaults():
    """Plan T5 §(d): min_session_count=3, cross_project_count=2 baked verbatim."""
    assert AGGREGATE_THRESHOLDS == {
        "min_session_count": 3,
        "cross_project_count": 2,
    }


# ---------------------------------------------------------------------------
# aggregate_by_skill
# ---------------------------------------------------------------------------


def test_aggregate_by_skill_groups_correctly():
    """target_pattern='loom-code:*' filters to matching invocations;
    2 sessions of loom-code:brainstorming → 1 record with 2 sessions.
    """
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T11:00:00.000Z",
            session="S2",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T12:00:00.000Z",
            session="S3",
            role="assistant",
            skill_invocation="skill-dev-toolkit:skill-judge",  # doesn't match pattern
        ),
    ]
    records = aggregate_by_skill(events, signals=[], target_pattern="loom-code:*")
    assert set(records.keys()) == {"loom-code:brainstorming"}
    rec = records["loom-code:brainstorming"]
    assert sorted(rec.sessions) == ["S1", "S2"]
    assert rec.event_count == 2


def test_aggregate_by_skill_tolerates_none_skill_invocation():
    """Events with skill_invocation=None must not break the filter."""
    events = [
        _ev("2026-05-22T10:00:00.000Z", session="S1", role="user"),  # None
        _ev(
            "2026-05-22T10:01:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
    ]
    records = aggregate_by_skill(events, signals=[], target_pattern="loom-code:*")
    assert set(records.keys()) == {"loom-code:brainstorming"}


def test_aggregate_by_skill_empty_input_returns_empty_dict():
    """Empty events + empty signals → empty dict, no exceptions."""
    records = aggregate_by_skill([], signals=[], target_pattern="loom-code:*")
    assert records == {}


def test_aggregate_by_skill_attaches_signals_by_session():
    """Signals are attached to the AggregateRecord whose sessions include
    the signal's session.
    """
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T11:00:00.000Z",
            session="S2",
            role="assistant",
            skill_invocation="loom-code:writing-plans",
        ),
    ]
    sig_S1 = Signal(
        kind="interrupt_after_brainstorm",
        session="S1",
        ts="2026-05-22T10:01:00.000Z",
        severity="high",
        evidence=[],
    )
    sig_S2 = Signal(
        kind="needs_revision_streak",
        session="S2",
        ts="2026-05-22T11:01:00.000Z",
        severity="mid",
        evidence=[],
    )
    records = aggregate_by_skill(
        events,
        signals=[sig_S1, sig_S2],
        target_pattern="loom-code:*",
    )
    assert {s.session for s in records["loom-code:brainstorming"].signals} == {"S1"}
    assert {s.session for s in records["loom-code:writing-plans"].signals} == {"S2"}


# ---------------------------------------------------------------------------
# reusability_score — crune 4-signal formula
# ---------------------------------------------------------------------------


def test_reusability_score_matches_crune_formula():
    """0.35*frequency + 0.25*timeCost + 0.25*crossProject + 0.15*recency.

    Pin all 4 normalized inputs and verify the weighted sum to 3 decimals.
    """
    rec = AggregateRecord(
        skill_name="loom-code:brainstorming",
        sessions=["S1", "S2", "S3"],
        event_count=10,
        signals=[],
        project_paths={"/p1", "/p2"},
        facet_summary={},
        confidence="low",
        # Pre-computed normalized fields (the 4 crune signals in [0,1]):
        frequency_norm=0.6,
        time_cost_norm=0.5,
        cross_project_norm=0.4,
        recency_norm=0.8,
    )
    expected = 0.35 * 0.6 + 0.25 * 0.5 + 0.25 * 0.4 + 0.15 * 0.8
    assert round(reusability_score(rec), 3) == round(expected, 3)


def test_reusability_score_clamps_to_unit_interval():
    """Defensive: inputs > 1 don't blow past 1; inputs < 0 don't go negative."""
    rec = AggregateRecord(
        skill_name="x",
        sessions=["S1"],
        event_count=1,
        signals=[],
        project_paths=set(),
        facet_summary={},
        confidence="low",
        frequency_norm=2.0,  # out-of-range
        time_cost_norm=-1.0,  # out-of-range
        cross_project_norm=0.0,
        recency_norm=0.0,
    )
    score = reusability_score(rec)
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# fingerprint_count — sha256 over (kind + normalized evidence text)
# ---------------------------------------------------------------------------


def test_signal_fingerprint_stable_across_session():
    """Same kind + same normalized evidence text → same fingerprint
    regardless of session field. This is the cross-project counting primitive.
    """
    evidence = [
        _ev("2026-05-22T10:00:00.000Z", session="S1", tool_error="ENOENT no such file"),
    ]
    sig_a = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=evidence,
    )
    sig_b = Signal(
        kind="tool_error_cluster",
        session="S2",  # different session, same content
        ts="2026-05-22T11:00:00.000Z",  # different ts too
        severity="high",
        evidence=[
            _ev("2026-05-22T11:00:00.000Z", session="S2", tool_error="ENOENT no such file"),
        ],
    )
    assert signal_fingerprint(sig_a) == signal_fingerprint(sig_b)


def test_signal_fingerprint_differs_by_kind():
    """Different kind → different fingerprint."""
    sig_a = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=[_ev("2026-05-22T10:00:00.000Z", tool_error="boom")],
    )
    sig_b = Signal(
        kind="needs_revision_streak",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=[_ev("2026-05-22T10:00:00.000Z", text="NEEDS_REVISION")],
    )
    assert signal_fingerprint(sig_a) != signal_fingerprint(sig_b)


def test_fingerprint_count_returns_distinct_project_count():
    """Two Signals with same fingerprint (kind + evidence) but appearing in
    different project paths → fingerprint_count returns 2.
    """
    evidence_text = "ENOENT no such file"
    sig_a = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=[_ev("2026-05-22T10:00:00.000Z", session="S1", tool_error=evidence_text)],
    )
    sig_b = Signal(
        kind="tool_error_cluster",
        session="S2",
        ts="2026-05-22T11:00:00.000Z",
        severity="high",
        evidence=[_ev("2026-05-22T11:00:00.000Z", session="S2", tool_error=evidence_text)],
    )
    # Build a rec carrying both signals; sessions stand in for "projects" at v0.1.
    rec = AggregateRecord(
        skill_name="x",
        sessions=["S1", "S2"],
        event_count=2,
        signals=[sig_a, sig_b],
        project_paths={"/p1", "/p2"},
        facet_summary={},
        confidence="low",
    )
    # Map session → project for the v0.1 in-memory fingerprint counter.
    session_to_project = {"S1": "/p1", "S2": "/p2"}
    assert fingerprint_count(rec, session_to_project) == 2


# ---------------------------------------------------------------------------
# min_session_count filter + confidence tagging
# ---------------------------------------------------------------------------


def test_min_session_count_filters_low_signal_skills():
    """Skill with 2 sessions dropped from rank_top_n; skill with 3+ kept."""
    low = AggregateRecord(
        skill_name="low",
        sessions=["S1", "S2"],
        event_count=2,
        signals=[],
        project_paths=set(),
        facet_summary={},
        confidence="low",
        frequency_norm=0.9,  # high score but should still be dropped
        time_cost_norm=0.9,
        cross_project_norm=0.9,
        recency_norm=0.9,
    )
    high = AggregateRecord(
        skill_name="high",
        sessions=["S1", "S2", "S3"],
        event_count=3,
        signals=[],
        project_paths=set(),
        facet_summary={},
        confidence="low",
        frequency_norm=0.1,
        time_cost_norm=0.1,
        cross_project_norm=0.1,
        recency_norm=0.1,
    )
    ranked = rank_top_n([low, high], n=5)
    assert [r.skill_name for r in ranked] == ["high"]


def test_confidence_tagging_uses_cross_project_count():
    """An AggregateRecord with project_paths ≥ cross_project_count is tagged
    'high'; below threshold is 'low'.
    """
    multi_project_events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S2",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
    ]
    records = aggregate_by_skill(
        multi_project_events,
        signals=[],
        target_pattern="loom-code:*",
        session_to_project={"S1": "/p1", "S2": "/p2"},
    )
    rec = records["loom-code:brainstorming"]
    assert rec.confidence == "high"  # 2 distinct projects meets cross_project_count=2

    one_project_events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T11:00:00.000Z",
            session="S2",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
    ]
    records2 = aggregate_by_skill(
        one_project_events,
        signals=[],
        target_pattern="loom-code:*",
        session_to_project={"S1": "/p1", "S2": "/p1"},
    )
    assert records2["loom-code:brainstorming"].confidence == "low"


# ---------------------------------------------------------------------------
# rank_top_n
# ---------------------------------------------------------------------------


def _qualifying_rec(name: str, score_inputs: tuple[float, float, float, float]) -> AggregateRecord:
    """Helper — build a min_session_count-qualifying record with the given
    4 normalized inputs.
    """
    f, t, cp, r = score_inputs
    return AggregateRecord(
        skill_name=name,
        sessions=["S1", "S2", "S3"],
        event_count=3,
        signals=[],
        project_paths=set(),
        facet_summary={},
        confidence="low",
        frequency_norm=f,
        time_cost_norm=t,
        cross_project_norm=cp,
        recency_norm=r,
    )


def test_rank_top_n_returns_sorted_desc():
    """5 qualifying records with predictable scores → top 3 in desc order."""
    # Score = 0.35*f + 0.25*t + 0.25*cp + 0.15*r
    # Use frequency_norm only (others 0) so score == 0.35 * f:
    recs = [
        _qualifying_rec("a", (0.1, 0, 0, 0)),  # 0.035
        _qualifying_rec("b", (0.5, 0, 0, 0)),  # 0.175
        _qualifying_rec("c", (0.8, 0, 0, 0)),  # 0.280
        _qualifying_rec("d", (0.3, 0, 0, 0)),  # 0.105
        _qualifying_rec("e", (0.6, 0, 0, 0)),  # 0.210
    ]
    top3 = rank_top_n(recs, n=3)
    assert [r.skill_name for r in top3] == ["c", "e", "b"]


def test_rank_top_n_default_n_is_five():
    """Plan T5 §(e): default n=5."""
    recs = [_qualifying_rec(f"r{i}", (i / 10, 0, 0, 0)) for i in range(7)]
    top = rank_top_n(recs)
    assert len(top) == 5


# ---------------------------------------------------------------------------
# T4 🟡 carry-forward — dedup overlapping cluster signals
# ---------------------------------------------------------------------------


def test_aggregate_dedups_T4_overlapping_cluster_signals():
    """T4's detect_tool_error_clusters emits N-1 overlapping Signals per
    N-event cluster. After aggregate_by_skill, the resulting AggregateRecord
    must hold the dedup'd Signal set — 3 errors in proximity → 1 Signal
    after dedup, NOT 2 (the overlapping pair).
    """
    # 3 tool_error events in immediate proximity within session S1, ALL
    # carrying the same skill_invocation so they aggregate to one record.
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
            tool_error="boom1",
        ),
        _ev(
            "2026-05-22T10:00:01.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
            tool_error="boom2",
        ),
        _ev(
            "2026-05-22T10:00:02.000Z",
            session="S1",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
            tool_error="boom3",
        ),
    ]
    raw_signals = detect_tool_error_clusters(events, proximity_events=5)
    # T4's known behavior: 3 errors emit 2 overlapping Signals (indices 0 and 1
    # each have ≥2 errors in their forward window; index 2 alone has only 1).
    assert len(raw_signals) == 2  # baseline of the inflation we're fixing

    records = aggregate_by_skill(
        events,
        signals=raw_signals,
        target_pattern="loom-code:*",
    )
    rec = records["loom-code:brainstorming"]
    cluster_signals = [s for s in rec.signals if s.kind == "tool_error_cluster"]
    assert len(cluster_signals) == 1  # dedup'd at aggregate layer


def test_dedup_signals_collapses_overlapping_clusters_path_a():
    """Path A (preferred): dedup by sha256(kind + session + sorted evidence UUIDs).

    Two Signals built over overlapping evidence subsets of the same cluster
    must collapse to 1 because the fingerprint of (kind, session, evidence
    identity set) makes them peers.
    """
    e1 = _ev("2026-05-22T10:00:00.000Z", session="S1", tool_error="a")
    e2 = _ev("2026-05-22T10:00:01.000Z", session="S1", tool_error="b")
    e3 = _ev("2026-05-22T10:00:02.000Z", session="S1", tool_error="c")
    # Overlapping clusters from T4's detector:
    sig_overlap_1 = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=[e1, e2, e3],  # full window from index 0
    )
    sig_overlap_2 = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts="2026-05-22T10:00:01.000Z",
        severity="mid",
        evidence=[e2, e3],  # forward window from index 1 (subset of sig_overlap_1)
    )
    deduped = dedup_signals([sig_overlap_1, sig_overlap_2])
    # Both signals belong to the same cluster (sig_overlap_2's evidence is a
    # subset of sig_overlap_1's). Dedup keeps the largest / earliest.
    assert len(deduped) == 1
    assert deduped[0].kind == "tool_error_cluster"


def test_dedup_signals_preserves_distinct_kinds_and_sessions():
    """Signals across different kinds OR different sessions must NOT dedup."""
    e1 = _ev("2026-05-22T10:00:00.000Z", session="S1", tool_error="a")
    e2 = _ev("2026-05-22T11:00:00.000Z", session="S2", tool_error="b")
    sig_a = Signal(
        kind="tool_error_cluster",
        session="S1",
        ts=e1.ts,
        severity="high",
        evidence=[e1],
    )
    sig_b = Signal(
        kind="tool_error_cluster",
        session="S2",  # different session — distinct
        ts=e2.ts,
        severity="high",
        evidence=[e2],
    )
    sig_c = Signal(
        kind="needs_revision_streak",  # different kind — distinct
        session="S1",
        ts=e1.ts,
        severity="high",
        evidence=[e1],
    )
    deduped = dedup_signals([sig_a, sig_b, sig_c])
    assert len(deduped) == 3


# ---------------------------------------------------------------------------
# Edge: recency_norm derivation from event timestamps
# ---------------------------------------------------------------------------


def test_aggregate_computes_recency_from_events():
    """When session_to_project is omitted, aggregate_by_skill should still
    populate recency_norm based on the most-recent event timestamp (closer
    to "now" → closer to 1.0). At least: a record with all events from
    yesterday scores higher recency_norm than one from 30 days ago.
    """
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    long_ago = (now - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    events_fresh = [
        _ev(
            yesterday,
            session=f"S{i}",
            role="assistant",
            skill_invocation="loom-code:fresh",
        )
        for i in range(3)
    ]
    events_stale = [
        _ev(
            long_ago,
            session=f"T{i}",
            role="assistant",
            skill_invocation="loom-code:stale",
        )
        for i in range(3)
    ]
    records = aggregate_by_skill(
        events_fresh + events_stale,
        signals=[],
        target_pattern="loom-code:*",
    )
    assert (
        records["loom-code:fresh"].recency_norm
        > records["loom-code:stale"].recency_norm
    )


# ---------------------------------------------------------------------------
# severity_score_for_session — per-session signal severity-weight sum
# ---------------------------------------------------------------------------


def test_severity_score_for_session_sums_severity_weights():
    """Score signals in a record filtered by session, using severity weights:
    high=3.0, mid=1.0, low=0.3.

    Fixture:
    - session_a: 2 high + 1 mid → 2*3.0 + 1*1.0 = 7.0
    - session_b: 1 low → 0.3
    - missing_session: no matching signals → 0.0
    """

    sig_high_1 = Signal(
        kind="interrupt_after_brainstorm",
        session="session_a",
        ts="2026-05-22T10:00:00.000Z",
        severity="high",
        evidence=[],
    )
    sig_high_2 = Signal(
        kind="tool_error_cluster",
        session="session_a",
        ts="2026-05-22T10:01:00.000Z",
        severity="high",
        evidence=[],
    )
    sig_mid = Signal(
        kind="needs_revision_streak",
        session="session_a",
        ts="2026-05-22T10:02:00.000Z",
        severity="mid",
        evidence=[],
    )
    sig_low = Signal(
        kind="redispatch_concentration",
        session="session_b",
        ts="2026-05-22T10:03:00.000Z",
        severity="low",
        evidence=[],
    )

    rec = AggregateRecord(
        skill_name="loom-code:brainstorming",
        sessions=["session_a", "session_b"],
        event_count=4,
        signals=[sig_high_1, sig_high_2, sig_mid, sig_low],
        project_paths=set(),
        facet_summary={},
        confidence="low",
    )

    # Test: score for session_a
    assert severity_score_for_session(rec, "session_a") == 7.0

    # Test: score for session_b
    assert severity_score_for_session(rec, "session_b") == 0.3

    # Test: missing session returns 0.0
    assert severity_score_for_session(rec, "missing_session") == 0.0


def test_severity_score_for_session_raises_on_unknown_severity():
    """Unknown severity should raise KeyError to enforce fail-loud discipline.

    Fixture: construct a Signal with severity="critical" (not in the
    severity_weights dict). Assert pytest.raises(KeyError) when calling
    severity_score_for_session(rec, "session_a").
    """
    import pytest

    sig_unknown_severity = Signal(
        kind="interrupt_after_brainstorm",
        session="session_a",
        ts="2026-05-22T10:00:00.000Z",
        severity="critical",  # not in the weights dict
        evidence=[],
    )

    rec = AggregateRecord(
        skill_name="loom-code:brainstorming",
        sessions=["session_a"],
        event_count=1,
        signals=[sig_unknown_severity],
        project_paths=set(),
        facet_summary={},
        confidence="low",
    )

    # Must raise KeyError on unknown severity
    with pytest.raises(KeyError):
        severity_score_for_session(rec, "session_a")
