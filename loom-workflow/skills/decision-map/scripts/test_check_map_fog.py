"""Tests for check_map_fog.py — the fog-monotonicity gate.

WHY: map-format.md §Fog entries requires a base-ref fog id to only
shrink, graduate, or move to Out-of-scope — never silently vanish.
These tests pin the three legal transitions (shrink/graduate/
out-of-scope) as clean, the illegal transition (silent deletion) as a
violation, and the two operational edge cases (brand-new map, and an
unreadable repo).

Fixtures are REAL throwaway git repos: `git init` in `tmp_path`,
commit a base version of MAP.md on the default branch, branch off and
commit a modified version, then run the checker with HEAD on the
feature branch (mirrors how this gate runs in CI — comparing a
feature branch against its base).

External surfaces grounded (per
loom-code/skills/subagent-driven-development/standards/
external-surface-grounding.md):

- git plumbing used by check_map_fog.py (``git symbolic-ref
  refs/remotes/origin/HEAD``, ``git rev-parse --verify <ref>``, ``git
  merge-base <a> <b>``, ``git show <ref>:<path>``): source-(a) live
  verification — ``git --version`` reports ``git version 2.50.1
  (Apple Git-155)`` (run 2026-08-28); ``git symbolic-ref --help``
  confirms the one-argument form reads which ref a symbolic ref
  points at; ``git rev-parse --help``'s ``--verify`` section confirms
  it emits the resolved object name for exactly one valid ref
  argument and errors otherwise (the basis for `resolve_default_
  branch`'s existence probes); ``git merge-base --help`` confirms
  ``git merge-base <commit> <commit>`` finds a common ancestor of the
  two, non-zero exit when none exists; ``git show --help`` plus
  gitrevisions(7)'s ``<rev>:<path>`` syntax confirm ``git show
  <ref>:<path>`` reads a path's blob at that revision without
  touching the working tree. This suite additionally live-drives
  every one of these invocations against real throwaway repos built
  below (including the origin-only, master-only, and detached-HEAD
  fixtures), so a flag or behavior drift fails the suite instead of
  slipping past it.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import check_map_fog  # noqa: E402

MAP_ID = "wayfinder"

BASE_MAP_MD = """---
map-id: wayfinder
schema_version: 1
state: charting
---

## Destination

Chart the decision-map layer.

## Notes

Nothing special.

## Decisions-so-far

- We chose stdlib-only parsing (tickets/decision-a.md)

## Not-yet-specified (fog)

- F-1: how does the fog id survive a rename?
- F-2: what happens when a ticket graduates?
- F-3: does out-of-scope need its own section?

## Out-of-scope

## Parts

| Part | Join key | Status |
|---|---|---|
| Engine | `wayfinder / Part: Engine` | in-progress |
"""

TICKET_GRADUATED = """---
type: task
status: open
claim: null
graduated-from: F-2
---

What happens when a ticket graduates?
"""


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
    )


def _init_repo(repo_root: Path) -> None:
    _git(["init", "-b", "main"], repo_root)
    _git(["config", "user.email", "test@example.com"], repo_root)
    _git(["config", "user.name", "Test"], repo_root)


def _map_dir(repo_root: Path) -> Path:
    return repo_root / "docs" / "loom" / "maps" / MAP_ID


def _commit_base(repo_root: Path, map_md_text: str) -> None:
    _write(_map_dir(repo_root) / "MAP.md", map_md_text)
    _git(["add", "."], repo_root)
    _git(["commit", "-m", "base map"], repo_root)


def _branch_and_commit_current(repo_root: Path, map_md_text: str, ticket: tuple[str, str] | None = None) -> None:
    _git(["checkout", "-b", "feature"], repo_root)
    _write(_map_dir(repo_root) / "MAP.md", map_md_text)
    if ticket is not None:
        slug, text = ticket
        _write(_map_dir(repo_root) / "tickets" / f"{slug}.md", text)
    _git(["add", "."], repo_root)
    _git(["commit", "-m", "current map"], repo_root)


def _rewrite_fog_section(map_md_text: str, new_fog_body: str, new_out_of_scope_body: str = "") -> str:
    return map_md_text.replace(
        "## Not-yet-specified (fog)\n\n"
        "- F-1: how does the fog id survive a rename?\n"
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n\n"
        "## Out-of-scope\n",
        f"## Not-yet-specified (fog)\n\n{new_fog_body}\n"
        f"## Out-of-scope\n\n{new_out_of_scope_body}",
    )


def test_flags_vanished_fog_entry(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    # F-1 silently deleted: not shrunk, not graduated, not out-of-scope.
    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _branch_and_commit_current(repo_root, current)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 2
    assert "F-1" in message


def test_shrink_is_clean(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    # F-1's text narrows but the id stays.
    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-1: fog id survival?\n"
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _branch_and_commit_current(repo_root, current)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 0


def test_graduation_is_clean(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    # F-2 removed from fog, but a ticket records graduated-from: F-2.
    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-1: how does the fog id survive a rename?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _branch_and_commit_current(
        repo_root, current, ticket=("decision-b", TICKET_GRADUATED)
    )

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 0


def test_out_of_scope_move_is_clean(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    # F-3 removed from fog, relocated verbatim (id intact) to Out-of-scope.
    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-1: how does the fog id survive a rename?\n"
        "- F-2: what happens when a ticket graduates?\n",
        "- F-3: does out-of-scope need its own section?\n",
    )
    _branch_and_commit_current(repo_root, current)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 0


def test_new_map_with_no_base_version_is_clean(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    # Base commit has no MAP.md at all for this map-id.
    _write(repo_root / "README.md", "placeholder\n")
    _git(["add", "."], repo_root)
    _git(["commit", "-m", "init"], repo_root)

    _branch_and_commit_current(repo_root, BASE_MAP_MD)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 0
    assert "new map" in message


def test_unreadable_repo_is_operational_error(tmp_path: Path) -> None:
    not_a_repo = tmp_path / "not-a-repo"
    map_dir = not_a_repo / "docs" / "loom" / "maps" / MAP_ID
    _write(map_dir / "MAP.md", BASE_MAP_MD)

    code, message = check_map_fog.check_fog_monotonicity(
        map_dir, not_a_repo, base_ref=None
    )
    assert code == 1


def test_missing_map_directory_is_operational_error(tmp_path: Path) -> None:
    code, message = check_map_fog.check_fog_monotonicity(
        tmp_path / "no-such-map", tmp_path, base_ref=None
    )
    assert code == 1


def test_origin_only_default_branch_falls_back_to_remote_ref(tmp_path: Path) -> None:
    """origin/HEAD's symbolic-ref resolves to `main`, but no LOCAL
    `main` branch exists — only `refs/remotes/origin/main`. This is
    the realistic post-clone-and-delete-local-branch shape: the
    default branch is known only as a remote-tracking ref.
    `resolve_default_branch` must fall back to the `origin/<name>`
    form rather than handing `merge-base` a name with no local ref
    (which fails and surfaces as an operational error instead of
    running the gate)."""
    origin_repo = tmp_path / "origin"
    origin_repo.mkdir()
    _init_repo(origin_repo)
    _commit_base(origin_repo, BASE_MAP_MD)

    local_repo = tmp_path / "local"
    _git(["clone", str(origin_repo), str(local_repo)], tmp_path)
    _git(["checkout", "-b", "feature"], local_repo)
    _git(["branch", "-D", "main"], local_repo)  # only origin/main remains

    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _write(_map_dir(local_repo) / "MAP.md", current)
    _git(["add", "."], local_repo)
    _git(["commit", "-m", "current map"], local_repo)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(local_repo), local_repo, base_ref=None
    )
    assert code == 2
    assert "F-1" in message


def test_master_only_repo_resolves_default_branch(tmp_path: Path) -> None:
    """No origin remote at all; the only branch is a local `master`.
    `resolve_default_branch`'s fallback loop must find it directly via
    `refs/heads/master` (documents the local-only-repo shape, distinct
    from the origin-only shape above)."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _git(["init", "-b", "master"], repo_root)
    _git(["config", "user.email", "test@example.com"], repo_root)
    _git(["config", "user.name", "Test"], repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _git(["checkout", "-b", "feature"], repo_root)
    _write(_map_dir(repo_root) / "MAP.md", current)
    _git(["add", "."], repo_root)
    _git(["commit", "-m", "current map"], repo_root)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 2
    assert "F-1" in message


def test_detached_head_still_resolves_against_default_branch(tmp_path: Path) -> None:
    """HEAD detached at the vanishing-fog commit (no branch name at
    all). `resolve_base_ref` only ever needs `HEAD` as a revision for
    `merge-base`, which resolves from a detached HEAD exactly like a
    branch tip — chosen behavior: detachment does not change the
    gate's verdict."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _init_repo(repo_root)
    _commit_base(repo_root, BASE_MAP_MD)

    current = _rewrite_fog_section(
        BASE_MAP_MD,
        "- F-2: what happens when a ticket graduates?\n"
        "- F-3: does out-of-scope need its own section?\n",
    )
    _branch_and_commit_current(repo_root, current)
    detach_target = subprocess.run(
        ["git", "rev-parse", "feature"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    _git(["checkout", "--detach", detach_target], repo_root)

    code, message = check_map_fog.check_fog_monotonicity(
        _map_dir(repo_root), repo_root, base_ref=None
    )
    assert code == 2
    assert "F-1" in message
