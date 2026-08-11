"""Shared pin module for review-scope/loop-shape changes landed by the
2026-08-11 review-cost-reduction plan (docs/loom/plans/2026-08-11-review-
cost-reduction.md). Task 8 adds the first pin function; sibling tasks (7,
9, 10, 11, 12) each add one more pin function to this same module so a
partial cascade (one site updated, another forgotten) fails loudly instead
of passing silently -- plan §Notes "Classification glob SSOT chain".
"""
import re
from pathlib import Path

RCR_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)

DOCS_REVIEWER_AGENT = (
    Path(__file__).resolve().parent.parent / "agents" / "docs-reviewer.md"
)

RDR_SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "requesting-docs-review"
    / "SKILL.md"
)


def _rcr_text() -> str:
    return RCR_SKILL_MD.read_text(encoding="utf-8")


def _docs_reviewer_text() -> str:
    return DOCS_REVIEWER_AGENT.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a hard-wrapped phrase still matches a
    single-line pin, and strip markdown emphasis markers so bold text is
    not falsely distinct from the equivalent plain phrase -- mirrors
    test_docs_reviewer_agent.py's _norm. NOTE: this also strips `*`
    characters, so it must never be used to check a glob literal
    (`**/*.md`) -- check those against the raw, un-normalized slice."""
    return re.sub(r"\s+", " ", s.replace("*", "")).strip()


def _section(text: str, heading_prefix: str) -> str:
    """Slice from the first `## `-heading line starting with
    heading_prefix to the next `## `-heading line (or EOF). Scopes an
    assertion to the one section it names, so a mutation inside that
    section is guaranteed to redden the test that names it -- rather
    than a whole-file substring search a mutation elsewhere could
    accidentally keep green."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i
            break
    assert start is not None, f"heading {heading_prefix!r} not found in text"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "".join(lines[start:end])


def _rdr_text() -> str:
    return RDR_SKILL_MD.read_text(encoding="utf-8")


def test_rcr_scope_classification():
    """requesting-code-review/SKILL.md must install the contract/record
    classification SSOT (Task 8): the glob rule verbatim, the record-class
    exemption-at-any-mix statement, and the record-only continuity
    mechanism's verb name -- so Task 7's agent copy and Task 14's Python
    encoding have a stable heading + literal to cite."""
    text = _rcr_text()

    # the glob rule, verbatim per the plan's authoring literal (Task 8
    # Description / Task 7 Description, same literal in both)
    assert "<plugin>/skills/**/*.md" in text
    assert "<plugin>/agents/*.md" in text
    assert "<plugin>/hooks/*.md" in text
    assert "<plugin>/scripts/*.md" in text
    assert "README*" in text
    assert "CHANGELOG*" in text
    assert "record-class" in text and "docs/**" in text

    # record-class exemption at any mix (docs arm receives contract-class
    # files ONLY)
    assert "exempt from review at any mix" in text

    # record-only continuity mechanism, named (Task 14's marker verb)
    assert "mint --review-na-record-only" in text


def test_docs_reviewer_scope_and_confirmation():
    """docs-reviewer.md (Task 7) must carry: (a) the scope contract --
    the SAME glob literal as rcr SKILL.md's SSOT heading (byte-equal;
    Task 13's cross-file lockstep assertion pins the two against each
    other later), the SSOT-citation sentence naming the rcr heading
    (not the bare `SSOT` token, which recurs elsewhere in this file's
    injected boilerplate -- e.g. the baseline/rule-sheet blocks' own
    "SSOT note" headers), and the record-class N/A-loudly jurisdiction
    duty as ONE contiguous restrictive sentence; (b) the NEW
    delta-confirmation duty -- the CONFIRMED_RESOLVED / STILL_BLOCKING
    reply, delta-scoped via SendMessage, with the NEVER polarity on the
    whole-corpus re-sample ban intact (not just the bare noun phrase).

    Each clause is asserted inside `_section()`'s slice of the ONE
    section that carries it -- clause-scoped, not whole-file -- and the
    polarity-bearing phrases are checked as contiguous strings so a
    mutation flipping "never" -> "always", or inverting the
    jurisdiction sentence, reddens this test (manually verified against
    two temp-mutated copies; see the T7 fix-round report)."""
    text = _docs_reviewer_text()
    scope = _section(text, "## Scope contract")
    delta = _section(text, "## Delta-confirmation duty")

    # (a) scope contract: glob literal byte-equal to rcr's SSOT --
    # checked against the RAW (un-normalized) slice: _norm strips `*`,
    # which would silently eat the glob wildcards
    for literal in (
        "<plugin>/skills/**/*.md",
        "<plugin>/agents/*.md",
        "<plugin>/hooks/*.md",
        "<plugin>/scripts/*.md",
        "README*",
        "CHANGELOG*",
    ):
        assert literal in scope, (
            f"glob literal {literal!r} missing from ## Scope contract"
        )
    assert "record-class" in scope and "docs/**" in scope

    norm_scope = _norm(scope)

    # SSOT-citation sentence, contiguous -- naming the exact rcr heading
    # AND the cite-don't-re-derive instruction together, not the bare
    # "SSOT" token alone
    assert (
        'per the SSOT heading `loom-code/skills/requesting-code-review/SKILL.md` '
        '§"Classification: contract-class vs record-class" '
        '([source](../skills/requesting-code-review/SKILL.md)) '
        '— cite it, never re-derive the rule yourself'
    ) in norm_scope, (
        "the SSOT-citation sentence naming the rcr heading must survive "
        "as one contiguous sentence, not scattered independent tokens"
    )

    # record-class OUT of jurisdiction: ONE contiguous restrictive
    # sentence -- flipping "do not review them" to its positive, or
    # dropping "only" from "review only the contract-class remainder",
    # must redden this assertion
    assert (
        "do not review them: state `N/A` for that file, loudly, in your "
        "summary — and review only the contract-class remainder of "
        "the dispatch packet"
    ) in norm_scope, (
        "the jurisdiction sentence must survive as one contiguous "
        "restriction, not two independently-flippable clauses"
    )

    # (b) NEW delta-confirmation duty
    assert "SendMessage" in delta
    assert "CONFIRMED_RESOLVED" in delta
    assert "STILL_BLOCKING" in delta

    norm_delta = _norm(delta)
    assert (
        "never a fresh whole-corpus re-sample of the artifact set"
        in norm_delta
    ), (
        "the NEVER polarity must survive on the whole-corpus re-sample "
        "ban, not just the bare noun phrase"
    )


def test_rdr_single_round_confirmation():
    """requesting-docs-review/SKILL.md (Task 9) must carry the
    single-round-with-confirmation contract that REPLACES the 2-round
    cap + qualifying-shape auto-delta-round design: round 1 whole-artifact
    is the ONLY full review; a gating verdict is fixed then confirmed by
    the SAME reviewer via SendMessage, delta-scoped, never a fresh
    whole-corpus re-sample; STILL_BLOCKING after one fix cycle STOPs and
    surfaces to the user; the terminal state is 'no gating findings',
    never 'clean'; the old bounded-cap machinery (2-round cap, the
    qualifying-shape auto-delta round) is gone from the shipped text."""
    text = _rdr_text()
    low = text.lower()

    assert "round 1" in low and "only full review" in low, (
        "must state round 1 whole-artifact is the ONLY full review"
    )
    assert "delta confirmation" in low, (
        "must name the delta-confirmation step"
    )
    assert "sendmessage" in low, (
        "confirmation must be dispatched via SendMessage, not a fresh "
        "Agent dispatch"
    )
    assert "confirmed_resolved" in low and "still_blocking" in low, (
        "must name both confirmation verdicts"
    )
    assert "stop" in low and "surface" in low, (
        "STILL_BLOCKING after one fix cycle must STOP and surface to "
        "the user"
    )
    assert "no gating findings" in low, (
        "the terminal state must be 'no gating findings', never 'clean'"
    )
    assert "whole-corpus re-sample" in low, (
        "delta confirmation must never be a fresh whole-corpus re-sample"
    )

    # old bounded-cap machinery must be gone from the shipped text.
    assert "2 review rounds" not in low, (
        "the old '2 review rounds' bounded-cap phrase must not survive"
    )
    assert "auto-delta" not in low, (
        "the old auto-delta-round machinery must not survive"
    )
    assert "qualifying-shape" not in low, (
        "the old qualifying-shape auto-delta-round machinery must not "
        "survive"
    )
