"""Prose-pin tests for SDD's mechanical self-check gaining a third part
("Suite green") — Task 1 of
docs/loom/plans/2026-08-04-mechanical-lane-suite-gate.md.

Live motivation: `Review-weight: mechanical` skipped both reviewers and
the deterministic self-check verified only content match + scope match;
nothing between a task's commit and the whole-branch review ran the
package suite, so a mechanical edit could redden a file no task
touches (the 0.51.0 bump task passed its self-check while the
shipping-version pin test — in a file no task touched — was red).

Assertions, whitespace-normalized where the target prose may wrap at
the file's prevailing width:
  - the pinned part-3 sentence is present (normalized comparison)
  - "all required:" is present (raw substring — the "two parts, both
    required" -> "three parts, all required" rewrite)
  - "both required:" is absent (guards the old wording was actually
    replaced, not just appended alongside)
  - the file's word count stays <= 4500 (CHK-SKL-010's proxy for the
    SKILL.md token budget; matches check-skill-structure.py's
    `len(text.split())` method)
  - anti-vacuous positive: "2. **Scope match.**" is present, so this
    test cannot pass by grepping the wrong file/section entirely

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SDD_SKILL = (
    REPO_ROOT
    / "loom-code"
    / "skills"
    / "subagent-driven-development"
    / "SKILL.md"
)

WORD_HARD_CAP = 4500

PART_3_SENTENCE = (
    "3. **Suite green.** Run the resolved package test command after "
    "the task's commit; any failure fails the self-check — a "
    "mechanical edit can redden a file no task touches (live case: a "
    "version bump vs the shipping-version pin test)."
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def test_part_3_suite_green_sentence_present():
    text = _normalize_ws(_read(SDD_SKILL))
    assert _normalize_ws(PART_3_SENTENCE) in text


def test_all_required_present_and_both_required_absent():
    text = _read(SDD_SKILL)
    assert "all required:" in text
    assert "both required:" not in text


def test_skill_md_word_count_within_budget():
    word_count = len(_read(SDD_SKILL).split())
    assert word_count <= WORD_HARD_CAP


def test_scope_match_item_still_present_anti_vacuous():
    text = _read(SDD_SKILL)
    assert "2. **Scope match.**" in text
