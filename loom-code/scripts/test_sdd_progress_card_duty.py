"""Pin tests for the SDD progress-card Delivery-form duty (Task 4 of
docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md, reworded
by Task 2 of docs/loom/plans/2026-08-08-progress-display-hardening.md).

The "**Delivery form.**" paragraph in
subagent-driven-development/SKILL.md rebinds the render duty to the
mechanical ledger actions: `--set-status`/`--set-stage` print the card
themselves after the flip, and ANY turn that runs one of them must
relay the printed card. A new "**Host todo mirror.**" paragraph adds a
conditional, display-only projection onto the host's built-in task
tools (Claude Code) — the plan file's Status ledger stays the SSOT;
hosts without task tools skip silently.

Assertions are whitespace-normalized (encoding="utf-8"). The
positive-fact control pins the adjacent Worked-example sentence that
predates this arc, proving the file reads real content.
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

# The Delivery-form lead sentence (whitespace-normalized).
N3_LEAD = (
    "**Delivery form.** The ledger actions — "
    '`python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"`'
)

# The two ledger-action command strings that print the card.
COMMAND_STRING_STATUS = (
    'python3 scripts/plan_card.py <plan-path> --set-status "T<N>=<status>"'
)
COMMAND_STRING_STAGE = '--set-stage "<text>"'

# The MUST-relay duty bound to running either ledger action.
RELAY_DUTY = "ANY turn that runs one of these actions MUST relay that printed card"

# The mechanical-act binding sentence (per-wave/stage/checkpoint moments
# flip the ledger via the script, so the card rides them by construction).
STAGE_DUTY = (
    "Per-wave status reports, stage transitions, and checkpoint "
    "sign-offs flip the ledger via the script, so the card rides them "
    "by construction"
)

# BOTH pointers (Gap-A invariant locally visible: the family-relay
# pointer phrase must survive the reword alongside the progress-card
# variant pointer).
FAMILY_RELAY_POINTER = "family-relay.md §Family relay discipline"
PROGRESS_CARD_VARIANT_POINTER = "§(a2) Progress card"

# The inline-fallback field list (script absent).
FALLBACK_FIELD_LIST = (
    "render the four fields inline: goal, task table, stage, next"
)

# The two-limb fallback trigger — family-relay absence is a live
# conditional-plugin host state distinct from script absence; round-1
# narrowed this to one limb, dropping the family-relay-absent case.
TWO_LIMB_TRIGGER = "(family-relay or script absent → render the four fields inline"

# The script-absent duty clause — anchors the MUST-relay duty to the
# moments on the no-script path (per-wave/stage/checkpoint), so the
# duty does not evaporate when no ledger-action script runs.
SCRIPT_ABSENT_DUTY = (
    "when the script is absent, the same relay duty binds directly at "
    "per-wave status reports, stage transitions, and checkpoint "
    "sign-offs, with the inline four fields"
)

# The never-compose-from-memory rule.
NEVER_COMPOSE_RULE = (
    "The card re-reads the plan file by construction — never compose "
    "it from memory."
)

# --- Host todo mirror pins ---------------------------------------------

TODO_MIRROR_LEAD = "**Host todo mirror.**"

# The SSOT sentence — the mirror must not read as a second source of truth.
SSOT_SENTENCE = "the plan file's Status ledger stays the SSOT"

# The conditional posture — must not read as mandatory on hosts without
# task tools.
CONDITIONAL_POSTURE = "Hosts without task tools → skip silently"

# Positive-fact control — adjacent, pre-existing, untouched by this arc.
CONTROL_WORKED_EXAMPLE = (
    "**Worked example — the built-in `/recap` style is the target.**"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _norm(path: Path) -> str:
    return _normalize_ws(_read(path))


# --- positive-fact control (runs first; proves real content is read) -------


def test_control_worked_example_sentence_present():
    assert CONTROL_WORKED_EXAMPLE in _norm(SDD_SKILL)


# --- Delivery-form pins ------------------------------------------------------


def test_n3_lead_present():
    assert N3_LEAD in _norm(SDD_SKILL)


def test_plan_card_command_strings_present():
    text = _norm(SDD_SKILL)
    assert COMMAND_STRING_STATUS in text
    assert COMMAND_STRING_STAGE in text


def test_relay_duty_present():
    assert RELAY_DUTY in _norm(SDD_SKILL)


def test_stage_duty_present():
    assert STAGE_DUTY in _norm(SDD_SKILL)


def test_both_family_relay_pointers_present():
    text = _norm(SDD_SKILL)
    assert FAMILY_RELAY_POINTER in text
    assert PROGRESS_CARD_VARIANT_POINTER in text


def test_inline_fallback_field_list_present():
    assert FALLBACK_FIELD_LIST in _norm(SDD_SKILL)


def test_fallback_trigger_is_two_limbed():
    assert TWO_LIMB_TRIGGER in _norm(SDD_SKILL)


def test_script_absent_duty_present():
    assert SCRIPT_ABSENT_DUTY in _norm(SDD_SKILL)


def test_never_compose_rule_present():
    assert NEVER_COMPOSE_RULE in _norm(SDD_SKILL)


# --- Host todo mirror pins ---------------------------------------------------


def test_todo_mirror_lead_present():
    assert TODO_MIRROR_LEAD in _norm(SDD_SKILL)


def test_todo_mirror_ssot_sentence_present():
    assert SSOT_SENTENCE in _norm(SDD_SKILL)


def test_todo_mirror_conditional_posture_present():
    assert CONDITIONAL_POSTURE in _norm(SDD_SKILL)
