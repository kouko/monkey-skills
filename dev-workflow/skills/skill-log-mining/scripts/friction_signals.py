"""friction_signals.py — four Q5-default friction detectors over Event[].

Pattern provenance (ported, not vendored, from /tmp/code-toolkit-mine.py
demo run on ~/.claude/projects/ 2026-05-22):

- **Pattern 1** (interrupt-after-brainstorm): 25% of mined `[Request
  interrupted by user]` events fired within 10 min of a brainstorming
  Skill invocation. `detect_interrupt_after_brainstorm` emits one Signal
  per (brainstorming, interrupt) pair with `Δt ≤ window_sec`.
- **Pattern 3** (NEEDS_REVISION streak per session): 7/10 explicit
  re-dispatch prompts targeted code-reviewer. `detect_needs_revision_streak`
  emits one Signal per session whose NEEDS_REVISION text-match count
  meets or exceeds `threshold`.
- **Pattern 3 symmetric** (RE-DISPATCH FIX concentration):
  `detect_redispatch_concentration` mirrors Pattern 3 over the
  `RE-DISPATCH FIX` literal.
- **Pattern 4** (write-before-read tool error cluster): tool_use_error
  events cluster within `proximity_events` of one another. The detector
  emits one Signal per event whose forward window of `proximity_events`
  contains ≥2 tool errors (inclusive of the anchor).

Q5 thresholds (baked from the same demo run; see plan Part 1 §Task 4):

    BAKED_THRESHOLDS = {
        "interrupt_window_sec": 600,
        "needs_revision_threshold": 2,
        "redispatch_threshold": 2,
        "tool_error_proximity_events": 10,
    }

`load_thresholds(override_path)` reads a JSON override file (NOT YAML —
stdlib-lean per plan-time Decision 1) and merges its keys over the baked
defaults; unknown keys survive but emit a `warnings.warn` so the operator
sees the typo.

Per Plan Part 1 §Task 4.
"""

from __future__ import annotations

import json
import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from event import Event

# ---------------------------------------------------------------------------
# Baked Q5 thresholds (plan T4 §Q5 verbatim).
# ---------------------------------------------------------------------------

BAKED_THRESHOLDS: dict[str, int] = {
    "interrupt_window_sec": 600,
    "needs_revision_threshold": 2,
    "redispatch_threshold": 2,
    "tool_error_proximity_events": 10,
}

# Skill names that count as "brainstorming" for Pattern 1. Accept both
# bare and plugin-qualified forms because ingest.py preserves whichever
# shape Claude Code emitted (Skill tool_use input.skill verbatim).
_BRAINSTORMING_SKILLS = frozenset(
    {
        "brainstorming",
        "code-toolkit:brainstorming",
        "superpowers:brainstorming",
    }
)

# Severity bucket boundary thresholds (judgment calls; surfaced here so
# downstream aggregate.py / reporting code reads from one place).
_NEEDS_REVISION_HIGH_COUNT = 4  # 4+ revisions in one session = high
_REDISPATCH_HIGH_COUNT = 4
_TOOL_ERROR_CLUSTER_HIGH_COUNT = 4

_NEEDS_REVISION_RE = re.compile(r"\bNEEDS_REVISION\b")
_REDISPATCH_RE = re.compile(r"RE-DISPATCH FIX")


# ---------------------------------------------------------------------------
# Signal dataclass — uniform shape across all detectors.
# ---------------------------------------------------------------------------


@dataclass
class Signal:
    """One detected friction occurrence.

    Fields:

    - kind: stable string identifying which detector fired
      ("interrupt_after_brainstorm" / "tool_error_cluster" /
      "needs_revision_streak" / "redispatch_concentration").
    - session: source `Event.session` string. For per-session aggregate
      detectors (Pattern 3 / 3-symmetric), this is the session whose
      threshold was crossed. For pair-shaped detectors (Pattern 1), this
      is the session of the triggering interrupt.
    - ts: the timestamp of the "triggering" event (interrupt for Pattern
      1; first tool_error in the cluster for Pattern 4; first matching
      event for Pattern 3 / 3-symmetric).
    - severity: "low" / "mid" / "high" — derived from how far the count
      exceeds the threshold, or how short the Δt is for Pattern 1.
    - evidence: list of Events that produced this signal. Order is
      chronological. Caller may render the first / last for context.
    """

    kind: str
    session: str
    ts: str
    severity: str
    evidence: list[Event] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers.
# ---------------------------------------------------------------------------


def _parse_ts(ts: str) -> datetime | None:
    """Parse ISO-8601 timestamp; tolerate trailing 'Z'. Return None on failure."""
    if not isinstance(ts, str) or not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _is_brainstorming(event: Event) -> bool:
    """True iff event.skill_invocation is a recognized brainstorming variant."""
    return event.skill_invocation in _BRAINSTORMING_SKILLS


def _severity_for_count(count: int, threshold: int, high_at: int) -> str:
    """Map a count-vs-threshold delta to severity bucket."""
    if count >= high_at:
        return "high"
    if count > threshold:
        return "mid"
    return "low"


# ---------------------------------------------------------------------------
# Pattern 1 — interrupt-after-brainstorm
# ---------------------------------------------------------------------------


def detect_interrupt_after_brainstorm(
    events: list[Event],
    window_sec: int = 600,
) -> list[Signal]:
    """Pattern 1 — pair each user_interrupt with the most recent
    brainstorming Skill call within `window_sec`.

    For each interrupt event:
      - Find the latest brainstorming event in the same session whose
        timestamp is at or before the interrupt AND within `window_sec`.
      - If found, emit one Signal of kind ``interrupt_after_brainstorm``
        carrying both events as evidence.

    Severity: ``high`` if Δt ≤ 60s (immediate gut-feel rejection);
    ``mid`` otherwise (within the 10-minute window but not snap-back).
    """
    signals: list[Signal] = []

    # Track the most recent brainstorming event per session as we walk
    # chronologically. Caller is expected to pass events in the order
    # ingest.py emitted them, but we sort defensively anyway.
    sorted_events = sorted(events, key=lambda e: e.ts)
    last_brainstorm: dict[str, Event] = {}

    for event in sorted_events:
        if _is_brainstorming(event):
            last_brainstorm[event.session] = event
            continue
        if not event.user_interrupt:
            continue
        anchor = last_brainstorm.get(event.session)
        if anchor is None:
            continue
        anchor_dt = _parse_ts(anchor.ts)
        event_dt = _parse_ts(event.ts)
        if anchor_dt is None or event_dt is None:
            continue
        delta = (event_dt - anchor_dt).total_seconds()
        if delta < 0 or delta > window_sec:
            continue
        severity = "high" if delta <= 60 else "mid"
        signals.append(
            Signal(
                kind="interrupt_after_brainstorm",
                session=event.session,
                ts=event.ts,
                severity=severity,
                evidence=[anchor, event],
            )
        )

    return signals


# ---------------------------------------------------------------------------
# Pattern 4 — tool error clusters
# ---------------------------------------------------------------------------


def detect_tool_error_clusters(
    events: list[Event],
    proximity_events: int = 10,
) -> list[Signal]:
    """Pattern 4 — emit one Signal per tool_error whose forward window of
    `proximity_events` contains ≥2 tool errors (inclusive).

    "Forward window of N" means the next N events (chronological) starting
    from and including the current event. Operating on the linear event
    stream rather than a wall-clock window mirrors the demo's
    "N-events proximity" semantic; this catches retry storms regardless of
    how fast or slow they fire.

    To avoid double-reporting an obvious cluster as N overlapping
    signals, we only emit when the anchor event is itself a tool_error
    AND the window contains at least one OTHER tool_error.
    """
    signals: list[Signal] = []
    sorted_events = sorted(events, key=lambda e: e.ts)
    n = len(sorted_events)

    for i, anchor in enumerate(sorted_events):
        if anchor.tool_error is None:
            continue
        window = sorted_events[i : i + proximity_events]
        errors_in_window = [e for e in window if e.tool_error is not None]
        if len(errors_in_window) < 2:
            continue
        severity = _severity_for_count(
            len(errors_in_window),
            threshold=2,
            high_at=_TOOL_ERROR_CLUSTER_HIGH_COUNT,
        )
        signals.append(
            Signal(
                kind="tool_error_cluster",
                session=anchor.session,
                ts=anchor.ts,
                severity=severity,
                evidence=errors_in_window,
            )
        )

    return signals


# ---------------------------------------------------------------------------
# Pattern 3 — NEEDS_REVISION streak per session
# ---------------------------------------------------------------------------


def detect_needs_revision_streak(
    events: list[Event],
    threshold: int = 2,
) -> list[Signal]:
    """Pattern 3 — emit one Signal per session whose NEEDS_REVISION
    text-match count meets or exceeds `threshold`.

    Per-session aggregate detector (one Signal per qualifying session,
    not one per matching event). The signal's ``ts`` is the timestamp of
    the first matching event in that session; ``evidence`` carries all
    matching events.
    """
    return _detect_text_pattern_per_session(
        events,
        pattern=_NEEDS_REVISION_RE,
        threshold=threshold,
        kind="needs_revision_streak",
        high_at=_NEEDS_REVISION_HIGH_COUNT,
    )


# ---------------------------------------------------------------------------
# Pattern 3 symmetric — RE-DISPATCH FIX concentration per session
# ---------------------------------------------------------------------------


def detect_redispatch_concentration(
    events: list[Event],
    threshold: int = 2,
) -> list[Signal]:
    """Pattern 3 symmetric — emit one Signal per session whose
    ``RE-DISPATCH FIX`` literal match count meets or exceeds `threshold`.
    """
    return _detect_text_pattern_per_session(
        events,
        pattern=_REDISPATCH_RE,
        threshold=threshold,
        kind="redispatch_concentration",
        high_at=_REDISPATCH_HIGH_COUNT,
    )


def _detect_text_pattern_per_session(
    events: list[Event],
    *,
    pattern: re.Pattern[str],
    threshold: int,
    kind: str,
    high_at: int,
) -> list[Signal]:
    """Shared core for Pattern 3 / 3-symmetric: group matching events by
    session, emit one Signal per session over threshold.
    """
    sorted_events = sorted(events, key=lambda e: e.ts)
    by_session: dict[str, list[Event]] = {}
    for event in sorted_events:
        if not event.text:
            continue
        if pattern.search(event.text):
            by_session.setdefault(event.session, []).append(event)

    signals: list[Signal] = []
    for session, matches in by_session.items():
        if len(matches) < threshold:
            continue
        severity = _severity_for_count(len(matches), threshold=threshold, high_at=high_at)
        signals.append(
            Signal(
                kind=kind,
                session=session,
                ts=matches[0].ts,
                severity=severity,
                evidence=matches,
            )
        )
    return signals


# ---------------------------------------------------------------------------
# Threshold override loader.
# ---------------------------------------------------------------------------


def load_thresholds(override_path: Path | None) -> dict[str, int]:
    """Return baked thresholds, optionally overridden by a JSON file.

    Args:
        override_path: path to a JSON file whose top-level object's
            keys override the matching baked keys. If None, return a
            fresh copy of ``BAKED_THRESHOLDS`` (mutating the result must
            never affect the module constant).

    JSON-only (NOT YAML) per plan-time Decision 1 — stdlib-lean, zero
    third-party deps.

    Unknown keys in the override file are kept in the returned dict but
    a ``warnings.warn`` is emitted so the operator notices a typo.
    """
    merged: dict[str, int] = dict(BAKED_THRESHOLDS)
    if override_path is None:
        return merged

    raw = override_path.read_text(encoding="utf-8")
    override_data = json.loads(raw)
    if not isinstance(override_data, dict):
        raise ValueError(
            f"threshold override file must contain a JSON object at top level, "
            f"got {type(override_data).__name__}"
        )

    unknown_keys = [k for k in override_data if k not in BAKED_THRESHOLDS]
    if unknown_keys:
        warnings.warn(
            f"unknown threshold keys in {override_path}: {sorted(unknown_keys)} "
            f"(known keys: {sorted(BAKED_THRESHOLDS)})",
            stacklevel=2,
        )

    merged.update(override_data)
    return merged
