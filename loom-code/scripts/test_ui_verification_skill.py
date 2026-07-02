"""Structural grep-test guarding the ui-verification SKILL.md load-bearing
contract.

SKILL.md is a prompt artifact, not executable code. The contract under guard
(born from the 2026-07-03 pipeline dogfood, where the GUI half shipped with
"no live browser" verification):

- CONDITIONAL gate: fires only when a ui-flows.md exists AND the branch
  touches a UI surface — it is N/A machinery otherwise, mirroring the D8
  principles-conformance pattern.
- Drives the states ui-flows.md ALREADY enumerates (render variants, flows,
  entry/exit) against the real rendered app — the design station owns the
  checklist, this skill owns the runtime gate (#442 seam precedent).
- N/A-loud degradation: no browser/device tooling available -> emit N/A with
  the reason; never fake a pass, never silently skip.
- Verdict is two-valued (PASS_WITH_NOTES / NEEDS_REVISION, no bare PASS):
  coverage is relative to ui-flows.md's enumeration, and claiming more would
  be the banned completeness claim.
- DESIGN.md token conformance is EXPLICITLY out of scope — that machine
  consumer is parked with re-triggers (PR #473); this skill must not
  front-run the park.
- Does NOT replace verification-before-completion's package-test hard gate.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "ui-verification" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def test_frontmatter_name_and_conditional_description():
    text = _text()
    assert "name: ui-verification" in text
    low = text.lower()
    assert "ui-flows.md" in text, \
        "description/body must condition on the ui-flows.md artifact"
    assert "do not" in low or "not for" in low or "n/a" in low, \
        "description must carry a when-NOT boundary"


def test_conditional_gate_on_ui_flows_and_ui_surface():
    low = _text().lower()
    assert "ui-flows.md" in low
    assert "n/a" in low, \
        "must define the N/A outcome when the gate's conditions do not hold"


def test_na_loud_tooling_degradation():
    """No browser/device tooling -> N/A with reason, never a fake pass."""
    low = _text().lower()
    assert "never" in low and ("fake" in low or "fabricat" in low or
                               "pretend" in low or "simulate" in low), \
        "must forbid faking verification when tooling is absent"
    assert "n/a" in low


def test_two_valued_verdict_no_bare_pass():
    text = _text()
    assert "PASS_WITH_NOTES" in text and "NEEDS_REVISION" in text
    low = text.lower()
    import re
    assert re.search(r"(no|never|not)\b[^.\n]*\bunqualified pass|"
                     r"(no|never|not)\b[^.\n]*\bbare pass|"
                     r"deliberately\s+(has\s+)?no\s+pass\b", low), \
        "must state that an unqualified/bare PASS is deliberately absent"


def test_token_conformance_explicitly_out_of_scope():
    """Must respect the #473 park: behavioral states yes, DESIGN.md token
    conformance no."""
    text = _text()
    assert "DESIGN.md" in text
    low = text.lower()
    assert "token" in low and ("out of scope" in low or "excluded" in low or
                               "parked" in low), \
        "DESIGN.md token conformance must be explicitly out of scope (#473)"


def test_does_not_replace_package_test_gate():
    text = _text()
    assert "verification-before-completion" in text, \
        "must name the package-test sibling gate it complements"
    low = text.lower()
    assert "replace" in low or "substitute" in low, \
        "must state it does not replace the package-test gate"


def test_evidence_is_per_state_observation():
    low = _text().lower()
    assert "screenshot" in low or "snapshot" in low, \
        "evidence contract must name observation artifacts"
    assert "per-state" in low or "each state" in low or "per state" in low or \
           "every state" in low or "each enumerated" in low, \
        "evidence must be tied to the enumerated states"


def test_coverage_honesty_relative_to_enumeration():
    low = _text().lower()
    assert "relative to" in low, \
        "coverage statement must be relative to ui-flows.md's enumeration"
