"""Structural grep-test guarding brainstorming's Axis 0 — the upstream-artifact
check that fronts the 5-axis framework (loom family connective-tissue plan,
Task E1).

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE + POSITION of a compact new subsection: "Axis 0 — Upstream artifacts
(family §Intake)" placed immediately BEFORE "Axis 1 — Problem". Axis 0 must:

1. Point at the loom family reception's on-ramp criteria table
   (`loom-code/hooks/family-reception.md`) rather than copy it — SSOT
   drift prevention (plan-level note "Reception SSOT rule").
2. On a triggered row, first honor a KICKOFF-DEFAULTS.md standing choice; otherwise
   write `pending` in the brief's `## Design-side on-ramp` line and surface
   the recommendation ONCE as a standalone ask (naming the concrete
   design-side sequence); only the user's answer is recorded — never an
   agent default, never re-raised after the answer.
3. Carry a negative-guard verbatim-equivalent: bug fix / refactor /
   test-covered increment → Axis 0 is skipped silently (no noise on
   incremental work).

These checks assert on load-bearing PHRASES (intent), tolerant of wording
variation, so the test guards meaning without being brittle.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _axis0_section() -> str:
    """Just the `### Axis 0 …` section body, up to the next `### ` heading.

    Whole-document greps false-green on a token that happens to appear
    ANYWHERE in SKILL.md — the failure this slicer exists to prevent
    (round-1 review D4: the record-choice assertion passed on an
    'offered' living in a different paragraph)."""
    text = _text()
    start = re.search(r"^###\s*Axis 0\b.*$", text, re.MULTILINE)
    assert start is not None, "Axis 0 heading missing"
    rest = text[start.end():]
    end = re.search(r"^###\s", rest, re.MULTILINE)
    return rest[: end.start()] if end else rest


# --- presence + position -----------------------------------------------


def test_axis0_heading_present_before_axis1():
    """'Axis 0' heading must exist and appear strictly before the 'Axis 1'
    heading — Axis 0 fronts the framework, it does not append to it."""
    text = _text()
    axis0_match = re.search(r"^#+\s*Axis 0\b", text, re.MULTILINE)
    axis1_match = re.search(r"^#+\s*Axis 1\b", text, re.MULTILINE)
    assert axis0_match is not None, "Axis 0 heading missing"
    assert axis1_match is not None, "Axis 1 heading missing (sibling regression)"
    assert axis0_match.start() < axis1_match.start(), \
        "Axis 0 must be positioned before Axis 1"


# --- reception reference (point, don't copy) ----------------------------


def test_axis0_references_reception_criteria():
    """Axis 0 must name the loom family reception file / label as the
    criteria SSOT — never copy the on-ramp table body into this SKILL.md."""
    text = _text()
    assert "loom-code/hooks/family-reception.md" in text or \
        "family-reception.md" in text, \
        "Axis 0 must name the reception file (point, don't copy)"
    low = text.lower()
    assert "loom family reception" in low or "family reception" in low, \
        "Axis 0 must reference 'the loom family reception' by name"


# --- queue read (dissolve-direction-layer Task 8) ------------------------


def test_axis0_reads_ready_not_direction():
    """The Backlog ready check instructs the `--ready` read only — the
    old per-repo direction-layer file's `## Now`/`## Next` read is gone
    (plan docs/loom/plans/2026-08-21-dissolve-direction-layer.md Task 8:
    that layer itself no longer exists for Axis 0 to read)."""
    axis0 = _axis0_section()
    assert "--ready" in axis0, "Axis 0 must instruct the --ready read"
    # Split so this test's own source carries no matching substring —
    # otherwise it would trip the arc sweep's own grep pattern
    # (see the arc sweep pattern in the plan's `## Notes`).
    direction_token = "DIREC" + "TION"
    assert direction_token not in axis0, \
        "Axis 0 must not instruct reading the deleted direction layer"


# --- recommend-once + record-choice --------------------------------------


def test_axis0_recommend_once_and_record_choice():
    """On a triggered row: surface the recommendation ONCE naming a concrete
    sequence, then record the USER'S OWN answer in the brief, and never
    re-raise after a decline.

    The record-choice assertions are scoped to the Axis 0 section and
    pinned to the current contract's tokens (`user chose` / `pending` /
    `standalone ask`). The previous whole-document `"offered"` grep was a
    false green — that word lives in the loom-init paragraph and would
    have stayed satisfied even if the on-ramp answer machinery vanished."""
    text = _text()
    low = text.lower()
    axis0 = _axis0_section().lower()
    assert "recommend" in low, "Axis 0 must describe surfacing a recommendation"
    assert "once" in low, "Axis 0 must state the recommendation fires ONCE"
    assert "design-side on-ramp" in low, \
        "Axis 0 must name the brief line '## Design-side on-ramp'"
    assert "user chose" in axis0, \
        "Axis 0 must record the USER's answer ('user chose <X>'), not a default"
    assert "pending" in axis0, \
        "Axis 0 must name the 'pending' state held until the user answers"
    assert "standalone ask" in axis0, \
        "Axis 0 must surface the recommendation as a standalone ask"
    assert "never re-raise" in low or "not re-raise" in low \
        or "do not re-raise" in low or "never re-ask" in low, \
        "Axis 0 must forbid re-raising the recommendation after a decline"
    # the concrete sequence must be named, not left abstract
    assert "using-loom-design" in text, \
        "Axis 0 must name a concrete station in the design-side sequence"


def test_axis0_standalone_ask_pending_no_agent_default():
    """A fired row must first check KICKOFF-DEFAULTS.md's standing choices; absent
    a standing entry, the brief line starts `pending` and the recommendation
    fires as a standalone ask — never an agent-recorded default. The old
    'proceed either way' phrasing (which let an unanswered ask sit
    unresolved) must be gone."""
    text = _text()
    low = text.lower()
    assert "standalone ask" in low, \
        "Axis 0 must fire the recommendation as a standalone ask"
    assert "pending" in low, \
        "Axis 0 must name the 'pending' brief-line state before the user answers"
    assert "standing" in low, \
        "Axis 0 must check KICKOFF-DEFAULTS.md's standing choices before asking"
    assert "kickoff-defaults.md" in low, \
        "Axis 0 must name KICKOFF-DEFAULTS.md as the standing-choice source"
    assert "proceed either way" not in low, \
        "Axis 0 must drop the old 'proceed either way' phrasing"


# --- inclusive mandate ----------------------------------------------------


def test_mandate_includes_axis0():
    """The framework's walk mandate must include Axis 0 — the document may
    keep '5-axis' as the framework's historical name, but the count language
    ('walk all five', 'the 5 axes below') must not structurally exclude
    Axis 0 from the mandatory walk."""
    text = _text()
    assert "Walk all axes below, starting at Axis 0" in text, \
        "mandate must be inclusive: 'Walk all axes below, starting at Axis 0'"
    # the frontmatter description must surface the Axis-0 upstream gate too
    frontmatter = text.split("---")[1]
    assert "Axis 0" in frontmatter, \
        "frontmatter description must mention the Axis-0 upstream gate"
    # the old exclusive count-mandate must be gone
    assert "Walk all five. Don't skip any." not in text, \
        "the old five-only walk mandate must be replaced by the inclusive one"


# --- negative guard -------------------------------------------------------


def test_axis0_negative_guard_silent_skip():
    """Bug fix / refactor / test-covered increment → Axis 0 is skipped
    silently — no noise on incremental work."""
    text = _text()
    low = text.lower()
    assert "bug fix" in low, "negative guard must name bug fix"
    assert "refactor" in low, "negative guard must name refactor"
    assert "test-covered increment" in low or "test covered increment" in low, \
        "negative guard must name test-covered increment"
    assert "silently" in low, \
        "negative guard must state the skip happens SILENTLY (no noise)"


# --- router (using-loom-code) red-flag + family pointer (Task E2) ---------

ROUTER = Path(__file__).parents[1] / "skills" / "using-loom-code" / "SKILL.md"

# using-loom-code/SKILL.md line count immediately before Task E2 (measured
# `wc -l` on the untouched file). This file is hook-injected every session,
# so its net growth is capped at 15 lines — test-asserted against this fixed
# baseline rather than a moving git ref.
_ROUTER_BASELINE_LINES = 114
_ROUTER_GROWTH_CAP = 15


def _router_text() -> str:
    assert ROUTER.is_file(), f"using-loom-code/SKILL.md is absent at {ROUTER}"
    return ROUTER.read_text(encoding="utf-8")


def test_router_axis0_red_flag():
    """using-loom-code/SKILL.md must:
    (a) carry a red-flag row naming skipping brainstorming's Axis 0 upstream
        check before writing a brief as a violation;
    (b) point to the loom family reception (loom-code's SessionStart
        hook) as the family map + on-ramp criteria SSOT;
    (c) update rule #1's '5-axis framework' mention with one clause noting
        the walk now starts at Axis 0, without rewriting the rule;
    and stay within the ≤15 net-line-growth cap (this file is hook-injected
    every session)."""
    text = _router_text()
    low = text.lower()

    # (a) red-flag row: a single line names both Axis 0 and "brief", and
    # calls the skip out as a violation.
    axis0_red_flag_lines = [
        line for line in text.splitlines()
        if "axis 0" in line.lower() and "brief" in line.lower()
    ]
    assert axis0_red_flag_lines, \
        "no line names both Axis 0 and 'brief' together (expected red-flag row)"
    assert any("violation" in line.lower() for line in axis0_red_flag_lines), \
        "the Axis 0 red-flag row must call the skip a violation"

    # (b) family pointer — loom-code reception as the family map SSOT,
    # attributed to the SessionStart hook mechanism.
    assert "loom-code" in text, \
        "router must point to loom-code (the reception's home plugin)"
    assert "family reception" in low or "family-reception.md" in text, \
        "router must name the loom family reception by name/path"
    assert "sessionstart" in low or "session-start" in low, \
        "router must attribute the reception to the SessionStart hook mechanism"

    # (c) rule #1 update: historical-name clause on the SAME rule, not a
    # rewrite.
    rule1_match = re.search(
        r"^1\.\s+\*\*Brainstorm before implementing\.\*\*.*$", text, re.MULTILINE
    )
    assert rule1_match is not None, \
        "rule #1 ('Brainstorm before implementing') must still exist unrewritten"
    rule1_low = rule1_match.group(0).lower()
    assert "axis 0" in rule1_low, \
        "rule #1 must mention Axis 0 (the walk now starts there)"
    assert "5-axis" in rule1_low or "5 axis" in rule1_low, \
        "rule #1 must retain '5-axis' as the framework's historical name"

    # net-growth cap
    current_lines = len(text.splitlines())
    growth = current_lines - _ROUTER_BASELINE_LINES
    assert growth <= _ROUTER_GROWTH_CAP, (
        f"using-loom-code/SKILL.md grew by {growth} lines "
        f"(baseline {_ROUTER_BASELINE_LINES} -> {current_lines}); "
        f"cap is {_ROUTER_GROWTH_CAP} (hook-injected every session)"
    )
