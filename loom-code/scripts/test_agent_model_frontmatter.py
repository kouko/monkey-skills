"""Tests for loom-code agent frontmatter after the 1.0 station redesign.

The four pre-1.0 verdict contracts (spec-reviewer, code-quality-reviewer,
docs-reviewer, code-reviewer) each pinned `model: sonnet` because
dispatch-profile.md called rubric review `standard`-tier work. Both those
contracts and that profile are deleted: one `reviewer.md` now carries every
lens, and the review station chooses the model per dispatch and records it
in `review.json` `dispatch[]`. The model-pin arm is therefore gone with the
mechanism it described, not weakened.

What survives is the effort rule, which was never per-contract: no agent
frontmatter may pin `effort:`, so every role inherits the dispatching
session's effort and the portable profile cannot be overridden by a static
value. Asserted here over the whole `agents/` directory rather than a hand
list, so a fifth contract cannot be added outside the rule.
"""
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"

ROLES = ["implementer", "reviewer", "blind-runner", "adversary"]


def _frontmatter(agent_name):
    text = (AGENTS_DIR / f"{agent_name}.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{agent_name}.md missing frontmatter opening fence"
    end = text.index("\n---", 4)
    return text[4:end]


def test_the_agent_population_is_the_four_station_roles():
    assert sorted(p.stem for p in AGENTS_DIR.glob("*.md")) == sorted(ROLES)


def test_no_agent_pins_effort():
    for path in sorted(AGENTS_DIR.glob("*.md")):
        frontmatter = _frontmatter(path.stem)
        assert "effort:" not in frontmatter, (
            f"{path.name} frontmatter must inherit session effort"
        )
