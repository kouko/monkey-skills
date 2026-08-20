"""Report unlanded changes to the direction layer.

`docs/loom/DIRECTION.md`'s `## Now` section, plus one
`docs/loom/backlog/<name>.md` file per entry named there, are the
GOVERNING FILES this check watches. For each local branch other than
the base branch, a file counts as an unlanded change only when it is
in the intersection of two sets:

    - files the branch itself changed since its merge-base with the
      base branch (``git diff --name-only <merge-base>..<branch>``)
    - files whose content still differs from the base branch right now
      (``git diff --name-only <base> <branch>``)

Ancestry (``git merge-base --is-ancestor``) is deliberately NOT used:
under squash merge a landed branch's tip is not an ancestor of the
base branch, so ancestry misreports every branch as unmerged. The
intersection test above clears a squash-landed branch correctly,
because its content no longer differs from the base once landed.

This module shells out to git — `backlog_index.py` deliberately does
not (see its own comments at lines 60, 70-73, 502), and that boundary
is why this check lives in a separate module rather than a new flag on
the old one.

This check REPORTS; it never blocks or raises for an unhealthy repo
state — a missing `DIRECTION.md`, or a `DIRECTION.md` with no
`## Now` section, yields an empty list rather than an exception.

# grounding: four git plumbing surfaces used throughout this module —
# `diff --name-only`, `merge-base`, `for-each-ref --format=%(refname:short)`,
# `log -1 --format=%as` — one module-level cite covers all four, they
# are the same well-established git plumbing:
#   - `diff --name-only` + `merge-base`: in-repo precedent
#     review_scope.py:268 and review_scope.py:223 (same flags, same
#     purpose); also live-measured against this repo's own branches in
#     this task's plan (docs/loom/plans/2026-08-20-direction-queue-gate.md,
#     Task 1 `External surfaces`) — 6 branches sampled, intersection
#     test flagged 2 and cleared 4 correctly.
#   - `for-each-ref --format=%(refname:short)`: live-verified —
#     `git for-each-ref --format='%(refname:short)' refs/heads/` run
#     against this repo returned one short branch name per line (22
#     local branches, `main` among them), matching this module's use.
#   - `log -1 --format=%as`: live-verified — `git log -1 --format=%as
#     HEAD` run against this repo returned `2026-08-19`, an ISO date
#     with no extra formatting, matching this module's use.

Stdlib only.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_NOW_HEADING_RE = re.compile(r"^##\s+Now\s*$")
_HEADING_RE = re.compile(r"^##\s+")
_NOW_ENTRY_RE = re.compile(r"^-\s+(?P<name>.+?)\s+—\s+.*$")


def _git_lines(repo_root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _parse_now_entry_names(direction_text: str) -> list[str] | None:
    """Names listed under `## Now`, or ``None`` if there is no such
    heading at all (distinct from a heading present but empty)."""
    lines = direction_text.splitlines()
    in_now = False
    found_heading = False
    names: list[str] = []
    for line in lines:
        if _NOW_HEADING_RE.match(line):
            in_now = True
            found_heading = True
            continue
        if in_now and _HEADING_RE.match(line):
            break
        if in_now:
            match = _NOW_ENTRY_RE.match(line)
            if match:
                names.append(match.group("name"))
    return names if found_heading else None


def _governing_files(repo_root: Path) -> list[str]:
    """Repo-relative paths (posix separators, matching git's own
    ``diff --name-only`` output) of the files this check watches, or an
    empty list when the direction layer isn't set up (missing file, or
    no `## Now` section)."""
    direction_path = repo_root / "docs" / "loom" / "DIRECTION.md"
    if not direction_path.exists():
        return []
    now_names = _parse_now_entry_names(direction_path.read_text(encoding="utf-8"))
    if now_names is None:
        return []
    files = ["docs/loom/DIRECTION.md"]
    files.extend(f"docs/loom/backlog/{name}.md" for name in now_names)
    return files


def find_unlanded_direction_changes(
    repo_root: Path, base_branch: str = "main"
) -> list[str]:
    """Every governing-file change that a local branch (other than
    `base_branch`) still carries and the base branch does not.

    Returns formatted strings ``"<branch> — <path> (tip <date>)"``,
    one per (branch, path) hit, so one glance is enough to dismiss a
    false positive. Returns an empty list when the direction layer
    isn't set up — see `_governing_files`."""
    governing = set(_governing_files(repo_root))
    if not governing:
        return []

    branches = _git_lines(
        repo_root, "for-each-ref", "--format=%(refname:short)", "refs/heads/"
    )
    findings: list[str] = []
    for branch in branches:
        if branch == base_branch:
            continue
        try:
            merge_base = subprocess.run(
                ["git", "-C", str(repo_root), "merge-base", base_branch, branch],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except subprocess.CalledProcessError:
            continue
        branch_changed = set(
            _git_lines(repo_root, "diff", "--name-only", f"{merge_base}..{branch}")
        )
        still_differs = set(
            _git_lines(repo_root, "diff", "--name-only", base_branch, branch)
        )
        unlanded = branch_changed & still_differs & governing
        if not unlanded:
            continue
        tip_date = subprocess.run(
            ["git", "-C", str(repo_root), "log", "-1", "--format=%as", branch],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        for path in sorted(unlanded):
            findings.append(f"{branch} — {path} (tip {tip_date})")
    return findings
