"""W1-04 -- `references/lane-switch.md` carries the three-option consequence
prompt review's SKILL.md §1 points readers at.

Four pieces of text, pinned by presence and shape:
1. the three-option block (a lose/keep/estimate row per lane, including
   the lane the delta forbids);
2. the "listed with its reason" sentence -- the forbidden option stays on
   the list rather than being dropped;
3. the spoken mapping table (快速模式 -> express, 只過閘/不用審 -> gate-only);
4. the switch-line grammar, `lane: <name> — switched <YYYY-MM-DD> by
   <name>, from <wave <n>|round <n>>`.

These are presence/shape pins on this new reference file, not the
affirmative-sentence NEGATION_RE pins the four station-text test files
carry for their own new sentences (that machinery lives in
test_review_station_text.py, test_build_station_text.py and
test_ship_station_text.py).
"""
from __future__ import annotations

import re
from pathlib import Path

from prose_pin import NEGATION_RE

REPO = Path(__file__).resolve().parents[2]
LANE_SWITCH = REPO / "loom-code/skills/review/references/lane-switch.md"


def _text() -> str:
    assert LANE_SWITCH.is_file(), f"{LANE_SWITCH} does not exist."
    return LANE_SWITCH.read_text(encoding="utf-8")


def test_file_exists() -> None:
    assert LANE_SWITCH.is_file()


def test_spoken_mapping_table_present() -> None:
    text = _text()
    assert "快速模式" in text
    assert "express" in text
    assert "只過閘" in text
    assert "不用審" in text
    assert "gate-only" in text
    # both spoken forms map to the same lane, in the same table
    table_start = text.index("## Spoken mapping")
    table_end = text.index("## The three-option prompt")
    table = text[table_start:table_end]
    assert "快速模式" in table and "`express`" in table
    assert "只過閘" in table and "`gate-only`" in table
    assert "不用審" in table and "`gate-only`" in table


def test_three_option_block_covers_full_express_gateonly() -> None:
    text = _text()
    start = text.index("## The three-option prompt")
    end = text.index("## The switch-line grammar")
    block = text[start:end]
    assert "| Lane | What you lose | What stays | Estimate |" in block
    assert "`full`" in block
    assert "`express`" in block
    assert "`gate-only`" in block
    assert "cost" in block.lower()
    assert "no estimate" in block.lower()


def test_forbidden_option_listed_with_its_reason() -> None:
    text = _text()
    start = text.index("## The three-option prompt")
    end = text.index("## The switch-line grammar")
    block = text[start:end]
    flat = " ".join(block.split())
    hits = [
        s for s in re.split(r"(?<=[.!?])\s+", flat)
        if "stays listed" in s.lower() and "reason" in s.lower()
    ]
    assert hits, (
        "lane-switch.md has no sentence stating the forbidden option "
        "stays listed with its reason"
    )
    negated = [s for s in hits if NEGATION_RE.search(s)]
    assert not negated, (
        "the 'stays listed ... reason' sentence carries a negation token, "
        f"so it does not affirmatively state the invariant: {negated!r}"
    )


def test_switch_line_grammar_present() -> None:
    text = _text()
    assert (
        "lane: <name> — switched <YYYY-MM-DD> by <name>, from "
        "<wave <n>|round <n>>" in text
    )


def test_switch_line_written_by_user_only() -> None:
    text = _text()
    start = text.index("## The switch-line grammar")
    section = text[start:]
    flat = " ".join(section.split())
    assert "Only the user writes this line" in flat


def test_questions_entry_type_consequence() -> None:
    text = _text()
    start = text.index("## Recording the answer")
    section = text[start:]
    assert '"type": "consequence"' in section
    assert "questions[]" in section


def test_review_skill_points_at_lane_switch() -> None:
    review_skill = (
        REPO / "loom-code/skills/review/SKILL.md"
    ).read_text(encoding="utf-8")
    assert "references/lane-switch.md" in review_skill
