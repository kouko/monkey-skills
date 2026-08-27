"""
Structural tests for goal-shape.md reference.

Tests verify:
- The four field names appear, in order: Outcome, Constraints, Verification, Stop-when
- Outcome is defined as one measurable end state, not a vision
- Constraints is defined as what must not change
- Verification requires a check AND requires that check's output be surfaced in
  the conversation, with the reason stated (goal evaluator reads only the
  conversation — no commands run, no files opened)
- Stop-when bounds the run (a turn-clause example)
- The 4,000-character budget is stated
- The file-pointer rule for goals that exceed the budget is stated
- Both vendor URLs are cited
- Attribution is accurate: Stop-when is not claimed as a shared four-field
  vendor standard

WHY: This reference is the SSOT for the four-field goal shape that the rest of
`loom-workflow:goal-create` routes to. Any drift in field names, the budget
number, or the surfacing requirement silently breaks every downstream skill
section that assumes this contract.
"""

import re
from pathlib import Path

REFERENCE_PATH = (
    Path(__file__).parent.parent / "references" / "goal-shape.md"
)

FIELD_NAMES_IN_ORDER = ["Outcome", "Constraints", "Verification", "Stop-when"]

VENDOR_URLS = [
    "https://code.claude.com/docs/en/goal",
    "https://learn.chatgpt.com/use-cases/follow-goals",
    "https://learn.chatgpt.com/docs/long-running-work",
]


def _read_reference() -> str:
    """Read the reference file; fail with a descriptive message if missing."""
    assert REFERENCE_PATH.exists(), (
        f"Reference file not found: {REFERENCE_PATH}\n"
        "This is expected at RED stage. Create the reference to make this test pass."
    )
    return REFERENCE_PATH.read_text(encoding="utf-8")


def test_defines_four_fields_budget_and_surfacing() -> None:
    content = _read_reference()
    content_lower = content.lower()

    # --- four field names present, in order ---
    last_index = -1
    for field in FIELD_NAMES_IN_ORDER:
        idx = content.find(field)
        assert idx != -1, f"Field name '{field}' not found in reference."
        assert idx > last_index, (
            f"Field '{field}' must appear after the previous field — "
            "expected order: Outcome, Constraints, Verification, Stop-when."
        )
        last_index = idx

    # --- Outcome: one measurable end state, not a vision ---
    assert "measurable" in content_lower, (
        "Outcome must be defined as one measurable end state."
    )
    assert "vision" in content_lower, (
        "Outcome must explicitly contrast with a vision (not a vision)."
    )

    # --- Constraints: what must not change ---
    assert "must not change" in content_lower, (
        "Constraints must state what must not change on the way to the outcome."
    )

    # --- Verification: names a check AND requires surfacing ---
    assert "surfaced in the conversation" in content_lower or (
        "surfaced" in content_lower and "conversation" in content_lower
    ), "Verification must require that the check's output be surfaced in the conversation."
    assert "goal evaluator" in content_lower, (
        "Verification's surfacing rule must name Claude Code's goal evaluator."
    )
    assert "no commands" in content_lower or "runs no commands" in content_lower, (
        "Verification's rationale must state the evaluator runs no commands."
    )
    assert "no files" in content_lower or "opens no files" in content_lower, (
        "Verification's rationale must state the evaluator opens no files."
    )

    # --- Stop-when: bounds the run, e.g. a turn clause ---
    assert "turn" in content_lower, (
        "Stop-when must give a turn-clause example bounding the run."
    )

    # --- 4,000-character budget ---
    assert "4,000" in content or "4000" in content, (
        "The 4,000-character budget must be stated."
    )
    assert "character" in content_lower, (
        "The budget must be stated in characters."
    )

    # --- file-pointer rule for goals exceeding the budget ---
    assert re.search(r"points? (at|to) a file", content_lower), (
        "A goal exceeding the budget must point at a file rather than inlining detail."
    )

    # --- vendor URLs cited ---
    missing_urls = [url for url in VENDOR_URLS if url not in content]
    assert not missing_urls, f"Missing vendor citation URL(s): {missing_urls}"

    # --- attribution accuracy: do not claim both vendors document four fields ---
    assert "both vendors document four fields" not in content_lower, (
        "Must not claim both vendors document four fields — Stop-when is this "
        "skill's own addition, not shared vendor guidance."
    )
    assert "this skill" in content_lower, (
        "Must attribute Stop-when-as-required-field as this skill's own choice."
    )
