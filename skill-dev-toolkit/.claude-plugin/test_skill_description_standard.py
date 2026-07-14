"""Structural grep-test: the house skill-description standard must be encoded in
the two skill-dev-toolkit skills that author / judge descriptions.

The standard (SSOT rationale: docs/skill-mining/2026-06-19-skill-description-standard.md)
is inlined into each consuming skill per this repo's self-contained-skill convention —
EXCEPT the length numbers, which live ONLY in description-design.md §Principle 5 (the
number authority); the creator copy defers to it. This test guards that the other
craft rules stay inlined in both copies and no cap figure drifts back into SCA.

Stdlib only (pathlib + re).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CREATOR = ROOT / "skill-dev-toolkit" / "skills" / "skill-creator-advance" / "SKILL.md"
JUDGE = ROOT / "skill-dev-toolkit" / "skills" / "skill-judge" / "SKILL.md"
DESIGN = (ROOT / "skill-dev-toolkit" / "skills" / "skill-creator-advance"
          / "references" / "description-design.md")


def _low(p: Path) -> str:
    """Lowercased text with whitespace collapsed to single spaces, so phrase
    assertions match regardless of markdown line-wrapping in the source."""
    assert p.is_file(), f"missing {p}"
    return re.sub(r"\s+", " ", p.read_text(encoding="utf-8").lower())


# --- skill-creator-advance: authoring must target the standard -------------

def test_creator_defers_length_numbers_to_ssot():
    """Length numbers live ONLY in description-design.md Principle 5 (the
    number authority); the SCA body may name the two-tier shape but must not
    carry standalone cap figures that can drift from the SSOT."""
    t = _low(CREATOR)
    assert "references/description-design.md" in t and "number authority" in t, \
        "creator body must defer to description-design.md as the length number authority"
    # Phrasing-independent drift guard: slice the section that owns the house
    # description standard and ban ANY standalone cap figure inside it. Section
    # scoping is deliberate — the unrelated '4,500 words' body-size figure
    # elsewhere in SKILL.md must stay legal (no full-file ban).
    raw = CREATOR.read_text(encoding="utf-8")
    sec_m = re.search(r"^## Description Optimization\b.*?(?=^## |\Z)", raw,
                      re.M | re.S)
    assert sec_m, "creator must keep a '## Description Optimization' section"
    for tok in ("150", "250", "500"):
        assert not re.search(rf"(?<!\d){tok}(?!\d)", sec_m.group(0)), \
            (f"standalone {tok!r} in SCA §Description Optimization: length caps "
             f"belong ONLY in description-design.md §Principle 5 (drift risk)")


def test_ssot_principle5_pins_two_tier_semantics():
    """description-design.md §Principle 5 is the number authority; the guard
    must FAIL if the two-tier statement is broken, not merely if substrings
    vanish elsewhere in the file (assertion-must-encode-the-property)."""
    text = DESIGN.read_text(encoding="utf-8")
    m = re.search(r"^### 5\..*?(?=### 6\.|\Z)", text, re.M | re.S)
    assert m, "description-design.md must contain a '### 5.' length principle section"
    p5 = re.sub(r"\s+", " ", m.group(0).lower())
    for needle in ("soft lint line", "not a hard cap", "≤150", "≤500",
                   "firing-evidence"):
        assert needle in p5, \
            f"Principle 5 two-tier statement broken: missing {needle!r}"


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
