"""Pin tests for the review-round Stage-flip duty sentence.

Arc 2026-08-07 (stage-owner-and-blocked-enum): whole-branch review rounds
previously had no owner for flipping the plan's `Stage:` header to
`review:round-N`, so plans went stale during review. requesting-code-review/
SKILL.md now carries ONE self-contained duty sentence making the
orchestrator flip the Stage at each round start. These tests pin that
sentence (whitespace-normalized substring) so refactors cannot silently
drop or splice it.

Covered here:
- test_rcr_carries_stage_flip_duty — requesting-code-review/SKILL.md.
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
