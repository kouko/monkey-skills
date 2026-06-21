"""Structural grep-test guarding the greenfield UI-coverage nudge that was
added to the brainstorming SKILL.md.

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing, single-subsection nudge the `extract-to-reference`
memory warns gets silently lost in prose: in greenfield / thin Current-State-
Evidence AND for a UI / interaction / stateful surface, the agent must
enumerate UI states across the six categories (empty / error / loading /
state-transition / permission / boundary) BEFORE finalizing the brief — with
an explicit gate (only greenfield + UI; NOT brownfield, NOT pure-logic), a DRY
guardrail (category reminder only; full method lives in loom-spec:
spec-expansion; do not reproduce it here), and a forward-pointer to
loom-spec:spec-expansion marked Tier 2 / deferred.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


# --- the six UI-state categories -------------------------------------------

def test_six_ui_state_categories_present():
    """All six standard UI-state category names must be enumerated."""
    low = _text().lower()
    for category in (
        "empty",
        "error",
        "loading",
        "state-transition",
        "permission",
        "boundary",
    ):
        assert category in low, f"UI-state category missing: {category}"


# --- the greenfield-AND-UI gate --------------------------------------------

def test_greenfield_and_ui_gate():
    """The nudge must fire ONLY when both conditions hold: greenfield / thin
    Current-State-Evidence AND a UI / interaction / stateful surface. The gate
    text must co-locate 'greenfield' with a UI/interaction/state-surface phrase
    and an only-when / not-brownfield guard."""
    low = _text().lower()
    assert "greenfield" in low, "gate must reference the greenfield condition"

    # find the nudge region: a window of lines around the first 'greenfield'
    # mention that also names the UI surface (the nudge), not the brief schema
    # 'N/A — greenfield' line alone.
    ui_phrases = ("interaction", "stateful", "state surface",
                  "state-surface", "interactive")
    surface_hit = bool(re.search(r"\bui\b", low)) or any(
        p in low for p in ui_phrases)
    assert surface_hit, \
        "gate must name a UI / interaction / stateful surface as a fire condition"

    # the gate must be explicit that it does NOT fire in brownfield, and not for
    # pure-logic / data-only features.
    assert "brownfield" in low, \
        "gate must explicitly exclude brownfield (recon already covers it)"
    assert "pure-logic" in low or "pure logic" in low \
        or "data feature" in low or "data-only" in low or "pure-data" in low, \
        "gate must explicitly exclude pure-logic / data features"

    # an only-when / only / not framing must be present so the nudge is gated,
    # not unconditional.
    assert "only" in low or "not in brownfield" in low or "not brownfield" in low, \
        "the nudge must be explicitly gated (only when ...), not unconditional"


def test_gate_and_categories_colocated():
    """The six categories must live in the SAME nudge region as the greenfield
    gate — guarding against the categories being mentioned somewhere unrelated
    while the gate sits elsewhere."""
    text = _text()
    low = text.lower()
    lines = low.splitlines()

    # locate the nudge: the line range spanning from the first 'greenfield'
    # gate mention that is co-located with a UI surface word, to within a
    # ~25-line window. Then assert the six categories appear inside it.
    # match "ui" only as a whole word (avoid 'required' / 'build' substrings);
    # the longer surface words can match as substrings safely.
    def _surface(line: str) -> bool:
        if re.search(r"\bui\b", line):
            return True
        return any(p in line for p in ("interaction", "stateful", "interactive"))

    nudge_start = None
    for i, line in enumerate(lines):
        if "greenfield" in line and _surface(line):
            nudge_start = i
            break
    # fall back: the heading/sentence that introduces the enumeration
    if nudge_start is None:
        for i, line in enumerate(lines):
            if "enumerate" in line and (
                "state" in line or "ui" in line
            ):
                nudge_start = i
                break
    assert nudge_start is not None, \
        "could not locate the greenfield UI-nudge region (gate + surface)"

    window = "\n".join(lines[max(0, nudge_start - 12):nudge_start + 18])
    for category in ("empty", "error", "loading", "state-transition",
                     "permission", "boundary"):
        assert category in window, \
            f"category '{category}' must sit in the same nudge region as the gate"


def test_nudge_fires_before_finalizing_brief():
    """The nudge must instruct enumerating the states BEFORE finalizing the
    brief — its timing is the whole point."""
    low = _text().lower()
    assert "before" in low, "nudge must fire BEFORE finalizing the brief"
    assert "enumerate" in low or "walk" in low or "list" in low, \
        "nudge must instruct enumerating / walking the UI states"


# --- the DRY guardrail ------------------------------------------------------

def test_dry_guardrail_reminder_only():
    """A one-line DRY guardrail: this is a category reminder only; the full
    method lives in loom-spec:spec-expansion; do NOT reproduce it here."""
    text = _text()
    low = text.lower()
    assert "loom-spec:spec-expansion" in text, \
        "DRY guardrail must name the SSOT: loom-spec:spec-expansion"
    assert "reminder" in low, \
        "guardrail must frame the nudge as a category reminder (not the method)"
    assert ("do not reproduce" in low or "don't reproduce" in low
            or "not reproduce" in low or "not duplicate" in low
            or "do not copy" in low), \
        "guardrail must forbid reproducing the full method here"
    # the full method (BVA / state-machine / permission matrix) lives there,
    # not here.
    assert "full method" in low or "full lens" in low or "full matrix" in low \
        or "method (" in low, \
        "guardrail must point at the full method living in spec-expansion"


# --- the forward-pointer ----------------------------------------------------

def test_forward_pointer_tier2_deferred():
    """A forward-pointer to loom-spec:spec-expansion for high-coverage /
    high-risk greenfield, marked Tier 2 and deferred (active once writing-plans
    reads OpenSpec change-folders)."""
    text = _text()
    low = text.lower()
    assert "loom-spec:spec-expansion" in text, \
        "forward-pointer must name loom-spec:spec-expansion"
    assert "tier 2" in low or "tier-2" in low, \
        "forward-pointer must be marked Tier 2"
    assert "defer" in low, \
        "forward-pointer must be marked deferred"
    # the deferral condition: once writing-plans reads OpenSpec change-folders
    assert "openspec" in low, \
        "forward-pointer must name the OpenSpec change-folder activation condition"


def test_forward_pointer_high_coverage_risk():
    """The forward-pointer scopes spec-expansion to high-coverage / high-risk
    greenfield (the heavyweight path), distinguishing it from the lightweight
    inline nudge."""
    low = _text().lower()
    assert "high-coverage" in low or "high coverage" in low \
        or "high-risk" in low or "high risk" in low, \
        "forward-pointer must scope spec-expansion to high-coverage / high-risk work"
