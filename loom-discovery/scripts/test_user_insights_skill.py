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
        if re.match(r"^#+.*\bsolution", line.strip(), re.IGNORECASE):
            raise AssertionError(f"template leaks a solution heading: {line!r}")


def test_template_has_job_story_phrasing():
    # Why: needs are expressed as Torres/Intercom job stories, not features.
    body = INSIGHTS_TEMPLATE.read_text(encoding="utf-8")
    assert "When" in body and "I want" in body and "so I can" in body, (
        "template must carry job-story phrasing: When …, I want …, so I can …"
    )


def test_validate_step_wired_with_bounded_retry():
    # Why: Task 3 — the discovery validator must be mandatory before declaring
    # done, with a bounded fix-and-rerun loop (not infinite retry, not a
    # silent skip) — mirrors product-principles Step 8's validator wiring.
    body = SKILL.read_text(encoding="utf-8")
    assert "validate_discovery_artifacts.py" in body, (
        "validator invocation missing from SKILL.md"
    )
    assert "bounded at 2 attempts" in body, (
        "the 2-attempt fix-and-rerun bound must be stated explicitly"
    )
    assert "surface" in body and "user" in body, (
        "must document surfacing remaining problems to the user after exhaustion"
    )


def test_validate_step_tolerates_greenfield_first_run():
    # Why: first-run artifact creation (assess-first intermediate state) must
    # not be treated as a validator failure — plan Task 3 explicit constraint.
    body = SKILL.read_text(encoding="utf-8")
    assert "greenfield" in body.lower() or "first-run" in body.lower(), (
        "must document tolerance for greenfield/first-run artifact creation"
    )


def test_no_nested_subfolders():
    # Why: Anthropic skill convention — subfolders stay single-level (hook-enforced).
    for sub in SKILL_DIR.iterdir():
        if sub.is_dir():
            for child in sub.iterdir():
                assert not child.is_dir(), f"nested subfolder not allowed: {child}"
