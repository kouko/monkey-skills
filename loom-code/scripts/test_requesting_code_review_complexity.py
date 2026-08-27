"""Contract test for the branch-review implementation complexity lens."""

from pathlib import Path


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "requesting-code-review" / "SKILL.md"
EVIDENCE = ROOT / "skills" / "requesting-code-review" / "references" / "design-evidence.md"
REVIEWER = ROOT / "agents" / "code-reviewer.md"
LENS = ROOT / "skills" / "requesting-code-review" / "references" / "implementation-complexity-lens.md"


def test_deletion_first_compares_actual_and_planned_complexity():
    skill = SKILL.read_text(encoding="utf-8")
    evidence = EVIDENCE.read_text(encoding="utf-8")
    reviewer = REVIEWER.read_text(encoding="utf-8")
    lens = LENS.read_text(encoding="utf-8")
    flat_lens = " ".join(lens.split())

    assert "references/implementation-complexity-lens.md" in skill
    assert "Implementation complexity lens" in evidence
    assert "actual additions" in flat_lens and "planned complexity evidence" in flat_lens
    assert "landed deletions" in flat_lens and "simpler alternative" in flat_lens
    assert "downstream operational risk" in lens
    assert "independent local assessment" in lens
    assert "preserves the required outcome" in lens.lower()
    assert "scope trade-off" in lens.lower()
    assert "implementation complexity lens" in reviewer.lower()


def test_implementation_lens_carries_all_four_handoff_meanings():
    """Spec BI-2 requires all four meanings of every stage lens.

    The other five lenses each ask why retained complexity is worthwhile; this
    one asked only about added burden, deletions, and downstream risk. The
    branch names copied four-question prose drifting apart as its own downstream
    risk, so the contract test pins the meaning rather than trusting the copy.
    """
    lens = LENS.read_text(encoding="utf-8")
    flat = " ".join(lens.split()).lower()
    assert "actual additions" in flat, "added-burden meaning"
    assert "landed deletions" in flat, "outcome-preserving deletion meaning"
    assert "downstream operational risk" in flat, "downstream-risk meaning"
    assert "worth" in flat, (
        "the implementation lens must ask why the retained complexity is worth "
        "its cost — the fourth handoff meaning required of every stage lens"
    )


def test_reviewer_fallback_is_not_narrower_than_the_lens():
    """The agent file must not shrink the no-evidence fallback.

    The reviewer reads `code-reviewer.md` before the lens, so a fallback there
    that names only downstream risk licenses skipping the added-burden and
    landed-deletion assessment whenever no plan evidence exists.
    """
    reviewer = REVIEWER.read_text(encoding="utf-8")
    flat = " ".join(reviewer.split())
    marker = "**Implementation complexity lens.**"
    assert marker in flat
    paragraph = flat[flat.index(marker) : flat.index(marker) + 700]
    lowered = paragraph.lower()
    assert "when evidence is absent" in lowered or "when planned evidence is absent" in lowered
    assert "from the diff" in lowered, (
        "the no-evidence fallback must send the reviewer to the diff for the "
        "whole assessment, not only for downstream risk"
    )
