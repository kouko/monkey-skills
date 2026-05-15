"""Deterministic tests for grade_issue_spot.py.

Fixtures live FLAT in tests/ (not tests/fixtures/) per Anthropic flat-folder
rule. Each test invokes the grader as a subprocess with the canonical
--issues / --business CLI; exit code is the contract.

Test surface:
    1. test_passing_fixture_exits_0           — happy path
    2. test_missing_issues_md_exits_1         — file existence
    3. test_missing_business_md_exits_1       — file existence
    4. test_path_a_antipattern_72hr_exits_1   — bank: 72hr GDPR
    5. test_path_a_antipattern_controller_processor_exits_1 — bank: controller/processor
    6. test_template_orphan_in_issues_md_exits_1     — orphan {{var}} (issues.md)
    7. test_template_orphan_in_business_md_exits_1   — orphan {{var}} (business.md)
    8. test_yellow_in_subsumption_no_handoff_exits_1 — handoff_when_yellow
    9. test_red_risk_no_escalation_exits_1            — escalation_when_red
   10. test_missing_disclaimer_exits_1                — disclaimer_footer
"""
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GRADER = SKILL_DIR / "scripts" / "grade_issue_spot.py"
FIXTURES = Path(__file__).resolve().parent  # FLAT — fixtures live in tests/, not tests/fixtures/

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run_grader(issues_md: Path, business_md: Path) -> int:
    result = subprocess.run(
        [sys.executable, str(GRADER), "--issues", str(issues_md), "--business", str(business_md)],
        env=ENV, capture_output=True, text=True,
    )
    return result.returncode


def test_passing_fixture_exits_0():
    rc = _run_grader(FIXTURES / "fixture-issues-pass.md", FIXTURES / "fixture-business-pass.md")
    assert rc == 0


def test_missing_issues_md_exits_1():
    rc = _run_grader(FIXTURES / "nonexistent.md", FIXTURES / "fixture-business-pass.md")
    assert rc == 1


def test_missing_business_md_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-pass.md", FIXTURES / "nonexistent.md")
    assert rc == 1


def test_path_a_antipattern_72hr_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-72hr-antipattern.md", FIXTURES / "fixture-business-pass.md")
    assert rc == 1


def test_path_a_antipattern_controller_processor_exits_1():
    rc = _run_grader(
        FIXTURES / "fixture-issues-controller-processor-antipattern.md",
        FIXTURES / "fixture-business-pass.md",
    )
    assert rc == 1


def test_template_orphan_in_issues_md_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-orphan-tbd.md", FIXTURES / "fixture-business-pass.md")
    assert rc == 1


def test_template_orphan_in_business_md_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-pass.md", FIXTURES / "fixture-business-orphan-tbd.md")
    assert rc == 1


def test_yellow_in_subsumption_no_handoff_exits_1():
    rc = _run_grader(
        FIXTURES / "fixture-issues-yellow-no-handoff.md",
        FIXTURES / "fixture-business-yellow-no-handoff.md",
    )
    assert rc == 1


def test_red_risk_no_escalation_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-pass.md", FIXTURES / "fixture-business-red-no-escalation.md")
    assert rc == 1


def test_missing_disclaimer_exits_1():
    rc = _run_grader(FIXTURES / "fixture-issues-pass.md", FIXTURES / "fixture-business-no-disclaimer.md")
    assert rc == 1
