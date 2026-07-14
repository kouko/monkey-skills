"""Tests for analysis-kpi/scripts/kpi_validate.py — rule-based value
validation (operational-kpi capability, slice 4).

This slice's Task 1 ships the module scaffold + `check_sign(value, kpi_def)`:
a kpi_def declared `sign == "non-negative"` FAILS (passed False) when `value`
is negative; `sign` absent or `"any"` means no constraint applies (passed
True). kpi_validate.py is PURE-COMPUTE (stdlib only) — it does NOT import
`_store_fs`, resolve a store dir, lock, or persist anything; it only reads
values + kpi_defs and returns verdicts. No `KPI_STORE_DIR` fixture is needed.

The library function is exercised by loading `kpi_validate.py` via importlib
(same convention as test_kpi_store.py's `kpi_store_module` fixture).

No `@req` tags: this dispatch's plan/spec trace work by named change-folder
Requirements (operational-kpi / "Rule-based validation of parsed values"),
NOT by registered loom-spec REQ-ids — so `@req` is omitted per the
implementer contract.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys

from conftest import KPI_VALIDATE_SCRIPT

import pytest


@pytest.fixture(scope="module")
def kpi_validate_module():
    """Load kpi_validate.py as an importable module for unit tests of its
    library surface (check_sign/...) before check_unit/check_subtotal/
    check_gaap/validate/CLI are added (Tasks 2-6).
    """
    spec = importlib.util.spec_from_file_location("kpi_validate_test", KPI_VALIDATE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["kpi_validate_test"] = module
    spec.loader.exec_module(module)
    return module


def test_check_sign_rejects_negative_for_nonneg_kpi(kpi_validate_module):
    nonneg_def = {"sign": "non-negative"}
    any_def = {"sign": "any"}
    absent_def = {}

    result = kpi_validate_module.check_sign(-5, nonneg_def)
    assert result["rule"] == "sign"
    assert result["passed"] is False

    result_any = kpi_validate_module.check_sign(-5, any_def)
    assert result_any["passed"] is True

    result_absent = kpi_validate_module.check_sign(-5, absent_def)
    assert result_absent["passed"] is True

    result_zero = kpi_validate_module.check_sign(0, nonneg_def)
    assert result_zero["passed"] is True


def test_check_unit_flags_mismatch(kpi_validate_module):
    kpi_def = {"unit": "units"}

    mismatch = kpi_validate_module.check_unit("USD", kpi_def)
    assert mismatch["rule"] == "unit"
    assert mismatch["passed"] is False

    match = kpi_validate_module.check_unit("units", kpi_def)
    assert match["passed"] is True

    # A kpi_def with no declared unit → N/A (None), NOT a hard fail — matching
    # the sibling checks' third-state pattern (an undeclared constraint is not
    # a failure).
    na = kpi_validate_module.check_unit("USD", {})
    assert na["passed"] is None


def test_check_subtotal_flags_sum_mismatch(kpi_validate_module):
    ok = kpi_validate_module.check_subtotal([10, 20, 30], 60)
    assert ok["rule"] == "subtotal"
    assert ok["passed"] is True

    mismatch = kpi_validate_module.check_subtotal([10, 20, 30], 100)
    assert mismatch["passed"] is False

    na_no_segments = kpi_validate_module.check_subtotal([], 60)
    assert na_no_segments["passed"] is None

    na_none_segments = kpi_validate_module.check_subtotal(None, 60)
    assert na_none_segments["passed"] is None

    na_no_total = kpi_validate_module.check_subtotal([10, 20, 30], None)
    assert na_no_total["passed"] is None


def test_check_gaap_does_not_force_nongaap(kpi_validate_module):
    nongaap_absent = kpi_validate_module.check_gaap({}, has_gaap_match=False)
    assert nongaap_absent["rule"] == "gaap"
    assert nongaap_absent["passed"] is not False

    nongaap_explicit = kpi_validate_module.check_gaap({"gaap": False}, has_gaap_match=False)
    assert nongaap_explicit["passed"] is not False

    gaap_missing_match = kpi_validate_module.check_gaap({"gaap": True}, has_gaap_match=False)
    assert gaap_missing_match["passed"] is False

    gaap_with_match = kpi_validate_module.check_gaap({"gaap": True}, has_gaap_match=True)
    assert gaap_with_match["passed"] is True


def test_validate_aggregates_applicable_rules(kpi_validate_module):
    """Task 5: `validate(value_record, kpi_def)` runs every APPLICABLE rule
    (sign/unit/subtotal/gaap) and aggregates: a rule's `passed is None` is
    N/A — it never counts as a failure and never blocks eligibility; only
    `passed is False` is a failure.
    """
    kpi_def = {"sign": "non-negative", "unit": "units"}

    # (a) passes every applicable rule → eligible True, no failures.
    passing_record = {
        "value": 231000000,
        "unit": "units",
        "segments": [100000000, 131000000],
        "total": 231000000,
    }
    verdict = kpi_validate_module.validate(passing_record, kpi_def)
    assert verdict == {"eligible": True, "failures": []}

    # (b) negative value against a non-negative kpi_def → eligible False,
    # failures contains the "sign" entry.
    negative_record = {
        "value": -5,
        "unit": "units",
        "segments": [100000000, 131000000],
        "total": 231000000,
    }
    verdict_negative = kpi_validate_module.validate(negative_record, kpi_def)
    assert verdict_negative["eligible"] is False
    failure_rules = [f["rule"] for f in verdict_negative["failures"]]
    assert "sign" in failure_rules
    assert all("detail" in f for f in verdict_negative["failures"])

    # (c) no segments/total → subtotal is N/A (None): must NOT appear in
    # failures and must NOT make the record ineligible.
    no_segments_record = {
        "value": 231000000,
        "unit": "units",
    }
    verdict_no_segments = kpi_validate_module.validate(no_segments_record, kpi_def)
    assert verdict_no_segments == {"eligible": True, "failures": []}
    assert "subtotal" not in [f["rule"] for f in verdict_no_segments["failures"]]


def test_cli_validate_roundtrip():
    """Task 6: the `validate` subcommand reads `{value_record, kpi_def}` JSON
    from stdin, prints the verdict, and exits 0 on ANY valid verdict —
    including eligible:false (a validly-rejected value is not a CLI error).
    Malformed/non-object JSON exits 2, cleanly (no raw traceback). `--help`
    must list the `validate` subcommand.
    """
    kpi_def = {"sign": "non-negative"}

    def run_validate(stdin_text):
        return subprocess.run(
            ["uv", "run", "--script", str(KPI_VALIDATE_SCRIPT), "validate"],
            input=stdin_text, capture_output=True, text=True, timeout=60,
        )

    # (1) passing record → exit 0, eligible True
    passing_input = json.dumps({
        "value_record": {"value": 100},
        "kpi_def": kpi_def,
    })
    passing = run_validate(passing_input)
    assert passing.returncode == 0, passing.stderr
    assert json.loads(passing.stdout) == {"eligible": True, "failures": []}

    # (2) failing record (negative value, non-negative kpi_def) → still
    # exit 0 — a validly-rejected value is NOT a CLI error.
    failing_input = json.dumps({
        "value_record": {"value": -5},
        "kpi_def": kpi_def,
    })
    failing = run_validate(failing_input)
    assert failing.returncode == 0, failing.stderr
    failing_verdict = json.loads(failing.stdout)
    assert failing_verdict["eligible"] is False
    assert any(f["rule"] == "sign" for f in failing_verdict["failures"])

    # (3) malformed JSON → exit 2, no traceback
    malformed = run_validate("this is not json")
    assert malformed.returncode == 2, malformed.stderr
    assert "Traceback" not in malformed.stderr

    # (4) valid JSON but not an object (a list) → exit 2, no traceback
    not_a_dict = run_validate("[1, 2, 3]")
    assert not_a_dict.returncode == 2, not_a_dict.stderr
    assert "Traceback" not in not_a_dict.stderr

    # (4b) valid object but value_record missing the required "value" key →
    # exit 2 CLEANLY (no raw KeyError traceback), per the CLI's fail-loud
    # contract — a structurally-incomplete payload is malformed input.
    missing_value = run_validate(json.dumps({"value_record": {}, "kpi_def": kpi_def}))
    assert missing_value.returncode == 2, missing_value.stderr
    assert "Traceback" not in missing_value.stderr
    no_value_record = run_validate(json.dumps({"kpi_def": kpi_def}))
    assert no_value_record.returncode == 2, no_value_record.stderr
    assert "Traceback" not in no_value_record.stderr

    # (5) --help lists the validate subcommand
    help_result = subprocess.run(
        ["uv", "run", "--script", str(KPI_VALIDATE_SCRIPT), "--help"],
        capture_output=True, text=True, timeout=60,
    )
    assert help_result.returncode == 0, help_result.stderr
    assert "validate" in help_result.stdout
