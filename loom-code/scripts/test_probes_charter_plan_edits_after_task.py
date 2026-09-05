"""Adversarial probes for W1-02 (plan edits after the plan commit) of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- written AFTER the
implementation (`check_plan_edits_after_commit` / `plan.edits-after-commit`
in loom-code/scripts/loom_checker.py) landed at da7c74fd, against the
up-front probes at ./test_abuse_plan_edits.py, which this file does not
duplicate.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_plan_edits_after_task.py -q -k <name>

This file is self-contained (its own tmp-repo helpers) so it survives on
its own even if the sibling probe file is edited or removed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
CHANGE_ID = "2099-01-02-probe-plan-edits-after-task"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def run_plan_edits(repo: Path, change_id: str = CHANGE_ID, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return run_checker("plan-edits", change_id, cwd=cwd if cwd is not None else repo)


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def _plan_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "plan.md"


def _init_repo(tmp_path: Path) -> Path:
    """A fresh tmp repo pinned to LF line endings regardless of the host's
    global git config -- otherwise a CRLF-hostile checkout can mask what
    test_working_tree_crlf_plan_causes_false_block is trying to isolate."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    git(repo, "config", "core.autocrlf", "false")
    return repo


def _base_plan_text(*, extra_task_block: str = "", task_ids: str = "W1-01, W1-02") -> str:
    lines = [
        f"# Probe plan -- {CHANGE_ID}",
        f"intent: {CHANGE_ID}@0000000",
        "charter: 1.0",
        "",
        "## Current State Evidence",
        "- Forward: some/path.py:1 names the current gap in one short bullet here.",
        "",
        "## Task DAG",
        "",
        "**W1-01 First task**  after: --",
        "- Files: a.py, b.py",
        "- Test: the W1-01 test passes",
        "- Risk: agent-decided -- low risk",
        "",
        "**W1-02 Second task**  after: W1-01",
        "- Files: c.py",
        "- Test: the W1-02 test passes",
        "- Risk: agent-decided -- low risk",
        "",
    ]
    if extra_task_block:
        lines.append(extra_task_block)
        lines.append("")
    lines += [
        "## Questions asked",
        "① — what — one recorded question and its answer here.",
        "",
        "## Risks",
        "1. agent-decided -- a single bounded plan-wide risk, one line.",
        "",
    ]
    return "\n".join(lines)


def _seed_plan_commit(repo: Path, text: str, *, subject: str | None = None) -> str:
    path = _plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    subject = subject if subject is not None else f"docs(loom): plan {CHANGE_ID}"
    git(repo, "commit", "-q", "-m", subject)
    return git(repo, "rev-parse", "HEAD")


def _commit_plan_edit(repo: Path, text: str, message: str) -> str:
    _plan_path(repo).write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def _land_task(repo: Path, task_id: str) -> str:
    marker = repo / f"landed-{task_id}.txt"
    marker.write_text("done\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"feat: land {task_id}\n\nTask: {task_id}")
    return git(repo, "rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# 1. `mentioned()` matches by raw substring, not exact id -- a sibling id
#    that contains the removed id as a prefix hides the removal.
# ---------------------------------------------------------------------------


def test_removed_task_id_substring_of_renamed_sibling_hides_removal_block(tmp_path: Path) -> None:
    """W1-1 (unlanded) is deleted from the plan in the same edit that adds
    W1-10; the commit message names only W1-10, never W1-1 on its own --
    but `mentioned()` checks `task_id in message`, and "W1-1" is a
    substring of "W1-10", so the removal of W1-1 is wrongly treated as
    justified and no BLOCK for W1-1 is raised."""
    repo = _init_repo(tmp_path)
    seed = _base_plan_text(
        extra_task_block=(
            "**W1-1 Renamable task**  after: --\n"
            "- Files: r.py\n"
            "- Test: the W1-1 test passes\n"
            "- Risk: agent-decided -- low risk"
        )
    )
    _seed_plan_commit(repo, seed)
    renamed = _base_plan_text(
        extra_task_block=(
            "**W1-10 Renamable task**  after: --\n"
            "- Files: r.py\n"
            "- Test: the W1-1 test passes\n"
            "- Risk: agent-decided -- low risk"
        )
    )
    _commit_plan_edit(repo, renamed, "chore(loom): rename W1-10 task block")
    result = run_plan_edits(repo)
    rules = blocked_rules(result)
    # An honest rule would BLOCK the disappearance of W1-1 (never landed,
    # never named on its own in the message). This probe records whether
    # it actually does.
    assert result.returncode != 0, (
        "vulnerability: W1-1's removal slipped through unblocked because "
        "'W1-1' is a substring of 'W1-10' in the commit message -- "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "plan.edits-after-commit" in rules


# ---------------------------------------------------------------------------
# 2. The memory-task exemption skips ANY new `W<n>-memory` id with no cap
#    on count and no check on position.
# ---------------------------------------------------------------------------


def test_two_new_memory_tasks_with_different_ids_both_bypass_mention_check(tmp_path: Path) -> None:
    """Two brand-new memory-shaped task ids (W1-memory, W2-memory) are
    both added in one edit with a commit message naming neither -- the
    exemption is per-id-shape, not per-plan, so nothing blocks a plan
    that grows more than one unmentioned memory task."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    memory_block = (
        "**W1-memory Memory step**  after: W1-01, W1-02\n"
        "- Files: docs/loom/memory/\n"
        "- Test: the memory entry exists\n"
        "- Risk: agent-decided -- none\n"
        "\n"
        "**W2-memory Second memory step**  after: W1-01, W1-02\n"
        "- Files: docs/loom/memory/\n"
        "- Test: the second memory entry exists\n"
        "- Risk: agent-decided -- none"
    )
    edited = _base_plan_text(extra_task_block=memory_block)
    _commit_plan_edit(repo, edited, "chore(loom): housekeeping, nothing to see here")
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        "expected both unmentioned memory-shaped ids to pass silently -- "
        f"stderr={result.stderr!r}"
    )


def test_memory_task_inserted_mid_wave_bypasses_position_check(tmp_path: Path) -> None:
    """A `W1-memory` block is inserted BETWEEN W1-01 and W1-02 in the Task
    DAG (not appended after the whole wave) with no mention in the commit
    message -- the exemption regex only checks the id's shape, never its
    position, so an out-of-order memory task passes exactly like a
    correctly-placed one."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    inserted = (
        "# Probe plan -- " + CHANGE_ID + "\n"
        f"intent: {CHANGE_ID}@0000000\n"
        "charter: 1.0\n"
        "\n"
        "## Current State Evidence\n"
        "- Forward: some/path.py:1 names the current gap in one short bullet here.\n"
        "\n"
        "## Task DAG\n"
        "\n"
        "**W1-01 First task**  after: --\n"
        "- Files: a.py, b.py\n"
        "- Test: the W1-01 test passes\n"
        "- Risk: agent-decided -- low risk\n"
        "\n"
        "**W1-memory Memory step**  after: W1-01\n"
        "- Files: docs/loom/memory/\n"
        "- Test: the memory entry exists\n"
        "- Risk: agent-decided -- none\n"
        "\n"
        "**W1-02 Second task**  after: W1-01\n"
        "- Files: c.py\n"
        "- Test: the W1-02 test passes\n"
        "- Risk: agent-decided -- low risk\n"
        "\n"
        "## Questions asked\n"
        "① — what — one recorded question and its answer here.\n"
        "\n"
        "## Risks\n"
        "1. agent-decided -- a single bounded plan-wide risk, one line.\n"
    )
    _commit_plan_edit(repo, inserted, "chore(loom): insert memory task early")
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        "expected the mid-wave memory task to pass silently despite being "
        f"out of position -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# 3. `_landed_task_ids` scans every commit reachable in the range,
#    including merge commits -- a trailer that lives only on the merge
#    commit's own message (no corresponding diff) still marks a task
#    landed.
# ---------------------------------------------------------------------------


def test_task_trailer_on_merge_commit_message_marks_task_landed(tmp_path: Path) -> None:
    """A `Task: W1-01` trailer sitting only on a merge commit's message
    (not on any commit that actually touches W1-01's files) is enough to
    flip W1-01 into 'landed', so a later plan edit to it is blocked as
    'changed after landing' rather than as an ordinary unmentioned edit."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    git(repo, "checkout", "-q", "-b", "side")
    (repo / "side-file.txt").write_text("side\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: unrelated side work")
    git(repo, "checkout", "-q", "main")
    git(
        repo, "merge", "--no-ff", "-q", "side",
        "-m", "merge: bring in side work\n\nTask: W1-01",
    )
    edited = _base_plan_text().replace(
        "the W1-01 test passes", "the W1-01 test passes with extra assertions"
    )
    _commit_plan_edit(repo, edited, "chore(loom): tighten W1-01's test wording")
    result = run_plan_edits(repo)
    rules = blocked_rules(result)
    assert result.returncode != 0
    assert "plan.edits-after-commit" in rules
    assert "git history" in result.stderr, (
        "expected the merge-commit-only trailer to have promoted W1-01 to "
        f"'landed' -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# 4. Boundary: HEAD is the plan commit itself (empty delta).
# ---------------------------------------------------------------------------


def test_head_at_plan_commit_itself_reports_no_edits(tmp_path: Path) -> None:
    """When HEAD IS the plan commit (no edits have happened yet at all),
    the rule must report a clean pass, not a false block from comparing
    the plan commit against itself."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# 5. Hostile input: CRLF line endings on the working-tree plan file that
#    the committed blob does not have.
# ---------------------------------------------------------------------------


def test_working_tree_crlf_plan_does_not_cause_false_block(tmp_path: Path) -> None:
    """The plan commit stores LF line endings; the current working tree
    is then rewritten byte-for-byte identical except every line ending is
    CRLF (as a checkout under a CRLF-hostile git config might produce).
    No content changed, only the encoding of the newline. This attack
    FAILS: `read_text` reads via `Path.read_text` with the default
    universal-newlines translation, so CRLF on disk becomes LF in memory
    before any comparison runs -- the section-level text compares equal
    and no false BLOCK fires. Recorded as a survived attack, not a
    silent assumption."""
    repo = _init_repo(tmp_path)
    text = _base_plan_text()
    _seed_plan_commit(repo, text)
    crlf_text = text.replace("\n", "\r\n")
    _plan_path(repo).write_bytes(crlf_text.encode("utf-8"))
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        f"a pure CRLF rewrite should not trip a false BLOCK -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# 6. Hostile input: nested parentheses inside an otherwise-allowed
#    `blocked(...)` mark break the naive `[^)]*` strip regex.
# ---------------------------------------------------------------------------


def test_nested_parens_in_blocked_mark_on_landed_task_causes_false_block(tmp_path: Path) -> None:
    """`blocked(...)` is charter-allowed even on a LANDED task, but
    MARK_STRIP's `[^)]*` body stops at the FIRST `)` it sees. W1-01 is
    landed, then given a `blocked(<reason with its own parenthetical>)`
    mark and nothing else -- an ordinary piece of English prose, not an
    attempt to break anything semantically. Because the task is landed,
    `_check_task_dag` blocks on `title_changed` alone with no rescue from
    `mentioned()`, so the stray un-stripped `)` left by the naive regex
    is enough to turn a charter-legal mark into a false 'changed after
    landing' BLOCK."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    _land_task(repo, "W1-01")
    edited = _base_plan_text().replace(
        "**W1-01 First task**  after: --",
        "**W1-01 First task** blocked(waiting on upstream (see #42))  after: --",
    )
    _commit_plan_edit(repo, edited, "chore(loom): block W1-01 pending upstream")
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        "vulnerability: a charter-legal blocked(...) mark with its own "
        "parenthetical was misparsed by MARK_STRIP's [^)]* into a false "
        f"title-change BLOCK on a landed task -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# 7. Boundary: the plan-commit subject has trailing whitespace.
# ---------------------------------------------------------------------------


def test_plan_commit_subject_trailing_whitespace_still_finds_plan_commit(tmp_path: Path) -> None:
    """`git commit -m "docs(loom): plan <id> "` (one trailing space) is
    attempted, aiming to make `find_plan_commit_sha`'s exact-string match
    against `%s` miss its own baseline forever. This attack FAILS: git's
    own `--format=%s` pretty-printer strips the commit message's trailing
    whitespace before `find_plan_commit_sha` ever sees it, so the exact
    match still succeeds and an untouched plan still passes cleanly."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(
        repo, _base_plan_text(), subject=f"docs(loom): plan {CHANGE_ID} "
    )
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        f"expected the trailing-whitespace subject to still be found -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# 8. The rule is invoked with cwd inside a subdirectory of the repo.
# ---------------------------------------------------------------------------


def test_rule_runs_correctly_from_nested_cwd(tmp_path: Path) -> None:
    """`plan-edits` is run with cwd set two levels below the repo root
    (mirroring an agent that `cd`s into docs/loom/<change-id>/ first) --
    `repo_root` must still resolve the real top and the rule must behave
    identically to running from the repo root."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _base_plan_text())
    nested_cwd = _plan_path(repo).parent
    result = run_plan_edits(repo, cwd=nested_cwd)
    assert result.returncode == 0, (
        f"expected a clean pass from a nested cwd -- stderr={result.stderr!r}"
    )


# ---------------------------------------------------------------------------
# Synthetic self-tests for the substring-mention assertion strings above --
# one affirmative match, one rejected non-match.
# ---------------------------------------------------------------------------


def test_blocked_rules_helper_parses_block_line_affirmatively() -> None:
    """`blocked_rules` must recognize a genuine `BLOCK <rule-id>: ...`
    stderr line and extract exactly the rule id before the colon."""
    fake = subprocess.CompletedProcess(
        args=[], returncode=1, stdout="",
        stderr="BLOCK plan.edits-after-commit: W1-1 removed; goes to spec\n",
    )
    assert blocked_rules(fake) == {"plan.edits-after-commit"}


def test_blocked_rules_helper_rejects_non_block_line() -> None:
    """A stderr line that does NOT start with `BLOCK ` (e.g. an ordinary
    informational line) must not be mistaken for a blocked-rule report."""
    fake = subprocess.CompletedProcess(
        args=[], returncode=0, stdout="",
        stderr="not a block line, no rule here\n",
    )
    assert blocked_rules(fake) == set()
