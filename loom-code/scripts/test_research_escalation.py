"""Structural grep-tests for the v1 reactive research-escalation mechanism
(plan: docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md, task 2).

Why this exists: the 2026-07-16 fiscal-year incident spun 4 review rounds
on a business-domain-convention question while SDD's 3-round cap escalated
straight to the user with zero research attached. This mechanism inserts a
classify-then-research step BEFORE that escalation, at two action moments:
(a) the 2nd same-question NEEDS_REVISION round, (b) an implementer about to
return BLOCKED on a semantics/convention dispute. It never replaces or
extends the existing 3-round cap / 4th-retry escalation.

Grep-tests over prose files go false-green when the asserted phrase
pre-exists elsewhere in the file (docs/loom/memory/
grep-tests-scope-to-measured-neighborhood.md) — the SKILL.md checks below
are windowed around unique anchor strings, radius small enough to exclude
sibling paragraphs, measured against the real file. Each window assertion
was proven RED against `git show HEAD:<file>` pre-change content before the
mount edits landed (see task report; SKILL.md's pre-change content has
neither anchor's neighborhood mentioning "research-escalation.md" at all).

Stdlib only (pathlib).
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

REFERENCE = (
    REPO_ROOT
    / "loom-code/skills/subagent-driven-development/references/research-escalation.md"
)
SDD_SKILL = REPO_ROOT / "loom-code/skills/subagent-driven-development/SKILL.md"

# Unique anchor strings in SDD SKILL.md, and the window radius (chars) around
# each that the mount edit must land inside. Radii are measured against the
# actual file: large enough to catch a mount sentence placed immediately
# before/after the anchor, small enough to exclude the anchor's siblings
# (the "Same 3-round cap." table cell above the cap paragraph; the
# `NEEDS_CONTEXT` status-handling line above the BLOCKED line).
_CAP_ANCHOR = "A 3-round cap prevents infinite loops on ambiguous specs."
_CAP_RADIUS = 400

_BLOCKED_ANCHOR = (
    "even if the unblock step is trivial, log what was done so the final "
    "summary names it. A `NEEDS_CONTEXT` question with product stakes goes "
    "through the same two-axis framing (§Asking the user ①) before "
    "it reaches the user."
)
_BLOCKED_RADIUS = 400


def _read(path: Path) -> str:
    assert path.is_file(), f"expected file at {path}"
    return path.read_text(encoding="utf-8")


def _window(text: str, anchor: str, radius: int) -> str:
    idx = text.find(anchor)
    assert idx != -1, f"anchor not found in file: {anchor!r}"
    start = max(0, idx - radius)
    end = min(len(text), idx + len(anchor) + radius)
    return text[start:end]


# --- Reference file: exists + carries the pinned vocabulary + doctrine -----


def test_reference_file_exists():
    assert REFERENCE.is_file(), (
        "loom-code/skills/subagent-driven-development/references/"
        "research-escalation.md must exist (plan task 2)"
    )


def test_reference_file_carries_three_bucket_names():
    text = _read(REFERENCE)
    assert "**craft**" in text
    assert "**domain-convention**" in text
    assert "**project-local**" in text


def test_reference_file_carries_classification_question():
    text = _read(REFERENCE)
    assert (
        "Who can overrule this fact" in text
    ), "the pinned classification question must be transcribed verbatim"


def test_reference_file_carries_tag_format():
    text = _read(REFERENCE)
    assert "evidence_needed: craft | domain-convention | project-local" in text


def test_reference_file_restates_cap_unchanged():
    """Cross-reference-severing guard (docs/loom/memory/
    extraction-severing-cross-ref-needs-weak-model-test.md): the reference
    file must restate, in its own text, that SDD's 3-round cap and 4th-retry
    user escalation still apply unchanged — this file only inserts a
    research step BEFORE that escalation, never replaces or extends it."""
    text = _read(REFERENCE)
    assert "3-round cap" in text
    assert "4th-retry" in text or "4th retry" in text
    assert "unchanged" in text


# --- SDD SKILL.md mounts: minimal, windowed, imperative ---------------------


def test_cap_paragraph_window_names_research_escalation_reference():
    text = _read(SDD_SKILL)
    window = _window(text, _CAP_ANCHOR, _CAP_RADIUS)
    assert "references/research-escalation.md" in window, (
        "the 3-round-cap paragraph's neighborhood must point at "
        "references/research-escalation.md — mount fires at the 2nd "
        "same-question NEEDS_REVISION round, before the 4th-retry escalation"
    )


def test_cap_paragraph_window_names_second_round_trigger():
    text = _read(SDD_SKILL)
    window = _window(text, _CAP_ANCHOR, _CAP_RADIUS).lower()
    assert "2nd" in window and "same" in window, (
        "the mount must name the 2nd-same-question trigger explicitly, not "
        "just point at the file"
    )


def test_blocked_window_names_research_escalation_reference():
    text = _read(SDD_SKILL)
    window = _window(text, _BLOCKED_ANCHOR, _BLOCKED_RADIUS)
    assert "references/research-escalation.md" in window, (
        "the BLOCKED/status-handling neighborhood must point at "
        "references/research-escalation.md — mount fires before surfacing a "
        "BLOCKED that hinges on a semantics/convention dispute"
    )


def test_blocked_window_names_semantics_dispute_trigger():
    text = _read(SDD_SKILL)
    window = _window(text, _BLOCKED_ANCHOR, _BLOCKED_RADIUS)
    assert "semantics" in window or "convention" in window, (
        "the mount must scope itself to a semantics/convention dispute, not "
        "every BLOCKED (e.g. a missing dependency must NOT trigger research)"
    )


# --- v2 addition (plan task 10): reviewer evidence_needed tag ---------------
# Source: docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md task 10
# ("loom-code (0.32.0 -> 0.33.0): reviewer agents gain the optional
# evidence_needed tag ... SDD SKILL.md one-line mount: a reviewer finding
# carrying the tag triggers the research-escalation triage IMMEDIATELY").

_IMMEDIATE_TRIGGER_ANCHOR = (
    "before the 3rd re-dispatch — so research evidence rides that round."
)
_IMMEDIATE_TRIGGER_RADIUS = 250

AGENTS_DIR = REPO_ROOT / "loom-code/agents"
CODE_QUALITY_REVIEWER = AGENTS_DIR / "code-quality-reviewer.md"
CODE_REVIEWER = AGENTS_DIR / "code-reviewer.md"

_EVIDENCE_NEEDED_FIELD = "evidence_needed: craft | domain-convention | project-local"


def test_cap_paragraph_window_names_evidence_needed_immediate_trigger():
    """The 2nd-round mount's neighborhood must also cover the reviewer-tag
    immediate trigger — a finding carrying evidence_needed: triggers the
    triage NOW, not just at the 2nd same-question round (the tag is the
    Loop-Breaker SWITCH signal; no round-burning)."""
    text = _read(SDD_SKILL)
    window = _window(text, _IMMEDIATE_TRIGGER_ANCHOR, _IMMEDIATE_TRIGGER_RADIUS)
    assert "evidence_needed" in window, (
        "the 2nd-round mount's neighborhood must name the evidence_needed "
        "immediate trigger"
    )
    assert "before any re-dispatch" in window or "immediately" in window.lower(), (
        "the immediate-trigger sentence must say the triage runs before any "
        "re-dispatch, not wait for the 2nd round"
    )


def test_code_quality_reviewer_findings_schema_carries_evidence_needed():
    text = _read(CODE_QUALITY_REVIEWER)
    assert _EVIDENCE_NEEDED_FIELD in text, (
        "code-quality-reviewer.md's findings schema must gain the optional "
        "evidence_needed tag (plan task 10)"
    )
    assert "never runs the research" in text, (
        "the schema addition needs its one-sentence flag-don't-search rule "
        "(reviewer flags, never searches)"
    )


def test_code_reviewer_findings_schema_carries_evidence_needed():
    text = _read(CODE_REVIEWER)
    assert _EVIDENCE_NEEDED_FIELD in text, (
        "code-reviewer.md's findings schema must gain the optional "
        "evidence_needed tag (plan task 10)"
    )
    assert "never runs the research" in text, (
        "the schema addition needs its one-sentence flag-don't-search rule "
        "(reviewer flags, never searches)"
    )


def test_reference_file_carries_reviewer_tag_supplement_after_existing_sections():
    """The supplement must land AFTER the pin block AND after the existing
    'Mount doctrine' / 'Cap unchanged' sections — never inside the pin
    (docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md
    supplement-after-pin rule)."""
    text = _read(REFERENCE)
    cap_idx = text.find("## Cap unchanged")
    assert cap_idx != -1, "existing '## Cap unchanged' section must survive"
    supplement_idx = text.find("Reviewer-tag trigger")
    assert supplement_idx != -1, (
        "research-escalation.md must gain a reviewer-tag-trigger supplement"
    )
    assert supplement_idx > cap_idx, (
        "the supplement must come AFTER the existing sections (including "
        "'## Cap unchanged'), never inside the pin or before it"
    )
    assert "pre-classif" in text.lower() or "already named it" in text.lower(), (
        "the supplement must say the tag pre-classifies the bucket, so this "
        "trigger only verifies (and reclassifies if obviously wrong) rather "
        "than re-deriving the bucket from scratch"
    )
    assert text.count("unchanged") >= 2, (
        "the supplement must restate caps-unchanged (existing section already "
        "has one 'unchanged'; the new supplement adds a second)"
    )
