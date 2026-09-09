"""Executable contract for `loom_checker.py intake <station> <change-id>`
(plan W0-03) -- what write-spec and write-plan are allowed to accept.

`intake.spec-ready` checks the spec's explicit risk declaration without a
persistent review ledger; reviewer independence stays inside write-spec.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

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
{open_questions}
"""

SPEC = """# A change — spec
intent: {change}@abc1234
{confirmed_behavior}
{pre_build_review}

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
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")
    # Every fixture works on a branch: on the trunk itself `merge-base HEAD
    # main` is HEAD, and branch_base() refuses to hand a rule an empty diff.
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def write_attestation(repo: Path, *, payload: dict | None = None, change: str = CHANGE) -> None:
    path = repo / "docs/loom" / change / "attestation.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload
            or {
                "schema": "loom-attestation/v1",
                "change_id": change,
                "content_digest": "historical-digest",
                "executions": [{
                    "kind": "package-tests", "command": "pytest", "artifact": "",
                    "result": "pass", "command_digest": "0" * 64,
                }],
                "verdicts": [{
                    "reviewer": "fixture", "vendor": "test", "model": "test",
                    "lens": "code", "verdict": "PASS", "findings": [],
                }],
                "findings": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def publish_remote_default_snapshot(repo: Path, *, with_attestation: bool = True) -> str:
    git(repo, "checkout", "-q", "-b", "delivered-snapshot")
    if with_attestation:
        write_attestation(repo)
        git(repo, "add", f"docs/loom/{CHANGE}/attestation.json")
        git(repo, "commit", "-q", "-m", "deliver fixture (#123)")
    snapshot = git(repo, "rev-parse", "HEAD")
    git(repo, "update-ref", "refs/remotes/origin/main", snapshot)
    git(repo, "checkout", "-q", "work")
    git(repo, "branch", "-D", "delivered-snapshot")
    return snapshot


def write_intent(
    repo: Path,
    *,
    kind: str = "engineering",
    needs_design: str = "no — internal only",
    status: str = "status: confirmed 2026-09-02",
    open_questions: str = "- None yet.",
    change: str = CHANGE,
) -> None:
    path = repo / "docs/loom/intent" / f"{change}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        INTENT.format(
            kind=kind,
            needs_design=needs_design,
            status=status,
            open_questions=open_questions,
        ),
        encoding="utf-8",
    )


def write_plan(repo: Path, task_dag: str, *, change: str = CHANGE) -> None:
    path = repo / "docs/loom" / change / "plan.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# A change — plan
intent: {change}@abc1234
charter: 1.0

## Task DAG
{task_dag}

## Questions asked
1 — what — none

## Risks
1. Fixture only.
""",
        encoding="utf-8",
    )


def write_spec(
    repo: Path,
    *,
    confirmed_behavior: str = "",
    pre_build_review: str = "pre-build-review: not-required — fixture",
    change: str = CHANGE,
    sha: bool = True,
) -> None:
    """`sha=True` appends the `@<spec-blob-sha7>` the confirmation line owes,
    computed the way the checker recomputes it (the spec WITHOUT that line).
    Pass sha=False to write the pre-W2 shape a test wants rejected."""
    path = repo / "docs/loom" / change / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(
            change=change,
            confirmed_behavior="",
            pre_build_review=pre_build_review,
        ),
        encoding="utf-8",
    )
    if not confirmed_behavior:
        return
    # Write the line first, THEN hash: the identity is the file with that
    # line removed, and removing it is not the same as never writing it (the
    # template leaves a blank line in its place).
    path.write_text(
        SPEC.format(
            change=change,
            confirmed_behavior=confirmed_behavior,
            pre_build_review=pre_build_review,
        ),
        encoding="utf-8",
    )
    if not sha or "@" in confirmed_behavior:
        return
    path.write_text(
        SPEC.format(
            change=change,
            confirmed_behavior=f"{confirmed_behavior} @{spec_confirmation_sha(repo, change)}",
            pre_build_review=pre_build_review,
        ),
        encoding="utf-8",
    )


ADVERSARIAL = {"kind": "adversarial", "scope": "spec", "command": "red-team the spec", "sha": "abc1234",
               "result": "pass", "artifact": "evidence/red-team.md"}


def write_review(
    repo: Path,
    verdicts: list[dict],
    *,
    change: str = CHANGE,
    scope: str = "spec",
    probes: list[dict] | None = None,
    reviewed_sha: str | None = None,
    spec_sha: bool = True,
    dispatch: list[dict] | None = None,
) -> None:
    path = repo / "docs/loom" / change / "review.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    spec_path = repo / "docs/loom" / change / "spec.md"
    if spec_sha and spec_path.is_file():
        current = spec_confirmation_blob(repo, change)
        verdicts = [
            entry if entry.get("spec_sha") else {**entry, "spec_sha": current}
            for entry in verdicts
        ]
    path.write_text(
        json.dumps(
            {
                # Default to a commit that exists: a round naming a sha this
                # repo does not have cannot be checked for freshness at all,
                # which intake.spec-pass now says out loud.
                "reviewed_sha": reviewed_sha or git(repo, "rev-parse", "HEAD"),
                "scope": scope,
                "vendors": ["anthropic"],
                "verdicts": verdicts,
                "probes": [ADVERSARIAL] if probes is None else probes,
                "open_findings": [],
                "dispatch": [] if dispatch is None else dispatch,
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


def test_not_required_spec_skips_formal_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(
        repo,
        pre_build_review="pre-build-review: not-required — routine internal change",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_invalid_pre_build_review_declaration_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo, pre_build_review="pre-build-review: maybe")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-ready" in blocked_rules(result)


def test_needs_design_no_needs_no_spec_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_needs_design_no_with_an_engineering_spec_present_still_passes(
    tmp_path: Path,
) -> None:
    """Design decision "engineering spec for an oversized Risk line"
    (branch-end-01 fix round): write-plan may itself write
    `docs/loom/<change-id>/spec.md` for a `needs-design: no` change when a
    task's rationale outgrows its Risk line. `intake.spec-pass` gates only
    `needs-design: yes` at write-plan (`yes_at_write_plan` in
    loom_checker.py) -- the spec's mere presence, with no review round of
    its own, must not trip intake at all."""
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec(repo)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_write_spec_does_not_require_a_spec_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_new_plan_accepts_positive_and_negative_pair(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, open_questions="- none")
    write_plan(
        repo,
        "**W0-01 First**  after: —  acceptance: 1\n"
        "- Files: `first.py`\n"
        "- Test: A1 positive: works; negative: rejects-empty.\n"
        "- Risk: agent-decided — fixture.\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "task_dag",
    [
        (
            "**W0-01 First**  after: —  acceptance: 2\n"
            "- Files: `first.py`\n"
            "- Test: A2 positive: works; boundary: edge.\n"
            "- Risk: agent-decided — fixture.\n"
        ),
        (
            "**W0-01 First**  after: —  acceptance: 1\n"
            "- Files: `first.py`\n"
            "- Test: A1 positive: works; negative:\n"
            "- Risk: agent-decided — fixture.\n"
        ),
        (
            "**W0-01 First**  after: —  acceptance: 1\n"
            "- Files: `first.py`\n"
            "- Test: A1 positive: works; negative: rejects-empty.\n"
            "- Risk: agent-decided — fixture.\n\n"
            "**W0-02 Second**  after: W0-01\n"
            "- Files: `second.py`\n"
            "- Test: second works.\n"
            "- Risk: agent-decided — fixture.\n"
        ),
    ],
)
def test_new_plan_rejects_missing_or_invalid_case_contract(
    tmp_path: Path, task_dag: str
) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, open_questions="- none")
    write_plan(repo, task_dag)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.test-case-pair" in blocked_rules(result)


def test_new_plan_rejects_unresolved_open_questions(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_plan(
        repo,
        "**W0-01 First**  after: —  acceptance: 1\n"
        "- Files: `first.py`\n"
        "- Test: A1 positive: works; boundary: edge.\n"
        "- Risk: agent-decided — fixture.\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.test-case-pair" in blocked_rules(result)
    assert "Open questions" in result.stderr


def test_new_plan_cannot_self_exempt_by_removing_charter_and_acceptance(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, open_questions="- none")
    write_plan(
        repo,
        "**W0-01 First**  after: —\n"
        "- Files: `first.py`\n"
        "- Test: works.\n"
        "- Risk: fixture.\n",
    )
    plan = repo / "docs/loom" / CHANGE / "plan.md"
    plan.write_text(plan.read_text().replace("charter: 1.0\n", ""))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.test-case-pair" in blocked_rules(result)


def test_committed_charter_era_plan_keeps_legacy_task_grammar(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, open_questions="- none")
    write_plan(
        repo,
        "**W0-01 Legacy task**  after: —  review: after-task\n"
        "- Files: `first.py`\n"
        "- Test: run the legacy check.\n"
        "- Risk: fixture.\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "legacy plan")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_committed_new_plan_cannot_strip_readiness_to_claim_legacy(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, open_questions="- none")
    write_plan(
        repo,
        "**W0-01 First**  after: —  acceptance: 1\n"
        "- Files: `first.py`\n"
        "- Test: A1 positive: works; negative: rejects-empty.\n"
        "- Risk: fixture.\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "new paired plan")
    plan = repo / "docs/loom" / CHANGE / "plan.md"
    plan.write_text(
        plan.read_text()
        .replace("charter: 1.0\n", "")
        .replace("  acceptance: 1", "")
        .replace("A1 positive: works; negative: rejects-empty.", "run smoke")
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.test-case-pair" in blocked_rules(result)


def test_missing_spec_file_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-ready" in blocked_rules(result)


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


def test_a_traversing_change_id_exits_2(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    for bad in ("../evil", "a/b", "a b", ""):
        result = run_checker("intake", "write-plan", bad, cwd=repo)
        assert result.returncode == 2, bad


# --- intake.spec-pass: a later round must not stand in for the spec one ----
#
# W0-13. review.json accumulates: the spec round is round 1, and every wave
# of the build adds another. Reading only the newest round, or only the
# file-level `scope` line the newest round overwrote, makes a passing code
# round answer for a spec that was never reviewed -- and makes a failing
# code round block a spec that passed. The round's own `scope` is what
# decides; when no verdict carries one, the lens does.


def scoped_verdict(name: str, value: str, round_: int, scope: str, lens: str = "spec") -> dict:
    entry = verdict(name, value, round_)
    entry["scope"] = scope
    entry["lens"] = lens
    return entry


# --- shared fixtures for the W2 hardening rules -----------------------------


def blob_sha(text: str) -> str:
    """`git hash-object` over a string -- the same value the checker
    recomputes, produced by git itself so the test cannot agree with a bug
    in a hand-rolled hasher."""
    return subprocess.run(
        ["git", "hash-object", "--stdin"],
        input=text, capture_output=True, text=True, check=True,
    ).stdout.strip()


CONFIRMED_LINE = re.compile(r"^confirmed-behavior:.*\n?", re.MULTILINE)


def spec_text(repo: Path, change: str = CHANGE) -> str:
    return (repo / "docs/loom" / change / "spec.md").read_text(encoding="utf-8")


def spec_confirmation_blob(repo: Path, change: str = CHANGE) -> str:
    """The one spec identity both freshness rules use: the file MINUS the
    `confirmed-behavior:` line, so the value is not a hash of itself and
    writing the confirmation does not invalidate the review that preceded
    it."""
    return blob_sha(CONFIRMED_LINE.sub("", spec_text(repo, change), count=1))


def spec_confirmation_sha(repo: Path, change: str = CHANGE) -> str:
    return spec_confirmation_blob(repo, change)[:7]


def write_spec_confirmation(repo: Path, date: str, change: str = CHANGE) -> None:
    """Append the confirmation line to a spec already on disk, naming the sha
    of the text it confirms."""
    path = repo / "docs/loom" / change / "spec.md"
    text = CONFIRMED_LINE.sub("", path.read_text(encoding="utf-8"), count=1)
    line = f"confirmed-behavior: {date} @{blob_sha(text)[:7]}"
    lines = text.splitlines()
    for index, existing in enumerate(lines):
        if existing.startswith("intent:"):
            lines.insert(index + 1, line)
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def commit_file(repo: Path, rel: str, content: str = "x\n") -> None:
    target = repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", rel)
    git(repo, "commit", "-q", "-m", f"add {rel}")


def fresh_verdicts(repo: Path, change: str = CHANGE) -> list[dict]:
    sha = spec_confirmation_blob(repo, change)
    return [
        dict(verdict("a", "PASS", 1), spec_sha=sha),
        dict(verdict("b", "PASS", 1), spec_sha=sha),
    ]


# --- intent.kind-recompute at intake (W2 adversary P05) --------------------


def test_intake_blocks_an_engineering_kind_over_an_interface_diff(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/cli/add.py")
    write_intent(repo, kind="engineering", needs_design="yes — the CLI grows a flag")
    write_spec(repo)
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intent.kind-recompute" in blocked_rules(result)


def test_intake_leaves_an_engineering_kind_off_the_surfaces_alone(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/store/index.py")
    write_intent(repo)
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


# --- intake.spec-pass freshness (W2 adversary P09) -------------------------


def test_a_confirmation_naming_the_current_spec_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 2026-09-02")
    write_spec(
        repo,
        confirmed_behavior=f"confirmed-behavior: 2026-09-02 @{spec_confirmation_sha(repo)}",
    )
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_confirmation_naming_another_spec_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 2026-09-02 @0000000")
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed-behavior" in blocked_rules(result)


def test_a_confirmation_without_a_sha_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 2026-09-02", sha=False)
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed-behavior" in blocked_rules(result)
    assert "git hash-object" in result.stderr


def test_an_impossible_confirmation_date_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 9999-99-99")
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed-behavior" in blocked_rules(result)
    assert "not a real date" in result.stderr


# --- intake.confirmed: the status date is a date too (W2 re-review F6) -----


def test_an_impossible_confirmed_status_date_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: confirmed 9999-99-99")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "not a real date" in result.stderr


def test_a_real_confirmed_status_date_is_accepted(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: confirmed 2028-02-29")
    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0


# --- intake.confirmed: delivered is derived from remote-default evidence ---


def test_remote_default_delivery_blocks_duplicate_intake(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_intent(repo, "status: confirmed 2026-09-02")
    publish_remote_default_snapshot(repo)

    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)

    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "delivered" in result.stderr


def test_worktree_only_attestation_does_not_prove_delivery(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_attestation(repo)

    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0


@pytest.mark.parametrize(
    "payload",
    [
        {"change_id": CHANGE},
        {
            "schema": "loom-attestation/v999",
            "change_id": CHANGE,
            "content_digest": "historical-digest",
            "executions": [],
            "verdicts": [],
            "findings": [],
        },
        {
            "schema": "loom-attestation/v1",
            "change_id": "another-change",
            "content_digest": "historical-digest",
            "executions": [],
            "verdicts": [],
            "findings": [],
        },
        {
            "schema": "loom-attestation/v1",
            "change_id": CHANGE,
            "content_digest": "historical-digest",
            "executions": [{
                "kind": None, "command": None, "artifact": None,
                "result": None, "command_digest": None,
            }],
            "verdicts": [{
                "reviewer": "fixture", "vendor": "test", "model": "test",
                "lens": "code", "verdict": "PASS", "findings": [],
            }],
            "findings": [],
        },
        {
            "schema": "loom-attestation/v1",
            "change_id": CHANGE,
            "content_digest": "historical-digest",
            "executions": [{
                "kind": "package-tests", "command": "pytest", "artifact": "",
                "result": "fail", "command_digest": "0" * 64,
            }],
            "verdicts": [{
                "reviewer": "fixture", "vendor": "test", "model": "test",
                "lens": "code", "verdict": "PASS", "findings": [],
            }],
            "findings": [],
        },
        {
            "schema": "loom-attestation/v1",
            "change_id": CHANGE,
            "content_digest": "historical-digest",
            "executions": [{
                "kind": "package-tests", "command": "pytest", "artifact": "",
                "result": "pass", "command_digest": "0" * 64,
            }],
            "verdicts": [{
                "reviewer": "fixture", "vendor": "test", "model": "test",
                "lens": "code", "verdict": [], "findings": [],
            }],
            "findings": [],
        },
        {
            "schema": "loom-attestation/v1",
            "change_id": CHANGE,
            "content_digest": "historical-digest",
            "executions": [{
                "kind": "package-tests", "command": "pytest", "artifact": "",
                "result": "pass", "command_digest": "0" * 64,
            }],
            "verdicts": [{
                "reviewer": "fixture", "vendor": "test", "model": "test",
                "lens": "code", "verdict": "PASS", "findings": [],
            }],
            "findings": {},
        },
    ],
)
def test_partial_unsupported_or_mismatched_remote_witness_stays_active(
    tmp_path: Path, payload: dict
) -> None:
    repo = make_repo(tmp_path)
    commit_intent(repo, "status: confirmed 2026-09-02")
    git(repo, "checkout", "-q", "-b", "invalid-snapshot")
    write_attestation(repo, payload=payload)
    git(repo, "add", f"docs/loom/{CHANGE}/attestation.json")
    git(repo, "commit", "-q", "-m", "invalid witness")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "work")

    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0


def test_later_unrelated_remote_commit_does_not_reopen_delivery(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_intent(repo, "status: confirmed 2026-09-02")
    snapshot = publish_remote_default_snapshot(repo)
    git(repo, "checkout", "-q", "-b", "later", snapshot)
    (repo / "later.txt").write_text("unrelated\n", encoding="utf-8")
    git(repo, "add", "later.txt")
    git(repo, "commit", "-q", "-m", "unrelated later change")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "work")

    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "delivered" in result.stderr


def test_remote_attestation_without_canonical_intent_stays_active(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    git(repo, "checkout", "-q", "main")
    write_attestation(repo)
    git(repo, "add", f"docs/loom/{CHANGE}/attestation.json")
    git(repo, "commit", "-q", "-m", "orphan witness")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "work")

    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0


def test_legacy_closed_on_remote_default_still_blocks_intake(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_intent(repo, "status: confirmed 2026-09-02")
    git(repo, "checkout", "-q", "-b", "closed-snapshot")
    commit_intent(repo, "status: closed 2026-09-03 — PR #42")
    git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
    git(repo, "checkout", "-q", "work")

    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "closed (PR #42)" in result.stderr


def test_unresolved_remote_default_blocks_intake_as_indeterminate(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    git(repo, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")

    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)

    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "indeterminate" in result.stderr


@pytest.mark.parametrize("failing_path", ["intent", "attestation"])
def test_remote_snapshot_read_failure_is_indeterminate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failing_path: str
) -> None:
    import loom_checker as lc

    repo = make_repo(tmp_path)
    commit_intent(repo, "status: confirmed 2026-09-02")
    publish_remote_default_snapshot(repo)
    real_run_git = lc.run_git
    suffix = (
        f"docs/loom/intent/{CHANGE}.md"
        if failing_path == "intent"
        else f"docs/loom/{CHANGE}/attestation.json"
    )

    def fail_selected_read(repo_path: Path, *args: str, **kwargs):
        if args and args[0] in {"ls-tree", "show"} and args[-1].endswith(suffix):
            raise subprocess.TimeoutExpired(["git", *args], timeout=1)
        return real_run_git(repo_path, *args, **kwargs)

    monkeypatch.setattr(lc, "run_git", fail_selected_read)

    state, detail = lc.intent_delivery_state(repo, CHANGE)
    assert state == "indeterminate"
    assert "read" in detail


# --- intake.confirmed: closed is terminal (W0-01) ---------------------------


def test_a_closed_intent_is_blocked_from_intake_with_the_pr_number(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: closed 2026-09-03 — PR #780")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "closed (PR #780)" in result.stderr


def test_an_impossible_closed_status_date_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, status="status: closed 2026-02-30 — PR #1")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "not a real date" in result.stderr


# --- intake.confirmed: closed is terminal even off the current status line
# (W0-02) -- reopen is caught by recomputing branch history and the trunk
# copy, not by trusting the intent file's own status line, which a reopen
# has by definition already changed back.


def commit_intent(repo: Path, status: str, *, change: str = CHANGE) -> None:
    write_intent(repo, status=status, change=change)
    git(repo, "add", f"docs/loom/intent/{change}.md")
    git(repo, "commit", "-q", "-m", f"intent: {status}")


def test_reopen_blocked_when_branch_history_shows_a_closed_status(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_intent(repo, "status: closed 2026-09-03 — PR #7")
    commit_intent(repo, "status: confirmed 2026-09-03")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.confirmed" in blocked_rules(result)
    assert "not reopened" in result.stderr
    assert "PR #7" in result.stderr


def test_local_trunk_close_does_not_override_remote_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)  # on "work", branched from main at the seed commit
    commit_intent(repo, "status: confirmed 2026-09-02")  # work's own history stays clean
    git(repo, "checkout", "-q", "main")
    commit_intent(repo, "status: closed 2026-09-03 — PR #42")
    git(repo, "checkout", "-q", "work")
    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0


def test_local_trunk_absence_does_not_hide_the_remote_default(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    git(repo, "branch", "-D", "main")
    write_intent(repo, kind="product", status="status: confirmed 2026-09-02")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_reopen_log_pattern_derives_from_the_status_closed_alternative() -> None:
    import loom_checker as lc

    assert lc.STATUS_CLOSED_LITERAL
    assert lc.STATUS_CLOSED_LITERAL in lc.STATUS.pattern
    assert lc.REOPEN_LOG_PATTERN.endswith(lc.STATUS_CLOSED_LITERAL)


# --- spec.req-grammar (W2 adversary P03) ----------------------------------


REQ_BODY = """# A change — spec
intent: {change}@abc1234

## Requirements
{requirements}

## Design decision
Cache the aggregate.

## Alternatives considered
- Do nothing.

## Current state evidence
- Forward: report.py:10

## UI flows
N/A
"""


def write_spec_requirements(repo: Path, requirements: str, change: str = CHANGE) -> None:
    path = repo / "docs/loom" / change / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REQ_BODY.format(change=change, requirements=requirements), encoding="utf-8")


def test_contiguous_unique_reqs_pointing_at_real_acceptance_pass(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec_requirements(
        repo,
        "REQ-1 — fast report\n  It renders in under a minute. → Acceptance #1",
    )
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_a_skipped_req_number_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec_requirements(
        repo,
        "REQ-1 — a\n  one → Acceptance #1\n"
        "REQ-4 — b\n  two → Acceptance #1",
    )
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "spec.req-grammar" in blocked_rules(result)
    assert "REQ-4" in result.stderr


def test_a_duplicate_req_number_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec_requirements(
        repo,
        "REQ-1 — a\n  one → Acceptance #1\n"
        "REQ-2 — b\n  two → Acceptance #1\n"
        "REQ-2 — c\n  three → Acceptance #1",
    )
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert "spec.req-grammar" in blocked_rules(result)
    assert "REQ-2" in result.stderr


def test_a_req_with_no_acceptance_pointer_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec_requirements(
        repo,
        "REQ-1 — a\n  one → Acceptance #1\n"
        "REQ-2 — b\n  two, pointing nowhere",
    )
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert "spec.req-grammar" in blocked_rules(result)
    assert "REQ-2" in result.stderr


def test_a_req_pointing_at_an_acceptance_that_does_not_exist_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)   # the intent carries exactly one Acceptance item
    write_spec_requirements(
        repo,
        "REQ-1 — a\n  one → Acceptance #7",
    )
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert "spec.req-grammar" in blocked_rules(result)
    assert "#7" in result.stderr


def test_a_requirements_section_with_no_req_line_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo)
    write_spec_requirements(repo, "- the report must be fast")
    result = run_checker("intake", "write-spec", CHANGE, cwd=repo)
    assert "spec.req-grammar" in blocked_rules(result)


# --- spec.ui-flows-recompute (W2 adversary P06) ---------------------------


def test_ui_flows_na_while_the_diff_touches_a_surface_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "web/DuePill.tsx")
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_spec(repo, confirmed_behavior="confirmed-behavior: 2026-09-02")
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "spec.ui-flows-recompute" in blocked_rules(result)
    assert "web/DuePill.tsx" in result.stderr


def test_ui_flows_na_with_a_reason_and_no_surface_diff_is_fine(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "src/store/index.py")
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_real_ui_flows_over_a_surface_diff_are_fine(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "web/DuePill.tsx")
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    path = repo / "docs/loom" / CHANGE / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(
            change=CHANGE,
            confirmed_behavior="confirmed-behavior: 2026-09-02",
            pre_build_review="pre-build-review: not-required — fixture",
        )
        .replace(
            "## UI flows\nN/A",
            "## UI flows\n- `todo list` → every row shows its due date\n",
        ),
        encoding="utf-8",
    )
    write_review(repo, fresh_verdicts(repo))
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "spec.ui-flows-recompute" not in blocked_rules(result)


@pytest.mark.parametrize("placeholder", [
    "N/A", "N/A — no interface", "None.", "沒有介面", "_none_", "Not applicable",
    "The list gets a due-date column.",     # prose, but no operation → reaction
])
def test_ui_flows_without_a_flow_line_is_blocked(tmp_path: Path, placeholder: str) -> None:
    """The rule is not "does not say N/A" -- five spellings of nothing exist.
    It is "carries at least one `<operation> → <reaction>` line", which is
    what decision point 2 reads back to the user."""
    repo = make_repo(tmp_path)
    commit_file(repo, "web/DuePill.tsx")
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    path = repo / "docs/loom" / CHANGE / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(change=CHANGE, confirmed_behavior="", pre_build_review="pre-build-review: not-required — fixture")
        .replace("## UI flows\nN/A", f"## UI flows\n{placeholder}"),
        encoding="utf-8",
    )
    write_spec_confirmation(repo, "2026-09-02")
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1, result.stderr
    assert "spec.ui-flows-recompute" in blocked_rules(result)


@pytest.mark.parametrize("arrow", ["→", "->"])
def test_a_single_flow_line_with_either_arrow_is_enough(tmp_path: Path, arrow: str) -> None:
    repo = make_repo(tmp_path)
    commit_file(repo, "web/DuePill.tsx")
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    path = repo / "docs/loom" / CHANGE / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(change=CHANGE, confirmed_behavior="", pre_build_review="pre-build-review: not-required — fixture")
        .replace("## UI flows\nN/A", f"## UI flows\n- `todo list` {arrow} rows show the due date"),
        encoding="utf-8",
    )
    write_spec_confirmation(repo, "2026-09-02")
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


# --- spec.ui-flows-recompute: what counts as a flow (re-review NF-2) -------


def write_ui_flows(repo: Path, body: str, change: str = CHANGE) -> None:
    path = repo / "docs/loom" / change / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        SPEC.format(change=change, confirmed_behavior="", pre_build_review="pre-build-review: not-required — fixture")
        .replace("## UI flows\nN/A", f"## UI flows\n{body}"),
        encoding="utf-8",
    )
    write_spec_confirmation(repo, "2026-09-02")


def ui_flows_verdict(tmp_path: Path, body: str) -> subprocess.CompletedProcess:
    repo = make_repo(tmp_path)
    commit_file(repo, "web/DuePill.tsx")
    write_intent(repo, kind="product", needs_design="yes — new visible surface")
    write_ui_flows(repo, body)
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)])
    return run_checker("intake", "write-plan", CHANGE, cwd=repo)


ESCAPES = {
    "an arrow inside a mermaid fence":
        "```mermaid\nflowchart LR\n  add --> list\n```",
    "an arrow inside a python fence":
        "```python\ndef add(task) -> None: ...\n```",
    "an arrow inside an HTML comment":
        "<!-- todo add --due friday → the row shows the date -->",
    "an arrow with nothing on the left":
        "→ the todo is stored with its due date",
    "an arrow with one token on each side":
        "add → stored",
    "None. as the whole answer": "None.",
    "無 as the whole answer": "無",
}


@pytest.mark.parametrize("label", sorted(ESCAPES))
def test_these_do_not_count_as_a_flow(tmp_path: Path, label: str) -> None:
    result = ui_flows_verdict(tmp_path, ESCAPES[label])
    assert result.returncode == 1, result.stderr
    assert "spec.ui-flows-recompute" in blocked_rules(result)


def test_a_real_flow_line_counts(tmp_path: Path) -> None:
    result = ui_flows_verdict(
        tmp_path,
        "todo add --due 2026-09-10 'buy milk' → the todo is stored with its due date",
    )
    assert result.returncode == 0, result.stderr


def test_a_real_flow_survives_a_mermaid_fence_beside_it(tmp_path: Path) -> None:
    result = ui_flows_verdict(
        tmp_path,
        "```mermaid\nflowchart LR\n  add --> list\n```\n"
        "- `todo list` → every row shows its due date",
    )
    assert result.returncode == 0, result.stderr


# --- intake.spec-pass: every reviewer names the text (re-review NF-3) ------


# The rule counts visible characters on each side of an arrow, in any
# script, and nothing else. It carries no list of nothing-words: three
# rounds of keyword patches each reopened, and a checker that tries to read
# meaning is a checker that can be talked around. What a flow line SAYS is
# the reviewer lens's territory, and some structurally-fine lines are poor
# flows -- that is the intended division of labour, asserted below.


STRUCTURAL_PASSES = {
    "a quoted line whose left side is a placeholder — the reviewer's job, not the checker's":
        "> N/A — no interface -> see x",
    "a Traditional Chinese flow with no spaces in it":
        "在待辦清單輸入到期日 → 每一列顯示該到期日",
    "a Japanese flow with no spaces in it":
        "期限を入力する → 一覧に期限が表示される",
    "a markdown table row":
        "| todo add --due D | → | shows the due date |",
}


@pytest.mark.parametrize("label", sorted(STRUCTURAL_PASSES))
def test_these_clear_the_structural_floor(tmp_path: Path, label: str) -> None:
    result = ui_flows_verdict(tmp_path, STRUCTURAL_PASSES[label])
    assert result.returncode == 0, result.stderr


STRUCTURAL_BLOCKS = {
    "three characters on the left": "add → stored",
    "an arrow that lives only inside a fence":
        "```mermaid\nflowchart LR\n  add --> list\n```",
    "an empty section": "",
}


@pytest.mark.parametrize("label", sorted(STRUCTURAL_BLOCKS))
def test_these_do_not_clear_the_structural_floor(tmp_path: Path, label: str) -> None:
    result = ui_flows_verdict(tmp_path, STRUCTURAL_BLOCKS[label])
    assert result.returncode == 1, result.stdout
    assert "spec.ui-flows-recompute" in blocked_rules(result)
