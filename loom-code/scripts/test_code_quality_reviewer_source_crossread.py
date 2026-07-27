"""Structural grep-test guarding the Task 5b addition to
code-quality-reviewer.md's role contract: a conditional instruction to
open a plan's cited source and cross-check it against the plan's
stated fact, triggered only when the plan text this task is judged
against actually carries a source citation
(docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md, Task 5b;
mirrors Task 5a's spec-reviewer test -- same five assertions, this
contract).

code-quality-reviewer.md is a prompt artifact, not executable code;
its correctness here is the PRESENCE of load-bearing PHRASES (intent),
tolerant of wording variation -- see
loom-code/scripts/test_writing_plans_verdict_gate.py for the shape.

Scoping note (load-bearing): this file already carries an UNRELATED,
pre-existing, correct unconditional mandate in the dimension table's
external-surface-grounding row ("verify every external-surface call
in this task's diff carries a grounding cite" -- dimension D7). That
mandate is out of scope for Task 5b and must be left alone. (Its line
number has already drifted once, from :365 to :372, because Tasks 5a
and 5b were written concurrently and 5b's own insertion shifted it --
which is exactly why this note anchors on the row's content, not a
line number that the next insertion will invalidate again.) The final
assertion below (the ADDED instruction reads as a trigger, not a
blanket mandate) is therefore scoped to the added section only, via
an anchor unique to the new text -- an unscoped "no unconditional
mandate anywhere in this file" check would be unsatisfiable both
before and after this task, since that row's mandate is legitimate
and untouched.

Stdlib only (pathlib). Resolve the agent file relative to this test.
"""

from pathlib import Path

AGENT = Path(__file__).parents[1] / "agents" / "code-quality-reviewer.md"

ANCHOR = "conditional source cross-read"


def _text() -> str:
    assert AGENT.is_file(), f"code-quality-reviewer.md is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _added_section(text: str) -> str:
    """Isolate the added instruction, anchored on a marker phrase that
    exists only in the new text -- never in the pre-existing,
    far-away external-surface-grounding mandate (dimension table),
    which uses entirely different wording. Cuts at the next
    blank-line-preceded boundary, matching Task 5a's sibling test
    (test_spec_reviewer_source_crossread.py::_crossread_section)
    rather than hardcoding the reviewer-discipline managed-block
    marker string: a fixed marker string is tighter only against that
    one specific neighbor and would still swallow a future role-
    contract item 8 inserted, blank-line-separated, between this item
    and the marker -- exactly the failure mode of an item 8 appended
    directly (no blank line) that Task 5a's own boundary shares, since
    this file's numbered-list items are single-newline-separated with
    no blank line until the section actually ends. Aligning to the
    tighter, convention-based cut removes the dependency on knowing
    the neighbor's exact marker text, which is the part actually worth
    tightening."""
    low = text.lower()
    start = low.index(ANCHOR)
    tail = text[start:]
    end_markers = ["\n\n", "\n#"]
    end = len(tail)
    for m in end_markers:
        idx = tail.find(m, len(ANCHOR))
        if idx != -1:
            end = min(end, idx)
    return tail[:end]


def test_code_quality_reviewer_carries_conditional_crossread():
    """The contract must state: (a) the if-a-citation-is-present
    condition, (b) the open-and-compare action, (c) the explicit
    no-citation no-op, (d) an inline definition of what counts as a
    source citation, and (e) that the ADDED instruction (never the
    pre-existing, out-of-scope external-surface-grounding mandate) is
    bounded by a condition whose false branch is a stated no-op --
    not an unconditional verify-everything mandate."""
    text = _text()
    assert ANCHOR in text.lower(), (
        "code-quality-reviewer.md must carry the conditional source "
        "cross-read instruction (Task 5b)"
    )
    section = _added_section(text)
    low = section.lower()

    # (a) if-a-citation-is-present condition
    assert "carries a source citation" in low, (
        "must state the if-a-citation-is-present condition"
    )

    # (b) open-and-compare action
    assert "open" in low and "confirm" in low, (
        "must state the open-and-compare action (open the cited "
        "source and confirm it says what the plan claims)"
    )

    # (c) explicit no-citation no-op
    assert "no-op" in low, "must state the explicit no-op"
    assert "no citation" in low, (
        "the no-op must be conditioned on citation absence"
    )

    # (d) inline definition of what counts as a source citation
    assert "file:line" in low, (
        "must define what counts as a source citation (file:line, "
        "commit SHA, or an explicit pointer)"
    )

    # (e) trigger, not mandate -- scoped to the ADDED section only.
    # The pre-existing external-surface-grounding mandate ("verify
    # every external-surface call ... carries a grounding cite") is
    # untouched, out of scope, and must not satisfy this assertion.
    #
    # This checks the actual property (a condition whose false branch
    # is a stated no-op), not a "when"-present/"every"-absent keyword
    # proxy: that proxy PASSES on the counterexample "When judging any
    # plan, always cross-check its cited facts" -- it contains "when",
    # omits "every", yet is functionally unconditional. Verified by
    # mutation (loom-code/scripts, this task's report has both runs).
    #
    # Structural check: the trigger condition, the open/confirm
    # action, and the no-op must appear in that order (condition ->
    # action -> negated-condition -> no-op) -- if the no-op does not
    # come after the action, it is not actually gating that action.
    trigger_idx = low.find("carries a source citation")
    action_idx = low.find("open")
    noop_idx = low.find("no-op")
    assert trigger_idx != -1 and action_idx != -1 and noop_idx != -1, (
        "trigger, action, and no-op must all be present in the added "
        "section (see assertions a/b/c above)"
    )
    assert trigger_idx < action_idx < noop_idx, (
        "the trigger condition must precede the open/confirm action, "
        "which must precede the stated no-op -- otherwise the no-op "
        "is not actually the condition's false branch"
    )
    # Reject unconditional-strengthening language that would override
    # the stated conditionality even with a valid trigger/action/no-op
    # ordering in place (e.g. "always", "regardless" nearby).
    unconditional_tells = (
        "always", "any plan", "regardless", "unconditionally",
        "no matter", "every",
    )
    found_tells = [w for w in unconditional_tells if w in low]
    assert not found_tells, (
        f"the added instruction must not contain unconditional-"
        f"strengthening language {found_tells} -- that would override "
        "the stated conditionality even if a trigger word and a "
        "no-op are both present"
    )
