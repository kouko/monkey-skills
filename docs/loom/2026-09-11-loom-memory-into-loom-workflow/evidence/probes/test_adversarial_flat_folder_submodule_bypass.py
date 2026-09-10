"""Adversarial probe (surface 5): the flat-folder test's `git ls-files` blind spot.

`loom-workflow/skills/loom-memory/scripts/test_skill_contract.py::
test_skill_folder_is_flat_no_nested_subfolder` asks `git ls-files -- <skill
dir>` for what is tracked, then checks each tracked path is at most two
segments below the skill directory (`SKILL.md` plus one level of
subfolder). This is deliberately git-aware instead of filesystem-aware, to
avoid false positives from an untracked `__pycache__`.

`git ls-files` (without `--recurse-submodules`) does not descend into a
submodule's own tracked tree — it reports the submodule's mount point as
ONE gitlink entry, e.g. `skills/loom-memory/sub`, with no indication of
anything nested inside it. A skill directory that ships a submodule at
exactly one level of nesting therefore reads as depth 1 to this test's
logic — passing cleanly — while the submodule's own tree, checked out by
any ordinary `git clone --recurse-submodules` (or a later `git submodule
update --init`), can nest arbitrarily deep on disk. The flat-folder
contract this test exists to enforce is violated by real shipped content
the test never sees.

Run:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
        docs/loom/2026-09-11-loom-memory-into-loom-workflow/evidence/probes/test_adversarial_flat_folder_submodule_bypass.py -v -s
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def _git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=True,
    )


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git("init", "-q", cwd=path)
    _git("config", "user.email", "a@b.c", cwd=path)
    _git("config", "user.name", "tester", cwd=path)


def _skill_folder_flat_check(repo_root: Path, skill_dir_rel: str) -> list[str]:
    """The exact logic under
    `test_skill_folder_is_flat_no_nested_subfolder`, reimplemented against
    an arbitrary (repo_root, skill_dir) pair so it can be pointed at a
    synthetic repo. Returns the list of tracked paths that violate the
    depth<=2 rule — empty means "test would pass"."""
    tracked = subprocess.run(
        ["git", "ls-files", "--", skill_dir_rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=True,
    ).stdout.split()
    violations = []
    for rel in tracked:
        depth = Path(rel).relative_to(skill_dir_rel).parts
        if len(depth) > 2:
            violations.append(rel)
    return violations


def test_flat_folder_ls_files_check_misses_deeply_nested_content_inside_a_submodule(tmp_path):
    """A skill directory ships a git submodule one level down. The
    submodule's own history contains a file nested four levels deep. `git
    ls-files` on the host repo reports only the submodule's single gitlink
    entry, so the depth check the real test performs sees no violation —
    while `git clone --recurse-submodules` (the standard way to pull a
    repo with submodules) genuinely checks out that four-deep file inside
    the skill directory."""
    submodule_src = tmp_path / "submodule-src"
    _init_repo(submodule_src)
    deep_dir = submodule_src / "deep" / "nested" / "dir"
    deep_dir.mkdir(parents=True)
    (deep_dir / "file.txt").write_text("shipped content, four levels deep\n", encoding="utf-8")
    _git("add", "-A", cwd=submodule_src)
    _git("commit", "-q", "-m", "init", cwd=submodule_src)

    host_repo = tmp_path / "host-repo"
    _init_repo(host_repo)
    skill_dir = host_repo / "skills" / "loom-memory"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (skill_dir / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
    _git("add", "-A", cwd=host_repo)
    _git("commit", "-q", "-m", "init skill", cwd=host_repo)

    subprocess.run(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            "-q",
            str(submodule_src),
            "skills/loom-memory/sub",
        ],
        cwd=host_repo,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=True,
    )
    _git("commit", "-q", "-m", "add submodule under skill", cwd=host_repo)

    # Prove the submodule's own tracked content is genuinely nested four
    # levels deep on disk (what a --recurse-submodules clone ships).
    shipped_deep_file = host_repo / "skills" / "loom-memory" / "sub" / "deep" / "nested" / "dir" / "file.txt"
    assert shipped_deep_file.is_file()

    violations = _skill_folder_flat_check(host_repo, "skills/loom-memory")

    ls_files_output = subprocess.run(
        ["git", "ls-files", "--", "skills/loom-memory"],
        cwd=host_repo,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=True,
    ).stdout.split()

    # The defect: ls-files reports the submodule as a single shallow
    # entry, so the depth check finds nothing to flag.
    assert "skills/loom-memory/sub" in ls_files_output
    assert not any("deep" in line for line in ls_files_output), (
        "expected git ls-files to never mention the submodule's own "
        "nested tree at all"
    )
    assert violations == [], (
        "expected the ls-files-based depth check to miss the submodule's "
        "real four-level nesting (this documents the surviving gap); if "
        "this now fails, the check has been hardened against submodules"
    )
