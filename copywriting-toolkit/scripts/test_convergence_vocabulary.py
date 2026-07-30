"""Pins for the canonical convergence vocabulary in copywriting-toolkit/CLAUDE.md.

Window discipline (docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md):
every presence assertion is scoped to the vocabulary section extracted by its
unique heading anchor — never whole-file — so generic terms elsewhere in
CLAUDE.md ("verdict", "gate", "contract") cannot false-green a pin. The one
whole-file assertion is the ABSENCE pin (no 2+ 🟡 accumulation rule survives),
where whole-file scope is the point.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import re
from pathlib import Path

CLAUDE_MD = Path(__file__).resolve().parent.parent / "CLAUDE.md"
HEADING = "## Gate Convergence Vocabulary"


def _text() -> str:
    return CLAUDE_MD.read_text(encoding="utf-8")


def _section() -> str:
    """The vocabulary section: from its unique heading to the next H2."""
    text = _text()
    start = text.find(HEADING)
    assert start != -1, f"canonical section heading {HEADING!r} absent from CLAUDE.md"
    nxt = text.find("\n## ", start + len(HEADING))
    return text[start:nxt] if nxt != -1 else text[start:]


def test_class_definitions_and_fail_closed():
    # WHY: the class taxonomy is the SSOT every gate skill points at; without
    # the objective-referent framing, "contract" degrades to reviewer taste.
    s = _section()
    assert "class: contract | craft" in s
    assert "objective checkable referent" in s
    for referent in ("brief constraint", "form spec", "declared voice target", "ethics rule"):
        assert referent in s, f"contract-class referent {referent!r} missing"
    assert "qualitative observation" in s
    # fail-closed polarity: unclear -> contract (never craft)
    fail_closed = re.search(r"unclear[^.]*`contract`[^.]*fail closed", s)
    assert fail_closed, "fail-closed sentence (unclear -> contract) missing"


def test_contract_only_aggregation():
    # WHY: craft findings gating verdicts is the exact accumulation pathology
    # (2+ soft findings flipping a verdict) this vocabulary retires.
    s = _section()
    assert "contract-class findings ONLY" in s
    assert "never gate" in s
    assert "recorded observations" in s


def test_round2_duty_and_relitigation_ban():
    # WHY: the round-2 duty is what makes the loop converge — prior findings
    # verified against the current draft before anything new is raised.
    s = _section()
    assert "verbatim" in s
    assert "BEFORE raising anything new" in s
    assert "re-litigation" in s
    assert re.search(r"[Rr]e-raising a closed finding in new words is forbidden", s)


def test_oscillation_stop():
    # WHY: a fix-verified finding resurfacing means the loop is oscillating,
    # not converging — counters must not be able to keep it alive.
    s = _section()
    assert "fix-verified" in s
    assert "ends the loop" in s
    assert "operator" in s
    assert "regardless of counter" in s


def test_ethics_fatal_unchanged():
    # WHY: the vocabulary must not be readable as softening the ethics gate.
    s = _section()
    assert "FATAL" in s
    assert "UNCHANGED" in s
    assert "blocks unconditionally" in s


def test_no_yellow_accumulation_rule_survives():
    # WHY: absence pin (whole-file on purpose) — the retired "2+ yellow ->
    # NEEDS_REVISION" accumulation vocabulary must not survive anywhere in
    # CLAUDE.md outside historical/CHANGELOG-style text (CLAUDE.md has none).
    text = _text()
    assert not re.search(r"2\+\s*🟡", text), "retired 2+ 🟡 accumulation wording present"
    assert not re.search(r"two or more 🟡", text)


def test_section_is_not_a_trailing_appendix():
    # WHY: prominence decides weak-model firing (memory:
    # imperative-placement-prominence-decides-weak-model-firing) — the section
    # must sit adjacent to the gate/verdict sections, before the caller guide.
    text = _text()
    vocab = text.find(HEADING)
    caller_guide = text.find("## External Caller Guide")
    assert vocab != -1 and caller_guide != -1
    assert vocab < caller_guide, "vocabulary section must precede External Caller Guide"
