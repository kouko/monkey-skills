"""Ownership guard for the obsidian-canvas skill rename cross-references
(loom change 2026-10-06-rename-canvas-skill, task W1-02, acceptance A2).

W1-01 renamed the skill directory and SKILL.md identity to `obsidian-canvas`.
What these tests check (and only this): the live repo cross-references name
the new skill id — the using-obsidian router row, the obsidian-research
Related-skills entry, and the three per-skill README titles self-identify as
"Obsidian Canvas" — and that the Original Source attribution blocks survive
the rename with their axtonliu links intact.

Skill-index rows in obsidian/skills/README*.md, the plugin-root READMEs,
ATTRIBUTION.md and CHANGELOG.md belong to task W2-01 and are deliberately
out of scope here; historical records (docs/loom/, docs/skill-dogfood/,
.worktrees/) keep the old name by design.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = REPO_ROOT / "obsidian" / "skills"
CANVAS_DIR = SKILLS / "obsidian-canvas"

README_FILES = [
    CANVAS_DIR / "README.md",
    CANVAS_DIR / "README.ja.md",
    CANVAS_DIR / "README.zh-TW.md",
]
ROUTER = SKILLS / "using-obsidian" / "SKILL.md"
RESEARCH = SKILLS / "obsidian-research" / "SKILL.md"

OLD_ID = "obsidian-canvas-creator"
OLD_TITLE = "Canvas Creator"
NEW_TITLE = "# Obsidian Canvas"

# Attribution block content that must survive the rename (colons differ per
# language — en/ja use ": ", zh-TW uses "：" — so assert on the link text
# and the verbatim field values, not the separator).
ATTRIBUTION_SNIPPETS = [
    "## Original Source",
    "[axtonliu](https://github.com/axtonliu)",
    "[axtonliu/axton-obsidian-visual-skills](https://github.com/axtonliu/axton-obsidian-visual-skills)",
    "`obsidian-visual-skills`",
    "`axton-obsidian-visual-skills`",
]


def test_cross_refs_point_to_new_name():
    # The router table row must name the skill id that actually exists on
    # disk, and neither live cross-reference may carry the old id.
    assert (CANVAS_DIR / "SKILL.md").is_file(), (
        "router id `obsidian-canvas` must resolve to a skill directory"
    )
    for live_ref in (ROUTER, RESEARCH):
        text = live_ref.read_text(encoding="utf-8")
        assert OLD_ID not in text, f"{live_ref.name} still names {OLD_ID}"
        assert "`obsidian-canvas`" in text, (
            f"{live_ref.name} must reference the renamed skill "
            "(backticked exact form — `obsidian-canvas` is a substring of "
            "the old id, so a bare substring check cannot go red)"
        )
    # Each per-skill README self-identifies with the new name.
    for readme in README_FILES:
        text = readme.read_text(encoding="utf-8")
        first_line = text.splitlines()[0]
        assert first_line == NEW_TITLE, (
            f"{readme.name} title is {first_line!r}, expected {NEW_TITLE!r}"
        )
        assert OLD_ID not in text and OLD_TITLE not in text, (
            f"{readme.name} still self-identifies with the old skill name"
        )


def test_attribution_source_links_kept():
    for readme in README_FILES:
        text = readme.read_text(encoding="utf-8")
        missing = [s for s in ATTRIBUTION_SNIPPETS if s not in text]
        assert not missing, (
            f"{readme.name} lost Original Source attribution: {missing}"
        )
