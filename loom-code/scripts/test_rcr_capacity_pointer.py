"""Prose-pin tests for Task 8 (E-3 capacity-recovery pointer within the word cap).

Pins two edits to requesting-code-review/SKILL.md:
  (a) Step 2 — trim the unpinned version tag from the code-reviewer panel
      dispatch paragraph.
  (b) Step 3 — insert a capacity-recovery pointer sentence immediately
      after the dead-arm anchor sentence.

Net word delta of the two edits is 0 (-5 trim, +5 pointer), so the file
must stay within CHK-SKL-010's 4,500-word hard cap.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_MD = REPO_ROOT / "loom-code" / "skills" / "requesting-code-review" / "SKILL.md"

DEAD_ARM_ANCHOR = "a single-arm verdict is degraded evidence — G4 measured why)."

CAPACITY_POINTER = (
    "Capacity-error recovery: "
    "[`dispatch-hygiene-notes.md`]"
    "(../subagent-driven-development/references/dispatch-hygiene-notes.md) "
    "§Capacity-error recovery."
)

OLD_VERSION_TAG = "; plugin-level agent, v0.6.0 / P15-12 Phase 2, at"
NEW_VERSION_TAG = "; plugin-level agent at"


def _normalized_text() -> str:
    """Whitespace-normalized SKILL.md text (collapses the source's hard
    wraps so a contiguous-sentence match doesn't depend on line breaks)."""
    text = SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_dead_arm_anchor_sentence_present():
    """Positive-fact control: the dead-arm anchor sentence pre-exists (not
    introduced by this task) — proves the pointer test below is not vacuous."""
    assert DEAD_ARM_ANCHOR in _normalized_text()


def test_capacity_recovery_pointer_immediately_after_dead_arm_anchor():
    """Task 8(b): the capacity-recovery pointer sentence appears contiguous
    (whitespace-normalized) immediately after the dead-arm anchor sentence."""
    normalized = _normalized_text()
    expected = f"{DEAD_ARM_ANCHOR} {CAPACITY_POINTER}"
    assert expected in normalized, (
        f"expected contiguous pointer sentence not found:\n{expected!r}"
    )


def test_version_tag_trimmed_from_panel_dispatch_paragraph():
    """Task 8(a): the unpinned version tag is removed exactly once, replaced
    by the untagged form, in the Step 2 panel dispatch paragraph."""
    text = SKILL_MD.read_text(encoding="utf-8")
    assert OLD_VERSION_TAG not in text
    assert text.count(NEW_VERSION_TAG) == 1


def test_skill_md_word_count_within_chk_skl_010_cap():
    """Net word delta of the two Task 8 edits must be 0, keeping SKILL.md
    within the CHK-SKL-010 hard cap of 4,500 words."""
    text = SKILL_MD.read_text(encoding="utf-8")
    word_count = len(text.split())
    assert word_count <= 4500, f"SKILL.md is {word_count} words, over the 4500 cap"


def test_check_skill_structure_reports_no_chk_skl_010_violation():
    """End-to-end: the repo's own word-cap checker must report no
    CHK-SKL-010 violation for requesting-code-review under loom-code."""
    checker = REPO_ROOT / "scripts" / "check-skill-structure.py"
    result = subprocess.run(
        [sys.executable, str(checker), "loom-code"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    violation_lines = [
        line
        for line in result.stdout.splitlines()
        if "CHK-SKL-010" in line and "requesting-code-review" in line
    ]
    assert not violation_lines, f"CHK-SKL-010 violation found:\n{result.stdout}"
