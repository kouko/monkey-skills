"""Structural grep-test guarding code-reviewer.md's principles-conformance
ACTIVATION semantics (Task 13, docs/loom/plans/2026-07-10-designer-pm-loop-
implementation.md).

Prior contract: "Fires only when the orchestrator passes a
docs/loom/PRINCIPLES.md path" — activation was orchestrator-gated. That is
wrong: the reviewer has filesystem access to the target repo it is reviewing
and should derive existence of docs/loom/PRINCIPLES.md ITSELF. An
orchestrator-passed path should be an override for a non-standard location,
not the thing that turns the dimension on — otherwise an orchestrator that
forgets to pass the path silently suppresses a dimension that should have
fired.

The fix: the agent contract must say the reviewer checks the target repo for
docs/loom/PRINCIPLES.md itself (self-derived activation), that an
orchestrator-passed path is only an override for non-standard locations, and
must retain the N/A-honesty rule (no findings fabricated when the file is
genuinely absent).

These checks assert on load-bearing PHRASES (intent), tolerant of exact
wording, so the test guards meaning without being brittle. Stdlib only.
"""

from pathlib import Path

_ROOT = Path(__file__).parents[1]
AGENT = _ROOT / "agents" / "code-reviewer.md"
REQUESTING_REVIEW_SKILL = (
    _ROOT / "skills" / "requesting-code-review" / "SKILL.md"
)

_OLD_GATE_PHRASE = "Fires **only** when the orchestrator passes a"
_OLD_STEP2_GATE_PHRASE = (
    "pass nothing — each reviewer emits `principles-conformance: N/A`"
)


def _text() -> str:
    assert AGENT.is_file(), f"file is absent at {AGENT}"
    return AGENT.read_text(encoding="utf-8")


def _d8_block() -> str:
    """Isolate the D8 section (#### D8 — ... through the next #### heading)."""
    text = _text()
    start = text.index("#### D8 — Principles Conformance")
    end = text.index("#### D9", start)
    return text[start:end]


def _requesting_review_text() -> str:
    assert REQUESTING_REVIEW_SKILL.is_file(), (
        f"file is absent at {REQUESTING_REVIEW_SKILL}"
    )
    return REQUESTING_REVIEW_SKILL.read_text(encoding="utf-8")


def test_reviewer_derives_principles_existence_itself():
    """The contract must instruct the agent to check the TARGET REPO for
    docs/loom/PRINCIPLES.md itself — activation is a filesystem derivation,
    not something only the orchestrator can supply."""
    text = _text()
    assert "docs/loom/PRINCIPLES.md" in text
    derivation_markers = [
        "checks the target repo for",
        "self-derived",
    ]
    assert any(m in text for m in derivation_markers), (
        "code-reviewer.md must state the agent derives principles-conformance "
        "activation by checking the target repo for docs/loom/PRINCIPLES.md "
        "itself — none of the derivation markers "
        f"{derivation_markers} were found"
    )


def test_orchestrator_path_is_override_not_gate():
    """An orchestrator-passed path must be documented as an OVERRIDE for a
    non-standard location, not the activation condition."""
    text = _text()
    assert "override" in text.lower(), (
        "code-reviewer.md must document the orchestrator-passed path as an "
        "override (for non-standard PRINCIPLES.md locations), not the "
        "activation condition"
    )
    assert "non-standard location" in text or "non-standard PRINCIPLES.md" in text, (
        "code-reviewer.md must state the override is for a non-standard "
        "location specifically"
    )


def test_old_orchestrator_only_gate_wording_is_gone():
    """The old exclusive-gating phrase must be removed — activation is no
    longer conditioned solely on the orchestrator passing a path."""
    assert _OLD_GATE_PHRASE not in _text(), (
        f"code-reviewer.md still carries the old orchestrator-only gate "
        f"phrase '{_OLD_GATE_PHRASE}' — activation must be self-derived, "
        "not orchestrator-gated"
    )


def test_na_honesty_retained_no_fabrication():
    """N/A must stay honest: no findings fabricated when PRINCIPLES.md is
    genuinely absent (checked at the standard location, no override
    resolving either)."""
    text = _text()
    assert "N/A" in text
    assert "never fabricate" in text, (
        "code-reviewer.md must retain the never-fabricate N/A-honesty rule "
        "for principles-conformance"
    )


def test_d8_anchors_via_concrete_git_toplevel_mechanism():
    """Round-2 fix (finding 2): D8's self-derivation must reuse the SAME
    concrete anchor pattern R1 already uses six lines up (git rev-parse
    --show-toplevel, then check <root>/docs/loom/PRINCIPLES.md) — not the
    vague "checks the target repo for ... itself" phrase alone, which gives
    no executable resolution and risks a false-N/A from a nested/worktree
    cwd."""
    d8 = _d8_block()
    assert "git rev-parse --show-toplevel" in d8, (
        "code-reviewer.md's D8 block must anchor principles-conformance "
        "derivation at the repo root via `git rev-parse --show-toplevel` "
        "(the same concrete mechanism R1 uses for standards_version), so "
        "worktree/nested-cwd dispatches can't false-N/A"
    )
    assert "docs/loom/PRINCIPLES.md" in d8


def test_requesting_review_step2_old_gating_wording_is_gone():
    """Round-2 fix (finding 1): requesting-code-review/SKILL.md's Step 2
    principles-conformance sub-bullet still describes the OLD
    orchestrator-gated model ("If absent, pass nothing — each reviewer
    emits N/A"). That phrase must be gone — the new semantics are:
    self-derived activation, orchestrator path is an override only."""
    text = _requesting_review_text()
    assert _OLD_STEP2_GATE_PHRASE not in text, (
        "requesting-code-review/SKILL.md's Step 2 principles-conformance "
        f"sub-bullet still carries the old gating phrase "
        f"'{_OLD_STEP2_GATE_PHRASE}' — must describe self-derived "
        "activation with the orchestrator path as override-only"
    )
    assert "self-derived" in text or "self-derives" in text, (
        "requesting-code-review/SKILL.md's Step 2 principles-conformance "
        "sub-bullet must state activation is self-derived by the reviewer"
    )
    assert "override" in text.lower(), (
        "requesting-code-review/SKILL.md's Step 2 principles-conformance "
        "sub-bullet must document the orchestrator-passed path as an "
        "override only, matching code-reviewer.md's D8 semantics"
    )
