"""Structural grep-test guarding the Continuous-mode FREEZE (entry) extension
that accepts a human-approved loom-spec change-folder as an alternative entry
artifact alongside the brainstorming brief (Task 3 of the spec→code wiring).

SKILL.md is a prompt artifact, not executable code. Its correctness is the
PRESENCE of the load-bearing convention described in
`docs/loom/specs/2026-06-21-spec-to-code-wiring.md` Decision §2 (R6):

  Continuous-mode freeze accepts EITHER the brainstorming brief OR a
  human-approved loom-spec change-folder. Discrimination is NOT content-shape
  sniffing — the USER DECLARES which artifact, and the freeze CONFIRMS by
  (a) named-artifact presence (`specs/<capability>/spec.md` at the declared
  path) AND (b) `validate_spec_output.py` exit 0. Upstream stays human-gated;
  the STOP contract + never-auto-merge invariant are UNCHANGED.

These checks assert on the load-bearing PHRASES (intent), tolerant of wording
variation (lowercase substring / regex), so the test guards MEANING without
being brittle — but each assertion targets a real phrase from the contract.

Stdlib only (pathlib + re). Resolve SKILL.md relative to this test file.

This test is RED until the freeze section is extended (Task 3 GREEN).
"""

import re
from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "using-loom-code" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _freeze_window() -> str:
    """The Continuous-mode ENTRY/freeze block — from the 'Continuous mode'
    heading down to (but excluding) the 'Auto-advance behavior' heading.
    The change-folder alternative must live inside the entry/freeze block,
    not anywhere else in the file."""
    low = _text().lower()
    start = low.find("continuous mode")
    assert start != -1, "Continuous mode section must exist"
    end = low.find("auto-advance behavior", start)
    assert end != -1, "Auto-advance behavior heading must follow the entry block"
    return low[start:end]


def test_skill_md_exists():
    """Guard: the router SKILL.md must exist where we expect it."""
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"


# --- 1. the freeze names the change-folder as an alternative entry artifact --

def test_freeze_names_changefolder_alternative():
    """The freeze/entry block must name a loom-spec change-folder as an
    alternative entry artifact ALONGSIDE the brainstorming brief."""
    window = _freeze_window()
    assert "change-folder" in window or "change folder" in window, \
        "freeze entry must name a loom-spec change-folder as an alternative artifact"
    # it is an ALTERNATIVE — the brief must still be a valid entry too
    assert "brief" in window, \
        "the brainstorming brief must remain a valid entry artifact alongside the change-folder"


# --- 2. discrimination = user-declaration (NOT content-shape sniffing) -------

def test_discrimination_is_user_declaration_not_shape_sniffing():
    """R6: the user DECLARES which artifact; the freeze must NOT sniff content
    shape to classify the artifact."""
    window = _freeze_window()
    # user declares which artifact
    assert ("declare" in window or "declares" in window or "declared" in window), \
        "discrimination must be by user declaration (the user declares which artifact)"
    # explicit refusal of content-shape sniffing
    assert re.search(r"(not|no|never|without|rather than).{0,60}"
                     r"(content[-\s]*shape|shape[-\s]*sniff|sniff)", window), \
        "the freeze must explicitly state it does NOT rely on content-shape sniffing"


# --- 3. confirmation = named-artifact presence + validator exit 0 -----------

def test_confirmation_by_named_artifact_presence():
    """The freeze confirms by named-artifact presence: `specs/<capability>/
    spec.md` exists at the declared path."""
    window = _freeze_window()
    assert "specs/" in window, \
        "freeze must confirm by presence of the `specs/...` path"
    assert "spec.md" in window, \
        "freeze must confirm by presence of the named `spec.md` artifact"


def test_confirmation_by_validator_exit_zero():
    """The freeze confirms by `validate_spec_output.py` exit 0 (reuses the
    loom-spec validator — no new validator)."""
    window = _freeze_window()
    assert "validate_spec_output" in window, \
        "freeze must reuse loom-spec's validate_spec_output.py as the gate"
    assert ("exit 0" in window or "exit-0" in window or "exit code 0" in window), \
        "the validator gate must require exit 0"


# --- 4. invariants UNCHANGED: STOP contract + never-auto-merge --------------

def test_never_auto_merge_invariant_intact():
    """The never-auto-merge invariant (Stop-contract row 7) must remain — the
    freeze extension must NOT weaken the terminal merge gate."""
    low = _text().lower()
    assert "never auto-merge" in low or "never auto merge" in low, \
        "the never-auto-merge invariant must remain intact"


def test_stop_contract_invariant_intact():
    """The STOP contract must remain present and unweakened — the freeze
    extension touches ENTRY, not the stop rules."""
    text = _text()
    low = text.lower()
    assert "stop contract" in low or "stop trigger" in low, \
        "the STOP contract must remain present"
    # terminal PR-open stop row still references the never-auto-merge terminal
    assert "PR-open reached" in text or "pr-open reached" in low, \
        "the terminal PR-open stop row must remain in the STOP contract"
