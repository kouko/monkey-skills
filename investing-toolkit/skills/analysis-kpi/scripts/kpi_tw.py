#!/usr/bin/env python3
"""kpi_tw.py — TW iXBRL fact -> kpi_store point adapter (pure-compute).

Layer-2 producer helpers for the TW-market kpi_store. This module takes
ALREADY-PARSED facts (the twse_ixbrl_parser record shape: dicts carrying
`concept` / `raw_value` / `period` / ...) as input — it does NOT parse
HTML and MUST NOT import any data-markets module. Crossing the
analysis↔data-markets boundary is forbidden here
([[durable-store-mirrors-cache-util-not-imports-it]]); callers that need
facts parse the document in the data layer and hand the list in.

stdlib only (`re`, `datetime`).
"""
from __future__ import annotations

import re
from datetime import date
from typing import Any

# KPI-worthy canonical fields — the market-agnostic KPI spine emitted as store
# points. This is the task's named set, using the REAL canonical field names
# (twse_ixbrl_canonical.py): `total_liabilities`/`total_equity` (not the loose
# "liabilities"/"equity"), `operating_cash_flow`/... (not "OCF"/...). It
# deliberately EXCLUDES two canonical fields present in a -ci filing:
#   - `ebit` — a pure alias of operating_income (identical concept AND value);
#     emitting both would be a redundant duplicate series.
#   - `total_debt` — a derived debt aggregate (concept=None), outside the
#     tearsheet KPI set this arc.
# A financial-family canonical (-fh/-basi/...) carries only the overlapping
# spine fields (total_assets/total_equity/cash/net_income/eps_basic); the
# absent -ci-only lines are simply not emitted (whichever allowlisted fields
# a filing actually carries are emitted, never fabricated).
_KPI_FIELDS: frozenset[str] = frozenset(
    {
        "revenue",
        "gross_profit",
        "operating_income",
        "pretax_income",
        "net_income",
        "eps_basic",
        "total_assets",
        "total_liabilities",
        "total_equity",
        "cash",
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "capex",
        "fcf",
    }
)

_STATEMENTS = ("income_statement", "balance_sheet", "cash_flow")

# TW iXBRL points share one source_table_id (mirrors the US producer's
# "xbrl:companyfacts"/"xbrl:dimensional" convention, kpi_xbrl.py:519-523).
_SOURCE_TABLE_ID = "tw:ixbrl"

# The nonNumeric note fact carrying the board authorisation-for-issue date
# (財報經授權發布日). Its value is free text that wraps the date in 董事會
# procedure wording, e.g. "本合併財務報告於115年5月13日經董事會通過。".
_AUTH_CONCEPT = (
    "tifrs-notes:DateAndProceduresOfAuthorisationForIssueOfFinancialStatements"
)

# 年月日 date (民國 or Gregorian): the year group's digit-count is the
# era discriminator — 4 digits is Gregorian, 2-3 digits is ROC (民國).
# The left `(?<!\d)` anchors the year to its start so a 4-digit "2026年"
# is captured whole, never as ROC "026年" (026+1911 = 1937, a silent
# wrong-century as_of).
_CJK_DATE_RE = re.compile(r"(?<!\d)(\d{2,4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
# Gregorian separator date: YYYY-MM-DD (also accepts / or . separators).
_ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})")

_ROC_YEAR_OFFSET = 1911


def _parse_auth_date(value: str) -> str | None:
    """Extract an ISO date (YYYY-MM-DD) from an auth-date fact value.

    The value carries a ROC-era or Gregorian date plus procedure text.
    Returns None when no parseable date is present (a FINDING for the
    caller — never fabricated).
    """
    cjk = _CJK_DATE_RE.search(value)
    if cjk is not None:
        raw_year = int(cjk.group(1))
        year = raw_year if len(cjk.group(1)) == 4 else raw_year + _ROC_YEAR_OFFSET
        month, day = int(cjk.group(2)), int(cjk.group(3))
    else:
        iso = _ISO_DATE_RE.search(value)
        if iso is None:
            return None
        year, month, day = int(iso.group(1)), int(iso.group(2)), int(iso.group(3))
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def extract_tw_authorisation_date(facts: list[dict[str, Any]]) -> str | None:
    """Return the board authorisation-for-issue date as an ISO string.

    Finds the `tifrs-notes:DateAndProceduresOfAuthorisationForIssue...`
    fact and parses an ISO date (YYYY-MM-DD) out of its value, which may
    carry procedure text around the date. Returns None when the concept
    is absent or its value carries no parseable date. This ISO date is
    the non-wall-clock `as_of` for every TW KPI point.
    """
    for fact in facts:
        if fact.get("concept") != _AUTH_CONCEPT:
            continue
        raw = fact.get("raw_value")
        if not isinstance(raw, str):
            continue
        parsed = _parse_auth_date(raw)
        if parsed is not None:
            return parsed
    return None


def _tw_kpi_id(field: str, basis: str | None) -> str:
    """Derive a TW kpi_id from a canonical field name + consolidation basis.

    Shape: `<field-slug>` optionally suffixed `__basis-<C|A>` (C=合併/
    consolidated, A=個體/parent-only). TW has NO us-gaap dimensional axes, so
    the consolidation basis is the ONLY series discriminator — it substitutes
    for the US `axis=member` signature (plan ## Notes PIN).

    The field-slug is the lowercased field name — a LOSSY normalization, so
    two DISTINCT source fields CAN collapse to one id. The caller's injective
    guard fails loud on that collision rather than silently merging two series
    ([[derived-durable-id-slug-is-a-lossy-one-way-door]]).

    NO LONGER a mirror of the US derivation, as of investing-toolkit 2.37.0:
    `kpi_xbrl_ingest.derive_kpi_id` now appends a digest of the case-folded
    identity tuple (this one has no digest), and the US guard now ACCEPTS a
    case-insensitively equal claimant (this one still raises). The divergence is
    deliberate for now — TW ids come from a repo-canonical field allowlist, not
    filer-authored qnames, so they carry no namespace or case-drift source. See
    the "TW producer" line under BACKLOG §"full three-statement + management-KPI
    history in kpi_store" before assuming the two should be re-aligned.
    """
    slug = field.lower()
    return f"{slug}__basis-{basis}" if basis else slug


def _period_fields(period: dict[str, Any] | None) -> tuple:
    """Map a parser period dict to the store's period identity fields.

    Returns `(period_start, period_end, period_kind, period_label)` from an
    instant `{"type":"instant","instant":D}` or duration
    `{"type":"duration","start":S,"end":E}` context (twse_ixbrl_parser shape).

    `period_label` is the write-side dedup discriminator: kpi_store.append
    keys its idempotency 5-tuple on `point["period"]` (kpi_store
    _DEDUP_KEY_FIELDS), so a filing's several comparatives (all sharing one
    accession + as_of) MUST carry distinct `period` values or the store
    collapses them to one key and silently drops every prior-period vintage.
    An instant labels by its date; a duration by `start/end`.
    """
    if not period:
        return None, None, None, None
    if period.get("type") == "instant":
        instant = period.get("instant")
        return None, instant, "instant", instant
    start = period.get("start")
    end = period.get("end")
    return start, end, "duration", f"{start}/{end}"


def tw_canonical_to_points(
    canonical: dict[str, Any],
    basis: str | None,
    as_of: str,
    provenance: dict[str, Any],
) -> list[dict[str, Any]]:
    """Map a TW canonical into market-agnostic kpi_store points.

    `canonical` is the twse_ixbrl_canonical.build_canonical output (three
    statement keys, each a per-field value-list + a parallel `_meta[field]
    ["periods"]`); passed IN as a dict — this module never imports data-markets
    (the analysis↔data-markets boundary). `basis` is the consolidation code
    (C/A) that discriminates the two series. `as_of` is the non-wall-clock
    board authorisation-for-issue date (extract_tw_authorisation_date, Task 1).
    `provenance` supplies filing metadata (`company`, `source_accession`,
    `source_form`, `source_kind`).

    For each KPI-worthy canonical field (`_KPI_FIELDS`) that the filing
    carries, one point per period is emitted — INCLUDING flat totals and every
    comparative (the US empty-dims skip is inverted: TW has no dimensions, the
    flat total IS the fact). `value` is the raw base-scaled figure, so
    `scale` is 1 (twse_ixbrl_parser already base-scales). A derived field
    (fcf) has no single XBRL concept; `source_cell_ref` falls back to the
    field name so the store's non-empty provenance guard still passes.

    Injective guard: two distinct source fields deriving one kpi_id raises
    ValueError — never silently merge two series (mirrors
    kpi_xbrl_ingest's collision guard).
    """
    company = provenance.get("company")
    source_accession = provenance.get("source_accession")
    source_form = provenance.get("source_form")
    source_kind = provenance.get("source_kind")

    points: list[dict[str, Any]] = []
    claimed_by: dict[str, str] = {}  # kpi_id -> the field that first claimed it
    for statement in _STATEMENTS:
        stmt = canonical.get(statement) or {}
        meta = stmt.get("_meta") or {}
        for field, values in stmt.items():
            if field == "_meta" or field.lower() not in _KPI_FIELDS:
                continue
            kpi_id = _tw_kpi_id(field, basis)
            prior = claimed_by.get(kpi_id)
            if prior is not None and prior != field:
                raise ValueError(
                    f"kpi_tw: kpi_id collision — distinct canonical fields "
                    f"{prior!r} and {field!r} both derive kpi_id {kpi_id!r}; "
                    "refusing to silently merge two different series"
                )
            claimed_by[kpi_id] = field

            field_meta = meta.get(field) or {}
            concept = field_meta.get("concept")
            periods = field_meta.get("periods") or []
            source_cell_ref = concept or field  # derived field -> field name
            for value, period in zip(values, periods):
                period_start, period_end, period_kind, period_label = _period_fields(
                    period
                )
                points.append(
                    {
                        "company": company,
                        "kpi_id": kpi_id,
                        "period": period_label,
                        "period_start": period_start,
                        "period_end": period_end,
                        "period_kind": period_kind,
                        "scale": 1,
                        "value": value,
                        "as_of": as_of,
                        "source_accession": source_accession,
                        "source_form": source_form,
                        "source_table_id": _SOURCE_TABLE_ID,
                        "source_cell_ref": source_cell_ref,
                        "source_kind": source_kind,
                        # The canonical _meta carries unit="TWD"; copy it onto
                        # the point (mirrors kpi_xbrl.py:569-570) so the market-
                        # agnostic tearsheet renders the currency label — else
                        # correct amounts render with no unit (2330 dogfood).
                        "unit": field_meta.get("unit"),
                    }
                )
    return points
