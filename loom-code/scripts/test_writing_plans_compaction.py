"""Static contract for writing-plans compaction."""

import json
from pathlib import Path
import subprocess
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/writing-plans/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_splitting_gates_review_schema_and_change_binding_within_word_range():
    text = SKILL.read_text(encoding="utf-8")
    words = int(subprocess.run(
        ["wc", "-w", str(SKILL)], capture_output=True, check=True, text=True
    ).stdout.split()[0])
    assert 3149 <= words <= 3598

    required = (
        "<SUBAGENT-STOP>",
        "## When NOT to use",
        "single atomic task",
        "## The splitting framework",
        "ONE failing test",
        "≤1 module / ≤1 file boundary",
        "runnable capability note",
        "runnable capability",
        "No time-box criterion",
        "Post-split parallel-marking pass",
        "same dependency level",
        "disjoint",
        "semantic dependency",
        "Dependencies",
        "Seam",
        "payload: none",
        "critical-path depth ≤5",
        "No hard width cap",
        "depth >5",
        "For an initial depth>5 brief, the two options are a closed list: there is no depth-limit exception, structural-split escape hatch, or “record the risk and continue” path.",
        "Structural-split escape hatch",
        "round-2 NEEDS_REVISION",
        "fresh sibling",
        "## BLOCKED fallback",
        "Child Test",
        "unblock_step",
        "plan-document-reviewer",
        "PROMPT FILE",
        "dispatch-profile.md",
        "one-shot blocking call",
        "Plan-document-reviewer verdict: PENDING",
        "Brief item covered:",
        "check_open_questions.py <plan-path>",
        "check_onramp_choice.py <brief-path>",
        "Exit 1 → STOP (brief missing)",
        "Exit 2 → STOP: do not draft; relay the printed question to the user, wait",
        "update the brief's `## Design-side on-ramp` line, re-run",
        "check_queue_relation.py <brief-path>",
        "check_field_microstructure.py --brief <brief-path>",
        "check_field_microstructure.py <plan-path>",
        "check_seam_coverage.py <plan-path>",
        "check_scenario_coverage.py <change-folder> <plan>",
        "check_scenario_coverage.py --brief <brief> <plan>",
        "Up to 2 rounds",
        "Amending a PASS plan",
        "closed list",
        "Stamping the verdict",
        "Fixing a typo",
        "Filling a schema field",
        "skip note",
        "## Kickoff briefing",
        "After PASS and before SDD, kickoff is mandatory even for a small or obvious plan. Never skip it.",
        "Goal:",
        "Stage:",
        "plan_card.py <plan-path>",
        "## Language policy",
        "## Output contract",
        "## Task-flow diagram",
        "## Open Questions",
        "Files touched:",
        "Context paths:",
        "Acceptance:",
        "External surfaces:",
        "Independent:",
        "Status: pending",
        "Gloss:",
        "## Consuming a loom-design change-folder",
        "validate_spec_output.py",
        "TARGET repo's root",
        "Layer 0 — explicit handoff wins",
        "branch-slug match",
        "non-archived folder count",
        "Mandatory once bound",
        "Wrong-bind reversal trigger",
        "structural-clean ≠ critic-fresh-and-passed",
        "installed skill",
        "PASS_WITH_NOTES",
        "Exit 2",
        "Exit 3",
        "Exit 4",
        "scenario → task mapping",
        "Consumer read-only",
        "NEVER edit the producer's change-folder",
        "Coverage self-check",
        "paths + structured seed context",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing writing-plans essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["writing-plans"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
