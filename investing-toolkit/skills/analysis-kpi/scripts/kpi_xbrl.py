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

from datetime import date


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
