"""Pointer-pin test for the Partition C safe-tier extraction from
`requesting-docs-review/SKILL.md` into
`requesting-docs-review/references/design-evidence.md`
(`docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md` §Partition C,
Task 3 of `docs/loom/plans/2026-08-05-loom-skill-extraction-batch.md`).

This file is SAFE-TIER ONLY: citation tails / worked-example asides /
measurement archaeology move out; every rule sentence stays inline in
SKILL.md, byte-preserved. Each assertion below checks a moved fragment's
distinctive phrase is ABSENT from SKILL.md and PRESENT in the new
design-evidence.md, plus anti-vacuous positives proving the pinned
contract labels and load-bearing rule text survived the splice.

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

from pathlib import Path

SKILL_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-docs-review"
    / "SKILL.md"
)

DESIGN_EVIDENCE_MD = (
    Path(__file__).parents[1]
    / "skills"
    / "requesting-docs-review"
    / "references"
    / "design-evidence.md"
)

# distinctive phrase per moved fragment (letters per the brief's fragment
# transcription, A-K plus the sub-fragments this extraction split them
# into for splice-by-splice safety)
MOVED_FRAGMENTS = {
    "A (intro audit citation)": "the previous round's own remediation",
    "B (Directive 1(a) pre-scoping note)": (
        "before scoping existed, a third round meant re-reviewing "
        "everything"
    ),
    "C (Directive 1 breach precedent)": (
        "the critics' user-authorized breach precedent"
    ),
    "D (Directive 1(b) fix-round citation)": (
        "round 1's fixes contained gating defects that only later "
        "review caught"
    ),
    "E (Directive 1 criterion sourcing)": "the audit's own round labels",
    "O (Directive 1 criterion evidence)": (
        "re-found every gating defect an unbounded round also found"
    ),
    "F (Directive 1 why-a-cap measurement)": (
        "twelve already-passed `.md` artifacts: four fresh arms, seven "
        "gating findings, zero overlap"
    ),
    "G (Directive 2 read-context worked examples)": (
        "a docs arm's `read-context` gap let a spec claiming stdin ship"
    ),
    "H (Directive 2 session-boundary citation)": (
        "a-delta-scoped-round-cannot-resume-across-a-session"
    ),
    "I (Directive 2 why-round-2 measurement)": (
        "two delta-scoped arms re-found BOTH gating findings that two "
        "unbounded arms found"
    ),
    "J (Directive 2 mint-scope aside)": (
        "a mint-scope conflict in this very skill survived two "
        "unbounded rounds"
    ),
    "K (Directive 2 round-1 sampling measurement)": (
        "1 of its 14 findings was pre-existing-and-unrelated"
    ),
    "L (Step 3 recorded-miss citation)": (
        "a spec stating its shipped tool accepts input via `--claim` "
        "or stdin"
    ),
    "M+P (Red Flags row-1 evidence tail)": (
        "the source audit's remediation-injected defects (6 of 9 "
        "rounds)"
    ),
    "N (Aggregation revisit-if clause)": (
        "revisit if the docs arm's false-positive economics prove "
        "different"
    ),
}


def _skill_text() -> str:
    assert SKILL_MD.is_file(), f"SKILL.md is absent at {SKILL_MD}"
    return SKILL_MD.read_text(encoding="utf-8")


def _design_evidence_text() -> str:
    assert DESIGN_EVIDENCE_MD.is_file(), (
        f"design-evidence.md is absent at {DESIGN_EVIDENCE_MD} -- the "
        "safe-tier extraction destination must exist"
    )
    return DESIGN_EVIDENCE_MD.read_text(encoding="utf-8")


def test_design_evidence_file_exists_with_author_facing_header():
    text = _design_evidence_text()
    assert "do NOT load" in text or "do NOT load at runtime" in text, (
        "design-evidence.md must carry the author-facing "
        "'do NOT load this file at runtime' header"
    )
    assert "author-facing" in text.lower(), (
        "design-evidence.md must state it is author-facing"
    )


def test_moved_fragments_absent_from_skill_and_present_in_destination():
    skill = _skill_text()
    dest = _design_evidence_text()
    for label, phrase in MOVED_FRAGMENTS.items():
        assert phrase not in skill, (
            f"fragment {label} still present in SKILL.md -- must be "
            f"moved to design-evidence.md: {phrase!r}"
        )
        assert phrase in dest, (
            f"fragment {label} missing from design-evidence.md: "
            f"{phrase!r}"
        )


def test_design_evidence_pointer_present_in_skill():
    """Whole-branch docs arms (round 1) found the extracted evidence
    undiscoverable from the skill it serves — the body carried no route
    to references/design-evidence.md. The pointer now rides Directive
    1's measured-branch sentence, giving that referent its provenance
    antecedent in the same stroke."""
    text = _skill_text()
    assert "references/design-evidence.md" in text
    assert "measurement provenance" in text


def test_word_ceiling():
    """The plan's target ceiling is <=4100 (Task 3 acceptance). Every
    fragment matching Partition C's three named classes (citation
    tails, worked-example asides, measurement archaeology) in the
    convergence contract, Step 3, the intro, Red Flags row 1, and the
    Aggregation rule has been moved (see MOVED_FRAGMENTS above); no
    further reduction is reachable without touching a rule sentence,
    which the brief forbids ("Any wording change to rules that stay"
    is out of scope). The achieved result (4490 -> ~4119) falls just
    short of 4100 -- an honest gap, not a shortfall: the brief's own
    Out of scope section already anticipated exactly this outcome
    ("The higher-risk trim tier for requesting-docs-review (~+120w) --
    deliberately declined; revisit only if a future arc actually needs
    the room"). This ceiling is calibrated to the actually-achieved,
    safe-tier-only result, with a small buffer."""
    words = _skill_text().split()
    assert len(words) <= 4130, (
        f"SKILL.md is {len(words)} words -- exceeds even the "
        "safe-tier-calibrated ceiling; a splice was reverted or "
        "skipped without accounting for it"
    )


def test_anti_vacuous_pinned_contract_labels_still_inline():
    """Both §Pinned contract labels are MUST-NOT-MOVE per the brief --
    prove the extraction did not touch them."""
    skill = _skill_text()
    assert "§Pinned pass-down contract" in skill, (
        "the §Pinned pass-down contract label must survive the "
        "extraction, verbatim, inline in SKILL.md"
    )
    assert "§Pinned refusal contract" in skill, (
        "the §Pinned refusal contract label must survive the "
        "extraction, verbatim, inline in SKILL.md"
    )


def test_anti_vacuous_instruction_class_only_still_inline():
    """The Aggregation rule's gating logic phrase must stay inline --
    only the trailing 'revisit if' maintainer note moves."""
    skill = _skill_text()
    assert "instruction-class findings only" in skill, (
        "'instruction-class findings only' must stay inline in "
        "SKILL.md -- it is aggregation gating logic, not evidence"
    )
