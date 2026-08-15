"""Structural test: using-loom-pipeline SKILL.md carries the 3-segment
execution map, the 4 human gates between segments, and the driver
prohibitions (verbatim) + stable-prefix dispatch convention note.

"""
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[1]
SKILL_MD = PLUGIN_ROOT / "skills" / "using-loom-pipeline" / "SKILL.md"


def _body(text: str) -> str:
    """Text AFTER the closing frontmatter fence.

    Mirrors test_pipeline_skill_contract.py's _body() helper: the
    description frontmatter can legitimately mention station names /
    gates in passing, so whole-file matching would let a body section
    be deleted while the test stays green.
    """
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md lost its frontmatter fences"
    return parts[2]


def test_segments_gates_prohibitions():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    body = _body(text)
    body_lower = body.lower()

    # --- §Segments: 3 segments, one Workflow invocation each ---
    assert "principles" in body_lower and "design" in body_lower, \
        "missing Segment 1 (principles + design) in the body"
    assert "design-critic" in body_lower, \
        "missing Segment 1's design-critic panel mention in the body"
    assert "spec" in body_lower, "missing Segment 2 (spec) in the body"
    assert "completeness-critic" in body_lower, \
        "missing Segment 2's completeness-critic mention in the body"
    assert "validator" in body_lower, \
        "missing Segment 2's validator gate mention in the body"
    assert "sdd" in body_lower or "subagent-driven-development" in body_lower, \
        "missing Segment 3 (SDD) in the body"
    assert "whole-branch" in body_lower, \
        "missing Segment 3's whole-branch review mention in the body"
    assert "ui-verify" in body_lower or "ui-verification" in body_lower, \
        "missing Segment 3's ui-verify mention in the body"

    # --- §Human gates: exactly 4, each with when + what human decides ---
    assert "change-id" in body_lower, \
        "missing gate (a) change-id minting in the body"
    assert "brief-before-asking" in body_lower, \
        "missing gate (b) brief-before-asking reference in the body"
    assert "#475" in body, \
        "missing gate (b) #475 complex-fork escalation reference in the body"
    assert "budget" in body_lower and (
        "model tier" in body_lower or "cost" in body_lower
    ), "missing gate (c) cost policy / budget+model-tier confirmation in the body"
    assert "merge" in body_lower, \
        "missing gate (d) final merge in the body"
    assert "never merges" in body_lower, \
        "missing 'the pipeline NEVER merges' framing for gate (d) in the body"

    # --- §Driver prohibitions: verbatim ---
    assert "never edits station artifacts" in body_lower, \
        "missing verbatim prohibition: never edits station artifacts"
    assert "never produces verdicts" in body_lower, \
        "missing verbatim prohibition: never produces verdicts"
    # "never merges" alone also matches gate (d)'s sentence — assert the
    # prohibition BULLET's own phrasing so deleting the bullet turns RED.
    assert "the driver never merges" in body_lower, \
        "missing verbatim prohibition bullet: the driver never merges"
    assert "cross-plugin delegation contract" in body_lower, \
        "missing cross-plugin delegation contract sentence in the body"

    # --- stable-prefix dispatch convention ---
    assert "stable-prefix" in body_lower or "stable prefix" in body_lower, \
        "missing stable-prefix dispatch convention note in the body"
    assert "appended" in body_lower or "append" in body_lower, \
        "missing 'appended, never prepended' framing in the body"
