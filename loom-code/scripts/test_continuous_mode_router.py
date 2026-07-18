"""Structural grep-test guarding the opt-in "Continuous mode" convention.

Continuous mode is SessionStart-hook-injected via the using-loom-code router,
so the router body is token-budgeted (~2000 tokens). The full Continuous-mode
doctrine therefore lives in `references/continuous-mode.md`; the router body
carries only a short STUB (what it is + entry precondition + a MANDATORY
loading trigger + a one-line invariant pointer).

Correctness is the PRESENCE of the load-bearing convention + stop contract
described in `docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md`:
spec-frozen (NOT plan-frozen) entry, design/spec stay human-gated while the
plan is auto-generated + gated, an explicit stop contract (every trigger row
of the spec's table), a crutch-vs-verification line forbidding
re-plan/re-scope/re-route, two-layer escalation (stop-and-wait baseline +
optional proactive push that degrades gracefully), and an opt-in
continuous-mode exception amended onto the router's "does not auto-invoke
downstream skills" caveat.

After the structural refactor the FULL doctrine is asserted against the
REFERENCE (`references/continuous-mode.md`); the router STUB is asserted to
name continuous mode, carry the mandatory loading trigger, and point at the
never-auto-merge invariant. No invariant is lost — each is asserted somewhere.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation (lowercase substring / regex), so the test guards MEANING without
being brittle — but each assertion targets a real phrase from the contract.

Stdlib only (pathlib + re). Resolve files relative to this test file.
"""

import re
from pathlib import Path

_SKILLS = Path(__file__).parents[1] / "skills" / "using-loom-code"
SKILL = _SKILLS / "SKILL.md"
REF = _SKILLS / "references" / "continuous-mode.md"


def _skill() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _ref() -> str:
    assert REF.is_file(), f"continuous-mode.md reference is absent at {REF}"
    return REF.read_text(encoding="utf-8")


def test_skill_md_exists():
    """Guard: the router SKILL.md must exist where we expect it."""
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"


def test_reference_exists():
    """Guard: the relocated Continuous-mode doctrine reference must exist."""
    assert REF.is_file(), f"continuous-mode.md reference is absent at {REF}"


def test_reference_is_single_level():
    """The reference is a single-level file directly under references/ —
    no nested directory (Anthropic flat-subfolder skill convention)."""
    assert REF.parent.name == "references", \
        "continuous-mode.md must live directly under references/, not nested"
    assert REF.parent.parent == _SKILLS, \
        "references/ must sit directly under the skill dir (single level)"


# --- STUB (router body) assertions -----------------------------------------

def test_stub_names_continuous_mode_and_opt_in():
    """The router body STUB must name continuous mode AND mark it opt-in
    (the default stays human-pumped)."""
    low = _skill().lower()
    assert "continuous mode" in low, \
        "the router body stub must name 'continuous mode'"
    assert "opt-in" in low or "opt in" in low, \
        "continuous mode must be marked opt-in (not a changed default)"


def test_stub_has_mandatory_loading_trigger():
    """The STUB must carry a MANDATORY trigger to READ the reference IN FULL
    before auto-advancing — orphan-reference prevention."""
    low = _skill().lower()
    assert "references/continuous-mode.md" in low, \
        "the stub must point at references/continuous-mode.md"
    assert "in full" in low, \
        "the stub must require reading the reference IN FULL"
    assert ("read references/continuous-mode.md" in low
            or re.search(r"read .{0,40}continuous-mode\.md", low)), \
        "the stub must instruct READING the reference before auto-advancing"


def test_stub_entry_precondition_present():
    """The STUB must state the entry precondition: a human-approved frozen
    brief OR a validated change-folder."""
    low = _skill().lower()
    assert ("frozen" in low and "brief" in low) or "change-folder" in low \
        or "change folder" in low, \
        "the stub must state the entry precondition (frozen brief OR change-folder)"
    assert "human-approved" in low or "human approved" in low \
        or "human-gated" in low or "human gated" in low, \
        "the stub entry precondition must reference human approval"


def test_stub_invariant_pointer_never_auto_merge():
    """The STUB must carry the one-line invariant pointer: never auto-merge;
    HALT on re-plan/re-scope/re-route; PR-open is terminal."""
    low = _skill().lower()
    assert "never auto-merge" in low or "never auto merge" in low, \
        "the stub must point at the never-auto-merge invariant"
    assert "halt" in low, "the stub must point at the HALT-on-deviation invariant"


# --- 1. the reference exists and is opt-in ---------------------------------

def test_continuous_mode_section_is_opt_in():
    """The reference must mark continuous mode opt-in (default human-pumped)."""
    low = _ref().lower()
    assert "continuous mode" in low, \
        "a 'continuous mode' section must exist in the reference"
    assert "opt-in" in low or "opt in" in low, \
        "continuous mode must be marked opt-in (not a changed default)"


# --- 2. entry / freeze at the spec, human-gated design, auto-gated plan -----

def test_entry_freezes_spec_not_plan():
    """Entry references a frozen SPEC (not plan) as the entry point."""
    low = _ref().lower()
    assert re.search(r"frozen\s+spec", low) or re.search(r"spec[-\s]*frozen", low) \
        or re.search(r"spec.{0,30}freeze", low), \
        "entry must reference a frozen SPEC as the entry point"


def test_design_and_spec_stay_human_gated():
    """Design + spec remain human-gated (the approach is locked by a human)."""
    low = _ref().lower()
    assert "human-gated" in low or "human gated" in low \
        or "human-approved" in low or "human approved" in low \
        or "sign-off" in low or "sign off" in low, \
        "design/spec must stay human-gated / human-approved"


def test_plan_is_auto_generated_and_gated():
    """The plan is auto-generated AND gated (not a mandatory human checkpoint
    — it is one more auto-advance-with-gate stage)."""
    low = _ref().lower()
    assert ("auto-generate" in low or "auto-generated" in low
            or "automatable" in low or "auto-advance" in low), \
        "the plan must be described as auto-generated / auto-advanced"
    assert "plan gate" in low or "plan-document-reviewer" in low \
        or re.search(r"plan.{0,20}gate", low), \
        "the plan stage must still be gated"


# --- 3. stop-contract trigger terms (every row of the spec table) ----------

def test_stop_contract_blocked_trigger():
    """Row 1: implementer returns BLOCKED."""
    assert "BLOCKED" in _ref(), "stop contract must include the BLOCKED trigger"


def test_stop_contract_plan_depth_routeback():
    """Row 0a: plan critical-path depth >5 → route back."""
    text = _ref()
    low = text.lower()
    assert "depth" in low, "stop contract must reference plan critical-path depth"
    assert ">5" in text or "> 5" in text or "depth >" in low \
        or "exceeds 5" in low or "more than 5" in low, \
        "stop contract must reference the depth >5 threshold"
    assert "route" in low or "route-back" in low or "route back" in low \
        or "re-cut" in low, \
        "depth trigger must route back / re-cut the spec"


def test_stop_contract_plan_reviewer_two_rounds():
    """Row 0b: plan-document-reviewer NEEDS_REVISION for 2 rounds."""
    low = _ref().lower()
    assert "plan-document-reviewer" in low, \
        "stop contract must reference plan-document-reviewer"
    assert "2 rounds" in low or "two rounds" in low or "2-round" in low \
        or "2 round" in low or "two-round" in low, \
        "plan-reviewer trigger must reference the 2-round cap"


def test_stop_contract_review_revision_loop_bound():
    """Row 2a: review-revision loop has a round-trip bound.

    Scoped to Row-2a-distinct phrasing (review-revision / round-trip /
    reviewer↔implementer)."""
    low = _ref().lower()
    assert ("review-revision" in low or "review revision" in low
            or "round-trip" in low or "round trip" in low
            or "reviewer↔implementer" in low or "reviewer ↔ implementer" in low
            or "reviewer<->implementer" in low), \
        "stop contract must name the review-revision (reviewer↔implementer) loop"
    assert re.search(r"2\s*(reviewer|round|round-trip|round trip)", low) \
        or "two round-trip" in low or "two round trip" in low \
        or "2 round-trips" in low or "2 round trips" in low, \
        "the review-revision loop must be bounded by a round-trip count"


def test_stop_contract_review_revision_deliberate_slack_note():
    """Row 2a: the 2-round halt is deliberately one round earlier than SDD's
    3-round cap (no human pumping the loop -> slack handed back sooner), and
    continuous-mode.md cross-references SDD's cap section by name (mirrors
    the wording SDD's SKILL.md already carries pointing back at this file)."""
    low = _ref().lower()
    assert "one round earlier" in low or "1 round earlier" in low, \
        "must state the 2-round halt is deliberately one round earlier than SDD's cap"
    assert "3-round cap" in low or "three-round cap" in low or "3 round cap" in low, \
        "must name SDD's 3-round cap being referenced"
    assert "no human" in low and ("pumping" in low or "pump" in low), \
        "must carry the rationale: no human is pumping the loop"
    assert "subagent-driven-development" in low, \
        "must cross-reference subagent-driven-development by name (mirrors SDD's pointer back here)"


def test_stop_contract_debug_websearch_anchored_guard():
    """Row 2b: debug loop (systematic-debugging exhausts) is a stop trigger
    that reuses the Anchored-thinking guard / mandatory WebSearch."""
    low = _ref().lower()
    assert ("debug loop" in low or "debug-loop" in low), \
        "stop contract must name the debug loop as a stop trigger"
    assert ("exhaust" in low or "falsified" in low or "still falsified" in low
            or "hypothesis #3" in low or "hypothesis 3" in low
            or "third hypothesis" in low), \
        "the debug-loop trigger must fire when the loop exhausts (anchored-thinking guard)"
    assert "websearch" in low or "web search" in low, \
        "debug-loop trigger must reference the mandatory WebSearch step"
    assert "anchored" in low or "anchored-thinking" in low \
        or "systematic-debugging" in low or "hypothesis" in low, \
        "debug-loop trigger must reference the anchored-thinking guard"


def test_stop_contract_scope_decision_not_specified():
    """Row 3: a scope / decision the plan/spec did not specify arises."""
    low = _ref().lower()
    assert "scope" in low and (
        "not specified" in low or "did not specify" in low
        or "didn't specify" in low or "unspecified" in low), \
        "stop contract row 3 must trigger on a scope/decision the plan did not specify"


def test_stop_contract_self_declared_assumption():
    """Row 4: the agent self-declares an assumption outside plan/spec."""
    low = _ref().lower()
    assert "assumption" in low, \
        "stop contract must trigger on a self-declared assumption"
    assert "self-declare" in low or "self declare" in low \
        or "self-declared" in low or "declare" in low, \
        "the assumption trigger must be an honest self-declaration"


def test_stop_contract_whole_branch_needs_revision_stops():
    """Row 5: whole-branch review = NEEDS_REVISION → direct stop."""
    text = _ref()
    low = text.lower()
    assert "whole-branch" in low or "whole branch" in low, \
        "stop contract must reference whole-branch review"
    assert "NEEDS_REVISION" in text, \
        "whole-branch trigger must reference NEEDS_REVISION"


def test_stop_contract_pass_with_notes_auto_advances():
    """Row 6: PASS_WITH_NOTES → auto-advance + accumulate notes."""
    text = _ref()
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
    text = _ref()
    low = text.lower()
    assert "PR" in text, "stop contract must reach a PR-open terminal stop"
    assert "never auto-merge" in low or "never auto merge" in low \
        or "not auto-merge" in low or "auto-merge" in low, \
        "PR stop must state never-auto-merge (human merges)"


# --- 4. crutch line: forbids re-plan / re-scope / re-route -----------------

def test_crutch_line_forbids_replan_rescope_reroute():
    """The crutch-vs-verification line forbids re-plan / re-scope / re-route
    (auto-advance must NOT do these — they are stop conditions)."""
    low = _ref().lower()
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
    low = _ref().lower()
    assert "stop-and-wait" in low or "stop and wait" in low \
        or "halt" in low, \
        "escalation must have a stop-and-wait baseline"
    assert "proactive" in low or "push notification" in low \
        or "pushnotification" in low or "notify" in low \
        or "notification" in low, \
        "escalation must have an optional proactive notification layer"
    assert "degrade" in low or "degrades gracefully" in low \
        or "gracefully" in low or "fall back" in low or "falls back" in low \
        or "fallback" in low, \
        "the proactive layer must degrade gracefully (not a hard dependency)"


# --- 6. router caveat carries the opt-in continuous-mode exception ----------

def test_router_caveat_has_continuous_mode_exception():
    """The router's 'does not auto-invoke downstream skills' caveat must
    carry an explicit opt-in continuous-mode exception. Assert BOTH the
    original caveat phrase AND a nearby opt-in / continuous-mode exception
    token are present (this stays in the router body)."""
    text = _skill()
    low = text.lower()
    assert "does not auto-invoke downstream skills" in low \
        or re.search(r"does\s+\W*not\W*\s*auto-invoke downstream skills", low), \
        "the original 'does not auto-invoke downstream skills' caveat must remain"
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
