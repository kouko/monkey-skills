"""Structural grep-window test guarding `requesting-docs-review`'s Step 1:
it must consume a passed-down scope when one was handed to it, and only
call the `review_scope.py` resolver itself when none was supplied (Task 6
of `docs/loom/plans/2026-08-03-review-scope-resolver.md`).

SKILL.md is a prompt/contract artifact, not executable code -- nothing
importable observes whether the orchestrator actually skips the resolver
call on a delegated dispatch. This file IS the instruction the
orchestrator reads at dispatch, so its correctness condition is the
PRESENCE of the load-bearing phrases -- same convention as
`test_requesting_docs_review_skill.py` (window-scoped, not whole-file
substring greps, per
`docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md`).

The two §Pinned contracts (pass-down, refusal) are written at BOTH ends
of the protocol: `requesting-code-review` sends, this skill receives.
The hazard is drift between the copies, so the assertions below compare
the two files to each other rather than pinning either one's wording:
rewording both together stays green, changing one alone fails. Presence
inside the Step 1 window is pinned separately, since two copies that
were both deleted would still agree.

Stdlib only (pathlib, re).
"""
# Residual gap (recorded, not built): no test in this file discriminates
# a conditional Step 1 from an unconditional one -- only a behavioural
# cold-read round would (per
# docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md),
# and building that probe for one Step-1 conditional was judged
# disproportionate to this task's scope.
from __future__ import annotations

import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-docs-review"
    / "SKILL.md"
)

CODE_REVIEW_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-code-review"
    / "SKILL.md"
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _contract(text: str, name: str) -> str:
    """Body of the `§Pinned <name> contract` as written in `text`.

    Two renderings are in use across the family and both are accepted:
    the quoted form (`§Pinned pass-down contract: "..."`) and the
    unquoted `(transcribed verbatim):` form that runs to end of line.
    Whitespace is normalized so a re-wrap is not a difference.
    """
    label = (
        rf"§Pinned {re.escape(name)} contract\*{{0,2}}\s*"
        r"(?:\(transcribed verbatim\))?\s*:\s*"
    )
    quoted = re.search(label + r'"([^"]+)"', text)
    if quoted:
        return _norm(quoted.group(1))
    bare = re.search(label + r"(.+)", text)
    assert bare, (
        f"no `§Pinned {name} contract` is present at all -- it was "
        "deleted or its label was renamed"
    )
    return _norm(bare.group(1))


def _process_section(text: str) -> str:
    """Window from `## Process` to the next `## ` heading."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and "process" in line.lower():
            start = i
            break
    assert start is not None, "SKILL.md carries no '## Process' heading"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "".join(lines[start:end])


def _step1_window(text: str) -> str:
    """Step 1 only -- from the line starting `1. ` to the line starting
    `2. ` inside `## Process`. Narrower than the whole steps list so a
    phrase belonging to a later step (e.g. Step 3's dispatch) cannot
    satisfy an assertion meant to pin Step 1 specifically.
    """
    proc = _process_section(text)
    lines = proc.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^1\.\s", line):
            start = i
            break
    assert start is not None, (
        "`## Process` carries no numbered Step 1 at column 0"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^2\.\s", lines[j]):
            end = j
            break
    assert end != len(lines), (
        "Step 1 must be followed by a Step 2 at column 0 -- window has no "
        "closing boundary"
    )
    return "".join(lines[start:end])


def _assert_conditional_resolve(low: str) -> None:
    """Raise AssertionError unless `low` states Step 1 resolves scope
    itself ONLY when no `resolved-scope` was handed down, naming that
    exact token."""
    assert "`resolved-scope`" in low, (
        "Step 1 must name the pass-down token verbatim as `resolved-scope`"
    )
    assert "only when no `resolved-scope` was supplied" in low, (
        "Step 1 must state the delegate resolves scope itself ONLY when "
        "no `resolved-scope` was supplied -- the §Pinned pass-down "
        "contract's own conditional, verbatim"
    )


def test_step1_resolves_only_when_no_resolved_scope_supplied():
    """Asserts Step 1's text names `resolved-scope` and states the
    ONLY-when-absent conditional -- presence, not behavior."""
    low = _norm(_step1_window(_text())).lower()
    _assert_conditional_resolve(low)


def _assert_refusal_stops_before_dispatch(low: str) -> None:
    assert "stops this station before any dispatch" in low, (
        "Step 1 must state a refusal stops the station before dispatching "
        "anything -- not just refuse and continue"
    )
    assert "do not dispatch the docs-reviewer panel" in low, (
        "the STOP must be spelled out as a concrete instruction: do not "
        "dispatch the docs-reviewer panel on a refusal"
    )


def test_refusal_stops_station_before_dispatch():
    """Asserts Step 1's text states the STOP-before-dispatch phrasing
    verbatim -- presence, not behavior."""
    low = _norm(_step1_window(_text())).lower()
    _assert_refusal_stops_before_dispatch(low)


def _assert_contract_agrees_with_code_review(name: str) -> None:
    """Both ends of the protocol carry the SAME contract text.

    The invariant these pins exist to protect is agreement between the
    two copies, not any particular wording: `requesting-code-review`
    writes the sending end and this skill writes the receiving end, so a
    drift on one side silently unwires the protocol. Comparing the two
    copies states that directly -- a deliberate rewording applied to
    both sides stays green, while a change to one side alone fails.
    """
    ours = _contract(_text(), name)
    theirs = _contract(CODE_REVIEW_MD.read_text(encoding="utf-8"), name)
    assert ours == theirs, (
        f"the §Pinned {name} contract has drifted between the two ends "
        "of the protocol -- reword both copies together or neither.\n"
        f"  requesting-docs-review:  {ours}\n"
        f"  requesting-code-review:  {theirs}"
    )


def test_pass_down_contract_agrees_with_code_review():
    """The pass-down contract says the same thing on both ends."""
    _assert_contract_agrees_with_code_review("pass-down")


def test_refusal_contract_agrees_with_code_review():
    """The refusal contract says the same thing on both ends."""
    _assert_contract_agrees_with_code_review("refusal")


def test_both_contracts_are_carried_inside_step_1():
    """Neither contract may drift out of the Step 1 window it governs.

    Agreement between the copies is not enough on its own: deleting the
    contract from BOTH files would keep them equal. This pins presence
    at the place the orchestrator reads.
    """
    step1 = _norm(_step1_window(_text()))
    for name in ("pass-down", "refusal"):
        assert _contract(_text(), name) in step1, (
            f"the §Pinned {name} contract is no longer inside Step 1"
        )


def test_no_unconditional_branch_diff_survives():
    """No line anywhere in the file still computes scope via the old
    unconditional branch-diff invocation -- Step 1 must resolve scope
    exclusively through the pass-down / resolver-CLI path above."""
    text = _text()
    pattern = re.compile(r"git diff( --name-only)? main\.\.\.HEAD")
    offending = [
        line for line in text.splitlines() if pattern.search(line)
    ]
    assert not offending, (
        "an unconditional branch-diff invocation survives in SKILL.md: "
        f"{offending!r} -- Task 6 requires deleting it in the same edit "
        "that adds the conditional resolve"
    )


def test_resolver_cli_named_in_step1():
    """Step 1 names the resolver CLI it falls back to when no scope was
    handed down."""
    low = _norm(_step1_window(_text())).lower()
    assert "review_scope.py" in low, (
        "Step 1 must name the `review_scope.py` resolver CLI it calls "
        "when no `resolved-scope` was supplied"
    )
