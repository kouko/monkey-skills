"""Pins for using-copywriting-toolkit/SKILL.md router validator wiring (Task 10).

Task 9 landed CLAUDE.md's `## Envelope Validation` section (the mechanics:
work-file convention, exit codes, `--prev` duty). This task wires the
ACTING-MOMENT imperative into the router's own SKILL.md — the routing loop
must instruct serialize -> validate -> proceed-on-exit-0 / STOP-on-nonzero
as something the router itself does at every stage boundary, pointing at
CLAUDE.md for the mechanics rather than restating them.

These are grep-style pins over the prose, window-scoped to the new section
so a future unrelated edit elsewhere in the file doesn't accidentally
satisfy them.

No registered REQ-ids in this dispatch -- @req tags intentionally omitted.
"""

from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "using-copywriting-toolkit"
    / "SKILL.md"
)

SECTION_HEADING = "## Envelope Validation"


def _text() -> str:
    return SKILL_MD.read_text(encoding="utf-8")


def _section() -> str:
    text = _text()
    assert SECTION_HEADING in text, "router SKILL.md is missing the new section"
    after = text.split(SECTION_HEADING, 1)[1]
    # window-scope to just this section: stop at the next top-level heading
    lines = after.splitlines()
    end = len(lines)
    for i, line in enumerate(lines):
        if line.startswith("## "):
            end = i
            break
    return "\n".join(lines[:end])


def test_validation_imperative_present_at_acting_moment():
    # WHY: the plan's ask is that the router's OWN routing loop states this
    # as an imperative it performs -- not just a cross-reference that the
    # mechanics exist somewhere else.
    section = _section()
    assert "EVERY stage boundary" in section
    assert "serializ" in section.lower()  # serializes / serialize
    assert "validate_envelope.py" in section


def test_exit_0_gate_and_stop_wording_present():
    # WHY: the CLAUDE.md contract's core rule (proceed ONLY on exit 0; any
    # non-zero is STOP and surface, never hand-repair) must be restated as
    # an instruction to the router, since the router is the actor that runs
    # the validator between every skill hand-off.
    section = _section()
    assert "exit 0" in section
    assert "STOP" in section
    assert "non-zero" in section.lower()
    assert "never hand-repair" in section.lower()


def test_prev_duty_at_seq_greater_than_1_present():
    # WHY: --prev is the single most silently-skippable step (validator
    # still exits 0 without it, just with weaker checks) -- the router text
    # must carry this as a duty at the acting moment, not leave it to be
    # inferred from CLAUDE.md alone.
    section = _section()
    assert "--prev" in section
    assert "MUST" in section
    assert "seq > 1" in section or "seq>1" in section


def test_points_at_claude_md_without_restating_mechanics():
    # WHY: plan Task 10 explicitly requires "pointer, no restatement" -- the
    # router section must send readers to CLAUDE.md for exit-code meanings
    # / work-file convention / alt-entry shape rather than duplicating that
    # prose (duplication is how the two docs drift apart).
    section = _section()
    assert "CLAUDE.md" in section
    assert "Envelope Validation" in section
    # mechanics restated in CLAUDE.md's own section that must NOT be
    # duplicated here: the full work-file template and the exit-code table
    assert "${TMPDIR:-/tmp}/copywriting-run-<run_id>/envelope-<seq>.json" not in section
    assert "phase-audit-entry" not in section
    assert "ENFORCES" not in section


def test_intro_distinguishes_the_two_validation_layers():
    """Review 🟡 (T10 quality): the intro's responsibilities list must name
    the envelope-file validation as its own duty, distinct from the
    per-skill Preconditions check — a weak orchestrator otherwise runs one
    layer and believes it satisfied both."""
    intro = _text().split(SECTION_HEADING, 1)[0]
    assert "Four responsibilities" in intro
    assert "SEPARATE layer" in intro
    assert "passing one never satisfies the other" in intro
