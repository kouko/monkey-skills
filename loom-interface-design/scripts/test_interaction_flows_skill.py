"""Structural grep-test guarding the interaction-flows SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing, modality-aware interaction-flow instructions plus
the hard constraints the task and the host enforce:

  - YAML frontmatter declaring `name: interaction-flows` and a non-empty,
    key-free `description` within the Codex 1024-char HARD limit, carrying
    en + zh-TW + ja trigger phrasings for mapping a product's screens /
    commands, navigation, and UX flows.
  - the modality-aware body procedure: read the two reference docs (ux-flow
    checklist + ascii patterns) → read the governing PRINCIPLES.md → detect
    modality → generate ui-flows.md over the 7 dimensions → emit into the
    consumer project → validate.
  - references to BOTH reference docs (`references/ux-flow-checklist.md`,
    `references/ascii-ui-patterns.md`) AND the validator
    (`scripts/validate_design_output.py`) by relative path.
  - PRINCIPLES.md framed as the GOVERNING constraint (surface if absent).
  - the render-variant FLAG-only rule, with the full state machine deferred to
    `loom-spec:spec-expansion` (the seam is named).
  - flat-skill: every subfolder under the skill dir is single-level.

Checks assert on load-bearing PHRASES (intent), tolerant of wording variation.
Stdlib only (pathlib + re). Mirrors test_design_system_skill.py.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "interaction-flows"
    / "SKILL.md"
)

# Codex hard limit on a skill description.
_CODEX_DESC_LIMIT = 1024


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter() -> str:
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    return m.group(1)


# --- YAML frontmatter -------------------------------------------------------

def test_frontmatter_name_is_interaction_flows():
    front = _frontmatter()
    assert re.search(r"^name:\s*interaction-flows\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: interaction-flows'"


def test_description_present_and_within_codex_limit():
    front = _frontmatter()
    m = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert m and m.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"
    desc = m.group(1).strip()
    assert len(desc) <= _CODEX_DESC_LIMIT, (
        f"description is {len(desc)} chars; Codex HARD limit is "
        f"{_CODEX_DESC_LIMIT} — trim it"
    )


def test_description_carries_trilingual_triggers():
    """The skill must fire on screen/nav/UX-flow intent in en + zh-TW + ja."""
    front = _frontmatter().lower()
    # en
    assert "flow" in front, \
        "description must carry an English trigger (flow / user flow / UX flow)"
    # zh-TW (Traditional) — contains Han characters
    assert re.search(r"[一-鿿]", _frontmatter()), \
        "description must carry a zh-TW trigger (Traditional Chinese)"
    # ja — contains kana
    assert re.search(r"[぀-ヿ]", _frontmatter()), \
        "description must carry a ja trigger (kana)"


# --- modality-aware body procedure ------------------------------------------

def test_body_references_both_reference_docs_by_relative_path():
    text = _text()
    assert "references/ux-flow-checklist.md" in text, \
        "body must reference the ux-flow checklist by relative path"
    assert "references/ascii-ui-patterns.md" in text, \
        "body must reference the ascii patterns by relative path"


def test_body_references_validator_by_relative_path():
    text = _text()
    assert "scripts/validate_design_output.py" in text, \
        "body must reference the validator by relative path"


def test_body_reads_principles_as_governing_constraint():
    text = _text()
    assert "PRINCIPLES.md" in text, \
        "body must read the product's PRINCIPLES.md"
    low = text.lower()
    assert "govern" in low or "constrain" in low, \
        "body must frame PRINCIPLES.md as the governing constraint"
    assert "absent" in low or "missing" in low or "surface" in low, \
        "body must surface when PRINCIPLES.md is absent"


def test_body_detects_modality():
    low = _text().lower()
    assert "modality" in low, "body must detect/ask the modality"
    assert "gui" in low, "body must handle the GUI modality"
    assert "tui" in low and "cli" in low, \
        "body must handle the TUI / CLI modality"


def test_body_emits_ui_flows_to_consumer_project():
    text = _text()
    assert "ui-flows.md" in text, "body must emit ui-flows.md"
    assert "docs/interface-design-toolkit/" in text, \
        "body must emit into docs/interface-design-toolkit/"


def test_body_names_spec_expansion_seam():
    """ui-flows.md is the rich seed to loom-spec:spec-expansion."""
    text = _text()
    assert "spec-expansion" in text or "loom-spec:spec-expansion" in text, \
        "body must name the spec-expansion seam (ui-flows.md seeds it)"


def test_body_states_render_variant_flag_only_rule():
    """Render variants are FLAG-only; the full state machine is spec-expansion's."""
    low = _text().lower()
    assert "flag" in low, "body must state the render-variant flag rule"
    assert "state machine" in low or "fan-out" in low or "fan out" in low, \
        "body must defer the full state machine / fan-out to spec-expansion"


def test_body_invokes_mermaid_visualizer():
    text = _text()
    assert "obsidian-mermaid-visualizer" in text or "mermaid-visualizer" in text, \
        "body must invoke obsidian:obsidian-mermaid-visualizer for the flow diagrams"


def test_body_mandates_validation_step():
    low = _text().lower()
    assert "validat" in low, \
        "body must instruct running the validator before declaring done"


# --- flat-skill structure (repo hook enforces) ------------------------------

def test_skill_folder_is_flat():
    skill_dir = SKILL.parent
    for sub in skill_dir.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), (
                    f"flat-skill violation: nested subdir {child} under {sub} "
                    f"(subfolders must be single-level)"
                )
