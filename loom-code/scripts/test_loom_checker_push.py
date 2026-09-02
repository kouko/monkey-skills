"""Executable contract for `loom_checker.py push` (plan W0-04).

Every fixture is a real git repo: the push rules are about the shape of
HEAD and of review.json against that HEAD, so a mocked repo would test
nothing. The two named risks in the plan get their own cases -- amending
the code commit under a written review.json, and a review-only commit
that quietly carries a second file.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")
CHANGE = "2026-09-02-a"
REVIEW = f"docs/loom/{CHANGE}/review.json"
DISPATCH = f"docs/loom/{CHANGE}/review.json.dispatch"


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


def review_body(reviewed_sha: str, **overrides) -> dict:
    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "wave 1 code delta",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "rev-a", "vendor": "anthropic", "model": "m", "lens": "code",
             "verdict": "PASS", "dimension_scores": {}, "findings": []},
            {"reviewer": "rev-b", "vendor": "anthropic", "model": "m", "lens": "code",
             "verdict": "PASS_WITH_NOTES", "dimension_scores": {}, "findings": []},
        ],
        "probes": [
            {"kind": "package-tests", "command": "pytest -q", "result": "pass",
             "artifact": "evidence/tests.txt"},
        ],
        "open_findings": [
            {"id": "F-1", "anchor": "a.py:1", "origin_sha": "deadbee",
             "raised_by": "rev-a", "resolved": "fixed in HEAD^"},
        ],
    }
    body.update(overrides)
    return body


DISPATCH_LINES = [
    {"task": "T1", "role": "implementer", "agent_id": "agent-imp", "model": "m",
     "started": "2026-09-02T09:00:00Z"},
    {"task": "T1", "role": "reviewer", "agent_id": "agent-rev", "model": "m",
     "started": "2026-09-02T10:00:00Z"},
    {"task": "T1", "role": "blind-runner", "agent_id": "agent-blind", "model": "m",
     "started": "2026-09-02T11:00:00Z"},
]


def build_repo(tmp_path: Path, *, dispatch: list[dict] | None = DISPATCH_LINES) -> Path:
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
    paths = ["a.py"]
    if dispatch is not None:
        write_dispatch(repo, dispatch)
        paths.append(DISPATCH)
    git(repo, "add", *paths)
    git(repo, "commit", "-q", "-m", "feat: a")

    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


def write_review(repo: Path, body: dict) -> None:
    path = repo / REVIEW
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=1), encoding="utf-8")


def write_dispatch(repo: Path, entries: list[dict]) -> None:
    path = repo / DISPATCH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")


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
                 "dismissed": "out of scope by kouko"}
            ],
        ),
    )
    assert run_checker("push", cwd=repo).returncode == 0


# --- push.probes-package-tests --------------------------------------------


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


def test_failing_package_test_probe_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    parent = git(repo, "rev-parse", "HEAD~1")
    recommit_review(
        repo,
        review_body(
            parent,
            probes=[{"kind": "package-tests", "command": "pytest -q", "result": "fail"}],
        ),
    )
    result = run_checker("push", cwd=repo)
    assert "push.probes-package-tests" in blocked_rules(result)


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


# --- push.reviewer-ne-implementer -----------------------------------------


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
    repo = build_repo(tmp_path, dispatch=None)
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


def test_a_malformed_dispatch_line_fails_closed(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, dispatch=None)
    (repo / DISPATCH).write_text("not json\n", encoding="utf-8")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.reviewer-ne-implementer" in blocked_rules(result)


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
