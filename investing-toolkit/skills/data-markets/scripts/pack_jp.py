"""
pack_jp.py — investing-toolkit JP market pack builder.

Migrated from skills/data-jp/scripts/pack.py (fetch-only Japan data
bundler); the CLI shell is dropped here — the unified `pack.py` facade
(data-markets/scripts/pack.py, T4) owns argument parsing, market
auto-detection, and the exit-code contract. This module exposes the
pure `build_pack(pack_name, tickers)` dispatcher + `SUPPORTED_PACKS`,
the interface shared identically across all 5 market pack modules.

Composes yfinance .T + EDINET (Tier A) / TDnet + BOJ + estat + ECB into
named "packs" that downstream Layer-2 analysis / Layer-3 report skills
consume verbatim. No analysis, no scoring, no verdicts.

Pack types
----------
  snapshot          single ticker — yfinance info + 2y price history
                                    + recent TDnet timely-disclosure index
                                    (always available; no key needed)
  memo-fetch        single ticker — snapshot
                                    + EDINET 有報/四半期/material events IF
                                      EDINET_API_KEY is set (Tier A)
                                    + yfinance financials fallback otherwise
                                      (provenance label "Tier 2 fallback")
  comps-multiples   single OR batch — yfinance info filtered to multiples-only
                                      fields (trailingPE, forwardPE,
                                      priceToSales, priceToBook,
                                      enterpriseToEbitda, enterpriseToRevenue,
                                      marketCap, enterpriseValue)
  screener-batch    batch — lightweight yfinance batch (info + 1y price)
  regime-pack       no ticker — BOJ rates + estat CPI/IP/unemployment
                                + ESRI 景気動向指数 CI 一致/先行 + 機械受注
                                + Tankan 業況判断 DI (4 categories)
                                + ECB JP real 10Y yield (always Tier A)

Ticker convention
-----------------
4-digit JP 証券コード (e.g. 7203, 6758, 9984). Auto-appends `.T`
when calling yfinance. EDINET/TDnet take the bare 4-digit code.

Tier routing (memo-fetch only)
------------------------------
EDINET_API_KEY env var detected at runtime:
  set     → Tier A: EDINET filing-summary + material events + TDnet
  unset   → Tier 2 fallback: yfinance financials annual + quarterly,
            JSON `_provenance.tier_label = "Tier 2 fallback"`,
            `_provenance.upgrade_hint` includes EDINET registration URL.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "pack-jp"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()

# Multiples-only field whitelist for comps-multiples pack.
COMPS_FIELDS = (
    "trailingPE",
    "forwardPE",
    "priceToSales",
    "priceToBook",
    "enterpriseToEbitda",
    "enterpriseToRevenue",
    "marketCap",
    "enterpriseValue",
)

EDINET_REGISTER_URL = (
    "https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html"
)


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _to_yf_ticker(code: str) -> str:
    """4-digit JP code -> .T suffix; pass through if suffix already present."""
    code = code.strip().upper()
    if code.endswith((".T", ".TO")):
        return code
    return f"{code}.T"


def _bare_ticker(code: str) -> str:
    """Strip .T / .TO -> bare 4-digit code (for EDINET / TDnet)."""
    code = code.strip().upper()
    for suffix in (".T", ".TO"):
        if code.endswith(suffix):
            return code[: -len(suffix)]
    return code


def _client_timeout() -> int:
    """Per-subprocess timeout in seconds. Override via DATA_JP_CLIENT_TIMEOUT env."""
    raw = os.environ.get("DATA_JP_CLIENT_TIMEOUT", "").strip()
    if raw:
        try:
            val = int(raw)
            if val > 0:
                return val
        except ValueError:
            pass
    return 300


def _run_client(script: str, args: list[str]) -> dict[str, Any]:
    """Run a sibling client script and return its parsed JSON.

    Cache location resolves via cache_util's ladder (INVESTING_TOOLKIT_CACHE
    override > XDG default); we just inherit the parent's environment.

    Subprocess wall-clock timeout defaults to 300s; override with the
    DATA_JP_CLIENT_TIMEOUT env var. On timeout, returns a structured-error
    payload matching the existing shape.
    """
    cmd = ["uv", "run", str(SCRIPT_DIR / script), *args]
    timeout = _client_timeout()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError as e:
        return {"error": f"uv not on PATH: {e}", "_cmd": cmd}
    except subprocess.TimeoutExpired:
        return {"error": f"client timeout after {timeout}s", "_cmd": cmd}

    payload: dict[str, Any]
    if proc.stdout.strip():
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            payload = {
                "error": f"client returned non-JSON: {e}",
                "_stdout_head": proc.stdout[:500],
            }
    else:
        payload = {"error": "client returned empty stdout"}

    if proc.returncode != 0 and "error" not in payload:
        payload["error"] = (
            f"exit {proc.returncode}; stderr={proc.stderr.strip()[:300]}"
        )
    # Only attach _stderr on failure — yfinance / other libs print
    # FutureWarning / DeprecationWarning to stderr on success, and Layer 2/3
    # consumers may treat the field as an error signal.
    if (
        proc.stderr.strip()
        and (proc.returncode != 0 or "error" in payload)
        and "_stderr" not in payload
    ):
        payload["_stderr"] = proc.stderr.strip()[:500]
    return payload


# --------------------------------------------------------------------------- #
# Pack: snapshot
# --------------------------------------------------------------------------- #


_YF_LABEL_MAP_JP = {
    "revenue": ["Total Revenue", "Operating Revenue"],
    "operating_income": ["Operating Income", "Total Operating Income As Reported"],
    "net_income": ["Net Income", "Net Income Common Stockholders"],
    "operating_cash_flow": ["Operating Cash Flow"],
    "capex": ["Capital Expenditure"],
    "free_cash_flow": ["Free Cash Flow"],
    "long_term_debt": ["Long Term Debt"],
    "short_term_debt": ["Current Debt"],
    "total_debt": ["Total Debt"],
    "cash": ["Cash And Cash Equivalents"],
}


def _build_canonical_from_yf_financials_jp(financials: dict) -> dict:
    """T3 (yfinance Tier 2 fallback for JP) — extract canonical statements
    from yfinance --action financials annual output. Per ADR-0003.

    Note: yfinance reports JP issuers' consolidated (連結) statements in
    JPY (or sometimes USD for ADRs — caller responsible). Most-recent-first,
    annual depth 5.
    """
    if not isinstance(financials, dict):
        financials = {}
    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}
    periods = sorted(set(income) | set(balance) | set(cashflow), reverse=True)[:5]

    def _extract(src: dict, canonical: str) -> tuple[list[float], str | None]:
        labels = _YF_LABEL_MAP_JP.get(canonical, [])
        used_label: str | None = None
        out: list[float] = []
        for p in periods:
            row = src.get(p, {})
            v = None
            for label in labels:
                if label in row and row[label] is not None:
                    v = row[label]
                    if used_label is None:
                        used_label = label
                    break
            if v is not None:
                try:
                    out.append(float(v))
                except (TypeError, ValueError):
                    pass
        return out, used_label

    revenue, rev_label = _extract(income, "revenue")
    operating_income, op_label = _extract(income, "operating_income")
    net_income, ni_label = _extract(income, "net_income")
    ocf, ocf_label = _extract(cashflow, "operating_cash_flow")
    capex_raw, capex_label = _extract(cashflow, "capex")
    fcf, fcf_label = _extract(cashflow, "free_cash_flow")
    long_term_debt, ltd_label = _extract(balance, "long_term_debt")
    short_term_debt, std_label = _extract(balance, "short_term_debt")
    total_debt_raw, td_label = _extract(balance, "total_debt")
    cash, cash_label = _extract(balance, "cash")

    capex = [abs(v) for v in capex_raw]
    total_debt = total_debt_raw if total_debt_raw else [
        (long_term_debt[i] if i < len(long_term_debt) else 0.0)
        + (short_term_debt[i] if i < len(short_term_debt) else 0.0)
        for i in range(max(len(long_term_debt), len(short_term_debt)))
    ]

    def _meta(canonical: str, label: str | None, periods_used: list[str]) -> dict:
        return {
            "source_label": label,
            "source_labels_tried": _YF_LABEL_MAP_JP.get(canonical, []),
            "fiscal_year_ends": periods_used[: len(periods_used)],
            "accounting_standard": "ifrs",  # yfinance default; some JP issuers use jp_gaap (caller checks jp_specific)
            "unit": "JPY",
            "tier": "Tier 2 (yfinance scraper — EDINET preferred)",
        }

    return {
        "income_statement": {
            "revenue": revenue,
            "operating_income": operating_income,
            "ebit": operating_income,
            "net_income": net_income,
            "_meta": {
                "revenue": _meta("revenue", rev_label, periods[: len(revenue)]),
                "operating_income": _meta("operating_income", op_label, periods[: len(operating_income)]),
                "ebit": {**_meta("operating_income", op_label, periods[: len(operating_income)]), "note": "alias of operating_income"},
                "net_income": _meta("net_income", ni_label, periods[: len(net_income)]),
            },
        },
        "cash_flow": {
            "operating_cash_flow": ocf,
            "capex": capex,
            "fcf": fcf,
            "_meta": {
                "operating_cash_flow": _meta("operating_cash_flow", ocf_label, periods[: len(ocf)]),
                "capex": {**_meta("capex", capex_label, periods[: len(capex)]), "note": "absolute value"},
                "fcf": _meta("free_cash_flow", fcf_label, periods[: len(fcf)]),
            },
        },
        "balance_sheet": {
            "long_term_debt": long_term_debt,
            "short_term_debt": short_term_debt,
            "total_debt": total_debt,
            "cash": cash,
            "_meta": {
                "long_term_debt": _meta("long_term_debt", ltd_label, periods[: len(long_term_debt)]),
                "short_term_debt": _meta("short_term_debt", std_label, periods[: len(short_term_debt)]),
                "total_debt": (
                    _meta("total_debt", td_label, periods[: len(total_debt)])
                    if total_debt_raw
                    else {
                        "source_label": None,
                        "derivation": "long_term_debt + short_term_debt",
                        "components": {"long_term_debt": ltd_label, "short_term_debt": std_label},
                    }
                ),
                "cash": _meta("cash_and_equivalents", cash_label, periods[: len(cash)]),
            },
        },
    }


def pack_snapshot(ticker_code: str, period: str = "2y") -> dict[str, Any]:
    """yfinance info + price history + recent TDnet timely-disclosure index."""
    yf = _to_yf_ticker(ticker_code)
    bare = _bare_ticker(ticker_code)
    _log("snapshot start", bare)
    t0 = time.monotonic()

    _log("pack [info]", yf)
    info = _run_client("yfinance_client.py", ["--ticker", yf, "--action", "info"])
    _log("pack [history]", f"{yf} period={period}")
    history = _run_client(
        "yfinance_client.py",
        ["--ticker", yf, "--action", "history", "--period", period],
    )
    _log("pack [tdnet]", bare)
    tdnet = _run_client(
        "tdnet_client.py", ["--ticker", bare, "--limit", "20"]
    )
    _log("snapshot done", f"{bare} in {time.monotonic() - t0:.1f}s")

    rows = history.get("data", []) if isinstance(history, dict) else []
    return {
        "pack": "snapshot",
        "ticker": bare,
        "yf_ticker": yf,
        "fetched_at": _now_iso(),
        "info": info,
        "price_history": history,
        "history": rows,  # T1 canonical OHLCV alias (cross-country symmetric)
        "timely_disclosures": tdnet,
        "_provenance": {
            "tier": "tier_1",
            "tier_label": "Tier 1 (yfinance + TDnet, no key needed)",
            "sources": [
                "Yahoo Finance (.T)",
                "TDnet via Yanoshin",
            ],
        },
    }


# --------------------------------------------------------------------------- #
# Pack: memo-fetch (tier-routed)
# --------------------------------------------------------------------------- #


def pack_memo_fetch(
    ticker_code: str, period: str = "2y", days: int = 365
) -> dict[str, Any]:
    """Snapshot + (Tier A EDINET filings | Tier 2 yfinance financials fallback)."""
    _log("memo-fetch start", ticker_code)
    t0 = time.monotonic()
    base = pack_snapshot(ticker_code, period=period)
    base["pack"] = "memo-fetch"

    yf = base["yf_ticker"]
    bare = base["ticker"]

    has_key = bool(os.environ.get("EDINET_API_KEY"))
    _log("memo-fetch tier", "A (EDINET)" if has_key else "2 (yfinance fallback)")

    if has_key:
        # Tier A: EDINET filing summary + material events
        _log("pack [edinet filing-summary]", bare)
        filing_summary = _run_client(
            "edinet_client.py",
            [
                "--action",
                "filing-summary",
                "--ticker",
                bare,
                "--days",
                str(days),
            ],
        )
        _log("pack [edinet material-events]", bare)
        material_events = _run_client(
            "edinet_client.py",
            [
                "--action",
                "list-filings",
                "--ticker",
                bare,
                "--forms",
                "180,220,350",
                "--days",
                "180",
                "--limit",
                "15",
            ],
        )
        base["fundamentals"] = {
            "tier": "tier_a",
            "tier_label": "Tier A (EDINET)",
            "filing_summary": filing_summary,
        }
        base["material_events"] = material_events
        base["_provenance"] = {
            "tier": "tier_a",
            "tier_label": "Tier A (EDINET 金融庁 primary-source)",
            "sources": [
                "EDINET v2 (金融庁)",
                "TDnet via Yanoshin",
                "Yahoo Finance (.T)",
            ],
            "license": "PDL 1.0 (EDINET)",
        }
    else:
        # Tier 2 fallback: yfinance financials
        _log("pack [yf financials annual]", yf)
        annual = _run_client(
            "yfinance_client.py",
            ["--ticker", yf, "--action", "financials", "--period", "annual"],
        )
        _log("pack [yf financials quarterly]", yf)
        quarterly = _run_client(
            "yfinance_client.py",
            ["--ticker", yf, "--action", "financials", "--period", "quarterly"],
        )
        base["fundamentals"] = {
            "tier": "tier_2",
            "tier_label": "Tier 2 fallback",
            "annual": annual,
            "quarterly": quarterly,
        }
        base["material_events"] = {
            "_skipped": "EDINET_API_KEY not set; material events (180/220/350) unavailable in Tier 2 fallback",
        }
        base["_provenance"] = {
            "tier": "tier_2",
            "tier_label": "Tier 2 fallback",
            "sources": [
                "Yahoo Finance (.T) financials (Yahoo-scraped, may diverge from regulator filings)",
                "TDnet via Yanoshin",
            ],
            "upgrade_hint": (
                "Set EDINET_API_KEY to switch to Tier A primary-source 金融庁 "
                f"filings. Register free at {EDINET_REGISTER_URL}"
            ),
        }
        # T3 canonical staging — Tier 2 yfinance fallback path
        canonical = _build_canonical_from_yf_financials_jp(annual)
        base["income_statement"] = canonical["income_statement"]
        base["cash_flow"] = canonical["cash_flow"]
        base["balance_sheet"] = canonical["balance_sheet"]

    # Common across both tiers — T1+T3 canonical surface
    info_dict = base.get("info") if isinstance(base.get("info"), dict) else {}
    base["shares_outstanding"] = info_dict.get("sharesOutstanding") if info_dict else None
    base["current_price"] = info_dict.get("regularMarketPrice") if info_dict else None
    if has_key:
        # Tier A path — EDINET filing_summary contains key_metrics; multi-year
        # extraction into canonical arrays is deferred to a future PR. Emit
        # placeholder canonical blocks so downstream readers find expected keys.
        base.setdefault("income_statement", {
            "revenue": [], "operating_income": [], "ebit": [], "net_income": [],
            "_meta": {"note": "Tier A EDINET multi-year canonical extraction deferred. See fundamentals.filing_summary for raw."},
        })
        base.setdefault("cash_flow", {
            "operating_cash_flow": [], "capex": [], "fcf": [],
            "_meta": {"note": "Tier A EDINET multi-year canonical extraction deferred."},
        })
        base.setdefault("balance_sheet", {
            "long_term_debt": [], "short_term_debt": [], "total_debt": [], "cash": [],
            "_meta": {"note": "Tier A EDINET multi-year canonical extraction deferred."},
        })
    base["jp_specific"] = {
        "ordinary_income_note": "経常利益 (recurring profit / pre-tax) is JP-specific; not in canonical income_statement. EDINET key_metrics expose it directly when EDINET_API_KEY is set; yfinance Tier 2 does not surface it.",
        "consolidated_basis_note": "yfinance reports JP issuers' consolidated (連結) statements. 単体 (parent-only) is exposed by EDINET 有報 type=5 CSV when key set.",
        "accounting_standard_note": "JP issuers may use JP-GAAP, IFRS, or 米基準 — varies per issuer and may switch mid-history. yfinance Tier 2 does not disclose which; EDINET filing_summary identifies the standard via accountingStandardsDEI.",
    }
    _log("memo-fetch done", f"{ticker_code} in {time.monotonic() - t0:.1f}s")
    return base


# --------------------------------------------------------------------------- #
# Pack: comps-multiples
# --------------------------------------------------------------------------- #


def _filter_multiples(info_payload: dict[str, Any]) -> dict[str, Any]:
    """Whitelist only multiples + size fields from a yfinance info payload."""
    if not isinstance(info_payload, dict):
        return {"error": "info payload not a dict"}
    if "error" in info_payload:
        return info_payload
    return {k: info_payload.get(k) for k in COMPS_FIELDS}


def pack_comps_multiples(ticker_codes: list[str]) -> dict[str, Any]:
    """yfinance multiples-only fields for one ticker or a batch (anchor + peers).

    Uses a single batch `yfinance_client.py --tickers a,b,c --action info`
    invocation (one Python interpreter spin-up + one uv resolution) and splits
    the result per ticker, instead of N serial subprocesses.
    """
    _log("comps-multiples start", f"{len(ticker_codes)} ticker(s)")
    t0 = time.monotonic()
    yf_tickers = [_to_yf_ticker(c) for c in ticker_codes]
    bare_tickers = [_bare_ticker(c) for c in ticker_codes]

    out: dict[str, Any] = {
        "pack": "comps-multiples",
        "fetched_at": _now_iso(),
        "tickers": [],
        "_provenance": {
            "tier": "tier_1",
            "tier_label": "Tier 1 (yfinance multiples)",
            "sources": ["Yahoo Finance (.T)"],
            "fields": list(COMPS_FIELDS),
        },
    }

    _log("pack [batch info]", f"{len(yf_tickers)} tickers")
    batch = _run_client(
        "yfinance_client.py",
        ["--tickers", ",".join(yf_tickers), "--action", "info"],
    )

    # Batch shape: {"mode": "batch", "tickers": {"7203.T": {...}, ...}, ...}
    # On batch-level error (e.g. uv missing, timeout), `error` is set and
    # `tickers` is absent — fall back to per-ticker error payloads so the
    # output shape stays stable for downstream consumers.
    per_ticker_info = batch.get("tickers") if isinstance(batch, dict) else None
    batch_error = (
        batch.get("error") if isinstance(batch, dict) and "error" in batch else None
    )

    info_by_ticker: dict[str, dict] = {}
    for yf, bare in zip(yf_tickers, bare_tickers):
        if isinstance(per_ticker_info, dict) and yf.upper() in per_ticker_info:
            info = per_ticker_info[yf.upper()]
        elif batch_error is not None:
            info = {"error": batch_error}
        else:
            info = {"error": "ticker missing from batch response"}
        multiples = _filter_multiples(info)
        out["tickers"].append(
            {
                "ticker": bare,
                "yf_ticker": yf,
                "multiples": multiples,
            }
        )
        if isinstance(multiples, dict) and "error" not in multiples:
            info_by_ticker[bare] = multiples
    # T1 canonical multiples alias — analysis-comps reads pack.info[ticker]
    out["info"] = info_by_ticker
    _log("comps-multiples done", f"{len(ticker_codes)} ticker(s) in {time.monotonic() - t0:.1f}s")
    return out


# --------------------------------------------------------------------------- #
# Pack: screener-batch
# --------------------------------------------------------------------------- #


def pack_screener_batch(
    ticker_codes: list[str], period: str = "1y"
) -> dict[str, Any]:
    """Lightweight yfinance batch — info + price history for many tickers."""
    _log("screener-batch start", f"{len(ticker_codes)} tickers period={period}")
    t0 = time.monotonic()
    yf_tickers = [_to_yf_ticker(c) for c in ticker_codes]
    _log("pack [batch info]", f"{len(yf_tickers)} tickers")
    info_batch = _run_client(
        "yfinance_client.py",
        ["--tickers", ",".join(yf_tickers), "--action", "info"],
    )
    _log("pack [batch history]", f"{len(yf_tickers)} tickers period={period}")
    history_batch = _run_client(
        "yfinance_client.py",
        [
            "--tickers",
            ",".join(yf_tickers),
            "--action",
            "history",
            "--period",
            period,
        ],
    )
    _log("screener-batch done", f"{len(ticker_codes)} tickers in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "screener-batch",
        "fetched_at": _now_iso(),
        "tickers": [_bare_ticker(c) for c in ticker_codes],
        "yf_tickers": yf_tickers,
        "info_batch": info_batch,
        "history_batch": history_batch,
        "_provenance": {
            "tier": "tier_1",
            "tier_label": "Tier 1 (yfinance batch)",
            "sources": ["Yahoo Finance (.T)"],
        },
    }


# --------------------------------------------------------------------------- #
# Pack: regime-pack
# --------------------------------------------------------------------------- #


def _flatten_regime_to_series(root: dict) -> dict:
    """T2 canonical (per ADR-0002) — walk regime-pack root and emit flat
    `series: {indicator_id: [floats]}` block for analysis-macro-regime.
    Identical helper to data-kr / data-cn / data-tw.
    """
    flat: dict[str, list[float]] = {}

    def visit(node, path):
        if not isinstance(node, dict):
            return
        obs = node.get("observations")
        if isinstance(obs, list):
            values = []
            for o in obs:
                if isinstance(o, dict) and o.get("value") is not None:
                    try:
                        values.append(float(o["value"]))
                    except (TypeError, ValueError):
                        pass
            if not values:
                return
            preset = node.get("preset")
            series_field = node.get("series")
            if isinstance(preset, str):
                primary = preset
            elif isinstance(series_field, str):
                primary = series_field
            elif path:
                primary = path[-1]
            else:
                return
            if primary not in flat:
                flat[primary] = values
            if len(path) >= 2 and isinstance(path[0], str):
                key = f"{path[0]}.{primary}"
                if key not in flat:
                    flat[key] = values
            return
        for k, v in node.items():
            if isinstance(k, str) and k.startswith("_"):
                continue
            if isinstance(v, dict):
                visit(v, path + (k,))

    for k, v in root.items():
        if isinstance(k, str) and k.startswith("_"):
            continue
        if isinstance(v, dict):
            visit(v, (k,))
    return flat


def pack_regime() -> dict[str, Any]:
    """BOJ + estat + ECB macro indicators (no per-ticker dimension)."""
    _log("regime-pack start", "JP macro bundle")
    t0 = time.monotonic()
    today = dt.date.today()
    start_yyyymm = (today - dt.timedelta(days=730)).strftime("%Y%m")

    _log("pack [boj call-rate]", f"FM01/STRDCLUCON from {start_yyyymm}")
    boj_call = _run_client(
        "boj_client.py",
        ["--db", "FM01", "--code", "STRDCLUCON", "--start-date", start_yyyymm],
    )
    _log("pack [boj tankan-price-outlook]", "1/3/5Y")
    boj_tankan_outlook = _run_client(
        "boj_client.py",
        [
            "--tankan-price-outlook",
            "--horizons",
            "1,3,5",
            "--periods",
            "8",
        ],
    )
    _log("pack [boj tankan-business-di]", "4 categories")
    boj_tankan_business_di = _run_client(
        "boj_client.py",
        [
            "--tankan-business-di",
            "--periods",
            "12",
        ],
    )
    # PR-3 (ADR-0004): coincident-index / leading-index / machine-orders added
    # to the regime-pack preset list. The presets exist in estat_client.py;
    # they were simply omitted from pack.py's call. classify_jp.py reads
    # ESRI 景気動向指数 CI as its native cycle proxy (replaces the previous
    # missing coincident-index resolve in _legacy_ic.py).
    _log("pack [estat macro]", "8 presets")
    estat_macro = _run_client(
        "estat_client.py",
        [
            "--preset",
            "cpi,core-cpi,ip,unemployment,jgb10y,"
            "coincident-index,leading-index,machine-orders",
        ],
    )
    _log("pack [ecb real-yield]", "JP 10Y")
    ecb_real_yield = _run_client(
        "ecb_client.py",
        [
            "--series",
            "M.JP.JPY.4F.BB.R_JP10YT_RR.YLDA",
            "--periods",
            "24",
        ],
    )

    groups_dict = {
        "rates": {"call_rate_on": boj_call},
        "inflation": {"estat": estat_macro},
        # ESRI 景気動向指数 CI (一致 / 先行) lives under estat too — the
        # T2 flatten helper extracts each indicator by its preset name, so
        # `coincident-index` / `leading-index` / `machine-orders` will surface
        # as top-level series keys regardless of which group they sit under.
        "cycle": {"estat_cycle_alias": {"_note": "see groups.inflation.estat — coincident/leading/machine-orders presets are flattened to series"}},
        "business_sentiment": {"tankan_business_di": boj_tankan_business_di},
        "real_rates": {
            "real_10y_monthly_ecb": ecb_real_yield,
            "tankan_inflation_outlook": boj_tankan_outlook,
        },
    }
    _log("regime-pack done", f"in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "regime-pack",
        "fetched_at": _now_iso(),
        "groups": groups_dict,
        "series": _flatten_regime_to_series(groups_dict),  # T2 canonical
        "_provenance": {
            "tier": "tier_a",
            "tier_label": "Tier A (BOJ + 統計DB + ECB primary-source)",
            "sources": [
                "BOJ Time-Series API (日銀, FM01 + CO Tankan)",
                "Statistics Dashboard / 統計DB (e-Stat — CPI / Core-CPI / IP / "
                "Unemployment / JGB10y / ESRI 景気動向指数 CI / 機械受注)",
                "ECB Data Portal",
            ],
        },
    }


# --------------------------------------------------------------------------- #
# Unified interface — SUPPORTED_PACKS + build_pack(pack_name, tickers)
# --------------------------------------------------------------------------- #


SUPPORTED_PACKS: tuple[str, ...] = (
    "snapshot",
    "memo-fetch",
    "comps-multiples",
    "screener-batch",
    "regime-pack",
)


def build_pack(pack_name: str, tickers: list[str]) -> dict[str, Any]:
    """Dispatch to the pack builder matching `pack_name`.

    `tickers` semantics mirror the original CLI:
      - snapshot / memo-fetch: exactly one ticker (tickers[0])
      - comps-multiples / screener-batch: one or more tickers
      - regime-pack: no ticker dimension; `tickers` is ignored
    """
    if pack_name not in SUPPORTED_PACKS:
        raise ValueError(
            f"unknown pack {pack_name!r}; supported: {sorted(SUPPORTED_PACKS)}"
        )
    if pack_name == "regime-pack":
        return pack_regime()
    if pack_name == "snapshot":
        if not tickers:
            raise ValueError("snapshot requires exactly one ticker")
        return pack_snapshot(tickers[0])
    if pack_name == "memo-fetch":
        if not tickers:
            raise ValueError("memo-fetch requires exactly one ticker")
        return pack_memo_fetch(tickers[0])
    if pack_name == "comps-multiples":
        if not tickers:
            raise ValueError("comps-multiples requires at least one ticker")
        return pack_comps_multiples(tickers)
    if pack_name == "screener-batch":
        if not tickers:
            raise ValueError("screener-batch requires at least one ticker")
        return pack_screener_batch(tickers)
    raise ValueError(f"unhandled pack {pack_name!r}")  # pragma: no cover
