from pathlib import Path


SKILL = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "complexity-critique"
    / "SKILL.md"
)


def test_entrypoint_preserves_mindset_three_questions_and_verdicts_under_word_ceiling():
    text = SKILL.read_text(encoding="utf-8")

    assert 1_397 <= len(text.split()) <= 1_612
    assert "Load at least one" in text
    assert "references/" in text

    questions = [
        "Q1. What's the smallest end state that solves this?",
        "Q2. Does the proposed change result in less total code?",
        "Q3. What can we delete?",
    ]
    positions = [text.index(question) for question in questions]
    assert positions == sorted(positions)

    assert "Pure greenfield handling" in text
    assert '"0 lines = decline to build"' in text
    for verdict in ("PROCEED", "PROCEED-WITH-CAVEAT", "RESHAPE", "REJECT"):
        assert verdict in text
    assert "name the trade-off" in text.lower()
    assert "single change" in text.lower()
    assert "proposal-critique" in text
