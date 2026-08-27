"""Static contract for the tdd-iron-law entrypoint compaction."""

import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/tdd-iron-law/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_exemptions_red_green_refactor_and_false_green():
    text = SKILL.read_text(encoding="utf-8")

    required = (
        "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST",
        "Delete the code. Write the test. Start over.",
        "## Grounding (primary sources)",
        "Beck (2002)",
        "Martin (2008)",
        "和田卓人",
        "## Red-Green-Refactor",
        "Three steps. In order. Every time.",
        "It MUST fail",
        "simplest code",
        "revert and take a smaller step",
        "## When NOT to Use",
        "Throwaway / spike",
        "Pure code generation",
        "Trivial getter / setter / pure delegation",
        "Pure configuration",
        "Explicit user override",
        "Do not invent new exceptions",
        "## Red Flags",
        '"I already wrote the code. Now what?"',
        "Distinct from legitimate legacy-code backfill",
        '"The test passed on first run — done!"',
        "Force RED first",
        "## Legitimate legacy-code backfill",
        "Characterization Tests",
        "was the test-first opportunity available",
        "## False-green diagnostic",
        "Comment out the production code change",
        "If it still passes",
        "Rewrite the test until it can fail",
        "Restore the production code",
        "## Cross-skill contract",
        "subagent-driven-development",
        "verification-before-completion",
        "implementer prompt loads this skill",
        "## Reference",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing tdd-iron-law essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["tdd-iron-law"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
