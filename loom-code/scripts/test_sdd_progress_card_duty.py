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

import pytest

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
# 2026-08-10 ship-progress-tooling whole-branch 🟡: "script absent"
# re-qualified as BOTH copies absent (repo-root shim + plugin-shipped),
# so the inline fallback can no longer be read as licensed while the
# plugin copy exists — property (two limbs) unchanged.
TWO_LIMB_TRIGGER = (
    "(family-relay absent, or both script copies absent → render the "
    "four fields inline"
)

# The script-absent duty clause — anchors the MUST-relay duty to the
# moments on the no-script path (per-wave/stage/checkpoint), so the
# duty does not evaporate when no ledger-action script runs.
SCRIPT_ABSENT_DUTY = (
    "when both copies are absent, the same relay duty binds directly at "
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


# --- Plugin-fallback cascade duty (ship-progress-tooling arc, Task 2) --------
#
# T1 moved plan_card.py / backlog_index.py into loom-code/scripts/ (plugin-
# shipped) with exec shims at the repo root. Every skill-body invocation must
# therefore carry the two-step resolution cascade: repo-root copy first, then
# the plugin-shipped copy via the `${CLAUDE_PLUGIN_ROOT}` load-time
# substitution. A paragraph (or table row) that invokes the script without
# naming the fallback silently degrades external repos to hand-editing.

CASCADE_SKILLS = [
    "subagent-driven-development",
    "writing-plans",
    "requesting-code-review",
    "brainstorming",
    "finishing-a-development-branch",
]

_TOOLING_INVOCATION_RE = re.compile(
    r"python3 scripts/(?:plan_card|backlog_index)\.py"
)
PLUGIN_FALLBACK = "${CLAUDE_PLUGIN_ROOT}/scripts/"


def _units(text: str) -> list[str]:
    """Paragraph-or-table-row units: blank-line-separated blocks, with
    table rows (lines starting with `|`) split out as individual units
    so one row's fallback cannot satisfy a neighboring row."""
    units: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        lines = block.splitlines()
        table_rows = [ln for ln in lines if ln.lstrip().startswith("|")]
        prose = "\n".join(
            ln for ln in lines if not ln.lstrip().startswith("|")
        )
        units.extend(table_rows)
        if prose.strip():
            units.append(prose)
    return units


@pytest.mark.parametrize("skill", CASCADE_SKILLS)
def test_every_tooling_invocation_unit_carries_plugin_fallback(skill):
    path = REPO_ROOT / "loom-code" / "skills" / skill / "SKILL.md"
    offenders = [
        unit
        for unit in _units(_read(path))
        if _TOOLING_INVOCATION_RE.search(unit)
        and PLUGIN_FALLBACK not in unit
    ]
    assert not offenders, (
        f"{skill}/SKILL.md: {len(offenders)} invocation unit(s) lack the "
        f"plugin fallback {PLUGIN_FALLBACK!r}:\n"
        + "\n---\n".join(u[:200] for u in offenders)
    )
