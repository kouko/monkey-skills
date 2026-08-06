"""Prose-pin test for Task 1 (plan-format progress headers + default-on ledger).

Pins the two new header-schema lines (`Goal:` / `Stage:` enum) added to
plan-format.md's top-level header block, and the §Progress ledger
default-on flip: writing-plans now emits `Status: pending` per task at
plan time, while a plan without `Status` fields (written before the
default) behaves exactly as before. Matching is whitespace-normalized
contiguous (helper shape from test_dispatch_hygiene_worktree_section.py).
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_FORMAT_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-format.md"
)

GOAL_SCHEMA_LINE = (
    "Goal: <one sentence transcribed from the brief's Smallest End State at "
    "plan time — frozen with the plan; never edited afterward>"
)

STAGE_ENUM_LINE = (
    "Stage: <planning | sdd:wave-N | review:round-N | finishing — updated by "
    "the orchestrator at each transition, committed with the nearest "
    "ledger or close-out commit>"
)

DEFAULT_ON_SENTENCE = (
    "The ledger is DEFAULT-ON: writing-plans emits `Status: pending` on "
    "every task at plan time."
)

OLD_PLAN_COMPAT_SENTENCE = (
    "A plan without `Status` fields (written "
    "before this default) behaves exactly as before — the ledger stays "
    "opt-in-by-presence for old plans."
)


def _normalized_text() -> str:
    """Whitespace-normalized plan-format.md text (collapses hard wraps so
    a contiguous-phrase match doesn't depend on line breaks)."""
    text = PLAN_FORMAT_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def _normalize(phrase: str) -> str:
    return " ".join(phrase.split())


def test_progress_ledger_heading_present():
    """Positive-fact control: the pre-existing §Progress ledger heading is
    present — proves the pin tests below are not vacuous (the file is
    actually being read/matched, not a stub)."""
    assert "#### Progress ledger — the `Status` field" in _normalized_text()


def test_goal_schema_line_present():
    """Task 1(a): the `Goal:` header schema line (N1, verbatim) exists."""
    assert _normalize(GOAL_SCHEMA_LINE) in _normalized_text()


def test_stage_enum_line_present():
    """Task 1(a): the `Stage:` enum header schema line (N1, verbatim)
    exists, carrying the four-value enum
    planning / sdd:wave-N / review:round-N / finishing."""
    assert _normalize(STAGE_ENUM_LINE) in _normalized_text()


def test_status_ledger_default_on_sentence_present():
    """Task 1(b): §Progress ledger carries the default-on sentence (N1b) —
    writing-plans emits `Status: pending` on every task at plan time."""
    assert _normalize(DEFAULT_ON_SENTENCE) in _normalized_text()


def test_old_plan_compatibility_sentence_present():
    """Task 1(b): §Progress ledger carries the old-plan compatibility
    sentence (N1b) — a plan without `Status` fields behaves as before."""
    assert _normalize(OLD_PLAN_COMPAT_SENTENCE) in _normalized_text()
