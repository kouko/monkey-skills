"""T6: dedup brief-before-fork — using-loom-discovery points at the SSOT.

The 6 router/skill copies of the brief-before-fork trigger template are
collapsed to one source (`loom-pipeline/hooks/family-reception.md
§Brief before a complex fork`, established by T5) + 6 pointers. This
test covers the using-loom-discovery copy.

WHY this test exists: a dedup that only *adds* a pointer while leaving
the verbatim threshold copy in place is not a dedup — it doubles the
surface that can drift. The test asserts BOTH (a) the pointer is
present AND (b) the verbatim threshold phrase `≥3 trade-offs` is GONE
from the file (the copy was removed, not just augmented). The
non-vacuity test proves the "absent" assertion is load-bearing by
re-inserting the threshold phrase into a tmp_path copy and showing
the check raises.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

SKILL_REL = "loom-discovery/skills/using-loom-discovery/SKILL.md"

# The pointer must name the SSOT file + section.
POINTER_NEEDLE = "family-reception.md"
SECTION_NEEDLE = "Brief before a complex fork"

# The verbatim threshold phrase from the old full copy — its presence
# means the copy was NOT removed (dedup failed).
THRESHOLD_PHRASE = "≥3 trade-offs"


def check(root: Path) -> None:
    """Assert the SKILL.md points at the SSOT AND dropped the threshold copy."""
    text = (root / SKILL_REL).read_text(encoding="utf-8")

    if POINTER_NEEDLE not in text:
        raise AssertionError(
            f"{SKILL_REL}: pointer to {POINTER_NEEDLE!r} not found — "
            "the SSOT pointer is missing"
        )
    if SECTION_NEEDLE not in text:
        raise AssertionError(
            f"{SKILL_REL}: section name {SECTION_NEEDLE!r} not found — "
            "the pointer must name §Brief before a complex fork"
        )
    if THRESHOLD_PHRASE in text:
        raise AssertionError(
            f"{SKILL_REL}: verbatim threshold phrase {THRESHOLD_PHRASE!r} "
            "still present — the full copy was not removed (dedup failed; "
            "pointer was added alongside the copy instead of replacing it)"
        )


def test_discovery_points_at_source():
    check(REPO_ROOT)


def test_check_catches_a_reinserted_threshold_phrase(tmp_path):
    """Proves check() is load-bearing, not vacuous.

    The real tree currently satisfies check() exactly, so the test above
    alone would stay green even if the "absent" assertion were a no-op.
    This test extracts the SKILL.md into an isolated tmp_path copy (zero
    mutation residue in the real tree — house RED-on-extracted-copy
    pattern), re-inserts the threshold phrase, and shows check() raises,
    naming the threshold phrase.
    """
    src = REPO_ROOT / SKILL_REL
    dst = tmp_path / SKILL_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    mutated = dst.read_text(encoding="utf-8")
    assert THRESHOLD_PHRASE not in mutated
    dst.write_text(
        mutated.replace(
            SECTION_NEEDLE,
            SECTION_NEEDLE + " (old copy: " + THRESHOLD_PHRASE + ")",
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert THRESHOLD_PHRASE in message
    assert SKILL_REL in message