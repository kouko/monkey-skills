"""Compaction contract for design-system's executable entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[2] / "skills" / "design-system" / "SKILL.md"
TEXT = SKILL.read_text(encoding="utf-8")
LOW = TEXT.lower()
FLAT = " ".join(LOW.split())


def test_entrypoint_preserves_modality_gui_contract_and_ending_gate_within_word_range():
    assert "references/design-md-schema.md" in TEXT
    assert "docs/loom/principles.md" in LOW and "## anchors" in LOW
    assert "3-5 tone & manner adjectives" in LOW and "governing mood" in LOW
    assert "proceed only on their say-so" in FLAT
    assert all(modality in LOW for modality in ("gui", "tui", "cli"))
    assert "references/knowledge-triage.md" in TEXT and "first" in LOW
    gui = LOW.split("### step 4a", 1)[1].split("### step 4b", 1)[0]
    gui_flat = " ".join(gui.split())
    sections = (
        "overview / brand", "colors", "typography", "layout",
        "elevation & depth", "shapes", "components", "do's & don'ts",
    )
    section_jobs = gui.split("the eight sections have distinct jobs:", 1)[1]
    positions = [section_jobs.index(f"**{section}**") for section in sections]
    assert positions == sorted(positions), "all eight GUI sections must remain ordered"
    assert "yaml blocks exist only for **colors**, **typography**, **spacing**, **rounded**, and **components**" in gui_flat
    assert "the other three stay prose-only" in gui_flat
    assert "propose 3-5 surface-treatment candidates" in FLAT
    assert "1-2 considered-but-rejected candidates" in FLAT
    assert "the user decides" in LOW
    assert "bespoke — no canon treatment fits" in gui and "escape hatch" in gui
    assert "when there is no `## anchors` tone & manner row" in LOW
    assert "derive mood" in LOW and "say so explicitly" in LOW
    assert "wcag-aa" in LOW and "npx @google/design.md" in TEXT
    assert "lightweight conventions stub" in LOW and "phase-2" in LOW
    assert "docs/loom/" in TEXT and "scripts/interface/validate_design_output.py" in TEXT
    assert "ending gate" in LOW and "exists on disk" in LOW and "failed run" in LOW
    assert "visual system only" in LOW and "not flows" in LOW
    words = len(TEXT.split())
    assert 1_388 <= words <= 1_585, f"expected 1388..1585 words, got {words}"
