"""Structural grep-test guarding the using-loom-product-principles entry skill.

This is the loom-product-principles FAMILY ENTRY (thin router), not the
member skill that authors PRINCIPLES.md. Its correctness is the PRESENCE of:

  - the SKILL.md file itself, with `name: using-loom-product-principles`
  - a `## §Intake` section carrying the three load-bearing steps: step 1
    (前站檢查 — reference the loom family reception's on-ramp criteria table,
    never copy it), step 2 (對站檢查 — redirect design/spec/code asks to
    their own family entries), step 3 (hand off to `product-principles` for
    the actual principles-writing work)
  - an ENTRY-framed frontmatter `description` (start-here / routing /
    不確定從哪開始 intent) that does NOT contain product-principles' own
    direct-ask trigger phrasing (產品原則 / north star / 憲章) — #456
    positive-specificity: the entry must not steal the member's direct pull
  - flat-skill: no nested subfolders (repo hook enforces)

Checks assert on load-bearing PHRASES (intent), tolerant of wording
variation. Stdlib only (pathlib + re). Resolve SKILL.md relative to this
test file.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "using-loom-product-principles"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter() -> str:
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    return m.group(1)


# House description-length standard (ADOPTED 2026-06-19):
# docs/skill-mining/2026-06-19-skill-description-standard.md — target ≤150,
# hard cap 250. Measured on the YAML-parsed, whitespace-folded value.
_HOUSE_DESC_CAP = 250


def _description() -> str:
    """YAML-parsed, whitespace-folded description value."""
    front = _frontmatter()
    m = re.search(
        r"description:\s*[|>]?-?\s*\n?(.*?)(?:\n\S|\Z)", front, re.DOTALL
    )
    assert m and m.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"
    return " ".join(m.group(1).split())


def test_description_within_house_length_cap():
    """Rendered description must fit the house hard cap of 250 chars
    (target ≤150) per the adopted skill-description standard."""
    desc = _description()
    assert len(desc) <= _HOUSE_DESC_CAP, (
        f"description renders to {len(desc)} chars; house hard cap is "
        f"{_HOUSE_DESC_CAP} (target ≤150) — trim it"
    )


def test_using_entry_intake_contract():
    """Single comprehensive contract test (plan-named acceptance test):
    file exists, frontmatter name correct, description is entry-framed and
    does not overlap the member's direct-ask triggers, and §Intake carries
    all three steps."""
    text = _text()
    front = _frontmatter()

    # frontmatter name
    assert re.search(
        r"^name:\s*using-loom-product-principles\s*$", front, re.MULTILINE
    ), "frontmatter must declare 'name: using-loom-product-principles'"

    # description present
    m = re.search(r"description:\s*\|?\s*\n?(.*?)(?:\nversion:|\Z)", front, re.DOTALL)
    assert m and m.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"
    desc = m.group(1)

    # entry-framing tokens (start-here / routing / 不確定從哪開始 intent)
    assert "family entry" in desc, \
        "description must be ENTRY-framed: carry 'family entry'"
    assert "intake" in desc.lower(), \
        "description must mention intake"
    assert "rout" in desc.lower(), \
        "description must mention routing"
    assert "不確定從哪開始" in desc or "where do i start" in desc.lower() \
        or "where do you start" in desc.lower(), \
        "description must carry a 不確定從哪開始/'where do I start' intent phrase"

    # must NOT steal product-principles' own direct-ask triggers (#456)
    assert "產品原則" not in desc, \
        "description must not overlap product-principles' direct trigger 產品原則"
    assert "north star" not in desc.lower(), \
        "description must not overlap product-principles' direct trigger 'north star'"
    assert "憲章" not in desc, \
        "description must not overlap product-principles' direct trigger 憲章"

    # §Intake section with three steps
    assert "## §Intake" in text, "body must have a '## §Intake' section"
    assert "前站檢查" in text, \
        "§Intake step 1 must be labeled 前站檢查 (upstream check)"
    assert "對站檢查" in text, \
        "§Intake step 2 must be labeled 對站檢查 (sibling-station redirect)"
    assert "product-principles" in text, \
        "§Intake step 3 must hand off to the member skill 'product-principles'"

    # step 1 references the reception SSOT, never copies its table
    assert "family-reception.md" in text or "family reception" in text.lower(), \
        "step 1 must reference the loom family reception's on-ramp criteria (SSOT)"

    # step 2 redirects the three sibling concerns
    assert "using-loom-interface-design" in text, \
        "step 2 must redirect design-surface asks to using-loom-interface-design"
    assert "using-loom-spec" in text, \
        "step 2 must redirect spec fan-out asks to using-loom-spec"
    assert "using-loom-code" in text, \
        "step 2 must redirect coding asks to using-loom-code"


def test_skill_folder_is_flat():
    """The skill dir may hold SKILL.md plus single-level subfolders; no
    subfolder may itself contain a subfolder (the repo hook blocks
    otherwise)."""
    skill_dir = SKILL.parent
    assert skill_dir.is_dir(), f"skill dir absent at {skill_dir}"
    for sub in skill_dir.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), (
                    f"flat-skill violation: nested subdir {child} under "
                    f"{sub} (subfolders must be single-level)"
                )
