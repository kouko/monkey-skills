"""RED test for Task 11 — decision-session SKILL.md core sitting protocol.

@req: BI-6
@req: BI-7
@req: BI-12
"""
from __future__ import annotations

import re
from pathlib import Path

SKILL_MD = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "decision-session"
    / "SKILL.md"
)

WORD_CAP = 4500

REQUIRED_LITERALS = (
    "dag.py check",
    "dag.py render",
    "break-assumption",
    "references/node-schema.md",
    "references/research-rules.md",
    "references/blind-spot-checklist.md",
)

# The three interrupt points: each token must appear in a sentence that also
# carries the interrupt verb ("confirm" / "ask") — naming the token alone is
# not the contract, being an interrupt point is.
INTERRUPT_TOKENS = ("GOAL", "assumption", "DECISION")


def _body(text: str) -> str:
    """Return the SKILL.md body — everything after the YAML frontmatter."""
    assert text.startswith("---\n"), "SKILL.md must open with YAML frontmatter"
    return text.split("---\n", 2)[2]


def _sentences(body: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", body) if s.strip()]


def test_decision_session_skill_names_cli_verbs_interrupts_view_prohibition_and_word_cap():
    # @req: BI-6
    text = SKILL_MD.read_text(encoding="utf-8")
    body = _body(text)

    assert len(body.split()) <= WORD_CAP, (
        f"SKILL.md body is {len(body.split())} words, cap is {WORD_CAP}"
    )

    for literal in REQUIRED_LITERALS:
        assert literal in body, f"SKILL.md body must name {literal!r}"

    assert re.search(r"never read.*views/", body, re.IGNORECASE) or re.search(
        r"views/.*never", body, re.IGNORECASE
    ), "SKILL.md body must state the views/ read prohibition"

    sentences = _sentences(body)
    for token in INTERRUPT_TOKENS:
        assert any(
            token in s and re.search(r"confirm|ask", s, re.IGNORECASE)
            for s in sentences
        ), f"no confirm/ask sentence names the interrupt point {token!r}"
