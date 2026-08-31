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

    # Fact 1: which of the three field names each vendor actually uses.
    # OpenAI's long-running-work names all three; Anthropic's page names only
    # `Constraints`, and calls the other two "One measurable end state" and
    # "A stated check".
    #
    # Pinned on the EVIDENCE — Anthropic's own three bullet labels — rather
    # than on the author's connective vocabulary. Those quotes are what makes
    # the attribution checkable by a reader, so any honest rewrite keeps them,
    # while "describes" / "labels" / "only OpenAI" are interchangeable
    # phrasings a copy-edit may legitimately replace. An earlier version of
    # this pin required those connectives and two reviewers each wrote a
    # faithful paraphrase that failed it.
    #
    # Bound, stated: this catches the paragraph claiming all three names are
    # shared, and it catches the quotes going missing. It does NOT catch the
    # opposite overclaim -- denying Anthropic the one label it does use --
    # because no substring distinguishes that from a correct sentence. What
    # guards that direction is the quotes sitting in the same paragraph,
    # where a reader meets "Constraints that matter" next to any claim about
    # Anthropic not using these words. That is a human guard, not a
    # mechanical one, and this comment is the honest statement of it.
    # Selected by the paragraph's own bold lead label, never by keyword
    # soup: the vendor citation bullets are a single paragraph that already
    # contains every vendor name, every field name, and every quote below,
    # so a keyword selector silently binds there instead and every assertion
    # that follows passes against the wrong text. That is not hypothetical --
    # an earlier revision of this block did exactly that and survived two
    # mutations that should have killed it.
    attribution = next(
        (p for p in paragraphs_lower if p.startswith("**attribution accuracy**")),
        None,
    )
    assert attribution, (
        "Must carry a paragraph led by **Attribution accuracy** stating "
        "which of the three field names each vendor actually uses."
    )
    for field in ("outcome", "constraints", "verification"):
        assert field in attribution, (
            f"The attribution paragraph must name {field!r}."
        )
    for vendor in ("anthropic", "openai"):
        assert vendor in attribution, (
            f"The attribution paragraph must name {vendor!r}."
        )
    for anthropic_label in (
        "one measurable end state",
        "a stated check",
        "constraints that matter",
    ):
        assert anthropic_label in attribution, (
            f"Must quote Anthropic's own bullet label {anthropic_label!r}, so "
            "a reader can check for themselves which of the three names that "
            "page actually uses."
        )
    assert not re.search(r"named by both|both vendors name", attribution), (
        "Must not attribute all three FIELD NAMES to both vendors: Anthropic "
        "names only `Constraints`."
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
    # shared/mandatory guidance. Matches "require"/"requires"/"mandatory" as
    # whole words only — "required" (as in "not a required field", the real
    # reference's own negation) must not false-trigger it. This block used
    # to also carry an exact-phrase sibling ("both vendors document four
    # fields" not in content_lower): its own comment already said it was
    # "kept as a cheap extra tripwire; the facts above are what actually
    # gates this" — it pinned one specific wording of the same inaccuracy
    # and nothing else, while Facts 2-4 above plus this regex guard gate
    # the real, wording-independent attribution-accuracy invariant in this
    # same test. Deleted per B1 hard rule 3.
    for p in paragraphs_lower:
        if "both" in p and "stop-when" in p and re.search(r"\b(requires?|mandatory)\b", p):
            raise AssertionError(
                "Must not claim both vendors require Stop-when as "
                "shared/mandatory guidance — Stop-when is this skill's own "
                f"addition. Offending paragraph: {p!r}"
            )


def _section_four(content: str) -> str:
    """Extract '## 4 — `Stop-when`' section's own text, heading-scoped.

    Bounded to the text between that heading and the next `---` rule (the
    "## The 4,000-character budget" section starts after it) — so an
    assertion below can only be satisfied by §4's own words, never by
    unrelated text living in §2 or the budget/attribution sections.
    """
    match = re.search(
        r"## 4 — `Stop-when`\n\n(.*?)(?=\n---|\Z)",
        content,
        re.DOTALL,
    )
    assert match, "Expected to find the '## 4 — `Stop-when`' section."
    return match.group(1)


def _negation_binds(text: str, negation: str, target: str, max_gap_words: int = 6) -> bool:
    """Bound negation-to-target polarity check (word-boundary safe).

    True iff a `negation` alternation sits within `max_gap_words` words
    directly BEFORE `target`. See
    docs/loom/memory/a-list-of-forbidden-words-is-defeated-by-the-word-outside-it.md
    — a bare `negation.*target` is satisfied by unrelated co-occurrence
    anywhere in the text; this keeps the match local to the clause the
    negation actually governs.
    """
    pattern = (
        r"\b(?:"
        + negation
        + r")\b(?:\s+\S+){0,"
        + str(max_gap_words)
        + r"}\s+"
        + target
    )
    return re.search(pattern, text) is not None


def test_stop_when_is_one_bound_written_as_completion() -> None:
    content = _read_reference()
    section_lower = _section_four(content).lower()

    # --- count: exactly one bound (turn count or wall-clock limit), never
    # a list of exit conditions ---
    assert re.search(r"\bone\b", section_lower) and "bound" in section_lower, (
        "Stop-when must state exactly one bound."
    )
    assert _negation_binds(section_lower, r"never|not", r"a\s+list\s+of"), (
        "Stop-when must state it is never a list of exit conditions, with "
        "the negation bound to 'a list of'."
    )

    # --- completion: reaching the bound with a status report posted in the
    # conversation counts as the run completing, as a failure report ---
    assert re.search(r"\breport\b(?:\s+\S+){0,10}\s+\bcomplet\w*", section_lower) or re.search(
        r"\bcomplet\w*(?:\s+\S+){0,10}\s+\breport\b", section_lower
    ), (
        "Stop-when must bind a status report posted to the run completing."
    )
    assert "failure report" in section_lower, (
        "Must state reaching the bound with a report posted counts as a "
        "failure report."
    )

    # --- why: a bare 'stop after N turns' is read by the evaluator as
    # permission to stop, not as the condition being met, so it neither
    # releases the run nor bounds it ---
    assert "permission" in section_lower, (
        "Must state the evaluator reads a bare stop clause as permission "
        "to stop."
    )
    assert _negation_binds(section_lower, "not", r"the\s+condition"), (
        "Must state this is NOT the condition being met, with the "
        "negation bound to 'the condition'."
    )
    assert _negation_binds(section_lower, "neither", r"releases?\s+the\s+run"), (
        "Must state it neither releases the run — negation bound to "
        "'releases the run'."
    )

    # --- forks: human-dependent forks are not Stop-when material — pointer
    # to input-floor.md §4 item 3 ---
    assert _negation_binds(section_lower, "never|not", r"stop-when\s+material"), (
        "Must state a human-dependent fork is never Stop-when material, "
        "negation bound to 'Stop-when material'."
    )
    assert "human" in section_lower, (
        "Must name the human-dependent fork explicitly."
    )
    assert "input-floor" in section_lower, (
        "Must point at input-floor.md for where a human-dependent fork "
        "goes instead."
    )

    # --- example: one canonical example, still containing 'turn' (existing
    # pin: "turn" in content_lower must keep holding) ---
    assert "turn" in section_lower, (
        "Stop-when's example must contain 'turn' (existing whole-file pin)."
    )
