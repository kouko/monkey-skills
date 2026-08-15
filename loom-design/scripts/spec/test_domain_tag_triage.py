"""Behavioral grep-test for the v1 domain-tag triage mechanism
(docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md, task 3).

Guards three things:
1. `references/domain-tag-triage.md` exists and carries: the three bucket
   names verbatim, the `evidence_needed:` tag format, and the
   SHAPING/DEFERRABLE two-tier distinction plus the "spec-expansion never
   runs WebSearch" closed-world restatement.
2. SKILL.md's expansion loop (Phase ③ lens layer, anchored on the unique
   "Prune through the lens layer." phrase) names the reference file — the
   mount that fires classification BEFORE an edge case's expected behavior
   is written.
3. SKILL.md's gate/VERIFY section (anchored on the unique "Validate the
   emitted directory with" phrase) carries the shaping-tag gate rule.

Per docs/loom/memory/grep-tests-scope-to-measured-neighborhood.md,
assertions for (2) and (3) are scoped to a measured window around each
unique anchor, not the whole file — a whole-file grep for a generic phrase
like "domain" would false-green against unrelated content. Window radii
below were measured against the real file: they include the newly-inserted
mount text and exclude the anchor's nearest sibling section.

Stdlib only (pathlib). Resolve paths relative to this test file so the
suite runs from any cwd.
"""

from pathlib import Path

SKILL = Path(__file__).parent.parent / "skills" / "spec-expansion" / "SKILL.md"
REF = Path(__file__).parent.parent / "skills" / "spec-expansion" / "references" / "domain-tag-triage.md"


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
    assert REF.is_file(), f"references/domain-tag-triage.md is absent at {REF}"


def test_reference_carries_three_bucket_names_verbatim():
    text = REF.read_text(encoding="utf-8")
    assert "**craft**" in text, "must carry the craft bucket, pin-verbatim bold form"
    assert "**domain-convention**" in text, \
        "must carry the domain-convention bucket, pin-verbatim bold form"
    assert "**project-local**" in text, \
        "must carry the project-local bucket, pin-verbatim bold form"
    assert "Classify ONCE, walk ONE route (triage, not checklist)" in text, \
        "must carry the pin's triage-not-checklist framing verbatim"


def test_reference_carries_tag_format():
    text = REF.read_text(encoding="utf-8")
    assert "evidence_needed: craft | domain-convention | project-local" in text, \
        "must carry the pin's exact tag-format line"


def test_reference_carries_shaping_deferrable_distinction():
    text = REF.read_text(encoding="utf-8")
    assert "SHAPING" in text, "must name the SHAPING tier"
    assert "DEFERRABLE" in text, "must name the DEFERRABLE tier"
    assert "acceptance criteria" in text and "state machine" in text, \
        "SHAPING bar must be defined against acceptance criteria / data semantics / state machine"
    assert "deferred:" in text, \
        "gate escape hatch must name the deferred: <reason> note format"


def test_reference_restates_closed_world_never_websearch():
    text = REF.read_text(encoding="utf-8")
    assert "never runs WebSearch" in text or "never run WebSearch" in text, \
        "must explicitly restate spec-expansion stays closed-world (no live WebSearch)"
    assert "outside this skill" in text.lower() or "outside this skill" in text, \
        "must state shaping-tag resolution happens outside spec-expansion"


# --- SKILL.md mount: expansion loop -----------------------------------------

def test_expansion_loop_mount_names_reference_file():
    """Phase ③'s lens-layer pruning (where FLAGged edge cases are drafted)
    must point at the reference and classify BEFORE writing behavior."""
    text = _skill_text()
    window = _window(text, "**Prune through the lens layer.**", before=600, after=50)
    assert "references/domain-tag-triage.md" in window, \
        "expansion-loop mount must name references/domain-tag-triage.md"
    assert "classify" in window.lower(), \
        "expansion-loop mount must instruct classifying FIRST"
    assert "derivable" in window.lower(), \
        "expansion-loop mount must gate on behavior not derivable from seed/PRINCIPLES/ui-flows"


# --- SKILL.md mount: gate / VERIFY section ----------------------------------

def test_gate_section_carries_shaping_tag_rule():
    """The VERIFY/gate section must state the shaping-tag gate rule: an
    unresolved SHAPING domain-convention tag blocks VERIFY unless deferred."""
    text = _skill_text()
    window = _window(text, "Validate the emitted directory with", before=700, after=50)
    assert "references/domain-tag-triage.md" in window, \
        "gate mount must name references/domain-tag-triage.md"
    assert "SHAPING" in window, "gate mount must name the SHAPING tier"
    assert "deferred:" in window, \
        "gate mount must carry the deferred: <reason> escape hatch"
