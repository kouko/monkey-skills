"""test_main_e2e.py — golden-fixture end-to-end test for main.main().

Plan Part 2 §Task 10. Exercises the full Stage 1+2 pipeline end-to-end:

    JSONL files on disk
        → ingest.py
        → facets.py (join /insights pre-classification)
        → friction_signals.py (4 detectors)
        → aggregate.py (group + dedup + score + rank)
        → main.py (top-N + subagent_payload)
        → JSON on stdout

The three synthetic JSONL session fixtures + one facets fixture are
embedded as Python string constants in this file (see ``_SESSION_*_JSONL``
and ``_SESSION1_FACET_JSON`` below). The test writes them to a per-test
``tmp_path``-shaped tree at runtime rather than committing ``.jsonl``
files at ``scripts/`` root — committed JSONLs would be picked up by
``test_ingest.py``'s directory-recursive walker over ``scripts/`` and
break the existing ``len(events) == 8`` assertion against
``fixture_sample.jsonl``. The fixture content stays "golden" in the
git-tracked sense: the strings are version-controlled here, the hash is
locked.

The three sessions exercise two friction patterns plus one low-friction
control:

- **Session 1** — interrupt-after-brainstorm Pattern 1. Two brainstorming
  Skill calls each immediately followed by ``[Request interrupted by
  user]`` within 30s, producing two high-severity
  ``interrupt_after_brainstorm`` signals — ``friction_level=high``.
  Carries a /insights facet (``outcome=partially_achieved``) so the
  facet-aware kind classifier confirms ``kind=failure``.
- **Session 2** — tool_error_cluster Pattern 4 + Pattern 3 NEEDS_REVISION
  streak. Four tool_use_error rows within proximity (cluster size 4 →
  ``severity=high``) plus four ``NEEDS_REVISION`` text matches → two
  high-severity signals stacked, ``friction_level=high``. No /insights
  facet — exercises the friction-level fallback in
  ``_kinds_for_session``.
- **Session 3** — clean control. One brainstorming Skill call, one
  assistant text reply, one polite user thank-you. Zero friction signals
  → ``friction_level=low``, ``kind=success`` via the fallback.

Two assertion classes back the snapshot:

1. **Structural** — top_skills carries ``code-toolkit:brainstorming``
   with all 3 sessions present and at least one high-friction session;
   subagent_payload references real ``agents/prompt-{failure,success}-
   analysis.md`` paths and the locked Haiku model literal.
2. **Snapshot hash** — sha256 over the stable subset (sorted (skill,
   friction_level) tuples + sorted prompt_paths + models). Run-id and
   timestamp are excluded so the test stays deterministic.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Allow `import main` when pytest is invoked from the repo root — same
# pattern as test_main.py.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import main  # noqa: E402


# ---------------------------------------------------------------------------
# Session fixtures — embedded JSONL content.
# ---------------------------------------------------------------------------

_SESSION1_ID = "e2e1ssss-aaaa-bbbb-cccc-dddddddddddd"
_SESSION2_ID = "e2e2ssss-aaaa-bbbb-cccc-dddddddddddd"
_SESSION3_ID = "e2e3ssss-aaaa-bbbb-cccc-dddddddddddd"


def _line(record: dict) -> str:
    """Serialize one JSONL record line."""
    return json.dumps(record, separators=(",", ":"))


def _session1_jsonl() -> str:
    """Pattern 1 — two brainstorming → interrupt pairs, each Δt ≤ 30s.

    Yields two high-severity ``interrupt_after_brainstorm`` signals →
    ``friction_level=high``.
    """
    sid = _SESSION1_ID
    return "\n".join([
        _line({
            "parentUuid": None, "isSidechain": False, "type": "user",
            "message": {"role": "user", "content": "<e2e session1 prompt>"},
            "uuid": "e2e10001-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T10:00:00.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e10001-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": "msg_e2e_1_01",
                "role": "assistant",
                "content": [{
                    "type": "tool_use", "id": "toolu_e2e_1_01",
                    "name": "Skill",
                    "input": {"skill": "code-toolkit:brainstorming",
                              "args": "first attempt"},
                }],
            },
            "uuid": "e2e10002-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T10:00:05.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e10002-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "user",
            "message": {"role": "user", "content": [
                {"type": "text", "text": "[Request interrupted by user]"},
            ]},
            "uuid": "e2e10003-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T10:00:30.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e10003-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": "msg_e2e_1_02",
                "role": "assistant",
                "content": [{
                    "type": "tool_use", "id": "toolu_e2e_1_02",
                    "name": "Skill",
                    "input": {"skill": "code-toolkit:brainstorming",
                              "args": "second attempt"},
                }],
            },
            "uuid": "e2e10004-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T10:01:00.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e10004-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "user",
            "message": {"role": "user", "content": [
                {"type": "text", "text": "[Request interrupted by user]"},
            ]},
            "uuid": "e2e10005-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T10:01:20.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
    ]) + "\n"


def _session2_jsonl() -> str:
    """Pattern 4 + Pattern 3 stacked.

    - Four tool_use_error tool_results within proximity=10 → tool_error
      cluster of 4 → high severity.
    - Four ``NEEDS_REVISION`` text matches → needs_revision_streak of 4
      → high severity.

    Two stacked high-severity signals → ``friction_level=high``. No
    /insights facet, so the friction-level fallback in
    ``_kinds_for_session`` decides kind.
    """
    sid = _SESSION2_ID
    records = [
        {
            "parentUuid": None, "isSidechain": False, "type": "user",
            "message": {"role": "user", "content": "<e2e session2 prompt>"},
            "uuid": "e2e20001-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T11:00:00.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        },
        {
            "parentUuid": "e2e20001-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": "msg_e2e_2_01",
                "role": "assistant",
                "content": [{
                    "type": "tool_use", "id": "toolu_e2e_2_01",
                    "name": "Skill",
                    "input": {"skill": "code-toolkit:brainstorming",
                              "args": "plan refactor"},
                }],
            },
            "uuid": "e2e20002-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T11:00:05.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        },
    ]
    # Four Edit-then-tool_error pairs, all within proximity_events=10.
    for i, letter in enumerate("abcd"):
        records.append({
            "parentUuid": f"e2e2000{2 + 2 * i}-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": f"msg_e2e_2_{i + 2:02d}",
                "role": "assistant",
                "content": [{
                    "type": "tool_use", "id": f"toolu_e2e_2_{i + 2:02d}",
                    "name": "Edit",
                    "input": {"file_path": f"/tmp/{letter}.py",
                              "old_string": "x", "new_string": "y"},
                }],
            },
            "uuid": f"e2e2000{3 + 2 * i}-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": f"2026-05-22T11:00:{10 + i * 5:02d}.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        })
        records.append({
            "parentUuid": f"e2e2000{3 + 2 * i}-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "user",
            "message": {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": f"toolu_e2e_2_{i + 2:02d}",
                "content": (
                    "<tool_use_error>File has not been read yet. "
                    "Read it first before writing to it.</tool_use_error>"
                ),
                "is_error": True,
            }]},
            "uuid": f"e2e2000{4 + 2 * i}-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": f"2026-05-22T11:00:{12 + i * 5:02d}.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        })
    # Four NEEDS_REVISION user messages — text-pattern detector counts 4.
    for i in range(4):
        records.append({
            "parentUuid": f"e2e2001{i}-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "user",
            "message": {
                "role": "user",
                "content": (
                    f"Reviewer round {i + 1}: NEEDS_REVISION on T{i + 1} "
                    "(severity-rule mismatch). Please redo."
                ),
            },
            "uuid": f"e2e2002{i}-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": f"2026-05-22T11:01:{i * 5:02d}.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        })
    return "\n".join(_line(r) for r in records) + "\n"


def _session3_jsonl() -> str:
    """Clean baseline — one brainstorm Skill call, clean reply, polite
    user thank-you. Zero friction signals → ``friction_level=low``,
    ``kind=success``.
    """
    sid = _SESSION3_ID
    return "\n".join([
        _line({
            "parentUuid": None, "isSidechain": False, "type": "user",
            "message": {"role": "user",
                        "content": "<e2e session3 prompt — calm flow>"},
            "uuid": "e2e30001-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T12:00:00.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e30001-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": "msg_e2e_3_01",
                "role": "assistant",
                "content": [{
                    "type": "tool_use", "id": "toolu_e2e_3_01",
                    "name": "Skill",
                    "input": {"skill": "code-toolkit:brainstorming",
                              "args": "calm exploration"},
                }],
            },
            "uuid": "e2e30002-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T12:00:05.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e30002-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "assistant",
            "message": {
                "model": "claude-opus-4-7", "id": "msg_e2e_3_02",
                "role": "assistant",
                "content": [{
                    "type": "text",
                    "text": "Here is a clean brainstorm output with no friction.",
                }],
            },
            "uuid": "e2e30003-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T12:00:10.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
        _line({
            "parentUuid": "e2e30003-aaaa-bbbb-cccc-dddddddddddd",
            "isSidechain": False, "type": "user",
            "message": {"role": "user",
                        "content": "Thanks, this is exactly what I needed."},
            "uuid": "e2e30004-aaaa-bbbb-cccc-dddddddddddd",
            "timestamp": "2026-05-22T12:00:30.000Z",
            "sessionId": sid, "version": "2.1.144", "gitBranch": "main",
        }),
    ]) + "\n"


def _session1_facet_json() -> str:
    """Matching /insights facet for session 1.

    ``outcome=partially_achieved`` → kind classifier confirms
    ``kind=failure`` for the session-1 entries (irrespective of the
    friction_level fallback path).
    """
    return json.dumps({
        "session_id": _SESSION1_ID,
        "underlying_goal": "<e2e session1 underlying goal>",
        "goal_categories": {"feature": 1},
        "outcome": "partially_achieved",
        "user_satisfaction_counts": {"dissatisfied": 1},
        "claude_helpfulness": "moderately_helpful",
        "session_type": "single_task",
        "friction_counts": {"interrupts": 1},
        "friction_detail": "<e2e session1 friction detail>",
        "primary_success": "design_clarity",
        "brief_summary": "<e2e session1 brief summary>",
    }, indent=2)


# ---------------------------------------------------------------------------
# Locked snapshot hash.
# ---------------------------------------------------------------------------


# sha256 over ``_snapshot_subset(payload)`` json-dump. Captured on first
# GREEN run; any pipeline-shape change (severity thresholds, kind
# classifier rules, model literal swap) breaks this test loudly. To
# update: run the test, copy the ``actual`` value from the failure
# message into here.
EXPECTED_SNAPSHOT_HASH = (
    "d80119feaace01022b4695d1b4f6bb18770692387549afb85c54257f56986655"
)


# ---------------------------------------------------------------------------
# Fixture tree builder.
# ---------------------------------------------------------------------------


def _build_e2e_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Write the embedded fixture content to a Claude Code-shaped tree
    under tmp_path.

    Returns (projects_root, facets_root) where:

    - projects_root contains ``-Users-kouko-e2e-fixture/<session_id>.jsonl``
      for each of the three sessions.
    - facets_root contains ``<session1_id>.json`` (only session 1 carries
      a facet — sessions 2 and 3 stay facet-less, exercising the
      no-facet branch in ``main._kinds_for_session``).
    """
    projects_root = tmp_path / "projects"
    project_dir = projects_root / "-Users-kouko-e2e-fixture"
    project_dir.mkdir(parents=True)

    facets_root = tmp_path / "facets"
    facets_root.mkdir()

    (project_dir / f"{_SESSION1_ID}.jsonl").write_text(
        _session1_jsonl(), encoding="utf-8"
    )
    (project_dir / f"{_SESSION2_ID}.jsonl").write_text(
        _session2_jsonl(), encoding="utf-8"
    )
    (project_dir / f"{_SESSION3_ID}.jsonl").write_text(
        _session3_jsonl(), encoding="utf-8"
    )

    (facets_root / f"{_SESSION1_ID}.json").write_text(
        _session1_facet_json(), encoding="utf-8"
    )

    return projects_root, facets_root


def _run_main(argv: list[str]) -> tuple[dict, str]:
    """Invoke ``main.main(argv)`` capturing stdout (parsed JSON) + stderr."""
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        rc = main.main(argv)
    assert rc == 0, f"main exited non-zero (rc={rc}); stderr={stderr.getvalue()}"
    payload = json.loads(stdout.getvalue())
    return payload, stderr.getvalue()


# ---------------------------------------------------------------------------
# Snapshot hash builder — stable subset excluding nondeterministic fields.
# ---------------------------------------------------------------------------


def _snapshot_subset(payload: dict) -> dict:
    """Extract the deterministic subset of the payload for hashing.

    Excludes ``run_id`` (uuid4) and ``generated_at`` (timestamp). Includes:

    - Sorted ``[(skill, friction_level), ...]`` across all top_skills
      sessions — captures the per-session friction classification.
    - Sorted ``prompt_path`` values — captures kind classification
      (failure vs success).
    - Sorted ``model`` values — pins the SUBAGENT_MODEL_ID literal.

    trajectory_id is deterministic (uuid5) but we don't include it
    because the goal here is "the analysis produced these
    classifications for these inputs" (already covered by
    test_main.py::test_trajectory_id_is_deterministic_across_runs).
    """
    sf_pairs: list[tuple[str, str]] = []
    for entry in payload["top_skills"]:
        skill = entry["skill"]
        for sess in entry["sessions"]:
            sf_pairs.append((skill, sess["friction_level"]))
    sf_pairs.sort()

    prompt_paths = sorted(e["prompt_path"] for e in payload["subagent_payload"])
    models = sorted({e["model"] for e in payload["subagent_payload"]})

    return {
        "skill_friction": sf_pairs,
        "prompt_paths": prompt_paths,
        "models": models,
    }


def _snapshot_hash(payload: dict) -> str:
    subset = _snapshot_subset(payload)
    blob = json.dumps(subset, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


# ---------------------------------------------------------------------------
# The E2E test.
# ---------------------------------------------------------------------------


def test_e2e_pipeline_produces_correct_payload(tmp_path: Path) -> None:
    projects_root, facets_root = _build_e2e_tree(tmp_path)

    payload, _stderr = _run_main(
        [
            "--target-skill-pattern",
            "code-toolkit:*",
            "--project-root",
            str(projects_root),
            "--facets-root",
            str(facets_root),
            "--top-n",
            "3",
        ]
    )

    # ---- Structural assertions ----

    # 3 sessions of code-toolkit:brainstorming → clears min_session_count=3.
    skill_names = [s["skill"] for s in payload["top_skills"]]
    assert len(payload["top_skills"]) >= 1, (
        f"expected >=1 top_skill, got 0; skill_names={skill_names!r}"
    )
    assert "code-toolkit:brainstorming" in skill_names, (
        f"code-toolkit:brainstorming missing from top_skills; got {skill_names!r}"
    )

    top = next(
        s for s in payload["top_skills"]
        if s["skill"] == "code-toolkit:brainstorming"
    )
    assert len(top["sessions"]) == 3, (
        f"expected 3 sessions for brainstorming, got {len(top['sessions'])}; "
        f"sessions={top['sessions']!r}"
    )

    # Sessions 1 + 2 each carry ≥2 high-severity signals → at least one
    # session must be classified high.
    friction_levels = [s["friction_level"] for s in top["sessions"]]
    assert "high" in friction_levels, (
        f"expected at least one high-friction session; "
        f"got friction_levels={friction_levels!r}"
    )

    # subagent_payload — locked model literal + real prompt paths.
    assert payload["subagent_payload"], "subagent_payload must be non-empty"
    for entry in payload["subagent_payload"]:
        assert entry["model"] == "claude-sonnet-4-6", (
            f"unexpected model literal {entry['model']!r}; "
            "expected claude-sonnet-4-6"
        )
        assert entry["prompt_path"] in (
            "agents/prompt-failure-analysis.md",
            "agents/prompt-success-analysis.md",
        ), f"unexpected prompt_path {entry['prompt_path']!r}"

    # At least one entry must route to prompt-failure-analysis.md (the
    # high-friction sessions are kind=failure).
    failure_entries = [
        e for e in payload["subagent_payload"]
        if e["prompt_path"].endswith("agents/prompt-failure-analysis.md")
    ]
    assert failure_entries, (
        "expected at least one subagent_payload entry routed to "
        "prompt-failure-analysis.md (no failure session detected)"
    )

    # ---- Snapshot hash ----

    actual_hash = _snapshot_hash(payload)
    assert actual_hash == EXPECTED_SNAPSHOT_HASH, (
        "E2E snapshot drift: pipeline output stable subset hash changed.\n"
        f"  expected: {EXPECTED_SNAPSHOT_HASH}\n"
        f"  actual:   {actual_hash}\n"
        f"  subset:   "
        f"{json.dumps(_snapshot_subset(payload), sort_keys=True, indent=2)}\n"
        "If the change is intentional (severity threshold shift, new "
        "detector, kind-classifier tweak), update EXPECTED_SNAPSHOT_HASH "
        "in this file."
    )
