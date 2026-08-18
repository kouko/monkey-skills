"""Structural grep-test guarding `handoff-brief-format.md`'s new
`## Design-side on-ramp` three-state grammar (on-ramp explicit-choice gate,
Task 1 / BI-1).

The reference is prose, not executable code. Its correctness is the
PRESENCE of a `### `## Design-side on-ramp`` subsection inside
`## Required sections`, a matching block inside `## Template`, and the
canonical-grammar tokens appearing within that subsection (not merely
somewhere in the file).

Stdlib only (pathlib + re). Resolve the reference relative to this test
file.
"""

import re
from pathlib import Path

REFERENCE = (
    Path(__file__).parent
    / ".."
    / "skills"
    / "brainstorming"
    / "references"
    / "handoff-brief-format.md"
).resolve()

GRAMMAR_TOKENS = [
    "not fired —",
    "fired: rows",
    "user chose",
    "standing",
    "pending",
    "unresolved",
]


def _text() -> str:
    assert REFERENCE.is_file(), f"handoff-brief-format.md is absent at {REFERENCE}"
    return REFERENCE.read_text(encoding="utf-8")


def _section(text: str, heading_pattern: str) -> str:
    """Return the body of the first `##`-level section whose heading matches
    heading_pattern, up to (not including) the next `##`-level heading."""
    match = re.search(
        rf"^##\s+{heading_pattern}\s*$", text, re.MULTILINE
    )
    assert match is not None, f"heading matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^##\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def test_required_sections_and_template_carry_design_side_on_ramp_three_states():
    text = _text()

    required_sections = _section(text, r"Required sections")
    assert "### `## Design-side on-ramp`" in required_sections, (
        "Required sections must declare a "
        "'### `## Design-side on-ramp`' subsection"
    )

    onramp_subsection_match = re.search(
        r"^###\s+`## Design-side on-ramp`\s*$", required_sections, re.MULTILINE
    )
    assert onramp_subsection_match is not None
    rest = required_sections[onramp_subsection_match.end():]
    next_subsection = re.search(r"^###\s+\S", rest, re.MULTILINE)
    onramp_subsection_body = rest[: next_subsection.start()] if next_subsection else rest

    for token in GRAMMAR_TOKENS:
        assert token in onramp_subsection_body, (
            f"Required-sections '## Design-side on-ramp' subsection missing "
            f"token {token!r}"
        )

    # The Template section's body is a fenced code block (nested `##`
    # headings inside it are skeleton content, not real sections), so slice
    # the fence directly rather than via `_section`.
    template_heading = re.search(r"^##\s+Template\s*$", text, re.MULTILINE)
    assert template_heading is not None, "'## Template' heading not found"
    fence_start = text.index("```markdown", template_heading.end())
    fence_end = text.index("```", fence_start + len("```markdown"))
    template_fence = text[fence_start:fence_end]

    assert "## Design-side on-ramp" in template_fence, (
        "Template block must include a '## Design-side on-ramp' heading"
    )

    template_onramp_match = re.search(
        r"^##\s+Design-side on-ramp\s*$", template_fence, re.MULTILINE
    )
    assert template_onramp_match is not None
    template_rest = template_fence[template_onramp_match.end():]
    template_next = re.search(r"^##\s+\S", template_rest, re.MULTILINE)
    template_onramp_body = (
        template_rest[: template_next.start()] if template_next else template_rest
    )

    for token in GRAMMAR_TOKENS:
        assert token in template_onramp_body, (
            f"Template '## Design-side on-ramp' block missing token {token!r}"
        )
