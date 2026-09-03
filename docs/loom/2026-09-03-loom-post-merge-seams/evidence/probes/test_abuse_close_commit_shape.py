"""Adversarial probes against `check_close_commit_shape` (spec REQ-1,
`push.review-only-head`'s close-commit shape recompute, W0-04). Updated at
fd3d9dbf (round 3): the recompute is now regenerate-and-compare, triggered
structurally on any intent-template path in HEAD^'s first-parent raw diff,
not on a before/after content parse -- two round-1 cases below (marked
"expectation changed at fd3d9dbf") whose old assertions targeted the prior
design have been corrected in place, not deleted, so the regression they
guard stays covered. Each case is a real commit chain in a temp git repo;
the checker is run as `loom_checker.py push`, never mocked.

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


def test_close_commit_trailing_comment_change_is_blocked_by_regeneration(tmp_path: Path) -> None:
    """expectation changed at fd3d9dbf: under regenerate-and-compare, step
    (c) always writes the BARE form `status: closed <date> — PR #<N>`, with
    no comment appended, regardless of what comment either the before or
    after line carried -- so a close commit that ALSO changes the trailing
    `# comment` annotation on the same status line is now BLOCKED, even
    though STATUS's shared grammar still accepts a trailing `\\s+#.*`
    comment on the closed alternative (condition (b) passes; condition (c)
    does not, because regeneration never reproduces any comment).
    Attack: the close commit's status-line diff ALSO changes a trailing
    `# comment` annotation -- still exactly one removed and one added line,
    and grammar-valid on its own. Round-1's expectation (PASS, matching the
    OLD diff-based design) no longer holds.
    Expected per spec (REQ-1, W0-04 round-3): BLOCKED on
    push.review-only-head, blob mismatch. Observed: BLOCKED (no defect --
    this file's own round-1 expectation was stale, not the code)."""
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
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "HEAD^'s blob to equal the regenerated closed blob" in result.stderr


# --- (2) CRLF riding on the status line only -------------------------------


def test_close_commit_crlf_line_ending_on_status_line_is_blocked(tmp_path: Path) -> None:
    """Attack: the added status line ends `\\r\\n` instead of `\\n` (a stray
    CRLF on just that one line), while every other line in the file keeps
    `\\n`. Under regenerate-and-compare (condition (c)), the checker
    rebuilds the canonical closed blob and compares it byte-for-byte to
    HEAD^'s actual blob; the trailing `\\r` is one byte more than the
    regenerated canonical, so the close commit is not shape-conformant.
    The earlier PASS expectation was a leftover of the first grammar-strip
    design (`added[0][1:].strip()`, which discarded the `\\r` as
    whitespace) and only held locally because this machine's global
    `core.autocrlf=input` stripped the CR at `git add`; pinning
    `core.autocrlf=false` on the temp repo makes the byte survive to the
    commit on every machine.
    Expected: BLOCK push.review-only-head. Observed: BLOCK
    push.review-only-head (correct)."""
    repo = build_repo(tmp_path)
    git(repo, "config", "core.autocrlf", "false")
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
    assert result.returncode == 1, result.stderr
    assert "push.review-only-head" in result.stderr


# --- (3) a second `status:` line inserted alongside the real one ----------


def test_close_commit_inserted_second_status_line_is_blocked(tmp_path: Path) -> None:
    """expectation changed at fd3d9dbf: the diagnostic is no longer a
    removed/added diff-line count (that belonged to the OLD design). Under
    regenerate-and-compare, condition (b) does its own raw, whole-file scan
    for every line starting with the literal bytes `status:`
    (`_status_line_positions`, not scoped to the diff) and requires exactly
    one; two lines fails the count before any value is even parsed.
    Attack: the close commit INSERTS a second `status: closed ...` line
    right after the original (unchanged) `status: confirmed ...` line.
    `parse_document` keeps the LAST `status:` value it sees, so a
    content-only reading would call the file closed -- but HEAD^'s file now
    has TWO raw `status:` lines, not one.
    Expected: BLOCKED on push.review-only-head. Observed: BLOCKED (no
    defect -- condition (b)'s raw-line count catches it; round-1's
    diagnostic substring was stale, not the block itself)."""
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
    assert "expected exactly one `status:` line in HEAD^'s file" in result.stderr
    assert "got 2" in result.stderr


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


# --- (7) HEAD^^ itself carries two `status:` lines to regenerate from -----


def test_close_commit_head_pre_caret_with_two_status_lines_is_blocked(tmp_path: Path) -> None:
    """Attack: HEAD^^ (the file BEFORE the close, not HEAD^ as in probe 3)
    already has TWO raw `status:` lines -- the real frontmatter one plus a
    body decoy carrying the identical text. The close commit changes the
    frontmatter line to `closed ...` AND deletes the body decoy in the same
    edit, so HEAD^'s file ends up with exactly ONE raw `status:` line --
    condition (b)'s HEAD^-side count guard is satisfied, so this is a
    genuinely different probe from case 3 above (which trips condition
    (b)). Condition (c) does its OWN independent raw-line count on
    HEAD^^'s file before it will regenerate anything
    (`_close_blob_failures`'s own `_status_line_positions(before_text)`
    check, separate from condition (b)'s), and two lines there means there
    is no single line to regenerate from.
    Expected per spec (REQ-1 condition c): BLOCKED on push.review-only-head,
    named "exactly one `status:` line in HEAD^^'s file to regenerate from".
    Observed: BLOCKED (no defect -- confirms (c) does not fall back to
    picking one of several candidate lines, or to trusting the deletion as
    intentional)."""
    repo = build_repo(tmp_path)
    intent_rel = f"docs/loom/intent/{CHANGE}.md"
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / intent_rel).write_text(
        "# x\nstatus: confirmed 2026-09-01\n\n## Problem\nx\n"
        "status: confirmed 2026-09-01\n",
        encoding="utf-8",
    )
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    (repo / intent_rel).write_text(
        "# x\nstatus: closed 2026-09-03 — PR #999\n\n## Problem\nx\n",
        encoding="utf-8",
    )
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert (
        "exactly one `status:` line in HEAD^^'s file to regenerate from"
        in result.stderr
    )
    assert "got 2" in result.stderr


# --- (8) `status:` is not the FIRST frontmatter key ------------------------


def test_close_commit_status_key_not_first_in_frontmatter_passes(tmp_path: Path) -> None:
    """Attack: HEAD^^'s intent file has other frontmatter keys (`owner:`,
    `kind:`) sitting BEFORE `status:` -- an attempt to see whether the
    regenerate-and-compare recompute silently assumes `status:` is the
    first line, e.g. by regenerating with the wrong line index or by
    letting the extra keys shift `_status_line_positions`'s single raw
    match. `_status_line_positions` scans the WHOLE file for lines
    starting with the literal bytes `status:`, unconditioned on position,
    so an ordinary, well-formed close should be unaffected by where in
    the frontmatter the key sits.
    Expected per spec: PASS (frontmatter key order is not part of the
    close-commit shape). Observed: PASS (no defect)."""
    repo = build_repo(tmp_path)
    intent_rel = f"docs/loom/intent/{CHANGE}.md"
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / intent_rel).write_text(
        "# x\nowner: kouko\nstatus: confirmed 2026-09-01\nkind: engineering\n"
        "\n## Problem\nx\n",
        encoding="utf-8",
    )
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(r"status: .*\n", "status: closed 2026-09-03 — PR #999\n", text)
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (9) manifest intent template mistyped ---------------------------------


def test_manifest_intent_template_mistyped_blocks_with_named_diagnostic(tmp_path: Path) -> None:
    """Attack: the manifest's `artifacts.intent.path` has been hand-edited
    away from `INTENT_PATH_TEMPLATE`. Rather than trusting a mistyped glob
    to build a matcher that could match nothing (or something wider) and
    fail OPEN, `check_close_commit_shape` compares the live manifest to its
    own constant first and reports the drift by name. Called directly
    (like `test_manifest_intent_path_drift_fails_closed` in the sibling
    push suite) since the manifest is a module-level path the CLI always
    resolves to this repo's real contract/manifest.yaml -- there is no CLI
    flag to point it at a temp file.
    Expected per spec (REQ-1): BLOCKED, naming both the expected and the
    drifted template. Observed: BLOCKED (no defect)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit_here(repo, intent_rel)
    _checkpoint_after(repo, close_sha)

    sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))
    import loom_checker  # local import: needs the module, not the CLI

    manifest = loom_checker.load_manifest()
    drifted = json.loads(json.dumps(manifest))
    drifted["artifacts"]["intent"]["path"] = "docs/loom/renamed-intent/<change-id>.md"

    head_sha = git(repo, "rev-parse", "HEAD")
    failures = loom_checker.check_close_commit_shape(drifted, repo, head_sha)
    assert failures
    assert all(rule == "push.review-only-head" for rule, _ in failures)
    assert any("docs/loom/renamed-intent/<change-id>.md" in msg for _, msg in failures)
    assert any("docs/loom/intent/<change-id>.md" in msg for _, msg in failures)


# --- (10) CRLF throughout the WHOLE file, both HEAD^^ and HEAD^ -----------


def test_close_commit_crlf_file_wide_regeneration_drops_the_cr(tmp_path: Path) -> None:
    """Attack (per round-4 dispatch): a repo whose intent files are CRLF
    throughout -- not just the round-1 probe's single CRLF-ending status
    line riding alone (which every OTHER line in that file kept `\\n`, so
    the regenerated line's `ending = "\\n"` accidentally matched it). Here
    EVERY line in both HEAD^^'s and HEAD^'s file ends `\\r\\n`, including
    the status line before and after -- a plausible, self-consistent
    close commit on a CRLF-native repo, with `core.autocrlf false` set
    explicitly so this probe is not neutralized by an ambient global git
    config silently normalizing CRLF to LF on `git add` (observed on this
    machine without the explicit config -- a second, environment-dependent
    hazard this probe controls for).

    `_regenerated_closed_text` derives the replaced line's ending from
    `lines[index].endswith("\\n")` -- true for BOTH `\\n` and `\\r\\n` --
    and always reconstructs it as the literal two characters `\\n`, never
    `\\r\\n`. In a file where the untouched lines around it stay `\\r\\n`,
    the regenerated status line is the only line missing its `\\r`, so the
    regenerated blob can never equal the real one.

    Expected per spec (REQ-1, condition c): a legitimate, byte-consistent
    CRLF close commit should PASS -- nothing in the spec singles out line
    endings as a reason to reject a close. Observed: BLOCKED on
    push.review-only-head (blob mismatch) -- a real close commit on a
    CRLF-native repo is unconditionally rejected.
    # DEFECT: `_regenerated_closed_text` (loom_checker.py, step c) always
    # appends bare `\\n` for a replaced line's ending, even when the
    # original ending -- and every other line's ending in the same file --
    # is `\\r\\n`. Fix: capture the ORIGINAL ending's exact bytes (e.g.
    # `stripped = lines[index].rstrip("\\r\\n"); ending = lines[index][len(stripped):]`)
    # instead of collapsing every non-empty ending to `\\n`.
    """
    repo = build_repo(tmp_path)
    git(repo, "config", "core.autocrlf", "false")
    git(repo, "config", "core.safecrlf", "false")
    intent_rel = f"docs/loom/intent/{CHANGE}.md"
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    before_text = "# x\r\nstatus: confirmed 2026-09-01\r\n\r\n## Problem\r\nx\r\n"
    (repo / intent_rel).write_bytes(before_text.encode("utf-8"))
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    raw = (repo / intent_rel).read_bytes()
    raw = raw.replace(
        b"status: confirmed 2026-09-01\r\n",
        "status: closed 2026-09-03 — PR #999\r\n".encode("utf-8"),
    )
    (repo / intent_rel).write_bytes(raw)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (  # FIXED by 6f7a19a5; kept as a regression guard
        "expected PASS for a byte-consistent CRLF close commit, got "
        f"BLOCKED: {result.stderr}"
    )


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
