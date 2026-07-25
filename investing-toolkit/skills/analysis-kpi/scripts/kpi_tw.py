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

# ROC-era (民國) date: NNN年M月D日. ROC year + 1911 = Gregorian year.
_ROC_DATE_RE = re.compile(r"(\d{2,3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
# Gregorian ISO-ish date: YYYY-MM-DD (also accepts / or . separators).
_ISO_DATE_RE = re.compile(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})")

_ROC_YEAR_OFFSET = 1911


def _parse_auth_date(value: str) -> str | None:
    """Extract an ISO date (YYYY-MM-DD) from an auth-date fact value.

    The value carries a ROC-era or Gregorian date plus procedure text.
    Returns None when no parseable date is present (a FINDING for the
    caller — never fabricated).
    """
    roc = _ROC_DATE_RE.search(value)
    if roc is not None:
        year = int(roc.group(1)) + _ROC_YEAR_OFFSET
        month, day = int(roc.group(2)), int(roc.group(3))
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
