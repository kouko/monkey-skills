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
import yaml

import codex_scaffold  # sibling module, same scripts/ dir (W0-05 plumbing exemption)
import loom_checker  # W0-02: change_lane unit tests mirror the adversary's probes

CHECKER = Path(__file__).with_name("loom_checker.py")
MANIFEST_PATH = Path(__file__).resolve().parents[1] / "contract" / "manifest.yaml"
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


# --- push.review-only-head: the close line rides in the review-only
# commit itself (W1-03) -------------------------------------------------


def _review_only_close_commit(repo: Path, intent_rel: str, *, kind: str = "PR",
                              identifier: str = "999", date: str = "2026-09-03",
                              extra_line: bool = False,
                              third_file: str | None = None) -> str:
    """Replace the review-only HEAD (built by `_seed_intent`) with one that
    ALSO carries the close line: review.json plus the intent file's status
    line flipping to a closed form -- the new combined shape (spec REQ-1,
    W1-03). `third_file`, when given, rides along as a THIRD touched path
    -- still must block."""
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    text = (repo / intent_rel).read_text(encoding="utf-8")
    descriptor = f"PR #{identifier}" if kind == "PR" else f"branch {identifier}"
    text = re.sub(r"status: .*\n", f"status: closed {date} — {descriptor}\n", text)
    if extra_line:
        text = text.replace("## Problem\nx\n", "## Problem\ny\n")
    (repo / intent_rel).write_text(text, encoding="utf-8")
    paths = [REVIEW, intent_rel]
    if third_file is not None:
        (repo / third_file).parent.mkdir(parents=True, exist_ok=True)
        (repo / third_file).write_text("x\n", encoding="utf-8")
        paths.append(third_file)
    git(repo, "add", *paths)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return git(repo, "rev-parse", "HEAD")


def test_review_only_head_with_pr_form_status_line_passes(tmp_path: Path) -> None:
    """The review-only commit touches review.json AND the intent file, but
    the intent file's whole diff is its `status:` line flipping to the PR
    closed form -- must PASS, not BLOCK on a second touched path."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    _review_only_close_commit(repo, intent_rel, kind="PR", identifier="999")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.review-only-head" not in blocked_rules(result)


def test_review_only_head_with_branch_form_status_line_passes(tmp_path: Path) -> None:
    """Same shape, but the closed form names a branch instead of a PR."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    _review_only_close_commit(repo, intent_rel, kind="branch", identifier="ship-it")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.review-only-head" not in blocked_rules(result)


def test_review_only_head_with_another_intent_line_changed_is_blocked(tmp_path: Path) -> None:
    """Same shape, but an UNRELATED intent body line changes alongside the
    status flip -- the close-line exemption stays scoped to the status
    line alone and must still BLOCK."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    _review_only_close_commit(repo, intent_rel, extra_line=True)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


def test_review_only_head_with_a_third_file_is_blocked(tmp_path: Path) -> None:
    """Same shape, but a THIRD file rides in the same commit -- still
    blocks; the exemption is exactly {review.json, this change's intent}."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    _review_only_close_commit(repo, intent_rel, third_file="docs/loom/notes.md")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "docs/loom/notes.md" in result.stderr


def test_the_old_separate_close_commit_shape_still_passes_with_branch_form(tmp_path: Path) -> None:
    """The OLD shape -- a close commit of its own under a review-only
    commit -- must keep passing, now also with the branch form."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    close_sha = _close_commit_with_kind(repo, intent_rel, kind="branch", identifier="ship-it")
    _checkpoint_after(repo, close_sha)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def _close_commit_with_kind(repo: Path, intent_rel: str, *, kind: str,
                            identifier: str, date: str = "2026-09-03") -> str:
    """Like `_close_commit`, but the closed form is chosen by `kind`
    ('PR' or 'branch') rather than always the PR form."""
    text = (repo / intent_rel).read_text(encoding="utf-8")
    descriptor = f"PR #{identifier}" if kind == "PR" else f"branch {identifier}"
    text = re.sub(r"status: .*\n", f"status: closed {date} — {descriptor}\n", text)
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): close intent {CHANGE}")
    return git(repo, "rev-parse", "HEAD")


# --- intake.confirmed: both closed forms are terminal (W1-03) --------------


def _intent_only_repo(tmp_path: Path, status: str, change_id: str = CHANGE) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    intent_rel = f"docs/loom/intent/{change_id}.md"
    (repo / intent_rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / intent_rel).write_text(
        f"# {change_id}\nstatus: {status}\n\n## Problem\nx\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def test_intake_write_plan_blocks_the_pr_closed_form_as_terminal(tmp_path: Path) -> None:
    repo = _intent_only_repo(tmp_path, "closed 2026-09-03 — PR #999")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "closed (PR #999)" in result.stderr
    assert "start a new intent" in result.stderr


def test_intake_write_plan_blocks_the_branch_closed_form_as_terminal(tmp_path: Path) -> None:
    repo = _intent_only_repo(tmp_path, "closed 2026-09-05 — branch ship-it")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "closed (branch ship-it)" in result.stderr
    assert "start a new intent" in result.stderr


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


# --- push.reviewed-sha: content-tree bound (W1-02) -------------------------


def test_reviewed_sha_message_only_code_commit_rewrite_passes(tmp_path: Path) -> None:
    """reviewed_sha / message_only_code_commit_rewrite / passes
    Attack: `git commit --amend` rewrites the code commit's MESSAGE only
    (a trailer added, no file touched) after the checkpoint was already
    recorded against the original sha, then the review-only commit is
    replayed on top of the amended one -- same tree throughout, a brand
    new commit id. RED before W1-02: `reviewed_id != parent` compared
    exact commit ids and blocked even though nothing a reviewer looked at
    moved. GREEN after: `same_reviewed_content` falls back to
    `content_tree_id`, and a message-only rewrite's tree never moves."""
    repo = build_repo(tmp_path)
    original_code_sha = git(repo, "rev-parse", "HEAD~1")
    git(repo, "checkout", "-q", original_code_sha)
    git(repo, "commit", "-q", "--amend", "-m", "feat: a (message rewritten)\n\nTask: T1")
    new_code_sha = git(repo, "rev-parse", "HEAD")
    git(repo, "rebase", "-q", "--onto", new_code_sha, original_code_sha, "work")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_reviewed_sha_review_only_commit_stacked_between_verdict_and_head_passes(
    tmp_path: Path,
) -> None:
    """reviewed_sha / review_only_commit_stacked / passes
    Attack: every verdict is recorded against the CODE commit, but the
    pushed review-only HEAD's `reviewed_sha` names a SEPARATE review-only
    commit stacked one level higher on that same code commit -- its tree,
    minus this change's own review.json, is byte-identical to the code
    commit's. RED before W1-02: `verdict_id != reviewed_id` compared exact
    commit ids. GREEN after: content matches once review.json is set
    aside."""
    repo = build_repo(tmp_path)
    code_sha = git(repo, "rev-parse", "HEAD~1")
    git(repo, "reset", "-q", "--hard", code_sha)

    round_a = review_body(code_sha)
    write_review(repo, round_a)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review round A")
    review_y = git(repo, "rev-parse", "HEAD")

    round_b = review_body(review_y)
    round_b["verdicts"] = round_a["verdicts"]  # still sha'd to code_sha, not review_y
    write_review(repo, round_b)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review round B")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_reviewed_sha_extra_file_change_between_verdict_and_head_still_blocks(
    tmp_path: Path,
) -> None:
    """reviewed_sha / extra_file_change_between / still_blocks
    Attack: same shape as the pass case above, but the intermediate
    review-only commit ALSO carries an unrelated file change (`b.py`) --
    a genuine content difference, not just review.json. Regression pin:
    `content_tree_id` excludes ONLY this change's review.json, so a real
    file difference must still block."""
    repo = build_repo(tmp_path)
    code_sha = git(repo, "rev-parse", "HEAD~1")
    git(repo, "reset", "-q", "--hard", code_sha)

    round_a = review_body(code_sha)
    write_review(repo, round_a)
    (repo / "b.py").write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", REVIEW, "b.py")
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review round A + b.py")
    review_y = git(repo, "rev-parse", "HEAD")

    round_b = review_body(review_y)
    round_b["verdicts"] = round_a["verdicts"]
    write_review(repo, round_b)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review round B")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)


def test_reviewed_sha_recorded_verdict_sha_not_resolving_still_blocks_with_existing_message(
    tmp_path: Path,
) -> None:
    """reviewed_sha / recorded_verdict_sha_not_resolving / still_blocks
    Attack: a verdict records a `sha` that names no commit at all. W1-02
    never touches this branch (the message names no "commit"/"content"
    word to update) -- pinned so a future edit cannot silently change it."""
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
                 "verdict": "PASS_WITH_NOTES", "sha": "abcdef1234567"},
            ],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewed-sha" in blocked_rules(result)
    assert "does not resolve to a commit" in result.stderr


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
    assert "not the reviewed content" in result.stderr


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


# --- W1-01: a fix round needs only the raising reader ----------------------
#
# These build their own two-commit branch (a code commit, then a fix
# commit) rather than reusing `build_repo`/`recommit_review`, because the
# scenario needs a real second review-only checkpoint on top of a real fix
# commit -- the shape `latest_round`/`check_verdicts` actually recompute
# from, not two review bodies layered over the same parent.

FIX_ROUND_DISPATCH = [
    {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
     "started": "2026-09-05T09:00:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-a", "model": "m",
     "started": "2026-09-05T09:10:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-b", "model": "m",
     "started": "2026-09-05T09:11:00Z", "fresh_context": True},
    {"task": "T1", "role": "reviewer", "agent_id": "rev-c", "model": "m",
     "started": "2026-09-05T09:12:00Z", "fresh_context": True},
]


def _fix_round_body(reviewed_sha: str, *, scope: str, verdicts: list[dict],
                    open_findings: list[dict]) -> dict:
    return {
        "reviewed_sha": reviewed_sha,
        "scope": scope,
        "vendors": ["anthropic"],
        "verdicts": verdicts,
        "probes": [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": reviewed_sha,
             "result": "pass", "artifact": "evidence/tests.txt"},
        ],
        "open_findings": open_findings,
        "dispatch": FIX_ROUND_DISPATCH,
    }


def _init_fix_round_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {PASSING_COMMAND}"
        " — the fixture's whole suite (2026-09-05)\n",
        encoding="utf-8",
    )
    (repo / "evidence").mkdir(parents=True, exist_ok=True)
    (repo / "evidence/tests.txt").write_text("all passed\n", encoding="utf-8")
    return repo


def _commit_fix_round_review(repo: Path, body: dict) -> str:
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return git(repo, "rev-parse", "HEAD")


def test_first_round_of_a_checkpoint_still_needs_the_lane_floor(tmp_path: Path) -> None:
    """A checkpoint's first round (no earlier round of the same scope) keeps
    the plain reviewer-count floor, even when the round already carries
    `scope` and `open_findings` -- the fix-round exemption never applies to
    round 1."""
    repo = _init_fix_round_repo(tmp_path)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    (repo / "notes/F.md").write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")
    body = _fix_round_body(
        code_sha,
        scope="checkpoint",
        verdicts=[
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": code_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a"},
        ],
    )
    _commit_fix_round_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def _build_fix_round_scenario(tmp_path: Path, *, touch_outside_anchor: bool) -> Path:
    """Round 1: `rev-a` and `rev-b` both review; `rev-a` raises a finding
    anchored at `notes/F.md:1`, `rev-b` passes clean. The fix commit
    resolves it; round 2 carries only `rev-a`'s confirming PASS.
    `touch_outside_anchor` decides whether the fix commit also edits
    `notes/G.md`, a file no open finding names."""
    repo = _init_fix_round_repo(tmp_path)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    (repo / "notes/F.md").write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    round1 = _fix_round_body(
        code_sha,
        scope="checkpoint",
        verdicts=[
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": code_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a"},
        ],
    )
    _commit_fix_round_review(repo, round1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    if touch_outside_anchor:
        (repo / "notes/G.md").write_text("# G\nunrelated\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    round2 = _fix_round_body(
        fix_sha,
        scope="checkpoint",
        verdicts=round1["verdicts"] + [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a",
             "resolved": f"fixed in {fix_sha[:8]}; confirmed rev-a round 2"},
        ],
    )
    _commit_fix_round_review(repo, round2)
    return repo


def test_a_fix_round_counts_a_standing_pass_inside_the_anchor(tmp_path: Path) -> None:
    """Round 2 carries only `rev-a`'s (the raising reader's) PASS, and the
    fix delta touches only `notes/F.md`, the file the finding anchors.
    `rev-b`'s round-1 PASS stands, so the full-lane floor of 2 is met and
    the push is not blocked."""
    repo = _build_fix_round_scenario(tmp_path, touch_outside_anchor=False)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.verdicts-ge-2" not in blocked_rules(result)


def test_a_fix_round_with_a_path_outside_the_anchors_still_blocks(tmp_path: Path) -> None:
    """Same round-2-single-reader shape, but the fix commit also touches
    `notes/G.md`, a file no open finding names -- the standing-PASS
    exemption must never cover a delta that leaves the finding's own
    files, so the floor of 2 distinct readers still applies."""
    repo = _build_fix_round_scenario(tmp_path, touch_outside_anchor=True)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_ghost_verdict_earlier_round_cannot_stand(tmp_path: Path) -> None:
    """A `ghost` PASS with no dispatch[] entry at all is planted in round 1
    alongside the two real reviewers (rev-a raises F-1, rev-b passes
    clean). Round 2 carries only rev-a's confirming PASS, with the fix
    delta confined to notes/F.md -- exactly the anchor rev-a raised, the
    same shape that lets a real co-reviewer stand. `ghost` has no
    dispatch[] entry as reviewer/blind-runner/adversary in any round, so
    it poisons round 1 for standing purposes: nobody from that round --
    not even the legitimately dispatched rev-b -- can stand on it, and the
    full-lane floor of 2 falls back to a plain headcount of 1 (rev-a
    alone), which blocks."""
    repo = _init_fix_round_repo(tmp_path)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    (repo / "notes/F.md").write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    round1 = _fix_round_body(
        code_sha,
        scope="checkpoint",
        verdicts=[
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": code_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
            {"reviewer": "ghost", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a"},
        ],
    )
    _commit_fix_round_review(repo, round1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    round2 = _fix_round_body(
        fix_sha,
        scope="checkpoint",
        verdicts=round1["verdicts"] + [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha, "raised_by": "rev-a",
             "resolved": f"fixed in {fix_sha[:8]}"},
        ],
    )
    _commit_fix_round_review(repo, round2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_dispatched_non_returning_reviewer_still_stands(tmp_path: Path) -> None:
    """Regression: with no ghost anywhere, `rev-b` -- a genuinely dispatched
    reviewer (FIX_ROUND_DISPATCH names it as `reviewer`) who passed clean in
    round 1 and never raised anything -- does not need to return in round 2
    when the fix delta stays inside the anchor of the finding the
    returning reader (rev-a) raised. The round-poisoning check this task
    adds must not punish a clean round: `rev-b` still stands, the
    full-lane floor of 2 is met by headcount 1 (rev-a) + standing 1
    (rev-b), and the push is not blocked."""
    repo = _build_fix_round_scenario(tmp_path, touch_outside_anchor=False)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.verdicts-ge-2" not in blocked_rules(result)


def test_round_scoring_uses_the_checkpoints_own_scope(tmp_path: Path) -> None:
    """A wave-end checkpoint reached round 3 with only one reviewer (a
    single-reader fix round the wave-end checkpoint itself already
    accepted); the branch-end checkpoint that follows starts its own round
    1 with two reviewers. Without per-scope round selection, `latest_round`
    would pick the globally-highest round number (the wave-end's round 3,
    one reviewer) and block the branch-end push that actually has two."""
    repo = _init_fix_round_repo(tmp_path)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    (repo / "notes/F.md").write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    wave_sha = git(repo, "rev-parse", "HEAD")
    wave_verdicts = [
        {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
         "scope": "wave-end:1", "round": 3, "verdict": "PASS", "dimension_scores": {},
         "sha": wave_sha, "findings": []},
    ]
    wave_body = _fix_round_body(
        wave_sha, scope="wave-end:1", verdicts=wave_verdicts, open_findings=[],
    )
    _commit_fix_round_review(repo, wave_body)

    (repo / "notes/H.md").write_text("# H\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add H\n\nTask: T1")
    branch_sha = git(repo, "rev-parse", "HEAD")
    # review.json accumulates every round of the change: the wave-end
    # round stays in `verdicts[]` alongside the new branch-end round.
    branch_body = _fix_round_body(
        branch_sha,
        scope="branch-end",
        verdicts=wave_verdicts + [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "scope": "branch-end", "round": 1, "verdict": "PASS", "dimension_scores": {},
             "sha": branch_sha, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "scope": "branch-end", "round": 1, "verdict": "PASS", "dimension_scores": {},
             "sha": branch_sha, "findings": []},
        ],
        open_findings=[],
    )
    _commit_fix_round_review(repo, branch_body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr
    assert "push.verdicts-ge-2" not in blocked_rules(result)


def test_a_multi_name_raised_by_requires_every_named_reviewer_to_return(tmp_path: Path) -> None:
    """A finding's `raised_by` names two reviewers, comma-separated
    (`"rev-a, rev-b"`). Round 2 brings back only the third, uninvolved
    reviewer `rev-c` -- `rev-a` and `rev-b` are both still required, so
    neither of their round-1 PASSes may stand and the floor of 2 is not
    met even though a reviewer did return."""
    repo = _init_fix_round_repo(tmp_path)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    (repo / "notes/F.md").write_text("# F\nv1\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: add F\n\nTask: T1")
    code_sha = git(repo, "rev-parse", "HEAD")

    round1 = _fix_round_body(
        code_sha,
        scope="checkpoint",
        verdicts=[
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "NEEDS_REVISION", "dimension_scores": {}, "sha": code_sha,
             "findings": [{"severity": "important", "dimension": "correctness",
                           "anchor": "notes/F.md:1", "text": "wrong", "fix": "fix it"}]},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
            {"reviewer": "rev-c", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 1, "verdict": "PASS", "dimension_scores": {}, "sha": code_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
             "raised_by": "rev-a, rev-b"},
        ],
    )
    _commit_fix_round_review(repo, round1)

    (repo / "notes/F.md").write_text("# F\nv2 fixed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "fix: address finding\n\nTask: T1")
    fix_sha = git(repo, "rev-parse", "HEAD")

    round2 = _fix_round_body(
        fix_sha,
        scope="checkpoint",
        verdicts=[
            {"reviewer": "rev-c", "vendor": "anthropic", "model": "m", "lens": "code",
             "round": 2, "verdict": "PASS", "dimension_scores": {}, "sha": fix_sha, "findings": []},
        ],
        open_findings=[
            {"id": "F-1", "anchor": "notes/F.md:1", "origin_sha": code_sha,
             "raised_by": "rev-a, rev-b",
             "resolved": f"fixed in {fix_sha[:8]}"},
        ],
    )
    _commit_fix_round_review(repo, round2)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)


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
    """`main` (the seed commit) has genuinely different content from the
    reviewed commit -- unlike naming this same change's own prior
    review-only commit (W1-02: that now matches on content, since the two
    trees differ only by review.json)."""
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    body["probes"][0]["sha"] = git(repo, "rev-parse", "main")
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


# --- push.dispatch-covers-tasks: evidence-only task covered by an
# adversary dispatch entry (W0-02 fix, adversary-first tasks) -------------


def test_an_evidence_only_task_is_covered_by_an_adversary_dispatch_entry(
    tmp_path: Path,
) -> None:
    """An adversary-first task (e.g. W0-01) whose trailered commit touches
    only `**/evidence/**` paths needs no implementer dispatch entry -- the
    adversary who wrote the probe covers it. Giving it an implementer
    entry too would trip push.reviewer-ne-implementer, so the checker
    must accept the adversary-only shape."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / "evidence/probe_w9.py").write_text(
        "raise SystemExit(0)\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "test: adversary probe\n\nTask: W9-01")
    new_sha = git(repo, "rev-parse", "HEAD")
    dispatch = [dict(entry) for entry in DISPATCH_ENTRIES]
    dispatch.append(
        {"task": "W9-01", "role": "adversary", "agent_id": "agent-adv", "model": "m",
         "started": "2026-09-02T12:00:00Z", "fresh_context": True}
    )
    write_review(repo, review_body(new_sha, dispatch=dispatch))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert "push.dispatch-covers-tasks" not in blocked_rules(result)


def test_an_evidence_plus_code_task_still_needs_an_implementer_entry(
    tmp_path: Path,
) -> None:
    """The same commit also touches a non-evidence path (`b.py`) under the
    same `Task:` trailer -- the adversary-only exemption is per-task, not
    per-path, so a task with ANY non-evidence path still needs an
    implementer dispatch entry, adversary entry or not."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    (repo / "evidence/probe_w9.py").write_text(
        "raise SystemExit(0)\n", encoding="utf-8"
    )
    (repo / "b.py").write_text("value = 2\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "test: adversary probe plus code\n\nTask: W9-01")
    new_sha = git(repo, "rev-parse", "HEAD")
    dispatch = [dict(entry) for entry in DISPATCH_ENTRIES]
    dispatch.append(
        {"task": "W9-01", "role": "adversary", "agent_id": "agent-adv", "model": "m",
         "started": "2026-09-02T12:00:00Z", "fresh_context": True}
    )
    write_review(repo, review_body(new_sha, dispatch=dispatch))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1, result.stdout
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    match = re.search(r"BLOCK push\.dispatch-covers-tasks: (.*)", result.stderr)
    assert match, result.stderr
    assert "W9-01" in match.group(1)


def test_a_plumbing_path_is_blocked_when_the_checker_copy_is_a_symlink(
    tmp_path: Path,
) -> None:
    """REQ-3 (round-2 after-task finding): the stamp gate reads the
    committed checker copy's CONTENT but must also require its git mode
    be a plain `100644` file. A symlink whose blob content -- not a real
    file's content, the symlink's OWN target string -- happens to spell
    exactly the expected stamp line satisfies the old content-only check,
    so a `git_exec.py`-only refresh sitting beside that symlink in the
    same commit must still not be exempt."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    checker_copy = repo / ".codex" / "hooks" / "loom_checker.py"
    checker_copy.unlink()
    checker_copy.symlink_to(
        codex_scaffold.stamp_line(codex_scaffold.plugin_version())
    )
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        "# tampered\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m",
        "chore: bootstrap scaffold with a symlinked checker copy and a "
        "tampered git_exec.py\n\nTask: T1")
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
    assert "symlink" in match.group(1)


def test_a_plumbing_path_is_blocked_when_the_checker_copy_mode_is_not_100644(
    tmp_path: Path,
) -> None:
    """Same gate, the mode-mismatch trigger: a genuine, byte-identical
    checker copy that is `chmod +x`'d (mode `100755`) still fails the
    gate -- content alone is never enough, the tracked mode must also be
    the plain `100644` a scaffold write always produces."""
    repo = build_repo(tmp_path)

    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    checker_copy = repo / ".codex" / "hooks" / "loom_checker.py"
    checker_copy.chmod(checker_copy.stat().st_mode | 0o111)
    (repo / ".codex" / "hooks" / "git_exec.py").write_text(
        "# tampered\n", encoding="utf-8"
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m",
        "chore: bootstrap scaffold with an executable checker copy and a "
        "tampered git_exec.py\n\nTask: T1")
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
    assert "mode mismatch" in match.group(1)


# --- W0-02: change_lane -----------------------------------------------------
# Unit-test mirrors of docs/loom/2026-09-03-small-change-lane/evidence/probes/
# test_abuse_change_lane.py -- kept here as the permanent regression lock;
# the probe file is the adversary's, this file is the implementer's.


def _lane_init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "lane_repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def _lane_commit(repo: Path, files: dict[str, str], message: str) -> str:
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


@pytest.mark.parametrize(
    "files",
    [
        {"loom-code/scripts/test_lane_a.py": "def test_x():\n    assert True\n"},
        {"README.md": "docs change\n"},
        {".github/workflows/x.yml": "name: x\non: push\n"},
        {"requirements-dev.txt": "pytest\n"},
        {"docs/loom/memory/note.md": "a memory note\n"},
    ],
    ids=["test-file", "docs", "ci-workflow", "requirements", "memory"],
)
def test_change_lane_preauthorised_classes_are_small(tmp_path: Path, files: dict) -> None:
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(repo, files, "chore: lane class probe")
    assert loom_checker.change_lane(repo, sha) == "small"


@pytest.mark.parametrize(
    "files,fragment",
    [
        ({"loom-code/scripts/lane_helper.py": "x = 1\n"}, "non-test code"),
        ({"loom-code/hooks/lane.sh": "#!/bin/sh\necho x\n"}, "gate"),
        ({"loom-code/skills/lane/SKILL.md": "# lane\n"}, "skill"),
        ({"loom-code/contract/templates/lane.md": "# t\n"}, "interface surface"),
    ],
    ids=["nontest-code", "hook", "skill", "template"],
)
def test_change_lane_full_triggers(tmp_path: Path, files: dict, fragment: str) -> None:
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(repo, files, "feat: lane trigger probe")
    lane, reason = loom_checker.change_lane_detail(repo, sha)
    assert lane == "full"
    assert fragment in reason


def test_change_lane_kickoff_defaults_is_full(tmp_path: Path) -> None:
    """W0-02 branch-end fix: a standing document (here KICKOFF-DEFAULTS.md,
    whose lines are gate inputs) always forces the full lane -- intent
    point 1 / PRINCIPLES.md non-negotiable 2."""
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(
        repo,
        {"docs/loom/KICKOFF-DEFAULTS.md": "standing-docs: waived -- probe (2026-09-04)\n"},
        "chore: kickoff-defaults probe",
    )
    lane, reason = loom_checker.change_lane_detail(repo, sha)
    assert lane == "full"
    assert "standing document" in reason


def test_change_lane_two_plugins_is_full_even_test_only(tmp_path: Path) -> None:
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(
        repo,
        {
            "loom-code/scripts/test_a.py": "def test_a():\n    assert True\n",
            "loom-design/scripts/test_b.py": "def test_b():\n    assert True\n",
        },
        "test: two-plugin probe",
    )
    assert loom_checker.change_lane(repo, sha) == "full"


def test_change_lane_ignores_this_changes_own_review_json(tmp_path: Path) -> None:
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(
        repo, {f"docs/loom/{CHANGE}/review.json": '{"reviewed_sha": "x"}\n'}, "chore(loom): review only"
    )
    assert loom_checker.change_lane(repo, sha) == "small"


# --- W0-02: push.verdicts-ge-2 floor is lane-dependent ----------------------


def _lane_push_repo(
    tmp_path: Path, *, files: dict[str, str], kickoff_lines: list[str],
    verdicts: list[dict], review_overrides: dict | None = None,
) -> Path:
    repo = tmp_path / "lane_repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    # KICKOFF-DEFAULTS.md lands on the base branch, not the change branch:
    # it is a standing document (branch-end fix, W0-02) and would otherwise
    # force full lane on every one of these small-lane fixtures merely for
    # carrying the test's package-tests/second-vendor scaffolding.
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"- package-tests: {PASSING_COMMAND} — the fixture's suite (2026-09-04)", *kickoff_lines]
    kickoff.write_text("# Kickoff Defaults\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    git(repo, "add", "seed.txt", "docs/loom/KICKOFF-DEFAULTS.md")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    (repo / "evidence").mkdir(exist_ok=True)
    for name in ABUSE_CASES:
        (repo / f"evidence/abuse_{name}.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    (repo / "evidence/tests.txt").write_text("1 passed\n", encoding="utf-8")
    for rel, content in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: lane push probe\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")
    overrides = dict(review_overrides or {})
    overrides["verdicts"] = [dict(entry, sha=reviewed_sha) for entry in verdicts]
    overrides.setdefault(
        "probes",
        [
            {"kind": "package-tests", "command": PASSING_COMMAND, "sha": reviewed_sha,
             "result": "pass", "artifact": "evidence/tests.txt"},
            *_adversarial_records(reviewed_sha, 3),
        ],
    )
    overrides.setdefault("dispatch", [dict(entry) for entry in DISPATCH_ENTRIES])
    write_review(repo, review_body(reviewed_sha, **overrides))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


_ONE_ANTHROPIC_VERDICT = [
    {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m", "lens": "code",
     "verdict": "PASS", "dimension_scores": {}, "findings": []},
]
_TWO_ANTHROPIC_VERDICTS = [
    {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m", "lens": "code",
     "verdict": "PASS", "dimension_scores": {}, "findings": []},
    {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m", "lens": "code",
     "verdict": "PASS_WITH_NOTES", "dimension_scores": {}, "findings": []},
]


def test_small_lane_verdict_floor_is_one(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/test_floor.py": "def test_x():\n    assert True\n"},
        kickoff_lines=["- docs-lint: none — not adopted (2026-09-04)"],
        verdicts=_ONE_ANTHROPIC_VERDICT,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_full_lane_verdict_floor_stays_two_and_names_the_lane(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/floor_helper.py": "x = 1\n"},
        kickoff_lines=["- docs-lint: none — not adopted (2026-09-04)"],
        verdicts=_ONE_ANTHROPIC_VERDICT,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.verdicts-ge-2" in blocked_rules(result)
    assert "full lane" in result.stderr


# --- W0-02: second-vendor: ask ----------------------------------------------


def test_second_vendor_ask_answer_none_passes(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/ask_none.py": "x = 1\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_TWO_ANTHROPIC_VERDICTS,
        review_overrides={"second_vendor": "none"},
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


def test_second_vendor_ask_missing_answer_blocks_in_full_lane(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/ask_missing.py": "x = 1\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_TWO_ANTHROPIC_VERDICTS,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


def test_second_vendor_ask_not_asked_in_small_lane(tmp_path: Path) -> None:
    repo = _lane_push_repo(
        tmp_path,
        files={"loom-code/scripts/test_ask_small.py": "def test_x():\n    assert True\n"},
        kickoff_lines=[
            "- second-vendor: ask — trial (2026-09-04)",
            "- docs-lint: none — not adopted (2026-09-04)",
        ],
        verdicts=_ONE_ANTHROPIC_VERDICT,
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr


# --- W0-02: docs-lint KICKOFF-DEFAULTS grammar ------------------------------


def test_docs_lint_is_a_declared_kickoff_defaults_key() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    names = {entry["name"] for entry in manifest.get("kickoff_defaults", [])}
    assert "docs-lint" in names


def test_second_vendor_grammar_includes_ask() -> None:
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    entry = next(e for e in manifest["kickoff_defaults"] if e["name"] == "second-vendor")
    assert "ask" in entry["grammar"]


# --- W0-02 fix round: dot-dirs are not plugins; every change-folder record
# is excluded (not an enumerated subset) ---------------------------------


def test_change_lane_ci_config_plus_one_plugin_test_file_is_small(tmp_path: Path) -> None:
    """`.github/workflows/x.yml` starts with `.`, so it must not count as a
    second "plugin directory" alongside `loom-code/`."""
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(
        repo,
        {
            ".github/workflows/x.yml": "name: x\non: push\n",
            "loom-code/scripts/test_dotdir_probe.py": "def test_x():\n    assert True\n",
        },
        "ci: dot-dir plugin probe",
    )
    assert loom_checker.change_lane(repo, sha) == "small"


def test_change_lane_spec_md_alone_is_small(tmp_path: Path) -> None:
    """`docs/loom/<change-id>/spec.md` is a change-folder record, same as
    plan.md/review.json/evidence -- the exclusion must not enumerate a
    subset of record file names."""
    repo = _lane_init_repo(tmp_path)
    sha = _lane_commit(
        repo, {"docs/loom/demo/spec.md": "intent: demo@aaaaaaa\n"}, "docs: spec-only probe"
    )
    assert loom_checker.change_lane(repo, sha) == "small"
