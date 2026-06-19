"""Structural grep-test: the house skill-description standard must be encoded in
the two dev-workflow skills that author / judge descriptions.

The standard (SSOT rationale: docs/skill-mining/2026-06-19-skill-description-standard.md)
is inlined into each consuming skill per this repo's self-contained-skill convention
(skills carry their own operative rules; we do NOT cross-reference at runtime). This
test guards that both copies carry the load-bearing rules, tolerant of wording.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREATOR = ROOT / "dev-workflow" / "skills" / "skill-creator-advance" / "SKILL.md"
JUDGE = ROOT / "dev-workflow" / "skills" / "skill-judge" / "SKILL.md"


def _low(p: Path) -> str:
    """Lowercased text with whitespace collapsed to single spaces, so phrase
    assertions match regardless of markdown line-wrapping in the source."""
    assert p.is_file(), f"missing {p}"
    return re.sub(r"\s+", " ", p.read_text(encoding="utf-8").lower())


# --- skill-creator-advance: authoring must target the standard -------------

def test_creator_has_length_cap():
    t = _low(CREATOR)
    assert "250" in t and "150" in t, "creator must state the ≤150 target / 250 cap"


def test_creator_what_plus_when():
    t = _low(CREATOR)
    assert "what it does + when to use it" in t, \
        "creator must keep the distinctive what+when rule phrasing (not just the words)"


def test_creator_no_cjk_redundancy():
    assert "cjk" in _low(CREATOR), "creator must state: no CJK/multilingual redundancy"


def test_creator_procedure_in_body_not_description():
    t = _low(CREATOR)
    assert "out of the description" in t and "body" in t, \
        "creator must say procedure/workflow stays OUT of the description (in the body)"


def test_creator_avoids_always_and_negation():
    t = _low(CREATOR)
    assert "always invoke" in t and ("do not use for" in t or "negation" in t), \
        "creator must flag 'ALWAYS invoke' + behavioral negation as anti-patterns"


def test_creator_links_standard_doc():
    assert "2026-06-19-skill-description-standard" in CREATOR.read_text(encoding="utf-8"), \
        "creator must point to the standard doc for rationale"


# --- skill-judge: D4 must score against the standard -----------------------

def test_judge_has_length_cap():
    t = _low(JUDGE)
    assert "250" in t and "150" in t, "judge D4 must penalize over-250 / target ≤150"


def test_judge_no_cjk_redundancy():
    assert "cjk" in _low(JUDGE), "judge must penalize CJK/multilingual redundancy"


def test_judge_avoids_always_and_negation():
    t = _low(JUDGE)
    assert "always invoke" in t and ("do not use for" in t or "negation" in t), \
        "judge must penalize 'ALWAYS invoke' / behavioral-negation reliance"


def test_judge_procedure_in_body():
    t = _low(JUDGE)
    assert "belongs in the body, not the description" in t, \
        "judge must penalize procedure/workflow placed in the description (distinctive clause)"


def test_judge_links_standard_doc():
    assert "2026-06-19-skill-description-standard" in JUDGE.read_text(encoding="utf-8"), \
        "judge must point to the standard doc"
