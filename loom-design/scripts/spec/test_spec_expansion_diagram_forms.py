"""Structural grep-test guarding that the OOUX `## OOUX object model` visible
artifact instruction (spec-expansion SKILL.md Phase (2)) names the Mermaid
diagram forms for state machines and object relations, governed by the
fill-or-declare contract (Pin B, docs/loom/plans/2026-08-11-
visualization-trigger-layer.md §Pinned wording).

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[2] / "skills" / "spec-expansion" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_ooux_names_mermaid_diagram_forms():
    text = _text()

    assert "stateDiagram-v2" in text, \
        "OOUX visible artifact must name the Mermaid 'stateDiagram-v2' form " \
        "for per-object state machines"
    assert text.count("stateDiagram-v2") == 1, \
        "'stateDiagram-v2' should appear exactly once (load-bearing, not " \
        "incidental prose)"

    assert "erDiagram" in text, \
        "OOUX visible artifact must name the Mermaid 'erDiagram' form for " \
        "object-to-object relations"
    assert text.count("erDiagram") == 1, \
        "'erDiagram' should appear exactly once (load-bearing, not " \
        "incidental prose)"

    # Pin A — the sanctioned empty-slot line's full prefix (verbatim from the
    # plan's §Pinned wording).
    assert "N/A — no flow/state/architecture-shaped content:" in text, \
        "must carry Pin A's N/A line prefix (fill-or-declare empty-slot form)"

    # Section header literals must stay untouched (validator + existing
    # test_spec_expansion_skill.py pin these whole-line headers).
    assert "## USM backbone" in text
    assert "## OOUX object model" in text
    assert "## Path × edge matrix" in text
