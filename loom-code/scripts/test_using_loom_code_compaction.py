"""Static contract for the using-loom-code router compaction."""

import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/using-loom-code/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_rules_stage_router_autonomy_and_safety():
    text = SKILL.read_text(encoding="utf-8")

    required = (
        "<SUBAGENT-STOP>",
        "parent orchestrator only",
        "Five load-bearing rules",
        "Brainstorm before implementing",
        "TDD is the iron law",
        "Split + dispatch",
        "Never push without review",
        "Research before asking",
        "## Instruction priority",
        "## How to access skills",
        "Claude Code",
        "Codex CLI",
        "## Skill priority",
        "Discovery",
        "Planning",
        "Execution",
        "Discipline",
        "Repair",
        "Review",
        "Verification",
        "UI verification",
        "Branch close",
        "## Autonomous execution",
        "human-approved",
        "READ references/continuous-mode.md IN FULL",
        "Never auto-merge",
        "privacy, merge, deploy, delete, failed safety gates",
        "PR-open is terminal",
        "dispatching-parallel-agents",
        "≥2 tasks",
        "Independent: true",
        "disjoint `Files touched`",
        "one implementer at a time",
        "## Red flags",
        "## Skill types",
        "## Coexistence",
        "domain-teams:code-team",
        "loom-workflow:{git-memory, complexity-critique, proposal-critique}",
        "obra/superpowers",
        "## What this router does NOT do",
        "## Reference",
        "only when its trigger fires",
        "Claude Code canonical tool names",
        "Codex CLI tool mapping",
        "environment-gotchas.md",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing using-loom-code essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["using-loom-code"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
