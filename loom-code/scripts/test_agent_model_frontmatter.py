"""Tests for Claude role defaults in loom-code agent frontmatter.

Pinned arms (spec-reviewer, code-quality-reviewer, docs-reviewer, and —
since the 2026-08-24 overturn of the 0.75.0 carve-out — code-reviewer)
default to sonnet: rubric/checklist review is `standard`-tier work per
dispatch-profile.md, and an explicit dispatch-time `model` param remains
the upward-override path (frontier branches). All roles inherit the
dispatching session's effort so the portable profile cannot be overridden
by a static frontmatter value. The implementer is the remaining judgment
arm and inherits the dispatching session's model tier.
"""
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"


def _frontmatter(agent_name):
    text = (AGENTS_DIR / f"{agent_name}.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{agent_name}.md missing frontmatter opening fence"
    end = text.index("\n---", 4)
    return text[4:end]


def test_checklist_arms_pin_model_but_all_roles_inherit_effort():
    checklist_arms = [
        "spec-reviewer",
        "code-quality-reviewer",
        "docs-reviewer",
        "code-reviewer",
    ]
    judgment_arms = ["implementer"]

    for agent_name in checklist_arms:
        frontmatter = _frontmatter(agent_name)
        assert "model: sonnet" in frontmatter, (
            f"{agent_name}.md frontmatter must pin model: sonnet"
        )
    for agent_name in checklist_arms + judgment_arms:
        frontmatter = _frontmatter(agent_name)
        assert "effort:" not in frontmatter, (
            f"{agent_name}.md frontmatter must inherit session effort"
        )

    for agent_name in judgment_arms:
        frontmatter = _frontmatter(agent_name)
        assert "model:" not in frontmatter, (
            f"{agent_name}.md frontmatter must not carry a model: key"
        )
