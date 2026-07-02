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


# --- L3 journey-navigation layer --------------------------------------------

def test_l3_journey_navigation_present():
    """The L3 journey-navigation layer: Phase ① ALSO builds the backbone as a
    navigation graph; a Phase ③c sub-step applies 0-switch state-transition
    coverage to it (broadly, any flow with ≥2 stages); proposal.md carries a
    `## Journey navigation` section as the Phase ③c artifact."""
    text = _text()
    low = text.lower()
    # the Phase ③c announce marker (exact bytes — validator hard-codes same)
    assert "— Phase ③c journey navigation —" in text, \
        "must announce '— Phase ③c journey navigation —'"
    # the visible proposal.md artifact section (exact bytes)
    assert "## Journey navigation" in text, \
        "Phase ③c must emit a visible '## Journey navigation' section"
    # the backbone-as-navigation-graph instruction
    assert "navigation graph" in low, \
        "Phase ① must ALSO build the backbone as a navigation graph"
    # a coverage cue: 0-switch or state-transition
    assert "0-switch" in low or "state-transition" in low or "state transition" in low, \
        "Phase ③c must apply 0-switch / state-transition coverage to the graph"


def test_single_surface_backbone_collapse_present():
    """A single-surface / utility / floating app with no sequential journey
    has no multi-stage spine to lay; forcing one manufactures fiction (the
    seed-adequacy honesty rail). Phase ① must permit the USM backbone to
    COLLAPSE to ~1 stage node, with the navigation graph (Phase ③c) carrying
    the structure instead — a legitimate, honest output shape."""
    low = _text().lower()
    # single-surface cue
    assert "single-surface" in low or "single surface" in low, \
        "Phase ① must name the single-surface / utility / floating-app case"
    # collapse cue in proximity to the nav-graph / backbone structure carrier
    found_collapse = False
    for line in low.splitlines():
        if "collapse" in line and (
            "navigation graph" in line or "nav graph" in line
            or "backbone" in line
        ):
            found_collapse = True
            break
    assert found_collapse, \
        "Phase ① must say the backbone may COLLAPSE to ~1 node with the " \
        "navigation graph carrying the structure (collapse near nav-graph/backbone)"


# --- L2 cross-object-combination layer --------------------------------------

def test_l2_cross_object_combinations_present():
    """The L2 cross-object-combination layer: a Phase ③b sub-step enumerates
    per-stage joint state combinations of co-active objects, GATED on
    interaction-density; wide stages (≥4 co-active objects) call
    scripts/pairwise.py; proposal.md carries a `## Cross-object combinations`
    section as the Phase ③b artifact."""
    text = _text()
    low = text.lower()
    # the Phase ③b announce marker (exact bytes — validator hard-codes same)
    assert "— Phase ③b cross-object combinations —" in text, \
        "must announce '— Phase ③b cross-object combinations —'"
    # the visible proposal.md artifact section (exact bytes)
    assert "## Cross-object combinations" in text, \
        "Phase ③b must emit a visible '## Cross-object combinations' section"
    # the interaction-density gate
    assert "interaction-density" in low, \
        "Phase ③b must be gated on interaction-density"
    # the wide-stage pairwise generator path
    assert "scripts/pairwise.py" in text, \
        "wide stages (≥4 objects) must call scripts/pairwise.py"


def test_l2_wide_stage_mandates_pairwise_tool():
    """Wide stages (≥4 co-active objects) must be IMPERATIVE about tool use:
    the executor MUST run scripts/pairwise.py (a real-seed dogfood found the
    LLM bypasses it and reasons combinations inline, which the shipped A/B
    proved LEAKS). Two cues must co-occur on the wide-stage instruction:
    (1) an imperative MUST-run/MUST-invoke directive near pairwise.py, and
    (2) a ban on enumerating wide-stage combinations inline by reasoning."""
    low = _text().lower()

    # (1) imperative tool-use directive in proximity to pairwise.py — a soft
    # "instead call the generator" is NOT enough; require a MUST run/invoke
    # cue on a line that also names the tool.
    imperative_near_tool = False
    for line in low.splitlines():
        if "pairwise.py" in line and (
            "must run" in line or "must invoke" in line or "must call" in line
        ):
            imperative_near_tool = True
            break
    assert imperative_near_tool, \
        "wide-stage instruction must IMPERATIVELY mandate running " \
        "scripts/pairwise.py (MUST run/invoke/call), not softly suggest it"

    # (2) ban on inline enumeration of wide-stage combinations by reasoning.
    ban_inline = (
        "must not enumerate" in low
        or "do not enumerate" in low
        or "never enumerate" in low
        or "not inline" in low
        or ("inline" in low and "leak" in low)
    )
    assert ban_inline, \
        "wide-stage instruction must BAN inline reasoning-based enumeration " \
        "(the A/B-validated leak) — e.g. 'must not enumerate ... inline'"


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


# --- persistent intent layer authoring convention ---------------------------

def test_skill_documents_intent_layer():
    """The skill MUST document how to author the PERSISTENT intent layer:
    the TOP/MID locations, the three canonical TOP MODEL.md sections (which
    MUST mirror validate_intent_layer.py's _TOP_SECTIONS), the per-capability
    MID README.md, cut rule #4, and the MID-no-restate anti-pattern."""
    text = _text()
    low = text.lower()

    # an explicitly-named intent-layer authoring section
    assert "persistent intent layer" in low, \
        "must document authoring the persistent intent layer in a named section"

    # TOP + MID locations (exact paths)
    assert "docs/loom/spec/MODEL.md" in text, \
        "must name the TOP MODEL.md location docs/loom/spec/MODEL.md"
    assert "docs/loom/spec/<capability>/README.md" in text, \
        "must name the MID per-capability README.md location " \
        "docs/loom/spec/<capability>/README.md"
    assert "top" in low and "mid" in low, \
        "must distinguish the TOP vs MID altitudes"

    # the canonical TOP sections — imported from the validator (the SSOT) so a
    # VALIDATOR-side rename of _TOP_SECTIONS trips this test too, not only a
    # doc-side drift; this closes the doc-mirrors-code loop (Task-4 ↔ Task-1).
    from validate_intent_layer import _TOP_SECTIONS
    for header in _TOP_SECTIONS:
        assert header in text, \
            f"TOP MODEL.md canonical section missing: {header}"

    # cut rule #4: delete-the-capability test → YES→MID, NO→TOP
    assert "cut rule" in low, "must state cut rule #4 by name"
    found_cut = False
    for line in low.splitlines():
        if "delet" in line and "capability" in line:
            found_cut = True
            break
    assert found_cut, \
        "cut rule #4 must frame the 'remove this capability — does this " \
        "content get deleted?' test"
    assert "yes" in low and "no" in low, \
        "cut rule #4 must route YES→MID, NO→TOP"

    # the MID-no-restate anti-pattern (human-reviewed, NOT a CI gate)
    found_antipattern = False
    for line in low.splitlines():
        if "mid" in line and "restate" in line and (
            "test" in line or "behavior" in line
        ):
            found_antipattern = True
            break
    assert found_antipattern, \
        "must carry the anti-pattern: MID must not restate behavior a test owns"
    assert "rot" in low, \
        "anti-pattern must name the residual-rot surface it guards against"


# --- prior-state intake (closed loop: read own persisted layer) -------------

def test_skill_documents_prior_state_intake():
    """The skill MUST document consuming its OWN persisted intent layer as
    prior-state for the next cycle (closing the spec→spec loop). The section
    must carry: (a) point-don't-copy + link-back (never copy persisted
    content), (b) a seam-mapping table routing each persisted prior-state to
    the phase it feeds (5 rows), (c) the empty base case (additive / may be
    empty / absent → treat as a generic seed, no cold-start deadlock), and
    (d) the INDEX referenced WHEN-PRESENT."""
    text = _text()
    low = text.lower()

    # an explicitly-named prior-state intake section
    assert "prior-state" in low, \
        "must document consuming the persisted intent layer as prior-state " \
        "in a named section"

    # (a) point-don't-copy + link-back + never-copy wording
    assert "point-don't-copy" in low or "point don't copy" in low, \
        "(a) must carry the point-don't-copy convention"
    assert "link back" in low or "link-back" in low or "links back" in low \
        or "references" in low, \
        "(a) must link back / reference the persisted files by path"
    found_never_copy = False
    for line in low.splitlines():
        if ("never" in line or "not" in line) and "cop" in line:
            found_never_copy = True
            break
    assert found_never_copy, \
        "(a) must say it NEVER copies persisted content into the change-folder"

    # (b) the seam-mapping table: 5 prior-state → phase rows. Each cue must
    # co-occur with its target phase ON ONE source line (markdown table rows
    # are single lines), so wrapping cannot split the mapping.
    rows = [
        # (needle in the prior-state cell, needle in the phase cell)
        (("readme.md", "mid"), ("phase ①", "phase 1", "usm")),
        (("object state machines",), ("phase ②", "phase 2", "ooux")),
        (("invariants",), ("phase ③", "phase 3", "matrix")),
        (("out of scope",), ("phase ③", "phase 3", "prun")),
        (("index",), ("net-new", "net new", "fan")),
    ]
    for state_needles, phase_needles in rows:
        found = False
        for line in low.splitlines():
            if any(s in line for s in state_needles) and \
                    any(p in line for p in phase_needles):
                found = True
                break
        assert found, (
            f"seam-mapping row missing: a prior-state {state_needles} must map "
            f"to its phase {phase_needles} on one line"
        )

    # the canonical TOP section headers must be named as prior-state sources
    # (exact bytes, mirrors validate_intent_layer._TOP_SECTIONS).
    assert "## Object state machines" in text, \
        "(b) must reference TOP MODEL.md's '## Object state machines' section"
    assert "## Invariants" in text, \
        "(b) must reference TOP MODEL.md's '## Invariants' section"
    assert "## Out of scope" in text, \
        "(b) must reference TOP MODEL.md's '## Out of scope' section"

    # (c) the empty base case — additive, may be empty, absent → generic seed
    assert "additive" in low, \
        "(c) prior-state intake must be ADDITIVE"
    found_may_be_empty = False
    for line in low.splitlines():
        if "empty" in line and ("may" in line or "additive" in line):
            found_may_be_empty = True
            break
    assert found_may_be_empty, \
        "(c) must say the prior-state MAY BE EMPTY"
    found_generic = False
    for line in low.splitlines():
        if ("absent" in line or "no" in line or "nothing" in line) and \
                "generic seed" in line:
            found_generic = True
            break
    assert found_generic, \
        "(c) absent/empty layer → treat the input as a generic seed " \
        "(mirror the ui-flows stance)"
    assert "authoritative" in low, \
        "(c) an empty/absent layer is NEVER authoritative (no cold-start deadlock)"

    # (d) the INDEX referenced when-present
    found_index_when_present = False
    for line in low.splitlines():
        if "index" in line and ("when present" in line or "when-present" in line
                                 or "if present" in line):
            found_index_when_present = True
            break
    assert found_index_when_present, \
        "(d) the generated INDEX must be referenced read-WHEN-PRESENT"

    # READ-ONLY: this read path must not author/edit the persisted layer
    assert "read-only" in low or "read only" in low, \
        "the prior-state intake path must be READ-ONLY (authoring is a " \
        "separate section's job)"


# --- governing constitution (PRINCIPLES.md seam) -----------------------------

def test_body_reads_principles_as_governing_constraint():
    """The spec GENERATE station must read the product constitution the same
    way the design station's generators do (interaction-flows / design-system
    both carry a governing-constraint section): PRINCIPLES.md governs the
    fan-out WHEN PRESENT, and its absence is surfaced loudly — never silently
    treated as an unconstrained spec. Before this seam existed,
    product-principles claimed to govern spec-expansion but only the
    completeness-critic (lens 6, post-hoc) ever read the constitution."""
    text = _text()
    lines = text.splitlines()
    hits = [ln for ln in lines if "PRINCIPLES.md" in ln]
    assert len(hits) >= 2, \
        "body must READ the product's PRINCIPLES.md as a governing input — " \
        "not merely list it once as a sibling artifact path"
    assert any("govern" in ln.lower() or "constrain" in ln.lower()
               for ln in hits), \
        "some PRINCIPLES.md mention must frame it as governing/constraining " \
        "the expansion"
    # absence surfaced near a PRINCIPLES.md mention (8-line window)
    idxs = [i for i, ln in enumerate(lines) if "PRINCIPLES.md" in ln]
    window_ok = any(
        any(w in lines[j].lower() for w in ("absent", "absence", "missing"))
        for i in idxs
        for j in range(max(0, i - 4), min(len(lines), i + 5))
    )
    assert window_ok, \
        "PRINCIPLES.md absence must be surfaced (fail loud), near the " \
        "governing-constraint text"


# --- boundary: stops at GENERATE --------------------------------------------

def test_generate_boundary_no_tdd_no_review():
    low = _text().lower()
    assert "generate" in low, "must state it stops at GENERATE"
    # hands off to loom-code VERIFY
    assert "loom-code" in low and ("verify" in low or "writing-plans" in low), \
        "must hand off to loom-code's VERIFY layer"
