"""Mechanical marker-grep tests for the loom-memory same-branch timing rule.

RED-first: both tests below are expected to FAIL until the charter and
the finishing-a-development-branch pointer bullet are added.

Source: docs/loom/specs/2026-07-08-loom-memory-same-branch-timing.md
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

MEMORY_README = REPO_ROOT / "docs/loom/memory/README.md"
FINISHING_SKILL = REPO_ROOT / "loom-code/skills/finishing-a-development-branch/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_charter_has_when_to_record_section():
    """
    The charter (docs/loom/memory/README.md) must gain a `## When to
    record` section stating the same-branch timing rule.
    """
    text = _read(MEMORY_README)
    assert "## When to record" in text
    assert "same branch" in text
    assert "post-merge" in text


def test_finishing_branch_points_at_when_to_record():
    """
    finishing-a-development-branch/SKILL.md Step 8 must point at the
    charter's new section (pointer only) — it must NOT restate the
    charter's rule body verbatim (e.g. the literal phrase "never a
    separate post-merge branch" must live ONLY in the charter).
    """
    text = _read(FINISHING_SKILL)
    assert "docs/loom/memory/README.md" in text
    assert "When to record" in text
    assert "never a separate post-merge branch" not in text
