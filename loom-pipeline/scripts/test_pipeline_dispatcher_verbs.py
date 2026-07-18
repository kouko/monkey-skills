"""Structural test: using-loom-pipeline SKILL.md's §Batch mode dispatcher
loop documents the Task 9/10/12 verb semantics the dispatcher must actually
invoke — mark-running immediately after Workflow() returns, reconcile before
next on session takeover, and the reset/force-fail recovery verbs with their
SUSPECT / SUSPECT-COMPLETE operator handling.

Plan: docs/loom/plans/2026-07-18-loop-convergence-fixes.md Task 21.
"""
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[1]
SKILL_MD = PLUGIN_ROOT / "skills" / "using-loom-pipeline" / "SKILL.md"


def _body(text: str) -> str:
    """Text AFTER the closing frontmatter fence (see test_pipeline_skill_contract.py)."""
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md lost its frontmatter fences"
    return parts[2]


def _batch_mode_section(body: str) -> str:
    body_lower = body.lower()
    batch_idx = body_lower.find("## §batch mode")
    assert batch_idx != -1, "missing §Batch mode heading"
    return body[batch_idx:]


def test_mark_running_invoked_immediately_after_workflow_returns():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    section = _batch_mode_section(_body(text))

    workflow_idx = section.find("Workflow(")
    assert workflow_idx != -1, "missing Workflow( call in §Batch mode"
    mark_running_idx = section.find("mark-running")
    assert mark_running_idx != -1, "missing mark-running verb in §Batch mode"
    assert workflow_idx < mark_running_idx, (
        "mark-running must be documented AFTER Workflow() returns, not before"
    )
    assert "--run-id" in section and "--session-dir" in section, (
        "mark-running invocation must document both --run-id and --session-dir"
    )


def test_reconcile_runs_before_next_on_session_takeover():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    section = _batch_mode_section(_body(text))
    section_lower = section.lower()

    assert "reconcile" in section_lower, "missing reconcile verb in §Batch mode"
    assert (
        "fresh session" in section_lower or "takeover" in section_lower or "takes over" in section_lower
    ), "missing fresh-session-takeover framing for reconcile"

    reconcile_idx = section_lower.find("reconcile")
    next_idx = section_lower.find("batch_queue.py next")
    assert reconcile_idx != -1 and next_idx != -1
    assert reconcile_idx < next_idx, (
        "reconcile must be documented as running BEFORE next on takeover"
    )


def test_recovery_verbs_and_suspect_handling_documented():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    section = _batch_mode_section(_body(text))
    section_lower = section.lower()

    assert "reset" in section_lower, "missing reset recovery verb"
    assert "force-fail" in section_lower, "missing force-fail recovery verb"

    assert "suspect-complete" in section_lower, "missing SUSPECT-COMPLETE handling"
    assert "suspect" in section_lower, "missing SUSPECT handling"

    # SUSPECT is informational, human decides via the verbs.
    assert "human" in section_lower, (
        "missing human-decides framing for SUSPECT/SUSPECT-COMPLETE operator handling"
    )
