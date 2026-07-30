"""Pins for the copywriter-evaluator contract (contract/craft classes +
prior_findings_check round-2 duty).

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
presence assertions are scoped to the evaluator section extracted by its unique
heading anchor — never whole-file — so generic terms elsewhere cannot
false-green a pin. The whole-file assertion is the ABSENCE pin (retired
"2+ 🟡 → NEEDS_REVISION" accumulation rule must not survive anywhere).

Side-by-side discipline: phrases the evaluator TRANSCRIBES from the canonical
vocabulary (copywriting-toolkit/CLAUDE.md § Gate Convergence Vocabulary) are
asserted in BOTH files — a drifted restatement fails the pin.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALUATOR_MD = ROOT / "agents" / "copywriter-evaluator.md"
CLAUDE_MD = ROOT / "CLAUDE.md"

VOCAB_HEADING = "## Gate Convergence Vocabulary"


def _evaluator() -> str:
    return EVALUATOR_MD.read_text(encoding="utf-8")


def _claude_vocab() -> str:
    """The canonical vocabulary section of CLAUDE.md (heading → next H2)."""
    text = CLAUDE_MD.read_text(encoding="utf-8")
    start = text.find(VOCAB_HEADING)
    assert start != -1, f"canonical heading {VOCAB_HEADING!r} absent from CLAUDE.md"
    nxt = text.find("\n## ", start + len(VOCAB_HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def _norm(s: str) -> str:
    """Collapse whitespace so markdown hard-wrapping cannot break a verbatim
    phrase match — side-by-side means identical wording, not identical wrapping."""
    return re.sub(r"\s+", " ", s)


def _window(heading: str, terminators=("\n## ",)) -> str:
    """Evaluator window: from a unique heading to the next section heading."""
    text = _evaluator()
    start = text.find(heading)
    assert start != -1, f"heading {heading!r} absent from copywriter-evaluator.md"
    ends = [
        i
        for t in terminators
        if (i := text.find(t, start + len(heading))) != -1
    ]
    return text[start : min(ends)] if ends else text[start:]


# Phrases shared verbatim between CLAUDE.md vocabulary and the evaluator
# contract (transcription, not re-derivation).
CLASS_SHARED = (
    "class: contract | craft",
    "objective checkable referent",
    "a brief constraint, a form spec limit or mandatory element, "
    "a declared voice target, or an ethics rule",
    "check the violation without taste",
    "qualitative observation: affinity thickness, flow, tone nuance, "
    "positioning polish",
    "is tagged `contract` (fail closed)",
)

AGGREGATION_SHARED = (
    "contract-class findings ONLY",
    "recorded observations that never gate",
)

ROUND2_SHARED = (
    "Re-raising a closed finding in new words is forbidden",
    "re-litigation, not review",
    "ends the loop",
    "regardless of counter state",
)


def test_finding_class_definitions_transcribed_from_claude_md():
    # WHY: the class definitions must be a verbatim transcription of the
    # canonical vocabulary — a paraphrase would fork the SSOT and drift.
    vocab = _claude_vocab()
    window = _window("## Finding Class")
    for phrase in CLASS_SHARED:
        assert phrase in _norm(vocab), f"canonical phrase {phrase!r} missing from CLAUDE.md"
        assert phrase in _norm(window), f"phrase {phrase!r} not transcribed into evaluator"


def test_mode2_contract_class_aggregation():
    # WHY: craft findings gating verdicts is the accumulation pathology the
    # vocabulary retires — the flag-mode verdict must aggregate contract-only.
    vocab = _claude_vocab()
    window = _window("### Mode 2", terminators=("\n## ", "\n### "))
    for phrase in AGGREGATION_SHARED:
        assert phrase in _norm(vocab), f"canonical phrase {phrase!r} missing from CLAUDE.md"
        assert phrase in _norm(window), f"phrase {phrase!r} missing from Mode 2 verdict rules"
    assert re.search(r"contract-class 🔴 → `NEEDS_REVISION`", window)
    assert re.search(r"contract-class 🟡[^\n]*`PASS_WITH_NOTES`", window)
    # fail-closed polarity reachable at verdict time: unclear -> contract
    assert re.search(r"unclear[^\n]*`contract`[^\n]*fail closed", window)


def test_old_yellow_accumulation_rule_absent():
    # WHY: absence pin (whole-file on purpose) — the retired count-based
    # "2+ 🟡 → NEEDS_REVISION" rule must not survive anywhere in the contract.
    text = _evaluator()
    assert not re.search(r"2\+\s*🟡", text), "retired 2+ 🟡 accumulation rule present"
    assert not re.search(r"two or more 🟡", text)


def test_first_action_precedence_over_gate_file_verdict_rules():
    # WHY: Mode 2 (:81-89) hardcodes contract-class aggregation, and mid-arc
    # gate rubrics / future gates may still carry the retired verdict-rules
    # block — :145 must scope to criteria only and state that Mode 2's
    # aggregation wins over any verdict-rules block a gate_file carries.
    window = _window("## First Action")
    assert "defines your evaluation criteria" in window
    assert "verdict rules" not in _norm(window).split("Precedence")[0], (
        "First Action step 2 should scope to criteria only, not bundle "
        "'verdict rules' before the precedence clause"
    )
    assert re.search(r"Mode 2['’]s contract-class aggregation", window)
    assert re.search(r"WINS over any verdict-rules block", window)


def test_prior_findings_check_round2_duty():
    # WHY: the round-2 duty is what makes the gate loop converge — prior
    # findings verified against quoted current draft text before anything new.
    vocab = _claude_vocab()
    window = _window("## Round-2 Duty")
    assert "prior_findings_check" in window
    assert "status: fix-verified | not-fixed | resurfaced" in window
    assert "restated verbatim" in window
    assert "BEFORE raising anything new" in window
    assert "quote:" in window, "prior_findings_check entries must quote current draft text"
    for phrase in ROUND2_SHARED:
        assert phrase in _norm(vocab), f"canonical phrase {phrase!r} missing from CLAUDE.md"
        assert phrase in _norm(window), f"phrase {phrase!r} missing from round-2 duty"
    # any resurfaced finding -> report oscillation
    assert re.search(r"resurface[sd][^\n]*fix-verified|fix-verified[^\n]*resurface", window)
    assert "oscillation" in window
