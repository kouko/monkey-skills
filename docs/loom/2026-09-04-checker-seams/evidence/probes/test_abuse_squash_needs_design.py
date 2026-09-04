"""Adversarial probes against W0-03 (squash-merge drops the needs-design
line), written BEFORE W0-03 exists, per plan task W0-01.

Target (does not exist yet at W0-01 time): `check_needs_design_reason()` in
`loom-code/scripts/loom_checker.py` treating a decided-on-main commit whose
subject is GitHub-squash-shaped (single parent, subject ending ` (#<n>)`,
and that commit IS on `main`'s history) as already having satisfied the
line on the branch that produced it, instead of demanding the line appear
verbatim in the squash commit's own message.

Live-verified findings that correct the plan's Current State Evidence:

* The SQUASH case (single-parent commit produced by `git merge --squash` +
  a hand-written commit message ending ` (#12)`, no `needs-design:` line in
  that message) IS blocked today -- `deciding_commit()` finds the squash
  commit itself (it is the newest commit that changed the frontmatter
  lines), and its message lacks the line. Verified live: `BLOCK
  intent.needs-design-reason: the commit message (commit <sha>, which last
  changed status/needs-design) does not carry the line ...`, exit 1. This
  case is `xfail(strict=True)`.

* The REAL MERGE case (`git merge --no-ff`, two parents) is **NOT** RED
  today, contrary to the plan's Current State Evidence line 6 ("這條 W0-03
  的 squash 判定... 真正的 merge commit 兩個 parent 也一樣紅"). `git show`
  on a merge commit prints an empty diff by default (no `-m`/`-c` flag), so
  `_decides_in_frontmatter()` returns False for the merge commit and
  `deciding_commit()` falls through `git log` to the ORIGINAL branch commit
  that carries the line -- which still passes today's check. Verified live:
  `intent docs/loom/intent/<id>.md` on the post-merge main HEAD exits 0
  already. Recorded as a plain (non-xfail) case below so this does not
  silently regress once W0-03 lands, and reported as a plan-fact
  correction in the adversary report rather than folded into the RED set.

* A branch commit that FAKES the squash shape (subject hand-written to end
  ` (#1)`, single parent, no needs-design line) but is NOT reachable from
  `main` must still be blocked, both today (no exception logic exists at
  all) and after W0-03 (the fix's topology check --
  `merge-base --is-ancestor <sha> <trunk>` per the plan -- excludes it).

* A plain single-parent commit sitting ON main, with no `(#n)` suffix and
  no needs-design line, must also still be blocked both today and after --
  it is not squash-shaped by either signal.

* The ordinary branch case (the deciding commit's own message DOES carry
  the line) must keep passing both today and after -- the fix must not
  regress the happy path it usually replaces.

No mutation/fuzz tool is declared for this repo, so this file is the
required executable abuse/boundary cases (5 here, floor is 3). Every
fixture is a real git repo with a real `main` + feature branch, run through
the real `loom_checker.py intent` subcommand via subprocess -- topology
(parent count, ancestry, subject shape) is exactly what is under attack, so
a mocked repo would test nothing.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"

# kind: product + needs-design: yes keeps this file scoped to W0-03 alone --
# kind: engineering (or needs-design: no) would also invoke
# touched_interface_surfaces() -> branch_base(), which raises when HEAD sits
# on main itself (W0-02's territory, not this file's).
INTENT_TEXT = """# {title}
originator: kouko
kind: product
needs-design: yes — {reason}
status: confirmed {date}

## Problem
people cannot see something they need to see.

## Proposed outcome
show it to them plainly.

## Acceptance
1. it works.

## Constraints
- none

## Out of scope
- none

## Open questions
- none
"""


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


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def _intent_relpath(change_id: str) -> str:
    return f"docs/loom/intent/{change_id}.md"


def _write_intent_on_branch(
    repo: Path, change_id: str, *, reason: str, commit_message: str
) -> None:
    """Feature-branch commit that writes the intent AND carries the
    needs-design line verbatim in its own commit message."""
    path = repo / _intent_relpath(change_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        INTENT_TEXT.format(title=change_id, reason=reason, date=change_id[:10]),
        encoding="utf-8",
    )
    git(repo, "add", _intent_relpath(change_id))
    git(repo, "commit", "-q", "-m", commit_message)


# --- (1) squash-shaped commit on main: RED until W0-03 ---------------------


@pytest.mark.xfail(
    strict=True,
    reason=(
        "RED until W0-03: check_needs_design_reason() does not yet recognise a "
        "single-parent, subject-ending-`(#n)` commit on main as squash-shaped, "
        "so it demands the line verbatim in the squash commit's own message. "
        "Observed today: BLOCK intent.needs-design-reason "
        "(\"the commit message (commit <sha>, which last changed "
        "status/needs-design) does not carry the line ...\"), exit 1."
    ),
)
def test_squash_shaped_commit_on_main_passes_after_fix(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    change_id = "2099-03-01-squash"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=(
            f"docs(loom): intent {change_id} confirmed\n\n"
            "needs-design: yes — new page for the team to see something"
        ),
    )
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "--squash", "feature", "-q")
    # GitHub-squash shape: single parent (a plain `git commit`, not the
    # merge machinery), subject ending in ` (#<n>)`, message body dropped --
    # exactly what GitHub's "Squash and merge" button produces.
    git(repo, "commit", "-q", "-m", f"docs(loom): intent {change_id} confirmed (#12)")
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 1  # single parent
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (2) real merge commit: already passes TODAY, must keep passing --------


def test_real_merge_commit_on_main_already_passes_today(tmp_path: Path) -> None:
    """Plan-fact correction: this is NOT a RED-until-W0-03 case. `git show`
    on a 2-parent commit prints no diff by default, so `deciding_commit()`
    skips it and finds the original feature-branch commit (which DOES carry
    the line) instead. Kept as a floor case so W0-03 cannot regress it."""
    repo = _init_repo(tmp_path)
    change_id = "2099-03-02-merge"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=(
            f"docs(loom): intent {change_id} confirmed\n\n"
            "needs-design: yes — new page for the team to see something"
        ),
    )
    git(repo, "checkout", "-q", "main")
    git(
        repo,
        "merge",
        "--no-ff",
        "feature",
        "-q",
        "-m",
        "Merge pull request #12 from x/feature",
    )
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 2  # two parents
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 0, result.stderr


# --- (3) fake squash shape on a branch NOT reachable from main -------------


def test_fake_squash_subject_off_main_still_blocked(tmp_path: Path) -> None:
    """A branch commit whose author hand-writes a `(#1)`-suffixed subject
    (mimicking the squash shape) but that commit is not on `main`'s history
    at all -- the topology check must not be fooled by subject text alone."""
    repo = _init_repo(tmp_path)
    change_id = "2099-03-03-fake-squash"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=f"docs(loom): intent {change_id} confirmed (#1)",
    )
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 1  # single parent
    is_ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", "HEAD", "main"]
    ).returncode
    assert is_ancestor != 0  # NOT reachable from main -- the attack's whole point
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-reason" in blocked_rules(result)


# --- (4) plain non-squash commit on main ------------------------------------


def test_plain_non_squash_commit_on_main_still_blocked(tmp_path: Path) -> None:
    """Single parent, no `(#n)` suffix, no needs-design line: not
    squash-shaped by either signal, so no exception should ever apply."""
    repo = _init_repo(tmp_path)
    change_id = "2099-03-04-plain-main"
    path = repo / _intent_relpath(change_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        INTENT_TEXT.format(
            title=change_id, reason="new page for the team to see something",
            date=change_id[:10],
        ),
        encoding="utf-8",
    )
    git(repo, "add", _intent_relpath(change_id))
    git(repo, "commit", "-q", "-m", f"docs(loom): intent {change_id} confirmed")
    assert len(git(repo, "log", "-1", "--pretty=%P").split()) == 1
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 1
    assert "intent.needs-design-reason" in blocked_rules(result)


# --- (5) branch commit that DOES carry the line: floor, both today+after ---


def test_branch_commit_carrying_the_line_passes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    change_id = "2099-03-05-happy-path"
    git(repo, "checkout", "-q", "-b", "feature")
    _write_intent_on_branch(
        repo,
        change_id,
        reason="new page for the team to see something",
        commit_message=(
            f"docs(loom): intent {change_id} confirmed\n\n"
            "needs-design: yes — new page for the team to see something"
        ),
    )
    result = run_checker("intent", _intent_relpath(change_id), cwd=repo)
    assert result.returncode == 0, result.stderr
