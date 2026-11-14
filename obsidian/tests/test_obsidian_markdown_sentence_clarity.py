"""Wiring guard for the sentence-clarity rules.

The rules live in one file under obsidian-markdown, the skill every note
goes through, so they are stated once. These tests check (and only this):
the file exists and states four numbered rules, obsidian-markdown's SKILL.md
links it exactly once, and obsidian-research points to the obsidian-markdown
rules without keeping a local copy. Whether notes actually read better is
NOT checked here — compare a note written before and after.
"""

import re
from pathlib import Path

SKILLS = Path(__file__).parent.parent / "skills"
RULES = SKILLS / "obsidian-markdown/references/sentence-clarity.md"
MARKDOWN_SKILL_MD = SKILLS / "obsidian-markdown/SKILL.md"
RESEARCH_SKILL_MD = SKILLS / "obsidian-research/SKILL.md"
OLD_COPY = SKILLS / "obsidian-research/references/sentence-clarity.md"


def test_rules_file_exists():
    assert RULES.is_file(), f"missing {RULES}"


def test_rules_file_states_four_numbered_rules():
    text = RULES.read_text(encoding="utf-8")
    numbers = re.findall(r"^(\d+)\. \*\*", text, re.M)
    assert numbers == ["1", "2", "3", "4"], f"expected rules 1-4, found {numbers}"


def test_markdown_skill_links_rules_exactly_once():
    text = MARKDOWN_SKILL_MD.read_text(encoding="utf-8")
    count = len(re.findall(r"\(references/sentence-clarity\.md\)", text))
    assert count == 1, f"SKILL.md must link the rules exactly once, found {count}"


def test_research_skill_has_no_local_copy():
    assert not OLD_COPY.exists(), f"rules must live in one file only: {OLD_COPY}"
    text = RESEARCH_SKILL_MD.read_text(encoding="utf-8")
    assert "(references/sentence-clarity.md)" not in text


def test_research_skill_points_to_markdown_skill_rules():
    text = RESEARCH_SKILL_MD.read_text(encoding="utf-8")
    assert re.search(r"sentence-clarity rules in the `obsidian-markdown` skill", text)
