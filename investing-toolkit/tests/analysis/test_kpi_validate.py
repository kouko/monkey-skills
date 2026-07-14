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
