"""Structural grep-test guarding the design-critic SKILL.md load-bearing
instructions.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of buried, single-sentence, load-bearing rules that get silently lost
in prose: the writer != judge panel, loop-until-dry, the multi-lens design-
surface interrogation (grounded in Nielsen's heuristics, NOT a fresh invented
checklist), the MUST-emit-its-own-blind-spots instruction (ban-"complete"), the
surface-not-behavioral boundary, and the conditional PRINCIPLES.md omission lens.

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "design-critic" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# --- YAML frontmatter -------------------------------------------------------

def test_yaml_frontmatter_name_and_description():
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    front = m.group(1)
    assert re.search(r"^name:\s*design-critic\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: design-critic'"
    desc = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert desc and desc.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"


def test_description_under_codex_limit():
    # Codex CLI silently drops skills whose description exceeds 1024 chars.
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    front = m.group(1)
    desc = re.search(r"^description:\s*(.+)$", front, re.MULTILINE)
    assert desc, "frontmatter must carry a description"
    assert len(desc.group(1).strip()) <= 1024, \
        "description must be <=1024 chars (Codex limit)"


def test_description_triggers_on_design_critique_intent():
    text = _text().lower()
    front = text.split("---", 2)[1] if text.count("---") >= 2 else text
    # description should signal design review / heuristic evaluation / blind spots
    assert "design" in front, "description must trigger on design"
    assert "blind spot" in front or "gap" in front or "omission" in front \
        or "missing" in front or "review" in front or "critique" in front, \
        "description must trigger on design review / blind spots / omissions"


# --- writer != judge panel + loop-until-dry ---------------------------------

def test_writer_not_judge_panel():
    low = _text().lower()
    assert "writer" in low and "judge" in low, \
        "must ground in writer != judge (an external critic, not self-review)"
    # decorrelated fresh-context lens subagents (the panel mechanism)
    assert "fresh context" in low or "fresh-context" in low \
        or "decorrelat" in low or "separate pass" in low, \
        "panel must dispatch fresh-context / decorrelated lens critics"


def test_loop_until_dry_present():
    low = _text().lower()
    assert "loop-until-dry" in low or "loop until dry" in low, \
        "must name the loop-until-dry strategy"
    assert "consecutive" in low, \
        "loop-until-dry must terminate after K consecutive empty rounds"
    assert "re-seed" in low or "reseed" in low or "re-seeds" in low \
        or ("seed" in low and "back" in low), \
        "must re-seed found gaps back into the next round"


# --- the multi-lens design-surface panel ------------------------------------

def test_multi_lens_panel_present():
    low = _text().lower()
    assert "lens" in low, "must describe a multi-lens interrogation"
    # lens 1: render-state completeness (empty/loading/error/success)
    for kw in ("empty", "loading", "error", "success"):
        assert kw in low, f"render-state lens missing keyword: {kw}"
    # lens 2: dead-end & exit / user control / reversible-undo
    assert "dead-end" in low or "dead end" in low, "lens: dead-end / exit"
    assert "exit" in low, "lens: exit coverage"
    assert "undo" in low or "reversible" in low or "user control" in low, \
        "lens: user control / reversible-undo"
    # lens 3: navigation reachability & entry
    assert "reach" in low, "lens: navigation reachability"
    assert "entry" in low, "lens: entry points"
    # lens 4: error prevention & recovery
    assert "error prevention" in low or "recovery" in low or "confirm" in low, \
        "lens: error prevention / recovery"
    # lens 5: modality fit & accessibility
    for kw in ("gui", "tui", "cli"):
        assert kw in low, f"modality lens missing keyword: {kw}"
    assert "a11y" in low or "accessibility" in low, "lens: accessibility"


def test_lenses_grounded_in_nielsen_canon():
    low = _text().lower()
    # grounded in canon, NOT an invented checklist
    assert "nielsen" in low, "lenses must be grounded in Nielsen's heuristics"
    assert "heuristic" in low, "must reference heuristic evaluation"


def test_lenses_are_independent():
    low = _text().lower()
    assert "blind to" in low or "independent" in low or "separate pass" in low \
        or "separate passes" in low or "decorrelat" in low, \
        "lenses must each be blind to the others (independent passes)"


# --- MUST emit its own blind spots ------------------------------------------

def test_must_emit_own_blind_spots():
    text = _text()
    low = text.lower()
    assert "blind spot" in low, "must instruct emitting its own blind spots"
    assert "cannot judge" in low or "can't judge" in low \
        or "cannot assess" in low, \
        "must state it emits aspects it CANNOT judge"
    assert "human" in low and "field" in low, \
        "blind spots are tagged 'needs human/field input'"
    assert "## Blind spots" in text, \
        "must write into a '## Blind spots' section"
    assert "non-empty" in low or "never empty" in low \
        or "must not be empty" in low, \
        "the Blind spots section MUST be non-empty"


def test_ban_claiming_complete():
    low = _text().lower()
    assert "complete" in low, "must reference the banned claim 'complete'"
    assert "never claim" in low or "ban" in low or "do not claim" in low \
        or "must not claim" in low or "cannot claim" in low, \
        "must ban claiming 'complete'"


# --- boundary: surface (design) NOT behavioral (spec) NOT code --------------

def test_surface_not_behavioral_boundary():
    low = _text().lower()
    assert "surface" in low, "boundary: critiques the design surface"
    # does NOT hunt spec behavioral omissions / does NOT review code
    assert "behavioral" in low or "behaviour" in low, \
        "boundary: surface omissions, NOT behavioral (spec) omissions"
    assert "completeness-critic" in low, \
        "boundary: behavioral completeness is completeness-critic's job"
    assert "fan-out" in low or "fan out" in low, \
        "boundary: flag here, fan-out there (the surface/depth split)"


# --- conditional PRINCIPLES.md omission lens (P2 parity) --------------------

def test_principles_conditional_lens():
    low = _text().lower()
    assert "principles.md" in low, \
        "must read PRINCIPLES.md when present (the conditional lens)"
    assert "n/a" in low, \
        "the PRINCIPLES lens must be an N/A no-op when PRINCIPLES.md is absent"


# --- Bitter-Lesson deletable-lens note --------------------------------------

def test_bitter_lesson_deletable_lens_note():
    low = _text().lower()
    assert "bitter lesson" in low or "bitter-lesson" in low, \
        "must carry the Bitter-Lesson deletable-lens note"
    assert "deletable" in low or "delete" in low or "prune" in low \
        or "re-baseline" in low or "rebaseline" in low, \
        "must state each lens is deletable / re-baseline periodically"
