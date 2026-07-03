"""Structural grep-test guarding the product-principles SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing, principles-first instructions plus the hard
constraints the task and the host enforce:

  - YAML frontmatter declaring `name: product-principles` and a non-empty,
    key-free `description` that fits the Codex 1024-char HARD limit and carries
    en + zh-TW + ja trigger phrasings.
  - the principles-first body procedure (read the rules contract → elicit idea →
    North Star → 3-7 falsifiable principles each carrying the literal `— check:`
    marker → emit PRINCIPLES.md → validate).
  - references to BOTH the authoring contract (`references/principles-rules.md`)
    and the validator (`scripts/validate_principles_output.py`) by relative path.
  - the cross-cutting-constitution framing (governs interface-design / spec /
    code, incl headless), key-free + git-diffable.
  - flat-skill: the only subfolder under the skill dir is `references/` and it is
    single-level (no nested subdirs) — the repo hook blocks otherwise.

Checks assert on load-bearing PHRASES (intent), tolerant of wording variation.
Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = (
    Path(__file__).parents[1]
    / "skills"
    / "product-principles"
    / "SKILL.md"
)

# Codex hard limit on a skill description.
_CODEX_DESC_LIMIT = 1024


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _frontmatter() -> str:
    text = _text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "SKILL.md must open with a YAML frontmatter block (--- ... ---)"
    return m.group(1)


# --- YAML frontmatter -------------------------------------------------------

def test_frontmatter_name_is_product_principles():
    front = _frontmatter()
    assert re.search(r"^name:\s*product-principles\s*$", front, re.MULTILINE), \
        "frontmatter must declare 'name: product-principles'"


def test_description_present_and_within_codex_limit():
    """description must exist, be non-empty, and fit the Codex 1024-char HARD
    limit (the whole value, not just the first line)."""
    front = _frontmatter()
    m = re.search(r"^description:\s*(\S.*)$", front, re.MULTILINE)
    assert m and m.group(1).strip(), \
        "frontmatter must carry a non-empty 'description:'"
    desc = m.group(1).strip()
    assert len(desc) <= _CODEX_DESC_LIMIT, (
        f"description is {len(desc)} chars; Codex HARD limit is "
        f"{_CODEX_DESC_LIMIT} — trim it"
    )


def test_description_carries_trilingual_triggers():
    """The skill must fire on goal / principle / constitution intent in
    en + zh-TW + ja."""
    front = _frontmatter().lower()
    # en
    assert "principle" in front, "description must carry an English trigger"
    # zh-TW (Traditional)
    assert ("產品原則" in front or "設計原則" in front
            or "產品憲章" in front), \
        "description must carry a zh-TW trigger (產品原則 / 設計原則 / 產品憲章)"
    # ja
    assert ("原則" in front or "プロダクト指針" in front
            or "製品の原則" in front), \
        "description must carry a ja trigger (製品の原則 / プロダクト指針)"


def test_description_states_principles_md_output():
    """description must signal it produces a PRINCIPLES.md governing
    design / spec / code, key-free."""
    front = _frontmatter()
    assert "PRINCIPLES.md" in front, \
        "description must state it produces a PRINCIPLES.md"
    low = front.lower()
    assert "north star" in low, "description must mention the North Star"


# --- principles-first body procedure ----------------------------------------

def test_body_references_rules_contract_by_relative_path():
    text = _text()
    assert "references/principles-rules.md" in text, \
        "body must reference the authoring contract by relative path"


def test_body_references_validator_by_relative_path():
    text = _text()
    assert "scripts/validate_principles_output.py" in text, \
        "body must reference the validator by relative path"


def test_body_has_north_star_and_principles_sections():
    text = _text()
    assert "## North Star" in text, \
        "body must instruct writing a '## North Star' section"
    assert "## Product Principles" in text, \
        "body must instruct writing a '## Product Principles' section"


def test_body_mandates_falsifiable_check_marker():
    """The load-bearing rule: every principle carries the literal '— check:'
    em-dash marker; platitudes are rejected."""
    text = _text()
    assert "— check:" in text, \
        "body must mandate the literal '— check:' em-dash marker on every principle"
    low = text.lower()
    assert "falsifiable" in low, "body must name the falsifiable-check rule"
    assert "platitude" in low or "push back" in low, \
        "body must reject platitudes / push back on un-checkable principles"
    assert "3" in text and ("7" in text), \
        "body must state the 3-7 principle count"


def test_body_emits_to_consumer_project_path():
    """The skill writes PRINCIPLES.md into the consumer project at the
    docs/<toolkit>/ convention — product-level, one per product."""
    text = _text()
    assert "docs/loom/PRINCIPLES.md" in text, \
        "body must emit PRINCIPLES.md to docs/loom/"


def test_body_mandates_validation_step():
    low = _text().lower()
    assert "validat" in low, \
        "body must instruct running the validator before declaring done"


def test_body_states_cross_cutting_constitution_role():
    """PRINCIPLES.md is the cross-cutting constitution governing downstream
    interface-design / spec / code, incl headless, key-free + git-diffable."""
    low = _text().lower()
    assert "constitution" in low, \
        "body must frame PRINCIPLES.md as the product constitution"
    assert "headless" in low or "cli" in low, \
        "body must state it applies to headless / CLI products"
    assert "key-free" in low, "body must state PRINCIPLES.md is key-free"
    assert "git-diffable" in low or "git diffable" in low, \
        "body must state PRINCIPLES.md is git-diffable"


def test_body_elicits_idea_and_target_user():
    low = _text().lower()
    assert "target user" in low, \
        "body must elicit the product idea + target user"


# --- flat-skill structure (repo hook enforces) ------------------------------

def test_skill_folder_is_flat():
    """The skill dir may hold SKILL.md plus single-level subfolders; no
    subfolder may itself contain a subfolder (the repo hook blocks otherwise)."""
    skill_dir = SKILL.parent
    for sub in skill_dir.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), (
                    f"flat-skill violation: nested subdir {child} under {sub} "
                    f"(subfolders must be single-level)"
                )
