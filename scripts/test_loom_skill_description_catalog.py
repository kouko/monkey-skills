"""Freeze Loom's description budget and the routing-evaluation corpus.

The baseline describes the 20 leaf skills before the router change.  Candidate
accounting deliberately includes every router description: counting only leaf
descriptions would make an apparent saving that a new Codex session cannot
actually receive.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOOM_PLUGINS = ("loom-code", "loom-design", "loom-workflow")
BASELINE_LEAF_COUNT = 20
BASELINE_RENDERED_DESCRIPTION_CHARS = 6_746
DESCRIPTION_BUDGET = 4_047
ROUTER_NAMES = {
    "loom-code": "using-loom-code",
    "loom-design": "using-loom-design",
    "loom-workflow": "using-loom-workflow",
}
CORPUS = (
    REPO_ROOT
    / "docs/skill-dogfood/2026-09-13-compress-loom-skill-descriptions/cases.md"
)
CASE_BLOCK = re.compile(r"```json routing-cases\n(?P<body>.*?)\n```", re.DOTALL)


def _description(skill_md: Path) -> str:
    """Render the frontmatter block scalar as Codex receives it."""

    frontmatter = skill_md.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    match = re.search(r"^description:\s*\|[-+]?\n(?P<body>(?:[ \t]+.*\n?)*)", frontmatter, re.MULTILINE)
    assert match, f"missing block-scalar description: {skill_md.relative_to(REPO_ROOT)}"
    return " ".join(line.strip() for line in match.group("body").splitlines())


def _skills() -> dict[str, dict[str, Path]]:
    return {
        plugin: {
            skill_md.parent.name: skill_md
            for skill_md in sorted((REPO_ROOT / plugin / "skills").glob("*/SKILL.md"))
        }
        for plugin in LOOM_PLUGINS
    }


def _routing_cases() -> list[dict[str, object]]:
    text = CORPUS.read_text(encoding="utf-8")
    match = CASE_BLOCK.search(text)
    assert match, "cases.md must contain one ```json routing-cases block"
    cases = json.loads(match.group("body"))
    assert isinstance(cases, list)
    return cases


def test_frozen_leaf_baseline_is_accounted_before_router_edits() -> None:
    """The W0 RED must be attributable to the candidate, not a moving baseline."""

    skills = _skills()
    leaf_descriptions = [
        _description(skill_md)
        for plugin, skill_map in skills.items()
        for name, skill_md in skill_map.items()
        if name != ROUTER_NAMES[plugin]
    ]

    assert len(leaf_descriptions) == BASELINE_LEAF_COUNT
    assert sum(map(len, leaf_descriptions)) == BASELINE_RENDERED_DESCRIPTION_CHARS


def test_candidate_has_exactly_one_router_per_loom_plugin() -> None:
    """Routers are a bounded addition, not a hidden expansion of the surface."""

    skills = _skills()
    missing = [
        f"{plugin}/skills/{router}/SKILL.md"
        for plugin, router in ROUTER_NAMES.items()
        if router not in skills[plugin]
    ]
    assert not missing, f"missing Loom routers: {', '.join(missing)}"

    assert sum(len(skill_map) for skill_map in skills.values()) == (
        BASELINE_LEAF_COUNT + len(ROUTER_NAMES)
    )


def test_candidate_rendered_description_total_counts_router_overhead() -> None:
    """All exposed descriptions, including router metadata, fit the net budget."""

    descriptions = [
        _description(skill_md)
        for skill_map in _skills().values()
        for skill_md in skill_map.values()
    ]
    assert sum(map(len, descriptions)) <= DESCRIPTION_BUDGET


def test_routing_corpus_covers_positive_boundary_and_non_trigger_cases() -> None:
    """Keep W2 dogfooding honest about routing, not merely byte reduction."""

    cases = _routing_cases()
    by_id = {case["id"]: case for case in cases}
    assert set(by_id) == {
        "plugin-umbrella",
        "direct-leaf",
        "adjacent-skill-collision",
        "ordinary-request",
        "multilingual-request",
        "explicit-only-goal-create",
    }

    assert by_id["plugin-umbrella"]["expected"] == "using-loom-code"
    assert by_id["direct-leaf"]["expected"] == "write-plan"
    assert by_id["adjacent-skill-collision"]["expected"] == "write-plan"
    assert "capture-intent" in by_id["adjacent-skill-collision"]["forbidden"]
    assert by_id["ordinary-request"]["expected"] == "none"
    assert by_id["multilingual-request"]["expected"] == "write-spec"
    assert by_id["explicit-only-goal-create"]["expected"] == "goal-create"
    assert by_id["explicit-only-goal-create"]["invocation"] == "explicit-only"
