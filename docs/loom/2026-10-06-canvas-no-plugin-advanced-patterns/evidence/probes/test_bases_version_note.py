# concern: user-facing Bases capability claims must carry the Obsidian 1.13+
# requirement, or an older-Obsidian user reads a capability the release cannot
# provide. The plugin READMEs, SKILL.md and the reference all qualify Bases with
# 1.13+; the three per-skill READMEs list "Bases-in-canvas" with no version at
# all, so the change is not internally consistent about its own version note.
"""Adversarial probe: every doc that advertises Bases-in-canvas qualifies it.

The document set below is the change's user-facing Bases surface. A file that
names the Bases capability without the 1.13 requirement is a defect: the whole
point of the note (spec Risk 3 / plan Risk 3) is that Bases-in-canvas silently
fails on Obsidian < 1.13, and a capability list without the note advertises it
just as unconditionally.

RED against the change as it stands: obsidian/skills/obsidian-canvas-creator
README.md / README.ja.md / README.zh-TW.md name Bases-in-canvas with no 1.13.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]

DOCS = [
    "obsidian/README.md",
    "obsidian/README.ja.md",
    "obsidian/README.zh-TW.md",
    "obsidian/skills/README.md",
    "obsidian/skills/obsidian-canvas-creator/README.md",
    "obsidian/skills/obsidian-canvas-creator/README.ja.md",
    "obsidian/skills/obsidian-canvas-creator/README.zh-TW.md",
    "obsidian/skills/obsidian-canvas-creator/SKILL.md",
    "obsidian/skills/obsidian-canvas-creator/references/no-plugin-patterns.md",
    "obsidian/CHANGELOG.md",
]

VERSION_MARKER = "1.13"


def unqualified_bases_claim(text: str) -> bool:
    """True when text advertises the Bases capability with no 1.13 marker."""
    return "Bases" in text and VERSION_MARKER not in text


@pytest.mark.parametrize("rel_path", DOCS)
def test_bases_readme_versioned(rel_path):
    """A doc naming Bases-in-canvas also states the Obsidian 1.13 requirement."""
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"expected doc missing: {rel_path}"

    assert not unqualified_bases_claim(path.read_text(encoding="utf-8")), (
        f"{rel_path} advertises Bases-in-canvas without the {VERSION_MARKER}+ "
        "requirement"
    )


def test_bases_check_accepts():
    """The check clears a capability line that carries the version marker."""
    assert not unqualified_bases_claim(
        "zero-plugin advanced patterns (worldbuilding, Bases-in-canvas 1.13+)"
    )


def test_bases_check_rejects():
    """The check flags a capability line that omits the version marker."""
    assert unqualified_bases_claim(
        "zero-plugin advanced patterns (worldbuilding, Bases-in-canvas)"
    )
