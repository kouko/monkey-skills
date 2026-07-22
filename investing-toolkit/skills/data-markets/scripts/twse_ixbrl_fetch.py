#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""twse_ixbrl_fetch.py — investing-toolkit TW iXBRL raw-filing fetch helper

Fetches the full tagged inline-XBRL instance for a TW filer via MOPS' legacy
`t164sb01` endpoint — the same URL for every market tier (上市/上櫃/興櫃/KY):
a gate-free HTTP GET, no CAPTCHA / session / paid E-Shop. Big5-decodes the
raw body, caches it via `cache_util`, detects the ~98-byte "檔案不存在!"
body as a period-not-filed absence sentinel (never an error/exception),
retries transient HTTP 502 with backoff, and offers a season-fallback
helper for filers whose cadence skips seasons (興櫃/emerging-board primary
filing seasons are Q2/Q4; Q1/Q3 are optional).

Tier-specific logic (season order) lives here, at the fetch/orchestration
layer, never in the parser — see docs/loom/specs/2026-07-19-tw-ixbrl-ingestion.md
§Coverage across market tiers.

Usage:
  from twse_ixbrl_fetch import build_t164sb01_url, fetch_ixbrl_body, \\
      fetch_with_season_fallback

  body = fetch_ixbrl_body(co_id="2330", year=2024, season=3, report_id="C")
  if body is None:
      ...  # period not filed (absence sentinel), not an error

  body, season = fetch_with_season_fallback("2330", 2024, "C")
"""
from __future__ import annotations

import sys
import time

import requests

import cache_util
from twse_ixbrl_parser import decode_ixbrl_document

BASE_URL = "https://mopsov.twse.com.tw/server-java/t164sb01"
NOT_FOUND_MARKER = "檔案不存在"

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0

# Default season-try order for season-fallback. 興櫃 (emerging board) filing
# cadence is semiannual (Q2/H1 + annual mandatory; Q1/Q3 optional), so its
# fallback prioritizes Q2/Q4 over Q1/Q3.
DEFAULT_SEASON_ORDER: tuple[int, ...] = (4, 3, 2, 1)
EMERGING_BOARD_SEASON_ORDER: tuple[int, ...] = (2, 4, 1, 3)

_QUIET = False
_LOG_TAG = "twse-ixbrl-fetch"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


def build_t164sb01_url(co_id: str, year: int, season: int, report_id: str) -> str:
    """Build the t164sb01 request URL. Same URL for every market tier
    (上市/上櫃/興櫃/KY) — `report_id` "C"=consolidated (合併),
    "A"=individual/parent-only (個別). The A/C split tracks CONSOLIDATION
    SCOPE, not filer type: consolidated (-ci) filers are served only at C
    (A 檔案不存在), but individual-only filers — standalone insurers and
    bills-finance filers (e.g. 華票 2820) — are served ONLY at A (C 404s).
    Grounding: -fh arc live probe 2026-07-22 (2820 2026Q1 A=406KB body /
    C=98-byte 檔案不存在; insurers 2851/2867 same); reconciles spec §7's
    -ci-specific "A never served" negative — see docs/loom/specs/
    2026-07-19-tw-ixbrl-ingestion.md:115. See `fetch_with_report_fallback`."""
    return (
        f"{BASE_URL}?step=1&CO_ID={co_id}&SYEAR={year}"
        f"&SSEASON={season}&REPORT_ID={report_id}"
    )


def is_not_found_body(body: str) -> bool:
    """True when `body` is the "檔案不存在" absence sentinel — period not
    filed, never an error. See brief edge cases #7/#11."""
    return NOT_FOUND_MARKER in body


def _get_with_retry(url: str) -> requests.Response:
    """GET `url`, retrying on transient HTTP 502 with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        resp = requests.get(url, timeout=30)
        if resp.status_code == 502 and attempt < MAX_RETRIES - 1:
            _log("retry 502", f"attempt {attempt + 1}/{MAX_RETRIES}")
            time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
            continue
        if resp.status_code == 502:
            raise RuntimeError(f"t164sb01 HTTP 502 after {MAX_RETRIES} attempts: {url}")
        return resp
    raise RuntimeError(f"t164sb01 request failed after retries: {url}")


def fetch_ixbrl_body(co_id: str, year: int, season: int, report_id: str,
                      *, use_cache: bool = True) -> str | None:
    """Fetch + smart-decode the t164sb01 body for one (co_id, year, season,
    report_id). Returns None when TWSE serves the "檔案不存在" absence
    sentinel (period not filed) — never an error/exception.

    Decoding tries UTF-8 strict first, falling back to big5hkscs — MOPS
    declares charset=big5 for every market tier but in practice serves the
    financial family (-fh/-basi/-bd/-ins) as UTF-8; only genuine -ci
    filings are actually Big5. See `twse_ixbrl_parser.decode_ixbrl_document`.

    Cached via cache_util under source "twse_ixbrl"; the absence sentinel
    is NOT cached (so a later fetch, once the filing lands, retries live).
    """
    key = f"{co_id}_{year}Q{season}_{report_id}"
    path = cache_util.cache_path("twse_ixbrl", key)
    if use_cache:
        ttl = cache_util.compute_ttl("quarterly", None)
        cached = cache_util.load_cache(path, ttl)
        if cached is not None and "body" in cached:
            return cached["body"]

    url = build_t164sb01_url(co_id, year, season, report_id)
    resp = _get_with_retry(url)
    body = decode_ixbrl_document(resp.content)

    if is_not_found_body(body):
        return None

    if use_cache:
        cache_util.save_cache(path, {"body": body})
    return body


def fetch_with_season_fallback(
    co_id: str, year: int, report_id: str,
    *, season_order: tuple[int, ...] = DEFAULT_SEASON_ORDER,
    fetch_fn=fetch_ixbrl_body,
) -> tuple[str | None, int | None]:
    """Try each season in `season_order` in turn; the first one whose body
    is not the absence sentinel wins. Returns (body, season), or
    (None, None) if every season in `season_order` is absent.
    """
    for season in season_order:
        body = fetch_fn(co_id, year, season, report_id)
        if body is not None:
            return body, season
    return None, None


# report_id try-order for consolidation-scope fallback. "C" (consolidated)
# is served for -ci filers; individual-only filers (standalone insurers,
# bills-finance filers e.g. 華票 2820) are served ONLY at "A" (individual).
DEFAULT_REPORT_ORDER: tuple[str, ...] = ("C", "A")


def fetch_with_report_fallback(
    co_id: str, year: int, season: int,
    *, report_order: tuple[str, ...] = DEFAULT_REPORT_ORDER,
    fetch_fn=fetch_ixbrl_body,
) -> tuple[str | None, str | None]:
    """Try each report_id in `report_order` in turn ("C" consolidated,
    then "A" individual); the first whose body is not the absence sentinel
    wins. Returns (body, report_id_used), or (None, None) if every
    report_id in `report_order` is absent — same (value, tag) shape as
    `fetch_with_season_fallback`, so callers can unpack unconditionally.

    Handles the CONSOLIDATION-SCOPE split: consolidated (-ci) filers are
    served only at C, but individual-only filers — standalone insurers and
    bills-finance filers (e.g. 華票 2820) — are served ONLY at A (C 404s).
    """
    for report_id in report_order:
        body = fetch_fn(co_id, year, season, report_id)
        if body is not None:
            return body, report_id
    return None, None
