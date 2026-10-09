"""Ownership guard for the obsidian-canvas rename of plugin-level docs
(loom change 2026-10-06-rename-canvas-skill, task W2-01, acceptance A2/A5).

W1-01 renamed the skill directory and W1-02 the per-skill cross-references.
What these tests check (and only this): the plugin-root and skill-index
documentation — the three plugin READMEs, the three skills/READMEs,
ATTRIBUTION.md and the CHANGELOG's new entry — name the renamed skill
`obsidian-canvas` and no longer carry the old id, while the CHANGELOG's
new entry and its historical entries record the rename / the old name by
design, and the historical records (docs/loom/2026-10-06-canvas-no-plugin-
advanced-patterns/, docs/skill-dogfood/, .worktrees/) keep the old name
untouched.

Per-skill READMEs, the router, the obsidian-research reference and the
skill's own SKILL.md belong to W1-01/W1-02; test-path updates belong to
W2-02 — deliberately out of scope here.
"""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
OBSIDIAN = REPO_ROOT / "obsidian"

PLUGIN_README_FILES = [
    OBSIDIAN / "README.md",
    OBSIDIAN / "README.ja.md",
    OBSIDIAN / "README.zh-TW.md",
]
SKILL_INDEX_FILES = [
    OBSIDIAN / "skills" / "README.md",
    OBSIDIAN / "skills" / "README.ja.md",
    OBSIDIAN / "skills" / "README.zh-TW.md",
]
ATTRIBUTION = REPO_ROOT / "ATTRIBUTION.md"
CHANGELOG = OBSIDIAN / "CHANGELOG.md"

OLD_ID = "obsidian-canvas-creator"
NEW_ID = "obsidian-canvas"
# The exact table-cell spellings, so the assertion cannot pass on the old id
# (which contains NEW_ID as a substring).
PLUGIN_TABLE_CELL = f"| `{NEW_ID}` |"      # backticked, e.g. `obsidian-canvas`
INDEX_TABLE_CELL = f"| {NEW_ID} |"         # bare, e.g. | obsidian-canvas |
TREE_LINE = f"{NEW_ID}/ #"                  # repository-structure tree entry
ATTRIBUTION_PATH = f"obsidian/skills/{NEW_ID}/"
NEW_CHANGELOG_HEADING = (
    f"## [3.24.0] — 2026-10-06 rename {OLD_ID} skill to {NEW_ID}"
)


def test_plugin_docs_use_new_name():
    """A2 positive: the six READMEs and ATTRIBUTION.md point at obsidian-canvas."""
    for readme in PLUGIN_README_FILES:
        text = readme.read_text(encoding="utf-8")
        assert PLUGIN_TABLE_CELL in text, (
            f"{readme.name} skill table row must be `` | `{NEW_ID}` | ``"
        )
        assert TREE_LINE in text, (
            f"{readme.name} repository tree must list `{NEW_ID}/`"
        )
    for readme in SKILL_INDEX_FILES:
        text = readme.read_text(encoding="utf-8")
        assert INDEX_TABLE_CELL in text, (
            f"{readme.name} attribution table row must be `| {NEW_ID} |`"
        )
    attribution = ATTRIBUTION.read_text(encoding="utf-8")
    assert ATTRIBUTION_PATH in attribution, (
        f"ATTRIBUTION.md must list `{ATTRIBUTION_PATH}`"
    )
    # The license file moved with the directory; the row's link follows it.
    assert f"[LICENSE]({ATTRIBUTION_PATH}LICENSE)" in attribution, (
        "ATTRIBUTION.md license link must resolve under the renamed path"
    )
    # MIT attribution and license cell survive the rename unchanged.
    assert "License: MIT, Copyright (c) 2025 Axton Liu" in attribution


def test_stale_name_absent_from_live_docs():
    """A2 negative: no live doc outside CHANGELOG carries the old id."""
    for readme in [*PLUGIN_README_FILES, *SKILL_INDEX_FILES]:
        text = readme.read_text(encoding="utf-8")
        assert OLD_ID not in text, (
            f"{readme.name} still names {OLD_ID}"
        )
    assert OLD_ID not in ATTRIBUTION.read_text(encoding="utf-8"), (
        f"ATTRIBUTION.md still names {OLD_ID}"
    )
    # CHANGELOG is the one sanctioned holder: the new rename entry at the
    # top and historical entries below it. Nothing above the new entry.
    changelog = CHANGELOG.read_text(encoding="utf-8").splitlines()
    heading_line = changelog.index(NEW_CHANGELOG_HEADING)
    assert heading_line == 6, (
        f"new CHANGELOG entry must sit directly under the preamble "
        f"(found at line {heading_line + 1})"
    )
    first_old = next(
        i for i, line in enumerate(changelog) if OLD_ID in line
    )
    assert first_old >= heading_line, (
        f"old id appears above the new rename entry (line {first_old + 1})"
    )


def test_docs_loom_and_worktrees_retain_old_name():
    """A5 positive: historical records keep the old name untouched."""
    loom_plan = (
        REPO_ROOT
        / "docs/loom/2026-10-06-canvas-no-plugin-advanced-patterns/plan.md"
    )
    assert OLD_ID in loom_plan.read_text(encoding="utf-8"), (
        "docs/loom historical plan must retain the old skill name"
    )
    dogfood_report = (
        REPO_ROOT / "docs/skill-dogfood/2026-06-17-ascii-graph/report.md"
    )
    # This report refers to the skill by its distractor-list shorthand
    # `canvas-creator`, not the full dir id — assert the token it uses.
    assert "canvas-creator" in dogfood_report.read_text(encoding="utf-8"), (
        "docs/skill-dogfood report must retain the old skill name"
    )
    worktrees = REPO_ROOT / ".worktrees"
    if not worktrees.is_dir():
        pytest.skip(".worktrees/ is untracked and absent in this checkout")
    assert any(
        OLD_ID in path.read_text(encoding="utf-8", errors="ignore")
        for path in worktrees.rglob("*")
        if path.is_file()
    ), ".worktrees/ old copies must still carry the old skill name"


def test_git_diff_shows_no_edits_to_historical_records():
    """A5 boundary: the branch diff touches no historical record path."""
    main_check = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "cat-file", "-e", "main"],
        capture_output=True,
    )
    if main_check.returncode != 0:
        pytest.skip("no `main` ref in this checkout to diff against")
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "diff", "--name-only", "main...HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout
    changed = set(line for line in out.splitlines() if line)
    # This change's own loom records are allowed in the diff; historical
    # records of prior changes are not. The whole change directory is
    # allowed so every artifact this change produces (plan, acceptance
    # report, attestation, evidence) passes the guard.
    own_prefix = "docs/loom/2026-10-06-rename-canvas-skill/"
    own_intent = "docs/loom/intent/2026-10-06-rename-canvas-skill.md"
    forbidden = {
        p for p in changed
        if (p.startswith("docs/loom/") and p != own_intent
            and not p.startswith(own_prefix))
        or p.startswith(".worktrees/")
        or p.startswith("docs/skill-dogfood/")
    }
    assert not forbidden, (
        f"branch diff edits historical records: {sorted(forbidden)}"
    )
