"""test_main.py — Stage 1+2 orchestrator (main.py) tests.

Verifies that ``main.main(argv)``:

1. Walks a fixture project tree, ingests JSONL, detects friction signals,
   aggregates per-skill, and emits a JSON payload on stdout.
2. ``--top-n N`` caps the ``top_skills`` list at ``N``.
3. ``--config <override.json>`` swaps thresholds (cross-checked via
   ``friction_signals.load_thresholds``).
4. Stderr carries a human-readable markdown summary with section headers.

Per dev-workflow/skills/distill-sessions Plan Part 2 §Task 9.
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

import main
from aggregate import AggregateRecord
from event import Event
from friction_signals import Signal


HERE = Path(__file__).parent


# ---------------------------------------------------------------------------
# Fixture builder — minimal synthetic project tree exercising friction
# signal detectors. Sessions are constructed inline (no on-disk fixtures
# beyond what already lives at scripts/ root) so the test stays
# self-contained and flat-subfolder hook stays clean.
# ---------------------------------------------------------------------------


def _build_fixture_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Build a tiny ~/.claude/projects-shaped tree under tmp_path.

    Returns (projects_root, facets_root). 3 sessions invoking
    ``code-toolkit:brainstorming`` so the skill clears the
    ``min_session_count=3`` threshold; each session has an immediate
    user_interrupt after the brainstorming call → high-severity
    interrupt_after_brainstorm signals.
    """
    projects_root = tmp_path / "projects" / "-Users-kouko-fixture"
    projects_root.mkdir(parents=True)
    facets_root = tmp_path / "facets"
    facets_root.mkdir()

    base_ts = "2026-05-22T10:14:0"
    sessions = [
        f"sess{i:04d}-aaaa-bbbb-cccc-dddddddddddd" for i in range(3)
    ]

    for i, session_id in enumerate(sessions):
        # One brainstorming Skill call + one snap-back user_interrupt
        # (Δt < 60s → high severity per friction_signals.py).
        lines = [
            json.dumps(
                {
                    "type": "assistant",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.000Z",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"toolu_{i}_01",
                                "name": "Skill",
                                "input": {
                                    "skill": "code-toolkit:brainstorming",
                                    "args": "test",
                                },
                            }
                        ],
                    },
                }
            ),
            json.dumps(
                {
                    "type": "user",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.500Z",
                    "message": {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "[Request interrupted by user]"}
                        ],
                    },
                }
            ),
        ]
        (projects_root / f"{session_id}.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    return projects_root.parent, facets_root


def _run_main(argv: list[str]) -> tuple[dict, str]:
    """Invoke ``main.main(argv)`` capturing stdout (parsed as JSON) and stderr."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = main.main(argv)
    assert rc == 0, f"main exited non-zero (rc={rc}); stderr={stderr.getvalue()}"
    raw = stdout.getvalue()
    payload = json.loads(raw)
    return payload, stderr.getvalue()


# ---------------------------------------------------------------------------
# Test 1 — payload shape.
# ---------------------------------------------------------------------------


def test_main_emits_payload_json_to_stdout(tmp_path: Path) -> None:
    projects_root, facets_root = _build_fixture_tree(tmp_path)

    payload, _stderr = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
        ]
    )

    # Required top-level keys.
    assert "run_id" in payload
    assert "generated_at" in payload
    assert "config" in payload
    assert "top_skills" in payload
    assert "subagent_payload" in payload
    assert isinstance(payload["top_skills"], list)
    assert isinstance(payload["subagent_payload"], list)

    # The fixture has 3 sessions of code-toolkit:brainstorming with a
    # high-severity interrupt each — that skill MUST be in top_skills.
    skill_names = [s["skill"] for s in payload["top_skills"]]
    assert "code-toolkit:brainstorming" in skill_names

    top = next(s for s in payload["top_skills"] if s["skill"] == "code-toolkit:brainstorming")
    assert "sessions" in top
    assert "aggregate_record" in top
    assert isinstance(top["sessions"], list)
    assert len(top["sessions"]) == 3
    for sess in top["sessions"]:
        assert set(sess.keys()) >= {"session_id", "friction_level", "event_count"}
        assert sess["friction_level"] in ("low", "mid", "high")

    # subagent_payload entries reference the agents/ prompt paths and the
    # locked subagent model ID (Sonnet 4.6 1M-context per v0.4 brief Q-v0.4-1).
    assert payload["subagent_payload"], "subagent_payload must be non-empty"
    for entry in payload["subagent_payload"]:
        assert entry["model"] == "claude-sonnet-4-6"
        assert entry["prompt_path"] in (
            "agents/prompt-failure-analysis.md",
            "agents/prompt-success-analysis.md",
        )
        assert entry["kind"] in ("failure", "success")
        assert "input" in entry
        inp = entry["input"]
        assert "session_events" in inp
        assert "target_skill_path" in inp
        assert "target_skill_md_content" in inp
        assert isinstance(inp["session_events"], list)


# ---------------------------------------------------------------------------
# Test 2 — --top-n caps the list.
# ---------------------------------------------------------------------------


def test_top_n_caps_returned_skills(tmp_path: Path) -> None:
    """Synthesize multiple qualifying skills, assert --top-n 1 returns 1."""
    projects_root = tmp_path / "projects" / "p"
    projects_root.mkdir(parents=True)

    base_ts = "2026-05-22T10:14:0"
    # Two skills, each with ≥3 sessions to clear min_session_count.
    for skill in ("code-toolkit:brainstorming", "code-toolkit:writing-plans"):
        for i in range(3):
            session_id = f"{skill[-12:]}-sess-{i:04d}-cccc-dddddddddddd".replace(
                ":", "-"
            ).replace(" ", "")
            # Ensure session_id is 36-char-ish; ingest just needs str.
            lines = [
                json.dumps(
                    {
                        "type": "assistant",
                        "sessionId": session_id,
                        "timestamp": f"{base_ts}{i}.000Z",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "tool_use",
                                    "id": f"toolu_{skill}_{i}",
                                    "name": "Skill",
                                    "input": {"skill": skill, "args": "x"},
                                }
                            ],
                        },
                    }
                ),
                # Add a NEEDS_REVISION text marker so the skill picks up a
                # friction signal and qualifies as "interesting".
                json.dumps(
                    {
                        "type": "user",
                        "sessionId": session_id,
                        "timestamp": f"{base_ts}{i}.500Z",
                        "message": {
                            "role": "user",
                            "content": "NEEDS_REVISION on T1; NEEDS_REVISION on T2",
                        },
                    }
                ),
            ]
            (projects_root / f"{session_id}.jsonl").write_text(
                "\n".join(lines) + "\n", encoding="utf-8"
            )

    payload, _ = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root.parent),
            "--facets-root",
            str(tmp_path / "no-facets"),
            "--top-n",
            "1",
        ]
    )
    assert len(payload["top_skills"]) == 1


# ---------------------------------------------------------------------------
# Test 3 — --config override swaps thresholds.
# ---------------------------------------------------------------------------


def test_config_override_swaps_thresholds(tmp_path: Path) -> None:
    """Write a JSON override; assert the emitted ``config`` block carries the
    override value (cross-checks ``friction_signals.load_thresholds`` plumbing).
    """
    projects_root, facets_root = _build_fixture_tree(tmp_path)

    override_path = tmp_path / "override.json"
    override_path.write_text(
        json.dumps({"needs_revision_threshold": 99, "interrupt_window_sec": 30}),
        encoding="utf-8",
    )

    payload, _ = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
            "--config",
            str(override_path),
        ]
    )

    cfg = payload["config"]
    assert cfg["thresholds"]["needs_revision_threshold"] == 99
    assert cfg["thresholds"]["interrupt_window_sec"] == 30
    # Untouched threshold survives.
    assert cfg["thresholds"]["redispatch_threshold"] == 2


# ---------------------------------------------------------------------------
# Test 4 — stderr summary.
# ---------------------------------------------------------------------------


def test_stderr_contains_markdown_summary(tmp_path: Path) -> None:
    projects_root, facets_root = _build_fixture_tree(tmp_path)

    _payload, stderr_text = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
        ]
    )

    # Some markdown section header for top skills.
    assert "## Top skills" in stderr_text
    # And at least the qualifying skill name printed in the summary.
    assert "code-toolkit:brainstorming" in stderr_text


# ---------------------------------------------------------------------------
# Test 5 — trajectory_id determinism across runs.
#
# Round-2 fix for T9 🟡 #2: ``uuid.uuid5(namespace, "skill|session|kind")``
# is supposed to produce identical trajectory_ids across runs of the same
# mine so subagent results stay cacheable. A future refactor to uuid4
# would silently break that. Pin the contract.
# ---------------------------------------------------------------------------


def test_trajectory_id_is_deterministic_across_runs(tmp_path: Path) -> None:
    """Two runs of main() over the same fixture must produce identical
    subagent_payload trajectory_ids in the same order.
    """
    projects_root, facets_root = _build_fixture_tree(tmp_path)

    argv = [
        "--target-skill-pattern",
        "code-toolkit:*",
        "--project-root",
        str(projects_root),
        "--facets-root",
        str(facets_root),
    ]
    payload1, _ = _run_main(argv)
    payload2, _ = _run_main(argv)

    ids1 = [e["trajectory_id"] for e in payload1["subagent_payload"]]
    ids2 = [e["trajectory_id"] for e in payload2["subagent_payload"]]

    assert ids1, "subagent_payload must be non-empty for the determinism test to mean anything"
    assert ids1 == ids2, (
        f"trajectory_id determinism broken: run1={ids1!r} run2={ids2!r}"
    )


# ---------------------------------------------------------------------------
# Test 6 — low-friction session without facet maps to kind=success.
#
# Round-2 fix for T9 🟡 #1: ``_build_subagent_entries`` used to hardcode
# ``friction_level="high"`` as the fallback to ``_kinds_for_session``, so
# any session without a facet got tagged ``kind="failure"`` and routed to
# ``prompt-failure-analysis.md`` — even when the session's real
# friction_level was ``low`` (no signals at all). Pin the contract: a
# low-friction, no-facet session must be tagged ``kind="success"``.
# ---------------------------------------------------------------------------


def _build_fixture_with_low_friction_session(tmp_path: Path) -> tuple[Path, Path, str]:
    """Same base as ``_build_fixture_tree`` but with one extra session that
    has zero friction signals (just a Skill call, no interrupt, no
    NEEDS_REVISION, no tool errors). That session should get
    friction_level="low" → kind="success".

    Returns (projects_root, facets_root, low_session_id).
    """
    projects_root = tmp_path / "projects" / "-Users-kouko-fixture"
    projects_root.mkdir(parents=True)
    facets_root = tmp_path / "facets"
    facets_root.mkdir()

    base_ts = "2026-05-22T10:14:0"
    high_sessions = [
        f"sess{i:04d}-aaaa-bbbb-cccc-dddddddddddd" for i in range(3)
    ]
    low_session_id = "sessLOWX-aaaa-bbbb-cccc-dddddddddddd"

    # 3 high-friction sessions (interrupt within 0.5s of brainstorming).
    for i, session_id in enumerate(high_sessions):
        lines = [
            json.dumps(
                {
                    "type": "assistant",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.000Z",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"toolu_{i}_01",
                                "name": "Skill",
                                "input": {
                                    "skill": "code-toolkit:brainstorming",
                                    "args": "test",
                                },
                            }
                        ],
                    },
                }
            ),
            json.dumps(
                {
                    "type": "user",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.500Z",
                    "message": {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "[Request interrupted by user]"}
                        ],
                    },
                }
            ),
        ]
        (projects_root / f"{session_id}.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    # 4th session: brainstorming Skill call, zero friction signals,
    # zero facets → friction_level="low", kind should be "success".
    lines = [
        json.dumps(
            {
                "type": "assistant",
                "sessionId": low_session_id,
                "timestamp": f"{base_ts}4.000Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_low_01",
                            "name": "Skill",
                            "input": {
                                "skill": "code-toolkit:brainstorming",
                                "args": "calm-session",
                            },
                        }
                    ],
                },
            }
        ),
    ]
    (projects_root / f"{low_session_id}.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )

    return projects_root.parent, facets_root, low_session_id


def test_low_friction_no_facet_session_is_tagged_kind_success(tmp_path: Path) -> None:
    projects_root, facets_root, low_session_id = (
        _build_fixture_with_low_friction_session(tmp_path)
    )

    payload, _ = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
        ]
    )

    # Locate the low-friction session entry in subagent_payload.
    low_entries = [
        e for e in payload["subagent_payload"]
        if e["session_id"] == low_session_id
    ]
    assert low_entries, (
        f"low-friction session {low_session_id!r} missing from subagent_payload; "
        f"got sessions={[e['session_id'] for e in payload['subagent_payload']]!r}"
    )
    low = low_entries[0]
    assert low["kind"] == "success", (
        f"low-friction no-facet session should be kind=success, got kind={low['kind']!r}; "
        "this is the 🟡 #1 round-1 regression — friction_level fallback was hardcoded to 'high'"
    )
    assert low["prompt_path"] == "agents/prompt-success-analysis.md", (
        f"low-friction session should route to prompt-success-analysis.md, got {low['prompt_path']!r}"
    )

    # Sanity: the high-friction sessions remain kind=failure.
    high_entries = [
        e for e in payload["subagent_payload"]
        if e["session_id"] != low_session_id
    ]
    for e in high_entries:
        assert e["kind"] == "failure", (
            f"high-friction session {e['session_id']!r} should be kind=failure, "
            f"got kind={e['kind']!r}"
        )


# ---------------------------------------------------------------------------
# Test 7 — high-friction-success session emits dual-dispatch entries.
#
# Q-v0.3-3 (locked in brief): when friction_level="high" AND
# facet.outcome ∈ {"fully_achieved", "mostly_achieved"}, the pipeline
# must emit TWO subagent_payload entries for the same session:
#   - kind="failure" → agents/prompt-failure-analysis.md
#   - kind="success" → agents/prompt-success-analysis.md
# with distinct trajectory_ids (uuid5 namespace includes kind).
# One session counts as 2 dispatches for --max-trajectories-per-skill.
#
# Per feedback_kind_classifier_facet_outcome_dominates.md canonical fix-shape.
# ---------------------------------------------------------------------------


def _build_fixture_with_high_friction_success_session(
    tmp_path: Path,
) -> tuple[Path, Path, str]:
    """A minimal project tree with 3 high-friction sessions PLUS one
    high-friction session that also has facet.outcome="fully_achieved".

    Returns (projects_root_parent, facets_root, hfs_session_id) where
    hfs_session_id is the high-friction-success session that should trigger
    dual-dispatch.
    """
    projects_root = tmp_path / "projects" / "-Users-kouko-hfs"
    projects_root.mkdir(parents=True)
    facets_root = tmp_path / "facets"
    facets_root.mkdir()

    base_ts = "2026-05-25T08:00:0"
    # 3 plain high-friction sessions to clear min_session_count=3.
    plain_sessions = [
        f"sessHF{i:02d}-aaaa-bbbb-cccc-dddddddddddd" for i in range(3)
    ]
    # The 4th session: high-friction (interrupt) + fully_achieved outcome.
    hfs_session_id = "sessHFSX-aaaa-bbbb-cccc-dddddddddddd"

    for i, session_id in enumerate(plain_sessions):
        lines = [
            json.dumps(
                {
                    "type": "assistant",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.000Z",
                    "message": {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": f"toolu_hfs_{i}",
                                "name": "Skill",
                                "input": {
                                    "skill": "code-toolkit:brainstorming",
                                    "args": "test",
                                },
                            }
                        ],
                    },
                }
            ),
            # Interrupt within 0.5s → high-severity friction signal.
            json.dumps(
                {
                    "type": "user",
                    "sessionId": session_id,
                    "timestamp": f"{base_ts}{i}.500Z",
                    "message": {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "[Request interrupted by user]"}
                        ],
                    },
                }
            ),
        ]
        (projects_root / f"{session_id}.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    # hfs_session_id: 2 brainstorm calls + 2 immediate interrupts → 2
    # high-severity signals → _friction_level_for_session returns "high".
    hfs_lines = [
        json.dumps(
            {
                "type": "assistant",
                "sessionId": hfs_session_id,
                "timestamp": f"{base_ts}4.000Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_hfs_4a",
                            "name": "Skill",
                            "input": {
                                "skill": "code-toolkit:brainstorming",
                                "args": "test",
                            },
                        }
                    ],
                },
            }
        ),
        json.dumps(
            {
                "type": "user",
                "sessionId": hfs_session_id,
                "timestamp": f"{base_ts}4.500Z",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "[Request interrupted by user]"}
                    ],
                },
            }
        ),
        json.dumps(
            {
                "type": "assistant",
                "sessionId": hfs_session_id,
                "timestamp": f"{base_ts}5.000Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "tool_use",
                            "id": "toolu_hfs_4b",
                            "name": "Skill",
                            "input": {
                                "skill": "code-toolkit:brainstorming",
                                "args": "retry",
                            },
                        }
                    ],
                },
            }
        ),
        json.dumps(
            {
                "type": "user",
                "sessionId": hfs_session_id,
                "timestamp": f"{base_ts}5.500Z",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "[Request interrupted by user]"}
                    ],
                },
            }
        ),
    ]
    (projects_root / f"{hfs_session_id}.jsonl").write_text(
        "\n".join(hfs_lines) + "\n", encoding="utf-8"
    )

    # Write a facet JSON for hfs_session_id with outcome="fully_achieved".
    facet_payload = {
        "session_id": hfs_session_id,
        "outcome": "fully_achieved",
    }
    (facets_root / f"{hfs_session_id}.json").write_text(
        json.dumps(facet_payload), encoding="utf-8"
    )

    return projects_root.parent, facets_root, hfs_session_id


def test_high_friction_success_session_emits_dual_dispatch_entries(
    tmp_path: Path,
) -> None:
    """High-friction session with facet.outcome=fully_achieved must produce
    2 subagent_payload entries: kind=failure + kind=success, distinct
    trajectory_ids, correct prompt_path per kind.
    """
    projects_root, facets_root, hfs_session_id = (
        _build_fixture_with_high_friction_success_session(tmp_path)
    )

    payload, _ = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
        ]
    )

    hfs_entries = [
        e for e in payload["subagent_payload"]
        if e["session_id"] == hfs_session_id
    ]

    assert len(hfs_entries) == 2, (
        f"high-friction-success session should emit 2 entries "
        f"(kind=failure + kind=success), got {len(hfs_entries)}: "
        f"{[e['kind'] for e in hfs_entries]!r}"
    )

    kinds = {e["kind"] for e in hfs_entries}
    assert kinds == {"failure", "success"}, (
        f"expected kinds={{'failure','success'}}, got {kinds!r}"
    )

    failure_entry = next(e for e in hfs_entries if e["kind"] == "failure")
    success_entry = next(e for e in hfs_entries if e["kind"] == "success")

    assert failure_entry["prompt_path"] == "agents/prompt-failure-analysis.md", (
        f"failure entry has wrong prompt_path: {failure_entry['prompt_path']!r}"
    )
    assert success_entry["prompt_path"] == "agents/prompt-success-analysis.md", (
        f"success entry has wrong prompt_path: {success_entry['prompt_path']!r}"
    )

    assert failure_entry["trajectory_id"] != success_entry["trajectory_id"], (
        "failure and success entries must have distinct trajectory_ids"
    )


# ---------------------------------------------------------------------------
# Test 8 — cross-skill routing: session attributed to highest-friction skill.
#
# Q-v0.3-2 (locked in brief): when a session appears in 2+ skills' rec.sessions,
# _build_subagent_entries must emit an entry for that session ONLY for the skill
# with the highest severity_score_for_session. The lower-friction skill must
# skip that session.
#
# Mechanism: new kw-only arg ``session_to_skill: dict[str, str] | None`` on
# ``_build_subagent_entries``; gate inside the session loop skips sessions
# attributed to a different skill.
# ---------------------------------------------------------------------------


def _make_signal(session_id: str, severity: str, kind: str = "interrupt_after_brainstorm") -> Signal:
    """Minimal Signal for testing — evidence list can be empty for scoring tests."""
    ev = Event(
        agent="claude-code",
        session=session_id,
        ts="2026-05-25T10:00:00.000Z",
        role="user",
        text="[Request interrupted by user]",
        user_interrupt=True,
    )
    return Signal(kind=kind, session=session_id, ts=ev.ts, severity=severity, evidence=[ev])


def _make_aggregate_record(skill_name: str, sessions: list[str], signals: list[Signal]) -> AggregateRecord:
    """Minimal AggregateRecord for routing tests."""
    return AggregateRecord(
        skill_name=skill_name,
        sessions=sessions,
        event_count=len(sessions),
        signals=signals,
        project_paths=set(sessions),
    )


def _make_events_by_session(session_id: str, skill_name: str) -> dict[str, list[Event]]:
    """One event per session, enough to make _build_subagent_entries emit entries."""
    ev = Event(
        agent="claude-code",
        session=session_id,
        ts="2026-05-25T10:00:00.000Z",
        role="assistant",
        text=f"Skill call: {skill_name}",
        skill_invocation=skill_name,
    )
    return {session_id: [ev]}


def test_cross_skill_routing_attributes_session_to_highest_friction_skill() -> None:
    """Session with 2 high signals on brainstorming, 0 on writing-plans →
    only brainstorming subagent_payload should contain an entry for that session.

    Tests the ``session_to_skill`` gate in ``_build_subagent_entries`` and the
    ``_compute_session_to_skill`` helper in main.py.
    """
    shared_session = "sess-SHARED-aaaa-bbbb-cccc-dddddddddddd"
    brainstorm_skill = "code-toolkit:brainstorming"
    writing_plans_skill = "code-toolkit:writing-plans"

    # brainstorming rec: 2 high signals for the shared session.
    brainstorm_signals = [
        _make_signal(shared_session, "high"),
        _make_signal(shared_session, "high"),
    ]
    brainstorm_rec = _make_aggregate_record(brainstorm_skill, [shared_session], brainstorm_signals)

    # writing-plans rec: shared session listed, but 0 signals for it.
    writing_plans_rec = _make_aggregate_record(writing_plans_skill, [shared_session], [])

    ranked = [brainstorm_rec, writing_plans_rec]

    # Compute session_to_skill via the new helper.
    session_to_skill = main._compute_session_to_skill(ranked)

    # shared_session must be attributed to brainstorming (score=6.0 vs 0.0).
    assert session_to_skill.get(shared_session) == brainstorm_skill, (
        f"expected {shared_session!r} → {brainstorm_skill!r}, "
        f"got {session_to_skill.get(shared_session)!r}"
    )

    # Build entries for each skill using session_to_skill.
    events_by_session = _make_events_by_session(shared_session, brainstorm_skill)
    session_friction = {shared_session: "high"}

    brainstorm_entries = main._build_subagent_entries(
        skill_name=brainstorm_skill,
        selected_sessions=[shared_session],
        events_by_session=events_by_session,
        target_skill_path=None,
        target_skill_md_content="",
        session_friction=session_friction,
        session_to_skill=session_to_skill,
    )
    writing_plans_entries = main._build_subagent_entries(
        skill_name=writing_plans_skill,
        selected_sessions=[shared_session],
        events_by_session=events_by_session,
        target_skill_path=None,
        target_skill_md_content="",
        session_friction=session_friction,
        session_to_skill=session_to_skill,
    )

    brainstorm_sessions = {e["session_id"] for e in brainstorm_entries}
    writing_plans_sessions = {e["session_id"] for e in writing_plans_entries}

    assert shared_session in brainstorm_sessions, (
        f"brainstorming should contain entry for {shared_session!r}; "
        f"got sessions={brainstorm_sessions!r}"
    )
    assert shared_session not in writing_plans_sessions, (
        f"writing-plans must NOT contain entry for {shared_session!r} "
        f"(routed away by friction-density); got sessions={writing_plans_sessions!r}"
    )


def test_cross_skill_routing_tie_breaks_alphabetically() -> None:
    """Session with equal friction-density in both skills →
    routes to the alphabetically-first skill name.

    Equal scores: 1 high signal each (3.0 each). Alphabetic order:
    'code-toolkit:brainstorming' < 'code-toolkit:writing-plans'
    → brainstorming wins tie-break.
    """
    shared_session = "sess-TIE-aaaa-bbbb-cccc-dddddddddddd"
    brainstorm_skill = "code-toolkit:brainstorming"
    writing_plans_skill = "code-toolkit:writing-plans"

    # Each skill gets exactly 1 high signal for shared_session → score 3.0 each.
    brainstorm_rec = _make_aggregate_record(
        brainstorm_skill,
        [shared_session],
        [_make_signal(shared_session, "high")],
    )
    writing_plans_rec = _make_aggregate_record(
        writing_plans_skill,
        [shared_session],
        [_make_signal(shared_session, "high")],
    )

    ranked = [brainstorm_rec, writing_plans_rec]
    session_to_skill = main._compute_session_to_skill(ranked)

    # Tie → alphabetically first: brainstorming < writing-plans.
    assert session_to_skill.get(shared_session) == brainstorm_skill, (
        f"tie-break should route to alphabetically-first skill; "
        f"expected {brainstorm_skill!r}, got {session_to_skill.get(shared_session)!r}"
    )


# ---------------------------------------------------------------------------
# Test — _render_summary_markdown cost-estimate preview line.
#
# T5: the summary block must include a human-readable cost estimate so
# the user can make an informed decision at the preview pause before
# dispatching Sonnet subagents.
# ---------------------------------------------------------------------------


def test_render_summary_markdown_includes_cost_estimate() -> None:
    """_render_summary_markdown emits a '- estimated cost' line.

    WHY: before dispatching Sonnet subagents, the user sees this summary on
    stderr and decides whether to proceed. Without a cost hint, large sessions
    silently consume budget. The line must document the model and rate so the
    number is meaningful.
    """
    top_skills: list[dict] = []
    config: dict = {
        "run_id": "test-run",
        "target_pattern": "code-toolkit:*",
        "top_n": 3,
        "max_trajectories_per_skill": 5,
    }
    # A minimal subagent_payload — one entry with enough JSON bytes to produce
    # a non-zero cost estimate.
    subagent_payload = [
        {
            "trajectory_id": "aaaa-bbbb",
            "skill": "code-toolkit:brainstorming",
            "kind": "failure",
            "context": {"session_id": "sess-1", "target_skill_path": "/some/path"},
        }
    ]

    result = main._render_summary_markdown(top_skills, config, subagent_payload)

    assert "estimated cost" in result, (
        "_render_summary_markdown must include an 'estimated cost' line"
    )
    assert "Sonnet 4.6" in result, (
        "cost line must document model name so the rate is unambiguous"
    )
    assert "$3/Mtok" in result, (
        "cost line must document the per-token rate"
    )
