"""W1-03 — adversary.md and engineering-baseline.md state the prose-pin
rule: a test that pins a sentence of prose requires an affirmative verb
before the pinned literal, rejects any negation token in that same
sentence, and carries synthetic self-tests.

Mirrors test_language_station_text.py's negation-aware matcher shape:
resolve REPO via `git rev-parse`, read each file, split into sentences,
and assert one sentence carries the required affirmative-verb-then-
keyword shape with no negation token anywhere in the sentence.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

_REPO_RESULT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True,
    text=True,
    check=True,
)
REPO = Path(_REPO_RESULT.stdout.strip())

ADVERSARY_MD = REPO / "loom-code" / "agents" / "adversary.md"
BASELINE_MD = REPO / "loom-code" / "references" / "engineering-baseline.md"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)
_AFFIRM_VERB_RE = re.compile(r"\b(require|requires|must|is|are|asserts)\b")
_AFFIRM_KW_RE = re.compile(r"\baffirmative(ly)?\b")
_NEGATION_KW_RE = re.compile(r"\bnegat(?:ion|ed)\b")
_SELFTEST_KW_RE = re.compile(r"\b(self-test|synthetic)\b")


def _sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces —
    same normalization test_language_station_text.py uses, so a sentence
    that line-wraps in the source still reads as one unit here."""
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _sentence_pins_prose_rule(sentence: str) -> bool:
    """True iff `sentence` (lowercased for keyword matching) names
    "affirmative"/"affirmatively", "negation"/"negated", and "self-test"/
    "synthetic", has one of the affirmative verb forms
    (require/requires/must/is/are/asserts) BEFORE the earliest of those
    three keyword hits, and carries no negation token anywhere in the
    sentence."""
    low = sentence.lower()
    m_affirm = _AFFIRM_KW_RE.search(low)
    m_negation = _NEGATION_KW_RE.search(low)
    m_selftest = _SELFTEST_KW_RE.search(low)
    if not (m_affirm and m_negation and m_selftest):
        return False
    first_kw_idx = min(m_affirm.start(), m_negation.start(), m_selftest.start())
    if not _AFFIRM_VERB_RE.search(low[:first_kw_idx]):
        return False
    return not _has_negation(sentence)


def test_adversarymd_prosepinsentence_present() -> None:
    """adversary.md must carry one sentence pinning the prose-pin rule
    (affirmative verb before affirmative/negation/self-test vocabulary,
    no negation token anywhere in that sentence)."""
    text = ADVERSARY_MD.read_text(encoding="utf-8")
    hits = [s for s in _sentences(text) if _sentence_pins_prose_rule(s)]
    assert hits, (
        "loom-code/agents/adversary.md has no sentence pinning the "
        "prose-pin rule"
    )


def test_engineeringbaselinemd_prosepinsentence_present() -> None:
    """engineering-baseline.md must carry one sentence pinning the
    prose-pin rule (affirmative verb before affirmative/negation/
    self-test vocabulary, no negation token anywhere in that sentence)."""
    text = BASELINE_MD.read_text(encoding="utf-8")
    hits = [s for s in _sentences(text) if _sentence_pins_prose_rule(s)]
    assert hits, (
        "loom-code/references/engineering-baseline.md has no sentence "
        "pinning the prose-pin rule"
    )


def test_sentencepinsproserule_negatedsynthetic_rejected() -> None:
    """Self-test on `_sentence_pins_prose_rule`: a negated synthetic
    sentence carrying all three keyword groups must be rejected, and an
    affirmative synthetic sentence carrying the same three keyword groups
    must be accepted — otherwise the two tests above could be satisfied
    by a sentence that FORBIDS the rule rather than requiring it."""
    affirmative = (
        "A prose-pin rule requires an affirmative sentence verified "
        "through a self-test against a synthetic negated example."
    )
    assert _sentence_pins_prose_rule(affirmative), (
        "a genuinely affirmative synthetic sentence must pass"
    )

    negated = (
        "A prose-pin rule does not require an affirmative sentence, and "
        "skips both the self-test and the synthetic negated example."
    )
    assert not _sentence_pins_prose_rule(negated), (
        "a negated synthetic sentence must be rejected even though it "
        "names all three keyword groups"
    )


if __name__ == "__main__":  # pragma: no cover
    import sys
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
