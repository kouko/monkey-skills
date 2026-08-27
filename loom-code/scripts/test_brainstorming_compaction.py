"""Compaction oracle for the brainstorming entrypoint."""

from pathlib import Path


SKILL = Path(__file__).parents[1] / "skills" / "brainstorming" / "SKILL.md"


def test_entrypoint_preserves_gate_axes_brief_and_handoff():
    text = SKILL.read_text(encoding="utf-8")
    low = text.lower()

    # Invocation boundary, hard gate, and closed exemptions.
    for phrase in (
        "<SUBAGENT-STOP>",
        "DO NOT START IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT",
        "One-line known-pattern fix",
        "Pure refactor under existing test coverage",
        "Bug fix where the failing test already exists",
        "Explicit user override",
    ):
        assert phrase in text

    # Axis 0 is mandatory except for its narrow silent guard; backlog and
    # scaffold/on-ramp checks retain their independent behavior.
    for phrase in (
        "Walk all axes below, starting at Axis 0",
        "Negative guard (silent skip)",
        "Backlog ready check",
        "backlog_index.py --ready",
        "loom_init.py",
        "Loom-init offer:",
        "KICKOFF-DEFAULTS.md",
        "pending",
        "standalone ask",
        "user chose",
        "never re-raise",
        "using-loom-design",
    ):
        assert phrase in text

    # All discovery decisions, one-axis questioning, and bilingual evidence
    # remain inline rather than being displaced to a reference.
    for heading in (
        "Axis 1 — Problem",
        "Axis 2 — Users",
        "Axis 3 — Smallest End State",
        "Axis 4 — Alternatives Considered",
        "Axis 5 — What Becomes Obsolete",
    ):
        assert heading in text
    for phrase in (
        "at most one axis per `AskUserQuestion` call",
        "one-line state anchor",
        "Outcome, not mechanism",
        "brief-before-asking",
        "one English AND one Japanese",
        "disagreement between EN and JA is itself a finding",
        "My take: Recommend / Why / Conditional reversal",
    ):
        assert phrase in text

    # Brief schema, evidence checks, user sign-off, and path-only delegation.
    for phrase in (
        "## Output Contract — the brief",
        "## Design-side on-ramp",
        "## Problem",
        "## Users",
        "## Smallest End State",
        "## Current State Evidence",
        "Forward / Reverse / Error / Data / Boundary",
        "## Decision",
        "## Out of Scope",
        "## Queue relation",
        "## Alternatives Considered",
        "## Diagrams",
        "docs/loom/specs/<date>-<topic>.md",
        "check_field_microstructure.py --brief",
        "explicit user sign-off",
        "protocols/adjudication-view.md",
        "paths + structured seed context",
    ):
        assert phrase in text

    # UI/state and visual boundaries stay explicit.
    for phrase in (
        "Greenfield UI-state nudge",
        "empty / error / loading / state-transition / permission / boundary",
        "does **not** fire in brownfield",
        "pure-logic / data-only",
        "reminder only",
        "do not reproduce it here",
        "Active / wired",
        "ascii-graph-toolkit",
        "never hand-drawn box art",
        "Does **not** write code",
        "Does **not** make the final decision for the user",
    ):
        assert phrase in text

    assert "references/axis4-research-protocol.md" in text
    assert "references/handoff-brief-format.md" in text
    assert "references/red-flags.md" in text
    assert "references/visual-companion.md" in text
    assert "not English" not in text
    assert "side-by-side" not in text
    assert "tier 2 — deferred" not in low
