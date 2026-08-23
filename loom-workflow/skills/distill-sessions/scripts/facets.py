"""facets.py — ~/.claude/usage-data/facets/*.json adapter → joined Event[].

External surface (memory project_external_surface_grounding_discipline.md):
Claude Code's `/insights` slash command (released Feb 2026 by Anthropic's
Thariq Shihipar) emits per-session pre-classified data to
`~/.claude/usage-data/facets/<session_id>.json`. This is an
**undocumented internal Anthropic format**; verified against 49 real
fixtures on 2026-05-22 (~1.0 MB total) — all 49 files share the same
11-key shape:

    {
      "session_id": str,                    // UUID
      "underlying_goal": str,               // 1-sentence summary
      "goal_categories": dict[str, int],    // ~10 canonical labels
      "outcome": str,                       // fully_achieved / mostly_achieved
                                            //   / partially_achieved / failed
      "user_satisfaction_counts": dict[str, int],  // satisfied / likely_satisfied
                                                   //   / dissatisfied
      "claude_helpfulness": str,            // very_helpful / moderately_helpful
                                            //   / slightly_helpful / unhelpful
      "session_type": str,                  // single_task / multi_task /
                                            //   iterative_refinement
      "friction_counts": dict[str, int],    // key signal
      "friction_detail": str,
      "primary_success": str,
      "brief_summary": str
    }

Deviation status (T3 ingest of 5 real fixtures 2026-05-22): **none observed**.
All 11 keys present and shape matches the research-memo spec verbatim. The
parser still tolerates missing keys (older `/insights` versions or future
schema additions) via FacetRecord field defaults — see _from_dict.

Per Plan Part 1 §Task 3.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from event import Event

# Default facets dir — overridable for tests.
DEFAULT_FACETS_ROOT = Path.home() / ".claude" / "usage-data" / "facets"


@dataclass
class FacetRecord:
    """One parsed `~/.claude/usage-data/facets/<session_id>.json` record.

    All fields default to None (or empty dict for the *_counts / *_categories
    mappings) so older facets JSONs missing newer keys still load cleanly.
    Callers can do `rec.friction_counts.items()` without a None guard.
    """

    session_id: str | None = None
    underlying_goal: str | None = None
    goal_categories: dict[str, int] = field(default_factory=dict)
    outcome: str | None = None
    user_satisfaction_counts: dict[str, int] = field(default_factory=dict)
    claude_helpfulness: str | None = None
    session_type: str | None = None
    friction_counts: dict[str, int] = field(default_factory=dict)
    friction_detail: str | None = None
    primary_success: str | None = None
    brief_summary: str | None = None


def _from_dict(payload: dict) -> FacetRecord | None:
    """Build a FacetRecord from a parsed JSON dict, or None when the
    payload is unusable (missing session_id — the join key).

    Type-checks each field individually so a malformed value (e.g.
    `outcome: 123`) falls back to the FacetRecord default rather than
    propagating bad data into Stage 2-5 consumers. Quietly drops bad
    values; surfacing them as warnings would require a logger which is
    out of scope for v0.1 stdlib-only discipline.
    """
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    def _str_or_none(key: str) -> str | None:
        v = payload.get(key)
        return v if isinstance(v, str) else None

    def _dict_or_empty(key: str) -> dict[str, int]:
        v = payload.get(key)
        if not isinstance(v, dict):
            return {}
        # Filter to string-keyed int-valued entries — defensive against
        # future schema drift adding nested objects.
        return {k: val for k, val in v.items() if isinstance(k, str) and isinstance(val, int)}

    return FacetRecord(
        session_id=session_id,
        underlying_goal=_str_or_none("underlying_goal"),
        goal_categories=_dict_or_empty("goal_categories"),
        outcome=_str_or_none("outcome"),
        user_satisfaction_counts=_dict_or_empty("user_satisfaction_counts"),
        claude_helpfulness=_str_or_none("claude_helpfulness"),
        session_type=_str_or_none("session_type"),
        friction_counts=_dict_or_empty("friction_counts"),
        friction_detail=_str_or_none("friction_detail"),
        primary_success=_str_or_none("primary_success"),
        brief_summary=_str_or_none("brief_summary"),
    )


def load_facets(root: Path | None = None) -> dict[str, FacetRecord]:
    """Walk `root/*.json` and return dict[session_id, FacetRecord].

    Args:
        root: directory holding `<session_id>.json` files. Defaults to
            `~/.claude/usage-data/facets`. For testing, point at a temp
            directory.

    Returns:
        Dict keyed by session_id. Files that fail to parse (non-JSON,
        missing session_id, IO error) are skipped silently — same
        line-by-line resilience discipline as ingest_claude_jsonl.

    Empty dict when root does not exist (graceful — no `/insights` run
    yet on this machine).
    """
    if root is None:
        root = DEFAULT_FACETS_ROOT
    root = Path(root).expanduser()
    if not root.exists() or not root.is_dir():
        return {}

    out: dict[str, FacetRecord] = {}
    for path in sorted(root.glob("*.json")):
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            # Stray bad file — skip silently per docstring.
            continue
        if not isinstance(payload, dict):
            continue
        record = _from_dict(payload)
        if record is None or record.session_id is None:
            continue
        out[record.session_id] = record
    return out


def attach_facets_to_events(
    events: Iterable[Event],
    facets: dict[str, FacetRecord],
) -> Iterator[Event]:
    """Yield each event with `event.facet` populated when the event's
    session has a matching FacetRecord in `facets`.

    Args:
        events: Event iterable (typically the output of
            ingest_claude_jsonl — a generator).
        facets: dict from load_facets.

    Yields:
        Event records, one per input event. event.facet is set to the
        matching FacetRecord when `event.session in facets`, otherwise
        left as None.

    Generator on purpose: a full ingest may produce millions of Event
    records; we never materialize the joined list.
    """
    for ev in events:
        ev.facet = facets.get(ev.session)
        yield ev
