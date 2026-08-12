#!/usr/bin/env python3
"""Tests for adjudication_lint.py — hard checks (Task 3).

Fixtures are inline units-JSON dicts (repo convention — see
test_adjudication_split.py). No file I/O needed: run_checks() takes
units (a list of dicts) directly; a thin CLI wrapper handles the file
read in main().
"""

import unittest

from adjudication_lint import run_checks, CHECKS, check_nonempty_rendition, check_anchor_echo


def _unit(id_="u1", heading="Task 1", source_text="do 42 things", anchors=("42",), rendition="做 42 件事"):
    return {
        "id": id_,
        "heading": heading,
        "source_text": source_text,
        "anchors": list(anchors),
        "rendition": rendition,
    }


class TestHardChecks(unittest.TestCase):
    def test_missing_anchor_echo_fails_lint(self):
        units = [_unit(rendition="做一些事情")]  # "42" not echoed
        violations = run_checks(units)
        self.assertTrue(violations, "expected at least one violation")
        self.assertTrue(any("u1" in v and "42" in v for v in violations))

    def test_clean_fixture_passes_lint(self):
        units = [
            _unit(id_="u1", source_text="do 42 things", anchors=("42",), rendition="做 42 件事"),
            _unit(id_="u2", source_text="must use `foo_bar`", anchors=("foo_bar",), rendition="必須使用 `foo_bar`"),
        ]
        violations = run_checks(units)
        self.assertEqual(violations, [])

    def test_empty_rendition_fails_lint(self):
        units = [_unit(rendition="")]
        violations = run_checks(units)
        self.assertTrue(any("u1" in v and "empty" in v.lower() for v in violations))

    def test_check_nonempty_rendition_direct(self):
        self.assertEqual(check_nonempty_rendition(_unit(rendition="")), ["u1: empty rendition"])
        self.assertEqual(check_nonempty_rendition(_unit(rendition="有內容")), [])

    def test_check_anchor_echo_direct(self):
        unit = _unit(anchors=("42", "foo_bar"), rendition="做 42 件事")
        self.assertEqual(check_anchor_echo(unit), ["u1: missing anchor 'foo_bar'"])

    def test_checks_list_is_composable(self):
        # Task 4 appends language checks to this list without changing
        # run_checks' signature — pin the composability contract.
        self.assertIn(check_nonempty_rendition, CHECKS)
        self.assertIn(check_anchor_echo, CHECKS)
        for fn in CHECKS:
            self.assertTrue(callable(fn))

    def test_numeric_anchor_inside_larger_number_fails_lint(self):
        # "1" must not be considered echoed merely because it is a
        # digit substring of "10" — plain `in` would false-negative
        # this (the source's "1" was never actually rendered).
        unit = _unit(anchors=("1",), rendition="失敗時必須以 10 結束")
        violations = check_anchor_echo(unit)
        self.assertTrue(any("u1" in v and "'1'" in v for v in violations))

    def test_unit_with_zero_anchors_passes_lint(self):
        units = [_unit(anchors=(), rendition="沒有錨點")]
        self.assertEqual(run_checks(units), [])

    def test_multiple_missing_anchors_all_reported(self):
        unit = _unit(anchors=("42", "foo_bar", "99"), rendition="做一些事情")
        violations = check_anchor_echo(unit)
        self.assertEqual(len(violations), 3)
        self.assertTrue(any("'42'" in v for v in violations))
        self.assertTrue(any("'foo_bar'" in v for v in violations))
        self.assertTrue(any("'99'" in v for v in violations))

    def test_numeric_anchor_cjk_punctuation_boundary_passes(self):
        # Non-digit boundary (CJK punctuation flush against the
        # number) must still count as echoed.
        unit = _unit(anchors=("42",), rendition="次數為 42。")
        self.assertEqual(check_anchor_echo(unit), [])

    def test_dotted_version_anchor_still_matches_via_substring(self):
        # "0.77" is not purely digits (contains "."), so it keeps
        # plain substring matching — must still match inside "0.77.0".
        unit = _unit(anchors=("0.77",), rendition="升級到 0.77.0 版本")
        self.assertEqual(check_anchor_echo(unit), [])


if __name__ == "__main__":
    unittest.main()
