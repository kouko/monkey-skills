"""Structural grep-test guarding the spec-expansion SKILL.md load-bearing
instructions.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of buried, single-sentence, load-bearing rules that the
`extract-to-reference` memory warns get silently lost in prose: the 5-stage
pipeline, provenance tagging (all three tags), the ban-the-word-"complete"
guardrail, and the hybrid output-format markers the validator enforces.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "spec-expansion" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# --- YAML frontmatter -------------------------------------------------------

def test_yaml_frontmatter_name_and_description():
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    front = m.group(1)
    assert re.search(r"^name:\s*spec-expansion\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: spec-expansion'"
    desc = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert desc and desc.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"


def test_description_triggers_on_spec_expansion_intent():
    text = _text().lower()
    front = text.split("---", 2)[1] if text.count("---") >= 2 else text
    # description should signal spec-expansion / fan-out / edge-case coverage
    assert "spec-expansion" in front or "spec expansion" in front
    assert "edge" in front  # edge-case coverage trigger


# --- the 5-stage pipeline ---------------------------------------------------

def test_five_stage_pipeline_present():
    text = _text().lower()
    # ① extract objects + CTAs
    assert "object" in text and ("cta" in text or "call to action" in text), \
        "stage 1: extract objects + CTAs"
    # ② OOUX fan-out (per-object attributes/states/relationships)
    assert "ooux" in text, "stage 2: OOUX fan-out"
    assert "state" in text and "relationship" in text, \
        "stage 2: per-object attributes/states/relationships"
    # ③ the backbone x object x CTA x state grid
    assert "backbone" in text and "grid" in text, \
        "stage 3: backbone x object x CTA x state grid"
    # ④ lens layer prune (name several lenses)
    assert "lens" in text, "stage 4: lens layer"
    for lens in ("bva", "crud", "permission", "nfr"):
        assert lens in text, f"stage 4 lens missing: {lens}"
    assert "state-transition" in text or "state transition" in text, \
        "stage 4 lens: state-transition legality"
    # ⑤ emit
    assert "emit" in text, "stage 5: emit"


def test_multi_agent_fan_out_referenced():
    text = _text().lower()
    assert "dispatching-parallel-agents" in text or "fan-out" in text \
        or "fan out" in text or "parallel" in text, \
        "must reference multi-agent fan-out for per-object expansion"


# --- provenance tagging (all three tags) ------------------------------------

def test_provenance_tags_all_three():
    text = _text().lower()
    for tag in ("seeded", "inferred", "critic-found"):
        assert tag in text, f"provenance tag missing: {tag}"
    assert "provenance" in text, "must instruct provenance tagging"


# --- ban-the-word-"complete" guardrail --------------------------------------

def test_ban_complete_guardrail():
    text = _text()
    low = text.lower()
    # the guardrail phrase: never claim "complete"
    assert "complete" in low, "guardrail must reference the banned word"
    assert "coverage relative to seed" in low, \
        "guardrail must mandate 'coverage relative to seed + N lenses' framing"


# --- hybrid output-format markers (validator contract) ----------------------

def test_hybrid_format_markers():
    text = _text()
    # additive sections the validator enforces (exact header strings)
    assert "## Provenance" in text
    assert "## Blind spots" in text
    assert "## Path × edge matrix" in text
    # OpenSpec skeleton joint
    assert "## ADDED Requirements" in text
    assert "### Requirement:" in text
    assert "#### Scenario:" in text
    low = text.lower()
    assert "given" in low and "when" in low and "then" in low, \
        "scenario skeleton must name GIVEN/WHEN/THEN"


def test_specs_delta_stays_openspec_pure():
    low = _text().lower()
    # the specs/ delta stays validate-clean; richness lives in proposal.md
    assert "proposal.md" in low
    assert "specs/" in low or "specs/" in _text()


# --- boundary: stops at GENERATE --------------------------------------------

def test_generate_boundary_no_tdd_no_review():
    low = _text().lower()
    assert "generate" in low, "must state it stops at GENERATE"
    # hands off to code-toolkit VERIFY
    assert "code-toolkit" in low and ("verify" in low or "writing-plans" in low), \
        "must hand off to code-toolkit's VERIFY layer"
