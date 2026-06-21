"""Structural grep-test guarding the opt-in "Continuous mode" section that
will be added to the using-loom-code router SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing convention + stop contract described in
`docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md`:
spec-frozen (NOT plan-frozen) entry, design/spec stay human-gated while the
plan is auto-generated + gated, an explicit stop contract (every trigger row
of the spec's table), a crutch-vs-verification line forbidding
re-plan/re-scope/re-route, two-layer escalation (stop-and-wait baseline +
optional proactive push that degrades gracefully), and an opt-in
continuous-mode exception amended onto the router's "does not auto-invoke
downstream skills" caveat.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation (lowercase substring / regex), so the test guards MEANING without
being brittle — but each assertion targets a real phrase from the contract.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.

This test is RED until the Continuous-mode section is written (Task 2).
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "using-loom-code" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_skill_md_exists():
    """Guard: the router SKILL.md must exist where we expect it."""
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"


# --- 1. the section exists and is opt-in -----------------------------------

def test_continuous_mode_section_is_opt_in():
    """A 'continuous mode' section must exist AND be marked opt-in (default
    stays human-pumped)."""
    low = _text().lower()
    assert "continuous mode" in low, \
        "a 'continuous mode' section must exist in the router"
    assert "opt-in" in low or "opt in" in low, \
        "continuous mode must be marked opt-in (not a changed default)"


# --- 2. entry / freeze at the spec, human-gated design, auto-gated plan -----

def test_entry_freezes_spec_not_plan():
    """Entry references a frozen SPEC (not plan) as the entry point."""
    low = _text().lower()
    # a frozen spec must be named as the entry point
    assert re.search(r"frozen\s+spec", low) or re.search(r"spec[-\s]*frozen", low) \
        or re.search(r"spec.{0,30}freeze", low), \
        "entry must reference a frozen SPEC as the entry point"


def test_design_and_spec_stay_human_gated():
    """Design + spec remain human-gated (the approach is locked by a human)."""
    low = _text().lower()
    assert "human-gated" in low or "human gated" in low \
        or "human-approved" in low or "human approved" in low \
        or "sign-off" in low or "sign off" in low, \
        "design/spec must stay human-gated / human-approved"


def test_plan_is_auto_generated_and_gated():
    """The plan is auto-generated AND gated (not a mandatory human checkpoint
    — it is one more auto-advance-with-gate stage)."""
    low = _text().lower()
    # the plan is generated automatically ...
    assert ("auto-generate" in low or "auto-generated" in low
            or "automatable" in low or "auto-advance" in low), \
        "the plan must be described as auto-generated / auto-advanced"
    # ... and still gated (plan gate)
    assert "plan gate" in low or "plan-document-reviewer" in low \
        or re.search(r"plan.{0,20}gate", low), \
        "the plan stage must still be gated"


# --- 3. stop-contract trigger terms (every row of the spec table) ----------

def test_stop_contract_blocked_trigger():
    """Row 1: implementer returns BLOCKED."""
    assert "BLOCKED" in _text(), "stop contract must include the BLOCKED trigger"


def test_stop_contract_plan_depth_routeback():
    """Row 0a: plan critical-path depth >5 → route back."""
    low = _text().lower()
    assert "depth" in low, "stop contract must reference plan critical-path depth"
    assert ">5" in _text() or "> 5" in _text() or "depth >" in low \
        or "exceeds 5" in low or "more than 5" in low, \
        "stop contract must reference the depth >5 threshold"
    assert "route" in low or "route-back" in low or "route back" in low \
        or "re-cut" in low, \
        "depth trigger must route back / re-cut the spec"


def test_stop_contract_plan_reviewer_two_rounds():
    """Row 0b: plan-document-reviewer NEEDS_REVISION for 2 rounds."""
    text = _text()
    low = text.lower()
    assert "plan-document-reviewer" in low, \
        "stop contract must reference plan-document-reviewer"
    assert "2 rounds" in low or "two rounds" in low or "2-round" in low \
        or "2 round" in low or "two-round" in low, \
        "plan-reviewer trigger must reference the 2-round cap"


def test_stop_contract_review_revision_loop_bound():
    """Row 2a: review-revision loop has a round-trip bound.

    Scoped to Row-2a-distinct phrasing (review-revision / round-trip /
    reviewer↔implementer) that does NOT pre-exist in the router, so this test
    is RED until the stop-contract row is written. The bare `reviewer`+`round`
    tokens are deliberately NOT accepted — they already appear elsewhere (SDD
    reviewers; Row 0b's "2 rounds") and would make this a no-op guard."""
    low = _text().lower()
    # the review-revision loop concept (Row-2a-specific, absent today)
    assert ("review-revision" in low or "review revision" in low
            or "round-trip" in low or "round trip" in low
            or "reviewer↔implementer" in low or "reviewer ↔ implementer" in low
            or "reviewer<->implementer" in low), \
        "stop contract must name the review-revision (reviewer↔implementer) loop"
    # ... and a round-trip count bounding it
    assert re.search(r"2\s*(reviewer|round|round-trip|round trip)", low) \
        or "two round-trip" in low or "two round trip" in low \
        or "2 round-trips" in low or "2 round trips" in low, \
        "the review-revision loop must be bounded by a round-trip count"


def test_stop_contract_debug_websearch_anchored_guard():
    """Row 2b: debug loop (systematic-debugging exhausts) is a stop trigger
    that reuses the Anchored-thinking guard / mandatory WebSearch.

    Scoped to Row-2b-distinct phrasing (a 'debug loop' framed as a stop
    trigger that EXHAUSTS / is falsified) so it cannot pass on the router's
    pre-existing incidental `websearch` (L20) / `systematic-debugging` (L52/78)
    tokens. RED until the stop-contract row is written."""
    low = _text().lower()
    # Row-2b-distinct framing: a debug loop that exhausts / is exhausted as a
    # stop trigger (this phrasing is absent from the router today).
    assert ("debug loop" in low or "debug-loop" in low), \
        "stop contract must name the debug loop as a stop trigger"
    assert ("exhaust" in low or "falsified" in low or "still falsified" in low
            or "hypothesis #3" in low or "hypothesis 3" in low
            or "third hypothesis" in low), \
        "the debug-loop trigger must fire when the loop exhausts (anchored-thinking guard)"
    # and it must reuse the existing WebSearch / anchored-thinking machinery
    assert "websearch" in low or "web search" in low, \
        "debug-loop trigger must reference the mandatory WebSearch step"
    assert "anchored" in low or "anchored-thinking" in low \
        or "systematic-debugging" in low or "hypothesis" in low, \
        "debug-loop trigger must reference the anchored-thinking guard"


def test_stop_contract_scope_decision_not_specified():
    """Row 3: a scope / decision the plan/spec did not specify arises.

    Pinned to the brief's load-bearing phrasing ("the plan did not specify")
    plus the scope/decision subject — NOT the cosmetic "(not in the spec)"
    parenthetical, so the guard fails on a semantic change, not a wording tweak."""
    low = _text().lower()
    assert "scope" in low and (
        "not specified" in low or "did not specify" in low
        or "didn't specify" in low or "unspecified" in low), \
        "stop contract row 3 must trigger on a scope/decision the plan did not specify"


def test_stop_contract_self_declared_assumption():
    """Row 4: the agent self-declares an assumption outside plan/spec."""
    low = _text().lower()
    assert "assumption" in low, \
        "stop contract must trigger on a self-declared assumption"
    assert "self-declare" in low or "self declare" in low \
        or "self-declared" in low or "declare" in low, \
        "the assumption trigger must be an honest self-declaration"


def test_stop_contract_whole_branch_needs_revision_stops():
    """Row 5: whole-branch review = NEEDS_REVISION → direct stop."""
    text = _text()
    low = text.lower()
    assert "whole-branch" in low or "whole branch" in low, \
        "stop contract must reference whole-branch review"
    assert "NEEDS_REVISION" in text, \
        "whole-branch trigger must reference NEEDS_REVISION"


def test_stop_contract_pass_with_notes_auto_advances():
    """Row 6: PASS_WITH_NOTES → auto-advance + accumulate notes."""
    text = _text()
    low = text.lower()
    assert "PASS_WITH_NOTES" in text, \
        "stop contract must reference PASS_WITH_NOTES"
    assert "auto-advance" in low or "auto advance" in low, \
        "PASS_WITH_NOTES must auto-advance (not stop)"
    assert "accumulate" in low or "accrue" in low or "surface them" in low \
        or "surface all" in low, \
        "PASS_WITH_NOTES notes must be accumulated / surfaced at the PR"


def test_stop_contract_pr_open_never_auto_merge():
    """Row 7: PR-open is the terminal stop; never auto-merge."""
    text = _text()
    low = text.lower()
    assert "PR" in text, "stop contract must reach a PR-open terminal stop"
    assert "never auto-merge" in low or "never auto merge" in low \
        or "not auto-merge" in low or "auto-merge" in low, \
        "PR stop must state never-auto-merge (human merges)"


# --- 4. crutch line: forbids re-plan / re-scope / re-route -----------------

def test_crutch_line_forbids_replan_rescope_reroute():
    """The crutch-vs-verification line forbids re-plan / re-scope / re-route
    (auto-advance must NOT do these — they are stop conditions)."""
    low = _text().lower()
    assert "re-plan" in low or "replan" in low or "re plan" in low, \
        "crutch line must forbid re-plan"
    assert "re-scope" in low or "rescope" in low or "re scope" in low, \
        "crutch line must forbid re-scope"
    assert "re-route" in low or "reroute" in low or "re route" in low, \
        "crutch line must forbid re-route"


# --- 5. two-layer escalation -----------------------------------------------

def test_escalation_is_two_layer():
    """Escalation is two-layer: a stop-and-wait baseline AND an optional
    proactive notification that degrades gracefully."""
    low = _text().lower()
    # baseline: stop and wait + a why-I-stopped message
    assert "stop-and-wait" in low or "stop and wait" in low \
        or "halt" in low, \
        "escalation must have a stop-and-wait baseline"
    # optional proactive push
    assert "proactive" in low or "push notification" in low \
        or "pushnotification" in low or "notify" in low \
        or "notification" in low, \
        "escalation must have an optional proactive notification layer"
    # graceful degradation when the host lacks the capability
    assert "degrade" in low or "degrades gracefully" in low \
        or "gracefully" in low or "fall back" in low or "falls back" in low \
        or "fallback" in low, \
        "the proactive layer must degrade gracefully (not a hard dependency)"


# --- 6. router caveat carries the opt-in continuous-mode exception ----------

def test_router_caveat_has_continuous_mode_exception():
    """The router's 'does not auto-invoke downstream skills' caveat must
    carry an explicit opt-in continuous-mode exception. Assert BOTH the
    original caveat phrase AND a nearby opt-in / continuous-mode exception
    token are present."""
    text = _text()
    low = text.lower()
    # original caveat phrase still present
    assert "does not auto-invoke downstream skills" in low \
        or re.search(r"does\s+\W*not\W*\s*auto-invoke downstream skills", low), \
        "the original 'does not auto-invoke downstream skills' caveat must remain"
    # the amended exception: the caveat line must sit near a continuous-mode /
    # opt-in exception token (same ~6-line window).
    lines = low.splitlines()
    caveat_idx = None
    for i, line in enumerate(lines):
        if "auto-invoke downstream skills" in line:
            caveat_idx = i
            break
    assert caveat_idx is not None, "could not locate the auto-invoke caveat line"
    window = "\n".join(lines[max(0, caveat_idx - 3):caveat_idx + 4])
    assert "continuous mode" in window or "continuous-mode" in window \
        or "opt-in" in window or "exception" in window, \
        "the caveat must carry an opt-in continuous-mode exception nearby"
