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

    # --- the budget's own attribution caveat: only Anthropic documents
    # this cap; OpenAI does not. Structural: bound to the paragraph that
    # follows the "## The 4,000-character budget" heading's first
    # paragraph, so a mutant that drops or inverts the caveat fails here
    # rather than being rescued by unrelated text elsewhere in the file. ---
    budget_section_match = re.search(
        r"## The 4,000-character budget\n\n.*?\n\n(.*?)(?=\n---|\Z)",
        content,
        re.DOTALL,
    )
    assert budget_section_match, "Expected the budget section's second paragraph."
    caveat_para = re.sub(r"\s+", " ", budget_section_match.group(1)).strip().lower()
    assert "openai" in caveat_para and "anthropic" in caveat_para, (
        "The budget section must name both vendors when caveating the cap."
    )
    # Positive-obligation check: OpenAI must be stated as documenting NO
    # length limit — bind "no" to "limit" within the caveat.
    assert re.search(r"\bno\b.*\blimit\b", caveat_para), (
        "Must state OpenAI's guidance documents no length limit — expected "
        "'no ... limit' within the caveat."
    )
    # Bound negation guard: a mutant that drops the "no limit" fact but
    # keeps both vendor names (e.g. claiming OpenAI documents the same
    # cap) must fail — require the caveat to also deny OpenAI documents
    # its own cap.
    assert re.search(r"\bnot\b.*\bopenai\b.*\bdocuments?\b", caveat_para) or (
        re.search(r"\bnot\s+because\s+openai\s+documents\b", caveat_para)
    ), (
        "Must state the cap is applied for portability, NOT because "
        "OpenAI documents one — expected a negation bound to 'OpenAI "
        "documents' within the caveat."
    )

    # --- vendor URLs cited ---
    missing_urls = [url for url in VENDOR_URLS if url not in content]
    assert not missing_urls, f"Missing vendor citation URL(s): {missing_urls}"

    # --- attribution accuracy: positive checks on the actual facts, so that
    # reintroducing false vendor attribution in *different* wording fails
    # too, not just the one hardcoded phrase (see loom-code Rule 9) ---
    paragraphs_lower = [
        re.sub(r"\s+", " ", p).lower() for p in re.split(r"\n\s*\n", content)
    ]

    def _paragraph_containing(*keywords: str):
        for p in paragraphs_lower:
            if all(kw in p for kw in keywords):
                return p
        return None

    # Fact 1: Outcome, Constraints, and Verification are each named by both
    # vendors' guidance. "each" disambiguates this claim from the vendor
    # citation bullets, which merely list the three names without asserting
    # both vendors document them.
    assert _paragraph_containing(
        "outcome", "constraints", "verification", "both vendor", "each"
    ), (
        "Must state that Outcome, Constraints, and Verification are each "
        "named by both vendors' guidance."
    )

    # Fact 2: Stop-when is first-class in OpenAI's guidance.
    assert _paragraph_containing("stop-when", "openai", "first-class"), (
        "Must state that Stop-when is first-class in OpenAI's guidance."
    )

    # Fact 3: Stop-when is only optional/suggested in Anthropic's guidance —
    # not a required field there.
    assert _paragraph_containing(
        "stop-when", "anthropic", "optional"
    ) or _paragraph_containing("stop-when", "anthropic", "suggested"), (
        "Must state that Stop-when is only optional/suggested in Anthropic's "
        "guidance, not a required field there."
    )

    # Fact 4: treating Stop-when as a required fourth field is this skill's
    # own choice, not something either vendor requires.
    assert _paragraph_containing("stop-when", "this skill", "own choice"), (
        "Must attribute Stop-when-as-required-fourth-field to this skill's "
        "own choice, not to either vendor's requirement."
    )

    # --- negative guard: must not claim both vendors require Stop-when as
    # shared/mandatory guidance (kept as a cheap extra tripwire; the facts
    # above are what actually gates this). Matches "require"/"requires"/
    # "mandatory" as whole words only — "required" (as in "not a required
    # field", the real reference's own negation) must not false-trigger it.
    for p in paragraphs_lower:
        if "both" in p and "stop-when" in p and re.search(r"\b(requires?|mandatory)\b", p):
            raise AssertionError(
                "Must not claim both vendors require Stop-when as "
                "shared/mandatory guidance — Stop-when is this skill's own "
                f"addition. Offending paragraph: {p!r}"
            )
    assert "both vendors document four fields" not in content_lower, (
        "Must not claim both vendors document four fields — Stop-when is this "
        "skill's own addition, not shared vendor guidance."
    )
