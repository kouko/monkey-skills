"""Guards the post-draft overlay-mode output-envelope example in
copywriting-neta-injection/SKILL.md against passthrough-field drift.

The canonical envelope shape (copywriting-toolkit/CLAUDE.md §Handoff
Envelope) carries `express_mode_used`, `audit_trail`, and `retries` as
immutable passthrough fields every mid-pipeline stage must preserve. The
overlay-mode (post-draft) output envelope example omitted all three while
the sibling pre-draft bake-in example in the same file (aligned in commit
e15aa12f) already carries them — this is the drift this test pins.

Window-scoped to the "### Post-draft overlay mode" example block only
(bounded by the next "## " heading) so this test cannot pass by matching
the bake-in example's fields instead.

No REQ-ids are registered for this dispatch; @req tags are intentionally
omitted per the implementer contract.

Stdlib + pytest only, path-based.
"""

import re
from pathlib import Path

import pytest

SKILL_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "copywriting-neta-injection"
    / "SKILL.md"
)

ANCHOR = "### Post-draft overlay mode"


def _text() -> str:
    assert SKILL_PATH.is_file(), f"SKILL.md is absent at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def _overlay_section_window(text: str) -> str:
    """Return the overlay-mode section, from ANCHOR to the next '## ' heading.

    Asserts ANCHOR is unique first — a non-unique anchor would make the
    window ambiguous (ties to the earlier docstring's stated precondition).
    """
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1, (
        f"anchor {ANCHOR!r} must be unique in SKILL.md, found "
        f"{len(occurrences)} occurrences"
    )
    start = occurrences[0]
    next_h2 = re.search(r"\n## ", text[start:])
    end = start + next_h2.start() if next_h2 else len(text)
    return text[start:end]


def _output_envelope_json_block(section: str) -> str:
    """Return the json fenced block following '**Output envelope**:' in section."""
    marker = "**Output envelope**:"
    marker_idx = section.index(marker)
    fence_start = section.index("```json", marker_idx)
    fence_end = section.index("```", fence_start + len("```json"))
    return section[fence_start:fence_end]


def test_overlay_anchor_is_unique():
    text = _text()
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1


def test_overlay_output_envelope_carries_express_mode_used():
    block = _output_envelope_json_block(_overlay_section_window(_text()))
    assert '"express_mode_used"' in block


def test_overlay_output_envelope_carries_retries():
    block = _output_envelope_json_block(_overlay_section_window(_text()))
    assert '"retries"' in block
    assert "bounce_round" in block
    assert "revise_round_count" in block
    assert "total_retries" in block


def test_overlay_output_envelope_carries_audit_trail():
    block = _output_envelope_json_block(_overlay_section_window(_text()))
    assert '"audit_trail"' in block


def test_bakein_output_envelope_still_carries_the_fields_unchanged():
    """Sibling regression guard: the pre-draft bake-in example (already
    aligned in commit e15aa12f) must not be touched by this fix."""
    text = _text()
    bakein_anchor = "### Pre-draft bake-in mode"
    start = text.index(bakein_anchor)
    end = text.index(ANCHOR)
    section = text[start:end]
    block = _output_envelope_json_block(section)
    assert '"express_mode_used"' in block
    assert '"audit_trail"' in block
    assert '"retries"' in block


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
