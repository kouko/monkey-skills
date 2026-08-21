"""Pointer-pin pytest for the writing-plans SKILL.md extraction batch,
Partition A (docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md
§Partition A — the FROZEN extraction SSOT).

Guards: A1 (Cross-skill contract) + A2 (What this skill does NOT do) fold
into references/cross-skill-map.md, headings absent from SKILL.md, a
residue/pointer line present in each's old location; A3 (Red Flags table)
moves to references/red-flags.md under pilot house shape — the heading +
a one-line refusal-posture distillation STAY inline, only the table rows
move; A4 (maintainer-facing fragments in §BLOCKED fallback, §Plan size
ceiling, §Consuming) move to references/design-evidence.md (author-facing
header) while the rules they qualify, and the 5-step process / anti-pattern
paragraph / detection-cascade rule sentences, stay inline verbatim. Word
ceiling <=4430 — the 2026-08-19 field-value-microstructure arc's Task 11
(the §Field-microstructure gate paragraph in §Self-review, mirroring the
Open-questions gate paragraph it sits directly under) landed the gate
paragraph on revision round 1 at 4510 words, 90 over the cap, and left
the cap test deliberately failing rather than raised (see
docs/loom/plans/2026-08-19-field-value-microstructure.md Task 11
revision round 1). Round 2 resolved it by CUTTING, not raising: four
paragraphs under §Consuming a loom-design change-folder (scenario→task
mapping, point-don't-copy/link-back, the verbatim-copy carve-out, and
target-repo recon + MODIFIED/REMOVED deltas — 408 words) moved verbatim
to the new references/consuming-a-change-folder.md, replaced by one
~85-word pointer paragraph carrying every pinned token (the join key,
`OOUX`, `MODIFIED`/`REMOVED`, `verbatim`) inline; the detection cascade,
the mandatory-once-bound rule, and the structural/critic-verdict
validator gates were left untouched per test_writing_plans_change_binding.py
and test_writing_plans_verdict_gate.py's section-anchored pins. New
count 4232, 188 under the cap. Before the round-1 raise to 4420 by the
2026-08-18
onramp-explicit-choice-gate arc's Task 9 (the §On-ramp choice gate
paragraph in §Self-review, mirroring the Open-questions gate paragraph
it sits under; new count 4409), and before that by the 2026-08-14
language-layering arc's T1 (the §Language policy section + the §Progress
surface reword reference; new count 4312), and before that TWICE by the
2026-08-13 brief-item-addressability arc: 4220 -> 4250 for T8's fix round
(the gate's reachability pointer in §Self-review, where a brief-only author
acts), and before that 4210 -> 4220 by the same arc (coverage gate learns
brief mode; the docstring had also drifted, still saying 4200 after the
08-12 raise to 4210), and before that from 4099 by the 2026-08-11
review-cost-reduction arc's misroute fix (plan-document-reviewer routing
substitution-proofing: §Self-review prompt-file/no-substitution/model-default
sentences + SUBAGENT-STOP disambiguation; new count 4134; prior raises
4047 → 4099 by the 2026-08-10 cheap-hardening-batch arc, 4023 → 4047 by the
2026-08-06 progress-card-roadmap-view arc, 3900 → 4023 by the 2026-08-06
progress-cards-and-plan-ledger arc). §Amending a PASS plan (MUST NOT MOVE, including
its exactly-3-item closed list — pinned separately by
test_post_pass_amendment_gate.py) and the splitting framework are
untouched anti-vacuous survivors.
"""
import re
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "writing-plans"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"


def _norm(text: str) -> str:
    """Whitespace-normalize for robust substring checks."""
    return re.sub(r"\s+", " ", text).strip()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill_text() -> str:
    return _read(SKILL_MD)


# --- (a) pointer/residue lines present in SKILL.md -------------------------

def test_cross_skill_map_pointer_present():
    assert "references/cross-skill-map.md" in _skill_text()


def test_red_flags_pointer_present():
    assert "references/red-flags.md" in _skill_text()


def test_design_evidence_pointer_present():
    assert "references/design-evidence.md" in _skill_text()


# --- (b) moved section headings absent from SKILL.md, present in destinations (A1 + A2) ---

def test_cross_skill_contract_heading_absent_from_skill_present_in_reference():
    assert "## Cross-skill contract" not in _skill_text()
    dest = _read(REFERENCES / "cross-skill-map.md")
    assert "Cross-skill contract" in dest
    assert "**Upstream**" in dest and "`brainstorming`" in dest


def test_what_skill_does_not_do_heading_absent_from_skill_present_in_reference():
    assert "## What this skill does NOT do" not in _skill_text()
    dest = _read(REFERENCES / "cross-skill-map.md")
    assert "What this skill does NOT do" in dest
    assert "Does **not** write code" in dest


# --- (c) Red Flags: pilot house shape — heading + distillation STAY, table moves ---

def test_red_flags_table_absent_from_skill_present_in_reference():
    marker = '"Just skip planning, the brief is enough."'
    assert marker not in _skill_text()
    dest = _read(REFERENCES / "red-flags.md")
    assert marker in dest
    assert "「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」" in dest
    # house shape (requesting-code-review pilot): the heading itself stays
    assert "## Red Flags — refuse these rationalizations" in _skill_text()


# --- (d) A4 maintainer fragments absent from SKILL.md, present in design-evidence.md ---

def test_beck_quote_absent_from_skill_present_in_design_evidence():
    fragment = "When you are working on a test and it gets too big"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_why_depth_evidence_absent_from_skill_present_in_design_evidence():
    fragment = "a depth-5 chain at ~95% per-step reliability succeeds only ~77% of the time"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_industry_precedent_parenthetical_absent_from_skill_present_in_design_evidence():
    fragment = "spec-kit, OpenSpec, Jira smart commits"
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_d8_mirror_sentence_absent_from_skill_present_in_design_evidence():
    fragment = 'mirrors `code-reviewer.md`\'s D8 "Activation is self-derived" anchor pattern'
    assert fragment not in _skill_text()
    dest = _read(REFERENCES / "design-evidence.md")
    assert fragment in dest


def test_design_evidence_header_states_author_facing_no_runtime_load():
    dest_norm = _norm(_read(REFERENCES / "design-evidence.md"))
    assert "author-facing" in dest_norm
    assert "do NOT load this file at runtime" in dest_norm


# --- (e) pinned survivors still inline in SKILL.md (anti-vacuous positives) ---

def test_amending_a_pass_plan_still_inline():
    text = _skill_text()
    assert "**Amending a PASS plan:**" in text
    # its exactly-3-item closed list must survive untouched
    assert "**Stamping the verdict**" in text
    assert "**Fixing a typo**" in text
    assert "**Filling a schema field**" in text


def test_splitting_framework_heading_still_inline():
    assert "## The splitting framework" in _skill_text()


def test_blocked_fallback_five_step_process_and_anti_pattern_stay_inline():
    text = _skill_text()
    assert "Applies the splitting framework to produce **child tasks**" in text
    assert "**Anti-pattern**" in text


def test_consuming_section_and_detection_rule_sentences_stay_inline():
    text = _skill_text()
    assert "## Consuming a loom-design change-folder" in text
    assert "git rev-parse --show-toplevel" in text
    assert "resolve the target repo's root" in text


def test_plan_size_ceiling_core_rule_stays_inline():
    text = _skill_text()
    assert "critical-path **depth**" in text
    assert "Route back to brainstorming" in text


# --- (g) progress surface — emit duty + plan-PASS card (2026-08-06 arc) -----

def test_progress_surface_lead_phrase_present():
    assert "**Progress surface.**" in _skill_text()


def test_plan_card_command_string_present():
    assert "python3 scripts/plan_card.py" in _skill_text()


def test_fire_and_continue_clause_present():
    assert "fire-and-continue, not a new pause" in _norm(_skill_text())


def test_family_relay_progress_card_pointer_present():
    assert (
        "loom-code/hooks/family-relay.md §(a2) Progress card"
        in _norm(_skill_text())
    )


def test_inline_fallback_field_list_present():
    assert (
        "render the four fields inline: goal, task table, stage, next"
        in _norm(_skill_text())
    )


def test_progress_surface_steps_and_gloss_emit_duty_present():
    # N2 clause (2026-08-06 progress-card-roadmap-view arc): plan-time
    # emission of Steps titles + Gloss lines, in the user's language.
    # 2026-08-14 language-layering arc: the per-field statement now
    # references the umbrella §Language policy (BI-7 consolidation,
    # reworded not deleted).
    norm = _norm(_skill_text())
    assert (
        "an optional `Steps:` title block, and per-task `Gloss:` lines"
        in norm
    )
    assert (
        "Steps titles and Gloss lines are written at plan time in the "
        "user's conversation language per §Language policy" in norm
    )


# --- (g1) layered language policy (2026-08-14 language-layering arc) --------

def test_layered_language_policy_declared():
    # BI-1 + BI-4 (2026-08-14 language-layering arc): the plan document
    # is written in two layers — Description/Acceptance in English, the
    # human-facing fields in the conversation language — and
    # adjudication-view is cited as the display layer for careful
    # reading of the English precision content in zh-Hant/ja.
    norm = _norm(_skill_text())
    assert "## Language policy" in _skill_text()
    assert (
        "**Description** bodies and **Acceptance** (RED/GREEN) are "
        "written in English" in norm
    )
    assert (
        "**Steps** titles, **Gloss**, **Goal**, task titles, and "
        "**Notes** stay in the session's conversation language" in norm
    )
    assert "adjudication-view" in norm
    assert "zh-Hant/ja" in norm


def test_minimal_structure_block_carries_progress_schema_lines():
    text = _skill_text()
    assert "Goal: <one sentence transcribed from the brief" in _norm(text)
    assert "Stage: planning" in text
    assert "- Status: pending" in text


# --- (h) NEEDS_REVISION loop self-screens the revision delta (2026-08-10) ----

def test_needs_revision_loop_self_screens_the_revision_delta():
    # 2026-08-10 cheap-hardening-batch arc: three consecutive arcs'
    # round-2 findings were defects the round-2 revision itself
    # introduced (n>=8) — the loop must self-screen the revision delta
    # before re-dispatching the reviewer.
    norm = _norm(_skill_text())
    # the pinned loop sentence stays intact (anti-splice guard)
    assert (
        "If reviewer returns `NEEDS_REVISION`, writing-plans "
        "**fixes the plan** and re-runs the reviewer." in norm
    )
    # the new duty is its own sentence in the same loop context; the
    # reference matches the actual label at the Pre-patch paragraph
    # (quality-review 🟡 2026-08-10: a §-ref to a nonexistent label)
    assert (
        "re-run the **Pre-patch before dispatch** self-screen on the "
        "revision delta itself" in norm
    )
    assert "every line the fix added or changed" in norm


# --- (i) the coverage gate names brief mode (2026-08-13) --------------------

_GATE_LEAD = "**Coverage self-check"

# A scope-restricting token. A sentence carrying one of these AND naming the
# change-folder is asserting this gate is change-folder-only, which brief
# mode falsifies. The pin is an ABSENCE over the WHOLE sliced paragraph
# rather than a named sentence to fix, because the claim sat on TWO
# sentences — the bold lead-in and the body — and an earlier revision of
# this change fixed the lead-in and left the body asserting the same
# falsehood.
_SCOPE_RESTRICTIONS = ("only", "not apply", "no change-folder")


_GATE_SECTION_HEADING = "\n## Consuming a loom-design change-folder"


def _coverage_gate_paragraph() -> str:
    """The coverage-self-check paragraph, sliced from its bold lead-in to the
    next blank line, ANCHORED INSIDE the section that owns it.

    Slicing binds PLACEMENT, not vocabulary: a duty relocated intact into a
    neighbouring paragraph leaves this slice and fails the pin.

    The anchor is the owning section's heading, not the file-wide first
    occurrence of the lead-in: §Self-review sits ABOVE this section and
    legitimately mentions the gate, so a file-wide `index` re-anchors onto
    any bolded mention above and validates text the shipped paragraph never
    earned. Last-occurrence would also dodge that decoy, but it is rejected
    because it fails SILENTLY — it would follow a second gate paragraph
    added below, exactly the class of bug this fix removes. The heading
    anchor fails LOUDLY when the document is restructured.
    """
    assert _GATE_SECTION_HEADING in _skill_text(), (
        f"cannot locate the section {_GATE_SECTION_HEADING.strip()!r} that "
        "owns the coverage-gate paragraph — if it was renamed or moved, "
        "re-point _GATE_SECTION_HEADING at its new heading text"
    )
    section = _section(_GATE_SECTION_HEADING)
    assert _GATE_LEAD in section, (
        f"the section {_GATE_SECTION_HEADING.strip()!r} carries no "
        f"{_GATE_LEAD!r} lead-in — the coverage-gate paragraph has left the "
        "section that owns it"
    )
    start = section.index(_GATE_LEAD)
    end = section.index("\n\n", start)
    return _norm(section[start:end])


def _sentences(paragraph: str) -> list[str]:
    return [s for s in re.split(r"(?<=\.)\s+", paragraph) if s]


def test_brief_mode_coverage_gate_is_named():
    para = _coverage_gate_paragraph()

    # (1) brief mode is named in this paragraph, in its own sentence, with
    # the shipped `--brief` invocation form, the reviewer-dispatch ordering,
    # and the blocking condition brief mode ACTUALLY carries.
    #
    # This assertion previously required the word "non-zero" and its comment
    # claimed brief mode blocks by "the same rule the change-folder mode
    # carries". Whole-branch review falsified that against the code: brief
    # mode's exit 1 fires for an unresolvable citation only, while an id no
    # task cites is warned and the run still exits 0. The pin was therefore
    # holding a false statement in place — a passing test guaranteeing the
    # prose stayed wrong. Strengthened rather than dropped: it now pins the
    # distinction itself, so prose that re-flattens the two gates into one
    # rule fails here.
    brief_sentences = [s for s in _sentences(para) if "--brief" in s]
    assert len(brief_sentences) == 1, (
        "the coverage-gate paragraph must name brief mode in exactly one "
        f"sentence of its own; found {len(brief_sentences)}"
    )
    sentence = brief_sentences[0]
    assert "BI-" in sentence
    assert "brief mode" in sentence.lower()
    assert "plan-document-reviewer" in sentence
    assert "unresolvable" in sentence.lower(), (
        "the brief-mode sentence must name the condition that actually "
        "blocks (an unresolvable citation), not a generic non-zero exit"
    )
    assert "uncovered" in sentence.lower(), (
        "the brief-mode sentence must also say what does NOT block — an "
        "uncovered id only warns — or a reader infers the change-folder "
        "path's stronger rule applies here too"
    )

    # (2) and no sentence in the same paragraph still restricts the check to
    # the change-folder input path.
    offenders = [
        s for s in _sentences(para)
        if "change-folder" in s.lower()
        and any(token in s.lower() for token in _SCOPE_RESTRICTIONS)
    ]
    assert not offenders, (
        "the coverage-gate paragraph still restricts the check to the "
        f"change-folder input path: {offenders}"
    )


# --- (i1) the slice cannot be captured by a decoy above it -----------------

# A synthetic SKILL.md in which §Self-review carries a paragraph satisfying
# every substring `test_brief_mode_coverage_gate_is_named` checks for, while
# the REAL gate paragraph — in the section that owns it — violates the pin.
# A file-wide first-occurrence anchor validates the decoy and reports a pass
# the shipped text has not earned. Reproduced live on this branch: T8's own
# fix round bolded a §Self-review mention and the pin followed it.
_DECOY_DOC = """# writing-plans

## Self-review — plan-document-reviewer

**Coverage self-check.** When the brief declares `BI-` ids, run the script \
in brief mode — `python3 check_scenario_coverage.py --brief <brief> <plan>` \
— before the plan-document-reviewer dispatch, blocking on a non-zero exit.

Other self-review prose.

## Consuming a loom-design change-folder

**Coverage self-check.** After producing the plan, run the script. It applies \
only to a change-folder input.

Trailing section prose.
"""


def _patched_skill_text(monkeypatch, doc: str) -> None:
    monkeypatch.setattr(sys.modules[__name__], "_skill_text", lambda: doc)


def test_decoy_paragraph_above_the_gate_cannot_capture_the_pin(monkeypatch):
    """The production pin — not a helper stand-in — must reject the decoy.

    `test_brief_mode_coverage_gate_is_named` is invoked directly so the
    assertion under test is the shipped one.
    """
    _patched_skill_text(monkeypatch, _DECOY_DOC)

    # sanity: the decoy really does carry everything the pin checks for, so a
    # pass here would come from the decoy and not from the real paragraph.
    decoy = _norm(_DECOY_DOC[_DECOY_DOC.index(_GATE_LEAD):])
    for token in ("--brief", "BI-", "brief mode", "plan-document-reviewer",
                  "non-zero"):
        assert token in decoy

    with pytest.raises(AssertionError):
        test_brief_mode_coverage_gate_is_named()


def test_renamed_owning_section_fails_loudly_not_silently(monkeypatch):
    """Restructure probe: the anchor's whole point is WHICH failure it picks.

    Renaming the owning section must name the heading it could not find,
    not silently re-slice whatever `**Coverage self-check` appears first.
    """
    _patched_skill_text(
        monkeypatch,
        _DECOY_DOC.replace(
            "## Consuming a loom-design change-folder",
            "## Consuming a loom-design spec-folder",
        ),
    )

    with pytest.raises(AssertionError) as excinfo:
        _coverage_gate_paragraph()
    assert "Consuming a loom-design change-folder" in str(excinfo.value)


def test_gate_paragraph_missing_from_its_section_fails_loudly(monkeypatch):
    """The complementary restructure: heading intact, paragraph moved away."""
    _patched_skill_text(
        monkeypatch,
        _DECOY_DOC.replace(
            "**Coverage self-check.** After producing the plan, run the "
            "script. It applies only to a change-folder input.",
            "Only unrelated prose lives here now.",
        ),
    )

    with pytest.raises(AssertionError) as excinfo:
        _coverage_gate_paragraph()
    assert _GATE_LEAD in str(excinfo.value)


# --- (i2) the brief-mode duty is reachable from the brief-only path ---------

_SELF_REVIEW_HEADING = "\n## Self-review"


def _section(heading: str) -> str:
    """The slice from `heading` to the next top-level `## ` heading.

    Slicing is the point: this pin asserts REACHABILITY, i.e. that the
    pointer sits in the section the acting author is actually reading at
    the moment of the reviewer dispatch. A pointer parked anywhere else in
    the file leaves this slice and fails.
    """
    text = _skill_text()
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:len(text) if nxt == -1 else nxt]


def test_coverage_gate_reachable_from_self_review():
    """A brief-only author never opens §Consuming a loom-design change-folder,
    so the brief-mode coverage duty must be reachable from §Self-review —
    where the plan-document-reviewer dispatch it gates is described.

    The pointer's TARGET is resolved from the pointer's own text, not
    hardcoded here: a pointer aimed at the wrong section fails because the
    gate is not found there.
    """
    self_review = _norm(_section(_SELF_REVIEW_HEADING))

    pointers = [s for s in _sentences(self_review) if _GATE_LEAD[2:] in s]
    assert len(pointers) == 1, (
        "§Self-review must carry exactly one pointer to the Coverage "
        f"self-check; found {len(pointers)}"
    )
    pointer = pointers[0]

    # the duty it makes reachable is the BRIEF-mode one, with the shipped
    # invocation form and the gate ordering that binds it to this dispatch.
    assert "--brief" in pointer
    assert "brief mode" in pointer.lower()
    assert "before dispatching the reviewer" in pointer.lower()

    # follow the pointer: the section it names must exist and must be where
    # the gate paragraph actually lives.
    target = re.search(r"§([^—]+?)\s+—", pointer)
    assert target, f"the pointer names no resolvable §section: {pointer}"
    heading = "\n## " + target.group(1).strip()
    assert heading in _skill_text(), (
        f"the pointer aims at {heading.strip()!r}, which is not a section "
        "of this SKILL.md"
    )
    assert _GATE_LEAD in _section(heading), (
        f"the pointer aims at {heading.strip()!r}, but the coverage-gate "
        "paragraph does not live there"
    )


# --- (j) open-questions gate wired unconditionally (Task 4, 2026-08-13) -----

_OPEN_Q_GATE_LEAD = "**Open-questions gate"


def _open_questions_gate_paragraph() -> str:
    """The open-questions-gate paragraph, sliced from its bold lead-in to the
    next blank line, ANCHORED INSIDE §Self-review — the section that owns
    it. Same anchoring discipline as `_coverage_gate_paragraph`: a duty
    relocated intact into another section leaves this slice and fails the
    pin, rather than being silently re-found by a file-wide index."""
    text = _skill_text()
    assert _SELF_REVIEW_HEADING in text, (
        f"cannot locate the section {_SELF_REVIEW_HEADING.strip()!r} that "
        "owns the open-questions-gate paragraph — if it was renamed or "
        "moved, re-point _SELF_REVIEW_HEADING at its new heading text"
    )
    section = _section(_SELF_REVIEW_HEADING)
    assert _OPEN_Q_GATE_LEAD in section, (
        f"section {_SELF_REVIEW_HEADING.strip()!r} carries no "
        f"{_OPEN_Q_GATE_LEAD!r} lead-in — the open-questions-gate paragraph "
        "has left the section that owns it"
    )
    start = section.index(_OPEN_Q_GATE_LEAD)
    end = section.index("\n\n", start)
    return _norm(section[start:end])


def test_skill_wires_open_questions_gate_unconditionally():
    para = _open_questions_gate_paragraph()

    # (1) names the checker's full repo-root-relative invocation, not a
    # bare basename — same reasoning as the finishing-a-development-branch
    # sibling row's own test (`test_finishing_open_questions_gate.py`):
    # a bare basename is satisfiable by any path prefix
    # (loom-design/scripts/, tools/scripts/, ../scripts/).
    assert "python3 loom-code/scripts/check_open_questions.py" in para

    # (2) states the gate runs on every plan — UNCONDITIONAL, unlike the two
    # existing check_scenario_coverage.py invocations (SKILL.md:253), both
    # of which fire only under a condition (a bound change-folder / a brief
    # declaring `BI-` ids). A gate paragraph that reintroduces either
    # condition is the exact regression this pin exists to catch.
    assert "every plan" in para.lower(), (
        "the open-questions gate must state it runs on every plan"
    )
    assert "change-folder" not in para.lower(), (
        "the open-questions gate paragraph must not gate on a change-folder "
        "condition — that would make it conditional, like the coverage gate"
    )
    assert "bi-" not in para.lower(), (
        "the open-questions gate paragraph must not gate on the brief "
        "declaring BI- ids — that would make it conditional, like the "
        "coverage gate's brief mode"
    )

    # (3) a non-zero exit blocks the plan from PASS
    assert "non-zero" in para.lower()
    assert "blocks the plan from pass" in para.lower()

    # (4) exactly one such paragraph — not duplicated across sections, and
    # not satisfiable by a decoy mention elsewhere in the file.
    assert _skill_text().count(_OPEN_Q_GATE_LEAD) == 1


def test_open_questions_gate_relocated_out_of_self_review_fails_loudly(monkeypatch):
    """Reachability, not just wording: the paragraph pinned above must live
    in §Self-review — where the plan-document-reviewer dispatch it gates is
    described — not merely somewhere, anywhere, in the file.

    Reproduces the reviewer's exact mutation: relocate the whole gate
    paragraph out of §Self-review into §Consuming a loom-design change-folder,
    leaving its wording, and file-wide uniqueness, untouched. A file-wide
    `index` on `_OPEN_Q_GATE_LEAD` would still find it and pass; anchoring
    the slice to §Self-review must not.
    """
    original = _skill_text()
    start = original.index(_OPEN_Q_GATE_LEAD)
    end = original.index("\n\n", start) + 2
    paragraph = original[start:end]
    relocated = original[:start] + original[end:]

    anchor = "\n## Consuming a loom-design change-folder\n"
    assert relocated.count(anchor) == 1
    insert_at = relocated.index(anchor) + len(anchor)
    relocated = relocated[:insert_at] + paragraph + relocated[insert_at:]

    # sanity: wording and file-wide uniqueness both survive the mutation —
    # this must be a placement failure, not a wording one.
    assert relocated.count(_OPEN_Q_GATE_LEAD) == 1

    _patched_skill_text(monkeypatch, relocated)

    assert _OPEN_Q_GATE_LEAD not in _section(_SELF_REVIEW_HEADING)

    with pytest.raises(AssertionError) as excinfo:
        _open_questions_gate_paragraph()
    assert "left the section that owns it" in str(excinfo.value)


def test_open_questions_gate_owning_heading_missing_fails_loudly(monkeypatch):
    """Complementary restructure: the paragraph stays put, but §Self-review's
    heading itself is renamed/removed. The anchor must fail LOUDLY, naming
    the missing section — not silently fall back to a file-wide slice."""
    original = _skill_text()
    mutated = original.replace(
        "## Self-review — plan-document-reviewer",
        "## Wrapping up before dispatch",
    )
    assert mutated != original

    _patched_skill_text(monkeypatch, mutated)

    with pytest.raises(AssertionError) as excinfo:
        _open_questions_gate_paragraph()
    assert _SELF_REVIEW_HEADING.strip() in str(excinfo.value)


# --- (f) word cap ------------------------------------------------------------

def test_word_count_at_most_4430():
    word_count = len(_skill_text().split())
    assert word_count <= 4430, (
        f"SKILL.md is {word_count} words, over the 4430 cap. "
        "Raised from 4420 by the 2026-08-21 dissolve-direction-layer "
        "arc's round-4 review fix: the §Queue-relation gate paragraph's "
        "exit-1 clause named two causes while the shipped script had "
        "four — the round-3 fix guarded main()'s store and brief reads, "
        "and each guard is its own exit-1 cause with its own remedy. "
        "Compressed twice before raising; it cannot lose the "
        "store-absent distinction without reintroducing the fail-open "
        "reading the guard exists to prevent. Prior accounting: the "
        "2026-08-19 field-value-microstructure arc's Task 11 (the "
        "§Field-microstructure gate paragraph, mirroring the "
        "Open-questions gate paragraph it sits directly under in "
        "§Self-review) tried to fit under this cap on revision and could "
        "not: compressed to its practical floor (91 words — two "
        "invocation-mode timings, the exit-1/exit-2 distinction, a "
        "negation-resistant blocking clause, and the brief-authorship "
        "answer, each pinned and none droppable) it still leaves the file "
        "90 words over. Left failing deliberately — see "
        "docs/loom/plans/2026-08-19-field-value-microstructure.md Task 11 "
        "revision round 1 for the full accounting — rather than raised a "
        "sixth time with no compression round behind it; prior raise from "
        "4350 by the 2026-08-18 "
        "onramp-explicit-choice-gate arc's Task 9 — the §On-ramp choice gate "
        "paragraph, mirroring the Open-questions gate paragraph it sits "
        "directly under in §Self-review; untrimmable without dropping the "
        "checker invocation, the STOP directive, or the git-guard.py "
        "cross-reference; prior raise from 4250 by the 2026-08-14 "
        "language-layering "
        "arc's T1: the §Language policy section + the §Progress surface "
        "reword reference — the policy is untrimmable without dropping "
        "the layered statement or the adjudication-view citation; prior "
        "raise from 4220 by the 2026-08-13 brief-item-addressability "
        "arc's T8 fix round: the gate's reachability pointer in §Self-review "
        "— a duty stated only under §Consuming a loom-design change-folder is "
        "unreachable from the brief-only path, and relocating the gate "
        "paragraph instead would drag the change-folder mechanics with it; "
        "SECOND raise in one arc, deliberate — flagged for the reviewer "
        "rather than resolved by shrinking the contract; prior raise from "
        "4210 by the same arc's T8: the coverage gate's brief-mode "
        "sentence, net +11 after "
        "deleting the two change-folder-only claims it falsifies — the "
        "duty is untrimmable without dropping either the `--brief` form "
        "or the gate order; prior raise from 4200 by the 2026-08-12 "
        "adjudication-view "
        "arc's T10 document-view pointer sentences at the kickoff "
        "briefing and post-PASS card relay — pointer-not-copy, "
        "untrimmable without losing the duty; prior raise from 4099 "
        "by the 2026-08-11 review-cost-reduction "
        "arc's misroute fix — §Self-review prompt-file/no-substitution/"
        "model-default sentences + SUBAGENT-STOP disambiguation; prior "
        "raises 4047 -> 4099 by the 2026-08-10 cheap-hardening-batch arc, "
        "4023 -> 4047 by the 2026-08-06 progress-card-roadmap-view arc)"
    )
