"""Shared negation matcher for prose-pin tests.

A test that pins a sentence of station text rejects any negation token in
that sentence (engineering baseline, prose-pin rule). One regex here, one
place to widen it: nine test modules used to carry private copies of
``\\b(?:not|never|no)\\b|n't`` and none of them caught ``cannot``,
``without`` or ``nothing`` (wave-end adversary, review-sees-complexity).

``none`` and ``nothing`` are deliberately absent: they are quantifiers
that pinned affirmative sentences use ("a reader who raised none keeps its
previous PASS"; "that one intent line, nothing more"), and the hostile
rewrites the adversary built used ``cannot`` and ``without``.
"""
from __future__ import annotations

import re

NEGATION_RE = re.compile(
    r"\b(?:not|never|no|cannot|without|neither|nobody|nor)\b|n't",
    re.IGNORECASE,
)


def has_negation(sentence: str) -> bool:
    return bool(NEGATION_RE.search(sentence))
