#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Rule-based value validation (operational-kpi capability, slice 4).

Layer 2 (Analysis) PURE-COMPUTE — mirrors analysis-comps/dcf compute
scripts: stdlib only, JSON in -> verdict out. This module is NOT a durable
store: it does NOT import `_store_fs`, does NOT resolve a store dir, does
NOT lock or write files. It reads an already-parsed value + a kpi_def and
returns a rule verdict; persistence (kpi_store.py) and schema lifecycle
(kpi_schema.py) are separate seams this module never touches.

A rule FAILURE is a normal `{"passed": False, ...}` verdict, not an
exception; only MALFORMED input (wrong types) is a loud error.

This slice's Task 1 ships the module scaffold + `check_sign(value,
kpi_def)`: a kpi_def declared `sign == "non-negative"` FAILS (passed False)
when `value` is negative; `sign` absent or `"any"` means no constraint
applies (passed True). Tasks 2-6 add check_unit/check_subtotal/check_gaap/
validate/CLI.
"""
from __future__ import annotations

import math


def check_sign(value: float, kpi_def: dict) -> dict:
    """Check a value's sign against its kpi_def's declared sign convention.

    kpi_def["sign"] == "non-negative" -> value must be >= 0.
    kpi_def["sign"] absent or "any" -> no constraint (always passes).
    """
    sign = kpi_def.get("sign", "any")
    if sign == "non-negative" and value < 0:
        return {
            "rule": "sign",
            "passed": False,
            "detail": f"value {value} is negative; kpi_def requires non-negative",
        }
    return {
        "rule": "sign",
        "passed": True,
        "detail": "no sign constraint violated",
    }


def check_unit(value_unit: str, kpi_def: dict) -> dict:
    """Check a value's unit against its kpi_def's declared unit.

    kpi_def["unit"] must equal value_unit exactly; mismatch -> not passed.
    If the kpi_def declares NO unit, the rule is N/A (passed None) — matching
    the sibling checks' third-state pattern (an undeclared constraint is not a
    failure): we cannot check a value's unit against an expected unit that the
    schema never declared.
    """
    expected = kpi_def.get("unit")
    if expected is None:
        return {
            "rule": "unit",
            "passed": None,
            "detail": "kpi_def declares no unit — unit rule not applicable",
        }
    if value_unit != expected:
        return {
            "rule": "unit",
            "passed": False,
            "detail": f"value unit {value_unit!r} does not match kpi_def unit {expected!r}",
        }
    return {
        "rule": "unit",
        "passed": True,
        "detail": "unit matches kpi_def",
    }


def check_subtotal(segments: list | None, total: float | None, tol: float = 0.01) -> dict:
    """Check that segments sum to total within a relative tolerance.

    If segments is absent/empty or total is None, the rule is N/A
    (passed=None) -- a distinct third state, not a failure.
    """
    if not segments or total is None:
        return {
            "rule": "subtotal",
            "passed": None,
            "detail": "no segments or total to compare; rule not applicable",
        }
    segment_sum = sum(segments)
    if math.isclose(segment_sum, total, rel_tol=tol):
        return {
            "rule": "subtotal",
            "passed": True,
            "detail": f"segment sum {segment_sum} matches total {total} within rel_tol={tol}",
        }
    return {
        "rule": "subtotal",
        "passed": False,
        "detail": f"segment sum {segment_sum} does not match total {total} within rel_tol={tol}",
    }


def check_gaap(kpi_def: dict, has_gaap_match: bool) -> dict:
    """Check GAAP-tag alignment -- a company-defined non-GAAP KPI must
    NEVER be failed for lacking a GAAP match; the rule only constrains
    a kpi_def explicitly declared gaap=True.
    """
    if not kpi_def.get("gaap", False):
        return {
            "rule": "gaap",
            "passed": None,
            "detail": "kpi_def is non-GAAP; GAAP-match rule not applicable",
        }
    if not has_gaap_match:
        return {
            "rule": "gaap",
            "passed": False,
            "detail": "kpi_def declared gaap=True but no GAAP match was found",
        }
    return {
        "rule": "gaap",
        "passed": True,
        "detail": "kpi_def declared gaap=True and a GAAP match was found",
    }
