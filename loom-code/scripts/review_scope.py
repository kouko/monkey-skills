"""Review-scope resolver: a freshness verdict on a branch's merge-base,
and the changed-file list gated on it.

`check_freshness` derives a fetch target from `default_branch_ref`'s
revision name, fetches that ref narrowly, and reports whether the
branch's merge-base with the default branch is the remote's current
tip. Every way freshness can fail to be established REFUSES rather than
falling back to a verdict computed from whatever is on disk: see
§Pinned refusal contract below. `FreshnessResult.fresh is False` IS the
refusal signal, for a genuinely stale base and for an unestablishable
one alike; `base_sha`/`remote_sha` stay `None` on the latter, since no
comparison ever ran.

`main` is the CLI entry point:
`python3 review_scope.py [--repo <path>] [--reviewed-sha <sha>]`.

Exit codes:
  0 — the base is fresh. The branch's changed-file list is printed to
      stdout, one path per line, byte-identical to
      `git diff <default-branch>...<reviewed-sha> --name-only` (three-dot,
      unchanged — the brief's §Decision is that the defect was the
      base, never the dot count).
  1 — refusal. No file list is printed. stderr carries the reason from
      `FreshnessResult.reason`, and — only for the stale-base shape,
      the one case where both shas resolved — the concrete
      `git rebase --onto <remote_sha> <old_base> HEAD` remedy, where
      `<old_base>` is the branch's reflog creation sha
      (`branch_creation_sha`) when it is a descendant-or-equal of the
      merge-base AND an ancestor of HEAD, falling back to the merge-base
      itself otherwise. The creation sha is preferred because a
      squash-merge repo can leave merge-base..HEAD carrying
      already-squashed foreign commits whose replay conflicts (squashing
      changes patch-ids, so rebase's duplicate-skip cannot drop them) —
      the merge-base fallback is textbook-correct for merge/rebase
      workflows but unsafe in exactly that state — when it happens, one
      extra stderr line follows the rebase remedy: a caveat naming the
      verifiable recovery action (`git rebase --abort`, then retry with
      the reflog's own last-line sha) so the caller need not judge
      whether the printed old-base was safe. No caveat is printed when
      the creation sha was used. Every other refusal
      shape has no shas to fill in, so no rebase invocation is printed
      for it. There are seven, and the list is
      exhaustive against `check_freshness`'s early returns: an
      unresolvable default branch, a local-only ref, a failed or
      expired fetch, a failed or expired lookup of the remote's live
      default branch, a default-branch ref that no longer matches the
      remote's live default branch, a ref that still will not resolve
      after a successful fetch, and a failed merge-base computation. A
      third exit-1 source
      exists past the freshness verdict: a fresh base whose
      `resolve_changed_files` diff still fails. That shape carries a
      hardcoded stderr message, not a `FreshnessResult.reason` (no
      `FreshnessResult` describes it — the verdict was already fresh),
      and prints no rebase remedy either.

This module writes its own stdlib `subprocess` git helper rather than
importing `loom_gate_markers._git` — that name is private, and reaching
for a second private cross-module name would recommit the dependency the
`default_branch_ref` promotion (this repo's Task 1) exists to remove.

A successful fetch of `default_branch_ref`'s ref is not, by itself,
proof that the ref is still the remote's *current* default branch: a
clone's local `origin/HEAD` symref is captured once, at clone time, and
never auto-updates (`git remote set-head origin -a` is a separate manual
step almost nobody runs). If the remote later renames its default branch
without deleting the old one — the ordinary post-rename state on a real
host — the old ref stays real and fetchable, and a freshness check that
stops at "did the fetch succeed" reports fresh against a branch nobody
treats as default anymore. `check_freshness` therefore also queries the
remote's LIVE default branch (`git ls-remote --symref <remote> HEAD`,
bounded by the same fetch timeout) and refuses on any mismatch or failed
lookup, rather than trusting the local symref.

§Pinned refusal contract (transcribed verbatim):

A stale base, or any failure to establish freshness, REFUSES.
The resolver never returns a file list it cannot vouch for, and a
station that receives a refusal STOPS before dispatching anything.

§Pinned local-ref rule (transcribed verbatim):

default_branch_ref returns a revision NAME, not a fetch target: either
`origin/<branch>` (origin/HEAD, prefix stripped) or a bare local `main`
/ `master`, or None. A return with no remote component is a LOCAL-ONLY
ref: comparing against it answers "am I current with my own local main",
which is a false all-clear. Local-only is a freshness FAILURE, never a
fresh verdict.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
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


def _is_full_object_id(repo: Path, candidate: str) -> bool:
    """Return whether ``candidate`` is a full hex object ID for ``repo``.

    A revision name (including HEAD or a branch) may resolve today and move
    tomorrow, so it cannot be accepted as an immutable review-packet endpoint.
    """
    object_format = _git(repo, "rev-parse", "--show-object-format")
    expected_length = {"sha1": 40, "sha256": 64}.get(object_format)
    return (
        expected_length is not None
        and len(candidate) == expected_length
        and all(character in "0123456789abcdefABCDEF" for character in candidate)
    )


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


def _remote_live_default_branch(
    repo: Path, remote: str, *, timeout: float
) -> str | None:
    """Query `remote`'s LIVE default branch via `git ls-remote --symref
    <remote> HEAD` — the remote's own answer to "what is my default
    branch right now", independent of anything cached locally. Returns
    the branch name (no `refs/heads/` prefix), or None on any failure
    (non-zero exit, timeout, or no `ref:` line in the output). A failed
    or timed-out lookup is a freshness FAILURE for the caller — it must
    never fall back to trusting the local `origin/HEAD` symref, which is
    exactly the value this check exists to cross-verify."""
    output = _git(repo, "ls-remote", "--symref", remote, "HEAD", timeout=timeout)
    if not output:
        return None
    for line in output.splitlines():
        if line.startswith("ref:"):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].removeprefix("refs/heads/")
    return None


def check_freshness(
    repo: Path,
    *,
    fetch_timeout: float = _FETCH_TIMEOUT_SECONDS,
    reviewed_sha: str = "HEAD",
) -> FreshnessResult:
    """Report whether `reviewed_sha`'s base is current with the remote
    default branch. Never exits — see module docstring; every
    failure-to-establish-freshness shape refuses via `fresh=False` with
    `base_sha`/`remote_sha` left `None`, per §Pinned refusal contract."""
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

    live_branch = _remote_live_default_branch(repo, remote, timeout=fetch_timeout)
    if live_branch is None:
        return FreshnessResult(
            fresh=False,
            reason=(
                f"could not verify {remote}'s live default branch "
                "(ls-remote --symref failed or timed out)"
            ),
        )
    if live_branch != branch:
        return FreshnessResult(
            fresh=False,
            reason=(
                f"default-branch ref is stale: resolved to {branch!r} but "
                f"{remote}'s current default branch is {live_branch!r}"
            ),
        )

    remote_sha = _git(repo, "rev-parse", ref)
    if remote_sha is None:
        return FreshnessResult(
            fresh=False, reason=f"could not resolve {ref} after fetch"
        )

    base_sha = _git(repo, "merge-base", reviewed_sha, ref)
    if base_sha is None:
        return FreshnessResult(fresh=False, reason="merge-base computation failed")

    fresh = base_sha == remote_sha
    return FreshnessResult(
        fresh=fresh,
        reason=None if fresh else "branch base predates the remote's current tip",
        base_sha=base_sha,
        remote_sha=remote_sha,
    )


def branch_creation_sha(repo: Path) -> str | None:
    """Return the sha the current branch was cut from, or None when it
    cannot be established. Resolves the current branch name via `git
    symbolic-ref --short -q HEAD` (None on detached HEAD, where there is
    no branch to look up); reads that branch's reflog OLDEST entry via
    `git log -g --format=%H%x1f%gs refs/heads/<branch>` (the reflog is
    printed newest-first, so the oldest entry is the last output line);
    returns that entry's sha only when its subject starts with `branch:
    Created from` — a pruned or rewritten reflog whose oldest surviving
    entry is not the creation entry returns None rather than a wrong
    sha. Any git failure (including no reflog at all) returns None."""
    branch = _git(repo, "symbolic-ref", "--short", "-q", "HEAD")
    if branch is None:
        return None

    output = _git(repo, "log", "-g", "--format=%H%x1f%gs", f"refs/heads/{branch}")
    if not output:
        return None

    lines = output.splitlines()
    sha, _, subject = lines[-1].partition("\x1f")
    if not subject.startswith("branch: Created from"):
        return None
    return sha


def resolve_changed_files(
    repo: Path, ref: str, *, reviewed_sha: str = "HEAD"
) -> list[str] | None:
    """Return `repo`'s branch's changed-file list against `ref`, computed
    the same way the review stations do today — `git diff
    <ref>...<reviewed-sha> --name-only`, three-dot — so the output is
    byte-identical to what they already compute. Returns None on any git
    failure; an empty list is a valid ("no changes") result, distinct from
    failure."""
    output = _git(repo, "diff", f"{ref}...{reviewed_sha}", "--name-only")
    if output is None:
        return None
    if output == "":
        return []
    return output.splitlines()


def main(argv: list[str] | None = None) -> int:
    """CLI entry: `python3 review_scope.py [--repo <path>]
    [--reviewed-sha <sha>]` (default cwd / current HEAD).
    See the module docstring for the exit-code contract."""
    parser = argparse.ArgumentParser(
        description="Resolve review scope: a changed-file list gated on base freshness"
    )
    parser.add_argument("--repo", default=".", help="repo path (default: cwd)")
    parser.add_argument(
        "--reviewed-sha",
        help=(
            "immutable commit this review packet authorizes "
            "(default: current HEAD)"
        ),
    )
    args = parser.parse_args(argv)
    repo = Path(args.repo)

    reviewed_sha = "HEAD"
    if args.reviewed_sha is not None:
        if not _is_full_object_id(repo, args.reviewed_sha):
            print(
                "review-scope: refused — reviewed SHA must be a full commit SHA",
                file=sys.stderr,
            )
            return 1
        reviewed_sha = _git(
            repo, "rev-parse", "--verify", f"{args.reviewed_sha}^{{commit}}"
        )
        if reviewed_sha is None:
            print(
                "review-scope: refused — reviewed SHA does not resolve to a commit",
                file=sys.stderr,
            )
            return 1
        current_head = _git(repo, "rev-parse", "HEAD")
        if current_head != reviewed_sha:
            print(
                "review-scope: refused — reviewed SHA no longer matches current HEAD",
                file=sys.stderr,
            )
            return 1

    result = check_freshness(repo, reviewed_sha=reviewed_sha)
    if not result.fresh:
        print(f"review-scope: refused — {result.reason}", file=sys.stderr)
        if result.base_sha is not None and result.remote_sha is not None:
            old_base = result.base_sha
            creation = branch_creation_sha(repo)
            # TRAP: _git returns "" (falsy, not None) on a SUCCESSFUL
            # `merge-base --is-ancestor` — it emits no stdout on a zero
            # exit. Test both ancestry conditions with `is not None`,
            # never truthiness, or a real usable creation sha reads as a
            # failed check here.
            creation_usable = (
                creation is not None
                and _git(repo, "merge-base", "--is-ancestor", result.base_sha, creation)
                is not None
                and _git(repo, "merge-base", "--is-ancestor", creation, "HEAD")
                is not None
            )
            if creation_usable:
                old_base = creation
            print(
                "review-scope: rebase onto the current base: "
                f"git rebase --onto {result.remote_sha} {old_base} HEAD",
                file=sys.stderr,
            )
            if not creation_usable:
                # The remedy fell back to the merge-base rather than the
                # branch's own creation sha, so merge-base..HEAD may carry
                # already-squashed foreign commits (see module docstring).
                # Print a verifiable recovery action rather than leaving
                # the caller to judge whether the printed old-base is
                # safe: abort and retry with the reflog's own last-line
                # sha, not a guess.
                branch = _git(repo, "symbolic-ref", "--short", "-q", "HEAD")
                branch_label = branch if branch is not None else "<branch>"
                print(
                    "review-scope: if the rebase stops on commits that are "
                    "not this branch's own work, run git rebase --abort and "
                    "retry with the second sha replaced by the last-line sha "
                    f"of: git reflog show {branch_label}",
                    file=sys.stderr,
                )
        return 1

    ref = default_branch_ref(repo)
    files = (
        resolve_changed_files(repo, ref, reviewed_sha=reviewed_sha)
        if ref is not None
        else None
    )
    if files is None:
        print(
            "review-scope: refused — changed-file list could not be resolved",
            file=sys.stderr,
        )
        return 1

    for path in files:
        print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
