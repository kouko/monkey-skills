#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1", "edgartools==5.42.0"]
# ///
"""
sec_edgar_client.py — investing-toolkit SEC EDGAR data adapter
Fetches US regulatory filings & XBRL structured facts from data.sec.gov.

Two layers:
  (a) XBRL structured facts via JSON API (companyfacts + companyconcept)
  (b) Filing narrative via the edgartools typed section API (10-K/10-Q/8-K)

Usage:
  # Ticker → CIK lookup
  uv run sec_edgar_client.py --ticker NVDA --action cik

  # All XBRL facts for a company
  uv run sec_edgar_client.py --ticker NVDA --action facts

  # Single concept time-series
  uv run sec_edgar_client.py --ticker NVDA --action facts --concept Revenues

  # Recent filings (all forms)
  uv run sec_edgar_client.py --ticker NVDA --action filings --limit 20

  # Recent filings filtered by form
  uv run sec_edgar_client.py --ticker NVDA --action filings --forms 10-K,10-Q,8-K --limit 10

  # Segment a specific filing into its enumerated item sections
  uv run sec_edgar_client.py --accession 0001045810-24-000316 --action narrative

Auth: none required. SEC EDGAR MANDATES identified User-Agent header with
      format "<name> <email>". Without it, requests return 403.
Rate limit: SEC EDGAR permits ≤10 req/sec. Built-in 0.1s throttle + 429 backoff.
Cache: $INVESTING_TOOLKIT_CACHE/sec_edgar/
       Falls back to ~/.cache/investing-toolkit/sec_edgar/ if env var not set.
       (resolved + read/written via cache_util.py — see that module for
       the full precedence ladder and envelope format. Freshness is now
       envelope-`fetched_at`-based, not file-mtime-based.)
"""

import argparse
import calendar
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests as _requests

import cache_util

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SEC_COMPANYCONCEPT_URL = (
    "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{concept}.json"
)
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/{doc}"

# SEC mandates identified User-Agent: "<name> <email>" format.
USER_AGENT = "kouko investing-toolkit <noreply@anthropic.com>"

TTL_TICKERS = 7 * 86400       # 7 days
TTL_FACTS = 86400             # 24 hours
TTL_SUBMISSIONS = 86400       # 24 hours
TTL_NARRATIVE = cache_util.compute_ttl("immutable", None)  # permanent; filings don't change
TTL_EXHIBIT_RAW = cache_util.compute_ttl("immutable", None)  # permanent; a filed exhibit's bytes never change

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
THROTTLE_SECONDS = 0.1        # ≤10 req/sec


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "sec-edgar-us"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# HTTP helpers (throttle + retry + User-Agent)
# ---------------------------------------------------------------------------

def _sec_get(url: str, *, as_json: bool = True) -> dict | str | None:
    """GET with User-Agent, 10 req/sec throttle, 429 backoff."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
        "Host": url.split("/")[2],
    }

    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(THROTTLE_SECONDS)
            resp = _requests.get(url, headers=headers, timeout=30)

            if resp.status_code == 429:
                if attempt < MAX_RETRIES - 1:
                    retry_after = resp.headers.get("Retry-After")
                    delay = (
                        float(retry_after) if retry_after and retry_after.isdigit()
                        else RETRY_BASE_DELAY * (2 ** attempt)
                    )
                    time.sleep(delay)
                    continue
                return {"error": "SEC EDGAR rate-limited (429) after retries"}

            if resp.status_code == 404:
                return {"error": f"SEC EDGAR 404: {url}"}

            if resp.status_code != 200:
                return {"error": f"SEC EDGAR HTTP {resp.status_code}: {url}"}

            return resp.json() if as_json else resp.text

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": "SEC EDGAR request timed out"}
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            return {"error": f"SEC EDGAR connection error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    return {"error": "SEC EDGAR request failed after retries"}


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_provenance(reference_period: str | None = None) -> dict:
    fetched_at = _now_iso()
    staleness = None
    if reference_period:
        try:
            ref = datetime.strptime(reference_period[:10], "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            staleness = (datetime.now(tz=timezone.utc) - ref).days
        except (ValueError, TypeError):
            pass
    return {
        "source": "SEC EDGAR (data.sec.gov)",
        "source_authority": "U.S. Securities and Exchange Commission",
        "data_type": "official_regulatory_filing",
        "update_cycle": "filing-driven",
        "typical_lag": "0-60 days depending on form",
        "fetched_at": fetched_at,
        "reference_period": reference_period,
        "staleness_days": staleness,
    }


# ---------------------------------------------------------------------------
# Ticker → CIK lookup
# ---------------------------------------------------------------------------

def load_ticker_map() -> dict:
    """Load global ticker→CIK map (7-day cache)."""
    path = cache_util.cache_path("sec_edgar", "tickers")
    cached = cache_util.load_cache(path, TTL_TICKERS)
    if cached:
        cached["_cache"] = "hit"
        return cached

    raw = _sec_get(SEC_TICKERS_URL)
    if isinstance(raw, dict) and "error" in raw:
        return raw

    # company_tickers.json is {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "..."}, ...}
    ticker_to_cik = {}
    for _, entry in raw.items():
        ticker = entry.get("ticker", "").upper()
        cik = entry.get("cik_str")
        title = entry.get("title", "")
        if ticker and cik is not None:
            ticker_to_cik[ticker] = {"cik": int(cik), "title": title}

    result = {
        "fetched_at": _now_iso(),
        "_cache": "miss",
        "count": len(ticker_to_cik),
        "tickers": ticker_to_cik,
    }
    cache_util.save_cache(path, result)
    return result


def resolve_cik(ticker: str) -> dict:
    ticker = ticker.upper()
    tmap = load_ticker_map()
    if "error" in tmap:
        return tmap

    entry = tmap.get("tickers", {}).get(ticker)
    if not entry:
        return {"error": f"Ticker {ticker} not found in SEC EDGAR registry"}

    return {
        "ticker": ticker,
        "cik": entry["cik"],
        "cik_padded": f"{entry['cik']:010d}",
        "title": entry["title"],
        "fetched_at": _now_iso(),
        "_cache": tmap.get("_cache", "miss"),
        "_provenance": _make_provenance(),
    }


# ---------------------------------------------------------------------------
# XBRL facts
# ---------------------------------------------------------------------------

def fetch_facts(cik: int, concept: str | None) -> dict:
    """Fetch companyfacts or single-concept time-series."""
    if concept:
        key = f"concept_{cik:010d}_{concept}"
    else:
        key = f"facts_{cik:010d}"
    path = cache_util.cache_path("sec_edgar", key)
    cached = cache_util.load_cache(path, TTL_FACTS)
    if cached:
        cached["_cache"] = "hit"
        return cached

    if concept:
        url = SEC_COMPANYCONCEPT_URL.format(cik=cik, concept=concept)
    else:
        url = SEC_COMPANYFACTS_URL.format(cik=cik)

    raw = _sec_get(url)
    if isinstance(raw, dict) and "error" in raw:
        return raw

    result = {
        "cik": cik,
        "concept": concept,
        "fetched_at": _now_iso(),
        "_cache": "miss",
        "data": raw,
    }
    cache_util.save_cache(path, result)
    return result


def summarize_concept(raw_concept: dict) -> list[dict]:
    """Extract USD time-series from companyconcept response.

    Preserves `start` alongside `end` so downstream consumers can
    distinguish annual (12-month window) from quarterly observations
    when both are tagged `fp: FY` in a single 10-K filing (common for
    Revenues with disaggregated quarterly + annual values).
    """
    units = raw_concept.get("units", {})
    # Prefer USD, fall back to first available unit
    series = units.get("USD") or next(iter(units.values()), [])
    return [
        {
            "start": row.get("start"),
            "end": row.get("end"),
            "value": row.get("val"),
            "accn": row.get("accn"),
            "form": row.get("form"),
            "fy": row.get("fy"),
            "fp": row.get("fp"),
            "filed": row.get("filed"),
        }
        for row in series
    ]


def _companyfacts_pack_error_slot(cik: int, detail: str) -> dict:
    """A loud, sentinel-compatible error slot for a companyfacts fetch failure
    (Open-Q2 keystone, `build_companyfacts_pack`) — mirrors this file's
    error-slot convention (`_acquire_error`/`_statement_extraction_error_slot`):
    a typed dict the caller can branch on, never a fabricated/empty Source-B
    pack. Not `_acquire_error` itself — that helper's message is hardcoded to
    filing acquisition, which would misdescribe a companyfacts JSON-fetch
    failure."""
    return {
        "error": f"SEC EDGAR companyfacts fetch failed for CIK {cik}: {detail}",
        "error_class": "companyfacts_fetch_failed",
        "identifier": str(cik),
    }


def build_companyfacts_pack(cik: int) -> dict:
    """Reshape the CIK's full companyfacts payload into the exact Source-B
    pack shape `analysis-xval/scripts/xval_compute.py::build_source_b_index`
    requires (the Open-Q2 keystone it declares but leaves unwired):
      {"cik": <int>, "facts": {"<taxonomy>": {"<tag>": [<row>, ...]}}}
    where each row is exactly `summarize_concept`'s output shape (`{start,
    end, value, accn, form, fy, fp, filed}`).

    Fetches via the existing `fetch_facts(cik, concept=None)` (full
    companyfacts, cached). The raw SEC endpoint nests each tag one level
    deeper than the consumer expects — `data["facts"][taxonomy][tag]` is a
    `{label, description, units: {"USD": [rows]}}` object, not a bare row
    list — so this flattens `units.USD` into the per-tag row list by
    reusing `summarize_concept` (which already knows how to prefer USD and
    fall back to the first available unit) rather than re-implementing that
    unit-selection logic divergently.

    On a companyfacts fetch error, returns a loud `_companyfacts_pack_error_slot`
    (this file's `_acquire_error` convention) — NEVER a fabricated or empty
    Source-B pack.
    """
    fetched = fetch_facts(cik, None)
    if "error" in fetched:
        return _companyfacts_pack_error_slot(cik, fetched["error"])

    raw_facts = fetched.get("data", {}).get("facts", {})
    facts = {
        taxonomy: {
            tag: summarize_concept(concept_obj)
            for tag, concept_obj in tags.items()
        }
        for taxonomy, tags in raw_facts.items()
    }
    return {"cik": cik, "facts": facts}


# ---------------------------------------------------------------------------
# Filings index
# ---------------------------------------------------------------------------

def fetch_submissions(cik: int) -> dict:
    path = cache_util.cache_path("sec_edgar", f"submissions_{cik:010d}")
    cached = cache_util.load_cache(path, TTL_SUBMISSIONS)
    if cached:
        cached["_cache"] = "hit"
        return cached

    raw = _sec_get(SEC_SUBMISSIONS_URL.format(cik=cik))
    if isinstance(raw, dict) and "error" in raw:
        return raw

    result = {
        "cik": cik,
        "fetched_at": _now_iso(),
        "_cache": "miss",
        "data": raw,
    }
    cache_util.save_cache(path, result)
    return result


def list_filings(
    cik: int,
    forms: list[str] | None,
    limit: int,
    min_filing_date: str | None = None,
) -> list[dict]:
    """Return recent filings, optionally filtered by form and/or a minimum
    filing date.

    `min_filing_date` (an ISO ``YYYY-MM-DD`` string), when given, OVERRIDES
    `limit`'s row-count truncation as the stop condition: every row is scanned
    to the end of the `recent` arrays and a row is kept only if its
    `filingDate` is on or after the cutoff -- rows are never dropped early
    just because `limit` matching-form rows were already collected. This
    filters rather than breaks early specifically so it does NOT depend on
    the `recent` arrays being date-descending -- that ordering assumption is
    unverified beyond a handful of live probes, and an early `break` on an
    unverified ordering claim is the same "truncate early on an assumption"
    shape as the original `--limit 8` bug this fixes, just relocated to
    dates. The arrays are already fully in memory and small (one company's
    filing history), so a full scan costs nothing worth trading correctness
    for.

    This exists to fix a live-observed false gap (2026-07-13, real AAPL run):
    a `limit`-only (row-count) window is capped ACROSS ALL forms combined, so
    a company's own 8-K/10-Q filing volume can crowd a once-a-year 10-K out
    of the returned rows entirely -- `select_narrative_filings` then
    (correctly, given what it was handed) reports a PHANTOM "no 10-K" gap. A
    count window drifts with filing frequency; a date window does not, so
    `min_filing_date` is what a caller wanting a policy-sufficient depth
    should pass (see `narrative_filings_window_days`), not a bigger `limit`.

    `limit` alone (`min_filing_date=None`) preserves the original count-based
    behavior unchanged for other callers (e.g. ad hoc CLI browsing).
    """
    sub = fetch_submissions(cik)
    if "error" in sub:
        return []

    recent = sub.get("data", {}).get("filings", {}).get("recent", {})
    forms_list = recent.get("form", [])
    dates_list = recent.get("filingDate", [])
    accn_list = recent.get("accessionNumber", [])
    primary_doc_list = recent.get("primaryDocument", [])
    primary_desc_list = recent.get("primaryDocDescription", [])
    items_list = recent.get("items", [])
    report_date_list = recent.get("reportDate", [])

    rows: list[dict] = []
    for i in range(len(forms_list)):
        filing_date = dates_list[i] if i < len(dates_list) else None
        if (
            min_filing_date is not None
            and filing_date is not None
            and filing_date < min_filing_date
        ):
            # A row-by-row FILTER, never an early `break`: whether `recent`
            # is date-descending across all forms is not something this code
            # verifies, and breaking on an unverified ordering assumption is
            # the same "truncate early on an assumption" shape as the
            # original `--limit 8` bug, just relocated to dates. The arrays
            # are already fully in memory and small, so scanning to the end
            # costs nothing worth trading correctness for.
            continue
        form = forms_list[i]
        if forms and form not in forms:
            continue
        rows.append({
            "form": form,
            "filingDate": filing_date,
            "accessionNumber": accn_list[i] if i < len(accn_list) else None,
            "primaryDocument": primary_doc_list[i] if i < len(primary_doc_list) else None,
            "primaryDocDescription": primary_desc_list[i] if i < len(primary_desc_list) else None,
            "items": items_list[i] if i < len(items_list) else None,
            "reportDate": report_date_list[i] if i < len(report_date_list) else None,
        })
        if min_filing_date is None and len(rows) >= limit:
            break
    return rows


# ---------------------------------------------------------------------------
# select_narrative_filings — quarter-anchored filing-selection policy (pure
# function, no I/O) over already-fetched `list_filings` rows. Decides WHICH
# filings the memo's narrative reads: the latest 10-K, the latest 10-Q, and
# one earnings 8-K per quarter for the last `n_quarters` quarters.
#
# Two non-negotiable design laws:
#   1. Selection is by ITEM CODE, never recency rank. An 8-K's most recent
#      filing is often a 5.02 executive-change filing, not the earnings
#      release (live-observed on AAPL, 2026-07-13: the latest 8-K was
#      items="5.02"; the actual earnings 8-K was an older one in the same
#      quarter, items="2.02,9.01"). Item-code membership is checked by
#      splitting the comma-separated `items` field into a set, never by
#      substring (so a hypothetical "12.02" never matches "2.02").
#   2. The window is anchored in TIME (quarters), never in filing count.
#      8-K volume is unpredictable (it is the "any material event" form), so
#      a count-based window drifts with a company's filing frequency.
# ---------------------------------------------------------------------------

def _quarter_of(date_str: str | None) -> tuple[int, int] | None:
    """(year, quarter) for an ISO date string, or None if unparseable/absent."""
    if not date_str:
        return None
    try:
        d = date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
    return (d.year, (d.month - 1) // 3 + 1)


def _quarter_label(year_quarter: tuple[int, int]) -> str:
    year, quarter = year_quarter
    return f"{year}Q{quarter}"


def _quarter_shift(year_quarter: tuple[int, int], n: int) -> tuple[int, int]:
    """(year, quarter) shifted back by `n` quarters (n >= 0)."""
    year, quarter = year_quarter
    total = year * 4 + (quarter - 1) - n
    return (total // 4, total % 4 + 1)


def _has_item_code(items: str | None, code: str) -> bool:
    """Exact set-membership over the comma-separated `items` field — never a
    substring search (a hypothetical "12.02" must not match "2.02")."""
    if not items:
        return False
    return code in {part.strip() for part in items.split(",")}


def _latest_filing(filings: list[dict], form: str) -> dict | None:
    rows = [r for r in filings if r.get("form") == form and r.get("filingDate")]
    if not rows:
        return None
    return max(rows, key=lambda r: r["filingDate"])


def select_narrative_filings(
    filings: list[dict],
    n_quarters: int = 4,
    as_of: date | None = None,
) -> dict:
    """Select the filings the memo's narrative reads from `filings` rows (as
    returned by `list_filings`): the latest 10-K, the latest 10-Q, and one
    earnings 8-K (submissions `items` containing "2.02") per quarter for the
    last `n_quarters` quarters, anchored at `as_of` (defaults to
    `date.today()` — injectable for deterministic tests; no wall-clock read
    happens inside the selection logic below this point).

    Returns:
      {
        "selected": [ <filing row> + {"role": "10-K"|"10-Q"|"8-K",
                                       "quarter": "<YYYYQn>" for 8-K only}, ... ],
        "gaps": [ {"role": ..., "quarter": ..., "error": "...",
                    "error_class": "no_filing"|"no_earnings_8k"}, ... ],
        "requested": 2 + n_quarters,  # fixed by the policy, never by outcome
      }

    A quarter with no qualifying item-2.02 8-K yields an explicit gap entry
    naming the quarter and the reason — never a silent omission, mirroring
    the repo's `_section_gap` gap-slot idiom (`error` + `error_class`).
    """
    anchor = as_of or date.today()
    anchor_yq = (anchor.year, (anchor.month - 1) // 3 + 1)

    selected: list[dict] = []
    gaps: list[dict] = []

    for role, form in (("10-K", "10-K"), ("10-Q", "10-Q")):
        latest = _latest_filing(filings, form)
        if latest:
            selected.append({**latest, "role": role})
        else:
            gaps.append({
                "role": role,
                "error": f"no {form} filing found",
                "error_class": "no_filing",
            })

    earnings_by_quarter: dict[tuple[int, int], list[dict]] = {}
    for row in filings:
        if row.get("form") != "8-K" or not _has_item_code(row.get("items"), "2.02"):
            continue
        year_quarter = _quarter_of(row.get("reportDate") or row.get("filingDate"))
        if year_quarter is None:
            continue
        earnings_by_quarter.setdefault(year_quarter, []).append(row)

    for n in range(n_quarters):
        target_yq = _quarter_shift(anchor_yq, n)
        label = _quarter_label(target_yq)
        candidates = earnings_by_quarter.get(target_yq)
        if candidates:
            pick = max(candidates, key=lambda r: r.get("filingDate") or "")
            selected.append({**pick, "role": "8-K", "quarter": label})
        else:
            gaps.append({
                "role": "8-K",
                "quarter": label,
                "error": f"no earnings 8-K (item 2.02) found for quarter {label}",
                "error_class": "no_earnings_8k",
            })

    return {
        "selected": selected,
        "gaps": gaps,
        "requested": 2 + n_quarters,
    }


# SEC 10-K filing deadlines (Exchange Act reporting-company categories): large
# accelerated filers must file within 60 days of fiscal year end, accelerated
# filers within 75, all other filers within 90 of fiscal year end. But 90 is
# NOT the worst case: Rule 12b-25 lets ANY filer submit a Form 12b-25 (NT
# 10-K) and receive an automatic 15-calendar-day extension on top of its own
# deadline -- routine for non-accelerated/small-cap filers. The true worst
# case is 90 + 15 = 105 days.
_MAX_10K_FILING_LAG_DAYS = 105
# Deliberate buffer ON TOP of the true worst case above -- not shaved to the
# boundary. A prior implementation used a 1-day margin (455 worst-case vs a
# 456-day window) with no test covering it; this margin exists so the window
# tolerates minor calendar edge cases (e.g. a deadline landing on a
# weekend/holiday, which SEC rules roll to the next business day) without
# re-deriving exact worst-case arithmetic each time.
_FILING_LAG_SAFETY_MARGIN_DAYS = 30
_DAYS_PER_YEAR = 366  # leap-safe
_DAYS_PER_QUARTER = 92  # calendar-quarter upper bound (Jan-Mar=90 .. Jul-Sep=92)


def narrative_filings_window_days(n_quarters: int = 4) -> int:
    """The lookback window (in days) a raw filings fetch MUST cover so that
    `select_narrative_filings` can find every filing its policy asks for --
    the latest 10-K, the latest 10-Q, and an earnings 8-K per quarter for the
    last `n_quarters` -- regardless of how many OTHER filings (8-Ks/10-Qs)
    intervened.

    This is the fix for a live-observed false gap (2026-07-13, real AAPL
    run): the raw filings fetch used to cap on a filing COUNT (`--limit 8`,
    applied across ALL forms combined), and AAPL's own 8-K/10-Q volume
    crowded the once-a-year 10-K out of the last 8 rows entirely --
    `select_narrative_filings` then (correctly, given what it was handed)
    reported a PHANTOM "no 10-K" gap for a filer that obviously has one. A
    count window drifts with a company's filing frequency; a TIME window
    does not -- so this returns DAYS, never a row count, and a caller should
    pass the result to `list_filings`'s `min_filing_date`, never bump a
    `limit` integer.

    Two lower bounds; the wider one wins:
      - the LATEST 10-K: filed once per fiscal year, up to
        `_MAX_10K_FILING_LAG_DAYS` (105 -- the 90-day non-accelerated
        deadline PLUS Rule 12b-25's automatic 15-day NT-10-K extension) after
        the fiscal year it reports, plus `_FILING_LAG_SAFETY_MARGIN_DAYS` of
        deliberate buffer. One full year back plus that lag+margin is
        provably sufficient against a filer using the Rule 12b-25 extension
        -- but NOT against a filer who blows even the EXTENDED deadline
        (genuinely delinquent, > 105 days late). That residual case is
        accepted deliberately, not overlooked: if a 10-K is that late, the
        filing really is overdue, and `select_narrative_filings` reporting a
        gap for it is arguably correct behavior, not a false negative.
      - `n_quarters` of earnings 8-Ks: `n_quarters` calendar quarters back
        (`_DAYS_PER_QUARTER` upper-bounds one quarter's length).
    """
    annual_bound = (
        _DAYS_PER_YEAR + _MAX_10K_FILING_LAG_DAYS + _FILING_LAG_SAFETY_MARGIN_DAYS
    )  # 366 + 105 + 30 = 501
    quarterly_bound = n_quarters * _DAYS_PER_QUARTER
    return max(annual_bound, quarterly_bound)


# ---------------------------------------------------------------------------
# Accession helper (shared by the provenance URL + section-text path builders)
# ---------------------------------------------------------------------------

def _accession_nodash(accession: str) -> str:
    return accession.replace("-", "")


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

def action_cik(ticker: str) -> dict:
    _log("cik fetch", ticker)
    t0 = time.monotonic()
    result = resolve_cik(ticker)
    if "error" in result:
        return result
    result["action"] = "cik"
    _log("cik done", f"{ticker} -> {result.get('cik')} in {time.monotonic() - t0:.1f}s")
    return result


def action_facts(ticker: str, concept: str | None) -> dict:
    _log("facts fetch", f"{ticker}{(' concept=' + concept) if concept else ''}")
    t0 = time.monotonic()
    cik_info = resolve_cik(ticker)
    if "error" in cik_info:
        return cik_info
    cik = cik_info["cik"]

    facts = fetch_facts(cik, concept)
    if "error" in facts:
        facts["ticker"] = ticker
        facts["action"] = "facts"
        return facts

    out: dict = {
        "ticker": ticker,
        "cik": cik,
        "title": cik_info.get("title"),
        "action": "facts",
        "concept": concept,
        "fetched_at": facts.get("fetched_at"),
        "_cache": facts.get("_cache"),
    }

    if concept:
        observations = summarize_concept(facts.get("data", {}))
        ref = observations[-1]["end"] if observations else None
        out["observations"] = observations
        out["count"] = len(observations)
        out["latest"] = observations[-1] if observations else None
        out["_provenance"] = _make_provenance(ref)
    else:
        # Return concept names + count summary, not full dump
        us_gaap = facts.get("data", {}).get("facts", {}).get("us-gaap", {})
        dei = facts.get("data", {}).get("facts", {}).get("dei", {})
        out["concept_counts"] = {
            "us-gaap": len(us_gaap),
            "dei": len(dei),
        }
        out["us_gaap_concepts"] = sorted(us_gaap.keys())
        out["entityName"] = facts.get("data", {}).get("entityName")
        out["_provenance"] = _make_provenance()

    cache_label = "cache hit" if facts.get("_cache") == "hit" else f"in {time.monotonic() - t0:.1f}s"
    _log("facts done", f"{ticker}{(' concept=' + concept) if concept else ''} {cache_label}")
    return out


def action_filings(
    ticker: str,
    forms: list[str] | None,
    limit: int,
    since_days: int | None = None,
) -> dict:
    """`since_days`, when given, fetches by a DATE window (today - since_days)
    instead of `limit`'s row count -- see `list_filings`'s `min_filing_date`
    and `narrative_filings_window_days` for why: a count window drifts with a
    company's filing frequency (the root cause of a live-observed false gap),
    a date window does not."""
    min_filing_date = (
        (date.today() - timedelta(days=since_days)).isoformat()
        if since_days is not None else None
    )
    _log(
        "filings fetch",
        f"{ticker} forms={forms or 'ALL'} "
        + (f"since_days={since_days}" if since_days is not None else f"limit={limit}"),
    )
    t0 = time.monotonic()
    cik_info = resolve_cik(ticker)
    if "error" in cik_info:
        return cik_info
    cik = cik_info["cik"]

    rows = list_filings(cik, forms, limit, min_filing_date=min_filing_date)
    latest_date = rows[0]["filingDate"] if rows else None
    _log("filings done", f"{ticker} {len(rows)} rows in {time.monotonic() - t0:.1f}s")
    return {
        "ticker": ticker,
        "cik": cik,
        "title": cik_info.get("title"),
        "action": "filings",
        "forms_filter": forms,
        "limit": limit,
        "since_days": since_days,
        "min_filing_date": min_filing_date,
        "count": len(rows),
        "filings": rows,
        "fetched_at": _now_iso(),
        "_provenance": _make_provenance(latest_date),
    }


def _looks_like_email(token: str) -> bool:
    """True if a whitespace token — stripped of the angle brackets SEC's
    `<name> <email>` convention allows — is email-shaped (local@dotted.domain)."""
    candidate = token.strip("<>").strip()
    if candidate.count("@") != 1:
        return False
    local, _, domain = candidate.partition("@")
    return bool(local) and "." in domain and not domain.startswith(".") and not domain.endswith(".")


def _is_compliant_identity(identity: str) -> bool:
    """SEC fair-access mandates a `<name> <email>` User-Agent. Compliant means at
    least one name token precedes an email-shaped token (an email alone, or an
    empty string, is non-compliant)."""
    tokens = (identity or "").split()
    email_idx = next(
        (i for i, tok in enumerate(tokens) if _looks_like_email(tok)), None
    )
    return email_idx is not None and email_idx >= 1


def _ensure_edgar_identity(identity: str | None = None) -> dict | None:
    """Configure edgartools' SEC identity from USER_AGENT BEFORE any network request.

    Returns a loud ``{"error": ...}`` slot — rejecting before send — when no
    compliant `<name> <email>` identity is configured; otherwise sets the identity
    on edgartools and returns None.

    This pre-send guard is load-bearing: edgartools does NOT fail-fast on an unset
    identity (``get_identity()`` prompts interactively, then raises ``TimeoutError``
    after ~60s), so the SEC fair-access identity requirement is enforced here, not
    by the library default.
    """
    ident = (USER_AGENT if identity is None else identity or "").strip()
    if not _is_compliant_identity(ident):
        return {
            "error": (
                "SEC EDGAR identity not configured: a compliant "
                "'<name> <email>' User-Agent is required before any sec.gov "
                f"request (got {ident!r})"
            )
        }
    import edgar

    edgar.set_identity(ident)
    return None


# ---------------------------------------------------------------------------
# edgartools-based filing acquisition (edgartools 5.42.0)
# ---------------------------------------------------------------------------
# Real Filing shape captured live 2026-07-12 (AAPL FY2024 10-K, accession
# 0000320193-24-000123; anchored by test_data_markets_live.py
# ::test_edgartools_acquire_real_10k_shape):
#   accession_no:str  cik:int  form:str  filing_date:datetime.date(!)
#   period_of_report:str  filing_url:str (primary-doc URL)  homepage_url:str
# edgartools has NO `primary_document` attr — the primary-doc filename is the
# last path segment of filing_url, which is itself the reconstructable SEC
# Archives URL `.../data/{cik}/{accession-no-dashes}/{document}`.


def _filing_date_iso(value) -> str | None:
    """Serialize edgartools' ``Filing.filing_date`` (a ``datetime.date``, not a
    string) to an ISO ``YYYY-MM-DD`` string; pass None/str through defensively."""
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _primary_document(filing) -> str | None:
    """The filing's primary-document filename — the tail of edgartools'
    ``Filing.filing_url`` (edgartools exposes no ``primary_document`` attr, so the
    last path segment of ``filing_url`` is the reconstructable filename)."""
    filing_url = filing.filing_url
    return filing_url.rsplit("/", 1)[-1] if filing_url else None


def _filing_ref(filing) -> dict:
    """Build a JSON-safe filing reference from a real edgartools ``Filing``.

    Carries the six provenance fields the spec requires (accession, CIK, form,
    filingDate, period_of_report, primaryDocument) plus the reconstructable SEC
    Archives ``url``. ``filingDate`` derives from the filing's disclosure date
    (never wall-clock — as_of invariant); ``primaryDocument`` and ``url`` come
    from ``filing_url`` (edgartools exposes no ``primary_document`` attribute).
    """
    filing_url = filing.filing_url
    primary_document = _primary_document(filing)
    return {
        "accession": filing.accession_no,
        "cik": filing.cik,
        "form": filing.form,
        "filingDate": _filing_date_iso(filing.filing_date),
        "period_of_report": filing.period_of_report,
        "primaryDocument": primary_document,
        "url": filing_url,
    }


def _acquire_error(error_class: str, detail: str, *, identifier=None,
                   form: str | None = None) -> dict:
    """A loud, flat ``{"error": ...}`` acquisition-failure slot (read by
    pack_inventory/_status), tagged with a distinguishing ``error_class`` so the
    resolution and form-unavailable failure modes stay distinct."""
    slot: dict = {
        "error": f"SEC EDGAR filing acquisition failed: {detail}",
        "error_class": error_class,
    }
    if identifier is not None:
        slot["identifier"] = str(identifier)
    if form is not None:
        slot["form"] = form
    return slot


def _acquire_raw_filing(accession: str) -> object:
    """Acquire the RAW edgartools ``Filing`` object for an accession — the SHARED
    producer boundary the acquire→segment seam is built on.

    Returns the raw edgartools Filing (which exposes ``.obj()`` / ``.form`` /
    ``.cik`` / ``.filing_date`` — the surface both segmentation and metadata
    reads need) on success, or a loud ``{"error": ...}`` resolution slot when the
    identity is unset, edgartools raised, or the accession did not resolve to a
    filing — never a silent ``None``.

    Both ``acquire_filing`` (which projects this to a JSON ``_filing_ref`` dict)
    and ``fetch_narrative_sections`` (which segments the raw filing + reads its
    disclosure metadata) go through here, so the two callers can NEVER diverge on
    the producer shape: passing the JSON ref dict to ``segment_filing`` would
    crash on ``filing.obj()`` / ``filing.form`` (a ``dict`` has neither). Keeping
    the raw filing at this seam is what preserves the live ``--action narrative``
    contract against real edgartools.
    """
    identity_error = _ensure_edgar_identity()
    if identity_error is not None:
        return identity_error

    import edgar

    try:
        filing = edgar.get_by_accession_number(accession)
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        return _acquire_error(
            "resolution",
            f"accession {accession!r} did not resolve to a filing ({exc})",
            identifier=accession,
        )
    if filing is None:
        return _acquire_error(
            "resolution",
            f"accession {accession!r} did not resolve to a filing",
            identifier=accession,
        )
    return filing


def acquire_filing(
    identifier: str | int | None = None,
    *,
    form: str | None = None,
    accession: str | None = None,
) -> dict:
    """Acquire a 10-K/10-Q/8-K filing reference via edgartools.

    Two acquisition modes (edgartools 5.42.0):
      - by ``accession``: ``edgar.get_by_accession_number(accession)`` (via the
        shared ``_acquire_raw_filing`` producer boundary), then projected to a
        JSON ``_filing_ref`` dict.
      - by ``identifier`` (ticker or CIK) + optional ``form`` filter:
        ``edgar.Company(identifier).get_filings(form=form).latest()``

    Returns a filing-reference dict (see ``_filing_ref``) on success, or one of
    two DISTINCT loud ``{"error": ...}`` slots on failure, tagged by
    ``error_class``:
      - ``"resolution"``       — the ticker/CIK/accession did not resolve to a
        registered SEC filer (never a silent-empty result).
      - ``"form_unavailable"`` — the filer resolved but never filed ``form``
        within the lookup window (empirically an empty ``Filings`` whose
        ``.latest()`` is ``None``), distinct from a resolution error and never a
        silent substitution.

    The not-found shape is unverified as an exception, so resolution failure is
    detected defensively: an exception from ``Company``/``get_by_accession_number``,
    a falsy company, ``company.not_found``, or a falsy ``company.cik`` all map to
    the resolution slot.
    """
    if accession is not None:
        filing = _acquire_raw_filing(accession)
        if isinstance(filing, dict):  # a loud error slot (never a raw Filing)
            return filing
        return _filing_ref(filing)

    # ticker / CIK path
    identity_error = _ensure_edgar_identity()
    if identity_error is not None:
        return identity_error

    import edgar

    try:
        company = edgar.Company(identifier)
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        return _acquire_error(
            "resolution",
            f"identifier {identifier!r} did not resolve to a registered SEC filer ({exc})",
            identifier=identifier,
        )
    if company is None or getattr(company, "not_found", False) or not getattr(company, "cik", None):
        return _acquire_error(
            "resolution",
            f"identifier {identifier!r} did not resolve to a registered SEC filer",
            identifier=identifier,
        )

    filings = company.get_filings(form=form)
    latest = filings.latest() if filings is not None else None
    if latest is None:
        return _acquire_error(
            "form_unavailable",
            f"form {form!r} not available for identifier {identifier!r} within the lookup window",
            identifier=identifier,
            form=form,
        )
    return _filing_ref(latest)


# ---------------------------------------------------------------------------
# edgartools-based item segmentation (edgartools 5.42.0)
# ---------------------------------------------------------------------------
# Real TenK/TenQ section-API shape captured live 2026-07-12 (AAPL FY2024 10-K
# 0000320193-24-000123 + AAPL latest 10-Q; anchored by test_data_markets_live.py
# ::test_edgartools_segment_real_10k_shape):
#   filing.obj() -> TenK / TenQ.
#   TenK / TenQ / CurrentReport: `obj.items` enumerates the FULL item-id set;
#     each item's text is read via the subscript `obj[item_id]` -> `str` (or
#     `None` when absent from this filing, issue #710). (edgartools also exposes
#     convenience props like `management_discussion`/`risk_factors`, but
#     segmentation enumerates ALL items so it uses the generic subscript.)
#
# SECTION-OBJECT CONTRACT (established here, reused by Tasks 4-12) --------------
# `segment_filing()` returns a LIST of per-item section dicts in enumerated order:
#   SUCCESS section: {"item": "<item id>", "text_path": "<file path>", **extra}
#     — a plain dict later tasks EXTEND in place. The extracted body is written
#       to a file and referenced by `text_path` (paths-not-content, Task 7 —
#       which REPLACED the earlier inline `text` key), never inlined in the
#       section dict / JSON result; T6 added provenance, T9 adds
#       `disclosure_status`. `extra` is a per-section provenance dict merged
#       in by `_build_section`; empty for 10-K/10-Q, and for 8-K it carries
#       `{"exhibit": "<EX-99.x filename>"}` (Task 4) — the source-exhibit
#       filename the item's narrative text was followed to.
#   FAILURE slot:    {"item": "<item id>", "error": "<why>",
#                     "error_class": "absent_item"}
#     — a sentinel-compatible dict; the top-level `error` key is read unchanged
#       by pack.py's `_status`, and the slot NAMES the missing item so an
#       enumerated-but-absent item is never dropped or fabricated.
# A multi-section result is a list later tasks append to / extend.
#
# EXTRACTOR CONTRACT (widened by Task 4; text made lazy by Task 8) -------------
# A registered extractor is called `extractor(obj, filing)` and returns a LIST
# of per-item entries; each entry is either a 2-tuple `(item_id, text_thunk)`
# or a 3-tuple `(item_id, text_thunk, extra_dict)` where `text_thunk` is a
# ZERO-ARG CALLABLE returning the item's text-or-None (Task 8: the text is
# resolved lazily, NOT at list-build time, so `segment_filing` can call each
# thunk under its own try/except and ISOLATE a mid-parse throw to that one item's
# error slot while the other items still segment), and `extra_dict` is the
# per-section provenance merged into a SUCCESS section (see `extra` above), OR a
# ready-made section/gap dict (Task 4/5) — used when the extractor ALONE can
# detect a gap the shared absent-item logic can't classify (8-K's missing or
# ambiguous Exhibit 99.x -> a `"missing_exhibit"` gap slot); `segment_filing`
# passes such a dict through unchanged. The `filing` arg is passed to every
# extractor (10-K/10-Q ignore it); 8-K needs it to reach the filing's exhibit
# attachments. The 3rd tuple element widens the T3 2-tuple contract WITHOUT
# breaking it — 2-tuples still work (extra = {}).


def _segment_all_body_items(obj, filing) -> list[tuple[str, object]]:
    """Every item edgartools enumerates on a 10-K/10-Q typed object — one
    ``(item id, text-thunk)`` pair per id in ``obj.items`` (the full ordered
    item-id list; a live probe 2026-07-12 showed an AAPL 10-K's ``obj.items``
    enumerating all 23 items). Pure data-acquisition (design pivot): the layer
    preserves EVERY body item (Business, Risk Factors, MD&A, Financial Statements,
    Controls, Governance, ...) and NO curated Item-7/1A subset — the read/relevance
    decision is deferred to downstream consumers.

    Each pair's text element is a ZERO-ARG THUNK reading ``obj[item_id]`` (the
    item's text as ``str``, or ``None`` when the item is absent from THIS filing
    -> the shared absent-item gap in ``_build_section``; issue #710), so
    ``segment_filing`` evaluates each subscript under its own try/except and
    ISOLATES a mid-parse throw to that one item's error slot (Task 8) — the other
    items still segment. Each lambda binds ``item=item_id`` as a default arg so the
    thunk captures ITS OWN id, not the shared loop variable (the classic Python
    late-binding closure bug). ``filing`` is unused here (10-K/10-Q text is on
    ``obj``); it is in the signature for the uniform extractor contract that 8-K's
    exhibit-following needs."""
    return [(item_id, lambda item=item_id: obj[item]) for item_id in obj.items]


def _segment_10k(obj, filing) -> list[tuple[str, object]]:
    """All-item ``(item id, text-thunk)`` pairs for a 10-K ``TenK`` typed object
    (design pivot: every ``obj.items`` id, not the retired Item 7 + Item 1A
    subset). See ``_segment_all_body_items`` for the enumeration + closure-capture
    contract."""
    return _segment_all_body_items(obj, filing)


def _segment_10q(obj, filing) -> list[tuple[str, object]]:
    """All-item ``(item id, text-thunk)`` pairs for a 10-Q ``TenQ`` typed object
    (design pivot: every ``obj.items`` id, not the retired single Item 2). See
    ``_segment_all_body_items`` for the enumeration + closure-capture contract."""
    return _segment_all_body_items(obj, filing)


# 8-K reported-item codes whose substantive narrative lives in an Exhibit 99.x
# (the 8-K body carries only the announcement). Item 9.01 (Financial Statements
# and Exhibits) merely lists the exhibits and is not itself a narrative item.
_EIGHTK_EXHIBIT_ITEMS = ("Item 2.02", "Item 7.01", "Item 8.01")


def _exhibit_gap(item_id: str, filing, *, item_count: int, release_count: int) -> dict:
    """A loud, sentinel-compatible gap slot for a reported 8-K exhibit-bearing
    item whose Exhibit 99.x cannot be resolved to source its narrative — either
    absent (no press-release exhibit) or ambiguous (>=2 exhibit-bearing items, so
    per-item correspondence isn't determinable). Names the accession + item code;
    read unchanged by pack.py's ``_status`` (Task 5)."""
    return {
        "item": item_id,
        "error": (
            f"8-K item {item_id!r} reported in filing "
            f"{getattr(filing, 'accession_no', None)!r} but its Exhibit 99.x "
            f"could not be resolved to source its narrative "
            f"({item_count} exhibit-bearing item(s), {release_count} EX-99.x "
            f"press-release exhibit(s); safe pairing requires exactly one of each)"
        ),
        "error_class": "missing_exhibit",
    }


def _segment_8k(obj, filing) -> list[object]:
    """Per-item entries for an 8-K — one entry for EVERY reported item in
    ``obj.items`` (design pivot: pure acquisition, NOT a curated 2.02/7.01/8.01
    subset), the read/relevance decision deferred to downstream consumers.

    An exhibit-bearing item (2.02/7.01/8.01 — ``_EIGHTK_EXHIBIT_ITEMS``, whose
    substance lives in an Exhibit 99.x while the 8-K body carries only the
    announcement) is FOLLOWED to its exhibit: a success triple ``(item id,
    exhibit text, {"exhibit": filename, "disclosure_status": "furnished"})`` when
    resolvable, else a loud missing-exhibit gap dict (never a silent skip, an
    empty section, a positional guess, or an uncaught IndexError). Every OTHER
    reported item carries its OWN body text via a ``(item id, obj[item_id])``
    thunk — resolved lazily by ``segment_filing`` (str, or None → the shared
    absent-item gap) and defaulting to ``disclosure_status: "filed"`` in
    ``_build_section`` (a body-sourced 8-K item is filed, not furnished).

    Live-captured shape (edgartools 5.42.0; ``filing.obj()`` -> ``CurrentReport``,
    NOT ``EightK`` — plan-grounding correction): ``obj.items`` is a list of
    reported item-id strings (a live probe 2026-07-12 showed AAPL's 8-K reporting
    ``['Item 2.02', 'Item 9.01']``); ``obj[item_id]`` gives an item's body text;
    ``obj.press_releases`` is the collection of EX-99.x press-release exhibits,
    each a ``PressRelease`` with ``.document`` (the EX-99.x filename) + ``.text()``
    (the exhibit body). We read the exhibit text (not the 8-K body announcement)
    for an exhibit-bearing item and record the source exhibit filename in the
    section's `exhibit` provenance field.

    Only the unambiguous 1:1 case (exactly one reported exhibit-bearing item and
    exactly one press-release exhibit) is paired — there the correspondence is
    determined, not guessed. Any other shape (no exhibit for a reported item, a
    count mismatch, or >=2 exhibit-bearing items whose item->exhibit mapping is
    non-positional) emits a loud named gap per affected exhibit-bearing item:
    silent-wrong is the enemy, so we never mis-attribute an exhibit to the wrong
    item (T4 review finding, folded in by Task 5). Non-exhibit items are
    unaffected by exhibit ambiguity — they always source their own body text.

    LOOM-SIMPLIFY: shortcut: a >=2-exhibit-item 8-K (or count mismatch) is emitted
    as loud per-item gaps rather than resolving each reported item body's
    "Exhibit 99.x" cross-reference to map it to the right exhibit | ceiling: a real
    8-K reporting >=2 exhibit-bearing items each with its own recoverable EX-99.x
    (e.g. Item 2.02->EX-99.1, Item 7.01->EX-99.2) whose content we want extracted,
    not gapped | upgrade: parse each reported item's body text for its referenced
    exhibit number and map by that | ref: spec Requirement "8-K Full-Item
    Segmentation with Exhibit-Following". (The gap itself is loud + tested; this
    cut defers the multi-exhibit RESOLUTION, not the fail-loud behaviour.)
    """
    following = [item_id for item_id in obj.items if item_id in _EIGHTK_EXHIBIT_ITEMS]
    releases = list(obj.press_releases)
    # Resolve each exhibit-bearing item to its exhibit entry (success triple) or a
    # loud gap, keyed by item id so the all-items enumeration below can look it up.
    if len(following) == 1 and len(releases) == 1:
        item_id, release = following[0], releases[0]
        # ``release.text`` is a zero-arg method → pass it AS the text-thunk so
        # `segment_filing` evaluates the exhibit body under its own try/except
        # (Task 8 per-item isolation); ``release.document`` (the filename) is
        # read eagerly for provenance. ``disclosure_status: "furnished"`` (Task 9)
        # is derived from the SOURCE TYPE (an 8-K Item 2.02/7.01/8.01 Exhibit 99.x
        # is FURNISHED, not filed) — NOT read from edgartools — so a downstream
        # consumer can weight it distinctly from filed 10-K/10-Q content.
        exhibit_entries = {
            item_id: (
                item_id, release.text,
                {"exhibit": release.document, "disclosure_status": "furnished"},
            )
        }
    else:
        exhibit_entries = {
            item_id: _exhibit_gap(
                item_id, filing, item_count=len(following), release_count=len(releases)
            )
            for item_id in following
        }
    # Emit a section for EVERY reported item, in reported order: exhibit-bearing
    # items use their resolved exhibit entry; every other item sources its own
    # body text (``obj[item_id]``, lazily thunked so a mid-parse throw is isolated
    # to that item — Task 8; ``item=item_id`` default binds each thunk's own id,
    # avoiding the late-binding closure bug).
    return [
        exhibit_entries[item_id]
        if item_id in exhibit_entries
        else (item_id, lambda item=item_id: obj[item])
        for item_id in obj.items
    ]


# form -> extractor(obj, filing) returning per-item entries (see EXTRACTOR
# CONTRACT above): [(item id, text-or-None[, extra_dict]), ...] from filing.obj().
_ITEM_EXTRACTORS = {
    "10-K": _segment_10k,
    "10-Q": _segment_10q,
    "8-K": _segment_8k,
}


def _timeout_exc_types() -> tuple:
    """The exception types that classify as a distinct ``timeout`` acquisition
    failure (Task 10) — the builtin ``TimeoutError`` plus edgartools' ``httpx``
    timeout family when ``httpx`` is importable (edgartools does its HTTP over
    ``httpx``, so a real fetch timeout surfaces as ``httpx.TimeoutException``).

    ``httpx`` is NOT guaranteed importable in offline CI, so its timeout type is
    added only when reachable — a soft, conditional import, never a hard top-level
    one (which would break offline). In production a real ``httpx`` timeout means
    ``httpx`` IS installed (edgartools raised it), so it is in the tuple then; the
    builtin ``TimeoutError`` is always present as the offline-testable stand-in."""
    types: list = [TimeoutError]
    try:
        import httpx

        types.append(httpx.TimeoutException)
    except Exception:  # noqa: BLE001 — httpx absent offline; builtin TimeoutError suffices
        pass
    return tuple(types)


# Narrower-than-Exception timeout family, resolved once at import (see Task 10).
_TIMEOUT_EXC_TYPES = _timeout_exc_types()


def _all_sections_failed(form: str, filing, exc: BaseException, slot=None) -> list[dict]:
    """A single loud FORM-LEVEL error slot, for when `filing.obj()` or extractor
    building failed wholesale — no top-level success is claimed. Post design-pivot
    the item set is DYNAMIC (every ``obj.items`` id), so once ``obj()`` itself
    fails the items are UNKNOWABLE and cannot be enumerated; every form (10-K/
    10-Q/8-K) falls back to a single ``"form <FORM>"`` slot so the failure is
    never silently dropped (there is no static per-item map to reconstruct).

    `slot` is the per-item slot builder (signature ``(item_id, filing, exc)``);
    defaults to ``_extraction_error_slot`` (Task 8's generic wholesale-failure
    class) but the timeout carve-out (Task 10) passes ``_timeout_error_slot`` so a
    wholesale TIMEOUT classifies the form-level slot as the distinct ``timeout``
    class, not the generic ``extraction_error``. (Default resolved in the body,
    not the signature, because ``_extraction_error_slot`` is defined below this
    function.)"""
    slot = slot or _extraction_error_slot
    return [slot(f"form {form}", filing, exc)]


def _section_gap(item_id: str, filing) -> dict:
    """A loud, sentinel-compatible per-section error slot naming the missing
    item + its accession (read by pack.py's `_status`)."""
    return {
        "item": item_id,
        "error": (
            f"section {item_id!r} not present in filing "
            f"{getattr(filing, 'accession_no', None)!r} "
            f"(form {getattr(filing, 'form', None)!r})"
        ),
        "error_class": "absent_item",
    }


def _extraction_error_slot(item_id: str, filing, exc: BaseException) -> dict:
    """A loud, sentinel-compatible per-section error slot for an item whose
    extraction RAISED (Task 8) — distinct from the `"absent_item"` (None) and
    `"missing_exhibit"` gaps: here edgartools threw while parsing/building the
    section (a single item's property/subscript access, or `filing.obj()`
    wholesale). The throw is isolated to this slot so the OTHER items still
    segment and nothing crashes `segment_filing`; the top-level `error` key is
    read unchanged by pack.py's `_status`, classifying the aggregate as partial
    (some fail) / failed (all fail)."""
    return {
        "item": item_id,
        "error": (
            f"section {item_id!r} extraction failed for filing "
            f"{getattr(filing, 'accession_no', None)!r} "
            f"(form {getattr(filing, 'form', None)!r}): {exc}"
        ),
        "error_class": "extraction_error",
    }


def _timeout_error_slot(item_id: str, filing, exc: BaseException) -> dict:
    """A loud, sentinel-compatible per-section error slot for an item whose
    extraction TIMED OUT (Task 10) — a DISTINCT, retryable class carved out of the
    generic ``extraction_error`` (Task 8) so a transient network timeout is not
    merged into a content gap. Same ``(item_id, filing, exc)`` signature as
    ``_extraction_error_slot`` so the wholesale-failure path (`_all_sections_failed`)
    can swap it in. Carries ``retryable: True`` — the timeout class is safe to
    retry, unlike a content gap or a version-drift shape mismatch; the top-level
    ``error`` key is still read unchanged by pack.py's ``_status``."""
    return {
        "item": item_id,
        "error": (
            f"section {item_id!r} fetch timed out for filing "
            f"{getattr(filing, 'accession_no', None)!r} "
            f"(form {getattr(filing, 'form', None)!r}): {exc}"
        ),
        "error_class": "timeout",
        "retryable": True,
    }


def _version_drift_slot(item_id: str, filing, value) -> dict:
    """A loud, sentinel-compatible per-section error slot for a section whose
    successfully-thunked value is NOT the pinned-edgartools-5.42.0 ``str`` shape
    (Task 10) — a plausible post-upgrade API drift (a section accessor changed to
    return a structured object). DISTINCT from ``extraction_error`` (a throw) and
    the content gaps: here nothing raised, the value simply has an unexpected
    shape. Fail loud on the mismatch — the value's text is NEVER written out (no
    ``text_path``) — rather than emit possibly-wrong section text. The top-level
    ``error`` key is read unchanged by pack.py's ``_status``."""
    return {
        "item": item_id,
        "error": (
            f"section {item_id!r} for filing "
            f"{getattr(filing, 'accession_no', None)!r} "
            f"(form {getattr(filing, 'form', None)!r}) returned an unexpected "
            f"shape ({type(value).__name__}, expected str) — possible edgartools "
            f"version drift; refusing to emit possibly-wrong section text"
        ),
        "error_class": "version_drift",
    }


def _section_provenance(filing, document: str | None) -> dict:
    """The complete provenance tuple stamped on every SUCCESS section (Task 6):
    accession, cik, filingDate, period_of_report (where available), and a
    reconstructable SEC Archives ``url`` to ``document`` — the SECTION'S OWN
    source doc (the filing's primary doc for a 10-K/10-Q section, the sourced
    Exhibit 99.x for an 8-K section).

    Reconstructable WITHOUT an additional lookup: the URL is built from the same
    tuple fields (cik + accession-no-dashes + document). ``filingDate`` derives
    from the filing's disclosure date, never wall-clock (as_of invariant).
    ``period_of_report`` may be absent on some forms — passed through as-is
    (edgartools yields ``None`` there)."""
    accession = filing.accession_no
    return {
        "accession": accession,
        "cik": filing.cik,
        "filingDate": _filing_date_iso(filing.filing_date),
        "period_of_report": filing.period_of_report,
        "url": SEC_ARCHIVES_URL.format(
            cik_int=filing.cik,
            accession_nodash=_accession_nodash(accession),
            doc=document,
        ),
    }


# Any char outside the cache-key-safe set is collapsed to `_` so a sanitized
# item id (e.g. "Item 2.02") can never escape the sections dir (mirrors
# cache_util._UNSAFE_KEY_CHARS's path-safety contract).
_UNSAFE_ITEM_CHARS = re.compile(r"[^A-Za-z0-9_-]+")


def _section_text_path(accession: str, item_id: str) -> Path:
    """The deterministic per-(accession, item) file path for a section's text,
    under the toolkit cache dir: ``<cache>/sec_edgar/sections/<sanitized-
    accession>/<sanitized-item>.txt``.

    Keyed by disclosure identity (accession + item), NEVER wall-clock, so a
    re-run of the same section is byte-stable and re-uses the same file (as_of
    invariant). BOTH path segments — accession AND item id — are run through the
    ``[A-Za-z0-9_-]`` allowlist (defense in depth, CHK-SEC-004), so ``/``, ``.``,
    and ``..`` can never survive into either segment; neither can escape the
    ``sections`` dir. Real SEC accessions are digit-dash so the accession
    sanitization is a no-op on them (matching the provenance URL's
    ``_accession_nodash``), and only hardens against a crafted/malformed value."""
    accession_seg = _UNSAFE_ITEM_CHARS.sub("_", _accession_nodash(accession)) or "_"
    sanitized = _UNSAFE_ITEM_CHARS.sub("_", item_id) or "_"
    return (
        cache_util.resolve_cache_dir()
        / "sec_edgar"
        / "sections"
        / accession_seg
        / f"{sanitized}.txt"
    )


def _write_section_text(accession: str, item_id: str, text: str) -> str:
    """Write a section's extracted ``text`` to its deterministic per-(accession,
    item) file and return that path as a string — the section's ``text_path``.

    Paths-not-content (Task 7): the section body is file-backed, not inlined in
    the section dict / JSON result. Parent dir is created; the file lives
    strictly under the toolkit cache dir, never the repo tree.

    Structural traversal guard (CHK-SEC-004, belt-and-suspenders with the
    segment sanitization in ``_section_text_path``): the resolved target MUST be
    contained under the resolved cache dir, else fail loud — an explicit raise
    (not a bare ``assert`` that ``-O`` would strip), making an escape structurally
    impossible for ANY segment regardless of input."""
    cache_root = cache_util.resolve_cache_dir()
    path = _section_text_path(accession, item_id)
    resolved = path.resolve()
    if not resolved.is_relative_to(cache_root.resolve()):
        raise ValueError(
            f"refusing to write section text outside the cache dir: {resolved!r} "
            f"escapes {cache_root!r} (accession={accession!r}, item={item_id!r})"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def _build_section(item_id: str, text, filing, extra: dict | None = None) -> dict:
    """A success section when text is present, else a named absent-item error slot
    — never an empty or fabricated section.

    A success section is `{"item", "text_path", **extra, **provenance}`: the
    extracted body is written to a file and referenced by ``text_path``
    (paths-not-content, Task 7) rather than inlined. ``extra`` is the per-section
    extra merged in (8-K's `{"exhibit": ...}`, Task 4; empty/None for 10-K/10-Q),
    and ``provenance`` (Task 6) is the complete provenance tuple whose
    reconstructable URL targets the section's OWN source doc — the Exhibit 99.x
    for an 8-K (``extra["exhibit"]``), else the filing's primary doc."""
    if text is None or (isinstance(text, str) and not text.strip()):
        return _section_gap(item_id, filing)
    section = {
        "item": item_id,
        "text_path": _write_section_text(filing.accession_no, item_id, text),
        # disclosure_status (Task 9) defaults to "filed" — the legal status of a
        # 10-K/10-Q section — derived from the SOURCE TYPE, never read from
        # edgartools. The 8-K exhibit-following path overrides this to "furnished"
        # via its `extra` dict (merged below), the one source type that is
        # furnished rather than filed. GAP slots return above and never reach here.
        "disclosure_status": "filed",
    }
    if extra:
        section.update(extra)
    document = (extra or {}).get("exhibit") or _primary_document(filing)
    section.update(_section_provenance(filing, document))
    return section


def segment_filing(filing) -> list[dict]:
    """Segment a 10-K / 10-Q / 8-K filing into per-item section objects via
    edgartools' typed section API (``filing.obj()`` -> ``TenK`` / ``TenQ`` /
    ``CurrentReport``), NOT the retired regex ``parse_item_sections``.

    Pure data acquisition — NO analysis filtering: every item the primary
    document enumerates is emitted. Returns a LIST of section dicts (see the
    SECTION-OBJECT CONTRACT above):
      - 10-K / 10-Q -> one section per item in ``obj.items`` (the FULL body
        item set — e.g. a 10-K's Item 1..16 including Business + Financial
        Statements), each read via ``obj[item_id]``.
      - 8-K -> one section per reported item in ``obj.items``; an exhibit-
        bearing item (2.02/7.01/8.01) is sourced from its Exhibit 99.x
        (``disclosure_status: furnished``, exhibit filename in provenance),
        every other reported item from its own body text (``filed``).
    An enumerated item absent from THIS filing (edgartools returns ``None``,
    issue #710) becomes a per-section error slot naming the missing item, never
    an empty/fabricated section. An unregistered form fails loud (``ValueError``)
    rather than silently returning no sections.

    Fail-loud per-section isolation (Task 8): an extraction that RAISES never
    aborts the whole segmentation. A throw building `filing.obj()` or the
    extractor's entry list (the primary document cannot be fetched/parsed at all)
    turns the whole filing into a single loud form-level `extraction_error` slot
    (all-fail — the dynamic item set is unknowable once `obj()` itself fails);
    a throw evaluating ONE item's text-thunk turns just that item into an
    `extraction_error` slot while the other items still segment. The resulting
    list classifies through pack.py's `_status` as partial (some fail) / failed
    (all fail), never a fabricated/silent-empty section.

    Distinct failure classes (Task 10) carved out ABOVE the generic
    `extraction_error` (narrower-except-first): a TIMEOUT (builtin `TimeoutError`
    or edgartools' `httpx` timeout family — see `_TIMEOUT_EXC_TYPES`) in either
    handler becomes a distinct retryable `timeout` slot, never merged into a
    content gap; and a successfully-thunked section value that is not the expected
    `str` (a plausible post-upgrade edgartools shape) becomes a loud
    `version_drift` slot rather than possibly-wrong emitted text.
    """
    form = filing.form
    extractor = _ITEM_EXTRACTORS.get(form)
    if extractor is None:
        raise ValueError(
            f"segment_filing: no section extractor registered for form {form!r} "
            "(10-K/10-Q/8-K supported)"
        )
    try:
        obj = filing.obj()
        entries = list(extractor(obj, filing))
    except _TIMEOUT_EXC_TYPES as exc:  # noqa: BLE001 — timeout is its OWN retryable class
        # Wholesale TIMEOUT (Task 10): obj()/extractor build exceeded the timeout.
        # Every enumerated section becomes the DISTINCT retryable `timeout` slot,
        # NOT the generic extraction_error — narrower-except-first, above Exception.
        return _all_sections_failed(form, filing, exc, slot=_timeout_error_slot)
    except Exception as exc:  # noqa: BLE001 — fail loud per enumerated section, don't crash
        # Wholesale failure: obj() or extractor building threw, so no per-item
        # text-thunk was ever reached. Every enumerated section becomes a loud
        # extraction-error slot; no top-level success is claimed.
        return _all_sections_failed(form, filing, exc)
    sections = []
    for entry in entries:
        # An extractor may yield a ready-made section/gap dict for a gap it alone
        # can detect (8-K missing/ambiguous exhibit, Task 5); pass it through
        # unchanged. Otherwise it is a (item id, text_thunk[, extra]) tuple whose
        # text is resolved lazily HERE so a mid-parse throw is isolated to this
        # one item (Task 8).
        if isinstance(entry, dict):
            sections.append(entry)
            continue
        item_id, text_thunk = entry[0], entry[1]
        extra = entry[2] if len(entry) > 2 else None
        try:
            text = text_thunk()
        except _TIMEOUT_EXC_TYPES as exc:  # noqa: BLE001 — timeout is its OWN retryable class
            # Per-item TIMEOUT (Task 10): a DISTINCT retryable slot, carved above
            # the generic extraction_error (narrower-except-first) so a transient
            # timeout is never merged into a content gap; the other items still
            # segment.
            sections.append(_timeout_error_slot(item_id, filing, exc))
            continue
        except Exception as exc:  # noqa: BLE001 — isolate this item's throw
            sections.append(_extraction_error_slot(item_id, filing, exc))
            continue
        if text is not None and not isinstance(text, str):
            # Version-drift shape guard (Task 10): a successfully-thunked section
            # value must be the pinned-5.42.0 `str` (or None → absent-item gap in
            # `_build_section`). Any other shape is possible post-upgrade API drift
            # — fail loud on the mismatch, NEVER emit possibly-wrong section text.
            sections.append(_version_drift_slot(item_id, filing, text))
            continue
        sections.append(_build_section(item_id, text, filing, extra))
    return sections


def fetch_narrative_sections(accession: str) -> dict:
    """Cache-backed edgartools narrative-section fetch for an accession (the unit
    Task 12 wires into ``--action narrative``).

    Cache HIT — a warm accession within the immutable window — returns the cached
    section list WITHOUT re-hitting edgartools (SEC fair-access: never re-fetch
    what we already have). Cache MISS acquires the RAW edgartools Filing via the
    shared ``_acquire_raw_filing`` producer boundary — NOT ``acquire_filing``'s
    JSON ref dict, which would crash ``segment_filing`` (a dict has no ``.obj()``/
    ``.form``) — then segments it (``segment_filing``) and reads its contract
    metadata (cik/form/filingDate) off the same raw filing, caching the resulting
    section-list wrapper.

    The cache key derives from the disclosure IDENTITY (the accession), NEVER
    wall-clock, so a same-day re-run of the same accession is a HIT, not a
    double-fetch (as_of invariant). It is DISTINCT from the legacy regex
    ``fetch_narrative``'s ``narrative_{accession}`` key: the edgartools payload
    stores ``sections`` as a LIST of section dicts whereas the legacy payload
    stored it as a DICT (item->body), and both share the immutable TTL + envelope
    v2.0 — so a shared key would let a machine with a warm LEGACY entry get a
    schema-passing HIT of the WRONG shape (never self-healing under immutable TTL).
    The ``narrative_sections_`` prefix ensures the two caches can never alias.
    A failed acquisition is a loud ``{"error": ...}`` slot that is SURFACED, never
    cached as success — so a transient 429/403 that edgartools' own backoff could
    not recover from is not poisoned into the cache. This wrapper adds NO
    retry-defeating catch around the edgartools call: ``acquire_filing`` reaches
    edgartools directly, leaving its built-in ``pyrate-limiter``/``stamina``
    backoff authoritative (edgartools does its own HTTP over ``httpx``; the
    ``requests``-based ``_sec_get`` throttle does not cover this path).

    The returned wrapper carries its OWN extraction-health summary derived from
    the section list: ``narrative_status`` (``"ok"`` / ``"partial"`` / ``"failed"``
    — pack.py's vocabulary) and ``failed_items`` (the item ids whose section
    carries an ``error`` key; ``[]`` when healthy). This exists because the
    per-section fail-loud slots live INSIDE ``sections``: a downstream consumer
    that embeds this wrapper as a sub-field and inspects the whole thing (a
    classifier walking one level into dict-valued sub-fields) never reaches a
    LIST-nested error, so the partial/failed state would silently read as ``ok``.
    A downstream consumer therefore reads THIS summary rather than relying on a
    classifier walking into ``sections``. It is ADDITIVE (the 5 CLI contract keys
    accession/cik/form/filingDate/sections are unchanged) and is NOT a top-level
    ``error`` key — a partial extraction is not a wholesale acquisition failure,
    so exit-1-iff-``error`` stays unchanged. Both fields are cached alongside the
    rest, so a warm HIT carries them too.
    """
    path = cache_util.cache_path("sec_edgar", f"narrative_sections_{accession}")
    cached = cache_util.load_cache(path, TTL_NARRATIVE)
    if cached is not None:
        cached["_cache"] = "hit"
        return cached

    # Obtain the RAW edgartools Filing (NOT acquire_filing's JSON ref dict) so
    # segment_filing gets a real Filing (`.obj()`/`.form`) and the contract-key
    # reads below hit `.cik`/`.form`/`.filing_date` — a dict ref would crash both.
    filing = _acquire_raw_filing(accession)
    if isinstance(filing, dict):  # a loud error slot (never a raw Filing)
        # Loud acquisition failure (e.g. a 429/403 that escaped edgartools' own
        # backoff) — surface it; do NOT segment, do NOT cache it as success.
        return filing

    sections = segment_filing(filing)
    # Extraction-health summary carried ON THE WRAPPER (review 🟡): the
    # per-section fail-loud slots live inside `sections`, so a consumer that
    # inspects the whole wrapper as one dict sub-field (e.g. the future memo
    # pipeline embedding this result) never reaches them — a one-level classifier
    # only walks a dict's dict-valued sub-fields, and `sections` is a LIST. Derive
    # the partial/failed state HERE from the section list (NO pack.py import — data
    # layer must not depend on the report-equity-memo facade) and surface it as
    # top-level, non-`_`-prefixed fields so the failure state travels WITH the
    # wrapper: `narrative_status` (ok/partial/failed, pack.py's vocabulary) plus
    # `failed_items` naming each erroring item id. A downstream consumer reads THIS
    # summary rather than relying on a classifier walking into `sections`.
    failed_items = [s["item"] for s in sections if "error" in s]
    if not failed_items:
        narrative_status = "ok"
    elif len(failed_items) == len(sections):
        narrative_status = "failed"
    else:
        narrative_status = "partial"
    result = {
        "accession": accession,
        # Contract keys the CLI `--action narrative` surface preserves
        # (Task 12): cik/form/filingDate derived from the RAW filing's disclosure
        # identity (NEVER wall-clock), and STORED in the cached payload so a
        # warm-cache HIT carries them too — otherwise a warm run would be missing
        # contract keys.
        "cik": filing.cik,
        "form": filing.form,
        "filingDate": _filing_date_iso(filing.filing_date),
        "sections": sections,
        "section_count": len(sections),
        # Additive extraction-health summary (cached alongside the rest → present
        # on HIT + MISS). NOT a top-level `error` key: a partial extraction is not
        # a wholesale acquisition failure, so exit-1-iff-error is unchanged.
        "narrative_status": narrative_status,
        "failed_items": failed_items,
        "_cache": "miss",
    }
    cache_util.save_cache(path, result)
    return result


def action_narrative(accession: str) -> dict:
    identity_error = _ensure_edgar_identity()
    if identity_error is not None:
        identity_error["action"] = "narrative"
        return identity_error
    _log("narrative fetch", accession)
    t0 = time.monotonic()
    res = fetch_narrative_sections(accession)
    res["action"] = "narrative"
    cache_label = "cache hit" if res.get("_cache") == "hit" else f"{res.get('section_count', 0)} sections in {time.monotonic() - t0:.1f}s"
    _log("narrative done", f"{accession} {cache_label}")
    return res


# ---------------------------------------------------------------------------
# Route B: 8-K earnings-exhibit RAW acquisition (edgartools `filing.attachments`)
# ---------------------------------------------------------------------------
# A DISTINCT acquisition path from `_segment_8k`/`fetch_narrative_sections`: it
# grabs the WHOLE EX-99.x exhibit document's RAW HTML (`attachment.content`), not
# the per-item flattened `.text()` the narrative path produces — a downstream
# table walker (exhibit_tables.py) needs the raw <table> DOM, which the flattened
# text destroys. Going via `filing.attachments` also sidesteps `_segment_8k`'s
# LOOM-SIMPLIFY >=2-exhibit-item gap ceiling: enumerating every EX-99.x
# attachment has no per-item->exhibit pairing to be ambiguous about (the spike
# 2026-07-19 confirmed the ceiling trips on real NFLX acc 0001065280-25-000033
# under the old path; this path returns both exhibits cleanly).
#
# Live-grounded shape (edgartools 5.42.0, probed 2026-07-19): `filing.attachments`
# is iterable, yielding `Attachment` objects carrying `document` (filename) /
# `document_type` (e.g. "EX-99.1") / `size` etc., with `content` a PROPERTY that
# downloads + returns the raw document. The Route B spike read
# `filing.attachments -> the EX-99.1 attachment -> .content` (429,234 chars of
# raw HTML) — see scratchpad/route-b-inventory-spike.md.


def _is_ex99_attachment(document_type) -> bool:
    """True iff an attachment's ``document_type`` marks it an EX-99.x exhibit
    (the press-release / earnings-letter family Route B extracts). Normalizes
    case + interior spaces so "EX-99.1" / "ex-99.2" / "EX-99" all match, while a
    non-exhibit attachment (the primary "8-K" body doc, a "GRAPHIC") is filtered
    out."""
    if not document_type:
        return False
    return str(document_type).upper().replace(" ", "").startswith("EX-99")


def _resolve_latest_earnings_8k_accession(ticker: str) -> str | dict:
    """Resolve the ticker's LATEST earnings 8-K (Item 2.02) accession, reusing
    the shipped primitives: ``resolve_cik`` -> ``list_filings`` (over a
    policy-sufficient DATE window, never a magic row count) -> the established
    ``_has_item_code(..., "2.02")`` earnings-8-K membership check, then the most
    recent by ``filingDate``.

    "Latest earnings 8-K" is a recency pick over item-2.02 8-Ks, NOT the
    quarter-anchored per-quarter selection ``select_narrative_filings`` does (that
    would reject a valid recent earnings 8-K merely because it is not in the
    current calendar quarter). Returns the accession string on success, or a loud
    ``{"error": ...}`` slot (never a silent None) when the ticker does not resolve
    or no earnings 8-K exists inside the lookup window — mirroring
    ``acquire_filing``'s resolution / form_unavailable error classes."""
    cik_result = resolve_cik(ticker)
    if "error" in cik_result:
        return _acquire_error(
            "resolution",
            f"ticker {ticker!r} did not resolve to a registered SEC filer "
            f"({cik_result['error']})",
            identifier=ticker,
        )
    cik = cik_result["cik"]
    window_days = narrative_filings_window_days(n_quarters=1)
    min_filing_date = (date.today() - timedelta(days=window_days)).isoformat()
    # `min_filing_date` (a DATE cutoff) is the real stop condition; the 100 is a
    # generous count ceiling only (list_filings scans to the array end when a
    # min_filing_date is given — see its docstring).
    rows = list_filings(cik, ["8-K"], 100, min_filing_date=min_filing_date)
    earnings = [r for r in rows if _has_item_code(r.get("items"), "2.02")]
    if not earnings:
        return _acquire_error(
            "form_unavailable",
            f"no earnings 8-K (item 2.02) found for ticker {ticker!r} within the "
            f"lookup window ({min_filing_date}..)",
            identifier=ticker,
            form="8-K",
        )
    latest = max(earnings, key=lambda r: r.get("filingDate") or "")
    return latest["accessionNumber"]


def fetch_exhibit_documents(ticker: str, accession: str | None = None) -> dict:
    """Acquire the RAW EX-99.x exhibit documents of an earnings 8-K.

    Resolution: when ``accession`` is given, that filing is fetched directly (via
    the shared ``_acquire_raw_filing`` producer boundary); when it is ``None``,
    the ticker's LATEST earnings 8-K (Item 2.02) is resolved first
    (``_resolve_latest_earnings_8k_accession``). Either way, ALL EX-99.*
    attachments are enumerated off ``filing.attachments`` and each document's RAW
    HTML (``attachment.content``) + metadata (accession / document / exhibit_type
    / filingDate) is returned.

    Cache: each document is cached under the NEW key family
    ``exhibit_raw_{accession}_{document}`` — NEVER the legacy
    ``narrative_sections_{accession}`` slot. The two payload shapes are
    incompatible (this path stores raw exhibit HTML per document; the narrative
    path stores a section list) and both share the immutable TTL, so a shared key
    would let a pre-warmed machine get a schema-passing HIT of the WRONG shape
    that never self-heals (cache-key-collision-across-migration). The distinct
    ``exhibit_raw_`` prefix makes the two caches un-aliasable. A cache HIT on a
    document's key skips re-downloading that exhibit's bytes (SEC fair-access);
    the filing itself is still resolved once to enumerate which exhibits exist.

    A failed resolution/acquisition is a loud ``{"error": ...}`` slot that is
    SURFACED, never cached — a transient 429/403 is not poisoned into the cache."""
    if accession is None:
        accession = _resolve_latest_earnings_8k_accession(ticker)
        if isinstance(accession, dict):  # a loud error slot (never an accession)
            return accession

    filing = _acquire_raw_filing(accession)
    if isinstance(filing, dict):  # a loud error slot (never a raw Filing)
        return filing

    resolved_accession = filing.accession_no
    filing_date = _filing_date_iso(filing.filing_date)

    documents: list[dict] = []
    for attachment in filing.attachments:
        if not _is_ex99_attachment(getattr(attachment, "document_type", None)):
            continue
        document = attachment.document
        path = cache_util.cache_path(
            "sec_edgar", f"exhibit_raw_{resolved_accession}_{document}"
        )
        cached = cache_util.load_cache(path, TTL_EXHIBIT_RAW)
        if cached is not None:
            cached["_cache"] = "hit"
            documents.append(cached)
            continue
        doc = {
            "accession": resolved_accession,
            "document": document,
            "exhibit_type": attachment.document_type,
            "filingDate": filing_date,
            "raw_html": attachment.content,
        }
        cache_util.save_cache(path, doc)
        documents.append({**doc, "_cache": "miss"})

    return {
        "accession": resolved_accession,
        "ticker": ticker,
        "cik": filing.cik,
        "form": filing.form,
        "filingDate": filing_date,
        "documents": documents,
        "document_count": len(documents),
    }


# ---------------------------------------------------------------------------
# Source A: statement-cell extraction (edgartools XBRL statement API)
# ---------------------------------------------------------------------------
# Live shape captured 2026-07-13 (AAPL FY2025 10-K, accession
# 0000320193-25-000079; anchored by test_data_markets_live.py
# ::test_extract_statement_cells_live_shape):
#   filing.xbrl().get_statement(name) -> list[dict] of RENDERED rows, one per
#     line item, in table row order; each row carries `concept` (underscore
#     form, e.g. "us-gaap_CashAndCashEquivalentsAtCarryingValue") and
#     `values`/`decimals` dicts keyed by a `period_key` (e.g.
#     "instant_2025-09-27"). Raises `StatementNotFound` on an absent/
#     unrecognized statement (Task 2 wraps this; not handled here).
#   filing.xbrl().facts.to_dataframe() -> per-CELL fact table (~1044x55 for
#     an AAPL 10-K); columns read here: `concept` (COLON form, e.g.
#     "us-gaap:CashAndCashEquivalentsAtCarryingValue"), `statement_type`
#     (matches the `get_statement` name argument verbatim, e.g.
#     "BalanceSheet"), `context_ref`/`fact_id` (citation), `value` (str) /
#     `numeric_value` (float) / `decimals` (str), `period_type`
#     ("instant"|"duration") + `period_instant`/`period_start`/`period_end`,
#     `period_key` (the join key back to a rendered row's `values`/`decimals`
#     dict — reused here as the cell's `col`), `is_dimensioned` (bool) +
#     `dimension`/`member` (colon form, e.g. "srt:ProductOrServiceAxis" /
#     "aapl:IPhoneMember"), `label`. A live probe found every BalanceSheet
#     fact's colon-concept, with `:` -> `_`, resolves to a `get_statement` row
#     (0/154 misses) — the join this extractor relies on.
# DEAD TRAPS (NOT-EXPOSED on 5.42.0) — do NOT use: filing.xbrl().instance,
# Company(...).financials (returns None).


def _is_nan(value: object) -> bool:
    """True for a pandas/NumPy float NaN (the fact-table's null marker) —
    NaN is the only float that is not equal to itself, so this needs neither
    a ``math`` nor a ``pandas`` import."""
    return isinstance(value, float) and value != value


def _statement_row_index(rendered_rows: list[dict]) -> dict[str, int]:
    """Map each rendered row's underscore-form `concept` to its FIRST row
    index in `get_statement`'s row-ordered list — the doc-table's own row
    position, reused as a cell citation's `row`."""
    index: dict[str, int] = {}
    for i, row in enumerate(rendered_rows):
        index.setdefault(row.get("concept"), i)
    return index


def _statement_extraction_error_slot(statement_name: str, filing, exc: BaseException) -> dict:
    """A loud, sentinel-compatible extraction-failure slot for a statement whose
    `get_statement` call RAISED (Task 2) — e.g. edgartools' `StatementNotFound`
    on a pre-XBRL filing or an unrecognized/unparseable statement variant.
    Mirrors this file's existing per-item error-slot convention
    (`_extraction_error_slot`/`_acquire_error`): the failure is returned as a
    typed dict the caller can branch on (`isinstance(result, dict)`, same
    discriminator `_acquire_raw_filing`'s callers use) — never raised further
    uncaught, and never masked by an LLM-guessed or regex/free-text-scraped
    fallback cell value."""
    return {
        "statement_name": statement_name,
        "error": (
            f"statement {statement_name!r} extraction failed for filing "
            f"{getattr(filing, 'accession_no', None)!r}: {exc}"
        ),
        "error_class": "statement_not_found",
    }


def extract_statement_cells(filing, statement_name: str) -> list[dict] | dict:
    """Extract a primary financial-statement table's cells from a filing's
    REAL XBRL statement data — NEVER free-text / regex the document body.

    Combines two edgartools 5.42.0 surfaces (see the module-header shape
    note above): `get_statement(statement_name)` for the rendered row order
    (a cell's table `row` position) and `facts.to_dataframe()` filtered to
    `statement_type == statement_name` for the per-cell fact graph (the
    numeric value + full citation, incl. `context_ref`/`fact_id`). A fact
    with no reported numeric value (e.g. a placeholder concept such as
    `CommitmentsAndContingencies`, live-observed on this filing) is not a
    doc-table cell with a number to compare — skipped, never fabricated as
    0/None.

    Returns a list of cells in the declared Source-A schema (plan
    docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md Notes
    §Declared schemas) on success:
      {concept, period:{type, instant?|start?+end?}, dimension:null|{axis,
       member}, value_displayed, numeric_value, decimals, citation:
       {accession, statement_name, row, col, label, context_ref, fact_id}}

    Task 2: when the filing/statement variant has no XBRL-backed statement
    (pre-XBRL filing, or a statement edgartools cannot parse — surfaces as
    `StatementNotFound`), `get_statement`'s exception is caught here and
    converted into a loud `_statement_extraction_error_slot` dict — NEVER
    left to propagate uncaught, and NEVER papered over with a regex-scraped
    or LLM-guessed cell value. Callers discriminate success vs failure the
    same way `_acquire_raw_filing`'s callers do: `isinstance(result, dict)`
    (success is always a `list`, failure is always a `dict`).

    A fact whose concept does NOT resolve to a rendered `get_statement` row
    (empirically 0/152 on the AAPL fixture, but this extractor is reused
    across other statements/filers) is not silently dropped to
    `citation.row: None` — the miss is logged via `_log` (module-level
    stderr helper) naming the orphaned concept, so a future join gap is
    visible rather than a silent citation degradation. The emitted cell
    schema is unchanged either way (`row` may still be `None`).

    Filtering + record conversion happens here (the only spot that touches
    the pandas-shaped `facts.to_dataframe()`); the actual cell-building
    logic lives in `_build_statement_cells`, which operates on plain dict
    records and is offline-unit-testable without pandas or edgartools
    installed (see tests/data/test_sec_xval.py).
    """
    xb = filing.xbrl()
    try:
        rendered_rows = xb.get_statement(statement_name)
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape; never a scrape fallback
        return _statement_extraction_error_slot(statement_name, filing, exc)
    row_index = _statement_row_index(rendered_rows)

    facts_records = xb.facts.to_dataframe().to_dict("records")
    statement_facts = [
        fact for fact in facts_records if fact.get("statement_type") == statement_name
    ]

    return _build_statement_cells(
        statement_facts, row_index, filing.accession_no, statement_name
    )


def _build_statement_cells(
    statement_facts: list[dict],
    row_index: dict[str, int],
    accession: str,
    statement_name: str,
) -> list[dict]:
    """Pure cell-building logic for `extract_statement_cells`: NaN-skip,
    instant/duration period branching, dimension building, row/col citation
    join. Operates on plain dict records (already filtered to
    `statement_name`, already off of pandas) — no pandas/edgartools import
    needed to exercise this, which is what makes it offline-unit-testable
    (tests/data/test_sec_xval.py)."""
    cells: list[dict] = []
    for fact in statement_facts:
        if _is_nan(fact.get("numeric_value")):
            continue  # placeholder concept, no reported number — never fabricate one

        concept = fact["concept"]
        row_key = concept.replace(":", "_")
        row = row_index.get(row_key)
        if row is None:
            _log(
                "row index miss",
                f"{concept} (statement={statement_name!r}) has no matching "
                f"get_statement row — citation.row will be None",
            )

        if fact["period_type"] == "instant":
            period = {"type": "instant", "instant": fact.get("period_instant")}
        else:
            period = {
                "type": "duration",
                "start": fact.get("period_start"),
                "end": fact.get("period_end"),
            }

        dimension = (
            {"axis": fact.get("dimension"), "member": fact.get("member")}
            if fact.get("is_dimensioned")
            else None
        )

        cells.append({
            "concept": concept,
            "period": period,
            "dimension": dimension,
            "value_displayed": fact.get("value"),
            "numeric_value": float(fact["numeric_value"]),
            "decimals": str(fact.get("decimals")),
            "citation": {
                "accession": accession,
                "statement_name": statement_name,
                "row": row,
                "col": fact.get("period_key"),
                "label": fact.get("label"),
                "context_ref": fact.get("context_ref"),
                "fact_id": fact.get("fact_id"),
            },
        })
    return cells


# ---------------------------------------------------------------------------
# Dimensional-revenue fact-pack extractor (Task 5, operational-kpi tier-②
# XBRL pilot — docs/loom/plans/2026-07-14-operational-kpi-companyfacts-pilot.md)
# ---------------------------------------------------------------------------
# The Apple false-negative lesson (plan Task 5, grounding the axis-namespace
# set below): Apple's product-line dimension moved from
# us-gaap:ProductOrServiceAxis (pre-2018) to srt:ProductOrServiceAxis
# (post-2018) across the 2018 revenue-recognition tagging-regime shift —
# filtering a single namespace silently drops half the fact's history.
_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES = {
    "ProductOrServiceAxis",
    "StatementBusinessSegmentsAxis",
    "StatementGeographicalAxis",
    "SubsegmentsAxis",
}

# srt:ConsolidationItemsAxis is a reconciliation QUALIFIER (e.g.
# "OperatingSegmentsMember" disambiguating a segment total from a
# consolidating-adjustments view), never a breakdown axis — captured
# separately as `consolidation`, never folded into `dimensions`.
#
# srt:ConsolidatedEntitiesAxis is a SIBLING spelling of the SAME
# consolidation-qualifier semantics (live-sweep regression, real INTC pack:
# 2021-2023-era filings tag segment revenue facts with
# `srt:ConsolidatedEntitiesAxis = OperatingSegmentsMember` — the identical
# default member ConsolidationItemsAxis uses, per kpi_xbrl.py's
# `_normalize_consolidation`). Both local names fold into the SAME
# `consolidation` slot — never `dimensions`, never excluded as unknown.
# When a fact carries BOTH with the SAME member, that is one value; with
# DIFFERING members, that is genuinely ambiguous and the whole fact is
# excluded (`_dimension_signature`'s "consolidation_conflict" category).
_CONSOLIDATION_AXIS_LOCAL_NAMES = (
    "ConsolidationItemsAxis",
    "ConsolidatedEntitiesAxis",
)

# srt:RestatementAxis (any member, matched namespace-agnostically like
# `_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES` — the same Apple false-negative
# lesson applies) tags a prior-period reclassification/restatement
# adjustment vintage, never a real breakdown axis and never the current
# period's bindable value (Task 1, docs/loom/plans/2026-07-19-jnj-
# restatement-axis-signature.md — XBRL US guidance: the default,
# axis-absent member IS the restated current value). A fact carrying this
# axis is EXCLUDED from `dimensions`/the pack's primary facts entirely and
# counted as the named "vintage" category in `_dimension_signature`'s
# `exclusions` — never silently collapsed onto the default signature.
_VINTAGE_AXIS_LOCAL_NAME = "RestatementAxis"


def _is_dimensional_revenue_axis(axis: str | None) -> bool:
    """True when `axis` (colon form, e.g. "srt:ProductOrServiceAxis") is one
    of the four axis local names, REGARDLESS of its `us-gaap:`/`srt:`
    namespace prefix — see the module note above: never filter a single
    namespace."""
    if not axis:
        return False
    return axis.rsplit(":", 1)[-1] in _DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES


# ALLOW: legitimate non-RFCC operating-revenue concept local names (Task 2,
# docs/loom/plans/2026-07-16-operational-kpi-quarterly.md — "Revenue-concept
# matching is an allow/deny + $-unit gate, not a substring"). Checked BEFORE
# the deny-list so a future deny pattern can never accidentally swallow one
# of these named-safe concepts. `RevenueFromContractWithCustomer*` (the
# ASC-606 standard concept family) is NOT listed here — it already passes
# the general "Revenue"-substring path below and hits no deny pattern.
# Sources: docs/loom/references/xbrl-verification-universe.md (Filter-bug
# findings + Special-condition index, live-verified 2026-07-16/17).
_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES = (
    "Revenues",
    "RevenuesNetOfInterestExpense",                              # banks (JPM/BAC/WFC/C)
    "RevenueNotFromContractWithCustomer",                        # energy/utilities (SO/COP)
    "RevenueNotFromContractWithCustomerExcludingInterestIncome",  # XOM's exact tag
    "RevenueFromContractWithCustomerIncludingAssessedTax",       # utilities (NEE/DUK/SO/DOW)
)

# DENY: `*Revenue*`-substring concepts that are NOT operating revenue (Task 2
# plan/spec). Substring (not prefix) matching — WFC's
# `OtherCostOfOperatingRevenue` has the "Operating" infix that defeats a
# literal "CostOfRevenue" prefix/substring check, so the deny key is the
# narrower "CostOf" fragment. Live-verified real concepts each pattern
# catches (docs/loom/references/xbrl-verification-universe.md, Filter-bug
# findings section + 2026-07-17 spot-checks):
#   CostOf                    -> CostOfRevenue (CAT), OtherCostOfOperatingRevenue (WFC)
#   Percent                   -> *Percentage / *ChangePercent ratio concepts (BA/HON/AMAT)
#   RemainingPerformanceObligation -> RPO/backlog disclosure (widespread)
#   DeferredRevenue           -> deferred-revenue liability concepts (SBUX/BLK)
#   ContractWithCustomerLiability -> contract-liability reconciliation items (pre-existing exclusion, generalized)
#   CollaborativeArrangement  -> non-operating collaborative-arrangement revenue (PFE/MRK)
#   ProForma                  -> class 6 REIT M&A pro-forma revenue: O's
#                                 us-gaap:BusinessAcquisitionsProFormaRevenue
#                                 (10-K 0000726728-26-000011) and
#                                 o:AssetAcquisitionProFormaInformationRevenue...
#                                 — HYPOTHETICAL revenue as if an acquisition
#                                 had closed at period start; admitting it
#                                 double-counts against actual revenue.
#   NetIncreaseDecreaseToRentalRevenue -> class 6 REIT lease-ladder schedule:
#                                 PLD's pld:NetIncreaseDecreaseToRentalRevenue*
#                                 family (10-K 0001193125-26-051453) — a
#                                 forward-looking roll-forward figure, not
#                                 recognized revenue. Deliberately the LONGER
#                                 fragment (not bare "RentalRevenue") so the
#                                 real pld:RentalRevenue concept stays allowed.
_REVENUE_DENY_SUBSTRINGS = (
    "CostOf",
    "Percent",
    "RemainingPerformanceObligation",
    "DeferredRevenue",
    "ContractWithCustomerLiability",
    "CollaborativeArrangement",
    "ProForma",
    "NetIncreaseDecreaseToRentalRevenue",
)


def _is_revenue_concept(concept: str | None) -> bool:
    """True when `concept` is real operating revenue — an ALLOW/DENY gate
    (Task 2, docs/loom/plans/2026-07-16-operational-kpi-quarterly.md;
    folds a scope-A/2.21.0 correctness defect), NOT the old shipped
    substring test (`"Revenue" in local_name`) that admitted dimensioned
    `CostOfRevenue` as revenue (CAT: 20 bogus facts, live-reproduced),
    percentage-valued `*RevenuePercentage` concepts as if they were dollar
    amounts (BA/HON), and RemainingPerformanceObligation / deferred-revenue
    liability concepts as earned revenue (SBUX).

    Algorithm: (1) an explicit ALLOW of named legitimate non-RFCC concepts
    (`_REVENUE_ALLOW_CONCEPT_LOCAL_NAMES`) short-circuits True; (2) local
    name must contain "Revenue" at all (rejects `CostOfGoodsSold` etc.);
    (3) a DENY substring (`_REVENUE_DENY_SUBSTRINGS`) rejects the known
    false-positive classes. This stays generalizable to unenumerable
    company-extension revenue concepts (e.g. `us-gaap:AdvertisingRevenue`,
    `nflx:*`) via step (2)'s general pass — an exhaustive allow-list alone
    cannot cover every filer's extension taxonomy.

    NOTE: this checks the CONCEPT NAME only — it cannot see the fact's
    XBRL unit. The $-unit guard (`_is_currency_amount_fact`) is a SEPARATE
    check applied at the full-fact layer in `_is_dimensional_revenue_fact`,
    because a percentage-valued concept's local name still legitimately
    contains "Revenue" (e.g. HON's
    `RevenueFromContractWithCustomerPercentage`) and is not reliably
    distinguishable by name alone."""
    if not concept:
        return False
    local_name = concept.rsplit(":", 1)[-1]
    if local_name in _REVENUE_ALLOW_CONCEPT_LOCAL_NAMES:
        return True
    if "Revenue" not in local_name:
        return False
    return not any(deny in local_name for deny in _REVENUE_DENY_SUBSTRINGS)


def _is_currency_amount_fact(fact: dict) -> bool:
    """$-unit guard (Task 2, docs/loom/plans/2026-07-16-operational-kpi-
    quarterly.md — 'a $-UNIT guard that rejects any fact whose XBRL unit is
    not a currency amount'): True only when `fact`'s XBRL unit is a currency
    amount, never a percentage/ratio. edgartools' `facts.to_dataframe()`
    carries a `currency` column (an ISO code, e.g. "USD") populated for a
    currency-unit fact and None/NaN for a percentage/ratio fact tagged
    `unit_ref="number"`/"pure" — live-verified 2026-07-17: BA's
    `ba:RevenuefromContractwithCustomerexcludingassessedtaxPercentage`
    (unit_ref="number", currency=None, value=1.0 i.e. 100%) vs
    `us-gaap:CostOfRevenue` / `us-gaap:RevenueNotFromContractWithCustomer...`
    (unit_ref="usd", currency="USD").

    Fail-closed (docs/loom/memory/fail-closed-default-must-be-enforced-not-
    emergent.md): a missing/NaN/empty currency is treated as NOT a currency
    fact — an explicit check, never an emergent side effect of a later
    numeric comparison."""
    currency = fact.get("currency")
    if currency is None or _is_nan(currency):
        return False
    return bool(str(currency).strip())


def _dimensional_revenue_error_slot(ticker: str, form: str, detail: str) -> dict:
    """A loud, sentinel-compatible error slot for
    `extract_dimensional_revenue` (mirrors this file's `_acquire_error`/
    `_companyfacts_pack_error_slot` convention) — never a fabricated/empty
    fact-pack."""
    return {
        "error": (
            f"SEC EDGAR dimensional-revenue extraction failed for "
            f"{ticker!r} ({form}): {detail}"
        ),
        "error_class": "dimensional_revenue_extraction_failed",
        "identifier": ticker,
    }


_FOREIGN_PRIVATE_ISSUER_ANNUAL_FORM = "20-F"
_FOREIGN_PRIVATE_ISSUER_INTERIM_FORMS = ("6-K", "6-K/A")


def _foreign_private_issuer_no_quarterly_reason(cik: int, form: str) -> str | None:
    """Detect the ADR/foreign-private-issuer 20-F+6-K filing regime from
    `cik`'s REAL submissions form histogram (`fetch_submissions` — the SEC
    submissions REST API's `filings.recent.form` array), never a hardcoded
    ticker list (a hardcoded list is a fabrication risk and rots — Task 4,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md). Live-verified
    2026-07-17 against TSM (CIK 1046179): 15x 20-F + 750x 6-K + 6x 6-K/A,
    ZERO 10-Q/10-K anywhere in the 1002-row recent window.

    Returns a reason string only when `form` is ABSENT from the histogram
    AND the histogram carries the annual FPI form (20-F) AND at least one
    interim FPI form (6-K/6-K-A) — the permanent regime signature the spec
    names, distinct from a merely-transient form gap. Returns None when the
    signature does not match (never guessed) or submissions can't be read."""
    sub = fetch_submissions(cik)
    if not isinstance(sub, dict) or "error" in sub:
        return None
    forms = set(
        sub.get("data", {}).get("filings", {}).get("recent", {}).get("form", [])
    )
    if form in forms:
        return None
    if _FOREIGN_PRIVATE_ISSUER_ANNUAL_FORM not in forms:
        return None
    if not any(f in forms for f in _FOREIGN_PRIVATE_ISSUER_INTERIM_FORMS):
        return None
    return (
        "no quarterly XBRL (foreign 20-F/6-K regime) — submissions history "
        f"shows {_FOREIGN_PRIVATE_ISSUER_ANNUAL_FORM} + 6-K filings, "
        f"no {form!r}"
    )


def _foreign_private_issuer_na_slot(ticker: str, form: str, reason: str) -> dict:
    """An explicit, loud N/A slot for the foreign-private-issuer 20-F/6-K
    regime (spec: docs/loom/2026-07-16-operational-kpi-quarterly/specs/
    operational-kpi-quarterly/spec.md — 'A foreign/ADR filer with no 10-Q is
    detected and returned N/A, never silently empty'). Carries its own
    DISTINCT `error_class` (`foreign_private_issuer_no_quarterly_xbrl`) —
    never the generic `dimensional_revenue_extraction_failed` used for
    fetch errors and out-of-range requests — plus a `reason` string.

    CONTRACT (corrected — see docs/loom/memory/fail-closed-default-must-
    be-enforced-not-emergent.md): this slot deliberately omits the
    `facts` key, but that omission is NOT a structural guarantee by
    itself. A caller that reads `fact_pack.get("facts", [])` (a `.get()`
    WITH A DEFAULT — e.g. `investing-toolkit/skills/analysis-kpi/scripts/
    kpi_xbrl.py:169,254`) does NOT raise on a missing key; it silently
    treats this slot as a real empty series, which is exactly the
    silent-empty failure this slot exists to prevent. The safety
    property is EMERGENT on the consumer's access pattern, not enforced
    by this shape. Every caller MUST branch on `error_class ==
    "foreign_private_issuer_no_quarterly_xbrl"` (or at minimum check for
    the `"error"` key) BEFORE reading `facts` — never assume the absent
    key alone will fail loud."""
    return {
        "error": (
            f"SEC EDGAR dimensional-revenue extraction failed for "
            f"{ticker!r} ({form}): {reason}"
        ),
        "error_class": "foreign_private_issuer_no_quarterly_xbrl",
        "identifier": ticker,
        "reason": reason,
    }


def _dimension_signature(
    fact: dict,
) -> tuple[dict[str, str], str | None, list[dict]]:
    """Build (dimensions, consolidation, exclusions) from `fact`'s per-row
    `dim_<namespace>_<AxisLocalName>` columns — e.g. `dim_srt_ProductOrServiceAxis`,
    `dim_us-gaap_StatementBusinessSegmentsAxis` — NEVER from the singular
    `dimension`/`member` convenience columns (the wrong-layer trap: those
    expose only ONE axis per fact). A single row/context routinely carries
    MULTIPLE populated `dim_<axis>` columns at once — live-verified
    2026-07-15 on a real NFLX 10-K row: `dim_srt_ProductOrServiceAxis`
    ("nflx:StreamingMember") AND `dim_srt_StatementGeographicalAxis`
    ("nflx:UnitedStatesAndCanadaMember") both populated on the SAME row.

    `dimensions` collects only the REAL breakdown axes
    (`_DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES`, matching BOTH `us-gaap:`/`srt:`
    namespaces via `_is_dimensional_revenue_axis` — the Apple false-negative
    lesson applies here too), keyed by the axis local name with the trailing
    "Axis" dropped (e.g. "ProductOrService"), valued by the member's local
    name (namespace prefix stripped). `srt:ConsolidationItemsAxis` and its
    sibling `srt:ConsolidatedEntitiesAxis` (`_CONSOLIDATION_AXIS_LOCAL_NAMES`
    — live-sweep INTC regression) are reconciliation QUALIFIERS, not a
    breakdown axis — captured separately as `consolidation`, never folded
    into `dimensions` as a second axis. When BOTH are present on the same
    row with the SAME member, that is one value; with DIFFERING members,
    that is genuinely ambiguous and reported via `exclusions` (category
    "consolidation_conflict") instead of guessing which one wins.

    `exclusions` (Task 1, docs/loom/plans/2026-07-19-jnj-restatement-axis-
    signature.md — kills the prior silent fall-through) lists, IN ORDER,
    every OTHER `dim_` axis on this row that is neither a whitelisted
    breakdown axis nor a consolidation qualifier — each entry
    `{"category": "vintage"|"unknown", "axis": "<namespace>:<AxisLocalName>",
    "member": <member local name>}`. `"vintage"` is `_VINTAGE_AXIS_LOCAL_NAME`
    (`srt:RestatementAxis`, any member, namespace-agnostic); everything else
    is `"unknown"` — fail-closed toward exclusion, never toward silent
    collision (docs/loom/memory/shared-classifier-over-open-dialects-needs-
    allowlist.md: the JNJ sweep proves only RestatementAxis collided, not
    that no sibling dialect exists). A conflicting pair of consolidation
    axes gets its own `{"category": "consolidation_conflict", "axis":
    "<ns:AxisLocalName>,<ns:AxisLocalName>" (sorted), "member":
    "<member>,<member>" (same order)}` entry — self-describing rather than
    folded into "unknown", since it IS a recognized qualifier axis, just an
    ambiguous one. A NON-EMPTY `exclusions` means the caller must exclude
    the WHOLE fact from primary output — a disallowed axis is never just
    dropped while `dimensions` stays populated from the fact's OTHER
    (allowed) axes, which is exactly how a restatement/reclassification
    pair used to collide onto the real quarter fact's signature (see
    `_is_dimensional_revenue_fact`)."""
    dimensions: dict[str, str] = {}
    consolidation_matches: list[tuple[str, str, str]] = []
    exclusions: list[dict] = []
    for key, value in fact.items():
        if not key.startswith("dim_") or value is None or _is_nan(value):
            continue
        _prefix, namespace, axis_local = key.split("_", 2)
        member_local = str(value).rsplit(":", 1)[-1]
        if axis_local in _CONSOLIDATION_AXIS_LOCAL_NAMES:
            consolidation_matches.append((namespace, axis_local, member_local))
        elif _is_dimensional_revenue_axis(f"{namespace}:{axis_local}"):
            dimensions[axis_local[: -len("Axis")]] = member_local
        elif axis_local == _VINTAGE_AXIS_LOCAL_NAME:
            exclusions.append({
                "category": "vintage",
                "axis": f"{namespace}:{axis_local}",
                "member": member_local,
            })
        else:
            exclusions.append({
                "category": "unknown",
                "axis": f"{namespace}:{axis_local}",
                "member": member_local,
            })

    consolidation: str | None = None
    if consolidation_matches:
        members = {member for _ns, _al, member in consolidation_matches}
        if len(members) == 1:
            consolidation = next(iter(members))
        else:
            ordered = sorted(consolidation_matches, key=lambda m: (m[0], m[1]))
            exclusions.append({
                "category": "consolidation_conflict",
                "axis": ",".join(f"{ns}:{al}" for ns, al, _m in ordered),
                "member": ",".join(m for _ns, _al, m in ordered),
            })
    return dimensions, consolidation, exclusions


def _dimensional_revenue_candidate_gates(fact: dict) -> bool:
    """The non-axis gates shared between `_is_dimensional_revenue_fact` and
    `_dimensional_axis_exclusions` (Task 1, docs/loom/plans/2026-07-19-jnj-
    restatement-axis-signature.md): dimensioned + a DURATION context +
    concept is revenue-shaped (`_is_revenue_concept`) + the fact's XBRL unit
    is a currency amount (`_is_currency_amount_fact`) + a reported numeric
    value (never NaN). Does NOT check the axis signature itself — callers
    combine this with `_dimension_signature`'s `dimensions`/`exclusions`."""
    if not fact.get("is_dimensioned"):
        return False
    if fact.get("period_type") != "duration":
        return False
    if not _is_revenue_concept(fact.get("concept")):
        return False
    if not _is_currency_amount_fact(fact):
        return False
    if _is_nan(fact.get("numeric_value")):
        return False
    return True


def _is_dimensional_revenue_fact(fact: dict) -> bool:
    """The combined filter predicate for `extract_dimensional_revenue`:
    `_dimensional_revenue_candidate_gates` (dimensioned + at least one REAL
    breakdown axis present on the row, both namespaces via
    `_is_dimensional_revenue_axis` + concept/currency/value/duration gates)
    + NO disallowed `dim_` axis (Task 1, docs/loom/plans/2026-07-19-jnj-
    restatement-axis-signature.md): a fact carrying `srt:RestatementAxis`
    (any member) or any other unrecognized `dim_` axis is EXCLUDED here
    WHOLE — never emitted with the disallowed axis merely dropped while its
    OTHER (allowed) axes keep `dimensions` populated, which used to let a
    restatement/reclassification pair collide onto the real quarter fact's
    signature. `extract_dimensional_revenue`'s per-fact loop counts these
    exclusions via `_dimensional_axis_exclusions` for the ones this
    predicate rejects."""
    if not _dimensional_revenue_candidate_gates(fact):
        return False
    dimensions, _consolidation, exclusions = _dimension_signature(fact)
    if exclusions:
        return False
    return bool(dimensions)


def _dimensional_axis_exclusions(fact: dict) -> list[dict]:
    """The pack-accounting companion to `_is_dimensional_revenue_fact`
    (Task 1, docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md):
    returns `fact`'s `_dimension_signature` `exclusions` list WHEN `fact`
    is otherwise a qualifying dimensional-revenue candidate
    (`_dimensional_revenue_candidate_gates`) — i.e. it would have emitted
    but for the disallowed axis. A fact that fails an UNRELATED gate (wrong
    concept, non-currency unit, instant context, ...) contributes no
    exclusion accounting — it was never in the running, so counting it
    would flood the pack's `coverage.axis_exclusions` channel with noise
    unrelated to the vintage/unknown-axis blind spot this exists to close.
    Returns an empty list for a fact with no disallowed axis (either it
    emits normally, or it fails an unrelated gate)."""
    if not _dimensional_revenue_candidate_gates(fact):
        return []
    _dimensions, _consolidation, exclusions = _dimension_signature(fact)
    return exclusions


_AVG_DAYS_PER_MONTH = 30.44


def _duration_span_days(fact: dict, ticker: str, period_end: str, *, field: str) -> int:
    """Shared fail-loud `period_start` -> `period_end` day-span extraction
    used by BOTH `_duration_months` and `_duration_weeks` (Task 1,
    docs/loom/plans/2026-07-18-52-53-week-filer-support.md) — one date-
    parsing path, never two copies that could silently drift (mirrors the
    single-shared-week-band-table constraint this module also carries).

    Fails loud (`ValueError` naming `period_start`) on a missing/malformed
    `period_start` instead of guessing or defaulting: a guessed duration
    fabricates financial data, matching this module's anti-fabrication
    posture (mirrors the `period_end` fail-loud check above). `field` names
    the caller's derived quantity (`"duration_months"` / `"duration_weeks"`)
    in the error message only."""
    period_start = fact.get("period_start")
    if not isinstance(period_start, str) or not period_start.strip():
        raise ValueError(
            f"dimensional revenue fact for {ticker!r} has a missing/malformed "
            f"period_start (cannot derive {field}): "
            f"concept={fact.get('concept')!r} period_start={period_start!r} "
            f"period_end={period_end!r}"
        )
    try:
        start_date = date.fromisoformat(period_start)
        end_date = date.fromisoformat(period_end)
    except ValueError as exc:
        raise ValueError(
            f"dimensional revenue fact for {ticker!r} has a missing/malformed "
            f"period_start (cannot derive {field}): "
            f"concept={fact.get('concept')!r} period_start={period_start!r} "
            f"period_end={period_end!r} ({exc})"
        ) from exc
    span_days = (end_date - start_date).days
    if span_days <= 0:
        raise ValueError(
            f"dimensional revenue fact for {ticker!r} has a missing/malformed "
            f"period_start (period_start={period_start!r} is not before "
            f"period_end={period_end!r}, cannot derive {field}): "
            f"concept={fact.get('concept')!r}"
        )
    return span_days


def _duration_months(fact: dict, ticker: str, period_end: str) -> int:
    """Derive the whole-month span of a duration-context fact from its XBRL
    `period_start` -> `period_end` context (Task 1,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md — 'Period
    duration is emitted per fact'): a 10-Q routinely tags BOTH a 3-month
    quarter AND a year-to-date cumulative under the SAME period_end — e.g.
    MSFT's FY26-Q3 10-Q ProductivityAndBusinessProcesses segment revenue:
    3mo ending 2026-03-31 = $35,013M vs 9mo ending 2026-03-31 = $102,149M
    (live-verified 2026-07-16, accession 0001193125-26-191507) — without
    this discriminator the two silently conflate downstream."""
    span_days = _duration_span_days(fact, ticker, period_end, field="duration_months")
    return round(span_days / _AVG_DAYS_PER_MONTH)


# Week-based duration bands (positive allowlist, Task 1,
# docs/loom/plans/2026-07-18-52-53-week-filer-support.md — the SINGLE
# shared table both Gate P (fiscal-boundary labeling, this module) and
# Gate C (duration-class mapping, kpi_xbrl.py lazy-imports this SAME
# function per the module's `-toolkit-r2` two-path-desync lesson,
# edgartools issue #816: no parallel patched copies) decide through.
# Live recon (plan Notes, 2026-07-18) observed 52/53-week filers' XBRL
# duration spans land EXACTLY on a whole-week multiple, or one day short
# of it (12wk=83-84d, 16wk≈111d, 17wk≈119d, 24wk=167d, 36wk≈251d) — never
# a wider drift. Each band is (label, week-counts); a span classifies only
# when it lands in [weeks*7 - 1, weeks*7] for one of the band's week
# counts — deliberately narrow clusters WITH GAPS between them, never one
# wide contiguous range (an ordinary ~365d calendar year must never fall
# into the FY band merely by proximity to 364/371 — fail-closed unchanged,
# docs/loom/memory/shared-classifier-over-open-dialects-needs-allowlist.md).
_WEEK_BANDS: tuple[tuple[str, tuple[int, ...]], ...] = (
    ("quarter", (12, 13)),
    ("week-Q4", (16, 17)),
    ("H1", (24, 26)),
    ("YTD-through-Q3", (36, 39)),
    ("FY", (52, 53)),
)


def _week_lane_class(span_days: int) -> str | None:
    """Pure day-span -> week-lane band label, via the `_WEEK_BANDS`
    positive allowlist. Out-of-band spans return None — fail-closed
    unchanged, never a nearest-guess. This is the single shared
    classification decision both Gate P and Gate C route through."""
    for label, week_counts in _WEEK_BANDS:
        for weeks in week_counts:
            exact_days = weeks * 7
            if exact_days - 1 <= span_days <= exact_days:
                return label
    return None


def _week_count(span_days: int) -> int:
    """Pure day-span -> whole-week-count helper: `round(span_days / 7)`.
    Emitted on EVERY duration fact as `duration_weeks` regardless of which
    lane (month or week) classifies it — Q4-derivation arithmetic
    (FY_weeks - YTD_weeks) needs week-count honesty independent of
    classification (plan Notes, class-lane precedence)."""
    return round(span_days / 7)


def _duration_weeks(fact: dict, ticker: str, period_end: str) -> int:
    """Derive the whole-week span of a duration-context fact from its XBRL
    `period_start` -> `period_end` context, mirroring `_duration_months`'s
    fail-loud posture (never a guessed/defaulted duration). Emitted
    alongside `duration_months` on EVERY duration fact — week-count
    honesty independent of which lane ultimately classifies the fact."""
    span_days = _duration_span_days(fact, ticker, period_end, field="duration_weeks")
    return _week_count(span_days)


# Fiscal-boundary matching tolerance (Task 13; the plan's ruling on the
# spec's deferred constant — docs/loom/plans/2026-07-16-operational-kpi-
# quarterly.md "Plan constants"): covers the live-verified <=6-day
# 52/53-week drift with margin, far below a quarter's width. Task 16 builds
# the beyond-tolerance unclassifiable DQC flag on this same constant.
FISCAL_BOUNDARY_TOLERANCE_DAYS = 10


# Week-based filer quarter structures (Task 2, docs/loom/plans/2026-07-18-
# 52-53-week-filer-support.md — Gate P). Colocated with `_WEEK_BANDS` above
# (the single week-arithmetic home this module keeps): two week-based
# quarter shapes observed among 52/53-week filers (plan Notes, live recon)
# — COST-style (Q1-Q3 each 12wk, Q4 16 or 17wk in a 53-week year) and
# 13-week-quarter filers (Q1-Q3 each 13wk, Q4 13 or 14wk) — expressed ONCE
# as (Q1, Q2, Q3, Q4) week-tuples per FY length. This is the SINGLE SOURCE
# for the week-offset allowlist below; it is declared as data rather than a
# hand-typed offset table because a hand-typed table silently drifted
# (Task 2 round-2 correctness finding: `_WEEK_QUARTER_OFFSETS["Q2"] =
# (26, 28)` omitted the 53-week-year offsets 27 and 29, raising
# UnclassifiablePeriodError on every legitimate Q2 period_end of a
# 53-week-year 13-week-quarter or COST-style filer).
_WEEK_QUARTER_STRUCTURES: tuple[tuple[int, int, int, int], ...] = (
    (13, 13, 13, 13),  # 13-week-quarter family, 52-week fiscal year
    (13, 13, 13, 14),  # 13-week-quarter family, 53-week fiscal year
    (12, 12, 12, 16),  # COST-style family, 52-week fiscal year
    (12, 12, 12, 17),  # COST-style family, 53-week fiscal year
)


def _compute_week_quarter_offsets(
    structures: tuple[tuple[int, int, int, int], ...],
) -> dict[str, tuple[int, ...]]:
    """Derive the Q1-Q3 week-offset positive allowlist from
    `_WEEK_QUARTER_STRUCTURES`: for each (Q1, Q2, Q3, Q4) week-tuple, a
    quarter boundary's offset is the whole-week distance BACKWARD from the
    fiscal-year-end to that boundary — Q3's boundary is Q4 weeks before
    FYE, Q2's is (Q4 + Q3) weeks before FYE, Q1's is (Q4 + Q3 + Q2) weeks
    before FYE. Q4's own boundary is the fiscal-year-end itself (offset 0),
    already covered by the month lane's `boundaries["Q4"]` in
    `_derive_fiscal_label` — no separate week entry needed. Computed, not
    hand-typed, so the offsets can never drift out of sync with the
    structures they are derived from (the bug this function replaces)."""
    offsets: dict[str, set[int]] = {"Q1": set(), "Q2": set(), "Q3": set()}
    for q1, q2, q3, q4 in structures:
        offsets["Q3"].add(q4)
        offsets["Q2"].add(q4 + q3)
        offsets["Q1"].add(q4 + q3 + q2)
    return {label: tuple(sorted(values)) for label, values in offsets.items()}


# A positive allowlist: a period_end classifies to a quarter only when it
# lands within `_WEEK_BOUNDARY_TOLERANCE_DAYS` of one of ITS quarter's
# computed week offsets, never a nearest guess (fail-closed unchanged).
_WEEK_QUARTER_OFFSETS: dict[str, tuple[int, ...]] = _compute_week_quarter_offsets(
    _WEEK_QUARTER_STRUCTURES
)

# Week-lane boundary tolerance (Task 2 kickoff decision, plan Notes: "tight
# (≈±2d) ... widen only on an observed counterexample, never toward the
# month lane's ±10d"). Deliberately its OWN constant, never reusing
# `FISCAL_BOUNDARY_TOLERANCE_DAYS` — the month lane's tolerance must stay
# byte-identical (T2 requirement: WITHOUT touching the month lane's ±10d).
_WEEK_BOUNDARY_TOLERANCE_DAYS = 2


class UnreadableFiscalCalendarError(ValueError):
    """A filing's dei fiscal calendar is absent or malformed, so its facts
    CANNOT be fiscally labeled — a DISTINCT DQC-schema error naming the
    filing (spec: 'an unreadable fiscal calendar fails loud, never a
    calendar fallback'). `period_end[:4]` (the calendar year) is NEVER
    emitted as a fiscal_year in its place — that fallback is trap 1 of the
    root-cause defect (docs/loom/memory/fiscal-year-derive-per-fact-against-
    filing-calendar.md).

    Quarantine semantics (Task 19, docs/loom/plans/2026-07-16-operational-
    kpi-quarterly.md): the calendar is a per-filing property, so the
    extraction loop catches this error, EXCLUDES the whole filing's facts
    from fiscal-labeled output, surfaces `.dqc` under
    `coverage.unlabelable_filings` (the quarter reports
    `filed_but_unlabelable`), and CONTINUES — one unlabelable filing never
    aborts the multi-year run. The fail-loud property lives in that flag,
    never in silence.

    `.dqc` carries the ONE DQC flag schema (type, old, new, accessions,
    reason — the plan's kickoff decision: no per-class schema variants)."""

    def __init__(self, ticker: str, accession: str, reason: str):
        self.dqc = {
            "type": "unreadable_fiscal_calendar",
            "old": None,
            "new": None,
            "accessions": [accession],
            "reason": reason,
        }
        super().__init__(
            f"unreadable dei fiscal calendar for {ticker!r} filing "
            f"{accession!r}: {reason} — facts from this filing cannot be "
            f"fiscally labeled (the calendar year is NEVER emitted as a "
            f"fiscal_year fallback)"
        )


class UnclassifiablePeriodError(ValueError):
    """A fact's `period_end` lands beyond `FISCAL_BOUNDARY_TOLERANCE_DAYS`
    of EVERY fiscal-quarter boundary (a transition/stub period), so the fact
    CANNOT be fiscally labeled — and is never nearest-guessed onto the
    closest boundary (spec: 'an out-of-tolerance period_end is
    unclassifiable, never nearest-guessed'). Quarantine semantics (Task 16,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md): the extraction
    loop catches this error, EXCLUDES the one fact from fiscal-labeled
    output, surfaces `.dqc` under `coverage.unclassifiable_periods`, and
    CONTINUES — one stub period never aborts the whole extraction. Contrast
    `UnreadableFiscalCalendarError` (no calendar at all), quarantined at
    FILING granularity (Task 19): the whole filing's facts are excluded.

    `.dqc` carries the ONE DQC flag schema (type, old, new, accessions,
    reason — the plan's kickoff decision: no per-class schema variants)."""

    def __init__(
        self,
        ticker: str,
        accession: str,
        period_end: date,
        fiscal_year: int,
        fiscal_year_end: date,
    ):
        reason = (
            f"period_end {period_end.isoformat()} for {ticker!r} filing "
            f"{accession!r} matches no FY{fiscal_year} fiscal-quarter "
            f"boundary within {FISCAL_BOUNDARY_TOLERANCE_DAYS} days "
            f"(nominal fiscal year end {fiscal_year_end.isoformat()}) — a "
            f"transition/stub period is never nearest-guessed"
        )
        self.dqc = {
            "type": "unclassifiable_period",
            "old": None,
            "new": None,
            "accessions": [accession],
            "reason": reason,
        }
        super().__init__(reason)


def _parse_fiscal_year_end_month_day(value) -> tuple[int, int] | None:
    """Parse a `dei:CurrentFiscalYearEndDate` value (`--MM-DD`, e.g.
    `--01-25`) into `(month, day)`. Returns None on an absent/malformed
    value (callers fail loud — never guess a calendar)."""
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"--(\d{2})-(\d{2})", value.strip())
    if match is None:
        return None
    month, day = int(match.group(1)), int(match.group(2))
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return month, day


def _nominal_fiscal_year_end(year: int, month: int, day: int) -> date:
    """The NOMINAL fiscal-year-end date of fiscal year `year` for a filer
    whose `dei:CurrentFiscalYearEndDate` is `--MM-DD` (day clamped to the
    month's real length, e.g. --02-29 in a non-leap year). Nominal only: a
    52/53-week filer's ACTUAL year end drifts a few days around it, which
    is why every comparison against it carries
    `FISCAL_BOUNDARY_TOLERANCE_DAYS`."""
    return date(year, month, min(day, calendar.monthrange(year, month)[1]))


def _derive_fiscal_label(
    period_end: date,
    duration_months: int | None,
    dei_calendar: dict | None,
    ticker: str,
    accession: str,
) -> tuple[int, str]:
    """(fiscal_year, fiscal_quarter) for ONE fact, derived from the fact's
    OWN `period_end` measured against ITS filing's dei fiscal calendar —
    the only correct derivation (docs/loom/memory/fiscal-year-derive-per-
    fact-against-filing-calendar.md). NEVER `period_end[:4]` (trap 1: the
    calendar year) and NEVER the filing's `dei:DocumentFiscalYearFocus`
    stamped on every fact (trap 2: a 10-K/10-Q carries ~3 comparative
    years — AAPL's FY2019 10-K would collapse FY2017/18/19 to 2019). The
    focus tag is the filing's own answer for the CURRENT-period fact only
    (live-verified 90/90); this per-period_end derivation reproduces it for
    that fact and, unlike a stamp, stays correct for comparatives. Task 14
    reconciles the declared focus against range membership post-fetch.

    fiscal_year: the fiscal year whose nominal year-end
    (`dei:CurrentFiscalYearEndDate`, per-filing — it DRIFTS for 52/53-week
    filers, never cache it) is the first at-or-after `period_end` within
    tolerance. fiscal_quarter ∈ {Q1, Q2, Q3, Q4, FY}, derived JOINTLY with
    the duration: a 12-month fact is FY, never a bare Q4 (a YTD fact
    carries the quarter its period_end sits on; `duration_months`
    distinguishes it from the single-quarter point).

    Fails loud: `UnreadableFiscalCalendarError` (distinct DQC-schema error)
    on an absent/malformed calendar; `UnclassifiablePeriodError` when
    `period_end` matches no fiscal-quarter boundary within tolerance (a
    transition/stub period — the extraction loop quarantines the ONE fact
    and surfaces the flag, Task 16; never a nearest-boundary guess)."""
    fye_raw = (dei_calendar or {}).get("fiscal_year_end")
    month_day = _parse_fiscal_year_end_month_day(fye_raw)
    if month_day is None:
        raise UnreadableFiscalCalendarError(
            ticker, accession,
            f"dei:CurrentFiscalYearEndDate is absent or malformed "
            f"(got {fye_raw!r}, expected '--MM-DD')",
        )
    month, day = month_day

    year = period_end.year - 1
    while (
        period_end - _nominal_fiscal_year_end(year, month, day)
    ).days > FISCAL_BOUNDARY_TOLERANCE_DAYS:
        year += 1
    fiscal_year = year
    fiscal_year_end = _nominal_fiscal_year_end(fiscal_year, month, day)

    if duration_months == 12:
        # The annual path carries the SAME boundary tolerance as the
        # sub-annual paths (Task 16 round-2 fix): a 12-month comparative
        # ending on an OLD fiscal-year-end inside an FYE-change filing
        # lands far from the new calendar's nominal year-end — quarantine
        # it, never silently label it FY.
        if abs((period_end - fiscal_year_end).days) <= (
            FISCAL_BOUNDARY_TOLERANCE_DAYS
        ):
            return fiscal_year, "FY"
        raise UnclassifiablePeriodError(
            ticker, accession, period_end, fiscal_year, fiscal_year_end
        )

    boundaries = {
        "Q1": _subtract_months(fiscal_year_end, 9),
        "Q2": _subtract_months(fiscal_year_end, 6),
        "Q3": _subtract_months(fiscal_year_end, 3),
        "Q4": fiscal_year_end,
    }
    for label, boundary in boundaries.items():
        if abs((period_end - boundary).days) <= FISCAL_BOUNDARY_TOLERANCE_DAYS:
            return fiscal_year, label

    # Week lane (Task 2, docs/loom/plans/2026-07-18-52-53-week-filer-
    # support.md — Gate P): the month lane above misses a week-based
    # filer's period ends by design (its quarters do not sit on whole-
    # month boundaries), so try the week-offset positive allowlist,
    # measured from the SAME `fiscal_year_end`, with its own tight
    # tolerance — never widening `FISCAL_BOUNDARY_TOLERANCE_DAYS` above.
    for label, week_offsets in _WEEK_QUARTER_OFFSETS.items():
        for weeks in week_offsets:
            week_boundary = fiscal_year_end - timedelta(weeks=weeks)
            if abs((period_end - week_boundary).days) <= _WEEK_BOUNDARY_TOLERANCE_DAYS:
                return fiscal_year, label

    raise UnclassifiablePeriodError(
        ticker, accession, period_end, fiscal_year, fiscal_year_end
    )


def _parse_declared_fiscal_year(value) -> int | None:
    """Parse a filing's declared `dei:DocumentFiscalYearFocus` (a 4-digit
    year string, live-verified 90/90 across 6 filers × 5 FYs) into an int
    fiscal year. Returns None on an absent/malformed value — the caller
    surfaces a distinct DQC flag naming the filing (Task 14); range
    membership is NEVER re-bucketed by `period_of_report[:4]` in its place
    (trap 1 of docs/loom/memory/fiscal-year-derive-per-fact-against-filing-
    calendar.md)."""
    if value is None:
        return None
    text = str(value).strip()
    if re.fullmatch(r"\d{4}", text) is None:
        return None
    return int(text)


def _reconcile_selection_guess(
    guess: int | None,
    declared_raw,
    accession: str,
    since_year: int,
    until_year: int | None,
) -> tuple[bool, dict | None]:
    """Post-fetch reconciliation of ONE guess-selected filing against its
    DECLARED `dei:DocumentFiscalYearFocus` (Task 14; spec: 'the pre-fetch
    index derivation is a GUESS and the dei declaration is the TRUTH ...
    on disagreement the declaration wins and the correction is surfaced —
    never silent in either direction').

    Returns `(keep, flag)` — `keep` is the filing's final range membership;
    `flag` (or None) follows the ONE DQC schema (type, old, new,
    accessions, reason — the plan's kickoff decision, no per-class
    variants):

    - declaration readable + equal to the guess → confirmed: `(True, None)`
      (a clean reconciliation is not noise);
    - declaration readable + different → `fiscal_year_guess_mismatch`
      (old=guess, new=declared); the DECLARATION decides membership, so the
      filing is excluded when the declared year is out of range and kept
      (still flagged) when it is in range — never silently kept, never
      silently dropped;
    - declaration absent/malformed → `unreadable_fiscal_year_declaration`
      naming the filing; membership stands on the sanctioned pre-fetch
      guess — the filing is never silently dropped and NEVER re-bucketed by
      `period_of_report[:4]` (the calendar year, trap 1 of the root-cause
      defect)."""
    declared = _parse_declared_fiscal_year(declared_raw)
    if declared is None:
        return True, {
            "type": "unreadable_fiscal_year_declaration",
            "old": guess,
            "new": None,
            "accessions": [accession],
            "reason": (
                f"dei:DocumentFiscalYearFocus is absent or malformed "
                f"(got {declared_raw!r}, expected a 4-digit year) — the "
                f"selection guess FY{guess} cannot be reconciled; range "
                f"membership stands on the pre-fetch guess and is never "
                f"re-bucketed by the calendar year of period_of_report"
            ),
        }
    if declared == guess:
        return True, None
    keep = _fiscal_year_guess_in_range(declared, since_year, until_year)
    return keep, {
        "type": "fiscal_year_guess_mismatch",
        "old": guess,
        "new": declared,
        "accessions": [accession],
        "reason": (
            f"pre-fetch selection guessed FY{guess} but the fetched filing "
            f"declares dei:DocumentFiscalYearFocus={declared} — the "
            f"declaration wins: "
            + (
                f"FY{declared} falls inside the requested range "
                f"[{since_year}, "
                f"{until_year if until_year is not None else 'latest'}], "
                f"filing kept under its declared year"
                if keep else
                f"FY{declared} falls outside the requested range "
                f"[{since_year}, "
                f"{until_year if until_year is not None else 'latest'}], "
                f"filing excluded from the result"
            )
        ),
    }


def _build_dimensional_revenue_fact(
    fact: dict, ticker: str, accession: str, filed, dei_calendar: dict | None,
) -> dict:
    """Build one normalized fact-pack row from an edgartools fact record
    already known to pass `_is_dimensional_revenue_fact`.

    Emits the full-signature shape (Task 4,
    docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md):
    `dimensions` — a dict of ALL real breakdown axes present on the row
    (`_dimension_signature`) — and a separate `consolidation` field (the
    srt:ConsolidationItemsAxis reconciliation qualifier, or None). Replaces
    the pilot's single `{axis, member}` model in the same change.

    Fails loud (`ValueError` naming `period_end`) instead of silently
    emitting a null-dated fact: a revenue fact with no period_end cannot be
    placed on the fiscal timeline, and this extractor's anti-fabrication
    posture never emits a fact it cannot date — plan amendment (a),
    spec-reviewer NEEDS_REVISION.

    Emits the PARALLEL period-label groups (Task 13, docs/loom/plans/
    2026-07-16-operational-kpi-quarterly.md — mirrors Compustat DATADATE/
    DATACQTR/DATAFQTR; never one collapsed into another):
    (1) the raw window — `period_end` (+ `period_start` via
    `duration_months`); (2) a CALENDAR label — `calendar_year` +
    `calendar_quarter`, mechanically the calendar quarter containing
    `period_end` (Compustat's DATACQTR rule); (3) a FISCAL label —
    `fiscal_year` + `fiscal_quarter`, derived by `_derive_fiscal_label`
    from this fact's OWN period_end measured against `dei_calendar` (THIS
    filing's per-filing dei read, `_extract_dei_calendar`). Neither of the
    two root-cause traps is ever emitted (docs/loom/memory/fiscal-year-
    derive-per-fact-against-filing-calendar.md): `fiscal_year` is never
    `period_end[:4]` (that is `calendar_year`'s honest job now), and never
    the filing's `dei:DocumentFiscalYearFocus` stamped uniformly (a
    comparative derives from its own period). An unreadable calendar
    raises `UnreadableFiscalCalendarError` — never a calendar fallback.

    The fiscal label also records `derivation_basis` (Task 16, spec: 'each
    fiscal label MUST record its derivation basis'): here ALWAYS
    "dei-declared" — a per-fact label rests on its OWN filing's in-hand
    `dei:CurrentFiscalYearEndDate` (no tag → the raise above, never a
    projection). The "projected" basis exists only at the COVERAGE layer
    (`_quarterly_completeness_report`), where an in-progress fiscal year's
    calendar rests on the +12mo forward projection of the prior declared
    FYE because its own declaration does not yet exist.

    Also derives the raw fiscal_year column trap away: the label is NEVER
    taken from edgartools' raw `fiscal_year` column, which is unreliable
    for prior-year comparatives (live-verified on AAPL's 2025 10-K, the
    iPhone fact with period_end 2024-09-28 is column-labeled
    fiscal_year=2025 but is really FY2024).

    A duration-context fact also carries `duration_months` (Task 1,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md — `_duration_months`,
    fail-loud on a missing/malformed period_start) AND `duration_weeks`
    (Task 1, docs/loom/plans/2026-07-18-52-53-week-filer-support.md —
    `_duration_weeks`, same fail-loud posture, emitted on EVERY duration
    fact regardless of which lane ultimately classifies it). An
    instant-context fact (reached only via a direct caller —
    `extract_dimensional_revenue`'s `_is_dimensional_revenue_fact`
    predicate excludes instant contexts before this function is ever
    called) carries neither key: it is not a duration flow and never gets
    a fabricated/guessed duration.

    Also carries `week_lane_band` (Task 3 fix round 2, spec-reviewer
    NEEDS_REVISION on 111e4530) — the ONE week-lane classification
    decision, made HERE from the same raw day-span `duration_weeks` is
    derived from, via the shared `_week_lane_class` primitive: the band
    label str, or None when the span is out-of-band. `kpi_xbrl.py`'s
    `_week_lane_duration_class` is now a PURE TRANSCRIPTION of this
    field — it never re-decides membership from the already-rounded
    `duration_weeks` int (that re-derivation had up to +-3d slop wider
    than `_week_lane_class`'s tight [weeks*7-1, weeks*7] window and
    could silently reintroduce the edgartools #816 two-path desync this
    module's ONE-shared-primitive constraint exists to prevent)."""
    dimensions, consolidation, _exclusions = _dimension_signature(fact)
    period_end = (
        fact.get("period_end") if fact.get("period_type") == "duration"
        else fact.get("period_instant")
    )
    if not period_end:
        raise ValueError(
            f"dimensional revenue fact for {ticker!r} has no period_end "
            f"(cannot be dated): concept={fact.get('concept')!r} "
            f"dimensions={dimensions!r} consolidation={consolidation!r}"
        )
    try:
        period_end_date = date.fromisoformat(str(period_end))
    except ValueError as exc:
        raise ValueError(
            f"dimensional revenue fact for {ticker!r} has a malformed "
            f"period_end (cannot be dated or period-labeled): "
            f"concept={fact.get('concept')!r} period_end={period_end!r} "
            f"({exc})"
        ) from exc
    built = {
        "concept": fact.get("concept"),
        "dimensions": dimensions,
        "consolidation": consolidation,
        "value": float(fact.get("numeric_value")),
        "period_end": period_end,
        "accession": accession,
        "filed": filed,
    }
    if fact.get("period_type") == "duration":
        built["duration_months"] = _duration_months(fact, ticker, period_end)
        built["duration_weeks"] = _duration_weeks(fact, ticker, period_end)
        week_span_days = _duration_span_days(
            fact, ticker, period_end, field="duration_weeks",
        )
        built["week_lane_band"] = _week_lane_class(week_span_days)
    fiscal_year, fiscal_quarter = _derive_fiscal_label(
        period_end_date, built.get("duration_months"), dei_calendar,
        ticker, accession,
    )
    built["calendar_year"] = period_end_date.year
    built["calendar_quarter"] = f"Q{(period_end_date.month - 1) // 3 + 1}"
    built["fiscal_year"] = fiscal_year
    built["fiscal_quarter"] = fiscal_quarter
    # Always tag-grounded at fact level — see the docstring's
    # derivation-basis note (projection exists only at the coverage layer).
    built["derivation_basis"] = "dei-declared"
    return built


def _filing_period_end_calendar_year(filing) -> int | None:
    """The CALENDAR year of `filing`'s `period_of_report` — an honest name
    for what the retired `_filing_period_year` computed while its docstring
    claimed "the fiscal year a filing REPORTS" (the scope-B root-cause
    defect: docs/loom/memory/fiscal-year-derive-per-fact-against-filing-
    calendar.md, trap 1).

    What this value IS: for an ANNUAL filing (10-K), the fiscal-year LABEL
    by SEC convention (a fiscal year is named for the calendar year its
    period ends in) — the sanctioned filings-index GUESS for annual forms,
    reconciled post-fetch against the declared `dei:DocumentFiscalYearFocus`
    (Task 14). What it is NOT: the fiscal year of a 10-Q at any
    non-December-FYE filer (NVDA's FY2026 quarters all end in calendar
    2025) — quarterly fiscal-year candidates come from
    `_quarterly_fiscal_year_guesses`, never from this value.

    Reads filings-list metadata only — never fetches `.xbrl()`. Returns
    None when `period_of_report` is absent/unparseable (never guessed)."""
    period = getattr(filing, "period_of_report", None)
    if not period:
        return None
    try:
        return int(str(period)[:4])
    except (ValueError, TypeError):
        return None


def extract_dimensional_revenue(
    ticker: str,
    form: str = "10-K",
    since_year: int | None = None,
    until_year: int | None = None,
    as_of: date | None = None,
) -> dict:
    """Fetch `ticker`'s `form` XBRL via edgartools and emit the normalized
    full-signature dimensional-revenue fact-pack (Task 4,
    docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md
    — the declared shape, tests/analysis/fixtures/xbrl_signature_factpack.json):
      {"company": <ticker>, "facts": [{"concept", "dimensions": {axis_local:
       member_local, ...}, "consolidation": member_local|None, "value",
       "period_end", "fiscal_year", "accession", "filed"}, ...]}

    Range-bounded consecutive multi-filing fetch (Task 1,
    docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md):

    - `since_year=None, until_year=None` (default): latest filing only —
      today's behavior, UNCHANGED (no cold-fetch surprise: pulling all ~16
      historical `.xbrl()`s is too heavy for a default).
    - `since_year` set: every exact-form filing whose fiscal period (from the
      filings-list `period_of_report` metadata) falls in the INCLUSIVE year
      range `[since_year, until_year]` is fetched and its facts concatenated
      into the one flat `facts` list. `until_year=None` → `[since_year, latest]`.
      CONSECUTIVE — every in-range filing, never strided (striding risks silent
      year-gaps and breaks the overlap policy). Filing selection reads the
      filings-list metadata; only the selected filings' `.xbrl()` is fetched.
      Selection is a pre-fetch GUESS reconciled post-fetch against each
      fetched filing's declared `dei:DocumentFiscalYearFocus` (Task 14,
      docs/loom/plans/2026-07-16-operational-kpi-quarterly.md —
      `_reconcile_selection_guess`): an out-of-range declaration excludes
      the filing, an unreadable declaration is flagged by name; either
      outcome is surfaced under `coverage.fiscal_year_reconciliation`
      (a DQC-schema flag list; `None` when no range was requested).

    A fact whose period_end matches no fiscal-quarter boundary within
    `FISCAL_BOUNDARY_TOLERANCE_DAYS` (a transition/stub period) is
    QUARANTINED (Task 16): excluded from `facts`, surfaced under
    `coverage.unclassifiable_periods` (a DQC-schema flag list, always
    present — empty means "ran, none found"), never nearest-guessed and
    never a whole-run abort.

    `until_year` WITHOUT `since_year` is UNSUPPORTED and raises loudly: the
    range is `[since_year, until_year]`, and with no lower bound the call would
    silently fall to latest-only and could return a filing NEWER than the
    stated `until_year` — a silent contradiction of the caller's request
    (fail-loud: silent-wrong is the enemy). The Decision Log defines only
    both-None (latest-only) and `since_year`-alone (`[since_year, latest]`).

    Emits every REVENUE fact (`_is_revenue_concept`) carrying at least one
    REAL breakdown dimensional axis (`_dimension_signature`, via
    `_is_dimensional_revenue_axis` — matching BOTH `us-gaap:*` and `srt:*`
    namespaces; see the module note above for why filtering one namespace
    is wrong). A fact with no reported
    numeric value (NaN — mirrors `_build_statement_cells`'s `_is_nan` skip,
    e.g. a placeholder concept) is not emitted — never fabricated as 0.

    Returns a loud `{"error": ...}` slot (never a fabricated/empty fact-pack)
    when the ticker does not resolve to a registered SEC filer, or no `form`
    filing matches the requested window/range.

    When `form="10-Q"`, `coverage` also carries `quarterly_coverage` +
    `selection_gaps` (Task 18, docs/loom/plans/2026-07-16-operational-kpi-
    quarterly.md — supersedes T10): one record per fiscal year the FULL
    filings index evidences (never just the requested range or the
    selected set) reporting which of the 4 expected filings (10-K +
    Q1/Q2/Q3) are present vs. missing-with-reason — the index-absence
    states not_yet_filed / out_of_requested_range (on the FISCAL year) /
    unclassified, plus index_visible_not_selected for an index filing the
    pre-fetch derivation could not place (`_quarterly_completeness_
    report`); `selection_gaps` lists those never-selected filings as
    DQC-schema flags. Both are `None` for any other `form` (not
    applicable — never a silently-empty list). `as_of` anchors the
    not-yet-filed classification (defaults to `date.today()`,
    injectable for deterministic tests — same convention as
    `select_narrative_filings`'s `as_of`).

    `coverage` also carries the two OBSERVED per-filing failure states
    (Task 19), both always-list (the extraction loop always runs; empty =
    ran, none found): `fetch_failures` — a selected filing whose
    download/XBRL parse RAISED, recorded `attempted_fetch_failed` with the
    in-hand exception class + message (retryable) — and
    `unlabelable_filings` — a filing that fetched fine but whose dei
    calendar failed the fail-loud derivation, quarantined whole
    (`filed_but_unlabelable` on its quarter; see
    `UnreadableFiscalCalendarError`). In both cases the run CONTINUES —
    one bad filing's blast radius is exactly that filing.

    This function's labeled-fact output is UNCACHED (Task 17,
    docs/loom/plans/2026-07-16-operational-kpi-quarterly.md — implementation
    recon found no cache write/read path here; the only caches in this
    module are schema-independent raw-source keys: tickers/facts_{cik}/
    concept_{cik}_{concept}/submissions_{cik}/narrative_sections_{accession}).
    Any FUTURE cache of this labeled-fact payload MUST use a
    schema-versioned distinct key, never a legacy key — see spec
    constraint (d), docs/loom/2026-07-16-operational-kpi-quarterly/specs/
    operational-kpi-quarterly/spec.md.
    """
    ticker = ticker.upper()
    if since_year is None and until_year is not None:
        raise ValueError(
            "until_year requires since_year: an upper bound with no lower "
            "bound is unsupported (the range is [since_year, until_year]; "
            "without since_year the call would fall to latest-only and could "
            f"return a filing newer than until_year={until_year})"
        )
    identity_error = _ensure_edgar_identity()
    if identity_error is not None:
        return identity_error

    import edgar

    try:
        company = edgar.Company(ticker)
    except Exception as exc:  # noqa: BLE001 — fail loud, don't guess the shape
        return _dimensional_revenue_error_slot(
            ticker, form,
            f"identifier did not resolve to a registered SEC filer ({exc})",
        )
    if company is None or getattr(company, "not_found", False) or not getattr(company, "cik", None):
        return _dimensional_revenue_error_slot(
            ticker, form, "identifier did not resolve to a registered SEC filer",
        )

    filings = company.get_filings(form=form)
    # `filings.latest()` is a loose/prefix match on `form` — live-verified
    # 2026-07-15 that TSLA's most recent filing is a "10-K/A" amendment
    # (0 dimensional-revenue facts), which `.latest()` would return and
    # let shadow the real annual report. Filter to an EXACT form match
    # first, then take the most recent by filing_date — an amendment
    # never wins even when it postdates the real filing (Task 6,
    # docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md).
    exact_filings = (
        [f for f in filings if getattr(f, "form", None) == form]
        if filings is not None else []
    )
    if not exact_filings:
        regime_reason = _foreign_private_issuer_no_quarterly_reason(company.cik, form)
        if regime_reason is not None:
            return _foreign_private_issuer_na_slot(ticker, form, regime_reason)
        return _dimensional_revenue_error_slot(
            ticker, form, f"form {form!r} not available within the lookup window",
        )

    annual_form = _QUARTERLY_COMPANION_ANNUAL_FORM.get(form)
    annual_exact_filings: list = []
    if annual_form is not None:
        # Fetched BEFORE selection (Task 13): a quarterly form's fiscal-year
        # candidates derive from the companion annual index's fiscal windows
        # (`_quarterly_fiscal_year_guesses`) — a cheap filings-list lookup
        # only (never a `.xbrl()` fetch, the usage-cost lever the plan
        # flags), reusing the SAME `company` object already resolved above.
        # The Task 10 completeness report below reuses this same list.
        annual_company_filings = company.get_filings(form=annual_form)
        annual_exact_filings = (
            [f for f in annual_company_filings if getattr(f, "form", None) == annual_form]
            if annual_company_filings is not None else []
        )
        quarterly_guesses = _quarterly_fiscal_year_guesses(
            annual_exact_filings, exact_filings
        )

        def _fiscal_year_guess(filing):
            return quarterly_guesses.get(getattr(filing, "accession_no", None))
    else:
        # An ANNUAL filing's fiscal-year label IS the calendar year of its
        # period end by SEC convention — the sanctioned index-metadata
        # guess for annual forms (see `_filing_period_end_calendar_year`;
        # the declared dei:DocumentFiscalYearFocus stays the truth, T14).
        _fiscal_year_guess = _filing_period_end_calendar_year

    if since_year is None:
        # Default (latest-only) path — pick the single most-recent exact-form
        # filing. Behaviorally identical to the pre-range collapse.
        selected = [max(exact_filings, key=lambda f: f.filing_date)]
    else:
        # Range path — select from filings-list metadata by each filing's
        # GUESSED DECLARED FISCAL YEAR (Task 13; the root-cause fix: never
        # the calendar year of period_of_report), without fetching every
        # `.xbrl()` first (the plan's kickoff decision).
        selected = sorted(
            (
                f for f in exact_filings
                if _fiscal_year_guess_in_range(
                    _fiscal_year_guess(f), since_year, until_year
                )
            ),
            key=lambda f: f.filing_date,
        )
        if not selected:
            return _dimensional_revenue_error_slot(
                ticker, form,
                f"no {form!r} filing's guessed declared fiscal year falls "
                f"within [{since_year}, "
                f"{until_year if until_year is not None else 'latest'}]"
                + (
                    " (quarterly candidates derive from the companion "
                    f"{annual_form!r} index's fiscal windows; a filer with "
                    "no annual filing on file has no derivable fiscal "
                    "calendar and is never calendar-bucketed into the range)"
                    if annual_form is not None else ""
                ),
            )

    facts = []
    fiscal_calendars: dict[str, dict] = {}
    # Task 14: post-fetch reconciliation of the selection guess — a
    # DQC-schema flag list when a fiscal range was requested, None otherwise
    # (not applicable — same convention as `quarterly_coverage`, never a
    # silently-empty list standing in for "did not run").
    fiscal_year_reconciliation: list[dict] | None = (
        [] if since_year is not None else None
    )
    # Task 16: out-of-tolerance (transition/stub) periods are quarantined —
    # the ONE fact is excluded from fiscal-labeled output, the run
    # continues, and the exclusion is surfaced here (the ONE DQC schema).
    # Always a list: label derivation runs on every extraction, so an empty
    # list means "ran, none found" — never "did not run".
    unclassifiable_periods: list[dict] = []
    # Task 19: the two OBSERVED per-filing failure states, each grounded by
    # in-hand evidence (never inferred from index absence — that lane is
    # `_missing_quarter_reason`'s). Both always-list (this loop always
    # runs): empty means "ran, none found" — never "did not run".
    fetch_failures: list[dict] = []
    unlabelable_filings: list[dict] = []
    # Task 1, docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md:
    # every `dim_` axis excluded by `_dimension_signature` (vintage —
    # srt:RestatementAxis, any member — or unknown-axis) is counted here,
    # by category, with enough context (axis/member/concept/accession/
    # period_end) for a downstream coverage flag (Task 2). Always a list —
    # this loop always runs — empty means "ran, none found", matching the
    # other DQC-style channels above.
    axis_exclusions: list[dict] = []
    for filing in selected:
        accession = filing.accession_no
        try:
            xb = filing.xbrl()
            facts_records = xb.facts.to_dataframe().to_dict("records")
        except Exception as exc:  # noqa: BLE001 — Task 19: ANY download/parse
            # failure for ONE filing is caught, recorded with its in-hand
            # exception (class + message — the positive ground the
            # `fetch_error` reservation in `_missing_quarter_reason` was
            # waiting for), and the run CONTINUES — one failed filing's
            # blast radius is that filing, never the whole extraction.
            fetch_failures.append({
                "type": "attempted_fetch_failed",
                "old": None,
                "new": None,
                "accessions": [accession],
                "reason": (
                    f"download/XBRL parse raised for filing {accession!r}: "
                    f"{type(exc).__name__}: {exc} — attempted and failed "
                    "with the exception in hand (retryable; distinct from "
                    "an index absence, which grounds no retry claim)"
                ),
            })
            continue
        filed = _filing_date_iso(filing.filing_date)
        # Task 3 (docs/loom/plans/2026-07-16-operational-kpi-quarterly.md —
        # 'the fiscal calendar is read per-filing from dei tags, never cached
        # per ticker'): read straight from THIS filing's own facts_records,
        # keyed by ITS OWN accession, inside this per-filing loop iteration —
        # never a module-level/ticker-level cache. See `_extract_dei_calendar`.
        # Task 13: the SAME per-filing calendar grounds each fact's fiscal
        # label (per-fact, own period_end — `_build_dimensional_revenue_fact`).
        dei_calendar = _extract_dei_calendar(facts_records)
        fiscal_calendars[accession] = dei_calendar
        if fiscal_year_reconciliation is not None:
            # Task 14: the pre-fetch guess was only a CANDIDATE; the fetched
            # filing's own declared dei:DocumentFiscalYearFocus is the truth.
            # Re-check range membership BEFORE emitting this filing's facts;
            # an out-of-range declaration excludes the filing (surfaced,
            # never silent), an unreadable declaration is flagged by name
            # (kept on the guess — never re-bucketed by period_of_report[:4]).
            keep, reconciliation_flag = _reconcile_selection_guess(
                _fiscal_year_guess(filing),
                dei_calendar.get("fiscal_year_focus"),
                accession, since_year, until_year,
            )
            if reconciliation_flag is not None:
                fiscal_year_reconciliation.append(reconciliation_flag)
            if not keep:
                continue
        filing_facts: list[dict] = []
        quarantine_flag: dict | None = None
        for fact in facts_records:
            if not _is_dimensional_revenue_fact(fact):
                # Task 1: count every disallowed dim_ axis this WOULD-BE
                # revenue fact carries (never a fact that fails an
                # unrelated gate — `_dimensional_axis_exclusions` scopes
                # to candidates only, no unrelated-fact noise).
                for exclusion in _dimensional_axis_exclusions(fact):
                    axis_exclusions.append({
                        **exclusion,
                        "concept": fact.get("concept"),
                        "accession": accession,
                        "period_end": (
                            fact.get("period_end")
                            if fact.get("period_type") == "duration"
                            else fact.get("period_instant")
                        ),
                    })
                continue
            try:
                filing_facts.append(
                    _build_dimensional_revenue_fact(
                        fact, ticker, accession, filed, dei_calendar,
                    )
                )
            except UnclassifiablePeriodError as exc:
                # Task 16 quarantine: exclude the ONE fact, surface the
                # flag, keep going — never nearest-guess a boundary, never
                # abort the extraction for one transition/stub period.
                unclassifiable_periods.append(exc.dqc)
            except UnreadableFiscalCalendarError as exc:
                # Task 19 quarantine, FILING granularity: the calendar is a
                # per-filing property, so NONE of this filing's facts can
                # be fiscally labeled — exclude them ALL from labeled
                # output (`filing_facts` is discarded below; the calendar
                # year is NEVER emitted in their place — trap 1 of
                # docs/loom/memory/fiscal-year-derive-per-fact-against-
                # filing-calendar.md), surface the DQC flag, and CONTINUE:
                # one unlabelable filing never aborts the multi-year run.
                # The fail-loud property MOVES to this flag (+ the
                # quarter's filed_but_unlabelable coverage state) — loud in
                # coverage, never silent.
                quarantine_flag = exc.dqc
                break
        if quarantine_flag is not None:
            unlabelable_filings.append(quarantine_flag)
        else:
            facts.extend(filing_facts)

    quarterly_coverage = None
    selection_gaps = None
    if annual_form is not None:
        # Task 18 (supersedes T10): per-quarter completeness over the
        # ALREADY-FETCHED filings-list metadata (annual index reused from
        # the selection block above — never a second fetch). The
        # comparison universe is the FULL 10-Q index (`exact_filings`),
        # never the `selected` subset — a filing the derivation missed
        # must surface as a selection gap, not vanish with the selection.
        quarterly_coverage, selection_gaps = _quarterly_completeness_report(
            annual_exact_filings, exact_filings,
            since_year, until_year, as_of or date.today(),
        )
        # Task 19: an index-matched filing whose fetch raised, or whose
        # calendar was unreadable, is NOT covered — override its quarter's
        # index-presence claim with the OBSERVED state (in-hand evidence
        # beats index inference, same precedence rule as
        # `_surface_selection_gaps`).
        _apply_observed_failure_states(
            quarterly_coverage, fetch_failures, unlabelable_filings,
        )

    available_fiscal_years = [
        y for y in (_fiscal_year_guess(f) for f in exact_filings)
        if y is not None
    ]
    return {
        "company": ticker,
        "facts": facts,
        "coverage": {
            **_dimensional_revenue_coverage(
                since_year, until_year, available_fiscal_years, facts, form,
            ),
            "quarterly_coverage": quarterly_coverage,
            "selection_gaps": selection_gaps,
            "fiscal_year_reconciliation": fiscal_year_reconciliation,
            "unclassifiable_periods": unclassifiable_periods,
            "fetch_failures": fetch_failures,
            "unlabelable_filings": unlabelable_filings,
            "axis_exclusions": axis_exclusions,
        },
        "fiscal_calendars": fiscal_calendars,
    }


def _extract_dei_calendar(facts_records: list[dict]) -> dict:
    """Read ONE filing's own `dei:DocumentFiscalPeriodFocus` +
    `dei:CurrentFiscalYearEndDate` from its ALREADY-FETCHED `facts_records`
    (Task 3, docs/loom/plans/2026-07-16-operational-kpi-quarterly.md — 'the
    fiscal calendar is read per-filing from dei tags, never cached per
    ticker'). dei rows share the SAME records list as the us-gaap facts
    (live-verified 2026-07-17, edgartools 5.42.0: a filing's
    `xbrl().facts.to_dataframe()` carries both `dei:*` and `us-gaap:*`
    concepts in one frame), so this reads the list callers already fetched —
    no extra `.xbrl()` call.

    Reads ONLY rows from THIS filing's own records — never a module-level or
    ticker-level cache — so a 52/53-week filer's fiscal-year-end that DRIFTS
    between filings (live-verified: NVDA's `dei:CurrentFiscalYearEndDate` was
    `--01-31` in accession 0001045810-21-000010 and `--01-25` in accession
    0001045810-26-000021) is captured correctly per filing instead of one
    filing's calendar silently overwriting or shadowing another's.

    Task 13 extends the read with the THIRD cover tag,
    `dei:DocumentFiscalYearFocus` — the filing's own declared fiscal year,
    authoritative for its CURRENT-period fact only (never stamped on
    comparatives — trap 2 of docs/loom/memory/fiscal-year-derive-per-fact-
    against-filing-calendar.md) and the declaration Task 14 reconciles the
    pre-fetch selection guess against.

    Returns `{"fiscal_period_focus": <value>|None, "fiscal_year_end":
    <value>|None, "fiscal_year_focus": <value>|None}` — `None` when a tag
    is absent from this filing's records, never fabricated/guessed (a real
    10-K/10-Q always carries all three per SEC dei taxonomy requirements;
    an absence here is a test-double gap, not a real-filing shape)."""
    def _first_value(concept: str):
        for row in facts_records:
            if row.get("concept") == concept:
                return row.get("value")
        return None

    return {
        "fiscal_period_focus": _first_value("dei:DocumentFiscalPeriodFocus"),
        "fiscal_year_end": _first_value("dei:CurrentFiscalYearEndDate"),
        "fiscal_year_focus": _first_value("dei:DocumentFiscalYearFocus"),
    }


def _dimensional_revenue_coverage(
    since_year: int | None,
    until_year: int | None,
    available_fiscal_years: list[int],
    facts: list[dict],
    form: str,
) -> dict:
    """Coverage report + availability clamp (Task 2,
    docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md — DQC
    honesty): `{requested:{since,until}, actual:{min_year,max_year},
    clamp_reason: str|None}`.

    `actual` is the real span of the facts actually returned (their honest
    per-fact `fiscal_year` labels, Task 13) — never a fabricated echo of
    the request. `clamp_reason` fires when the request reaches outside the
    company's real filing availability — `available_fiscal_years` is the
    caller's guessed declared fiscal year per EXACT-form filing (ALL of
    them, not just the ones selected for this call; annual convention or
    quarterly window-match, same basis the selection used — never the
    calendar year of `period_of_report`), i.e. no filing exists to satisfy
    the requested bound. It is `None` when the request is fully within
    availability, even though the returned facts' span may legitimately
    fall short of the request for other reasons (e.g. a filing's
    comparative years don't reach that far)."""
    fact_years = [f["fiscal_year"] for f in facts]
    actual = {
        "min_year": min(fact_years) if fact_years else None,
        "max_year": max(fact_years) if fact_years else None,
    }
    available_min_year = (
        min(available_fiscal_years) if available_fiscal_years else None
    )
    available_max_year = (
        max(available_fiscal_years) if available_fiscal_years else None
    )

    reasons = []
    if (
        since_year is not None
        and available_min_year is not None
        and since_year < available_min_year
    ):
        reasons.append(
            f"requested since_year={since_year} precedes the earliest "
            f"available {form!r} filing (fiscal period {available_min_year})"
        )
    if (
        until_year is not None
        and available_max_year is not None
        and until_year > available_max_year
    ):
        reasons.append(
            f"requested until_year={until_year} exceeds the latest "
            f"available {form!r} filing (fiscal period {available_max_year})"
        )

    return {
        "requested": {"since": since_year, "until": until_year},
        "actual": actual,
        "clamp_reason": "; ".join(reasons) if reasons else None,
    }


_QUARTERLY_COMPANION_ANNUAL_FORM = {"10-Q": "10-K"}
_QUARTER_LABELS = ("Q1", "Q2", "Q3")
_QUARTER_MATCH_TOLERANCE_DAYS = 20


def _subtract_months(d: date, months: int) -> date:
    """`d` minus `months` calendar months, clamping the day to the target
    month's real length (e.g. Mar 31 - 1mo -> Feb 28/29, never a raise).
    Pure, no clock read — used to derive expected quarter-end dates from a
    fiscal year end."""
    month_index = d.month - 1 - months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _expected_quarterly_period_ends(fiscal_year_end: date) -> dict[str, date]:
    """The approximate period-end date of each of a fiscal year's THREE
    separately-filed 10-Qs (Task 10, docs/loom/plans/2026-07-16-operational-
    kpi-quarterly.md — Q4 has no standalone 10-Q; it is derived from
    FY-9moYTD, Task 8), as `fiscal_year_end` minus 9/6/3 months. A
    month-only approximation: a 52/53-week filer's real quarter-end can
    drift several days from the calendar month-end (NVDA: --01-25 vs
    --01-31), so callers match against this with a day-count TOLERANCE
    (`_QUARTER_MATCH_TOLERANCE_DAYS`), never an exact-date compare."""
    return {
        "Q1": _subtract_months(fiscal_year_end, 9),
        "Q2": _subtract_months(fiscal_year_end, 6),
        "Q3": _subtract_months(fiscal_year_end, 3),
    }


def _match_quarter_filing(expected_end: date, quarterly_filings: list):
    """The first filing in `quarterly_filings` whose `period_of_report`
    falls within `_QUARTER_MATCH_TOLERANCE_DAYS` days of `expected_end`, or
    None. A filing with no/unparseable `period_of_report` never matches
    (never guessed)."""
    for filing in quarterly_filings:
        period = getattr(filing, "period_of_report", None)
        if not period:
            continue
        try:
            actual = date.fromisoformat(str(period))
        except ValueError:
            continue
        if abs((actual - expected_end).days) <= _QUARTER_MATCH_TOLERANCE_DAYS:
            return filing
    return None


def _missing_quarter_reason(
    expected_end: date,
    fiscal_year: int,
    since_year: int | None,
    until_year: int | None,
    as_of: date,
) -> tuple[str, str]:
    """Classify WHY an expected filing (a quarter's 10-Q, or the 10-K
    itself) is absent from the filings INDEX — one of FOUR MODELED states,
    THREE of which this function actually returns (`fetch_error` is
    RESERVED, see below — Task 10 revision round 2, finding 4: the spec,
    not this code, owns closing that gap) — never inferred by falling
    through a comparison to a specific-sounding claim the code has no
    grounds for, docs/loom/
    memory/fail-closed-default-must-be-enforced-not-emergent.md):

    - "out_of_requested_range": the quarter's FISCAL year falls outside
      the caller's requested `[since_year, until_year]` window — the
      caller never asked for this period. The comparison rides
      `fiscal_year`, NEVER `expected_end.year` (Task 18: that is the
      CALENDAR year — trap 1 of docs/loom/memory/fiscal-year-derive-per-
      fact-against-filing-calendar.md; AAPL FY2025-Q1's expected end
      2024-12-27 must never classify out-of-range for [2025, 2025]).
      Checked FIRST: the caller's window verdict is independent of the
      clock, so an out-of-range future quarter is out-of-range, not
      not_yet_filed.
    - "not_yet_filed": `expected_end` is still in the future relative to
      `as_of` — the period hasn't happened yet (current in-progress FY).
    - "fetch_error": RESERVED for a filing the code has POSITIVE grounds
      to believe failed to fetch (e.g. a caught network/parse exception on
      a filing known to exist). This function never has such grounds — a
      filings-list absence is equally consistent with "never filed" (e.g.
      a company IPO'd mid-year and an early quarter never existed) as with
      a genuine fetch gap — so it never returns this value. (The OBSERVED
      `attempted_fetch_failed` state, grounded by an in-hand exception at
      the fetch site, is implemented by Task 19: the extraction loop
      records the caught exception in `coverage.fetch_failures` and
      `_apply_observed_failure_states` overrides the quarter's record.)
    - "unclassified": `expected_end` is in the past AND within the
      requested range, so the filing SHOULD exist by now, but its absence
      has no more specific explanation available. This branch used to
      return "fetch_error" — a caller reading that as "retry me" would
      retry FOREVER for a filing that will never exist (the mid-FY-IPO
      case above). "unclassified" makes no retryability claim either way.

    Exactly one branch fires per call (checked in this order). These are
    INDEX-ABSENCE states only: a filing that IS in the index but was not
    selected is positive evidence, and the caller
    (`_quarterly_completeness_report`, Task 18) overrides any state this
    function inferred with `index_visible_not_selected` — inference never
    outranks evidence in hand."""
    if since_year is not None and fiscal_year < since_year:
        return (
            "out_of_requested_range",
            f"fiscal year {fiscal_year} precedes requested "
            f"since_year={since_year}",
        )
    if until_year is not None and fiscal_year > until_year:
        return (
            "out_of_requested_range",
            f"fiscal year {fiscal_year} exceeds requested "
            f"until_year={until_year}",
        )
    if expected_end > as_of:
        return (
            "not_yet_filed",
            f"expected period end {expected_end.isoformat()} is in the "
            f"future (as of {as_of.isoformat()})",
        )
    return (
        "unclassified",
        f"expected period end {expected_end.isoformat()} is within the "
        "requested range and already due, but no matching filing was "
        "found and there is no positive evidence of why (could be a "
        "genuine fetch gap, or a period the filer never filed — e.g. "
        "pre-IPO; not assumed retryable)",
    )


def _quarterly_year_completeness(
    fiscal_year: int,
    fiscal_year_end: date | None,
    has_10k: bool,
    quarterly_filings: list,
    since_year: int | None,
    until_year: int | None,
    as_of: date,
    derivation_basis: str | None,
) -> dict:
    """Per-fiscal-year completeness record (Task 10): a 10-K + up to 3
    standalone 10-Qs = 4 expected filings. `present` lists what was found;
    `missing` lists each absent expected filing with an EXPLICIT reason
    (`_missing_quarter_reason`). Filing-level completeness only — never
    zero-fills a dimension's value (see `_dimension_quarterly_absence`).

    `derivation_basis` (Task 16, spec: 'a projection-grounded label or
    verdict is marked as such') discloses what grounds this record's fiscal
    calendar — and thereby its fiscal_year label and every not_yet_filed/
    due-date verdict computed against `fiscal_year_end`: "dei-declared"
    (the year's own filed 10-K fixes the FYE — the filer's declaration in
    hand), "projected" (the +12mo forward projection of the prior declared
    FYE, an in-progress year whose declaration does not yet exist —
    sanctioned FALLBACK only), or None (no fiscal calendar derivable at
    all — since Task 18 only the unparseable-10-K-period edge, as every
    window-matched year carries a known/projected FYE and unmatched
    filings route to selection gaps instead of phantom years).
    Never omitted — a projection must stay distinguishable from a
    declared read."""
    expected_total = 4
    present: list[dict] = []
    missing: list[dict] = []

    if has_10k:
        present.append({"filing": "10-K"})
    elif fiscal_year_end is not None:
        reason, detail = _missing_quarter_reason(
            fiscal_year_end, fiscal_year, since_year, until_year, as_of
        )
        missing.append({"filing": "10-K", "reason": reason, "detail": detail})
    else:
        missing.append({
            "filing": "10-K", "reason": "unclassified",
            "detail": "fiscal year end unknown; cannot classify 10-K absence",
        })

    if fiscal_year_end is None:
        # Task 10 revision round 2 fatal fix: this branch used to DISCARD
        # `quarterly_filings` outright — reporting Q1/Q2/Q3 all missing even
        # when a filing was already in hand, because no fiscal calendar was
        # available to derive expected period ends from. A specific
        # Q1/Q2/Q3 label can't be derived without a fiscal calendar, but a
        # filing in hand is NOT reported missing — it is present, under the
        # generic "quarter" label (no fabricated per-quarter identity
        # claim). Since Task 18 removed the coverage caller's calendar
        # fallback, a window-matched year always carries a known/projected
        # `fiscal_year_end`, so this branch only fires on the
        # unparseable-10-K-period edge (where `quarterly_filings` is
        # empty) — kept as the honest degraded path, never a guess.
        for filing in quarterly_filings:
            present.append({
                "filing": "quarter",
                "accession": getattr(filing, "accession_no", None),
                "period_of_report": str(getattr(filing, "period_of_report", None)),
            })
    else:
        expected = _expected_quarterly_period_ends(fiscal_year_end)
        remaining = list(quarterly_filings)
        for label in _QUARTER_LABELS:
            expected_end = expected[label]
            match = _match_quarter_filing(expected_end, remaining)
            if match is not None:
                remaining.remove(match)
                present.append({
                    "filing": label,
                    "accession": getattr(match, "accession_no", None),
                    "period_of_report": str(getattr(match, "period_of_report", None)),
                })
            else:
                reason, detail = _missing_quarter_reason(
                    expected_end, fiscal_year, since_year, until_year, as_of
                )
                missing.append({"filing": label, "reason": reason, "detail": detail})

    return {
        "fiscal_year": fiscal_year,
        "status": "full" if len(present) == expected_total else "partial",
        "present_count": len(present),
        "expected_count": expected_total,
        "present": present,
        "missing": missing,
        "derivation_basis": derivation_basis,
    }


_MAX_PROJECTED_FISCAL_YEARS_FORWARD = 2
# LOOM-SIMPLIFY: shortcut=cap forward fiscal-calendar projection at 2 years
# past the latest known 10-K instead of projecting indefinitely |
# ceiling=a real filer whose quarterly filings still don't match after 2
# projected years (i.e. >2 consecutive fiscal years with zero 10-Ks on
# file) | upgrade=make the cap a parameter or grow it dynamically until
# `unmatched` is exhausted | ref=docs/loom/plans/2026-07-16-operational-kpi-
# quarterly.md Task 10 revision round 2 — every real filer's in-progress
# year is exactly 1 year past its latest 10-K, so 2 is generous headroom,
# never load-bearing for the shipped scenario (tested via AAPL FY2026 above).


def _assign_quarterly_filings_to_fiscal_years(
    annual_filings: list, quarterly_filings: list,
) -> tuple[dict[int, list], dict[int, date], list]:
    """Assign each quarterly filing to the fiscal year whose expected-quarter
    window (`_expected_quarterly_period_ends`) it falls within — NOT by the
    calendar year of the filing's OWN `period_of_report` (Task 10 revision
    round 1, fatal finding: a non-December fiscal-year-end quarter's
    calendar year and fiscal year diverge — live-verified AAPL FY2025 Q1
    ends 2024-12-28, calendar year 2024, fiscal year 2025 — calendar-year
    bucketing put it in the wrong year, fabricating a `fetch_error`/
    `unclassified` for a filing already in hand plus a phantom prior-year
    record).

    Builds one expected-quarter window per KNOWN fiscal year (every
    `annual_filings` 10-K's own `period_of_report` fixes that year's fiscal
    year end via `_expected_quarterly_period_ends`), then matches each
    quarterly filing against ALL of them (`_QUARTER_MATCH_TOLERANCE_DAYS`
    tolerance) — a filing lands in the one fiscal year whose window it
    actually falls inside.

    For filings that match no KNOWN window, PROJECTS the fiscal calendar
    FORWARD from the latest known 10-K's fiscal year end
    (`_subtract_months(fye, -12)` per year, up to
    `_MAX_PROJECTED_FISCAL_YEARS_FORWARD`) and re-matches against each
    projected window in turn (Task 10 revision round 2 fatal fix: every
    filer's CURRENT in-progress fiscal year has no 10-K yet, by definition
    — falling straight to the calendar-year fallback for that case
    reinstated the exact bug round 1 removed. Live-verified: AAPL FY2026's
    real Q1/Q2 10-Qs, filed months before FY2026's 10-K, match the
    projected FYE within 0-1 day — well inside tolerance).

    Returns `(by_year, projected_fiscal_year_ends, unmatched)`.
    `projected_fiscal_year_ends` maps a fiscal year that has NO 10-K yet but
    WAS resolved via forward projection to its projected fiscal year end —
    the caller (`_quarterly_completeness_report`) passes this through so
    that year's 10-K/Q3 absence is classified `not_yet_filed` (not
    `unclassified`) when its projected due date hasn't arrived.
    `unmatched` holds filings that fall inside NO known OR projected
    window. NEITHER caller buckets them by calendar year (Task 18 removed
    the old reporting-layer fallback): fiscal-range SELECTION leaves them
    guess-less (`_quarterly_fiscal_year_guesses`), and the COVERAGE caller
    surfaces each as an `index_visible_not_selected` selection gap
    (`_surface_selection_gaps`) — never a phantom calendar-year "present"
    claim for a filing that was never fetched."""
    known_fiscal_year_ends: dict[int, date] = {}
    windows: list[tuple[int, date]] = []
    for annual in annual_filings:
        # a 10-K's fiscal-year label == the calendar year of its period end
        # (SEC convention — the annual-form index guess, see
        # `_filing_period_end_calendar_year`)
        year = _filing_period_end_calendar_year(annual)
        period = getattr(annual, "period_of_report", None)
        if year is None or not period:
            continue
        try:
            fiscal_year_end = date.fromisoformat(str(period))
        except ValueError:
            continue
        known_fiscal_year_ends[year] = fiscal_year_end
        windows.extend(
            (year, expected_end)
            for expected_end in _expected_quarterly_period_ends(fiscal_year_end).values()
        )

    def _parsed_period(filing) -> date | None:
        period = getattr(filing, "period_of_report", None)
        if not period:
            return None
        try:
            return date.fromisoformat(str(period))
        except ValueError:
            return None

    def _match(actual: date, candidate_windows: list[tuple[int, date]]) -> int | None:
        return next(
            (
                year for year, expected_end in candidate_windows
                if abs((actual - expected_end).days) <= _QUARTER_MATCH_TOLERANCE_DAYS
            ),
            None,
        )

    by_year: dict[int, list] = {}
    remaining: list = []
    for filing in quarterly_filings:
        actual = _parsed_period(filing)
        matched_year = _match(actual, windows) if actual is not None else None
        if matched_year is not None:
            by_year.setdefault(matched_year, []).append(filing)
        else:
            remaining.append(filing)

    projected_fiscal_year_ends: dict[int, date] = {}
    if known_fiscal_year_ends and remaining:
        year = max(known_fiscal_year_ends)
        fye = known_fiscal_year_ends[year]
        for _ in range(_MAX_PROJECTED_FISCAL_YEARS_FORWARD):
            if not remaining:
                break
            year += 1
            fye = _subtract_months(fye, -12)
            projected_windows = [
                (year, expected_end)
                for expected_end in _expected_quarterly_period_ends(fye).values()
            ]
            still_remaining = []
            matched_any = False
            for filing in remaining:
                actual = _parsed_period(filing)
                if actual is not None and _match(actual, projected_windows) is not None:
                    by_year.setdefault(year, []).append(filing)
                    matched_any = True
                else:
                    still_remaining.append(filing)
            if matched_any:
                projected_fiscal_year_ends[year] = fye
            remaining = still_remaining

    return by_year, projected_fiscal_year_ends, remaining


_SELECTION_GAP_QUARTER_ASSOCIATION_DAYS = 46


def _quarterly_completeness_report(
    annual_filings: list,
    quarterly_filings: list,
    since_year: int | None,
    until_year: int | None,
    as_of: date,
) -> tuple[list[dict], list[dict]]:
    """Build one `_quarterly_year_completeness` record per fiscal year the
    filings INDEX evidences (Task 18, docs/loom/plans/2026-07-16-
    operational-kpi-quarterly.md, supersedes old T10), from ALREADY-FETCHED
    filing-list metadata (never a fresh fetch per year). Returns
    `(report, selection_gaps)`.

    The comparison universe is the FULL filings index, NOT the requested
    range and NOT the selected set: an out-of-range year with index
    filings still gets a record, its absent quarters classified
    `out_of_requested_range` on their FISCAL year — so a caller can always
    tell "you never asked for it" from "it should be there and isn't".

    Fiscal years are keyed off each 10-K's OWN `period_of_report` calendar
    year (`_filing_period_end_calendar_year` — the fiscal-year LABEL for a
    10-K by SEC convention, whose period end IS the fiscal year end).
    Quarterly filings are grouped into fiscal years by
    `_assign_quarterly_filings_to_fiscal_years` (window-matched against
    the 10-K's fiscal calendar, never the quarter's own calendar year —
    Task 10 revision round 1 fatal finding), with a PROJECTED-forward
    fiscal calendar for a year with no 10-K yet (Task 10 revision round 2
    fatal fix — every filer's in-progress current year, always).

    A filing matching no known OR projected window is EXACTLY the filing
    the pre-fetch selection derivation left guess-less and never selected
    (`_quarterly_fiscal_year_guesses` runs on the same windows). Task 18
    killed the old reporting-layer calendar-year fallback for it (trap 1
    of docs/loom/memory/fiscal-year-derive-per-fact-against-filing-
    calendar.md — it could claim a phantom year "present" for a filing
    that was never even fetched): each such filing now surfaces as a
    SELECTION GAP — `index_visible_not_selected` — in `selection_gaps`
    (the ONE DQC schema), and, when its period sits within
    `_SELECTION_GAP_QUARTER_ASSOCIATION_DAYS` of a reported year's missing
    quarter slot, on that quarter's `missing` entry too (positive index
    evidence overriding any date-inferred state — never not_yet_filed).
    The association bound is half the ~91-day inter-quarter spacing:
    nearer than that, "nearest missing quarter" is unambiguous; farther,
    the filing stays an unattached gap entry rather than a fabricated
    quarter identity. This is a REPORTING association only — the filing's
    facts are never emitted and no fiscal label is minted from it (the
    never-nearest-guess red line binds labels, not gap reporting)."""
    by_year_10k: dict[int, object] = {}
    for f in annual_filings:
        y = _filing_period_end_calendar_year(f)
        if y is not None:
            by_year_10k[y] = f

    by_year_10q, projected_fiscal_year_ends, unmatched = (
        _assign_quarterly_filings_to_fiscal_years(annual_filings, quarterly_filings)
    )

    fiscal_years = sorted(set(by_year_10k) | set(by_year_10q))

    report = []
    year_ends: dict[int, date] = {}
    for year in fiscal_years:
        tenk = by_year_10k.get(year)
        fiscal_year_end = None
        derivation_basis = None
        if tenk is not None:
            period = getattr(tenk, "period_of_report", None)
            if period:
                try:
                    fiscal_year_end = date.fromisoformat(str(period))
                except ValueError:
                    fiscal_year_end = None
            if fiscal_year_end is not None:
                # The year's own filed 10-K fixes the FYE — the filer's
                # declaration in hand (Task 16 basis disclosure).
                derivation_basis = "dei-declared"
        elif year in projected_fiscal_year_ends:
            fiscal_year_end = projected_fiscal_year_ends[year]
            # In-progress year: no 10-K/declaration exists yet, the
            # calendar rests on the +12mo forward projection — marked so a
            # projection-grounded verdict is never mistaken for a declared
            # read (Task 16).
            derivation_basis = "projected"
        if fiscal_year_end is not None:
            year_ends[year] = fiscal_year_end
        report.append(
            _quarterly_year_completeness(
                fiscal_year=year,
                fiscal_year_end=fiscal_year_end,
                has_10k=tenk is not None,
                quarterly_filings=by_year_10q.get(year, []),
                since_year=since_year,
                until_year=until_year,
                as_of=as_of,
                derivation_basis=derivation_basis,
            )
        )

    selection_gaps = _surface_selection_gaps(unmatched, report, year_ends)
    return report, selection_gaps


def _surface_selection_gaps(
    unmatched: list, report: list[dict], year_ends: dict[int, date],
) -> list[dict]:
    """Task 18: turn each window-unmatched (therefore never-selected) index
    filing into an `index_visible_not_selected` DQC flag, and stamp the
    state onto the nearest missing quarter entry of a reported year when
    the filing sits within `_SELECTION_GAP_QUARTER_ASSOCIATION_DAYS` of
    that quarter's expected end (see `_quarterly_completeness_report` for
    the bound's rationale). Mutates the matched `missing` entries in
    `report`; returns the flag list (empty = ran, none found)."""
    # (year, label, expected_end, missing_entry) per missing Q1/Q2/Q3 slot.
    missing_slots: list[tuple[int, str, date, dict]] = []
    for record in report:
        fye = year_ends.get(record["fiscal_year"])
        if fye is None:
            continue
        expected = _expected_quarterly_period_ends(fye)
        for entry in record["missing"]:
            if entry["filing"] in expected:
                missing_slots.append(
                    (record["fiscal_year"], entry["filing"],
                     expected[entry["filing"]], entry)
                )

    gaps: list[dict] = []
    for filing in sorted(
        unmatched,
        key=lambda f: (str(getattr(f, "period_of_report", "")),
                       str(getattr(f, "accession_no", ""))),
    ):
        accession = getattr(filing, "accession_no", None)
        period = str(getattr(filing, "period_of_report", None))
        try:
            actual = date.fromisoformat(period)
        except ValueError:
            actual = None
        nearest = None
        if actual is not None and missing_slots:
            nearest = min(
                missing_slots, key=lambda s: abs((actual - s[2]).days)
            )
            if abs((actual - nearest[2]).days) > (
                _SELECTION_GAP_QUARTER_ASSOCIATION_DAYS
            ):
                nearest = None
        attached = ""
        if nearest is not None:
            year, label, _expected_end, entry = nearest
            entry["reason"] = "index_visible_not_selected"
            entry["detail"] = (
                f"a 10-Q ({accession}, period {period}) is present in the "
                "filings index near this quarter but matched no "
                "known/projected fiscal-quarter window, so the pre-fetch "
                "selection derivation could not place it and it was never "
                "selected/fetched — positive index evidence, never "
                "not_yet_filed, never calendar-bucketed"
            )
            entry["accession"] = accession
            attached = f"; nearest missing quarter slot FY{year}-{label}"
        gaps.append({
            "type": "index_visible_not_selected",
            "old": None,
            "new": None,
            "accessions": [accession],
            "reason": (
                f"10-Q {accession} (period {period}) is present in the "
                "filings index but matched no known/projected "
                "fiscal-quarter window: the pre-fetch selection derivation "
                "left it guess-less, so it was never selected/fetched — a "
                "SELECTION gap, not an index absence" + attached
            ),
        })
    return gaps


def _apply_observed_failure_states(
    report: list[dict],
    fetch_failures: list[dict],
    unlabelable_filings: list[dict],
) -> None:
    """Task 19: override a quarter's index-presence claim with an OBSERVED
    per-filing failure state — the same precedence rule as
    `_surface_selection_gaps` (evidence in hand beats index inference,
    docs/loom/memory/fail-closed-default-must-be-enforced-not-emergent.md):

    - `attempted_fetch_failed`: the filing's download/XBRL parse RAISED at
      the fetch site (retryable — the one absence-adjacent state allowed to
      claim retryability, because the caught exception is the ground; this
      is the observed counterpart of the `fetch_error` reservation in
      `_missing_quarter_reason`).
    - `filed_but_unlabelable`: the filing fetched fine but its dei fiscal
      calendar failed the fail-loud derivation, so the whole filing is
      quarantined from fiscal-labeled output.

    `_quarterly_completeness_report` marks such a filing "present" from
    index metadata alone — silently claiming it covered would be exactly
    the dishonesty the spec forbids ('never silently covered'). Each
    matching `present` entry MOVES to `missing` carrying the observed
    reason + the grounding detail from its DQC flag, and the record's
    `present_count`/`status` are recomputed. Mutates `report` in place
    (same convention as `_surface_selection_gaps`); the flags themselves
    ride `coverage.fetch_failures` / `coverage.unlabelable_filings`."""
    observed: dict[str, tuple[str, str]] = {}
    for flag in fetch_failures:
        for accession in flag["accessions"]:
            observed[accession] = ("attempted_fetch_failed", flag["reason"])
    for flag in unlabelable_filings:
        for accession in flag["accessions"]:
            observed[accession] = ("filed_but_unlabelable", flag["reason"])
    if not observed:
        return
    for record in report:
        kept: list[dict] = []
        for entry in record["present"]:
            state = observed.get(entry.get("accession"))
            if state is None:
                kept.append(entry)
                continue
            reason, detail = state
            record["missing"].append({
                "filing": entry["filing"],
                "reason": reason,
                "detail": detail,
                "accession": entry.get("accession"),
            })
        record["present"] = kept
        record["present_count"] = len(kept)
        record["status"] = (
            "full" if len(kept) == record["expected_count"] else "partial"
        )


def _fact_dimensional_signature(fact: dict) -> tuple:
    """(concept, sorted dimensions items, consolidation) — the identity a
    dimensional-revenue fact is compared by, ignoring value/period/accession
    so a 10-K fact and a 10-Q fact for the SAME breakdown match regardless
    of which filing reported them."""
    return (
        fact.get("concept"),
        tuple(sorted(fact.get("dimensions", {}).items())),
        fact.get("consolidation"),
    )


def _fact_effective_fiscal_year(
    fact: dict, annual_windows: list[tuple[int, date]],
) -> int | None:
    """The FISCAL year `fact` belongs to, window-matched against
    `annual_windows` (each known 10-K's `_expected_quarterly_period_ends`,
    built by the caller) — mirrors `_assign_quarterly_filings_to_fiscal_
    years` at fact granularity, never trusting a tagged year alone (Task
    10 revision round 2, finding 2: the pre-Task-13 `fiscal_year` field
    was the CALENDAR year of `period_end`, a 100% false-flag rate
    live-verified on a January-FYE filer, NVDA; since Task 13 the emitted
    field is the honestly-derived per-fact fiscal label, so the window
    match is defense-in-depth for legacy-shaped inputs). Falls back to
    `fact['fiscal_year']` when `period_end` is absent/unparseable or
    matches no known window — the same escape `_assign_quarterly_filings_
    to_fiscal_years` uses for a filing it has no fiscal reference to place
    (never a crash, never a guess beyond what's derivable)."""
    period = fact.get("period_end")
    try:
        actual = date.fromisoformat(str(period)) if period else None
    except ValueError:
        actual = None
    if actual is not None:
        matched = next(
            (
                year for year, expected_end in annual_windows
                if abs((actual - expected_end).days) <= _QUARTER_MATCH_TOLERANCE_DAYS
            ),
            None,
        )
        if matched is not None:
            return matched
    return fact.get("fiscal_year")


def _dimension_quarterly_absence(
    annual_facts: list[dict], quarterly_facts: list[dict]
) -> list[dict]:
    """Flag every dimensional-revenue signature present in `annual_facts`
    (10-K) that carries NO fact in `quarterly_facts` (10-Q) for the SAME
    FISCAL year — Task 10: 'a dimension present in the 10-K but absent
    from the 10-Qs' is reported as `"no_quarterly_coverage"`, distinct from
    a real zero and from a discontinued segment (never inferable from a
    flag alone — that judgment is the caller's). Never zero-filled: the
    returned entry carries no `value` key, only the identifying signature.

    A quarterly fact's fiscal year is resolved via `_fact_effective_fiscal_
    year` (window-matched against each annual fact's OWN `period_end`,
    which for a 10-K IS the fiscal year end) — never the quarterly fact's
    own tagged `fiscal_year`, which is a calendar-year label that diverges
    from the fiscal year for a non-December FYE (Task 10 revision round 2,
    finding 2 — same defect class as the filing-level grouping fix)."""
    annual_windows: list[tuple[int, date]] = []
    seen_years: set = set()
    for f in annual_facts:
        fy = f.get("fiscal_year")
        period = f.get("period_end")
        if fy is None or period is None or fy in seen_years:
            continue
        try:
            fye = date.fromisoformat(str(period))
        except ValueError:
            continue
        seen_years.add(fy)
        annual_windows.extend(
            (fy, expected_end)
            for expected_end in _expected_quarterly_period_ends(fye).values()
        )

    quarterly_signatures = {
        (_fact_effective_fiscal_year(f, annual_windows), _fact_dimensional_signature(f))
        for f in quarterly_facts
    }
    seen = set()
    flags = []
    for fact in annual_facts:
        key = (fact.get("fiscal_year"), _fact_dimensional_signature(fact))
        if key in quarterly_signatures or key in seen:
            continue
        seen.add(key)
        flags.append({
            "concept": fact.get("concept"),
            "dimensions": fact.get("dimensions"),
            "consolidation": fact.get("consolidation"),
            "fiscal_year": fact.get("fiscal_year"),
            "flag": "no_quarterly_coverage",
        })
    return flags


def _quarterly_fiscal_year_guesses(
    annual_filings: list, quarterly_filings: list,
) -> dict[str, int]:
    """accession -> GUESSED declared fiscal year for each quarterly filing —
    the sanctioned PRE-FETCH index-metadata derivation (Task 13; spec:
    selection runs before any filing is downloaded, has no dei tags in
    hand, and MAY derive candidate fiscal years from form /
    `period_of_report` / filing date, for selection purposes only).

    Windows come from the companion annual index via
    `_assign_quarterly_filings_to_fiscal_years`: each 10-K's own period end
    fixes that fiscal year's expected quarter windows, and the in-progress
    year (no 10-K yet, by definition) is projected forward — NEVER
    `period_of_report[:4]`, which is the calendar year (trap 1 of the
    root-cause defect, docs/loom/memory/fiscal-year-derive-per-fact-
    against-filing-calendar.md: NVDA's FY2026 quarters all end in calendar
    2025). For a fixed-December-FYE filer the window match reproduces the
    calendar year exactly, so selection there is byte-identical to the
    old behaviour.

    The value is explicitly a CANDIDATE GUESS: the fetched filing's own
    `dei:DocumentFiscalYearFocus` is the truth, and range membership is
    reconciled against it post-fetch (Task 14). A filing matching no known
    or projected window has NO derivable candidate and is absent from the
    map — it is never calendar-bucketed into a fiscal range (its selection
    gap surfaces at the coverage layer, Task 18)."""
    by_year, _projected, _unmatched = _assign_quarterly_filings_to_fiscal_years(
        annual_filings, quarterly_filings
    )
    return {
        accession: year
        for year, filings in by_year.items()
        for accession in (getattr(f, "accession_no", None) for f in filings)
        if accession is not None
    }


def _fiscal_year_guess_in_range(
    year: int | None, since_year: int, until_year: int | None,
) -> bool:
    """Whether a guessed declared fiscal year falls in the INCLUSIVE range
    `[since_year, until_year]`; `until_year=None` leaves the upper bound
    open ([since_year, latest]). A filing with no derivable guess
    (`year=None`) is not range-selectable (never guessed into the range)."""
    if year is None or year < since_year:
        return False
    return until_year is None or year <= until_year


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SEC EDGAR data adapter for investing-toolkit"
    )
    parser.add_argument("--ticker", help="US stock ticker (e.g. NVDA)")
    parser.add_argument("--accession", help="Filing accession number (e.g. 0001045810-24-000316)")
    parser.add_argument(
        "--action",
        required=True,
        choices=["cik", "facts", "filings", "narrative"],
        help="Which SEC endpoint / transformation to run",
    )
    parser.add_argument("--concept", help="XBRL us-gaap concept (e.g. Revenues, NetIncomeLoss)")
    parser.add_argument(
        "--forms",
        help="Comma-separated form types to filter (e.g. 10-K,10-Q,8-K)",
    )
    parser.add_argument(
        "--limit", type=int, default=20,
        help="Max filings to return for --action filings (default 20)",
    )
    parser.add_argument(
        "--since-days", type=int, default=None,
        help=(
            "Fetch --action filings by a DATE window (today - N days) instead "
            "of --limit's row count -- overrides --limit's truncation (see "
            "narrative_filings_window_days for a policy-derived value)"
        ),
    )
    parser.add_argument("--no-cache", action="store_true", help="Bypass cache for this run")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    # Optional cache bust
    if args.no_cache:
        # Only blow away the file that's about to be written
        if args.ticker:
            t = args.ticker.upper()
            tmap = load_ticker_map()
            entry = tmap.get("tickers", {}).get(t) if "error" not in tmap else None
            if entry:
                cik = entry["cik"]
                for key in (
                    f"facts_{cik:010d}",
                    f"submissions_{cik:010d}",
                    f"concept_{cik:010d}_{args.concept}" if args.concept else "",
                ):
                    if key:
                        p = cache_util.cache_path("sec_edgar", key)
                        if p.exists():
                            p.unlink()
        if args.accession:
            # The edgartools narrative cache key (Task 12) is
            # narrative_sections_{accession} — DISTINCT from the retired regex
            # fetch_narrative's narrative_{accession}; unlink the NEW key so
            # --no-cache actually clears what fetch_narrative_sections writes.
            p = cache_util.cache_path(
                "sec_edgar", f"narrative_sections_{args.accession}"
            )
            if p.exists():
                p.unlink()

    if args.action == "cik":
        if not args.ticker:
            print("--ticker required for --action cik", file=sys.stderr)
            sys.exit(2)
        result = action_cik(args.ticker)

    elif args.action == "facts":
        if not args.ticker:
            print("--ticker required for --action facts", file=sys.stderr)
            sys.exit(2)
        result = action_facts(args.ticker, args.concept)

    elif args.action == "filings":
        if not args.ticker:
            print("--ticker required for --action filings", file=sys.stderr)
            sys.exit(2)
        forms = (
            [f.strip() for f in args.forms.split(",") if f.strip()]
            if args.forms else None
        )
        result = action_filings(args.ticker, forms, args.limit, args.since_days)

    elif args.action == "narrative":
        if not args.accession:
            print("--accession required for --action narrative", file=sys.stderr)
            sys.exit(2)
        result = action_narrative(args.accession)

    print(json.dumps(result, default=str, indent=2))
    sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
    main()
