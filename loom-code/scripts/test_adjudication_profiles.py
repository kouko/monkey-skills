#!/usr/bin/env python3
"""Tests for adjudication_profiles.py (Task 1): the zh-Hant profile must
carry the three language facts moved verbatim out of adjudication_lint.py,
and get_profile() must resolve tags / raise clearly on an unknown one.
"""

import unittest

from adjudication_profiles import get_profile


class TestZhHantProfile(unittest.TestCase):
    def test_zh_hant_profile_carries_the_shipped_language_facts(self):
        profile = get_profile("zh-Hant")
        self.assertEqual(profile.negation_markers, "不未無非沒勿")
        # A TUPLE of prefix strings, not a character set: ja needs
        # multi-character kana prefixes (see
        # test_negation_prefix_is_a_tuple_of_strings). zh-Hant's three
        # characters become one-character strings -- same semantics.
        self.assertEqual(profile.negation_prefix, ("不", "未", "非"))
        self.assertEqual(
            profile.modality_map,
            (
                ("must not", ("不得",)),
                ("should not", ("不應",)),
                ("must", ("必須",)),
                ("should", ("應",)),
                ("may", ("可",)),
            ),
        )
        self.assertEqual(profile.negation_tier, "hard")

    def test_modality_map_values_are_tuples(self):
        profile = get_profile("zh-Hant")
        for _term, forms in profile.modality_map:
            self.assertIsInstance(forms, tuple)

    def test_verdict_labels_are_per_profile(self):
        # Whole-branch review F3: the verdict table's two content column
        # labels are per-language presentation facts and belong beside
        # page_lang / font_stack. zh-Hant's pair is pinned byte-identical
        # to the shipped header; ja's is natural Japanese, not Chinese.
        self.assertEqual(get_profile("zh-Hant").verdict_labels, ("摘述", "錨點"))
        self.assertEqual(get_profile("ja").verdict_labels, ("要約", "アンカー"))

    def test_negation_prefix_is_a_tuple_of_strings(self):
        # Whole-branch review F5: ja's negation morphemes that can sit
        # between the verb and a modality suffix (「なく」/「ない」) are
        # multi-character, so a character set cannot express them and
        # ja's polarity guard was a no-op. Both profiles now carry a
        # tuple of prefix STRINGS.
        for lang in ("zh-Hant", "ja"):
            prefix = get_profile(lang).negation_prefix
            self.assertIsInstance(prefix, tuple, lang)
            for item in prefix:
                self.assertIsInstance(item, str, lang)
        self.assertEqual(get_profile("ja").negation_prefix, ("なく", "ない"))

    def test_unknown_lang_raises_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_profile("fr")
        self.assertIn("fr", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
