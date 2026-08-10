"""Pointer-pin tests for the SDD Partition B extraction (Task 2 of
docs/loom/plans/2026-08-05-loom-skill-extraction-batch.md).

subagent-driven-development/SKILL.md sits at the CHK-SKL-010 wall
(4482 words). Partition B moves three zero-pin blocks whole behind
pointers:

  B1. Environment hygiene (bold-lead) -> APPEND to the existing
      references/dispatch-hygiene-notes.md as a new "## Environment
      hygiene" section; residue = one pointer line in SKILL.md.
  B2. Progress ledger + Decision Log maintenance (two bold-leads) ->
      new references/plan-ledger-notes.md, each reproduced as its own
      H2 heading carrying the identical lead phrase; residue = one
      pointer line each in SKILL.md.
  B3. Definition of Done -- command-surface accretion (H2 heading,
      full body) -> new references/command-surface-accretion.md;
      residue = the H2 heading stays inline (Red-Flags-style, not
      Cross-skill-contract-style) with a ~30w core-rule stub + pointer.

HEADING-SHAPE caveat (plan Notes): "Progress ledger" and "Decision Log
maintenance" are BOLD-PARAGRAPH LEADS in the source, not `^##`
headings -- this file pins the lead PHRASES (whitespace-normalized
substring match), never a heading-anchored regex, so a bold lead
reproduced as an H2 in the destination still counts as "identical."

Assertions are whitespace-normalized and read with encoding="utf-8"
throughout. Anti-vacuous positives prove this file is reading real
content, not vacuously passing: the Mechanical review-weight
exemption's part-3 "Suite green" sentence and the Prose review-weight
substitution bold lead must still be inline in SKILL.md (both are
MUST NOT MOVE per the brief's Partition B).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SDD_SKILL = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)
DISPATCH_HYGIENE_NOTES = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "references"
    / "dispatch-hygiene-notes.md"
)
PLAN_LEDGER_NOTES = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "references"
    / "plan-ledger-notes.md"
)
COMMAND_SURFACE_ACCRETION = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "references"
    / "command-surface-accretion.md"
)
ENVIRONMENT_GOTCHAS = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "using-loom-code"
    / "references"
    / "environment-gotchas.md"
)

# Raised deliberately 4130 -> 4175 by the 2026-08-10 ship-progress-tooling
# arc, Task 2: two plugin-fallback cascade sentences (Delivery form +
# Progress ledger) so external repos resolve the plugin-shipped
# plan_card.py instead of degrading to hand-edits.
WORD_CEILING = 4175

# --- distinctive phrases, whitespace-normalized ---------------------------

# B1: the four Environment hygiene bullets' distinctive openers.
ENV_HYGIENE_BULLET_1 = (
    "Prefix every `pytest` invocation with `PYTHONDONTWRITEBYTECODE=1`"
)
ENV_HYGIENE_BULLET_2 = "Resolve `git worktree add` paths from the **repo root**"
ENV_HYGIENE_BULLET_4 = (
    "run `git status --short` and confirm **only that task's files are staged**"
)
ENV_HYGIENE_HEADING = "## Environment hygiene"

# B2: distinctive tails only present in the FULL bold-lead sentences (the
# residue pointers below are deliberately shorter and omit these tails).
PROGRESS_LEDGER_FULL_LEAD = (
    "maintain `Status` per task + resume from it "
    "(v0.10.0+; default-on since v0.60.0 — old plans opt-in by presence)"
)
DECISION_LOG_FULL_LEAD_TAIL = (
    "an agent-decided engineering choice that was classified by the "
    "§Asking the user two-axis test"
)
PROGRESS_LEDGER_HEADING = (
    "## Progress ledger — maintain `Status` per task + resume from it "
    "(v0.10.0+; default-on since v0.60.0 — old plans opt-in by presence)"
)
DECISION_LOG_HEADING = "## Decision Log maintenance — append during execution"
RESUME_AFTER_INTERRUPTION_LEAD = "**Resume after interruption:**"

# B3: distinctive full-body paragraphs.
DOD_EVENT_DRIVEN_LEAD = "**Event-driven — not per-task polling.**"
DOD_MECHANICS_LEAD = "**Mechanics.**"
DOD_HEADING = "## Definition of Done — command-surface accretion"

# Residue pointer lines expected in SKILL.md after extraction.
ENV_HYGIENE_RESIDUE_POINTER = (
    "[`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) "
    "§Environment hygiene"
)
PROGRESS_LEDGER_RESIDUE_POINTER = (
    "[`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) "
    "§Progress ledger"
)
DECISION_LOG_RESIDUE_POINTER = (
    "[`references/plan-ledger-notes.md`](references/plan-ledger-notes.md) "
    "§Decision Log maintenance"
)
COMMAND_SURFACE_RESIDUE_POINTER = (
    "[`references/command-surface-accretion.md`](references/command-surface-accretion.md)"
)

# Anti-vacuous positives -- MUST NOT MOVE, so still inline in SKILL.md.
MECHANICAL_PART_3_SENTENCE = (
    "3. **Suite green.** Run the resolved package test command after "
    "the task's commit; any failure fails the self-check — a "
    "mechanical edit can redden a file no task touches (live case: a "
    "version bump vs the shipping-version pin test)."
)
PROSE_SUBSTITUTION_LEAD = "**Prose review-weight substitution.**"

# Duplicate-avoidance: B1's push+PR bullet must cross-reference
# environment-gotchas.md's S2(a), not restate it wholesale.
ENV_GOTCHAS_S2A_DISTINCTIVE = (
    "Issue the branch push and `gh pr create` as two separate Bash calls."
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _norm(path: Path) -> str:
    return _normalize_ws(_read(path))


# --- anti-vacuous positives (run first; prove the SSOT itself is intact) --


def test_anti_vacuous_mechanical_part_3_sentence_still_inline():
    assert _normalize_ws(MECHANICAL_PART_3_SENTENCE) in _norm(SDD_SKILL)


def test_anti_vacuous_prose_substitution_lead_still_inline():
    assert PROSE_SUBSTITUTION_LEAD in _norm(SDD_SKILL)


# --- B1: Environment hygiene -----------------------------------------------


def test_environment_hygiene_bullets_absent_from_skill_md():
    text = _norm(SDD_SKILL)
    assert ENV_HYGIENE_BULLET_1 not in text
    assert ENV_HYGIENE_BULLET_2 not in text
    assert ENV_HYGIENE_BULLET_4 not in text


def test_environment_hygiene_residue_pointer_present_in_skill_md():
    assert ENV_HYGIENE_RESIDUE_POINTER in _norm(SDD_SKILL)


def test_environment_hygiene_section_present_in_dispatch_hygiene_notes():
    text = _norm(DISPATCH_HYGIENE_NOTES)
    assert ENV_HYGIENE_HEADING in text
    assert ENV_HYGIENE_BULLET_1 in text
    assert ENV_HYGIENE_BULLET_2 in text
    assert ENV_HYGIENE_BULLET_4 in text


def test_dispatch_hygiene_notes_preamble_names_environment_hygiene():
    """The preamble's section-kind sentence must be updated to cover the
    new standing-guidance section (it enumerates §Capacity-error
    recovery and §Worktree-isolated reviewer dispatch by name today)."""
    text = _norm(DISPATCH_HYGIENE_NOTES)
    assert "§Environment hygiene" in text.split("## Environment hygiene")[0], (
        "preamble (text before the new heading) must name "
        "§Environment hygiene"
    )


def test_pinned_capacity_and_worktree_sections_undisturbed():
    """B1's append must not disturb the two pinned sections other tests
    pin: §Capacity-error recovery (test_rcr_capacity_pointer.py's target
    heading) and §Worktree-isolated reviewer dispatch (test_dispatch_
    hygiene_worktree_section.py)."""
    text = _norm(DISPATCH_HYGIENE_NOTES)
    assert "## Capacity-error recovery" in text
    assert "## Worktree-isolated reviewer dispatch" in text
    section_idx = text.find("## Worktree-isolated reviewer dispatch")
    worked_example_idx = text.find("## Worked example")
    assert section_idx != -1
    assert worked_example_idx != -1
    assert section_idx < worked_example_idx


def test_environment_hygiene_cross_references_not_duplicates_dcg_framing():
    """The push+PR bullet must cross-reference environment-gotchas.md's
    S2(a) instead of restating its dcg framing wholesale (brief:
    'cross-reference instead of duplicating any dcg framing already in
    environment-gotchas.md')."""
    notes_text = _norm(DISPATCH_HYGIENE_NOTES)
    assert "environment-gotchas.md" in notes_text
    assert "S2(a)" in notes_text
    assert ENV_GOTCHAS_S2A_DISTINCTIVE not in notes_text, (
        "must not restate environment-gotchas.md's S2(a) sentence verbatim"
    )
    # Positive control: the duplicate sentence actually exists over there,
    # proving this is a real cross-reference target, not a stale pointer.
    assert ENV_GOTCHAS_S2A_DISTINCTIVE in _norm(ENVIRONMENT_GOTCHAS)


# --- B2: Progress ledger + Decision Log maintenance -------------------------


def test_progress_ledger_full_lead_absent_from_skill_md():
    assert PROGRESS_LEDGER_FULL_LEAD not in _norm(SDD_SKILL)


def test_decision_log_full_lead_tail_absent_from_skill_md():
    assert DECISION_LOG_FULL_LEAD_TAIL not in _norm(SDD_SKILL)


def test_progress_ledger_and_decision_log_residue_pointers_present():
    text = _norm(SDD_SKILL)
    assert PROGRESS_LEDGER_RESIDUE_POINTER in text
    assert DECISION_LOG_RESIDUE_POINTER in text


def test_plan_ledger_notes_carries_identical_headings_and_bodies():
    text = _norm(PLAN_LEDGER_NOTES)
    assert PROGRESS_LEDGER_HEADING in text
    assert DECISION_LOG_HEADING in text
    assert PROGRESS_LEDGER_FULL_LEAD in text
    assert DECISION_LOG_FULL_LEAD_TAIL in text
    assert RESUME_AFTER_INTERRUPTION_LEAD in text


def test_plan_ledger_notes_progress_ledger_precedes_decision_log():
    text = _norm(PLAN_LEDGER_NOTES)
    progress_idx = text.find(PROGRESS_LEDGER_HEADING)
    decision_idx = text.find(DECISION_LOG_HEADING)
    assert progress_idx != -1
    assert decision_idx != -1
    assert progress_idx < decision_idx


def test_ledger_flip_names_the_writer():
    """T3(a) of the 2026-08-06 ledger-writer-and-plan-tooling-hardening
    arc: SKILL.md's Progress-ledger paragraph must name the deterministic
    ledger writer (`plan_card.py --set-status`) as the flip path and keep
    hand-editing as the script-absent fallback only — flip-by-hand caused
    two incidents (the 0.62.0 duplicate-Status field among them)."""
    text = _norm(SDD_SKILL)
    assert '--set-status "T<N>=<status>"' in text
    assert "hand-edit only when the script is absent" in text


# --- B3: Definition of Done -- command-surface accretion --------------------


def test_dod_full_paragraphs_absent_from_skill_md():
    text = _norm(SDD_SKILL)
    assert DOD_EVENT_DRIVEN_LEAD not in text
    assert DOD_MECHANICS_LEAD not in text


def test_dod_heading_and_core_rule_stub_stay_inline():
    """B3's residue keeps the H2 heading (Red-Flags-style: the concept
    stays visible in the body) plus a ~30w core-rule stub + pointer --
    unlike B1/B2's bold-leads, which drop to a bare pointer line."""
    text = _norm(SDD_SKILL)
    assert DOD_HEADING in text
    assert COMMAND_SURFACE_RESIDUE_POINTER in text
    assert "new runnable capability" in text
    assert "declared in the command surface" in text


def test_command_surface_accretion_file_carries_full_body():
    text = _norm(COMMAND_SURFACE_ACCRETION)
    assert DOD_EVENT_DRIVEN_LEAD in text
    assert DOD_MECHANICS_LEAD in text
    assert "new runnable capability" in text


def test_command_surface_accretion_implementer_links_resolve_one_level_deeper():
    """The moved body's two implementer.md links must be fixed from
    SKILL.md's `../../agents/implementer.md` to the reference file's
    one-level-deeper `../../../agents/implementer.md` (pilot lesson:
    fix relative links when prose moves one level deeper)."""
    text = _read(COMMAND_SURFACE_ACCRETION)
    assert "../../../agents/implementer.md" in text
    assert "](../../agents/implementer.md)" not in text
    target = (
        REPO_ROOT
        / "loom-code"
        / "skills"
        / "subagent-driven-development"
        / "references"
        / "../../../agents/implementer.md"
    ).resolve()
    assert target == (REPO_ROOT / "loom-code" / "agents" / "implementer.md")
    assert target.is_file()


# --- Dispatch-packet context (2026-08-06 dispatch-efficiency trio, T1) ------

DPC_HEADING = "## Dispatch-packet context"
DPC_RULE_A = (
    "anchored by verbatim string or stable heading — never by line number alone"
)
DPC_RULE_B_GUESS_LABEL = (
    "A statement without a named source is a guess and must be labeled as one"
)
DPC_RULE_B_PROVENANCE_MARKER = (
    "the checkable surface feature is the presence of a provenance marker, "
    "never the agent's self-assessment"
)
DPC_RULE_B_NON_GOVERNANCE = (
    "does not govern plan-format §Reuse-adequacy blocks, whose closed "
    "three-marker vocabulary stays authoritative there"
)
DPC_RULE_C_LOCATE_ARM = "dispatch a locate arm first"
DPC_RULE_C_STAY_HOME = (
    "never Read files into the main conversation just to quote them"
)
DPC_RULE_C_FILE_MAP_VALVE = "packets then carry only the path"
DPC_RULE_D = "claims-to-verify, never conclusions-to-adopt"
DPC_SKILL_POINTER = (
    "[`references/dispatch-hygiene-notes.md`](references/dispatch-hygiene-notes.md) "
    "§Dispatch-packet context"
)


def test_dispatch_packet_context_section():
    """T1 of docs/loom/plans/2026-08-06-dispatch-efficiency-trio.md: the
    notes file carries §Dispatch-packet context with the four rules'
    load-bearing phrases, the preamble enumeration names the new
    standing-guidance section, and SKILL.md's dispatch area carries ONE
    pointer sentence to it."""
    notes = _norm(DISPATCH_HYGIENE_NOTES)
    assert DPC_HEADING in notes
    # (a) string/heading anchors, never line numbers alone
    assert DPC_RULE_A in notes
    # (b) inline source provenance; unsourced = labeled guess (action-type
    # formulation), plus the §Reuse-adequacy non-governance sentence
    assert DPC_RULE_B_GUESS_LABEL in notes
    assert DPC_RULE_B_PROVENANCE_MARKER in notes
    assert DPC_RULE_B_NON_GOVERNANCE in notes
    # (c) consumer-count threshold + commander-stays-home + file-map valve
    assert DPC_RULE_C_LOCATE_ARM in notes
    assert DPC_RULE_C_STAY_HOME in notes
    assert DPC_RULE_C_FILE_MAP_VALVE in notes
    # (d) reviewer packets carry claims, never conclusions
    assert DPC_RULE_D in notes
    # preamble section-enumeration sentence must name the new section
    # (stale enumeration = falsified neighbor)
    assert "§Dispatch-packet context" in notes.split(DPC_HEADING)[0], (
        "preamble (text before the new heading) must name "
        "§Dispatch-packet context"
    )
    # SKILL.md pointer sentence in the dispatch area
    assert DPC_SKILL_POINTER in _norm(SDD_SKILL)


# --- word ceiling + destination-file existence ------------------------------


def test_skill_md_word_count_within_ceiling():
    word_count = len(_read(SDD_SKILL).split())
    assert word_count <= WORD_CEILING, (
        f"SKILL.md is {word_count} words, over the {WORD_CEILING} ceiling "
        "(raised deliberately 3974 -> 4015 by the 2026-08-06 "
        "ledger-writer-and-plan-tooling-hardening arc to admit the "
        "Progress-ledger flip-via-plan_card.py duty sentence; raised "
        "again 4015 -> 4130 by the 2026-08-08 progress-display-hardening "
        "arc to admit the Delivery-form ledger-action reword + Host "
        "todo mirror paragraph)"
    )


def test_all_three_destination_files_exist():
    assert DISPATCH_HYGIENE_NOTES.is_file()
    assert PLAN_LEDGER_NOTES.is_file()
    assert COMMAND_SURFACE_ACCRETION.is_file()
