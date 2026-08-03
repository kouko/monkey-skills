"""Review-scope resolver: a freshness verdict on a branch's merge-base.

Task 2 of this module's build: `check_freshness` derives a fetch target
from `default_branch_ref`'s revision name, fetches that ref narrowly, and
reports whether the branch's merge-base with the default branch is the
remote's current tip. It REPORTS only — it never refuses and never exits;
turning a non-fresh result into a refusal (and the file-list resolution +
CLI entry point) is later work on this module.

This module writes its own stdlib `subprocess` git helper rather than
importing `loom_gate_markers._git` — that name is private, and reaching
for a second private cross-module name would recommit the dependency the
`default_branch_ref` promotion (this repo's Task 1) exists to remove.

§Pinned local-ref rule (transcribed verbatim):

default_branch_ref returns a revision NAME, not a fetch target: either
`origin/<branch>` (origin/HEAD, prefix stripped) or a bare local `main`
/ `master`, or None. A return with no remote component is a LOCAL-ONLY
ref: comparing against it answers "am I current with my own local main",
which is a false all-clear. Local-only is a freshness FAILURE, never a
fresh verdict.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from loom_gate_markers import default_branch_ref

# The fetch is the only network call on this path. Unbounded, a dead
# remote hangs a review indefinitely, which is worse than failing it —
# there is no existing timeout convention to inherit (loom_gate_markers.py
# passes no `timeout=` anywhere), so this bound is chosen fresh here.
_FETCH_TIMEOUT_SECONDS = 30.0


@dataclass(frozen=True)
class FreshnessResult:
    """Verdict on whether a branch's base is current with the remote
    default branch. `fresh` is True only when a narrow fetch of a
    remote-qualified default-branch ref succeeded AND the branch's
    merge-base with it equals the freshly-fetched remote tip. Every
    other outcome — unresolvable default branch, a local-only ref, or a
    failed/expired fetch — is `fresh=False` with `reason` set."""

    fresh: bool
    reason: str | None = None
    base_sha: str | None = None
    remote_sha: str | None = None


def _git(repo: Path, *args: str, timeout: float | None = None) -> str | None:
    """Run git in `repo`; return stripped stdout, or None on any failure
    (non-zero exit, timeout, or the git binary failing to launch)."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def split_fetch_target(ref: str) -> tuple[str, str] | None:
    """Split a `default_branch_ref` revision NAME into (remote, branch)
    for `git fetch <remote> <branch>`. `git fetch origin origin/main` is
    not a valid refspec — the remote component must be split off first.

    Returns None when `ref` has no remote component — the bare local
    `main` / `master` shape `default_branch_ref` can also return. That
    shape cannot be fetched and is exactly the LOCAL-ONLY hazard named
    in §Pinned local-ref rule above.
    """
    remote, sep, branch = ref.partition("/")
    if not sep or not remote or not branch:
        return None
    return remote, branch


def check_freshness(
    repo: Path, *, fetch_timeout: float = _FETCH_TIMEOUT_SECONDS
) -> FreshnessResult:
    """Report whether `repo`'s HEAD branch base is current with the
    remote default branch. Reports only — see module docstring."""
    ref = default_branch_ref(repo)
    if ref is None:
        return FreshnessResult(fresh=False, reason="no default branch resolved")

    target = split_fetch_target(ref)
    if target is None:
        return FreshnessResult(
            fresh=False, reason=f"local-only default-branch ref: {ref!r}"
        )
    remote, branch = target

    fetched = _git(repo, "fetch", remote, branch, timeout=fetch_timeout) is not None
    if not fetched:
        return FreshnessResult(
            fresh=False, reason=f"git fetch {remote} {branch} failed or timed out"
        )

    remote_sha = _git(repo, "rev-parse", ref)
    if remote_sha is None:
        return FreshnessResult(
            fresh=False, reason=f"could not resolve {ref} after fetch"
        )

    base_sha = _git(repo, "merge-base", "HEAD", ref)
    if base_sha is None:
        return FreshnessResult(fresh=False, reason="merge-base computation failed")

    fresh = base_sha == remote_sha
    return FreshnessResult(
        fresh=fresh,
        reason=None if fresh else "branch base predates the remote's current tip",
        base_sha=base_sha,
        remote_sha=remote_sha,
    )
