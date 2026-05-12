#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""abac_filter — ABAC gate matching for variant-folder playbook entries.

Given a deal_context (deal_size / counterparty_type / jurisdiction /
data_subjects_jurisdiction / etc.) and a list of variants (each with
a `gates` frontmatter rule), pick the variant whose gates ALL match.

Returns:
  - exactly 1 match → that variant
  - 0 matches      → ("advisory", None) — caller routes to advisory mode
  - >1 matches     → ("multi", first variant) + log warning; caller
                     handles per L7 protocol (first-match, log warning,
                     and detect_conflicts.py catches the bad gates at
                     author-time anyway)

Gate semantics (matches schema.json gate_value union):
  - { eq: N }            — equality (numeric or string)
  - { lt: N }            — less than (numeric)
  - { lte: N }           — less than or equal
  - { gt: N }            — greater than
  - { gte: N }           — greater than or equal
  - { any_of: [...] }    — value in enum
  - "any"                — always matches (wildcard)
  - combinations like { gte: 100000, lt: 1000000 } — half-open range

Multi-key gates ALL must match (AND semantics).

Usage:
    abac_filter.py --deal-context <json|@path> --variants <json|@path>

Importable: from abac_filter import match_variant
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _read_json_arg(value: str) -> Any:
    """Accept inline JSON string OR @path/to/file.json."""
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def check_gate(gate: Any, ctx_value: Any) -> bool:
    """Does the given gate value match the context's actual value?

    A wildcard "any" gate always returns True.
    A missing ctx_value against a non-wildcard gate is treated as no-match
    (caller is expected to supply all relevant deal_context keys; absence
    means "we don't know" which we treat conservatively).
    """
    if gate == "any":
        return True
    if not isinstance(gate, dict):
        return False
    if ctx_value is None:
        # Strict — we cannot match when caller didn't supply the attribute.
        return False
    # Equality (most specific test, evaluate first)
    if "eq" in gate:
        return ctx_value == gate["eq"]
    # Enum
    if "any_of" in gate:
        return ctx_value in gate["any_of"]
    # Numeric range — all relevant comparisons must hold
    try:
        n = float(ctx_value)
    except (TypeError, ValueError):
        return False
    if "lt" in gate and not (n < float(gate["lt"])):
        return False
    if "lte" in gate and not (n <= float(gate["lte"])):
        return False
    if "gt" in gate and not (n > float(gate["gt"])):
        return False
    if "gte" in gate and not (n >= float(gate["gte"])):
        return False
    # If at least one numeric bound was specified and all passed, match.
    if any(k in gate for k in ("lt", "lte", "gt", "gte")):
        return True
    return False


def match_variant(deal_context: dict, variants: list[dict]) -> tuple[str, dict | None, list[dict]]:
    """Run ABAC pre-filter; return (outcome, chosen, all_matched).

    outcome ∈ {"single", "advisory", "multi"}.
    chosen is the working variant (None for advisory; first for multi).
    all_matched is the list of every variant whose gates passed.
    """
    matched: list[dict] = []
    for v in variants:
        gates = v.get("gates") or {}
        if not isinstance(gates, dict):
            continue
        ok = all(check_gate(gates[k], deal_context.get(k)) for k in gates.keys())
        if ok:
            matched.append(v)
    if len(matched) == 0:
        return ("advisory", None, [])
    if len(matched) == 1:
        return ("single", matched[0], matched)
    return ("multi", matched[0], matched)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--deal-context",
        required=True,
        help="JSON object (or @path) with deal_size / counterparty_type / etc.",
    )
    parser.add_argument(
        "--variants",
        required=True,
        help="JSON array of variant entries (each with .gates) (or @path)",
    )
    parser.add_argument("--format", choices=("text", "json"), default="json")
    args = parser.parse_args()

    deal_ctx = _read_json_arg(args.deal_context)
    variants = _read_json_arg(args.variants)

    outcome, chosen, matched = match_variant(deal_ctx, variants)

    report = {
        "outcome": outcome,
        "chosen_variant_id": (chosen or {}).get("variant_id"),
        "matched_count": len(matched),
        "matched_variant_ids": [m.get("variant_id") for m in matched],
    }
    if args.format == "json":
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(f"outcome: {report['outcome']}")
        print(f"chosen:  {report['chosen_variant_id']}")
        print(f"matched: {report['matched_count']} -- {report['matched_variant_ids']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
