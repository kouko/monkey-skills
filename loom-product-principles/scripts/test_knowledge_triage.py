"""Behavioral grep-test for the v2 product-principles knowledge-triage
mount (docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md,
task 8).

Guards three things:
1. `references/knowledge-triage.md` exists and carries: the pin's three
   bucket names verbatim, the `evidence_needed:` tag format, the
   domain-convention route (existing Tripwire punt channel to
   `using-loom-discovery`, DRAFT status, the `— assumption:` escape
   hatch), the craft pointer (no restatement of the canon audit), the
   standing (not stall-triggered) posture, and the cross-severing guard
   (validator + no-external-runtime posture untouched).
2. SKILL.md's `— check:`-drafting moment (anchored on the unique
   "Reject platitudes — push back." phrase) names the reference file and
   instructs classifying BEFORE writing a guessed check.

Per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md,
assertion (2) is scoped to a measured window around the unique anchor,
not the whole file. Window radius below was measured against the real
file: it includes the newly-inserted mount line and excludes the
"Draft-time count self-check" bullet that follows it.

Stdlib only (pathlib). Resolve paths relative to this test file so the
suite runs from any cwd.
"""

from pathlib import Path

SKILL = Path(__file__).parent.parent / "skills" / "product-principles" / "SKILL.md"
REF = (
    Path(__file__).parent.parent
    / "skills"
    / "product-principles"
    / "references"
    / "knowledge-triage.md"
)


def _skill_text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _window(text: str, anchor: str, before: int = 0, after: int = 400) -> str:
    """Return a character window around the unique `anchor` substring.
    Fails loud if the anchor is missing or not unique (a non-unique anchor
    means the window could silently land on the wrong occurrence)."""
    count = text.count(anchor)
    assert count == 1, f"anchor {anchor!r} must be unique in the file, found {count}"
    idx = text.index(anchor)
    start = max(0, idx - before)
    end = min(len(text), idx + len(anchor) + after)
    return text[start:end]


# --- reference file: bucket vocabulary pin ----------------------------------


def test_reference_file_exists():
    assert REF.is_file(), f"references/knowledge-triage.md is absent at {REF}"


def test_reference_carries_three_bucket_names_verbatim():
    text = REF.read_text(encoding="utf-8")
    assert "**craft**" in text, "must carry the craft bucket, pin-verbatim bold form"
    assert "**domain-convention**" in text, (
        "must carry the domain-convention bucket, pin-verbatim bold form"
    )
    assert "**project-local**" in text, (
        "must carry the project-local bucket, pin-verbatim bold form"
    )
    assert "Classify ONCE, walk ONE route (triage, not checklist)" in text, (
        "must carry the pin's triage-not-checklist framing verbatim"
    )


def test_reference_carries_tag_format():
    text = REF.read_text(encoding="utf-8")
    assert "evidence_needed: craft | domain-convention | project-local" in text, (
        "must carry the pin's exact tag-format line"
    )


# --- reference file: station mount doctrine ----------------------------------


def test_reference_craft_route_points_to_canon_audit_not_restated():
    text = REF.read_text(encoding="utf-8")
    assert "canon-*.md" in text, (
        "craft route must point at the existing canon-*.md completeness audit"
    )
    assert "Do not restate that audit here" in text, (
        "craft route must be a pointer, not a restatement, per the pin's"
        " per-station-free doctrine"
    )


def test_reference_domain_convention_routes_to_existing_tripwire_punt():
    text = REF.read_text(encoding="utf-8")
    assert "using-loom-discovery" in text, (
        "domain-convention route must name the existing punt channel target"
    )
    assert "Tripwire" in text, (
        "domain-convention route must name the skill's EXISTING Tripwire punt"
        " channel, not invent a new one"
    )
    assert "evidence-backed needs mapping" in text, (
        "must restate enough of the Tripwire's own wording to survive"
        " extraction-severing (weak-model cross-ref proximity)"
    )


def test_reference_domain_convention_stays_draft_until_evidence_or_assumption():
    text = REF.read_text(encoding="utf-8")
    assert "**DRAFT**" in text, (
        "a domain-convention principle must be marked DRAFT, not shipped"
        " into PRINCIPLES.md as resolved"
    )
    assert "## Open Questions" in text, (
        "DRAFT items must route through the skill's existing Open Questions"
        " mechanism, not a new artifact"
    )
    assert "— assumption: <reason>" in text or "-- assumption: <reason>" in text, (
        "the user-accepts-assumption escape hatch must use the pin-idiom"
        " marker with its own reason field"
    )


def test_reference_states_standing_posture():
    text = REF.read_text(encoding="utf-8")
    assert "Standing posture" in text, "must explicitly name the standing posture"
    assert "one-way door" in text, (
        "must justify standing (not stall-triggered) via the constitution's"
        " one-way-door reversibility"
    )


def test_reference_states_cross_severing_guard():
    text = REF.read_text(encoding="utf-8")
    assert "validate_principles_output.py" in text, (
        "cross-severing guard must name the structural validator it leaves"
        " untouched"
    )
    assert "no external runtime" in text.lower() or "no** api key" in text.lower(), (
        "cross-severing guard must restate the skill's no-external-runtime"
        " posture"
    )
    assert "using-loom-discovery" in text, (
        "cross-severing guard must state research happens only in discovery,"
        " never in this drafting station"
    )


# --- SKILL.md mount: check-drafting moment -----------------------------------


def test_check_drafting_mount_names_reference_file():
    """The `— check:` platitude-rejection paragraph (where a guessed check
    would otherwise get written) must point at the reference and instruct
    classifying BEFORE writing the check."""
    text = _skill_text()
    window = _window(text, "**Reject platitudes — push back.**", before=0, after=600)
    assert "references/knowledge-triage.md" in window, (
        "check-drafting mount must name references/knowledge-triage.md"
    )
    assert "classify" in window.lower(), (
        "check-drafting mount must instruct classifying FIRST"
    )
    assert "guessing" in window.lower(), (
        "check-drafting mount must gate on a check that requires guessing"
        " an unverified fact"
    )
