"""main.py — Stage 1+2 orchestrator + subagent payload emitter.

Walks ``~/.claude/projects/**/*.jsonl``, joins ``~/.claude/usage-data/facets``,
detects friction signals, aggregates per target Skill, ranks top-N, and emits
two artifacts:

- **JSON payload on stdout** consumed by the Part 3 SKILL.md prose that drives
  ``code-toolkit:dispatching-parallel-agents`` fan-out. Shape per plan T9 §(f).
- **Markdown summary on stderr** for human read-along during runs.

Python does NOT call ``Agent()`` itself — see Plan Part 2 §"Plan-time decisions
inherited from Part 1" / "Subagent dispatch": the dispatch is handled by Claude
at runtime via ``code-toolkit:dispatching-parallel-agents``; this script just
prepares the payload.

External surface verification (memory project_external_surface_grounding_discipline.md):

- ``claude-haiku-4-5-20251001`` model literal — locked at this writing per
  system-prompt environment metadata.
- ``code-toolkit:dispatching-parallel-agents`` — internal sibling skill in
  this repo at ``code-toolkit/skills/dispatching-parallel-agents/SKILL.md``;
  verified by ``ls`` at implementer-time. Not a 3rd-party API.

Per Plan Part 2 §Task 9.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path

from aggregate import (
    AggregateRecord,
    aggregate_by_skill,
    rank_top_n,
    severity_score_for_session,
)
from event import Event
from facets import attach_facets_to_events, load_facets
from friction_signals import (
    Signal,
    detect_interrupt_after_brainstorm,
    detect_needs_revision_streak,
    detect_redispatch_concentration,
    detect_tool_error_clusters,
    load_thresholds,
)
from ingest import ingest_claude_jsonl

# Locked Haiku model literal for per-trajectory subagent dispatch.
HAIKU_MODEL_ID = "claude-haiku-4-5-20251001"

# Cap on how many trajectories (sessions) we dispatch per target skill.
# Limits subagent fan-out so we don't burn the org budget on big mines.
DEFAULT_MAX_TRAJECTORIES_PER_SKILL = 5

# Default top-N for ranking.
DEFAULT_TOP_N = 5

# Default target skill glob.
DEFAULT_TARGET_PATTERN = "code-toolkit:*"

# Repo-root resolution: this file lives at
# ``dev-workflow/skills/distill-sessions/scripts/main.py``. monkey-skills root
# is 4 parents up.
_REPO_ROOT = Path(__file__).resolve().parents[4]


# ---------------------------------------------------------------------------
# Skill name → SKILL.md path resolver.
# ---------------------------------------------------------------------------


def _resolve_skill_md_path(skill_name: str) -> Path | None:
    """Map ``<plugin>:<skill>`` → ``<plugin>/skills/<skill>/SKILL.md`` under
    the monkey-skills repo root.

    Returns the resolved Path (regardless of existence) or None when
    ``skill_name`` is not of the form ``<plugin>:<skill>``.
    """
    if ":" not in skill_name:
        return None
    plugin, skill = skill_name.split(":", 1)
    if not plugin or not skill:
        return None
    return _REPO_ROOT / plugin / "skills" / skill / "SKILL.md"


def _read_skill_md(path: Path | None) -> str:
    """Read SKILL.md content; return empty string if missing / unreadable.

    The payload still carries the path so the subagent can decide what to do
    when the body is absent (e.g. external-surface skill).
    """
    if path is None or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


# ---------------------------------------------------------------------------
# Friction-level heuristic (per-session).
# ---------------------------------------------------------------------------


def _friction_level_for_session(
    session_id: str, signals: list[Signal]
) -> str:
    """Map (session, attached signals) → "low" / "mid" / "high".

    - **high**: ≥2 high-severity signals in this session.
    - **mid**: any mid-or-high severity signal in this session, OR ≥2 signals
      of any severity.
    - **low**: otherwise (≤1 low-severity signal).
    """
    per_session = [s for s in signals if s.session == session_id]
    high_count = sum(1 for s in per_session if s.severity == "high")
    mid_or_high = sum(1 for s in per_session if s.severity in ("mid", "high"))
    if high_count >= 2:
        return "high"
    if mid_or_high >= 1 or len(per_session) >= 2:
        return "mid"
    return "low"


# ---------------------------------------------------------------------------
# Per-session kind classifier (failure vs success).
# ---------------------------------------------------------------------------


def _kind_for_session(session_id: str, events: list[Event], friction_level: str) -> list[str]:
    """Decide kind(s) for one session.

    Returns a list of kind strings. Normally a single-element list; dual-
    dispatch when the session was high-friction but ultimately succeeded
    (both failure-analysis and success-analysis prompts add value).

    Preference order:
      1. /insights facet ``outcome``: ``failed`` / ``partially_achieved`` →
         [``failure``]; ``fully_achieved`` / ``mostly_achieved`` → [``success``],
         EXCEPT when friction_level is ``high`` → dual [``failure``, ``success``].
      2. Fallback (no facet): friction_level ``high`` or ``mid`` → [``failure``];
         ``low`` → [``success``].
    """
    for ev in events:
        if ev.session != session_id:
            continue
        if ev.facet is None or ev.facet.outcome is None:
            continue
        if ev.facet.outcome in ("failed", "partially_achieved"):
            return ["failure"]
        if ev.facet.outcome in ("fully_achieved", "mostly_achieved"):
            if friction_level == "high":
                return ["failure", "success"]
            return ["success"]
    return ["failure"] if friction_level in ("high", "mid") else ["success"]


# ---------------------------------------------------------------------------
# Event → JSON-safe dict (asdict + drop FacetRecord cycle hazards).
# ---------------------------------------------------------------------------


def _event_to_dict(event: Event) -> dict[str, object]:
    """Convert Event → JSON-safe dict.

    ``dataclasses.asdict`` would recurse into ``event.facet`` (also a dataclass)
    fine, but the resulting payload bloats the per-trajectory subagent input.
    We strip ``facet`` from the per-event dict (the orchestrator already
    consumed it for kind classification).
    """
    d = asdict(event)
    d.pop("facet", None)
    return d


def _aggregate_record_to_dict(rec: AggregateRecord) -> dict[str, object]:
    """Convert AggregateRecord → JSON-safe dict.

    ``project_paths`` is a set → list. ``signals`` carries Event references in
    its evidence → convert to dicts. Everything else is already JSON-safe.
    """
    return {
        "skill_name": rec.skill_name,
        "sessions": list(rec.sessions),
        "event_count": rec.event_count,
        "signals": [
            {
                "kind": s.kind,
                "session": s.session,
                "ts": s.ts,
                "severity": s.severity,
                "evidence": [_event_to_dict(ev) for ev in s.evidence],
            }
            for s in rec.signals
        ],
        "project_paths": sorted(rec.project_paths),
        "facet_summary": rec.facet_summary,
        "confidence": rec.confidence,
        "frequency_norm": rec.frequency_norm,
        "time_cost_norm": rec.time_cost_norm,
        "cross_project_norm": rec.cross_project_norm,
        "recency_norm": rec.recency_norm,
    }


# ---------------------------------------------------------------------------
# Cross-skill session routing: attribute each multi-skill session to the
# skill with the highest friction-density score for that session.
# ---------------------------------------------------------------------------


def _compute_session_to_skill(ranked: list[AggregateRecord]) -> dict[str, str]:
    """Build a ``{session_id: skill_name}`` map for friction-density routing.

    For every session that appears in 2+ skills' ``rec.sessions``, compute
    ``severity_score_for_session(rec, session_id)`` for each skill that lists
    it, and assign the session to the skill with the maximum score.

    Tie-break: alphabetically-first skill name (``min()`` over skill names).
    This preserves determinism across runs and matches the task spec.

    Sessions that appear in exactly ONE skill are attributed to that skill
    unconditionally — no scoring overhead needed.

    Returns a dict covering ALL sessions across all ranked records.
    """
    # Map each session_id → set of skill names that list it.
    session_skills: dict[str, list[str]] = {}
    for rec in ranked:
        for session_id in rec.sessions:
            session_skills.setdefault(session_id, []).append(rec.skill_name)

    # Build lookup: skill_name → rec (for score computation).
    rec_by_skill: dict[str, AggregateRecord] = {rec.skill_name: rec for rec in ranked}

    result: dict[str, str] = {}
    for session_id, skills in session_skills.items():
        if len(skills) == 1:
            result[session_id] = skills[0]
        else:
            # Multi-skill: pick skill with max score; tie-break = min(skill_name).
            best_skill = min(
                skills,
                key=lambda sk: (-severity_score_for_session(rec_by_skill[sk], session_id), sk),
            )
            result[session_id] = best_skill

    return result


# ---------------------------------------------------------------------------
# subagent_payload entry builder.
# ---------------------------------------------------------------------------


def _build_subagent_entries(
    skill_name: str,
    selected_sessions: list[str],
    events_by_session: dict[str, list[Event]],
    target_skill_path: Path | None,
    target_skill_md_content: str,
    session_friction: dict[str, str],
    *,
    session_to_skill: dict[str, str] | None = None,
) -> list[dict[str, object]]:
    """Build one subagent_payload entry per (session, kind) pair.

    Each entry's ``trajectory_id`` is a deterministic uuid5 over the
    (skill, session, kind) tuple so two runs of the same mine produce
    identical IDs — useful for caching subagent results.

    ``session_friction`` is a ``{session_id: "low"|"mid"|"high"}`` map
    produced by the caller (``main()``) from the same Signal list used to
    build ``top_skills.sessions``. We thread the real friction_level
    through rather than hardcoding a fallback so a low-friction session
    without a /insights facet routes to ``prompt-success-analysis.md``
    instead of being silently tagged ``kind="failure"``.
    """
    out: list[dict[str, object]] = []
    namespace = uuid.UUID("00000000-0000-0000-0000-000000000001")
    target_path_str = str(target_skill_path) if target_skill_path else ""
    for session_id in selected_sessions:
        # Cross-skill routing gate: skip sessions attributed to a different skill.
        if session_to_skill is not None and session_to_skill.get(session_id, skill_name) != skill_name:
            continue
        sess_events = events_by_session.get(session_id, [])
        if not sess_events:
            continue
        # Per-session kind from /insights facet outcome (preferred) OR the
        # real friction_level (caller-supplied; "low"|"mid"|"high"). Default
        # to "low" → success only if the session is genuinely absent from
        # the friction map (defensive; should not happen because main()
        # populates it for every session it dispatches).
        friction_level = session_friction.get(session_id, "low")
        kinds = _kind_for_session(session_id, sess_events, friction_level=friction_level)
        session_events_dicts = [_event_to_dict(ev) for ev in sess_events]
        for kind in kinds:
            prompt_path = (
                "agents/prompt-failure-analysis.md"
                if kind == "failure"
                else "agents/prompt-success-analysis.md"
            )
            trajectory_id = str(
                uuid.uuid5(namespace, f"{skill_name}|{session_id}|{kind}")
            )
            out.append(
                {
                    "trajectory_id": trajectory_id,
                    "session_id": session_id,
                    "kind": kind,
                    "prompt_path": prompt_path,
                    "model": HAIKU_MODEL_ID,
                    "input": {
                        "session_events": session_events_dicts,
                        "target_skill_path": target_path_str,
                        "target_skill_md_content": target_skill_md_content,
                    },
                }
            )
    return out


# ---------------------------------------------------------------------------
# Markdown stderr summary renderer.
# ---------------------------------------------------------------------------


def _render_summary_markdown(
    top_skills: list[dict[str, object]],
    config: dict[str, object],
) -> str:
    """Human-readable summary block for stderr."""
    lines: list[str] = []
    lines.append("# distill-sessions v0.1 — run summary")
    lines.append("")
    lines.append(f"- run_id: `{config.get('run_id')}`")
    lines.append(f"- target_pattern: `{config.get('target_pattern')}`")
    lines.append(f"- top_n: {config.get('top_n')}")
    lines.append(f"- max_trajectories_per_skill: {config.get('max_trajectories_per_skill')}")
    lines.append("")
    lines.append("## Top skills")
    lines.append("")
    if not top_skills:
        lines.append("_(no skills cleared the min_session_count threshold)_")
    else:
        for entry in top_skills:
            lines.append(f"- **{entry['skill']}**")
            for sess in entry["sessions"]:
                lines.append(
                    f"  - session `{sess['session_id']}`: "
                    f"friction={sess['friction_level']}, "
                    f"events={sess['event_count']}"
                )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entrypoint.
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main",
        description=(
            "Stage 1+2 orchestrator: walk Claude Code JSONL transcripts, "
            "detect friction signals, aggregate per target Skill, emit "
            "subagent dispatch payload on stdout + markdown summary on stderr."
        ),
    )
    parser.add_argument(
        "--target-skill-pattern",
        default=DEFAULT_TARGET_PATTERN,
        help="fnmatch glob applied to skill_invocation (default: %(default)s)",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="optional JSON file overriding thresholds (see friction_signals.load_thresholds)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=DEFAULT_TOP_N,
        help="cap on top_skills returned (default: %(default)s)",
    )
    parser.add_argument(
        "--max-trajectories-per-skill",
        type=int,
        default=DEFAULT_MAX_TRAJECTORIES_PER_SKILL,
        help="cap on subagent_payload entries per skill (default: %(default)s)",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="override ~/.claude/projects root (mainly for tests)",
    )
    parser.add_argument(
        "--facets-root",
        default=None,
        help="override ~/.claude/usage-data/facets root (mainly for tests)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the Stage 1+2 orchestrator.

    Returns process exit code (0 on success). Stdout receives the JSON
    payload; stderr receives the markdown summary.
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    # Step (a) — thresholds (Q5 defaults; --config overrides).
    config_path = Path(args.config).expanduser() if args.config else None
    thresholds = load_thresholds(config_path)

    # Step (b) — walk JSONL.
    project_root = Path(args.project_root).expanduser() if args.project_root else None
    events_iter = ingest_claude_jsonl(root=project_root)

    # Step (c) — load facets and join.
    facets_root = Path(args.facets_root).expanduser() if args.facets_root else None
    facets = load_facets(root=facets_root)
    joined_iter = attach_facets_to_events(events_iter, facets)

    # Materialize once — Part-1 modules accept list-shaped inputs.
    events: list[Event] = list(joined_iter)

    # Step (d) — extract signals.
    signals: list[Signal] = []
    signals.extend(
        detect_interrupt_after_brainstorm(
            events, window_sec=thresholds["interrupt_window_sec"]
        )
    )
    signals.extend(
        detect_tool_error_clusters(
            events, proximity_events=thresholds["tool_error_proximity_events"]
        )
    )
    signals.extend(
        detect_needs_revision_streak(
            events, threshold=thresholds["needs_revision_threshold"]
        )
    )
    signals.extend(
        detect_redispatch_concentration(
            events, threshold=thresholds["redispatch_threshold"]
        )
    )

    # Step (e) — aggregate + rank.
    records = aggregate_by_skill(
        events, signals, target_pattern=args.target_skill_pattern
    )
    ranked = rank_top_n(records, n=args.top_n)

    # Build per-skill events index for kind classification + payload input.
    events_by_session: dict[str, list[Event]] = {}
    for ev in events:
        events_by_session.setdefault(ev.session, []).append(ev)

    # Step (f) — JSON payload.
    run_id = str(uuid.uuid4())
    generated_at = datetime.now(timezone.utc).isoformat()

    top_skills_out: list[dict[str, object]] = []
    subagent_payload: list[dict[str, object]] = []

    # Compute cross-skill session routing before the per-skill loop so each
    # skill's _build_subagent_entries call can skip sessions attributed away.
    session_to_skill = _compute_session_to_skill(ranked)

    for rec in ranked:
        target_skill_path = _resolve_skill_md_path(rec.skill_name)
        target_skill_md_content = _read_skill_md(target_skill_path)

        # Per-session friction levels (uses signals attached to this rec).
        sessions_out: list[dict[str, object]] = []
        for session_id in rec.sessions:
            friction_level = _friction_level_for_session(session_id, rec.signals)
            event_count = sum(
                1 for ev in events_by_session.get(session_id, [])
                if ev.skill_invocation == rec.skill_name
            )
            sessions_out.append(
                {
                    "session_id": session_id,
                    "friction_level": friction_level,
                    "event_count": event_count,
                }
            )

        # Sort sessions by friction (high→mid→low), keep top-K for dispatch.
        _rank = {"high": 0, "mid": 1, "low": 2}
        sessions_out_sorted = sorted(
            sessions_out, key=lambda s: _rank.get(str(s["friction_level"]), 3)
        )
        selected = [
            str(s["session_id"])
            for s in sessions_out_sorted[: args.max_trajectories_per_skill]
        ]

        # Real per-session friction_level — threaded into the entry builder
        # so the kind classifier's friction-level fallback reflects the
        # session's actual signal load (not a hardcoded "high").
        session_friction = {
            str(s["session_id"]): str(s["friction_level"])
            for s in sessions_out
        }

        top_skills_out.append(
            {
                "skill": rec.skill_name,
                "sessions": sessions_out,
                "aggregate_record": _aggregate_record_to_dict(rec),
            }
        )

        subagent_payload.extend(
            _build_subagent_entries(
                skill_name=rec.skill_name,
                selected_sessions=selected,
                events_by_session=events_by_session,
                target_skill_path=target_skill_path,
                target_skill_md_content=target_skill_md_content,
                session_friction=session_friction,
                session_to_skill=session_to_skill,
            )
        )

    config_block: dict[str, object] = {
        "run_id": run_id,
        "target_pattern": args.target_skill_pattern,
        "top_n": args.top_n,
        "max_trajectories_per_skill": args.max_trajectories_per_skill,
        "thresholds": thresholds,
    }

    payload = {
        "run_id": run_id,
        "generated_at": generated_at,
        "config": config_block,
        "top_skills": top_skills_out,
        "subagent_payload": subagent_payload,
    }

    # Stdout — single JSON object, no trailing newline noise.
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))

    # Stderr — markdown summary for human read-along.
    sys.stderr.write(_render_summary_markdown(top_skills_out, config_block))

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
