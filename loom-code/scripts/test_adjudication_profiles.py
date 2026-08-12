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
        self.assertEqual(profile.negation_prefix, "不未非")
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

    def test_unknown_lang_raises_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_profile("fr")
        self.assertIn("fr", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
