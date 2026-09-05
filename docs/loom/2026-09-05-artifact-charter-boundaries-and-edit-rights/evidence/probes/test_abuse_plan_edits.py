"""Adversarial probes for W1-02 (plan edits after the plan commit) of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- written BEFORE the
implementer, against `loom_checker.py plan-edits <change-id>` and the new
`plan.edits-after-commit` rule described in the plan's W1-02 task line.

None of this exists yet at the commit these probes were written against:
there is no `plan-edits` sub-command and no `plan.edits-after-commit` rule
in `RULES`. Every test below is expected to FAIL or ERROR today (unknown
sub-command, `--list-rules` missing the new id, wrong exit codes). That is
the implementer's RED: turning every one of these green, without weakening
any assertion here, is the acceptance bar for W1-02.

Each test is independently re-runnable from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_plan_edits.py -q -k <name>

Interface pins (the W1-02 task line and dispatch prompt left these to the
adversary to nail down first; each is a `findings` entry in the report,
not a silent guess):
  - the sub-command is `plan-edits <change-id>`, run with cwd at the repo
    root (mirrors every other git-aware sub-command in this file's sibling
    `test_loom_checker_push.py`);
  - the plan commit is found by exact subject match
    `docs(loom): plan <change-id>` on the first-reached such commit walking
    from HEAD (oldest-first among candidates, i.e. `git log --reverse`'s
    first hit) -- two commits sharing that subject pin the earlier one;
  - a landed task is one whose id appears in a `Task: <id>` trailer on any
    commit in `<plan-commit>..HEAD`; matching is exact-id, not substring;
  - the Risks-section BLOCK line names `review` as the goes_to (the
    interface note says this explicitly: "goes_to `review` from the
    charter's must_not");
  - missing plan.md file is exit 2; no plan commit found is exit 1 with
    `no plan commit found` in stderr; no `charter:` frontmatter key is a
    silent exit 0 skip regardless of what else changed.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args], capture_output=True, text=True, cwd=str(cwd)
    )


def run_plan_edits(repo: Path, change_id: str) -> subprocess.CompletedProcess:
    return run_checker("plan-edits", change_id, cwd=repo)


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


CHANGE_ID = "2099-01-01-probe-plan-edits"


def _plan_text(
    *,
    charter: str | None = "charter: 1.0",
    w101_files: str = "a.py, b.py",
    w101_test: str = "the W1-01 test passes",
    w101_mark: str = "",
    w102_test: str = "the W1-02 test passes",
    w102_mark: str = "",
    extra_task_block: str = "",
    cse_bullet: str = "Forward: some/path.py:1 names the current gap in one short bullet here.",
    extra_cse_bullet: str = "",
    risks_item: str = "1. agent-decided -- a single bounded plan-wide risk, one line.",
    extra_risks_item: str = "",
    questions_line: str = "① — what — one recorded question and its answer here.",
    extra_questions_line: str = "",
    extra_section: str = "",
) -> str:
    lines = [
        f"# Probe plan -- {CHANGE_ID}",
        f"intent: {CHANGE_ID}@0000000",
    ]
    if charter is not None:
        lines.append(charter)
    lines.append("")
    lines.append("## Current State Evidence")
    lines.append(f"- {cse_bullet}")
    if extra_cse_bullet:
        lines.append(f"- {extra_cse_bullet}")
    lines.append("")
    lines.append("## Task DAG")
    lines.append("")
    lines.append(f"**W1-01 First task**{w101_mark}  after: --")
    lines.append(f"- Files: {w101_files}")
    lines.append(f"- Test: {w101_test}")
    lines.append("- Risk: agent-decided -- low risk")
    lines.append("")
    lines.append(f"**W1-02 Second task**{w102_mark}  after: W1-01")
    lines.append("- Files: c.py")
    lines.append(f"- Test: {w102_test}")
    lines.append("- Risk: agent-decided -- low risk")
    lines.append("")
    if extra_task_block:
        lines.append(extra_task_block)
        lines.append("")
    lines.append("## Questions asked")
    lines.append(questions_line)
    if extra_questions_line:
        lines.append(extra_questions_line)
    lines.append("")
    lines.append("## Risks")
    lines.append(risks_item)
    if extra_risks_item:
        lines.append(extra_risks_item)
    if extra_section:
        lines.append("")
        lines.append(extra_section)
    lines.append("")
    return "\n".join(lines)


def _plan_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "plan.md"


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    return repo


def _seed_plan_commit(repo: Path, text: str, *, subject: str | None = None) -> str:
    """Writes plan.md and commits it with the exact plan-commit subject the
    rule looks for (unless overridden), returning the new commit sha."""
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
    """A no-op code commit carrying a `Task: <id>` trailer -- this is what
    makes a task 'landed' for the rule."""
    marker = repo / f"landed-{task_id}.txt"
    marker.write_text("done\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"feat: land {task_id}\n\nTask: {task_id}")
    return git(repo, "rev-parse", "HEAD")


# ---------------------------------------------------------------------------
# Allowed edits -- must all pass (exit 0).
# ---------------------------------------------------------------------------


def test_plan_edits_unchanged_since_commit_passes(tmp_path: Path) -> None:
    """An untouched plan.md since its own plan commit must never block."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_claimed_mark_on_task_passes(tmp_path: Path) -> None:
    """A `claimed(@branch)` mark appended to a task's title line is an
    explicitly allowed edit even though the task is landed."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    _land_task(repo, "W1-01")
    edited = _plan_text(w101_mark=" claimed(@work)")
    _commit_plan_edit(repo, edited, "chore(loom): claim W1-01")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_blocked_mark_on_task_passes(tmp_path: Path) -> None:
    """A `blocked(<reason>)` mark on a task title line is allowed."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(w102_mark=" blocked(waiting on upstream)")
    _commit_plan_edit(repo, edited, "chore(loom): block W1-02")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_appended_memory_task_passes(tmp_path: Path) -> None:
    """A whole new `**W<n>-memory ...**` task block appended to the last
    wave is an explicitly allowed edit."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    memory_block = (
        "**W1-memory Memory step**  after: W1-01, W1-02\n"
        "- Files: docs/loom/memory/\n"
        "- Test: the memory entry exists\n"
        "- Risk: agent-decided -- none"
    )
    edited = _plan_text(extra_task_block=memory_block)
    _commit_plan_edit(repo, edited, "chore(loom): append memory task")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_unlanded_task_field_change_with_id_in_message_passes(tmp_path: Path) -> None:
    """An un-landed task's Test line may change when the reason is stated
    -- the task id appears in the commit message that changed it."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(w102_test="the corrected W1-02 test wording passes")
    _commit_plan_edit(
        repo, edited, "fix(loom): W1-02's original test line assumed the wrong fixture"
    )
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_questions_asked_append_passes(tmp_path: Path) -> None:
    """A newly appended `## Questions asked` line is allowed."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(
        extra_questions_line="② — what — a second question asked later, and its answer."
    )
    _commit_plan_edit(repo, edited, "chore(loom): record a later question")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


def test_plan_edits_no_charter_key_skips_even_with_risks_append(tmp_path: Path) -> None:
    """A plan with no `charter:` frontmatter key is skipped entirely --
    even a Risks-section append, which would otherwise block, passes."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text(charter=None))
    edited = _plan_text(
        charter=None,
        extra_risks_item="2. a brand-new plan-wide risk appended after sign-off.",
    )
    _commit_plan_edit(repo, edited, "chore(loom): add a risk, no charter stamp")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 0, result.stderr


# ---------------------------------------------------------------------------
# Disallowed edits -- must all block (exit 1, naming the rule).
# ---------------------------------------------------------------------------


def test_plan_edits_unlanded_task_field_change_without_id_in_message_blocks(tmp_path: Path) -> None:
    """The same Test-line edit as the passing case above, but the commit
    message never names the task id -- must block."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(w102_test="the corrected test wording passes")
    _commit_plan_edit(repo, edited, "chore: tidy up some wording")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_landed_task_files_change_blocks(tmp_path: Path) -> None:
    """A landed task's Files line changing at all is blocked, regardless of
    what the commit message says."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    _land_task(repo, "W1-01")
    edited = _plan_text(w101_files="a.py, b.py, c.py")
    _commit_plan_edit(
        repo, edited, "fix(loom): W1-01 needed one more file, explained right here"
    )
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_appended_risks_item_blocks_naming_review(tmp_path: Path) -> None:
    """A new `## Risks` item is blocked, and the BLOCK line names `review`
    as the goes_to artifact (charter must_not: build/review diary)."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(
        extra_risks_item="2. a brand-new plan-wide risk appended after sign-off."
    )
    _commit_plan_edit(repo, edited, "chore(loom): add a risk after sign-off")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)
    assert "review" in result.stderr


def test_plan_edits_current_state_evidence_change_blocks(tmp_path: Path) -> None:
    """A changed `## Current State Evidence` bullet is blocked."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(
        cse_bullet="Forward: some/path.py:1 now says something completely different."
    )
    _commit_plan_edit(repo, edited, "chore(loom): rewrite the CSE bullet")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_landed_sha_annotation_blocks(tmp_path: Path) -> None:
    """Adding a `landed: <sha>` annotation to a task line is blocked -- the
    interface names this explicitly as a disallowed edit shape."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    _land_task(repo, "W1-01")
    edited = _plan_text(w101_mark=" landed(deadbeefcafe)")
    _commit_plan_edit(repo, edited, "chore(loom): annotate W1-01 with its landed sha")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_frontmatter_charter_change_blocks(tmp_path: Path) -> None:
    """Changing the frontmatter `charter:` value itself is blocked."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(charter="charter: 1.1")
    _commit_plan_edit(repo, edited, "chore(loom): bump charter stamp")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_new_section_added_blocks(tmp_path: Path) -> None:
    """A brand-new `## ` section (e.g. `## Lessons`) is blocked."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text())
    edited = _plan_text(
        extra_section="## Lessons\n- a lesson that belongs in memory, not the plan."
    )
    _commit_plan_edit(repo, edited, "chore(loom): add a Lessons section")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_no_plan_commit_found_blocks(tmp_path: Path) -> None:
    """No commit with the exact plan-commit subject exists -- the rule
    blocks with `no plan commit found` rather than silently passing."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text(), subject="docs(loom): a differently worded commit")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "no plan commit found" in result.stderr


def test_plan_edits_two_plan_commits_same_subject_pins_the_first(tmp_path: Path) -> None:
    """Two commits share the exact plan-commit subject; the earlier one is
    the baseline. A landed-task Files change made between the two commits
    must still be caught -- if the rule wrongly pinned the LATER commit as
    baseline, this diff would vanish and the run would wrongly pass."""
    repo = _init_repo(tmp_path)
    _seed_plan_commit(repo, _plan_text(w101_files="a.py, b.py"))
    _seed_plan_commit(repo, _plan_text(w101_files="a.py, b.py, c.py"))
    _land_task(repo, "W1-01")
    result = run_plan_edits(repo, CHANGE_ID)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)


# ---------------------------------------------------------------------------
# Absent/hostile input and CLI surface.
# ---------------------------------------------------------------------------


def test_plan_edits_missing_plan_file_exits_2(tmp_path: Path) -> None:
    """A change-id with no plan.md at all exits 2 (usage/internal error),
    never 0 or 1 -- there is nothing to check."""
    repo = _init_repo(tmp_path)
    git(repo, "commit", "-q", "--allow-empty", "-m", "seed")
    result = run_plan_edits(repo, "no-such-change-id")
    assert result.returncode == 2


def test_list_rules_gains_plan_edits_after_commit_at_thirty(tmp_path: Path) -> None:
    """`--list-rules` must grow to exactly 30 rules and name the new one --
    the rule table is the SSOT this repo's CLAUDE.md points at; a silent
    count drift here is itself a regression. (Count bumped to 31 for
    W1-03's review.round-append-only, authorised by that task's own
    dispatch instructions.)"""
    result = run_checker("--list-rules", cwd=REPO)
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 31, f"expected 31 rules, got {len(lines)}"
    ids = {line.split("\t", 1)[0] for line in lines}
    assert "plan.edits-after-commit" in ids
