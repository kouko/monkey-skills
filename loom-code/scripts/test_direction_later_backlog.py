"""Task 8 (docs/loom/plans/2026-08-20-north-star-serves-link.md) --
DIRECTION.md's three `## Later` lines become OPEN backlog entries and the
`## Later` section is removed. `## Now`, `## Next`, and `## On-ramp
standing choices` are untouched machine-read contracts.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DIRECTION_PATH = REPO_ROOT / "docs" / "loom" / "DIRECTION.md"
BACKLOG_DIR = REPO_ROOT / "docs" / "loom" / "backlog"

# The three lane themes the removed `## Later` lines named, transcribed
# verbatim from the section this test asserts is gone.
LATER_THEMES = (
    "投資線營運指標敘事層",
    "loom 機制 Codex 移植線",
    "obsidian wiki 知識線深化",
)


def test_direction_has_no_later_heading_but_keeps_the_other_three_sections():
    text = DIRECTION_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    assert not any(line.strip() == "## Later" for line in lines), (
        "docs/loom/DIRECTION.md still has a '## Later' heading"
    )
    for heading in ("## Now", "## Next", "## On-ramp standing choices"):
        assert any(line.strip() == heading for line in lines), (
            f"docs/loom/DIRECTION.md is missing required heading {heading!r}"
        )


def test_three_open_backlog_entries_carry_the_later_lane_themes():
    entry_texts = [
        p.read_text(encoding="utf-8") for p in BACKLOG_DIR.glob("*.md")
    ]

    for theme in LATER_THEMES:
        matches = [
            t
            for t in entry_texts
            if theme in t and "status: OPEN" in t
        ]
        assert matches, (
            f"no OPEN backlog entry found carrying the lane theme {theme!r}"
        )
