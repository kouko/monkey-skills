"""Freeze Loom's description budget and the routing-evaluation corpus.

The baseline describes the 20 leaf skills before the router change.  Candidate
accounting deliberately includes every router description: counting only leaf
descriptions would make an apparent saving that a new Codex session cannot
actually receive.
"""

from __future__ import annotations

import json
import hashlib
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


def _render_description(text: str) -> str:
    """Render the frontmatter block scalar as Codex receives it."""

    frontmatter = text.split("\n---\n", 1)[0]
    match = re.search(r"^description:\s*\|[-+]?\n(?P<body>(?:[ \t]+.*\n?)*)", frontmatter, re.MULTILINE)
    assert match, "missing block-scalar description"
    return " ".join(line.strip() for line in match.group("body").splitlines())


def _description(skill_md: Path) -> str:
    return _render_description(skill_md.read_text(encoding="utf-8"))


def _baseline() -> dict[str, str]:
    match = re.search(
        r"```json description-baseline\n(.*?)\n```",
        CORPUS.read_text(encoding="utf-8"), re.DOTALL,
    )
    assert match, "missing frozen description baseline"
    return json.loads(match.group(1))


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
    leaf_paths = {
        str(skill_md.relative_to(REPO_ROOT))
        for plugin, skill_map in skills.items()
        for name, skill_md in skill_map.items()
        if name != ROUTER_NAMES[plugin]
    }

    baseline = _baseline()
    assert leaf_paths == set(baseline)
    assert len(baseline) == BASELINE_LEAF_COUNT
    assert hashlib.sha256("\n".join(baseline.values()).encode()).hexdigest() == (
        "96d9cc72c5fa5e35e28ecd3596ff797bb430261ee209b82c5a52ceb793ffc275"
    )
    assert sum(map(len, baseline.values())) == BASELINE_RENDERED_DESCRIPTION_CHARS
    assert sum(len(value.split()) for value in baseline.values()) == 1052


def test_description_accounting_excludes_bodies_and_other_metadata() -> None:
    text = "---\nname: example\ndescription: |\n  Only this\n  is counted.\nversion: 99\n---\n"
    assert _render_description(text) == "Only this is counted."
    assert _render_description(text + "description: |\n  decoy\n" * 1000) == (
        "Only this is counted."
    )


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
    candidate = sum(map(len, descriptions))
    assert candidate <= DESCRIPTION_BUDGET
    assert candidate * 100 <= BASELINE_RENDERED_DESCRIPTION_CHARS * 60


def test_router_tables_preserve_direct_leaf_targets_and_goal_boundary() -> None:
    """Check executable links and policy text, not an inferred model verdict."""
    for plugin, skills in _skills().items():
        router_name = ROUTER_NAMES[plugin]
        router = skills[router_name].read_text(encoding="utf-8")
        targets = re.findall(r"\]\(\.\./([^/]+)/SKILL\.md\)", router)
        assert len(targets) == len(set(targets))
        assert set(targets) == set(skills) - {router_name}
        assert "direct" in router.lower()
    workflow = _skills()["loom-workflow"]
    assert "must be invoked by name" in _description(workflow["goal-create"])
    assert "Do not select `goal-create` from an inferred need or an unnamed goal request" in (
        workflow["using-loom-workflow"].read_text(encoding="utf-8")
    )


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
        "held-out-design-specific",
        "held-out-workflow-specific",
        "held-out-unnamed-goal",
        "held-out-design-umbrella",
        "held-out-workflow-umbrella",
    }

    assert len(cases) == len(by_id), "duplicate routing case id"
    available = {name for skills in _skills().values() for name in skills} | {"none"}
    for case in cases:
        assert case["expected"] in available
        assert set(case["forbidden"]) <= available
        assert case["expected"] not in case["forbidden"]
        assert case["request"].strip()

    assert by_id["plugin-umbrella"]["expected"] == "using-loom-code"
    assert by_id["direct-leaf"]["expected"] == "write-plan"
    assert by_id["adjacent-skill-collision"]["expected"] == "write-plan"
    assert "capture-intent" in by_id["adjacent-skill-collision"]["forbidden"]
    assert by_id["ordinary-request"]["expected"] == "none"
    assert by_id["multilingual-request"]["expected"] == "write-spec"
    assert by_id["explicit-only-goal-create"]["expected"] == "goal-create"
    assert by_id["explicit-only-goal-create"]["invocation"] == "explicit-only"
    assert by_id["held-out-design-specific"]["expected"] == "design-system"
    assert by_id["held-out-workflow-specific"]["expected"] == "critique"
    assert by_id["held-out-design-umbrella"]["expected"] == "using-loom-design"
    assert by_id["held-out-workflow-umbrella"]["expected"] == "using-loom-workflow"
    assert by_id["held-out-unnamed-goal"]["expected"] == "none"
    assert "goal-create" in by_id["held-out-unnamed-goal"]["forbidden"]
