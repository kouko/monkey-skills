#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
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
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import requests as _requests

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SEC_COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SEC_COMPANYCONCEPT_URL = (
    "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{concept}.json"
)
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives/edgar/data/{cik_int}/{accession_nodash}/{doc}"

# SEC mandates identified User-Agent: "<name> <email>" format.
USER_AGENT = "kouko investing-toolkit <noreply@anthropic.com>"

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(
    Path.home() / ".cache" / "investing-toolkit"
)
CACHE_DIR = Path(_CACHE_BASE) / "sec_edgar"

TTL_TICKERS = 7 * 86400       # 7 days
TTL_FACTS = 86400             # 24 hours
TTL_SUBMISSIONS = 86400       # 24 hours
TTL_NARRATIVE = None          # permanent; filings don't change

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
THROTTLE_SECONDS = 0.1        # ≤10 req/sec


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _cache_path(filename: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / filename


def _load_cache(path: Path, ttl: int | None) -> dict | None:
    if not path.exists():
        return None
    if ttl is not None and time.time() - path.stat().st_mtime > ttl:
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _save_cache(path: Path, data: dict) -> None:
    try:
        path.write_text(json.dumps(data, default=str, indent=2))
    except Exception:
        pass


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
    path = _cache_path("tickers.json")
    cached = _load_cache(path, TTL_TICKERS)
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
    _save_cache(path, result)
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
        filename = f"concept_{cik:010d}_{concept}.json"
    else:
        filename = f"facts_{cik:010d}.json"
    path = _cache_path(filename)
    cached = _load_cache(path, TTL_FACTS)
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
    _save_cache(path, result)
    return result


def summarize_concept(raw_concept: dict) -> list[dict]:
    """Extract USD time-series from companyconcept response."""
    units = raw_concept.get("units", {})
    # Prefer USD, fall back to first available unit
    series = units.get("USD") or next(iter(units.values()), [])
    return [
        {
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
    path = _cache_path(f"submissions_{cik:010d}.json")
    cached = _load_cache(path, TTL_SUBMISSIONS)
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
    _save_cache(path, result)
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
    path = _cache_path(f"narrative_{accession}.json")
    cached = _load_cache(path, TTL_NARRATIVE)
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
    _save_cache(path, result)
    return result


# ---------------------------------------------------------------------------
# Action dispatch
# ---------------------------------------------------------------------------

def action_cik(ticker: str) -> dict:
    result = resolve_cik(ticker)
    if "error" in result:
        return result
    result["action"] = "cik"
    return result


def action_facts(ticker: str, concept: str | None) -> dict:
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

    return out


def action_filings(ticker: str, forms: list[str] | None, limit: int) -> dict:
    cik_info = resolve_cik(ticker)
    if "error" in cik_info:
        return cik_info
    cik = cik_info["cik"]

    rows = list_filings(cik, forms, limit)
    latest_date = rows[0]["filingDate"] if rows else None
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


def action_narrative(accession: str) -> dict:
    res = fetch_narrative(accession)
    res["action"] = "narrative"
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

    args = parser.parse_args()

    # Optional cache bust
    if args.no_cache:
        # Only blow away the file that's about to be written
        if args.ticker:
            t = args.ticker.upper()
            tmap = load_ticker_map()
            entry = tmap.get("tickers", {}).get(t) if "error" not in tmap else None
            if entry:
                cik = entry["cik"]
                for fn in (
                    f"facts_{cik:010d}.json",
                    f"submissions_{cik:010d}.json",
                    f"concept_{cik:010d}_{args.concept}.json" if args.concept else "",
                ):
                    if fn:
                        p = CACHE_DIR / fn
                        if p.exists():
                            p.unlink()
        if args.accession:
            p = CACHE_DIR / f"narrative_{args.accession}.json"
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
