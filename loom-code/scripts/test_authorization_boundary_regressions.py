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
    """STILL_BLOCKING after the one fix cycle is a quality stop, never a
    permission boundary that would make the agent wait on the user to
    authorize continuing. The four sibling `not in text` checks this test
    used to run (guarding against the exact historical wrong phrasings
    "no second cycle without explicit user authorization", "on its own
    authority", "on your own authority", "hands the decision to the user")
    were deleted: each pinned the ABSENCE of one specific old string, so a
    regression restated in different words would pass them silently, while
    a harmless paraphrase of the same old string would fail them for no
    behavioral reason -- pure phrasing pins with no invariant of their own
    (Hard rule 3a). The positive assertion below already states the
    corrected invariant directly."""
    text = DOCS_REVIEW.read_text(encoding="utf-8")

    assert "quality stop, not a new permission boundary" in text


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
    """The ff-to-origin sync is gated on the human merge already happening,
    and is the fast-forward command, not an agent-performed merge. The
    third assertion this test used to run ("synchronization, not an
    agent-performed merge" in text) was deleted: that "this is sync, not a
    merge" distinction is already pinned twice over in this same file --
    by the ff-command mechanism kept below, and by
    `test_finishing_enumerates_agent_never_main_mutations` forbidding
    `gh pr merge` / merging into `main` outright -- so it protected no
    invariant not already covered here (Hard rule 3b)."""
    text = " ".join(FINISHING.read_text(encoding="utf-8").split())

    assert "After the user has merged the PR" in text
    assert "fast-forward local `main` to `origin/main`" in text
