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
    authorize continuing.

    The positive assertion carries the rule; it is the primary guard, since
    an absence check can only catch a LITERAL return of the old text and
    never a reworded one. The four absence checks below are kept anyway,
    because each retired string is a CONFLICTING INSTRUCTION rather than a
    rationale: an executor who found any of them would stop and wait for
    user authorization, and the positive sentence does not prevent one of
    them being re-added alongside it. They stay UNNARROWED for the same
    reason -- a window would let the retired instruction return elsewhere in
    the file."""
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
