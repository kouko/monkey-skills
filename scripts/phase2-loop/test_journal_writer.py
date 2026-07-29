from pathlib import Path

import pytest

from journal_writer import append_journal_line

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_CAMPAIGN_DOC = REPO_ROOT / "docs" / "dbt-wiki-quality-campaign.md"

NEW_LINE = "- 2026-07-11: nightly loop appended this journal entry."


def _section_bounds(text: str, heading: str) -> tuple[int, int]:
    """Return (start, end) line indices of the section under `heading` (end exclusive)."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.strip() == heading)
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## ") or lines[i].startswith("# "):
            end = i
            break
    return start, end


def test_appends_one_line_to_end_of_journal_section(tmp_path):
    original = REAL_CAMPAIGN_DOC.read_text(encoding="utf-8")
    doc = tmp_path / "campaign.md"
    doc.write_text(original, encoding="utf-8")

    append_journal_line(doc, NEW_LINE)

    updated = doc.read_text(encoding="utf-8")

    # Exactly one new line added.
    assert len(updated.splitlines()) == len(original.splitlines()) + 1

    # All prior content preserved byte-identically (Journal is the last section,
    # so the append lands at true EOF and the original is an exact prefix).
    assert updated.startswith(original)

    # The new line is the LAST line of the ## Journal section specifically.
    start, end = _section_bounds(updated, "## Journal")
    assert updated.splitlines()[end - 1] == NEW_LINE


def test_locates_by_heading_not_eof(tmp_path):
    original = REAL_CAMPAIGN_DOC.read_text(encoding="utf-8")
    dummy_section = "\n## Some Later Section\n\n- a dummy trailing section\n"
    seeded = original + dummy_section

    # Capture the seeded doc's last Journal bullet dynamically -- do not
    # hard-code its live text, which this module's own job is to change.
    # Skip trailing blank lines before the next heading to land on the last
    # actual content line (mirrors journal_writer.py's own boundary logic).
    seeded_journal_start, seeded_journal_end = _section_bounds(seeded, "## Journal")
    seeded_lines = seeded.splitlines()
    _last = seeded_journal_end - 1
    while _last > seeded_journal_start and not seeded_lines[_last].strip():
        _last -= 1
    original_last_journal_line = seeded_lines[_last]

    doc = tmp_path / "campaign.md"
    doc.write_text(seeded, encoding="utf-8")

    append_journal_line(doc, NEW_LINE)

    updated = doc.read_text(encoding="utf-8")
    lines = updated.splitlines()

    assert len(lines) == len(seeded.splitlines()) + 1

    # New line lands INSIDE ## Journal (by heading, not at true EOF), and
    # before the dummy later section.
    journal_start, journal_end = _section_bounds(updated, "## Journal")
    new_idx = lines.index(NEW_LINE)
    dummy_idx = lines.index("## Some Later Section")

    assert journal_start < new_idx < journal_end
    assert new_idx < dummy_idx

    # It sits immediately after the last existing Journal bullet (captured
    # dynamically above, not literal-matched against today's doc content).
    assert lines[new_idx - 1] == original_last_journal_line

    # The dummy section content is untouched and still after the new line.
    assert "- a dummy trailing section" in lines[dummy_idx:]
