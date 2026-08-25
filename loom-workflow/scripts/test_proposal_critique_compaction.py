from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "proposal-critique"
    / "SKILL.md"
)


def test_entrypoint_preserves_axes_matrix_fallthrough_and_output_under_word_ceiling():
    text = SKILL.read_text(encoding="utf-8")

    # Frozen baseline: 1,366 words. The brief requires a 25-35% reduction.
    assert 888 <= len(text.split()) <= 1_024

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
    assert "fall through DEFER to DROP" in text
    assert "three buckets" in text
    assert "one-line reason per item" in text

    assert "Single specific change" in text
    assert "complexity-critique" in text
    assert "Simple Q&A" in text
    assert "Pre-completion verification" in text
