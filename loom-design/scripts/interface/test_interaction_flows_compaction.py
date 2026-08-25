"""Compaction contract for interaction-flows' executable entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "interaction-flows" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.split())


def test_entrypoint_preserves_intake_dimensions_diagrams_and_ending_gate_within_word_range():
    for reference in (
        "references/ux-flow-checklist.md",
        "references/ascii-ui-patterns.md",
        "references/knowledge-triage.md",
    ):
        assert reference in TEXT

    assert "docs/loom/PRINCIPLES.md" in TEXT and "govern" in LOW
    assert "if `principles.md` is absent" in LOW
    assert "no principles — design is unconstrained" in LOW
    assert "explicit approval" in LOW
    assert "ask the user" in LOW and "do not guess" in LOW
    assert all(modality in LOW for modality in ("gui", "tui", "cli"))

    dimensions = (
        "screen / panel / command inventory",
        "user flows (mermaid)",
        "ui structure (ascii layout)",
        "transitions",
        "entry points",
        "exit points",
        "information density + mobile flow",
    )
    dimension_section = LOW.split("### 4. generate `ui-flows.md` covering the 7 dimensions", 1)[1]
    positions = [dimension_section.index(dimension) for dimension in dimensions]
    assert positions == sorted(positions), "all seven dimensions must remain ordered"

    assert "obsidian:obsidian-mermaid-visualizer" in TEXT
    assert "ascii skeleton" in LOW and "ascii-vs-mermaid split" in LOW
    assert "flag-only" in LOW and all(
        variant in LOW for variant in ("empty", "loading", "error", "success")
    )
    assert "classification question first" in FLAT

    assert "docs/loom/<change-id>/ui-flows.md" in TEXT
    assert "stable, addressable heading" in LOW
    assert "scripts/interface/validate_design_output.py" in TEXT
    assert "argv: [" in TEXT and "never through a shell" in LOW
    assert "ending gate" in LOW and "exists on disk" in LOW and "failed run" in LOW
    assert "surface" in LOW and "spec owns" in LOW and "flag here, fan-out there" in LOW

    words = len(TEXT.split())
    assert 1_012 <= words <= 1_156, f"expected 1012..1156 words, got {words}"
