"""Adversarial probe (surface 5): the flat-folder test's `git ls-files` blind spot.

`loom-workflow/skills/loom-memory/scripts/test_skill_contract.py::
test_skill_folder_is_flat_no_nested_subfolder` used to ask `git ls-files --
<skill dir>` for what is tracked, then check each tracked path is at most
two segments below the skill directory (`SKILL.md` plus one level of
subfolder). This is deliberately git-aware instead of filesystem-aware, to
avoid false positives from an untracked `__pycache__`.

`git ls-files` (without `--recurse-submodules`) does not descend into a
submodule's own tracked tree — it reports the submodule's mount point as
ONE gitlink entry, e.g. `skills/loom-memory/sub`, with no indication of
anything nested inside it. A skill directory that ships a submodule at
exactly one level of nesting therefore used to read as depth 1 to this
test's logic — passing cleanly — while the submodule's own tree, checked
out by any ordinary `git clone --recurse-submodules` (or a later `git
submodule update --init`), can nest arbitrarily deep on disk. The
flat-folder contract this test exists to enforce was violated by real
shipped content the test never saw.

The fix uses `git ls-files --stage` instead, which reports each tracked
entry's mode, and flags a gitlink (mode `160000`) directly as a violation —
a skill ships files, not submodules — rather than trying to recurse into
it (which would depend on the clone's own submodule-init state to mean
anything).

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
    """The exact fixed logic under
    `test_skill_folder_is_flat_no_nested_subfolder` (`git ls-files
    --stage`, flagging a mode-`160000` gitlink directly), reimplemented
    against an arbitrary (repo_root, skill_dir) pair so it can be pointed
    at a synthetic repo. Returns the list of tracked paths that violate
    either the gitlink rule or the depth<=2 rule — empty means "test would
    pass"."""
    staged = subprocess.run(
        ["git", "ls-files", "--stage", "--", skill_dir_rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        check=True,
    ).stdout.splitlines()
    violations = []
    for line in staged:
        left, _, rel = line.partition("\t")
        mode = left.split()[0]
        if mode == "160000":
            violations.append(rel)
            continue
        depth = Path(rel).relative_to(skill_dir_rel).parts
        if len(depth) > 2:
            violations.append(rel)
    return violations


def test_flat_folder_gitlink_check_now_catches_a_submodule_mounted_under_the_skill(tmp_path):
    """A skill directory ships a git submodule one level down. The
    submodule's own history contains a file nested four levels deep. `git
    ls-files` (plain) on the host repo reports only the submodule's single
    gitlink entry — no visibility into what a `--recurse-submodules` clone
    would check out inside it — but the fixed check reads `git ls-files
    --stage` and flags that gitlink entry (mode `160000`) directly,
    without ever needing to see inside it."""
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

    # Plain `git ls-files` still reports the submodule as a single shallow
    # entry with no visibility into its own nested tree — the fixed check
    # does not rely on seeing that tree; it flags the gitlink itself.
    assert "skills/loom-memory/sub" in ls_files_output
    assert not any("deep" in line for line in ls_files_output), (
        "expected plain git ls-files to never mention the submodule's own "
        "nested tree at all"
    )
    assert violations == ["skills/loom-memory/sub"], (
        "expected the fixed --stage-based check to flag the submodule's "
        "gitlink directly; if this fails, the gitlink hardening regressed"
    )
