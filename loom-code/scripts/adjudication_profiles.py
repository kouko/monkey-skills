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

`negation_pattern` (Task 2): zh-Hant's negation model is a CHARACTER
SET (`negation_markers`) — Chinese negation is a standalone character.
Japanese negation is inflectional (a kana suffix on the verb), which a
character set cannot express, so `negation_pattern` carries an
optional regex string that the checker prefers over `negation_markers`
when present. This keeps one negation-counting code path in
adjudication_lint.py instead of forking a second function per model
shape — see `_count_negation_markers`.

stdlib only.
"""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class LanguageProfile:
    lang: str
    negation_markers: str
    negation_prefix: str
    modality_map: Tuple[Tuple[str, Tuple[str, ...]], ...]
    negation_tier: str  # "hard" | "warning"
    # Optional regex string; when set, the checker counts pattern
    # matches instead of scanning `negation_markers` char-by-char.
    # None for zh-Hant (its character-set model is unchanged).
    negation_pattern: Optional[str] = None


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
    "ja": LanguageProfile(
        lang="ja",
        # Unused: this profile's negation detection uses
        # `negation_pattern` (below), not a character set. Kept empty
        # rather than omitted so every profile has the same shape.
        negation_markers="",
        # Unused for the same reason: the modality polarity-inversion
        # check (`_all_occurrences_negated`) looks for a PREFIX
        # character immediately before a modality form, which is a
        # zh-Hant-specific (prefix-negation) grammatical fact that
        # does not hold for Japanese (suffix/inflectional negation).
        # An empty set makes that check a no-op for ja rather than
        # silently reusing zh-Hant's prefix chars.
        negation_prefix="",
        # JIS Z 8301:2019 Clause 7 (Tables 3-5), derived-from per the
        # brief's two caveats: the English column is 参考 not 規定, and
        # our "must"/"should" map by force (semantic obligation) to
        # JIS's 要求/推奨 tables, not to JIS's own literal "must" row
        # (which denotes an external constraint in JIS's own scheme).
        # Order matters, same convention as zh-Hant: two-word terms
        # before their single-word prefixes.
        #
        # DELIBERATE NARROWING from the JIS Table 3 list (Task 2
        # revision round 1, Finding A): JIS also lists bare `する` and
        # the copula construction `とする` as acceptable "must" forms.
        # Both were dropped here -- this is a recorded deviation from
        # JIS, not conformance (see the module docstring's caveat),
        # narrowing permitted for that reason. Measured reason: a
        # generic verb stem carries no lexical obligation signal, so
        # it cannot distinguish obligation from prohibition. Reproduced
        # failure: source "you must execute this", rendition
        # 「実行しないこととする」 (a PROHIBITION, meaning fully
        # inverted) -- `とする` is a substring of that prohibitive
        # construction (`...ないこととする`), so with `とする` accepted
        # the mapping matched and emitted zero warnings on an inverted
        # rendition. `しなければならない` is the one JIS form that is
        # lexically unambiguous (the construction itself encodes
        # obligation, not just a bare verb ending), so it is the only
        # form kept.
        modality_map=(
            ("must not", ("してはならない", "しない")),
            ("should not", ("望ましくない", "しない方がよい")),
            ("must", ("しなければならない",)),
            ("should", ("することが望ましい", "するのがよい", "することを推奨する")),
            ("may", ("してもよい", "してよい", "差し支えない")),
        ),
        # Warning tier by design, not omission (brief Alternatives):
        # a naive kana negation regex is a homograph of the い-adjective
        # ending — 少ない (few) / 危ない (dangerous) / つまらない (boring)
        # all match, none are negations. No third-party morphological
        # analyzer is in budget (stdlib-only contract), so the signal
        # is real but unreliable; it informs, it must never gate. Do
        # NOT promote this to "hard" without new evidence — see the
        # plan's ## Notes "Japanese negation stays WARNING-tier".
        negation_tier="warning",
        # Kana negation pattern, NARROWED (Task 2 revision round 1,
        # Finding B) from the plan's original ない/ません/ぬ/ず/まい to
        # just ない/ません. Measured reason: ぬ and まい are archaic/rare
        # in modern technical prose, so their recall value is near
        # zero, while ず collides with common words that are NOT
        # negation -- most notably 必ず ("surely"/"without fail"), one
        # of the most frequent words in Japanese technical
        # instructions. Reproduced failure: source "The verdict block
        # must not be rewritten.", rendition 「verdict ブロックを必ず
        # 書き換えます。」 (meaning fully INVERTED -- it asserts the
        # rewrite WILL happen) matched `ず` inside 必ず and
        # check_negation_preserved silently returned zero warnings.
        # Other measured ず-collision words with the same risk:
        # わずか, いぬ, 死ぬ, うまい. Dropping ぬ/ず/まい turns those
        # silent misses into correctly-triggered warnings without
        # adding an exception lexicon (out of scope per the brief).
        # Same い-adjective false-positive caveat as the tier comment
        # above still applies to the remaining ない/ません forms.
        negation_pattern=r"ません|ない",
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
