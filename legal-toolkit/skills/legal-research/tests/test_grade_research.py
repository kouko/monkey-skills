"""Deterministic tests for grade_research.py.

Fixtures live FLAT in tests/ (not tests/fixtures/) per Anthropic flat-folder
rule. Each test invokes the grader as a subprocess with the canonical
--plan / --state / --memo / --summary CLI; exit code is the contract.

Test surface (16):
     1. test_passing_fixture_exits_0                — happy path; 9 sources, 4 types, early_stop
     2. test_missing_plan_exits_1                   — file existence: plan
     3. test_missing_state_exits_1                  — file existence: state
     4. test_missing_memo_exits_1                   — file existence: memo
     5. test_missing_summary_exits_1                — file existence: summary
     6. test_state_over_cap_exits_1                 — rounds=6 (> MAX_ROUNDS=5)
     7. test_state_inconsistent_no_warn_exits_1     — forced_stop=true + memo no ⚠️
     8. test_state_forced_stop_with_warn_exits_2    — forced_stop=true + memo ⚠️ + §Escalation → PASS_WITH_NOTES
     9. test_memo_7_citations_no_warn_exits_1       — 7 citations + no ⚠️
    10. test_memo_single_type_exits_1               — 8 citations + 1 type only + no ⚠️
    11. test_memo_no_relevance_exits_1              — citation missing `→ <relevance>`
    12. test_memo_72hr_antipattern_exits_1          — Path A bank: 72hr GDPR
    13. test_memo_orphan_tbd_exits_1                — orphan {{tbd_section_x}}
    14. test_summary_no_disclaimer_exits_1          — §Disclaimer missing
    15. test_summary_no_conclusion_marker_exits_1   — ✅/⚠️/❌ missing from §結論
    16. test_escalation_missing_when_forced_stop_exits_1 — forced_stop=true + summary no §Escalation → exit 1
"""
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
GRADER = SKILL_DIR / "scripts" / "grade_research.py"
FIXTURES = Path(__file__).resolve().parent  # FLAT — fixtures live in tests/, not tests/fixtures/

ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


def _run_grader(plan: Path, state: Path, memo: Path, summary: Path) -> int:
    result = subprocess.run(
        [
            sys.executable, str(GRADER),
            "--plan", str(plan),
            "--state", str(state),
            "--memo", str(memo),
            "--summary", str(summary),
        ],
        env=ENV, capture_output=True, text=True,
    )
    return result.returncode


# Fixture shortcuts (resolved once at module import).
PLAN_PASS = FIXTURES / "fixture-plan-pass.md"
STATE_PASS = FIXTURES / "fixture-state-pass.json"
MEMO_PASS = FIXTURES / "fixture-memo-pass.md"
SUMMARY_PASS = FIXTURES / "fixture-summary-pass.md"


# ---------------------------------------------------------- Test 1 — happy path
def test_passing_fixture_exits_0():
    rc = _run_grader(PLAN_PASS, STATE_PASS, MEMO_PASS, SUMMARY_PASS)
    assert rc == 0


# ---------------------------------------------------------- Tests 2-5 — existence
def test_missing_plan_exits_1():
    rc = _run_grader(FIXTURES / "nonexistent-plan.md", STATE_PASS, MEMO_PASS, SUMMARY_PASS)
    assert rc == 1


def test_missing_state_exits_1():
    rc = _run_grader(PLAN_PASS, FIXTURES / "nonexistent-state.json", MEMO_PASS, SUMMARY_PASS)
    assert rc == 1


def test_missing_memo_exits_1():
    rc = _run_grader(PLAN_PASS, STATE_PASS, FIXTURES / "nonexistent-memo.md", SUMMARY_PASS)
    assert rc == 1


def test_missing_summary_exits_1():
    rc = _run_grader(PLAN_PASS, STATE_PASS, MEMO_PASS, FIXTURES / "nonexistent-summary.md")
    assert rc == 1


# ---------------------------------------------------------- Tests 6-8 — state integrity
def test_state_over_cap_exits_1():
    """rounds=6 (> MAX_ROUNDS=5) MUST trigger state_within_cap fail."""
    rc = _run_grader(
        PLAN_PASS,
        FIXTURES / "fixture-state-over-cap.json",
        MEMO_PASS,
        SUMMARY_PASS,
    )
    assert rc == 1


def test_state_inconsistent_no_warn_exits_1():
    """forced_stop=true + memo has NO ⚠️ block → state_consistency fail."""
    rc = _run_grader(
        PLAN_PASS,
        FIXTURES / "fixture-state-inconsistent.json",
        MEMO_PASS,
        SUMMARY_PASS,
    )
    assert rc == 1


def test_state_forced_stop_with_warn_exits_2():
    """forced_stop=true + memo HAS ⚠️ block + 7 citations + §Escalation → PASS_WITH_NOTES (exit 2).

    Per spec §6.6: forced_stop with a properly-surfaced ⚠️ block is the
    acceptable degraded path; sources < 8 floor is excused by the ⚠️ block
    via citation_count_or_warn. §Escalation is also required (check #16).
    """
    rc = _run_grader(
        PLAN_PASS,
        FIXTURES / "fixture-state-inconsistent.json",
        FIXTURES / "fixture-memo-7-citations-with-warn.md",
        FIXTURES / "fixture-summary-forced-stop.md",
    )
    assert rc == 2


# ---------------------------------------------------------- Tests 9-11 — citations
def test_memo_7_citations_no_warn_exits_1():
    """7 citations + no ⚠️ block → citation_count_or_warn fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        FIXTURES / "fixture-memo-7-citations-no-warn.md",
        SUMMARY_PASS,
    )
    assert rc == 1


def test_memo_single_type_exits_1():
    """8 citations + 1 type only + no ⚠️ → source_type_coverage fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        FIXTURES / "fixture-memo-single-type.md",
        SUMMARY_PASS,
    )
    assert rc == 1


def test_memo_no_relevance_exits_1():
    """A citation missing `→ <relevance>` continuation → citation_has_relevance fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        FIXTURES / "fixture-memo-no-relevance.md",
        SUMMARY_PASS,
    )
    assert rc == 1


# ---------------------------------------------------------- Tests 12-13 — safety bank
def test_memo_72hr_antipattern_exits_1():
    """`72 hours` string in memo → Path A bank fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        FIXTURES / "fixture-memo-72hr-antipattern.md",
        SUMMARY_PASS,
    )
    assert rc == 1


def test_memo_orphan_tbd_exits_1():
    """`{{tbd_section_x}}` orphan in memo → template_orphan_check fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        FIXTURES / "fixture-memo-orphan-tbd.md",
        SUMMARY_PASS,
    )
    assert rc == 1


# ---------------------------------------------------------- Tests 14-15 — summary
def test_summary_no_disclaimer_exits_1():
    """summary.md missing §Disclaimer → disclaimer_footer fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        MEMO_PASS,
        FIXTURES / "fixture-summary-no-disclaimer.md",
    )
    assert rc == 1


def test_summary_no_conclusion_marker_exits_1():
    """summary.md §結論 missing ✅/⚠️/❌ → conclusion_marker_required fail."""
    rc = _run_grader(
        PLAN_PASS,
        STATE_PASS,
        MEMO_PASS,
        FIXTURES / "fixture-summary-no-conclusion-marker.md",
    )
    assert rc == 1


# ---------------------------------------------------------- Test 16 — escalation
def test_escalation_missing_when_forced_stop_exits_1():
    """forced_stop=true + summary has NO §Escalation → escalation_when_forced_stop fail."""
    rc = _run_grader(
        PLAN_PASS,
        FIXTURES / "fixture-state-inconsistent.json",
        FIXTURES / "fixture-memo-7-citations-with-warn.md",
        SUMMARY_PASS,
    )
    assert rc == 1
