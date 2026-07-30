"""Guards copywriting-ethics-check-stage/SKILL.md's FIXABLE auto-revise
clause (the `PASS_WITH_NOTES` row + its neighborhood, ~:163-172) against a
worker/judge seam violation.

Per plan Task 11 (2026-07-30-copywriting-convergence-modernization.md):
FIXABLE fixes must be applied by a `copywriter` (worker) DISPATCH — never
by the orchestrating context (this SKILL.md's own execution) — and the
gate must RE-VERIFY the affected checklist items after the fix. The
evaluator's re-check, not the copywriter's revision claim, is what closes
the finding.

The prior wording ("Apply evaluator's deterministic notes ... via a brief
auto-revise turn") named no actor, leaving room for the orchestrating
context to "just edit the draft itself" and treat that edit as
self-closing the finding — exactly the writer==judge collapse this plugin's
two-agent separation (CLAUDE.md §Agents) exists to prevent. This test pins
three things: (1) an explicit worker-dispatch instruction naming the
`copywriter` agent, (2) an explicit prohibition on the orchestrating
context applying the fix directly (the polarity pin), and (3) that
re-running the gate re-verifies the affected items and the evaluator's
re-check — not the fixer's claim — is what closes the finding.

Window-scoped to "## Output — Verdict Handling" .. "## Returned Envelope"
so this cannot pass by matching unrelated prose elsewhere in the file
(e.g. the NEEDS_REVISION stop-rule section, which this task does not
touch).

No REQ-ids are registered for this dispatch; @req tags are intentionally
omitted per the implementer contract.

Stdlib + pytest only, path-based.
"""

from pathlib import Path

import pytest

SKILL_PATH = (
    Path(__file__).parents[1]
    / "skills"
    / "copywriting-ethics-check-stage"
    / "SKILL.md"
)

START_ANCHOR = "## Output — Verdict Handling"
END_ANCHOR = "## Returned Envelope"


def _text() -> str:
    assert SKILL_PATH.is_file(), f"SKILL.md is absent at {SKILL_PATH}"
    return SKILL_PATH.read_text(encoding="utf-8")


def _verdict_handling_window(text: str) -> str:
    assert text.count(START_ANCHOR) == 1, (
        f"anchor {START_ANCHOR!r} must be unique, found {text.count(START_ANCHOR)}"
    )
    assert text.count(END_ANCHOR) == 1, (
        f"anchor {END_ANCHOR!r} must be unique, found {text.count(END_ANCHOR)}"
    )
    start = text.index(START_ANCHOR)
    end = text.index(END_ANCHOR)
    assert end > start, "END_ANCHOR must follow START_ANCHOR"
    return text[start:end]


def test_anchors_are_unique_and_ordered():
    _verdict_handling_window(_text())


def test_worker_dispatch_names_copywriter_agent():
    """FIXABLE fixes must route through a real copywriter dispatch, not
    prose the orchestrating context could execute itself."""
    window = _verdict_handling_window(_text())
    assert "Dispatch the `copywriter` agent" in window


def test_orchestrator_self_apply_is_explicitly_prohibited():
    """Polarity pin: the text must NOT permit orchestrator-applied fixes
    to self-close a finding. This asserts the explicit prohibition
    sentence exists — not merely that a worker-dispatch phrase is present
    elsewhere, which alone would not rule out the orchestrator also doing
    it."""
    window = _verdict_handling_window(_text())
    assert (
        "never apply the fix directly from this orchestrating context"
        in window
    )


def test_worker_dispatch_carries_nested_dispatch_stop_path():
    """Review 🟡: in a nested-subagent context the Agent tool is absent
    AND self-apply is prohibited — without a STOP clause the instruction
    dead-ends. The copywriter dispatch must carry the same
    STOP-and-surface path as the evaluator dispatch guard."""
    window = _verdict_handling_window(_text())
    assert "STOP and surface to the parent orchestrator" in window


def test_gate_reverifies_affected_checklist_items_after_fix():
    window = _verdict_handling_window(_text())
    assert "the gate re-verifies the affected checklist items" in window


def test_evaluator_recheck_not_fixer_claim_closes_the_finding():
    window = _verdict_handling_window(_text())
    assert "closes the finding" in window
    assert "not the copywriter's revision claim" in window


def test_old_unattributed_auto_revise_phrase_is_gone():
    """The prior ambiguous phrasing (names no actor) must be fully
    replaced, not merely supplemented — otherwise a reader could still
    follow the old sentence and skip the worker dispatch."""
    text = _text()
    assert "via a brief auto-revise turn" not in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
