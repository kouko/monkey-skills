"""Regression contracts for review remediation and main-merge boundaries."""

from pathlib import Path


SKILLS = Path(__file__).parents[1] / "skills"
DOCS_REVIEW = SKILLS / "requesting-docs-review" / "SKILL.md"
FINISHING = SKILLS / "finishing-a-development-branch" / "SKILL.md"


def test_docs_review_distinguishes_review_only_from_authorized_change() -> None:
    text = DOCS_REVIEW.read_text(encoding="utf-8")

    assert "Review-only request" in text
    assert "Authorized change task" in text
    assert "without asking again" in text
    assert "Do NOT auto-fix" not in text


def test_docs_review_treats_confirmation_limit_as_quality_stop() -> None:
    text = DOCS_REVIEW.read_text(encoding="utf-8")

    assert "quality stop, not a new permission boundary" in text
    assert "no second cycle without explicit user authorization" not in text
    assert "on its own authority" not in text
    assert "on your own authority" not in text
    assert "hands the decision to the user" not in text


def test_finishing_treats_docs_confirmation_limit_as_quality_stop() -> None:
    text = FINISHING.read_text(encoding="utf-8")

    assert "quality-limit diagnosis" in text
    assert "explicit user authorization" not in text


def test_finishing_enumerates_agent_never_main_mutations() -> None:
    text = " ".join(FINISHING.read_text(encoding="utf-8").split())

    for forbidden in (
        "merge a feature branch into local `main`",
        "push directly to remote `main`",
        "run `gh pr merge`",
        "enable auto-merge",
    ):
        assert forbidden in text


def test_finishing_allows_sync_only_after_human_merge() -> None:
    text = " ".join(FINISHING.read_text(encoding="utf-8").split())

    assert "After the user has merged the PR" in text
    assert "fast-forward local `main` to `origin/main`" in text
    assert "synchronization, not an agent-performed merge" in text
