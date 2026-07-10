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
