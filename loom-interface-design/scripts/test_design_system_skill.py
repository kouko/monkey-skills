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

SCHEMA = (
    Path(__file__).parents[1]
    / "skills"
    / "design-system"
    / "references"
    / "design-md-schema.md"
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


def test_description_carries_positive_triggers():
    """The description must carry a positive, specific English trigger for
    visual/design-system intent. Per the house description standard, triggers
    are positive English keywords — no CJK / multilingual keyword redundancy
    (cross-lingual triggering is A/B-verified redundant)."""
    front = _frontmatter().lower()
    assert "design system" in front or "design-system" in front, \
        "description must carry an English trigger (design system)"
    assert not re.search(r"[一-鿿぀-ヿ]", _frontmatter()), \
        "description must carry NO CJK / kana keyword redundancy (house standard)"


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
    assert "docs/loom/PRINCIPLES.md" in text, \
        "body must read PRINCIPLES.md from the consumer project path"
    low = text.lower()
    assert "govern" in low or "constrain" in low, \
        "body must frame PRINCIPLES.md as the governing constraint"
    assert "absent" in low or "missing" in low or "surface" in low, \
        "body must surface when PRINCIPLES.md is absent"


def _step2_block() -> str:
    """The Step 2 section of the body — lowercased, whitespace-flattened.

    Scoped to the block that must carry the anchor-inheritance instruction —
    a whole-file membership pin would pass on a SKILL.md that mentions the
    anchor anywhere at all (see docs/loom/memory/
    grep-tests-scope-to-measured-neighborhood.md). Flattened so a pinned
    phrase still matches across the prose's line wraps.
    """
    text = _text()
    start = text.index("### Step 2")
    end = text.index("### Step 3", start)
    return re.sub(r"\s+", " ", text[start:end]).lower()


def test_step2_inherits_tone_and_manner_anchor():
    """Step 2 INHERITS the upstream tone & manner anchor as the governing mood
    (it does not re-derive it), and falls back LOUDLY when no anchor exists.

    Every phrase is pinned inside the Step 2 block, and the fallback is pinned
    as coming AFTER the inherit rule (a fallback that precedes the rule it
    falls back from is not a fallback) — a positional assertion, because the
    claim is relational (see docs/loom/memory/
    assertion-must-encode-the-property-it-claims.md).
    """
    block = _step2_block()

    # (a) the `## Anchors` section of PRINCIPLES.md is a named read target
    assert "## anchors" in block, \
        "Step 2 must name the `## Anchors` section of PRINCIPLES.md as a read target"

    # (b) the 3-5 tone & manner adjectives ARE the governing mood
    assert "3-5 tone & manner adjectives" in block, \
        "Step 2 must name the 3-5 tone & manner adjectives (upstream vocabulary)"
    assert "governing mood" in block, \
        "Step 2 must state the adjectives are the GOVERNING mood"

    # (c) inherited, NOT re-derived
    inherit_at = block.index("inherit")
    assert "re-derive" in block, \
        "Step 2 must state the mood is NOT re-derived"
    assert "do not re-derive" in block or "never re-derive" in block, \
        "Step 2 must forbid re-deriving the mood when an anchor exists"

    # (d) the loud fallback — absent anchor: derive as before AND say so
    fallback_at = block.index("no `## anchors` tone & manner row")
    assert "say so explicitly" in block, \
        "Step 2's fallback must require saying explicitly that the mood was derived"
    assert "never silently invent" in block, \
        "Step 2's fallback must forbid silently inventing a mood while appearing to inherit"
    assert inherit_at < fallback_at, (
        "the inherit rule must come BEFORE the absent-anchor fallback — "
        "the fallback is subordinate to it, not the primary path"
    )


def _surface_block() -> str:
    """The surface-treatment candidate-round block of the body — lowercased,
    whitespace-flattened.

    Scoped to the block that must carry the pick protocol; a whole-file
    membership pin would false-green on a SKILL.md that merely mentions a
    treatment (and a bare "3-5" already occurs elsewhere in this repo's
    skills — see docs/loom/memory/
    grep-tests-scope-to-measured-neighborhood.md). Flattened so a pinned
    phrase still matches across the prose's line wraps.
    """
    text = _text()
    start = text.index("**Surface treatment — the candidate round")
    end = text.index("### Step 4b", start)
    return re.sub(r"\s+", " ", text[start:end]).lower()


def test_surface_treatment_candidate_pick_protocol():
    """The GUI beat runs a real surface-treatment PICK — a candidate round from
    the Axis-B canon, a surfaced rejection list, and a USER decision — whose
    result is named in prose in Overview / Brand and constrains the Elevation &
    Depth + Shapes tokens.

    Full phrases are pinned inside the block (never bare "3-5"), and both
    ordering claims — the round is downstream of the tone & manner anchor, and
    the constraint is stated before the proposal — are positional assertions,
    because the claims are relational (see docs/loom/memory/
    assertion-must-encode-the-property-it-claims.md).
    """
    text = _text()
    block = _surface_block()

    # (a) the Axis-B canon is cited by relative path
    assert "references/canon-design-surface.md" in text, \
        "body must cite the surface canon by relative path"
    assert "references/canon-design-surface.md" in block, \
        "the candidate round must draw its candidates from the surface canon"

    # (b) 3-5 candidates with fit/tension
    assert "propose 3-5 surface-treatment candidates" in block, \
        "the round must propose 3-5 surface-treatment candidates"
    assert "fit/tension" in block, \
        "each candidate must carry fit/tension notes"

    # (c) 1-2 considered-but-rejected, SURFACED with reasons
    assert "1-2 considered-but-rejected candidates" in block, \
        "the round must name 1-2 considered-but-rejected candidates"
    assert "surface them to the user with reasons" in block, \
        "the rejection list must be surfaced to the user with reasons"

    # (d) the USER decides, with the bespoke escape hatch
    assert "the user decides" in block, \
        "the USER — not the agent — picks the surface treatment"
    assert "bespoke — no canon treatment fits" in block, \
        "the bespoke escape hatch must be legal and named"
    assert "escape hatch" in block, \
        "the bespoke option must be framed as a legal escape hatch"

    # (e) the pick is NAMED + rationalized in prose in Overview / Brand,
    #     riding inside the frozen 8-section contract (no 9th section)
    assert "overview / brand" in block, \
        "the pick must be named in the existing Overview / Brand section"
    assert "surface treatment: x — because" in block, \
        "the pick must be named AND rationalized in prose (name + because)"
    assert "do not add a 9th" in block, \
        "the pick rides in prose — it must NOT add a 9th `##` section"
    assert "all 8 `##` sections in order" in text, \
        "the frozen 8-section contract must remain stated verbatim"

    # (f) the pick constrains the Elevation & Depth + Shapes token blocks
    constrains_at = block.index("constrains the `## elevation & depth`")
    assert "`## shapes`" in block[constrains_at:], \
        "the pick must constrain BOTH the Elevation & Depth and Shapes tokens"

    # (g) the anti-costume law carries over
    assert "anti-costume law" in block, \
        "the anti-costume law must carry over to the surface axis"
    assert "never overrides a principles value" in block, \
        "a treatment may enrich candidates but never override a PRINCIPLES value"

    # (h) the WCAG risk flag is a BLOCKER, not a note
    wcag_at = block.index("wcag risk flag")
    assert "blocker" in block[wcag_at:wcag_at + 200], \
        "an unresolved WCAG risk flag must be a BLOCKER, not a note"

    # ordering 1 — the round is DOWNSTREAM of the Step-2 tone & manner anchor
    assert text.index("### Step 2") < text.index(
        "**Surface treatment — the candidate round"
    ), "the candidate round must sit downstream of the Step-2 anchor"

    # ordering 2 — the anchor CONSTRAINS the proposal, so it is stated first
    anchor_at = block.index("downstream of the tone & manner anchor")
    propose_at = block.index("propose 3-5 surface-treatment candidates")
    assert anchor_at < propose_at, (
        "the anchor constraint must be stated BEFORE the proposal instruction "
        "— it governs which treatments are proposable at all"
    )


def _schema_overview_block() -> str:
    """The `## Overview / Brand` section of the schema — lowercased,
    whitespace-flattened.

    Scoped to the section that carries the Derivation contract (Visual concept
    / Mood / Generative visual principles); a whole-file pin would pass on a
    schema that mentions the anchor anywhere at all (see docs/loom/memory/
    grep-tests-scope-to-measured-neighborhood.md). Flattened so a pinned phrase
    still matches across the prose's line wraps.
    """
    assert SCHEMA.is_file(), f"design-md-schema.md is absent at {SCHEMA}"
    text = SCHEMA.read_text(encoding="utf-8")
    start = text.index("## Overview / Brand")
    end = text.index("## Colors", start)
    return re.sub(r"\s+", " ", text[start:end]).lower()


def test_schema_mood_is_inherited_from_anchor():
    """The schema's Derivation contract must state Mood is INHERITED from
    PRINCIPLES.md's `## Anchors` tone & manner anchor (feeding `brand_voice`),
    not invented by the agent — mirroring SKILL.md Step 2's vocabulary — and
    must carry the same LOUD fallback when no anchor exists.

    The fallback is pinned as coming AFTER the inherit rule (a fallback that
    precedes the rule it falls back from is not a fallback) — a positional
    assertion, because the claim is relational (see docs/loom/memory/
    assertion-must-encode-the-property-it-claims.md).
    """
    block = _schema_overview_block()

    # (a) the anchor's source is named: PRINCIPLES.md's `## Anchors` section
    assert "principles.md" in block, \
        "the Derivation contract must name PRINCIPLES.md as the mood's source"
    assert "## anchors" in block, \
        "the Derivation contract must name PRINCIPLES.md's `## Anchors` section"

    # (b) the 3-5 tone & manner adjectives ARE the governing mood (SKILL.md
    #     Step 2's exact vocabulary — a paraphrase makes the two files disagree)
    assert "3-5 tone & manner adjectives" in block, \
        "the Derivation contract must name the 3-5 tone & manner adjectives"
    assert "governing mood" in block, \
        "the Derivation contract must state the adjectives are the GOVERNING mood"

    # (c) Mood feeds `brand_voice`, and is inherited — NOT re-derived / invented
    assert "brand_voice" in block, \
        "the Derivation contract must keep Mood feeding the `brand_voice` token"
    inherit_at = block.index("inherit")
    assert "do not re-derive" in block or "never re-derive" in block, \
        "the Derivation contract must forbid re-deriving the mood when an anchor exists"

    # (d) the loud fallback — absent anchor: derive as before AND say so
    fallback_at = block.index("no `## anchors` tone & manner row")
    assert "say so explicitly" in block, \
        "the fallback must require saying explicitly that the mood was derived here"
    assert "never silently invent" in block, \
        "the fallback must forbid silently inventing a mood while appearing to inherit"
    assert inherit_at < fallback_at, (
        "the inherit rule must come BEFORE the absent-anchor fallback — "
        "the fallback is subordinate to it, not the primary path"
    )


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
    assert "docs/loom/" in text, \
        "body must emit into docs/loom/"
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
