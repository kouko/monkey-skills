#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
tdnet_client.py — investing-toolkit Japan timely-disclosure adapter (v1.15.0+)

Wraps the Yanoshin TDnet WEB-API (https://webapi.yanoshin.jp/), a
free JSON gateway to JPX's TDnet 適時開示情報. TDnet covers material
events, 決算短信 (preliminary earnings, faster than EDINET 有報),
corporate actions, and governance disclosures — the Japan equivalent
of SEC Form 8-K + selected 13D/G.

**Tier classification**: Index / pointer-only. Yanoshin is an
unofficial third-party aggregator (one-person project, informal ToS).
This client fetches DISCLOSURE INDEX METADATA ONLY (title + pubdate +
document URL). Full disclosure documents must be downloaded directly
from JPX (release.tdnet.info PDFs) per Yanoshin's redirect pattern —
we do NOT re-host or cache response payloads beyond index metadata.
Complements EDINET (official + primary-source) for same-day coverage
of events that take up to 45 days to appear in EDINET 臨時報告書.

Auth: None. Rate limiting: polite ~1 req/sec (no enforced throttle
declared). No API key required.

Usage:
  uv run tdnet_client.py --action list --ticker 7203 --limit 20
  uv run tdnet_client.py --action list --ticker 6758 --keyword 決算短信 --limit 10
  uv run tdnet_client.py --action list --ticker 7203 --days 365

Cache: $INVESTING_TOOLKIT_CACHE/tdnet/{ticker}_{limit}_{keyword}.json  TTL: 1h
       Short TTL because disclosures are event-driven and time-sensitive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(
    Path.home() / ".cache" / "investing-toolkit"
)
CACHE_DIR = Path(_CACHE_BASE) / "tdnet"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL_SECONDS = 3600  # 1h — index is event-driven, low-frequency update


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "tdnet-jp"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


BASE = "https://webapi.yanoshin.jp/webapi/tdnet"
DEFAULT_USER_AGENT = (
    "kouko investing-toolkit (github.com/kouko/monkey-skills) "
    "tdnet_client.py/1.0"
)


# Disclosure-type heuristic classifier — matches on title substrings.
# Order matters: more specific classes listed first so first-match wins.
_DISCLOSURE_TYPES: list[tuple[str, str]] = [
    ("決算短信",            "kessan_tanshin"),
    ("四半期決算",          "q_earnings"),
    ("業績予想",            "guidance_revision"),
    ("配当予想",            "dividend_revision"),
    ("自己株券買付",        "buyback_status"),
    ("自己株式",            "own_shares"),
    ("公開買付",            "tender_offer"),
    ("ストックオプション",  "stock_options"),
    ("株主総会",            "shareholder_meeting"),
    ("役員",                "officer_change"),
    ("配当金",              "dividend_payment"),
    ("合併",                "merger"),
    ("会社分割",            "split"),
    ("株式交換",            "share_swap"),
    ("業務提携",            "business_alliance"),
    ("資本提携",            "capital_alliance"),
    ("重要な訴訟",          "material_litigation"),
    ("有価証券報告書",      "annual_report_linkout"),
    ("四半期報告書",        "quarterly_report_linkout"),
    ("臨時報告書",          "extraordinary_linkout"),
    ("定款",                "articles_change"),
]


def _classify(title: str) -> str:
    for keyword, cls in _DISCLOSURE_TYPES:
        if keyword in title:
            return cls
    return "other"


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _cache_path(key: str) -> Path:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
    return CACHE_DIR / f"{digest}.json"


def _load_cache(path: Path) -> dict | None:
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > CACHE_TTL_SECONDS:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_cache(path: Path, data: dict) -> None:
    try:
        path.write_text(
            json.dumps(data, default=str, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_provenance(*, count: int, latest: str | None) -> dict:
    return {
        "source": "Yanoshin TDnet WEB-API (webapi.yanoshin.jp/tdnet)",
        "source_authority": (
            "JPX TDnet via unofficial Yanoshin aggregator — index only; "
            "full documents served from release.tdnet.info (JPX-hosted)"
        ),
        "data_type": "third_party_aggregated_index",
        "data_tier": "tier_2_index",
        "update_cycle": "event-driven, polled every few minutes by aggregator",
        "typical_lag": "~5 min from TDnet official publication",
        "license_note": (
            "Yanoshin terms informal; do NOT re-host response payloads. "
            "Follow document_url for content (JPX-served PDFs under TDnet ToS)."
        ),
        "fetched_at": _now_iso(),
        "reference_period": latest,
        "count": count,
    }


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _http_get(url: str, *, params: dict | None = None,
              timeout: int = 30) -> dict:
    r = requests.get(
        url, params=params, timeout=timeout,
        headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"},
    )
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def _normalize_ticker_for_tdnet(ticker: str) -> str:
    """Yanoshin accepts both 4-digit (7203) and 5-digit (72030) codes;
    normalize to 4-digit. Strip JP market suffixes."""
    t = ticker.strip().upper().replace(".T", "").replace(".TO", "")
    # Trailing-0 normalization: 72030 → 7203 (FSA/JPX 5-digit legacy)
    if re.fullmatch(r"\d{5}", t) and t.endswith("0"):
        return t[:4]
    return t[:4]


def _normalize_item(raw: dict) -> dict:
    """Flatten Yanoshin's {Tdnet: {...}} wrapper into a compact record."""
    item = raw.get("Tdnet", {}) if "Tdnet" in raw else raw
    title = item.get("title", "")
    return {
        "id": item.get("id"),
        "pubdate": item.get("pubdate"),
        "company_code": item.get("company_code"),
        "company_name": item.get("company_name"),
        "title": title,
        "disclosure_type": _classify(title),
        "document_url": item.get("document_url"),
        "xbrl_url": item.get("url_xbrl"),
        "market": item.get("markets_string"),
        "report_urls": {
            "summary": item.get("url_report_type_summary"),
            "fs_consolidated": item.get("url_report_type_fs_consolidated"),
            "fs_non_consolidated": item.get("url_report_type_fs_non_consolidated"),
            "earnings_forecast": item.get("url_report_type_earnings_forecast"),
            "expected_dividends": item.get("url_report_type_expected_dividends"),
        },
    }


# ---------------------------------------------------------------------------
# Public actions
# ---------------------------------------------------------------------------

def list_disclosures(
    ticker: str, *, limit: int = 20, keyword: str | None = None,
) -> dict:
    """List recent TDnet disclosures for a JP ticker.

    `keyword` filters in-memory on normalized title after fetch (API itself
    doesn't support title keyword filtering for the /list/{ticker} endpoint).
    """
    _log("list fetch", f"{ticker} limit={limit}{(' keyword=' + keyword) if keyword else ''}")
    t0 = time.monotonic()
    tnorm = _normalize_ticker_for_tdnet(ticker)
    cache_key = f"list:{tnorm}:{limit}:{keyword or ''}"
    cache_path = _cache_path(cache_key)
    cached = _load_cache(cache_path)
    if cached is not None:
        cached["_cache"] = "hit"
        _log("list done", f"{ticker} cache hit")
        return cached

    # Over-fetch if keyword filter applied (so we still have `limit` hits
    # after narrowing).
    fetch_limit = min(limit * 4 if keyword else limit, 100)

    try:
        raw = _http_get(
            f"{BASE}/list/{tnorm}.json",
            params={"limit": fetch_limit},
        )
    except Exception as e:
        return {
            "error": f"Yanoshin TDnet fetch failed: {e}",
            "ticker": ticker,
            "hint": "Check webapi.yanoshin.jp reachability; aggregator may be down.",
        }

    items = raw.get("items", []) or []
    normalized = [_normalize_item(i) for i in items]

    if keyword:
        kw = keyword.strip()
        normalized = [i for i in normalized if kw in (i.get("title") or "")]

    normalized = normalized[:limit]
    latest = normalized[0]["pubdate"] if normalized else None

    result = {
        "ticker": ticker,
        "normalized_ticker": tnorm,
        "keyword": keyword,
        "limit": limit,
        "count": len(normalized),
        "total_available": raw.get("total_count"),
        "disclosures": normalized,
        "fetched_at": _now_iso(),
        "_cache": "miss",
        "_provenance": _make_provenance(
            count=len(normalized), latest=latest,
        ),
    }
    _save_cache(cache_path, result)
    _log("list done", f"{ticker} {len(normalized)} disclosures in {time.monotonic() - t0:.1f}s")
    return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="TDnet adapter (via Yanoshin WEB-API) for investing-toolkit",
    )
    parser.add_argument(
        "--action", default="list", choices=["list"],
        help="Currently only 'list' is supported",
    )
    parser.add_argument("--ticker", required=True,
                        help="4-digit JP ticker (e.g. 7203)")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max disclosures returned (1-100)")
    parser.add_argument("--keyword", default=None,
                        help="Filter title substring (e.g. '決算短信')")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass cache")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    if args.no_cache:
        tnorm = _normalize_ticker_for_tdnet(args.ticker)
        cache_key = f"list:{tnorm}:{args.limit}:{args.keyword or ''}"
        cp = _cache_path(cache_key)
        if cp.exists():
            cp.unlink()

    result = list_disclosures(
        args.ticker, limit=args.limit, keyword=args.keyword,
    )
    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
