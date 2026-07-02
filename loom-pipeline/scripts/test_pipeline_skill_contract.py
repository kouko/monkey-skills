"""Structural test: using-loom-pipeline SKILL.md carries the fire-condition
gate, the N/A-loud clause, the 6-field run-input contract, and the
Workflow({scriptPath...}) invocation resolved from the skill's base path.

# @req: REQ-LOOM-PIPELINE-SKILL-CONTRACT-1
"""
from pathlib import Path

PLUGIN_ROOT = Path(__file__).parents[1]
SKILL_MD = PLUGIN_ROOT / "skills" / "using-loom-pipeline" / "SKILL.md"


def _body(text: str) -> str:
    """Text AFTER the closing frontmatter fence.

    The description frontmatter legitimately mentions Workflow / the station
    plugins / N/A, so whole-file matching would let the body's §When-it-fires
    section be deleted while the test stays green (house precedent:
    loom-code/scripts/test_ui_verification_skill.py's _frontmatter split).
    """
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md lost its frontmatter fences"
    return parts[2]


def test_fire_inputs_and_invocation():
    # @req: REQ-LOOM-PIPELINE-SKILL-CONTRACT-1
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    lower = text.lower()
    body = _body(text)
    body_lower = body.lower()

    # Both fire conditions — asserted against the BODY so deleting
    # §When it fires cannot pass on frontmatter mentions alone.
    assert "workflow" in body_lower and "available" in body_lower, \
        "missing Workflow-tool-availability fire condition in the body"
    assert (
        "loom-product-principles" in body
        and "loom-interface-design" in body
        and "loom-spec" in body
        and "loom-code" in body
    ), "missing the four station-plugin names in the body"

    # N/A-loud clause (body-scoped).
    assert "loom-pipeline: n/a" in body_lower, \
        "missing the N/A-loud emission clause in the body"

    # 5 run-input fields.
    assert "change-id" in lower, "missing change-id run input"
    assert "project path" in lower, "missing target project path run input"
    assert "budget" in lower, "missing token-budget run input"
    assert "model" in lower, "missing model-policy run input"
    assert "resumerunid" in lower, "missing resumeRunId run input"
    assert "skillsroot" in lower, "missing skillsRoot run input"

    # Invocation mechanism.
    assert "Workflow({scriptPath" in text, \
        "missing the literal Workflow({scriptPath invocation snippet"
    assert "base path" in lower or "base directory" in lower, \
        "missing base-path-resolution mention"
