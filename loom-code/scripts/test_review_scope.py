"""Tests for review_scope — the freshness verdict Task 2 builds, and the
refusal contract Task 3 locks down.

Each test builds a THROWAWAY pair of git repos under tmp_path: an
`upstream` repo (plays the role of the remote) and a `repo` clone of it
(plays the role of the branch under review). No dependency on the outer
repo. Commits are made directly in `upstream`'s own working tree — never
via `git push` into it — so `upstream` can stay a normal (non-bare) repo.

External-surface grounding (source a — live verification): the git
invocations `check_freshness` depends on — `fetch <remote> <branch>`,
`rev-parse <ref>`, and `merge-base HEAD <ref>` — are exercised LIVE by
this suite against the throwaway repos above, both the stale-base and
the fresh-base paths, so a flag regression in the installed git surfaces
here, not via belief. Task 3 adds the three ways a REAL git repo fails
to establish freshness, also exercised live rather than mocked: a
`fetch` that genuinely fails (origin pointed at a non-repo path), a
repo with no default branch resolvable at all, and a repo with a
LOCAL-ONLY default-branch ref — a real, fetchable `origin` remote IS
configured, but `refs/remotes/origin/HEAD` is unset, so
`default_branch_ref` falls through to the bare local `main` shape.
Task 4 adds a fourth git invocation, `resolve_changed_files`'s
`diff <ref>...HEAD --name-only` — live-verified by
`test_cli_emits_file_list_matching_three_dot_diff`, which drives it
through `main()` and cross-checks stdout against a raw `git diff`
subprocess run directly against the same repo, byte-for-byte. A fifth
invocation, `_remote_live_default_branch`'s
`ls-remote --symref <remote> HEAD`, is live-verified by
`test_stale_origin_head_after_default_branch_rename_refuses` (a genuinely
renamed upstream default branch, real symref mismatch, no mocking) and
`test_current_origin_head_still_reports_fresh` (the matching case, so the
guard is proven not to refuse everything).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import review_scope


def _git(repo: Path, *args: str) -> str:
    """Run a git command in `repo`, return stdout (stripped)."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_upstream(tmp_path: Path) -> Path:
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q")
    _git(upstream, "config", "user.email", "test@example.com")
    _git(upstream, "config", "user.name", "Test User")
    _git(upstream, "commit", "--allow-empty", "-m", "init")
    return upstream


def _clone(tmp_path: Path, upstream: Path) -> Path:
    repo = tmp_path / "repo"
    subprocess.run(
        ["git", "clone", "-q", str(upstream), str(repo)],
        check=True,
        capture_output=True,
        text=True,
    )
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    return repo


def test_stale_base_is_not_fresh(tmp_path):
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    # Branch off the base BEFORE a new commit lands on upstream's default
    # branch — the base then predates a commit already on the default
    # branch, which is the stale scenario.
    _git(repo, "checkout", "-q", "-b", "feature")
    _git(upstream, "commit", "--allow-empty", "-m", "already on default branch")

    result = review_scope.check_freshness(repo)

    assert result.fresh is False
    assert result.base_sha == base_sha


def test_fresh_base_reports_fresh(tmp_path):
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    # Branch off the base with nothing new pushed to upstream afterward —
    # the branch's base IS the current remote tip.
    _git(repo, "checkout", "-q", "-b", "feature")

    result = review_scope.check_freshness(repo)

    assert result.fresh is True
    assert result.base_sha == base_sha
    assert result.remote_sha == base_sha


def test_fetch_failure_refuses(tmp_path):
    # Failure shape 1 of 3 (§Pinned refusal contract): the fetch
    # subprocess itself fails. Point origin at a path with no git repo
    # at all, so "git fetch origin main" exits non-zero for real — this
    # suite prefers a live failure over mocking subprocess, matching the
    # external-surface-grounding note above. No verdict may be computed
    # from whatever is on disk: base_sha/remote_sha must stay None,
    # never fall back to a merge-base run against the stale local ref.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    _git(repo, "checkout", "-q", "-b", "feature")
    _git(repo, "remote", "set-url", "origin", str(tmp_path / "nonexistent-remote"))

    result = review_scope.check_freshness(repo)

    assert result.fresh is False
    assert result.base_sha is None
    assert result.remote_sha is None


def test_no_resolvable_default_branch_refuses(tmp_path):
    # Failure shape 2 of 3: default_branch_ref returns None — no
    # origin/HEAD, no local main, no local master. check_freshness must
    # refuse before ever attempting a fetch.
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "not-main-or-master")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "commit", "--allow-empty", "-m", "init")

    result = review_scope.check_freshness(repo)

    assert result.fresh is False
    assert result.base_sha is None
    assert result.remote_sha is None


def test_local_only_ref_refuses(tmp_path):
    # Failure shape 3 of 3: default_branch_ref resolves, but to a bare
    # local `main` with no remote component (§Pinned local-ref rule).
    # A real, FETCHABLE `origin` remote is configured here — only
    # `refs/remotes/origin/HEAD` is missing — so this discriminates the
    # local-only-ref guard specifically: if that guard were weakened to
    # fall back to ("origin", ref) instead of refusing, the fetch would
    # genuinely succeed and produce a false fresh=True verdict, not an
    # incidental fetch-failure refusal. check_freshness must refuse
    # before ever attempting that fetch.
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", "-b", "main")
    _git(upstream, "config", "user.email", "test@example.com")
    _git(upstream, "config", "user.name", "Test User")
    _git(upstream, "commit", "--allow-empty", "-m", "init")

    repo = _clone(tmp_path, upstream)
    _git(repo, "symbolic-ref", "-d", "refs/remotes/origin/HEAD")
    _git(repo, "checkout", "-q", "-b", "feature")

    result = review_scope.check_freshness(repo)

    assert result.fresh is False
    assert result.base_sha is None
    assert result.remote_sha is None


def test_cli_refuses_stale_base_with_rebase_remedy(tmp_path, capsys):
    # Task 4 RED (a): the CLI on a stale-base repo must exit non-zero and
    # print the CONCRETE `git rebase --onto <remote_sha> <base_sha> HEAD`
    # remedy — both shas filled in, not a template. Fails today because
    # review_scope.main does not exist yet.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    _git(repo, "checkout", "-q", "-b", "feature")
    _git(upstream, "commit", "--allow-empty", "-m", "already on default branch")
    remote_sha = _head(upstream)

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert captured.out == ""
    assert f"git rebase --onto {remote_sha} {base_sha} HEAD" in captured.err


def test_cli_refuses_without_shas_prints_no_rebase_remedy(tmp_path, capsys):
    # Finding 2 (round 2): a refusal shape whose shas never resolved
    # (here, no default branch resolvable at all — same setup as
    # test_no_resolvable_default_branch_refuses, driven through main()
    # instead of check_freshness directly) must print the reason but
    # NOT the rebase remedy line — there are no shas to fill it with.
    # Guards the `result.base_sha is not None and result.remote_sha is
    # not None` gate at review_scope.py: a regression that drops it
    # (e.g. replacing the condition with `True`) would print
    # "git rebase --onto None None HEAD", an instruction that cannot
    # be run.
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "not-main-or-master")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "commit", "--allow-empty", "-m", "init")

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert captured.out == ""
    assert "review-scope: refused — no default branch resolved" in captured.err
    assert "git rebase --onto" not in captured.err


def test_cli_emits_file_list_matching_three_dot_diff(tmp_path, capsys):
    # Task 4 RED (b): on a fresh base, the CLI's stdout must be
    # byte-identical to `git diff <default-branch>...HEAD --name-only`
    # run directly against the same repo — not merely the same set of
    # names, the same bytes (ordering, trailing newline included). Fails
    # today because review_scope.main does not exist yet.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)

    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / "new_file.txt").write_text("hello\n")
    _git(repo, "add", "new_file.txt")
    _git(repo, "commit", "-m", "add new_file")

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    default_branch = review_scope.default_branch_ref(repo)
    raw = subprocess.run(
        ["git", "-C", str(repo), "diff", f"{default_branch}...HEAD", "--name-only"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert exit_code == 0
    assert captured.out == raw.stdout
    assert captured.out == "new_file.txt\n"


def test_stale_origin_head_after_default_branch_rename_refuses(tmp_path):
    # Whole-branch-review finding: upstream's default branch was renamed
    # old-main -> main and advanced two commits; old-main is NOT deleted
    # (the ordinary post-rename state on a real host). The clone's
    # `origin/HEAD` symref was captured at clone time and never
    # auto-updates (`git remote set-head origin -a` is a manual step
    # almost nobody runs), so `default_branch_ref` still resolves to
    # `origin/old-main` -- a ref that is real, fetchable, and
    # merge-base-comparable, just not the remote's CURRENT default.
    # Before this guard, check_freshness fetched old-main (unchanged
    # since the clone), found merge-base == old-main's tip, and reported
    # fresh=True while the branch sat two commits behind main -- a false
    # all-clear indistinguishable from a genuine pass.
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", "-b", "old-main")
    _git(upstream, "config", "user.email", "test@example.com")
    _git(upstream, "config", "user.name", "Test User")
    _git(upstream, "commit", "--allow-empty", "-m", "init")

    repo = _clone(tmp_path, upstream)
    _git(repo, "checkout", "-q", "-b", "feature")

    # Rename the remote's default branch to "main" and advance it two
    # commits; old-main stays around, unchanged and still fetchable.
    _git(upstream, "checkout", "-q", "-b", "main")
    _git(upstream, "commit", "--allow-empty", "-m", "rename 1")
    _git(upstream, "commit", "--allow-empty", "-m", "rename 2")

    # Confirm the setup actually reproduces the stale-symref state before
    # asserting on it.
    assert review_scope.default_branch_ref(repo) == "origin/old-main"

    result = review_scope.check_freshness(repo)

    assert result.fresh is False


def test_current_origin_head_still_reports_fresh(tmp_path):
    # Regression guard for the symref-freshness check above: when
    # `origin/HEAD` DOES match the remote's live default branch, the new
    # guard must not refuse a genuinely fresh base — a naive "refuse
    # when unsure" fix would pass the test above by refusing everything,
    # including this case.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)
    _git(repo, "checkout", "-q", "-b", "feature")

    result = review_scope.check_freshness(repo)

    assert result.fresh is True
    assert result.base_sha == base_sha
    assert result.remote_sha == base_sha


def _head(repo: Path) -> str:
    return _git(repo, "rev-parse", "HEAD")


def test_split_fetch_target_splits_on_first_slash_only():
    # ref.partition("/") must split on the FIRST separator only, so a
    # branch name that itself contains a slash (e.g. "release/2.0")
    # survives intact as the branch component rather than being cut at
    # the last slash — a later "fix" to rsplit/split("/") would break
    # this real-world branch-name shape while every slash-free test
    # still passed.
    assert review_scope.split_fetch_target("origin/release/2.0") == (
        "origin",
        "release/2.0",
    )


def test_split_fetch_target_returns_none_for_bare_local_ref():
    # A bare local ref ("main" / "master", no remote component) is the
    # LOCAL-ONLY hazard named in §Pinned local-ref rule: it cannot be
    # fetched, so split_fetch_target must signal that with None rather
    # than a fabricated split.
    assert review_scope.split_fetch_target("main") is None
