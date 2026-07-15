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
_CONSOLIDATION_AXIS_LOCAL_NAME = "ConsolidationItemsAxis"


def _is_dimensional_revenue_axis(axis: str | None) -> bool:
    """True when `axis` (colon form, e.g. "srt:ProductOrServiceAxis") is one
    of the three axis local names, REGARDLESS of its `us-gaap:`/`srt:`
    namespace prefix — see the module note above: never filter a single
    namespace."""
    if not axis:
        return False
    return axis.rsplit(":", 1)[-1] in _DIMENSIONAL_REVENUE_AXIS_LOCAL_NAMES


_DEFERRED_REVENUE_CONCEPT_PREFIXES = (
    "ContractWithCustomerLiabilityRevenue",
)


def _is_revenue_concept(concept: str | None) -> bool:
    """True when `concept`'s local name (post `:`) contains "Revenue" — e.g.
    `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` (post-2018)
    or `us-gaap:SalesRevenueNet` (pre-2018) — EXCLUDING deferred-revenue /
    contract-liability reconciliation concepts (e.g.
    `ContractWithCustomerLiabilityRevenueRecognized`,
    `...RecognizedExcludingOpeningBalance`) that merely contain "Revenue"
    but are not operating revenue (plan Task 5,
    docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md)."""
    if not concept:
        return False
    local_name = concept.rsplit(":", 1)[-1]
    if "Revenue" not in local_name:
        return False
    return not local_name.startswith(_DEFERRED_REVENUE_CONCEPT_PREFIXES)


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


def _dimension_signature(fact: dict) -> tuple[dict[str, str], str | None]:
    """Build (dimensions, consolidation) from `fact`'s per-row
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
    name (namespace prefix stripped). `srt:ConsolidationItemsAxis` is a
    reconciliation QUALIFIER, not a breakdown axis — captured separately as
    `consolidation`, never folded into `dimensions` as a second axis."""
    dimensions: dict[str, str] = {}
    consolidation: str | None = None
    for key, value in fact.items():
        if not key.startswith("dim_") or value is None or _is_nan(value):
            continue
        _prefix, namespace, axis_local = key.split("_", 2)
        member_local = str(value).rsplit(":", 1)[-1]
        if axis_local == _CONSOLIDATION_AXIS_LOCAL_NAME:
            consolidation = member_local
        elif _is_dimensional_revenue_axis(f"{namespace}:{axis_local}"):
            dimensions[axis_local[: -len("Axis")]] = member_local
    return dimensions, consolidation


def _is_dimensional_revenue_fact(fact: dict) -> bool:
    """The combined filter predicate for `extract_dimensional_revenue`:
    dimensioned + at least one REAL breakdown axis present on the row
    (`_dimension_signature`, both namespaces via `_is_dimensional_revenue_axis`)
    + concept is revenue-shaped (`_is_revenue_concept`) + a reported numeric
    value (never NaN — mirrors `_build_statement_cells`'s `_is_nan` skip; a
    placeholder concept with no reported number is never fabricated as 0)."""
    if not fact.get("is_dimensioned"):
        return False
    if not _is_revenue_concept(fact.get("concept")):
        return False
    if _is_nan(fact.get("numeric_value")):
        return False
    dimensions, _consolidation = _dimension_signature(fact)
    return bool(dimensions)


def _build_dimensional_revenue_fact(fact: dict, ticker: str, accession: str, filed) -> dict:
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

    fiscal_year is DERIVED from period_end (the year the fiscal period
    ENDS) — NEVER taken from edgartools' raw `fiscal_year` column, which is
    unreliable for prior-year comparatives: live-verified on AAPL's 2025
    10-K, the iPhone fact with period_end 2024-09-28 is column-labeled
    fiscal_year=2025 but is really FY2024. Shipping the raw column mislabels
    every prior-year comparative point."""
    dimensions, consolidation = _dimension_signature(fact)
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
    return {
        "concept": fact.get("concept"),
        "dimensions": dimensions,
        "consolidation": consolidation,
        "value": float(fact.get("numeric_value")),
        "period_end": period_end,
        "fiscal_year": int(period_end[:4]),
        "accession": accession,
        "filed": filed,
    }


def _filing_period_year(filing) -> int | None:
    """The fiscal year a filing REPORTS, from its filings-list metadata
    (`period_of_report`, the fiscal-period-end date string) — NOT by fetching
    its `.xbrl()`. edgartools exposes `period_of_report` on every real 10-K
    Filing (live-verified 2026-07-15, `_filing_ref`:851 relies on it; see the
    real-Filing-shape header at :808), so range selection reads it directly.
    Returns None when it is absent/unparseable (never guessed)."""
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
        return _dimensional_revenue_error_slot(
            ticker, form, f"form {form!r} not available within the lookup window",
        )

    if since_year is None:
        # Default (latest-only) path — pick the single most-recent exact-form
        # filing. Behaviorally identical to the pre-range collapse.
        selected = [max(exact_filings, key=lambda f: f.filing_date)]
    else:
        # Range path — select from filings-list metadata (period_of_report),
        # NOT by fetching every `.xbrl()` first (the plan's kickoff decision).
        selected = sorted(
            (
                f for f in exact_filings
                if _filing_in_year_range(f, since_year, until_year)
            ),
            key=lambda f: f.filing_date,
        )
        if not selected:
            return _dimensional_revenue_error_slot(
                ticker, form,
                f"no {form!r} filing reports a fiscal period within "
                f"[{since_year}, {until_year if until_year is not None else 'latest'}]",
            )

    facts = []
    for filing in selected:
        xb = filing.xbrl()
        facts_records = xb.facts.to_dataframe().to_dict("records")
        accession = filing.accession_no
        filed = _filing_date_iso(filing.filing_date)
        facts.extend(
            _build_dimensional_revenue_fact(fact, ticker, accession, filed)
            for fact in facts_records
            if _is_dimensional_revenue_fact(fact)
        )

    return {"company": ticker, "facts": facts}


def _filing_in_year_range(filing, since_year: int, until_year: int | None) -> bool:
    """Whether `filing`'s reported fiscal year (`_filing_period_year`) falls in
    the INCLUSIVE range `[since_year, until_year]`; `until_year=None` leaves the
    upper bound open ([since_year, latest]). A filing whose period year is
    unknown is not range-selectable (never guessed into the range)."""
    year = _filing_period_year(filing)
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
