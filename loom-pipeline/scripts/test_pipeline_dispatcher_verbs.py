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

    # --session-dir semantics: it must name the PARENT of workflows/, not the
    # workflows/ subfolder itself (batch_queue.py:529-559 joins
    # <session_dir>/workflows/wf_<run_id>.json). A literal "this session's
    # workflows dir" reading records a path one level too deep.
    session_dir_idx = section.find("--session-dir")
    nearby = section[session_dir_idx:session_dir_idx + 600]
    assert "workflows/" in nearby and (
        "holds" in nearby or "subfolder" in nearby or "contains" in nearby
    ), (
        "--session-dir description must name the parent-of-workflows/ semantics"
    )
    assert "session's workflows dir" not in section.lower(), (
        "--session-dir must not be described as 'this session's workflows dir' "
        "(that is the inverted, one-level-too-deep reading)"
    )


def test_session_dir_derivation_grounded_with_fallback():
    """--session-dir is required=True but points at undocumented host
    internals (audit §4c). The doc must (a) show the typical path shape with
    a grounding note mirroring the resumeRunId precedent at SKILL.md:84, and
    (b) give an honest fallback when the dispatcher can't determine it."""
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    section = _batch_mode_section(_body(text))
    section_lower = section.lower()

    assert "~/.claude/projects/" in section, (
        "missing typical --session-dir path shape "
        "(~/.claude/projects/<project-slug>/<session-id>/)"
    )
    assert "grounding" in section_lower, (
        "missing a grounding note for the undocumented --session-dir surface"
    )
    assert "2026-07-18-agent-loop-convergence-audit" in section, (
        "grounding note must cite the audit doc backing the wf-record layout"
    )
    assert "undocumented" in section_lower, (
        "must disclose --session-dir derivation relies on undocumented host internals"
    )

    assert "skip" in section_lower and "mark-running" in section_lower, (
        "missing fallback: skip mark-running when the session dir can't be determined"
    )
    assert "suspect" in section_lower, (
        "fallback must note the entry then only resolves via the SUSPECT staleness path, "
        "never via definitive wf-record evidence"
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


def test_reconcile_auto_fail_mutation_documented_and_never_mutates_scoped():
    """reconcile is NOT purely informational: on definitive failed/killed
    wf-record evidence it auto-transitions a RUNNING entry to AUTO-FAILED
    (batch_queue.py:659-692) — a real, breaker-visible mutation that can
    trip HALT. The doc's 'never mutates' phrasing must be scoped to the two
    SUSPECT flags only, so it can't be misread as covering this case."""
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    section = _batch_mode_section(_body(text))

    never_mutates_idx = section.lower().find("never mutates")
    assert never_mutates_idx != -1, "missing the 'never mutates' informational-flags sentence"
    nearby = section[never_mutates_idx:never_mutates_idx + 120].lower()
    assert "these two flags" in nearby or "either of these two" in nearby, (
        "'never mutates' must be explicitly scoped to the two SUSPECT flags, "
        "not phrased as an unqualified claim about reconcile"
    )

    auto_failed_idx = section.find("AUTO-FAILED")
    assert auto_failed_idx != -1, "missing the AUTO-FAILED transition sentence"
    assert auto_failed_idx > never_mutates_idx, (
        "AUTO-FAILED sentence must follow (and thus not be covered by) the "
        "scoped 'never mutates' sentence"
    )

    auto_failed_context = section[auto_failed_idx - 200:auto_failed_idx + 300].lower()
    assert "definitive" in auto_failed_context and (
        "failed" in auto_failed_context and "killed" in auto_failed_context
    ), "AUTO-FAILED sentence must name definitive failed/killed wf-record evidence"
    assert "mutat" in auto_failed_context or "halt" in auto_failed_context, (
        "AUTO-FAILED sentence must flag it as a real, breaker-visible mutation"
    )
