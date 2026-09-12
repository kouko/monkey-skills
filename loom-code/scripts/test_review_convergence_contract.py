from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = (ROOT / "loom-code/skills/review/SKILL.md").read_text(encoding="utf-8")
REVIEWER = (ROOT / "loom-code/agents/reviewer.md").read_text(encoding="utf-8")
REVIEW_WORDS = " ".join(REVIEW.split())
CONTRACT = " ".join((REVIEW + "\n" + REVIEWER).split())


def test_review_episode_has_three_distinct_content_rounds_and_no_identity_reset() -> None:
    assert "<!-- gate: review.bounded-episode -->" in REVIEW
    assert "<!-- /gate -->" in REVIEW
    assert "three distinct functional-content digests" in REVIEW_WORDS
    assert "does not reset" in REVIEW_WORDS
    for identity in ("reviewer", "vendor", "model", "task", "app", "branch"):
        assert identity in REVIEW_WORDS


def test_round_roles_require_relook_before_terminal_round() -> None:
    assert "Round 1" in REVIEW_WORDS
    assert "Round 2" in REVIEW_WORDS
    assert "Round 3" in REVIEW_WORDS
    assert "technical design re-look" in REVIEW_WORDS
    assert "NON_CONVERGENT" in CONTRACT
    assert "Round 4" in CONTRACT


def test_stuck_review_stops_local_patching() -> None:
    assert "same blocker survives two consecutive rounds" in REVIEW_WORDS
    assert "blocker count does not decrease" in REVIEW_WORDS
    assert "stop local patching" in REVIEW_WORDS


def test_agent_owns_technical_choices_until_product_contract_changes() -> None:
    assert "requirements, visible behavior, or guarantees" in REVIEW_WORDS
    assert "Do not ask the user whether to continue" in REVIEW_WORDS


def test_same_content_executor_retry_is_bounded_and_not_a_round() -> None:
    assert "same functional-content digest" in REVIEW_WORDS
    assert "retry once" in REVIEW_WORDS
    assert "EXECUTION_FAILED" in CONTRACT


def test_contract_adds_no_review_round_ledger_or_schema() -> None:
    forbidden = ("review-round.json", "rounds.json", "review_episode.json")
    assert not any(name in CONTRACT for name in forbidden)


def test_round_four_is_forbidden_in_context() -> None:
    assert "never dispatch Round 4" in REVIEW_WORDS
    assert "must not dispatch Round 4" in CONTRACT


def test_reviewer_yaml_is_converted_to_finalization_json() -> None:
    assert "structured YAML" in REVIEW_WORDS
    assert "convert" in REVIEW_WORDS
    assert "temporary JSON" in REVIEW_WORDS


# ---------------------------------------------------------------------------
# Acceptance A4/A5 — the recording passage at the end of convergence
#
# READ THIS BEFORE YOU EDIT OR DELETE ANYTHING BELOW.
#
# The passage these tests pin says three things: a lesson this branch already
# taught is written down while a round can still absorb it, a recorded lesson
# is ordinary functional content and never justifies a fourth digest, and
# almost nothing qualifies. It is deliberately inert — it names no plugin,
# calls no tool, and sits OUTSIDE the `review.bounded-episode` gate markers so
# it registers no mechanism and needs no budget exception.
#
# It has been lost once. From 2026-07-08 (#515) the timing half was carried by
# the `finishing-a-development-branch` skill and pinned by a test; the loom 1.0
# cutover (#780) deleted that skill, and the instruction and its test went out
# together. Nothing was left to go red, so nobody noticed, and two consecutive
# changes afterwards reached merge before anyone thought about memory at all.
#
# WHAT KIND OF TEST THIS IS, stated accurately because the previous wording
# here overclaimed it: this is a LITERAL-PHRASE pin. Whitespace is flattened
# first, so prose may rewrap freely — but the phrases below are matched
# literally, and a faithful rewrite that says "goes in the commit message"
# instead of "belongs in its commit message" WILL go red. That is not a defect
# and it is not a reason to delete the pin. The correct response to a red is:
#
#   1. check the clause is still in the passage and still says the same thing;
#   2. if it is, update the phrase list below in the same commit as the
#      rewrite, and say in that commit that the meaning was preserved;
#   3. if it is not, you are removing a station contract — that needs an
#      intent, not an edit here.
#
# Step 2 is the one that looks like the anti-pattern every reviewer is trained
# to stop. It is not, provided the commit shows the clause survived. Deleting
# the assertion is what the 2026-07 cutover did.
# ---------------------------------------------------------------------------

_WHY = (
    "This element belongs to the recording passage at the end of convergence. "
    "It was lost once already when loom 1.0 deleted the skill carrying it "
    "along with its test. If the passage was reworded and still says this, "
    "update the phrase here in the same commit; if the clause is gone, that is "
    "a station contract change and needs an intent. See this section's header."
)


def _recording_passage() -> str:
    """The whole passage between the convergence gate's close and Finalize.

    Selecting one `\n\n` block was a real gap: the scarcity paragraph sat
    outside it, so a plugin name or a gate marker could be added there with
    every test staying green. Acceptance 5 is a property of the passage.
    """
    finalize = REVIEW.index("\n## 5. Finalize")
    closes_episode = REVIEW.rindex("<!-- /gate -->", 0, finalize)
    return REVIEW[closes_episode + len("<!-- /gate -->") : finalize]


def _flat_passage() -> str:
    """The passage with whitespace flattened — every clause assertion in this
    section runs against THIS, never against the whole station file.

    Every defect this episode found was one assertion reading a wider text
    than the clause it defends: the clause survived somewhere else in the
    file and the test stayed green while its subject was deleted. Widening
    the scope of an assertion here does not make it stricter, it makes it
    about something other than its name.
    """
    return " ".join(_recording_passage().split())


def test_convergence_states_the_recording_moment() -> None:
    """Timing half: record while a round can still read it, not after merge."""
    passage = _flat_passage()
    for element in (
        "after the merge costs a branch",
        "docs/loom/memory/",
        "a digest the reviewers read",
    ):
        assert element in passage, (
            f"the recording passage no longer states {element!r}. {_WHY}"
        )


def test_convergence_forbids_spending_an_extra_digest_on_a_lesson() -> None:
    """Recording is not free: a memory entry is functional content, so the
    passage must say where it lands and that it never buys another round.

    Scoped to the passage. Against the whole file this test passed while the
    sentence it names was deleted, because `functional content` occurs four
    more times in the station text — the same union-scoping defect this
    episode had just fixed elsewhere, reintroduced in the commit that fixed
    it."""
    passage = _flat_passage()
    for element in (
        "functional content",
        "never justifies exceeding this episode's digests",
    ):
        assert element in passage, (
            f"the recording passage no longer states {element!r}. {_WHY}"
        )


def test_convergence_states_the_scarcity_bar() -> None:
    """Scarcity half: almost nothing surfaced by a review is durable."""
    passage = _flat_passage()
    for element in (
        "Almost nothing qualifies",
        "belongs in its commit message",
        "Zero to one durable lesson per change",
    ):
        assert element in passage, (
            f"the recording passage no longer states {element!r}. {_WHY}"
        )


def test_recording_passage_invokes_nothing_and_registers_no_mechanism() -> None:
    """The whole passage must stay inert: no plugin name, no tool call, and no
    gate marker anywhere in it, so the mechanism count is unchanged."""
    passage = _recording_passage()
    assert "cheap to keep" in passage, (
        "the recording passage is gone from the end of convergence. " + _WHY
    )
    assert "<!-- gate:" not in passage, (
        "the passage must not be marked as a gate: the charter forbids a "
        "prose-only gate, and its criterion is a judgement. " + _WHY
    )
    for plugin in ("loom-memory", "loom-workflow", "git-memory"):
        assert plugin not in passage, (
            f"the passage must not name {plugin!r}; it points at a store path "
            "that can be checked for existence, not at an install. " + _WHY
        )
    for invocation in ("Invoke", "invoke the", "Use `"):
        assert invocation not in passage, (
            f"the passage must not instruct an invocation ({invocation!r}); "
            "#821 REQ-4 forbids a station calling memory by virtue of being "
            "reached. " + _WHY
        )
