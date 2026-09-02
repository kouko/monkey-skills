"""Executable contract for `loom_checker.py intake <station> <change-id>`
(plan W0-03) -- what write-spec and write-plan are allowed to accept.

`intake.spec-pass` recomputes the verdict from review.json's LATEST
review round rather than trusting the `scope` prose: a file whose scope
line says "spec — PASS" while its newest round holds a NEEDS_REVISION is
blocked.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")
REPO_ROOT = Path(__file__).resolve().parents[2]

CHANGE = "2026-09-02-a"

INTENT = """# A change
originator: tester
kind: {kind}
needs-design: {needs_design}
{status}

## Problem
People who use the nightly report wait ten minutes and give up.

## Proposed outcome
Make it fast.

## Acceptance
1. After this I can open the report in under a minute.

## Constraints
- Stay inside the existing tool.

## Out of scope
- Everything else.

## Open questions
- None yet.
"""

SPEC = """# A change — spec
intent: {change}@abc1234
{confirmed_behavior}

## Requirements
REQ-1 — fast report
  The report renders in under a minute. → Acceptance #1

## Design decision
Cache the aggregate.

## Alternatives considered
- Do nothing.

## Current state evidence
- Forward: report.py:10

## UI flows
N/A
"""


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    return repo


def write_intent(
    repo: Path,
    *,
    kind: str = "engineering",
    needs_design: str = "no — internal only",
    status: str = "status: confirmed 2026-09-02",
    change: str = CHANGE,
) -> None:
    path = repo / "docs/loom/intent" / f"{change}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        INTENT.format(kind=kind, needs_design=needs_design, status=status), encoding="utf-8"
    )


def write_spec(repo: Path, *, confirmed_behavior: str = "", change: str = CHANGE) -> None:
    path = repo / "docs/loom" / change / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(change=change, confirmed_behavior=confirmed_behavior), encoding="utf-8"
    )


ADVERSARIAL = {"kind": "adversarial", "command": "red-team the spec", "sha": "abc1234",
               "result": "pass", "artifact": "evidence/red-team.md"}


def write_review(
    repo: Path,
    verdicts: list[dict],
    *,
    change: str = CHANGE,
    scope: str = "spec",
    probes: list[dict] | None = None,
) -> None:
    path = repo / "docs/loom" / change / "review.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "reviewed_sha": "abc1234",
                "scope": scope,
                "vendors": ["anthropic"],
                "verdicts": verdicts,
                "probes": [ADVERSARIAL] if probes is None else probes,
                "open_findings": [],
            }
        ),
        encoding="utf-8",
    )


def verdict(name: str, value: str, round_: int | None = None) -> dict:
    entry = {"reviewer": name, "vendor": "anthropic", "model": "m", "lens": "spec", "verdict": value}
    if round_ is not None:
        entry["round"] = round_
    return entry


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


# --- station argument ------------------------------------------------------


def test_unknown_station_exits_2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    result = run_checker("intake", "build", CHANGE, cwd=repo)
    assert result.returncode == 2
    assert "build" in result.stderr


# --- intake.confirmed ------------------------------------------------------


def test_confirmed_intent_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    for station in ("write-spec", "write-plan"):
        result = run_checker("intake", station, CHANGE, cwd=repo)
        assert result.returncode == 0, (station, result.stderr)


def test_open_intent_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: open")
    for station in ("write-spec", "write-plan"):
        result = run_checker("intake", station, CHANGE, cwd=repo)
        assert result.returncode == 1
        assert "intake.confirmed" in blocked_rules(result)


def test_absent_status_counts_as_open(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.confirmed" in blocked_rules(result)


def test_withdrawn_intent_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: withdrawn — changed my mind")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.confirmed" in blocked_rules(result)


def test_missing_intent_is_blocked_not_ignored(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)


# --- intake.spec-pass ------------------------------------------------------


def test_needs_design_yes_without_review_json_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)


def test_latest_round_needs_revision_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            verdict("a", "PASS", 1),
            verdict("b", "PASS", 1),
            verdict("a", "NEEDS_REVISION", 2),
            verdict("b", "PASS", 2),
        ],
        scope="spec — PASS, honest",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)


def test_latest_round_all_passing_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            verdict("a", "NEEDS_REVISION", 1),
            verdict("b", "NEEDS_REVISION", 1),
            verdict("a", "PASS", 2),
            verdict("b", "PASS_WITH_NOTES", 2),
        ],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_single_reviewer_round_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(repo, [verdict("a", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


def test_review_of_something_other_than_the_spec_does_not_count(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)], scope="wave 1 code delta"
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


def test_needs_design_no_needs_no_spec_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_write_spec_does_not_require_a_spec_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_missing_spec_file_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


# --- intake.confirmed-behavior --------------------------------------------


def test_product_spec_without_confirmed_behavior_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo)
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed-behavior" in blocked_rules(result)


def test_product_spec_with_confirmed_behavior_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 2026-09-02")
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_engineering_spec_needs_no_confirmed_behavior(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="engineering", needs_design="yes — many states, no spec")
    write_spec(repo)
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.confirmed-behavior" not in blocked_rules(result)


def test_write_spec_never_asks_for_confirmed_behavior(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert "intake.confirmed-behavior" not in blocked_rules(result)


# --- the repo's own first v10 change --------------------------------------


def test_the_repos_own_change_matches_its_own_review_json() -> None:
    """The checker agrees with what the file actually records -- whatever
    that currently is. The expectation is DERIVED from review.json (latest
    round: two distinct reviewers, all passing, an `adversarial` probe)
    rather than pinned to one round, so landing a new review round changes
    the repo's gate state without silently breaking this test."""
    review = json.loads(
        (REPO_ROOT / "docs/loom/2026-09-02-simple-loom-flow/review.json").read_text(
            encoding="utf-8"
        )
    )
    verdicts = review["verdicts"]
    newest = max(int(v.get("round", 1)) for v in verdicts)
    latest = [v for v in verdicts if int(v.get("round", 1)) == newest]
    passing = (
        len({v["reviewer"] for v in latest}) >= 2
        and all(v["verdict"] in {"PASS", "PASS_WITH_NOTES"} for v in latest)
        and any(p.get("kind") == "adversarial" for p in review["probes"])
    )
    result = run_checker("intake", "write-plan", "2026-09-02-simple-loom-flow", cwd=REPO_ROOT)
    if passing:
        assert result.returncode == 0, result.stderr
    else:
        assert blocked_rules(result) == {"intake.spec-pass"}, result.stderr


# --- intake.confirmed grammar (W0-03 review fix 4) -------------------------


def test_confirmed_without_a_date_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: confirmed")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)


def test_confirmed_with_a_trailing_comment_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: confirmed 2026-09-02   # re-confirmed after the fork")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_confirmed_looking_prefix_is_not_enough(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: confirmed-soon 2026-09-02")
    assert "intake.confirmed" in blocked_rules(run_checker("intake", "write-plan", CHANGE, cwd=repo))


# --- the spec lens is read + adversarial (review fix 9) --------------------


def test_a_spec_round_without_an_adversarial_probe_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [verdict("a", "PASS", 1), verdict("b", "PASS", 1)],
        probes=[{"kind": "cold-read", "command": "read it", "result": "pass"}],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)
    assert "adversarial" in result.stderr


# --- change-id operand (review fix 10) ------------------------------------


def test_a_traversing_change_id_exits_2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    for bad in ("../evil", "a/b", "a b", ""):
        result = run_checker("intake", "write-plan", bad, cwd=repo)
        assert result.returncode == 2, bad
