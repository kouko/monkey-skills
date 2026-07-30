"""Pins for copywriting-toolkit/CLAUDE.md §Envelope Validation (Task 9).

Task 8 shipped `scripts/validate_envelope.py` as the file-borne enforcement
medium for the handoff envelope; this task wires that contract into
CLAUDE.md so the prose that used to only WARN about counters/immutability
now POINTS at the mechanical check. These are grep-style pins over the
prose, not a schema check — they exist so a future edit can't silently
drop the MUST language, the work-file convention, the `--prev` duty, or
the flipped deferred-sync-script note.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

from pathlib import Path

CLAUDE_MD = Path(__file__).resolve().parent.parent / "CLAUDE.md"


def _text() -> str:
    return CLAUDE_MD.read_text(encoding="utf-8")


def test_envelope_validation_section_exists_with_must_language():
    # WHY: the brief's core ask is that this becomes a MUST, not a
    # suggestion — the section must name the acting moment (every stage
    # boundary), the actor (orchestrator serializes + runs the validator),
    # and the exit-0 gate explicitly.
    text = _text()
    assert "## Envelope Validation" in text
    section = text.split("## Envelope Validation", 1)[1].split("\n## ", 1)[0]
    assert "every stage boundary" in section.lower() or "EVERY stage boundary" in section
    assert "validate_envelope.py" in section
    assert "exit 0" in section
    assert "STOP" in section
    assert "never hand-repair the envelope silently" in section


def test_work_file_convention_stated():
    # WHY: without a fixed path convention, orchestrators would each invent
    # their own scratch location and --prev couldn't reliably name "the
    # previous stage-boundary file" — this pins the exact template string.
    text = _text()
    assert "${TMPDIR:-/tmp}/copywriting-run-<run_id>/envelope-<seq>.json" in text
    assert "run_id" in text
    assert "minted at intake" in text or "mints" in text


def test_prev_is_must_for_seq_greater_than_1():
    # WHY: validate_envelope.py's counter-monotonicity / immutable-field /
    # append-only checks (exit 4/5/6) only fire when --prev is supplied —
    # calling it single-file at seq>1 silently SKIPS those classes. The
    # doc must make --prev a MUST, not an option, once seq>1.
    text = _text()
    section = text.split("## Envelope Validation", 1)[1].split("\n## ", 1)[0]
    assert "--prev" in section
    assert "MUST" in section
    # the seq>1 condition must be named explicitly, not left implicit
    assert "seq > 1" in section or "seq>1" in section or "seq 1" in section


def test_counter_enforcement_warnings_point_to_validator():
    # WHY: the existing "Monotonic — counters only increment" table row and
    # the "Do NOT omit retries" caller warning were prose-only claims with
    # no enforcement path named. This pin fails if the doc still just
    # describes the behavior without naming the validator as what actually
    # checks it.
    text = _text()
    assert "Monotonic — counters only increment" in text  # original prose preserved
    section = text.split("## Envelope Validation", 1)[1].split("\n## ", 1)[0]
    assert "ENFORCES" in section or "enforces" in section
    assert "retries" in section.lower()


def test_deferred_sync_script_note_flipped():
    # WHY: the old note deferred the anchor-copy sync check indefinitely
    # ("If drift observed later, a sync script is acceptable"). Task 13
    # shipped that script (scripts/check_anchor_copies.py, commit
    # 7d064a4c) — the note must now point at it, not defer it.
    text = _text()
    assert "If drift observed later, a sync script is acceptable" not in text
    assert "check_anchor_copies.py" in text
    assert "7d064a4c" in text


def test_alt_entry_minimal_shape_interaction_stated():
    # WHY: alt-entry envelopes (phase-audit-entry) validate with the SAME
    # script under a relaxed schema shape (express_mode_used omissible) —
    # this must be stated so a caller doesn't assume alt-entry needs a
    # separate validation path.
    text = _text()
    section = text.split("## Envelope Validation", 1)[1].split("\n## ", 1)[0]
    assert "phase-audit-entry" in section
    assert "express_mode_used" in section
    assert "omissible" in section
    assert "same script" in section.lower()
