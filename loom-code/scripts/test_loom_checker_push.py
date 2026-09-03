"""Executable contract for `loom_checker.py push` (plan W0-04).

Every fixture is a real git repo: the push rules are about the shape of
HEAD and of review.json against that HEAD, so a mocked repo would test
nothing. The two named risks in the plan get their own cases -- amending
the code commit under a written review.json, and a review-only commit
that quietly carries a second file.

Since the W0 wave-end fixes, three things changed shape here:

* the dispatch record lives INSIDE review.json as `dispatch[]`
  (concept-model §2e), read from the reviewed commit's tree;
* `push.probes-package-tests` RUNS the recorded command itself
  (concept-model §7), so every fixture records a command that is cheap to
  execute and the agent's own `result` is recorded rather than believed;
* hook mode is entered only by `push --hook`, so a bare `push` never
  touches stdin and can never hang behind a pipe that stays open.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import codex_scaffold  # sibling module, same scripts/ dir (W0-05 plumbing exemption)

CHECKER = Path(__file__).with_name("loom_checker.py")
CHANGE = "2026-09-02-a"
REVIEW = f"docs/loom/{CHANGE}/review.json"

# Cheap enough to run once per test, and its exit code is the whole point.
PASSING_COMMAND = "python3 -c pass"
FAILING_COMMAND = "python3 -c 1/0"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


DISPATCH_ENTRIES = [
    {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
     "started": "2026-09-02T09:00:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "agent-rev", "model": "m",
     "started": "2026-09-02T10:00:00Z", "fresh_context": True},
    {"task": "T1", "role": "blind-runner", "agent_id": "agent-blind", "model": "m",
     "started": "2026-09-02T11:00:00Z", "fresh_context": True},
]


# Since the W1 adversary, an adversarial probe names a committed file and
# the command has to run THAT file: `true` exits 0 without attacking
# anything, and so does a command pointed at nothing.
ABUSE_CASES = ("empty", "boundary", "hostile")


def _adversarial_records(reviewed_sha: str, count: int,
                         command: str | None = None) -> list[dict]:
    return [
        {
            "kind": "adversarial",
            "command": command or f"python3 evidence/abuse_{name}.py",
            "sha": reviewed_sha,
            "result": "pass",
            "artifact": f"evidence/abuse_{name}.py",
        }
        for name in ABUSE_CASES[:count]
    ]


def review_body(reviewed_sha: str, **overrides) -> dict:
    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "wave 1 code delta",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m", "lens": "code",
             "verdict": "PASS", "dimension_scores": {}, "findings": [], "sha": reviewed_sha},
            {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m", "lens": "code",
             "verdict": "PASS_WITH_NOTES", "dimension_scores": {}, "findings": [], "sha": reviewed_sha},
        ],
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": reviewed_sha,
             "result": "pass", "artifact": "evidence/tests.txt"},
            # The branch touches `a.py`, which the §6 mapping types as code,
            # so push.probes-adversarial wants three of these.
            *_adversarial_records(reviewed_sha, 3),
        ],
        "open_findings": [
            {"id": "F-1", "anchor": "a.py:1", "origin_sha": "deadbee",
             "raised_by": "agent-rev", "resolved": "fixed in HEAD^"},
        ],
        "dispatch": [dict(entry) for entry in DISPATCH_ENTRIES],
    }
    body.update(overrides)
    return body


def build_repo(tmp_path: Path, *, dispatch: list[dict] | None = None,
               package_tests: str | None = None) -> Path:
    """A branch whose HEAD^ is the code commit and HEAD the review-only one."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    (repo / "evidence").mkdir()
    (repo / "evidence/tests.txt").write_text("2199 passed\n", encoding="utf-8")
    for name in ABUSE_CASES:
        (repo / f"evidence/abuse_{name}.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
    # A committed case that no longer passes -- the "regression eval that
    # stopped being one" the adversarial rule has to notice.
    (repo / "evidence/abuse_regressed.py").write_text(
        "raise SystemExit(1)\n", encoding="utf-8"
    )
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {package_tests or PASSING_COMMAND}"
        " — the fixture's whole suite (2026-09-02)\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    # The dispatch entries below claim task T1; a branch whose commits carry
    # no `Task:` trailer at all now blocks (push.dispatch-covers-tasks).
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")

    body = review_body(git(repo, "rev-parse", "HEAD"))
    if dispatch is not None:
        body["dispatch"] = dispatch
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


def write_review(repo: Path, body: dict) -> None:
    path = repo / REVIEW
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=1), encoding="utf-8")


def rebuild(repo: Path, **overrides) -> dict:
    """A review body for the current HEAD^ with `overrides` applied."""
    return review_body(git(repo, "rev-parse", "HEAD~1"), **overrides)


def recommit_review(repo: Path, body: dict) -> None:
    """Replace the review-only HEAD with one carrying `body`."""
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


# --- the happy path --------------------------------------------------------


def test_a_well_formed_checkpoint_push_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- push.review-only-head -------------------------------------------------


def test_head_carrying_a_second_file_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / "b.py").write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", REVIEW, "b.py")
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "b.py" in result.stderr


def test_head_that_is_a_code_commit_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "a.py").write_text("value = 3\n", encoding="utf-8")
    git(repo, "add", "a.py")
    git(repo, "commit", "-q", "-m", "feat: more")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_head_ref_can_be_chosen(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    good = git(repo, "rev-parse", "HEAD")
    (repo / "a.py").write_text("value = 3\n", encoding="utf-8")
    git(repo, "add", "a.py")
    git(repo, "commit", "-q", "-m", "feat: more")
    assert run_checker("push", "--head", good, cwd=repo).returncode == 0


# --- push.review-only-head: close-commit shape (W0-04) ---------------------

INTENT_REL = f"docs/loom/intent/{CHANGE}.md"


def _seed_intent(repo: Path, status: str = "confirmed 2026-09-01") -> str:
    """Amend the code commit so the intent file exists BEFORE any close
    commit -- a close commit's diff must show it going non-closed -> closed
    -- then rebuild the checkpoint (R1) on top. Returns the intent path."""
    git(repo, "reset", "-q", "--hard", "HEAD~1")  # back onto the code commit
    (repo / INTENT_REL).parent.mkdir(parents=True, exist_ok=True)
    (repo / INTENT_REL).write_text(
        f"# {CHANGE}\nstatus: {status}\n\n## Problem\nx\n", encoding="utf-8"
    )
    git(repo, "add", INTENT_REL)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return INTENT_REL


def _close_text(text: str, *, pr_number: str = "999", date: str = "2026-09-03",
                extra_line: bool = False) -> str:
    text = re.sub(r"status: .*\n", f"status: closed {date} — PR #{pr_number}\n", text)
    if extra_line:
        text = text.replace("## Problem\nx\n", "## Problem\ny\n")
    return text


def _close_commit(repo: Path, intent_rel: str, *, extra_files: dict[str, str] | None = None,
                  extra_line: bool = False) -> str:
    """A commit on the current HEAD (a checkpoint) turning the intent
    file's status to `closed`, optionally also touching `extra_files` or an
    extra unrelated line in the same file."""
    text = (repo / intent_rel).read_text(encoding="utf-8")
    (repo / intent_rel).write_text(_close_text(text, extra_line=extra_line), encoding="utf-8")
    paths = [intent_rel]
    for rel, content in (extra_files or {}).items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(content, encoding="utf-8")
        paths.append(rel)
    git(repo, "add", *paths)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    return git(repo, "rev-parse", "HEAD")


def _merge_close_commit(repo: Path, intent_rel: str) -> str:
    """A merge commit at HEAD^ whose first-parent diff carries the closed
    transition together with an unrelated file (test e)."""
    git(repo, "branch", "topic")
    git(repo, "checkout", "-q", "topic")
    (repo / "b.py").write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", "b.py")
    git(repo, "commit", "-q", "-m", "feat: b\n\nTask: T1")
    git(repo, "checkout", "-q", "work")
    git(repo, "merge", "-q", "--no-ff", "-m", "merge: topic", "topic")
    text = (repo / intent_rel).read_text(encoding="utf-8")
    (repo / intent_rel).write_text(_close_text(text), encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    return git(repo, "rev-parse", "HEAD")


def _insert_docs_commit(repo: Path, rel: str = "docs/loom/notes.md") -> None:
    """A plain docs commit that is NOT a checkpoint (touches no review.json)."""
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text("notes\n", encoding="utf-8")
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", "docs(loom): notes")


def _checkpoint_after(repo: Path, reviewed_sha: str) -> None:
    write_review(repo, review_body(reviewed_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


def test_a_close_commit_after_a_checkpoint_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit(repo, intent_rel)
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_crlf_file_wide_close_commit_passes(tmp_path: Path) -> None:
    """A legitimate close commit on a CRLF-native repo -- every line in
    both HEAD^^'s and HEAD^'s intent file ends `\\r\\n`, including the
    status line before and after -- must PASS. `core.autocrlf false` is
    set explicitly so this test is not neutralized by an ambient global
    git config silently normalizing CRLF to LF on `git add`. Regression
    for round-5: the regenerated status line used to always end in bare
    `\\n`, and separately `git_raw_text` used to read blobs through
    `subprocess.run(text=True)`, which always translates `\\r\\n` to `\\n`
    regardless of the encoding passed -- either defect alone made a
    byte-consistent CRLF close commit's regenerated blob differ from the
    real one and falsely BLOCK on `push.review-only-head`."""
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
    assert result.returncode == 0, (
        "expected PASS for a byte-consistent CRLF close commit, got "
        f"BLOCKED: {result.stderr}"
    )


def test_a_close_commit_with_a_stray_non_utf8_body_byte_passes(tmp_path: Path) -> None:
    """A legitimate close commit whose file carries a stray non-UTF-8 byte
    in the body, UNCHANGED between HEAD^^ and HEAD^, must PASS.
    Regression for round-6: `git_raw_text` decodes blob bytes with
    `errors="surrogateescape"`, but `_close_blob_failures` used to
    re-encode the regenerated text with strict UTF-8
    (`.encode("utf-8")`), so this legitimate close raised
    UnicodeEncodeError instead of performing the blob comparison."""
    repo = build_repo(tmp_path)
    intent_rel = f"docs/loom/intent/{CHANGE}.md"
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    before_bytes = b"# x\nstatus: confirmed 2026-09-01\n\n## Problem\nstray byte: \xff\n"
    (repo / intent_rel).write_bytes(before_bytes)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    raw = (repo / intent_rel).read_bytes()
    raw = raw.replace(
        b"status: confirmed 2026-09-01\n",
        "status: closed 2026-09-03 — PR #999\n".encode("utf-8"),
    )
    (repo / intent_rel).write_bytes(raw)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "expected PASS for a close commit with an unchanged stray non-UTF-8 "
        f"body byte, got BLOCKED/errored: {result.stderr}"
    )


def test_a_close_commit_that_changes_a_non_utf8_body_byte_is_blocked(tmp_path: Path) -> None:
    """Same fixture as above, but the stray body byte itself CHANGES in
    the close commit -- condition (c)'s regenerated blob must differ from
    the actual blob and BLOCK, with no exception along the way."""
    repo = build_repo(tmp_path)
    intent_rel = f"docs/loom/intent/{CHANGE}.md"
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    before_bytes = b"# x\nstatus: confirmed 2026-09-01\n\n## Problem\nstray byte: \xff\n"
    (repo / intent_rel).write_bytes(before_bytes)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "--amend", "--no-edit")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    raw = (repo / intent_rel).read_bytes()
    raw = raw.replace(
        b"status: confirmed 2026-09-01\n",
        "status: closed 2026-09-03 — PR #999\n".encode("utf-8"),
    )
    raw = raw.replace(b"stray byte: \xff\n", b"stray byte: \xfe\n")
    (repo / intent_rel).write_bytes(raw)
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, (
        "expected BLOCK for a close commit that also changes the stray "
        f"non-UTF-8 body byte, got: returncode={result.returncode} "
        f"stderr={result.stderr}"
    )
    assert "push.review-only-head" in blocked_rules(result)
    assert "HEAD^'s blob to equal the regenerated closed blob" in result.stderr


def test_a_close_commit_touching_another_file_is_blocked(tmp_path: Path) -> None:
    """Condition (a): the raw listing must be exactly one entry."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit(repo, intent_rel, extra_files={"docs/loom/notes.md": "x\n"})
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert f"expected exactly one changed path ({intent_rel})" in result.stderr
    assert f"got 2: {intent_rel}, docs/loom/notes.md" in result.stderr


def test_a_close_commit_with_an_extra_line_change_is_blocked(tmp_path: Path) -> None:
    """The extra body edit rides in the SAME file as the status change, so
    condition (a) sees one path, M, mode 100644 -- it only trips up
    condition (c): the regenerated blob (status line replaced, body
    untouched) cannot match the actual blob (status line replaced AND
    body edited)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit(repo, intent_rel, extra_line=True)
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "HEAD^'s blob to equal the regenerated closed blob" in result.stderr


def test_a_close_commit_whose_parent_is_not_a_checkpoint_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    _insert_docs_commit(repo)
    pre_close_sha = git(repo, "rev-parse", "HEAD")
    close_sha = _close_commit(repo, intent_rel)
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert pre_close_sha[:8] in result.stderr
    assert f"HEAD^^ ({pre_close_sha[:8]}) is not itself a checkpoint" in result.stderr
    assert f"expected HEAD^^ ({pre_close_sha[:8]}) to touch only review.json" in result.stderr
    # round-6: the diagnostic must carry the underlying `got` value -- the
    # actual touched path -- not just "touches something else".
    assert "docs/loom/notes.md" in result.stderr


def test_a_merge_close_commit_touching_another_file_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _merge_close_commit(repo, intent_rel)
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert f"expected exactly one changed path ({intent_rel})" in result.stderr
    assert "got 2: b.py" in result.stderr


def test_a_two_commit_branch_whose_head_caret_is_the_root_commit_passes(tmp_path: Path) -> None:
    """HEAD^ (an ordinary code commit) is itself the repo's ROOT commit --
    HEAD^^ cannot resolve. The close-commit recompute must not fire on an
    ordinary commit just because it sits at the bottom of a short branch
    (after-task W0-04 finding, adversary probe
    test_ordinary_root_commit_branch_wrongly_blocked_by_precondition)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "work")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "a.py").write_text("value = 1\n", encoding="utf-8")
    git(repo, "add", "a.py")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")  # the repo's ROOT commit
    root_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, root_sha)

    result = run_checker("push", cwd=repo)
    assert "push.review-only-head" not in blocked_rules(result), result.stderr


def test_a_close_commit_that_renames_the_intent_path_is_blocked(tmp_path: Path) -> None:
    """`--no-renames` splits a renamed-and-closed intent into a deleted old
    path and an added new path -- both match the intent template, so the
    trigger fires on either half, but the commit then touches two paths
    and condition (a) requires exactly one (after-task W0-04
    round-2/round-3 findings)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    renamed_rel = f"docs/loom/intent/{CHANGE}-renamed.md"
    text = (repo / intent_rel).read_text(encoding="utf-8")
    git(repo, "rm", "-q", intent_rel)
    (repo / renamed_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / renamed_rel).write_text(_close_text(text), encoding="utf-8")
    git(repo, "add", renamed_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert f"expected exactly one changed path ({renamed_rel})" in result.stderr
    assert f"got 2: {renamed_rel}, {intent_rel}" in result.stderr


def test_renaming_an_already_closed_intent_is_blocked(tmp_path: Path) -> None:
    """Renaming an intent file that is ALREADY `status: closed` still
    touches an intent path (both halves of the `--no-renames` split
    match the template), so the trigger fires and the commit is blocked
    for touching two paths -- by design: the recompute no longer asks
    whether the content became closed, only whether the commit touching
    an intent path has close-commit shape, and a rename never does (spec
    REQ-1, W0-04 round-3 design change)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo, status="closed 2026-08-01 — PR #100")
    renamed_rel = f"docs/loom/intent/{CHANGE}-renamed.md"
    text = (repo / intent_rel).read_text(encoding="utf-8")
    git(repo, "rm", "-q", intent_rel)
    (repo / renamed_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / renamed_rel).write_text(text, encoding="utf-8")
    git(repo, "add", renamed_rel)
    git(repo, "commit", "-q", "-m", f"chore(loom): rename closed intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "move other intent edits to an earlier commit" in result.stderr


def test_a_brand_new_already_closed_intent_is_blocked(tmp_path: Path) -> None:
    """A commit that ADDS an intent file already at `status: closed ...`
    touches an intent path (a single added path), so the trigger fires,
    but condition (a) requires status `M`, never `A` (after-task W0-04
    round-2/round-3 findings)."""
    repo = build_repo(tmp_path)
    new_rel = f"docs/loom/intent/{CHANGE}-new.md"
    (repo / new_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / new_rel).write_text(
        f"# {CHANGE}\nstatus: closed 2026-09-03 — PR #999\n\n## Problem\nx\n",
        encoding="utf-8",
    )
    git(repo, "add", new_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected status M and mode `100644` on both sides" in result.stderr
    assert "got status A, old 000000 / new 100644" in result.stderr


def test_deleting_an_already_closed_intent_is_blocked(tmp_path: Path) -> None:
    """Deleting an intent file touches an intent path, so the trigger
    fires -- and a delete is never a close commit: condition (a) checks
    the raw diff status explicitly (`M` only), rather than relying on a
    content-based transition check that a deletion could dodge either way
    (spec REQ-1, W0-04 round-3 design change)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo, status="closed 2026-08-01 — PR #100")
    git(repo, "rm", "-q", intent_rel)
    git(repo, "commit", "-q", "-m", "chore(loom): remove closed intent")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected status M and mode `100644` on both sides" in result.stderr
    assert "got status D, old 100644 / new 000000" in result.stderr


def test_an_intent_edit_that_never_touches_the_status_line_is_blocked(tmp_path: Path) -> None:
    """HEAD^ edits an intent file's Open Questions line only -- never the
    `status:` key. The trigger fires purely on the path being touched,
    with no content pre-check, so condition (a) passes (one path,
    modified, mode 100644), but condition (b)'s frontmatter value is
    still `confirmed`, never the closed alternative (spec REQ-1, W0-04
    round-3 design change)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace("## Problem\nx\n", "## Problem\nx\n\n## Open questions\ny\n")
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", "docs(loom): note an open question")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert (
        "expected HEAD^'s frontmatter `status:` value to be the closed alternative"
        in result.stderr
    )
    assert "confirmed 2026-09-01" in result.stderr


def test_a_commit_touching_no_intent_path_is_untouched(tmp_path: Path) -> None:
    """An ordinary commit at HEAD^ that never touches any intent path is
    left alone by the recompute entirely (spec REQ-1, W0-04)."""
    repo = build_repo(tmp_path)
    _seed_intent(repo)
    _insert_docs_commit(repo)
    _checkpoint_after(repo, git(repo, "rev-parse", "HEAD"))
    result = run_checker("push", cwd=repo)
    assert "push.review-only-head" not in blocked_rules(result), result.stderr


def test_a_close_commit_with_a_bom_before_the_status_key_is_blocked(tmp_path: Path) -> None:
    """A UTF-8 BOM (U+FEFF) immediately before the `status:` key makes
    that line no longer start with the literal bytes `status:` -- so
    condition (b)'s raw scan of HEAD^'s file finds ZERO `status:` lines,
    not one, and blocks on the count rather than trusting
    `parse_document`, which never runs here at all (spec REQ-1, W0-04
    round-3 finding)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(r"status: .*\n", "﻿status: closed 2026-09-03 — PR #999\n", text)
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected exactly one `status:` line in HEAD^'s file" in result.stderr
    assert "got 0" in result.stderr


def test_a_symlink_typechange_on_the_intent_path_is_blocked(tmp_path: Path) -> None:
    """The intent path is REPLACED by a symlink (a git typechange, status
    `T`) whose target string reads like a legitimate closed status line --
    a symlink's diff content IS its target text, indistinguishable from a
    real line change in text-diff output, so only the raw-listing's
    status/mode fields (condition a) catch it, never any parsed content
    (spec REQ-1, W0-04 round-3 addition)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    (repo / intent_rel).unlink()
    (repo / intent_rel).symlink_to("status: closed 2026-09-03 — PR #999")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected status M and mode `100644` on both sides" in result.stderr
    assert "got status T, old 100644 / new 120000" in result.stderr


def test_a_close_commit_with_trailing_garbage_on_the_status_line_is_blocked(tmp_path: Path) -> None:
    """The `status:` line's value is `closed <date> — PR #<n>` PLUS
    trailing text the comment group (`(?:\\s+#.*)?`) does not cover --
    `STATUS.fullmatch` on the whole value fails it, so condition (b)
    blocks before regeneration is even attempted (spec REQ-1, W0-04
    round-3 addition)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(
        r"status: .*\n", "status: closed 2026-09-03 — PR #999 extra garbage\n", text
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert (
        "expected HEAD^'s frontmatter `status:` value to be the closed alternative"
        in result.stderr
    )
    assert "extra garbage" in result.stderr


def test_a_body_decoy_status_line_pair_is_blocked(tmp_path: Path) -> None:
    """A decoy `status:` line, changed from `confirmed` to a legitimate
    closed value, sits in the BODY -- the real frontmatter `status:` line
    is never touched. HEAD^'s file now has TWO raw lines starting with
    `status:`, so condition (b)'s count guard blocks it before
    `parse_document` (which would in any case ignore the body line) is
    even consulted for a value (spec REQ-1, W0-04 round-3 addition)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace(
        "## Problem\nx\n", "## Problem\nx\nstatus: confirmed 2026-09-01\n"
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", "docs(loom): seed a body decoy line")
    decoy_seed_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, decoy_seed_sha)

    text = text.replace(
        "status: confirmed 2026-09-01\n",
        "status: closed 2026-09-03 — PR #999\n",
    )
    # Only the BODY decoy line changes -- the real frontmatter status line,
    # near the top of the file, is untouched.
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected exactly one `status:` line in HEAD^'s file" in result.stderr
    assert "got 2" in result.stderr


def test_a_body_decoy_line_alone_is_blocked_by_frontmatter_scope(tmp_path: Path) -> None:
    """The real frontmatter `status:` line is DELETED outright (not
    replaced), and a decoy `status: closed ...` line is inserted in the
    body instead -- HEAD^'s file has exactly ONE raw `status:` line
    (the count guard alone cannot catch this), but it sits after the
    file's `## ` heading, so `parse_document` never records it into
    frontmatter and condition (b)'s value is empty, not the closed
    alternative (spec REQ-1, W0-04 round-3 addition)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace("status: confirmed 2026-09-01\n", "")
    text = text.replace("x\n", "x\nstatus: closed 2026-09-03 — PR #999\n")
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert (
        "expected HEAD^'s frontmatter `status:` value to be the closed alternative"
        in result.stderr
    )


def test_a_close_commit_that_adds_a_trailing_comment_is_blocked(tmp_path: Path) -> None:
    """The ONLY difference from a legitimate close is a trailing `# ...`
    comment appended to the new `status:` value -- the grammar itself
    allows a comment (STATUS's shared `(?:\\s+#.*)?`), so condition (b)
    passes, but step (c) always regenerates the bare `status: closed
    <date> — PR #<N>` form with NO comment, so the regenerated blob does
    not match the actual one and (c) blocks it (spec REQ-1, W0-04
    round-3 addition: regeneration is stricter than the grammar it
    matches against)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = re.sub(
        r"status: .*\n", "status: closed 2026-09-03 — PR #999 #shipped\n", text
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "HEAD^'s blob to equal the regenerated closed blob" in result.stderr


def test_a_close_commit_that_drops_the_confirmed_lines_own_comment_passes(tmp_path: Path) -> None:
    """HEAD^^'s `status:` line carries a trailing `# ...` comment
    (`confirmed 2026-09-01 #old-note`); the close commit's new line drops
    it entirely (`closed 2026-09-03 — PR #999`, no comment). Step (c)'s
    regeneration REPLACES the whole value, comment included, so the
    regenerated blob has no comment either and matches the actual one --
    this passes (spec REQ-1, W0-04 round-3 addition: regeneration drops
    whatever comment the BEFORE line carried, since only the value is
    replaced, not appended to)."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo, status="confirmed 2026-09-01 #old-note")
    close_sha = _close_commit(repo, intent_rel)
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_root_commit_adding_an_already_closed_intent_is_blocked(tmp_path: Path) -> None:
    """The repo's ROOT commit itself ADDS an intent already `status:
    closed ...`. Relative to git's empty tree, an added path is ALWAYS
    status `A`, never `M` -- so condition (a) blocks this before
    condition (d)'s checkpoint-parent check is ever reached; per
    `check_close_commit_shape`'s own docstring, (d)'s `pre_close_sha is
    None` branch is structurally unreachable for exactly this reason
    (spec REQ-1, W0-04 round-2/round-3 findings)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "work")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    new_rel = f"docs/loom/intent/{CHANGE}-root.md"
    (repo / new_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / new_rel).write_text(
        f"# {CHANGE}\nstatus: closed 2026-09-03 — PR #999\n\n## Problem\nx\n",
        encoding="utf-8",
    )
    git(repo, "add", new_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")  # ROOT commit
    close_sha = git(repo, "rev-parse", "HEAD")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert close_sha[:8] in result.stderr
    assert "expected status M and mode `100644` on both sides" in result.stderr
    assert "got status A, old 000000 / new 100644" in result.stderr


def test_manifest_intent_path_drift_fails_closed(tmp_path: Path) -> None:
    """The trigger must not fail open when the manifest's own intent path
    template has drifted from `INTENT_PATH_TEMPLATE`, the checker's own
    expected constant -- `check_close_commit_shape` reports
    push.review-only-head naming the unexpected template rather than
    silently building a matcher from it (spec REQ-1, W0-04 round-3
    addition, Codex spec note). Called directly (not via the CLI
    subprocess), since the manifest is a module-level constant path the
    real CLI always resolves to this repo's own contract/manifest.yaml."""
    sys.path.insert(0, str(Path(__file__).parent))
    import loom_checker  # local import: needs the module, not the CLI

    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit(repo, intent_rel)
    _checkpoint_after(repo, close_sha)

    manifest = loom_checker.load_manifest()
    drifted = json.loads(json.dumps(manifest))
    drifted["artifacts"]["intent"]["path"] = "docs/loom/wrong/<change-id>.md"

    head_sha = git(repo, "rev-parse", "HEAD")
    failures = loom_checker.check_close_commit_shape(drifted, repo, head_sha)
    assert failures
    assert all(rule == "push.review-only-head" for rule, _ in failures)
    assert any("docs/loom/wrong/<change-id>.md" in msg for _, msg in failures)
    assert any("docs/loom/intent/<change-id>.md" in msg for _, msg in failures)


# --- push.reviewed-sha -----------------------------------------------------


def test_reviewed_sha_pointing_elsewhere_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, review_body("0000000"))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


def test_abbreviated_reviewed_sha_is_accepted(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(repo, review_body(parent[:8]))
    assert run_checker("push", cwd=repo).returncode == 0


def test_amending_the_code_commit_invalidates_the_review(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    stale = git(repo, "rev-parse", "HEAD")
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    (repo / "a.py").write_text("value = 99\n", encoding="utf-8")
    git(repo, "add", "a.py")
    git(repo, "commit", "-q", "--amend", "--no-edit")
    git(repo, "cherry-pick", stale)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


# --- push.open-findings-closed --------------------------------------------


def test_an_unresolved_finding_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[{"id": "F-2", "anchor": "a.py:1", "raised_by": "rev-b"}],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.open-findings-closed" in blocked_rules(result)
    assert "F-2" in result.stderr


def test_a_dismissed_finding_counts_as_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[
                {"id": "F-2", "anchor": "a.py:1", "raised_by": "rev-b",
                 "dismissed": "out of scope by agent-rev"}
            ],
        ),
    )
    assert run_checker("push", cwd=repo).returncode == 0


# --- push.dismissed-by-reviewer (spec A-2, concept-model §5) ---------------


def test_a_dismissal_naming_nobody_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[
                {"id": "F-3", "anchor": "a.py:1", "raised_by": "agent-rev",
                 "dismissed": "not worth it"}
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.dismissed-by-reviewer" in blocked_rules(result)
    assert "F-3" in result.stderr


def test_a_dismissal_by_the_implementer_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[
                {"id": "F-4", "anchor": "a.py:1", "raised_by": "agent-rev",
                 "dismissed": "already handled by agent-imp"}
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.dismissed-by-reviewer" in blocked_rules(result)
    assert "agent-imp" in result.stderr


def test_a_dismissal_by_a_stranger_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[
                {"id": "F-5", "anchor": "a.py:1", "raised_by": "agent-rev",
                 "dismissed": "waved through by kouko"}
            ],
        ),
    )
    assert "push.dismissed-by-reviewer" in blocked_rules(run_checker("push", cwd=repo))


def test_a_dismissal_with_an_explicit_by_field_is_accepted(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            open_findings=[
                {"id": "F-6", "anchor": "a.py:1", "raised_by": "agent-rev",
                 "dismissed": {"reason": "out of scope", "by": "agent-blind"}}
            ],
        ),
    )
    assert run_checker("push", cwd=repo).returncode == 0, "blind-runner may dismiss"


# --- push.probes-package-tests: the checker runs the command itself --------


def test_a_probe_command_that_exits_zero_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "exit code 0" in result.stdout


def test_a_probe_command_that_exits_one_blocks_despite_result_pass(tmp_path: Path) -> None:
    """The agent's `result` is a record; the observed exit code decides."""
    repo = build_repo(tmp_path, package_tests=FAILING_COMMAND)
    body = rebuild(repo)
    body["probes"][0]["command"] = FAILING_COMMAND
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "exit code 1" in result.stdout


def test_a_dirty_working_tree_blocks_the_probe(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "scratch.txt").write_text("uncommitted\n", encoding="utf-8")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "clean" in result.stderr


def test_missing_package_test_probe_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(parent, probes=[{"kind": "blind-run", "command": "run", "result": "pass"}]),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)


# --- push.probes-adversarial: the floor, the type gate, the re-run ---------


def _adversarial(reviewed_sha: str, count: int, command: str | None = None):
    return [
        {"kind": "package-tests", "command": PASSING_COMMAND, "sha": reviewed_sha,
         "result": "pass", "artifact": "evidence/tests.txt"},
    ] + _adversarial_records(reviewed_sha, count, command)


def test_two_adversarial_probes_do_not_meet_the_floor(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    recommit_review(repo, rebuild(repo, probes=_adversarial(reviewed, 2)))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "2 are usable" in result.stderr


def test_no_adversarial_probe_at_all_blocks_a_code_change(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    recommit_review(repo, rebuild(repo, probes=_adversarial(reviewed, 0)))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "none recorded" in result.stderr


def test_an_adversarial_probe_that_no_longer_passes_does_not_count(tmp_path: Path) -> None:
    """The recorded `result: pass` is never believed; the checker runs it."""
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    probes = _adversarial(reviewed, 3)
    probes[-1]["artifact"] = "evidence/abuse_regressed.py"
    probes[-1]["command"] = "python3 evidence/abuse_regressed.py"
    recommit_review(repo, rebuild(repo, probes=probes))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "exited 1 when the checker ran it" in result.stderr


def test_an_adversarial_probe_against_another_sha_does_not_count(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    probes = _adversarial(reviewed, 3)
    probes[-1]["sha"] = git(repo, "rev-parse", "main")
    recommit_review(repo, rebuild(repo, probes=probes))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "not the reviewed commit" in result.stderr


def test_a_docs_only_change_owes_no_adversarial_probe(tmp_path: Path) -> None:
    """The §6 mapping types `notes.md` as docs, which needs no adversary."""
    repo = tmp_path / "docsrepo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    (repo / "notes.md").write_text("prose\n", encoding="utf-8")
    (repo / "evidence").mkdir()
    (repo / "evidence/tests.txt").write_text("ok\n", encoding="utf-8")
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {PASSING_COMMAND} — the "
        "fixture's whole suite (2026-09-02)\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: notes")
    reviewed = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(reviewed, probes=_adversarial(reviewed, 0)))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- push.verdicts-ge-2 ----------------------------------------------------


def test_one_reviewer_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            verdicts=[{"reviewer": "rev-a", "vendor": "anthropic", "model": "m",
                       "verdict": "PASS"}],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_the_same_reviewer_twice_is_not_two_reviewers(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            verdicts=[
                {"reviewer": "rev-a", "verdict": "PASS"},
                {"reviewer": "rev-a", "verdict": "PASS"},
            ],
        ),
    )
    assert "push.verdicts-ge-2" in blocked_rules(run_checker("push", cwd=repo))


def test_a_needs_revision_latest_round_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            verdicts=[
                {"reviewer": "rev-a", "verdict": "PASS", "round": 1},
                {"reviewer": "rev-b", "verdict": "PASS", "round": 1},
                {"reviewer": "rev-a", "verdict": "NEEDS_REVISION", "round": 2},
                {"reviewer": "rev-b", "verdict": "PASS", "round": 2},
            ],
        ),
    )
    assert "push.verdicts-ge-2" in blocked_rules(run_checker("push", cwd=repo))


# --- push.reviewer-ne-implementer, read from review.json `dispatch[]` ------


def test_a_reviewer_who_also_implemented_blocks(tmp_path: Path) -> None:
    entries = [
        {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
         "started": "2026-09-02T09:00:00Z"},
        {"task": "T1", "role": "reviewer", "agent_id": "agent-imp", "model": "m",
         "started": "2026-09-02T10:00:00Z"},
    ]
    repo = build_repo(tmp_path, dispatch=entries)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)
    assert "agent-imp" in result.stderr


def test_a_missing_dispatch_record_fails_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, dispatch=[])
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)


def test_a_dispatch_record_without_a_reviewer_blocks(tmp_path: Path) -> None:
    entries = [
        {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
         "started": "2026-09-02T09:00:00Z"},
    ]
    repo = build_repo(tmp_path, dispatch=entries)
    assert "push.reviewer-ne-implementer" in blocked_rules(run_checker("push", cwd=repo))


def test_a_malformed_dispatch_entry_fails_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, dispatch=["not an object"])
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)


def test_a_dispatch_entry_missing_a_required_key_blocks(tmp_path: Path) -> None:
    entries = [
        {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
         "started": "2026-09-02T09:00:00Z"},
        {"task": "T1", "role": "reviewer", "agent_id": "agent-rev"},
        {"task": "T1", "role": "blind-runner", "agent_id": "agent-blind", "model": "m",
         "started": "2026-09-02T11:00:00Z"},
    ]
    repo = build_repo(tmp_path, dispatch=entries)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)
    assert "model" in result.stderr


def test_a_reviewer_absent_from_the_dispatch_record_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "verdict": "PASS"},
                {"reviewer": "ghost-reviewer", "verdict": "PASS"},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)
    assert "ghost-reviewer" in result.stderr


def test_the_working_tree_copy_of_review_json_is_ignored(tmp_path: Path) -> None:
    """The dispatch record is read from the reviewed commit's tree, so
    emptying the working-tree copy cannot make a reviewer disappear."""
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    body["dispatch"] = []
    write_review(repo, body)  # working tree only, never committed
    result = run_checker("push", cwd=repo)
    assert "push.reviewer-ne-implementer" not in blocked_rules(result)


# --- shape of the run ------------------------------------------------------


def test_a_push_with_no_review_json_in_head_is_blocked(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_every_failure_is_reported_not_just_the_first(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(
        repo,
        review_body(
            "0000000",
            probes=[],
            open_findings=[{"id": "F-9", "anchor": "a.py:1", "raised_by": "rev-b"}],
        ),
    )
    rules = blocked_rules(run_checker("push", cwd=repo))
    assert {"push.reviewed-sha", "push.probes-package-tests", "push.open-findings-closed"} <= rules


# --- hook mode is opt-in: `push --hook` ------------------------------------


def run_hook(payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "push", "--hook"], capture_output=True, text=True,
        cwd=str(cwd), input=json.dumps(payload),
    )


def test_a_bare_push_never_reads_stdin_and_cannot_hang(tmp_path: Path) -> None:
    """The hook flag, not the shape of stdin, selects hook mode: a plain
    `push` behind an open pipe must return instead of blocking on read()."""
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")  # no review.json in HEAD
    result = subprocess.run(
        [sys.executable, str(CHECKER), "push"],
        stdin=subprocess.PIPE, capture_output=True, text=True, cwd=str(repo), timeout=5,
    )
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_hook_mode_ignores_a_non_push_bash_command(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "c.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "c.py")
    git(repo, "commit", "-q", "-m", "feat(x): code on top of the review commit")
    result = run_hook({"tool_name": "Bash", "tool_input": {"command": "ls -la"}, "cwd": str(repo)}, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert "BLOCK" not in result.stderr


PUSH_SHAPED = (
    "git push origin HEAD",
    "cd sub && git push",
    "gh pr create --fill",
    "gh pr merge 12 --squash",
    "git -C /tmp/other push",
    "git --git-dir=/tmp/x/.git --work-tree=/tmp/x push",
    'eval "git push"',
    "git  push",
    "make build; git push --force-with-lease",
    "GIT_SSH_COMMAND=ssh git push",
    "true || gh pr merge --admin",
    "/usr/bin/git push",
    'bash -c "git push"',
    'sh -c "git push"',
    'zsh -c "git push"',
    'dash -c "git push"',
    "xargs git push",
)

NOT_PUSH_SHAPED = (
    "ls -la",
    "git pushd",
    "echo git push",
    'git commit -m "push"',
    "git status",
    "gh pr view 12",
    "git log --oneline",
    'bash -c "ls"',
    "bash script.sh",
)


def test_hook_mode_recognises_every_push_shape(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "c.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "c.py")
    git(repo, "commit", "-q", "-m", "feat(x): code on top of the review commit")
    for cmd in PUSH_SHAPED:
        result = run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(repo)}, cwd=tmp_path)
        assert result.returncode == 2, (cmd, result.stdout, result.stderr)
        assert "push.review-only-head" in blocked_rules(result), cmd


def test_hook_mode_lets_non_push_shapes_through(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    (repo / "c.py").write_text("x = 1\n", encoding="utf-8")
    git(repo, "add", "c.py")
    git(repo, "commit", "-q", "-m", "feat(x): code on top of the review commit")
    for cmd in NOT_PUSH_SHAPED:
        result = run_hook({"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": str(repo)}, cwd=tmp_path)
        assert result.returncode == 0, (cmd, result.stderr)


def test_hook_mode_passes_a_clean_push(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_hook({"tool_name": "Bash", "tool_input": {"command": "git push"}, "cwd": str(repo)}, cwd=tmp_path)
    assert result.returncode == 0, result.stderr


def test_hook_mode_malformed_payload_fails_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = subprocess.run([sys.executable, str(CHECKER), "push", "--hook"], capture_output=True,
                            text=True, cwd=str(repo), input="{not json")
    assert result.returncode == 2


def test_hook_mode_without_a_payload_fails_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = subprocess.run([sys.executable, str(CHECKER), "push", "--hook"], capture_output=True,
                            text=True, cwd=str(repo), input="")
    assert result.returncode == 2


# --- push.review-schema ----------------------------------------------------


def test_questions_is_optional(tmp_path: Path) -> None:
    """A change with no fork asks nothing; absence is not a schema error."""
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    assert "questions" not in body
    recommit_review(repo, body)
    assert run_checker("push", cwd=repo).returncode == 0


def test_a_well_formed_questions_entry_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, rebuild(repo, questions=[
        {"decision_point": 1, "text": "Is this what you want?", "type": "what"},
        {"decision_point": 3, "text": "Delete the old rows?", "type": "consequence"},
    ]))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_questions_entry_with_an_unknown_type_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, rebuild(repo, questions=[
        {"decision_point": 1, "text": "?", "type": "vibes"},
    ]))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)
    assert "type: vibes" in result.stderr


def test_a_questions_entry_missing_its_decision_point_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, rebuild(repo, questions=[{"text": "?", "type": "what"}]))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)
    assert "decision_point" in result.stderr


def test_questions_as_an_object_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, rebuild(repo, questions={"decision_point": 1}))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)
    assert "not list" in result.stderr


def test_a_missing_review_key_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    del body["vendors"]
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)
    assert "vendors" in result.stderr


def test_a_review_without_dispatch_blocks_the_schema(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    del body["dispatch"]
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)
    assert "dispatch" in result.stderr


def test_a_wrong_container_type_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, rebuild(repo, vendors="anthropic"))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-schema" in blocked_rules(result)


def test_a_too_short_reviewed_sha_blocks_the_schema(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, review_body("abc12"))
    result = run_checker("push", cwd=repo)
    assert "push.review-schema" in blocked_rules(result)


def test_a_non_hex_reviewed_sha_blocks_the_schema(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, review_body("HEAD~1"))
    assert "push.review-schema" in blocked_rules(run_checker("push", cwd=repo))


def test_a_reviewed_sha_that_names_no_commit_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(repo, review_body("abcdef1234567"))
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


def test_verdict_entries_missing_reviewer_or_verdict_do_not_count(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "verdict": "PASS"},
                {"reviewer": "agent-blind"},
                {"verdict": "PASS"},
                {"note": "a stray object"},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


# --- push.reviewed-sha ties every latest-round verdict to reviewed_sha -----


def test_a_verdict_missing_sha_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS", "sha": parent},
                {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS_WITH_NOTES"},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)
    assert "agent-blind" in result.stderr


def test_a_verdict_sha_pointing_to_an_older_commit_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    stale = git(repo, "rev-parse", "HEAD~2")
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS", "sha": parent},
                {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS_WITH_NOTES", "sha": stale},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)
    assert "agent-blind" in result.stderr


def test_every_verdict_sha_equal_to_reviewed_sha_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS", "sha": parent},
                {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
                 "verdict": "PASS_WITH_NOTES", "sha": parent},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_spec_scoped_verdict_missing_sha_still_blocks(tmp_path: Path) -> None:
    """No scope is exempt from push.reviewed-sha, `scope: spec` included."""
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        rebuild(
            repo,
            verdicts=[
                {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
                 "scope": "spec", "verdict": "PASS", "sha": parent},
                {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
                 "scope": "spec", "verdict": "PASS_WITH_NOTES"},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


# --- push.probes-package-tests, recomputed against the reviewed commit -----


def test_a_probe_for_another_commit_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    body["probes"][0]["sha"] = git(repo, "rev-parse", "HEAD")
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)


def test_a_probe_without_a_sha_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    del body["probes"][0]["sha"]
    recommit_review(repo, body)
    assert "push.probes-package-tests" in blocked_rules(run_checker("push", cwd=repo))


def test_a_probe_without_a_command_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    body["probes"][0]["command"] = "   "
    recommit_review(repo, body)
    assert "push.probes-package-tests" in blocked_rules(run_checker("push", cwd=repo))


def test_a_probe_artifact_absent_from_the_reviewed_tree_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    body["probes"][0]["artifact"] = "evidence/never-committed.txt"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "never-committed" in result.stderr


def test_a_probe_without_an_artifact_is_still_accepted(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    del body["probes"][0]["artifact"]
    recommit_review(repo, body)
    assert run_checker("push", cwd=repo).returncode == 0


# --- operands --------------------------------------------------------------


def test_the_dead_base_flag_is_gone(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", "--base", "main", cwd=repo)
    assert result.returncode == 2
    assert "--base" in result.stderr


# --- push.frozen-store-untouched (W3 adversary P07) ------------------------


FROZEN_STORES = ("plans", "specs", "backlog", "design", "archive")


def _rewrite_history_with(repo: Path, rel: str) -> subprocess.CompletedProcess:
    """Replace the branch's code commit with one that also writes `rel`."""
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("frozen store write\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): write into a frozen store\n\nTask: T1")
    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return run_checker("push", cwd=repo)


@pytest.mark.parametrize("store", FROZEN_STORES)
def test_a_write_into_a_frozen_store_blocks(tmp_path: Path, store: str) -> None:
    repo = build_repo(tmp_path)
    result = _rewrite_history_with(repo, f"docs/loom/{store}/2026-09-02-note.md")
    assert result.returncode == 1, result.stdout
    assert "push.frozen-store-untouched" in blocked_rules(result)
    assert store in result.stderr


def test_the_archived_marker_itself_is_still_writable(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = _rewrite_history_with(repo, "docs/loom/plans/ARCHIVED.md")
    assert result.returncode == 0, result.stderr


def test_a_live_store_is_untouched_by_the_freeze(tmp_path: Path) -> None:
    """`docs/loom/intent/` is not a frozen store, so `push.frozen-store-
    untouched` never fires on a write there -- unlike the plain-text
    write this fixture makes, though: since W0-04's structural trigger
    (spec REQ-1, round-3 design change), ANY write to an intent path is
    now also subject to `push.review-only-head`'s close-commit shape, and
    this write is not a close commit, so THAT rule blocks it instead."""
    repo = build_repo(tmp_path)
    result = _rewrite_history_with(repo, "docs/loom/intent/2026-09-02-a.md")
    assert "push.frozen-store-untouched" not in blocked_rules(result), result.stderr


# --- push.dispatch-covers-tasks: content-bound plumbing exemption (W0-05) --
#
# The exhaustive positive/negative matrix (genuine refresh, altered byte,
# extra file, deletion, mode-only change, symlink, stamp mismatch, altered
# shim, run-from-the-copy, unlisted path) lives in the adversary's probe
# file (docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/
# test_abuse_plumbing_exemption.py). These two cover combinations that
# probe file does not: restoring one deleted plumbing path (rather than a
# whole-tree version bump), and a commit that mixes an exempt plumbing
# path with an ordinary code file -- the exemption is per-path, not
# per-commit.


def test_a_restored_deleted_plumbing_path_with_no_trailer_is_exempt(tmp_path: Path) -> None:
    """A genuine scaffold write establishes the canonical baseline (with a
    trailer); a later commit deletes ONE plumbing path and then a second
    genuine scaffold call restores exactly that file, byte-and-mode
    identical to this running tree's canonical -- with no trailer. Unlike
    the probe's version-bump refresh, only a single sibling module changes
    here."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore(loom): scaffold hooks\n\nTask: T1")
    baseline_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(baseline_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / ".codex" / "hooks" / "git_exec.py").unlink()
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: drop a plumbing file\n\nTask: T1")
    deleted_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(deleted_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore(loom): restore scaffold file")
    restored_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(restored_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def _decoy_stamp_scaffold(repo: Path) -> None:
    """Scaffold genuine bytes into `repo`, then corrupt only the checker
    copy's own version stamp -- every other plumbing path (git_exec.py
    included) stays byte-identical to this running tree's canonical."""
    codex_scaffold.scaffold(repo)
    checker_copy = repo / ".codex" / "hooks" / "loom_checker.py"
    text = checker_copy.read_text(encoding="utf-8")
    stamped = text.replace(
        codex_scaffold.stamp_line(codex_scaffold.plugin_version()),
        codex_scaffold.stamp_line("0.0.1-decoy"),
        1,
    )
    assert stamped != text, "the stamp line must actually be present to mutate"
    checker_copy.write_text(stamped, encoding="utf-8")


def _canonical_git_exec_source() -> str:
    """This module's own sibling `git_exec.py` -- the canonical bytes the
    running checker would scaffold, without going through
    `codex_scaffold.scaffold()` again (which would also rewrite the
    checker copy's stamp back to genuine, undoing a decoy fixture)."""
    return (Path(__file__).parent / "git_exec.py").read_text(encoding="utf-8")


def test_a_plumbing_path_is_blocked_when_the_committed_checker_copys_stamp_is_a_decoy(
    tmp_path: Path,
) -> None:
    """REQ-3 (Design decision): the stamp gate reads the COMMITTED checker
    copy's stamp and compares it with this running checker's own version
    ONCE per commit, before any per-path blob comparison. A commit that
    touches only `git_exec.py`, restoring it to genuine canonical bytes,
    is still not exempt when the checker copy sitting beside it in that
    same commit's tree carries a decoy stamp -- the per-path blob match
    on git_exec.py alone must never be enough."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    _decoy_stamp_scaffold(repo)
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        "# tampered\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: bootstrap scaffold with decoy stamp\n\nTask: T1")
    baseline_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(baseline_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        _canonical_git_exec_source(), encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: refresh git_exec.py only")
    refreshed_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(refreshed_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, result.stdout
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    match = re.search(r"BLOCK push\.dispatch-covers-tasks: (.*)", result.stderr)
    assert match, result.stderr
    assert "version" in match.group(1)


def test_a_plumbing_path_is_blocked_when_the_checker_copy_is_absent_at_that_commit(
    tmp_path: Path,
) -> None:
    """Same gate, the other trigger: no `.codex/hooks/loom_checker.py` at
    all in that commit's tree -- nothing to read a stamp from at all, so
    a `git_exec.py`-only refresh in that same tree is not exempt either."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    (repo / ".codex" / "hooks" / "loom_checker.py").unlink()
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        "# tampered\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m",
        "chore: bootstrap scaffold with no checker copy\n\nTask: T1")
    baseline_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(baseline_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        _canonical_git_exec_source(), encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: refresh git_exec.py only")
    refreshed_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(refreshed_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, result.stdout
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    match = re.search(r"BLOCK push\.dispatch-covers-tasks: (.*)", result.stderr)
    assert match, result.stderr
    assert "absent" in match.group(1)


def test_a_commit_mixing_exempt_plumbing_and_a_code_file_still_needs_a_trailer(
    tmp_path: Path,
) -> None:
    """The exemption is per-path (Design decision), not per-commit: a
    genuine scaffold refresh landing in the SAME commit as an ordinary
    code file still owes a `Task:` trailer for the code file. Asserting
    only "code" in result.stderr (the original form of this test) stayed
    green even with no exemption at all -- b.py alone puts "code" there.
    Assert on the recomputed kind set itself instead: "code" survives,
    "gate" (the `**/hooks/**` type the scaffold paths carry) does not --
    that only holds once the exempt plumbing paths are actually removed
    from the set, which is the one thing this test exists to prove."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    (repo / "b.py").write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore(loom): scaffold hooks and add b.py")
    new_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(new_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, result.stdout
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    match = re.search(r"BLOCK push\.dispatch-covers-tasks: (.*)", result.stderr)
    assert match, result.stderr
    message = match.group(1)
    assert "code" in message
    assert "gate" not in message
