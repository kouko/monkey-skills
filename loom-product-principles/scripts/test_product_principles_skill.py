"""Structural grep-test guarding the product-principles SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing, principles-first instructions plus the hard
constraints the task and the host enforce:

  - YAML frontmatter declaring `name: product-principles` and a non-empty,
    key-free `description` that fits the Codex 1024-char HARD limit and carries
    en + zh-TW + ja trigger phrasings.
  - the principles-first body procedure (read the rules contract → elicit idea →
    North Star → 3-7 falsifiable principles each carrying the literal `— check:`
    marker → emit PRINCIPLES.md → validate).
  - references to BOTH the authoring contract (`references/principles-rules.md`)
    and the validator (`scripts/validate_principles_output.py`) by relative path.
  - the cross-cutting-constitution framing (governs interface-design / spec /
    code, incl headless), key-free + git-diffable.
  - flat-skill: the only subfolder under the skill dir is `references/` and it is
    single-level (no nested subdirs) — the repo hook blocks otherwise.

Checks assert on load-bearing PHRASES (intent), tolerant of wording variation.
Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "product-principles"
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


def _section(text: str, heading: str) -> str:
    """Body of a `## <heading>` section, up to the next `## ` heading."""
    m = re.search(r"^" + re.escape(heading) + r"\s*$", text, re.MULTILINE)
    assert m, f"SKILL.md must carry a '{heading}' section"
    nxt = re.search(r"^## ", text[m.end():], re.MULTILINE)
    return text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]


# --- YAML frontmatter -------------------------------------------------------

def test_frontmatter_name_is_product_principles():
    front = _frontmatter()
    assert re.search(r"^name:\s*product-principles\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: product-principles'"


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
    """The skill must fire on goal / principle / constitution intent in
    en + zh-TW + ja."""
    front = _frontmatter().lower()
    # en
    assert "principle" in front, "description must carry an English trigger"
    # zh-TW (Traditional)
    assert ("產品原則" in front or "設計原則" in front
            or "產品憲章" in front), \
        "description must carry a zh-TW trigger (產品原則 / 設計原則 / 產品憲章)"
    # ja
    assert ("原則" in front or "プロダクト指針" in front
            or "製品の原則" in front), \
        "description must carry a ja trigger (製品の原則 / プロダクト指針)"


def test_description_covers_design_and_engineering_triggers():
    """The three-jurisdiction scope must be routable in CJK too — a zh-TW/ja
    user asking specifically about design or engineering principles must hit
    this skill, not just product-principle phrasings."""
    front = _frontmatter()
    assert "設計原則" in front, \
        "description must carry a design-principles CJK trigger (設計原則)"
    assert ("工程原則" in front or "技術原則" in front
            or "エンジニアリング" in front), \
        "description must carry an engineering-principles CJK trigger " \
        "(工程原則 / 技術原則 / エンジニアリング原則)"


def test_description_states_principles_md_output():
    """description must signal it produces a PRINCIPLES.md governing
    design / spec / code, key-free."""
    front = _frontmatter()
    assert "PRINCIPLES.md" in front, \
        "description must state it produces a PRINCIPLES.md"
    low = front.lower()
    assert "north star" in low, "description must mention the North Star"


# --- principles-first body procedure ----------------------------------------

def test_body_references_rules_contract_by_relative_path():
    text = _text()
    assert "references/principles-rules.md" in text, \
        "body must reference the authoring contract by relative path"


def test_body_references_validator_by_relative_path():
    text = _text()
    assert "scripts/validate_principles_output.py" in text, \
        "body must reference the validator by relative path"


def test_body_has_north_star_and_principles_sections():
    text = _text()
    assert "## North Star" in text, \
        "body must instruct writing a '## North Star' section"
    assert "## Product Principles" in text, \
        "body must instruct writing a '## Product Principles' section"


def test_body_mandates_falsifiable_check_marker():
    """The load-bearing rule: every principle carries the literal '— check:'
    em-dash marker; platitudes are rejected."""
    text = _text()
    assert "— check:" in text, \
        "body must mandate the literal '— check:' em-dash marker on every principle"
    low = text.lower()
    assert "falsifiable" in low, "body must name the falsifiable-check rule"
    assert "platitude" in low or "push back" in low, \
        "body must reject platitudes / push back on un-checkable principles"
    assert "3" in text and ("7" in text), \
        "body must state the 3-7 principle count"


def test_body_emits_to_consumer_project_path():
    """The skill writes PRINCIPLES.md into the consumer project at the
    docs/<toolkit>/ convention — project-level, one per project."""
    text = _text()
    assert "docs/loom/PRINCIPLES.md" in text, \
        "body must emit PRINCIPLES.md to docs/loom/"


def test_body_mandates_validation_step():
    low = _text().lower()
    assert "validat" in low, \
        "body must instruct running the validator before declaring done"


def test_body_states_cross_cutting_constitution_role():
    """PRINCIPLES.md is the cross-cutting constitution governing downstream
    interface-design / spec / code, incl headless, key-free + git-diffable."""
    low = _text().lower()
    assert "constitution" in low, \
        "body must frame PRINCIPLES.md as the product constitution"
    assert "headless" in low or "cli" in low, \
        "body must state it applies to headless / CLI products"
    assert "key-free" in low, "body must state PRINCIPLES.md is key-free"
    assert "git-diffable" in low or "git diffable" in low, \
        "body must state PRINCIPLES.md is git-diffable"


def test_body_elicits_idea_and_target_user():
    low = _text().lower()
    assert "target user" in low, \
        "body must elicit the product idea + target user"


def test_skill_defines_three_jurisdiction_sections():
    """The generator elicits ALL three jurisdictions, not just Product: it
    must instruct writing '## Product Principles', '## Design Principles',
    and '## Engineering Principles' sections, with a dedicated elicitation
    step for design posture and one for engineering posture. Optional
    sections are emitted only for clauses the user actually commits to, and
    a jurisdiction with no committed clauses emits no section (never an
    empty heading)."""
    text = _text()
    low = text.lower()
    assert "## Product Principles" in text, \
        "body must instruct writing a '## Product Principles' section"
    assert "## Design Principles" in text, \
        "body must instruct writing a '## Design Principles' section"
    assert "## Engineering Principles" in text, \
        "body must instruct writing a '## Engineering Principles' section"
    assert "design stance" in low, \
        "body must have a design-stance elicitation step"
    assert "engineering stance" in low, \
        "body must have an engineering-stance elicitation step"
    assert "commit" in low, \
        "body must state clauses are emitted only from decisions the user " \
        "actually commits to"
    assert "empty" in low, \
        "body must state a jurisdiction with no committed clauses emits no " \
        "section (never an empty heading)"


# --- construction flow (instrument v0.1, designer/PM loop) -------------------
# No registered REQ-ids for this cluster — @req tags intentionally omitted.

def test_flow_user_states_first_and_probes_via_question_sets():
    """User-stated-first: the user states direction in their own words,
    then the agent probes via the question-sets reference (never inlined)."""
    text = _text()
    assert "references/question-sets.md" in text, \
        "body must point probing at references/question-sets.md by relative path"
    low = text.lower()
    assert "own words" in low, \
        "body must have the user state direction first, in their own words"


def test_flow_propose_then_react_on_stalls():
    """Stall recovery is a hypothesis to attack, never a repeated question."""
    low = _text().lower()
    assert "propose-then-react" in low, \
        "body must mandate propose-then-react on stalls"
    assert "stall" in low, "body must name the stall condition"
    assert "never repeat" in low, \
        "body must forbid repeating the open question on a stall"


def test_flow_cross_section_answer_propagation():
    """Decisions from an earlier section answer later questions — present a
    derived stance for confirmation instead of re-asking."""
    low = _text().lower()
    assert "cross-section" in low and "propagation" in low, \
        "body must mandate cross-section answer propagation"
    assert "re-ask" in low, \
        "body must forbid re-asking a question an earlier decision answers"


def test_flow_consults_four_canon_lists_as_completeness_audit():
    """The 4 canon base lists are agent-facing recall insurance consulted as
    a completeness audit; the user NEVER sees the raw lists."""
    text = _text()
    for ref in (
        "references/canon-product.md",
        "references/canon-design-interaction.md",
        "references/canon-design-visual.md",
        "references/canon-engineering.md",
    ):
        assert ref in text, f"body must reference {ref} by relative path"
    low = text.lower()
    assert "completeness audit" in low, \
        "body must frame the canon lists as a completeness audit"
    assert "raw lists" in low, \
        "body must state the user never sees the raw lists"


def test_flow_canon_double_guard_and_rejected_surfaced():
    """2-3 candidates with fit/tension notes; >=2 distinct traditions;
    1-2 considered-but-rejected SURFACED TO THE USER (FINDING-B2)."""
    text = _text()
    low = text.lower()
    assert "2-3" in text or "2–3" in text, \
        "body must propose 2-3 canon candidates"
    assert "≥2 distinct traditions" in text, \
        "body must require candidates from ≥2 distinct traditions"
    assert "considered-but-rejected" in low, \
        "body must name 1-2 considered-but-rejected candidates"
    assert "surface" in low, \
        "body must surface the considered-but-rejected candidates to the user"
    assert "fit/tension" in low, \
        "body must attach fit/tension notes to candidates"


def test_flow_user_decides_mix_and_bespoke_escape_hatch():
    low = _text().lower()
    assert "mix allowed" in low, "body must allow mixing canons"
    assert "bespoke" in low and "escape hatch" in low, \
        "body must keep the bespoke-section escape hatch legal"


def test_flow_anchors_and_deviation_ledger_version_pinned():
    text = _text()
    assert "## Anchors" in text, \
        "body must instruct writing an '## Anchors' section"
    assert "## Deviation Ledger" in text, \
        "body must instruct writing a '## Deviation Ledger' section"
    assert "version-pinned" in text.lower(), \
        "body must require anchors be version-pinned"


def test_flow_read_back_cadence_and_key_terms():
    """Per-section + final total read-back; the read-back surfaces the
    artifact's actual key terms (FINDING-B4, 報價單≠Invoice class)."""
    low = _text().lower()
    assert "read-back" in low, "body must mandate read-back confirmation"
    assert "per-section" in low or "per section" in low, \
        "body must mandate a per-section read-back"
    assert "final total" in low, \
        "body must mandate a final total read-back at the end"
    assert "key term" in low, \
        "read-back must surface the artifact's actual key terms"


def test_flow_question_coverage_self_check():
    """FINDING-B1: before leaving a section, enumerate its question set and
    verify coverage — don't trust recall."""
    low = _text().lower()
    assert "coverage self-check" in low, \
        "body must mandate a question-coverage self-check per section"
    assert "enumerate" in low, \
        "the coverage self-check must enumerate the question set, not recall it"


def test_flow_artifact_language_convention():
    """FINDING-B3: artifact language is a stated convention — repo
    convention wins; otherwise the user's conversation language."""
    low = _text().lower()
    assert "artifact language" in low, \
        "body must state the artifact-language convention"
    assert "repo convention" in low, \
        "artifact language: repo convention wins when one exists"
    assert "conversation language" in low or "user's language" in low, \
        "absent a repo convention the artifact is written in the user's language"


def test_flow_anchor_consistency_check():
    """FINDING-B5: an anchor cited for a decision that rejects that canon's
    direction fails read-back."""
    low = _text().lower()
    assert "anchor-consistency" in low, \
        "body must mandate an anchor-consistency check"


def test_flow_imperative_transition_after_stance_collection():
    """FINDING-B6: after the stance is collected, IMMEDIATELY run the canon
    audit + propose step; dispatching a subagent for the audit is sanctioned."""
    low = _text().lower()
    assert "immediately" in low, \
        "the stance→audit transition must be imperative (IMMEDIATELY)"
    assert "stance" in low, "body must name the collected stance as the trigger"
    assert "subagent" in low, \
        "body must sanction dispatching a subagent for the canon audit"


def test_flow_headless_seeded_mode():
    """§Headless/seeded: with no user available, every decision point
    degrades to its delegate-to-agent answer; choices recorded as
    agent-decided; read-back deferred-to-human; a run-input seed may
    pre-supply answers."""
    low = _text().lower()
    assert "seeded" in low, "body must define the headless / seeded mode"
    assert "delegate to agent" in low, \
        "every decision point must degrade to its delegate-to-agent answer"
    assert "agent-decided" in low, \
        "agent choices must be recorded as agent-decided"
    assert "deferred-to-human" in low, \
        "read-back must be marked deferred-to-human in headless mode"
    assert "run-input seed" in low, \
        "a run-input seed may pre-supply answers"


# --- round-2 review pins (code-quality findings, no registered REQ-ids) -----

def test_tripwire_routes_unanswerable_probing_to_discovery():
    """R2 finding 4a pin: when the problem/users probing is unanswerable,
    the Tripwire routes to using-loom-discovery instead of dead-ending into
    a fabricated North Star."""
    low = _text().lower()
    assert "tripwire" in low, \
        "body must carry the unanswerable-grilling tripwire"
    assert "using-loom-discovery" in low, \
        "the tripwire must route to using-loom-discovery"
    assert "fabricat" in low, \
        "the tripwire must name the fabricated-North-Star failure it prevents"


def test_test_rigor_clause_is_ceiling_above_iron_law_floor():
    """R2 finding 4b pin: a test-rigor clause is a ceiling above the TDD
    iron-law floor, never below it."""
    low = _text().lower()
    assert "ceiling" in low and "floor" in low, \
        "body must state the test-rigor clause is a ceiling above a floor"
    assert "iron-law" in low or "iron law" in low, \
        "the floor must be named as the TDD iron-law"


def test_headless_thin_seed_refuses_loudly_never_fabricates():
    """R2 finding 1: a headless run whose seed is too thin to ground a North
    Star REFUSES loudly — a BLOCKED-style structured refusal to the conductor
    stating what the seed lacks and naming using-loom-discovery as the
    human-side remedy — and NEVER fabricates."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "refus" in low, \
        "§Headless must state thin-seed runs refuse (not fabricate)"
    assert "blocked" in low, \
        "§Headless must shape the refusal as a BLOCKED-style structured return"
    assert "lack" in low, \
        "the refusal must state what the seed lacks"
    assert "using-loom-discovery" in low, \
        "§Headless must name using-loom-discovery as the human-side remedy"
    assert re.search(r"never\s+fabricate", low), \
        "the no-fabrication rule must stay unconditional in headless mode"


def test_headless_agent_decided_literal_marker_greppable():
    """R2 finding 2: agent-alone choices carry the literal `(agent-decided)`
    marker appended at the end of the same physical line as the choice (a
    Deviation Ledger entry or a `— check:` clause line); deferred-to-human
    read-back = grep the marker and walk the human through each hit. The
    bare undefined term 'decision entries' is gone."""
    text = _text()
    low = text.lower()
    assert "(agent-decided)" in text, \
        "body must define the literal '(agent-decided)' marker"
    assert "same physical line" in low, \
        "the marker sits at the end of the same physical line as its choice"
    assert "grep" in low, \
        "deferred-to-human read-back must grep '(agent-decided)' and walk " \
        "the human through each hit"
    assert "decision entries" not in low, \
        "the undefined bare term 'decision entries' must be dropped"


def test_stance_terminology_unified_with_question_sets():
    """R2 finding 3: one concept, one word across the pointer boundary —
    the instrument (references/question-sets.md) says 'stance'; SKILL.md
    must not alias it as 'posture'."""
    low = _text().lower()
    assert "design stance" in low, \
        "the design elicitation must use the instrument's term 'stance'"
    assert "engineering stance" in low, \
        "the engineering elicitation must use the instrument's term 'stance'"
    assert "posture" not in low, \
        "SKILL.md must not alias 'stance' as 'posture' (one concept, one word)"


def test_anchors_and_ledger_bullets_scoped_omit_when_empty():
    """R2 finding 5: the never-emit-an-empty-section scoping applies to the
    ## Anchors and ## Deviation Ledger bullets too — both read as optional
    (omit when empty), not unconditional."""
    low = _text().lower()
    assert low.count("omit when empty") >= 2, \
        "both the ## Anchors and ## Deviation Ledger bullets must carry " \
        "the '(likewise optional; omit when empty)' scoping"


# --- cold-operator dogfood fix pins (T6.1: F1/F2/F3, no registered REQ-ids) --

def test_flow_candidate_round_is_same_axis_alternatives():
    """F1: the 2-3 candidates in one proposal round are same-axis
    alternatives — answers to the SAME question; canons answering different
    questions are complementary and become separate Anchors rows, never one
    exclusive pick-one menu (live failure: Local-First / Clean Architecture /
    SwiftUI-MVVM / Modular Monolith offered as one menu; the user stalled)."""
    low = _text().lower()
    assert "same-axis" in low or "same axis" in low, \
        "candidates in one proposal round must be same-axis alternatives"
    assert "same question" in low, \
        "same-axis must be defined as answers to the SAME question"
    assert "complementary" in low, \
        "canons answering different questions must be named complementary"
    assert re.search(r"anchors`?\s+rows", low), \
        "complementary canons must be pinned as separate Anchors rows, " \
        "never one exclusive menu"


def test_flow_rejected_guard_is_per_round_every_section():
    """F2: the 1-2 considered-but-rejected guard applies to EVERY section's
    candidate round (Product AND Design AND Engineering), not just the first
    (live failure: operator did Product and Engineering, skipped Design)."""
    low = _text().lower()
    assert "per-round" in low or "per round" in low, \
        "the considered-but-rejected guard must be explicitly per-round"
    assert re.search(r"every\s+section", low), \
        "the guard must apply to every section's candidate round"
    assert re.search(r"not\s+just\s+the\s+first", low), \
        "the guard must state it is not just for the first round"


def test_draft_time_entry_count_self_check():
    """F3: at the drafting step, count the entries BEFORE presenting a
    draft; if over the section's cap, merge before showing the user — do
    not wait for the validator (live failure: operator drafted 8 and only
    the user's question caught it)."""
    low = _text().lower()
    assert "count the entries" in low, \
        "drafting step must count the entries before presenting a draft"
    assert "before presenting" in low or "before showing" in low, \
        "the count self-check happens BEFORE presenting the draft"
    assert "merge" in low, \
        "an over-cap draft must be merged before showing the user"
    assert re.search(r"wait\s+for\s+the\s+validator", low), \
        "the self-check must not defer the count to the validator"


# --- seed-traceability pins (n=4 headless replay findings, no registered
# REQ-ids) ---------------------------------------------------------------------


def test_headless_seed_traceability_invariant_no_silent_drops():
    """n=4 replay root cause: §Headless had no rule for seed content that is
    neither an answer nor a gap. The invariant: EVERY seed item lands in the
    artifact at AT LEAST one of a carrying principle, an Anchors row, an Open
    Question, an explicit Deviation Ledger entry, or (for North-Star-bound
    facts) the North Star — no silent drops. R2 🟡1: 'exactly one'
    contradicted the sub-clauses and the oracle — a seed-named canon
    legitimately lands BOTH as an Anchors row AND under a carrying
    principle; the floor is 'at least one'."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "seed-traceability" in low, \
        "§Headless must name the seed-traceability invariant"
    assert "at least one" in low, \
        "every seed item must land at AT LEAST one landing spot"
    assert "exactly one" not in low, \
        "'exactly one' forbids the legitimate double-landing (Anchors row " \
        "AND carrying principle for a seed-named canon) — it must be gone"
    assert "carrying principle" in low, \
        "a carrying principle must be a named landing spot"
    assert "anchors" in low, "an Anchors row must be a named landing spot"
    assert "open question" in low, \
        "an Open Question must be a named landing spot"
    assert "deviation ledger" in low, \
        "a Deviation Ledger entry must be a named landing spot"
    assert "silent" in low, \
        "the invariant must name the silent-drop failure it forbids"


def test_headless_deferred_seed_stance_becomes_open_question():
    """4/4 runs dropped the seed's deferred stance (成本=無法判斷→懸案): a
    seed stance marked undecidable/deferred MUST become an Open Question
    with a re-trigger condition — never dropped."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "deferred" in low or "undecidable" in low, \
        "§Headless must handle a seed stance marked undecidable/deferred"
    assert "open question" in low, \
        "a deferred seed stance must become an Open Question"
    assert "re-trigger" in low, \
        "the Open Question must carry a re-trigger condition"
    assert re.search(r"never\s+dropped", low), \
        "a deferred seed stance is never dropped"


def test_headless_seed_named_canon_lands_in_anchors():
    """Seed-named canons/tech-stack dropped from Anchors (Apple Design
    Language 0/4, Core ML 0/4, JTBD 1/4): every seed-named canon or
    tech-stack choice MUST land as a version-pinned Anchors row."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "seed-named" in low, \
        "§Headless must bind seed-NAMED canons/tech-stack to Anchors"
    assert "tech-stack" in low, \
        "the rule must cover tech-stack choices, not just canons"
    assert "version-pinned" in low, \
        "seed-named canons must land as version-pinned Anchors rows"


def test_headless_every_seed_stance_has_carrying_principle():
    """Stance coverage compressed 7→4-5: every seed stance MUST have a
    carrying principle — merging stances is fine; dropping one is not."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "carrying principle" in low, \
        "every seed stance must have a carrying principle"
    assert "merg" in low, "merging stances must be stated as legitimate"
    assert "dropping" in low, \
        "dropping a stance must be stated as illegitimate"


def test_headless_seed_walk_is_mechanical_not_self_report():
    """Superseded per plan 2026-07-12-principles-mechanical-seed-gate Decision
    Log 4: the old prose "Post-draft seed walk" self-report bullet is GONE
    (pinned negatively in test_inventory_step_and_checker_gate_present); in
    its place, §Headless points at Step 8's mechanical checker gate
    (check_seed_traceability.py against seed-inventory.md) as the thing that
    now enforces this invariant — never a memory-based re-walk."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "check_seed_traceability.py" in low, \
        "§Headless must point at the check_seed_traceability.py mechanical " \
        "gate as the seed-coverage enforcement mechanism"
    assert "mechanical" in low, \
        "the seed-coverage gate must be framed as mechanical, not a " \
        "self-report walk"
    assert "seed-inventory.md" in low, \
        "the mechanical gate must be run against the seed-inventory.md " \
        "written by the inventory-authoring step"


# --- round-2 seed-traceability review pins (3 🟡 findings, no registered
# REQ-ids) ---------------------------------------------------------------------


def test_headless_seed_item_granularity_is_decidable():
    """R2 🟡2a: 'seed item' was not decidable — a walk at bullet granularity
    passed while dropping 4 of 5 stances packed in one bullet. An item is
    each INDIVIDUAL stance, named canon, tech-stack choice, or deferred
    marker, EVEN when several share one bullet/line of the seed."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert re.search(r"each\s+individual\s+stance", low), \
        "a seed item must be defined as each INDIVIDUAL stance"
    assert "deferred marker" in low, \
        "the item definition must include deferred markers"
    assert re.search(r"share\s+one\s+bullet", low), \
        "the definition must hold even when several items share one bullet/line"
    assert "bullet granularity" in low, \
        "a bullet-granularity walk must be named as the violation it is"


def test_headless_north_star_bound_facts_land_in_north_star():
    """R2 🟡2b: the landing spots did not cover North-Star-bound seed facts
    (the idea / the target user / the success condition) — the `## North
    Star` section is their legitimate landing spot."""
    section = _section(_text(), "## Headless / seeded mode")
    assert "## North Star" in section, \
        "§Headless must name the ## North Star section as a landing spot"
    low = section.lower()
    assert "north-star-bound" in low, \
        "the North Star landing must be scoped to North-Star-bound facts"
    assert "target user" in low, \
        "the North-Star-bound facts must name the target user"


def test_headless_out_of_jurisdiction_noted_not_silently_skipped():
    """R2 🟡2b: seed content outside this skill's jurisdiction (per
    §Boundary — market / business-model / strategy turf) is explicitly
    noted as out-of-jurisdiction during the seed walk — not silently
    skipped, and not laundered into a spurious Open Question."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert "out-of-jurisdiction" in low, \
        "out-of-jurisdiction must be a named outcome of the seed walk"
    assert "boundary" in low, \
        "the out-of-jurisdiction rule must cite §Boundary as its scope source"
    assert re.search(r"not\s+silently\s+skipped", low), \
        "out-of-jurisdiction content is noted, never silently skipped"
    assert "spurious open question" in low, \
        "out-of-jurisdiction content must not become a spurious Open Question"


def test_headless_seed_named_canon_never_out_of_jurisdiction():
    """Round-3 replay leak (n=2, ADL 0/2, Swift 0/2, Core ML 0/2): the weak
    model used the out-of-jurisdiction escape hatch to drop seed-NAMED
    canons/tech-stack, rationalizing them as 'TECH-SPEC turf' or 'downstream
    spec'. Close the hatch: a seed-NAMED canon, tradition, or tech-stack
    choice is NEVER out-of-jurisdiction — that landing applies ONLY to the
    §Boundary-listed categories (market / business-model / strategy-document
    content); classifying a named canon/stack choice as out-of-
    jurisdiction during the seed walk is itself a violation."""
    low = _section(_text(), "## Headless / seeded mode").lower()
    assert re.search(r"never\s+out-of-jurisdiction", low), \
        "a seed-named canon/tradition/tech-stack choice must be stated as " \
        "NEVER out-of-jurisdiction"
    assert "only to the §boundary-listed categories" in low, \
        "the out-of-jurisdiction landing must be scoped ONLY to the " \
        "§Boundary-listed categories"
    assert "tech-spec turf" in low, \
        "classifying a named canon/stack choice as TECH-SPEC turf must be " \
        "named as the violation"
    assert "downstream spec" in low, \
        "classifying a named canon/stack choice as downstream spec must be " \
        "named as the violation"
    assert "violation" in low, \
        "misclassifying a seed-named canon/stack choice must be named a " \
        "violation of the invariant"


def test_inventory_step_and_checker_gate_present():
    """Mechanical seed-coverage gate (plan Task 1, no registered REQ-ids):
    (a) §Headless/seeded gains an inventory-authoring step BEFORE drafting
    that names both checker-format keys (`named_anchors:` / `deferred_items:`)
    and explicitly warns never to use `negative:` (must-be-ABSENT semantics,
    the wrong sense for an inventory); (b) Step 8 is extended so interactive
    sessions ALSO run check_seed_traceability.py and gate on exit 0; (c) the
    old prose "Post-draft seed walk" self-report bullet is superseded and
    gone — the mechanical gate replaces it (Decision Log 4)."""
    text = _text()
    low = text.lower()

    headless = _section(text, "## Headless / seeded mode")
    headless_low = headless.lower()
    assert "seed-inventory.md" in headless_low, \
        "§Headless must instruct writing a seed-inventory.md file before drafting"
    assert "named_anchors:" in headless, \
        "the inventory step must name the `named_anchors:` checker key"
    assert "deferred_items:" in headless, \
        "the inventory step must name the `deferred_items:` checker key"
    assert re.search(r"never\s+use\s+`?negative:", headless_low) or \
        re.search(r"never.{0,40}negative:", headless_low), \
        "the inventory step must warn to NEVER use `negative:` " \
        "(must-be-absent semantics, wrong for an inventory)"
    assert "write-only" in headless_low, \
        "the inventory step must be write-only (no scripts) for the drafting agent"

    assert "check_seed_traceability.py" in text, \
        "Step 8 must name the check_seed_traceability.py checker command"
    assert re.search(r"exit\s*0", low), \
        "Step 8's checker gate must proceed only on exit 0"

    assert "post-draft seed walk" not in low, \
        "the old prose 'Post-draft seed walk' self-report bullet must be " \
        "gone — superseded by the mechanical checker gate (Decision Log 4)"


def test_step8_interactive_seed_inventory_has_derivation_source():
    """R2 fix (spec-reviewer NEEDS_REVISION + quality 🟡, same root): Step 8's
    interactive-extension paragraph references "the seed-inventory document"
    but no interactive-flow step ever authors one — a dangling antecedent.
    Pin that interactive sessions derive it from the confirmed user answers
    (Steps 2-4), BEFORE running the checker."""
    text = _text()
    m = re.search(r"### Step 8.*?(?=\n## )", text, re.DOTALL)
    assert m, "SKILL.md must carry a Step 8 section"
    step8_low = m.group(0).lower()

    assert "derive" in step8_low, \
        "Step 8 must instruct deriving the interactive seed-inventory.md " \
        "(not just reference a document that nothing authors)"
    assert re.search(r"user'?s?\s+answers", step8_low), \
        "Step 8's derivation must be anchored in the confirmed user answers"
    assert "seed-inventory.md" in step8_low, \
        "Step 8 must name the seed-inventory.md artifact for interactive sessions"


def test_headless_open_question_points_at_rules_file_format():
    """R2 🟡3: the Open Question landing spot now has a defined format —
    the invariant clause points at the `## Open Questions` contract in
    references/principles-rules.md (relative path, as elsewhere)."""
    section = _section(_text(), "## Headless / seeded mode")
    assert "## Open Questions" in section, \
        "§Headless must name the ## Open Questions contract section"
    assert "references/principles-rules.md" in section, \
        "the Open Question clause must point at the rules file by relative path"


def test_canon_audit_lists_surface_file():
    """Task 4a: Step 3's canon-audit list must name BOTH visual canon files
    (canon-design-visual.md for Axis A cultural/graphic-design movements,
    canon-design-surface.md for Axis B UI-surface-treatment eras), and the
    body must describe the visual lens running as TWO axis-typed candidate
    rounds, each reading ONLY its own file (contamination guard), each
    landing as its own version-pinned ## Anchors row since the axes are
    complementary (different questions), never one pick-one menu."""
    text = _text()
    low = text.lower()
    assert "references/canon-design-surface.md" in text, \
        "Step 3's canon-audit list must also name references/canon-design-surface.md"
    assert "references/canon-design-visual.md" in text, \
        "Step 3's canon-audit list must still name references/canon-design-visual.md"
    assert "axis a" in low, \
        "body must name Axis A (cultural/graphic-design movements) round"
    assert "axis b" in low, \
        "body must name Axis B (UI-surface-treatment eras) round"
    assert "its own file" in low, \
        "body must state each axis-typed round reads ONLY its own file " \
        "(contamination guard)"
    assert "complementary" in low, \
        "the two axes must be named complementary, extending the existing " \
        "separate-Anchors-rows rule"


def test_visual_lens_3_5_carveout():
    """Task 5a: the VISUAL lens carves out 3-5 canon candidates (overriding
    the generic 2-3), including 1-2 deliberately divergent/exploratory
    candidates that deviate from the user's stated stance but stay
    defensible against the PRINCIPLES values (anti-costume: exploration
    never overrides the non-negotiable values). The generic 2-3 rule for
    Product/Engineering must remain unchanged — no global bump."""
    text = _text()
    low = text.lower()
    assert "3-5" in text or "3–5" in text, \
        "Step 3 must carve out 3-5 candidates for the visual lens"
    assert "divergent" in low or "exploratory" in low, \
        "the visual carve-out must name a divergent/exploratory candidate subset"
    assert "defensible" in low, \
        "the divergent candidates must be guarded as defensible against the values"
    # Guard: the generic 2-3 rule for Product/Engineering must still be present
    # (no global bump to 3-5). Anchored on the generic rule's own phrase so a
    # stray "2-3" (e.g. the carve-out's "overriding the generic 2-3") can't
    # satisfy it — the invariant is the propose-count rule itself.
    assert "2-3 canon candidates" in low or "2–3 canon candidates" in low, \
        "the generic '2-3 canon candidates' rule must remain for Product/Engineering"


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
