"""T11 — subagent-driven-development SKILL.md points at the brief-before-fork
SSOT; the full template copy is gone (replaced, not augmented).

Plan: docs/loom/plans/2026-08-15-plain-relay-contract.md Task 11.
RED: fails on the unedited repo (the full copy still carries the threshold
phrase, and no pointer to the family-reception SSOT exists).
GREEN: the copy is replaced by a one-line pointer to
`loom-code/hooks/family-reception.md §Brief before a complex fork`.
"""
from pathlib import Path
import shutil

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SDD_SKILL = "loom-code/skills/subagent-driven-development/SKILL.md"
POINTER_TARGET = "family-reception.md"
SSOT_HEADING = "Brief before a complex fork"
# The verbatim threshold phrase that lived in the full template copy (line 40).
# Its presence means the copy is still in the file (augmented, not replaced).
REMOVED_THRESHOLD = "≥3 trade-offs"


def check(root: Path) -> None:
    """Assert SDD SKILL.md carries the pointer AND has dropped the copy."""
    text = (root / SDD_SKILL).read_text(encoding="utf-8")
    assert POINTER_TARGET in text, (
        f"{SDD_SKILL} must point at {POINTER_TARGET} §{SSOT_HEADING}"
    )
    assert SSOT_HEADING in text, (
        f"{SDD_SKILL} must name the §{SSOT_HEADING} heading of the SSOT"
    )
    assert REMOVED_THRESHOLD not in text, (
        f"duplicated threshold phrase {REMOVED_THRESHOLD!r} still present in "
        f"{SDD_SKILL} — copy must be replaced by the pointer, not kept alongside"
    )


def test_sdd_points_at_source():
    check(REPO_ROOT)


def test_check_catches_a_reinserted_threshold(tmp_path):
    """Non-vacuity: re-inserting the threshold phrase flips check() red.

    Mirrors the house RED-on-extracted-copy pattern
    (test_router_card_rule_tokens.py:106-139): copy the real file into an
    isolated tmp_path, confirm the baseline passes, mutate by re-inserting
    the removed phrase, and show check() actually raises naming it.
    """
    dst = tmp_path / SDD_SKILL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / SDD_SKILL, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated = dst.read_text(encoding="utf-8")
    assert REMOVED_THRESHOLD not in mutated
    dst.write_text(mutated + f"\n{REMOVED_THRESHOLD}\n", encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)
    assert REMOVED_THRESHOLD in str(exc_info.value)