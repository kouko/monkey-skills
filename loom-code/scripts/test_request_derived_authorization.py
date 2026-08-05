"""Prose-pin test for request-derived authorization, Task 1 (router +
doctrine endpoint recognition).

Pins, whitespace-normalized contiguous (plan
docs/loom/plans/2026-08-05-request-derived-authorization.md, ## Notes
N1/N2):

- using-loom-code/SKILL.md §Continuous mode: the N1 recognition-block
  lead, the non-trigger sentence, the 「一站一站來」 escape hatch, and
  the plan-header recording format "endpoint named: yes → continuous";
  plus the router rule-5 once-clause pointer at §Continuous mode's
  request-recognition block.
- references/continuous-mode.md §Entry: the N2 recognition lead, the
  same escape hatch + recording format, and the doctrine paragraph's
  closing "never auto-merge" restatement.
- One positive-fact control per file (pre-existing headings) proving
  the matches are not vacuous.
"""

from pathlib import Path

_SKILLS = Path(__file__).resolve().parents[1] / "skills" / "using-loom-code"
SKILL = _SKILLS / "SKILL.md"
REF = _SKILLS / "references" / "continuous-mode.md"


def _normalized_text(path: Path) -> str:
    """Whitespace-normalized file text (collapses hard wraps so a
    contiguous-phrase match doesn't depend on line breaks)."""
    text = path.read_text(encoding="utf-8")
    return " ".join(text.split())


# --- positive-fact controls (must pass even before the edits) ---------------

def test_control_skill_continuous_mode_heading_present():
    """Positive-fact control: the pre-existing §Continuous mode heading
    is present in the router body — proves SKILL.md is actually being
    read/matched, not a stub."""
    assert (
        "## Continuous mode (opt-in): spec-frozen → PR auto-advance"
        in _normalized_text(SKILL)
    )


def test_control_ref_entry_heading_present():
    """Positive-fact control: the pre-existing §Entry heading is present
    in the doctrine reference."""
    assert "## Entry — at the SPEC, not the plan" in _normalized_text(REF)


# --- N1: router recognition block (SKILL.md §Continuous mode) ---------------

def test_router_recognition_lead():
    """N1 lead: opt-in is also recognized from the request itself —
    a kickoff request naming a publish endpoint is an explicit opt-in."""
    assert (
        "**Opt-in is also recognized from the request itself**: a kickoff "
        'request that names a publish endpoint — "finish this branch", '
        '"ship it", "開 PR", "run to PR" — is an explicit continuous opt-in'
        in _normalized_text(SKILL)
    )


def test_router_non_trigger_sentence():
    """N1: a request naming no endpoint never triggers the recognition."""
    assert (
        "A request naming no endpoint never triggers this"
        in _normalized_text(SKILL)
    )


def test_router_escape_hatch_stage_by_stage():
    """N1: 「一站一站來」 restores human-pumped mode and flips the
    recording."""
    normalized = _normalized_text(SKILL)
    assert "「一站一站來」" in normalized
    assert (
        "restores human-pumped mode from that point, and the recording flips"
        in normalized
    )


def test_router_plan_header_recording_format():
    """N1: the recognition is recorded in the plan header in the pinned
    one-line format."""
    assert "endpoint named: yes → continuous" in _normalized_text(SKILL)


# --- rule-5 sweep: once-clause pointer (SKILL.md router rule 5) -------------

def test_router_rule5_once_clause_pointer():
    """Rule-5 parenthetical carries the asked-once pointer at
    §Continuous mode's request-recognition block (no re-ask per
    outward action)."""
    assert (
        "asked once — see §Continuous mode's request-recognition block"
        in _normalized_text(SKILL)
    )


# --- N2: doctrine §Entry recognition paragraph (continuous-mode.md) ---------

def test_doctrine_entry_recognition_lead():
    """N2 lead: entry opt-in is also satisfied by the request itself."""
    assert (
        "Entry opt-in is also satisfied by the request itself: a kickoff "
        "request naming a publish endpoint"
        in _normalized_text(REF)
    )


def test_doctrine_escape_hatch_and_recording_format():
    """N2: same escape hatch and plan-header recording format in the
    doctrine register."""
    normalized = _normalized_text(REF)
    assert "「一站一站來」" in normalized
    assert "endpoint named: yes → continuous" in normalized


def test_doctrine_closing_never_auto_merge_restatement():
    """N2 closes by restating the invariant: the merge invariant is
    untouched — never auto-merge."""
    assert (
        "the merge invariant is untouched: **never auto-merge**"
        in _normalized_text(REF)
    )
