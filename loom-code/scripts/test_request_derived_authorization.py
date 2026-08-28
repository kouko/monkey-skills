"""Prose-pin test for approved-entry autonomy authorization (Task 1).

The approval of the frozen entry artifact, not a named publish endpoint,
authorizes autonomous execution. The router and doctrine each retain the
stage-by-stage escape hatch and never-auto-merge invariant; Rule 5 points to
the canonical four-outcome policy rather than carrying a second ask rule.
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


def _section_window(path: Path, heading: str) -> str:
    """Whitespace-normalized text from `heading` to the next `## `
    heading (or EOF). Narrows a pin to the section that governs it,
    instead of matching anywhere in the whole file."""
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i
            break
    assert start is not None, (
        f"heading {heading!r} not found -- section renamed or removed"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().startswith("## "):
            end = j
            break
    return " ".join("".join(lines[start:end]).split())


def _marker_window(path: Path, start_marker: str, end_marker: str) -> str:
    """Whitespace-normalized text between two literal markers. Used for
    the Rule 5 list item, which has no `## ` heading of its own."""
    raw = path.read_text(encoding="utf-8")
    start = raw.index(start_marker)
    end = raw.index(end_marker, start)
    return " ".join(raw[start:end].split())


# --- positive-fact controls (must pass even before the edits) ---------------

def test_control_skill_autonomous_execution_heading_present():
    """Positive-fact control: the router's autonomous-execution heading exists."""
    assert (
        "## Autonomous execution (default): approved scope → PR-ready"
        in _normalized_text(SKILL)
    )


def test_control_ref_entry_heading_present():
    """Positive-fact control: the pre-existing §Entry heading is present
    in the doctrine reference."""
    assert "## Entry — at the SPEC, not the plan" in _normalized_text(REF)


# --- Router authorization block ---------------------------------------------

def test_router_approved_entry_starts_autonomy():
    """A human-approved frozen entry, not an opt-in phrase, starts autonomy.

    Pinned inside the governing heading's window, not whole-file: this is
    the named mechanism that triggers autonomy, and matching it anywhere
    in the file would stay green even if the section were moved or the
    trigger condition were attached to unrelated prose elsewhere.
    """
    window = _section_window(
        SKILL, "## Autonomous execution (default): approved scope → PR-ready"
    )
    assert (
        "**Autonomy-by-default:** after a **human-approved**, frozen brief or "
        "validated loom-design change-folder fixes scope, auto-advance"
        in window
    )


def test_router_publish_endpoint_is_not_required():
    """A publish endpoint can name a terminal but is not a precondition."""
    window = _section_window(
        SKILL, "## Autonomous execution (default): approved scope → PR-ready"
    )
    assert (
        "a named publish endpoint may set the terminal, but is not required to "
        "start autonomous execution"
        in window
    )


def test_router_escape_hatch_stage_by_stage():
    """「一站一站來」 remains the explicit per-session override."""
    normalized = _normalized_text(SKILL)
    assert "「一站一站來」" in normalized
    assert (
        "is the per-session human-pumped override"
        in normalized
    )


# --- Rule 5 points at the canonical policy ----------------------------------

def test_router_rule5_points_to_canonical_policy():
    """Rule 5 delegates ask decisions to the shared four-outcome policy."""
    assert (
        "four-outcome policy in `references/continuous-mode.md`"
        in _normalized_text(SKILL)
    )
    # Narrowed to the Rule 5 list item itself: the halt condition is a
    # named escalation mechanism, not incidental phrasing, and pinning it
    # whole-file would stay green even if it drifted to a different rule.
    rule5_window = _marker_window(
        SKILL, "5. **Research before asking.**", "**Skipping any of these"
    )
    assert "halt for irreversible safety boundaries" in rule5_window


# --- Doctrine authorization block -------------------------------------------

def test_doctrine_entry_approval_authorizes_autonomy():
    """The doctrine names the entry artifact as the authority boundary."""
    window = _section_window(REF, "## Entry — at the SPEC, not the plan")
    assert (
        "The entry artifact, not a request naming a publish endpoint, "
        "authorizes autonomous execution"
        in window
    )


def test_doctrine_escape_hatch_and_approved_entry_recording():
    """The doctrine keeps the override and records the approved entry path."""
    normalized = _normalized_text(REF)
    assert "「一站一站來」" in normalized
    assert "Record the approved-entry path in the plan header" in normalized


def test_doctrine_closing_never_auto_merge_restatement():
    """The doctrine retains the never-auto-merge invariant, restated in
    the closing paragraph of the Entry section it governs."""
    window = _section_window(REF, "## Entry — at the SPEC, not the plan")
    assert "the merge invariant remains **never auto-merge**" in window
