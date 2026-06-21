"""Structural grep-test guarding the completeness-critic SKILL.md load-bearing
instructions.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of buried, single-sentence, load-bearing rules that the
`extract-to-reference` memory warns get silently lost in prose: loop-until-dry,
the multi-lens fixed interrogation checklist, the MUST-emit-its-own-blind-spots
instruction (with the writer != judge / 要件定義 grounding + ban-"complete"),
and the writer != judge / spec-not-code boundary.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "completeness-critic" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# --- YAML frontmatter -------------------------------------------------------

def test_yaml_frontmatter_name_and_description():
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    front = m.group(1)
    assert re.search(r"^name:\s*completeness-critic\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: completeness-critic'"
    desc = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert desc and desc.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"


def test_description_triggers_on_completeness_critique_intent():
    text = _text().lower()
    front = text.split("---", 2)[1] if text.count("---") >= 2 else text
    # description should signal completeness critique / gap-finding / blind spots
    assert "completeness" in front, "description must trigger on completeness"
    assert "blind spot" in front or "gap" in front or "omission" in front \
        or "missing" in front, \
        "description must trigger on finding gaps / blind spots / omissions"


# --- loop-until-dry ---------------------------------------------------------

def test_loop_until_dry_present():
    low = _text().lower()
    assert "loop-until-dry" in low or "loop until dry" in low, \
        "must name the loop-until-dry strategy"
    # K consecutive empty rounds termination
    assert "consecutive" in low, \
        "loop-until-dry must terminate after K consecutive empty rounds"
    # re-seed found gaps back into expansion
    assert "re-seed" in low or "reseed" in low or "re-seeds" in low \
        or "seed" in low and "back" in low, \
        "must re-seed found gaps back into the expansion"


# --- the multi-lens fixed interrogation checklist ---------------------------

def test_multi_lens_checklist_present():
    low = _text().lower()
    assert "lens" in low, "must describe a multi-lens interrogation"
    # lens 1: missing object/actor
    assert "actor" in low, "lens: missing object/actor"
    assert "object" in low, "lens: missing object/actor"
    # lens 2: state completeness (empty/partial/error/loading/no-permission)
    assert "state" in low, "lens: state completeness"
    for kw in ("empty", "error", "loading", "permission", "boundary"):
        assert kw in low, f"state-completeness lens missing keyword: {kw}"
    # lens 3: cross-object & system-layer failures
    for kw in ("concurrency", "network", "partial", "timing"):
        assert kw in low, f"system-layer-failure lens missing keyword: {kw}"
    # lens 4: NFR
    assert "nfr" in low, "lens: NFR"
    for kw in ("security", "privacy", "compliance"):
        assert kw in low, f"NFR lens missing keyword: {kw}"
    assert "a11y" in low or "accessibility" in low, "NFR lens: a11y"
    assert "i18n" in low or "internationalization" in low, "NFR lens: i18n"
    # lens 5: policy/legal/permissions
    assert "policy" in low, "lens: policy"
    assert "legal" in low, "lens: legal"


def test_lenses_are_independent():
    low = _text().lower()
    # each lens blind to the others (run as separate passes, not blended)
    assert "blind to" in low or "independent" in low or "separate pass" in low \
        or "separate passes" in low, \
        "lenses must each be blind to the others (independent passes)"


# --- MUST emit its own blind spots ------------------------------------------

def test_must_emit_own_blind_spots():
    text = _text()
    low = text.lower()
    # the required output: aspects it CANNOT judge -> needs human/field input
    assert "blind spot" in low, "must instruct emitting its own blind spots"
    assert "cannot judge" in low or "can't judge" in low \
        or "cannot assess" in low, \
        "must state it emits aspects it CANNOT judge"
    assert "human" in low and ("field" in low or "field input" in low), \
        "blind spots are tagged 'needs human/field input'"
    # the exact target section header the validator checks is non-empty
    assert "## Blind spots" in text, \
        "must write into the '## Blind spots' section the validator enforces"
    assert "non-empty" in low or "must be non-empty" in low \
        or "never empty" in low or "must not be empty" in low, \
        "the Blind spots section MUST be non-empty"


def test_blind_spots_grounding():
    low = _text().lower()
    # (a) writer != judge / self-evaluation fails (Planner-Generator-Evaluator)
    assert "writer" in low and "judge" in low, \
        "must ground in writer != judge"
    assert "self-eval" in low or "self eval" in low \
        or "self-evaluation" in low or "evaluator" in low, \
        "must reference self-evaluation failing (Planner-Generator-Evaluator)"
    # (b) 要件定義 caution: cannot manufacture missing business reality
    assert "manufacture" in low or "fabricate" in low or "hallucinate" in low, \
        "must state it cannot manufacture/hallucinate missing business reality"
    assert "business" in low or "domain" in low, \
        "must reference missing business-domain reality"


def test_ban_claiming_complete():
    low = _text().lower()
    assert "complete" in low, "must reference the banned claim 'complete'"
    # ban claiming "complete"
    assert "never claim" in low or "ban" in low or "do not claim" in low \
        or "must not claim" in low or "cannot claim" in low, \
        "must ban claiming 'complete'"


# --- boundary: writer != judge + spec-not-code ------------------------------

def test_spec_not_code_boundary():
    low = _text().lower()
    # critiques the SPEC for omissions only -- never code, never TDD
    assert "spec" in low, "boundary: critiques the spec"
    assert "not code" in low or "never code" in low \
        or "not review code" in low or "never reviews code" in low \
        or "never review code" in low, \
        "boundary: critiques spec NOT code"
    assert "tdd" in low, "boundary: never runs TDD"
    # that is loom-code's / VSDD's job
    assert "loom-code" in low or "vsdd" in low, \
        "boundary: code review / TDD is loom-code's / VSDD's job"


# --- dual-role note: L2/L3 systematization refocuses the critic ------------

def test_dual_role_note_present():
    low = _text().lower()
    # spec-expansion v0.2 systematizes L2 (cross-object) + L3 (journey)
    assert ("l2" in low and "l3" in low) \
        or ("cross-object" in low and "journey" in low), \
        "must note v0.2 systematizes L2 (cross-object) and L3 (journey)"
    # the critic REFOCUSES (not merely 'lighter') onto residual regimes
    assert "single-object" in low or "resume" in low or "landing" in low, \
        "must give a refocus cue (single-object / resume / landing)"


# --- how it writes back -----------------------------------------------------

def test_writes_back_provenance_critic_found():
    text = _text()
    low = text.lower()
    # appends/extends the Blind spots section + adds critic-found items
    assert "critic-found" in low, \
        "critic-found items must be tagged critic-found in Provenance"
    assert "## Provenance" in text, \
        "critic-found items go into the '## Provenance' section"
