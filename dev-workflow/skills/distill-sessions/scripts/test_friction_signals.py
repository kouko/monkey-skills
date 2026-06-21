"""test_friction_signals.py — tests for the 4 Q5 friction detectors.

Per Plan Part 1 §Task 4 acceptance:
1. test_interrupt_after_brainstorm_pattern1 — brainstorming → interrupt 50s later → ≥1 Signal.
2. test_tool_error_clusters_pattern4 — 3 tool errors within 5 events → ≥1 Signal.
3. test_needs_revision_streak_pattern3 — 3 NEEDS_REVISION events in one session → ≥1 Signal.
4. test_redispatch_concentration_pattern3 — 3 RE-DISPATCH FIX text matches → ≥1 Signal.
5. test_load_thresholds_merges_over_defaults — override shadows specific keys.
"""

from __future__ import annotations

import json
from pathlib import Path

from event import Event
from friction_signals import (
    BAKED_THRESHOLDS,
    Signal,
    detect_interrupt_after_brainstorm,
    detect_needs_revision_streak,
    detect_redispatch_concentration,
    detect_tool_error_clusters,
    load_thresholds,
)


def _ev(
    ts: str,
    *,
    session: str = "S1",
    role: str = "user",
    text: str = "",
    skill_invocation: str | None = None,
    tool_error: str | None = None,
    user_interrupt: bool = False,
) -> Event:
    return Event(
        agent="claude-code",
        session=session,
        ts=ts,
        role=role,
        text=text,
        skill_invocation=skill_invocation,
        tool_error=tool_error,
        user_interrupt=user_interrupt,
    )


# ---------------------------------------------------------------------------
# Pattern 1 — interrupt-after-brainstorm within window_sec
# ---------------------------------------------------------------------------


def test_interrupt_after_brainstorm_pattern1():
    """Brainstorming Skill call at t=0 → user interrupt 50s later → one Signal."""
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            role="assistant",
            text='{"skill":"brainstorming"}',
            skill_invocation="brainstorming",
        ),
        _ev(
            "2026-05-22T10:00:50.000Z",
            role="user",
            text="[Request interrupted by user]",
            user_interrupt=True,
        ),
    ]
    signals = detect_interrupt_after_brainstorm(events, window_sec=600)
    assert len(signals) >= 1
    assert signals[0].kind == "interrupt_after_brainstorm"
    assert signals[0].session == "S1"
    # Evidence should include the brainstorming call and the interrupt
    assert len(signals[0].evidence) >= 2


def test_interrupt_after_brainstorm_outside_window_no_signal():
    """Interrupt > window_sec after brainstorming → no signal."""
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            role="assistant",
            skill_invocation="brainstorming",
        ),
        _ev(
            "2026-05-22T10:30:00.000Z",  # 1800s later, well beyond 600s
            role="user",
            user_interrupt=True,
        ),
    ]
    signals = detect_interrupt_after_brainstorm(events, window_sec=600)
    assert signals == []


def test_interrupt_after_brainstorm_qualified_skill_form():
    """Skill invocation 'loom-code:brainstorming' is recognized too."""
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            role="assistant",
            skill_invocation="loom-code:brainstorming",
        ),
        _ev(
            "2026-05-22T10:00:30.000Z",
            role="user",
            user_interrupt=True,
        ),
    ]
    signals = detect_interrupt_after_brainstorm(events, window_sec=600)
    assert len(signals) >= 1


# ---------------------------------------------------------------------------
# Pattern 4 — tool error clusters within proximity_events
# ---------------------------------------------------------------------------


def test_tool_error_clusters_pattern4():
    """3 tool errors within 5-event window → at least one cluster Signal."""
    events = [
        _ev("2026-05-22T10:00:00.000Z", tool_error="ENOENT no such file"),
        _ev("2026-05-22T10:00:01.000Z", text="ok"),
        _ev("2026-05-22T10:00:02.000Z", tool_error="permission denied"),
        _ev("2026-05-22T10:00:03.000Z", text="ok"),
        _ev("2026-05-22T10:00:04.000Z", tool_error="parse error"),
    ]
    signals = detect_tool_error_clusters(events, proximity_events=5)
    assert len(signals) >= 1
    assert signals[0].kind == "tool_error_cluster"
    # Evidence should include at least 2 of the tool_error events
    error_count = sum(1 for e in signals[0].evidence if e.tool_error is not None)
    assert error_count >= 2


def test_tool_error_clusters_sparse_no_signal():
    """Single tool error with no neighbors → no signal."""
    events = [
        _ev("2026-05-22T10:00:00.000Z", tool_error="oops"),
        _ev("2026-05-22T10:00:01.000Z", text="ok"),
        _ev("2026-05-22T10:00:02.000Z", text="ok"),
    ]
    signals = detect_tool_error_clusters(events, proximity_events=5)
    assert signals == []


# ---------------------------------------------------------------------------
# Pattern 3 — NEEDS_REVISION streak per session
# ---------------------------------------------------------------------------


def test_needs_revision_streak_pattern3():
    """3 NEEDS_REVISION events in one session crosses threshold=2 → Signal."""
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            text="verdict: NEEDS_REVISION — fatal: X",
            session="S1",
        ),
        _ev(
            "2026-05-22T10:05:00.000Z",
            text="status: NEEDS_REVISION (2 yellow)",
            session="S1",
        ),
        _ev(
            "2026-05-22T10:10:00.000Z",
            text="Round 3 NEEDS_REVISION blocking gate",
            session="S1",
        ),
    ]
    signals = detect_needs_revision_streak(events, threshold=2)
    assert len(signals) >= 1
    assert signals[0].kind == "needs_revision_streak"
    assert signals[0].session == "S1"
    assert len(signals[0].evidence) >= 3


def test_needs_revision_streak_below_threshold_no_signal():
    """1 NEEDS_REVISION event with threshold=2 → no signal."""
    events = [
        _ev(
            "2026-05-22T10:00:00.000Z",
            text="status: NEEDS_REVISION once",
        ),
    ]
    signals = detect_needs_revision_streak(events, threshold=2)
    assert signals == []


# ---------------------------------------------------------------------------
# Pattern 3 symmetric — RE-DISPATCH FIX concentration per session
# ---------------------------------------------------------------------------


def test_redispatch_concentration_pattern3():
    """3 RE-DISPATCH FIX text matches in a session crosses threshold=2."""
    events = [
        _ev("2026-05-22T10:00:00.000Z", text="RE-DISPATCH FIX T1 round 2"),
        _ev("2026-05-22T10:05:00.000Z", text="RE-DISPATCH FIX T2 round 2"),
        _ev("2026-05-22T10:10:00.000Z", text="RE-DISPATCH FIX T3 round 2"),
    ]
    signals = detect_redispatch_concentration(events, threshold=2)
    assert len(signals) >= 1
    assert signals[0].kind == "redispatch_concentration"
    assert len(signals[0].evidence) >= 3


def test_redispatch_concentration_below_threshold_no_signal():
    events = [
        _ev("2026-05-22T10:00:00.000Z", text="RE-DISPATCH FIX once"),
    ]
    signals = detect_redispatch_concentration(events, threshold=2)
    assert signals == []


# ---------------------------------------------------------------------------
# load_thresholds override merging
# ---------------------------------------------------------------------------


def test_load_thresholds_no_override_returns_defaults():
    """None override → exact copy of BAKED_THRESHOLDS."""
    out = load_thresholds(None)
    assert out == BAKED_THRESHOLDS
    # Returned dict must be a copy — mutating it must not affect the baked.
    out["interrupt_window_sec"] = 999
    assert BAKED_THRESHOLDS["interrupt_window_sec"] == 600


def test_load_thresholds_merges_over_defaults(tmp_path: Path):
    """Override shadows interrupt_window_sec only; others untouched."""
    override_file = tmp_path / "thresholds.json"
    override_file.write_text(json.dumps({"interrupt_window_sec": 900}))

    out = load_thresholds(override_file)
    assert out["interrupt_window_sec"] == 900
    # Other 3 baked thresholds must remain intact.
    assert out["needs_revision_threshold"] == BAKED_THRESHOLDS["needs_revision_threshold"]
    assert out["redispatch_threshold"] == BAKED_THRESHOLDS["redispatch_threshold"]
    assert out["tool_error_proximity_events"] == BAKED_THRESHOLDS["tool_error_proximity_events"]


def test_baked_thresholds_are_q5_defaults():
    """The bundled thresholds match plan T4 §Q5 verbatim."""
    assert BAKED_THRESHOLDS == {
        "interrupt_window_sec": 600,
        "needs_revision_threshold": 2,
        "redispatch_threshold": 2,
        "tool_error_proximity_events": 10,
    }


def test_signal_dataclass_shape():
    """Signal carries {kind, session, ts, severity, evidence}."""
    ev = _ev("2026-05-22T10:00:00.000Z")
    sig = Signal(
        kind="x",
        session="S1",
        ts="2026-05-22T10:00:00.000Z",
        severity="mid",
        evidence=[ev],
    )
    assert sig.kind == "x"
    assert sig.session == "S1"
    assert sig.severity in {"low", "mid", "high"}
    assert sig.evidence[0] is ev
