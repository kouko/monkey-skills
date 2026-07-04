"""Structural test: using-loom-pipeline SKILL.md carries the fire-condition
gate, the N/A-loud clause, the 6-field run-input contract, and the
Workflow({scriptPath...}) invocation resolved from the skill's base path.

"""
import re
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


def test_skill_batch_mode_section_contract():
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    body = _body(text)
    body_lower = body.lower()

    batch_idx = body_lower.find("## §batch mode")
    assert batch_idx != -1, "missing §Batch mode heading"
    batch_section = body[batch_idx:]
    batch_section_lower = batch_section.lower()

    # Three dispatcher-only prohibitions, verbatim (plan Task 11 / brief
    # Smallest End State §3), scoped to the §Batch mode section itself so
    # this can't pass on an unrelated mention elsewhere in the file.
    assert "never parses the queue file" in batch_section_lower, \
        "missing 'never parses the queue file' prohibition"
    assert "never composes git commands" in batch_section_lower, \
        "missing 'never composes git commands' prohibition"
    assert "never diagnoses failures mid-batch" in batch_section_lower, \
        "missing 'never diagnoses failures mid-batch' prohibition"

    # next -> Workflow -> mark loop, in that order, within §Batch mode
    # (the §Invocation section earlier in the file has its own unrelated
    # Workflow({ call, so this must not scan the whole document).
    next_idx = batch_section.find("batch_queue.py next")
    workflow_idx = batch_section.find("Workflow(")
    mark_idx = batch_section.find("batch_queue.py mark")
    assert -1 not in (next_idx, workflow_idx, mark_idx), \
        "missing one of next / Workflow / mark in the §Batch mode loop description"
    assert next_idx < workflow_idx < mark_idx, \
        "next -> Workflow -> mark loop is not documented in that order"

    # Both queue files named.
    assert "QUEUE.toml" in batch_section, "missing QUEUE.toml"
    assert "queue-state.json" in batch_section, "missing queue-state.json"


def test_skill_intake_section_contract():
    """§Intake is the first '## ' section in the body, carries the three
    steps (前站檢查 / 對站檢查 / re-affirm this skill's own fire condition),
    references the reception's on-ramp table by path (never copies its
    rows), and leaves the existing N/A-loud wording byte-present and
    unsoftened (plan Task A2 / brief §Open Q2).
    """
    assert SKILL_MD.exists(), f"missing {SKILL_MD}"
    text = SKILL_MD.read_text()
    body = _body(text)

    headings = re.findall(r"^## (.+)$", body, re.MULTILINE)
    assert headings, "no '## ' headings found in body"
    assert headings[0].strip().lower() == "§intake", (
        f"§Intake must be the FIRST '## ' section in the body "
        f"(after frontmatter/SUBAGENT-STOP); found {headings[0]!r} first"
    )

    intake_idx = body.find("## " + headings[0])
    next_idx = body.find("\n## ", intake_idx + 1)
    intake_section = body[intake_idx:next_idx] if next_idx != -1 else body[intake_idx:]

    # Step 1 — 前站檢查: point to the reception's on-ramp table by
    # path/name, never copy the table body (Reception SSOT rule).
    assert "前站檢查" in intake_section, "missing step 1 前站檢查 label"
    assert "family-reception.md" in intake_section, \
        "step 1 must point to the reception file by path"
    assert "on-ramp" in intake_section.lower(), \
        "step 1 must name the on-ramp criteria table"
    assert "| Condition |" not in intake_section, \
        "§Intake must not copy the on-ramp criteria table body"

    # Step 2 — 對站檢查: interactive design/spec/code work hands off to
    # that family's own using-loom-* entry.
    assert "對站檢查" in intake_section, "missing step 2 對站檢查 label"
    for entry in (
        "using-loom-product-principles",
        "using-loom-interface-design",
        "using-loom-spec",
        "using-loom-code",
    ):
        assert entry in intake_section, f"step 2 missing hand-off to {entry}"

    # Step 3 — restates this skill's own fire condition; must not soften
    # or duplicate-with-drift the existing N/A-loud constitution.
    pinned_phrase = "never silently skip, and never fake the orchestration inline"
    assert pinned_phrase in body, \
        "existing N/A-loud phrase was altered or removed — no softening allowed"
