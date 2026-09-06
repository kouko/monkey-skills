"""Adversarial probes for W1-01 (plan.edits-after-commit reporting
NOT-APPLICABLE for a shipped change) -- `2026-09-06-graduated-probes-
survive-squash`.

The behaviour under attack does not exist yet: today `loom_checker.py
plan-edits <change-id>` always BLOCKs with `no plan commit found` when
the `docs(loom): plan <change-id>` commit is missing, regardless of
whether the change ever shipped. W1-01 is supposed to make that BLOCK
turn into a NOT-APPLICABLE (exit 0, naming the reason) exactly when the
change's own intent file reads a closed status -- and to keep BLOCKing
for every other shape, including a closed status the checker was
tricked into reading from the wrong place.

Every case here is built the same way as `loom-code/scripts/
test_plan_edits_after_commit.py`: a scratch git repo under `tmp_path`,
seeded with a `plan.md` and (for these cases) an `intent/<change-id>.md`
file, run through the real `loom_checker.py plan-edits <change-id>`
subprocess -- never a mock.

A case whose assertion fails today because the NOT-APPLICABLE path does
not exist yet is the expected RED for W1-01 to turn GREEN; that is noted
per test below rather than skipped or weakened.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parents[5] / "loom-code" / "scripts" / "loom_checker.py"
CHANGE_ID = "2099-04-04-shipped-plan-edits-probe"

# The literal em dash `_STATUS_CLOSED_ALT` uses in loom_checker.py -- copied
# verbatim so a hand-typed hyphen-minus never silently fails to match the
# real grammar.
EM_DASH = "—"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_plan_edits(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), "plan-edits", CHANGE_ID],
        capture_output=True, text=True, cwd=str(repo),
    )


def plan_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / CHANGE_ID / "plan.md"


def intent_path(repo: Path) -> Path:
    return repo / "docs" / "loom" / "intent" / f"{CHANGE_ID}.md"


def base_plan_text() -> str:
    return "\n".join([
        f"# Shipped plan-edits probe -- {CHANGE_ID}",
        f"intent: {CHANGE_ID}@0000000",
        "charter: 1.0",
        "",
        "## Current State Evidence",
        "- Forward: some/file.py:1 names the gap here.",
        "",
        "## Task DAG",
        "",
        "**W1 First task**  after: --",
        "- Files: x.py, y.py",
        "- Test: the base test passes",
        "- Risk: agent-decided -- low",
        "",
        "## Questions asked",
        "① — what -- one recorded question and its answer.",
        "",
        "## Risks",
        "1. agent-decided -- one bounded risk, one line.",
        "",
    ])


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "adv@example.com")
    git(repo, "config", "user.name", "Adversary")
    return repo


def write_intent(repo: Path, front_status_line: str, *, body_extra: str = "") -> None:
    """Writes `intent/<change-id>.md` with a real frontmatter `status:`
    line plus whatever extra prose the caller wants in the body -- never
    committed, since the checker reads the working-tree file directly
    (mirrors how `plan.md` itself is read, per `check_plan_edits_after_
    commit_at`)."""
    path = intent_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            f"# Shipped plan-edits probe -- {CHANGE_ID}",
            "originator: adversary",
            "kind: engineering",
            "needs-design: no -- probe fixture",
            front_status_line,
            "",
            "## Problem",
            body_extra,
            "",
        ]),
        encoding="utf-8",
    )


def seed_plan_without_commit(repo: Path, text: str) -> None:
    """Writes and commits `plan.md` under an ordinary commit message --
    never `docs(loom): plan <change-id>` -- so `find_plan_commit_sha`
    finds nothing, the shape every case in this file needs."""
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: seed plan without the sign-off commit")


def seed_plan_with_commit(repo: Path, text: str) -> None:
    path = plan_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"docs(loom): plan {CHANGE_ID}")


def edit_plan(repo: Path, text: str, message: str) -> None:
    plan_path(repo).write_text(text, encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", message)


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def combined_output(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


# --- 1. the positive case the feature exists for ----------------------------


def test_plan_edits_closed_intent_missing_commit_reports_not_applicable(tmp_path: Path) -> None:
    """A change whose intent is `status: closed ...` and whose plan commit
    is missing must exit 0 and NAME the outcome as not-applicable -- not a
    silent 0 that looks identical to 'nothing changed'.

    Expected RED for W1-01: today this BLOCKs at exit 1 with `no plan
    commit found`, because the checker never reads the intent file at
    all.
    """
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #999")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        "a shipped change's plan-edits question must not BLOCK: "
        f"stderr={result.stderr!r}"
    )
    assert (
        re.search(r"not.applicable", combined_output(result), re.I)
    ), (
        "the outcome must name itself not-applicable, distinguishing it "
        f"from an ordinary silent pass: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )


# --- 2. the guard the plan explicitly calls out -----------------------------


def test_plan_edits_confirmed_intent_missing_commit_still_blocks(tmp_path: Path) -> None:
    """An in-flight change (`status: confirmed ...`) whose plan commit is
    missing must still BLOCK -- a missing commit alone is never amnesty.

    This already holds today (the checker doesn't read the intent file at
    all yet, so it BLOCKs unconditionally); it must keep holding once
    W1-01 adds the closed-intent carve-out."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: confirmed 2026-09-01")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1
    assert "plan.edits-after-commit" in blocked_rules(result)
    assert "no plan commit found" in result.stderr


# --- 3. closed is not a blanket amnesty for a *present*, tampered commit ---


def test_plan_edits_closed_intent_present_commit_tampered_still_blocks(tmp_path: Path) -> None:
    """A closed intent must not become a blanket amnesty: when the plan
    commit IS present and a landed task's Files line is edited after the
    fact, that is still an illegal edit and must still BLOCK, exactly as
    it does for an in-flight change."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #999")
    seed_plan_with_commit(repo, base_plan_text())
    marker = repo / "landed-W1.txt"
    marker.write_text("ok\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: land W1\n\nTask: W1")
    tampered = base_plan_text().replace(
        "- Files: x.py, y.py", "- Files: x.py, y.py, z.py"
    )
    edit_plan(repo, tampered, "fix(loom): sneak an extra file past a closed intent")
    result = run_plan_edits(repo)
    assert result.returncode == 1, (
        "a closed intent must not blanket-authorise a tampered, already-"
        f"landed task: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "plan.edits-after-commit" in blocked_rules(result)


# --- 4. absent / unreadable intent is in-flight, per the plan's own Risk #2 -


def test_plan_edits_absent_intent_file_missing_commit_still_blocks(tmp_path: Path) -> None:
    """No intent file at all: the plan's own Risk #2 says an unreadable
    intent must be treated as in-flight and BLOCK, never silently pass as
    not-applicable. This already holds today (no intent is ever
    consulted); it is the regression guard for that Risk line."""
    repo = init_repo(tmp_path)
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1, (
        f"an absent intent must not silently pass: stdout={result.stdout!r}"
    )
    assert "plan.edits-after-commit" in blocked_rules(result)


def test_plan_edits_malformed_status_line_missing_commit_still_blocks(tmp_path: Path) -> None:
    """The intent file exists but its `status:` line does not match the
    grammar at all (garbage after `closed`, no real date) -- this must be
    treated as in-flight (BLOCK), never crash and never silently pass."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: closed banana -- not a real date or descriptor")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode in (0, 1), (
        f"malformed status must not crash the checker: {result.returncode}, "
        f"stderr={result.stderr!r}"
    )
    assert result.returncode == 1, (
        "a status line that fails to parse as closed must be treated as "
        f"in-flight and BLOCK: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "plan.edits-after-commit" in blocked_rules(result)


# --- 5. only the frontmatter status line counts, never prose that echoes it -


def test_plan_edits_closed_text_in_body_not_frontmatter_still_blocks(tmp_path: Path) -> None:
    """The real frontmatter `status:` line reads `confirmed`; the word
    'closed' with a real-looking date and PR number appears only inside
    the Problem paragraph, quoting an earlier report. The checker must
    read the frontmatter status line via the document parser (like
    `_status_closed_descriptor_from_text` already does elsewhere in this
    file) rather than grep the whole file for the word 'closed' -- so
    this must still BLOCK."""
    repo = init_repo(tmp_path)
    write_intent(
        repo,
        "status: confirmed 2026-09-01",
        body_extra=(
            f"上一版寫著 `status: closed 2020-01-01 {EM_DASH} PR #1` 但那是舊報告"
            "裡引用的一段文字，不是這份 intent 現在的狀態。"
        ),
    )
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 1, (
        "a 'closed' string inside body prose must never be read as the "
        f"frontmatter status: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "plan.edits-after-commit" in blocked_rules(result)


# --- 6. once closed, a later revert back to confirmed does not reopen it ---


def test_plan_edits_closed_then_reverted_status_reports_not_applicable(tmp_path: Path) -> None:
    """The intent was `status: closed ...` in an earlier commit, then a
    later commit reverted the frontmatter line back to `status: confirmed
    ...` (exactly the shape `check_intent_not_reopened` already defends
    against for the intake gate, loom_checker.py:1410). Expected
    behaviour, mirroring that existing terminal-close rule: the change
    stays shipped and plan-edits still reports NOT-APPLICABLE, recomputed
    from the intent file's own history rather than trusting whichever
    status line happens to be checked out right now -- a reverted status
    line must never resurrect a BLOCK-worthy in-flight change, and must
    never resurrect a live edit window on an already-shipped plan either.

    Expected RED for W1-01 either way: today the checker never reads the
    intent file, so this BLOCKs at exit 1. If the implementer instead
    reads only the current working-tree status line (not history), this
    case will assert NOT-APPLICABLE and fail loudly against a
    'confirmed'-reads-as-in-flight implementation -- surfacing the design
    gap explicitly rather than passing either way by accident."""
    repo = init_repo(tmp_path)
    write_intent(repo, f"status: closed 2026-09-01 {EM_DASH} PR #999")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): close intent")
    write_intent(repo, "status: confirmed 2026-09-01")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: revert status line back to confirmed")
    seed_plan_without_commit(repo, base_plan_text())
    result = run_plan_edits(repo)
    assert result.returncode == 0, (
        "a status line reverted back to 'confirmed' must not resurrect a "
        f"BLOCK on an already-shipped change: stderr={result.stderr!r}"
    )
    assert (
        re.search(r"not.applicable", combined_output(result), re.I)
    ), (
        f"must still name itself not-applicable: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )


# --- 7. not-applicable is not just "exit 0" -- it must be distinguishable --


def test_plan_edits_not_applicable_output_differs_from_silent_pass(tmp_path: Path) -> None:
    """A genuine pass (plan untouched since its own sign-off commit) is
    silent -- no stdout, no stderr, exit 0. A closed-intent
    not-applicable outcome is ALSO exit 0, but must not be silent in the
    same way, or a human (or a later machine check) cannot tell 'nothing
    is wrong' apart from 'the question no longer applies'."""
    repo = init_repo(tmp_path)
    write_intent(repo, "status: confirmed 2026-09-01")
    seed_plan_with_commit(repo, base_plan_text())
    silent_pass = run_plan_edits(repo)
    assert silent_pass.returncode == 0
    assert silent_pass.stdout == "" and silent_pass.stderr == "", (
        "an ordinary untouched-plan pass must stay silent: "
        f"stdout={silent_pass.stdout!r} stderr={silent_pass.stderr!r}"
    )

    repo2_root = tmp_path / "second"
    repo2_root.mkdir()
    repo2 = init_repo(repo2_root)
    write_intent(repo2, f"status: closed 2026-09-01 {EM_DASH} PR #999")
    seed_plan_without_commit(repo2, base_plan_text())
    not_applicable = run_plan_edits(repo2)
    assert not_applicable.returncode == 0
    assert combined_output(not_applicable) != "", (
        "a not-applicable outcome must not be silent -- it must say why, "
        "so it can never be mistaken for the ordinary silent pass above"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
