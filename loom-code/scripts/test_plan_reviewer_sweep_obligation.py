"""Prose-pin: §Verdict mapping NEEDS_REVISION bullet must carry the
per-check sweep obligation sentence (plan Task 7).

Whitespace-normalized contiguous-substring match, per
docs/loom/memory/verbatim-phrase-guards-break-on-hard-line-wrap.md —
hard line wrap must not be able to break this pin.
"""

import re
from pathlib import Path

TARGET = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "writing-plans"
    / "references"
    / "plan-document-reviewer-prompt.md"
)

SWEEP_OBLIGATION_SENTENCE = (
    "Before returning, re-scan every task against each check that failed "
    "anywhere; a check reported on one task but left unreported on "
    "another task with the same defect is a contract violation."
)

ANCHOR_SENTENCE = "List EVERY failure"


def _normalized_text() -> str:
    text = TARGET.read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", text)


def test_anchor_sentence_present():
    # Anti-vacuous positive fact: if this fails, the whole test file is
    # comparing against the wrong path/section and any pass would be
    # meaningless.
    normalized = _normalized_text()
    assert ANCHOR_SENTENCE in normalized


def test_sweep_obligation_sentence_present_after_anchor():
    normalized = _normalized_text()
    normalized_sentence = re.sub(r"\s+", " ", SWEEP_OBLIGATION_SENTENCE)
    assert normalized_sentence in normalized
    assert normalized.index(ANCHOR_SENTENCE) < normalized.index(
        normalized_sentence
    )
