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

Four deterministic checks, each returning `{"rule","passed","detail"}` with a
TRI-STATE `passed`: True (pass) / False (violation) / None (N/A — the
constraint does not apply, distinct from a failure):
- `check_sign` — a `sign == "non-negative"` kpi_def fails on a negative value
  (0 passes); `sign` absent or `"any"` → no constraint (passes).
- `check_unit` — the value's unit must equal the def's `unit`; no declared
  unit → N/A.
- `check_subtotal` — segments must sum to total within a relative tolerance;
  absent parts → N/A.
- `check_gaap` — a company-defined non-GAAP KPI is NEVER failed for lacking a
  GAAP tag (non-GAAP → N/A); only a `gaap: true` def with no match fails.
`validate(value_record, kpi_def)` aggregates the applicable rules into
`{"eligible", "failures"}` (an N/A rule is excluded from failures and never
blocks eligibility), and a thin `validate` CLI wraps it.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


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


def validate(value_record: dict, kpi_def: dict) -> dict:
    """Run every applicable rule (sign/unit/subtotal/gaap) against
    `value_record` + `kpi_def` and aggregate into one eligibility verdict.

    A rule's `passed is None` is N/A (the rule's precondition wasn't met —
    e.g. no declared unit, no segments to sum) and is excluded from
    `failures`; it never blocks eligibility. Only `passed is False` is a
    failure. Side-effect-free: reads its inputs, returns a new dict.
    """
    results = [
        check_sign(value_record["value"], kpi_def),
        check_unit(value_record.get("unit"), kpi_def),
        check_subtotal(value_record.get("segments"), value_record.get("total")),
        check_gaap(kpi_def, value_record.get("has_gaap_match", False)),
    ]
    failures = [
        {"rule": result["rule"], "detail": result["detail"]}
        for result in results
        if result["passed"] is False
    ]
    return {"eligible": len(failures) == 0, "failures": failures}


def _cli_validate(args: argparse.Namespace) -> int:
    """`validate` subcommand: read `{"value_record":..., "kpi_def":...}` JSON
    from `--file` (or stdin when omitted), call `validate`, print the
    verdict JSON to stdout. Exits 0 on ANY valid verdict — INCLUDING
    eligible:false, since a validly-rejected value is not a CLI error;
    exits 2 on malformed/non-object JSON, cleanly (no raw traceback).
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_validate validate: invalid JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict):
        print(
            "kpi_validate validate: expected a JSON object with "
            f"'value_record'/'kpi_def', got {type(payload).__name__}",
            file=sys.stderr,
        )
        return 2

    value_record = payload.get("value_record")
    if not isinstance(value_record, dict) or "value" not in value_record:
        print(
            "kpi_validate validate: payload.value_record must be a JSON object "
            "with a 'value' key — nothing to validate",
            file=sys.stderr,
        )
        return 2

    verdict = validate(value_record, payload.get("kpi_def", {}))
    json.dump(verdict, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rule-based operational-KPI value validation CLI (validate)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate one value_record against a kpi_def, printing the eligibility verdict.",
    )
    validate_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding {value_record, kpi_def} (default: read stdin).",
    )
    validate_parser.set_defaults(func=_cli_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
