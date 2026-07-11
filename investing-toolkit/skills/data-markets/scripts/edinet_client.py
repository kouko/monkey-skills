#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1", "pandas==3.0.2"]
# ///
"""
edinet_client.py — investing-toolkit Japan equity disclosure adapter (v1.15.0+)

Wraps EDINET v2 API (金融庁 Electronic Disclosure for Investors' NETwork),
Japan's equivalent of US SEC EDGAR. Tier A primary-source: redistribution
permitted under PDL 1.0 (出典：金融庁 EDINET attribution required).

Covered forms (docTypeCode):
  120  有価証券報告書         (annual, ~10-K)   + 130 訂正版
  140  四半期報告書           (quarterly, ~10-Q) + 150 訂正版
  160  半期報告書             (semi-annual)
  180  臨時報告書             (material events, ~8-K)
  220  自己株券買付状況報告書 (buyback status)
  350  大量保有報告書         (5% ownership, ~13G/D) + 360 変更/訂正

Historical depth:
  `/documents.json` date listing: 5-year rolling window.
  Individual filings by docID remain retrievable beyond 5 years.

Auth: EDINET_API_KEY env var required for /documents.json and
      /documents/{docID} endpoints. Free 5-min self-service registration
      at https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html
      The EDINET code list download (ticker→code mapping) is PUBLIC,
      no key required.

Usage (single ticker / typical):
  uv run edinet_client.py --action resolve-code --ticker 7203
  uv run edinet_client.py --action list-filings --ticker 7203 --forms 120,140 --days 90
  uv run edinet_client.py --action fetch-statements --doc-id S100U1EZ
  uv run edinet_client.py --action filing-summary --ticker 7203 --days 180

Cache (TTL):
  code-list       7 days   (FSA refreshes weekly)
  documents-list  1 day    (per-date listing)
  document-csv    30 days  (filings immutable after submit)

Companion docs: docs/edinet-guide.md (per-form structure + element IDs).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import time
import zipfile
from datetime import date, datetime, timedelta, timezone

import requests

import cache_util

API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
CODE_LIST_URL = (
    "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"
)

DEFAULT_USER_AGENT = (
    "kouko investing-toolkit (github.com/kouko/monkey-skills) "
    "edinet_client.py/1.0"
)
RATE_LIMIT_SECONDS = 0.5  # community-recommended pace per EDINET ToS

CODE_LIST_TTL_SECONDS = 7 * 86400
DOCUMENTS_LIST_TTL_SECONDS = 86400
DOCUMENT_CSV_ZIP_TTL_SECONDS = 30 * 86400

FORM_LABELS = {
    "120": "有価証券報告書 (annual)",
    "130": "訂正有価証券報告書",
    "140": "四半期報告書 (quarterly)",
    "150": "訂正四半期報告書",
    "160": "半期報告書 (semi-annual)",
    "170": "訂正半期報告書",
    "180": "臨時報告書 (material events)",
    "190": "訂正臨時報告書",
    "220": "自己株券買付状況報告書 (buyback)",
    "350": "大量保有報告書 (5% ownership)",
    "360": "訂正大量保有報告書",
}

# Key concepts for BS / PL / CF summary extraction (JP-GAAP + IFRS aliases).
# Aliases MUST be specific enough that substring match doesn't overlap
# between metrics (e.g. "ProfitLoss" would catch "OperatingProfitLoss" too).
# Prefer the "SummaryOfBusinessResults" suffix — it's the standard 5-year
# summary table present in every 有報 / 四半期報告書.
KEY_CONCEPTS: dict[str, list[str]] = {
    "revenue": [
        "NetSalesSummaryOfBusinessResults",
        "RevenueIFRSSummaryOfBusinessResults",
        "OperatingRevenuesIFRSKeyFinancialData",
        "SalesAndFinancialServicesRevenueIFRSKeyFinancialData",
        "RevenueSummaryOfBusinessResults",
        "NetSalesKeyFinancialData",
    ],
    "operating_income": [
        "OperatingIncomeLossSummaryOfBusinessResults",
        "OperatingProfitLossIFRSSummaryOfBusinessResults",
        "OperatingProfitLossIFRSKeyFinancialData",
        "OperatingProfitLossIFRS",  # jpigp_cor: — statement-body namespace
        "OperatingIncomeLoss",
    ],
    "ordinary_income": [
        "OrdinaryIncomeLossSummaryOfBusinessResults",
    ],
    "net_income": [
        # Strict: parent-attributable profit only, avoid overlap with
        # OperatingProfitLoss / ProfitLossBeforeTax / ProfitLossFromOp.
        "ProfitLossAttributableToOwnersOfParentSummaryOfBusinessResults",
        "ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
        "NetIncomeLossSummaryOfBusinessResults",
        "ProfitAttributableToOwnersOfParentCompanySummaryOfBusinessResults",
    ],
    "total_assets": [
        "TotalAssetsSummaryOfBusinessResults",
        "TotalAssetsIFRSSummaryOfBusinessResults",
    ],
    "net_assets": [
        "NetAssetsSummaryOfBusinessResults",
        "TotalEquityIFRSSummaryOfBusinessResults",
        "EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsSummaryOfBusinessResults",
        "CashAndCashEquivalentsIFRSSummaryOfBusinessResults",
    ],
    "eps": [
        "BasicEarningsPerShareSummaryOfBusinessResults",
        "BasicEarningsPerShareIFRSSummaryOfBusinessResults",
    ],
    "bps": [
        "NetAssetsPerShareSummaryOfBusinessResults",
        "EquityAttributableToOwnersOfParentPerShareIFRSSummaryOfBusinessResults",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivitiesSummaryOfBusinessResults",
        "CashFlowsFromUsedInOperatingActivitiesIFRSSummaryOfBusinessResults",
    ],
    "investing_cash_flow": [
        "NetCashProvidedByUsedInInvestingActivitiesSummaryOfBusinessResults",
        "CashFlowsFromUsedInInvestingActivitiesIFRSSummaryOfBusinessResults",
    ],
    "financing_cash_flow": [
        "NetCashProvidedByUsedInFinancingActivitiesSummaryOfBusinessResults",
        "CashFlowsFromUsedInFinancingActivitiesIFRSSummaryOfBusinessResults",
    ],
    "employees": [
        "NumberOfEmployeesSummaryOfBusinessResults",
    ],
}


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "edinet-jp"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Cache helpers — lazy cache_util usage (no import-time filesystem side
# effects; directory/path resolution happens only when a fetch actually runs).
# The code-list + documents-list caches are JSON and go through cache_util's
# envelope helpers; the document CSV ZIP cache stores raw bytes (not JSON),
# so it resolves its own path via cache_util.resolve_cache_dir() lazily and
# keeps the original mtime-based TTL check.
# ---------------------------------------------------------------------------

def _strip_cache_meta(d: dict) -> dict:
    """Remove cache_util's envelope-injected bookkeeping fields.

    Used only for caches whose value is a pure lookup table (not a
    fetch-result dict), where a stray `_cache` key could be confused for
    real data.
    """
    for k in ("_cache", "_cache_age_seconds", "_cache_ttl_seconds"):
        d.pop(k, None)
    return d


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_provenance(*, reference_period: str | None = None,
                     tier: str = "tier_a") -> dict:
    return {
        "source": "EDINET v2 (api.edinet-fsa.go.jp)",
        "source_authority": "金融庁 (Financial Services Agency, Japan)",
        "data_type": "official_regulatory_disclosure",
        "license": "PDL 1.0 (redistribution OK w/ 出典：金融庁 EDINET attribution)",
        "data_tier": tier,
        "update_cycle": "filing-driven",
        "typical_lag": "annual reports ~3mo after FY end; quarterly ~45d",
        "fetched_at": _now_iso(),
        "reference_period": reference_period,
    }


# ---------------------------------------------------------------------------
# API key + HTTP
# ---------------------------------------------------------------------------

def _require_api_key() -> str:
    key = os.environ.get("EDINET_API_KEY")
    if not key:
        raise SystemExit(
            "EDINET_API_KEY env var not set. Register free at "
            "https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html "
            "and `export EDINET_API_KEY=<key>`. The `resolve-code` action "
            "does NOT need a key — use that to test plumbing first."
        )
    return key


_last_call_ts = 0.0


def _throttle() -> None:
    global _last_call_ts
    delta = time.time() - _last_call_ts
    if delta < RATE_LIMIT_SECONDS:
        time.sleep(RATE_LIMIT_SECONDS - delta)
    _last_call_ts = time.time()


def _http_get(url: str, *, params: dict | None = None,
              headers: dict | None = None, timeout: int = 60) -> requests.Response:
    _throttle()
    hdr = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        hdr.update(headers)
    r = requests.get(url, params=params, headers=hdr, timeout=timeout)
    if r.status_code == 401:
        raise SystemExit(
            f"EDINET API returned 401 Unauthorized. Check EDINET_API_KEY is "
            f"valid (url={url})."
        )
    if r.status_code == 429:
        raise SystemExit(
            "EDINET API returned 429 Too Many Requests. Community guidance: "
            "wait ~60 min before retrying; reduce parallelism."
        )
    r.raise_for_status()
    return r


# ---------------------------------------------------------------------------
# EDINET code list (ticker → EDINET code) — public, no key
# ---------------------------------------------------------------------------

def _load_code_list(refresh: bool = False) -> dict[str, dict]:
    """Return mapping {4-digit ticker: {edinet_code, name, name_en, industry, ...}}."""
    cache = cache_util.cache_path("edinet", "code_list")
    if not refresh:
        cached = cache_util.load_cache(cache, CODE_LIST_TTL_SECONDS)
        if cached is not None:
            return _strip_cache_meta(cached)

    import pandas as pd

    r = _http_get(CODE_LIST_URL)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        # File name is 'EdinetcodeDlInfo.csv' in the ZIP root.
        names = [n for n in z.namelist() if n.endswith("EdinetcodeDlInfo.csv")]
        if not names:
            raise SystemExit(
                f"EdinetcodeDlInfo.csv not found in ZIP from {CODE_LIST_URL}"
            )
        with z.open(names[0]) as f:
            df = pd.read_csv(f, encoding="cp932", skiprows=1, dtype=str)

    def _s(v) -> str:
        """Coerce any pandas cell to stripped string; NaN/None → ''."""
        if v is None:
            return ""
        s = str(v).strip()
        return "" if s.lower() in ("nan", "none", "nat") else s

    # FSA stores 証券コード with trailing 0 (5-digit), e.g. 72030 for Toyota.
    # Normalize to 4-digit ticker. Some filers have no ticker (non-listed).
    mapping: dict[str, dict] = {}
    for _, row in df.iterrows():
        ticker5 = _s(row.get("証券コード"))
        if not ticker5:
            continue
        ticker4 = ticker5.rstrip("0")[:4] if len(ticker5) == 5 else ticker5[:4]
        entry = {
            "edinet_code": _s(row.get("ＥＤＩＮＥＴコード")),
            "name": _s(row.get("提出者名")),
            "name_en": _s(row.get("提出者名（英字）")),
            "name_yomi": _s(row.get("提出者名（ヨミ）")),
            "industry": _s(row.get("提出者業種")),
            "submitter_type": _s(row.get("提出者種別")),
            "listed": _s(row.get("上場区分")),
            "consolidated": _s(row.get("連結の有無")),
            "corporate_number": _s(row.get("提出者法人番号")),
            "fiscal_year_end": _s(row.get("決算日")),
            "ticker": ticker4,
            "ticker_5digit": ticker5,
        }
        mapping[ticker4] = entry

    cache_util.save_cache(cache, mapping)
    return mapping


def resolve_edinet_code(ticker: str) -> dict:
    """Resolve a 4-digit JP ticker to its EDINET code + metadata."""
    _log("resolve-code", ticker)
    t = ticker.strip().replace(".T", "").replace(".TO", "")[:4]
    mapping = _load_code_list()
    if t not in mapping:
        return {
            "error": f"Ticker {ticker} not found in EDINET code list.",
            "hint": (
                "Non-listed companies file via EDINET without a 証券コード. "
                "Confirm this is a JPX-listed issuer."
            ),
            "fetched_at": _now_iso(),
        }
    result = dict(mapping[t])
    result["fetched_at"] = _now_iso()
    result["_provenance"] = _make_provenance(tier="tier_a")
    return result


# ---------------------------------------------------------------------------
# /documents.json — per-date disclosure listing
# ---------------------------------------------------------------------------

def _fetch_documents_list(target_date: date) -> dict:
    """Return EDINET disclosure listing for a single date (cached 1 day)."""
    date_str = target_date.strftime("%Y-%m-%d")
    cache = cache_util.cache_path("edinet", f"documents_{date_str}")
    cached = cache_util.load_cache(cache, DOCUMENTS_LIST_TTL_SECONDS)
    if cached is not None:
        return cached

    api_key = _require_api_key()
    r = _http_get(
        f"{API_BASE}/documents.json",
        params={
            "date": date_str,
            "type": 2,  # 提出書類一覧及び取得
            "Subscription-Key": api_key,
        },
        timeout=30,
    )
    data = r.json()
    cache_util.save_cache(cache, data)
    return data


def list_filings(
    ticker: str, forms: list[str] | None, days: int, limit: int,
) -> dict:
    """Scan the last `days` of /documents.json, filter to `ticker`'s EDINET code."""
    _log("list-filings start", f"{ticker} forms={forms or 'ALL'} days={days} limit={limit}")
    t0 = time.monotonic()
    resolved = resolve_edinet_code(ticker)
    if "error" in resolved:
        return resolved

    edinet_code = resolved["edinet_code"]
    today = date.today()
    form_filter = set(forms) if forms else None
    results: list[dict] = []

    for offset in range(days):
        target = today - timedelta(days=offset)
        if offset > 0 and offset % 30 == 0:
            _log(f"list-filings [day {offset}/{days}]", f"{len(results)} hit(s) so far")
        try:
            listing = _fetch_documents_list(target)
        except SystemExit:
            raise
        except Exception as e:
            # Non-fatal — one bad date shouldn't stop the scan
            print(
                f"[edinet_client] warn: documents.json fetch failed for "
                f"{target.isoformat()}: {e}",
                file=sys.stderr,
            )
            continue

        for item in listing.get("results", []) or []:
            if item.get("edinetCode") != edinet_code:
                continue
            doc_type = item.get("docTypeCode") or ""
            if form_filter and doc_type not in form_filter:
                continue
            results.append({
                "doc_id": item.get("docID"),
                "doc_type_code": doc_type,
                "doc_type_label": FORM_LABELS.get(doc_type, f"(code {doc_type})"),
                "filer_name": item.get("filerName"),
                "doc_description": item.get("docDescription"),
                "submit_datetime": item.get("submitDateTime"),
                "period_start": item.get("periodStart"),
                "period_end": item.get("periodEnd"),
                "xbrl_available": bool(item.get("xbrlFlag") == "1"),
                "csv_available": bool(item.get("csvFlag") == "1"),
                "english_available": bool(item.get("englishDocFlag") == "1"),
            })
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break

    results.sort(key=lambda r: r.get("submit_datetime") or "", reverse=True)
    _log("list-filings done", f"{ticker} {len(results)} filings in {time.monotonic() - t0:.1f}s")
    return {
        "ticker": ticker,
        "edinet_code": edinet_code,
        "name": resolved.get("name"),
        "scanned_days": days,
        "forms_filter": forms,
        "count": len(results),
        "filings": results[:limit],
        "fetched_at": _now_iso(),
        "_provenance": _make_provenance(
            reference_period=results[0].get("submit_datetime", "").split("T")[0]
            if results else None,
        ),
    }


# ---------------------------------------------------------------------------
# /documents/{docID} — fetch CSV (type=5) and parse structured statements
# ---------------------------------------------------------------------------

def _fetch_document_csv_zip(doc_id: str) -> bytes:
    """Download the type=5 CSV ZIP for a filing (cached 30 days, raw bytes —
    not JSON, so it bypasses cache_util's JSON envelope and only borrows
    `resolve_cache_dir()` for the writable base directory, lazily)."""
    cache = cache_util.resolve_cache_dir() / "edinet" / f"doc_{doc_id}_csv.zip"
    if cache.exists() and time.time() - cache.stat().st_mtime < DOCUMENT_CSV_ZIP_TTL_SECONDS:
        return cache.read_bytes()

    api_key = _require_api_key()
    r = _http_get(
        f"{API_BASE}/documents/{doc_id}",
        params={"type": 5, "Subscription-Key": api_key},
        timeout=120,
    )
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(r.content)
    return r.content


def _extract_main_csv(zip_bytes: bytes) -> tuple[str, list[dict]]:
    """Pick the main 本文 CSV from a type=5 ZIP and parse rows.

    Returns (csv_filename, rows). Each row is a dict with keys:
      element_id, item_name, context_id, relative_year, consolidated,
      period_type, unit_id, unit, value
    """
    import pandas as pd

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        names = [n for n in z.namelist() if n.endswith(".csv")]
        if not names:
            raise SystemExit("Type=5 ZIP contained no CSV files.")
        # Heuristic: the main 本文 CSV has the largest file size and filename
        # starting with 'XBRL_TO_CSV/jpcrp' or 'XBRL_TO_CSV/jpigp'.
        main_csvs = [n for n in names if re.search(r"jp(crp|igp|pfs)", n)]
        candidates = main_csvs or names
        # Largest file wins if multiple.
        sizes = {n: z.getinfo(n).file_size for n in candidates}
        main_name = max(sizes, key=sizes.get)

        with z.open(main_name) as f:
            df = pd.read_csv(f, encoding="utf-16", sep="\t", dtype=str)

    def _s(v) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        return "" if s.lower() in ("nan", "none", "nat") else s

    rows = []
    for _, r in df.iterrows():
        rows.append({
            "element_id": _s(r.get("要素ID")),
            "item_name": _s(r.get("項目名")),
            "context_id": _s(r.get("コンテキストID")),
            "relative_year": _s(r.get("相対年度")),
            "consolidated": _s(r.get("連結・個別")),
            "period_type": _s(r.get("期間・時点")),
            "unit_id": _s(r.get("ユニットID")),
            "unit": _s(r.get("単位")),
            "value": _s(r.get("値")),
        })

    return main_name, rows


def _extract_key_metrics(rows: list[dict]) -> dict:
    """Pull common BS/PL/CF metrics using KEY_CONCEPTS substring matching.
    Prefers CurrentYear + 連結 rows. Returns {metric_name: {value, element_id, ...}}.
    """
    out: dict = {}
    for metric, aliases in KEY_CONCEPTS.items():
        best = None
        for row in rows:
            element = row.get("element_id", "")
            if not any(a in element for a in aliases):
                continue
            # Prefer current-year + consolidated
            score = 0
            if "CurrentYear" in row.get("context_id", ""):
                score += 2
            if row.get("consolidated") == "連結":
                score += 1
            val = row.get("value", "")
            if not val or val in ("-", "－"):
                continue
            candidate = {
                "value": val,
                "element_id": element,
                "item_name": row.get("item_name"),
                "context_id": row.get("context_id"),
                "consolidated": row.get("consolidated"),
                "unit": row.get("unit"),
                "_score": score,
            }
            if best is None or candidate["_score"] > best["_score"]:
                best = candidate
        if best is not None:
            best.pop("_score", None)
            out[metric] = best
    return out


def fetch_statements(doc_id: str, include_raw: bool = False) -> dict:
    """Fetch a filing's type=5 CSV and return structured BS/PL/CF extract."""
    _log("fetch-statements", doc_id)
    t0 = time.monotonic()
    zip_bytes = _fetch_document_csv_zip(doc_id)
    main_csv, rows = _extract_main_csv(zip_bytes)
    key_metrics = _extract_key_metrics(rows)
    _log("fetch-statements done", f"{doc_id} {len(rows)} rows in {time.monotonic() - t0:.1f}s")

    result: dict = {
        "doc_id": doc_id,
        "main_csv_name": main_csv,
        "row_count": len(rows),
        "key_metrics": key_metrics,
        "fetched_at": _now_iso(),
        "_provenance": _make_provenance(tier="tier_a"),
    }
    if include_raw:
        result["raw_rows"] = rows
    return result


# ---------------------------------------------------------------------------
# Composite: filing-summary (resolve → list → fetch latest annual + quarterly)
# ---------------------------------------------------------------------------

def filing_summary(ticker: str, days: int = 365) -> dict:
    """One-shot convenience: resolve ticker → list filings → fetch latest
    annual (120) + latest quarterly (140) statements."""
    _log("filing-summary start", f"{ticker} days={days}")
    t0 = time.monotonic()
    resolved = resolve_edinet_code(ticker)
    if "error" in resolved:
        return resolved

    filings = list_filings(
        ticker, forms=["120", "140"], days=days, limit=20,
    )
    if "error" in filings:
        return filings

    summary: dict = {
        "ticker": ticker,
        "edinet_code": resolved["edinet_code"],
        "name": resolved.get("name"),
        "name_en": resolved.get("name_en"),
        "industry": resolved.get("industry"),
        "fetched_at": _now_iso(),
        "latest_annual": None,
        "latest_quarterly": None,
        "_provenance": _make_provenance(tier="tier_a"),
    }

    latest_annual = next(
        (f for f in filings["filings"] if f["doc_type_code"] == "120"), None,
    )
    latest_quarterly = next(
        (f for f in filings["filings"] if f["doc_type_code"] == "140"), None,
    )

    if latest_annual and latest_annual.get("csv_available"):
        try:
            statements = fetch_statements(latest_annual["doc_id"])
            summary["latest_annual"] = {
                **latest_annual,
                "key_metrics": statements["key_metrics"],
            }
        except Exception as e:
            summary["latest_annual"] = {
                **latest_annual,
                "error": f"fetch_statements failed: {e}",
            }
    elif latest_annual:
        summary["latest_annual"] = {
            **latest_annual,
            "note": "CSV not available for this filing; use fetch_statements with XBRL parser (future work).",
        }

    if latest_quarterly and latest_quarterly.get("csv_available"):
        try:
            statements = fetch_statements(latest_quarterly["doc_id"])
            summary["latest_quarterly"] = {
                **latest_quarterly,
                "key_metrics": statements["key_metrics"],
            }
        except Exception as e:
            summary["latest_quarterly"] = {
                **latest_quarterly,
                "error": f"fetch_statements failed: {e}",
            }
    elif latest_quarterly:
        summary["latest_quarterly"] = {
            **latest_quarterly,
            "note": "CSV not available for this filing.",
        }

    _log("filing-summary done", f"{ticker} in {time.monotonic() - t0:.1f}s")
    return summary

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="EDINET v2 adapter for investing-toolkit (JP fundamentals, Tier A)",
    )
    parser.add_argument(
        "--action", required=True,
        choices=["resolve-code", "list-filings", "fetch-statements", "filing-summary"],
    )
    parser.add_argument("--ticker", help="4-digit JP ticker (e.g. 7203)")
    parser.add_argument("--doc-id", help="EDINET docID for fetch-statements")
    parser.add_argument(
        "--forms", default=None,
        help="Comma-separated docTypeCodes (e.g. 120,140). Default: all.",
    )
    parser.add_argument("--days", type=int, default=90, help="Scan window (default 90)")
    parser.add_argument("--limit", type=int, default=10, help="Max filings returned")
    parser.add_argument(
        "--include-raw", action="store_true",
        help="fetch-statements: also return raw_rows (~1k-10k rows per filing)",
    )
    parser.add_argument("--refresh-code-list", action="store_true",
                        help="Force-refresh the EDINET code list cache")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    if args.refresh_code_list:
        _load_code_list(refresh=True)
        print(json.dumps({"ok": True, "message": "Code list refreshed"}, indent=2))
        return

    if args.action == "resolve-code":
        if not args.ticker:
            raise SystemExit("--ticker required for resolve-code")
        result = resolve_edinet_code(args.ticker)
    elif args.action == "list-filings":
        if not args.ticker:
            raise SystemExit("--ticker required for list-filings")
        forms = (
            [f.strip() for f in args.forms.split(",")] if args.forms else None
        )
        result = list_filings(args.ticker, forms, args.days, args.limit)
    elif args.action == "fetch-statements":
        if not args.doc_id:
            raise SystemExit("--doc-id required for fetch-statements")
        result = fetch_statements(args.doc_id, include_raw=args.include_raw)
    elif args.action == "filing-summary":
        if not args.ticker:
            raise SystemExit("--ticker required for filing-summary")
        result = filing_summary(args.ticker, days=args.days)
    else:
        raise SystemExit(f"Unknown action: {args.action}")

    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
