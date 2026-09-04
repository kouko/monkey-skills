"""Graduated adversarial probes for `push.review-only-head` (close-commit
shape, REQ-1) and `push.dispatch-covers-tasks` (content-bound plumbing
exemption, REQ-3) that are NOT already covered by an existing test in
`test_loom_checker_push.py` -- see docs/loom/2026-09-03-loom-post-merge-seams
/evidence/probes/test_abuse_close_commit_shape.py and
test_abuse_plumbing_exemption.py for the full 21-case probe set and W1-04's
commit body for the graduated/overlap disposition of each case.

Reuses the sibling suite's fixtures and helpers rather than re-deriving
them (same rule test_abuse_close_commit_shape.py and
test_abuse_plumbing_exemption.py themselves state).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import codex_scaffold  # noqa: E402  (local import: needs SCRIPTS_DIR on sys.path)
import loom_checker  # noqa: E402  (W0-04: check_probes_adversarial dedup unit tests)
from test_loom_checker_push import (  # noqa: E402
    CHANGE,
    REVIEW,
    blocked_rules,
    build_repo,
    git,
    recommit_review,
    review_body,
    run_checker,
    write_review,
    _checkpoint_after,
    _seed_intent,
)


# ============================================================================
# push.review-only-head (close-commit shape, REQ-1)
# ============================================================================


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


def test_close_commit_crlf_line_ending_on_status_line_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_close_commit_crlf_line_ending_on_status_line_is_blocked
    Attack: the added status line ends `\\r\\n` instead of `\\n` (a stray
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
    Expected: BLOCK push.review-only-head."""
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


def test_close_commit_merge_whose_second_parent_carries_the_transition_passes(tmp_path: Path) -> None:
    """graduated | probe: test_close_commit_merge_whose_second_parent_carries_the_transition_passes
    Attack: HEAD^ is a clean (non-conflicting) merge; the first parent
    never touches the intent file at all, only the second parent (`topic`)
    closes it, and nothing else changes. The recompute reads HEAD^'s diff
    against ITS first parent (`git diff --raw --no-renames HEAD^^ HEAD^`),
    which is a plain two-tree diff -- it shows the intent file changed
    regardless of which parent contributed the change, so a clean merge
    carrying the transition through its second parent is indistinguishable
    from an ordinary close commit, PROVIDED the merge's first parent is
    itself a valid checkpoint and no other file differs.
    Expected: PASS."""
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


def test_close_commit_with_checkpoint_parent_carrying_garbage_reviewed_sha_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_close_commit_with_checkpoint_parent_carrying_garbage_reviewed_sha_is_blocked
    Attack: HEAD^^ has the right SHAPE of a checkpoint (touches only
    review.json) but its `reviewed_sha` is neither empty nor a real commit
    -- a stale, hand-edited, or corrupted value that does not resolve to
    HEAD^^^. Spec: "its parent HEAD^^ must itself be a checkpoint ... whose
    review.json records a reviewed_sha resolving to HEAD^^^".
    Expected: BLOCKED on push.review-only-head."""
    repo = build_repo(tmp_path)
    intent_rel = _seed_intent(repo)
    recommit_review(repo, review_body("not-a-real-sha-nonsense"))
    close_sha = _close_commit_here(repo, intent_rel)
    _checkpoint_after(repo, close_sha)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)
    assert "reviewed_sha must resolve to HEAD" in result.stderr


def test_close_commit_head_pre_caret_with_two_status_lines_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_close_commit_head_pre_caret_with_two_status_lines_is_blocked
    Attack: HEAD^^ (the file BEFORE the close) already has TWO raw
    `status:` lines -- the real frontmatter one plus a body decoy carrying
    the identical text. The close commit changes the frontmatter line to
    `closed ...` AND deletes the body decoy in the same edit, so HEAD^'s
    file ends up with exactly ONE raw `status:` line -- condition (b)'s
    HEAD^-side count guard is satisfied. Condition (c) does its OWN
    independent raw-line count on HEAD^^'s file before it will regenerate
    anything, and two lines there means there is no single line to
    regenerate from.
    Expected: BLOCKED on push.review-only-head, named "exactly one
    `status:` line in HEAD^^'s file to regenerate from"."""
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


def test_close_commit_status_key_not_first_in_frontmatter_passes(tmp_path: Path) -> None:
    """graduated | probe: test_close_commit_status_key_not_first_in_frontmatter_passes
    Attack: HEAD^^'s intent file has other frontmatter keys (`owner:`,
    `kind:`) sitting BEFORE `status:` -- checks whether the
    regenerate-and-compare recompute silently assumes `status:` is the
    first line. `_status_line_positions` scans the WHOLE file for lines
    starting with the literal bytes `status:`, unconditioned on position,
    so an ordinary, well-formed close should be unaffected by where in
    the frontmatter the key sits.
    Expected: PASS (frontmatter key order is not part of the close-commit
    shape)."""
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


# ============================================================================
# push.dispatch-covers-tasks (content-bound plumbing exemption, REQ-3)
# ============================================================================

RULE = "push.dispatch-covers-tasks"


def _plumbing_commit(repo: Path, *, trailer: bool, mutate=None,
                      msg: str = "chore(loom): scaffold hooks") -> str:
    """Undo the review-only HEAD `build_repo` left behind, scaffold a
    genuine `.codex/hooks/` copy from THIS repo's tree, optionally mutate
    it, commit (with or without a `Task:` trailer), rebuild review.json so
    `reviewed_sha` names the new commit, and re-commit the review-only
    HEAD on top. Returns the new commit's sha (HEAD^ after this call)."""
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    if mutate is not None:
        mutate(repo)
    full_msg = msg + ("\n\nTask: T1" if trailer else "")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", full_msg)
    new_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(new_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return new_sha


def test_an_altered_checker_copy_byte_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_an_altered_checker_copy_byte_is_blocked
    Attack: a genuine scaffold refresh whose committed checker copy then
    has one byte appended -- the plain blob-mismatch case, independent of
    the stamp/mode/symlink-specific gates the sibling suite already covers.
    Expected: BLOCK (blob mismatch against the canonical)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom_checker.py"
        path.write_text(path.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


def test_an_extra_contract_file_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_an_extra_contract_file_is_blocked
    Attack: an extra file under `.codex/hooks/contract/` with no canonical
    counterpart.
    Expected: BLOCK (a plumbing path with no canonical counterpart fails
    the comparison)."""
    def mutate(repo: Path) -> None:
        extra = repo / ".codex" / "hooks" / "contract" / "extra.yaml"
        extra.write_text("bogus: true\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


def test_a_deleted_sibling_module_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_a_deleted_sibling_module_is_blocked
    Attack: `git_exec.py` deleted and never restored (unlike the sibling
    suite's restore-then-refresh case, which passes).
    Expected: BLOCK (a deleted entry has no blob at the commit and fails
    the comparison like any other mismatch)."""
    def mutate(repo: Path) -> None:
        (repo / ".codex" / "hooks" / "git_exec.py").unlink()

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


def test_an_altered_shim_command_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_an_altered_shim_command_is_blocked
    Attack: `.codex/hooks/loom-checker`'s exec line gains an extra flag.
    Expected: BLOCK (`.codex/hooks/loom-checker` must equal the rendered
    SHIM_TEMPLATE for that version, byte for byte)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom-checker"
        text = path.read_text(encoding="utf-8")
        altered = text.replace(
            "exec python3 {checker} push --hook".format(checker=codex_scaffold.CHECKER_COPY),
            "exec python3 {checker} push --hook --extra-flag".format(
                checker=codex_scaffold.CHECKER_COPY
            ),
            1,
        )
        assert altered != text, "the exec line must actually be present to mutate"
        path.write_text(altered, encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


def test_running_the_copy_itself_is_never_exempt(tmp_path: Path) -> None:
    """graduated | probe: test_running_the_copy_itself_is_never_exempt
    Attack: run the checker AS the `.codex/hooks/` copy, not the
    canonical -- when the checker doing the push IS the copy there is no
    external canonical to compare against and no exemption applies.
    Expected: BLOCK. Also verifies the copy actually runs standalone (it
    imports git_exec.py and reads contract/manifest.yaml, both of which
    the scaffold ships beside it)."""
    import subprocess

    def _run_from_copy(repo: Path):
        copy = repo / ".codex" / "hooks" / "loom_checker.py"
        return subprocess.run(
            [sys.executable, str(copy), "push"],
            capture_output=True, text=True, cwd=str(repo),
        )

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False)
    result = _run_from_copy(repo)
    assert result.returncode in (1, 2), (
        f"the copy did not even run as a checker: {result.stderr or result.stdout}"
    )
    assert RULE in blocked_rules(result), (
        "the copy exempted its own trailer duty with no canonical to check "
        f"against: {result.stderr}"
    )


def test_an_unlisted_plumbing_path_is_never_exempt(tmp_path: Path) -> None:
    """graduated | probe: test_an_unlisted_plumbing_path_is_never_exempt
    Attack: `.codex/hooks/other-hook.sh` is not in HOST_PLUMBING_FILES and
    not under HOST_PLUMBING_DIR_PREFIX (`.codex/hooks/contract/`) -- it is
    gate work like any other hook script an adopting repo keeps in that
    directory.
    Expected: BLOCK."""
    def mutate(repo: Path) -> None:
        other = repo / ".codex" / "hooks" / "other-hook.sh"
        other.write_text("#!/usr/bin/env bash\necho hi\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


def test_a_forced_hook_fired_marker_commit_is_blocked(tmp_path: Path) -> None:
    """graduated | probe: test_a_forced_hook_fired_marker_commit_is_blocked
    Attack: `.loom-hook-fired` is explicitly ignored by the exemption and
    gitignored by the scaffold itself, so it never appears in a genuine
    refresh's diff -- forcing it into the commit anyway (`git add -f`)
    makes this a hostile input, not a genuine refresh, and must not, by
    itself, buy an exemption it would not otherwise earn.
    Expected: BLOCK."""
    def mutate(repo: Path) -> None:
        marker = repo / ".codex" / "hooks" / ".loom-hook-fired"
        marker.write_text("forced\n", encoding="utf-8")
        git(repo, "add", "-f", str(marker))

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# ============================================================================
# push.probes-adversarial (per-artifact dedup, W0-04)
# ============================================================================


def _dedup_repo(tmp_path: Path, counter: Path, *, rel: str = "probe.py",
                exit_code: int = 0) -> Path:
    """A minimal branch (not `build_repo` -- that fixture wires three
    distinct abuse files, and this rule's dedup is about many records over
    ONE artifact) whose committed artifact appends a line to `counter`
    (kept outside the repo, like the sibling probe file's fixture) every
    time it actually runs."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    path = repo / rel
    path.write_text(
        "import pathlib\n"
        f"pathlib.Path({str(counter)!r}).open('a').write('1\\n')\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", "feat: probe")
    return repo


def _dedup_records(artifact: str, sha: str, count: int) -> list[dict]:
    return [
        {"kind": "adversarial", "command": f"python3 {artifact}", "sha": sha,
         "result": "pass", "artifact": artifact}
        for _ in range(count)
    ]


def test_five_records_over_one_artifact_execute_it_exactly_once(tmp_path: Path) -> None:
    """RED until W0-04: `check_probes_adversarial` used to run the recorded
    command once per record; five records naming the same artifact used to
    mean five real subprocess invocations. After W0-04 it runs once per
    distinct artifact and applies that verdict to every record naming it."""
    counter = tmp_path / "counter.txt"
    repo = _dedup_repo(tmp_path, counter)
    sha = git(repo, "rev-parse", "HEAD")

    review = {"probes": _dedup_records("probe.py", sha, 5)}
    failures = loom_checker.check_probes_adversarial(repo, review, sha)

    assert failures == []
    assert counter.read_text(encoding="utf-8").count("1") == 1


def test_dotslash_and_bare_spellings_of_one_artifact_dedup_together(tmp_path: Path) -> None:
    """finding wave-end:0-02: `command_names_artifact()` itself treats
    `./probe.py` and `probe.py` as the same file, but the dedup dict used
    to key on the raw un-normalized artifact string -- two records for the
    identical physical file, one spelled each way, landed in two different
    groups and ran it twice. Keying on the normalized path collapses them
    into one execution."""
    counter = tmp_path / "counter.txt"
    repo = _dedup_repo(tmp_path, counter)
    sha = git(repo, "rev-parse", "HEAD")

    review = {
        "probes": _dedup_records("probe.py", sha, 2) + _dedup_records("./probe.py", sha, 1)
    }
    failures = loom_checker.check_probes_adversarial(repo, review, sha)

    assert failures == []
    assert counter.read_text(encoding="utf-8").count("1") == 1


def test_list_rules_states_the_dedup_counting_unit() -> None:
    """The `--list-rules` description for push.probes-adversarial names the
    counting unit (records) and says a file named by several records runs
    once -- so a cold reader of the rule table, not just of the source,
    learns the dedup semantics."""
    from io import StringIO

    out = StringIO()
    loom_checker.list_rules(out)
    text = out.getvalue()

    start = text.index("push.probes-adversarial")
    end = text.index("push.probes-package-tests", start)
    section = text[start:end]

    assert "records" in section
    assert "executed once" in section
