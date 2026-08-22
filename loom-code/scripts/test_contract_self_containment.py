"""Tests that the two reviewer contracts state the code-as-spec both-halves
obligation inline, so a reviewer holding only the contract (not this repo's
`docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md`) can still apply
it (plan `docs/loom/plans/2026-08-22-contracts-cite-only-what-ships.md`
Task 2 Acceptance).

This is the mechanical leg only: a whitespace-flattened word match. It
cannot catch a paraphrase that keeps the matching words while dropping or
reweighting a clause — that needs a fresh-reader judgment pass against
`code-as-spec-writing-rule.md` §Decision, which this test does not attempt.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The obligation's own words from §Decision, whitespace-flattened for a
# match tolerant of contract-side line wraps but not of dropped clauses.
OBLIGATION = (
    "prose must carry the reason, the goal, the expected effect, and how "
    "the implementation choice was made — sourced from a Decision Log "
    "entry, a memory file, or git history, never invented, and left "
    "unwritten with the gap reported when no source carries it"
).lower()


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def test_both_halves_obligation_is_stated_in_each_arm() -> None:
    for rel in ("loom-code/agents/code-reviewer.md", "loom-code/agents/docs-reviewer.md"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert OBLIGATION in _flatten(text), (
            f"{rel} does not state the both-halves obligation inline"
        )


def test_the_two_arms_no_longer_defer_to_the_dated_spec_for_this_obligation() -> None:
    citation = "docs/loom/specs/2026-08-21-code-as-spec-writing-rule.md"
    for rel in ("loom-code/agents/code-reviewer.md", "loom-code/agents/docs-reviewer.md"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert citation not in text, (
            f"{rel} still defers to the dated spec instead of stating the obligation"
        )
