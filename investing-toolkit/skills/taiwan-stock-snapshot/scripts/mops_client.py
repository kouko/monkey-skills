#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["requests==2.33.1"]
# ///
"""
mops_client.py — investing-toolkit MOPS JSON API adapter

Fetches Taiwan individual stock data from the new MOPS /mops/api/* endpoints
(public JSON API at mops.twse.com.tw, launched 2025-02).

No auth / session / cookie / CSRF required. User-Agent header mandatory
(Mozilla/5.0). Conservative 0.3s throttle between calls.

Year format: ROC calendar (民國年 = 西元 - 1911). 2024 = ROC 113.

Error semantics (all HTTP 200 with code in body):
  code:200 查詢成功            → success
  code:406 查無相符資料        → warning, return empty
  code:500 傳入參數異常        → raise MopsParameterError
  HTTP 302                      → raise MopsEndpointError

Primary-source grounding: Tier A (金管會法定揭露 / 證期局 / TWSE).

Usage:
  # Company basic
  uv run mops_client.py --ticker 2330 --action company-basic

  # Financial statements (ROC 113 = 2024)
  uv run mops_client.py --ticker 2330 --action balance-sheet --year 113 --season 4
  uv run mops_client.py --ticker 2330 --action income-statement --year 113 --season 4
  uv run mops_client.py --ticker 2330 --action cash-flow --year 113 --season 4

  # Monthly revenue (ROC 115 / 3 = 2026-03)
  uv run mops_client.py --ticker 2330 --action monthly-revenue --year 115 --month 3

  # Realtime announcements
  uv run mops_client.py --action realtime-announcements --market sii --count 10
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import urllib3
import requests as _requests

# Suppress InsecureRequestWarning — MOPS TWSE server has a known SSL certificate
# issue (missing Subject Key Identifier) on some macOS cert chains.
# verify=False is required.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MOPS_BASE = "https://mops.twse.com.tw/mops/api"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

_CACHE_BASE = os.environ.get("INVESTING_TOOLKIT_CACHE") or str(
    Path.home() / ".cache" / "investing-toolkit"
)
CACHE_DIR = Path(_CACHE_BASE) / "mops"

TTL_CURRENT = 86400           # 24h — current-quarter / recent data
TTL_HISTORICAL = None         # permanent — past periods don't change
TTL_REALTIME = 300            # 5 min — live announcement feed
HISTORICAL_AGE_DAYS = 90

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0
THROTTLE_SECONDS = 0.3


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class MopsError(Exception):
    """Base class for MOPS client errors."""


class MopsParameterError(MopsError):
    """Raised when MOPS returns code:500 (傳入參數異常)."""


class MopsEndpointError(MopsError):
    """Raised when MOPS returns HTTP 302 (endpoint not found)."""


# ---------------------------------------------------------------------------
# ROC calendar
# ---------------------------------------------------------------------------

def _roc_to_gregorian(roc_year: int) -> int:
    return roc_year + 1911


def _gregorian_to_roc(year: int) -> int:
    return year - 1911


# ---------------------------------------------------------------------------
# Cache
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
        path.write_text(json.dumps(data, default=str, ensure_ascii=False, indent=2))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# HTTP core
# ---------------------------------------------------------------------------

def _post(endpoint: str, body: dict) -> dict:
    """POST to /mops/api/{endpoint}, return result dict.

    Raises MopsEndpointError on HTTP 302, MopsParameterError on code:500.
    Returns {} on code:406 (no data). Returns result dict on code:200.
    """
    url = f"{MOPS_BASE}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(THROTTLE_SECONDS)
            resp = _requests.post(
                url, headers=headers, json=body,
                timeout=30, allow_redirects=False,
                verify=False,  # TWSE SSL cert missing Subject Key Identifier on macOS
            )

            if resp.status_code == 302:
                raise MopsEndpointError(f"MOPS endpoint not found: {endpoint}")

            if resp.status_code != 200:
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                raise MopsError(f"MOPS HTTP {resp.status_code}: {endpoint}")

            payload = resp.json()
            code = payload.get("code")
            message = payload.get("message", "")

            if code == 200:
                return payload.get("result", {}) or {}
            if code == 406:
                # 查無相符資料 — normal for period with no data
                print(
                    f"[mops_client] WARN {endpoint}: {message} (body={body})",
                    file=sys.stderr,
                )
                return {}
            if code == 500:
                raise MopsParameterError(
                    f"MOPS parameter error on {endpoint}: {message} (body={body})"
                )
            # Unknown code — treat as error
            raise MopsError(
                f"MOPS unexpected code={code} on {endpoint}: {message}"
            )

        except _requests.exceptions.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            raise MopsError(f"MOPS request timed out: {endpoint}")
        except _requests.exceptions.ConnectionError as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                continue
            raise MopsError(f"MOPS connection error on {endpoint}: {e}")

    raise MopsError(f"MOPS request failed after retries: {endpoint}")


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _make_provenance(reference_period: str | None = None, *,
                     lag_hint: str = "varies by form; quarterly FS ~45 days after period-end",
                     update_cycle: str = "filing-driven") -> dict:
    fetched_at = _now_iso()
    staleness = None
    if reference_period:
        try:
            # Try a few parse formats: "YYYY-MM-DD", "YYYY-Qn", "YYYY-MM"
            rp = reference_period
            if "-Q" in rp:
                y, q = rp.split("-Q")
                # End of quarter ~ midpoint
                month = int(q) * 3
                ref = datetime(int(y), month, 1, tzinfo=timezone.utc)
            elif len(rp) == 7 and "-" in rp:  # YYYY-MM
                y, m = rp.split("-")
                ref = datetime(int(y), int(m), 1, tzinfo=timezone.utc)
            else:
                ref = datetime.strptime(rp[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            staleness = (datetime.now(tz=timezone.utc) - ref).days
        except (ValueError, TypeError):
            pass
    return {
        "source": "MOPS JSON API (mops.twse.com.tw/mops/api)",
        "source_authority": "金管會證期局 / 台灣證券交易所",
        "data_type": "official_regulatory_disclosure",
        "update_cycle": update_cycle,
        "typical_lag": lag_hint,
        "fetched_at": fetched_at,
        "reference_period": reference_period,
        "staleness_days": staleness,
    }


# ---------------------------------------------------------------------------
# Cache key helper — historical data gets permanent cache after 90 days
# ---------------------------------------------------------------------------

def _is_historical(year_roc: int | None, season: int | None = None,
                   month: int | None = None) -> bool:
    """Decide if (year, season/month) is >= 90 days in the past."""
    if year_roc is None:
        return False
    year = _roc_to_gregorian(year_roc)
    if season is not None:
        # End of season
        end_month = season * 3
    elif month is not None:
        end_month = month
    else:
        end_month = 12
    try:
        # First day of month *after* period-end
        if end_month == 12:
            period_end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            period_end = datetime(year, end_month + 1, 1, tzinfo=timezone.utc)
    except ValueError:
        return False
    age = (datetime.now(tz=timezone.utc) - period_end).days
    return age > HISTORICAL_AGE_DAYS


def _cached_post(endpoint: str, body: dict, cache_key: str,
                 *, ttl: int | None = TTL_CURRENT) -> tuple[dict, str]:
    """POST with cache; returns (result, cache_status)."""
    path = _cache_path(cache_key)
    cached = _load_cache(path, ttl)
    if cached is not None:
        return cached, "hit"
    result = _post(endpoint, body)
    _save_cache(path, result)
    return result, "miss"


# ---------------------------------------------------------------------------
# MOPS client — 16 endpoints
# ---------------------------------------------------------------------------

class MopsClient:
    """MOPS JSON API client (Taiwan individual stock fundamentals)."""

    # ── Company metadata ────────────────────────────────────────────────

    def get_company_basic(self, ticker: str) -> tuple[dict, str]:
        """t05st03 公司基本資料"""
        return _cached_post(
            "t05st03",
            {"companyId": ticker},
            f"company_basic_{ticker}.json",
            ttl=TTL_CURRENT,
        )

    def get_company_overview(self, ticker: str) -> tuple[dict, str]:
        """t146sb05 公司總覽"""
        return _cached_post(
            "t146sb05",
            {"companyId": ticker},
            f"company_overview_{ticker}.json",
            ttl=TTL_CURRENT,
        )

    # ── Financial statements (quarterly) ────────────────────────────────

    def _fs_body(self, ticker: str, year: int, season: int) -> dict:
        return {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "season": str(season),
            "subsidiaryCompanyId": "",
        }

    def _fs_ttl(self, year: int, season: int) -> int | None:
        return TTL_HISTORICAL if _is_historical(year, season=season) else TTL_CURRENT

    def get_balance_sheet(self, ticker: str, year: int, season: int) -> tuple[dict, str]:
        """t164sb03 資產負債表 (~67 rows)"""
        return _cached_post(
            "t164sb03", self._fs_body(ticker, year, season),
            f"balance_sheet_{ticker}_{year}Q{season}.json",
            ttl=self._fs_ttl(year, season),
        )

    def get_income_statement(self, ticker: str, year: int, season: int) -> tuple[dict, str]:
        """t164sb04 綜合損益表 (~46 rows)"""
        return _cached_post(
            "t164sb04", self._fs_body(ticker, year, season),
            f"income_statement_{ticker}_{year}Q{season}.json",
            ttl=self._fs_ttl(year, season),
        )

    def get_cash_flow(self, ticker: str, year: int, season: int) -> tuple[dict, str]:
        """t164sb05 現金流量表 (~80 rows)"""
        return _cached_post(
            "t164sb05", self._fs_body(ticker, year, season),
            f"cash_flow_{ticker}_{year}Q{season}.json",
            ttl=self._fs_ttl(year, season),
        )

    def get_financial_status(self, ticker: str, year: int, season: int) -> tuple[dict, str]:
        """t163sb01 財務報告公告 (IFRS filing status)"""
        return _cached_post(
            "t163sb01", self._fs_body(ticker, year, season),
            f"financial_status_{ticker}_{year}Q{season}.json",
            ttl=self._fs_ttl(year, season),
        )

    # ── Monthly revenue ─────────────────────────────────────────────────

    def get_monthly_revenue(self, ticker: str, year: int, month: int) -> tuple[dict, str]:
        """t05st10_ifrs 月營收"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "month": str(month),
            "subsidiaryCompanyId": "",
        }
        ttl = TTL_HISTORICAL if _is_historical(year, month=month) else TTL_CURRENT
        return _cached_post(
            "t05st10_ifrs", body,
            f"monthly_revenue_{ticker}_{year}M{month:02d}.json",
            ttl=ttl,
        )

    # ── Dividends + holdings ────────────────────────────────────────────

    def get_dividends(self, ticker: str, first_year: int, last_year: int,
                      query_type: str = "1") -> tuple[dict, str]:
        """t05st09_2 股利分派"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "firstYear": str(first_year),
            "lastYear": str(last_year),
            "queryType": query_type,
        }
        return _cached_post(
            "t05st09_2", body,
            f"dividends_{ticker}_{first_year}_{last_year}_q{query_type}.json",
            ttl=TTL_CURRENT,
        )

    def get_director_holdings(self, ticker: str, year: int, month: int) -> tuple[dict, str]:
        """stapap1 董監持股餘額"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "month": str(month),
            "subsidiaryCompanyId": "",
        }
        ttl = TTL_HISTORICAL if _is_historical(year, month=month) else TTL_CURRENT
        return _cached_post(
            "stapap1", body,
            f"director_holdings_{ticker}_{year}M{month:02d}.json",
            ttl=ttl,
        )

    def get_insider_trades(self, ticker: str, year: int, month: int) -> tuple[dict, str]:
        """query6_1 內部人持股異動 (must specify month, `all` returns 500)"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "month": str(month),
            "subsidiaryCompanyId": "",
        }
        ttl = TTL_HISTORICAL if _is_historical(year, month=month) else TTL_CURRENT
        return _cached_post(
            "query6_1", body,
            f"insider_trades_{ticker}_{year}M{month:02d}.json",
            ttl=ttl,
        )

    def get_ex_dividend(self, ticker: str, year: int) -> tuple[dict, str]:
        """t108sb19 除權息公告"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "month": "all",
            "firstDay": "",
            "lastDay": "",
        }
        return _cached_post(
            "t108sb19", body,
            f"ex_dividend_{ticker}_{year}.json",
            ttl=TTL_CURRENT,
        )

    # ── Governance / investment ─────────────────────────────────────────

    def get_shareholder_meetings(self, ticker: str, year: int) -> tuple[dict, str]:
        """t108sb16_q1 股東常(臨時)會"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "month": "all",
            "firstDay": "",
            "lastDay": "",
        }
        return _cached_post(
            "t108sb16_q1", body,
            f"shareholder_meetings_{ticker}_{year}.json",
            ttl=TTL_CURRENT,
        )

    def get_china_investment(self, ticker: str, year: int, season: int) -> tuple[dict, str]:
        """t05st15 赴大陸投資"""
        body = {
            "companyId": ticker,
            "dataType": "2",
            "year": str(year),
            "season": str(season),
        }
        ttl = TTL_HISTORICAL if _is_historical(year, season=season) else TTL_CURRENT
        return _cached_post(
            "t05st15", body,
            f"china_investment_{ticker}_{year}Q{season}.json",
            ttl=ttl,
        )

    # ── Announcements ───────────────────────────────────────────────────

    def get_historical_announcements(self, ticker: str, year: int) -> tuple[dict, str]:
        """t05st01 歷史重大訊息 (ROC 85+)"""
        body = {
            "companyId": ticker,
            "year": str(year),
            "month": "all",
            "firstDay": "",
            "lastDay": "",
        }
        ttl = TTL_HISTORICAL if _is_historical(year) else TTL_CURRENT
        return _cached_post(
            "t05st01", body,
            f"historical_announcements_{ticker}_{year}.json",
            ttl=ttl,
        )

    def get_day_announcements(self, year: int, month: int, day: int) -> tuple[dict, str]:
        """t05st02 當日重大訊息 (market-wide for a single day)"""
        body = {"year": str(year), "month": str(month), "day": str(day)}
        ttl = TTL_HISTORICAL if _is_historical(year, month=month) else TTL_CURRENT
        return _cached_post(
            "t05st02", body,
            f"day_announcements_{year}{month:02d}{day:02d}.json",
            ttl=ttl,
        )

    def get_realtime_announcements(self, market: str = "sii",
                                   count: int = 10) -> tuple[dict, str]:
        """home_page/t05sr01_1 即時重大訊息 (market-wide)

        Note: endpoint path has special `home_page/` prefix.
        market: "sii" (上市) or "otc" (上櫃). "all" is rejected.
        """
        if market not in ("sii", "otc"):
            raise MopsParameterError(f"market must be 'sii' or 'otc', got {market!r}")
        body = {"count": count, "marketKind": market}
        return _cached_post(
            "home_page/t05sr01_1", body,
            f"realtime_announcements_{market}_{count}.json",
            ttl=TTL_REALTIME,
        )

    # ── Broad announcement search (optional P3) ─────────────────────────

    def search_announcements(
        self,
        *,
        ticker: str = "",
        market: str = "sii",
        first_date: str,
        last_date: str,
        announcement_type: str = "1",
        scope_type: str = "1",
        announcement_basis: str = "0",
        date_type: str = "1",
        sort: str = "2",
    ) -> tuple[dict, str]:
        """t146sb10 公告查詢 — broad multi-category search.

        first_date / last_date: ROC yyMMDD strings (e.g. "1131101").
        announcement_type: 1=全部, 2=取得處分資產, 7=資金貸與, 8=背書保證,
                           19=財報聲明書, 30=股利分派(94.5.5後).
        scope_type: "1" = single company (companyId required), "2" = market-wide.
        """
        body = {
            "scopeType": scope_type,
            "companyId": ticker,
            "marketKind": market,
            "announcementBasis": announcement_basis,
            "dateType": date_type,
            "firstDate": first_date,
            "lastDate": last_date,
            "announcementType": announcement_type,
            "sort": sort,
        }
        key = (
            f"search_{ticker or 'mkt'}_{market}_{first_date}_{last_date}"
            f"_t{announcement_type}_s{scope_type}.json"
        )
        return _cached_post("t146sb10", body, key, ttl=TTL_CURRENT)


# ---------------------------------------------------------------------------
# Output envelope
# ---------------------------------------------------------------------------

def _envelope(action: str, data: dict, *, cache_status: str,
              reference_period: str | None = None,
              extra: dict | None = None) -> dict:
    out = {
        "action": action,
        "fetched_at": _now_iso(),
        "_cache": cache_status,
        "_provenance": _make_provenance(reference_period),
        "data": data,
    }
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

def _run_action(args) -> dict:
    client = MopsClient()
    action = args.action

    # actions that require --ticker + year + season
    fs_actions = {
        "balance-sheet": ("get_balance_sheet", "balance-sheet"),
        "income-statement": ("get_income_statement", "income-statement"),
        "cash-flow": ("get_cash_flow", "cash-flow"),
        "financial-status": ("get_financial_status", "financial-status"),
        "china-investment": ("get_china_investment", "china-investment"),
    }

    if action in fs_actions:
        method_name, act = fs_actions[action]
        method = getattr(client, method_name)
        data, cache = method(args.ticker, args.year, args.season)
        ref = f"{_roc_to_gregorian(args.year)}-Q{args.season}"
        return _envelope(
            act, data, cache_status=cache, reference_period=ref,
            extra={"ticker": args.ticker, "year": args.year, "season": args.season},
        )

    if action == "company-basic":
        data, cache = client.get_company_basic(args.ticker)
        return _envelope(
            "company-basic", data, cache_status=cache,
            extra={"ticker": args.ticker},
        )

    if action == "company-overview":
        data, cache = client.get_company_overview(args.ticker)
        return _envelope(
            "company-overview", data, cache_status=cache,
            extra={"ticker": args.ticker},
        )

    if action == "monthly-revenue":
        data, cache = client.get_monthly_revenue(args.ticker, args.year, args.month)
        ref = f"{_roc_to_gregorian(args.year)}-{args.month:02d}"
        return _envelope(
            "monthly-revenue", data, cache_status=cache, reference_period=ref,
            extra={"ticker": args.ticker, "year": args.year, "month": args.month},
        )

    if action == "dividends":
        data, cache = client.get_dividends(
            args.ticker, args.first_year, args.last_year, args.query_type or "1",
        )
        return _envelope(
            "dividends", data, cache_status=cache,
            extra={
                "ticker": args.ticker,
                "first_year": args.first_year,
                "last_year": args.last_year,
            },
        )

    if action == "director-holdings":
        data, cache = client.get_director_holdings(args.ticker, args.year, args.month)
        ref = f"{_roc_to_gregorian(args.year)}-{args.month:02d}"
        return _envelope(
            "director-holdings", data, cache_status=cache, reference_period=ref,
            extra={"ticker": args.ticker, "year": args.year, "month": args.month},
        )

    if action == "insider-trades":
        data, cache = client.get_insider_trades(args.ticker, args.year, args.month)
        ref = f"{_roc_to_gregorian(args.year)}-{args.month:02d}"
        return _envelope(
            "insider-trades", data, cache_status=cache, reference_period=ref,
            extra={"ticker": args.ticker, "year": args.year, "month": args.month},
        )

    if action == "ex-dividend":
        data, cache = client.get_ex_dividend(args.ticker, args.year)
        return _envelope(
            "ex-dividend", data, cache_status=cache,
            reference_period=f"{_roc_to_gregorian(args.year)}",
            extra={"ticker": args.ticker, "year": args.year},
        )

    if action == "shareholder-meetings":
        data, cache = client.get_shareholder_meetings(args.ticker, args.year)
        return _envelope(
            "shareholder-meetings", data, cache_status=cache,
            extra={"ticker": args.ticker, "year": args.year},
        )

    if action == "historical-announcements":
        data, cache = client.get_historical_announcements(args.ticker, args.year)
        return _envelope(
            "historical-announcements", data, cache_status=cache,
            extra={"ticker": args.ticker, "year": args.year},
        )

    if action == "day-announcements":
        data, cache = client.get_day_announcements(args.year, args.month, args.day)
        ref = f"{_roc_to_gregorian(args.year)}-{args.month:02d}-{args.day:02d}"
        return _envelope(
            "day-announcements", data, cache_status=cache, reference_period=ref,
            extra={"year": args.year, "month": args.month, "day": args.day},
        )

    if action == "realtime-announcements":
        data, cache = client.get_realtime_announcements(args.market, args.count)
        return _envelope(
            "realtime-announcements", data, cache_status=cache,
            extra={"market": args.market, "count": args.count},
        )

    if action == "search-announcements":
        data, cache = client.search_announcements(
            ticker=args.ticker or "",
            market=args.market,
            first_date=args.first_date,
            last_date=args.last_date,
            announcement_type=args.announcement_type or "1",
            scope_type=args.scope_type or "1",
        )
        return _envelope(
            "search-announcements", data, cache_status=cache,
            extra={
                "ticker": args.ticker,
                "market": args.market,
                "first_date": args.first_date,
                "last_date": args.last_date,
                "announcement_type": args.announcement_type,
            },
        )

    raise SystemExit(f"Unknown action: {action}")


# ---------------------------------------------------------------------------
# MCP tool registration (v1.14.0+)
# ---------------------------------------------------------------------------


def register_mcp_tools(mcp) -> None:
    """Register MOPS (Taiwan MOPS JSON API) dispatch tool with a FastMCP instance."""
    import types

    @mcp.tool()
    def mops_fetch(
        action: str,
        ticker: str | None = None,
        year: int | None = None,
        season: int | None = None,
        month: int | None = None,
        day: int | None = None,
        first_year: int | None = None,
        last_year: int | None = None,
        first_date: str | None = None,
        last_date: str | None = None,
        market: str | None = None,
        count: int | None = None,
        query_type: str | None = None,
        announcement_type: str | None = None,
        scope_type: str | None = None,
    ) -> dict:
        """Fetch data from Taiwan MOPS JSON API (primary source, zero-auth).
        `year` uses ROC calendar (西元 - 1911); e.g. 2026 → 115.

        Actions (16 endpoints):
          Financial statements (ticker + year ROC + season 1-4):
            - balance-sheet / income-statement / cash-flow
            - financial-status / china-investment
          Company info (ticker):
            - company-basic / company-overview
          Revenue/dividends:
            - monthly-revenue (ticker, year, month)
            - dividends (ticker, first_year, last_year)
            - ex-dividend (ticker, year)
          Insider / governance (ticker, year [+ month]):
            - director-holdings / insider-trades
            - shareholder-meetings / historical-announcements
          Market-wide announcements:
            - day-announcements (year, month, day)
            - realtime-announcements (market, count)
            - search-announcements (ticker/market/first_date/last_date/
              announcement_type/scope_type)
        """
        args = types.SimpleNamespace(
            action=action, ticker=ticker, year=year, season=season,
            month=month, day=day,
            first_year=first_year, last_year=last_year,
            first_date=first_date, last_date=last_date,
            market=market, count=count,
            query_type=query_type, announcement_type=announcement_type,
            scope_type=scope_type,
        )
        try:
            return _run_action(args)
        except SystemExit as e:
            return {"error": str(e), "action": action}


def main():
    parser = argparse.ArgumentParser(
        description="MOPS JSON API adapter for investing-toolkit",
    )
    parser.add_argument("--ticker", help="Taiwan stock ticker (e.g. 2330)")
    parser.add_argument(
        "--action", required=True,
        choices=[
            "company-basic", "company-overview",
            "balance-sheet", "income-statement", "cash-flow",
            "financial-status", "monthly-revenue",
            "dividends", "director-holdings", "insider-trades",
            "ex-dividend", "shareholder-meetings", "china-investment",
            "historical-announcements", "day-announcements",
            "realtime-announcements", "search-announcements",
        ],
    )
    parser.add_argument("--year", type=int, help="ROC year (民國年; 2024 = 113)")
    parser.add_argument("--season", type=int, help="Quarter 1-4")
    parser.add_argument("--month", type=int, help="Month 1-12")
    parser.add_argument("--day", type=int, help="Day 1-31 (day-announcements)")
    parser.add_argument("--first-year", type=int, dest="first_year",
                        help="First ROC year for dividends range")
    parser.add_argument("--last-year", type=int, dest="last_year",
                        help="Last ROC year for dividends range")
    parser.add_argument("--query-type", dest="query_type", default="1",
                        help="dividends queryType (1 or 2)")
    parser.add_argument("--market", default="sii", choices=["sii", "otc"],
                        help="Market kind (default sii)")
    parser.add_argument("--count", type=int, default=10,
                        help="realtime-announcements count (default 10)")
    parser.add_argument("--first-date", dest="first_date",
                        help="search-announcements first date (ROC yyMMDD)")
    parser.add_argument("--last-date", dest="last_date",
                        help="search-announcements last date (ROC yyMMDD)")
    parser.add_argument("--announcement-type", dest="announcement_type",
                        help="search-announcements type code")
    parser.add_argument("--scope-type", dest="scope_type",
                        help="search-announcements scope (1=company, 2=market)")
    parser.add_argument("--no-cache", action="store_true",
                        help="Bypass cache for this run")

    args = parser.parse_args()

    # Cheap validation for common cases
    needs_ticker = {
        "company-basic", "company-overview",
        "balance-sheet", "income-statement", "cash-flow",
        "financial-status", "monthly-revenue",
        "dividends", "director-holdings", "insider-trades",
        "ex-dividend", "shareholder-meetings", "china-investment",
        "historical-announcements",
    }
    if args.action in needs_ticker and not args.ticker:
        print(f"--ticker required for --action {args.action}", file=sys.stderr)
        sys.exit(2)

    if args.no_cache:
        # Best-effort: clear matching cache files
        try:
            for p in CACHE_DIR.glob("*"):
                if args.ticker and args.ticker in p.name:
                    p.unlink()
                elif not args.ticker and args.action.replace("-", "_") in p.name:
                    p.unlink()
        except Exception:
            pass

    try:
        result = _run_action(args)
    except MopsEndpointError as e:
        result = {"action": args.action, "error": f"endpoint: {e}"}
    except MopsParameterError as e:
        result = {"action": args.action, "error": f"parameter: {e}"}
    except MopsError as e:
        result = {"action": args.action, "error": str(e)}

    print(json.dumps(result, default=str, ensure_ascii=False, indent=2))
    sys.exit(1 if "error" in result else 0)


if __name__ == "__main__":
    main()
