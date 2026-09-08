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
