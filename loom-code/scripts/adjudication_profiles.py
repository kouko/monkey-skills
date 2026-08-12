#!/usr/bin/env python3
"""Per-language profile table for the adjudication view (Task 1).

Language facts (negation markers, negation-inversion prefix, EN-modal
mapping, and the negation check's severity tier) used to be module-level
constants inside adjudication_lint.py — the checker WAS the SSOT, so a
second language had nowhere to live. This module extracts them into one
`LanguageProfile` per language tag, keyed off `get_profile(lang)`.

Each `modality_map` value is a TUPLE of accepted target-language forms,
not a single string. zh-Hant entries are single-element tuples — this
shape exists so a later profile (e.g. Japanese, which has several
JIS-sanctioned alternative forms per modal) can list a SET of accepted
forms without a second code path in the checks that consume it.

`negation_tier` ("hard" | "warning") lets a profile decide whether a
missing negation marker fails the lint outright or only warns — zh-Hant
is "hard" (unchanged shipped behavior); a future profile may choose
"warning" instead of forcing every language onto the same tier.

stdlib only.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class LanguageProfile:
    lang: str
    negation_markers: str
    negation_prefix: str
    modality_map: Tuple[Tuple[str, Tuple[str, ...]], ...]
    negation_tier: str  # "hard" | "warning"


_PROFILES = {
    "zh-Hant": LanguageProfile(
        lang="zh-Hant",
        # Moved verbatim from adjudication_lint._ZH_NEGATION_MARKERS.
        negation_markers="不未無非沒勿",
        # Moved verbatim from adjudication_lint._ZH_NEGATION_PREFIX.
        negation_prefix="不未非",
        # Moved verbatim from adjudication_lint._MODALITY_MAP, with each
        # ZH form wrapped in a single-element tuple. Order matters:
        # two-word phrases ("must not" / "should not") precede their
        # single-word prefixes ("must" / "should") so alternation
        # consumes the phrase whole.
        modality_map=(
            ("must not", ("不得",)),
            ("should not", ("不應",)),
            ("must", ("必須",)),
            ("should", ("應",)),
            ("may", ("可",)),
        ),
        negation_tier="hard",
    ),
}


def get_profile(lang):
    """Resolve a language tag to its `LanguageProfile`; raise `ValueError`
    with the supported set on an unknown tag."""
    try:
        return _PROFILES[lang]
    except KeyError:
        supported = ", ".join(sorted(_PROFILES))
        raise ValueError(
            f"unknown language profile {lang!r} (supported: {supported})"
        ) from None
