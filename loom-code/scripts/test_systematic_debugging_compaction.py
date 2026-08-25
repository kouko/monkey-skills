"""Static contract for the systematic-debugging entrypoint compaction."""

import json
from pathlib import Path
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/systematic-debugging/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_four_phase_evidence_and_bounded_fix_loop_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    words = int(subprocess.run(
        ["wc", "-w", str(SKILL)], capture_output=True, check=True, text=True
    ).stdout.split()[0])
    assert 1540 <= words <= 1760

    required = (
        "<SUBAGENT-STOP>",
        "NO FIXING WITHOUT REPRODUCING",
        "## When NOT to use",
        "tdd-iron-law",
        "## The 4 phases",
        "### Phase 1 — REPRODUCE",
        "reliable trigger",
        "Intermittent",
        "Cannot reproduce",
        "Do NOT proceed to Phase 2",
        "Gate to Phase 2",
        "### Phase 2 — ISOLATE",
        "Git bisect",
        "Input bisect",
        "Dependency bisect",
        "Component bisect",
        "5-Whys",
        "Gate to Phase 3",
        "### Phase 3 — HYPOTHESIZE",
        "falsifiable hypothesis",
        "every fix attempt requires a hypothesis stated in advance",
        "Log each experiment: hypothesis; one variable changed; command/input; observed result; confirmed/falsified.",
        "Gate to Phase 4",
        "### Phase 4 — VERIFY",
        "Hypothesis confirmed",
        "Hypothesis falsified",
        "Do NOT keep the failed-hypothesis fix in",
        "Revert any speculative changes",
        "Inconclusive",
        "regression test",
        "Anchored-thinking guard",
        "WebSearch mandatory",
        "EN + JA",
        "document empty results explicitly",
        "Hypothesis #3",
        "## Cross-skill contract",
        'unblock_step: "test will not go RED"',
        "paths + structured seed context",
        "## Red Flags",
        "1 hour",
        "observability instrumentation",
        "## What this skill does NOT do",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing systematic-debugging essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["systematic-debugging"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
