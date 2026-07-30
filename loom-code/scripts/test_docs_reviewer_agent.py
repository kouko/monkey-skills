"""Structural pins for the prose-native docs-reviewer agent contract
(Task 1, docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md).

Guards:
- `loom-code/agents/docs-reviewer.md` exists, mirrors code-reviewer.md's
  structure (frontmatter, verdict-only role contract, verdict template),
  and carries all three injection marker pairs (baseline-v1,
  reviewer-discipline-v1, rule-sheet-v1) so distribute.py can manage it.
- The verdict template is PROSE-native: five prose dimensions
  (omission / ambiguity / inconsistency / incorrect-fact /
  missing-population), per-finding `class: instruction | evidence`,
  path-like `where:` — schema-compatible with loom_gate_markers.py
  review-pass (kickoff decision: the docs arm mints the SAME marker).
- distribute.py routes docs-reviewer in all three target lists.

Assertions pin load-bearing phrases (intent), windowed to the section
they measure per
docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md.
Stdlib only.
"""
from __future__ import annotations

from pathlib import Path

import distribute

_ROOT = Path(__file__).parents[1]
AGENT = _ROOT / "agents" / "docs-reviewer.md"

_PROSE_DIMENSIONS = [
    "omission",
    "ambiguity",
    "inconsistency",
    "incorrect-fact",
    "missing-population",
]


def _text() -> str:
    assert AGENT.is_file(), f"agent file is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _output_contract() -> str:
    """Isolate the Output contract section (verdict template) — from its
    ## heading to the ### Aggregation rule heading."""
    text = _text()
    start = text.index("## Output contract")
    end = text.index("### Aggregation rule", start)
    return text[start:end]


def _role_contract_window() -> str:
    """Isolate `## Role contract — behavioral rules` — from its heading
    to the injected reviewer-discipline-v1 marker. Bounding on the
    marker (not the next `## ` heading, which lives further down inside
    the injected block) keeps this window to the hand-authored
    behavioral-rules list only, so a mutation that deletes the
    hand-authored role-contract sentence can't be masked by injected
    boilerplate re-using the same words elsewhere in the file."""
    text = _text()
    start = text.index("## Role contract")
    end = text.index("<!-- BEGIN reviewer-discipline", start)
    return text[start:end]


# ── file shape ─────────────────────────────────────────────────────────


def test_agent_exists_with_frontmatter():
    """Dispatchable agent definition: YAML frontmatter with name +
    description (Claude Code plugin validator requirement)."""
    text = _text()
    assert text.startswith("---\n"), "frontmatter must open the file"
    frontmatter = text.split("---", 2)[1]
    assert "name: docs-reviewer" in frontmatter
    assert "description:" in frontmatter


def test_carries_all_three_injection_marker_pairs():
    """distribute.py raises on a routed agent missing any marker pair —
    the exact BEGIN/END syntax is distribute.py's own constants (SSOT),
    not a re-typed copy."""
    text = _text()
    for begin, end, label in [
        (distribute.AGENT_BASELINE_BEGIN, distribute.AGENT_BASELINE_END,
         "baseline-v1"),
        (distribute.AGENT_REVIEWER_DISCIPLINE_BEGIN,
         distribute.AGENT_REVIEWER_DISCIPLINE_END, "reviewer-discipline-v1"),
        (distribute.AGENT_RULE_SHEET_BEGIN, distribute.AGENT_RULE_SHEET_END,
         "rule-sheet-v1"),
    ]:
        assert begin in text, f"missing BEGIN {label} marker"
        assert end in text, f"missing END {label} marker"
        assert text.index(begin) < text.index(end), (
            f"{label} BEGIN marker must precede END marker"
        )


def test_registered_in_all_three_distribute_target_lists():
    """docs-reviewer must ride baseline + reviewer-discipline + rule-sheet
    injection routing — an unrouted agent silently drifts from SSOT."""
    rel = "agents/docs-reviewer.md"
    assert rel in distribute.AGENT_BASELINE_TARGETS
    assert rel in distribute.AGENT_REVIEWER_DISCIPLINE_TARGETS
    assert rel in distribute.AGENT_RULE_SHEET_TARGETS


# ── verdict template (prose-native, marker-schema-compatible) ──────────


def test_verdict_template_is_prose_native():
    """The dimension_scores block lists exactly the five prose dimensions
    — never the code-shaped ones (this agent reviews prose, not code)."""
    window = _output_contract()
    for dim in _PROSE_DIMENSIONS:
        assert f"{dim}:" in window, (
            f"prose dimension '{dim}:' missing from the verdict template"
        )
    for code_dim in ["security:", "architecture:", "cross-task-coherence:"]:
        assert code_dim not in window, (
            f"code dimension '{code_dim}' must not appear in the "
            "docs-reviewer verdict template"
        )


def test_verdict_template_satisfies_gate_marker_schema():
    """Kickoff decision: docs arm mints the SAME review-pass marker via
    loom_gate_markers.py — template must carry standards_version, a
    three-valued verdict line, `dimension_scores:` at line start
    (loom_gate_markers.py:217), and findings opened by `- severity:`
    with a path-like `where:` (loom_gate_markers.py:224-247)."""
    window = _output_contract()
    assert "standards_version" in window
    assert "verdict: PASS | PASS_WITH_NOTES | NEEDS_REVISION" in window
    assert any(
        line == "dimension_scores:" for line in window.splitlines()
    ), "`dimension_scores:` must appear at line start in the template"
    assert "- severity:" in window
    assert "where:" in window
    assert "file:line" in window, (
        "the template's `where:` must demand a path-like citation "
        "(file:line) — loom_gate_markers rejects findings without one"
    )


def test_findings_carry_class_taxonomy():
    """Every finding carries `class: instruction | evidence` — the docs
    aggregation gates on instruction-class findings only."""
    window = _output_contract()
    assert "class: instruction | evidence" in window


# ── role contract ──────────────────────────────────────────────────────


def test_verdict_only_role_never_edits_never_runs_tests():
    """Evaluator role: produces verdicts, does NOT modify reviewed files,
    does NOT run tests (prose has no test suite to run — and running
    code tests is verification-before-completion's job).

    Windowed to `## Role contract` (not the whole file): the frontmatter
    description and the injected reviewer-discipline-v1 block both reuse
    "verdict-only" / "may not" / "run tests" independently, so a
    whole-file grep stays green even if the hand-authored role-contract
    sentence stating this is deleted -- narrowing to the window closes
    that false-green (T1 quality review, tests finding)."""
    window = _role_contract_window()
    low = window.lower()
    assert "verdict-only" in low
    assert "may not" in low
    assert "edit" in low or "modify" in low
    assert "run tests" in low


def test_whole_artifact_scope_duty():
    """The reviewer reads every reviewed artifact WHOLE — the diff is
    context, not scope; an unchanged line in a document is an untouched
    line, not a correct one."""
    text = _text()
    assert "whole" in text.lower()
    assert "context, not scope" in text, (
        "the contract must state the diff is context, not scope"
    )
    assert "unchanged" in text.lower(), (
        "the contract must direct the reviewer at UNCHANGED claims that "
        "contradict the change"
    )


def test_convergence_duties_present():
    """Agent-side convergence duties (skill owns orchestration): verify
    prior-round findings against quoted current text before raising
    anything new; never re-raise a closed finding in new words; assert
    absence only after reading the full text."""
    text = _text()
    assert "prior-round" in text or "round 1" in text or "previous round" in text, (
        "the contract must handle dispatch packets carrying prior-round "
        "findings"
    )
    assert "quoted" in text, (
        "fix-verification must be against QUOTED current text"
    )
    assert "re-raise" in text and "closed finding" in text, (
        "the re-litigation ban (never re-raise a closed finding in new "
        "words) must be stated"
    )
    assert (
        "asserting-absence-needs-full-text-not-an-abstract.md" in text
    ), (
        "absence assertions must cite the full-text-before-absence "
        "discipline (docs/loom/memory/"
        "asserting-absence-needs-full-text-not-an-abstract.md)"
    )
