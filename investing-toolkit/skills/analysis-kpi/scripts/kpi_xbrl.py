#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
XBRL fact -> kpi_store point adapter (operational-kpi tier-② XBRL pilot).

Layer 2 (Analysis) PURE-COMPUTE — mirrors kpi_parse.py / kpi_validate.py:
stdlib only, dict-in -> dict-out. This module is NOT a durable store: it
does NOT import `_store_fs`, does NOT resolve a store dir, does NOT lock
or write files, and touches neither the network nor an LLM.

`facts_to_points(fact_pack, kpi_id, match, company, source_kind)` selects
every fact in `fact_pack["facts"]` matching `match` (a
`{"concept", "dimensions"}` selector — `dimensions` compared by dict
EQUALITY, so an absent/empty `dimensions` matches only a flat fact's own
empty `dimensions`, i.e. the top-level total) and maps each matched fact
into a kpi_store-shaped point:

  - `source_accession` = fact `accession`
  - `source_table_id`  = `"xbrl:dimensional"` (fact has real breakdown
                          axes) or `"xbrl:companyfacts"` (fact `dimensions`
                          is empty, flat)
  - `source_cell_ref`  = `concept` (flat) or
                          `concept + "|" + <stable-sorted "axis=member" join>`
                          (dimensional, e.g.
                          `"concept|ProductOrService=StreamingMember"`)
  - `as_of`            = fact `filed`
  - `period`           = the year the fiscal period ENDS, taken from
                          `period_end[:4]` (e.g. `"2025-09-27"` -> `"2025"`)
                          — NEVER from the `fiscal_year` column, which
                          edgartools mislabels for prior-year comparatives
  - `value`            = fact `value`
  - plus `company`, `kpi_id`, `source_kind`

The CORE property is FAIL-LOUD (mirrors kpi_parse's UnparseableCell
discipline): a matched fact missing `value`/`accession`/`filed`/`period_end`,
carrying a non-numeric `value`, or a malformed (non-YYYY-MM-DD) `period_end`,
RAISES a distinct `ValueError` naming the offending field — this module
never emits a fabricated `0` or a period `"None"`. A true numeric `0` is a
real value, not a missing one.

Task 6 adds a thin argparse CLI (`build`), mirroring `kpi_memo_feed.py`'s
CLI shape and fail-loud exit-code convention: reads a fact-pack JSON from
`--file`/stdin and a binding JSON from `--binding`, calls `resolve_binding`
and prints the resulting points. 0 on success; 1 on a `resolve_binding`
ValueError (e.g. ambiguous binding); 2 on malformed or non-object
fact-pack JSON (nothing computed, no raw traceback).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# Resolve same-dir modules without a package (mirrors kpi_series.py's own
# import shim for kpi_break) so `import kpi_series` works both under
# `uv run --script` and importlib test loading. Only kpi_series is
# imported — NOT kpi_break: the declared/pre-applied break here
# intentionally bypasses kpi_break's persisted FLAGGED->CONFIRMED->APPLIED
# review-queue lifecycle.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import kpi_series  # noqa: E402


def _fact_matches(fact: dict, match: dict) -> bool:
    """EXACT-match a fact's full dimensional signature against `match` =
    `{concept, dimensions}`. `dimensions` is compared by dict EQUALITY — a
    match with an empty/absent `dimensions` matches ONLY a fact whose own
    `dimensions` is empty (the top-level total); a fact carrying EXTRA
    breakdown axes beyond `match`'s does NOT match (de-conflates e.g. a
    NFLX streaming total from its per-region slices).
    """
    return (
        fact.get("concept") == match.get("concept")
        and fact.get("dimensions", {}) == match.get("dimensions", {})
    )


def _require_value(fact: dict) -> float:
    if "value" not in fact or fact["value"] is None:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'value' "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    value = fact["value"]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'value' is non-numeric "
            f"({value!r}, concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated as 0"
        )
    return value


def _require_period(fact: dict) -> str:
    period_end = fact.get("period_end")
    if not isinstance(period_end, str) or not period_end:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required 'period_end' "
            f"(concept={fact.get('concept')!r}) — rejected, never fabricated "
            f'as period "None"'
        )
    try:
        date.fromisoformat(period_end)
    except ValueError:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact 'period_end' is malformed "
            f"({period_end!r}, concept={fact.get('concept')!r}) — expected "
            f'YYYY-MM-DD, rejected, never fabricated as period "None"'
        ) from None
    return period_end[:4]


def _require_field(fact: dict, field: str) -> str:
    value = fact.get(field)
    if not value:
        raise ValueError(
            f"kpi_xbrl.facts_to_points: fact missing required {field!r} "
            f"(concept={fact.get('concept')!r}, fiscal_year="
            f"{fact.get('fiscal_year')!r}) — rejected, never fabricated"
        )
    return value


def facts_to_points(
    fact_pack: dict,
    kpi_id: str,
    match: dict,
    company: str,
    source_kind: str,
) -> list[dict]:
    """Map every fact in `fact_pack["facts"]` matching `match` into a
    kpi_store-shaped point. See module docstring for the provenance
    mapping and the fail-loud field-by-field taxonomy.
    """
    points = []
    for fact in fact_pack.get("facts", []):
        if not _fact_matches(fact, match):
            continue

        value = _require_value(fact)
        accession = _require_field(fact, "accession")
        filed = _require_field(fact, "filed")
        period = _require_period(fact)

        concept = fact.get("concept")
        dimensions = fact.get("dimensions") or {}

        if dimensions:
            source_table_id = "xbrl:dimensional"
            dims_joined = ",".join(f"{k}={v}" for k, v in sorted(dimensions.items()))
            source_cell_ref = f"{concept}|{dims_joined}"
        else:
            source_table_id = "xbrl:companyfacts"
            source_cell_ref = concept

        points.append(
            {
                "company": company,
                "kpi_id": kpi_id,
                "period": period,
                "as_of": filed,
                "value": value,
                "source_accession": accession,
                "source_table_id": source_table_id,
                "source_cell_ref": source_cell_ref,
                "source_kind": source_kind,
            }
        )
    return points


def resolve_binding(fact_pack: dict, binding: dict, company: str) -> list[dict]:
    """Resolve a logical-KPI binding onto the fact-pack's full dimensional
    signatures: `binding` = `{kpi_id, sources: [{concept, dimensions,
    source_kind}]}`.

    A fact matches a source when `fact["concept"] == source["concept"]` AND
    `fact["dimensions"] == source["dimensions"]` EXACTLY (dict equality — an
    absent/empty `dimensions` matches ONLY the top-level total; a fact
    carrying extra breakdown axes does NOT match a narrower source). A
    matched fact is emitted (via `facts_to_points`, reusing its provenance
    mapping) under the single logical `kpi_id`. A fact matching no source is
    skipped, never fabricated. A fact matching more than one source RAISES —
    an ambiguous binding. INVARIANT: exactly ONE point per (signature,
    period). When a single source's signature matches TWO OR MORE facts for
    the SAME period, they collapse to exactly one point — if every matched
    fact agrees on `value`, the identical duplicate(s) are DEDUPED down to
    one point (never double-counted downstream); if the matched facts
    DISAGREE on `value`, resolve_binding RAISES ValueError naming the
    kpi_id + period — a genuine value conflict is never resolved
    arbitrarily. A period with exactly one matching fact resolves cleanly,
    unchanged.
    """
    kpi_id = binding["kpi_id"]
    sources = binding["sources"]

    facts_by_source_idx: list[list[dict]] = [[] for _ in sources]

    for fact in fact_pack.get("facts", []):
        matched_indices = []
        for idx, source in enumerate(sources):
            selector = {
                "concept": source["concept"],
                "dimensions": source.get("dimensions", {}),
            }
            if _fact_matches(fact, selector):
                matched_indices.append(idx)

        if len(matched_indices) > 1:
            raise ValueError(
                f"kpi_xbrl.resolve_binding: fact matches {len(matched_indices)} "
                f"sources for kpi_id {kpi_id!r} (concept={fact.get('concept')!r}, "
                f"period_end={fact.get('period_end')!r}) — ambiguous binding, "
                f"never resolved arbitrarily"
            )
        if matched_indices:
            facts_by_source_idx[matched_indices[0]].append(fact)

    # Reduce each source's matched facts to exactly ONE fact per period: a
    # period with >1 matching fact that all AGREE on value is deduped down
    # to a single representative fact (never double-counted downstream as
    # two identical points); a period with matching facts that DISAGREE on
    # value RAISES (a genuine conflict, never resolved arbitrarily).
    deduped_facts_by_source_idx: list[list[dict]] = [[] for _ in sources]
    for idx, source in enumerate(sources):
        matched_facts = facts_by_source_idx[idx]
        by_period: dict[str, list[dict]] = {}
        for fact in matched_facts:
            period_key = (fact.get("period_end") or "")[:4] or fact.get("period_end")
            by_period.setdefault(period_key, []).append(fact)
        for period_key, group in by_period.items():
            values = {fact.get("value") for fact in group}
            if len(values) > 1:
                raise ValueError(
                    f"kpi_xbrl.resolve_binding: signature for kpi_id {kpi_id!r} "
                    f"matches {len(group)} facts with different values for "
                    f"period {period_key!r} (concept={source.get('concept')!r}) "
                    f"— ambiguous, never resolved arbitrarily"
                )
            # exactly one distinct value across the group (1 or more identical
            # facts) -> keep exactly one representative fact for this period.
            deduped_facts_by_source_idx[idx].append(group[0])

    points = []
    for idx, source in enumerate(sources):
        matched_facts = deduped_facts_by_source_idx[idx]
        if not matched_facts:
            continue
        sub_pack = {"company": fact_pack.get("company"), "facts": matched_facts}
        selector = {
            "concept": source["concept"],
            "dimensions": source.get("dimensions", {}),
        }
        points.extend(
            facts_to_points(sub_pack, kpi_id, selector, company, source["source_kind"])
        )
    return points


def build_series_with_break(points: list[dict], break_at_period: str) -> dict:
    """Split `points` at a declared structural boundary `break_at_period`,
    delegating to `kpi_series.split_series` (plain-args pure compute, NO
    persisted break lifecycle) — never a naive concatenation across a
    tagging-regime change.

    Builds a local `applied_breaks = [{"break_period": break_at_period}]`
    from the declared boundary and returns `split_series`'s dict
    (`{as_reported, recast, break_markers}`) unchanged. This is NOT a
    reimplementation of the partitioning logic — kpi_series.split_series
    owns it.
    """
    applied_breaks = [{"break_period": break_at_period}]
    return kpi_series.split_series(points, applied_breaks)


def _cli_build(args: argparse.Namespace) -> int:
    """`build` subcommand: read a fact-pack JSON from `--file` (or stdin
    when omitted) and a binding JSON from `--binding`, call
    `resolve_binding(fact_pack, binding, company)` and print the resulting
    points list. Mirrors `kpi_memo_feed._cli_build`'s exit-code contract:
    malformed JSON or a non-object fact_pack/binding -> 2 (nothing
    computed); a `resolve_binding` rejection (ValueError, e.g. an
    ambiguous binding) -> 1; success -> 0.
    """
    if args.file is not None:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()

    try:
        fact_pack = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid fact-pack JSON input: {exc}", file=sys.stderr)
        return 2

    if not isinstance(fact_pack, dict):
        print(
            "kpi_xbrl build: expected a JSON object (fact_pack), got "
            f"{type(fact_pack).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    binding_raw = Path(args.binding).read_text(encoding="utf-8")
    try:
        binding = json.loads(binding_raw)
    except json.JSONDecodeError as exc:
        print(f"kpi_xbrl build: invalid --binding JSON: {exc}", file=sys.stderr)
        return 2

    if not isinstance(binding, dict):
        print(
            "kpi_xbrl build: expected a JSON object (--binding), got "
            f"{type(binding).__name__} — nothing computed",
            file=sys.stderr,
        )
        return 2

    try:
        points = resolve_binding(fact_pack, binding, args.company)
    except ValueError as exc:
        print(f"kpi_xbrl build: {exc}", file=sys.stderr)
        return 1

    json.dump(points, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="XBRL fact -> kpi_store point adapter CLI (build)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build",
        help="Resolve an era-specific binding against a fact-pack and print the points.",
    )
    build_parser.add_argument("--company", required=True)
    build_parser.add_argument(
        "--binding", type=Path, required=True,
        help="Path to a JSON file holding the binding ({kpi_id, sources: [...]}).",
    )
    build_parser.add_argument(
        "--file", type=Path, default=None,
        help="Path to a JSON file holding the fact_pack (default: read stdin).",
    )
    build_parser.set_defaults(func=_cli_build)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
