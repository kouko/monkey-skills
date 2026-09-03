"""Adversarial probes against `check_close_commit_shape` (spec REQ-1,
`push.review-only-head`'s close-commit shape recompute, W0-04, commit
942ced9e). Each case is a real commit chain in a temp git repo; the
checker is run as `loom_checker.py push`, never mocked.

Reuses the fixtures and helpers of `test_loom_checker_push.py` (same
directory) rather than re-deriving them -- a second, drifting copy of
`build_repo`/`_seed_intent`/`_close_commit` would be the adversarial
probe's own first bug.

A case that reveals a defect asserts the CORRECT behaviour per spec, so it
FAILS red against the current code; it is marked `# DEFECT:` inline so a
reviewer reads the assertion as a finding, not a broken test.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# file: docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/<this>.py
# parents: [0]=probes [1]=evidence [2]=<change-id> [3]=loom [4]=docs [5]=repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

from test_loom_checker_push import (  # noqa: E402
    CHANGE,
    REVIEW,
    build_repo,
    blocked_rules,
    git,
    recommit_review,
    review_body,
    run_checker,
    write_review,
    _checkpoint_after,
    _seed_intent,
)


# --- (1) trailing comment change riding on the same status line -----------


def test_close_commit_trailing_comment_change_still_matches_closed_grammar_passes(tmp_path: Path) -> None:
    """Attack: the close commit's status-line diff ALSO changes a trailing
    `# comment` annotation -- still exactly one removed and one added line.
    Spec (REQ-1): the added line must match "the closed alternative of the
    shared status regex", and STATUS's shared grammar explicitly allows a
    trailing `\\s+#.*` comment on every alternative (loom_checker.py:812-818).
    A comment edit riding along on the same physical line is still one
    logical status-line change, not a second edit.
    Expected per spec: PASS. Observed: PASS (no defect)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo, status="confirmed 2026-09-01 #old-note")
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(
        r"status: .*\n", "status: closed 2026-09-03 — PR #999 #new-note\n", text
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (2) CRLF riding on the status line only -------------------------------


def test_close_commit_crlf_line_ending_on_status_line_passes(tmp_path: Path) -> None:
    """Attack: the added status line ends `\\r\\n` instead of `\\n` (a stray
    CRLF on just that one line), while every other line in the file keeps
    `\\n`. The raw diff is still exactly one removed / one added line, and
    the checker's grammar check strips the added line before matching
    (`added[0][1:].strip()`), so the trailing `\\r` is whitespace it already
    discards -- same as the frontmatter parser's own `.strip()`.
    Expected: PASS (the CR is inert, not a shape violation). Observed: PASS
    (no defect)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    raw = (repo / intent_rel).read_bytes()
    raw = raw.replace(
        b"status: confirmed 2026-09-01\n",
        "status: closed 2026-09-03 — PR #999\r\n".encode("utf-8"),
    )
    (repo / intent_rel).write_bytes(raw)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (3) a second `status:` line inserted alongside the real one ----------


def test_close_commit_inserted_second_status_line_is_blocked(tmp_path: Path) -> None:
    """Attack: the close commit INSERTS a second `status: closed ...` line
    right after the original (unchanged) `status: confirmed ...` line.
    `parse_document` keeps the LAST `status:` value it sees, so the
    frontmatter parse reads the file as closed -- but the raw diff is an
    INSERTION (0 removed / 1 added line), not the one-removed/one-added
    transition the spec requires ("its diff on that path is exactly one
    removed and one added `status:` line").
    Expected: BLOCKED on push.review-only-head. Observed: BLOCKED (no
    defect -- condition (2)'s removed/added count catches it)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace(
        "status: confirmed 2026-09-01\n",
        "status: confirmed 2026-09-01\nstatus: closed 2026-09-03 — PR #999\n",
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "0 removed / 1 added" in result.stderr


# --- (4) merge whose SECOND parent alone carries the transition -----------


def test_close_commit_merge_whose_second_parent_carries_the_transition_passes(tmp_path: Path) -> None:
    """Attack: HEAD^ is a clean (non-conflicting) merge; the first parent
    never touches the intent file at all, only the second parent (`topic`)
    closes it, and nothing else changes. The recompute reads HEAD^'s diff
    against ITS first parent (`git diff --raw --no-renames HEAD^^ HEAD^`),
    which is a plain two-tree diff -- it shows the intent file changed
    regardless of which parent contributed the change, so a clean merge
    carrying the transition through its second parent is indistinguishable
    from an ordinary close commit, PROVIDED the merge's first parent is
    itself a valid checkpoint and no other file differs.
    Expected per spec (round 7 spec-R23, the commit message's own design):
    PASS. Observed: PASS (no defect) -- confirms the first-parent-diff
    design actually catches a same-file merge and does not wrongly block
    a clean one."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)  # HEAD is already a checkpoint here
    git(repo, "branch", "topic")
    git(repo, "checkout", "-q", "topic")
    text = re.sub(
        r"status: .*\n",
        "status: closed 2026-09-03 — PR #999\n",
        (repo / intent_rel).read_text(encoding="utf-8"),
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    git(repo, "checkout", "-q", "work")
    git(repo, "merge", "-q", "--no-ff", "-m", "merge: topic", "topic")
    merge_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, merge_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (5) the HEAD^^ existence precondition applied unconditionally --------


def test_ordinary_root_commit_branch_wrongly_blocked_by_precondition(tmp_path: Path) -> None:
    """Attack: a legitimate, minimal branch -- one ordinary code commit
    that happens to be the repo's own ROOT commit (no seed commit before
    it), followed by a checkpoint. HEAD^ never touches an intent file, let
    alone turns one `closed`; the commit message's own words are "An
    ordinary commit at HEAD^ ... is untouched by this recompute."

    `check_close_commit_shape` requires `HEAD^^` to resolve to a commit
    BEFORE it looks at whether HEAD^ touches any intent file at all
    (loom_checker.py: `pre_close_sha = git_maybe(..., f"{head_sha}^^")`,
    checked ahead of `_raw_diff_paths`/`intent_paths`). When HEAD^ is the
    repo's root commit, HEAD^^ cannot resolve, and the function reports
    `push.review-only-head` unconditionally -- even though the ordinary
    commit at HEAD^ was never a close commit and the recompute should
    never have fired.

    Expected per spec: PASS -- an ordinary commit at HEAD^ is untouched by
    this recompute, regardless of how short the branch's history is.
    Observed at 58b8f514: BLOCKED on push.review-only-head (the defect below);
    observed at efbd0198 and later: PASS -- fixed, this case is now a regression guard.
    # DEFECT (historical, fixed by efbd0198): the HEAD^^ existence precondition is evaluated unconditionally,
    # ahead of the "does HEAD^ even touch an intent file" gate, so it
    # over-fires on any close-commit-shaped position (root commit at HEAD^)
    # regardless of whether HEAD^ is a close commit. Fix: check
    # `intent_paths` (whether HEAD^'s diff touches an intent path at all)
    # before requiring HEAD^^ to resolve, or only require HEAD^^ once a
    # closing transition has actually been identified on HEAD^.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "work")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    git(repo, "add", "a.py")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")  # the repo's ROOT commit
    root_sha = git(repo, "rev-parse", "HEAD")

    write_review(
        repo,
        {
            "reviewed_sha": root_sha,
            "scope": "x",
            "vendors": ["anthropic"],
            "verdicts": [],
            "probes": [],
            "open_findings": [],
            "dispatch": [],
        },
    )
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    rules = blocked_rules(result)
    assert "push.review-only-head" not in rules, (  # fired before efbd0198; guards the fix
        "check_close_commit_shape blocks an ordinary root commit that never "
        f"touched an intent file. stderr:\n{result.stderr}"
    )


# --- (6) checkpoint parent's own reviewed_sha is stale/nonsense -----------


def test_close_commit_with_checkpoint_parent_carrying_garbage_reviewed_sha_is_blocked(tmp_path: Path) -> None:
    """Attack: HEAD^^ has the right SHAPE of a checkpoint (touches only
    review.json) but its `reviewed_sha` is neither empty nor a real commit
    -- a stale, hand-edited, or corrupted value that does not resolve to
    HEAD^^^. Spec: "its parent HEAD^^ must itself be a checkpoint ... whose
    review.json records a reviewed_sha resolving to HEAD^^^".
    Expected: BLOCKED on push.review-only-head. Observed: BLOCKED (no
    defect) -- the recompute reads the checkpoint's JSON content, not just
    its file-touch shape, and correctly refuses a checkpoint that vouches
    for nothing real."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    recommit_review(repo, review_body("not-a-real-sha-nonsense"))
    close_sha = _close_commit_here(repo, intent_rel)
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "reviewed_sha must resolve to HEAD" in result.stderr


def _close_commit_here(repo: Path, intent_rel: str) -> str:
    """Local, minimal stand-in for the sibling module's `_close_commit` --
    reused logic (status transition, single commit) kept inline here so
    this file's helper import list stays exactly the names actually used
    elsewhere; behaviourally identical to `_close_commit(extra_files=None,
    extra_line=False)`."""
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(
        r"status: .*\n", "status: closed 2026-09-03 — PR #999\n", text
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    return git(repo, "rev-parse", "HEAD")
