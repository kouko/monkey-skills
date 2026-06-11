"""Structural grep-test guarding the spec-expansion SKILL.md load-bearing
instructions.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of buried, single-sentence, load-bearing rules that the
`extract-to-reference` memory warns get silently lost in prose: the THREE
explicit phases (USM / OOUX / auto-expansion matrix), each ANNOUNCED during
execution and each emitting a VISIBLE proposal.md artifact section; provenance
tagging (all three tags), the ban-the-word-"complete" guardrail, and the
hybrid output-format markers the validator enforces.

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


# --- the three explicit phases (USM / OOUX / auto-expansion matrix) ----------

def test_three_explicit_phases_present():
    """The skill documents THREE explicitly-named top-level phases, not a
    flat 5-stage pipeline."""
    text = _text().lower()
    # the three phase NAMES must be present as named phases
    assert "usm" in text, "phase 1: USM"
    assert "ooux" in text, "phase 2: OOUX"
    assert "auto-expansion matrix" in text or "expansion matrix" in text \
        or "自動拓展矩陣" in _text(), "phase 3: auto-expansion matrix"
    # the THREE explicit phases must be marked as distinct phases (not "5 stages")
    assert "phase" in text, "phases must be named as explicit phases"
    assert "phase ①" in text and "phase ②" in text and "phase ③" in text, \
        "three phases must be explicitly numbered ① ② ③"
    # the old 5-stage framing must be gone (restructured, not flat pipeline)
    assert "5-stage pipeline" not in text and "5 stage pipeline" not in text, \
        "the flat '5-stage pipeline' framing must be replaced by three phases"


def test_phases_announced_during_execution():
    """Each phase MUST be announced as it runs (visible execution trace)."""
    text = _text()
    # the literal announce markers the skill instructs the agent to emit
    assert "— Phase ① USM backbone —" in text, \
        "must instruct announcing Phase ① USM backbone"
    assert "— Phase ② OOUX object model —" in text, \
        "must instruct announcing Phase ② OOUX object model"
    assert "— Phase ③ auto-expansion matrix —" in text, \
        "must instruct announcing Phase ③ auto-expansion matrix"
    low = text.lower()
    assert "announce" in low, "must instruct the agent to ANNOUNCE each phase"


def test_three_visible_artifact_sections_per_phase():
    """Each phase emits a VISIBLE intermediate artifact section in proposal.md."""
    text = _text()
    assert "## USM backbone" in text, \
        "Phase ① must emit a visible '## USM backbone' section"
    assert "## OOUX object model" in text, \
        "Phase ② must emit a visible '## OOUX object model' section"
    assert "## Path × edge matrix" in text, \
        "Phase ③ must emit a visible '## Path × edge matrix' section"


def test_phase_detail_preserved():
    """The old 5 stages' detail must survive as sub-steps under the 3 phases."""
    text = _text().lower()
    # USM phase folds in actor/journey extraction; objects + CTAs
    assert "object" in text and ("cta" in text or "call to action" in text), \
        "extraction of objects + CTAs preserved"
    assert "backbone" in text, "USM backbone (journey spine) preserved"
    # OOUX phase: per-object attributes/states-as-state-machine/relationships
    assert "state machine" in text, \
        "OOUX phase: states modeled as a state machine"
    assert "relationship" in text and "attribute" in text, \
        "OOUX phase: per-object relationships/attributes preserved"
    # matrix phase: cartesian grid + lens prune + emit
    assert "grid" in text, "matrix phase: the cartesian grid preserved"
    assert "lens" in text, "matrix phase: lens-layer prune preserved"
    for lens in ("bva", "crud", "permission", "nfr"):
        assert lens in text, f"matrix-phase lens missing: {lens}"
    assert "state-transition" in text or "state transition" in text, \
        "matrix-phase lens: state-transition legality preserved"
    assert "emit" in text, "matrix phase: emit preserved"


def test_lenses_teach_discrimination_not_just_list():
    """Each of the 6 lenses must carry a 'when it dominates' cue AND a
    keep/flag/drop (or in-scope/noise) discriminator — the engine of the
    high-recall claim. Listing the lens name alone is the gap this closes."""
    text = _text()
    low = text.lower()

    # the discrimination vocabulary must be present across the lens layer:
    assert "dominates when" in low or "dominates" in low, \
        "lenses must teach WHEN each dominates, not just name them"
    assert ("keep" in low and "flag" in low and "drop" in low) \
        or ("in-scope" in low and "noise" in low), \
        "lenses must teach a legal-vs-illegal / in-scope-vs-noise discriminator"

    # every one of the six lenses must carry teaching vocab ON its own line —
    # not just appear as a bare bullet label.
    lens_cues = {
        "state-transition": ("state transition", "state-transition"),
        "bva": ("bva", "boundary"),
        "crud": ("crud",),
        "permission": ("permission",),
        # anchor on "loading" — unique to the empty/error/loading lens;
        # "empty" alone also appears in the BVA bullet, which would match the
        # wrong line and weaken the guard for this lens.
        "empty": ("loading",),
        "nfr": ("nfr",),
    }
    teach_words = ("dominates", "keep", "flag", "drop", "in-scope",
                   "noise", "discrimin")
    for lens, needles in lens_cues.items():
        found_teaching = False
        for line in low.splitlines():
            if any(n in line for n in needles) and any(t in line for t in teach_words):
                found_teaching = True
                break
        assert found_teaching, \
            f"lens '{lens}' must carry when-it-dominates / keep-flag-drop teaching on its line"


def test_seed_adequacy_preflight_gate():
    """Phase ① must OPEN with a seed-adequacy pre-flight: if the seed is too
    sparse to fan out responsibly, surface what's missing and ask the user /
    flag it BEFORE expanding — rather than manufacturing fiction."""
    low = _text().lower()
    assert "too sparse" in low or "sparse" in low, \
        "pre-flight must name the too-sparse condition"
    assert "before" in low, "pre-flight must fire BEFORE fan-out / expanding"
    assert "ask" in low, "pre-flight must ask the user / surface the gap"
    assert "fiction" in low or "manufactur" in low or "fabricat" in low, \
        "pre-flight must forbid manufacturing fiction from a sparse seed"
    assert "pre-flight" in low or "preflight" in low or "seed-adequacy" in low \
        or "seed adequacy" in low, \
        "the gate must be a named seed-adequacy pre-flight"


def test_sparse_output_fallback():
    """If pruning leaves no high-priority surviving paths, report honestly
    rather than padding — the sparse-output fallback."""
    low = _text().lower()
    assert "no high-priority" in low or "no surviving" in low \
        or "nothing survives" in low or "no high priority" in low, \
        "must handle the empty-after-prune case"
    assert "pad" in low or "padding" in low, \
        "sparse-output fallback must forbid padding"


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
