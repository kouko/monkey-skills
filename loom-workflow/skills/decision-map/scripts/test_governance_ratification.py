"""Governance ratification records for the Outcome Map v3 arc (R1).

The v3 arc shipped with an empty Decision Log and an un-ratified proposal
status. These tests pin the retroactive ratification trail so the merged
v3 contract has a signed decision record.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
# W3-03 moved the seven inherited repo-level stores under
# docs/loom/evidence/; the v3 proposal went with outcome-map-v3/.
PROPOSAL_MD = REPO_ROOT / "docs" / "loom" / "evidence" / "outcome-map-v3" / "proposal.md"
PLAN_MD = REPO_ROOT / "docs" / "loom" / "plans" / "2026-08-30-outcome-map-v3.md"

RATIFIED_LINE = "Status: ratified — kouko, 2026-08-31"
USER_RATIFIED = "user-ratified: kouko, 2026-08-31"


def _decision_log_section(plan_text: str) -> str:
    """The `## Decision Log` section body (excluding the heading and the
    next `## ` heading), or raises via the assert callers already make
    on a `None` match."""
    match = re.search(r"^## Decision Log\n(.*?)(?=\n## )", plan_text, re.S | re.M)
    assert match, "plan has no Decision Log section"
    return match.group(1)


def test_proposal_status_is_ratified():
    proposal = PROPOSAL_MD.read_text(encoding="utf-8")
    assert RATIFIED_LINE in proposal


def test_plan_decision_log_has_at_least_five_ratified_entries():
    plan = PLAN_MD.read_text(encoding="utf-8")
    section = _decision_log_section(plan)
    entries = re.findall(r"^### ", section, re.M)
    assert len(entries) >= 5
    assert section.count(USER_RATIFIED) >= 5


def test_each_decision_log_entry_carries_user_ratified_line():
    plan = PLAN_MD.read_text(encoding="utf-8")
    section = _decision_log_section(plan)
    entries = re.split(r"^### ", section, flags=re.M)[1:]
    assert len(entries) >= 5
    for entry in entries:
        assert USER_RATIFIED in entry, entry.splitlines()[0]
