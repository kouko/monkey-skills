#!/usr/bin/env python3
"""Tests for adjudication_lint.py — language checks (Task 4): negation
presence (hard fail) and modality mapping (warning-only), per
loom-code/skills/using-loom-code/protocols/adjudication-view.md
"Fixed modality mapping" and "Lint-failure rule".

Fixtures follow test_adjudication_lint.py's inline-dict convention.
"""

import unittest

from adjudication_lint import (
    run_checks,
    exit_code_for,
    check_negation_preserved,
    check_modality_mapping,
)


def _unit(id_="u1", heading="Task 1", source_text="do 42 things", anchors=(), rendition="做 42 件事"):
    return {
        "id": id_,
        "heading": heading,
        "source_text": source_text,
        "anchors": list(anchors),
        "rendition": rendition,
    }


class TestNegationPreserved(unittest.TestCase):
    def test_negation_dropped_in_rendition_fails(self):
        # Source says "do not skip" — rendition drops the negation
        # entirely (reads as an affirmative instruction). This is the
        # dominant failure mode per the protocol's research note.
        unit = _unit(source_text="do not skip this step", rendition="跳過此步驟")
        violations = run_checks([unit])
        self.assertTrue(violations, "expected a negation-dropped violation")
        self.assertTrue(any("u1" in v and "negation" in v.lower() for v in violations))
        self.assertEqual(exit_code_for(violations), 1)

    def test_negation_preserved_in_rendition_passes(self):
        unit = _unit(source_text="do not skip this step", rendition="不要跳過此步驟")
        self.assertEqual(check_negation_preserved(unit), [])

    def test_without_token_requires_zh_negation(self):
        unit = _unit(source_text="ship without review", rendition="沒有審查就出貨")
        self.assertEqual(check_negation_preserved(unit), [])

    def test_without_token_dropped_fails(self):
        unit = _unit(source_text="ship without review", rendition="出貨並審查")
        violations = check_negation_preserved(unit)
        self.assertTrue(any("u1" in v for v in violations))

    def test_note_colon_does_not_trigger_negation(self):
        # "Note:" contains "not" as a substring but is not the word
        # "not" — must not require a ZH negation marker.
        unit = _unit(source_text="Note: this step is optional", rendition="這個步驟是選擇性的")
        self.assertEqual(check_negation_preserved(unit), [])

    def test_nothing_does_not_trigger_negation(self):
        # "nothing" contains both "no" and "not" as substrings but is
        # neither word — must not require a ZH negation marker.
        unit = _unit(source_text="there is nothing to configure here", rendition="這裡沒有東西要設定")
        self.assertEqual(check_negation_preserved(unit), [])

    def test_no_negation_in_source_is_quiet_regardless_of_rendition(self):
        unit = _unit(source_text="ship this feature", rendition="出貨這個功能")
        self.assertEqual(check_negation_preserved(unit), [])

    def test_multi_negation_partial_drop_warns_and_stays_exit_zero(self):
        # Round-1 finding 1: the old whole-unit any() check sees ONE
        # preserved marker and calls the unit clean — it cannot tell
        # that the *second* negation ("never merge") was dropped. The
        # two-tier count (N=2 source tokens, M=1 rendition markers)
        # must catch this as a WARNING, not silence, and must not
        # flip the exit code.
        unit = _unit(
            source_text="do not skip this step and never merge that branch",
            rendition="不要跳過此步驟，合併該分支",
        )
        violations = run_checks([unit])
        warning_lines = [v for v in violations if v.startswith("WARNING ")]
        self.assertTrue(warning_lines, "expected a negation count shortfall WARNING")
        self.assertTrue(
            any("u1" in v and "negation count shortfall" in v and "source 2" in v and "rendition 1" in v for v in warning_lines)
        )
        self.assertEqual(exit_code_for(violations), 0)

    def test_multi_negation_full_drop_is_hard_violation(self):
        # Same two-negation source as above, but M=0 this time — total
        # absence must stay the existing HARD, exit-affecting failure.
        unit = _unit(
            source_text="do not skip this step and never merge that branch",
            rendition="跳過此步驟，合併該分支",
        )
        violations = check_negation_preserved(unit)
        self.assertTrue(any("u1" in v and "negation dropped" in v for v in violations))
        self.assertFalse(any(v.startswith("WARNING ") for v in violations))
        self.assertEqual(exit_code_for(violations), 1)

    def test_negation_token_inside_backtick_span_is_excluded(self):
        # "no" inside `--no-verify`, backticked, must not count as a
        # source negation token (round-1 finding 2).
        unit = _unit(
            source_text="run `git commit --no-verify` to skip the hook",
            rendition="執行指令以跳過 hook",
        )
        self.assertEqual(run_checks([unit]), [])

    def test_negation_token_in_hyphen_flag_context_unbackticked_is_excluded(self):
        # Same "no" as above but NOT backticked — the hyphen-precede
        # check alone must exclude it (round-1 finding 2).
        unit = _unit(
            source_text="run git commit --no-verify to skip the hook",
            rendition="執行指令以跳過 hook",
        )
        self.assertEqual(run_checks([unit]), [])


class TestModalityMapping(unittest.TestCase):
    def test_modality_mismatch_emits_warning_and_stays_exit_zero(self):
        unit = _unit(source_text="you must complete this task", rendition="完成這個任務")
        violations = run_checks([unit])
        warning_lines = [v for v in violations if v.startswith("WARNING ")]
        self.assertTrue(warning_lines, "expected a modality WARNING line")
        self.assertTrue(any("u1" in v and "必須" in v for v in warning_lines))
        self.assertEqual(exit_code_for(violations), 0)

    def test_modality_match_is_quiet(self):
        unit = _unit(source_text="you must complete this task", rendition="必須完成這個任務")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_must_not_maps_to_bude_not_double_counted_as_must(self):
        # "must not" must map only to 不得 — it must NOT also demand
        # 必須 (that would be double-counting "must" inside "must not").
        unit = _unit(source_text="you must not skip this", rendition="不得跳過這個")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_must_not_missing_bude_warns_once_not_twice(self):
        unit = _unit(source_text="you must not skip this", rendition="跳過這個")
        warnings = check_modality_mapping(unit)
        self.assertEqual(len(warnings), 1)
        self.assertIn("不得", warnings[0])
        self.assertNotIn("必須", warnings[0])

    def test_should_not_maps_to_bu_ying(self):
        unit = _unit(source_text="you should not do this", rendition="不應這麼做")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_may_maps_to_ke(self):
        unit = _unit(source_text="you may skip this", rendition="可跳過")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_no_modal_verb_is_quiet(self):
        unit = _unit(source_text="ship this feature", rendition="出貨這個功能")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_modal_token_inside_backtick_span_excluded_from_scan(self):
        # Fix 3(a) — parity with _count_en_negations: a modal token
        # inside a backticked span (code/flag reference) is not a
        # modality claim.
        unit = _unit(source_text="run `you must confirm` first", rendition="先執行")
        self.assertEqual(check_modality_mapping(unit), [])

    def test_modality_polarity_inversion_only_negated_form_warns_distinctly(self):
        # Fix 3(b): source says "should" (affirmative obligation) but
        # the rendition only ever has 不應 (negated) -- never a
        # standalone 應. This is a distinct warning from "missing".
        unit = _unit(source_text="you should complete this task", rendition="你不應完成這個任務")
        warnings = check_modality_mapping(unit)
        self.assertEqual(len(warnings), 1)
        self.assertIn("應", warnings[0])
        self.assertIn("appears only negated", warnings[0])

    def test_modality_polarity_standalone_and_negated_form_is_quiet(self):
        # Fix 3(b): a rendition containing BOTH 應 standalone and 不應
        # is fine -- the standalone occurrence proves the polarity is
        # not universally inverted.
        unit = _unit(
            source_text="you should complete this task",
            rendition="你不應該偷懶但應完成這個任務",
        )
        self.assertEqual(check_modality_mapping(unit), [])

    def test_modality_hyphen_compound_excluded_from_scan(self):
        # Fix 3(c), live dogfood finding: "should-fix" (a severity
        # label carried verbatim, no separate 應 elsewhere in the
        # rendition) is not a modality claim -- must not fire a
        # warning. Real repro: this exact label fired 5 spurious
        # warnings on first real use.
        unit = _unit(source_text="severity: should-fix", rendition="嚴重度：should-fix")
        self.assertEqual(check_modality_mapping(unit), [])


class TestCleanBilingualFixtureFullyQuiet(unittest.TestCase):
    def test_clean_fixture_has_no_violations_and_no_warnings(self):
        units = [
            _unit(
                id_="u1",
                source_text="you must not skip this step",
                anchors=(),
                rendition="不得跳過此步驟",
            ),
            _unit(
                id_="u2",
                source_text="Note: this is optional, nothing required",
                anchors=(),
                rendition="這是選擇性的",
            ),
        ]
        violations = run_checks(units)
        self.assertEqual(violations, [])
        self.assertEqual(exit_code_for(violations), 0)


if __name__ == "__main__":
    unittest.main()
