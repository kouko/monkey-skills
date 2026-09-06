"""Adversarial probes for review-reduction readiness and lane isolation."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
CHECKER = REPO_ROOT / "loom-code/scripts/loom_checker.py"
CHANGE = "2026-09-06-review-reduction-probe"

sys.path.insert(0, str(CHECKER.parent))
_SPEC = importlib.util.spec_from_file_location("review_reduction_checker", CHECKER)
assert _SPEC is not None and _SPEC.loader is not None
loom_checker = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = loom_checker
_SPEC.loader.exec_module(loom_checker)


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "probe@example.com")
    _git(repo, "config", "user.name", "Probe")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-q", "-m", "seed")
    _git(repo, "checkout", "-q", "-b", "work")
    return repo


def _write_intent(repo: Path, *, acceptance_count: int = 2) -> None:
    acceptance = "\n".join(
        f"{number}. Observable outcome {number}."
        for number in range(1, acceptance_count + 1)
    )
    path = repo / f"docs/loom/intent/{CHANGE}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# Review reduction probe
originator: tester
kind: engineering
needs-design: yes — exercises the spec intake contract
status: confirmed 2026-09-06

## Problem
Repeated review delays delivery.

## Proposed outcome
Use the risk-triggered flow.

## Acceptance
{acceptance}

## Constraints
- Keep the closing review.

## Out of scope
- Shipping changes.

## Open questions
- none
""",
        encoding="utf-8",
    )


def _write_spec(repo: Path, declaration: str | None) -> Path:
    declaration_line = f"pre-build-review: {declaration}\n" if declaration else ""
    path = repo / f"docs/loom/{CHANGE}/spec.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# Review reduction probe — spec
intent: {CHANGE}@abc1234
{declaration_line}
## Requirements
REQ-1 — first outcome
  The first outcome is observable. → Acceptance #1
REQ-2 — second outcome
  The second outcome is observable. → Acceptance #2

## Design decision
- agent-decided — Exercise intake.

## Alternatives considered
- Keep the old flow.

## Current state evidence
- Forward: probe fixture.

## UI flows
N/A
""",
        encoding="utf-8",
    )
    return path


def _write_plan(repo: Path, *, cover_second: bool = True) -> None:
    second = "\n" if not cover_second else """

**W0-02 Cover the second outcome**  after: W0-01  acceptance: 2
- Files: `second.txt`
- Test: A2 positive: second-ok; boundary: second-edge.
- Risk: agent-decided — fixture task.
"""
    path = repo / f"docs/loom/{CHANGE}/plan.md"
    path.write_text(
        f"""# Review reduction probe — plan
intent: {CHANGE}@abc1234
spec: docs/loom/{CHANGE}/spec.md@abc1234
charter: 1.0

## Task DAG

**W0-01 Cover the first outcome**  after: —  acceptance: 1
- Files: `first.txt`
- Test: A1 positive: first-ok; negative: first-missing.
- Risk: agent-decided — fixture task.
{second}
## Questions asked
1 — what — none

## Risks
1. Fixture only.
""",
        encoding="utf-8",
    )


def _write_legacy_review(repo: Path, spec: Path) -> None:
    spec_sha = loom_checker.spec_identity(spec)
    verdicts = [
        {
            "reviewer": reviewer,
            "vendor": "anthropic",
            "model": "fixture",
            "lens": "spec",
            "round": 1,
            "verdict": "PASS",
            "spec_sha": spec_sha,
        }
        for reviewer in ("reader-a", "reader-b")
    ]
    path = repo / f"docs/loom/{CHANGE}/review.json"
    path.write_text(
        json.dumps(
            {
                "reviewed_sha": _git(repo, "rev-parse", "HEAD"),
                "scope": "spec",
                "vendors": ["anthropic"],
                "verdicts": verdicts,
                "probes": [
                    {
                        "kind": "adversarial",
                        "scope": "spec",
                        "command": "probe legacy spec",
                        "sha": "abc1234",
                        "result": "pass",
                        "artifact": "evidence/legacy-probe.md",
                    }
                ],
                "open_findings": [],
            }
        ),
        encoding="utf-8",
    )


def _run_intake(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "intake", "write-plan", CHANGE],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def _blocked(result: subprocess.CompletedProcess[str]) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def test_plan_paired_accepted(tmp_path: Path) -> None:
    """A1 positive: a new plan with complete case pairs passes readiness."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    spec = _write_spec(repo, "required — readiness fixture")
    _write_plan(repo)
    _write_legacy_review(repo, spec)

    result = _run_intake(repo)

    assert result.returncode == 0, result.stderr


def test_plan_uncovered_rejected(tmp_path: Path) -> None:
    """A1 negative: omitting ownership of one Acceptance line is refused."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    spec = _write_spec(repo, "required — readiness fixture")
    _write_plan(repo, cover_second=False)
    _write_legacy_review(repo, spec)

    result = _run_intake(repo)

    assert result.returncode == 1
    assert "intake.test-case-pair" in _blocked(result)


def test_spec_lowrisk_accepted(tmp_path: Path) -> None:
    """A2 positive: an explicit low-risk spec proceeds without review.json."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    _write_spec(repo, "not-required — routine internal behavior")
    _write_plan(repo)

    result = _run_intake(repo)

    assert result.returncode == 0, result.stderr


def test_spec_legacy_required(tmp_path: Path) -> None:
    """A2 boundary: a legacy undeclared spec retains the old review floor."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    spec = _write_spec(repo, None)
    _write_plan(repo)
    _write_legacy_review(repo, spec)

    result = _run_intake(repo)

    assert result.returncode == 0, result.stderr


def test_lane_lowrisk_preserved(tmp_path: Path) -> None:
    """A6 positive: pre-build review policy cannot change the closing lane."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    _write_spec(repo, "not-required — routine internal behavior")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/test_probe.py").write_text(
        "def test_probe(): pass\n", encoding="utf-8"
    )
    reviewed_sha = _commit(repo, "test(loom-code): add a test")

    lane, _reason = loom_checker.effective_lane_detail(
        repo, reviewed_sha, CHANGE, 1
    )

    assert lane == "small"


def test_lane_gatepath_full(tmp_path: Path) -> None:
    """A6 boundary: a forcing gate path stays full despite a low-risk spec."""
    repo = _repo(tmp_path)
    _write_intent(repo)
    _write_spec(repo, "not-required — routine internal behavior")
    (repo / "loom-code/scripts").mkdir(parents=True, exist_ok=True)
    (repo / "loom-code/scripts/loom_checker.py").write_text(
        "# forcing gate delta\n", encoding="utf-8"
    )
    reviewed_sha = _commit(repo, "feat(loom-code): touch a gate")

    lane, reason = loom_checker.effective_lane_detail(
        repo, reviewed_sha, CHANGE, 1
    )

    assert lane == "full"
    assert "loom_checker.py" in reason
