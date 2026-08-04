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

import re
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


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches, and strip
    markdown emphasis markers so bold text is not falsely distinct from
    the equivalent plain phrase when a test checks a phrase's presence
    or absence -- mirrors test_requesting_docs_review_skill.py's _norm
    (hard-wrap, whitespace, and inline-bold are the three vacuous-pin
    variants seen in this arc)."""
    return re.sub(r"\s+", " ", s.replace("*", "")).strip()


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


def _input_contract() -> str:
    """Isolate the Input contract section (dispatch packet shape) — from
    its ## heading to the ## Output contract heading."""
    text = _text()
    start = text.index("## Input contract")
    end = text.index("## Output contract", start)
    return text[start:end]


def _prior_findings_check_window() -> str:
    """The `prior_findings_check:` fence entry inside `## Output
    contract` -- from the `prior_findings_check:` line to the next
    top-level key line (`findings:`). Narrower than `_output_contract`,
    which also contains `findings:`'s own `- severity:` line and would
    false-green an assertion that no `- severity:` line appears inside
    the prior_findings_check fence."""
    window = _output_contract()
    lines = window.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("prior_findings_check:"):
            start = i
            break
    assert start is not None, (
        "## Output contract carries no `prior_findings_check:` fence"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^[a-z_]+:", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


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


def test_class_default_provenance_marker():
    """The `class:` line in the output contract may carry an optional
    `(defaulted)` annotation when the reviewer fail-closed defaulted to
    `instruction` instead of judging it, and the aggregation-equivalence
    sentence must say so verbatim (I5)."""
    window = _output_contract()
    norm = _norm(window).lower()
    assert "(defaulted)" in norm, (
        "Output contract must show the optional `(defaulted)` tag on "
        "the `class:` line"
    )
    assert "treated exactly as" in norm, (
        "Output contract must state the `(defaulted)` tag is treated "
        "exactly as `instruction` by the aggregation rule"
    )
    assert "class: instruction | evidence" in window, (
        "the pinned `class: instruction | evidence` literal must survive"
    )


def test_prior_findings_carrier_every_later_round():
    """The prior-findings carrier is not round-2-specific in either the
    input or output contract: every round after round 1 receives (and
    echoes back) the previous round's surviving findings (D1)."""
    input_window = _norm(_input_contract())
    assert (
        "### Prior-round findings (every round after round 1)"
        in input_window
    ), (
        "the input-contract heading must generalize to every round "
        "after round 1"
    )
    assert "round 2 only" not in input_window, (
        "the input-contract heading must not restrict the carrier to "
        "round 2 only"
    )
    assert "one extra round" in input_window and "retained" in input_window, (
        "the input-contract section must tell the reviewer that a "
        "fix-verified finding is retained in the carrier for exactly "
        "one extra round, so it knows a fix-verified item can appear "
        "once more and what to do with it"
    )

    output_window = _norm(_output_contract())
    assert "every round after round 1" in output_window, (
        "the output-template comment must generalize prior_findings_check "
        "to every round after round 1"
    )
    assert "round 2 only" not in output_window, (
        "the output-template comment must not restrict prior_findings_check "
        "to round 2 only"
    )


def test_prior_findings_restated_as_scalar():
    """A prior finding is restated as a one-line scalar, never the
    original `- severity:` block -- `_FINDING_RE`
    (`loom_gate_markers.py`) matches `- severity:` at ANY indent, so a
    verbatim block nested under `finding:` would land in the origin
    ledger a second time as a later-round finding, contaminating the
    population partition the ledger exists to keep clean (I2)."""
    raw = _prior_findings_check_window()
    norm = " ".join(raw.split()).lower()
    assert "one-line" in norm and "scalar" in norm, (
        "the restatement instruction must tell the reviewer to restate "
        "the prior finding as a one-line scalar summary"
    )
    assert not re.search(r"(?m)^\s*-\s*severity\s*:", raw), (
        "the prior_findings_check fence must not itself carry a "
        "`- severity:` finding-block line (the exact pattern "
        "loom_gate_markers.py's _FINDING_RE matches at any indent) -- "
        "a nested one would double-count the finding in the origin "
        "ledger as a new later-round finding"
    )


def test_reviewed_sha_fail_closed_no_self_resolve():
    """The output-contract fallback for a missing `reviewed_sha` must be
    fail-closed reporting (`unresolved`), never self-resolution -- a
    self-resolved sha becomes the left endpoint of the NEXT round's
    delta-scoped range and can silently narrow it (the exact fail-open
    direction SKILL.md's Directive 2 forbids), while `unresolved` trips
    the skill's existing "no prior reviewed_sha -> unbounded" fallback
    (D4). The input-contract template must also carry the HEAD-sha slot
    SKILL.md Step 3 requires the dispatch packet to state -- that
    omission is what makes the fallback reachable in the first place."""
    output_norm = _norm(_output_contract()).lower()
    assert "unresolved" in output_norm, (
        "the output contract must document a fail-closed `unresolved` "
        "value for reviewed_sha when the packet did not state one"
    )
    assert "resolve it yourself" not in output_norm, (
        "the output contract must not instruct the reviewer to "
        "self-resolve a missing HEAD sha -- checked on whitespace- and "
        "markdown-normalized text because the historical defect wording "
        "hard-wrapped this exact phrase across a line boundary, which "
        "made a raw substring check vacuous"
    )

    input_norm = _norm(_input_contract()).lower()
    assert "head sha" in input_norm, (
        "the input-contract template must carry the HEAD-sha slot the "
        "skill's Step 3 requires the dispatch packet to state, or the "
        "fail-closed fallback above stays reachable"
    )


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


def _out_of_scope_fence_window() -> str:
    """The `out_of_scope:` fence entry inside `## Output contract` --
    from the `out_of_scope:` line to the next top-level key line, or to
    the end of the output contract (it is the fence's last key, so
    there normally is no next key)."""
    window = _output_contract()
    lines = window.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("out_of_scope:"):
            start = i
            break
    assert start is not None, (
        "## Output contract carries no `out_of_scope:` fence"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^[a-z_]+:", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def test_out_of_scope_not_claimed_persisted():
    """The out_of_scope fence comment must not claim a suppressed
    defect is 'recorded so it is not lost' -- nothing persists it: the
    panel verdict text goes to an unspecified temp file and nothing
    re-injects the entry into a later round. State the honest fact
    instead: surfaced to the user with the verdict, persisted nowhere;
    deferral survives only if the user or orchestrator acts on it. The
    completeness counter-instruction ('a silently dropped observation
    is invisible to everyone downstream') must survive unchanged (D5)."""
    fence = " ".join(
        _out_of_scope_fence_window().replace("*", "").split()
    ).lower()
    assert "recorded so it is not lost" not in fence, (
        "the out_of_scope fence comment must not claim a suppressed "
        "defect is recorded so it is not lost"
    )
    assert "persisted nowhere" in fence, (
        "the out_of_scope fence comment must state the honest fact: "
        "persisted nowhere"
    )
    assert "silently" in fence and "dropped observation" in fence, (
        "the completeness counter-instruction must survive: a silently "
        "dropped observation is invisible to everyone downstream"
    )
