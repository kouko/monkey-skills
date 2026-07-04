"""Structural grep-test guarding using-loom-interface-design's §Intake section.

using-loom-interface-design/SKILL.md is a prompt artifact, not executable
code. This test asserts the PRESENCE of the load-bearing §Intake contract
(loom family connective-tissue plan, Task D1):

  - a `## §Intake` heading, positioned as the FIRST section after the
    frontmatter / <SUBAGENT-STOP> block (before the existing
    <EXTREMELY-IMPORTANT> modality block).
  - step 1 (前站檢查): references the loom family reception's on-ramp
    criteria (does NOT copy the table body — SSOT rule) and recommends
    `using-loom-product-principles` when the target repo lacks
    `docs/loom/PRINCIPLES.md`.
  - step 2 (對站檢查): redirects spec-shaped fan-out asks to `using-loom-spec`
    and coding asks to `using-loom-code`.
  - step 3: the EXISTING design-system / interaction-flows routing is kept,
    not duplicated — §Intake step 3 just hands off to the router's own
    Skill-priority table already in the file.

Checks assert on load-bearing PHRASES (intent), tolerant of wording
variation. Stdlib only (pathlib + re). Resolve SKILL.md relative to this
test file, matching the house convention in this scripts/ directory.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "using-loom-interface-design"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _body() -> str:
    """Text after the closing frontmatter fence.

    Split on the SECOND '---' occurrence so the frontmatter's own
    'description:' field (which may legitimately mention routing/design
    words) cannot satisfy body-scoped assertions.
    """
    text = _text()
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md lost its frontmatter fences"
    return parts[2]


def test_intake_heading_present():
    body = _body()
    assert "## §Intake" in body, "missing '## §Intake' heading in the body"


def test_intake_is_first_section_after_subagent_stop():
    body = _body()
    intake_idx = body.find("## §Intake")
    assert intake_idx != -1, "missing '## §Intake' heading"

    subagent_stop_idx = body.find("</SUBAGENT-STOP>")
    assert subagent_stop_idx != -1, "missing </SUBAGENT-STOP> close tag"
    assert intake_idx > subagent_stop_idx, \
        "§Intake must come after the <SUBAGENT-STOP> block"

    extremely_important_idx = body.find("<EXTREMELY-IMPORTANT>")
    assert extremely_important_idx != -1, "missing <EXTREMELY-IMPORTANT> block"
    assert intake_idx < extremely_important_idx, \
        "§Intake must be the FIRST section — before <EXTREMELY-IMPORTANT>"


def test_intake_step1_references_reception_and_principles_gap():
    body = _body()
    intake_idx = body.find("## §Intake")
    assert intake_idx != -1
    # Scope to the §Intake section only (up to the next '## ' heading).
    rest = body[intake_idx + len("## §Intake"):]
    next_heading = rest.find("\n## ")
    section = rest if next_heading == -1 else rest[:next_heading]
    section_lower = section.lower()

    assert "family reception" in section_lower or "on-ramp" in section_lower, \
        "step 1 must reference the loom family reception's on-ramp criteria"
    assert "principles.md" in section_lower, \
        "step 1 must check for docs/loom/PRINCIPLES.md"
    assert "using-loom-product-principles" in section, \
        "step 1 must recommend using-loom-product-principles when PRINCIPLES.md is absent"

    # SSOT rule: reference, don't copy the criteria table rows.
    assert "| # | condition | recommendation |" not in section_lower, \
        "step 1 must REFERENCE the reception criteria table, not copy its rows"


def test_intake_step2_redirects_spec_and_code_asks():
    body = _body()
    intake_idx = body.find("## §Intake")
    assert intake_idx != -1, "missing '## §Intake' heading"
    rest = body[intake_idx + len("## §Intake"):]
    next_heading = rest.find("\n## ")
    section = rest if next_heading == -1 else rest[:next_heading]

    assert "using-loom-spec" in section, \
        "step 2 must redirect spec fan-out asks to using-loom-spec"
    assert "using-loom-code" in section, \
        "step 2 must redirect coding asks to using-loom-code"


def test_intake_step3_hands_off_to_existing_routing_without_duplicating():
    body = _body()
    intake_idx = body.find("## §Intake")
    assert intake_idx != -1, "missing '## §Intake' heading"
    rest = body[intake_idx + len("## §Intake"):]
    next_heading = rest.find("\n## ")
    section = rest if next_heading == -1 else rest[:next_heading]
    section_lower = section.lower()

    assert "design-system" in section_lower and "interaction-flows" in section_lower, \
        "step 3 must hand off to the existing design-system/interaction-flows routing"

    # The existing "Skill priority" routing table must still exist exactly
    # once in the file (not duplicated inside §Intake).
    assert body.count("## Skill priority") == 1, \
        "the existing Skill-priority routing table must not be duplicated"
