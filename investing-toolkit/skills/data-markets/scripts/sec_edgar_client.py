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
  (b) HTML filing narrative via Item-section regex parsing

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

  # Parse Item sections of a specific filing
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
from datetime import datetime, timezone
from html.parser import HTMLParser
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


def list_filings(cik: int, forms: list[str] | None, limit: int) -> list[dict]:
    """Return recent filings, optionally filtered by form."""
    sub = fetch_submissions(cik)
    if "error" in sub:
        return []

    recent = sub.get("data", {}).get("filings", {}).get("recent", {})
    forms_list = recent.get("form", [])
    dates_list = recent.get("filingDate", [])
    accn_list = recent.get("accessionNumber", [])
    primary_doc_list = recent.get("primaryDocument", [])
    primary_desc_list = recent.get("primaryDocDescription", [])

    rows: list[dict] = []
    for i in range(len(forms_list)):
        form = forms_list[i]
        if forms and form not in forms:
            continue
        rows.append({
            "form": form,
            "filingDate": dates_list[i] if i < len(dates_list) else None,
            "accessionNumber": accn_list[i] if i < len(accn_list) else None,
            "primaryDocument": primary_doc_list[i] if i < len(primary_doc_list) else None,
            "primaryDocDescription": primary_desc_list[i] if i < len(primary_desc_list) else None,
        })
        if len(rows) >= limit:
            break
    return rows


# ---------------------------------------------------------------------------
# HTML narrative parsing
# ---------------------------------------------------------------------------

class _TextExtractor(HTMLParser):
    """Strip HTML, collapse whitespace, preserve line breaks at block boundaries."""

    BLOCK_TAGS = {
        "p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6",
        "table", "section", "article", "hr",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip_depth += 1
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag in self.BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data):
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        # Collapse runs of whitespace except newlines
        raw = re.sub(r"[ \t\u00a0]+", " ", raw)
        # Collapse multiple newlines
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        return raw.strip()


_ITEM_HEADER_RE = re.compile(
    r"^\s*Item\s+(\d+[A-Z]?)\.\s*(.{2,150}?)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def parse_item_sections(plain_text: str) -> dict[str, str]:
    """Split plain text into Item sections by regex-detected headers."""
    matches = list(_ITEM_HEADER_RE.finditer(plain_text))
    if not matches:
        return {}

    # SEC 10-K/10-Q bodies usually repeat the TOC Item headers; we want
    # the section boundaries, not the TOC. Strategy: collect all hits;
    # for each unique Item key, keep the span to next distinct Item header
    # whose starting offset is after the current, but skip if the detected
    # "title" field is empty/too short (TOC-like).
    sections: dict[str, str] = {}
    for idx, m in enumerate(matches):
        num = m.group(1).upper()
        title = m.group(2).strip()
        # Skip likely TOC hits: title shorter than 5 chars or purely numeric
        if len(title) < 5:
            continue
        key = f"Item {num}. {title}"
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(plain_text)
        body = plain_text[start:end].strip()
        # Keep only the longest body per Item number (body text vs TOC entry)
        existing_key = next(
            (k for k in sections if k.startswith(f"Item {num}.")),
            None,
        )
        if existing_key is None or len(body) > len(sections[existing_key]):
            if existing_key and existing_key != key:
                del sections[existing_key]
            sections[key] = body
    return sections


def _accession_nodash(accession: str) -> str:
    return accession.replace("-", "")


def fetch_narrative(accession: str) -> dict:
    """Fetch primary doc HTML for an accession and parse Item sections."""
    path = cache_util.cache_path("sec_edgar", f"narrative_{accession}")
    cached = cache_util.load_cache(path, TTL_NARRATIVE)
    if cached:
        cached["_cache"] = "hit"
        return cached

    # Need CIK for accession → look it up via EDGAR's accession redirect.
    # Accession format: XXXXXXXXXX-YY-NNNNNN where first 10 digits = filer CIK.
    try:
        cik_int = int(accession.split("-")[0])
    except (ValueError, IndexError):
        return {"error": f"Malformed accession number: {accession}"}

    # Must look up primaryDocument via submissions or filing index.
    # Quickest: fetch filing-index.json at the accession folder.
    accn_nodash = _accession_nodash(accession)
    index_url = (
        f"https://data.sec.gov/submissions/CIK{cik_int:010d}.json"
    )
    sub = fetch_submissions(cik_int)
    primary_doc = None
    form_type = None
    filing_date = None
    if "error" not in sub:
        recent = sub.get("data", {}).get("filings", {}).get("recent", {})
        accn_list = recent.get("accessionNumber", [])
        try:
            idx = accn_list.index(accession)
            primary_doc = recent.get("primaryDocument", [None])[idx]
            form_type = recent.get("form", [None])[idx]
            filing_date = recent.get("filingDate", [None])[idx]
        except ValueError:
            pass

    if not primary_doc:
        # Fall back: fetch index.json from Archives
        idx_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{accn_nodash}/index.json"
        idx = _sec_get(idx_url)
        if isinstance(idx, dict) and "error" not in idx:
            items = idx.get("directory", {}).get("item", [])
            # Pick first htm/html that isn't an exhibit index
            for item in items:
                name = item.get("name", "")
                if name.endswith((".htm", ".html")) and "index" not in name.lower():
                    primary_doc = name
                    break

    if not primary_doc:
        return {"error": f"Could not resolve primary document for accession {accession}"}

    doc_url = SEC_ARCHIVES_URL.format(
        cik_int=cik_int, accession_nodash=accn_nodash, doc=primary_doc
    )
    # Override Host header for this endpoint
    html = _sec_get(doc_url, as_json=False)
    if isinstance(html, dict) and "error" in html:
        return html

    extractor = _TextExtractor()
    extractor.feed(html)
    plain = extractor.text()
    sections = parse_item_sections(plain)

    result = {
        "accession": accession,
        "cik": cik_int,
        "form": form_type,
        "filingDate": filing_date,
        "primaryDocument": primary_doc,
        "doc_url": doc_url,
        "fetched_at": _now_iso(),
        "_cache": "miss",
        "sections": sections,
        "section_count": len(sections),
        "_provenance": _make_provenance(filing_date),
    }
    cache_util.save_cache(path, result)
    return result


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


def action_filings(ticker: str, forms: list[str] | None, limit: int) -> dict:
    _log("filings fetch", f"{ticker} forms={forms or 'ALL'} limit={limit}")
    t0 = time.monotonic()
    cik_info = resolve_cik(ticker)
    if "error" in cik_info:
        return cik_info
    cik = cik_info["cik"]

    rows = list_filings(cik, forms, limit)
    latest_date = rows[0]["filingDate"] if rows else None
    _log("filings done", f"{ticker} {len(rows)} rows in {time.monotonic() - t0:.1f}s")
    return {
        "ticker": ticker,
        "cik": cik,
        "title": cik_info.get("title"),
        "action": "filings",
        "forms_filter": forms,
        "limit": limit,
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


def acquire_filing(
    identifier: str | int | None = None,
    *,
    form: str | None = None,
    accession: str | None = None,
) -> dict:
    """Acquire a 10-K/10-Q/8-K filing reference via edgartools.

    Two acquisition modes (edgartools 5.42.0):
      - by ``accession``: ``edgar.get_by_accession_number(accession)``
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
    identity_error = _ensure_edgar_identity()
    if identity_error is not None:
        return identity_error

    import edgar

    if accession is not None:
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
        return _filing_ref(filing)

    # ticker / CIK path
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
#   TenK: `management_discussion` (Item 7) + `risk_factors` (Item 1A) are `str`
#     properties; an item absent from THIS filing yields `None` (issue #710).
#   TenQ: NO `management_discussion` property — Item 2 (MD&A) is read via the
#     subscript `obj["Part I, Item 2"]` -> `str` (also `None` when absent).
#
# SECTION-OBJECT CONTRACT (established here, reused by Tasks 4-12) --------------
# `segment_filing()` returns a LIST of per-item section dicts in requested order:
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
#       by pack.py's `_status`, and the slot NAMES the missing item so a
#       requested-but-absent item is never dropped or fabricated.
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


def _segment_10k(obj, filing) -> list[tuple[str, object]]:
    """Requested (item id, text-thunk) pairs for a 10-K TenK typed object.

    Item 7 (MD&A) / Item 1A (Risk Factors) via the grounded `str` properties;
    each yields `None` when the item is absent from this filing (issue #710).
    The text element is a ZERO-ARG THUNK (not the resolved text) so
    `segment_filing` can evaluate each item's property access under its own
    try/except and ISOLATE a mid-parse throw to that one item's error slot
    (Task 8) — the other items still segment. `filing` is unused here (10-K text
    is on `obj`); it is in the signature for the uniform extractor contract that
    8-K's exhibit-following needs."""
    return [
        ("Item 7", lambda: obj.management_discussion),
        ("Item 1A", lambda: obj.risk_factors),
    ]


def _segment_10q(obj, filing) -> list[tuple[str, object]]:
    """Requested (item id, text-thunk) pairs for a 10-Q TenQ typed object.

    TenQ exposes no MD&A property; Item 2 is read via the subscript
    `obj["Part I, Item 2"]` (`str`, or `None` when absent). The text element is a
    ZERO-ARG THUNK so a subscript throw is isolated per item by `segment_filing`
    (Task 8). `filing` unused (uniform extractor signature)."""
    return [
        ("Item 2", lambda: obj["Part I, Item 2"]),
    ]


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
    """Per-item entries for an 8-K, following each reported exhibit-bearing item
    to its Exhibit 99.x text — a success triple ``(item id, exhibit text,
    {"exhibit": filename})`` when resolvable, else a loud missing-exhibit gap
    dict (never a silent skip, an empty section, a positional guess, or an
    uncaught IndexError).

    Live-captured shape (edgartools 5.42.0; ``filing.obj()`` -> ``CurrentReport``,
    NOT ``EightK`` — plan-grounding correction): ``obj.items`` is a list of
    reported item-id strings; ``obj.press_releases`` is the collection of EX-99.x
    press-release exhibits, each a ``PressRelease`` with ``.document`` (the
    EX-99.x filename) + ``.text()`` (the exhibit body). We read the exhibit text
    (not the 8-K body announcement) and record the source exhibit filename in the
    section's `exhibit` provenance field.

    Only the unambiguous 1:1 case (exactly one reported exhibit-bearing item and
    exactly one press-release exhibit) is paired — there the correspondence is
    determined, not guessed. Any other shape (no exhibit for a reported item, a
    count mismatch, or >=2 exhibit-bearing items whose item->exhibit mapping is
    non-positional) emits a loud named gap per affected item: silent-wrong is the
    enemy, so we never mis-attribute an exhibit to the wrong item (T4 review
    finding, folded in by Task 5).

    LOOM-SIMPLIFY: shortcut=a >=2-exhibit-item 8-K (or count mismatch) is emitted
    as loud per-item gaps rather than resolving each reported item body's
    "Exhibit 99.x" cross-reference to map it to the right exhibit | ceiling=a real
    8-K reporting >=2 exhibit-bearing items each with its own recoverable EX-99.x
    (e.g. Item 2.02->EX-99.1, Item 7.01->EX-99.2) whose content we want extracted,
    not gapped | upgrade=parse each reported item's body text for its referenced
    exhibit number and map by that | ref=spec Requirement "8-K Item Segmentation
    with Exhibit-Following". (The gap itself is loud + tested; this cut defers the
    multi-exhibit RESOLUTION, not the fail-loud behaviour.)
    """
    following = [item_id for item_id in obj.items if item_id in _EIGHTK_EXHIBIT_ITEMS]
    releases = list(obj.press_releases)
    if len(following) == 1 and len(releases) == 1:
        item_id, release = following[0], releases[0]
        # ``release.text`` is a zero-arg method → pass it AS the text-thunk so
        # `segment_filing` evaluates the exhibit body under its own try/except
        # (Task 8 per-item isolation); ``release.document`` (the filename) is
        # read eagerly for provenance. ``disclosure_status: "furnished"`` (Task 9)
        # is derived from the SOURCE TYPE (an 8-K Item 2.02/7.01/8.01 Exhibit 99.x
        # is FURNISHED, not filed) — NOT read from edgartools — so a downstream
        # consumer can weight it distinctly from filed 10-K/10-Q content.
        return [
            (item_id, release.text,
             {"exhibit": release.document, "disclosure_status": "furnished"})
        ]
    return [
        _exhibit_gap(
            item_id, filing, item_count=len(following), release_count=len(releases)
        )
        for item_id in following
    ]


# form -> extractor(obj, filing) returning per-item entries (see EXTRACTOR
# CONTRACT above): [(item id, text-or-None[, extra_dict]), ...] from filing.obj().
_ITEM_EXTRACTORS = {
    "10-K": _segment_10k,
    "10-Q": _segment_10q,
    "8-K": _segment_8k,
}


# The requested item ids that are knowable form-statically, WITHOUT reading
# `filing.obj()` — used by the all-fail path (Task 8) when `obj()`/extractor
# building itself raises, so every requested section still gets a loud error slot
# (never a silent-empty result). A 10-K always requests Item 7 + Item 1A; a 10-Q
# Item 2. An 8-K's requested items are the filing-SPECIFIC reported item codes
# that live on `obj.items`; once `obj()` has failed they are unreadable, so the
# all-fail handler falls back to a single filing-level slot for it.
_FORM_REQUESTED_ITEMS = {
    "10-K": ("Item 7", "Item 1A"),
    "10-Q": ("Item 2",),
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
    """Every requested section as a loud error slot, for when `filing.obj()` or
    extractor building failed wholesale — no top-level success is claimed. 10-K/
    10-Q requested items are enumerated form-statically; a form whose requested
    items live on the now-unreadable `obj` (8-K) falls back to a single
    filing-level slot so the failure is never silently dropped.

    `slot` is the per-item slot builder (signature ``(item_id, filing, exc)``);
    defaults to ``_extraction_error_slot`` (Task 8's generic wholesale-failure
    class) but the timeout carve-out (Task 10) passes ``_timeout_error_slot`` so a
    wholesale TIMEOUT classifies every requested section as the distinct
    ``timeout`` class, not the generic ``extraction_error``. (Default resolved in
    the body, not the signature, because ``_extraction_error_slot`` is defined
    below this function.)"""
    slot = slot or _extraction_error_slot
    requested = _FORM_REQUESTED_ITEMS.get(form) or (f"form {form}",)
    return [slot(item_id, filing, exc) for item_id in requested]


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
    """Segment a 10-K / 10-Q filing into per-item section objects via edgartools'
    typed section API (``filing.obj()`` -> ``TenK`` / ``TenQ``), NOT the retired
    regex ``parse_item_sections``.

    Returns a LIST of section dicts (see the SECTION-OBJECT CONTRACT above):
      - 10-K -> distinct Item 7 (MD&A) + Item 1A (Risk Factors) sections.
      - 10-Q -> an Item 2 (MD&A) section.
      - 8-K  -> one section per reported exhibit-bearing item (2.02/7.01/8.01),
        each sourced from its Exhibit 99.x with the exhibit filename in
        provenance (Task 4).
    A requested item absent from THIS filing (edgartools returns ``None``,
    issue #710) becomes a per-section error slot naming the missing item, never
    an empty/fabricated section. An unregistered form fails loud (``ValueError``)
    rather than silently returning no sections.

    Fail-loud per-section isolation (Task 8): an extraction that RAISES never
    aborts the whole segmentation. A throw building `filing.obj()` or the
    extractor's entry list (the primary document cannot be fetched/parsed at all)
    turns EVERY requested section into a loud `extraction_error` slot (all-fail);
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
        # Every requested section becomes the DISTINCT retryable `timeout` slot,
        # NOT the generic extraction_error — narrower-except-first, above Exception.
        return _all_sections_failed(form, filing, exc, slot=_timeout_error_slot)
    except Exception as exc:  # noqa: BLE001 — fail loud per requested section, don't crash
        # Wholesale failure: obj() or extractor building threw, so no per-item
        # text-thunk was ever reached. Every requested section becomes a loud
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
    section list WITHOUT re-hitting edgartools/``acquire_filing`` (SEC fair-access:
    never re-fetch what we already have). Cache MISS acquires the filing via
    edgartools (``acquire_filing``) then segments it (``segment_filing``), and
    caches the resulting section-list wrapper.

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
    """
    path = cache_util.cache_path("sec_edgar", f"narrative_sections_{accession}")
    cached = cache_util.load_cache(path, TTL_NARRATIVE)
    if cached is not None:
        cached["_cache"] = "hit"
        return cached

    filing = acquire_filing(accession=accession)
    if isinstance(filing, dict) and "error" in filing:
        # Loud acquisition failure (e.g. a 429/403 that escaped edgartools' own
        # backoff) — surface it; do NOT segment, do NOT cache it as success.
        return filing

    sections = segment_filing(filing)
    result = {
        "accession": accession,
        "sections": sections,
        "section_count": len(sections),
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
    res = fetch_narrative(accession)
    res["action"] = "narrative"
    cache_label = "cache hit" if res.get("_cache") == "hit" else f"{res.get('section_count', 0)} sections in {time.monotonic() - t0:.1f}s"
    _log("narrative done", f"{accession} {cache_label}")
    return res

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
            p = cache_util.cache_path("sec_edgar", f"narrative_{args.accession}")
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
        result = action_filings(args.ticker, forms, args.limit)

    elif args.action == "narrative":
        if not args.accession:
            print("--accession required for --action narrative", file=sys.stderr)
            sys.exit(2)
        result = action_narrative(args.accession)

    print(json.dumps(result, default=str, indent=2))
    sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
    main()
