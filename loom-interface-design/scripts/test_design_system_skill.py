"""Structural grep-test guarding the design-system SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing, modality-aware design-system instructions plus
the hard constraints the task and the host enforce:

  - YAML frontmatter declaring `name: design-system` and a non-empty,
    key-free `description` that fits the Codex 1024-char HARD limit and carries
    en + zh-TW + ja trigger phrasings for designing a product's visual/design
    system (colors / typography / components / tokens).
  - the modality-aware body procedure: read the schema contract → read the
    governing PRINCIPLES.md → detect/ask the modality → GUI emits the
    8-section DESIGN.md / TUI-CLI emits a lightweight stub + phase-2 note →
    emit into the consumer project → validate.
  - references to BOTH the schema contract (`references/design-md-schema.md`)
    and the validator (`scripts/validate_design_output.py`) by relative path.
  - PRINCIPLES.md framed as the GOVERNING constraint (surface if absent).
  - DESIGN.md = visual system only (NOT flows) + tokens side-channel to
    frontend.
  - flat-skill: every subfolder under the skill dir is single-level (no nested
    subdirs) — the repo hook blocks otherwise.

Checks assert on load-bearing PHRASES (intent), tolerant of wording variation.
Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "design-system"
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

def test_frontmatter_name_is_design_system():
    front = _frontmatter()
    assert re.search(r"^name:\s*design-system\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: design-system'"


def test_description_present_and_within_codex_limit():
    """description must exist, be non-empty, and fit the Codex 1024-char HARD
    limit (the whole value, not just the first line)."""
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
    """The skill must fire on visual/design-system intent in en + zh-TW + ja."""
    front = _frontmatter().lower()
    # en
    assert "design system" in front or "design-system" in front, \
        "description must carry an English trigger (design system)"
    # zh-TW (Traditional)
    assert ("設計系統" in front or "視覺系統" in front
            or "設計規範" in front), \
        "description must carry a zh-TW trigger (設計系統 / 視覺系統 / 設計規範)"
    # ja
    assert ("デザインシステム" in front or "ビジュアル" in front
            or "デザイン" in front), \
        "description must carry a ja trigger (デザインシステム / ビジュアル)"


def test_description_states_design_concerns():
    """description must signal it covers a product's visual/design system —
    colors / typography / components / tokens."""
    low = _frontmatter().lower()
    assert "color" in low, "description must mention colors"
    assert "typograph" in low, "description must mention typography"
    assert "token" in low, "description must mention tokens"


# --- modality-aware body procedure ------------------------------------------

def test_body_references_schema_by_relative_path():
    text = _text()
    assert "references/design-md-schema.md" in text, \
        "body must reference the schema contract by relative path"


def test_body_references_validator_by_relative_path():
    text = _text()
    assert "scripts/validate_design_output.py" in text, \
        "body must reference the validator by relative path"


def test_body_reads_principles_as_governing_constraint():
    """PRINCIPLES.md is the GOVERNING constraint (surface if absent)."""
    text = _text()
    assert "PRINCIPLES.md" in text, \
        "body must read the product's PRINCIPLES.md"
    assert "docs/product-principles-toolkit/PRINCIPLES.md" in text, \
        "body must read PRINCIPLES.md from the consumer project path"
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


def test_body_gui_emits_eight_section_design_md():
    """GUI modality emits DESIGN.md with all 8 canonical sections."""
    text = _text()
    assert "DESIGN.md" in text, "body must emit DESIGN.md for the GUI modality"
    low = text.lower()
    assert "8" in text or "eight" in low, \
        "body must state DESIGN.md carries all 8 canonical sections"


def test_body_tui_cli_emits_stub_with_phase2_note():
    """TUI / CLI modality emits a lightweight stub + a phase-2 note."""
    low = _text().lower()
    assert "stub" in low, "body must emit a minimal stub for TUI / CLI"
    assert "phase-2" in low or "phase 2" in low or "phase2" in low, \
        "body must carry a phase-2 note for the unbuilt TUI/CLI design-system"


def test_body_emits_to_consumer_project_path():
    """The skill writes into the consumer project at the docs/<toolkit>/
    convention — DESIGN.md is product-level (one per product)."""
    text = _text()
    assert "docs/interface-design-toolkit/" in text, \
        "body must emit into docs/interface-design-toolkit/"
    low = text.lower()
    assert "product-level" in low or "one per product" in low, \
        "body must state DESIGN.md is product-level (one per product)"


def test_body_scopes_visual_system_not_flows():
    """DESIGN.md = visual system only (NOT flows — that's interaction-flows);
    tokens side-channel to frontend."""
    low = _text().lower()
    assert "visual system" in low, \
        "body must state DESIGN.md is the visual system only"
    assert "flow" in low, \
        "body must state DESIGN.md is NOT flows (interaction-flows owns that)"
    assert "side-channel" in low or "side channel" in low, \
        "body must state tokens side-channel to the frontend"


def test_body_mandates_validation_step():
    low = _text().lower()
    assert "validat" in low, \
        "body must instruct running the validator before declaring done"


# --- flat-skill structure (repo hook enforces) ------------------------------

def test_skill_folder_is_flat():
    """The skill dir may hold SKILL.md plus single-level subfolders; no
    subfolder may itself contain a subfolder (the repo hook blocks otherwise)."""
    skill_dir = SKILL.parent
    for sub in skill_dir.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), (
                    f"flat-skill violation: nested subdir {child} under {sub} "
                    f"(subfolders must be single-level)"
                )
