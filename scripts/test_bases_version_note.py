# concern: user-facing Bases capability claims must carry the Obsidian 1.9+
# requirement, or an older-Obsidian user reads a capability the release cannot
# provide. Bases shipped as a core plugin in Obsidian 1.9 and a direct .base
# embed in a canvas card works from 1.9 (1.9.5 fixed only a refresh edge case
# for moved cards), so 1.9 is the real requirement; every doc in the change's
# Bases surface must qualify Bases with
# 1.9+ and none may state the superseded 1.13 note.
"""Standing graduated copy of the Bases version-note adversarial probe.

This is the graduated copy of the Bases version-note probe for change
2026-10-06-canvas-no-plugin-advanced-patterns (task W2-03, per the
review.probe-graduation gate): the probe went RED on that change, so it is
carried into the standing suite (`pytest scripts/`) that runs on every later
change. The evidence-store copy lives at
docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/evidence/probes/.

The document set below is the change's user-facing Bases surface. A file that
names the Bases capability without the 1.9 requirement is a defect: Bases
ships as a core plugin in Obsidian 1.9, and a direct .base embed in a canvas
card works from 1.9 (1.9.5 fixed only a refresh edge case for moved cards) —
so a capability list without the 1.9+
note advertises the feature with no floor at all, and any doc still carrying
the earlier (factually wrong) 1.13 note misstates the real requirement.
"""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

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

VERSION_MARKER = "1.9"


def unqualified_bases_claim(text: str) -> bool:
    """True when text advertises the Bases capability with no 1.9 marker."""
    return "Bases" in text and VERSION_MARKER not in text


@pytest.mark.parametrize("rel_path", DOCS)
def test_bases_readme_versioned(rel_path):
    """A doc naming Bases-in-canvas also states the Obsidian 1.9 requirement."""
    path = REPO_ROOT / rel_path
    assert path.is_file(), f"expected doc missing: {rel_path}"

    assert not unqualified_bases_claim(path.read_text(encoding="utf-8")), (
        f"{rel_path} advertises Bases-in-canvas without the {VERSION_MARKER}+ "
        "requirement"
    )


def test_bases_check_accepts():
    """The check clears a capability line that carries the version marker."""
    assert not unqualified_bases_claim(
        "zero-plugin advanced patterns (worldbuilding, Bases-in-canvas 1.9+)"
    )


def test_bases_check_rejects():
    """The check flags a capability line that omits the version marker."""
    assert unqualified_bases_claim(
        "zero-plugin advanced patterns (worldbuilding, Bases-in-canvas)"
    )
