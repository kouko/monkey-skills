"""Executable contract for `loom_checker.py intake <station> <change-id>`
(plan W0-03) -- what write-spec and write-plan are allowed to accept.

`intake.spec-pass` recomputes the verdict from review.json's LATEST
review round rather than trusting the `scope` prose: a file whose scope
line says "spec — PASS" while its newest round holds a NEEDS_REVISION is
blocked.
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
    # Every fixture works on a branch: on the trunk itself `merge-base HEAD
    # main` is HEAD, and branch_base() refuses to hand a rule an empty diff.
    git(repo, "checkout", "-q", "-b", "work")
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


def write_spec(
    repo: Path,
    *,
    confirmed_behavior: str = "",
    change: str = CHANGE,
    sha: bool = True,
) -> None:
    """`sha=True` appends the `@<spec-blob-sha7>` the confirmation line owes,
    computed the way the checker recomputes it (the spec WITHOUT that line).
    Pass sha=False to write the pre-W2 shape a test wants rejected."""
    path = repo / "docs/loom" / change / "spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(SPEC.format(change=change, confirmed_behavior=""), encoding="utf-8")
    if not confirmed_behavior:
        return
    # Write the line first, THEN hash: the identity is the file with that
    # line removed, and removing it is not the same as never writing it (the
    # template leaves a blank line in its place).
    path.write_text(
        SPEC.format(change=change, confirmed_behavior=confirmed_behavior),
        encoding="utf-8",
    )
    if not sha or "@" in confirmed_behavior:
        return
    path.write_text(
        SPEC.format(
            change=change,
            confirmed_behavior=f"{confirmed_behavior} @{spec_confirmation_sha(repo, change)}",
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
    # Only the SPEC rounds answer for the spec (W0-13): rounds that name a
    # spec scope, else the ones that name no scope at all and were scored
    # through a spec-side lens. A later code round is not a spec review.
    spec_scoped = [v for v in verdicts if str(v.get("scope", "")).lower().startswith("spec")]
    spec_rounds = spec_scoped or [
        v
        for v in verdicts
        if not str(v.get("scope", "")).strip()
        and str(v.get("lens", "")).lower() in {"spec", "docs", "spec-adversarial"}
    ]
    newest = max(int(v.get("round", 1)) for v in spec_rounds) if spec_rounds else 0
    latest = [v for v in spec_rounds if int(v.get("round", 1)) == newest]
    passing = (
        bool(latest)
        and len({v["reviewer"] for v in latest}) >= 2
        and all(v["verdict"] in {"PASS", "PASS_WITH_NOTES"} for v in latest)
        and any(
            p.get("kind") == "adversarial"
            and str(p.get("scope", "spec")).lower().startswith("spec")
            for p in review["probes"]
        )
    )
    # Freshness is derived the same way (W2 re-review F3/F4): the round has
    # to name the spec it read, and the confirmation line has to name the
    # spec the user saw. Both are recomputed from the same identity -- the
    # spec WITHOUT its `confirmed-behavior:` line.
    spec_path = REPO_ROOT / "docs/loom/2026-09-02-simple-loom-flow/spec.md"
    spec_body = spec_path.read_text(encoding="utf-8")
    identity = blob_sha(CONFIRMED_LINE.sub("", spec_body, count=1))
    named = [str(v.get("spec_sha", "")).strip() for v in latest]
    fresh = any(value and identity.startswith(value[:7]) for value in named)

    expected = set()
    if not (passing and fresh):
        expected.add("intake.spec-pass")
    # Read the line the way the checker reads it: parse_document strips a
    # trailing ` # …` YAML comment before applying the grammar, so an oracle
    # that matches the raw line disagrees with the gate it is checking
    # (W2 re-review NF-1).
    uncommented = re.sub(r"\s+#\s.*$", "", spec_body, flags=re.MULTILINE)
    confirmation = re.search(
        r"^confirmed-behavior:\s*(\d{4}-\d{2}-\d{2})(?:\s+@([0-9a-f]{7,40}))?\s*$",
        uncommented, re.MULTILINE,
    )
    if not (confirmation and confirmation.group(2)
            and identity.startswith(confirmation.group(2))):
        expected.add("intake.confirmed-behavior")

    result = run_checker("intake", "write-plan", "2026-09-02-simple-loom-flow", cwd=REPO_ROOT)
    assert blocked_rules(result) == expected, result.stderr
    assert (result.returncode == 0) == (not expected), result.stderr


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


def test_a_later_code_round_does_not_stand_in_for_the_spec_round(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            scoped_verdict("a", "NEEDS_REVISION", 1, "spec"),
            scoped_verdict("b", "PASS", 1, "spec"),
            scoped_verdict("c", "PASS", 2, "wave-end:1", lens="code"),
            scoped_verdict("d", "PASS", 2, "wave-end:1", lens="code"),
        ],
        scope="wave-end:1",
        probes=[dict(ADVERSARIAL, scope="spec")],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)


def test_a_passing_spec_round_survives_a_later_failing_code_round(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            scoped_verdict("a", "PASS", 1, "spec"),
            scoped_verdict("b", "PASS_WITH_NOTES", 1, "spec"),
            scoped_verdict("c", "NEEDS_REVISION", 2, "wave-end:1", lens="code"),
            scoped_verdict("d", "PASS", 2, "wave-end:1", lens="code"),
        ],
        scope="wave-end:1",
        probes=[dict(ADVERSARIAL, scope="spec")],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_the_newest_spec_round_still_decides(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            scoped_verdict("a", "PASS", 1, "spec"),
            scoped_verdict("b", "PASS", 1, "spec"),
            scoped_verdict("a", "NEEDS_REVISION", 3, "spec round 2"),
            scoped_verdict("b", "PASS", 3, "spec round 2"),
        ],
        scope="spec",
        probes=[dict(ADVERSARIAL, scope="spec")],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


def test_only_code_rounds_means_the_spec_was_never_reviewed(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [
            scoped_verdict("c", "PASS", 1, "wave-end:1", lens="code"),
            scoped_verdict("d", "PASS", 1, "wave-end:1", lens="code"),
        ],
        scope="wave-end:1",
        probes=[dict(ADVERSARIAL, scope="wave-end:1")],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


def test_a_code_scoped_adversarial_probe_does_not_count_as_the_spec_red_team(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [scoped_verdict("a", "PASS", 1, "spec"), scoped_verdict("b", "PASS", 1, "spec")],
        scope="spec",
        probes=[dict(ADVERSARIAL, scope="wave-end:1")],
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)


def test_unscoped_verdicts_fall_back_to_the_lens(tmp_path: Path) -> None:
    """Records written before rounds carried a scope still work: the file's
    own scope line plus a spec-side lens is what they have."""
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)], scope="spec")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 0, result.stderr


def test_unscoped_verdicts_from_a_non_spec_lens_do_not_count(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    code = [verdict("a", "PASS", 1), verdict("b", "PASS", 1)]
    for entry in code:
        entry["lens"] = "code"
    write_review(repo, code, scope="spec")
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.spec-pass" in blocked_rules(result)


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


def test_a_spec_rewritten_after_its_passing_round_is_blocked(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(repo, fresh_verdicts(repo))
    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0

    path = repo / "docs/loom" / CHANGE / "spec.md"
    path.write_text(
        spec_text(repo).replace(
            "## Design decision",
            "REQ-2 — cloud mirror\n  Every row is mirrored to a paid service. "
            "→ Acceptance #1\n\n## Design decision",
        ),
        encoding="utf-8",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)
    assert "send it round again" in result.stderr


def test_a_round_without_spec_sha_is_blocked(tmp_path: Path) -> None:
    """No tolerance: a round that does not say which text it read cannot be
    checked for freshness, so it does not pass."""
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo, [verdict("a", "PASS", 1), verdict("b", "PASS", 1)], spec_sha=False
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)
    assert "spec_sha in the spec round" in result.stderr
    assert "git hash-object" in result.stderr and "grep -v" in result.stderr


# --- intake.confirmed-behavior freshness (W2 adversary P02) ----------------


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
        SPEC.format(change=CHANGE, confirmed_behavior="confirmed-behavior: 2026-09-02")
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
        SPEC.format(change=CHANGE, confirmed_behavior="")
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
        SPEC.format(change=CHANGE, confirmed_behavior="")
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
        SPEC.format(change=change, confirmed_behavior="")
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


def test_one_reviewer_without_spec_sha_blocks_and_is_named(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [dict(verdict("a", "PASS", 1), spec_sha=spec_confirmation_blob(repo)),
         verdict("b", "PASS", 1)],
        spec_sha=False,
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)
    assert "b" in result.stderr and "spec_sha" in result.stderr


def test_one_reviewer_naming_a_different_text_blocks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_intent(repo, needs_design="yes — many states, no spec exists")
    write_spec(repo)
    write_review(
        repo,
        [dict(verdict("a", "PASS", 1), spec_sha=spec_confirmation_blob(repo)),
         dict(verdict("b", "PASS", 1), spec_sha="0" * 40)],
        spec_sha=False,
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)


# --- spec.ui-flows-recompute is a SHAPE check (W3-04 redesign) -------------
#
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
