"""pack_cn.py — data-markets Layer 1 facade for China (CN).

Composes multi-source pulls into 5 pack types via `build_pack(pack_name,
tickers)`, the common interface shared across all 5 market pack modules
(pack_us / pack_jp / pack_tw / pack_kr / pack_cn) so the unified
`pack.py` facade (Task 4) can dispatch uniformly:

  snapshot         Quick overview card (yfinance info + price)
  memo-fetch       Equity memo full data (yfinance financials; CN
                    primary-source disclosure not in scope)
  comps-multiples  Multiples-only (yfinance), 1+ tickers
  screener-batch   Lightweight batch fields (yfinance batch)
  regime-pack      NBS macro (21 presets) + akshare PBOC/Caixin (8) + FRED USDCNY

Tier routing (CN):
  - NBS new-SPA API (primary, 21 indicators): nbs_client.py
  - PBOC + SHIBOR + Caixin PMI (aggregator, 8 indicators): akshare_client.py
  - USDCNY cross-rate + FX reserves: fred_client.py (canonical copy is
    Task 3a's — US-owned, invoked here only via subprocess by filename)
  - .SS (Shanghai) / .SZ (Shenzhen) / .HK individual stocks: yfinance_client.py
    (canonical copy is Task 3a's; auto-suffix appended if user passes a
    bare 6-digit code or HK 4-digit code)

No CLI shell — `build_pack` is called by the unified pack.py facade
(Task 4), which owns argument parsing and the exit-code contract.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Pack types this market supports — the data-markets common interface
# (see module docstring). Must match data-cn/scripts/pack.py's legacy
# `--pack` argparse choices.
SUPPORTED_PACKS: tuple[str, ...] = (
    "snapshot", "memo-fetch", "comps-multiples", "screener-batch", "regime-pack",
)


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "pack-cn"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()

# NBS preset list (21 indicators across 9 groups — see SKILL.md)
NBS_PRESETS = [
    # inflation
    "cpi-yoy", "core-cpi", "ppi-yoy",
    # growth
    "gdp-yoy", "industrial-yoy", "retail-yoy", "fai-yoy",
    # trade
    "exports-yoy", "imports-yoy", "trade-balance",
    # labor
    "urban-unemployment",
    # pmi (NBS official)
    "pmi-manufacturing", "pmi-non-manufacturing", "pmi-composite",
    # money
    "m2-yoy", "m1-yoy",
    # realestate
    "realestate-investment-yoy", "housing-sales-area-yoy",
    "housing-sales-value-yoy", "realestate-funding-yoy",
    # services
    "services-production-yoy",
]

# akshare preset list (8 indicators: PBOC rates + credit + Caixin PMI)
AKSHARE_PRESETS = [
    "lpr-1y", "lpr-5y", "rrr-major", "shibor-3m",
    "shrzgm", "new-loans",
    "caixin-mfg-pmi", "caixin-svc-pmi",
]

# FRED series for CN cross-rate + FX reserves
FRED_SERIES = ["DEXCHUS", "TRESEGCNM052N"]

# Macro market indices (overlay, optional in regime-pack)
MARKET_TICKERS = ["000300.SS", "000001.SS", "399006.SZ", "^HSI", "^HSCE"]


# ---------------------------------------------------------------------------
# Ticker normalisation (.SS / .SZ / .HK auto-suffix)
# ---------------------------------------------------------------------------

def _normalise_ticker(t: str) -> str:
    """Append exchange suffix if a bare numeric code is passed.

    Heuristic (CN/HK convention):
      - already has '.' suffix     -> unchanged
      - starts with '6' or '9' (6-digit) -> .SS  (Shanghai: 600/601/603/605/688/900)
      - starts with '0', '2', '3' (6-digit) -> .SZ  (Shenzhen: 000/002/300/301)
      - 4 digits (e.g. '0700', '9988') -> .HK  (Hong Kong)
      - 5 digits (e.g. '09988', '02318', '03690') -> .HK  (Hong Kong, leading-zero form)
      - otherwise unchanged + stderr warning. BSE (北京证券交易所, 4xx/8xx)
        and other unsupported formats fall through unchanged.
    """
    t = t.strip().upper()
    if "." in t or t.startswith("^"):
        return t
    if not t.isdigit():
        return t
    if len(t) == 4:
        return f"{t}.HK"
    if len(t) == 5:
        return f"{t}.HK"
    if len(t) == 6:
        first = t[0]
        if first in ("6", "9"):
            return f"{t}.SS"
        if first in ("0", "2", "3"):
            return f"{t}.SZ"
        # 6-digit BSE codes start with 4 or 8 (e.g. 430xxx, 830xxx, 870xxx) —
        # yfinance does not cover BSE; warn and pass through.
        if first in ("4", "8"):
            print(
                f"WARNING: BSE ticker '{t}' detected — yfinance does not cover "
                "Beijing Stock Exchange (北京证券交易所); pack will likely fail. "
                "BSE primary-source disclosure is not in v2.0.0 scope.",
                file=sys.stderr,
            )
            return t
    print(
        f"WARNING: Unrecognized CN ticker format: '{t}' "
        "(expected 4-digit HK / 5-digit HK / 6-digit SSE/SZSE). "
        "Passing through unchanged — yfinance may fail.",
        file=sys.stderr,
    )
    return t


def _normalise_ticker_list(csv: str) -> list[str]:
    return [_normalise_ticker(t) for t in csv.split(",") if t.strip()]


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> dict:
    """Run a client script and return parsed JSON (or error dict)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=False,
        )
    except FileNotFoundError as e:
        return {"_error": f"command not found: {e}", "_cmd": " ".join(cmd)}

    if result.returncode != 0 and not result.stdout.strip():
        return {
            "_error": f"client exited rc={result.returncode}",
            "_cmd": " ".join(cmd),
            "_stderr": result.stderr.strip()[-500:],
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return {
            "_error": f"invalid JSON from client: {e}",
            "_cmd": " ".join(cmd),
            "_stdout_head": result.stdout[:500],
            "_stderr": result.stderr.strip()[-500:],
        }


def _yf(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "yfinance_client.py"), *args])


def _nbs(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "nbs_client.py"), *args])


def _akshare(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "akshare_client.py"), *args])


def _fred(args: list[str]) -> dict:
    return _run(["uv", "run", str(SCRIPT_DIR / "fred_client.py"), *args])


# ---------------------------------------------------------------------------
# Pack builders
# ---------------------------------------------------------------------------

_YF_LABEL_MAP = {
    # yfinance row label → canonical field
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


def _build_canonical_from_yf_financials(financials: dict) -> dict:
    """T3 (yfinance Tier 2 fallback) — extract canonical statements from
    yfinance --action financials annual output. Per ADR-0003.
    Most-recent-first ordering, annual depth 5.
    """
    if not isinstance(financials, dict):
        financials = {}
    income = financials.get("income_statement") or {}
    balance = financials.get("balance_sheet") or {}
    cashflow = financials.get("cash_flow") or {}
    periods = sorted(set(income) | set(balance) | set(cashflow), reverse=True)[:5]

    def _extract(src: dict, canonical: str) -> tuple[list[float], str | None]:
        labels = _YF_LABEL_MAP.get(canonical, [])
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
            "source_labels_tried": _YF_LABEL_MAP.get(canonical, []),
            "fiscal_year_ends": periods_used[: len(periods_used)],
            "accounting_standard": "cas",  # China Accounting Standards (converged-with-IFRS)
            "unit": "CNY",
            "tier": "Tier 2 (yfinance scraper — cninfo/HKEXnews deferred)",
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


def pack_snapshot(ticker: str) -> dict:
    """Quick overview: yfinance info + 6mo price history."""
    _log("snapshot start", ticker)
    t0 = time.monotonic()
    t = _normalise_ticker(ticker)
    _log("pack [yf history 6mo]", t)
    yfinance_history = _yf(["--ticker", t, "--action", "history",
                            "--period", "6mo", "--interval", "1d"])
    rows = yfinance_history.get("data", []) if isinstance(yfinance_history, dict) else []
    _log("pack [yf info]", t)
    info = _yf(["--ticker", t, "--action", "info"])
    _log("snapshot done", f"{t} in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "snapshot",
        "ticker": t,
        "country": "CN",
        "yfinance_info": info,
        "yfinance_history": yfinance_history,  # raw envelope per Principle 1
        "history": rows,  # T1 canonical OHLCV alias (cross-country symmetric)
    }


def pack_memo_fetch(ticker: str) -> dict:
    """Memo data. Tier 2 only — CN primary-source individual-stock
    disclosure (e.g. CSRC-mandated annual reports via cninfo) is not
    yet integrated; yfinance financials is the current floor."""
    _log("memo-fetch start", ticker)
    t0 = time.monotonic()
    t = _normalise_ticker(ticker)
    _log("pack [yf info]", t)
    info = _yf(["--ticker", t, "--action", "info"])
    _log("pack [yf history 2y]", t)
    yfinance_history = _yf(["--ticker", t, "--action", "history",
                            "--period", "2y", "--interval", "1d"])
    _log("pack [yf financials annual]", t)
    fin_annual = _yf(["--ticker", t, "--action", "financials", "--period", "annual"])
    _log("pack [yf financials quarterly]", t)
    fin_quarterly = _yf(["--ticker", t, "--action", "financials", "--period", "quarterly"])
    rows = yfinance_history.get("data", []) if isinstance(yfinance_history, dict) else []
    canonical = _build_canonical_from_yf_financials(fin_annual)
    info_dict = info if isinstance(info, dict) else {}
    _log("memo-fetch done", f"{t} in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "memo-fetch",
        "ticker": t,
        "country": "CN",
        "_provenance": {
            "tier": 2,
            "tier_reason": ("CN primary-source individual-stock disclosure "
                            "not in v2.0.0 scope"),
            "primary_source_status": "deferred",
            "primary_source_candidates": ["cninfo (CSRC)", "HKEXnews"],
        },
        "tier_note": ("Tier 2 only — CN primary-source individual-stock "
                      "disclosure (cninfo / HKEXnews) not in v2.0.0 scope. "
                      "yfinance financials is the current floor."),
        "yfinance_info": info,
        "yfinance_history": yfinance_history,  # raw envelope
        "history": rows,  # T1 canonical OHLCV alias
        "yfinance_financials_annual": fin_annual,  # raw per Principle 1
        "yfinance_financials_quarterly": fin_quarterly,
        # T3 canonical staging (Tier 2 yfinance fallback per ADR-0003)
        "income_statement": canonical["income_statement"],
        "cash_flow": canonical["cash_flow"],
        "balance_sheet": canonical["balance_sheet"],
        "shares_outstanding": info_dict.get("sharesOutstanding"),
        "current_price": info_dict.get("regularMarketPrice"),
        "cn_specific": {
            "primary_source_note": "cninfo (CSRC-mandated annual reports) / HKEXnews integration deferred. All canonical financials are yfinance Tier 2 (CAS / converged-IFRS via Yahoo). CNY for A-shares, HKD for .HK tickers.",
            "consolidated_basis_note": "yfinance reports consolidated (合并) statements. Parent-only (母公司) and segment data not exposed; needs cninfo for full granularity.",
        },
    }


def pack_comps_multiples_single(ticker: str) -> dict:
    """Multiples for one ticker. Used as anchor or per-peer in
    analysis-comps."""
    t = _normalise_ticker(ticker)
    info = _yf(["--ticker", t, "--action", "info"])
    multiples = {}
    # yfinance_client emits info fields at top level of the result dict.
    if isinstance(info, dict):
        for k in ("trailingPE", "forwardPE", "enterpriseToEbitda",
                  "priceToSalesTrailing12Months", "priceToBook"):
            v = info.get(k)
            if v is not None:
                multiples[k] = v
    return {
        "ticker": t,
        "country": "CN",
        "multiples": multiples,
        "_yfinance_info": info,
        # T1 canonical alias: analysis-comps reads pack.info[ticker]
        "info": {t: multiples} if multiples else {},
    }


def pack_comps_multiples_batch(tickers: list[str]) -> dict:
    """Multiples for a list. analysis-comps consumes anchor + peers."""
    _log("comps-multiples start", f"{len(tickers)} tickers")
    t0 = time.monotonic()
    out = []
    info_dict: dict = {}
    for i, t in enumerate(tickers, 1):
        _log(f"pack [info {i}/{len(tickers)}]", t)
        single = pack_comps_multiples_single(t)
        out.append(single)
        if single.get("multiples"):
            info_dict[single["ticker"]] = single["multiples"]
    _log("comps-multiples done", f"{len(tickers)} tickers in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "comps-multiples",
        "country": "CN",
        "tickers": out,
        "info": info_dict,  # T1 canonical multiples alias (cross-country symmetric)
    }


def pack_screener_batch(tickers: list[str]) -> dict:
    """Lightweight batch fetch via yfinance batch mode.

    Note: tickers are expected to be already normalised by the caller
    (mirrors comps-multiples pattern); this function is a no-op on
    already-normalised input.
    """
    _log("screener-batch start", f"{len(tickers)} tickers")
    t0 = time.monotonic()
    csv = ",".join(tickers)
    _log("pack [batch info]", f"{len(tickers)} tickers")
    info_batch = _yf(["--tickers", csv, "--action", "info"])
    _log("pack [batch history 6mo]", f"{len(tickers)} tickers")
    history_batch = _yf(["--tickers", csv, "--action", "history",
                         "--period", "6mo", "--interval", "1d"])
    _log("screener-batch done", f"{len(tickers)} tickers in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "screener-batch",
        "country": "CN",
        "tickers": tickers,
        "yfinance_info_batch": info_batch,
        "yfinance_history_batch": history_batch,
    }


def _flatten_regime_to_series(root: dict) -> dict:
    """T2 canonical (per ADR-0002) — walk regime-pack root and emit flat
    `series: {indicator_id: [floats]}` block for analysis-macro-regime
    resolve_series. Identical helper to data-kr / data-jp / data-tw.

    Walks nested dicts; treats nodes with `observations: [{date, value}]`
    as leaves; keys by `preset` (preferred) / `series` string / deepest path.
    Also emits group-prefixed keys. Skips keys starting with `_`.
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


def _compute_credit_impulse(
    tsf_stock_yoy: list[float] | None,
    tsf_flow_monthly: list[float] | None,
    m2_yoy: list[float] | None,
) -> dict | None:
    """Credit impulse proxy (CN-specific).

    Per CICC convention (中金 2022; 国信 2023): TSF stock yoy 12-month
    rolling change. Specifically: latest TSF stock yoy minus 12-mo
    lagged TSF stock yoy = credit impulse (in pp). Positive value =
    expanding credit; negative = contracting.

    Path priority:
      1. `tsf_stock_yoy` direct (preferred — PBOC-published series).
      2. `tsf_flow_monthly` (akshare `shrzgm`) → derive stock-yoy proxy
         via trailing-12m sum, then take 12mo Δ. ±0.3pp drift vs PBOC
         published; acceptable for cycle-direction signal.
      3. `m2_yoy` 12mo Δ — last-resort fallback (M2 ↔ credit linkage
         weakened by 2024-2025 re-categorization).

    Returns dict with `value` (pp), `trend` (expanding/contracting/
    neutral), `methodology`, and intermediate `tsf_stock_yoy_proxy_now`
    when path 2 is used.

    See `analysis-macro-regime/references/credit-impulse-methodology.md`
    for full grounding.
    """
    threshold_pp = 0.5  # |Δ| > 0.5pp → trend tag fires (~2/3 sigma)

    def _trend(impulse_pp: float) -> str:
        if impulse_pp > threshold_pp:
            return "expanding"
        if impulse_pp < -threshold_pp:
            return "contracting"
        return "neutral"

    if tsf_stock_yoy and len(tsf_stock_yoy) >= 13:
        impulse = tsf_stock_yoy[-1] - tsf_stock_yoy[-13]
        return {
            "value": round(impulse, 3),
            "trend": _trend(impulse),
            "threshold_pp": threshold_pp,
            "methodology": "TSF stock yoy 12-month change (CICC convention)",
            "source": "tsf_stock_yoy direct",
        }

    if tsf_flow_monthly and len(tsf_flow_monthly) >= 25:
        recent_sum = sum(tsf_flow_monthly[-12:])
        prior_sum_t12 = sum(tsf_flow_monthly[-24:-12])
        if prior_sum_t12 != 0:
            stock_yoy_now = (recent_sum - prior_sum_t12) / prior_sum_t12 * 100
        else:
            stock_yoy_now = None
        if len(tsf_flow_monthly) >= 37:
            prior_recent = sum(tsf_flow_monthly[-24:-12])
            prior_prior = sum(tsf_flow_monthly[-36:-24])
            stock_yoy_prior = (
                (prior_recent - prior_prior) / prior_prior * 100
                if prior_prior != 0 else None
            )
        else:
            stock_yoy_prior = None
        if stock_yoy_now is not None and stock_yoy_prior is not None:
            impulse = stock_yoy_now - stock_yoy_prior
            return {
                "value": round(impulse, 3),
                "trend": _trend(impulse),
                "threshold_pp": threshold_pp,
                "methodology": (
                    "TSF flow → trailing-12m-sum YoY → 12-month change. "
                    "This is flow-yoy second-derivative, NOT stock-yoy "
                    "(which PBOC publishes directly = 8.3% at 2025-12). "
                    "Flow-yoy magnitudes can run 5-20pp larger than stock-yoy "
                    "because the denominator is one year of flow vs. "
                    "multi-decade accumulated stock. Trend direction "
                    "(expanding/contracting) is the load-bearing signal, "
                    "NOT the absolute magnitude. Switch to true stock-yoy "
                    "input when PBOC stock series becomes available in "
                    "akshare or via a direct PBOC scrape."
                ),
                "source": "akshare shrzgm (TSF monthly flow, 亿元)",
                "tsf_flow_yoy_now": round(stock_yoy_now, 3),
                "tsf_flow_yoy_12mo_prior": round(stock_yoy_prior, 3),
            }

    if m2_yoy and len(m2_yoy) >= 13:
        impulse = m2_yoy[-1] - m2_yoy[-13]
        return {
            "value": round(impulse, 3),
            "trend": _trend(impulse),
            "threshold_pp": threshold_pp,
            "methodology": (
                "M2 yoy 12-month change (TSF unavailable fallback; less "
                "precise — M2 ↔ credit linkage weakened by 2024-2025 "
                "re-categorization)."
            ),
            "source": "nbs m2-yoy",
        }

    return None


def _extract_observations(node: dict | None) -> list[float]:
    """Extract numeric value list from an indicator block's observations."""
    if not isinstance(node, dict):
        return []
    obs = node.get("observations") or []
    out: list[float] = []
    for o in obs:
        if isinstance(o, dict) and o.get("value") is not None:
            try:
                out.append(float(o["value"]))
            except (TypeError, ValueError):
                pass
    return out


def pack_regime_pack() -> dict:
    """Macro regime data: NBS (21) + akshare PBOC/Caixin (8) + FRED USDCNY.

    Adds a `cn_specific.credit_impulse` block computed from akshare TSF
    monthly flow + NBS M2 yoy per CICC convention. See
    `analysis-macro-regime/references/credit-impulse-methodology.md`.
    """
    _log("regime-pack start", "CN macro bundle")
    t0 = time.monotonic()
    _log("pack [nbs]", f"{len(NBS_PRESETS)} presets")
    nbs = _nbs(["--preset", ",".join(NBS_PRESETS)])
    _log("pack [akshare]", f"{len(AKSHARE_PRESETS)} presets")
    akshare = _akshare(["--preset", ",".join(AKSHARE_PRESETS)])
    _log("pack [fred]", f"{len(FRED_SERIES)} series")
    fred = _fred(["--series", ",".join(FRED_SERIES), "--periods", "24"])
    _log("pack [yf markets]", f"{len(MARKET_TICKERS)} indices")
    markets = _yf(["--tickers", ",".join(MARKET_TICKERS),
                   "--action", "history", "--period", "1y", "--interval", "1d"])
    sources_root = {"nbs": nbs, "akshare": akshare, "fred": fred, "markets": markets}
    series_flat = _flatten_regime_to_series(sources_root)

    # CN-specific helper computations (Phase 1 ADR-0004).
    ak_indicators = (akshare.get("indicators") or {}) if isinstance(akshare, dict) else {}
    nbs_indicators = (nbs.get("indicators") or {}) if isinstance(nbs, dict) else {}
    tsf_flow = _extract_observations(ak_indicators.get("shrzgm"))
    m2_yoy = _extract_observations(nbs_indicators.get("m2-yoy"))
    credit_impulse = _compute_credit_impulse(
        tsf_stock_yoy=None,         # PBOC stock-yoy series not in akshare; future T2 work
        tsf_flow_monthly=tsf_flow,
        m2_yoy=m2_yoy,
    )

    _log("regime-pack done", f"in {time.monotonic() - t0:.1f}s")
    return {
        "pack": "regime-pack",
        "country": "CN",
        "nbs": nbs,
        "akshare": akshare,
        "fred": fred,
        "markets": markets,
        "series": series_flat,  # T2 canonical flat alias per ADR-0002
        "cn_specific": {
            "credit_impulse": credit_impulse,
            "credit_impulse_methodology_doc": (
                "investing-toolkit/skills/analysis-macro-regime/references/"
                "credit-impulse-methodology.md"
            ),
        },
        "_provenance": {
            "nbs_indicators": NBS_PRESETS,
            "akshare_indicators": AKSHARE_PRESETS,
            "fred_series": FRED_SERIES,
            "market_tickers": MARKET_TICKERS,
        },
    }


# ---------------------------------------------------------------------------
# Common interface — build_pack(pack_name, tickers) -> dict
# ---------------------------------------------------------------------------

def build_pack(pack_name: str, tickers: list[str]) -> dict:
    """Dispatch to the CN pack builder for `pack_name`.

    `tickers` is always a list (the old --ticker/--tickers CLI mutex is
    gone with the CLI shell): single-ticker packs use tickers[0];
    comps-multiples/screener-batch accept 1+ tickers uniformly via the
    batch builders (comps-multiples always returns the `info` section,
    matching the current data-cn/pack.py batch shape).

    No exit-code logic here — the unified pack.py facade (Task 4) owns
    the fail-loud exit contract; this raises ValueError on a bad
    pack_name/empty ticker list for the facade to catch and slot.
    """
    if pack_name not in SUPPORTED_PACKS:
        raise ValueError(f"unsupported pack: {pack_name!r} (expected one of {SUPPORTED_PACKS})")

    if pack_name == "regime-pack":
        return pack_regime_pack()

    if not tickers:
        raise ValueError(f"pack {pack_name!r} requires at least one ticker")

    if pack_name == "snapshot":
        return pack_snapshot(tickers[0])
    if pack_name == "memo-fetch":
        return pack_memo_fetch(tickers[0])
    if pack_name == "comps-multiples":
        return pack_comps_multiples_batch(_normalise_ticker_list(",".join(tickers)))
    if pack_name == "screener-batch":
        return pack_screener_batch(_normalise_ticker_list(",".join(tickers)))

    raise AssertionError(f"unreachable: {pack_name!r} in SUPPORTED_PACKS but unhandled")
