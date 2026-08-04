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
guard is proven not to refuse everything). A sixth and seventh
invocation, `branch_creation_sha`'s `symbolic-ref --short -q HEAD` and
`log -g --format=%H%x1f%gs refs/heads/<branch>`, are live-verified by
`test_branch_creation_sha_returns_fork_sha` (a real branch cut from a
known commit, with real commits added on top, read back through a real
reflog), `test_branch_creation_sha_none_on_detached_head` (a real
detached HEAD, no mocking of the failed `symbolic-ref`), and
`test_branch_creation_sha_none_when_oldest_entry_not_creation` (a real
reflog file edited in place to simulate a pruned creation entry). An
eighth invocation, `merge-base --is-ancestor <ancestor> <descendant>`
— Task 2's old-base selection, gating whether the printed remedy uses
the creation sha or falls back to the merge-base — is live-verified by
`test_cli_stale_cut_remedy_uses_creation_sha_not_merge_base` (a real
stale-cut fixture where both ancestry checks genuinely hold) and
`test_cli_refuses_stale_base_with_rebase_remedy` (the creation-equals-
merge-base case, proving the guard is not vacuously true). Task 3 adds
no new invocation but exercises two further real states of the same
ancestry checks: `test_cli_stale_base_without_reflog_prints_caveat`
deletes the branch's real `.git/logs/refs/heads/<branch>` file so
`branch_creation_sha` genuinely returns None (confirmed live at
loom-code scratchpad probe: `git log -g` on a reflog-less ref exits 0
with empty stdout, not an error, which is why `branch_creation_sha`
must test `output` for emptiness rather than trust a non-None return);
and `test_cli_divergent_creation_sha_falls_back_with_caveat` builds a
real repo where the recorded creation sha passes the first ancestry
check (base-is-ancestor-of-creation) but fails the second
(creation-is-ancestor-of-HEAD) — a genuine reset-to-a-sibling-lineage
state, not a mock — proving that second check is load-bearing on its
own.
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


def test_cli_stale_cut_remedy_uses_creation_sha_not_merge_base(tmp_path, capsys):
    # Task 2 RED: reproduce the stale-cut state from the 0.50.0 fix arc
    # (docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md §Verified
    # root cause) — a branch cut from a local tip (`prev` at P2) whose
    # content was later squash-merged into upstream's default branch as a
    # single commit S. merge-base(arc, origin/main) is M0 (the clone
    # point), but the branch's OWN work only starts at P2: rebasing onto
    # M0 replays P1/P2, which upstream already carries (squashed, so
    # rebase's duplicate-skip cannot recognize them) and conflicts. The
    # printed remedy's old-base must be P2 (the reflog creation sha), not
    # M0 (the merge-base) — today's code always prints the merge-base, so
    # this fails before the fix.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    m0_sha = _head(repo)

    _git(repo, "checkout", "-q", "-b", "prev")
    (repo / "p1.txt").write_text("p1\n")
    _git(repo, "add", "p1.txt")
    _git(repo, "commit", "-q", "-m", "P1")
    (repo / "p2.txt").write_text("p2\n")
    _git(repo, "add", "p2.txt")
    _git(repo, "commit", "-q", "-m", "P2")
    p2_sha = _head(repo)

    # Upstream gains a squash-style commit S carrying the same content as
    # P1+P2 — the already-squashed foreign history the fix must avoid
    # replaying.
    (upstream / "p1.txt").write_text("p1\n")
    (upstream / "p2.txt").write_text("p2\n")
    _git(upstream, "add", "p1.txt", "p2.txt")
    _git(upstream, "commit", "-q", "-m", "S (squash of P1+P2)")
    s_sha = _head(upstream)

    _git(repo, "checkout", "-q", "-b", "arc")
    (repo / "o1.txt").write_text("o1\n")
    _git(repo, "add", "o1.txt")
    _git(repo, "commit", "-q", "-m", "O1")

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert f"git rebase --onto {s_sha} {p2_sha} HEAD" in captured.err
    assert m0_sha not in captured.err


def test_cli_stale_base_without_reflog_prints_caveat(tmp_path, capsys):
    # Task 3 RED (a): the plain stale-base fixture (same shape as
    # test_cli_refuses_stale_base_with_rebase_remedy), but with the
    # branch's real reflog FILE deleted before the CLI runs — a live,
    # unmocked way to force branch_creation_sha to return None (confirmed
    # separately: git log -g on a reflog-less ref exits 0 with empty
    # stdout, not a git failure). The fallback old-base must still be the
    # merge-base, and — new in Task 3 — a caveat line pointing at a
    # verifiable recovery action must appear on stderr.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    base_sha = _head(repo)

    _git(repo, "checkout", "-q", "-b", "feature")
    _git(upstream, "commit", "--allow-empty", "-m", "already on default branch")
    remote_sha = _head(upstream)

    reflog_path = repo / ".git" / "logs" / "refs" / "heads" / "feature"
    reflog_path.unlink()

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert f"git rebase --onto {remote_sha} {base_sha} HEAD" in captured.err
    assert "git rebase --abort" in captured.err
    assert "git reflog show feature" in captured.err


def test_cli_creation_sha_path_prints_no_caveat(tmp_path, capsys):
    # Task 3 RED (paired negative): Task 2's stale-cut fixture, where the
    # creation sha IS usable and becomes the printed old-base. No caveat
    # line may appear here — the remedy is already correct. Absence is
    # paired with the positive fact that the remedy line itself is
    # present, so this cannot pass vacuously on a broken CLI path.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)

    _git(repo, "checkout", "-q", "-b", "prev")
    (repo / "p1.txt").write_text("p1\n")
    _git(repo, "add", "p1.txt")
    _git(repo, "commit", "-q", "-m", "P1")
    (repo / "p2.txt").write_text("p2\n")
    _git(repo, "add", "p2.txt")
    _git(repo, "commit", "-q", "-m", "P2")
    p2_sha = _head(repo)

    (upstream / "p1.txt").write_text("p1\n")
    (upstream / "p2.txt").write_text("p2\n")
    _git(upstream, "add", "p1.txt", "p2.txt")
    _git(upstream, "commit", "-q", "-m", "S (squash of P1+P2)")
    s_sha = _head(upstream)

    _git(repo, "checkout", "-q", "-b", "arc")
    (repo / "o1.txt").write_text("o1\n")
    _git(repo, "add", "o1.txt")
    _git(repo, "commit", "-q", "-m", "O1")

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert f"git rebase --onto {s_sha} {p2_sha} HEAD" in captured.err
    assert "git rebase --abort" not in captured.err


def test_cli_divergent_creation_sha_falls_back_with_caveat(tmp_path, capsys):
    # Task 3 RED (b) — mutation-killing coverage for the SECOND ancestry
    # check (`creation is ancestor of HEAD`), found missing during
    # review: a fixture where the recorded creation sha passes the FIRST
    # check (base is ancestor of creation) but fails the second. Layout:
    #   G (clone point) --- R (upstream advances; branch "arc" cut here,
    #                          so branch_creation_sha == R)
    #    \
    #     S (a sibling line off G, NOT descending through R)
    # arc's own commit O1 is then hard-reset onto S, so current HEAD's
    # real ancestry no longer passes through R at all: merge-base(HEAD,
    # ref) resolves to G (R is-ancestor-of G's descendant R holds, so
    # check 1 — base(G)-is-ancestor-of-creation(R) — genuinely passes),
    # but R is NOT an ancestor of HEAD=S (check 2 genuinely fails). A
    # version of the code that only tested check 1 would wrongly select
    # R as old-base here; this proves check 2 is load-bearing on its own.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    g_sha = _head(repo)

    _git(upstream, "commit", "--allow-empty", "-m", "ROOT")
    root_sha = _head(upstream)
    default_branch = _git(upstream, "symbolic-ref", "--short", "HEAD")

    _git(upstream, "checkout", "-q", "-b", "sideline", g_sha)
    _git(upstream, "commit", "--allow-empty", "-m", "SIDE")
    side_sha = _head(upstream)
    _git(upstream, "checkout", "-q", default_branch)

    _git(repo, "fetch", "-q", "origin")
    _git(repo, "checkout", "-q", "-b", "arc", root_sha)
    (repo / "o1.txt").write_text("o1\n")
    _git(repo, "add", "o1.txt")
    _git(repo, "commit", "-q", "-m", "O1")
    _git(repo, "reset", "-q", "--hard", side_sha)

    _git(upstream, "commit", "--allow-empty", "-m", "further")
    remote_sha = _head(upstream)

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert f"git rebase --onto {remote_sha} {g_sha} HEAD" in captured.err
    assert root_sha not in captured.err
    assert "git rebase --abort" in captured.err
    assert "git reflog show arc" in captured.err


def test_cli_creation_sha_predating_merge_base_falls_back_with_caveat(
    tmp_path, capsys
):
    # Whole-branch review finding — mutation-killing coverage for the
    # FIRST ancestry check (`base is ancestor-or-equal of creation`),
    # the symmetric twin of the divergent-creation test above: a fixture
    # where the recorded creation sha fails the FIRST check while
    # passing the second. Layout: branch "arc" is cut at the clone
    # point G (creation == G), upstream then advances to M1 and M1 is
    # MERGED INTO arc — so merge-base(HEAD, ref) moves forward to M1,
    # leaving the creation sha STRICTLY BEHIND the merge-base. Check 1
    # (base(M1)-is-ancestor-of-creation(G)) genuinely fails; check 2
    # (creation(G)-is-ancestor-of-HEAD) genuinely passes. A version of
    # the code that only tested check 2 would wrongly select G as
    # old-base — replaying M1's already-based history — so this proves
    # check 1 is load-bearing on its own.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    g_sha = _head(repo)

    _git(repo, "checkout", "-q", "-b", "arc", g_sha)
    (repo / "o1.txt").write_text("o1\n")
    _git(repo, "add", "o1.txt")
    _git(repo, "commit", "-q", "-m", "O1")

    _git(upstream, "commit", "--allow-empty", "-m", "M1")
    m1_sha = _head(upstream)
    _git(repo, "fetch", "-q", "origin")
    _git(repo, "merge", "-q", "--no-edit", m1_sha)

    _git(upstream, "commit", "--allow-empty", "-m", "M2")
    remote_sha = _head(upstream)

    exit_code = review_scope.main(["--repo", str(repo)])
    captured = capsys.readouterr()

    assert exit_code != 0
    assert f"git rebase --onto {remote_sha} {m1_sha} HEAD" in captured.err
    assert f"--onto {remote_sha} {g_sha} HEAD" not in captured.err
    assert "git rebase --abort" in captured.err
    assert "git reflog show arc" in captured.err


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


def test_branch_creation_sha_returns_fork_sha(tmp_path):
    # Task 1 RED (positive): cut a branch from a known commit, add
    # commits on top, and confirm branch_creation_sha returns the
    # cut-point sha — the reflog's OLDEST entry for the branch ref
    # (`git checkout -b` writes a single "branch: Created from HEAD"
    # entry; later commits append newer entries, so the creation entry
    # is the reflog's last output line, not its first).
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    cut_sha = _head(repo)

    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / "a.txt").write_text("a\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "-q", "-m", "commit1")
    (repo / "b.txt").write_text("b\n")
    _git(repo, "add", "b.txt")
    _git(repo, "commit", "-q", "-m", "commit2")

    assert review_scope.branch_creation_sha(repo) == cut_sha


def test_branch_creation_sha_none_on_detached_head(tmp_path):
    # Task 1 RED (paired negative): a detached HEAD has no branch name to
    # resolve (`git symbolic-ref --short -q HEAD` fails), so
    # branch_creation_sha must return an honest None rather than
    # guessing at a ref.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)
    _git(repo, "checkout", "-q", "--detach")

    assert review_scope.branch_creation_sha(repo) is None


def test_branch_creation_sha_none_when_oldest_entry_not_creation(tmp_path):
    # Round-2 coverage fix: the detached-HEAD test above exits before the
    # `subject.startswith("branch: Created from")` guard ever runs, so
    # that guard had zero coverage. This test exercises it directly: cut
    # a branch, add a commit (a real reflog with two entries), then edit
    # the reflog file in place to replace the OLDEST entry's subject —
    # simulating the state `git reflog expire` leaves when it prunes the
    # creation entry but leaves later ones. The oldest surviving entry's
    # sha here still equals the true cut sha (edited in place, not
    # removed), so a version of branch_creation_sha that returned the
    # oldest entry's sha UNCONDITIONALLY would coincidentally still
    # return the right value — the guard is what makes an entry whose
    # subject isn't a creation entry return None instead of that sha.
    upstream = _init_upstream(tmp_path)
    repo = _clone(tmp_path, upstream)

    _git(repo, "checkout", "-q", "-b", "feature")
    (repo / "a.txt").write_text("a\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "-q", "-m", "commit1")

    reflog_path = repo / ".git" / "logs" / "refs" / "heads" / "feature"
    lines = reflog_path.read_text().splitlines(keepends=True)
    assert "branch: Created from HEAD" in lines[0]
    lines[0] = lines[0].replace("branch: Created from HEAD", "commit: pruned entry")
    reflog_path.write_text("".join(lines))

    assert review_scope.branch_creation_sha(repo) is None
