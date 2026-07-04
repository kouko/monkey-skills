"""Structural grep-test guarding the using-loom-spec entry SKILL.md.

using-loom-spec is the thin loom-family entry point for loom-spec: it does
not generate or critique anything itself, it routes. This test asserts the
load-bearing structural contract (mirrors test_completeness_critic_skill.py's
style — grep on PHRASES/intent, tolerant of wording, stdlib only):

- the file exists with a valid YAML frontmatter (name + description)
- the description is entry-framed (routing intent) and does not steal
  either member skill's own direct-ask trigger phrasing (#456 positive-
  specificity rule)
- a `## §Intake` section exists with the three load-bearing steps (前站檢查
  / 對站檢查 / family routing)
- step 3 names both member skills AND carries the expansion-vs-critic
  disambiguation phrasing that closes the #456-documented adjacent mis-route
  (critique-an-existing-draft asks wrongly routed to spec-expansion)

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "using-loom-spec" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    return m.group(1)


# --- existence + frontmatter -------------------------------------------------

def test_skill_file_exists():
    assert SKILL.is_file(), f"using-loom-spec/SKILL.md must exist at {SKILL}"


def test_yaml_frontmatter_name_and_description():
    front = _frontmatter(_text())
    assert re.search(r"^name:\s*using-loom-spec\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: using-loom-spec'"
    desc = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE | re.DOTALL)
    assert desc and desc.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"


def test_description_is_entry_framed():
    front = _frontmatter(_text()).lower()
    assert "router" in front or "entry point" in front or "entry" in front, \
        "description must frame this skill as the family entry/router, not a generator"
    assert "route" in front or "routes to" in front or "routing" in front, \
        "description must state it routes to member skills"


def test_description_does_not_steal_member_direct_asks():
    front = _frontmatter(_text()).lower()
    # spec-expansion's own direct-ask trigger phrase (its SKILL.md description)
    assert "requirement fan-out / edge-case coverage before implementation" not in front, \
        "entry description must not copy spec-expansion's own direct-ask trigger verbatim"
    # completeness-critic's own direct-ask trigger phrase (its SKILL.md description)
    assert "review a spec draft for gaps before verify" not in front, \
        "entry description must not copy completeness-critic's own direct-ask trigger verbatim"


# --- §Intake ------------------------------------------------------------------

def test_intake_section_present():
    text = _text()
    assert re.search(r"^##\s+§Intake\s*$", text, re.MULTILINE), \
        "SKILL.md must carry a '## §Intake' section"


def test_intake_step1_upstream_check_references_reception_ssot():
    low = _text().lower()
    assert "前站檢查" in _text() or "step 1" in low, \
        "§Intake step 1 (前站檢查) must be present"
    assert "family-reception.md" in _text() or "on-ramp criteria" in low, \
        "step 1 must reference the reception criteria SSOT (point, don't copy)"


def test_intake_step2_peer_check_present():
    low = _text().lower()
    assert "對站檢查" in _text() or "step 2" in low, \
        "§Intake step 2 (對站檢查) must be present"


def test_intake_step3_names_both_members_and_disambiguates():
    text = _text()
    low = text.lower()
    assert "step 3" in low or "family routing" in low, \
        "§Intake step 3 (family routing) must be present"
    assert "spec-expansion" in text, "step 3 must name spec-expansion"
    assert "completeness-critic" in text, "step 3 must name completeness-critic"
    # the #456 disambiguation phrasing itself
    assert re.search(r"draft.*expand.*seed", low) or "expand a spec from a seed" in low, \
        "step 3 must state the 'draft/expand a spec from a seed' trigger for spec-expansion"
    assert ("critique" in low or "audit" in low) and "existing draft" in low \
        and "omissions" in low, \
        "step 3 must state the 'critique/audit an existing draft for omissions' trigger for completeness-critic"


def test_intake_step3_names_the_456_mis_route():
    low = _text().lower()
    assert "456" in low or "mis-route" in low or "misroute" in low, \
        "step 3 should name the #456-documented adjacent mis-route this disambiguation closes"
