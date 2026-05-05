#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
etf_aggregator.py — build-time SPDR sector ETF aggregate computer (v2.2.0-c-bench).

For each of the 11 SPDR Select Sector ETFs, fetches ETF holdings from yfinance,
classifies each holding's schema (via v2.2.0-c sector_classifier), runs the
holding through compute_multiples_from_memo_fetch + compute_indicators_from_memo_fetch
under the holding's own schema, then takes a holdings-weighted average over each
multiple/indicator in the ETF's mapped schema (per references/etf-schema-map.json).

This is a build-time CLI tool — runs in GitHub Actions weekly cron. NOT pure-compute
(does network I/O via subprocess data-us pack.py + yfinance_client.py). Output JSONs
land in references/sector-etf-aggregate-<ETF>.json and are committed by the GHA bot.

CLI:
    uv run etf_aggregator.py --etf XLK
    uv run etf_aggregator.py --all          # all 11 ETFs
    uv run etf_aggregator.py --etf XLK --output -    # write to stdout instead of references/
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


# ---------------------------------------------------------------------------
# Progress logging (v2.2.0-p)
# ---------------------------------------------------------------------------
# Default-verbose stderr; --quiet opts out. Tag identifies the originating
# script. Inline (not shared module) to preserve PEP 723 zero-runtime-dependency.

_QUIET = False
_LOG_TAG = "etf-aggregator"


def _log(stage: str, msg: str = "") -> None:
    if _QUIET:
        return
    suffix = f": {msg}" if msg else ""
    sys.stderr.write(f"[{_LOG_TAG}] {stage}{suffix}\n")
    sys.stderr.flush()

# Import compute helpers (renamed in Task 1 to drop _ prefix).
from comps_compute import (  # noqa: E402
    compute_indicators_from_memo_fetch,
    compute_multiples_from_memo_fetch,
    _load_schema,
)
from sector_classifier import KNOWN_SCHEMA_IDS, classify  # noqa: E402

_REFERENCES_DIR = _SCRIPT_DIR.parent / "references"
_ETF_SCHEMA_MAP_PATH = _REFERENCES_DIR / "etf-schema-map.json"
_ROOT = _SCRIPT_DIR.parents[3]   # repo root
_DATA_US_PACK = _ROOT / "investing-toolkit" / "skills" / "data-us" / "scripts" / "pack.py"
_YFINANCE_CLIENT = _ROOT / "investing-toolkit" / "skills" / "data-us" / "scripts" / "yfinance_client.py"

# Outlier bounds (per spec §6.2):
#   multiples can be negative (P/E on a loss-making issuer); bound [0, 200]
#   excludes negatives outright (sector aggregates intentionally drop loss-makers
#   from per-multiple averages).
_MULTIPLE_BOUNDS = (0.0, 200.0)
#   indicators are percentages; allow negatives (margins/ROE can be negative)
#   but cap extremes.
_INDICATOR_BOUNDS = (-100.0, 200.0)


def _load_etf_to_schema() -> dict[str, str]:
    data = json.loads(_ETF_SCHEMA_MAP_PATH.read_text(encoding="utf-8"))
    mapping = data["etf_to_schema"]
    bad = [v for v in mapping.values() if v not in KNOWN_SCHEMA_IDS]
    if bad:
        raise ValueError(f"etf-schema-map.json has unknown schema_ids: {bad}")
    return mapping


# -- I/O facades (override in tests) ---------------------------------------

def fetch_holdings(etf: str) -> dict:
    """Subprocess yfinance_client.py --action holdings --ticker <etf>."""
    proc = subprocess.run(
        ["uv", "run", str(_YFINANCE_CLIENT), "--action", "holdings", "--ticker", etf],
        capture_output=True, text=True, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"yfinance_client holdings fetch failed for {etf}: {proc.stderr[:300]}")
    return json.loads(proc.stdout)


def fetch_memo_fetch(ticker: str) -> dict:
    """Subprocess data-us pack.py --pack memo-fetch --ticker <ticker>.

    Cache-aware: data-us pack.py reuses its own cache; back-to-back calls in the
    same session for the same ticker hit the cache.
    """
    proc = subprocess.run(
        ["uv", "run", str(_DATA_US_PACK), "--pack", "memo-fetch", "--ticker", ticker],
        capture_output=True, text=True, timeout=420,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"data-us memo-fetch failed for {ticker}: {proc.stderr[:300]}")
    return json.loads(proc.stdout)


# -- Aggregation ------------------------------------------------------------

def _classify_holding(memo: dict, ticker: str) -> Any:
    info = (memo.get("company_info") or {})
    return classify(ticker=ticker, sector=info.get("sector"), industry=info.get("industry"))


def _per_holding_compute(memo: dict, holding_schema: dict) -> tuple[dict, dict]:
    multiples, _multi_prov, _multi_warns = compute_multiples_from_memo_fetch(
        memo, direct_multiples={}, schema=holding_schema,
    )
    indicators, _ind_prov, _ind_warns = compute_indicators_from_memo_fetch(
        memo, holding_schema,
    )
    return multiples, indicators


def _weighted_average(
    contributions: list[tuple[float, float]],   # (weight, value)
    bounds: tuple[float, float],
) -> tuple[float | None, int]:
    """Returns (weighted_avg, outliers_dropped_count). None if no contributors."""
    lo, hi = bounds
    in_bounds = [(w, v) for w, v in contributions if v is not None and lo <= v <= hi]
    outliers = sum(1 for w, v in contributions if v is not None and not (lo <= v <= hi))
    if not in_bounds:
        return None, outliers
    total_weight = sum(w for w, _ in in_bounds)
    if total_weight <= 0:
        return None, outliers
    weighted = sum(w * v for w, v in in_bounds) / total_weight
    return weighted, outliers


def aggregate_etf(etf: str) -> dict:
    _log("etf start", etf)
    t_etf = time.monotonic()
    etf_to_schema = _load_etf_to_schema()
    if etf not in etf_to_schema:
        raise ValueError(f"unknown ETF {etf!r}; known: {sorted(etf_to_schema)}")
    etf_schema_id = etf_to_schema[etf]
    etf_schema = _load_schema(etf_schema_id)
    etf_multiple_ids = [m["id"] for m in etf_schema.get("multiples") or []]
    etf_indicator_ids = [i["id"] for i in etf_schema.get("indicators") or []]

    _log("etf [holdings]", f"{etf} (schema={etf_schema_id})")
    holdings_payload = fetch_holdings(etf)
    holdings = holdings_payload.get("holdings") or []
    _log("etf holdings", f"{etf} {len(holdings)} holdings")

    # Per-holding compute (gather contributions per multiple_id / indicator_id)
    multiple_contribs: dict[str, list[tuple[float, float]]] = {m: [] for m in etf_multiple_ids}
    indicator_contribs: dict[str, list[tuple[float, float]]] = {i: [] for i in etf_indicator_ids}
    skipped: list[dict] = []
    weight_consumed = 0.0
    schema_dispatch: dict[str, list[str]] = {}

    total_holdings = len(holdings)
    for i, h in enumerate(holdings, 1):
        ticker = h["ticker"]
        weight = float(h.get("weight") or 0)
        _log(f"holding [{i}/{total_holdings}]", f"{ticker} weight={weight:.4f}")
        try:
            memo = fetch_memo_fetch(ticker)
        except RuntimeError as exc:
            _log(f"holding [{i}/{total_holdings}] skipped", f"{ticker}: {str(exc)[:80]}")
            skipped.append({"ticker": ticker, "weight": weight, "reason": str(exc)[:120]})
            continue
        cls = _classify_holding(memo, ticker)
        h_schema = _load_schema(cls.schema_id)
        h_multiples, h_indicators = _per_holding_compute(memo, h_schema)
        weight_consumed += weight
        schema_dispatch.setdefault(cls.schema_id, []).append(ticker)

        for mid in etf_multiple_ids:
            v = h_multiples.get(mid)
            if v is not None:
                multiple_contribs[mid].append((weight, v))
        for iid in etf_indicator_ids:
            entry = h_indicators.get(iid)
            v = entry.get("value") if isinstance(entry, dict) else None
            if v is not None:
                indicator_contribs[iid].append((weight, v))

    # Weighted average + outlier drop
    multiples_out: dict[str, float | None] = {}
    indicators_out: dict[str, float | None] = {}
    outliers_dropped: dict[str, int] = {}
    for mid in etf_multiple_ids:
        avg, outliers = _weighted_average(multiple_contribs[mid], _MULTIPLE_BOUNDS)
        multiples_out[mid] = avg
        if outliers:
            outliers_dropped[mid] = outliers
    for iid in etf_indicator_ids:
        avg, outliers = _weighted_average(indicator_contribs[iid], _INDICATOR_BOUNDS)
        indicators_out[iid] = avg
        if outliers:
            outliers_dropped[iid] = outliers

    _log("etf done", f"{etf} {len(holdings) - len(skipped)}/{len(holdings)} holdings priced in {time.monotonic() - t_etf:.1f}s")
    return {
        "etf":       etf,
        "schema_id": etf_schema_id,
        "as_of":     datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "_meta": {
            "holdings_count":      len(holdings),
            "weight_coverage_pct": round(weight_consumed * 100.0, 2),
            "outliers_dropped":    outliers_dropped,
            "skipped_holdings":    skipped,
            "schema_dispatch":     {k: len(v) for k, v in schema_dispatch.items()},
            "source":              "yfinance funds_data + data-us memo-fetch",
        },
        "multiples":  multiples_out,
        "indicators": indicators_out,
    }


# -- CLI --------------------------------------------------------------------

def _main() -> int:
    parser = argparse.ArgumentParser(description="Build-time SPDR sector ETF aggregate computer (v2.2.0-c-bench).")
    parser.add_argument("--etf", type=str, default=None,
                        help="Single ETF ticker (e.g. XLK); mutually exclusive with --all")
    parser.add_argument("--all", action="store_true",
                        help="Aggregate all 11 SPDR ETFs from etf-schema-map.json")
    parser.add_argument("--output", type=str, default=None,
                        help="Output path; '-' = stdout; default writes to references/sector-etf-aggregate-<ETF>.json")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress progress logging on stderr (default: verbose)")
    args = parser.parse_args()
    global _QUIET
    _QUIET = args.quiet

    if args.all and args.etf:
        parser.error("--etf and --all are mutually exclusive")
    if not args.all and not args.etf:
        parser.error("specify one of --etf <ticker> or --all")

    etf_to_schema = _load_etf_to_schema()
    targets = sorted(etf_to_schema) if args.all else [args.etf.upper()]

    if args.all:
        _log("all-mode start", f"{len(targets)} ETFs")
        t_all = time.monotonic()
    for etf_idx, etf in enumerate(targets, 1):
        if args.all:
            _log(f"etf [{etf_idx}/{len(targets)}]", etf)
        result = aggregate_etf(etf)
        if args.output == "-":
            json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
        else:
            target_path = (
                Path(args.output) if args.output is not None
                else _REFERENCES_DIR / f"sector-etf-aggregate-{etf}.json"
            )
            target_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            sys.stderr.write(f"[etf_aggregator] wrote {target_path}\n")
    if args.all:
        _log("all-mode done", f"{len(targets)} ETFs in {time.monotonic() - t_all:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
