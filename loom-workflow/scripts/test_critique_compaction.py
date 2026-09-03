"""Compaction pins for the merged critique skill.

`proposal-critique` and `complexity-critique` became one skill with two
modes at loom 1.0. Their two compaction suites merge here: the shared
discipline is pinned once, and each mode keeps the mechanism pins that
guarded it before the merge, scoped to its own half of the file so a rule
that moves out of its governing section fails instead of matching bare
words elsewhere.
"""
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1] / "skills" / "critique" / "SKILL.md"


def _flat(text: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches its pin."""
    return " ".join(text.split())


def _window(text: str, start_marker: str, end_marker: str) -> str:
    """Flattened text from `start_marker` up to (not including) `end_marker`."""
    flat = _flat(text)
    start = flat.index(start_marker)
    end = flat.index(end_marker, start)
    return flat[start:end]


def _proposal(text: str) -> str:
    return _window(text, "## Mode: proposal", "## Mode: complexity")


def _complexity(text: str) -> str:
    flat = _flat(text)
    return flat[flat.index("## Mode: complexity"):]


def test_mode_routing_is_declared_before_either_lens():
    text = SKILL.read_text(encoding="utf-8")

    assert "mode: proposal" in text
    assert "mode: complexity" in text
    routing = _window(text, "## Choosing the mode", "## Shared discipline")
    assert "P0/P1/P2 backlog" in routing
    assert "One specific proposed change" in routing
    assert "Three or more distinct proposals" in routing
    assert text.index("## Choosing the mode") < text.index("## Mode: proposal")


def test_shared_discipline_is_stated_once():
    text = SKILL.read_text(encoding="utf-8")
    shared = _window(text, "## Shared discipline", "## Mode: proposal")

    assert "Assertion is not evidence" in shared
    assert "Uncertainty is stated, never invented" in shared
    assert "No silent softening" in shared
    assert "The gate is yours to run" in shared


def test_proposal_mode_preserves_axes_matrix_fallthrough_and_output():
    text = SKILL.read_text(encoding="utf-8")
    mode = _proposal(text)

    steps = [
        "1. **ENUMERATE-OR-DECOMPOSE.",
        "2. **GROUND.",
        "3. **ESSENTIAL?",
        "4. **TRIAGE.",
        "5. **PRESENT.",
    ]
    positions = [mode.index(step) for step in steps]
    assert positions == sorted(positions)

    for grounding in ("GROUNDED", "HEURISTIC-OK", "SPECULATIVE"):
        assert grounding in mode
    for necessity in ("ESSENTIAL", "SPECULATIVE"):
        assert necessity in mode

    assert "The triage matrix" in mode
    assert "KEEP-WITH-CAVEAT" in mode
    assert "articulable re-trigger condition" in mode
    assert "fall through DEFER to DROP" in mode

    present_step = _window(mode, "5. **PRESENT.", "### The triage matrix")
    assert "three buckets" in present_step
    assert "one-line reason per item" in present_step, (
        "the one-line-reason-per-item output requirement must live "
        "inside step 5 (PRESENT), not merely somewhere in the file"
    )


def test_complexity_mode_preserves_mindset_three_questions_and_verdicts():
    text = SKILL.read_text(encoding="utf-8")
    mode = _complexity(text)

    assert "Load at least one" in mode
    assert "references/" in mode

    questions = [
        "Q1. What is the smallest end state that solves this?",
        "Q2. Does the change result in less total code?",
        "Q3. What can we delete?",
    ]
    positions = [mode.index(question) for question in questions]
    assert positions == sorted(positions)

    assert "mindset-extension-standard.md" in mode
    assert "domain-teams:code-team/standards/mindset-*.md" in mode
    assert "never a silent PROCEED" in mode
    assert "Pure greenfield handling" in mode
    assert '"0 lines = decline to build"' in mode
    for verdict in ("PROCEED", "PROCEED-WITH-CAVEAT", "RESHAPE", "REJECT"):
        assert verdict in mode
    assert "name the trade-off" in mode.lower()


def test_routing_boundaries_survive_the_merge():
    text = SKILL.read_text(encoding="utf-8")

    assert "simple q&a" in _flat(text).lower()
    assert "verification workflow" in _flat(text)
    assert "code-simplification workflow" in _flat(text)
    # The merge deleted the two skills that used to route to each other.
    for gone in ("proposal-critique", "complexity-critique", "brief-before-asking"):
        assert gone not in text, f"critique still names the deleted {gone}"
