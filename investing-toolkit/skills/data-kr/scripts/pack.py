#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
pack.py — data-kr Layer 1 facade for Korea (KOSPI / KOSDAQ + macro)

Composes underlying clients into pack-typed bundles (Anthropic v2.0.0
three-layer convention). Stock-side is yfinance only (Tier 2) — Korea has
no primary-source equity client wired in this skill yet (DART deferred).
Regime-pack pulls BOK ECOS-KEYSTAT via FinanceDataReader.

Pack types:
  --pack snapshot          (single ticker; yfinance info + price summary)
  --pack memo-fetch        (single ticker; yfinance financials, Tier 2 only)
  --pack comps-multiples   (single or batch; multiples-only)
  --pack screener-batch    (batch; lightweight screening fields)
  --pack regime-pack       (no ticker; BOK ECOS-KEYSTAT 54-indicator pull)

Usage:
  pack.py --ticker 005930.KS --pack snapshot
  pack.py --ticker 005930   --pack snapshot          # auto-suffix .KS
  pack.py --tickers 005930.KS,000660.KS --pack screener-batch
  pack.py --pack regime-pack
  pack.py --pack regime-pack --indicators rates,inflation

Suffix convention:
  .KS = KOSPI (Korea Stock Exchange — large cap)
  .KQ = KOSDAQ

Auto-suffix rule for tickers:
  - 6-digit numeric ticker without suffix → append .KS by default
  - Tickers already ending in .KS or .KQ pass through unchanged
  - Use --kosdaq flag to force .KQ for ambiguous numeric tickers

Cache: $INVESTING_TOOLKIT_CACHE (inherited from underlying clients)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YFINANCE = SCRIPT_DIR / "yfinance_client.py"
FDR = SCRIPT_DIR / "fdr_client.py"

# Macro indicator groups (regime-pack) — mirrors korea-macro SKILL.md.
REGIME_GROUPS: dict[str, list[str]] = {
    "rates": [
        "policy-rate", "call-rate", "cd-91d", "koribor-3m",
        "treasury-3y", "treasury-5y", "corp-bond-3y",
    ],
    "inflation": ["cpi", "core-cpi", "ppi", "import-pi", "export-pi"],
    "growth": [
        "gdp-qoq", "gdp-nominal", "ipi", "manufacturing",
        "private-consumption", "equipment-investment", "construction-investment",
    ],
    "industry": [
        "manufacturing-inventory", "manufacturing-shipment",
        "manufacturing-operating-rate", "services-production",
        "retail-sales", "wholesale-retail", "credit-card-usage",
        "machinery-orders", "capital-goods-output",
        "construction-completion", "construction-orders",
    ],
    "labor": ["unemployment", "employment-rate"],
    "trade": ["current-account", "terms-of-trade", "goods-exports"],
    "money": ["m1", "m2", "lf", "household-credit"],
    "sentiment": ["consumer-sentiment", "economic-sentiment"],
    "cycle": ["leading-cycle", "coincident-cycle"],
    "markets": ["kospi", "kosdaq"],
    "fx": ["krw-usd", "krw-jpy", "krw-eur", "krw-cny", "fx-reserves"],
    "realestate": ["housing-price"],
    "demographics": ["population", "aging-ratio", "fertility-rate"],
}

# Lightweight fields for screener-batch (info action returns rich dict; we
# do not subset here — analysis-screener will project. Spec calls for
# "lightweight fields"; yfinance info is already the lightweight surface.)


# ---------------------------------------------------------------------------
# Ticker normalization (.KS / .KQ auto-suffix)
# ---------------------------------------------------------------------------

# Module-level collector for ticker-normalization warnings. Each call to
# normalize_ticker may append a string here; pack functions surface this
# under _provenance.ticker_normalization_warnings so consumers can audit.
TICKER_NORMALIZATION_WARNINGS: list[str] = []


def normalize_ticker(ticker: str, force_kosdaq: bool = False) -> str:
    """Append .KS (or .KQ if --kosdaq) to bare 6-digit numeric tickers.

    Edge-case handling:
      - 6-digit numeric: auto-suffix .KS (or .KQ with --kosdaq).
      - Already-suffixed (.KS / .KQ): pass through.
      - Bare numeric of any other length (e.g. 4/5/7-digit typo or
        leading-zero strip): pass through unchanged but warn to stderr
        and record under TICKER_NORMALIZATION_WARNINGS.
      - Non-numeric, non-suffixed token: pass through unchanged but warn.
    """
    t = ticker.strip().upper()
    if t.endswith(".KS") or t.endswith(".KQ"):
        return t
    # Bare 6-digit Korean ticker code (e.g. 005930)
    if t.isdigit() and len(t) == 6:
        return f"{t}.KQ" if force_kosdaq else f"{t}.KS"
    # Edge cases: bare numeric of wrong length, or non-numeric token.
    msg = (
        f"Unrecognized KR ticker format: '{ticker}' — expected 6-digit "
        f"(.KS auto-append) or explicit .KS/.KQ suffix; passing through "
        f"unchanged (yfinance lookup will likely fail)."
    )
    print(f"[data-kr WARN] {msg}", file=sys.stderr)
    TICKER_NORMALIZATION_WARNINGS.append(msg)
    return t


def normalize_tickers(tickers: str, force_kosdaq: bool = False) -> str:
    return ",".join(
        normalize_ticker(t, force_kosdaq) for t in tickers.split(",") if t.strip()
    )


def _consume_ticker_warnings() -> list[str]:
    """Drain and return the current ticker-normalization warning list."""
    out = list(TICKER_NORMALIZATION_WARNINGS)
    TICKER_NORMALIZATION_WARNINGS.clear()
    return out


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> dict:
    """Invoke a client script via uv run, parse stdout JSON, propagate errors."""
    full = ["uv", "run", str(cmd[0])] + cmd[1:]
    try:
        proc = subprocess.run(
            full, capture_output=True, text=True, check=False,
            env=os.environ.copy(),
        )
    except FileNotFoundError as e:
        return {"error": f"uv not found: {e}", "_partial": True}

    out = proc.stdout.strip()
    if not out:
        return {
            "error": f"empty stdout from {cmd[0]}",
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
            "_partial": True,
        }
    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        return {
            "error": f"invalid JSON from {cmd[0]}: {e}",
            "stdout_tail": out[-2000:],
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
            "_partial": True,
        }
    if proc.returncode != 0 and "error" not in data:
        data["_returncode"] = proc.returncode
    return data


# ---------------------------------------------------------------------------
# Pack implementations
# ---------------------------------------------------------------------------

def pack_snapshot(ticker: str) -> dict:
    """yfinance info + 1y price history — quick overview card."""
    info = _run([str(YFINANCE), "--ticker", ticker, "--action", "info"])
    history = _run([str(YFINANCE), "--ticker", ticker, "--action", "history",
                    "--period", "1y"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea has no primary-source equity client wired in data-kr "
            "yet. Tier A would be DART (전자공시시스템, dart.fss.or.kr) — "
            "integration deferred to a future minor version. Snapshot "
            "fields are yfinance-derived (Tier 2)."
        ),
        "exchange_suffix": ticker.split(".")[-1] if "." in ticker else None,
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    return {
        "pack": "snapshot",
        "country": "kr",
        "ticker": ticker,
        "info": info,
        "history": history,
        "_provenance": provenance,
    }


def pack_memo_fetch(ticker: str) -> dict:
    """yfinance financials only. Korean primary-source (DART) deferred."""
    info = _run([str(YFINANCE), "--ticker", ticker, "--action", "info"])
    financials_annual = _run([str(YFINANCE), "--ticker", ticker,
                              "--action", "financials", "--period", "annual"])
    financials_quarterly = _run([str(YFINANCE), "--ticker", ticker,
                                 "--action", "financials", "--period", "quarterly"])
    history = _run([str(YFINANCE), "--ticker", ticker, "--action", "history",
                    "--period", "5y"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea has no primary-source equity client wired in data-kr "
            "yet. Tier A would be DART (전자공시시스템, "
            "dart.fss.or.kr) — integration deferred to a future minor "
            "version. Treat all financials below as unverified scraper output."
        ),
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    return {
        "pack": "memo-fetch",
        "country": "kr",
        "ticker": ticker,
        "tier": "Tier 2 only",
        "info": info,
        "financials_annual": financials_annual,
        "financials_quarterly": financials_quarterly,
        "history": history,
        "_provenance": provenance,
    }


def pack_comps_multiples(tickers: list[str]) -> dict:
    """Multiples-only fetch for anchor + peers. Single or batch.

    Schema is normalized: regardless of single or batch, the result always
    exposes `info` keyed by ticker so analysis-comps consumes one shape:
        {"info": {"005930.KS": {...}, "000660.KS": {...}}}
    """
    if len(tickers) == 1:
        single = _run([str(YFINANCE), "--ticker", tickers[0], "--action", "info"])
        info_by_ticker: dict = {tickers[0]: single}
    else:
        batch = _run([str(YFINANCE), "--tickers", ",".join(tickers),
                      "--action", "info"])
        # yfinance_client batch shape (canonical):
        #   {"mode": "batch", "action": "info", "tickers": {ticker: {...}}, ...}
        # We extract the inner per-ticker dict so consumers always see
        # `info: {ticker: {...}}` regardless of single vs batch.
        if (
            isinstance(batch, dict)
            and isinstance(batch.get("tickers"), dict)
        ):
            info_by_ticker = batch["tickers"]
        elif isinstance(batch, dict) and "results" in batch and isinstance(
            batch["results"], dict
        ):
            info_by_ticker = batch["results"]
        else:
            # Fallback: wrap whole payload under a sentinel so consumer can
            # still inspect it; analysis-comps will treat as partial.
            info_by_ticker = {"_batch_unparsed": batch}
    result: dict = {
        "pack": "comps-multiples",
        "country": "kr",
        "tickers": tickers,
        "info": info_by_ticker,
    }
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Korea multiples are yfinance-derived. DART (전자공시시스템) "
            "integration deferred. Multiples extraction is downstream "
            "(analysis-comps)."
        ),
        "multiples_set": ["trailingPE", "forwardPE", "evEbitda",
                          "priceToSales", "priceToBook"],
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    result["_provenance"] = provenance
    return result


def pack_screener_batch(tickers: list[str]) -> dict:
    """Batch info pull for screener (lightweight fields)."""
    batch = _run([str(YFINANCE), "--tickers", ",".join(tickers),
                  "--action", "info"])
    provenance: dict = {
        "tier": "Tier 2 (yfinance unofficial)",
        "primary_source_status": "deferred",
        "primary_source_note": (
            "Screener batch is yfinance-derived. DART (전자공시시스템) "
            "integration deferred."
        ),
        "ticker_count": len(tickers),
    }
    warnings = _consume_ticker_warnings()
    if warnings:
        provenance["ticker_normalization_warnings"] = warnings
    return {
        "pack": "screener-batch",
        "country": "kr",
        "tickers": tickers,
        "batch": batch,
        "_provenance": provenance,
    }


def pack_regime_pack(indicators: str) -> dict:
    """Macro-regime pull via fdr_client → BOK ECOS-KEYSTAT (54 indicators)."""
    if indicators == "all":
        groups = list(REGIME_GROUPS.keys())
    else:
        groups = [g.strip() for g in indicators.split(",") if g.strip()]
        unknown = [g for g in groups if g not in REGIME_GROUPS]
        if unknown:
            return {
                "error": f"unknown indicator group(s): {unknown}",
                "available": list(REGIME_GROUPS.keys()),
                "_partial": True,
            }

    by_group: dict[str, dict] = {}
    for grp in groups:
        presets = REGIME_GROUPS[grp]
        result = _run([str(FDR), "--preset", ",".join(presets)])
        by_group[grp] = result

    return {
        "pack": "regime-pack",
        "country": "kr",
        "groups_requested": groups,
        "data": by_group,
        "_provenance": {
            "primary_source_status": "available",
            "primary_source_note": (
                "BOK ECOS-KEYSTAT via FinanceDataReader (Tier A primary). "
                "Secondary fallback: FRED (krw-usd only — DEXKOUS)."
            ),
            "indicator_count_total": sum(len(v) for k, v in REGIME_GROUPS.items()
                                         if k in groups),
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="data-kr pack facade — Korea (KOSPI/KOSDAQ + macro)",
    )
    ticker_group = parser.add_mutually_exclusive_group(required=False)
    ticker_group.add_argument("--ticker", help="Single ticker (e.g. 005930.KS)")
    ticker_group.add_argument("--tickers",
                              help="Comma-separated tickers (e.g. 005930.KS,000660.KS)")
    parser.add_argument("--pack", required=True,
                        choices=["snapshot", "memo-fetch", "comps-multiples",
                                 "screener-batch", "regime-pack"],
                        help="Pack type")
    parser.add_argument("--indicators", default="all",
                        help="(regime-pack only) Comma-separated groups or 'all'")
    parser.add_argument("--kosdaq", action="store_true",
                        help="Treat bare numeric tickers as KOSDAQ (.KQ) instead of KOSPI (.KS)")

    args = parser.parse_args()

    # Validate ticker presence per pack type
    if args.pack in {"snapshot", "memo-fetch"}:
        if not args.ticker:
            parser.error(f"--pack {args.pack} requires --ticker")
        ticker = normalize_ticker(args.ticker, args.kosdaq)
        if args.pack == "snapshot":
            out = pack_snapshot(ticker)
        else:
            out = pack_memo_fetch(ticker)

    elif args.pack == "comps-multiples":
        if not (args.ticker or args.tickers):
            parser.error("--pack comps-multiples requires --ticker or --tickers")
        raw = args.tickers if args.tickers else args.ticker
        tickers = [normalize_ticker(t, args.kosdaq)
                   for t in raw.split(",") if t.strip()]
        out = pack_comps_multiples(tickers)

    elif args.pack == "screener-batch":
        if not args.tickers:
            parser.error("--pack screener-batch requires --tickers")
        tickers = [normalize_ticker(t, args.kosdaq)
                   for t in args.tickers.split(",") if t.strip()]
        out = pack_screener_batch(tickers)

    elif args.pack == "regime-pack":
        out = pack_regime_pack(args.indicators)

    else:
        parser.error(f"unsupported pack: {args.pack}")
        return

    print(json.dumps(out, default=str, indent=2))
    if isinstance(out, dict) and out.get("_partial"):
        sys.exit(1)


if __name__ == "__main__":
    main()
