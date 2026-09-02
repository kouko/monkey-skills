"""The W1 adversary's escapes, closed (probes P02, P03, P04, P07, P11, P13).

Each case here reproduces one attack that the wave-end adversary got past
the checker, so every test is a regression eval in the §11 sense: it fails
on the checker as the adversary found it and passes on the checker as it
is now. The fixtures are real git repositories, for the same reason the
rest of the push suite uses them — every rule here recomputes a fact from
a tree or a diff, and a mock would only test the mock.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).with_name("loom_checker.py")
CHANGE = "2026-09-02-a"
REVIEW = f"docs/loom/{CHANGE}/review.json"
KICKOFF = "docs/loom/KICKOFF-DEFAULTS.md"

DECLARED_TESTS = 'python3 -c "raise SystemExit(0)"'


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def run_checker(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def adversarial_probes(sha: str, count: int = 3) -> list[dict]:
    return [
        {
            "kind": "adversarial",
            "command": f"python3 evidence/abuse_{n}.py",
            "sha": sha,
            "result": "pass",
            "artifact": f"evidence/abuse_{n}.py",
        }
        for n in range(count)
    ]


def review_body(sha: str, **overrides) -> dict:
    body = {
        "reviewed_sha": sha,
        "scope": "wave 1 code delta",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "agent-rev", "vendor": "anthropic", "model": "m",
             "lens": "code", "verdict": "PASS", "dimension_scores": {},
             "findings": [], "round": 1},
            {"reviewer": "agent-blind", "vendor": "anthropic", "model": "m",
             "lens": "code", "verdict": "PASS", "dimension_scores": {},
             "findings": [], "round": 1},
        ],
        "probes": [
            {"kind": "package-tests", "command": DECLARED_TESTS, "sha": sha,
             "result": "pass", "artifact": "evidence/tests.txt"},
            *adversarial_probes(sha),
        ],
        "open_findings": [],
        "questions": [],
        "dispatch": [
            {"task": "T1", "role": "implementer", "agent_id": "agent-imp",
             "model": "m", "started": "2026-09-02T09:00:00Z", "fresh_context": True},
            {"task": "T1", "role": "reviewer", "agent_id": "agent-rev",
             "model": "m", "started": "2026-09-02T10:00:00Z", "fresh_context": True},
            {"task": "T1", "role": "reviewer", "agent_id": "agent-blind",
             "model": "m", "started": "2026-09-02T11:00:00Z", "fresh_context": True},
        ],
    }
    body.update(overrides)
    return body


def write(repo: Path, rel: str, text: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_repo(tmp_path: Path, *, kickoff: str | None = None,
               task_trailer: str = "T1") -> Path:
    """HEAD^ is the code commit, HEAD the review-only one."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, "seed.txt", "seed\n")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    write(repo, "a.py", "value = 1\n")
    write(repo, "evidence/tests.txt", "2199 passed\n")
    for n in range(3):
        write(repo, f"evidence/abuse_{n}.py", "raise SystemExit(0)\n")
    write(
        repo,
        KICKOFF,
        kickoff
        if kickoff is not None
        else f"# Kickoff Defaults\n\n- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"feat: a\n\nTask: {task_trailer}")

    write_review(repo, review_body(git(repo, "rev-parse", "HEAD")))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


def write_review(repo: Path, body: dict) -> None:
    write(repo, REVIEW, json.dumps(body, indent=1))


def recommit_review(repo: Path, body: dict) -> None:
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


def rebuild(repo: Path, **overrides) -> dict:
    return review_body(git(repo, "rev-parse", "HEAD~1"), **overrides)


# --- the fixture itself still passes ---------------------------------------


def test_the_hardened_fixture_still_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr + result.stdout


# --- P04: a probe command that proves nothing ------------------------------


def test_a_package_test_probe_that_is_not_the_declared_command_blocks(tmp_path: Path) -> None:
    """`true` exits 0 for reasons that have nothing to do with the suite."""
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    body = rebuild(repo)
    body["probes"][0]["command"] = "true"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "true" in result.stderr and DECLARED_TESTS in result.stderr
    assert reviewed  # the fixture built what we think it built


def test_a_repo_declaring_no_test_command_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, kickoff="# Kickoff Defaults\n")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "package-tests:" in result.stderr


def test_a_declared_none_waives_the_package_test_probe(tmp_path: Path) -> None:
    """C7: a repo with no suite records the gap instead of faking a run."""
    repo = build_repo(
        tmp_path,
        kickoff="# Kickoff Defaults\n\n- package-tests: none — no suite yet (2026-09-02)\n",
    )
    body = rebuild(repo)
    body["probes"] = adversarial_probes(git(repo, "rev-parse", "HEAD~1"))
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "package-tests: none" in result.stdout


def test_pytest_is_detected_when_kickoff_declares_nothing(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, kickoff="# Kickoff Defaults\n")
    write(repo, "pyproject.toml", "[project]\nname = 'x'\n")
    git(repo, "add", "pyproject.toml")
    git(repo, "commit", "-q", "-m", "chore: pyproject\n\nTask: T1")
    body = review_body(git(repo, "rev-parse", "HEAD"))
    body["probes"][0]["command"] = "true"
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert "python3 -m pytest -q" in result.stderr


def test_an_adversarial_probe_with_a_trivial_command_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["command"] = "true"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


def test_an_adversarial_probe_naming_no_artifact_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["artifact"] = ""
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


def test_an_adversarial_probe_whose_artifact_is_absent_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["artifact"] = "evidence/never_committed.py"
            probe["command"] = "python3 evidence/never_committed.py"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


def test_an_adversarial_command_that_never_runs_its_artifact_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["command"] = DECLARED_TESTS
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


# --- P03: a rename hiding a deletion in the review-only commit --------------


def test_a_rename_into_the_review_path_still_counts_as_a_deletion(tmp_path: Path) -> None:
    """P03: rename detection collapsed a delete and an add into one path.

    The code commit adds a source file whose bytes are nearly the review
    body; the "review-only" commit renames that file onto the review path
    and patches it. Under `--name-only` git reports a single path and the
    source file vanishes from the tree unremarked.
    """
    repo = build_repo(tmp_path)
    reviewed = git(repo, "rev-parse", "HEAD~1")
    body = rebuild(repo)

    git(repo, "reset", "-q", "--hard", "HEAD~1")
    write(repo, "src/generated_fixture.json", json.dumps(body, indent=1))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: fixture\n\nTask: T1")
    reviewed = git(repo, "rev-parse", "HEAD")

    (repo / REVIEW).parent.mkdir(parents=True, exist_ok=True)
    git(repo, "mv", "src/generated_fixture.json", REVIEW)
    write_review(repo, review_body(reviewed))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    listing = git(repo, "show", "--name-only", "--pretty=format:", "HEAD")
    assert "src/generated_fixture.json" not in listing, (
        "the premise is stale: git no longer collapses this rename, so the "
        "attack this test reproduces cannot happen."
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.review-only-head" in blocked_rules(result)


# --- P13: a dispatch record that does not cover the tasks ------------------


def test_a_task_with_no_implementer_dispatch_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, task_trailer="T2")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    assert "T2" in result.stderr


def test_every_task_covered_by_an_implementer_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert "push.dispatch-covers-tasks" not in blocked_rules(result)


# --- P07: a second vendor that was named and never used --------------------


def test_a_named_second_vendor_absent_from_the_round_blocks(tmp_path: Path) -> None:
    repo = build_repo(
        tmp_path,
        kickoff=(
            "# Kickoff Defaults\n\n"
            f"- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n"
            "- second-vendor: codex — cross-vendor review (2026-09-02)\n"
        ),
    )
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)
    assert "openai" in result.stderr


def test_a_recorded_fallback_satisfies_the_second_vendor_rule(tmp_path: Path) -> None:
    repo = build_repo(
        tmp_path,
        kickoff=(
            "# Kickoff Defaults\n\n"
            f"- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n"
            "- second-vendor: codex — cross-vendor review (2026-09-02)\n"
        ),
    )
    body = rebuild(repo)
    body["verdicts"][0]["fallback"] = "codex missing at 2026-09-02"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, result.stderr + result.stdout


def test_second_vendor_none_asks_for_nothing(tmp_path: Path) -> None:
    repo = build_repo(
        tmp_path,
        kickoff=(
            "# Kickoff Defaults\n\n"
            f"- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n"
            "- second-vendor: none — one vendor is enough (2026-09-02)\n"
        ),
    )
    result = run_checker("push", cwd=repo)
    assert "push.second-vendor-honoured" not in blocked_rules(result)


# --- P11: KICKOFF-DEFAULTS narrowing the interface surfaces -----------------


def _intent(needs_design: str = "no — internal only") -> str:
    return (
        "# add a knob\n"
        "originator: kouko\n"
        "kind: engineering\n"
        f"needs-design: {needs_design}\n"
        "status: confirmed 2026-09-02\n"
        "\n## Problem\nThe retry delay is fixed.\n"
        "\n## Proposed outcome\nMake it configurable.\n"
        "\n## Acceptance\n1. The delay can be set.\n"
        "\n## Constraints\n- none\n"
        "\n## Out of scope\n- none\n"
        "\n## Open questions\n- none\n"
    )


def test_kickoff_can_add_interface_surfaces_but_never_narrow(tmp_path: Path) -> None:
    repo = tmp_path / "surfaces"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, "seed.txt", "seed\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    write(repo, f"docs/loom/intent/{CHANGE}.md", _intent())
    write(repo, "src/api/routes.py", "ROUTES = []\n")
    write(repo, KICKOFF, "# Kickoff Defaults\n\n- interface-surfaces: docs/nothing/** — narrowed (2026-09-02)\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: routes\n\nneeds-design: no — internal only")
    message = repo / "COMMIT_MSG.txt"
    message.write_text(
        "feat: routes\n\nneeds-design: no — internal only\n", encoding="utf-8"
    )

    result = run_checker(
        "intent", f"docs/loom/intent/{CHANGE}.md", "--commit-msg", str(message), cwd=repo
    )
    assert result.returncode == 1
    assert "intent.needs-design-recompute" in blocked_rules(result)
    assert "src/api/routes.py" in result.stderr


def test_a_kickoff_added_surface_is_also_enforced(tmp_path: Path) -> None:
    repo = tmp_path / "added"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, "seed.txt", "seed\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")

    write(repo, f"docs/loom/intent/{CHANGE}.md", _intent())
    write(repo, "src/widgets/panel.py", "PANEL = 1\n")
    write(repo, KICKOFF, "# Kickoff Defaults\n\n- interface-surfaces: **/widgets/** — this repo's UI lives here (2026-09-02)\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: panel\n\nneeds-design: no — internal only")
    message = repo / "COMMIT_MSG.txt"
    message.write_text(
        "feat: panel\n\nneeds-design: no — internal only\n", encoding="utf-8"
    )

    result = run_checker(
        "intent", f"docs/loom/intent/{CHANGE}.md", "--commit-msg", str(message), cwd=repo
    )
    assert result.returncode == 1
    assert "src/widgets/panel.py" in result.stderr


# --- P02: the after-task budget ---------------------------------------------


PLAN_HEAD = (
    "# w1 — plan\n"
    f"intent: {CHANGE}@abc1234\n"
    "\n## Current State Evidence\n- Forward: src/thing.py:1\n"
    "\n## Task DAG\n"
)
PLAN_TAIL = "\n## Risks\n1. none\n"


def _intake_repo(tmp_path: Path, plan_tasks: str) -> Path:
    repo = tmp_path / "intake"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, f"docs/loom/intent/{CHANGE}.md", _intent())
    write(repo, f"docs/loom/{CHANGE}/plan.md", PLAN_HEAD + plan_tasks + PLAN_TAIL)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): intent + plan")
    return repo


def test_a_fourth_after_task_without_a_reason_blocks(tmp_path: Path) -> None:
    repo = _intake_repo(
        tmp_path,
        "**W1-01 first** after: none review: after-task\n"
        "**W1-02 second** after: W1-01 review: after-task\n"
        "**W1-03 third** after: W1-02 review: after-task\n"
        "**W1-04 fourth** after: W1-03 review: after-task\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.after-task-budget" in blocked_rules(result)
    assert "W1-03" in result.stderr


def test_extra_after_tasks_carrying_a_reason_are_accepted(tmp_path: Path) -> None:
    repo = _intake_repo(
        tmp_path,
        "**W1-01 first** after: none review: after-task\n"
        "**W1-02 second** after: W1-01 review: after-task\n"
        "**W1-03 third** after: W1-02 review: after-task — touches the push gate\n"
        "**W1-04 fourth** after: W1-03 review: after-task — rewrites the schema\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.after-task-budget" not in blocked_rules(result)


def test_two_after_tasks_need_no_reason(tmp_path: Path) -> None:
    repo = _intake_repo(
        tmp_path,
        "**W1-01 first** after: none review: after-task\n"
        "**W1-02 second** after: W1-01 review: after-task\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert "intake.after-task-budget" not in blocked_rules(result)


# --- B1: an unscoped adversarial probe is not a spec red-team ---------------


def test_an_unscoped_adversarial_probe_does_not_satisfy_the_spec_gate(tmp_path: Path) -> None:
    repo = tmp_path / "spec"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, f"docs/loom/intent/{CHANGE}.md", _intent("yes — new CLI surface"))
    write(
        repo,
        f"docs/loom/{CHANGE}/spec.md",
        f"# spec\nintent: {CHANGE}@abc1234\n\n## Requirements\nREQ-1 — a\n"
        "\n## Design decision\n- a\n\n## Alternatives considered\n- a\n"
        "\n## Current state evidence\n- Forward: x\n\n## UI flows\nN/A\n",
    )
    review = {
        "reviewed_sha": "abc1234",
        "scope": "spec",
        "vendors": ["anthropic"],
        "verdicts": [
            {"reviewer": "r1", "vendor": "anthropic", "model": "m", "lens": "spec",
             "verdict": "PASS", "dimension_scores": {}, "findings": [], "round": 1,
             "scope": "spec"},
            {"reviewer": "r2", "vendor": "anthropic", "model": "m", "lens": "docs",
             "verdict": "PASS", "dimension_scores": {}, "findings": [], "round": 1,
             "scope": "spec"},
        ],
        "probes": [
            {"kind": "adversarial", "command": "python3 p.py", "sha": "abc1234",
             "result": "pass", "artifact": "p.py"},
        ],
        "open_findings": [],
        "dispatch": [],
    }
    write(repo, f"docs/loom/{CHANGE}/review.json", json.dumps(review, indent=1))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): spec round")

    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.spec-pass" in blocked_rules(result)
    assert "scope" in result.stderr

    review["probes"][0]["scope"] = "spec"
    write(repo, f"docs/loom/{CHANGE}/review.json", json.dumps(review, indent=1))
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): scope the probe")
    assert run_checker("intake", "write-plan", CHANGE, cwd=repo).returncode == 0
