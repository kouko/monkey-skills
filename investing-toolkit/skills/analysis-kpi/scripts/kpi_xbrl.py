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
`{"concept", "axis", "member"}` selector — `axis`/`member` compared
directly, so `None` matches a flat fact's `None` axis/member) and maps each
matched fact into a kpi_store-shaped point:

  - `source_accession` = fact `accession`
  - `source_table_id`  = `"xbrl:" + axis` (dimensional) or
                          `"xbrl:companyfacts"` (axis is `None`, flat)
  - `source_cell_ref`  = `concept` (flat) or `concept + "|" + member`
                          (dimensional)
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
"""
from __future__ import annotations

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
    return (
        fact.get("concept") == match.get("concept")
        and fact.get("axis") == match.get("axis")
        and fact.get("member") == match.get("member")
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

        axis = fact.get("axis")
        member = fact.get("member")
        concept = fact.get("concept")

        source_table_id = f"xbrl:{axis}" if axis else "xbrl:companyfacts"
        source_cell_ref = f"{concept}|{member}" if member else concept

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
    """Resolve an era-specific logical-KPI binding: `binding` =
    `{kpi_id, sources: [{concept, axis, member, fy_min, fy_max, source_kind}]}`.

    Each fact is matched against `sources` — a source matches when
    concept+axis+member are equal AND the fact's fiscal year (derived from
    `period_end[:4]`, same as `facts_to_points` — never the raw `fiscal_year`
    field) falls within `[fy_min, fy_max]`. A matched fact is emitted (via
    `facts_to_points`, reusing its provenance mapping) under the single
    logical `kpi_id`. A fact matching no source is skipped, never fabricated.
    A fact matching more than one source RAISES — an ambiguous binding.
    """
    kpi_id = binding["kpi_id"]
    sources = binding["sources"]

    facts_by_source_idx: list[list[dict]] = [[] for _ in sources]

    for fact in fact_pack.get("facts", []):
        matched_indices = []
        for idx, source in enumerate(sources):
            selector = {
                "concept": source["concept"],
                "axis": source.get("axis"),
                "member": source.get("member"),
            }
            if not _fact_matches(fact, selector):
                continue
            fiscal_year = int(_require_period(fact))
            if source["fy_min"] <= fiscal_year <= source["fy_max"]:
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

    points = []
    for idx, source in enumerate(sources):
        matched_facts = facts_by_source_idx[idx]
        if not matched_facts:
            continue
        sub_pack = {"company": fact_pack.get("company"), "facts": matched_facts}
        selector = {
            "concept": source["concept"],
            "axis": source.get("axis"),
            "member": source.get("member"),
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
