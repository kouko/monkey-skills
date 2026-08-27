"""Static contract for the using-git-worktrees entrypoint compaction."""

import json
from pathlib import Path
import sys


SKILL = Path(__file__).resolve().parents[1] / "skills/using-git-worktrees/SKILL.md"
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import skill_compaction_preflight as preflight


def test_entrypoint_preserves_applicability_setup_create_remove_and_isolation():
    text = SKILL.read_text(encoding="utf-8")

    required = (
        "<SUBAGENT-STOP>",
        "## What git worktrees solve",
        "one `.git/` shared",
        "## When to use",
        "## When NOT to use",
        "No parallelism needed",
        "Shared filesystem only",
        "Submodule-heavy repo",
        "## The `.worktrees/` convention",
        ".worktrees/",
        "git check-ignore",
        "git worktree list",
        "nonzero stops setup — add and commit `.worktrees/` in `.gitignore` first",
        "refuse an existing path or a branch already attached to a worktree, but allow an existing unattached branch",
        "git worktree add -b feat/foo .worktrees/feat-foo main",
        "git fetch origin",
        "git worktree add .worktrees/feat-foo feat/foo",
        "git worktree remove .worktrees/feat-foo",
        "git worktree prune",
        "uncommitted changes",
        "--force",
        "one worktree and one branch per concurrent session",
        "confirm before removing",
        "## Cross-skill contract",
        "finishing-a-development-branch",
        "git-memory",
        "## Red Flags",
        '"I\'ll just stash and switch."',
        '"I\'ll clone the repo a second time."',
        "## What this skill does NOT do",
    )
    missing = [phrase for phrase in required if phrase not in text]
    assert not missing, f"missing using-git-worktrees essence: {missing}"

    frozen = json.loads(
        (REPO_ROOT / "docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-preflight.json")
        .read_text(encoding="utf-8")
    )["skills"]["using-git-worktrees"]
    current = preflight.snapshot_skill(SKILL.parent)
    assert current["frontmatter"] == frozen["frontmatter"]
    assert current["declared_dependencies"] == frozen["declared_dependencies"]
