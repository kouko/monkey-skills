"""Pins for copywriting-audit-stage's variant re-gating aggregation
semantics (contract/craft convergence vocabulary, plan Task 6).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions are scoped to the "Variant re-gating loop — formal
contract" section (unique anchor -> next "## " heading) so generic terms
elsewhere in the file cannot false-green a pin.

Pointer discipline: this SKILL.md POINTS at copywriting-toolkit/CLAUDE.md
§ Gate Convergence Vocabulary rather than restating the contract/craft
definitions (that transcription privilege belongs to copywriter-evaluator.md
only, per CLAUDE.md's own wording). A restatement-absence pin guards this.

Counter-mechanics discipline: the per-variant counter mechanics (clone/reset
in step 1, atomic aggregate total in step 6 + the Execution strategy
paragraph) are pinned BYTE-UNCHANGED via hardcoded verbatim strings
transcribed from the pre-edit file.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

import pytest

SKILL_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "copywriting-audit-stage"
    / "SKILL.md"
)

ANCHOR = "**Variant re-gating loop — formal contract:**"

# Verbatim counter-mechanics text, transcribed from the file BEFORE this
# task's edit. Must survive byte-unchanged.
COUNTER_MECHANICS_UNCHANGED = (
    "**Construct per-variant envelope** — clone the main envelope, replace "
    "`draft` with `rewrite_variants[i].text`, reset "
    "`retries.revise_round_count` to 0 (each variant has its own revision "
    "budget), preserve all other fields (voice_quadrant from main Phase 5 "
    "result, tone_notes from Phase 6, brief unchanged).",
    "**Per-variant revise budget**: `revise_round_count < 2` → allow "
    "auto-revise for FIXABLE at Phase 7 or 8; `>= 2` → stop for that "
    "variant.",
    "**Aggregate total_retries**: sum across main + all variants. If "
    "`total_retries >= 4` at ANY point (main audit + variant gates "
    "combined), HALT entire audit and ask user — do not silently keep "
    "re-gating.",
    "**Execution strategy** — serial by default. Parallel execution is "
    "permitted if the orchestrator supports isolated variant sub-envelopes "
    "AND guarantees `retries.total_retries` aggregation atomicity. Default "
    "to serial to keep the counter coherent.",
)

# Full contract/craft class DEFINITIONS from CLAUDE.md — must NOT be
# restated here (pointer only). copywriter-evaluator.md is the sanctioned
# transcription exception; this SKILL.md is not.
CLAUDE_MD_DEFINITION_PHRASES_NOT_RESTATED = (
    "objective checkable referent",
    "qualitative observation: affinity thickness, flow, tone nuance, "
    "positioning polish",
)


def _text() -> str:
    assert SKILL_PATH.is_file(), f"SKILL.md is absent at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def _variant_window(text: str) -> str:
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1, (
        f"anchor {ANCHOR!r} must be unique in SKILL.md, found "
        f"{len(occurrences)} occurrences"
    )
    start = occurrences[0]
    next_h2 = re.search(r"\n## ", text[start:])
    end = start + next_h2.start() if next_h2 else len(text)
    return text[start:end]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def test_variant_anchor_is_unique():
    text = _text()
    occurrences = [m.start() for m in re.finditer(re.escape(ANCHOR), text)]
    assert len(occurrences) == 1


def test_per_variant_verdicts_aggregate_contract_class_findings_only():
    # WHY: this is the core semantics change — ethics_verdict / form_verdict
    # per variant must aggregate contract-class findings only, matching the
    # canonical vocabulary (not the retired 2+ 🟡 accumulation rule).
    window = _norm(_variant_window(_text()))
    assert "contract-class findings ONLY" in window, (
        "variant verdict aggregation must state contract-class-only "
        "aggregation"
    )
    assert "ethics_verdict" in window and "form_verdict" in window


def test_craft_observations_carried_as_recorded_notes():
    # WHY: craft findings must never gate a variant verdict — they are
    # explicitly recorded into the audit report as notes instead.
    window = _norm(_variant_window(_text()))
    assert "Craft-class findings" in window
    assert "recorded notes" in window
    assert "never flip" in window or "never gate" in window


def test_pointer_to_claude_md_vocabulary_present():
    window = _variant_window(_text())
    assert "CLAUDE.md" in window
    assert "Gate Convergence Vocabulary" in window


def test_no_local_restatement_of_class_definitions():
    # WHY: audit-stage POINTS at the CLAUDE.md vocabulary; it does not
    # transcribe the full contract/craft definitions (that privilege is
    # copywriter-evaluator.md's alone, per CLAUDE.md's own wording).
    window = _norm(_variant_window(_text())).lower()
    for phrase in CLAUDE_MD_DEFINITION_PHRASES_NOT_RESTATED:
        assert phrase.lower() not in window, (
            f"full definition phrase {phrase!r} must not be restated in "
            "copywriting-audit-stage/SKILL.md"
        )


def test_no_retired_accumulation_wording():
    # WHY: the old count-based "2+ 🟡 → NEEDS_REVISION" accumulation rule
    # must not survive anywhere in this file (whole-file, on purpose).
    text = _text()
    assert not re.search(r"2\+\s*🟡", text)
    assert not re.search(r"two or more 🟡", text)


def test_counter_mechanics_byte_unchanged():
    # WHY: clone/reset (step 1), the per-variant revise budget (step 5),
    # the atomic aggregate total (step 6), and the Execution strategy
    # atomicity paragraph must survive this rewrite verbatim — only the
    # verdict-aggregation wording changes, not the counter mechanics.
    text = _text()
    for chunk in COUNTER_MECHANICS_UNCHANGED:
        assert chunk in text, f"counter-mechanics text changed or moved: {chunk!r}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
