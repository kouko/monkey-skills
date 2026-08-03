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

§Pinned pass-down contract (transcribed verbatim, from the plan):

    The delegating station hands the delegate the resolved scope as
    `resolved-scope` in the dispatch packet. The delegate resolves scope
    itself ONLY when no `resolved-scope` was supplied.

§Pinned refusal contract (transcribed verbatim, from the plan):

    A stale base, or any failure to establish freshness, REFUSES.
    The resolver never returns a file list it cannot vouch for, and a
    station that receives a refusal STOPS before dispatching anything.

Both are asserted verbatim below (whitespace-normalized only) so a
paraphrase that drifts from the pin -- the exact hazard this pin exists
to prevent, since Task 5 writes the sending end of the same protocol in
parallel -- fails this test.

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

PASS_DOWN_CONTRACT = (
    "The delegating station hands the delegate the resolved scope as "
    "`resolved-scope` in the dispatch packet. The delegate resolves scope "
    "itself ONLY when no `resolved-scope` was supplied."
)

REFUSAL_CONTRACT = (
    "A stale base, or any failure to establish freshness, REFUSES. "
    "The resolver never returns a file list it cannot vouch for, and a "
    "station that receives a refusal STOPS before dispatching anything."
)


def _text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


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


def test_pass_down_contract_transcribed_verbatim():
    """§Pinned pass-down contract appears verbatim (whitespace-normalized
    only) somewhere in Step 1 -- not paraphrased, since Task 5 writes the
    sending end of the same protocol in parallel and only an identical
    token/wording on both ends keeps the protocol wired."""
    low = _norm(_step1_window(_text()))
    assert _norm(PASS_DOWN_CONTRACT) in low, (
        "the §Pinned pass-down contract must be transcribed verbatim in "
        "Step 1, not paraphrased"
    )


def test_refusal_contract_transcribed_verbatim():
    """§Pinned refusal contract appears verbatim (whitespace-normalized
    only) somewhere in Step 1."""
    low = _norm(_step1_window(_text()))
    assert _norm(REFUSAL_CONTRACT) in low, (
        "the §Pinned refusal contract must be transcribed verbatim in "
        "Step 1, not paraphrased"
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
