"""Guard the resolved description authority and its creator/judge consumers.

Craft rules and length numbers live in description-design.md, Principle 4
owns the numbers, and judge D4 inlines the scoring counterpart. Check these
scoped policies rather than requiring extracted prose back in the creator.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREATOR = ROOT / "skill-dev-toolkit" / "skills" / "skill-creator-advance" / "SKILL.md"
JUDGE = ROOT / "skill-dev-toolkit" / "skills" / "skill-judge" / "SKILL.md"
DESIGN = CREATOR.parent / "references" / "description-design.md"


def _low(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _section(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(start + r".*?(?=" + end + r"|\Z)", text, re.M | re.S)
    assert match, f"missing section {start!r} in {path}"
    return _low(match.group(0))


def test_description_authorities_agree():
    triggers = _section(DESIGN, r"^### Principle 2:", r"^### ")
    belt = _section(DESIGN, r"^### Multilingual keyword belt", r"^### ")
    judge = _section(JUDGE, r"^\*\*House description standard", r"^### D5:")
    assert "lead with positive specific triggers; add exclusions only to disambiguate adjacent skills" in triggers
    assert "limit exclusions to **2-3 negative triggers**" in triggers
    assert "**positive specific triggers first**; allow only 2-3 exclusions for adjacent-skill disambiguation" in judge
    assert "an optional short keyword belt (≤50 chars) may appear at the end" in belt
    assert "include it if the repo's prompts are routinely non-english, skip it otherwise" in belt
    assert "for repos with mixed-language prompts" in belt
    assert "**optional multilingual belt**: allow ≤50 chars only for mixed-language prompts routinely non-english; skip it otherwise" in judge
    # Resolved craft rules retain what+when, procedure placement, neutral
    # voice, and the over-triggering warning after reference extraction.
    purpose = _section(DESIGN, r"^## Purpose", r"^## ")
    assert "what it does + when to use it" in purpose
    assert "procedure / workflow / grounding belongs in the body" in purpose
    assert "third person" in triggers and "no xml tags" in triggers
    assert 'avoid "always invoke"' in triggers and "over-trigger" in triggers
    assert 'penalize reliance on "always invoke" directives (over-trigger at scale)' in judge
    assert "procedure / workflow / grounding** belongs in the body" in judge


def test_forbidden_description_policy_detected():
    creator = _section(CREATOR, r"^### Step 1:", r"^### Skill Writing Guide")
    judge = _section(JUDGE, r"^\*\*House description standard", r"^### D5:")
    assert 'avoid "do not use for x"' not in creator
    assert "no cjk / multilingual keyword redundancy" not in judge
    assert "a/b-verified redundant" not in judge
    assert "penalize >250" not in judge
    # Router status alone cannot admit an exception without evidence.
    assert "a new router/conditional skill with no evidence yet stays in the normal band" in judge
    assert "unjustified >250 = penalize" in judge


def test_resolved_reference_checks():
    best = _section(CREATOR, r"^### Description Best Practices", r"^### ")
    optimization = _section(CREATOR, r"^## Description Optimization", r"^### Packaging")
    judge = _section(JUDGE, r"^\*\*House description standard", r"^### D5:")
    for consumer in (best, optimization):
        assert "references/description-design.md" in consumer
        assert "principle 4" in consumer and "number authority" in consumer
    for token in ("150", "250", "500"):
        assert not re.search(rf"(?<!\d){token}(?!\d)", optimization)
    assert DESIGN.is_file()
    assert str(DESIGN.relative_to(ROOT)).lower() in judge
    assert "principle 4" in judge and "principle 5" not in judge
    assert "2026-06-19-skill-description-standard" in judge
    # Bounded authority paragraphs own the two-tier admission rules.
    length = _section(DESIGN, r"^### Principle 4:", r"^### ")
    for policy in (length, judge):
        for needle in ("≤150", "250", "soft lint line", "≤500",
                       "justification comment", "retained trigger surfaces",
                       "firing-evidence", "normal band", "yaml parse"):
            assert needle in policy, f"missing length admission rule: {needle}"
    assert "not failure" in length and "not a hard penalty" in judge
    assert "unjustified >250 remains a violation" in length
    assert "admission requires**: a firing-evidence note in the yaml justification" in length
    assert "exception band ≤500 requiring a firing-evidence note" in judge


def test_judge_word_budget():
    text = JUDGE.read_text(encoding="utf-8")
    assert len(text.split()) <= 4500
    dimensions = re.findall(r"^### D([1-8]):.*?\((\d+) points\)", text, re.M)
    assert dimensions == list(zip("12345678", ("20", "15", "15", "15", "15", "15", "10", "15")))
    assert sum(int(points) for _, points in dimensions) == 120
