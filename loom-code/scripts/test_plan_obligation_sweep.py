"""Structural grep-test for Task 3 (plan-stage fact grounding brief, item 4).

This is a prompt/contract edit, not executable code, so there is nothing to
unit-test in the usual sense. Per the repo's established prose-artifact RED
convention (see test_writing_plans_verdict_gate.py /
test_sdd_review_weight_marker.py), correctness is asserted as the presence of
load-bearing *phrases* — tolerant of wording variation — because the contract
is consumed by a reviewer subagent that reads prose, not code: if the phrase
is missing, a weak-tier reviewer has nothing to execute.

Task 3 amends Check 8 of plan-document-reviewer-prompt.md IN PLACE (no
renumbering — see docs/loom/memory/retire-numbered-checks-dont-renumber.md,
whose precedent is Check 5 in this same file). The third assertion below is
an append-only guard: it parses every numbered row in the checks table and
fails if Check 8's amendment introduced any number above the maximum this
table is expected to carry — proving that amendment happened in place
rather than appending a new check number.

`PRE_EXISTING_MAX_CHECK_NUMBER` is updated, not frozen at 16 forever: a
later, legitimately NEW check (Check 17, added by
docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md Task 3)
is an authorized append, not the renumbering-during-Check-8-edit regression
this guard exists to catch. The guard's job is "no *extra* numbers beyond
what the table is supposed to have," so the constant tracks the table's
current legitimate maximum.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PLAN_DOCUMENT_REVIEWER_PROMPT = (
    REPO_ROOT
    / "loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md"
)

# Current legitimate maximum check number in the table. Check 8's own
# amendment must not raise this further — it amends Check 8's row in place.
# Bumped 16 -> 17 when Check 17 (Reuse-adequacy) shipped, an authorized
# append, not a renumbering. Bumped 17 -> 18 when Check 18 (Open Questions
# gate) shipped (docs/loom/plans/2026-08-13-open-question-dispatch-gate.md
# Task 6), likewise an authorized append. Bumped 18 -> 19 when Check 19
# (field-value microstructure) shipped
# (docs/loom/plans/2026-08-19-field-value-microstructure.md Task 10),
# likewise an authorized append. Bumped 19 -> 20 when Check 20 (Seam
# field) shipped (docs/loom/plans/2026-08-25-seam-contracts.md Task 4),
# likewise an authorized append.
PRE_EXISTING_MAX_CHECK_NUMBER = 20


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_check8_sweeps_brief_obligations():
    """
    Check 8's row must, after this task:
      - carry the obligation-sweep instruction (brief item 4's own wording:
        "grep the brief for obligation sentences" ... "not covered by a
        task"), so a weak-tier reviewer has a literal action to run, not a
        judgment call.
      - define "obligation sentence" inline via a checkable marker list
        (e.g. modal-obligation words and deferred-verification phrases),
        so the reviewer can classify a sentence without judgment.
    And the checks table as a whole must show no renumbering: no row number
    exceeds the table's current legitimate maximum (18, since Check 18 shipped).
    """
    text = _read(PLAN_DOCUMENT_REVIEWER_PROMPT)

    row8_match = re.search(r"^\|\s*8\s*\|(.*)$", text, re.MULTILINE)
    assert row8_match, "expected a Check 8 row (`| 8 | ... |`) in the checks table"
    row8 = row8_match.group(1)

    assert "grep the brief for obligation sentences" in row8
    assert "not covered by a task" in row8

    assert "obligation sentence" in row8
    assert "obligation marker" in row8

    row_numbers = [
        int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|", text, re.MULTILINE)
    ]
    assert row_numbers, "expected at least one numbered row in the checks table"
    assert max(row_numbers) == PRE_EXISTING_MAX_CHECK_NUMBER, (
        f"checks table max row number is {max(row_numbers)}, expected "
        f"{PRE_EXISTING_MAX_CHECK_NUMBER} — Task 3 must amend Check 8 in "
        "place, not append a new check number"
    )
