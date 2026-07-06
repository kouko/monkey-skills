"""Mechanical marker-grep tests for the family relay-discipline SSOT.

Task 4 (this file) writes ALL SIX assertion targets. Only
test_relay_section is expected GREEN after Task 4 — the other five stay
RED by design until Tasks 5-11 add their one-line pointers / catalog
edits to files this task must NOT touch. Each test's docstring is the
contract: the exact marker string(s) a later implementer must add,
verbatim, to flip that test green.

Canonical pointer phrase (reused by tests 2-5): every seam that relays
to the family relay SSOT must contain this exact substring somewhere in
its file — never a copy of the section body. The SSOT body lives in its
own sibling file (loom-pipeline/hooks/family-relay.md) because
family-reception.md is injected verbatim every SessionStart and is
test-pinned to ≤60 non-empty lines; reception carries only a pointer.
"""

import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

POINTER_PHRASE = "family-relay.md §Family relay discipline"

FAMILY_RECEPTION = REPO_ROOT / "loom-pipeline/hooks/family-reception.md"
FAMILY_RELAY = REPO_ROOT / "loom-pipeline/hooks/family-relay.md"
SDD_SKILL = REPO_ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"
REVIEW_SKILL = REPO_ROOT / "loom-code/skills/requesting-code-review/SKILL.md"
BRAINSTORM_VISUAL_COMPANION = REPO_ROOT / "loom-code/skills/brainstorming/references/visual-companion.md"
BRAINSTORM_HANDOFF_BRIEF = REPO_ROOT / "loom-code/skills/brainstorming/references/handoff-brief-format.md"
BRAINSTORM_SKILL = REPO_ROOT / "loom-code/skills/brainstorming/SKILL.md"
BRIEF_BEFORE_ASKING_SKILL = REPO_ROOT / "dev-workflow/skills/brief-before-asking/SKILL.md"

DESIGN_SIDE_FILES = {
    "spec": REPO_ROOT / "loom-spec/skills/using-loom-spec/SKILL.md",
    "interface-design": REPO_ROOT / "loom-interface-design/skills/using-loom-interface-design/SKILL.md",
    "product-principles": REPO_ROOT / "loom-product-principles/skills/using-loom-product-principles/SKILL.md",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_relay_section():
    """
    Markers required in loom-pipeline/hooks/family-relay.md
    (this task writes them):
      1. "## Family relay discipline"        — section heading
      2. rollup-card slot names, all five, verbatim:
         "task restated", "current state", "what changed",
         "impact on you", "next + decision"
      3. "ascii-graph-toolkit"                — visual default (flow/state)
      4. "markdown comparison table"          — visual default (>=2 options)
      5. "never bury a briefing and an AskUserQuestion" — turn-ordering rule

    Discovery path: family-reception.md (the SessionStart-injected file)
    must contain a pointer naming "family-relay.md" so readers can find
    the SSOT — the body itself stays out of reception (line budget).

    Anti-copy: the distinctive ③ rule-body phrase "Outcome, not
    mechanism." (requesting-code-review/SKILL.md ③, rule 1) must NOT
    appear in family-relay.md — this section points at the loom-code
    gate, it never copies the rule text.
    """
    text = _read(FAMILY_RELAY)
    assert "## Family relay discipline" in text

    for slot in (
        "task restated",
        "current state",
        "what changed",
        "impact on you",
        "next + decision",
    ):
        assert slot in text, f"missing rollup-card slot: {slot!r}"

    assert "ascii-graph-toolkit" in text
    assert "markdown comparison table" in text
    assert "never bury a briefing and an AskUserQuestion" in text

    assert "Outcome, not mechanism." not in text, (
        "family-relay.md must POINT at requesting-code-review's ③ "
        "gate, never copy its rule bodies"
    )

    reception = _read(FAMILY_RECEPTION)
    assert "family-relay.md" in reception, (
        "family-reception.md must point readers to family-relay.md "
        "(discovery path for the pull-on-demand SSOT)"
    )


def test_sdd_pointer():
    """
    Task 5 adds the canonical pointer phrase to BOTH narration seams in
    loom-code/skills/subagent-driven-development/SKILL.md:
      - near '### ③ How to phrase' (Asking the user seam)
      - near '## Status handling' (checkpoint sign-off seam)
    Marker: POINTER_PHRASE ("family-relay.md §Family relay
    discipline") must occur at least twice in the file — no template
    body copied in either seam.
    """
    text = _read(SDD_SKILL)
    assert text.count(POINTER_PHRASE) >= 2, (
        "expected the pointer phrase in both the ③ seam and the "
        "Status handling seam"
    )


def test_review_pointer():
    """
    Task 6 adds the canonical pointer phrase to
    loom-code/skills/requesting-code-review/SKILL.md ③ (lines ~34-56),
    signalling the verdict-relay + remediation-option seam now defers
    to the shared family relay section instead of a locally-copied rule.
    Marker: POINTER_PHRASE present at least once.
    """
    text = _read(REVIEW_SKILL)
    assert POINTER_PHRASE in text


def test_brainstorming_visuals():
    """
    Task 7 edits three files under loom-code/skills/brainstorming/:
      - references/visual-companion.md: adds "ascii-graph-toolkit" (the
        named tool for flow/state shapes) AND "channel-aware
        degradation" (the catalog's new channel-table heading/phrase)
      - references/handoff-brief-format.md: adds "channel-aware
        degradation" to its `## Diagrams` section
      - SKILL.md: adds POINTER_PHRASE near its plain-language summary
        rule (~line 181)
    """
    visual_companion = _read(BRAINSTORM_VISUAL_COMPANION)
    handoff_brief = _read(BRAINSTORM_HANDOFF_BRIEF)
    skill = _read(BRAINSTORM_SKILL)

    assert "ascii-graph-toolkit" in visual_companion
    assert "channel-aware degradation" in visual_companion
    assert "channel-aware degradation" in handoff_brief
    assert POINTER_PHRASE in skill


@pytest.mark.parametrize("skill_id", ["spec", "interface-design", "product-principles"])
def test_design_side_pointers(skill_id):
    """
    Tasks 8/9/10 each add ONE line containing POINTER_PHRASE to the
    named using-loom-* SKILL.md's §Intake section:
      spec             -> loom-spec/skills/using-loom-spec/SKILL.md
      interface-design -> loom-interface-design/skills/using-loom-interface-design/SKILL.md
      product-principles -> loom-product-principles/skills/using-loom-product-principles/SKILL.md
    """
    text = _read(DESIGN_SIDE_FILES[skill_id])
    assert POINTER_PHRASE in text


def test_brief_before_asking_ordering():
    """
    Task 11 edits dev-workflow/skills/brief-before-asking/SKILL.md:
      - turn-ordering marker: "never bury a briefing and an
        AskUserQuestion" (same phrase as the relay section, ~line 20-22)
      - anti-diagram carve-out marker: "explicit user request for a
        visual is always honored" (rescoped wording, ~lines 73/185)
    """
    text = _read(BRIEF_BEFORE_ASKING_SKILL)
    assert "never bury a briefing and an AskUserQuestion" in text
    assert "explicit user request for a visual is always honored" in text
