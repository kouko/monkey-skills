from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "proposal-critique"
    / "SKILL.md"
)


def _window(text: str, start_marker: str, end_marker: str) -> str:
    """Text from `start_marker` up to (not including) `end_marker`.

    Keeps a mechanism/keyword pin scoped to the section that actually
    governs it, instead of matching anywhere in the whole SKILL.md --
    a whole-file match is a false green if the rule moves or is
    deleted from its governing section but the bare words survive
    elsewhere.
    """
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def test_entrypoint_preserves_axes_matrix_fallthrough_and_output():
    text = SKILL.read_text(encoding="utf-8")

    steps = [
        "1. **ENUMERATE-OR-DECOMPOSE.",
        "2. **GROUND.",
        "3. **ESSENTIAL?",
        "4. **TRIAGE.",
        "5. **PRESENT.",
    ]
    positions = [text.index(step) for step in steps]
    assert positions == sorted(positions)

    for grounding in ("GROUNDED", "HEURISTIC-OK", "SPECULATIVE"):
        assert grounding in text
    for necessity in ("ESSENTIAL", "SPECULATIVE"):
        assert necessity in text

    assert "The Triage Matrix" in text
    assert "KEEP-WITH-CAVEAT" in text
    assert "articulable re-trigger condition" in text

    fallthrough_section = _window(text, "### DEFER fall-through", "## Judgment Rules")
    assert "fall through DEFER to DROP" in fallthrough_section, (
        "the DEFER-fallthrough rule must live inside its own governing "
        "'### DEFER fall-through' section"
    )

    present_step = _window(text, "5. **PRESENT.", "## The Triage Matrix")
    assert "three buckets" in present_step
    assert "one-line reason per item" in present_step, (
        "the one-line-reason-per-item output requirement must live "
        "inside step 5 (PRESENT), not merely somewhere in the file"
    )

    assert "Single specific change" in text
    assert "complexity-critique" in text
    assert "Simple Q&A" in text
    assert "Pre-completion verification" in text
