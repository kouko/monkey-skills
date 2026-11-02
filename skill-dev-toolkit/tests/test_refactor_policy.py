"""Keep refactor instructions aligned with the existing executable vote policy."""

import importlib.util
import re
from pathlib import Path

import pytest


SKILL = Path(__file__).resolve().parents[1] / "skills" / "skill-refactor"
spec = importlib.util.spec_from_file_location("refactor_multi_judge", SKILL / "scripts/multi_judge.py")
judge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(judge)


def flag_escalation_is_qualified(passage):
    sentence = " ".join(passage.split()).lower()
    return (
        "escalate only `flag_tier_2` outcomes to human" in sentence
        and not re.search(r"\b(?:no|not|never|cannot|don't|doesn't)\b", sentence)
    )


@pytest.mark.parametrize("votes,reason,verdict", [
    ("EEE", "same behavior", "PASS_HIGH"),
    ("EEU", "unclear", "PASS_MODERATE"),
    ("EEN", "different emphasis", "FLAG_TIER_2"),
    ("ENU", "different emphasis", "FAIL"),
    ("NNN", "different emphasis", "FAIL"),
    ("ENU", "drops the warning", "FLAG_TIER_2"),
])
def test_refactor_policy_consistent(votes, reason, verdict):
    names = dict(E="equivalent", N="not_equivalent", U="uncertain")
    assert judge.aggregate_ensemble([
        {"verdict": names[v], "reason": reason} for v in votes
    ])["consensus"] == verdict
    text = (SKILL / "SKILL.md").read_text()
    for section in ("### Q1.", "## Tier Cascade"):
        scope = text.split(section, 1)[1].split("\n##", 1)[0]
        label = ("Specific behavior dissent" if reason == "drops the warning" else {
            "EEE": "3 `equivalent`", "EEU": "2 `equivalent` + 1 `uncertain`",
            "EEN": "2 `equivalent` + 1 `not_equivalent`",
        }.get(votes, "≤1 `equivalent`"))
        row = next(line for line in scope.splitlines() if label in line)
        assert verdict in row
        assert scope.index("Specific behavior dissent") < scope.index("≤1")


def test_unsafe_refactor_policy_rejected():
    affirmative = "Escalate only `FLAG_TIER_2` outcomes to human review."
    assert flag_escalation_is_qualified(affirmative)
    assert not flag_escalation_is_qualified("Do not " + affirmative)
    assert not flag_escalation_is_qualified("Escalate any disagreement to human review.")
    for filename in ("references/multi-judge-ensemble.md", "NOTICE"):
        consumer = (SKILL / filename).read_text()
        rationale = consumer.split("2. **", 1)[1].split("3. **", 1)[0]
        assert flag_escalation_is_qualified(rationale), filename
    for filename in ("README.md", "README.ja.md", "README.zh-TW.md"):
        consumer = (SKILL / filename).read_text()
        row = next(line for line in consumer.splitlines() if line.startswith("| (Tier 2) |"))
        assert row.split("|")[2].strip() == "Q1 = `FLAG_TIER_2`", filename
    text = (SKILL / "SKILL.md").read_text()
    dependency = next(row for row in text.splitlines() if "Declared dependencies" in row)
    assert "Preserve existing dependencies" in dependency
    assert "allow a new bundled reference required for equivalent extraction" in dependency
    assert "Never change without" not in dependency
    example = text.split("## Worked Example — token bloat", 1)[1].split("## Worked Example", 1)[0]
    assert "whole-package" in example and "**Verdict**: REJECT" in example
    assert "**Verdict**: PROCEED" not in example
    catalog = (SKILL / "references/refactor-moves-catalog.md").read_text()
    extraction = catalog.split("### Extract to references/", 1)[1].split("### ", 1)[0]
    assert "Use package mode" in extraction and "whole-package Q2" in extraction
    assert "Moving prose alone earns no reduction" in extraction
    ablation = (SKILL / "references/ablation-mode.md").read_text()
    current, historical = ablation.split("## Worked example", 1)
    assert "3 judges" in current and "2 judges" not in current
    assert "PASS_MODERATE" in current and "FLAG_TIER_2" in current
    assert "2-judge ensemble" in historical and "historical" in historical
