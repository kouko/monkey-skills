"""Bars the code-as-spec lens from declaring itself a no-op, in both arms.

@req: none (this arc carries no registered REQ-ids in its plan/spec).
"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CODE_REVIEWER = REPO_ROOT / "loom-code" / "agents" / "code-reviewer.md"
DOCS_REVIEWER = REPO_ROOT / "loom-code" / "agents" / "docs-reviewer.md"

# Each arm is pinned by TWO phrases, not one. Pinning only the headline
# clause left both the trigger and the prohibition unprotected: a synthetic
# string carrying the headline plus an unrelated sentence still matched, so
# an edit that softened "you may not declare" to a suggestion, or narrowed
# the trigger, would have kept the tests green (whole-branch review, both
# code arms, independently).
#
# The two arms are pinned SEPARATELY because they say different things. The
# code arm scores a `deletion-first` dimension and its trigger discriminates;
# the docs arm has no such dimension — its five are omission, ambiguity,
# inconsistency, incorrect-fact, missing-population — and every artifact it
# receives is prose, so its bar names `omission` and states that it always
# applies. A single shared constant hid that difference and shipped a
# dangling referent into the docs arm.
CODE_ARM_PHRASES = (
    "makes this dimension never a no-op",
    "you may not declare it not applicable, out of scope for the branch, "
    "or skipped as a no-op",
)
DOCS_ARM_PHRASES = (
    "This lens is never a no-op on any dispatch you receive",
    "You may still score `omission: PASS`",
    "you may not declare the lens not applicable, out of scope for the "
    "artifact, or skipped as a no-op",
)


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _assert_all_present(path: Path, phrases: tuple[str, ...], arm: str) -> None:
    # Reads the WORKING TREE, not a committed blob: an implementer cannot
    # commit under the SDD contract, so a test reading committed content can
    # never go green here.
    flattened = _flatten(path.read_text(encoding="utf-8"))
    missing = [p for p in phrases if p not in flattened]
    assert not missing, (
        f"{path.name}'s code-as-spec lens must bar the {arm} from declaring "
        f"the lens a no-op, and must keep the prohibition itself intact. "
        f"Missing: {missing}"
    )


def test_code_arm_bars_the_no_op_declaration():
    _assert_all_present(CODE_REVIEWER, CODE_ARM_PHRASES, "code arm")


def test_docs_arm_bars_the_no_op_declaration():
    _assert_all_present(DOCS_REVIEWER, DOCS_ARM_PHRASES, "docs arm")


def test_the_bar_carries_its_reason_in_both_arms():
    """The section two paragraphs below each bar legislates that prose must
    carry its reason, sourced and never invented. Both arms shipped the bar
    without one, and the whole-branch docs review filed that as the rule text
    breaking its own rule. This pins the remedy so it cannot silently rot
    back out.

    The provenance citation itself moved out of the contract to
    `requesting-code-review/references/design-evidence.md` and
    `requesting-docs-review/references/design-evidence.md` (plan
    `docs/loom/plans/2026-08-22-contracts-cite-only-what-ships.md` Task 3);
    the reason sentence stays inline, uncited, since an injected system
    prompt reader has no way to fetch the cited document anyway."""
    for path in (CODE_REVIEWER, DOCS_REVIEWER):
        flattened = _flatten(path.read_text(encoding="utf-8"))
        assert "The reason is that a reader sees only the verdict" in flattened, (
            f"{path.name}'s no-op bar must state its reason inline"
        )
