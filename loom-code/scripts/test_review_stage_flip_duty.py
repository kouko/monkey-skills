"""Pin tests for the review-round Stage-flip duty sentence.

Arc 2026-08-07 (stage-owner-and-blocked-enum): whole-branch review rounds
previously had no owner for flipping the plan's `Stage:` header to
`review:round-N`, so plans went stale during review. requesting-code-review/
SKILL.md now carries ONE self-contained duty sentence making the
orchestrator flip the Stage at each round start. These tests pin that
sentence (whitespace-normalized substring) so refactors cannot silently
drop or splice it.

Arc 2026-08-08 (progress-display-hardening, Task 3): plan_card.py gained a
`--set-stage` action (Task 1 of the same plan), which makes the old duty
sentence's "plan_card.py has no stage setter" claim false. The duty
sentence is rewritten to route through the script (hand-edit only as a
fallback when the script is absent), and this file's pins move with it —
plus a residue guard so the old claim can never silently creep back, and a
probe control proving the pin actually discriminates old vs. new wording.

Covered here:
- test_rcr_carries_stage_flip_duty — requesting-code-review/SKILL.md
  carries the new command-form duty sentence verbatim (whitespace-
  normalized).
- test_rcr_has_no_stale_stage_setter_residue — the old "plan_card.py has
  no stage setter" claim is gone.
- test_duty_sentence_pin_rejects_old_sentence_probe — RED-first control:
  a probe copy carrying only the OLD sentence must NOT satisfy the new
  pin's substring check.

(The planned requesting-docs-review sibling was descoped: its SKILL.md
sits at 4427 words against the 4430-word ceiling pinned by
test_rdr_extraction_pointers.py — the 31-word duty sentence would land
it at 4458 — and the brief rules cap-blown → skip the rider.)
"""
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"
RCR_SKILL_MD = SKILLS_DIR / "requesting-code-review" / "SKILL.md"

RCR_DUTY_SENTENCE = (
    "At the start of each review round (round 1 included), run "
    "`python3 scripts/plan_card.py <plan-path> --set-stage "
    '"review:round-N"` — the script prints the refreshed card; relay '
    "it — and commit the flip with that round's verdict or fixes; "
    "hand-edit only when the script is absent."
)

STALE_CLAIM = "plan_card.py has no stage setter"

OLD_DUTY_SENTENCE = (
    "At the start of each review round (round 1 included), update the "
    "plan's Stage: header to review:round-N by hand-edit — plan_card.py "
    "has no stage setter — and commit it with that round's verdict or "
    "fixes."
)


def _norm(text: str) -> str:
    """Whitespace-normalize for robust substring checks."""
    return re.sub(r"\s+", " ", text).strip()


def test_rcr_carries_stage_flip_duty():
    skill = _norm(RCR_SKILL_MD.read_text(encoding="utf-8"))
    assert _norm(RCR_DUTY_SENTENCE) in skill


def test_rcr_has_no_stale_stage_setter_residue():
    skill = RCR_SKILL_MD.read_text(encoding="utf-8")
    assert STALE_CLAIM not in skill


def test_duty_sentence_pin_rejects_old_sentence_probe():
    # RED-first control: a probe carrying only the OLD sentence must NOT
    # satisfy the new pin's assertion — proves
    # test_rcr_carries_stage_flip_duty discriminates on content, not just
    # on the presence of *a* duty sentence at that location.
    probe = _norm(f"## Process\n\n{OLD_DUTY_SENTENCE}\n\n1. more text")
    assert _norm(RCR_DUTY_SENTENCE) not in probe
    # And the live artifact itself must not still carry the OLD sentence —
    # a probe-only check can pass while the SKILL.md silently regressed to
    # the old wording; this closes that gap.
    skill = RCR_SKILL_MD.read_text(encoding="utf-8")
    assert OLD_DUTY_SENTENCE not in skill
