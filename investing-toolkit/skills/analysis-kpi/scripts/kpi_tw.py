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
