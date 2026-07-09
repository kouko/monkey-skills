"""Structural guard for the user-insights member skill.

SKILL.md + templates are prose/config (a tdd-iron-law exemption), so these
are presence/shape assertions, not iron-law-mandated logic tests. Paths are
resolved relative to this file so the test runs from any cwd.

Load-bearing invariants encoded here (why each matters):
- the commitment interaction contract must survive edits ("user ratifies");
- the research-delegation boundary must name deep-deep-research;
- the artifact template must stay problem-space-pure (NO solution section) —
  the Intercom rule the whole station is built on;
- needs must be expressed as job stories (the Torres opportunity-space
  semantics the brief adopted);
- the skill folder must stay flat (Anthropic skill convention, hook-enforced).
"""

import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent / "skills" / "user-insights"
SKILL = SKILL_DIR / "SKILL.md"
INSIGHTS_TEMPLATE = SKILL_DIR / "assets" / "user-insights-template.md"
EVIDENCE_TEMPLATE = SKILL_DIR / "assets" / "evidence-template.md"


def _frontmatter(md: Path) -> dict:
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, f"{md} lacks a leading --- frontmatter block"
    fields, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^\w[\w-]*:", line):
            key, _, val = line.partition(":")
            fields[key.strip()] = val.strip()
        elif key and line.strip():
            fields[key] = (fields.get(key, "") + " " + line.strip()).strip()
    return fields


def test_skill_and_templates_exist():
    # Why: the skill is nothing without its SKILL.md and its two artifact templates.
    assert SKILL.exists(), f"SKILL.md missing at {SKILL}"
    assert INSIGHTS_TEMPLATE.exists(), f"user-insights-template.md missing at {INSIGHTS_TEMPLATE}"
    assert EVIDENCE_TEMPLATE.exists(), f"evidence-template.md missing at {EVIDENCE_TEMPLATE}"


def test_frontmatter_valid():
    # Why: a skill with no name/description cannot be routed or auto-triggered.
    fm = _frontmatter(SKILL)
    assert fm.get("name") == "user-insights", f"unexpected name: {fm.get('name')!r}"
    assert fm.get("description", "").strip(), "description must be non-empty"


def test_description_within_budget():
    # Why: the listing evicts descriptions over the 1536-char per-skill budget.
    desc = _frontmatter(SKILL).get("description", "")
    assert len(desc) <= 1536, f"description is {len(desc)} chars, exceeds 1536 budget"


def test_user_ratifies_contract_present():
    # Why: the commitment interaction contract — agents never self-commit — is
    # load-bearing; the phrase "user ratifies" is its anchor.
    body = SKILL.read_text(encoding="utf-8")
    assert "user ratifies" in body, "commitment contract phrase 'user ratifies' missing"


def test_delegation_boundary_names_deep_research():
    # Why: the research boundary must delegate heavyweight work to the named engine.
    body = SKILL.read_text(encoding="utf-8")
    assert "deep-deep-research" in body, "research delegation target not named"


def test_template_has_no_solution_section():
    # Why: problem-space purity (Intercom rule) — a solution heading would leak HOW.
    body = INSIGHTS_TEMPLATE.read_text(encoding="utf-8")
    for line in body.splitlines():
        if re.match(r"^#+\s*solution\b", line.strip(), re.IGNORECASE):
            raise AssertionError(f"template leaks a solution heading: {line!r}")


def test_template_has_job_story_phrasing():
    # Why: needs are expressed as Torres/Intercom job stories, not features.
    body = INSIGHTS_TEMPLATE.read_text(encoding="utf-8")
    assert "When" in body and "I want" in body and "so I can" in body, (
        "template must carry job-story phrasing: When …, I want …, so I can …"
    )


def test_no_nested_subfolders():
    # Why: Anthropic skill convention — subfolders stay single-level (hook-enforced).
    for sub in SKILL_DIR.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), f"nested subfolder not allowed: {child}"
