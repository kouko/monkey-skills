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

import pytest

CHECKER = Path(__file__).with_name("loom_checker.py")
CHANGE = "2026-09-02-a"
REVIEW = f"docs/loom/{CHANGE}/review.json"
KICKOFF = "docs/loom/KICKOFF-DEFAULTS.md"

# Plain argv: the declared command is executed without a shell, so a
# metacharacter in it is a declaration error, not a command.
DECLARED_TESTS = "python3 -c pass"


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


# --- re-review N1: an argv match, not a substring ---------------------------


def test_an_adversarial_command_naming_its_artifact_only_in_a_comment_blocks(tmp_path) -> None:
    """R3: `python3 noop.py  # attack0.py` mentions the artifact and runs
    something else entirely. A substring test cannot tell those apart."""
    repo = build_repo(tmp_path)
    write(repo, "evidence/noop.py", "raise SystemExit(0)\n")
    body = rebuild(repo)
    for n, probe in enumerate(p for p in body["probes"] if p["kind"] == "adversarial"):
        probe["command"] = f"python3 evidence/noop.py  # evidence/abuse_{n}.py"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "argument" in result.stderr


def test_a_dot_slash_prefixed_artifact_argument_is_accepted(tmp_path) -> None:
    """`./evidence/abuse_0.py` names the same file; normalising is not
    loosening."""
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for n, probe in enumerate(p for p in body["probes"] if p["kind"] == "adversarial"):
        probe["command"] = f"python3 ./evidence/abuse_{n}.py"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert "push.probes-adversarial" not in blocked_rules(result), result.stderr


def test_an_unparseable_adversarial_command_blocks(tmp_path) -> None:
    repo = build_repo(tmp_path)
    body = rebuild(repo)
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["command"] = 'python3 "evidence/abuse_0.py'
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


# --- re-review N2: a detected command that fails says what to declare ------


def test_a_failing_detected_command_asks_for_a_kickoff_declaration(tmp_path) -> None:
    repo = build_repo(tmp_path, kickoff="# Kickoff Defaults\n")
    write(repo, "pyproject.toml", "[project]\nname = 'x'\n")
    write(repo, "test_red.py", "def test_red():\n    assert False\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: suite\n\nTask: T1")
    body = review_body(git(repo, "rev-parse", "HEAD"))
    body["probes"][0]["command"] = "python3 -m pytest -q"
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "declare `package-tests:` in" in result.stderr


# --- re-review N3: a task line may carry a list bullet ---------------------


def test_a_bullet_prefixed_after_task_line_is_still_counted(tmp_path: Path) -> None:
    repo = _intake_repo(
        tmp_path,
        "**W1-01 first** after: none review: after-task\n"
        "**W1-02 second** after: W1-01 review: after-task\n"
        "- **W1-03 third** after: W1-02 review: after-task\n"
        "* **W1-04 fourth** after: W1-03 review: after-task\n",
    )
    result = run_checker("intake", "write-plan", CHANGE, cwd=repo)
    assert result.returncode == 1
    assert "intake.after-task-budget" in blocked_rules(result)
    assert "W1-03" in result.stderr and "W1-04" in result.stderr


# --- re-review N4: `fallback` has a grammar --------------------------------


SECOND_VENDOR_KICKOFF = (
    "# Kickoff Defaults\n\n"
    f"- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n"
    "- second-vendor: codex — cross-vendor review (2026-09-02)\n"
)


def test_a_fallback_that_is_not_the_declared_grammar_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, kickoff=SECOND_VENDOR_KICKOFF)
    body = rebuild(repo)
    body["verdicts"][0]["fallback"] = "n/a"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)
    assert "codex missing at" in result.stderr


def test_a_fallback_naming_another_cli_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, kickoff=SECOND_VENDOR_KICKOFF)
    body = rebuild(repo)
    body["verdicts"][0]["fallback"] = "gemini missing at 2026-09-02"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


# --- re-review N5: no Task: trailer at all on a code branch ----------------


def _no_trailer_repo(tmp_path: Path, *, path: str, body: str) -> Path:
    repo = tmp_path / "notrailer"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, "seed.txt", "seed\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    write(repo, path, body)
    write(repo, "evidence/tests.txt", "ok\n")
    for n in range(3):
        write(repo, f"evidence/abuse_{n}.py", "raise SystemExit(0)\n")
    write(
        repo,
        KICKOFF,
        f"# Kickoff Defaults\n\n- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: no trailer here")
    reviewed = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(reviewed))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return repo


def test_a_code_branch_with_no_task_trailer_at_all_blocks(tmp_path: Path) -> None:
    repo = _no_trailer_repo(tmp_path, path="a.py", body="value = 1\n")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    assert "code" in result.stderr


def test_a_docs_only_branch_with_no_task_trailer_is_exempt(tmp_path: Path) -> None:
    repo = _no_trailer_repo(tmp_path, path="notes.md", body="prose\n")
    result = run_checker("push", cwd=repo)
    assert "push.dispatch-covers-tasks" not in blocked_rules(result), result.stderr


# --- round-3 F1: the checker runs the artifact, never a recorded string ----


def _masking(repo: Path, suffix: str) -> None:
    """Make every abuse case fail, and mask it in the recorded command."""
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    for n in range(3):
        write(repo, f"evidence/abuse_{n}.py", "raise SystemExit(1)\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--amend", "--no-edit")
    reviewed = git(repo, "rev-parse", "HEAD")
    body = review_body(reviewed)
    for n, probe in enumerate(p for p in body["probes"] if p["kind"] == "adversarial"):
        probe["command"] = f"python3 evidence/abuse_{n}.py{suffix}"
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


@pytest.mark.parametrize(
    "suffix", [" ; true", " || true", " && true", " > /dev/null || true"]
)
def test_a_shell_suffix_cannot_mask_a_failing_abuse_case(tmp_path: Path, suffix) -> None:
    """The recorded string is a record; the exit code of a shell pipeline it
    describes is not evidence about the artifact. The checker runs the file."""
    repo = build_repo(tmp_path)
    _masking(repo, suffix)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)


def test_a_passing_artifact_still_passes(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    result = run_checker("push", cwd=repo)
    assert "push.probes-adversarial" not in blocked_rules(result), result.stderr
    assert "evidence/abuse_0.py" in result.stdout


def test_an_artifact_with_no_runnable_form_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    write(repo, "evidence/abuse_note.txt", "an abuse case, allegedly\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--amend", "--no-edit")
    body = review_body(git(repo, "rev-parse", "HEAD"))
    for probe in body["probes"]:
        if probe["kind"] == "adversarial":
            probe["artifact"] = "evidence/abuse_note.txt"
            probe["command"] = "python3 evidence/abuse_note.txt"
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "not runnable" in result.stderr


def test_a_shell_script_artifact_runs_under_bash(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    write(repo, "evidence/abuse_0.sh", "exit 0\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--amend", "--no-edit")
    body = review_body(git(repo, "rev-parse", "HEAD"))
    first = next(p for p in body["probes"] if p["kind"] == "adversarial")
    first["artifact"] = "evidence/abuse_0.sh"
    first["command"] = "bash evidence/abuse_0.sh"
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert "push.probes-adversarial" not in blocked_rules(result), result.stderr


def test_a_declared_command_with_shell_metacharacters_blocks(tmp_path: Path) -> None:
    repo = build_repo(
        tmp_path,
        kickoff=(
            "# Kickoff Defaults\n\n"
            "- package-tests: python3 -m pytest -q || true — masked (2026-09-02)\n"
        ),
    )
    body = rebuild(repo)
    body["probes"][0]["command"] = "python3 -m pytest -q || true"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "plain argv command" in result.stderr


def test_a_recorded_command_with_a_quoted_hash_is_read_as_one_token(tmp_path: Path) -> None:
    """F4: `shlex.split(..., comments=True)` must not treat a quoted `#` as
    the start of a comment."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("lc", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    import sys as _sys

    _sys.path.insert(0, str(CHECKER.parent))
    spec.loader.exec_module(checker)
    assert checker.command_names_artifact('python3 "ev/a#b.py"', "ev/a#b.py")
    assert not checker.command_names_artifact("python3 noop.py  # ev/a.py", "ev/a.py")


# --- round-3 F2: a Task trailer per code-bearing commit --------------------


def test_a_code_commit_without_its_own_trailer_blocks(tmp_path: Path) -> None:
    """X2: the trailer sat on a docs commit while the code commit had none."""
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    write(repo, "b.py", "value = 2\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: b with no trailer")
    # loom_checker.py reports the offending sha truncated to 8 hex chars.
    untrailered_sha = git(repo, "rev-parse", "HEAD")[:8]
    write(repo, "notes.md", "prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: notes\n\nTask: T1")
    reviewed = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(reviewed))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.dispatch-covers-tasks" in blocked_rules(result)
    # The offending commit -- the trailerless "feat: b" -- must be named,
    # not just any commit mentioning a trailer in general.
    assert untrailered_sha in result.stderr


def test_a_docs_only_commit_needs_no_trailer(tmp_path: Path) -> None:
    repo = build_repo(tmp_path)
    git(repo, "reset", "-q", "--hard", "HEAD~1")
    write(repo, "notes.md", "prose\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: notes with no trailer at all")
    reviewed = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(reviewed))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    result = run_checker("push", cwd=repo)
    assert "push.dispatch-covers-tasks" not in blocked_rules(result), result.stderr


# --- round-3 F3: the fallback grammar is a fullmatch ----------------------


def test_a_fallback_with_trailing_junk_blocks(tmp_path: Path) -> None:
    repo = build_repo(tmp_path, kickoff=SECOND_VENDOR_KICKOFF)
    body = rebuild(repo)
    body["verdicts"][0]["fallback"] = "codex missing at 2026-09-02 (but really it was there)"
    recommit_review(repo, body)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert "push.second-vendor-honoured" in blocked_rules(result)


# --- round-4 #5: both TimeoutExpired branches ------------------------------
#
# `PROBE_RUN_TIMEOUT` reads `LOOM_PROBE_RUN_TIMEOUT` (loom_checker.py) so a
# test can force the timeout in seconds instead of waiting on the real
# 10-minute default. `run_checker` spawns a subprocess without an explicit
# `env=`, so it inherits the current process environment — the one
# `monkeypatch.setenv` edits — and the checker under test reads the
# monkeypatched value at startup.


def init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    write(repo, "seed.txt", "seed\n")
    git(repo, "add", "seed.txt")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def test_a_hung_package_tests_command_times_out_and_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = init_repo(tmp_path)
    write(repo, "a.py", "value = 1\n")
    write(repo, "evidence/hang.py", "import time\ntime.sleep(3)\n")
    for n in range(3):
        write(repo, f"evidence/abuse_{n}.py", "raise SystemExit(0)\n")
    write(
        repo, KICKOFF,
        "# Kickoff Defaults\n\n"
        "- package-tests: python3 evidence/hang.py — fixture (2026-09-02)\n",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")
    sha = git(repo, "rev-parse", "HEAD")

    body = review_body(sha)
    body["probes"][0] = {
        "kind": "package-tests", "command": "python3 evidence/hang.py",
        "sha": sha, "result": "pass", "artifact": "evidence/hang.py",
    }
    write_review(repo, body)
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    monkeypatch.setenv("LOOM_PROBE_RUN_TIMEOUT", "1")
    result = run_checker("push", cwd=repo)

    assert result.returncode == 1
    assert "push.probes-package-tests" in blocked_rules(result)
    assert "did not finish within 1s" in result.stderr


def test_a_hung_adversarial_probe_times_out_and_blocks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = init_repo(tmp_path)
    write(repo, "a.py", "value = 1\n")
    write(repo, "evidence/tests.txt", "2199 passed\n")
    for n in range(3):
        write(repo, f"evidence/abuse_{n}.py", "import time\ntime.sleep(3)\n")
    write(
        repo, KICKOFF,
        f"# Kickoff Defaults\n\n- package-tests: {DECLARED_TESTS} — fixture (2026-09-02)\n",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat: a\n\nTask: T1")
    sha = git(repo, "rev-parse", "HEAD")

    write_review(repo, review_body(sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")

    monkeypatch.setenv("LOOM_PROBE_RUN_TIMEOUT", "1")
    result = run_checker("push", cwd=repo)

    assert result.returncode == 1
    assert "push.probes-adversarial" in blocked_rules(result)
    assert "did not finish within 1s" in result.stderr
