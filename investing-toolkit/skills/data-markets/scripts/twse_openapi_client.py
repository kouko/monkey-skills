#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
twse_openapi_client.py — investing-toolkit TWSE + TPEx OpenAPI adapter

Fetches Taiwan market trading data (融資融券 / 行情 / 彙總 / 除權息) from
TWSE and TPEx public OpenAPI.

No auth required. Pure HTTPS GET. Primary-source grounding: Tier A
(臺灣證券交易所官方 / 證券櫃檯買賣中心官方).

Covers 交易資料 gap that MOPS JSON API does not provide (MOPS = 公司揭露
only; trading data = TWSE/TPEx OpenAPI).

Known OpenAPI gaps (2026-Q2 snapshot):
  - 三大法人 per-stock daily buy/sell flow (T86) is NOT exposed on
    openapi.twse.com.tw; only MI_QFIIS_sort_20 (top-20 foreign share
    holders, snapshot) and MI_QFIIS_cat (by industry category) are.
    For daily 三大法人 flow, fall back to FinMind TaiwanStockInstitutionalInvestorsBuySell.
  - 市場合計三大法人 (BFI82U) is NOT in OpenAPI either.
  - STOCK_DAY per-ticker by specified date is NOT in OpenAPI (only
    STOCK_DAY_ALL = market-wide latest snapshot). For historical daily
    OHLCV by ticker, filter STOCK_DAY_ALL (latest session only) or fall
    back to FinMind/yfinance.

Primary-source actions exposed:
  - get_listed_companies       (/opendata/t187ap03_L)
  - get_daily_price_all        (/exchangeReport/STOCK_DAY_ALL)
  - get_daily_price            — filter STOCK_DAY_ALL by ticker (latest session)
  - get_pe_pb_yield            (/exchangeReport/BWIBBU_ALL)
  - get_margin_balance         (/exchangeReport/MI_MARGN) — TWSE 上市
  - get_qfiis_holdings         (/fund/MI_QFIIS_sort_20) — top-20 foreign holders
  - get_industry_eps_summary   (/opendata/t187ap14_L)
  - get_ex_dividend_calendar   (/opendata/t187ap34_L)
  - get_tpex_daily_close       (/tpex_mainboard_daily_close_quotes) — TPEx 上櫃
  - get_tpex_margin_balance    (/tpex_mainboard_margin_balance) — TPEx 融資融券
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone

import urllib3
import requests as _requests

import cache_util

# TWSE server SSL cert is missing Subject Key Identifier on some macOS cert
# chains, producing CERTIFICATE_VERIFY_FAILED. verify=False is required
# (same workaround as mops_client.py).
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TWSE_BASE = "https://openapi.twse.com.tw/v1"
TPEX_BASE = "https://www.tpex.org.tw/openapi/v1"

# Non-OpenAPI endpoint — backs the user-facing stock-day.html form.
# Serves historical monthly OHLCV for TWSE-listed 個股. Tier A
# (TWSE-authored) but not documented in openapi.twse.com.tw catalogue.
# Discovered via stock-day.html form inspection 2026-04-19.
TWSE_RWD_BASE = "https://www.twse.com.tw/rwd/zh/afterTrading"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

TTL_DAILY = 24 * 3600   # 24h — daily snapshots + current month of stock-day-history
TTL_STATIC = 7 * 86400  # 7d  — rarely-changing metadata (listed companies)
TTL_MONTHLY = 30 * 86400  # 30d — past months of stock-day-history (immutable)

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class TwseOpenApiError(Exception):
    """Base class for TWSE/TPEx OpenAPI client errors."""


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "twse-openapi-tw"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# HTTP core
# ---------------------------------------------------------------------------

def _get(url: str, timeout: int = 30) -> list | dict:
    """GET JSON with retry. TWSE/TPEx OpenAPI = zero-auth, zero-param."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    last_err: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = _requests.get(url, headers=headers, timeout=timeout, verify=False)
            if resp.status_code != 200:
                raise TwseOpenApiError(f"HTTP {resp.status_code}: {url}")
            # Endpoint-does-not-exist on TWSE often returns HTML error page with 200
            ct = resp.headers.get("Content-Type", "")
            if "html" in ct.lower() or resp.text.lstrip().startswith("<"):
                raise TwseOpenApiError(f"Endpoint returned HTML (not JSON): {url}")
            return resp.json()
        except (_requests.RequestException, json.JSONDecodeError, TwseOpenApiError) as e:
            last_err = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            break
    raise TwseOpenApiError(f"Failed after {MAX_RETRIES} retries: {last_err}")


def _cached_get(url: str, cache_key: str, *, ttl: int) -> tuple[list | dict, str]:
    """GET with cache; returns (data, cache_status).

    cache_util.save_cache/load_cache assume dict-shaped `data` (they merge
    `_cache`/`_cache_age_seconds`/`_cache_ttl_seconds` into it on a hit).
    Several TWSE endpoints (e.g. STOCK_DAY_ALL) return a bare JSON *list*
    of rows, not a dict — wrap those in `{"_rows": [...]}` for the round
    trip and unwrap on load (no real TWSE/TPEx payload uses `_rows` as a
    field name, so this is an unambiguous marker).
    """
    path = cache_util.cache_path("twse_openapi", cache_key)
    cached = cache_util.load_cache(path, ttl)
    if cached is not None:
        return (cached["_rows"] if "_rows" in cached else cached), "hit"
    data = _get(url)
    payload = {"_rows": data} if isinstance(data, list) else data
    cache_util.save_cache(path, payload)
    return data, "miss"


# ---------------------------------------------------------------------------
# Filter helpers — endpoints use different key names for ticker
# ---------------------------------------------------------------------------

_TICKER_KEYS = ("Code", "股票代號", "公司代號", "SecuritiesCompanyCode")


def _filter_by_ticker(rows: list, ticker: str) -> list:
    """Return rows matching ticker across known key variants."""
    out = []
    for row in rows:
        for k in _TICKER_KEYS:
            if row.get(k) == ticker:
                out.append(row)
                break
    return out


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _roc_date_to_gregorian(roc_str: str) -> str | None:
    """Convert '1150417' → '2026-04-17'."""
    if not roc_str or not roc_str.isdigit() or len(roc_str) not in (6, 7):
        return None
    try:
        roc_y = int(roc_str[:-4])
        mm = roc_str[-4:-2]
        dd = roc_str[-2:]
        return f"{roc_y + 1911}-{mm}-{dd}"
    except (ValueError, TypeError):
        return None


def _make_provenance(*, source: str, authority: str, reference_period: str | None,
                     update_cycle: str = "daily after market close",
                     lag_hint: str = "end-of-day T+0 for daily snapshots") -> dict:
    staleness = None
    if reference_period:
        try:
            ref = datetime.strptime(reference_period[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            staleness = (datetime.now(tz=timezone.utc) - ref).days
        except (ValueError, TypeError):
            pass
    return {
        "source": source,
        "source_authority": authority,
        "data_type": "official_market_data",
        "update_cycle": update_cycle,
        "typical_lag": lag_hint,
        "fetched_at": _now_iso(),
        "reference_period": reference_period,
        "staleness_days": staleness,
    }


TWSE_PROV = dict(
    source="TWSE OpenAPI (openapi.twse.com.tw)",
    authority="臺灣證券交易所 (Taiwan Stock Exchange Corporation)",
)
TPEX_PROV = dict(
    source="TPEx OpenAPI (tpex.org.tw/openapi)",
    authority="證券櫃檯買賣中心 (Taipei Exchange)",
)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class TwseOpenApiClient:
    """TWSE + TPEx OpenAPI client (zero-auth, JSON-only)."""

    # ── TWSE metadata ──────────────────────────────────────────────────

    def get_listed_companies(self) -> tuple[list, str]:
        """t187ap03_L — all 上市 companies basic info (~1080 rows, 1.3 MB)."""
        return _cached_get(
            f"{TWSE_BASE}/opendata/t187ap03_L",
            "listed_companies.json",
            ttl=TTL_STATIC,
        )

    # ── TWSE price / quote ─────────────────────────────────────────────

    def get_daily_price_all(self) -> tuple[list, str]:
        """STOCK_DAY_ALL — all 上市 OHLCV latest session (~1350 rows)."""
        return _cached_get(
            f"{TWSE_BASE}/exchangeReport/STOCK_DAY_ALL",
            "daily_price_all.json",
            ttl=TTL_DAILY,
        )

    def get_pe_pb_yield(self) -> tuple[list, str]:
        """BWIBBU_ALL — P/E / 殖利率 / P/B daily (~1070 rows)."""
        return _cached_get(
            f"{TWSE_BASE}/exchangeReport/BWIBBU_ALL",
            "pe_pb_yield.json",
            ttl=TTL_DAILY,
        )

    # ── TWSE margin / institutional ────────────────────────────────────

    def get_margin_balance(self) -> tuple[list, str]:
        """MI_MARGN — 上市融資融券 daily (~1260 rows, 股票代號-keyed)."""
        return _cached_get(
            f"{TWSE_BASE}/exchangeReport/MI_MARGN",
            "margin_balance.json",
            ttl=TTL_DAILY,
        )

    def get_qfiis_holdings(self) -> tuple[list, str]:
        """MI_QFIIS_sort_20 — top-20 stocks by foreign-investor holding %.

        Note: this is a snapshot of holding ratio, NOT daily buy/sell flow.
        For daily 三大法人 flow, use FinMind fallback.
        """
        return _cached_get(
            f"{TWSE_BASE}/fund/MI_QFIIS_sort_20",
            "qfiis_holdings_top20.json",
            ttl=TTL_DAILY,
        )

    # ── TWSE reference ─────────────────────────────────────────────────

    def get_industry_eps_summary(self) -> tuple[list, str]:
        """t187ap14_L — quarterly per-company EPS / 營收 / 營益 / 淨利 (~1070 rows)."""
        return _cached_get(
            f"{TWSE_BASE}/opendata/t187ap14_L",
            "industry_eps_summary.json",
            ttl=TTL_DAILY,
        )

    def get_ex_dividend_calendar(self) -> tuple[list, str]:
        """t187ap34_L — 股東會 / 除權息公告 calendar (~3100 rows)."""
        return _cached_get(
            f"{TWSE_BASE}/opendata/t187ap34_L",
            "ex_dividend_calendar.json",
            ttl=TTL_DAILY,
        )

    # ── TPEx ───────────────────────────────────────────────────────────

    def get_tpex_daily_close(self) -> tuple[list, str]:
        """tpex_mainboard_daily_close_quotes — all 上櫃 OHLCV (~10600 rows)."""
        return _cached_get(
            f"{TPEX_BASE}/tpex_mainboard_daily_close_quotes",
            "tpex_daily_close.json",
            ttl=TTL_DAILY,
        )

    def get_tpex_margin_balance(self) -> tuple[list, str]:
        """tpex_mainboard_margin_balance — 上櫃融資融券 daily (~900 rows)."""
        return _cached_get(
            f"{TPEX_BASE}/tpex_mainboard_margin_balance",
            "tpex_margin_balance.json",
            ttl=TTL_DAILY,
        )

    # ── TWSE historical OHLCV (/rwd/ endpoint, v1.16.3+) ───────────────

    def get_stock_day_history_month(self, ticker: str, yyyymmdd: str
                                    ) -> tuple[dict, str]:
        """One month of daily OHLCV for a single TWSE-listed ticker.

        Wraps the TWSE /rwd/ stock-day.html backing endpoint. Passing any
        YYYYMMDD within the target month returns the full month of trading
        days. Historical months (not current) are immutable → 30-day
        TTL; the current month is still accumulating → 1-day TTL.

        Args:
            ticker: 4-digit 証券コード (e.g. "2330" for TSMC)
            yyyymmdd: any date string within the target month (e.g.
                "20260401" for April 2026)

        Returns:
            (raw response dict, cache_status) — see _normalize_stock_day
            for field extraction downstream.
        """
        current_yyyymm = datetime.now().strftime("%Y%m")
        target_yyyymm = yyyymmdd[:6]
        ttl = TTL_DAILY if target_yyyymm == current_yyyymm else TTL_MONTHLY
        url = (
            f"{TWSE_RWD_BASE}/STOCK_DAY"
            f"?date={yyyymmdd}&stockNo={ticker}&response=json"
        )
        return _cached_get(
            url, f"stock_day_{ticker}_{target_yyyymm}.json", ttl=ttl,
        )


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------

def _roc_slash_to_gregorian(roc_slash: str) -> str | None:
    """Convert '115/04/01' → '2026-04-01' (TWSE /rwd/ format uses slashes)."""
    if not roc_slash:
        return None
    try:
        parts = roc_slash.strip().split("/")
        if len(parts) != 3:
            return None
        roc_y, mm, dd = int(parts[0]), int(parts[1]), int(parts[2])
        return f"{roc_y + 1911:04d}-{mm:02d}-{dd:02d}"
    except (ValueError, TypeError):
        return None


def _strip_number(s: str) -> float | None:
    """Strip thousands separators + parse as float. '46,457,423' → 46457423.0.
    Returns None on empty/unparsable (e.g. '--' no-data marker)."""
    if s is None:
        return None
    try:
        return float(str(s).replace(",", "").replace("+", "").strip())
    except (ValueError, TypeError):
        return None


def _normalize_stock_day_rows(raw_month: dict) -> list[dict]:
    """Convert one month's /rwd/ STOCK_DAY response into ta_client-friendly
    OHLCV dicts (lowercase fields, Gregorian dates, parsed floats).

    Input schema (from TWSE /rwd/):
        fields: ["日期", "成交股數", "成交金額", "開盤價", "最高價",
                 "最低價", "收盤價", "漲跌價差", "成交筆數", "註記"]
        data: [["115/04/01", "46,457,423", ..., "1,840.00", "1,855.00",
                "1,830.00", "1,855.00", "+95.00", "103,263", ""], ...]
    Output: [{"date": "2026-04-01", "open": 1840.0, "high": 1855.0,
              "low": 1830.0, "close": 1855.0, "volume": 46457423.0}, ...]
    """
    if raw_month.get("stat") != "OK":
        return []
    rows = raw_month.get("data") or []
    out: list[dict] = []
    for r in rows:
        if not isinstance(r, list) or len(r) < 7:
            continue
        iso_date = _roc_slash_to_gregorian(r[0])
        if not iso_date:
            continue
        close = _strip_number(r[6])
        if close is None:  # skip rows with no Close price
            continue
        out.append({
            "date": iso_date,
            "open":   _strip_number(r[3]),
            "high":   _strip_number(r[4]),
            "low":    _strip_number(r[5]),
            "close":  close,
            "volume": _strip_number(r[1]),
        })
    return out


def _extract_date(rows: list) -> str | None:
    """Extract ROC date from first row's Date/出表日期 field, convert to YYYY-MM-DD."""
    if not rows or not isinstance(rows[0], dict):
        return None
    for k in ("Date", "出表日期", "日期"):
        v = rows[0].get(k)
        if v:
            conv = _roc_date_to_gregorian(str(v))
            if conv:
                return conv
    return None


def _envelope(action: str, data, *, cache_status: str, prov_kwargs: dict,
              reference_period: str | None = None,
              extra: dict | None = None) -> dict:
    out = {
        "action": action,
        "fetched_at": _now_iso(),
        "_cache": cache_status,
        "_provenance": _make_provenance(
            reference_period=reference_period, **prov_kwargs,
        ),
        "data": data,
    }
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

def _run_action(args) -> dict:
    _log(f"{args.action} fetch", args.ticker or "(no ticker)")
    client = TwseOpenApiClient()
    action = args.action
    ticker = args.ticker

    # ── TWSE metadata ──
    if action == "listed-companies":
        rows, cache = client.get_listed_companies()
        if ticker:
            rows = _filter_by_ticker(rows, ticker)
            data = rows[0] if rows else {}
        else:
            data = rows
        return _envelope(
            action, data, cache_status=cache, prov_kwargs=TWSE_PROV,
            extra={"ticker": ticker, "count": len(rows) if not ticker else (1 if data else 0)},
        )

    # ── TWSE price ──
    if action == "daily-price-all":
        rows, cache = client.get_daily_price_all()
        ref = _extract_date(rows)
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TWSE_PROV,
            reference_period=ref, extra={"count": len(rows)},
        )

    if action == "daily-price":
        if not ticker:
            raise SystemExit("--ticker required for daily-price")
        rows, cache = client.get_daily_price_all()
        matched = _filter_by_ticker(rows, ticker)
        ref = _extract_date(matched or rows)
        data = matched[0] if matched else {}
        return _envelope(
            action, data, cache_status=cache, prov_kwargs=TWSE_PROV,
            reference_period=ref,
            extra={
                "ticker": ticker,
                "note": (
                    "STOCK_DAY_ALL exposes latest-session snapshot only; "
                    "historical by-date queries are not in TWSE OpenAPI. "
                    "Use FinMind TaiwanStockPrice for history."
                    if not matched else None
                ),
            },
        )

    if action == "pe-pb-yield":
        rows, cache = client.get_pe_pb_yield()
        ref = _extract_date(rows)
        if ticker:
            matched = _filter_by_ticker(rows, ticker)
            data = matched[0] if matched else {}
            return _envelope(
                action, data, cache_status=cache, prov_kwargs=TWSE_PROV,
                reference_period=ref, extra={"ticker": ticker},
            )
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TWSE_PROV,
            reference_period=ref, extra={"count": len(rows)},
        )

    # ── TWSE margin / investors ──
    if action == "margin-balance":
        rows, cache = client.get_margin_balance()
        # MI_MARGN has no Date field on rows — use today as ref
        if ticker:
            matched = _filter_by_ticker(rows, ticker)
            data = matched[0] if matched else {}
            return _envelope(
                action, data, cache_status=cache, prov_kwargs=TWSE_PROV,
                extra={"ticker": ticker},
            )
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TWSE_PROV,
            extra={"count": len(rows)},
        )

    if action == "three-investor":
        # Gap: daily 三大法人 per-stock flow (T86 / BFI82U) not in OpenAPI.
        # Best approximation: MI_QFIIS_sort_20 (top-20 foreign-holding snapshot).
        rows, cache = client.get_qfiis_holdings()
        matched = _filter_by_ticker(rows, ticker) if ticker else rows
        data = (matched[0] if ticker and matched else matched) if matched else (
            {} if ticker else []
        )
        gap_note = (
            "TWSE OpenAPI exposes only MI_QFIIS_sort_20 (top-20 foreign "
            "shareholder snapshot, NOT daily buy/sell flow). For daily "
            "三大法人 per-stock flow, use FinMind "
            "TaiwanStockInstitutionalInvestorsBuySell."
        )
        return _envelope(
            action, data, cache_status=cache, prov_kwargs=TWSE_PROV,
            extra={"ticker": ticker, "note": gap_note},
        )

    # ── TWSE reference ──
    if action == "industry-eps":
        rows, cache = client.get_industry_eps_summary()
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TWSE_PROV,
            extra={"count": len(rows)},
        )

    if action == "ex-dividend-calendar":
        rows, cache = client.get_ex_dividend_calendar()
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TWSE_PROV,
            extra={"count": len(rows)},
        )

    # ── TPEx ──
    if action == "tpex-daily-close":
        rows, cache = client.get_tpex_daily_close()
        ref = _extract_date(rows)
        if ticker:
            matched = _filter_by_ticker(rows, ticker)
            data = matched[0] if matched else {}
            return _envelope(
                action, data, cache_status=cache, prov_kwargs=TPEX_PROV,
                reference_period=ref, extra={"ticker": ticker},
            )
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TPEX_PROV,
            reference_period=ref, extra={"count": len(rows)},
        )

    if action == "tpex-margin-balance":
        rows, cache = client.get_tpex_margin_balance()
        ref = _extract_date(rows)
        if ticker:
            matched = _filter_by_ticker(rows, ticker)
            data = matched[0] if matched else {}
            return _envelope(
                action, data, cache_status=cache, prov_kwargs=TPEX_PROV,
                reference_period=ref, extra={"ticker": ticker},
            )
        return _envelope(
            action, rows, cache_status=cache, prov_kwargs=TPEX_PROV,
            reference_period=ref, extra={"count": len(rows)},
        )

    # ── TWSE historical OHLCV (v1.16.3+) ──
    if action == "stock-day-history":
        if not ticker:
            raise SystemExit("--ticker required for stock-day-history")
        months = getattr(args, "months", None) or 12
        months = max(1, min(int(months), 60))  # 1..60 months clamp

        today = datetime.now()
        all_rows: list[dict] = []
        any_miss = False
        per_month_status: list[str] = []
        for offset in range(months):
            y = today.year
            m = today.month - offset
            while m <= 0:
                m += 12
                y -= 1
            yyyymmdd = f"{y:04d}{m:02d}01"
            try:
                raw, cache = client.get_stock_day_history_month(ticker, yyyymmdd)
            except TwseOpenApiError as e:
                per_month_status.append(f"{y:04d}-{m:02d}=error:{e}")
                continue
            if cache == "miss":
                any_miss = True
            per_month_status.append(f"{y:04d}-{m:02d}={cache}")
            all_rows.extend(_normalize_stock_day_rows(raw))

        # Sort + de-dupe by date (months may overlap at month boundaries)
        by_date: dict[str, dict] = {}
        for r in all_rows:
            by_date[r["date"]] = r
        data = sorted(by_date.values(), key=lambda r: r["date"])

        latest = data[-1] if data else None
        return _envelope(
            action, data, cache_status=("miss" if any_miss else "hit"),
            prov_kwargs=TWSE_PROV,
            reference_period=latest["date"] if latest else None,
            extra={
                "ticker": ticker,
                "period": f"{months}mo",
                "rows": len(data),
                "latest_date": latest["date"] if latest else None,
                "latest_close": latest["close"] if latest else None,
                "_months_fetched": per_month_status,
                "_endpoint": (
                    "twse.com.tw/rwd/zh/afterTrading/STOCK_DAY "
                    "(Tier A, not in openapi.twse.com.tw catalogue; "
                    "month-granularity; discovered via stock-day.html 2026-04-19)"
                ),
            },
        )

    raise SystemExit(f"Unknown action: {action}")



def main():
    parser = argparse.ArgumentParser(
        description="TWSE + TPEx OpenAPI adapter for investing-toolkit",
    )
    parser.add_argument(
        "--action", required=True,
        choices=[
            "listed-companies",
            "daily-price", "daily-price-all",
            "stock-day-history",
            "pe-pb-yield",
            "margin-balance", "three-investor",
            "industry-eps", "ex-dividend-calendar",
            "tpex-daily-close", "tpex-margin-balance",
        ],
    )
    parser.add_argument("--ticker", help="Taiwan stock ticker (e.g. 2330)")
    parser.add_argument("--months", type=int, default=12,
                        help="stock-day-history: months back (1-60, default 12)")
    parser.add_argument("--date", help="(reserved — OpenAPI returns latest only)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass cache for this run")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")

    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    if args.no_cache:
        try:
            twse_cache_dir = cache_util.resolve_cache_dir() / "twse_openapi"
            for p in twse_cache_dir.glob("*"):
                p.unlink()
        except Exception:
            pass

    t_main = time.monotonic()
    try:
        result = _run_action(args)
    except TwseOpenApiError as e:
        result = {"action": args.action, "error": str(e)}

    cache_status = result.get("_cache") if isinstance(result, dict) else None
    cache_label = "cache hit" if cache_status == "hit" else f"in {time.monotonic() - t_main:.1f}s"
    _log(f"{args.action} done", f"{args.ticker or ''} {cache_label}".strip())
    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))
    sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
    main()
