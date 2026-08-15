"""T8 drift guard: the brief-before-fork template copy in
loom-design/skills/using-loom-design/SKILL.md
must be replaced by a one-line pointer to the SSOT section
`## Brief before a complex fork` in
loom-code/hooks/family-reception.md.

WHY this test exists: the full template copy (≥3 trade-offs / ≥2
implementation paths / architectural blast radius) drifted from the
canonical source in family-reception.md. The dedup removes the copy
and leaves a pointer; this test pins both halves — pointer present,
copy gone — so a future edit that re-introduces the threshold text (or
drops the pointer) fails loud instead of silently drifting again.

Two assertions, each load-bearing:
- POINTER present  — the router tells the reader where the rule lives.
- THRESHOLD absent — the verbatim trigger text is not duplicated here;
  the copy was removed, not merely augmented alongside the pointer.

check(root) takes an arbitrary root so RED verification can run against
an extracted, perturbed temp copy without touching the real tree (house
mutation/RED-on-extracted-copy pattern, mirroring
test_router_card_rule_tokens.py's non-vacuity test).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

TARGET = "loom-design/skills/using-loom-design/SKILL.md"

POINTER = "loom-code/hooks/family-reception.md §Brief before a complex fork"
THRESHOLD = "≥3 trade-offs"


def check(root: Path) -> None:
    """Assert the SKILL.md points at the SSOT AND no longer carries the
    verbatim threshold phrase (the copy is removed, not augmented)."""
    text = (root / TARGET).read_text(encoding="utf-8")
    if POINTER not in text:
        raise AssertionError(
            f"pointer missing from {TARGET}: expected {POINTER!r}"
        )
    if THRESHOLD in text:
        raise AssertionError(
            f"verbatim threshold phrase {THRESHOLD!r} still present in "
            f"{TARGET} — the full template copy was not removed"
        )


def test_principles_points_at_source():
    check(REPO_ROOT)


def test_check_catches_reinserted_threshold(tmp_path):
    """Proves the THRESHOLD-absent assertion is load-bearing, not vacuous.

    Copies the real file into tmp_path, confirms the unmutated copy
    passes, then re-inserts the threshold phrase and shows check()
    raises naming the threshold.
    """
    src = REPO_ROOT / TARGET
    dst = tmp_path / TARGET
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    dst.write_text(text + "\n" + THRESHOLD + "\n", encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert THRESHOLD in message


def test_check_catches_dropped_pointer(tmp_path):
    """Proves the POINTER-present assertion is load-bearing, not vacuous.

    Copies the real file into tmp_path, confirms the unmutated copy
    passes, then strips the pointer out and shows check() raises naming
    the pointer.
    """
    src = REPO_ROOT / TARGET
    dst = tmp_path / TARGET
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

    check(tmp_path)  # baseline: unmutated copy passes

    text = dst.read_text(encoding="utf-8")
    assert POINTER in text
    dst.write_text(text.replace(POINTER, "REMOVED", 1), encoding="utf-8")

    with pytest.raises(AssertionError) as exc_info:
        check(tmp_path)

    message = str(exc_info.value)
    assert "pointer missing" in message
    assert POINTER in message