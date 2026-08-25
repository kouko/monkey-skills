"""Static contract for the ui-verification entrypoint compaction."""

import json
from pathlib import Path
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/ui-verification/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_conditional_states_tools_evidence_and_repair_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    words = int(subprocess.run(
        ["wc", "-w", str(SKILL)], capture_output=True, check=True, text=True
    ).stdout.split()[0])
    assert 838 <= words <= 956

    required = (
        "<SUBAGENT-STOP>",
        "## The gate is CONDITIONAL",
        "A `ui-flows.md` exists",
        "The branch touched a UI surface",
        "ui-verification: N/A",
        "first-class honest outcome",
        "## Tooling",
        "chrome-devtools",
        "Playwright",
        "agent-device",
        "TUI / CLI",
        "no browser/device automation available",
        "Never fake it",
        "## Process",
        "critic-found",
        "Launch the real app",
        "declared surface",
        "each inventory row and each flagged variant",
        "through real interactions",
        "screenshot or accessibility/DOM snapshot",
        "verified",
        "mismatch",
        "unreachable",
        "untestable",
        "long real-time waits",
        "half-measure",
        "where",
        "## Verdict",
        "NEEDS_REVISION",
        "PASS_WITH_NOTES",
        "no bare PASS",
        "N of M enumerated states verified",
        "## What this skill is NOT",
        "verification-before-completion",
        "DESIGN.md",
        "design-critic",
        "Verdict-only",
        "## Where it runs",
        "finishing-a-development-branch",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing ui-verification essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["ui-verification"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
