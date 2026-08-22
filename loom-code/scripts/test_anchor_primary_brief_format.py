"""Structural grep-test guarding `handoff-brief-format.md`'s
`## Current State Evidence` section being anchor-primary (not
line-number-first).

The reference is prose, not executable code. Its correctness is the
PRESENCE of anchor-primary wording within the `### `## Current State
Evidence`` subsection of `## Required sections`, and an anchor-primary
anti-pattern bullet inside `## Anti-patterns`. A line number is optional
precision; the anchor (a verbatim string or a stable heading) is the
required citation.

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


def _subsection(text: str, heading_pattern: str) -> str:
    """Return the body of the first `###`-level subsection whose heading
    matches heading_pattern, up to the next `###`- or `##`-level heading."""
    match = re.search(
        rf"^###\s+{heading_pattern}\s*$", text, re.MULTILINE
    )
    assert match is not None, f"subsection matching {heading_pattern!r} not found"
    rest = text[match.end():]
    next_heading = re.search(r"^(?:##|###)\s+\S", rest, re.MULTILINE)
    return rest[: next_heading.start()] if next_heading else rest


def _flatten(text: str) -> str:
    """Collapse whitespace runs to single spaces for whitespace-insensitive
    substring matching."""
    return re.sub(r"\s+", " ", text)


def test_current_state_evidence_is_anchor_primary():
    text = _text()

    required_sections = _section(text, r"Required sections")
    cse = _subsection(required_sections, r"`## Current State Evidence`")
    flat = _flatten(cse)

    # The section frames the citation as anchor-primary: an anchor is the
    # required form, a line number is optional precision.
    assert "anchor" in flat.lower(), (
        "§Current State Evidence must name an anchor as the required citation"
    )
    assert "line number" in flat.lower() and "optional" in flat.lower(), (
        "§Current State Evidence must state that a line number is optional "
        "precision, not the required form"
    )

    # The five sub-bullets describe their citation as an anchor (not as
    # `file:line`).
    assert "file:line" not in cse, (
        "§Current State Evidence sub-bullets must not keep the line-number-first "
        "`file:line` phrasing as the citation requirement"
    )


def test_anti_pattern_bullet_is_anchor_primary():
    text = _text()
    anti = _section(text, r"Anti-patterns")
    flat = _flatten(anti)

    # The anti-pattern bullet that was previously "bullets without `file:line`
    # citations defeat the purpose" must invert to anchor-primary.
    assert "anchor" in flat.lower(), (
        "§Anti-patterns must carry an anchor-primary anti-pattern bullet"
    )
    # The old line-number-first anti-pattern wording must be gone.
    assert "without `file:line` citations" not in flat, (
        "§Anti-patterns must drop the line-number-first 'without `file:line` "
        "citations' wording"
    )