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
    # Tuple of negation-morpheme STRINGS that invert a modality form
    # when they immediately precede it. Not a character set: Japanese
    # needs multi-character kana prefixes (whole-branch review F5).
    negation_prefix: Tuple[str, ...]
    modality_map: Tuple[Tuple[str, Tuple[str, ...]], ...]
    negation_tier: str  # "hard" | "warning"
    # Optional regex string; when set, the checker counts pattern
    # matches instead of scanning `negation_markers` char-by-char.
    # None for zh-Hant (its character-set model is unchanged).
    negation_pattern: Optional[str] = None
    # Task 3: the renderer's per-profile page attributes. `page_lang`
    # is the exact value that belongs in `<html lang="...">`.
    # `font_stack` is the exact CSS `font-family` value (the whole
    # comma-separated list, not just the CJK face) -- zh-Hant's is the
    # literal string that used to be hardcoded in adjudication_render.py,
    # copied verbatim so its output cannot shift.
    page_lang: str = "zh-Hant"
    font_stack: str = '-apple-system, "Segoe UI", "Noto Sans TC", sans-serif'
    # The verdict table's two content column labels, in table order
    # (summary, anchor). `#` and `severity` are not translated -- they
    # are the protocol's own field names. This lives here, beside
    # `page_lang` / `font_stack`, because it is the same kind of fact:
    # per-language presentation the renderer reads rather than hardcodes
    # (whole-branch review F3 -- verdict mode had never joined the
    # profile layer, so a `--lang ja` page carried Chinese headers).
    verdict_labels: Tuple[str, str] = ("摘述", "錨點")


_PROFILES = {
    "zh-Hant": LanguageProfile(
        lang="zh-Hant",
        # Moved verbatim from adjudication_lint._ZH_NEGATION_MARKERS.
        negation_markers="不未無非沒勿",
        # Moved verbatim from adjudication_lint._ZH_NEGATION_PREFIX,
        # each character now its own single-character string (the field
        # became a tuple for ja's sake) -- semantics unchanged.
        negation_prefix=("不", "未", "非"),
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
        page_lang="zh-Hant",
        font_stack='-apple-system, "Segoe UI", "Noto Sans TC", sans-serif',
        # Byte-identical to the labels the verdict renderer used to
        # hardcode -- zh-Hant output cannot shift.
        verdict_labels=("摘述", "錨點"),
    ),
    "ja": LanguageProfile(
        lang="ja",
        # Unused: this profile's negation detection uses
        # `negation_pattern` (below), not a character set. Kept empty
        # rather than omitted so every profile has the same shape.
        negation_markers="",
        # The modality polarity-inversion check
        # (`_all_occurrences_negated`) tests whether a modality form is
        # immediately preceded by a negation morpheme. This WAS empty
        # (a deliberate no-op) while every ja form carried a leading
        # 「し」 that incidentally excluded an intervening negation.
        # Making the forms verb-independent (F1) removed that guard and
        # opened a silent polarity inversion (whole-branch review F5):
        # 「書き換えなくてはならない」 (= must rewrite) ends in
        # 「てはならない」, and 「書き換えないことが望ましい」 (= desirable
        # NOT to rewrite) ends in 「ことが望ましい」, so both fully
        # inverted renditions matched their source modal and warned
        # nothing. 「なく」 (the 〜なくてはならない / 〜なくてもよい stem)
        # and 「ない」 (the plain negative before a nominalizer) are the
        # two morphemes that can sit in that slot; listing them makes
        # this check load-bearing for ja rather than a no-op.
        negation_prefix=("なく", "ない"),
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
        #
        # VERB-INDEPENDENT SUFFIXES (whole-branch review, Finding F1):
        # Japanese modality is a suffix on whatever verb precedes it, so
        # every form below is stored WITHOUT the サ変 verb that used to
        # lead it (「してはならない」 -> 「てはならない」,
        # 「することが望ましい」 -> 「ことが望ましい」). The old forms only
        # matched サ変 renditions (実行する): the correct rendition of
        # "you must rewrite it" is 「書き換えなければならない」 -- never
        # 「書き換えしなければならない」 -- and it warned. Each stored form
        # is a proper suffix of the form it replaces, so every rendition
        # that used to match still matches; only the added non-サ変
        # renditions are new. Forms carrying no サ変 verb at all
        # (「望ましくない」, 「差し支えない」) are unchanged.
        #
        # Bare 「しない」 (must not) is DROPPED rather than shortened:
        # its verb-independent form is 「ない」, which collides with every
        # い-adjective and with 「ならない」 itself -- far too coarse to
        # list. Dropping it retires the recorded T2 debt in passing
        # (「しない」 was a literal substring of should-not's
        # 「しない方がよい」, so a should-not rendition silently satisfied
        # a must-not source); must-not now matches only 「てはならない」.
        #
        # The class of collision that MATTERS here is an intervening
        # negation morpheme: because these forms are bare suffixes, an
        # inverted rendition can end in the very form its source modal
        # expects (「なくてはならない」 ⊃ 「てはならない」,
        # 「ないことが望ましい」 ⊃ 「ことが望ましい」). That is a full
        # direction flip, not a near-miss, and it is caught -- by
        # `negation_prefix` below, which `_all_occurrences_negated`
        # reads; see its comment for the two morphemes covered.
        #
        # Residual collision, recorded not fixed: 「のがよい」 (should)
        # matches inside 「ものがよい」, and 「ない方がよい」 (should not)
        # inside any 〜ない方がよい clause. Unlike the inversion class
        # above these do not flip direction -- they accept a rendition
        # whose modality is merely unproven -- so they stay false-QUIET
        # risks on a warning-tier check, one tier below the
        # false-warning F1 replaced.
        modality_map=(
            ("must not", ("てはならない",)),
            ("should not", ("望ましくない", "ない方がよい")),
            ("must", ("なければならない",)),
            ("should", ("ことが望ましい", "のがよい", "ことを推奨する")),
            ("may", ("てもよい", "てよい", "差し支えない")),
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
        # Construction-internal collision (whole-branch review F4,
        # reviewer-probed and re-verified here): 「ない」 also matches
        # INSIDE 「ならない」 — i.e. inside ja's own `must` form
        # 「〜なければならない」 — so an inverted rendition
        # 「ブロックを書き換えなければならない。」 for a must-not source
        # counts one marker and this check stays silent. The modality
        # check is the second line of defence there and does fire
        # (measured: `WARNING u1: expected 「てはならない」 for 'must not'`).
        negation_pattern=r"ません|ない",
        # Task 3: same shape as zh-Hant's stack, JP face swapped in as
        # the CJK-specific member of the list.
        page_lang="ja",
        font_stack='-apple-system, "Segoe UI", "Noto Sans JP", sans-serif',
        # Natural Japanese, not the Chinese labels transliterated:
        # 摘述 -> 要約, 錨點 -> アンカー.
        verdict_labels=("要約", "アンカー"),
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
