"""Tests for the model: pin in loom-code agent frontmatter.

Checklist arms (spec-reviewer, code-quality-reviewer, docs-reviewer) run
every task/round and default to sonnet. Judgment arms (implementer,
code-reviewer) inherit the dispatching session's model tier and must
carry no model: key.
"""
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"


def _frontmatter(agent_name):
    text = (AGENTS_DIR / f"{agent_name}.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{agent_name}.md missing frontmatter opening fence"
    end = text.index("\n---", 4)
    return text[4:end]


def test_checklist_arms_default_sonnet_judgment_arms_inherit():
    checklist_arms = ["spec-reviewer", "code-quality-reviewer", "docs-reviewer"]
    judgment_arms = ["implementer", "code-reviewer"]

    for agent_name in checklist_arms:
        frontmatter = _frontmatter(agent_name)
        assert "model: sonnet" in frontmatter, (
            f"{agent_name}.md frontmatter must pin model: sonnet"
        )

    for agent_name in judgment_arms:
        frontmatter = _frontmatter(agent_name)
        assert "model:" not in frontmatter, (
            f"{agent_name}.md frontmatter must not carry a model: key"
        )
