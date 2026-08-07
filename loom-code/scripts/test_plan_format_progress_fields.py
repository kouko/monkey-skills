"""Prose-pin test for Task 1 (plan-format progress headers + default-on ledger).

Pins the two new header-schema lines (`Goal:` / `Stage:` enum) added to
plan-format.md's top-level header block, and the §Progress ledger
default-on flip: writing-plans now emits `Status: pending` per task at
plan time, while a plan without `Status` fields (written before the
default) behaves exactly as before. Matching is whitespace-normalized
contiguous (helper shape from test_dispatch_hygiene_worktree_section.py).

Also pins the roadmap-view additions (plan 2026-08-06 Task 2): the
optional `Steps:` header block (N3a), the per-task `Gloss:` schema line
(N3b) with its never-a-name-restatement contract, the worked example
carrying a `Steps:` block plus bold `- **Gloss**:` lines, and the
plan-document-reviewer prompt's non-gating Gloss-contract sentence.
Schema pins are whitespace-normalized sentence pins, NOT `- Gloss:`
literal counts (the example uses the bold style `- **Gloss**:`).
"""

import subprocess
import sys
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
REVIEWER_PROMPT_MD = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)
PLAN_CARD_SCRIPT = REPO_ROOT / "scripts" / "plan_card.py"
WP_SKILL_MD = (
    REPO_ROOT / "loom-code" / "skills" / "writing-plans" / "SKILL.md"
)

GOAL_SCHEMA_LINE = (
    "Goal: <one sentence transcribed from the brief's Smallest End State at "
    "plan time — frozen with the plan (wrap continuation lines WITH "
    "indentation — unindented wraps silently truncate the rendered goal); "
    "never edited afterward>"
)

STAGE_ENUM_LINE = (
    "Stage: <planning | sdd:wave-N | review:round-N | blocked:user-decision "
    "| finishing — updated by the orchestrator at each transition, "
    "committed with the nearest ledger or close-out commit>"
)

BLOCKED_DUTY_SENTENCE = (
    "blocked:user-decision marks an arc halted awaiting a user ruling: set "
    "it when the orchestrator stops mid-arc to wait for a user decision "
    "(an open finding, a deferred choice), and on resume flip Stage to "
    "the stage the ruling re-enters."
)

SKILL_MD_ENUM_FRAGMENT = (
    "enum planning | sdd:wave-N | review:round-N | blocked:user-decision |"
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

STEPS_SCHEMA_BLOCK = (
    "Steps: <OPTIONAL numbered block, one line per derived dependency "
    "level, titles in the user's conversation language; when present "
    "the count must equal the plan's dependency-level count — "
    "plan_card.py exits 1 loud on mismatch>"
)

GLOSS_SCHEMA_LEAD = (
    "- **Gloss**: <one line in the user's conversation language stating "
    "the task's user-visible effect and why it matters to the goal"
)

GLOSS_NEVER_RESTATEMENT_SENTENCE = (
    "NEVER a restatement of the task name; rendered under the task row "
    "by plan_card.py; emitted by writing-plans for new plans, optional "
    "on old ones>"
)

REVIEWER_GLOSS_CONTRACT_SENTENCE = (
    "Gloss lines, when present, state effect + goal relation in the "
    "user's conversation language — accept and read, never require"
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
    exists, carrying the five-value enum
    planning / sdd:wave-N / review:round-N / blocked:user-decision /
    finishing."""
    assert _normalize(STAGE_ENUM_LINE) in _normalized_text()


def test_blocked_duty_sentence_present():
    """Plan 2026-08-07 Task 1: the blocked:user-decision when-to-set duty
    sentence exists as its own sentence (sibling prose OUTSIDE the header
    template block, so a plan copier never inherits rule text)."""
    assert _normalize(BLOCKED_DUTY_SENTENCE) in _normalized_text()


def _normalized_skill_md_text() -> str:
    """Whitespace-normalized writing-plans SKILL.md text (same collapse
    as _normalized_text, but for the SKILL.md schema-block copy)."""
    text = WP_SKILL_MD.read_text(encoding="utf-8")
    return " ".join(text.split())


def test_skill_md_enum_line_matches():
    """Plan 2026-08-07 Task 2: writing-plans SKILL.md's schema-block
    enum line carries the same five-value Stage enum as plan-format.md —
    the extended fragment including blocked:user-decision."""
    assert _normalize(SKILL_MD_ENUM_FRAGMENT) in _normalized_skill_md_text()


def test_status_ledger_default_on_sentence_present():
    """Task 1(b): §Progress ledger carries the default-on sentence (N1b) —
    writing-plans emits `Status: pending` on every task at plan time."""
    assert _normalize(DEFAULT_ON_SENTENCE) in _normalized_text()


def test_old_plan_compatibility_sentence_present():
    """Task 1(b): §Progress ledger carries the old-plan compatibility
    sentence (N1b) — a plan without `Status` fields behaves as before."""
    assert _normalize(OLD_PLAN_COMPAT_SENTENCE) in _normalized_text()


def _worked_example_text() -> str:
    """The canonical CSV worked-example section of plan-format.md —
    everything between the `## Worked example` heading and the next
    `### ` heading (the wide-but-shallow example). Raw text, NOT
    whitespace-normalized, so per-line bold-Gloss counting works."""
    text = PLAN_FORMAT_MD.read_text(encoding="utf-8")
    start = text.index("## Worked example")
    end = text.index("### Wide-but-shallow example", start)
    return text[start:end]


def test_steps_header_schema_block_present():
    """Task 2(a): the header schema carries the optional `Steps:` block
    (N3a, verbatim) — one line per derived dependency level, count must
    equal the plan's dependency-level count."""
    assert _normalize(STEPS_SCHEMA_BLOCK) in _normalized_text()


def test_gloss_per_task_schema_lead_present():
    """Task 2(b): the per-task schema carries the `- **Gloss**:` line
    (N3b lead) — one line in the user's conversation language stating
    effect + goal relation."""
    assert _normalize(GLOSS_SCHEMA_LEAD) in _normalized_text()


def test_gloss_never_restatement_contract_present():
    """Task 2(b): N3b's contract sentence — a Gloss is NEVER a
    restatement of the task name; rendered by plan_card.py; emitted by
    writing-plans for new plans, optional on old ones."""
    assert _normalize(GLOSS_NEVER_RESTATEMENT_SENTENCE) in _normalized_text()


def test_worked_example_carries_steps_block():
    """Task 2(c): the canonical CSV worked example declares a `Steps:`
    header block (English titles — the example's own language)."""
    assert "\nSteps:\n" in _worked_example_text()


def test_worked_example_carries_bold_gloss_lines():
    """Task 2(c): the canonical CSV worked example carries ≥3 bold
    `- **Gloss**:` lines — one per task, consistent with its siblings'
    bold field style."""
    count = _worked_example_text().count("- **Gloss**:")
    assert count >= 3, f"expected >=3 bold Gloss lines in example, found {count}"


def test_reviewer_prompt_gloss_contract_sentence_present():
    """Task 2(d): plan-document-reviewer-prompt.md carries the
    non-gating Gloss-contract sentence near its Status-field rule —
    accept and read, never require."""
    text = " ".join(REVIEWER_PROMPT_MD.read_text(encoding="utf-8").split())
    assert _normalize(REVIEWER_GLOSS_CONTRACT_SENTENCE) in text


def _canonical_worked_example_plan_text() -> str:
    """The fenced ```markdown plan body inside the canonical CSV-export
    worked example (NOT the wide-but-shallow example) — the literal
    plan text a reader would copy and run plan_card.py against."""
    section = _worked_example_text()
    fence_start = section.index("```markdown") + len("```markdown")
    fence_end = section.index("```", fence_start)
    return section[fence_start:fence_end].strip("\n") + "\n"


def test_canonical_worked_example_renders_with_plan_card(tmp_path):
    """Integration guard (F1): the canonical worked example must be a
    RUNNABLE plan, not just prose — extract its fenced plan body to a
    tmp file and run the real plan_card.py on it. Before the fix, Task
    2's `- **Dependencies**: none (parallel with Task 1)` value falls
    outside plan_card.py's Dependencies grammar and plan_card.py exits
    1; after the one-word fix it renders the two-step roadmap card."""
    plan_text = _canonical_worked_example_plan_text()
    plan_path = tmp_path / "worked-example-plan.md"
    plan_path.write_text(plan_text, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(PLAN_CARD_SCRIPT), str(plan_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        "-- step 1: Understand the CSV request and produce the file format --"
        in result.stdout
    ), result.stdout
    assert (
        "-- step 2: Connect them so the download actually happens "
        "(needs: T1 T2) --" in result.stdout
    ), result.stdout
