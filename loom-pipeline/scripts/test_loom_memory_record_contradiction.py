"""RED-then-GREEN test for loom-memory's §record contradiction-check step.

Pins O6a: the record verb must gain a mandatory contradiction-check step
between classify and write — grep the store for entries the new fact
contradicts, and on a hit update/replace the old entry instead of adding
a contradicting sibling.

Source: docs/loom/plans/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md
(Task 8) and docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md
(Smallest End State #5).

Scoped per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md:
assertions run against the §record section slice only (between the
"## record" and "## recall" headings), not the whole file — the
neighboring recall step already contains the generic phrase "grep the
store file bodies", so a whole-file substring check would false-green.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SKILL_MD = REPO_ROOT / "loom-pipeline/skills/loom-memory/SKILL.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _record_section(text: str) -> str:
    start = text.index("## record")
    end = text.index("## recall")
    assert start < end, "record section must precede recall section"
    return text[start:end]


def test_record_section_has_contradiction_check_step():
    """
    The §record section must contain a contradiction-check step: grep
    the store for entries the new fact contradicts, and on a hit,
    update or replace the old entry instead of adding a contradicting
    sibling.
    """
    record = _record_section(_read(SKILL_MD))
    assert "contradict" in record
    assert "sibling" in record
    assert "grep" in record


def test_contradiction_check_step_is_between_classify_and_write():
    """
    The new step must sit between the classify step and the write
    step (per the task's "between classify and write" placement), not
    appended after write/append/re-verify.
    """
    record = _record_section(_read(SKILL_MD))
    classify_pos = record.index("Classify against the charter")
    contradict_pos = record.index("contradict")
    write_pos = record.index("Write `<slug>.md`")
    assert classify_pos < contradict_pos < write_pos


def test_contradiction_check_points_at_git_memory_doctrine_not_copy():
    """
    Mirrors git-memory's backward-pointing `Supersedes:` doctrine by
    pointer, per the family anti-copy convention (SSOT section above)
    — the step must cite the standards file path, not restate its
    table.
    """
    record = _record_section(_read(SKILL_MD))
    assert "memory-conventions.md" in record


def test_skill_version_bumped_to_0_2_0():
    """
    Frontmatter version must bump 0.1.0 -> 0.2.0 (skill content
    changed).
    """
    text = _read(SKILL_MD)
    frontmatter = text[: text.index("---", 3)]
    assert "version: 0.2.0" in frontmatter
