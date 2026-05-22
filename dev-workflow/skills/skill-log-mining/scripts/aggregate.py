"""aggregate.py — per-skill aggregation + crune reusability score + cross-project fingerprint.

Stage 2 of skill-log-mining v0.1. Consumes Event[] (from ingest.py) and
Signal[] (from friction_signals.py), groups by target Skill invocation
glob, attaches per-session signals, computes a crune-style reusability
score, and ranks the high-friction skills.

Five exports per plan T5:

- ``aggregate_by_skill(events, signals, target_pattern)`` — filter +
  group + signal-join.
- ``reusability_score(rec)`` — crune 4-signal weighted sum
  ``0.35*frequency + 0.25*timeCost + 0.25*crossProject + 0.15*recency``.
- ``fingerprint_count(rec, session_to_project)`` — count distinct project
  trees a signal's friction-fingerprint appears in.
- ``rank_top_n(records, n=5)`` — min_session_count-filtered + sorted desc.
- ``AGGREGATE_THRESHOLDS`` module constant — ``min_session_count=3``,
  ``cross_project_count=2`` per plan Q5.

T4 🟡 dedup (Path A, preferred): ``dedup_signals(signals)`` fingerprints
each Signal as ``sha256(kind + session + sorted_evidence_event_ids)``
and keeps one representative per fingerprint cluster. Two Signals whose
evidence sets are subset-related (the inflation pattern emitted by
``friction_signals.detect_tool_error_clusters``) collapse via a second
pass that merges overlapping-evidence Signals within (kind, session).
This is uniform across all 4 Signal kinds, not a tool_error_cluster
special case — when a future detector also emits overlapping windows,
the same protection applies.

Project-path proxy (v0.1 limitation, documented for T2 / v0.2 follow-up):
``Event`` does not carry the JSONL file's project tree path; the
caller-supplied ``session_to_project`` mapping is the bridge.
``aggregate_by_skill`` accepts it as an optional kw-only arg; when
omitted, sessions stand in for project paths (1 session = 1 "project"
at v0.1 — approximation noted in T5 spec). v0.2 surfaces this as an
``Event.project_path`` field populated by ingest.py.

Per Plan Part 1 §Task 5.
"""

from __future__ import annotations

import fnmatch
import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from event import Event
from friction_signals import Signal

# ---------------------------------------------------------------------------
# Q5 baked aggregation thresholds (plan T5 §(d) verbatim).
# ---------------------------------------------------------------------------

AGGREGATE_THRESHOLDS: dict[str, int] = {
    "min_session_count": 3,
    "cross_project_count": 2,
}

# Severity → numeric weight for the timeCost crune signal.
_SEVERITY_WEIGHT: dict[str, int] = {"low": 1, "mid": 2, "high": 3}
_MAX_SEVERITY_WEIGHT = 3

# Recency normalization window — events within ``_RECENCY_WINDOW_DAYS`` days
# of "now" score in [0,1]; events older than the window saturate at 0.
_RECENCY_WINDOW_DAYS = 30

# Crune 4-signal weights (without /insights facets; plan T5 §(b)).
_W_FREQUENCY = 0.35
_W_TIME_COST = 0.25
_W_CROSS_PROJECT = 0.25
_W_RECENCY = 0.15

# Whitespace normalization for fingerprint hashing.
_WS_RE = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# AggregateRecord dataclass — the per-skill bucket.
# ---------------------------------------------------------------------------


@dataclass
class AggregateRecord:
    """One per-skill aggregation bucket carrying the inputs to
    ``reusability_score``.

    Fields:

    - ``skill_name``: the value from ``event.skill_invocation`` that this
      bucket groups on (e.g. ``"code-toolkit:brainstorming"``).
    - ``sessions``: distinct session ids in which this skill was invoked.
    - ``event_count``: total invocations across all sessions (one event
      per recognized Skill call).
    - ``signals``: Signal[] attached to this skill, post-dedup. A signal
      is "attached" when its ``session`` matches any element of
      ``sessions``.
    - ``project_paths``: distinct project trees this skill appeared in.
      v0.1 fed by ``session_to_project`` map; v0.2 expected to come
      from ``Event.project_path``.
    - ``facet_summary``: optional FacetRecord-derived aggregate (mean
      claude_helpfulness rank, outcome distribution, etc.). Empty dict at
      v0.1; populated by future facets joiner.
    - ``confidence``: ``"low"`` / ``"mid"`` / ``"high"`` tag driven by
      ``len(project_paths)`` vs ``cross_project_count`` threshold.
    - 4 normalized crune inputs (``frequency_norm`` / ``time_cost_norm`` /
      ``cross_project_norm`` / ``recency_norm``): pre-computed at
      aggregate-time so ``reusability_score`` is a pure weighted sum.
    """

    skill_name: str
    sessions: list[str]
    event_count: int
    signals: list[Signal]
    project_paths: set[str]
    facet_summary: dict[str, object] = field(default_factory=dict)
    confidence: str = "low"
    frequency_norm: float = 0.0
    time_cost_norm: float = 0.0
    cross_project_norm: float = 0.0
    recency_norm: float = 0.0


# ---------------------------------------------------------------------------
# Signal dedup (T4 🟡 carry-forward — Path A).
# ---------------------------------------------------------------------------


def _event_identity(event: Event) -> str:
    """Stable identity string for a single Event used inside signal
    fingerprinting.

    No UUID field on Event at v0.1; ``session + ts + role + first 80 chars
    of normalized text`` is good enough to identify "same event" across
    Signal evidence lists emitted in one detector pass — those lists
    reference the same Event objects, so even text snapshots match.
    """
    text_snip = _WS_RE.sub(" ", (event.text or "")).strip()[:80]
    return f"{event.session}|{event.ts}|{event.role}|{text_snip}"


def signal_fingerprint(signal: Signal) -> str:
    """sha256 over ``kind + normalized evidence text`` per plan T5 §(c).

    The fingerprint deliberately omits ``session`` and ``ts`` so the same
    friction shape detected in two different project trees produces the
    same hash — that's what makes cross-project counting work.

    Evidence text is normalized (whitespace-collapse) before hashing so
    cosmetic formatting differences don't fragment the fingerprint.
    """
    evidence_text_parts: list[str] = []
    for ev in signal.evidence:
        normalized = _WS_RE.sub(" ", (ev.text or "")).strip()
        normalized_err = _WS_RE.sub(" ", (ev.tool_error or "")).strip()
        evidence_text_parts.append(f"{normalized}|{normalized_err}")
    payload = signal.kind + "::" + "||".join(evidence_text_parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _dedup_key(signal: Signal) -> str:
    """sha256 over ``kind + session + sorted(evidence event identities)``.

    Differs from ``signal_fingerprint``: includes ``session`` (within-session
    dedup only — different sessions stay distinct) and uses identity
    rather than text content (catches in-detector inflation reliably).
    """
    identities = sorted(_event_identity(ev) for ev in signal.evidence)
    payload = signal.kind + "::" + signal.session + "::" + "||".join(identities)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def dedup_signals(signals: list[Signal]) -> list[Signal]:
    """Collapse overlapping Signals from one detector pass.

    Two-stage:

    1. **Exact identity dedup** — Signals with identical
       ``(kind, session, evidence identity set)`` collapse to one
       representative (first seen wins by detector emission order).
    2. **Evidence-subset merge** — within each (kind, session) bucket, if
       Signal B's evidence set is a subset of Signal A's evidence set,
       drop B. This catches the
       ``friction_signals.detect_tool_error_clusters`` inflation pattern
       where the forward-window walk emits one Signal per anchor event
       and each downstream anchor's window is a subset of the upstream
       anchor's.

    Different kinds and different sessions always stay distinct — the
    merge only runs within (kind, session).

    Returns: new list, original order preserved among survivors.
    """
    # Stage 1 — exact identity dedup.
    seen: dict[str, Signal] = {}
    for sig in signals:
        key = _dedup_key(sig)
        if key not in seen:
            seen[key] = sig
    stage1 = list(seen.values())

    # Stage 2 — within (kind, session), drop Signals whose evidence is a
    # strict subset of another surviving Signal's evidence in the same
    # bucket. Preserves the Signal with the larger evidence set.
    buckets: dict[tuple[str, str], list[Signal]] = {}
    for sig in stage1:
        buckets.setdefault((sig.kind, sig.session), []).append(sig)

    survivors: set[int] = set(range(len(stage1)))
    sig_to_index = {id(s): i for i, s in enumerate(stage1)}
    for bucket_sigs in buckets.values():
        # Sort by evidence-set size desc so the candidate to keep is
        # examined first — when B is a subset of A, A comes first.
        sorted_sigs = sorted(bucket_sigs, key=lambda s: -len(s.evidence))
        kept_id_sets: list[frozenset[str]] = []
        for sig in sorted_sigs:
            ev_ids = frozenset(_event_identity(ev) for ev in sig.evidence)
            # Drop sig if any already-kept superset covers it.
            if any(ev_ids.issubset(kept) and ev_ids != kept for kept in kept_id_sets):
                survivors.discard(sig_to_index[id(sig)])
                continue
            # Symmetric check: if a previously-kept set is a strict subset
            # of ev_ids, that kept signal should be dropped in favor of
            # this one (defensive — sort already ordered by size desc, but
            # ties can land in either order).
            kept_id_sets = [k for k in kept_id_sets if not (k.issubset(ev_ids) and k != ev_ids)]
            kept_id_sets.append(ev_ids)
        # Re-walk: drop any sig whose set is now a strict subset of any
        # surviving kept set.
        for sig in bucket_sigs:
            if sig_to_index[id(sig)] not in survivors:
                continue
            ev_ids = frozenset(_event_identity(ev) for ev in sig.evidence)
            if any(ev_ids.issubset(kept) and ev_ids != kept for kept in kept_id_sets):
                survivors.discard(sig_to_index[id(sig)])

    return [stage1[i] for i in sorted(survivors)]


# ---------------------------------------------------------------------------
# aggregate_by_skill — Stage 2 entrypoint.
# ---------------------------------------------------------------------------


def _parse_ts(ts: str) -> datetime | None:
    if not isinstance(ts, str) or not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _max_event_count(records: dict[str, AggregateRecord]) -> int:
    return max((r.event_count for r in records.values()), default=1) or 1


def _max_project_count(records: dict[str, AggregateRecord]) -> int:
    return max((len(r.project_paths) for r in records.values()), default=1) or 1


def aggregate_by_skill(
    events: list[Event],
    signals: list[Signal],
    target_pattern: str = "code-toolkit:*",
    *,
    session_to_project: dict[str, str] | None = None,
) -> dict[str, AggregateRecord]:
    """Group events by ``skill_invocation`` matching ``target_pattern``,
    attach matching signals, dedup, compute crune normalization inputs.

    Args:
        events: full Event[] iterable (typically post-ingest, optionally
            post-facets attached).
        signals: Signal[] from one or more
            ``friction_signals.detect_*`` calls. Signals are dedup'd via
            :func:`dedup_signals` before attachment.
        target_pattern: fnmatch glob applied to ``event.skill_invocation``
            (default ``"code-toolkit:*"``).
        session_to_project: optional dict mapping session id → project
            tree path. When omitted, sessions themselves stand in for
            project paths (v0.1 approximation; v0.2 plans Event.project_path).

    Returns:
        Dict keyed by skill name; one AggregateRecord per skill seen in
        ``events`` whose invocation matched ``target_pattern``.

    Empty ``events`` returns ``{}``. Events with ``skill_invocation=None``
    are silently skipped (graceful — most events don't carry a Skill
    invocation).
    """
    # Stage 0 — dedup signals once up front so overlapping cluster
    # inflation never reaches downstream count math.
    deduped_signals = dedup_signals(list(signals))

    # Stage 1 — group events by matching skill_invocation.
    by_skill: dict[str, list[Event]] = {}
    for event in events:
        skill = event.skill_invocation
        if not isinstance(skill, str) or not skill:
            continue
        if not fnmatch.fnmatch(skill, target_pattern):
            continue
        by_skill.setdefault(skill, []).append(event)

    if not by_skill:
        return {}

    # Stage 2 — build a session→skill map for signal attachment.
    session_to_skills: dict[str, set[str]] = {}
    for skill, sk_events in by_skill.items():
        for ev in sk_events:
            session_to_skills.setdefault(ev.session, set()).add(skill)

    # Stage 3 — assemble AggregateRecord per skill.
    records: dict[str, AggregateRecord] = {}
    now = datetime.now(timezone.utc)
    for skill, sk_events in by_skill.items():
        sessions = sorted({ev.session for ev in sk_events})
        # Project paths: prefer caller-supplied session_to_project; fall
        # back to sessions-as-projects.
        if session_to_project is None:
            project_paths = set(sessions)
        else:
            project_paths = {session_to_project.get(s, s) for s in sessions}

        # Attach signals whose session matches.
        attached = [s for s in deduped_signals if s.session in set(sessions)]

        # Time cost — sum of severity weights / max possible.
        time_cost_sum = sum(_SEVERITY_WEIGHT.get(s.severity, 0) for s in attached)
        max_possible_time_cost = max(_MAX_SEVERITY_WEIGHT * max(len(attached), 1), 1)
        time_cost_norm = _clamp(time_cost_sum / max_possible_time_cost)

        # Recency — most-recent event in this skill bucket. Closer to now
        # → closer to 1; older than the window → 0.
        latest_dt = None
        for ev in sk_events:
            dt = _parse_ts(ev.ts)
            if dt is None:
                continue
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt
        if latest_dt is None:
            recency_norm = 0.0
        else:
            # Make `now` and `latest_dt` comparable on naive vs aware.
            if latest_dt.tzinfo is None:
                latest_dt = latest_dt.replace(tzinfo=timezone.utc)
            age_days = max((now - latest_dt).total_seconds() / 86400.0, 0.0)
            recency_norm = _clamp(1.0 - (age_days / _RECENCY_WINDOW_DAYS))

        # Confidence tag — meets cross_project_count threshold?
        confidence = (
            "high"
            if len(project_paths) >= AGGREGATE_THRESHOLDS["cross_project_count"]
            else "low"
        )

        records[skill] = AggregateRecord(
            skill_name=skill,
            sessions=sessions,
            event_count=len(sk_events),
            signals=attached,
            project_paths=project_paths,
            facet_summary={},
            confidence=confidence,
            frequency_norm=0.0,  # filled in second pass (needs cross-record max)
            time_cost_norm=time_cost_norm,
            cross_project_norm=0.0,  # ditto
            recency_norm=recency_norm,
        )

    # Stage 4 — fill in normalization that needs the cross-record max.
    max_events = _max_event_count(records)
    max_projects = _max_project_count(records)
    for rec in records.values():
        rec.frequency_norm = _clamp(rec.event_count / max_events)
        rec.cross_project_norm = _clamp(len(rec.project_paths) / max_projects)

    return records


# ---------------------------------------------------------------------------
# reusability_score — crune 4-signal weighted sum.
# ---------------------------------------------------------------------------


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp ``x`` into ``[lo, hi]`` — defensive against out-of-range inputs."""
    return max(lo, min(hi, x))


def reusability_score(rec: AggregateRecord) -> float:
    """crune 4-signal weighted sum.

    ``0.35*frequency_norm + 0.25*time_cost_norm + 0.25*cross_project_norm +
    0.15*recency_norm``. Each input is clamped to [0,1] before weighting so
    the score is always in [0,1].

    Plan T5 §(b) verbatim.
    """
    f = _clamp(rec.frequency_norm)
    t = _clamp(rec.time_cost_norm)
    cp = _clamp(rec.cross_project_norm)
    r = _clamp(rec.recency_norm)
    return _W_FREQUENCY * f + _W_TIME_COST * t + _W_CROSS_PROJECT * cp + _W_RECENCY * r


# ---------------------------------------------------------------------------
# fingerprint_count — distinct projects per friction-fingerprint.
# ---------------------------------------------------------------------------


def fingerprint_count(
    rec: AggregateRecord,
    session_to_project: dict[str, str],
) -> int:
    """Return the largest "appears in N projects" count across the
    record's signals' fingerprints.

    For each Signal in ``rec.signals``, compute its
    ``signal_fingerprint`` and the project path of its session (via
    ``session_to_project``). Group fingerprints → distinct project paths.
    Return the max group size — that is, "how many distinct project
    trees does our most-widespread friction-shape appear in?".

    Returns 0 when ``rec.signals`` is empty.

    Per plan T5 §(c): "within-run in-memory count" (claude-coach
    pattern). Persistent ledger deferred to v0.2.
    """
    if not rec.signals:
        return 0
    fingerprint_projects: dict[str, set[str]] = {}
    for sig in rec.signals:
        fp = signal_fingerprint(sig)
        project = session_to_project.get(sig.session, sig.session)
        fingerprint_projects.setdefault(fp, set()).add(project)
    return max(len(projects) for projects in fingerprint_projects.values())


# ---------------------------------------------------------------------------
# rank_top_n — min_session_count filter + sorted desc.
# ---------------------------------------------------------------------------


def rank_top_n(
    records: list[AggregateRecord] | dict[str, AggregateRecord],
    n: int = 5,
) -> list[AggregateRecord]:
    """Filter records by ``min_session_count``, sort by
    ``reusability_score`` desc, return top ``n``.

    Accepts either a list[AggregateRecord] or the dict returned by
    ``aggregate_by_skill`` (caller convenience).

    Plan T5 §(e) verbatim, default ``n=5``.
    """
    if isinstance(records, dict):
        records = list(records.values())
    threshold = AGGREGATE_THRESHOLDS["min_session_count"]
    qualifying = [r for r in records if len(r.sessions) >= threshold]
    qualifying.sort(key=reusability_score, reverse=True)
    return qualifying[:n]
