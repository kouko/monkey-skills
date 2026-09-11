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
# Acceptance A4/A5 — the recording moment stated at the end of convergence
#
# READ THIS BEFORE YOU EDIT OR DELETE ANYTHING BELOW.
#
# The paragraph these tests pin says two things: a lesson this branch
# already taught is written down now, while recording is still free, and
# almost nothing qualifies. It is deliberately inert — it names no plugin,
# calls no tool, and sits OUTSIDE the `review.bounded-episode` gate markers
# so it registers no mechanism and needs no budget exception.
#
# It has been lost once. From 2026-07-08 (#515) the timing half was carried
# by the `finishing-a-development-branch` skill and pinned by a test; the
# loom 1.0 cutover (#780) deleted that skill, and the instruction and its
# test went out together. Nothing was left to go red, so nobody noticed,
# and two consecutive changes afterwards reached merge before anyone
# thought about memory at all.
#
# A phrase-presence assertion is a golden test at string granularity, and
# golden tests die by being re-approved rather than investigated. If one of
# these goes red, do not make it green. Check whether the paragraph is
# still in the station text; removing it on purpose is a change to what
# this station promises and needs an intent.
#
# The assertions pin required elements after whitespace flattening, never
# whole sentences, so rewording that keeps both halves stays green.
# ---------------------------------------------------------------------------

_WHY = (
    "This element belongs to the recording-moment paragraph at the end of "
    "convergence. It was lost once already when loom 1.0 deleted the skill "
    "carrying it along with its test. Removing it deliberately is a station "
    "contract change and needs an intent; see this section's header comment."
)


def test_convergence_states_the_recording_moment() -> None:
    """Timing half: record now, not after the merge."""
    for element in ("recording a lesson is free", "already known", "docs/loom/memory/"):
        assert element in REVIEW_WORDS, (
            f"the review station no longer states {element!r}. {_WHY}"
        )


def test_convergence_states_the_scarcity_bar() -> None:
    """Scarcity half: almost nothing surfaced by a review is durable."""
    for element in (
        "Almost nothing qualifies",
        "belongs in its commit message",
        "Zero to one durable lesson per change",
    ):
        assert element in REVIEW_WORDS, (
            f"the review station no longer states {element!r}. {_WHY}"
        )


def test_recording_moment_invokes_nothing_and_registers_no_mechanism() -> None:
    """The paragraph must stay inert: no plugin name, no tool call, and
    outside the gate markers so the mechanism count is unchanged."""
    where = REVIEW.find("recording a lesson is free")
    assert where != -1, "the recording-moment paragraph is gone. " + _WHY
    closes_episode = REVIEW.rfind("<!-- /gate -->", 0, where)
    finalize = REVIEW.find("\n## 5. Finalize")
    assert closes_episode != -1 and closes_episode < where < finalize, (
        "the paragraph must sit between the end of the convergence gate and "
        "Finalize: after Finalize the attestation exists, and a store edit "
        "then invalidates it. " + _WHY
    )
    paragraph = next(
        p for p in REVIEW.split("\n\n") if "recording a lesson is free" in p
    )
    assert "<!-- gate:" not in paragraph, (
        "the paragraph must not be marked as a gate: the charter forbids a "
        "prose-only gate, and its criterion is a judgement. " + _WHY
    )
    for plugin in ("loom-memory", "loom-workflow", "git-memory"):
        assert plugin not in paragraph, (
            f"the paragraph must not name {plugin!r}; it points at a store "
            "path that can be checked for existence, not at an install. " + _WHY
        )
