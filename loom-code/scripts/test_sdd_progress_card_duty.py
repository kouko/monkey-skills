"""Pin tests for the SDD progress-card Delivery-form duty (Task 4 of
docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md).

The "**Delivery form.**" paragraph in
subagent-driven-development/SKILL.md §Asking the user is replaced with
the plan's pinned text N3: every per-wave status report, stage
transition, and checkpoint sign-off renders the progress card first
(`python3 scripts/plan_card.py <plan-path>`), the `Stage:` header is
updated in the same commit as that wave's ledger writes, and the
paragraph carries the family-relay pointer `§Family relay
discipline` (present once, per loom-pipeline/scripts/test_family_relay.py's
POINTER_PHRASE) and the progress-card variant `§(a2) Progress card`,
plus the inline-fallback field list. Fix round 2 (same day) removed the
second narration seam's duplicate of POINTER_PHRASE — the Status
handling seam now cross-references this Delivery-form paragraph by the
literal "the **Delivery form** paragraph above" instead, which is what
test_family_relay.py::test_sdd_pointer pins (see that test's docstring
for the rationale).

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

# N3's lead sentence (whitespace-normalized).
N3_LEAD = (
    "**Delivery form.** Every per-wave status report, stage transition, "
    "and checkpoint sign-off renders the progress card first"
)

# The fill-from-file command string.
COMMAND_STRING = "python3 scripts/plan_card.py <plan-path>"

# The Stage-update duty sentence.
STAGE_UPDATE_DUTY = (
    "Update the plan's `Stage:` header in the same commit as that "
    "wave's ledger writes."
)

# BOTH pointers (Gap-A invariant locally visible: the family-relay
# pointer phrase must survive the N3 replacement alongside the new
# progress-card variant pointer).
FAMILY_RELAY_POINTER = "family-relay.md §Family relay discipline"
PROGRESS_CARD_VARIANT_POINTER = "§(a2) Progress card"

# The inline-fallback field list (script or family-relay absent).
FALLBACK_FIELD_LIST = (
    "render the four fields inline: goal, task table, stage, next"
)

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


# --- N3 pins ----------------------------------------------------------------


def test_n3_lead_present():
    assert N3_LEAD in _norm(SDD_SKILL)


def test_plan_card_command_string_present():
    assert COMMAND_STRING in _norm(SDD_SKILL)


def test_stage_update_duty_present():
    assert STAGE_UPDATE_DUTY in _norm(SDD_SKILL)


def test_both_family_relay_pointers_present():
    text = _norm(SDD_SKILL)
    assert FAMILY_RELAY_POINTER in text
    assert PROGRESS_CARD_VARIANT_POINTER in text


def test_inline_fallback_field_list_present():
    assert FALLBACK_FIELD_LIST in _norm(SDD_SKILL)
