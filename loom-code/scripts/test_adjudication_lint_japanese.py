#!/usr/bin/env python3
"""Tests for the `ja` language profile (Task 2): JIS-derived modality
set-membership and warning-tier negation, per
docs/loom/specs/2026-08-12-adjudication-view-japanese.md Smallest End
State item 4 and Task 2's acceptance criteria.

Fixtures follow test_adjudication_lint_language.py's inline-dict
convention; the check-list wiring mirrors adjudication_lint.main()'s
functools.partial(profile=...) pattern.
"""

import dataclasses
import functools
import unicodedata
import unittest

from adjudication_lint import (
    check_anchor_echo,
    check_modality_mapping,
    check_negation_preserved,
    check_nonempty_rendition,
    exit_code_for,
    run_checks,
)
from adjudication_profiles import get_profile


def _unit(id_="u1", heading="Task 1", source_text="do 42 things", anchors=(), rendition="做 42 件事"):
    return {
        "id": id_,
        "heading": heading,
        "source_text": source_text,
        "anchors": list(anchors),
        "rendition": rendition,
    }


def _checks_for(lang):
    profile = get_profile(lang)
    return [
        check_nonempty_rendition,
        check_anchor_echo,
        functools.partial(check_negation_preserved, profile=profile),
        functools.partial(check_modality_mapping, profile=profile),
    ]


class TestJapaneseNegationTier(unittest.TestCase):
    def test_japanese_negation_mismatch_warns_not_blocks(self):
        # Brief's measured failure case: a faithful Japanese rendition
        # of a negated source. Today's zh-Hant checker (looking for ZH
        # negation chars) exits 1 on this input; under --lang ja it
        # must exit 0 -- the negation IS preserved (「いけません」
        # carries 「ません」, a kana negation pattern), and even a
        # modality-form miss on this exact phrasing is warning-only.
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えてはいけません。",
        )
        violations = run_checks([unit], checks=_checks_for("ja"))
        self.assertEqual(exit_code_for(violations), 0)

    def test_japanese_negation_genuinely_dropped_warns_and_stays_exit_zero(self):
        # A rendition that drops the negation outright (reads as an
        # affirmative instruction, no kana negation pattern anywhere)
        # must still surface a WARNING line -- the signal is reported,
        # never silenced -- but must NOT flip the exit code, because
        # ja's negation_tier is "warning".
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えます。",
        )
        violations = run_checks([unit], checks=_checks_for("ja"))
        warning_lines = [v for v in violations if v.startswith("WARNING ")]
        self.assertTrue(
            any("u1" in v and "negation dropped" in v for v in warning_lines),
            f"expected a negation-dropped WARNING line, got: {violations}",
        )
        self.assertEqual(exit_code_for(violations), 0)

    def test_zh_hant_negation_still_hard_fails_tier_is_per_profile(self):
        # Regression pin: adding ja's warning tier must not soften
        # zh-Hant's existing hard tier. Same shape of dropped negation,
        # zh-Hant profile -- must still exit 1, and the violation line
        # must NOT be WARNING-prefixed.
        unit = _unit(source_text="do not skip this step", rendition="跳過此步驟")
        violations = run_checks([unit], checks=_checks_for("zh-Hant"))
        self.assertTrue(
            any("u1" in v and "negation dropped" in v and not v.startswith("WARNING ") for v in violations)
        )
        self.assertEqual(exit_code_for(violations), 1)


class TestJapaneseModalitySetMembership(unittest.TestCase):
    def test_may_accepts_shitemo_yoi_form(self):
        unit = _unit(source_text="you may skip this", rendition="スキップしてもよい")
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_may_accepts_sashitsukaenai_form(self):
        # A DIFFERENT JIS-accepted form for the SAME modal ("may") must
        # be equally quiet -- set-membership, not single-form match.
        unit = _unit(source_text="you may skip this", rendition="スキップしても差し支えない")
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_must_not_accepts_shitewa_naranai_form(self):
        unit = _unit(source_text="you must not skip this", rendition="スキップしてはならない")
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_missing_modality_form_still_warns_under_ja(self):
        unit = _unit(source_text="you may skip this", rendition="スキップする")
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(any("u1" in w for w in warnings))

    def test_must_accepts_only_shinakereba_naranai_form(self):
        # Regression pin: the one legitimate "must" form still passes
        # quietly after narrowing away する/とする.
        unit = _unit(source_text="you must do this", rendition="実行しなければならない")
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_must_bare_suru_no_longer_satisfies_the_mapping(self):
        # RED-A companion: with する/とする dropped, a bare-verb
        # rendition for "must" now correctly WARNS instead of silently
        # passing (する carried no obligation signal to begin with).
        unit = _unit(source_text="you must do this", rendition="実行する")
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(any("u1" in w for w in warnings))

    def test_must_prohibition_rendition_now_warns_instead_of_silent(self):
        # RED-A (Finding A, spec arm): source states an obligation
        # ("must execute"), but the rendition is actually a
        # PROHIBITION ("shall provide that [it] will not be
        # executed") -- meaning fully inverted. Before the fix,
        # `とする` is a substring of `しないこととする` and silently
        # satisfied the "must" mapping, so check_modality_mapping
        # returned [] on an inverted rendition. After narrowing
        # "must" to only 「しなければならない」, this must WARN.
        unit = _unit(
            source_text="you must execute this",
            rendition="実行しないこととする",
        )
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(
            any("u1" in w for w in warnings),
            f"expected a 'must' mapping WARNING, got: {warnings}",
        )


class TestJapaneseModalityFormsAreVerbIndependent(unittest.TestCase):
    """Whole-branch review finding F1: Japanese modality is a SUFFIX on
    whatever verb precedes it, so a form list that bakes in the サ変 stem
    「し」 only matches サ変 verbs (実行する). For a non-サ変 verb the
    sanctioned rendition is 「書き換えてはならない」 -- never
    「書き換えしてはならない」 -- so a grammatically CORRECT rendition
    warned. Every fixture below uses 書き換える (godan, not サ変)."""

    def test_must_accepts_non_sahen_verb(self):
        unit = _unit(
            source_text="you must rewrite it",
            rendition="verdict ブロックを書き換えなければならない。",
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_must_not_accepts_non_sahen_verb(self):
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えてはならない。",
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_should_accepts_non_sahen_verb(self):
        unit = _unit(
            source_text="you should rewrite it",
            rendition="verdict ブロックを書き換えることが望ましい。",
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_should_not_accepts_non_sahen_verb(self):
        unit = _unit(
            source_text="you should not rewrite it",
            rendition="verdict ブロックを書き換えない方がよい。",
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_may_accepts_non_sahen_verb(self):
        unit = _unit(
            source_text="you may rewrite it",
            rendition="verdict ブロックを書き換えてもよい。",
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_should_not_rendition_no_longer_satisfies_a_must_not_source(self):
        # The T2 Decision-Log debt (「しない」 ⊂ 「しない方がよい」) is
        # retired as a side effect of dropping bare 「しない」 from the
        # must-not set: a should-not rendition for a must-not source used
        # to pass silently, and must now WARN.
        unit = _unit(
            source_text="you must not skip this", rendition="スキップしない方がよい"
        )
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(
            any("u1" in w for w in warnings),
            f"expected a 'must not' mapping WARNING, got: {warnings}",
        )


class TestJapaneseModalityPolarityInversion(unittest.TestCase):
    """Whole-branch review finding F5: making the ja forms
    verb-independent (F1) dropped the leading 「し」 that had been
    INCIDENTALLY guarding against an intervening negation morpheme.
    「なくてはならない」 ends in 「てはならない」 and 「ないことが望ましい」
    ends in 「ことが望ましい」, so both fully-inverted renditions became
    silent. ja's `negation_prefix` (now a tuple of kana strings, not a
    character set) is the guard that makes them WARN again."""

    def test_must_not_source_rendered_as_an_obligation_warns(self):
        # 「書き換えなくてはならない」 = "must rewrite" -- the exact
        # opposite of the must-not source.
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えなくてはならない。",
        )
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(
            any("u1" in w and "appears only negated" in w for w in warnings),
            f"expected a polarity-inversion WARNING, got: {warnings}",
        )

    def test_should_source_rendered_as_a_negative_recommendation_warns(self):
        # 「書き換えないことが望ましい」 = "it is desirable NOT to
        # rewrite" -- the opposite of the affirmative should source.
        unit = _unit(
            source_text="you should rewrite it",
            rendition="verdict ブロックを書き換えないことが望ましい。",
        )
        warnings = check_modality_mapping(unit, profile=get_profile("ja"))
        self.assertTrue(
            any("u1" in w and "appears only negated" in w for w in warnings),
            f"expected a polarity-inversion WARNING, got: {warnings}",
        )

    def test_zh_hant_polarity_inversion_still_flags(self):
        # Regression pin, negative direction: zh-Hant's prefix chars
        # became one-character strings, so its polarity semantics must
        # be byte-for-byte unchanged.
        unit = _unit(source_text="you should skip this", rendition="不應跳過")
        warnings = check_modality_mapping(unit, profile=get_profile("zh-Hant"))
        self.assertTrue(
            any("appears only negated" in w for w in warnings),
            f"expected a polarity-inversion WARNING, got: {warnings}",
        )

    def test_zh_hant_affirmative_rendition_stays_quiet(self):
        unit = _unit(source_text="you should execute this", rendition="應執行")
        self.assertEqual(
            check_modality_mapping(unit, profile=get_profile("zh-Hant")), []
        )

    def test_zh_hant_must_not_rendition_stays_quiet(self):
        # 不得 IS the sanctioned must-not form; the 不 that opens it is
        # part of the form, not an intervening negation.
        unit = _unit(source_text="you must not skip this", rendition="不得跳過")
        self.assertEqual(
            check_modality_mapping(unit, profile=get_profile("zh-Hant")), []
        )


class TestJapaneseNegationCollisionWords(unittest.TestCase):
    def test_negation_dropped_but_masked_by_narazu_now_warns(self):
        # RED-B (Finding B, quality arm): source is a prohibition
        # ("must not be rewritten"), rendition asserts the opposite
        # ("will definitely rewrite") -- meaning fully inverted. Before
        # the fix, 必ず contains ず, so the ja negation_pattern
        # (which included ず) matched inside 必ず and
        # check_negation_preserved silently returned []. After
        # dropping ず (and ぬ/まい) from the pattern, this must WARN.
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを必ず書き換えます。",
        )
        violations = run_checks([unit], checks=_checks_for("ja"))
        warning_lines = [v for v in violations if v.startswith("WARNING ")]
        self.assertTrue(
            any("u1" in v and "negation dropped" in v for v in warning_lines),
            f"expected a negation-dropped WARNING line, got: {violations}",
        )
        self.assertEqual(exit_code_for(violations), 0)

    def test_correct_negation_via_nai_still_passes_quietly(self):
        # Regression pin: the legitimate ない negation form is
        # unaffected by dropping ぬ/ず/まい.
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えない。",
        )
        self.assertEqual(check_negation_preserved(unit, profile=get_profile("ja")), [])

    def test_correct_negation_via_masen_still_passes_quietly(self):
        # Regression pin: ません is unaffected.
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックを書き換えません。",
        )
        self.assertEqual(check_negation_preserved(unit, profile=get_profile("ja")), [])

    def test_narazu_inside_otherwise_correct_negation_does_not_double_count(self):
        # 必ず appearing alongside a genuine ない negation must not be
        # double-counted as a second negation marker (it still
        # contributes 0 real negation signal -- ず is no longer in the
        # pattern at all, so only the one ない match counts).
        unit = _unit(
            source_text="The verdict block must not be rewritten.",
            rendition="verdict ブロックは必ず書き換えない。",
        )
        self.assertEqual(check_negation_preserved(unit, profile=get_profile("ja")), [])


class TestRenditionIsUnicodeNormalizedBeforeMatching(unittest.TestCase):
    """Whole-branch review finding F2 (CHK-SEC-005, canonicalize before
    you compare): the checks match untrusted rendition text by exact
    codepoint against NFC-composed literals, so the SAME Japanese
    sentence submitted in NFD (dakuten as a combining mark) silently
    stopped matching every form containing 「ば」/「が」/「ざ」 -- turning a
    faithful rendition into a WARNING, and, on the negation side, hiding
    a preserved negation."""

    def test_nfd_rendition_still_matches_the_must_form(self):
        # 「なければならない」 carries ば -> U+306F + U+3099 under NFD.
        unit = _unit(
            source_text="you must do this",
            rendition=unicodedata.normalize("NFD", "実行しなければならない"),
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_nfd_rendition_still_matches_the_should_form(self):
        # 「ことが望ましい」 carries が -> U+304B + U+3099 under NFD.
        unit = _unit(
            source_text="you should do this",
            rendition=unicodedata.normalize("NFD", "実行することが望ましい"),
        )
        self.assertEqual(check_modality_mapping(unit, profile=get_profile("ja")), [])

    def test_nfd_rendition_still_counts_a_negation_marker(self):
        # Today's ja negation_pattern (ない/ません) happens to carry no
        # dakuten, so it cannot exhibit the bug itself. The negation scan
        # must normalize regardless -- pinned here with a profile whose
        # pattern carries a real dakuten negation form (godan ぶ-verbs:
        # 選ぶ -> 選ばない), which is exactly what a widened pattern would
        # add. Without normalization this rendition counts zero markers
        # and the unit warns.
        profile = dataclasses.replace(
            get_profile("ja"), negation_pattern=r"ばない|ません"
        )
        unit = _unit(
            source_text="do not choose it",
            rendition=unicodedata.normalize("NFD", "選ばない"),
        )
        self.assertEqual(check_negation_preserved(unit, profile=profile), [])


if __name__ == "__main__":
    unittest.main()
