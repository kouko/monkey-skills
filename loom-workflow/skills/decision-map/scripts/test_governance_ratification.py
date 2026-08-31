"""Governance ratification records for the Outcome Map v3 arc (R1).

The v3 arc shipped with an empty Decision Log and an un-ratified proposal
status. These tests pin the retroactive ratification trail so the merged
v3 contract has a signed decision record.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PROPOSAL_MD = REPO_ROOT / "docs" / "loom" / "outcome-map-v3" / "proposal.md"
PLAN_MD = REPO_ROOT / "docs" / "loom" / "plans" / "2026-08-30-outcome-map-v3.md"

RATIFIED_LINE = "Status: ratified — kouko, 2026-08-31"
USER_RATIFIED = "user-ratified: kouko, 2026-08-31"


def test_proposal_status_is_ratified():
    proposal = PROPOSAL_MD.read_text(encoding="utf-8")
    assert RATIFIED_LINE in proposal


def test_plan_decision_log_has_at_least_five_ratified_entries():
    plan = PLAN_MD.read_text(encoding="utf-8")
    match = re.search(r"^## Decision Log\n(.*?)(?=\n## )", plan, re.S | re.M)
    assert match, "plan has no Decision Log section"
    entries = re.findall(r"^### ", match.group(1), re.M)
    assert len(entries) >= 5
    assert match.group(1).count(USER_RATIFIED) >= 5


def test_each_decision_log_entry_carries_user_ratified_line():
    plan = PLAN_MD.read_text(encoding="utf-8")
    match = re.search(r"^## Decision Log\n(.*?)(?=\n## )", plan, re.S | re.M)
    assert match
    entries = re.split(r"^### ", match.group(1), flags=re.M)[1:]
    assert len(entries) >= 5
    for entry in entries:
        assert USER_RATIFIED in entry, entry.splitlines()[0]